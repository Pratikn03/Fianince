"""Test R1 (DRAFT until registered): does the horizon-limited absolute response measure risk where the margin did not?

Motivation. The stability margin was decided on three sets of new symbols (C2, C3, F1), but as a measure of risk it
failed: F1's registered forecast of the next day's largest adverse move from the margin failed (Clark-West t = 1.51), and
in the exploratory Pilot 7 the elasticity of adverse moves with respect to the amplification S = kappa/M was small and
negative (-0.13), not one. Theorem thm:absresp says why and what to use instead: when agents can be contrarian, the
summed response S does not bound worst-case loss, while the horizon-limited absolute response
Psi_H = sum_{t<=H} |h_t| does (a shock sequence of size w moves the displacement by at most w Psi_H within H steps, and
some sequence attains it), and Psi_H is certified from passive data at the parametric rate. R1 asks, once, on 40
perpetuals never used in this project (drawn only after Test S1's universe is committed, so the two cannot overlap),
whether the estimated Psi_H does what the margin did not.

Estimates for symbol s and day t, from the 20 valid days before t (within 30 calendar days; C3's valid-day rule; every
calendar day 2025-01-01 to 2026-09-30): C3's price equation gives impact kappa and reversion beta, C3's flow equation the
12-lag kernel k; the closed-loop response to a unit flow shock is h_1 = kappa, h_{n+1} = (1+beta) h_n +
kappa sum_{m<12} k_m h_{n-m}, and Psi_H = sum_{n<=H} |h_n| with H = 12 five-minute steps (one hour). The day's shock
size is the standard deviation of five-minute taker flow; its 20-day mean is the ex-ante shock. Outcomes on day t:
log(1 + maximum adverse excursion in bp), log(1 + RV).

Primaries (Holm across the three at 0.05):
  P1  Size. Within symbols, the next day's log(1 + MAE) rises with log Psi_H: 2SLS with symbol fixed effects, the
      20-day log Psi_H instrumented by its value from the 20 valid days before those (days t-40..t-21), controlling for
      the log ex-ante shock; holds if the elasticity is positive with one-sided p < 0.05 (standard errors clustered by
      date).
  P2  Forecast. F1's pooled out-of-sample design (symbol fixed effects, slopes on log(1 + RV) of the previous day and
      of the trailing 20 days, first 60% of each symbol's rows to fit, regressor winsorized at its training 5th and 95th
      percentiles, Clark-West differentials averaged within dates) with log Psi_H as the regressor and next-day
      log(1 + MAE) as the outcome; holds if the coefficient is positive and one-sided p < 0.05.
  P3  Beyond the margin. P2 with the winsorized margin M added to both the restricted and the full model; holds if the
      coefficient on log Psi_H is positive and p < 0.05.
Secondary: P1 and P2 for log(1 + RV); P1 with log S = log(kappa/M) instead (Pilot 7's regression on new symbols) and with
log S_H = log|sum_{n<=H} h_n|; P1 separately in symbols whose estimated feedback kappa*Phi is negative (contrarian) and
positive; H = 6 and 24; on S1's stress-day rule (20 worst market-wide days), the mean partial Spearman correlation
across symbols between log Psi_H and log(1 + MAE), controlling for the volatility terms; the median ratio Psi_H / |S_H|.
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
import s1_fragility as S1  # noqa: E402

THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/R1_absresp.json"
COUNTER = THESIS / "checks/prereg/R1_unlock.json"
RESULT = HERE / "R1_results.json"
ROWS = HERE / "R1_rows.csv.gz"
NUMBERS = THESIS / "checks/R1_numbers.tex"
DLLOG = HERE / "R1_download_log.json.gz"
UNIVERSE = HERE / "R1_universe.json"
S1_UNIVERSE = HERE / "S1_universe.json"

SEED, N_SYMBOLS = 20261109, 40
W, SPAN_DAYS, H, HS = 20, 30, 12, (6, 24)
EPS_M, ALPHA = 0.005, 0.05


# ----------------------------------------------------------------------------------------------------- data
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
    UNIVERSE.write_text(json.dumps({"rule": "ASCII USDT perpetuals absent from every repository text file (after S1's "
                                            "universe was committed), klines on 2025-01-04 and 2026-09-23, seeded order",
                                    "seed": SEED, "n_unused": len(unused), "checked_in_order": checked, "symbols": chosen,
                                    "written_utc": datetime.now(timezone.utc).isoformat()}, indent=1) + "\n")
    return chosen


def record(df, date):
    r = P4.day_record(df)
    if r is None:
        return None
    fl = np.nan_to_num(df["flow"].to_numpy(float)); cf = np.concatenate([[0.0], np.cumsum(fl)])
    m = np.arange(5, 1440, 5)
    r["date"] = date; r["flow_sd"] = float(np.std(cf[m + 1] - cf[m - 4]))
    return r


def load(cache_dir, symbols, ds, threads=16):
    per = {s: [] for s in symbols}
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(S1.get, s, d, cache_dir): (s, d) for s in symbols for d in ds}
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


# ----------------------------------------------------------------------------------------------------- estimates
def response(kappa, beta, k, n):
    h = np.zeros(n + 1); h[1] = kappa
    for t in range(1, n):
        lag = sum(k[m] * h[t - m] for m in range(len(k)) if t - m >= 1)
        h[t + 1] = (1 + beta) * h[t] + kappa * lag
    return h[1:]


def window(S, lo, hi):
    def solve(name):
        A = S[name][0][lo:hi].sum(0); b = S[name][1][lo:hi].sum(0)
        try:
            return np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            return np.full(b.shape, np.nan)
    pr, kx = solve("price"), solve("k_x")
    kappa, beta = pr[0], pr[1]; M = -beta - kappa * kx.sum()
    out = {"kappa": kappa, "M": M, "kphi": kappa * kx.sum()}
    if not np.all(np.isfinite(np.r_[pr, kx])):
        return {**out, **{f"Psi{n}": np.nan for n in (H,) + HS}, "SH": np.nan}
    h = response(kappa, beta, kx, max((H,) + HS))
    out.update({f"Psi{n}": float(np.abs(h[:n]).sum()) for n in (H,) + HS})
    out["SH"] = float(h[:H].sum())
    return out


def rows_for(sym, days):
    S = C3.stack([{k: d[k] for k in ("k_ret", "price", "k_x")} for d in days])
    dt = pd.to_datetime([d["date"] for d in days]); out = []
    for t in range(2 * W, len(days)):
        if (dt[t] - dt[t - W]).days > SPAN_DAYS:
            continue
        a = window(S, t - W, t); b = window(S, t - 2 * W, t - W)
        out.append({"symbol": sym, "t": t, "date": days[t]["date"], "M": a["M"], "kphi": a["kphi"], "kappa": a["kappa"],
                    **{f"Psi{n}": a[f"Psi{n}"] for n in (H,) + HS}, "SH": a["SH"], "Psi_lag": b[f"Psi{H}"],
                    "M_lag": b["M"], "kappa_lag": b["kappa"], "SH_lag": b["SH"],
                    "shock": float(np.mean([days[s]["flow_sd"] for s in range(t - W, t)])),
                    "log_mae": float(np.log1p(days[t]["y"]["mae"])), "log_rv": float(np.log1p(days[t]["y"]["rv"])),
                    "log_rv_lag": float(np.log1p(days[t - 1]["y"]["rv"])),
                    "log_rv_trail": float(np.log1p(np.mean([days[s]["y"]["rv"] for s in range(t - W, t)])))})
    return out


def add_logs(d):
    d = d.copy()
    pos = lambda c: np.where(d[c] > 0, d[c], np.nan)
    for n in (H,) + HS:
        d[f"logPsi{n}"] = np.log(pos(f"Psi{n}"))
    d["logPsi"] = d[f"logPsi{H}"]; d["logPsi_lag"] = np.log(pos("Psi_lag"))
    d["log_shock"] = np.log(pos("shock"))
    okS = (d.M > EPS_M) & (d.kappa > 0) & (d.M_lag > EPS_M) & (d.kappa_lag > 0)
    d["logS"] = np.where(okS, np.log(np.abs(d.kappa / d.M)), np.nan)
    d["logS_lag"] = np.where(okS, np.log(np.abs(d.kappa_lag / d.M_lag)), np.nan)
    d["logSH"] = np.log(np.where(np.abs(d.SH) > 0, np.abs(d.SH), np.nan))
    d["logSH_lag"] = np.log(np.where(np.abs(d.SH_lag) > 0, np.abs(d.SH_lag), np.nan))
    return d


# ----------------------------------------------------------------------------------------------------- statistics
def tsls(d, y, x, z, controls=("log_shock",)):
    d = d.replace([np.inf, -np.inf], np.nan).dropna(subset=[y, x, z, *controls])
    if len(d) < 100 or d.symbol.nunique() < 5:
        return {"evaluable": False, "n": int(len(d))}
    cols = [y, x, z, *controls]
    Z = d[cols] - d.groupby("symbol")[cols].transform("mean")
    X = Z[[x, *controls]].to_numpy(); Zi = Z[[z, *controls]].to_numpy(); yy = Z[y].to_numpy()
    Pz = Zi @ np.linalg.solve(Zi.T @ Zi, Zi.T @ X)
    b = np.linalg.solve(Pz.T @ X, Pz.T @ yy); e = yy - X @ b
    bread = np.linalg.inv(Pz.T @ X); k = X.shape[1]; meat = np.zeros((k, k))
    for _, g in pd.DataFrame({"date": d["date"].to_numpy(), "i": np.arange(len(d))}).groupby("date"):
        s_ = Pz[g["i"]].T @ e[g["i"]]; meat += np.outer(s_, s_)
    se = float(np.sqrt((bread @ meat @ bread.T)[0, 0])); t = float(b[0] / se)
    first = np.linalg.lstsq(Zi, X[:, 0], rcond=None)[0]
    fs_r2 = float(1 - np.var(X[:, 0] - Zi @ first) / np.var(X[:, 0]))
    return {"evaluable": True, "n": int(len(d)), "elasticity": float(b[0]), "se": se, "t": t,
            "p_one_sided_positive": float(stats.norm.sf(t)), "first_stage_r2": fs_r2,
            "elasticity_ols": float(np.linalg.lstsq(X, yy, rcond=None)[0][0])}


def forecast(d, y, extra=()):
    r = S1.pooled(d.replace([np.inf, -np.inf], np.nan), y, "M_winsorized", extra=extra, x_only="logPsi")
    if r.get("evaluable"):
        r["p_positive"] = r["p"]                         # S1.pooled's Clark-West p is one-sided for a gain
    return r


def evaluate(d, n_evaluable):
    out = {"n_evaluable": int(n_evaluable), "n_rows": int(len(d)), "void": bool(n_evaluable < C3.MIN_SYMBOLS)}
    if out["void"]:
        return out
    d = add_logs(d)
    p1 = tsls(d, "log_mae", "logPsi", "logPsi_lag")
    p2 = forecast(d, "log_mae")
    p3 = forecast(d, "log_mae", extra=("M",))
    pos = [p1.get("elasticity", -1) > 0, p2.get("coef_X", -1) > 0, p3.get("coef_X", -1) > 0]
    praw = [p1.get("p_one_sided_positive", 1.0) if p1.get("evaluable") else 1.0,
            p2["p"] if p2.get("evaluable") and np.isfinite(p2["p"]) else 1.0,
            p3["p"] if p3.get("evaluable") and np.isfinite(p3["p"]) else 1.0]
    adj = C2.holm(praw)
    out.update({"P1": p1, "P2": p2, "P3": p3, "p_raw": praw, "p_holm": adj,
                **{f"P{i + 1}_pass": bool(pos[i] and adj[i] < ALPHA) for i in range(3)}})
    sym_kphi = d.groupby("symbol")["kphi"].median()
    contr = d[d.symbol.map(sym_kphi) < 0]; mom = d[d.symbol.map(sym_kphi) > 0]
    days = S1.stress_days(d)[0]
    out["secondary"] = {
        "rv_size": tsls(d, "log_rv", "logPsi", "logPsi_lag"), "rv_forecast": forecast(d, "log_rv"),
        "logS_size": tsls(d, "log_mae", "logS", "logS_lag"), "logSH_size": tsls(d, "log_mae", "logSH", "logSH_lag"),
        "size_contrarian_symbols": tsls(contr, "log_mae", "logPsi", "logPsi_lag"),
        "size_momentum_symbols": tsls(mom, "log_mae", "logPsi", "logPsi_lag"),
        "logS_size_momentum_symbols": tsls(mom, "log_mae", "logS", "logS_lag"),
        "size_H6": tsls(d.assign(logPsi=d.logPsi6), "log_mae", "logPsi", "logPsi_lag"),
        "size_H24": tsls(d.assign(logPsi=d.logPsi24), "log_mae", "logPsi", "logPsi_lag"),
        "stress_partial_spearman": S1.stress_test(d.dropna(subset=["logPsi"]), x="logPsi", days=days),
        "median_ratio_Psi_to_abs_SH": float(np.nanmedian(d[f"Psi{H}"] / d.SH.abs())),
        "n_contrarian_symbols": int((sym_kphi < 0).sum()), "n_momentum_symbols": int((sym_kphi > 0).sum())}
    return out


def numbers_tex(e):
    if e["void"]:
        return "% generated by r1_absresp.py\n\\newcommand{\\RoneVoid}{void}\n"
    v = lambda k: "passed" if e[k] else "failed"
    g = lambda r, k: r.get(k, float("nan"))
    return "\n".join(["% generated by r1_absresp.py; do not edit",
                      f"\\newcommand{{\\RoneSymbols}}{{{e['n_evaluable']}}}",
                      "\\newcommand{\\RoneElast}{%.2f}\\newcommand{\\RoneElastSE}{%.2f}" % (g(e["P1"], "elasticity"), g(e["P1"], "se")),
                      "\\newcommand{\\RoneFcT}{%.2f}\\newcommand{\\RoneBeyondT}{%.2f}" % (
                          g(e["P2"], "clark_west_t_by_date"), g(e["P3"], "clark_west_t_by_date")),
                      f"\\newcommand{{\\RonePone}}{{{v('P1_pass')}}}\\newcommand{{\\RonePtwo}}{{{v('P2_pass')}}}"
                      f"\\newcommand{{\\RonePthree}}{{{v('P3_pass')}}}"]) + "\n"


# ----------------------------------------------------------------------------------------------------- gate and run
PIPELINE = (("r1_sha256", "r1_absresp.py"), ("s1_sha256", "s1_fragility.py"), ("c3_sha256", "c3_margin_more_days.py"),
            ("c2_sha256", "c2_margin_vs_identify.py"), ("pilot4_sha256", "pilot4_curve_and_risk.py"),
            ("binance_vision_sha256", "binance_vision.py"))


def gate(skip=False):
    if skip:
        return None, None, None
    assert SPEC.exists(), "Test R1 is a draft and is not registered; it cannot be run"
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    spec = json.loads(SPEC.read_text())
    for key, f in PIPELINE:
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == spec[key], f"{f} changed after registration"
    reg = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", str(SPEC.relative_to(ROOT))], cwd=ROOT, text=True).strip()
    assert reg, "the specification is not committed"
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(S1_UNIVERSE.relative_to(ROOT))], cwd=ROOT,
                             capture_output=True).returncode == 0
    assert tracked, "S1's universe is not committed yet; R1 waits so that the two tests cannot draw the same symbols"
    return spec, sha, reg


def run(cache_dir=None, threads=16, resume=False, skip_gate=False):
    spec, sha, reg = gate(skip_gate)
    if not skip_gate:
        c = json.loads(COUNTER.read_text())
        if resume:
            assert c["opens"] == 1, "nothing to resume"
        else:
            assert c["opens"] == 0, "Test R1 was already opened; it runs once"
            COUNTER.write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": reg,
                                           "opened_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
    syms = json.loads(UNIVERSE.read_text())["symbols"] if (resume and UNIVERSE.exists()) else universe()
    print("universe:", syms, flush=True)
    days_by = load(cache_dir, syms, S1.dates(), threads)
    per, rows = {}, []
    for s in syms:
        days = days_by.get(s, [])
        if len(days) < C3.MIN_VALID_DAYS:
            per[s] = {"n_days": len(days), "excluded": "fewer than 200 valid days"}; continue
        r = rows_for(s, days); rows += r; per[s] = {"n_days": len(days), "n_rows": len(r)}
        print(f"  {s}: valid days={len(days)} rows={len(r)}", flush=True)
    d = pd.DataFrame(rows)
    res = {"test": "R1", "spec_sha256": sha, "registration_commit": reg, "run_utc": datetime.now(timezone.utc).isoformat(),
           "symbols": syms, "per_symbol": per,
           "evaluation": evaluate(d, sum("excluded" not in v for v in per.values()))}
    RESULT.write_text(json.dumps(res, indent=1, default=float) + "\n")
    d.to_csv(ROWS, index=False, float_format="%.6g")
    NUMBERS.write_text(numbers_tex(res["evaluation"]))
    pd.Series([json.dumps(x) for x in bv.DL_LOG]).to_csv(DLLOG, index=False, header=False)
    print(json.dumps({k: v for k, v in res["evaluation"].items() if k != "secondary"}, indent=1, default=float))
    return res


# ----------------------------------------------------------------------------------------------------- selftest
def selftest():
    rng = np.random.default_rng(11)
    # 1. response: memory-zero contrarian cohort alternates, |S_H| < Psi_H; positive class S_H = Psi_H
    h = response(1.0, -0.1, np.array([-1.5]), 12); assert np.all(np.sign(h[1:]) != np.sign(h[:-1]))
    assert abs(h).sum() > abs(h.sum())
    hp = response(1.0, -0.3, np.array([0.1, 0.05]), 12); assert np.all(hp > 0) and abs(abs(hp).sum() - hp.sum()) < 1e-12
    # 2. the pipeline on simulated days: evaluable, and the estimated Psi tracks the true one
    per, dts = {}, pd.date_range("2025-01-01", periods=150).strftime("%Y-%m-%d")
    for j in range(21):
        days = []
        for dd in dts:
            pth = np.cumsum(rng.normal(0, 3, 1440)); fl = rng.normal(0, 1, 1440) * 0.01
            pth = pth - 0.5 * (pth - pd.Series(pth).ewm(span=60, adjust=False).mean().to_numpy())
            r = record(pd.DataFrame({"close": 100 * np.exp(pth / 1e4), "flow": fl}), dd)
            if r is not None:
                days.append(r)
        per[f"S{j}"] = days
    rows = sum((rows_for(s, v) for s, v in per.items()), [])
    e = evaluate(pd.DataFrame(rows), len(per))
    print(json.dumps({k: e.get(k) for k in ("n_evaluable", "p_raw", "P1_pass", "P2_pass", "P3_pass")}))
    assert not e["void"] and numbers_tex(e).startswith("%")
    # 3. planted effect: MAE = shock * Psi (log scale), Psi measured with error, lag a valid instrument
    n = 6000; sym = np.repeat([f"S{i}" for i in range(30)], n // 30); t = np.tile(np.arange(n // 30), 30)
    true = rng.normal(0, 0.4, n); shock = rng.normal(0, 0.3, n)
    d = pd.DataFrame({"symbol": sym, "t": t, "date": [str(x) for x in t], "logPsi": true + rng.normal(0, 0.4, n),
                      "logPsi_lag": true + rng.normal(0, 0.4, n), "log_shock": shock})
    d["log_mae"] = 1.0 * true + 1.0 * shock + rng.normal(0, 0.3, n)
    r = tsls(d, "log_mae", "logPsi", "logPsi_lag"); print("planted elasticity 1:", json.dumps(r))
    assert abs(r["elasticity"] - 1) < 0.15 and r["p_one_sided_positive"] < 0.01 and r["elasticity_ols"] < 0.75
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
