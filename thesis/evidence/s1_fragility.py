"""Test S1 (DRAFT until registered): does the certified margin measure fragility?

Motivation. C2, C3 and F1 showed, on three sets of new symbols, that the stability margin M = 1 - a - kappa*Phi is
decided from public data where the agents are not identified, always on the safe side. That shows these markets are far
from the feedback boundary; it does not show that the margin detects danger, and F1's registered forecast of the next
day's largest adverse move failed (Clark-West t = 1.51), while its secondary forecast of realized variance did not
(t = 2.92). S1 asks, once, on 40 perpetuals never used in this project, whether a lower margin means more fragility,
and whether the margin tells us anything that the standard measure of endogeneity, the Hawkes branching ratio, does not.

Theory. In the positive class the worst-case transient loss from a shock of size w is |I| w S with S = kappa / M, so at
a common shock, symbols with a smaller margin should move more; and day to day a smaller margin should mean more
variance and more frequent extreme moves. The branching ratio n of a Hawkes model of trade arrivals measures how much
trading is triggered by trading (Filimonov and Sornette 2012; Hardiman, Bercot and Bouchaud 2013); the margin measures
the price feedback loop. If the margin is only a noisy version of n, it adds nothing once n is known.

Universe and data. Binance USD-M USDT perpetuals in the public archive with an ASCII symbol absent from every text file
of the repository (so none of E1v2, D1, the pilots, C2, C3 or F1), with klines on 2025-01-04 and 2026-09-23, 40 drawn in
a seeded random order (seed 20261107) and written to S1_universe.json before any market data are downloaded. Every
calendar day from 2025-01-01 to 2026-09-30 (638 days; consecutive days are needed for stress windows). One-minute
klines only. Valid day: C3's rule. Evaluable symbol: at least 200 valid days. Void if fewer than 20 evaluable symbols or
fewer than 10 stress days.

Estimates for symbol s and day t, from the 20 valid days before t, used only if those 20 days lie within the previous 30
calendar days: the margin M (C3's estimator, point estimate, as in F1's forecast); the branching ratio n_hat, the sum of
the coefficients of a regression of the day-demeaned one-minute trade count on its ten previous minutes (the INAR(p)
approximation of a Hawkes process, Kirchner 2016), pooled over the 20 days; log(1 + RV) of the previous valid day and of
the trailing 20 days (mean RV). Outcomes on day t: log(1 + maximum adverse excursion in bp), log(1 + RV in bp^2).

Primaries (Holm across the four at 0.05):
  P1  Common shock, different damage. Market stress days: dates with rows for at least 20 symbols, ranked by the
      cross-sectional median of log(1 + MAE); the highest is taken, then the next highest at least 7 calendar days from
      every day already taken, until 20 are taken. On each, the partial Spearman correlation across symbols between M
      and log(1 + MAE), controlling for the two volatility terms (ranks of M and of the outcome each regressed on the
      ranks of the controls, residuals correlated). Holds if the mean of these correlations is negative with one-sided
      t-test p < 0.05 (the stress days as observations).
  P2  Variance. F1's pooled out-of-sample design (symbol fixed effects, pooled slopes on the two volatility terms,
      first 60% of each symbol's rows to fit, margin winsorized at the training 5th and 95th percentiles, Clark-West
      differentials averaged within dates) for next-day log(1 + RV). Holds if the coefficient on the margin is negative
      and the one-sided Clark-West p < 0.05.
  P3  Beyond the branching ratio. P2 with n_hat (winsorized at its training 5th and 95th percentiles) added to both
      the restricted and the full model. Holds if the coefficient on the margin is negative and p < 0.05.
  P4  Extreme moves. P2's design for the indicator that log(1 + MAE) exceeds the symbol's training 95th percentile
      (a linear probability model; the Clark-West test then compares Brier scores). Holds if the coefficient on the
      margin is negative and p < 0.05.
Secondary: P1 with n_hat as a further control, and with no controls; the branching ratio's own partial correlation on
stress days; the stress day of 2025-10-10 alone; whether margins were low before stress (percentile of the
cross-sectional median margin on stress days among all dates; share of symbol-stress pairs with the margin below the
symbol's median); P2 to P4 with the margin's within-symbol rank; next-day log(1 + MAE) as in F1; n_hat alone in P2's
design; the share of windows with a negative margin estimate.
"""
import argparse
import hashlib
import json
import subprocess
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
import c2_margin_vs_identify as C2  # noqa: E402
import c3_margin_more_days as C3  # noqa: E402
import pilot4_curve_and_risk as P4  # noqa: E402

THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/S1_fragility.json"
COUNTER = THESIS / "checks/prereg/S1_unlock.json"
RESULT = HERE / "S1_results.json"
ROWS = HERE / "S1_rows.csv.gz"
NUMBERS = THESIS / "checks/S1_numbers.tex"
DLLOG = HERE / "S1_download_log.json.gz"
UNIVERSE = HERE / "S1_universe.json"

SEED, N_SYMBOLS = 20261107, 40
START, END = "2025-01-01", "2026-09-30"
W, SPAN_DAYS, P_LAGS = 20, 30, 10
K_STRESS, SEP_DAYS, MIN_CROSS = 20, 7, 20
MIN_STRESS, FIT_SHARE, TAIL_Q, ALPHA = 10, 0.6, 0.95, 0.05
STRESS_DAY_NAMED = "2025-10-10"
CONTROLS = ["log_rv_lag", "log_rv_trail"]


def dates():
    return [d.strftime("%Y-%m-%d") for d in pd.date_range(START, END, freq="D")]


# ----------------------------------------------------------------------------------------------- universe and data
def universe():
    allsyms = [s for s in C2.list_archive_symbols() if s.isascii()]
    cand = [s for s in allsyms if s.endswith("USDT") and "_" not in s and s.isalnum()]
    text = C2.repo_text()
    unused = [s for s in cand if s not in text]
    order = np.random.default_rng(SEED).permutation(len(unused))
    chosen, checked = [], []
    for i in order:
        s = unused[i]
        ok = all(bv._http(bv.ds_url("klines", s, d), method="HEAD")[0] == 200 for d in ("2025-01-04", "2026-09-23"))
        checked.append({"symbol": s, "files_on_both_dates": ok})
        if ok:
            chosen.append(s)
        if len(chosen) == N_SYMBOLS:
            break
    u = {"rule": "ASCII USDT perpetuals in the archive, absent from every repository text file, klines on 2025-01-04 and "
                 "2026-09-23, seeded random order", "seed": SEED, "n_archive": len(allsyms), "n_candidates": len(cand),
         "n_unused": len(unused), "checked_in_order": checked, "symbols": chosen,
         "written_utc": datetime.now(timezone.utc).isoformat()}
    UNIVERSE.write_text(json.dumps(u, indent=1) + "\n")
    return chosen


