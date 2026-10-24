"""EXPLORATORY pilot after Tests E1v2 and D1 (not a registered test; nothing here is confirmatory evidence).

E1v2 and D1 are opened and reported as they came out. Their downloaded days (30 Binance USD-M perpetuals,
105 + 58 dates) are spent for confirmation, so they can be explored freely. This pilot asks which designs the
data can decide, so that the next confirmatory test (on symbols never used) is fixed before its data are seen:

  A. Margin certification. Theory (Paper 2, Theorem sum): the economy is safe iff a + kappa*Phi < 1, so the
     decision a guard needs is the sign of the margin M = 1 - a - kappa*Phi, not the relative precision of Phi.
     Five-minute marks, pooled over days with day-demeaning:
        price:  ret_t  = kappa * flow_t + beta * x_{t-1}        (a = 1 + beta)
        kernel: flow_t = sum_{m=1..12} k_m z_{t-m}, Phi = sum k_m, z = x (displacement) or ret
     x = p - EWMA(p, span s), s in (6, 12, 24) five-minute bars. Day-bootstrap 95% interval for M; the margin is
     DECIDED if the interval excludes zero. Diagnostic: the same decision with kappa*Phi removed, to see whether a
     decision rests on the feedback term or only on mean reversion.
  B. Identification without the 0-0.99 ceiling. Two exponentials fitted to the kernel (E1v2 code); memories are
     IDENTIFIED only if the Delta r interval excludes zero and neither rate interval touches the bounds.
  C. Decision curves: decided / identified at 10, 20, 40, 80 and all days (random nested subsamples).
  D. Stationarity of class memory (for D2): top-position rate per calendar quarter, heterogeneity chi-square;
     tagged-width slopes within quarters versus across the whole period (random and chronological order).

All OLS steps use per-day sufficient statistics, so a bootstrap draw is a sum over drawn days.

Usage (Colab):  pilot_after_e1v2.run([DRIVE/'E1v2_cache', DRIVE/'D1_cache'], out_json)
Local test:     python pilot_after_e1v2.py --selftest
"""
import argparse
import json
import math
import os
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats

SYMBOLS = ("ACHUSDT ALICEUSDT API3USDT ARPAUSDT CELRUSDT CHRUSDT CVXUSDT GTCUSDT HOTUSDT ICXUSDT "
           "IOSTUSDT IOTXUSDT LITUSDT OGNUSDT QNTUSDT RLCUSDT SPELLUSDT TUSDT WOOUSDT ZENUSDT "
           "DASHUSDT IMXUSDT IOTAUSDT NEOUSDT ONEUSDT ROSEUSDT STGUSDT VETUSDT XMRUSDT ZRXUSDT").split()
CLASSES = {"top_position": "top_pos_ratio", "top_account": "top_acc_ratio", "all_accounts": "acc_ratio"}
L = 12
SPANS = (6, 12, 24)
B = 200
SEED = 20261024
BOUND_LO, BOUND_HI = 0.005, 0.985
CURVE_N = (10, 20, 40, 80)


# ---------------------------------------------------------------------------------------------------
# per-day series and sufficient statistics
def day_series(df):
    """Five-minute marks of one day (E1v2 alignment): ret (bp), flow ($M), class positions n_c."""
    p = np.log(df["close"].to_numpy(float)) * 1e4
    fl = np.nan_to_num(df["flow"].to_numpy(float))
    cf = np.concatenate([[0.0], np.cumsum(fl)])
    m = np.arange(5, 1440, 5)
    out = {"p": p[m], "ret": p[m] - p[m - 5], "flow": cf[m + 1] - cf[m - 4]}
    for c, col in CLASSES.items():
        R = df[col].to_numpy(float)[m] if col in df else np.full(len(m), np.nan)
        out[c] = (R - 1) / (R + 1)
    out["n_class_marks"] = int(np.isfinite(out["top_position"]).sum())
    return out


def ss(X, y):
    """Day-demeaned sufficient statistics (XtX, Xty, n) of y on X, rows with all values finite."""
    ok = np.all(np.isfinite(X), 1) & np.isfinite(y)
    if ok.sum() < X.shape[1] + 10:
        return None
    Xo, yo = X[ok] - X[ok].mean(0), y[ok] - y[ok].mean()
    return Xo.T @ Xo, Xo.T @ yo, int(ok.sum())


def lags(z, n):
    return np.column_stack([np.r_[np.full(k, np.nan), z[:-k]] for k in range(1, n + 1)])


