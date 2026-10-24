"""EXPLORATORY Pilot 3: a horizon-matched comparison of price-only and class-tagged memories (not a registered test).

Why. The mock referee report's main point: Paper 1 and Test E1v2 compare price-only memory rates, fitted to a one-hour
kernel (12 five-minute lags) on [0, 0.99], with class-tagged rates near 0.99 per five minutes (half-lives of hours). A
one-hour kernel cannot see memories of that length, and a width ratio between an interval that fills the admissible range
and one that does not is not a ratio of precisions. This pilot asks whether the disclosure result survives a fair
comparison: kernels long enough to see the tagged memories, and both estimates in the same unit (half-life, in hours).

Per symbol (E1v2 and D1 caches, spent days; day bootstrap, 200 draws):
    price-only: five-minute flow on L lagged five-minute returns, L in {12, 48, 96} (1, 4 and 8 hours; separate days cannot be chained, so 8 hours is about the longest kernel a day supports), two exponentials
                fitted with rates in [0, 0.9995]; slow half-life h_slow = 5 ln(1/2) / ln(r_slow) minutes
    tagged:     n_{c,t} = r_c n_{c,t-1} + w_c ret_t for the three classes (E1v2); half-life of each class
Readings: the width of the 95% interval of log10 half-life for the price-only slow memory at each L, against the mean width
for the tagged classes; whether the price-only interval reaches a bound of the fit; whether the price-only slow half-life
interval overlaps the tagged half-lives.
"""
import json
import os
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize

SYMBOLS = ("ACHUSDT ALICEUSDT API3USDT ARPAUSDT CELRUSDT CHRUSDT CVXUSDT GTCUSDT HOTUSDT ICXUSDT "
           "IOSTUSDT IOTXUSDT LITUSDT OGNUSDT QNTUSDT RLCUSDT SPELLUSDT TUSDT WOOUSDT ZENUSDT "
           "DASHUSDT IMXUSDT IOTAUSDT NEOUSDT ONEUSDT ROSEUSDT STGUSDT VETUSDT XMRUSDT ZRXUSDT").split()
CLASSES = {"top_position": "top_pos_ratio", "top_account": "top_acc_ratio", "all_accounts": "acc_ratio"}
LS = (12, 48, 96)
RHI, BLO, BHI = 0.9995, 0.005, 0.999
B = 200
SEED = 20261027


def lags(z, n):
    return np.column_stack([np.r_[np.full(k, np.nan), z[:-k]] for k in range(1, n + 1)])


def ss(X, y):
    ok = np.all(np.isfinite(X), 1) & np.isfinite(y)
    if ok.sum() < X.shape[1] + 10:
        return None
    Xo, yo = X[ok] - X[ok].mean(0), y[ok] - y[ok].mean()
    return Xo.T @ Xo, Xo.T @ yo


def day_stats(df):
    p1 = np.log(df["close"].to_numpy(float)) * 1e4
    fl = np.nan_to_num(df["flow"].to_numpy(float)); cf = np.concatenate([[0.0], np.cumsum(fl)])
    m = np.arange(5, 1440, 5)
    ret, flow = p1[m] - p1[m - 5], cf[m + 1] - cf[m - 4]
    out = {f"k{L}": ss(lags(ret, L), flow) for L in LS}
    for c, col in CLASSES.items():
        R = df[col].to_numpy(float)[m] if col in df else np.full(len(m), np.nan)
        n = (R - 1) / (R + 1)
        out[f"tag_{c}"] = ss(np.column_stack([np.r_[np.nan, n[:-1]], ret]), n)
    if int(np.isfinite(df["top_pos_ratio"].to_numpy(float)[m]).sum()) < 100:
        return None
    return out


def stack(days):
    out = {}
    for k in days[0]:
        first = next((d[k] for d in days if d[k] is not None), None)
        if first is None:
            continue
        A = np.zeros((len(days),) + first[0].shape); b = np.zeros((len(days),) + first[1].shape)
        for i, d in enumerate(days):
            if d[k] is not None:
                A[i], b[i] = d[k]
        out[k] = (A, b)
    return out


def solve_w(S, name, W):
    A = np.einsum("bd,dij->bij", W, S[name][0]); b = W @ S[name][1]
    try:
        return np.linalg.solve(A, b[..., None])[..., 0]
    except np.linalg.LinAlgError:
        return (np.linalg.pinv(A) @ b[..., None])[..., 0]


