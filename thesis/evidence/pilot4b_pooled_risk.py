"""EXPLORATORY Pilot 4b on the spent C3 symbols (not a registered test; nothing here is confirmatory evidence).

Pilot 4 found the right sign in sample (lower margin, higher next-day risk; t = -2.9 for realized variance with 20-day
windows) but a loss out of sample, where each symbol had its own model. Pilot 4b asks whether one pooled coefficient
forecasts out of sample. Four pre-declared variants, and only these: window W = 20 days; outcome Y in {log realized
variance, log maximum adverse excursion}; predictor in {within-symbol rank of the margin, margin winsorized at the 5th
and 95th percentiles of the training data}. Design: symbol fixed effects and pooled slopes on log(1 + RV) of the previous
day and of the trailing window, fitted on the first 60% of each symbol's valid days; forecasts on the remaining 40%
(fixed effects from the training data); one-sided Clark-West test of adding the margin, over all test days.
Usage (Colab): pilot4b_pooled_risk.run(cache_dir, out_json)        Local test: python pilot4b_pooled_risk.py --selftest
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c3_margin_more_days as C3  # noqa: E402
import pilot4_curve_and_risk as P4  # noqa: E402

W = 20
FIT_SHARE = 0.6


def rows_for(sym, days):
    S = C3.stack([{k: d[k] for k in ("k_ret", "price", "k_x")} for d in days])
    out = []
    for t in range(W, len(days)):
        M, rev, kphi = P4.point_margin(S, t - W, t)
        past = [days[s]["y"]["rv"] for s in range(t - W, t)]
        out.append({"symbol": sym, "t": t, "M": M, "log_rv": np.log1p(days[t]["y"]["rv"]),
                    "log_mae": np.log1p(days[t]["y"]["mae"]), "log_rv_lag": np.log1p(days[t - 1]["y"]["rv"]),
                    "log_rv_trail": np.log1p(np.mean(past))})
    return out


def pooled_oos(d, y, xcol):
    d = d.dropna(subset=[y, "M", "log_rv_lag", "log_rv_trail"]).copy()
    d["n_sym"] = d.groupby("symbol")["t"].transform("count")
    d["rank_t"] = d.groupby("symbol")["t"].rank(method="first")
    d["train"] = d["rank_t"] <= FIT_SHARE * d["n_sym"]
    tr, te = d[d.train].copy(), d[~d.train].copy()
    if xcol == "M_rank":
        # rank against the symbol's training distribution (no look-ahead)
        for s, g in tr.groupby("symbol"):
            ref = np.sort(g["M"].to_numpy())
            tr.loc[g.index, "X"] = np.searchsorted(ref, g["M"].to_numpy(), side="right") / len(ref)
            idx = te.index[te.symbol == s]
            te.loc[idx, "X"] = np.searchsorted(ref, te.loc[idx, "M"].to_numpy(), side="right") / len(ref)
    else:
        lo, hi = tr["M"].quantile(0.05), tr["M"].quantile(0.95)
        tr["X"] = tr["M"].clip(lo, hi); te["X"] = te["M"].clip(lo, hi)
    base = ["log_rv_lag", "log_rv_trail"]

    def fit(cols):
        Z = tr[[y] + cols].copy(); means = Z.groupby(tr["symbol"]).transform("mean")
        Xd = (Z[cols] - means[cols]).to_numpy(); yd = (Z[y] - means[y]).to_numpy()
        b = np.linalg.lstsq(Xd, yd, rcond=None)[0]
        fe = (tr[y] - tr[cols].to_numpy() @ b).groupby(tr["symbol"]).mean()
        return te["symbol"].map(fe).to_numpy() + te[cols].to_numpy() @ b, b
    f0, _ = fit(base); f1, b1 = fit(base + ["X"]); yy = te[y].to_numpy()
    cw = (yy - f0) ** 2 - ((yy - f1) ** 2 - (f0 - f1) ** 2)
    t_cw = float(cw.mean() / (cw.std(ddof=1) / np.sqrt(len(cw))))
    sst = float(((yy - tr[y].mean()) ** 2).sum())
    return {"n_train": int(len(tr)), "n_test": int(len(te)), "coef_X": float(b1[-1]),
            "delta_r2_pct": 100 * (float(((yy - f0) ** 2).sum()) - float(((yy - f1) ** 2).sum())) / sst,
            "clark_west_t": t_cw, "p": float(stats.norm.sf(t_cw))}


def analyse(per_symbol_days):
    rows = []
    for s, days in per_symbol_days.items():
        if len(days) >= C3.MIN_VALID_DAYS:
            rows += rows_for(s, days)
    d = pd.DataFrame(rows)
    out = {}
    for y in ("log_rv", "log_mae"):
        for x in ("M_rank", "M_winsorized"):
            out[f"{y}|{x}"] = pooled_oos(d, y, x)
            print(y, x, json.dumps(out[f"{y}|{x}"]), flush=True)
    return {"n_symbols": int(d.symbol.nunique()) if len(d) else 0, "variants": out}


def run(cache_dir, out_json, symbols=None):
    symbols = symbols or json.loads((HERE / "C3_universe.json").read_text())["symbols"]
    per = P4.load(cache_dir, symbols, C3.dates())
    res = {"kind": "EXPLORATORY Pilot 4b (pooled out-of-sample risk forecast on the spent C3 symbols); not a registered test",
           "run_utc": datetime.now(timezone.utc).isoformat(), **analyse(per)}
    Path(out_json).write_text(json.dumps(res, indent=1, default=float) + "\n")
    return res


def selftest():
    rng = np.random.default_rng(8); per = {}
    for j in range(6):
        days = []
        for d in range(230):
            T = 1440; p = np.cumsum(rng.normal(0, 3, T)); fl = rng.normal(0, 1, T) * 0.01
            p = p - 0.5 * (p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy())
            r = P4.day_record(pd.DataFrame({"close": 100 * np.exp(p / 1e4), "flow": fl}))
            if r is not None:
                days.append(r)
        per[f"S{j}"] = days
    out = analyse(per)
    assert out["n_symbols"] == 6 and len(out["variants"]) == 4
    assert all(v["n_test"] > 100 for v in out["variants"].values())
    print("selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