def day_stats(s):
    """All per-day sufficient statistics used by the pilot."""
    out = {}
    ret, flow, p = s["ret"], s["flow"], s["p"]
    out["k_ret"] = ss(lags(ret, L), flow)
    for span in SPANS:
        ew = pd.Series(p).ewm(span=span, adjust=False).mean().to_numpy()
        x = p - ew
        x[:span] = np.nan                                        # EWMA warm-up
        xl = np.r_[np.nan, x[:-1]]
        out[f"price_{span}"] = ss(np.column_stack([flow, xl]), ret)
        out[f"k_x_{span}"] = ss(lags(x, L), flow)
    for c in CLASSES:
        n = s[c]
        out[f"tag_{c}"] = ss(np.column_stack([np.r_[np.nan, n[:-1]], ret]), n)
    return out


def stack(days):
    """Stack per-day sufficient statistics: name -> (A[d,p,p], b[d,p]); a missing day contributes zero."""
    names = days[0].keys(); out = {}
    for k in names:
        p = next((d[k][0].shape[0] for d in days if d[k] is not None), None)
        if p is None:
            continue
        A = np.zeros((len(days), p, p)); b = np.zeros((len(days), p))
        for i, d in enumerate(days):
            if d[k] is not None:
                A[i], b[i] = d[k][0], d[k][1]
        out[k] = (A, b)
    return out


def solve_w(S, name, W):
    """Pooled OLS for every row of the day-weight matrix W (draws x days): array (draws, p)."""
    if name not in S:
        return None
    A = np.einsum("bd,dij->bij", W, S[name][0]); b = W @ S[name][1]
    try:
        return np.linalg.solve(A, b[..., None])[..., 0]
    except np.linalg.LinAlgError:
        return (np.linalg.pinv(A) @ b[..., None])[..., 0]


def exp_fit(k):
    """Two exponentials fitted to a 12-tap kernel (E1v2 kernel_fit, same bounds and starts)."""
    m = np.arange(len(k))

    def resid(th):
        w1, r1, w2, r2 = th
        return w1 * r1 ** m + w2 * r2 ** m - k

    def jac(th):                                                 # analytic Jacobian (speed only)
        w1, r1, w2, r2 = th
        d1 = np.where(m > 0, m * np.power(max(r1, 1e-300), np.maximum(m - 1, 0)), 0.0)
        d2 = np.where(m > 0, m * np.power(max(r2, 1e-300), np.maximum(m - 1, 0)), 0.0)
        return np.column_stack([r1 ** m, w1 * d1, r2 ** m, w2 * d2])
    best = None
    for r1, r2 in [(0.2, 0.8), (0.1, 0.6), (0.4, 0.95), (0.05, 0.3)]:
        try:
            sol = optimize.least_squares(resid, [k[0] / 2, r1, k[0] / 2, r2], jac=jac,
                                         bounds=([-np.inf, 0, -np.inf, 0], [np.inf, 0.99, np.inf, 0.99]))
            if best is None or sol.cost < best.cost:
                best = sol
        except Exception:
            pass
    if best is None or not np.all(np.isfinite(k)):
        return np.nan, np.nan
    w1, r1, w2, r2 = best.x
    return (r1, r2) if r1 <= r2 else (r2, r1)


def ci(v):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return [float(np.quantile(v, .025)), float(np.quantile(v, .975))] if len(v) > 20 else [np.nan, np.nan]


def excludes_zero(c):
    return bool(np.isfinite(c[0]) and (c[0] > 0 or c[1] < 0))


# ---------------------------------------------------------------------------------------------------
# one symbol: estimates for a matrix of day weights (row 0 of a point estimate is all ones)
def estimates(S, W, with_id=False):
    out = {}
    kr = solve_w(S, "k_ret", W)
    out["Phi_ret"] = kr.sum(1)
    for span in SPANS:
        pr = solve_w(S, f"price_{span}", W); kx = solve_w(S, f"k_x_{span}", W)
        kappa, beta = pr[:, 0], pr[:, 1]
        out[f"kappa_{span}"], out[f"beta_{span}"], out[f"Phi_x_{span}"] = kappa, beta, kx.sum(1)
        out[f"M_x_{span}"] = -beta - kappa * kx.sum(1)
        out[f"M_ret_{span}"] = -beta - kappa * out["Phi_ret"]
        out[f"M_nofb_{span}"] = -beta
    for c in CLASSES:
        t = solve_w(S, f"tag_{c}", W)
        out[f"r_{c}"] = t[:, 0] if t is not None else np.full(W.shape[0], np.nan)
    if with_id:
        rr = np.array([exp_fit(k) for k in kr])
        out["r_fast"], out["r_slow"] = rr[:, 0], rr[:, 1]
    return pd.DataFrame(out)