def build(sym, date):
    """One-minute close and signed taker flow exactly as binance_vision.build_day makes them, plus the trade count."""
    raw = bv.fetch("klines", sym, date)
    if raw is None:
        return None
    t0 = int(pd.Timestamp(f"{date} 00:00:00", tz="UTC").timestamp())
    k = bv.read_zip_csv(raw, bv.KL_COLS)
    k = k.assign(m=(bv.to_utc_seconds(k["open_time"]) - t0) // 60).drop_duplicates("m").set_index("m").reindex(np.arange(1440))
    out = pd.DataFrame(index=np.arange(1440))
    out["close"] = k["close"].astype(float).ffill().bfill()
    out["flow"] = (2 * k["taker_buy_quote_volume"].astype(float) - k["quote_volume"].astype(float)).fillna(0) / 1e6
    out["count"] = k["count"].astype(float).fillna(0)
    return out


def get(sym, date, cache_dir=None):
    if cache_dir:
        d_ = Path(cache_dir) / sym; d_.mkdir(parents=True, exist_ok=True); pk = d_ / f"{date}_s1.pkl"
        if pk.exists():
            return pd.read_pickle(pk)
    out = build(sym, date)
    if cache_dir:
        pd.to_pickle(out, pk)
    return out


def hawkes_stats(count):
    c = np.asarray(count, float); c = c - c.mean()
    X = np.column_stack([c[P_LAGS - j - 1:len(c) - j - 1] for j in range(P_LAGS)]); y = c[P_LAGS:]
    return X.T @ X, X.T @ y


def record(df, date):
    r = P4.day_record(df)
    if r is None:
        return None
    r["date"] = date; r["hawkes"] = hawkes_stats(df["count"].to_numpy())
    return r


def load(cache_dir, symbols, ds, threads=16):
    per = {s: [] for s in symbols}
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(get, s, d, cache_dir): (s, d) for s in symbols for d in ds}
        for i, f in enumerate(as_completed(futs)):
            s, d = futs[f]
            try:
                df = f.result()
            except Exception as err:
                print("  download error", s, d, repr(err)[:100], flush=True); df = None
            if df is not None:
                r = record(df, d)
                if r is not None:
                    per[s].append(r)
            if (i + 1) % 2000 == 0:
                print(f"  {i + 1}/{len(futs)} symbol-days", flush=True)
    return {s: sorted(v, key=lambda r: r["date"]) for s, v in per.items()}


def rows_for(sym, days):
    S = C3.stack([{k: d[k] for k in ("k_ret", "price", "k_x")} for d in days])
    HA = np.stack([d["hawkes"][0] for d in days]); Hb = np.stack([d["hawkes"][1] for d in days])
    dt = pd.to_datetime([d["date"] for d in days])
    out = []
    for t in range(W, len(days)):
        if (dt[t] - dt[t - W]).days > SPAN_DAYS:
            continue
        M, _, _ = P4.point_margin(S, t - W, t)
        try:
            n_hat = float(np.linalg.solve(HA[t - W:t].sum(0), Hb[t - W:t].sum(0)).sum())
        except np.linalg.LinAlgError:
            n_hat = np.nan
        out.append({"symbol": sym, "t": t, "date": days[t]["date"], "M": float(M), "n_hat": n_hat,
                    "log_mae": float(np.log1p(days[t]["y"]["mae"])), "log_rv": float(np.log1p(days[t]["y"]["rv"])),
                    "log_rv_lag": float(np.log1p(days[t - 1]["y"]["rv"])),
                    "log_rv_trail": float(np.log1p(np.mean([days[s]["y"]["rv"] for s in range(t - W, t)])))})
    return out


# ----------------------------------------------------------------------------------------------------- statistics
def partial_spearman(g, x, y, controls):
    R = g[[x, y] + controls].rank().to_numpy()
    Z = np.column_stack([np.ones(len(R))] + [R[:, 2 + i] for i in range(len(controls))])
    res = [R[:, i] - Z @ np.linalg.lstsq(Z, R[:, i], rcond=None)[0] for i in (0, 1)]
    if np.std(res[0]) == 0 or np.std(res[1]) == 0:
        return np.nan
    return float(np.corrcoef(res[0], res[1])[0, 1])


def stress_days(d):
    cnt = d.groupby("date")["symbol"].nunique(); ok = cnt[cnt >= MIN_CROSS].index
    med = d[d.date.isin(ok)].groupby("date")["log_mae"].median().sort_values(ascending=False)
    chosen = []
    for day in med.index:
        if all(abs((pd.Timestamp(day) - pd.Timestamp(c)).days) >= SEP_DAYS for c in chosen):
            chosen.append(day)
        if len(chosen) == K_STRESS:
            break
    return chosen, med


