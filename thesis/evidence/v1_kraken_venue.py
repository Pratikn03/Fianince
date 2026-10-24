"""Test V1: does the thin-book effect appear on a spot venue never used before? (spec checks/prereg/V1_kraken_venue.json)

Chapter 3's statistic forecasts adverse excursions in thin Binance perpetuals, about a fifth as strongly in
thin US stocks, negligibly on Bybit and not at all on Coinbase spot. Two explanations predict different
things on a new spot venue without leverage. A thin-book explanation predicts an effect in the thinnest
pairs of any venue; a perpetual-leverage explanation predicts none on spot. Kraken spot (public REST trade
history, no account) has never been used in this project and is available from the United States.

Universe (fixed before any trade is downloaded): Kraken spot pairs quoted in USD that are online, excluding
stablecoins and wrapped or staked tokens, with at least 50 daily candles from 2025-03-01 to 2025-04-30, a
training-period window (Kraken's daily candles reach back 720 days). Liquidity = median daily dollar
volume (volume x VWAP) over those candles; thin = $0.5M-$5M and a median of at least 1,000 trades a day;
up to 20 thin pairs drawn with seed 20261028 (rng offset 1).
Days: training = the 7th, 14th, 21st and 28th of January-June 2025; test = the same days of July 2025 to
September 2026. A day is valid if at least 60% of its minutes have a trade.

Blocks and estimators are those of Chapter 3's Coinbase test (Part 17): hours 06-23 UTC, features from the
previous 360 minutes, outcome MAE over the next 60 minutes; candidate C3_flow (depth-free amplification
margin), placebo C3_placebo (flow circularly shifted by 180 minutes inside the window), baseline of
volatility, impact and hour controls with pair fixed effects; out-of-sample on test days, Clark-West
(6 lags), 2,000 date-block bootstrap draws.

V1  C3_flow forecasts MAE_60 beyond the baseline in thin Kraken pairs: Clark-West p < 0.05 and the 95%
    bootstrap interval of Delta R^2 above zero.
V2  (tested only if V1 passes; fixed sequence) the real statistic beats the placebo: paired interval of
    Delta R^2(real) - Delta R^2(placebo) above zero and p < 0.05.
Registered reading: a pass of V1 favours the thin-book explanation; a fail is consistent with Coinbase and
with an explanation specific to perpetual futures.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/V1_kraken_venue.json"
COUNTER = THESIS / "checks/prereg/V1_unlock.json"
UNIVERSE = HERE / "V1_universe.json"
RESULT = HERE / "V1_results.json"
NUMBERS = THESIS / "checks/V1_numbers.tex"
DLLOG = HERE / "V1_download_log.json"

API = os.environ.get("KRAKEN_API", "https://api.kraken.com")
SEED = 20261027
STABLE = {"USDT", "USDC", "DAI", "PYUSD", "EURC", "GUSD", "PAX", "PAXG", "BUSD", "UST", "TUSD", "USDS", "RLUSD", "FDUSD",
          "WBTC", "CBETH", "MSOL", "LSETH", "WETH", "CBBTC", "STETH", "WAXL", "USDG", "USDQ", "USDR", "EUROP", "EURR",
          "TBTC", "ETH2", "ETH2.S", "XAUT", "AUD", "EUR", "GBP", "CAD", "CHF", "JPY", "ZUSD", "ZEUR"}
MIN_COVERAGE = 0.60
MAX_PAGES = 120
HOURS_EVAL = list(range(6, 24))
PLACEBO_SHIFT = 180
DL_LOG = []


def train_dates():
    return [d.strftime("%Y-%m-%d") for d in pd.date_range("2025-01-01", "2025-06-30") if d.day in (7, 14, 21, 28)]


def test_dates():
    return [d.strftime("%Y-%m-%d") for d in pd.date_range("2025-07-01", "2026-09-30") if d.day in (7, 14, 21, 28)]


def rng(offset=0):
    return np.random.default_rng(SEED + offset)


# ---- HTTP: Kraken public REST with a shared rate limit -------------------------------------------
_lock = threading.Lock(); _last = [0.0]; RATE = float(os.environ.get("KRAKEN_RATE", "1.0"))


def _throttle():
    with _lock:
        wait = _last[0] + 1.0 / RATE - time.time()
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()


def api(path, params=None, tries=10, opener=None):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    last = None
    for i in range(tries):
        _throttle()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-replication/1.0"})
            with (opener or urllib.request.urlopen)(req, timeout=60) as r:
                js = json.loads(r.read().decode())
            if js.get("error"):
                msg = " ".join(js["error"])
                if "Too many requests" in msg or "Rate limit" in msg or "Busy" in msg:
                    time.sleep(min(60, 2 ** i)); last = msg; continue
                raise RuntimeError(msg)
            return js["result"]
        except urllib.error.HTTPError as e:
            last = e; time.sleep(min(60, 2 ** i))
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e; time.sleep(min(60, 2 ** i))
    raise RuntimeError(f"Kraken API error {url}: {last}")


# ---- universe ------------------------------------------------------------------------------------
def universe():
    pairs = api("/0/public/AssetPairs")
    cands = {}
    for name, p in pairs.items():
        ws = p.get("wsname", "")
        if not ws.endswith("/USD") or p.get("status", "online") != "online" or name.endswith(".d"):
            continue
        base = ws.split("/")[0]
        if base in STABLE:
            continue
        cands[name] = base
    t0 = int(pd.Timestamp("2025-03-01", tz="UTC").timestamp()); t1 = int(pd.Timestamp("2025-05-01", tz="UTC").timestamp())
    liq = {}
    for i, name in enumerate(sorted(cands)):
        res = api("/0/public/OHLC", {"pair": name, "interval": 1440, "since": t0})
        rows = [r for k, v in res.items() if k != "last" for r in v]
        rows = [r for r in rows if t0 <= int(r[0]) < t1]
        if len(rows) >= 50:
            dollar = [float(r[6]) * float(r[5]) for r in rows]          # volume x vwap
            trades = [int(r[7]) for r in rows]
            liq[name] = {"base": cands[name], "median_musd": float(np.median(dollar) / 1e6),
                         "median_trades": float(np.median(trades))}
        if i % 50 == 0:
            print(f"   universe {i}/{len(cands)}", flush=True)
    pool = sorted(k for k, v in liq.items() if 0.5 <= v["median_musd"] <= 5.0 and v["median_trades"] >= 1000)
    thin = sorted(rng(1).choice(pool, min(20, len(pool)), replace=False).tolist()) if pool else []
    return {"n_usd_pairs": len(cands), "eligible": len(liq), "liquidity": liq, "thin_pool": pool, "thin": thin}


# ---- trades to minute bars -----------------------------------------------------------------------
def build_day(pair, date, cache_dir=None):
    if cache_dir:
        d_ = os.path.join(cache_dir, pair); os.makedirs(d_, exist_ok=True)
        pk = os.path.join(d_, f"{date}.pkl")
        if os.path.exists(pk):
            return pd.read_pickle(pk)
    t0 = pd.Timestamp(f"{date} 00:00:00", tz="UTC"); t1 = t0 + pd.Timedelta("1D")
    since = str(int(t0.timestamp() * 1e9)); rows, pages = [], 0
    while pages < MAX_PAGES:
        res = api("/0/public/Trades", {"pair": pair, "since": since, "count": 1000}); pages += 1
        tr = [r for k, v in res.items() if k != "last" for r in v]
        if not tr:
            break
        rows += tr
        nxt = res.get("last")
        if float(tr[-1][2]) >= t1.timestamp() or nxt is None or nxt == since:
            break
        since = nxt
    if pages >= MAX_PAGES:
        out = (None, {"symbol": pair, "date": date, "reason": "too many trades", "pages": pages})
    elif not rows:
        out = (None, {"symbol": pair, "date": date, "reason": "no trades"})
    else:
        T = pd.DataFrame([r[:4] for r in rows], columns=["price", "volume", "time", "side"])
        T = T.astype({"price": float, "volume": float, "time": float})
        T = T[(T["time"] >= t0.timestamp()) & (T["time"] < t1.timestamp())].drop_duplicates()
        if T.empty:
            out = (None, {"symbol": pair, "date": date, "reason": "no trades in day"})
        else:
            notional = (T["price"] * T["volume"] / 1e6).to_numpy()
            sign = np.where(T["side"].to_numpy() == "b", 1.0, -1.0)          # Kraken reports the taker side
            m = ((T["time"].to_numpy() - t0.timestamp()) // 60).astype(int).clip(0, 1439)
            idx = np.arange(1440)
            g = pd.DataFrame({"m": m, "px": T["price"].to_numpy(), "f": sign * notional, "v": notional}).groupby("m")
            df = pd.DataFrame(index=idx)
            df["close"] = g["px"].last().reindex(idx).ffill().bfill()
            df["flow"] = g["f"].sum().reindex(idx).fillna(0.0)
            df["vol"] = g["v"].sum().reindex(idx).fillna(0.0)
            df["ntr"] = g["px"].size().reindex(idx).fillna(0).astype(int)
            cov = float((df["ntr"] > 0).mean())
            sha = hashlib.sha256(T.to_csv(index=False).encode()).hexdigest()
            st = {"symbol": pair, "date": date, "trades": int(len(T)), "pages": pages, "minute_coverage": cov,
                  "day_ok": bool(cov >= MIN_COVERAGE), "sha256": sha}
            DL_LOG.append({"symbol": pair, "date": date, "trades": int(len(T)), "sha256": sha})
            out = (df, st)
    if cache_dir:
        pd.to_pickle(out, pk)
    return out


# ---- Part 17 estimators --------------------------------------------------------------------------
def ols(y, X):
    ok = np.all(np.isfinite(X), 1) & np.isfinite(y)
    if ok.sum() < X.shape[1] + 20:
        return None
    return np.linalg.lstsq(np.column_stack([np.ones(ok.sum()), X[ok]]), y[ok], rcond=None)[0][1:]


def impulse_2s(a, kappa, eta, q, L=60):
    x = np.zeros(L); f = np.zeros(L)
    for t in range(L):
        if t > 0:
            f[t] = (1 - eta) * f[t - 1] + eta * q * x[t - 1]
        x[t] = (a * x[t - 1] if t else 0) + kappa * ((1.0 if t == 0 else 0.0) + f[t])
        if abs(x[t]) > 1e9:
            return np.full(L, np.nan)
    return x


def c3_flow(dpw, uw, xw):
    bp0 = ols(dpw[1:], np.column_stack([uw[1:], xw[:-1]]))
    bm0 = ols(uw[1:], np.column_stack([uw[:-1], xw[:-1]]))
    if bp0 is None or bm0 is None or abs(1 - bm0[0]) < 1e-6:
        return None
    k0, a0, e0 = bp0[0], 1 + bp0[1], 1 - bm0[0]; q0 = bm0[1] / e0
    return {"C3": k0 ** 2 * e0 * q0 - (1 - a0) * k0, "kappa": k0, "a": a0}


HOURS = list(range(7, 24))


def blocks(df, s, d, flow_scale):
    p = np.log(df["close"].to_numpy()) * 1e4; u = df["flow"].to_numpy() / flow_scale
    vol = df["vol"].to_numpy()
    x = p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy(); dp = np.diff(p, prepend=np.nan)
    ew = pd.Series(np.nan_to_num(dp) ** 2).ewm(alpha=0.06, adjust=False).mean().to_numpy()
    rows = []
    for hr in HOURS_EVAL:
        t = hr * 60; w, h, f = slice(t - 360, t), slice(t - 60, t), slice(t, min(t + 61, 1440))
        row = {"symbol": s, "date": d, "hour": hr}
        real = c3_flow(dp[w], u[w], x[w]); plac = c3_flow(dp[w], np.roll(u[w], PLACEBO_SHIFT), x[w])
        if real is not None:
            row.update({"C3_flow": real["C3"], "kappa_hat": real["kappa"]})
        if plac is not None:
            row["C3_placebo"] = plac["C3"]
        uu, yy = u[w][1:], dp[w][1:]; okk = np.isfinite(uu) & np.isfinite(yy)
        v60 = np.nansum(vol[h])
        row.update({"rv_60": np.nanstd(np.diff(p[h])), "rv_360": np.nanstd(np.diff(p[w])), "abs_ret_60": abs(p[t - 1] - p[t - 60]),
                    "flow_imb_60": np.nansum(u[h]) / (np.nansum(np.abs(u[h])) + 1e-12), "log_vol_60": np.log1p(v60),
                    "kyle_lam": float(np.polyfit(uu[okk], yy[okk], 1)[0]) if okk.sum() > 60 and np.std(uu[okk]) > 0 else np.nan,
                    "amihud_60": np.log(abs(p[t - 1] - p[t - 60]) / v60 + 1e-9) if v60 > 0 else np.nan,
                    "rv_15": np.nanstd(dp[t - 15:t]), "rv_day": np.nanstd(dp[1:t]), "ewma_vol": float(np.sqrt(ew[t - 1])),
                    "mae_lag60": float(np.nanmax(np.abs(p[t - 60:t] - p[t - 61]))),
                    "MAE_60": float(np.nanmax(np.abs(p[f] - p[t - 1])))})
        for hh in HOURS:
            row[f"hr_{hh}"] = float(hr == hh)
        rows.append(row)
    return rows


CTRL = ["rv_60", "rv_360", "abs_ret_60", "flow_imb_60", "log_vol_60", "kappa_hat", "kappa_sq", "kyle_lam", "amihud_60",
        "rv_15", "rv_day", "ewma_vol", "mae_lag60"] + [f"hr_{h}" for h in HOURS]


def cw_test(y, fb, ff, lags=6):
    adj = (y - fb) ** 2 - ((y - ff) ** 2 - (fb - ff) ** 2)
    m = adj.mean(); e = adj - m; n = len(adj)
    lrv = e @ e / n + 2 * sum((1 - lag / (lags + 1)) * (e[lag:] @ e[:-lag]) / n for lag in range(1, lags + 1))
    t_ = m / np.sqrt(lrv / n)
    return float(t_), float(1 - stats.norm.cdf(t_))


def design(D, cols, syms):
    X = [np.ones(len(D))] + [D[c].to_numpy() for c in cols] + [(D["symbol"] == s).to_numpy(float) for s in syms[1:]]
    return np.column_stack(X)


def evaluate(sub, B=2000, seed=171):
    A0 = sub[sub["split"] == "train"].copy(); B0 = sub[sub["split"] == "test"].copy()
    for c in ("C3_flow", "C3_placebo"):
        lo, hi = A0[c].quantile([0.01, 0.99]); A0[c + "_w"] = A0[c].clip(lo, hi); B0[c + "_w"] = B0[c].clip(lo, hi)
    need = CTRL + ["C3_flow_w", "C3_placebo_w", "MAE_60"]
    A = A0.dropna(subset=need); Bt = B0.dropna(subset=need)
    Bt = Bt[Bt["symbol"].isin(set(A["symbol"]))].sort_values(["date", "symbol", "hour"])
    if len(A) < 200 or len(Bt) < 200:
        return {"skipped": "too few blocks", "n_train": len(A), "n_test": len(Bt)}
    syms = sorted(A["symbol"].unique()); y = Bt["MAE_60"].to_numpy(); ytr = A["MAE_60"].to_numpy()
    fit = lambda cols: design(Bt, cols, syms) @ np.linalg.lstsq(design(A, cols, syms), ytr, rcond=None)[0]
    fb, fr, fp = fit(CTRL), fit(CTRL + ["C3_flow_w"]), fit(CTRL + ["C3_placebo_w"])
    ybar = ytr.mean(); sst = np.sum((y - ybar) ** 2)
    t_r, p_r = cw_test(y, fb, fr)
    Rb = rng(seed); dd = Bt["date"].to_numpy(); ud = np.unique(dd); pos = {d: np.where(dd == d)[0] for d in ud}
    dr, dp_ = [], []
    for _ in range(B):
        i = np.concatenate([pos[d] for d in Rb.choice(ud, len(ud))]); s_ = np.sum((y[i] - ybar) ** 2)
        base = np.sum((y[i] - fb[i]) ** 2)
        dr.append((base - np.sum((y[i] - fr[i]) ** 2)) / s_); dp_.append((base - np.sum((y[i] - fp[i]) ** 2)) / s_)
    dr, dp_ = np.array(dr), np.array(dp_); diff = dr - dp_
    q = lambda v: [float(np.quantile(v, .025)), float(np.quantile(v, .975))]
    return {"n_train": len(A), "n_test": len(Bt), "n_pairs": len(syms), "n_test_dates": len(ud),
            "delta_r2": float((np.sum((y - fb) ** 2) - np.sum((y - fr) ** 2)) / sst), "delta_r2_ci": q(dr),
            "clark_west_t": t_r, "clark_west_p": p_r,
            "delta_r2_placebo": float((np.sum((y - fb) ** 2) - np.sum((y - fp) ** 2)) / sst), "delta_r2_placebo_ci": q(dp_),
            "real_minus_placebo_ci": q(diff), "real_minus_placebo_p": float(np.mean(diff <= 0))}


def verdict(ev):
    if "skipped" in ev:
        return {"V1_pass": False, "V2_pass": False, "V2_tested": False}
    v1 = bool(ev["clark_west_p"] < 0.05 and ev["delta_r2_ci"][0] > 0)
    v2 = bool(v1 and ev["real_minus_placebo_p"] < 0.05 and ev["real_minus_placebo_ci"][0] > 0)
    return {"V1_pass": v1, "V2_pass": v2, "V2_tested": v1}


def numbers_tex(ev, vd):
    d = f"{100 * ev['delta_r2']:+.2f}" if "delta_r2" in ev else "n/a"
    return ("% generated by v1_kraken_venue.py; do not edit\n"
            f"\\newcommand{{\\VoneVerdict}}{{{'passed' if vd['V1_pass'] else 'failed'}}}"
            f"\\newcommand{{\\VtwoVerdict}}{{{'passed' if vd['V2_pass'] else ('failed' if vd['V2_tested'] else 'not tested')}}}"
            f"\\newcommand{{\\VoneDeltaRtwo}}{{{d}}}\n")


def gate():
    spec = json.loads(SPEC.read_text())
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    assert hashlib.sha256((HERE / "v1_kraken_venue.py").read_bytes()).hexdigest() == spec["v1_sha256"], "code changed"
    rel = str(SPEC.relative_to(ROOT))
    commit = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", rel], cwd=ROOT, text=True).strip()
    assert commit, "specification not committed"
    assert json.loads(COUNTER.read_text())["opens"] == 0, "V1 was already opened"
    return sha, commit


def run(cache_dir=None, threads=4, resume=False, skip_gate=False, pairs=None, train=None, test=None):
    if skip_gate:
        sha, commit = "test", None
    elif resume:
        c = json.loads(COUNTER.read_text()); assert c["opens"] == 1, "nothing to resume"
        sha, commit = c["spec_sha256"], c["registration_commit"]
    else:
        sha, commit = gate()
        COUNTER.write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": commit,
                                       "opened_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
    if pairs is None:
        cached = Path(cache_dir) / "V1_universe.json" if cache_dir else None
        if UNIVERSE.exists():
            U = json.loads(UNIVERSE.read_text())
        elif cached and cached.exists():
            U = json.loads(cached.read_text())
        else:
            U = universe(); U["fixed_utc"] = datetime.now(timezone.utc).isoformat()
            if cached:
                cached.write_text(json.dumps(U, indent=1) + "\n")
        UNIVERSE.write_text(json.dumps(U, indent=1) + "\n")
        pairs = U["thin"]
    train, test = train or train_dates(), test or test_dates()
    panel, status = {}, []
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(build_day, s, d, cache_dir): (s, d) for s in pairs for d in train + test}
        for i, f in enumerate(as_completed(futs)):
            s, d = futs[f]; df, st = f.result(); status.append(st)
            if df is not None and st.get("day_ok"):
                panel[(s, d)] = df
            if (i + 1) % 100 == 0:
                print(f"  {i + 1}/{len(futs)} pair-days", flush=True)
    trs = set(train)
    ntr = {s: sum((s, d) in panel for d in train) for s in pairs}; nte = {s: sum((s, d) in panel for d in test) for s in pairs}
    inc = [s for s in pairs if ntr[s] >= 12 and nte[s] >= 20]
    scale = {}
    for s in inc:
        v = [np.nanmedian(np.abs(panel[(s, d)]["flow"].to_numpy()[panel[(s, d)]["ntr"].to_numpy() > 0]))
             for d in train if (s, d) in panel]
        scale[s] = float(np.nanmedian(v)) if v and np.nanmedian(v) > 0 else 1.0
    rows = []
    for (s, d), df in sorted(panel.items()):
        if s in inc:
            rows += blocks(df, s, d, scale[s])
    ZB = pd.DataFrame(rows)
    if ZB.empty:
        ev = {"skipped": "no included pairs", "n_train": 0, "n_test": 0}
    else:
        ZB["split"] = np.where(ZB["date"].isin(trs), "train", "test")
        ZB["kappa_sq"] = ZB["kappa_hat"] ** 2
        for c in ["kappa_hat", "kappa_sq", "kyle_lam", "amihud_60", "rv_15", "rv_day", "ewma_vol", "mae_lag60"]:
            lo, hi = ZB.loc[ZB["split"] == "train", c].quantile([0.01, 0.99]); ZB[c] = ZB[c].clip(lo, hi)
        ev = evaluate(ZB.dropna(subset=["C3_flow", "C3_placebo"]))
    vd = verdict(ev)
    res = {"test": "V1", "spec_sha256": sha, "registration_commit": commit, "run_utc": datetime.now(timezone.utc).isoformat(),
           "pairs": pairs, "included": inc, "valid_days_train": ntr, "valid_days_test": nte, "flow_scale": scale,
           "evaluation": ev, "verdict": vd}
    if not skip_gate:
        RESULT.write_text(json.dumps(res, indent=1, default=float) + "\n")
        NUMBERS.write_text(numbers_tex(ev, vd))
        DLLOG.write_text(json.dumps(DL_LOG, indent=0) + "\n")
    print(json.dumps({"evaluation": ev, "verdict": vd}, indent=1, default=float))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--cache", default=None)
    a = ap.parse_args()
    if a.run:
        run(a.cache)