def boot_weights(n, rng, nb):
    return np.stack([np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(nb)]).astype(float)


def decisions(point, bt):
    out = {}
    for span in SPANS:
        for kind in ("x", "ret", "nofb"):
            key = f"M_{kind}_{span}"
            c = ci(bt[key])
            out[key] = {"point": float(point[key]), "ci": c, "decided": excludes_zero(c),
                        "sign": "safe" if c[0] > 0 else "unsafe" if c[1] < 0 else "undecided"}
        for comp in (f"kappa_{span}", f"beta_{span}", f"Phi_x_{span}"):
            out[comp] = {"point": float(point[comp]), "ci": ci(bt[comp])}
    out["Phi_ret"] = {"point": float(point["Phi_ret"]), "ci": ci(bt["Phi_ret"])}
    if "r_fast" in bt:
        rf, rs = ci(bt["r_fast"]), ci(bt["r_slow"]); dr = ci(bt["r_slow"] - bt["r_fast"])
        inside = all(np.isfinite(v) and BOUND_LO < v < BOUND_HI for v in rf + rs)
        out["identification"] = {"r_fast_ci": rf, "r_slow_ci": rs, "delta_r_ci": dr,
                                 "dr_excludes_zero": excludes_zero(dr), "inside_bounds": inside,
                                 "identified": bool(excludes_zero(dr) and inside),
                                 "saturated": bool(any(np.isfinite(v) and (v <= BOUND_LO or v >= BOUND_HI) for v in rf + rs))}
    tag_w = [np.diff(ci(bt[f"r_{c}"]))[0] for c in CLASSES]
    out["tag_width"] = float(np.nanmean(tag_w))
    return out


def tag_width(S, idx, rng, nb=100):
    """Mean width of the three class-tagged rate intervals on the days idx (day bootstrap)."""
    n = len(idx); W = np.zeros((nb, len(next(iter(S.values()))[1])))
    W[:, idx] = boot_weights(n, rng, nb)
    ws = []
    for c in CLASSES:
        t = solve_w(S, f"tag_{c}", W)
        ws.append(np.diff(ci(t[:, 0]))[0] if t is not None else np.nan)
    return float(np.nanmean(ws))


def slope(ns, ws):
    ns, ws = np.asarray(ns, float), np.asarray(ws, float)
    ok = np.isfinite(ws) & (ws > 0)
    return float(np.polyfit(np.log(ns[ok]), np.log(ws[ok]), 1)[0]) if ok.sum() >= 3 else np.nan


def run_on(S, idx, rng, nb):
    nd = len(next(iter(S.values()))[1])
    P = np.zeros((1, nd)); P[0, idx] = 1
    W = np.zeros((nb, nd)); W[:, idx] = boot_weights(len(idx), rng, nb)
    return decisions(estimates(S, P).iloc[0], estimates(S, W, with_id=True))