def stress_test(d, x="M", controls=CONTROLS, days=None):
    days = days if days is not None else stress_days(d)[0]
    rhos = {}
    for day in days:
        g = d[d.date == day].dropna(subset=[x, "log_mae"] + controls)
        if len(g) >= MIN_CROSS:
            rhos[day] = partial_spearman(g, x, "log_mae", controls)
    v = np.array([r for r in rhos.values() if np.isfinite(r)])
    if len(v) < 3:
        return {"n_days": int(len(v)), "per_day": rhos}
    t = float(v.mean() / (v.std(ddof=1) / np.sqrt(len(v))))
    return {"n_days": int(len(v)), "mean_rho": float(v.mean()), "median_rho": float(np.median(v)),
            "n_negative": int((v < 0).sum()), "t": t, "p_one_sided_negative": float(stats.t.cdf(t, len(v) - 1)),
            "per_day": rhos}


def pooled(d, y, xcol="M_winsorized", extra=(), tail=False, x_only=None):
    """F1's pooled out-of-sample design with optional extra controls and a tail-indicator outcome."""
    need = [y if not tail else "log_mae", "M", *CONTROLS, *extra] + ([x_only] if x_only else [])
    d = d.dropna(subset=need).copy()
    if d.empty:
        return {"evaluable": False}
    d["n_sym"] = d.groupby("symbol")["t"].transform("count")
    d["rank_t"] = d.groupby("symbol")["t"].rank(method="first")
    d["train"] = d["rank_t"] <= FIT_SHARE * d["n_sym"]
    tr, te = d[d.train].copy(), d[~d.train].copy()
    if len(tr) < 100 or len(te) < 100:
        return {"evaluable": False}
    if tail:
        thr = tr.groupby("symbol")["log_mae"].quantile(TAIL_Q)
        tr["Y"] = (tr["log_mae"] > tr["symbol"].map(thr)).astype(float)
        te["Y"] = (te["log_mae"] > te["symbol"].map(thr)).astype(float)
    else:
        tr["Y"], te["Y"] = tr[y], te[y]
    src = x_only or "M"
    if xcol == "M_rank":
        for s, g in tr.groupby("symbol"):
            ref = np.sort(g[src].to_numpy())
            tr.loc[g.index, "X"] = np.searchsorted(ref, g[src].to_numpy(), side="right") / len(ref)
            idx = te.index[te.symbol == s]
            te.loc[idx, "X"] = np.searchsorted(ref, te.loc[idx, src].to_numpy(), side="right") / len(ref)
    else:
        lo, hi = tr[src].quantile(0.05), tr[src].quantile(0.95)
        tr["X"] = tr[src].clip(lo, hi); te["X"] = te[src].clip(lo, hi)
    base = list(CONTROLS)
    for e in extra:
        lo, hi = tr[e].quantile(0.05), tr[e].quantile(0.95)
        tr[e + "_w"] = tr[e].clip(lo, hi); te[e + "_w"] = te[e].clip(lo, hi); base.append(e + "_w")
    te = te.dropna(subset=["X"])

    def fit(cols):
        Z = tr[["Y"] + cols]; means = Z.groupby(tr["symbol"]).transform("mean")
        b = np.linalg.lstsq((Z[cols] - means[cols]).to_numpy(), (Z["Y"] - means["Y"]).to_numpy(), rcond=None)[0]
        fe = (tr["Y"] - tr[cols].to_numpy() @ b).groupby(tr["symbol"]).mean()
        return te["symbol"].map(fe).to_numpy() + te[cols].to_numpy() @ b, b
    f0, _ = fit(base); f1, b1 = fit(base + ["X"]); yy = te["Y"].to_numpy()
    cw = pd.Series((yy - f0) ** 2 - ((yy - f1) ** 2 - (f0 - f1) ** 2), index=te.index)
    by_date = cw.groupby(te["date"]).mean()
    t_cw = float(by_date.mean() / (by_date.std(ddof=1) / np.sqrt(len(by_date)))) if len(by_date) > 2 else np.nan
    sst = float(((yy - tr["Y"].mean()) ** 2).sum())
    out = {"evaluable": True, "n_train": int(len(tr)), "n_test": int(len(te)), "n_test_dates": int(len(by_date)),
           "coef_X": float(b1[-1]), "clark_west_t_by_date": t_cw, "p": float(stats.norm.sf(t_cw)),
           "delta_r2_pct": 100 * (float(((yy - f0) ** 2).sum()) - float(((yy - f1) ** 2).sum())) / sst}
    if tail:
        out["test_events"] = int(yy.sum())
    return out


