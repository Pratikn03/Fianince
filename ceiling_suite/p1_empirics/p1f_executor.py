"""P1F executor: is trader composition irrelevant for forecasting prices? (registered 14 November 2026)

Implements ceiling_suite/p1_empirics/P1F_forecast_irrelevance_spec.md exactly. The pipeline (features, pooled
regression, bootstrap, verdicts, power gate) is the one checked by simulation in
research_extension/irrelevance/p1f_design_sim.py, applied to Binance archive files.

Usage (Colab): see P1F_Forecast_Irrelevance_Colab.ipynb.  run_all(workdir) does everything and writes
p1f_results.json, p1f_universe.json, p1f_coverage.json and p1f_log.txt into workdir.
"""
import concurrent.futures as cf
import datetime as dt
import hashlib
import io
import json
import time
import zipfile

import numpy as np
import pandas as pd

BASE = "https://data.binance.vision"
S3_LIST = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
WINDOW_START = dt.date(2022, 3, 1)
NDAYS = 60
TRAIN_DAYS = 30
VOLUME_MONTH = "2022-02"
N_SYMBOLS = 30
BAR = "30min"
HL = (2, 8, 32, 128)
DELTA = 0.005
DELTA_SECONDARY = 0.002
SEED = 20261114
BOOT = 2000
GATE_DRAWS = 200
GATE_POWER = 0.80
A1_R2 = 0.5
A1_SHARE = 0.75
COVERAGE = 0.90
CLASSES = ("sum_toptrader_long_short_ratio", "count_toptrader_long_short_ratio", "count_long_short_ratio")
KLINE_COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "count",
              "taker_buy_volume", "taker_buy_quote_volume", "ignore"]

LOG = []


def log(msg):
    line = f"{dt.datetime.utcnow().isoformat(timespec='seconds')}Z  {msg}"
    LOG.append(line)
    print(line, flush=True)


# ---------------------------------------------------------------- fetching (pluggable for offline testing)
def http_fetch(url, tries=4):
    import requests
    for k in range(tries):
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.content
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(2 * (k + 1))


FETCH = http_fetch


def days():
    return [WINDOW_START + dt.timedelta(d) for d in range(NDAYS)]


def get_zip_csv(url, verify=True):
    """Download a zip and its .CHECKSUM, verify SHA-256, return the CSV text (or None if absent)."""
    blob = FETCH(url)
    if blob is None:
        return None, "missing"
    status = "unverified"
    if verify:
        chk = FETCH(url + ".CHECKSUM")
        if chk is not None:
            want = chk.decode().split()[0].strip().lower()
            got = hashlib.sha256(blob).hexdigest()
            if want != got:
                raise RuntimeError(f"checksum mismatch: {url}")
            status = "verified"
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        name = z.namelist()[0]
        return z.read(name).decode(), status


# ---------------------------------------------------------------- universe (volume only, before the window)
def list_metric_symbols():
    import re
    syms, marker = [], ""
    while True:
        url = f"{S3_LIST}?delimiter=/&prefix=data/futures/um/daily/metrics/" + (f"&marker={marker}" if marker else "")
        xml = FETCH(url).decode()
        found = re.findall(r"<Prefix>data/futures/um/daily/metrics/([A-Z0-9]+)/</Prefix>", xml)
        syms += found
        nxt = re.findall(r"<NextMarker>([^<]+)</NextMarker>", xml)
        if not nxt:
            break
        marker = nxt[0]
    return sorted(set(s for s in syms if s.endswith("USDT")))


def exists(url):
    return FETCH(url) is not None


def universe():
    """The 30 USDT perpetuals with the largest February 2022 quote volume among those with a metrics file and a
    5-minute kline file on the first and last day of the window. Uses volume and file listings only."""
    first, last = WINDOW_START.isoformat(), days()[-1].isoformat()
    cands = list_metric_symbols()
    log(f"universe: {len(cands)} USDT symbols have a metrics folder")

    def check(sym):
        ok = all(exists(f"{BASE}/data/futures/um/daily/{kind}") for kind in (
            f"metrics/{sym}/{sym}-metrics-{first}.zip", f"metrics/{sym}/{sym}-metrics-{last}.zip",
            f"klines/{sym}/5m/{sym}-5m-{first}.zip", f"klines/{sym}/5m/{sym}-5m-{last}.zip"))
        if not ok:
            return sym, None
        txt, _ = get_zip_csv(f"{BASE}/data/futures/um/monthly/klines/{sym}/1d/{sym}-1d-{VOLUME_MONTH}.zip", verify=False)
        if txt is None:
            return sym, None
        df = read_klines(txt)
        return sym, float(df["quote_volume"].sum())

    with cf.ThreadPoolExecutor(16) as ex:
        vols = dict(ex.map(check, cands))
    ranked = sorted([(v, s) for s, v in vols.items() if v is not None], reverse=True)
    chosen = [s for _, s in ranked[:N_SYMBOLS]]
    log(f"universe: {len(ranked)} eligible; chosen {chosen}")
    return chosen, {s: v for v, s in ranked}