def exp_fit(k):
    m = np.arange(len(k))

    def resid(th):
        w1, r1, w2, r2 = th
        return w1 * r1 ** m + w2 * r2 ** m - k

    def jac(th):
        w1, r1, w2, r2 = th
        d1 = np.where(m > 0, m * np.power(max(r1, 1e-300), np.maximum(m - 1, 0)), 0.0)
        d2 = np.where(m > 0, m * np.power(max(r2, 1e-300), np.maximum(m - 1, 0)), 0.0)
        return np.column_stack([r1 ** m, w1 * d1, r2 ** m, w2 * d2])
    if not np.all(np.isfinite(k)):
        return np.nan, np.nan
    best = None
    for r1, r2 in [(0.2, 0.8), (0.4, 0.95), (0.6, 0.99), (0.1, 0.998)]:
        try:
            sol = optimize.least_squares(resid, [k[0] / 2, r1, k[0] / 2, r2], jac=jac,
                                         bounds=([-np.inf, 0, -np.inf, 0], [np.inf, RHI, np.inf, RHI]))
            if best is None or sol.cost < best.cost:
                best = sol
        except Exception:
            pass
    if best is None:
        return np.nan, np.nan
    _, r1, _, r2 = best.x
    return (r1, r2) if r1 <= r2 else (r2, r1)


