"""EXPLORATORY Pilot 4 on the spent C3 symbols (not a registered test; nothing here is confirmatory evidence).

Two questions, to design the flagship test before its data exist:
A. The learning curve (Theorem thm:passivecert, Chapter 4). For nested samples of n = 30, 60, 120, 240 and all valid days,
   how many symbols have a decided margin and how many have identified memories? The theorem predicts that the decided
   share rises with n (the standardized margin grows like sqrt(n)) while the identified share stays near zero. Read per
   symbol as the slope of log|z| on log n, where z is the margin over its bootstrap standard error (theory: 1/2).
B. Does the certificate matter? In rolling windows of W = 20 and 60 days, does the estimated margin (and its parts:
   reversion -beta and feedback kappa*Phi) forecast the next day's risk beyond trailing volatility? Outcomes: the
   next day's maximum adverse excursion (largest fall from a running maximum, bp) and realized variance. Pooled
   regressions with symbol fixed effects and day-clustered errors, and an out-of-sample split (first 60% of each
   symbol's days to fit, the rest to test) with the gain in R^2 over a volatility-only model.

Data: the 30 symbols and 430 dates of C3, read from the C3 download cache (re-downloaded only if missing); C3's valid-day rule.
Usage (Colab): pilot4_curve_and_risk.run(cache_dir, out_json)        Local test: python pilot4_curve_and_risk.py --selftest
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binance_vision as bv  # noqa: E402
import c2_margin_vs_identify as C2  # noqa: E402
import c3_margin_more_days as C3  # noqa: E402

NS = (30, 60, 120, 240)
WS = (20, 60)
B = 200
SEED = 20261104
FIT_SHARE = 0.6


def day_record(df):
    st = C3.day_stats(df)
    if st is None:
        return None
    p = np.log(df["close"].to_numpy(float)) * 1e4
    m = np.arange(5, 1440, 5); r = p[m] - p[m - 5]
    runmax = np.maximum.accumulate(p)
    st["y"] = {"mae": float(np.max(runmax - p)), "rv": float(np.sum(r ** 2)),
               "absret": float(abs(p[-1] - p[0])), "range": float(p.max() - p.min())}
    return st


def stats_of(days, j, salt=0, nb=B):
    """Margin decision, z-statistic and identification for a list of day records (C3's estimators)."""
    rng = np.random.default_rng(SEED + 101 * j + salt); n = len(days)
    S = C3.stack([{k: d[k] for k in ("k_ret", "price", "k_x")} for d in days])
    W = np.vstack([np.ones(n)] + [np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(nb)]).astype(float)
    pr, kx, kr = C2.solve_w(S, "price", W), C2.solve_w(S, "k_x", W), C2.solve_w(S, "k_ret", W)
    M = -pr[:, 1] - pr[:, 0] * kx.sum(1)
    c = C2.ci(M[1:]); sd = float(np.nanstd(M[1:]))
    rr = np.array([C2.exp_fit(k) for k in kr[: min(nb, 100) + 1]])
    rf, rs, dr = C2.ci(rr[1:, 0]), C2.ci(rr[1:, 1]), C2.ci(rr[1:, 1] - rr[1:, 0])
    inside = all(np.isfinite(v) and C3.BLO < v < C3.BHI for v in rf + rs)
    return {"n": n, "M": float(M[0]), "z": float(M[0] / sd) if sd > 0 else np.nan,
            "decided": bool(c[0] > 0 or c[1] < 0),
            "identified": bool(np.isfinite(dr[0]) and (dr[0] > 0 or dr[1] < 0) and inside)}


def point_margin(S, lo, hi):
    """Point estimates (M, reversion -beta, feedback kappa*Phi) from days lo..hi-1 of stacked sufficient statistics."""
    def solve(name):
        A = S[name][0][lo:hi].sum(0); b = S[name][1][lo:hi].sum(0)
        try:
            return np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            return np.full(b.shape, np.nan)
    pr, kx = solve("price"), solve("k_x")
    kphi = pr[0] * kx.sum(); rev = -pr[1]
    return rev - kphi, rev, kphi


def curve(days, j):
    out = {}
    for n in NS + (len(days),):
        if n > len(days):
            continue
        out[str(n) if n in NS else "all"] = stats_of(days[:n], j, salt=n)
    ns = [v["n"] for v in out.values() if np.isfinite(v["z"]) and v["z"] != 0]
    zs = [abs(v["z"]) for v in out.values() if np.isfinite(v["z"]) and v["z"] != 0]
    out["z_slope"] = float(np.polyfit(np.log(ns), np.log(zs), 1)[0]) if len(ns) >= 3 else np.nan
    return out


def rolling_rows(sym, days):
    S = C3.stack([{k: d[k] for k in ("k_ret", "price", "k_x")} for d in days])
    rows = []
    for W in WS:
        for t in range(W, len(days)):
            M, rev, kphi = point_margin(S, t - W, t)
            y = days[t]["y"]; past = [days[s]["y"]["rv"] for s in range(t - W, t)]
            rows.append({"symbol": sym, "W": W, "t": t, "M": M, "rev": rev, "kphi": kphi,
                         "log_mae": np.log1p(y["mae"]), "log_rv": np.log1p(y["rv"]),
                         "log_rv_lag": np.log1p(days[t - 1]["y"]["rv"]), "log_rv_trail": np.log1p(np.mean(past))})
    return rows


def panel_fit(df, yname, xnames):
    """OLS with symbol fixed effects (within transform) and errors clustered by symbol-day index t."""
    d = df.dropna(subset=[yname] + xnames).copy()
    if len(d) < 50:
        return None
    for c in [yname] + xnames:
        d[c] = d[c] - d.groupby("symbol")[c].transform("mean")
    X = d[xnames].to_numpy(); y = d[yname].to_numpy()
    XtX = X.T @ X; beta = np.linalg.solve(XtX, X.T @ y); e = y - X @ beta
    meat = np.zeros((len(xnames), len(xnames)))
    for _, g in d.assign(e=e).groupby("t"):
        s = g[xnames].to_numpy().T @ g["e"].to_numpy(); meat += np.outer(s, s)
    V = np.linalg.solve(XtX, np.linalg.solve(XtX, meat).T)
    se = np.sqrt(np.diag(V))
    return {"n": int(len(d)), "coef": dict(zip(xnames, beta.tolist())), "t": dict(zip(xnames, (beta / se).tolist()))}


def oos_gain(df, yname, base, extra):
    """Per symbol, fit on the first 60% of days and test on the rest; pooled out-of-sample R^2 gain of adding `extra`."""
    sse0 = sse1 = sst = 0.0; nsym = 0; wins = 0
    for _, g in df.dropna(subset=[yname] + base + extra).groupby("symbol"):
        g = g.sort_values("t"); k = int(FIT_SHARE * len(g))
        if k < 30 or len(g) - k < 20:
            continue
        tr, te = g.iloc[:k], g.iloc[k:]

        def pred(cols):
            X = np.column_stack([np.ones(len(tr))] + [tr[c] for c in cols]); b = np.linalg.lstsq(X, tr[yname], rcond=None)[0]
            Xt = np.column_stack([np.ones(len(te))] + [te[c] for c in cols]); return Xt @ b
        e0 = te[yname] - pred(base); e1 = te[yname] - pred(base + extra)
        sse0 += float(e0 @ e0); sse1 += float(e1 @ e1); sst += float(((te[yname] - tr[yname].mean()) ** 2).sum())
        nsym += 1; wins += int(e1 @ e1 < e0 @ e0)
    if nsym == 0:
        return None
    return {"n_symbols": nsym, "delta_r2_pct": 100 * (sse0 - sse1) / sst, "symbols_improved": wins}


def analyse(per_symbol_days):
    curves, rows = {}, []
    for j, (s, days) in enumerate(per_symbol_days.items()):
        if len(days) < C3.MIN_VALID_DAYS:
            continue
        curves[s] = curve(days, j)
        rows += rolling_rows(s, days)
        print(f"  {s}: " + " ".join(f"n={k}:{'D' if v['decided'] else '-'}{'I' if v['identified'] else '-'}"
                                    for k, v in curves[s].items() if k != "z_slope")
              + f" z-slope={curves[s]['z_slope']:.2f}", flush=True)
    summ = {"n_symbols": len(curves), "curve": {}}
    for k in [str(n) for n in NS] + ["all"]:
        vals = [c[k] for c in curves.values() if k in c]
        summ["curve"][k] = {"n_symbols": len(vals), "decided": sum(v["decided"] for v in vals),
                            "identified": sum(v["identified"] for v in vals)}
    summ["median_z_slope"] = float(np.nanmedian([c["z_slope"] for c in curves.values()])) if curves else None
    R = pd.DataFrame(rows); risk = {}
    for W in WS:
        d = R[R.W == W].copy()
        if d.empty:
            continue
        for v in ("M", "rev", "kphi"):                                   # rank within symbol: robust to outliers
            d[v + "_rk"] = d.groupby("symbol")[v].rank(pct=True)
        base = ["log_rv_lag", "log_rv_trail"]
        risk[str(W)] = {y: {"panel_M": panel_fit(d, y, base + ["M_rk"]),
                            "panel_parts": panel_fit(d, y, base + ["rev_rk", "kphi_rk"]),
                            "oos_M": oos_gain(d, y, base, ["M_rk"]),
                            "oos_kphi": oos_gain(d, y, base, ["kphi_rk"])} for y in ("log_mae", "log_rv")}
    summ["risk"] = risk
    return {"curves": curves, "summary": summ}


def load(cache_dir, symbols, dates, threads=16):
    per = {s: [] for s in symbols}
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(bv.get_day, s, d, cache_dir, False): (s, d) for s in symbols for d in dates}
        for i, f in enumerate(as_completed(futs)):
            s, d = futs[f]
            try:
                df, _ = f.result()
            except Exception:
                df = None
            if df is not None:
                r = day_record(df)
                if r is not None:
                    per[s].append((d, r))
            if (i + 1) % 2000 == 0:
                print(f"  {i + 1}/{len(futs)} symbol-days", flush=True)
    return {s: [r for _, r in sorted(v, key=lambda t: t[0])] for s, v in per.items()}