# ---------------------------------------------------------------- parsing and bars
def read_klines(txt):
    first = txt.split("\n", 1)[0]
    header = 0 if first.startswith("open_time") else None
    df = pd.read_csv(io.StringIO(txt), header=header)
    if header is None:
        df.columns = KLINE_COLS[:df.shape[1]]
    return df


def read_metrics(txt):
    df = pd.read_csv(io.StringIO(txt))
    df["create_time"] = pd.to_datetime(df["create_time"], utc=True)
    return df


def symbol_frames(sym, workers=8):
    """Download every day of the window for one symbol; returns 5-minute klines, metrics, and coverage counts."""
    urls = []
    for d in days():
        s = d.isoformat()
        urls.append(("k", d, f"{BASE}/data/futures/um/daily/klines/{sym}/5m/{sym}-5m-{s}.zip"))
        urls.append(("m", d, f"{BASE}/data/futures/um/daily/metrics/{sym}/{sym}-metrics-{s}.zip"))

    def get(item):
        kind, d, url = item
        txt, st = get_zip_csv(url)
        return kind, d, txt, st

    ks, ms, status = [], [], {"verified": 0, "unverified": 0, "missing": 0}
    with cf.ThreadPoolExecutor(workers) as ex:
        for kind, d, txt, st in ex.map(get, urls):
            status[st] += 1
            if txt is None:
                continue
            if kind == "k":
                ks.append(read_klines(txt))
            else:
                ms.append(read_metrics(txt))
    k = pd.concat(ks) if ks else pd.DataFrame(columns=KLINE_COLS)
    m = pd.concat(ms) if ms else pd.DataFrame(columns=["create_time"] + list(CLASSES))
    return k, m, status


def to_bars(k, m):
    """30-minute bars on a complete UTC grid. Close = last 5-minute close; flow = signed taker quote volume;
    metrics = last snapshot strictly before the bar's end (conservative against look-ahead)."""
    grid = pd.date_range(pd.Timestamp(WINDOW_START, tz="UTC"), periods=NDAYS * 48, freq=BAR)
    out = pd.DataFrame(index=grid)
    if len(k):
        k = k.copy()
        k["t"] = pd.to_datetime(k["open_time"].astype("int64"), unit="ms", utc=True)
        k = k.drop_duplicates("t").set_index("t").sort_index()
        k["flow"] = 2 * k["taker_buy_quote_volume"].astype(float) - k["quote_volume"].astype(float)
        g = k.resample(BAR, label="left", closed="left")
        cnt = g["close"].count()
        out["close"] = g["close"].last().reindex(grid)
        out["flow"] = g["flow"].sum().reindex(grid)
        out.loc[cnt.reindex(grid).fillna(0) < 6, ["close", "flow"]] = np.nan
    else:
        out["close"] = np.nan
        out["flow"] = np.nan
    if len(m):
        m = m.drop_duplicates("create_time").set_index("create_time").sort_index()
        ends = grid + pd.Timedelta(BAR)
        snap = m[["sum_open_interest_value"] + list(CLASSES)].astype(float)
        idx = snap.index.searchsorted(ends - pd.Timedelta("1ns"), side="right") - 1
        vals = np.full((len(grid), snap.shape[1]), np.nan)
        okk = idx >= 0
        vals[okk] = snap.values[idx[okk]]
        age = np.full(len(grid), np.inf)
        age[okk] = (ends[okk] - snap.index[idx[okk]]).total_seconds()
        vals[age > 1800] = np.nan  # the snapshot must fall inside the bar
        for j, c in enumerate(snap.columns):
            out[c] = vals[:, j]
    else:
        for c in ["sum_open_interest_value"] + list(CLASSES):
            out[c] = np.nan
    return out