def evaluate(d, n_evaluable):
    out = {"n_evaluable": int(n_evaluable), "n_rows": int(len(d))}
    days, med = stress_days(d) if len(d) else ([], pd.Series(dtype=float))
    out["stress_days"] = days
    out["void"] = bool(n_evaluable < C3.MIN_SYMBOLS or len(days) < MIN_STRESS)
    if out["void"]:
        return out
    p1 = stress_test(d, days=days)
    p2 = pooled(d, "log_rv")
    p3 = pooled(d, "log_rv", extra=("n_hat",))
    p4 = pooled(d, "log_mae", tail=True)
    praw = [p1.get("p_one_sided_negative", 1.0), *(r["p"] if r.get("evaluable") and np.isfinite(r["p"]) else 1.0
                                                   for r in (p2, p3, p4))]
    adj = C2.holm(praw)
    neg = [p1.get("mean_rho", 0) < 0] + [r.get("coef_X", 0) < 0 for r in (p2, p3, p4)]
    out.update({"p_raw": praw, "p_holm": adj, "P1": p1, "P2": p2, "P3": p3, "P4": p4})
    for i in range(4):
        out[f"P{i + 1}_pass"] = bool(neg[i] and adj[i] < ALPHA)
    # secondaries
    series = d.groupby("date")["M"].median()
    sym_med = d.groupby("symbol")["M"].median()
    pairs = d[d.date.isin(days)]
    named = stress_test(d, days=[STRESS_DAY_NAMED]) if STRESS_DAY_NAMED in set(d.date) else None
    named_rho = (named or {}).get("per_day", {}).get(STRESS_DAY_NAMED)
    out["secondary"] = {
        "stress_with_n_hat_control": stress_test(d, controls=CONTROLS + ["n_hat"], days=days),
        "stress_no_controls": stress_test(d, controls=[], days=days),
        "stress_branching_ratio": stress_test(d, x="n_hat", days=days),
        "stress_2025_10_10": {"in_sample": STRESS_DAY_NAMED in set(d.date), "rho": named_rho,
                              "rank_of_median_mae": int(list(med.index).index(STRESS_DAY_NAMED)) + 1
                              if STRESS_DAY_NAMED in med.index else None},
        "median_margin_percentile_on_stress_days": float(np.median([(series < series[x]).mean() for x in days if x in series.index])),
        "share_pairs_margin_below_symbol_median": float((pairs["M"] < pairs["symbol"].map(sym_med)).mean()),
        "P2_rank": pooled(d, "log_rv", "M_rank"), "P3_rank": pooled(d, "log_rv", "M_rank", extra=("n_hat",)),
        "P4_rank": pooled(d, "log_mae", "M_rank", tail=True),
        "mae_forecast": pooled(d, "log_mae"), "n_hat_alone_rv": pooled(d, "log_rv", x_only="n_hat"),
        "median_n_hat": float(d["n_hat"].median()), "share_windows_negative_margin": float((d["M"] < 0).mean())}
    return out