def half_life_h(r):
    r = np.asarray(r, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where((r > 0) & (r < 1), 5 * np.log(0.5) / np.log(r) / 60, np.nan)


def ci(v):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return [float(np.quantile(v, .025)), float(np.quantile(v, .975))] if len(v) > 20 else [np.nan, np.nan]


def symbol_pilot(days, j):
    rng = np.random.default_rng(SEED + 101 * j); n = len(days); S = stack(days)
    W = np.vstack([np.ones(n)] + [np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(B)]).astype(float)
    out = {"n_days": n, "price_only": {}, "tagged": {}}
    for c in CLASSES:
        if f"tag_{c}" not in S:
            continue
        r = solve_w(S, f"tag_{c}", W)[:, 0]
        hl = half_life_h(r)
        c_ = ci(np.log10(hl[1:]))
        out["tagged"][c] = {"r": float(r[0]), "half_life_h": float(hl[0]), "log10_hl_ci": c_, "width": c_[1] - c_[0]}
    tag_w = np.nanmean([v["width"] for v in out["tagged"].values()]) if out["tagged"] else np.nan
    tag_lo = np.nanmin([v["log10_hl_ci"][0] for v in out["tagged"].values()]) if out["tagged"] else np.nan
    tag_hi = np.nanmax([v["log10_hl_ci"][1] for v in out["tagged"].values()]) if out["tagged"] else np.nan
    for L in LS:
        k = solve_w(S, f"k{L}", W)
        rr = np.array([exp_fit(x) for x in k])
        rs = rr[:, 1]; hl = half_life_h(rs)
        rs_ci = ci(rs[1:]); c_ = ci(np.log10(hl[1:]))
        out["price_only"][str(L)] = {"r_slow": float(rs[0]), "half_life_h": float(hl[0]), "r_slow_ci": rs_ci,
                                     "log10_hl_ci": c_, "width": c_[1] - c_[0],
                                     "reaches_bound": bool(np.isfinite(rs_ci[0]) and (rs_ci[0] <= BLO or rs_ci[1] >= BHI)),
                                     "width_ratio_to_tagged": float((c_[1] - c_[0]) / tag_w) if tag_w and np.isfinite(tag_w) else np.nan,
                                     "overlaps_tagged": bool(np.isfinite(c_[0]) and c_[0] <= tag_hi and c_[1] >= tag_lo)}
    out["tagged_mean_width"] = float(tag_w)
    return out


def load(caches, sym):
    days = {}
    for cd in caches:
        for f in sorted((Path(cd) / sym).glob("*_nodepth.pkl")):
            try:
                obj = pd.read_pickle(f)
            except Exception:
                continue
            df = obj[0] if isinstance(obj, tuple) else obj
            if df is None:
                continue
            st = day_stats(df)
            if st is not None:
                days[f.name.split("_")[0]] = st
    return [days[d] for d in sorted(days)]


def _one(args):
    caches, s, j, part_dir = args
    part = Path(part_dir) / f"{s}.json" if part_dir else None
    if part is not None and part.exists():
        return s, json.loads(part.read_text())
    days = load(caches, s)
    r = symbol_pilot(days, j) if len(days) >= 30 else {"n_days": len(days), "excluded": "fewer than 30 valid days"}
    r = json.loads(json.dumps(r, default=lambda o: None if o is None else float(o)))
    if part is not None:
        part.write_text(json.dumps(r))
    return s, r


def summarize(per):
    ev = [v for v in per.values() if "price_only" in v]
    out = {"n_symbols": len(ev), "median_tagged_width_log10": float(np.median([v["tagged_mean_width"] for v in ev]))}
    for L in LS:
        rows = [v["price_only"][str(L)] for v in ev]
        out[f"L{L}"] = {"median_width_log10": float(np.nanmedian([r["width"] for r in rows])),
                        "median_ratio_to_tagged": float(np.nanmedian([r["width_ratio_to_tagged"] for r in rows])),
                        "ratio_at_least_10": int(sum((r["width_ratio_to_tagged"] or 0) >= 10 for r in rows)),
                        "reaches_bound": int(sum(r["reaches_bound"] for r in rows)),
                        "overlaps_tagged": int(sum(r["overlaps_tagged"] for r in rows)),
                        "median_half_life_h": float(np.nanmedian([r["half_life_h"] for r in rows]))}
    out["median_tagged_half_life_h"] = float(np.nanmedian([np.nanmedian([c["half_life_h"] for c in v["tagged"].values()]) for v in ev]))
    return out


def run(caches, out_json, part_dir=None, symbols=SYMBOLS, workers=None):
    if part_dir:
        Path(part_dir).mkdir(parents=True, exist_ok=True)
    jobs = [([str(c) for c in caches], s, j, str(part_dir) if part_dir else None) for j, s in enumerate(symbols)]
    per = {}
    with ProcessPoolExecutor(max_workers=workers or os.cpu_count()) as ex:
        for s, r in ex.map(_one, jobs):
            per[s] = r
            if "price_only" in r:
                p = r["price_only"]
                print(f"  {s}: tagged hl={np.nanmedian([c['half_life_h'] for c in r['tagged'].values()]):.1f}h  "
                      + "  ".join(f"L{L}: hl={p[str(L)]['half_life_h']:.1f}h ratio={p[str(L)]['width_ratio_to_tagged']:.1f} "
                                  f"bound={p[str(L)]['reaches_bound']}" for L in LS), flush=True)
            else:
                print(f"  {s}: excluded", flush=True)
    res = {"kind": "EXPLORATORY Pilot 3 (horizon-matched comparison); not a registered test",
           "run_utc": datetime.now(timezone.utc).isoformat(), "per_symbol": {s: per[s] for s in symbols},
           "summary": summarize(per)}
    Path(out_json).write_text(json.dumps(res, indent=1, default=lambda o: None if o is None else float(o)) + "\n")
    print(json.dumps(res["summary"], indent=1))
    return res


def selftest():
    import tempfile
    rng = np.random.default_rng(4)
    with tempfile.TemporaryDirectory() as td:
        for s in SYMBOLS[:2]:
            os.makedirs(f"{td}/{s}")
            for d in pd.date_range("2025-01-01", periods=40, freq="5D"):
                T = 1440; r = rng.normal(0, 3, T); p = np.cumsum(r)
                ret5 = pd.Series(r).rolling(5).sum().fillna(0).to_numpy()
                n = np.zeros(T); fl = np.zeros(T)
                for t in range(1, T):
                    n[t] = 0.9995 * n[t - 1] + 0.002 * ret5[t] / 5
                    fl[t] = 0.01 * n[t] + rng.normal(0, 0.05)
                R = np.full(T, np.nan); idx = np.arange(0, T, 5); R[idx] = (1 + n[idx]) / (1 - n[idx])
                pd.to_pickle((pd.DataFrame({"close": 100 * np.exp(p / 1e4), "flow": fl, "top_pos_ratio": R,
                                            "top_acc_ratio": R, "acc_ratio": R}), {}), f"{td}/{s}/{d:%Y-%m-%d}_nodepth.pkl")
        r = run([td], f"{td}/p3.json", symbols=SYMBOLS[:2], workers=1)
        assert r["summary"]["n_symbols"] == 2
    print("selftest: PASS")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