# ---------------------------------------------------------------- features (as in the design simulation)
def ema(z, hl):
    lam = 0.5 ** (1 / hl)
    out = np.empty_like(z)
    acc = np.zeros(z.shape[1:])
    for t in range(z.shape[0]):
        x = np.nan_to_num(z[t])
        acc = lam * acc + (1 - lam) * x
        out[t] = acc
    return out


def panel_arrays(bars):
    """bars: dict sym -> DataFrame. Returns arrays (T, S) for returns, flow, OI change, and (T, S, 3) class levels."""
    syms = list(bars)
    close = np.stack([bars[s]["close"].values for s in syms], 1)
    flow = np.stack([bars[s]["flow"].values for s in syms], 1)
    oi = np.stack([bars[s]["sum_open_interest_value"].values for s in syms], 1)
    R = np.diff(np.log(close), axis=0, prepend=np.nan)
    A = flow
    dOI = np.diff(np.log(oi), axis=0, prepend=np.nan)
    N = np.stack([np.stack([(bars[s][c].values - 1) / (bars[s][c].values + 1) for s in syms], 1) for c in CLASSES], -1)
    return R, A, dOI, N


def lag(z, k):
    out = np.roll(z, k, 0)
    out[:k] = np.nan
    return out


def features(R, A, dOI):
    cols = [R, lag(R, 1), lag(R, 2), A, lag(A, 1), lag(A, 2), dOI, lag(dOI, 1), lag(dOI, 2)]
    for hl in HL:
        cols += [ema(R, hl), ema(A, hl)]
    return np.stack(cols, -1)


def class_features(N):
    d1 = N - lag(N, 1)
    d8 = N - lag(N, 8)
    lev = N - ema(N, 48)
    lev[np.isnan(N)] = np.nan
    return np.concatenate([d1, d8, lev], -1)


def _std(Z, tr_mask):
    mu = np.nanmean(Z[tr_mask], 0)
    sd = np.nanstd(Z[tr_mask], 0)
    sd = np.where((sd == 0) | np.isnan(sd), 1.0, sd)
    return (Z - mu) / sd


# ---------------------------------------------------------------- the test
def evaluate(R, A, dOI, N, delta, train_end, test_end, inject=None, class_idx=None, rng=None, boot=BOOT, bpd=48):
    X = features(R, A, dOI)
    C = class_features(N)
    if class_idx is not None:
        C = C[..., [class_idx, class_idx + 3, class_idx + 6]]
    if inject is not None:
        C = np.concatenate([C, inject[..., None]], -1)
    y = np.roll(R, -1, 0)
    y[-1] = np.nan
    T, S = R.shape
    start = 2 * bpd  # warm-up for lags and moving averages
    tmask = np.zeros(T, bool)
    tmask[start:train_end] = True
    emask = np.zeros(T, bool)
    emask[train_end:test_end] = True
    Xs = np.stack([_std(X[:, s], tmask) for s in range(S)], 1)
    Cs = np.stack([_std(C[:, s], tmask) for s in range(S)], 1)
    ys = np.stack([_std(y[:, s][:, None], tmask)[:, 0] for s in range(S)], 1)
    full = np.concatenate([Xs, Cs], -1)
    ok = ~np.isnan(full).any(-1) & ~np.isnan(ys)
    rows_tr = ok & tmask[:, None]
    rows_te = ok & emask[:, None]

    def fit(Z):
        Ztr = Z[rows_tr]
        Ztr = np.column_stack([np.ones(len(Ztr)), Ztr])
        b = np.linalg.lstsq(Ztr, ys[rows_tr], rcond=None)[0]
        pred = b[0] + np.nan_to_num(Z) @ b[1:]
        return (ys - pred) ** 2

    eb = fit(Xs)
    ea = fit(full)
    d = np.where(rows_te, eb - ea, 0.0)
    yy = np.where(rows_te, ys, np.nan)
    mu_te = np.nanmean(yy, 0)
    v = np.where(rows_te, (ys - mu_te) ** 2, 0.0)
    nday = (test_end - train_end) // bpd
    sl = slice(train_end, train_end + nday * bpd)
    dd = d[sl].reshape(nday, bpd, S).sum((1, 2))
    vv = v[sl].reshape(nday, bpd, S).sum((1, 2))
    est = dd.sum() / vv.sum()
    rng = rng or np.random.default_rng(SEED)
    idx = rng.integers(0, nday, (boot, nday))
    boots = dd[idx].sum(1) / vv[idx].sum(1)
    lo, hi = np.quantile(boots, [0.10, 0.90])
    if hi < delta:
        verdict = "irrelevant"
    elif lo > 0 and est >= delta:
        verdict = "relevant"
    else:
        verdict = "inconclusive"
    per_sym = (d[sl].sum(0) / np.maximum(v[sl].sum(0), 1e-12))
    return {"verdict": verdict, "dR2": float(est), "lower90": float(lo), "upper90": float(hi),
            "n_test_rows": int(rows_te.sum()), "n_train_rows": int(rows_tr.sum()), "per_symbol_dR2": per_sym.tolist()}


