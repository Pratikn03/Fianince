"""Test E2 analysis (registered spec E2_prospective.json plus addendum E2_addendum_proxy.json).

Run once, after 2027-02-02, when the Binance archive holds every registered date:
    E2_Prospective_Analysis.ipynb in Colab   (or  python e2_analysis.py --run --cache DIR)

Data: the 20 registered thin USD-M perpetuals, every date from 2026-10-24 (the first full UTC day
after the registration push of 2026-10-23 00:05 UTC) to 2027-01-31: 1-minute klines, bookDepth and
5-minute metrics from data.binance.vision. Training = the first 50 dates, test = the last 50.

The forced-liquidation stream named in the original specification cannot be recorded from the US
(HTTP 451) and the archive holds no liquidation files, so the addendum, registered before any
post-registration file was downloaded, replaces liquidation volume by a forced-deleveraging proxy:

    LIQ(window) = 100 x sum over 5-minute marks k in the window of max(0, -dOI_k) 1{|ret_k| > 2 sd_k}
                  / OI at the window start,
    sd_k = standard deviation of the 72 previous 5-minute returns,

that is, open interest destroyed during unusually large five-minute moves, in percent of open
interest. The hourly blocks, the six-hour C3 estimate, the controls and the out-of-sample
evaluation are the Paper 2 code (Part 6, cells Z1 and Z5); only the columns these tests use are kept.

P1  C3_hat forecasts log(1 + LIQ next hour) beyond the volatility/flow/depth controls, the impact
    controls and log(1 + LIQ previous hour): Holm-adjusted Clark-West p < 0.05 and the date-block
    bootstrap 95% interval for Delta R^2 excludes zero.
P2  Adding realized log(1 + LIQ next hour) to the excursion model (outcome MAE_60) removes at least
    half of C3_hat's forecasting gain: share = 1 - gain_with_LIQ / gain_without >= 0.5, bootstrap
    95% interval for the share above zero, Holm-adjusted bootstrap p < 0.05; P2 is evaluable only
    if C3_hat's gain without LIQ has a bootstrap interval above zero (otherwise P2 fails).
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binance_vision as bv  # noqa: E402

THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/E2_prospective.json"
ADD = THESIS / "checks/prereg/E2_addendum_proxy.json"
COUNTER = THESIS / "checks/prereg/E2_unlock.json"
RESULT = HERE / "E2_results.json"
NUMBERS = THESIS / "checks/E2_numbers.tex"
DLLOG = HERE / "E2_download_log.json"

SYMBOLS = ("ACHUSDT ALICEUSDT API3USDT ARPAUSDT BATUSDT BELUSDT CELRUSDT CHRUSDT COTIUSDT CTSIUSDT "
           "CVXUSDT GTCUSDT HOTUSDT IOTXUSDT LITUSDT LQTYUSDT OGNUSDT RLCUSDT SPELLUSDT ZENUSDT").split()
START, END, N_TRAIN = "2026-10-24", "2027-01-31", 50
EARLIEST_RUN = "2027-02-02"
SEED = 20261024
H_GUARD = 60
CTRL = ["rv_60", "rv_360", "abs_ret_60", "flow_imb_60", "log_vol_60", "log_depth1", "imbalance", "oi_chg_60"]
IMPACT = ["kappa_hat", "kappa_sq", "kyle_lam", "amihud_60"]


def dates():
    return [d.strftime("%Y-%m-%d") for d in pd.date_range(START, END, freq="D")]


def rng(offset=0):
    return np.random.default_rng(SEED + offset)


# ---- Paper 2 code (Part 6, cell Z1), unchanged -------------------------------------------------
def prep(df, flow_scale):
    p = np.log(df["close"].to_numpy()) * 1e4
    u = df["flow"].to_numpy() / flow_scale
    tot = (df["bid1"] + df["ask1"]).to_numpy()
    d = ((df["bid1"] - df["ask1"]) / (df["bid1"] + df["ask1"])).to_numpy()
    x = p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy()
    return p, u, d, x, tot


def ols(y, X):
    ok = np.all(np.isfinite(X), 1) & np.isfinite(y)
    if ok.sum() < X.shape[1] + 20:
        return None
    return np.linalg.lstsq(np.column_stack([np.ones(ok.sum()), X[ok]]), y[ok], rcond=None)[0][1:]


def impulse_t6(a, phi, kappa, r, eps, eta, q, L=120):
    x = np.zeros(L); dd = np.zeros(L); f = np.zeros(L)
    for t in range(L):
        if t > 0:
            f[t] = (1 - eta) * f[t - 1] + eta * q * x[t - 1]
        tot = (1.0 if t == 0 else 0.0) + f[t]
        x[t] = (a * x[t - 1] + phi * dd[t - 1] if t else 0) + kappa * tot
        dd[t] = ((1 - r) * dd[t - 1] if t else 0) + eps * tot
        if abs(x[t]) > 1e9:
            return np.full(L, np.nan)
    return x


def fit_t6(p, u, d, x):
    dp = np.diff(p, prepend=np.nan)
    bp = ols(dp[1:], np.column_stack([u[1:], d[:-1], x[:-1]]))
    bd = ols(d[1:], np.column_stack([d[:-1], u[1:]]))
    bm = ols(u[1:], np.column_stack([u[:-1], x[:-1]]))
    if bp is None or bd is None or bm is None:
        return None
    kappa, phi, a = bp[0], bp[1], 1 + bp[2]
    r, eps, eta = 1 - bd[0], bd[1], 1 - bm[0]
    q = bm[1] / eta if abs(eta) > 1e-6 else np.nan
    return {"kappa": kappa, "phi": phi, "a": a, "r": r, "eps": eps, "eta": eta, "q": q,
            "C3": phi * eps + kappa ** 2 * eta * q - (1 - a) * kappa}


def auc_(y, s):
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    rk = stats.rankdata(np.concatenate([pos, neg]))
    return (rk[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def cw_test(y, fb, ff, lags=6):
    adj = (y - fb) ** 2 - ((y - ff) ** 2 - (fb - ff) ** 2)
    m = adj.mean(); e = adj - m; n = len(adj)
    lrv = e @ e / n + 2 * sum((1 - lag / (lags + 1)) * (e[lag:] @ e[:-lag]) / n for lag in range(1, lags + 1))
    t_ = m / np.sqrt(lrv / n)
    return float(t_), float(1 - stats.norm.cdf(t_))


def design(D, cols, syms):
    X = [np.ones(len(D))] + [D[c].to_numpy() for c in cols] + [(D["symbol"] == s).to_numpy(float) for s in syms[1:]]
    return np.column_stack(X)


def winsor_train(D, cols):
    D = D.copy()
    for c in cols:
        lo, hi = D.loc[D["split"] == "train", c].quantile([0.01, 0.99])
        D[c] = D[c].clip(lo, hi)
    return D


def evaluate_g(sub, outcome, cands, ctrl, B=2000, level=0.95, seed=88):
    cands = [cands] if isinstance(cands, str) else list(cands)
    A0 = sub[sub["split"] == "train"].copy(); B0 = sub[sub["split"] == "test"].copy()
    cw = []
    for c in cands:
        lo, hi = A0[c].quantile([0.01, 0.99]); A0[c + "_w"] = A0[c].clip(lo, hi); B0[c + "_w"] = B0[c].clip(lo, hi); cw.append(c + "_w")
    need = ctrl + cw + [outcome]
    A = A0.dropna(subset=need); Bt = B0.dropna(subset=need)
    Bt = Bt[Bt["symbol"].isin(set(A["symbol"]))].sort_values(["date", "symbol", "hour"])
    if len(A) < 200 or len(Bt) < 200 or A[outcome].std() < 1e-8 or any(A[c].std() < 1e-12 for c in cw):
        return {"skipped": "too few blocks or no variation", "n_train": len(A), "n_test": len(Bt),
                "clark_west_p": np.nan, "delta_r2": np.nan, "delta_r2_ci": [np.nan, np.nan]}
    syms = sorted(A["symbol"].unique()); y = Bt[outcome].to_numpy()
    bb = np.linalg.lstsq(design(A, ctrl, syms), A[outcome].to_numpy(), rcond=None)[0]
    bf = np.linalg.lstsq(design(A, ctrl + cw, syms), A[outcome].to_numpy(), rcond=None)[0]
    fb = design(Bt, ctrl, syms) @ bb; ff = design(Bt, ctrl + cw, syms) @ bf
    ybar = A[outcome].mean(); sst = np.sum((y - ybar) ** 2)
    t_, p_ = cw_test(y, fb, ff)
    tail = (y > A[outcome].quantile(0.9)).astype(int)
    Rb = rng(seed); dd = Bt["date"].to_numpy(); ud = np.unique(dd)
    pos = {d: np.where(dd == d)[0] for d in ud}; dR2, dA = [], []
    for _ in range(B):
        idx = np.concatenate([pos[d] for d in Rb.choice(ud, len(ud))])
        s_ = np.sum((y[idx] - ybar) ** 2)
        dR2.append((np.sum((y[idx] - fb[idx]) ** 2) - np.sum((y[idx] - ff[idx]) ** 2)) / s_)
        dA.append(auc_(tail[idx], ff[idx]) - auc_(tail[idx], fb[idx]))
    qa = (1 - level) / 2
    return {"n_train": len(A), "n_test": len(Bt), "n_symbols": len(syms), "n_test_dates": len(ud),
            "r2_base": 1 - np.sum((y - fb) ** 2) / sst, "r2_full": 1 - np.sum((y - ff) ** 2) / sst,
            "delta_r2": (np.sum((y - fb) ** 2) - np.sum((y - ff) ** 2)) / sst,
            "delta_r2_ci": [float(np.nanquantile(dR2, qa)), float(np.nanquantile(dR2, 1 - qa))],
            "auc_base": auc_(tail, fb), "auc_full": auc_(tail, ff),
            "clark_west_t": t_, "clark_west_p": p_, "ci_level": level,
            "coef_candidates_train": {c: float(bf[len(ctrl) + 1 + i]) for i, c in enumerate(cands)}}


# ---- liquidation proxy (addendum) ---------------------------------------------------------------
def liq_series(df):
    """Per-minute array: OI destroyed ($M) at 5-minute marks with an unusually large move, else 0."""
    p = np.log(df["close"].to_numpy()) * 1e4
    oi = df["oi"].to_numpy()
    marks = np.where(np.isfinite(oi))[0]
    out = np.zeros(len(df))
    if len(marks) < 80:
        return out, False
    r5 = np.diff(p[marks]); doi = np.diff(oi[marks])
    for j in range(72, len(r5)):
        sd = np.std(r5[j - 72:j])
        if sd > 0 and abs(r5[j]) > 2 * sd and doi[j] < 0:
            out[marks[j + 1]] = -doi[j]
    return out, True


def day_blocks_e2(df, s, d, flow_scale):
    """Part 6 day_blocks6 (Paper 2 features, without the class-tag columns) plus the LIQ proxy."""
    p, u, dd_, x, tot = prep(df, flow_scale)
    oi = df["oi"].ffill().to_numpy(); vol = df["vol"].to_numpy(); dp = np.diff(p, prepend=np.nan)
    liq, liq_ok = liq_series(df)
    rows = []
    for hr in range(6, 24):
        t = hr * 60
        w, h, f = slice(t - 360, t), slice(t - 60, t), slice(t, min(t + 61, 1440))
        est = fit_t6(p[w], u[w], dd_[w], x[w])
        row = {"symbol": s, "date": d, "hour": hr}
        if est is not None:
            row.update({"C3_hat": est["C3"], "kappa_hat": est["kappa"], "a_hat": est["a"]})
        uu, yy = u[w][1:], dp[w][1:]; okk = np.isfinite(uu) & np.isfinite(yy)
        kl = float(np.polyfit(uu[okk], yy[okk], 1)[0]) if okk.sum() > 60 and np.std(uu[okk]) > 0 else np.nan
        v60 = np.nansum(vol[h])
        oi0 = oi[t - 1]
        row.update({
            "rv_60": np.nanstd(np.diff(p[h])), "rv_360": np.nanstd(np.diff(p[w])), "abs_ret_60": abs(p[t - 1] - p[t - 60]),
            "flow_imb_60": np.nansum(u[h]) / (np.nansum(np.abs(u[h])) + 1e-12), "log_vol_60": np.log1p(v60),
            "log_depth1": np.log(tot[t - 1]) if np.isfinite(tot[t - 1]) and tot[t - 1] > 0 else np.nan,
            "imbalance": dd_[t - 1],
            "oi_chg_60": (oi[t - 1] / oi[t - 60] - 1) * 100 if np.isfinite(oi[t - 60]) and oi[t - 60] > 0 else np.nan,
            "kyle_lam": kl,
            "amihud_60": np.log(abs(p[t - 1] - p[t - 60]) / v60 + 1e-9) if v60 > 0 and np.isfinite(p[t - 60]) else np.nan,
            "MAE_60": float(np.nanmax(np.abs(p[f] - p[t - 1]))),
            "LIQ_next": float(np.log1p(100 * liq[t:t + 60].sum() / oi0)) if liq_ok and np.isfinite(oi0) and oi0 > 0 and t + 60 <= 1440 else np.nan,
            "LIQ_lag": float(np.log1p(100 * liq[t - 60:t].sum() / oi0)) if liq_ok and np.isfinite(oi0) and oi0 > 0 else np.nan})
        rows.append(row)
    return rows


def mediation(sub, ctrl, B=2000, seed=99):
    """C3's out-of-sample gain on MAE_60 without and with realized LIQ_next, on the same test rows."""
    A0 = sub[sub["split"] == "train"].copy(); B0 = sub[sub["split"] == "test"].copy()
    lo, hi = A0["C3_hat"].quantile([0.01, 0.99]); A0["C3_w"] = A0["C3_hat"].clip(lo, hi); B0["C3_w"] = B0["C3_hat"].clip(lo, hi)
    need = ctrl + ["C3_w", "LIQ_next", "MAE_60"]
    A = A0.dropna(subset=need); Bt = B0.dropna(subset=need)
    Bt = Bt[Bt["symbol"].isin(set(A["symbol"]))].sort_values(["date", "symbol", "hour"])
    if len(A) < 200 or len(Bt) < 200:
        return {"skipped": "too few blocks", "n_train": len(A), "n_test": len(Bt)}
    syms = sorted(A["symbol"].unique()); y = Bt["MAE_60"].to_numpy(); ytr = A["MAE_60"].to_numpy()
    fit = lambda cols: np.linalg.lstsq(design(A, cols, syms), ytr, rcond=None)[0]
    pred = lambda cols, b: design(Bt, cols, syms) @ b
    f0 = pred(ctrl, fit(ctrl)); f1 = pred(ctrl + ["C3_w"], fit(ctrl + ["C3_w"]))
    g0 = pred(ctrl + ["LIQ_next"], fit(ctrl + ["LIQ_next"])); g1 = pred(ctrl + ["LIQ_next", "C3_w"], fit(ctrl + ["LIQ_next", "C3_w"]))
    ybar = ytr.mean()

    def stats_(idx):
        sst = np.sum((y[idx] - ybar) ** 2)
        gain = (np.sum((y[idx] - f0[idx]) ** 2) - np.sum((y[idx] - f1[idx]) ** 2)) / sst
        gain_liq = (np.sum((y[idx] - g0[idx]) ** 2) - np.sum((y[idx] - g1[idx]) ** 2)) / sst
        return gain, gain_liq, (1 - gain_liq / gain) if gain != 0 else np.nan
    all_idx = np.arange(len(y))
    gain, gain_liq, share = stats_(all_idx)
    Rb = rng(seed); dd = Bt["date"].to_numpy(); ud = np.unique(dd); pos = {d: np.where(dd == d)[0] for d in ud}
    bs = np.array([stats_(np.concatenate([pos[d] for d in Rb.choice(ud, len(ud))])) for _ in range(B)])
    q = lambda v: [float(np.nanquantile(v, .025)), float(np.nanquantile(v, .975))]
    return {"n_train": len(A), "n_test": len(Bt), "n_test_dates": len(ud), "gain": gain, "gain_ci": q(bs[:, 0]),
            "gain_with_liq": gain_liq, "gain_with_liq_ci": q(bs[:, 1]), "share": share, "share_ci": q(bs[:, 2]),
            "p_share_le_0": float(np.mean(~(bs[:, 2] > 0)))}


