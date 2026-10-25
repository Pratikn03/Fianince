"""EXPLORATORY Pilot 7 on the spent C3 symbols (not a registered test; nothing here is confirmatory evidence).

Two questions.
A. The size of the effect, not only its sign. The worst-case transient loss is |I| w ||h||_1 and in the positive class
   ||h||_1 = S = kappa / M, so with the shock size w fixed, log(adverse move) should rise one-for-one with log S, and
   log(realized variance) two-for-one. Within symbols, regress the next day's log maximum adverse excursion (and log RV)
   on log S estimated from the previous 20 valid days, controlling for that day's shock size (log standard deviation of
   five-minute taker flow, times the estimated impact), with symbol fixed effects. The 20-day estimate is noisy, which
   biases OLS towards zero, so log S from the 20 days before that (days t-40..t-21) is used as an instrument (2SLS).
   Windows with a non-positive estimated margin are dropped. Theory: elasticity 1 for MAE and 2 for RV.
B. A stress test. On the market-wide stress day (the valid date with the largest median adverse excursion across
   symbols, and 2025-10-10 if different), did symbols with a lower margin over the previous 20 days have larger
   adverse moves? Spearman correlation across symbols (theory: negative), and the cross-sectional median margin in the
   20-day windows ending on each date (does it dip before the stress day?).
Usage (Colab): pilot7_size_and_crash.run(cache_dir, out_json)        Local test: python pilot7_size_and_crash.py --selftest
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binance_vision as bv  # noqa: E402
import c3_margin_more_days as C3  # noqa: E402
import pilot4_curve_and_risk as P4  # noqa: E402

W = 20
EPS = 0.005


def record(df, date):
    r = P4.day_record(df)
    if r is None:
        return None
    fl = np.nan_to_num(df["flow"].to_numpy(float)); cf = np.concatenate([[0.0], np.cumsum(fl)])
    m = np.arange(5, 1440, 5); flow5 = cf[m + 1] - cf[m - 4]
    r["date"] = date; r["flow_sd"] = float(np.std(flow5))
    return r


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
                r = record(df, d)
                if r is not None:
                    per[s].append(r)
            if (i + 1) % 2000 == 0:
                print(f"  {i + 1}/{len(futs)} symbol-days", flush=True)
    return {s: sorted(v, key=lambda r: r["date"]) for s, v in per.items()}


def window(S, lo, hi):
    def solve(name):
        A = S[name][0][lo:hi].sum(0); b = S[name][1][lo:hi].sum(0)
        try:
            return np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            return np.full(b.shape, np.nan)
    pr, kx = solve("price"), solve("k_x")
    kappa = pr[0]; M = -pr[1] - kappa * kx.sum()
    return kappa, M


def rows_for(sym, days):
    S = C3.stack([{k: d[k] for k in ("k_ret", "price", "k_x")} for d in days])
    out = []
    for t in range(2 * W, len(days)):
        k1, M1 = window(S, t - W, t); k0, M0 = window(S, t - 2 * W, t - W)
        out.append({"symbol": sym, "date": days[t]["date"], "M": M1, "kappa": k1, "M_lag": M0, "kappa_lag": k0,
                    "log_mae": np.log1p(days[t]["y"]["mae"]), "log_rv": np.log1p(days[t]["y"]["rv"]),
                    "shock": days[t]["flow_sd"]})
    return out


def within(d, cols):
    return d[cols] - d.groupby("symbol")[cols].transform("mean")


def tsls(d, y):
    """2SLS of y on log S (instrumented by its lag) and log shock, symbol fixed effects, errors clustered by date."""
    if len(d) < 50:
        return None
    Z = within(d, [y, "logS", "logS_lag", "log_shock"])
    X = Z[["logS", "log_shock"]].to_numpy(); Zi = Z[["logS_lag", "log_shock"]].to_numpy(); yy = Z[y].to_numpy()
    Pz = Zi @ np.linalg.solve(Zi.T @ Zi, Zi.T @ X)
    b = np.linalg.solve(Pz.T @ X, Pz.T @ yy); e = yy - X @ b
    bread = np.linalg.inv(Pz.T @ X); meat = np.zeros((2, 2))
    for _, g in pd.DataFrame({"date": d["date"].to_numpy(), "i": np.arange(len(d))}).groupby("date"):
        s_ = Pz[g["i"]].T @ e[g["i"]]; meat += np.outer(s_, s_)
    V = bread @ meat @ bread.T; se = np.sqrt(np.diag(V))
    first = np.linalg.lstsq(Zi, X[:, 0], rcond=None)[0]
    fs_r2 = 1 - np.var(X[:, 0] - Zi @ first) / np.var(X[:, 0])
    ols = np.linalg.lstsq(X, yy, rcond=None)[0]
    return {"n": int(len(d)), "elasticity_iv": float(b[0]), "se_iv": float(se[0]), "elasticity_ols": float(ols[0]),
            "first_stage_r2": float(fs_r2)}


def analyse(per):
    rows = []
    for s, days in per.items():
        if len(days) >= C3.MIN_VALID_DAYS:
            rows += rows_for(s, days)
    d = pd.DataFrame(rows)
    ok = (d.M > EPS) & (d.M_lag > EPS) & (d.kappa > 0) & (d.kappa_lag > 0) & (d.shock > 0)
    e = d[ok].copy()
    e["logS"] = np.log(e.kappa / e.M); e["logS_lag"] = np.log(e.kappa_lag / e.M_lag)
    e["log_shock"] = np.log(e.shock * e.kappa)
    size = {"n_kept": int(len(e)), "n_all": int(len(d)), "mae": tsls(e, "log_mae"), "rv": tsls(e, "log_rv")}
    print("size:", json.dumps(size), flush=True)
    # stress test
    med = d.groupby("date")["log_mae"].median().sort_values(ascending=False)
    stress_days = [med.index[0]] + (["2025-10-10"] if "2025-10-10" in med.index and med.index[0] != "2025-10-10" else [])
    stress = {}
    for sd in stress_days:
        g = d[(d.date == sd) & np.isfinite(d.M)]
        rho = stats.spearmanr(g["M"], g["log_mae"]) if len(g) >= 8 else None
        series = d[np.isfinite(d.M)].groupby("date")["M"].median()
        idx = list(series.index); k = idx.index(sd) if sd in idx else None
        stress[sd] = {"n_symbols": int(len(g)), "median_log_mae_rank": int(list(med.index).index(sd)) + 1,
                      "spearman_margin_vs_mae": float(rho.statistic) if rho else None,
                      "p_one_sided_negative": float(rho.pvalue / 2 if rho and rho.statistic < 0 else 1 - (rho.pvalue / 2 if rho else 0)) if rho else None,
                      "median_margin_window_ending_before": float(series.iloc[k]) if k is not None else None,
                      "median_margin_all_dates": float(series.median()),
                      "percentile_of_pre_stress_median": float((series < series.iloc[k]).mean()) if k is not None else None}
    print("stress:", json.dumps(stress), flush=True)
    return {"size": size, "stress": stress}


def run(cache_dir, out_json, symbols=None):
    symbols = symbols or json.loads((HERE / "C3_universe.json").read_text())["symbols"]
    res = {"kind": "EXPLORATORY Pilot 7 (effect size and stress test on the spent C3 symbols); not a registered test",
           "run_utc": datetime.now(timezone.utc).isoformat(), **analyse(load(cache_dir, symbols, C3.dates()))}
    Path(out_json).write_text(json.dumps(res, indent=1, default=float) + "\n")
    return res


def selftest():
    rng = np.random.default_rng(12); per = {}
    dates = pd.date_range("2025-01-01", periods=230).strftime("%Y-%m-%d")
    for j in range(10):
        days = []
        for k, dt in enumerate(dates):
            T = 1440; p = np.cumsum(rng.normal(0, 3, T)); fl = rng.normal(0, 1, T) * 0.01
            p = p - 0.5 * (p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy())
            r = record(pd.DataFrame({"close": 100 * np.exp(p / 1e4), "flow": fl}), dt)
            if r is not None:
                days.append(r)
        per[f"S{j}"] = days
    out = analyse(per)
    assert out["size"]["n_all"] > 1000 and len(out["stress"]) >= 1
    # planted elasticity: y = 1.0 * logS + 0.5 * log_shock + noise, logS measured with error, lag is an instrument
    n = 4000; sym = np.repeat([f"S{i}" for i in range(20)], n // 20)
    true = rng.normal(0, 0.5, n); shock = rng.normal(0, 0.3, n)
    d = pd.DataFrame({"symbol": sym, "date": np.tile(np.arange(n // 20).astype(str), 20),
                      "logS": true + rng.normal(0, 0.5, n), "logS_lag": true + rng.normal(0, 0.5, n), "log_shock": shock})
    d["log_mae"] = 1.0 * true + 0.5 * shock + rng.normal(0, 0.3, n)
    r = tsls(d, "log_mae"); print("planted:", json.dumps(r))
    assert abs(r["elasticity_iv"] - 1.0) < 0.15 and r["elasticity_ols"] < 0.7
    print("selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