def numbers_tex(e):
    if e["void"]:
        return "% generated by s1_fragility.py\n\\newcommand{\\SoneVoid}{void}\n"
    v = lambda k: "passed" if e[k] else "failed"
    L = ["% generated by s1_fragility.py; do not edit",
         f"\\newcommand{{\\SoneSymbols}}{{{e['n_evaluable']}}}\\newcommand{{\\SoneStress}}{{{e['P1']['n_days']}}}",
         "\\newcommand{\\SoneRho}{%.3f}\\newcommand{\\SoneRhoNeg}{%d}" % (e["P1"]["mean_rho"], e["P1"]["n_negative"]),
         "\\newcommand{\\SoneRvT}{%.2f}\\newcommand{\\SoneHawkesT}{%.2f}\\newcommand{\\SoneTailT}{%.2f}" % tuple(
             e[k]["clark_west_t_by_date"] for k in ("P2", "P3", "P4")),
         "\\newcommand{\\SonePholm}{%s}" % ", ".join("%.3g" % p for p in e["p_holm"]),
         f"\\newcommand{{\\SonePone}}{{{v('P1_pass')}}}\\newcommand{{\\SonePtwo}}{{{v('P2_pass')}}}",
         f"\\newcommand{{\\SonePthree}}{{{v('P3_pass')}}}\\newcommand{{\\SonePfour}}{{{v('P4_pass')}}}"]
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------------------------------- gate and run
PIPELINE = (("s1_sha256", "s1_fragility.py"), ("c3_sha256", "c3_margin_more_days.py"),
            ("c2_sha256", "c2_margin_vs_identify.py"), ("pilot4_sha256", "pilot4_curve_and_risk.py"),
            ("binance_vision_sha256", "binance_vision.py"))


def gate(skip=False):
    if skip:
        return None, None, None
    assert SPEC.exists(), "Test S1 is a draft and is not registered; it cannot be run"
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    spec = json.loads(SPEC.read_text())
    for key, f in PIPELINE:
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == spec[key], f"{f} changed after registration"
    reg = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", str(SPEC.relative_to(ROOT))], cwd=ROOT, text=True).strip()
    assert reg, "the specification is not committed"
    return spec, sha, reg


def run(cache_dir=None, threads=16, resume=False, skip_gate=False):
    spec, sha, reg = gate(skip_gate)
    if not skip_gate:
        c = json.loads(COUNTER.read_text())
        if resume:
            assert c["opens"] == 1, "nothing to resume"
        else:
            assert c["opens"] == 0, "Test S1 was already opened; it runs once"
            COUNTER.write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": reg,
                                           "opened_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
    syms = json.loads(UNIVERSE.read_text())["symbols"] if (resume and UNIVERSE.exists()) else universe()
    print("universe:", syms, flush=True)
    days_by = load(cache_dir, syms, dates(), threads)
    per, rows = {}, []
    for s in syms:
        days = days_by.get(s, [])
        if len(days) < C3.MIN_VALID_DAYS:
            per[s] = {"n_days": len(days), "excluded": "fewer than 200 valid days"}; continue
        r = rows_for(s, days); rows += r
        per[s] = {"n_days": len(days), "n_rows": len(r)}
        print(f"  {s}: valid days={len(days)} rows={len(r)}", flush=True)
    d = pd.DataFrame(rows)
    n_ev = sum("excluded" not in v for v in per.values())
    res = {"test": "S1", "spec_sha256": sha, "registration_commit": reg, "run_utc": datetime.now(timezone.utc).isoformat(),
           "symbols": syms, "per_symbol": per, "evaluation": evaluate(d, n_ev)}
    RESULT.write_text(json.dumps(res, indent=1, default=float) + "\n")
    d.to_csv(ROWS, index=False, float_format="%.6g")
    NUMBERS.write_text(numbers_tex(res["evaluation"]))
    pd.Series([json.dumps(x) for x in bv.DL_LOG]).to_csv(DLLOG, index=False, header=False)
    print(json.dumps({k: v for k, v in res["evaluation"].items() if k != "secondary"}, indent=1, default=float))
    return res