def holm(p):
    order = np.argsort(p); m = len(p); adj = np.empty(m); run = 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (m - k) * p[i])); adj[i] = run
    return adj.tolist()


def evaluate(ZB):
    ctrl = CTRL + IMPACT
    p1 = evaluate_g(ZB, "LIQ_next", "C3_hat", ctrl + ["LIQ_lag"])
    med = mediation(ZB, ctrl)
    p_raw = [p1.get("clark_west_p", np.nan), med.get("p_share_le_0", np.nan)]
    adj = holm([x if np.isfinite(x) else 1.0 for x in p_raw])
    p1_pass = bool(np.isfinite(p_raw[0]) and adj[0] < 0.05 and p1["delta_r2_ci"][0] > 0)
    evaluable = bool("gain_ci" in med and med["gain_ci"][0] > 0)
    p2_pass = bool(evaluable and med["share"] >= 0.5 and med["share_ci"][0] > 0 and adj[1] < 0.05)
    return {"P1": p1, "P2_mediation": med, "p_raw": p_raw, "p_holm": adj, "P1_pass": p1_pass,
            "P2_evaluable": evaluable, "P2_pass": p2_pass}


def gate(today=None):
    spec_sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert spec_sha == SPEC.with_suffix(".sha256").read_text().strip(), "original specification changed"
    add = json.loads(ADD.read_text())
    add_sha = hashlib.sha256(ADD.read_bytes()).hexdigest()
    assert add_sha == ADD.with_suffix(".sha256").read_text().strip(), "addendum hash mismatch"
    for key, path in (("analysis_sha256", HERE / "e2_analysis.py"), ("binance_vision_sha256", HERE / "binance_vision.py")):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == add[key], f"{path.name} changed after registration"
    today = today or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    assert today >= EARLIEST_RUN, f"E2 opens on or after {EARLIEST_RUN}; the prospective window ends {END}"
    assert json.loads(COUNTER.read_text())["opens"] == 0, "E2 was already opened"
    rel = str(ADD.relative_to(ROOT))
    commit = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", rel], cwd=ROOT, text=True).strip()
    assert commit, "addendum not committed"
    return spec_sha, add_sha, commit