def symbol_pilot(dated, j):
    """dated: list of (date, stats) sorted by date."""
    rng = np.random.default_rng(SEED + 101 * j)
    days = [s for _, s in dated]; n = len(days); S = stack(days)
    res = {"n_days": n, "full": run_on(S, np.arange(n), rng, B)}
    # C: decision curves on random nested subsamples
    order = rng.permutation(n); curve = {}
    for m in [k for k in CURVE_N if k < n] + [n]:
        d = run_on(S, order[:m], rng, 150)
        curve[str(m)] = {"M_x_12_decided": d["M_x_12"]["decided"], "M_ret_12_decided": d["M_ret_12"]["decided"],
                         "identified": d["identification"]["identified"], "tag_width": d["tag_width"]}
    res["curve"] = curve
    # D: stationarity of the top-position memory across quarters
    q = {}
    for i, (date, _) in enumerate(dated):
        q.setdefault(pd.Timestamp(date).to_period("Q").strftime("%YQ%q"), []).append(i)
    qs = {}
    for k, v in sorted(q.items()):
        if len(v) < 8:
            continue
        P = np.zeros((1, n)); P[0, v] = 1
        W = np.zeros((100, n)); W[:, v] = boot_weights(len(v), rng, 100)
        est, bt = solve_w(S, "tag_top_position", P), solve_w(S, "tag_top_position", W)
        if est is None:
            continue
        qs[k] = {"r": float(est[0, 0]), "se": float(np.nanstd(bt[:, 0])), "n": len(v)}
    if len(qs) >= 3:
        r = np.array([v["r"] for v in qs.values()]); se = np.array([v["se"] for v in qs.values()])
        w = 1 / np.maximum(se, 1e-6) ** 2; rbar = np.sum(w * r) / np.sum(w)
        Q = float(np.sum(w * (r - rbar) ** 2))
        res["stationarity"] = {"quarters": qs, "Q": Q, "df": len(qs) - 1, "p": float(stats.chi2.sf(Q, len(qs) - 1)),
                               "range": float(r.max() - r.min())}
    # D: slopes of the tagged width within quarters and across the period
    within = []
    for k, v in q.items():
        if len(v) < 16:
            continue
        o = rng.permutation(v); ns = [6, 12, len(v)]
        within.append(slope(ns, [tag_width(S, o[:m], rng) for m in ns]))
    ns = [m for m in (14, 28, 56, 112) if m < n] + [n]
    res["slopes"] = {"within_quarter_mean": float(np.nanmean(within)) if within else np.nan,
                     "within_quarter_n": len(within),
                     "across_random": slope(ns, [tag_width(S, order[:m], rng) for m in ns]),
                     "across_chronological": slope(ns, [tag_width(S, np.arange(m), rng) for m in ns])}
    return res


# ---------------------------------------------------------------------------------------------------
def load_days(cache_dirs, sym):
    dated = {}
    for cd in cache_dirs:
        d_ = Path(cd) / sym
        if not d_.exists():
            continue
        for f in sorted(d_.glob("*_nodepth.pkl")):
            date = f.name.split("_")[0]
            try:
                obj = pd.read_pickle(f)
            except Exception:
                continue
            df = obj[0] if isinstance(obj, tuple) else obj
            if df is None:
                continue
            s = day_series(df)
            if s["n_class_marks"] < 100:
                continue
            dated[date] = day_stats(s)
    return sorted(dated.items())


def summarize(per):
    ev = {s: v for s, v in per.items() if v.get("n_days", 0) >= 30}
    n = len(ev); out = {"n_symbols": n}
    for span in SPANS:
        for kind in ("x", "ret", "nofb"):
            key = f"M_{kind}_{span}"
            dec = [v["full"][key]["decided"] for v in ev.values() if key in v["full"]]
            safe = [v["full"][key]["sign"] == "safe" for v in ev.values() if key in v["full"]]
            out[f"decided_{key}"] = int(sum(dec)); out[f"safe_{key}"] = int(sum(safe))
    ids = [v["full"].get("identification", {}) for v in ev.values()]
    out["identified"] = int(sum(i.get("identified", False) for i in ids))
    out["dr_excludes_zero"] = int(sum(i.get("dr_excludes_zero", False) for i in ids))
    out["saturated"] = int(sum(i.get("saturated", False) for i in ids))
    out["curve"] = {}
    for m in [str(k) for k in CURVE_N] + ["all"]:
        rows = [v["curve"].get(m) if m != "all" else v["curve"][max(v["curve"], key=int)] for v in ev.values()]
        rows = [r for r in rows if r]
        out["curve"][m] = {"n": len(rows),
                           "M_x_12_decided": int(sum(bool(r["M_x_12_decided"]) for r in rows)),
                           "M_ret_12_decided": int(sum(bool(r["M_ret_12_decided"]) for r in rows)),
                           "identified": int(sum(bool(r["identified"]) for r in rows))}
    st = [v["stationarity"] for v in ev.values() if "stationarity" in v]
    out["stationarity_p_below_05"] = int(sum(s["p"] < 0.05 for s in st)); out["stationarity_n"] = len(st)
    sl = pd.DataFrame([v["slopes"] for v in ev.values()])
    out["median_slopes"] = {c: float(sl[c].median()) for c in ("within_quarter_mean", "across_random", "across_chronological")}
    out["within_slope_in_P1_range"] = int(((sl["within_quarter_mean"] >= -0.75) & (sl["within_quarter_mean"] <= -0.25)).sum())
    out["across_slope_in_P1_range"] = int(((sl["across_random"] >= -0.75) & (sl["across_random"] <= -0.25)).sum())
    return out