# --------------------------------------------------------------------------------------------------------- selftest
def selftest():
    rng = np.random.default_rng(7)
    # 1. the day builder's close and flow equal binance_vision's, on a synthetic kline file
    t0 = int(pd.Timestamp("2025-03-01", tz="UTC").timestamp()) * 1000
    k = pd.DataFrame({"open_time": t0 + 60000 * np.arange(1440), "open": 1.0, "high": 1.0, "low": 1.0,
                      "close": 1 + np.cumsum(rng.normal(0, 1e-3, 1440)), "volume": 1.0, "close_time": 0,
                      "quote_volume": rng.uniform(1, 2, 1440), "count": rng.poisson(30, 1440), "taker_buy_volume": 0.5,
                      "taker_buy_quote_volume": rng.uniform(0, 1, 1440), "ignore": 0})
    import io, zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("x.csv", k.to_csv(index=False, header=False))
    orig = bv.fetch
    bv.fetch = lambda ds, s, dd: buf.getvalue()
    try:
        mine = build("XUSDT", "2025-03-01"); ref, _ = bv.build_day("XUSDT", "2025-03-01", depth=False)
    finally:
        bv.fetch = orig
    assert np.allclose(mine["close"], ref["close"]) and np.allclose(mine["flow"], ref["flow"])
    assert np.allclose(mine["count"], k["count"])
    # 2. the INAR branching ratio recovers a planted value
    n_true, T = 0.6, 20 * 1440; c = np.zeros(T); lam0 = 5.0
    for t in range(T):
        c[t] = rng.poisson(lam0 + n_true * c[max(0, t - 3):t].mean() if t else lam0)
    A = sum(hawkes_stats(c[i * 1440:(i + 1) * 1440])[0] for i in range(20))
    b = sum(hawkes_stats(c[i * 1440:(i + 1) * 1440])[1] for i in range(20))
    nh = float(np.linalg.solve(A, b).sum()); print("planted n=0.6, INAR estimate", round(nh, 3))
    assert abs(nh - n_true) < 0.08
    # 3. the full pipeline on noise: evaluable, nothing planted
    per = {}
    dts = pd.date_range("2025-01-01", periods=240).strftime("%Y-%m-%d")
    for j in range(22):
        days = []
        for dd in dts:
            p = np.cumsum(rng.normal(0, 3, 1440)); fl = rng.normal(0, 1, 1440) * 0.01
            p = p - 0.5 * (p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy())
            r = record(pd.DataFrame({"close": 100 * np.exp(p / 1e4), "flow": fl, "count": rng.poisson(20, 1440)}), dd)
            if r is not None:
                days.append(r)
        per[f"S{j}"] = days
    rows = sum((rows_for(s, v) for s, v in per.items()), [])
    e = evaluate(pd.DataFrame(rows), len(per))
    print(json.dumps({k: e.get(k) for k in ("n_evaluable", "void", "p_raw", "P1_pass", "P2_pass", "P3_pass", "P4_pass")}))
    assert not e["void"] and len(e["stress_days"]) == K_STRESS and numbers_tex(e).startswith("%")
    # 4. planted effects are detected: common shock amplified by 1/M, variance and tails rising as M falls
    rr = []
    for j in range(30):
        w = rng.normal(0, 1, 400).cumsum(); M = 0.3 + 0.15 * (w - w.mean()) / w.std()
        v = rng.normal(0, 1, 400); nh = rng.normal(0.5, 0.1, 400)
        for t in range(400):
            shock = 3.0 if t % 37 == 0 else 0.0
            rr.append({"symbol": f"S{j}", "t": t, "date": str(pd.Timestamp("2025-01-01") + pd.Timedelta(days=t))[:10],
                       "M": M[t], "n_hat": nh[t], "log_rv_lag": v[t], "log_rv_trail": 0.5 * v[t] + 0.5 * rng.normal(),
                       "log_rv": 0.3 * v[t] - 1.5 * (M[t] - 0.3) + rng.normal(0, 0.5),
                       "log_mae": 0.3 * v[t] + shock * (1 - 2 * (M[t] - 0.3)) - 2.0 * (M[t] - 0.3) + rng.normal(0, 0.5)})
    pdx = pd.DataFrame(rr); ep = evaluate(pdx, 30)
    print("planted:", json.dumps({k: ep[k] for k in ("p_raw", "P1_pass", "P2_pass", "P3_pass", "P4_pass")}))
    assert ep["P1_pass"] and ep["P2_pass"] and ep["P3_pass"] and ep["P4_pass"]
    try:
        gate()
        raise SystemExit("gate should refuse an unregistered draft")
    except AssertionError as err:
        print("gate refuses as expected:", err)
    print("selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