def build_blocks(syms, ds, cache_dir, threads):
    jobs = [(s, d) for s in syms for d in ds]
    panel, status = {}, []
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(bv.get_day, s, d, cache_dir, True): (s, d) for s, d in jobs}
        for i, f in enumerate(as_completed(futs)):
            s, d = futs[f]
            df, st = f.result(); status.append(st)
            if df is not None and st.get("depth_day_ok"):
                panel[(s, d)] = df
            if (i + 1) % 300 == 0:
                print(f"  {i + 1}/{len(jobs)} symbol-days", flush=True)
    train = set(ds[:N_TRAIN])
    scale = {}
    for s in syms:
        v = [np.nanmedian(np.abs(panel[(s, d)]["flow"].to_numpy())) for d in ds if d in train and (s, d) in panel]
        scale[s] = float(np.nanmedian(v)) if v and np.nanmedian(v) > 0 else 1.0
    rows = []
    for (s, d), df in sorted(panel.items()):
        rows += day_blocks_e2(df, s, d, scale[s])
    ZB = pd.DataFrame(rows)
    ZB["split"] = np.where(ZB["date"].isin(train), "train", "test")
    ZB["kappa_sq"] = ZB["kappa_hat"] ** 2
    ZB = winsor_train(ZB, IMPACT)
    return ZB, status, scale