def _one(args):
    cache_dirs, s, j, part_dir = args
    part = Path(part_dir) / f"{s}.json" if part_dir else None
    if part is not None and part.exists():
        return s, json.loads(part.read_text())
    dated = load_days(cache_dirs, s)
    if len(dated) < 30:
        r = {"n_days": len(dated), "excluded": "fewer than 30 valid days"}
    else:
        r = symbol_pilot(dated, j)
    if part is not None:
        part.write_text(json.dumps(r, default=lambda o: None if o is None else float(o)))
    return s, json.loads(json.dumps(r, default=lambda o: None if o is None else float(o)))


def run(cache_dirs, out_json, symbols=SYMBOLS, part_dir=None, workers=None):
    """part_dir: per-symbol results are saved there, so an interrupted run resumes where it stopped."""
    from concurrent.futures import ProcessPoolExecutor
    if part_dir:
        Path(part_dir).mkdir(parents=True, exist_ok=True)
    jobs = [(list(map(str, cache_dirs)), s, j, str(part_dir) if part_dir else None) for j, s in enumerate(symbols)]
    per = {}
    with ProcessPoolExecutor(max_workers=workers or os.cpu_count()) as ex:
        for s, r in ex.map(_one, jobs):
            per[s] = r
            if "full" in r:
                f = r["full"]
                print(f"  {s}: days={r['n_days']} margin(x,12)={f['M_x_12']['sign']} margin(ret,12)={f['M_ret_12']['sign']} "
                      f"no-feedback={f['M_nofb_12']['sign']} identified={f['identification']['identified']} "
                      f"saturated={f['identification']['saturated']}", flush=True)
            else:
                print(f"  {s}: {r['n_days']} days, excluded", flush=True)
    per = {s: per[s] for s in symbols}
    res = {"kind": "EXPLORATORY pilot after E1v2 and D1; not a registered test", "run_utc": datetime.now(timezone.utc).isoformat(),
           "cache_dirs": [str(c) for c in cache_dirs], "per_symbol": per, "summary": summarize(per)}
    Path(out_json).write_text(json.dumps(res, indent=1, default=lambda o: None if o is None else float(o)) + "\n")
    print(json.dumps(res["summary"], indent=1))
    return res


# ---------------------------------------------------------------------------------------------------
def _fake_day(rng, kappa=0.8, a=0.9, mom=0.05, mem=0.7, scale=1.0):
    """Synthetic minute frame with the cache's columns, for the self-test only."""
    T = 1440; x = 0.0; f_state = 0.0; p = [0.0]; flow = []
    for t in range(T):
        f_state = mem * f_state + (1 - mem) * mom * x
        u = f_state + rng.normal(0, 0.3)
        eff = rng.normal(0, 2.0)
        x = a * x + kappa * u
        p.append(p[-1] + eff + (x - (p[-1] - p[0] if False else 0)) * 0 + kappa * u)
        flow.append(u * scale)
    p = np.array(p[1:]); close = 100 * np.exp(p / 1e4)
    ratio = np.full(T, np.nan); idx = np.arange(0, T, 5)
    pos = np.tanh(pd.Series(np.diff(p, prepend=0)).ewm(alpha=0.2).mean().to_numpy() / 3)
    ratio[idx] = (1 + 0.3 * pos[idx] + rng.normal(0, 0.01, len(idx))) / (1 - 0.3 * pos[idx] + rng.normal(0, 0.01, len(idx)))
    df = pd.DataFrame({"close": close, "flow": flow, "vol": np.abs(flow),
                       "top_pos_ratio": ratio, "top_acc_ratio": ratio * 1.01, "acc_ratio": ratio * 0.99})
    return df


def selftest():
    import tempfile
    rng = np.random.default_rng(1)
    with tempfile.TemporaryDirectory() as td:
        for s in SYMBOLS[:3]:
            os.makedirs(f"{td}/{s}")
            for d in pd.date_range("2025-01-01", periods=160, freq="4D"):
                pd.to_pickle((_fake_day(rng), {}), f"{td}/{s}/{d:%Y-%m-%d}_nodepth.pkl")
        r = run([td], f"{td}/pilot.json", symbols=SYMBOLS[:3], part_dir=f"{td}/parts")
        r2 = run([td], f"{td}/pilot2.json", symbols=SYMBOLS[:3], part_dir=f"{td}/parts")
        assert r2["summary"] == r["summary"]
        assert r["summary"]["n_symbols"] == 3
        json.loads(Path(f"{td}/pilot.json").read_text())
    print("selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