def power_gate(R, A, dOI, N, train_end, rng, draws=GATE_DRAWS, bpd=48):
    """Training half only: split it in two, inject a synthetic class feature with true dR2 about 2*DELTA."""
    y = np.roll(R, -1, 0)
    T, S = R.shape
    tmask = np.zeros(T, bool)
    tmask[2 * bpd:train_end] = True
    ys = np.stack([_std(y[:, s][:, None], tmask)[:, 0] for s in range(S)], 1)
    c = np.sqrt(2 * DELTA / (1 - 2 * DELTA))
    mid = 2 * bpd + ((train_end - 2 * bpd) // bpd // 2) * bpd
    hits = 0
    for _ in range(draws):
        z = c * np.nan_to_num(ys) + rng.standard_normal(ys.shape)
        z[train_end:] = 0.0
        r = evaluate(R, A, dOI, N, DELTA, mid, train_end, inject=z, rng=rng, boot=400, bpd=bpd)
        hits += r["verdict"] == "relevant"
    return hits / draws


def a1(R, A, dOI, N, train_end, test_end, bpd=48):
    X = features(R, A, dOI)
    tgt = np.roll(N[..., 0], -8, 0) - N[..., 0]
    tgt[-8:] = np.nan
    T, S = R.shape
    r2s = []
    for s in range(S):
        Z = X[:, s]
        ok = ~np.isnan(Z).any(-1) & ~np.isnan(tgt[:, s])
        tr = ok.copy(); tr[:2 * bpd] = False; tr[train_end:] = False
        te = ok.copy(); te[:train_end] = False; te[test_end:] = False
        if tr.sum() < 100 or te.sum() < 100:
            r2s.append(float("nan")); continue
        Ztr = np.column_stack([np.ones(tr.sum()), Z[tr]])
        b = np.linalg.lstsq(Ztr, tgt[tr, s], rcond=None)[0]
        e = tgt[te, s] - (b[0] + Z[te] @ b[1:])
        r2s.append(float(1 - np.mean(e ** 2) / np.var(tgt[te, s])))
    valid = [r for r in r2s if not np.isnan(r)]
    share = float(np.mean([r < A1_R2 for r in valid])) if valid else float("nan")
    return {"pass": bool(share >= A1_SHARE), "share_below": share, "per_symbol_r2": r2s}


def spearman(x, y):
    rx = pd.Series(x).rank().values
    ry = pd.Series(y).rank().values
    return float(np.corrcoef(rx, ry)[0, 1])


# ---------------------------------------------------------------- driver
def run_all(workdir=".", syms=None, max_symbols=None):
    import os
    os.makedirs(workdir, exist_ok=True)
    t0 = time.time()
    log(f"P1F executor start; window {WINDOW_START} + {NDAYS} days; train {TRAIN_DAYS} days")
    vols = {}
    if syms is None:
        syms, vols = universe()
    if max_symbols:
        syms = syms[:max_symbols]
    json.dump({"symbols": syms, "feb2022_quote_volume": vols}, open(f"{workdir}/p1f_universe.json", "w"), indent=1)

    bars, coverage, files = {}, {}, {"verified": 0, "unverified": 0, "missing": 0}
    for s in syms:
        k, m, st = symbol_frames(s)
        for kk in files:
            files[kk] += st[kk]
        b = to_bars(k, m)
        bars[s] = b
        complete = b[["close", "flow", "sum_open_interest_value"] + list(CLASSES)].notna().all(1).values
        half = TRAIN_DAYS * 48
        coverage[s] = {"train": float(complete[:half].mean()), "test": float(complete[half:].mean())}
        log(f"{s}: coverage train {coverage[s]['train']:.3f} test {coverage[s]['test']:.3f}; files {st}")
    kept = [s for s in syms if coverage[s]["train"] >= COVERAGE and coverage[s]["test"] >= COVERAGE]
    excluded = [s for s in syms if s not in kept]
    log(f"coverage rule: kept {len(kept)}, excluded {excluded}")
    json.dump({"per_symbol": coverage, "kept": kept, "excluded": excluded, "files": files},
              open(f"{workdir}/p1f_coverage.json", "w"), indent=1)

    res = {"spec": "P1F_forecast_irrelevance_spec.md", "window_start": WINDOW_START.isoformat(), "days": NDAYS,
           "symbols_kept": kept, "symbols_excluded": excluded, "files": files}
    if len(kept) < 20:
        res["status"] = "VOID: fewer than 20 symbols meet the coverage rule"
        log(res["status"])
        _write(workdir, res)
        return res

    R, A, dOI, N = panel_arrays({s: bars[s] for s in kept})
    train_end, test_end = TRAIN_DAYS * 48, NDAYS * 48 - 1
    rng = np.random.default_rng(SEED)

    gate = power_gate(R, A, dOI, N, train_end, rng)
    res["A3_power_gate"] = {"power": gate, "required": GATE_POWER, "pass": bool(gate >= GATE_POWER)}
    log(f"A3 power gate (training half only): {gate:.3f}")
    if gate < GATE_POWER:
        res["status"] = "UNINFORMATIVE: the power gate failed; the test half was not evaluated"
        log(res["status"])
        _write(workdir, res)
        return res

    res["A1"] = a1(R, A, dOI, N, train_end, test_end)
    res["A2_primary"] = evaluate(R, A, dOI, N, DELTA, train_end, test_end, rng=np.random.default_rng(SEED))
    res["A2_delta_0.002"] = evaluate(R, A, dOI, N, DELTA_SECONDARY, train_end, test_end,
                                     rng=np.random.default_rng(SEED))
    res["A2_by_class"] = {c: evaluate(R, A, dOI, N, DELTA, train_end, test_end, class_idx=j,
                                      rng=np.random.default_rng(SEED))
                          for j, c in enumerate(CLASSES)}
    drift = np.nanstd(np.diff(N[::48, :, 0], axis=0), axis=0)
    psym = np.array(res["A2_primary"]["per_symbol_dR2"])
    rho = spearman(drift, psym)
    rb = np.random.default_rng(SEED)
    bs = [spearman(drift[i], psym[i]) for i in [rb.integers(0, len(drift), len(drift)) for _ in range(1000)]]
    res["A4_drift_spearman"] = {"rho": rho, "ci90": [float(np.nanquantile(bs, 0.05)), float(np.nanquantile(bs, 0.95))]}

    a2 = res["A2_primary"]["verdict"]
    if res["A1"]["pass"] and a2 == "irrelevant":
        res["joint_reading"] = "SUPPORTIVE: composition was invisible to prices and irrelevant for price forecasts"
    else:
        res["joint_reading"] = f"NOT SUPPORTIVE: A1 {'pass' if res['A1']['pass'] else 'fail'}, A2 {a2}"
    words = {"irrelevant": "Class positions did not improve price forecasts by delta or more beyond public prices and anonymous flow.",
             "relevant": "Class positions improved price forecasts beyond public prices and anonymous flow; the irrelevance prediction is rejected.",
             "inconclusive": "The test could not tell whether class positions improve price forecasts by delta."}
    res["A2_registered_wording"] = words[a2]
    res["A1_registered_wording"] = ("Prices and anonymous flow did not reveal how top-trader positions moved."
                                    if res["A1"]["pass"] else "Prices and anonymous flow revealed how top-trader positions moved.")
    res["status"] = "COMPLETE"
    res["seconds"] = round(time.time() - t0)
    log(f"A1 {res['A1']['pass']} ({res['A1']['share_below']:.2f}); A2 {a2} dR2 {res['A2_primary']['dR2']:.5f} "
        f"[{res['A2_primary']['lower90']:.5f}, {res['A2_primary']['upper90']:.5f}]; {res['joint_reading']}")
    _write(workdir, res)
    return res


def _write(workdir, res):
    json.dump(res, open(f"{workdir}/p1f_results.json", "w"), indent=1)
    open(f"{workdir}/p1f_log.txt", "w").write("\n".join(LOG) + "\n")