def numbers_tex(ev):
    f = lambda x: f"{100 * x:.2f}" if x is not None and np.isfinite(x) else "n/a"
    p1, m = ev["P1"], ev["P2_mediation"]
    L = ["% generated by e2_analysis.py; do not edit",
         f"\\newcommand{{\\EtwoPoneVerdict}}{{{'passed' if ev['P1_pass'] else 'failed'}}}",
         f"\\newcommand{{\\EtwoPtwoVerdict}}{{{'passed' if ev['P2_pass'] else 'failed'}}}",
         f"\\newcommand{{\\EtwoPoneDeltaRtwo}}{{{f(p1.get('delta_r2'))}}}",
         f"\\newcommand{{\\EtwoShare}}{{{f(m.get('share'))}}}"]
    return "\n".join(L) + "\n"


def run(cache_dir=None, threads=12):
    spec_sha, add_sha, commit = gate()
    COUNTER.write_text(json.dumps({"opens": 1, "spec_sha256": spec_sha, "addendum_sha256": add_sha,
                                   "addendum_commit": commit, "opened_utc": datetime.now(timezone.utc).isoformat()},
                                  indent=2) + "\n")
    ZB, status, scale = build_blocks(SYMBOLS, dates(), cache_dir, threads)
    ev = evaluate(ZB)
    res = {"test": "E2", "spec_sha256": spec_sha, "addendum_sha256": add_sha, "addendum_commit": commit,
           "run_utc": datetime.now(timezone.utc).isoformat(), "dates": dates(), "symbols": SYMBOLS,
           "flow_scale": scale, "blocks": {"train": int((ZB["split"] == "train").sum()), "test": int((ZB["split"] == "test").sum())},
           "valid_symbol_days": int(sum(bool(s.get("depth_day_ok")) for s in status)), "evaluation": ev}
    RESULT.write_text(json.dumps(res, indent=1, default=float) + "\n")
    NUMBERS.write_text(numbers_tex(ev))
    DLLOG.write_text(json.dumps(bv.DL_LOG, indent=0) + "\n")
    print(json.dumps(ev, indent=1, default=float))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--cache", default=None)
    ap.add_argument("--threads", type=int, default=12)
    a = ap.parse_args()
    if a.run:
        run(a.cache, a.threads)