def run(cache_dir, out_json, symbols=None, dates=None):
    symbols = symbols or json.loads((HERE / "C3_universe.json").read_text())["symbols"]
    dates = dates or C3.dates()
    per = load(cache_dir, symbols, dates)
    res = {"kind": "EXPLORATORY Pilot 4 (learning curve and margin-predicts-risk on the spent C3 symbols); not a registered test",
           "run_utc": datetime.now(timezone.utc).isoformat(), **analyse(per)}
    Path(out_json).write_text(json.dumps(res, indent=1, default=float) + "\n")
    print(json.dumps(res["summary"], indent=1, default=float))
    return res


def selftest():
    rng = np.random.default_rng(4); per = {}
    for j in range(4):
        days = []
        for d in range(250):
            T = 1440; p = np.cumsum(rng.normal(0, 3, T)); fl = rng.normal(0, 1, T) * 0.01
            p = p - 0.5 * (p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy())
            r = day_record(pd.DataFrame({"close": 100 * np.exp(p / 1e4), "flow": fl}))
            if r is not None:
                days.append(r)
        per[f"S{j}"] = days
    out = analyse(per)
    s = out["summary"]; print(json.dumps(s["curve"]), s["median_z_slope"])
    assert s["n_symbols"] == 4 and set(s["curve"]) == {"30", "60", "120", "240", "all"}
    assert s["risk"]["20"]["log_mae"]["panel_M"]["n"] > 100 and abs(s["median_z_slope"] - 0.5) < 0.35
    print("selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
