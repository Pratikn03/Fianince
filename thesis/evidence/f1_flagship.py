"""Test F1 (DRAFT until registered): the flagship test of "certify, don't identify" on symbols never used.

One universe, one estimator, three registered predictions (Holm across them):
  P1  certification works: the stability margin M = 1 - a - kappa*Phi is decided (95% day-bootstrap interval excludes 0)
      in at least 75% of evaluable symbols (one-sided binomial p < 0.05);
  P2  identification fails where certification succeeds: b = #(decided, not identified) > c = #(identified, not
      decided), exact one-sided McNemar p < 0.05;
  P3  the certificate carries information about risk: the margin estimated on the previous 20 valid days forecasts the
      next valid day's maximum adverse excursion (log(1 + bp)) beyond volatility. Design (fixed from the exploratory
      Pilot 4b on the spent C3 symbols, where all four of its pre-declared variants passed): symbol fixed effects and
      pooled slopes on log(1 + RV) of the previous day and of the trailing 20 days, fitted on the first 60% of each
      symbol's rolling observations; the margin winsorized at the 5th and 95th percentiles of the training data;
      forecasts on the remaining 40%. P3 holds if the pooled coefficient on the margin is negative (lower margin, larger
      adverse move) and the one-sided Clark-West test of adding the margin, with the loss differentials averaged within
      each calendar date before the t-statistic (so that symbols sharing a date are not counted as independent), has
      p < 0.05.
Secondary: the same forecast for realized variance and with the margin's within-symbol rank; the learning curve (margin
decided and memories identified on the first 60, 120, 240 and all valid days, and the slope of log|z| on log n); the
decision on the first 105 valid days; the decision without feedback; contrarian count; safe and unsafe counts.
Not a primary: the per-symbol growth of the standardized margin, which Pilot 4 found positive in only 11 of 25 symbols
because margins drift; it is reported as a secondary.

Universe, dates, valid-day rule and estimators: C3's, with seed 20261105 and a universe drawn from symbols absent from
every text file of the repository (this excludes every symbol of E1v2, D1, the pilots, C2 and C3).
"""
import argparse
import hashlib
import json
import math
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
SPEC = THESIS / "checks/prereg/F1_flagship.json"
COUNTER = THESIS / "checks/prereg/F1_unlock.json"
RESULT = HERE / "F1_results.json"
NUMBERS = THESIS / "checks/F1_numbers.tex"
DLLOG = HERE / "F1_download_log.json"
UNIVERSE = HERE / "F1_universe.json"

SEED, N_SYMBOLS = 20261105, 30
CURVE_NS = (60, 120, 240)
W_RISK, FIT_SHARE = 20, 0.6
SHARE, ALPHA = 0.75, 0.05


def universe():
    allsyms = C2.list_archive_symbols()
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
    u = {"rule": "USDT perpetuals in the archive, absent from every repository text file, klines on 2025-01-04 and "
                 "2026-09-23, seeded random order", "seed": SEED, "n_archive": len(allsyms), "n_candidates": len(cand),
         "n_unused": len(unused), "checked_in_order": checked, "symbols": chosen,
         "written_utc": datetime.now(timezone.utc).isoformat()}
    UNIVERSE.write_text(json.dumps(u, indent=1) + "\n")
    return chosen


def load(cache_dir, symbols, dates, threads=16):
    """Day records with their dates, in date order (Pilot 4's record: C3's valid-day statistics plus outcomes)."""
    per = {s: [] for s in symbols}
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(bv.get_day, s, d, cache_dir, False): (s, d) for s in symbols for d in dates}
        for i, f in enumerate(as_completed(futs)):
            s, d = futs[f]
            try:
                df, _ = f.result()
            except Exception as err:
                print("  download error", s, d, repr(err)[:100], flush=True); df = None
            if df is not None:
                r = P4.day_record(df)
                if r is not None:
                    r["date"] = d; per[s].append(r)
            if (i + 1) % 2000 == 0:
                print(f"  {i + 1}/{len(futs)} symbol-days", flush=True)
    return {s: sorted(v, key=lambda r: r["date"]) for s, v in per.items()}


def symbol_eval(days, j):
    full = C3.symbol_eval([{k: d[k] for k in ("k_ret", "price", "k_x")} for d in days], j)
    curve, zs, ns = {}, [], []
    for n in CURVE_NS + (len(days),):
        if n <= len(days):
            st = P4.stats_of(days[:n], j, salt=n)
            curve[str(n)] = {"decided": st["decided"], "identified": st["identified"], "z": st["z"]}
            if np.isfinite(st["z"]) and st["z"] != 0:
                ns.append(n); zs.append(abs(st["z"]))
    slope = float(np.polyfit(np.log(ns), np.log(zs), 1)[0]) if len(ns) >= 3 else np.nan
    return {**full, "curve": curve, "z_slope": slope}


def risk_rows(sym, days):
    S = C3.stack([{k: d[k] for k in ("k_ret", "price", "k_x")} for d in days])
    rows = []
    for t in range(W_RISK, len(days)):
        M, _, _ = P4.point_margin(S, t - W_RISK, t)
        past = [days[s]["y"]["rv"] for s in range(t - W_RISK, t)]
        rows.append({"symbol": sym, "t": t, "date": days[t].get("date", str(t)), "M": M,
                     "log_mae": np.log1p(days[t]["y"]["mae"]), "log_rv": np.log1p(days[t]["y"]["rv"]),
                     "log_rv_lag": np.log1p(days[t - 1]["y"]["rv"]), "log_rv_trail": np.log1p(np.mean(past))})
    return rows


def pooled_forecast(d, y, xcol):
    """Pilot 4b's pooled out-of-sample design, with Clark-West differentials averaged within calendar dates."""
    d = d.dropna(subset=[y, "M", "log_rv_lag", "log_rv_trail"]).copy()
    if d.empty:
        return {"evaluable": False}
    d["n_sym"] = d.groupby("symbol")["t"].transform("count")
    d["rank_t"] = d.groupby("symbol")["t"].rank(method="first")
    d["train"] = d["rank_t"] <= FIT_SHARE * d["n_sym"]
    tr, te = d[d.train].copy(), d[~d.train].copy()
    if len(tr) < 100 or len(te) < 100:
        return {"evaluable": False}
    if xcol == "M_rank":
        for s, g in tr.groupby("symbol"):
            ref = np.sort(g["M"].to_numpy())
            tr.loc[g.index, "X"] = np.searchsorted(ref, g["M"].to_numpy(), side="right") / len(ref)
            idx = te.index[te.symbol == s]
            te.loc[idx, "X"] = np.searchsorted(ref, te.loc[idx, "M"].to_numpy(), side="right") / len(ref)
    else:
        lo, hi = tr["M"].quantile(0.05), tr["M"].quantile(0.95)
        tr["X"] = tr["M"].clip(lo, hi); te["X"] = te["M"].clip(lo, hi)
    te = te.dropna(subset=["X"])
    base = ["log_rv_lag", "log_rv_trail"]

    def fit(cols):
        Z = tr[[y] + cols]; means = Z.groupby(tr["symbol"]).transform("mean")
        b = np.linalg.lstsq((Z[cols] - means[cols]).to_numpy(), (Z[y] - means[y]).to_numpy(), rcond=None)[0]
        fe = (tr[y] - tr[cols].to_numpy() @ b).groupby(tr["symbol"]).mean()
        return te["symbol"].map(fe).to_numpy() + te[cols].to_numpy() @ b, b
    f0, _ = fit(base); f1, b1 = fit(base + ["X"]); yy = te[y].to_numpy()
    cw = pd.Series((yy - f0) ** 2 - ((yy - f1) ** 2 - (f0 - f1) ** 2), index=te.index)
    by_date = cw.groupby(te["date"]).mean()
    t_cw = float(by_date.mean() / (by_date.std(ddof=1) / np.sqrt(len(by_date)))) if len(by_date) > 2 else np.nan
    sst = float(((yy - tr[y].mean()) ** 2).sum())
    return {"evaluable": True, "n_train": int(len(tr)), "n_test": int(len(te)), "n_test_dates": int(len(by_date)),
            "coef_X": float(b1[-1]), "clark_west_t_by_date": t_cw, "p": float(stats.norm.sf(t_cw)),
            "delta_r2_pct": 100 * (float(((yy - f0) ** 2).sum()) - float(((yy - f1) ** 2).sum())) / sst}


def evaluate(per, rows):
    ev = {s: v for s, v in per.items() if v.get("n_days", 0) >= C3.MIN_VALID_DAYS and "M" in v}
    n = len(ev); out = {"n_evaluable": n, "void": n < C3.MIN_SYMBOLS}
    if out["void"]:
        return out
    dec = sum(v["decided"] for v in ev.values()); ident = sum(v["identified"] for v in ev.values())
    b = sum(v["decided"] and not v["identified"] for v in ev.values())
    c = sum(v["identified"] and not v["decided"] for v in ev.values())
    d = pd.DataFrame(rows)
    risk = pooled_forecast(d, "log_mae", "M_winsorized") if len(d) else {"evaluable": False}
    p1 = float(stats.binom.sf(dec - 1, n, 0.5))
    p2 = float(stats.binom.sf(b - 1, b + c, 0.5)) if b + c > 0 else 1.0
    p3 = risk["p"] if risk.get("evaluable") and np.isfinite(risk["p"]) else 1.0
    adj = C2.holm([p1, p2, p3]); need = math.ceil(SHARE * n)
    curve = {}
    for k in [str(x) for x in CURVE_NS] + ["all"]:
        vals = [v["curve"][k if k != "all" else str(v["n_days"])] for v in ev.values()
                if (k if k != "all" else str(v["n_days"])) in v["curve"]]
        curve[k] = {"n": len(vals), "decided": sum(x["decided"] for x in vals), "identified": sum(x["identified"] for x in vals)}
    out.update({"threshold_count": need, "decided": dec, "identified": ident, "mcnemar_b": b, "mcnemar_c": c,
                "p_raw": [p1, p2, p3], "p_holm": adj,
                "P1_pass": bool(dec >= need and adj[0] < ALPHA),
                "P2_pass": bool(b > c and adj[1] < ALPHA),
                "P3_pass": bool(risk.get("evaluable") and adj[2] < ALPHA and risk["coef_X"] < 0),
                "risk": risk,
                "secondary": {
                    "risk_rv_winsorized": pooled_forecast(d, "log_rv", "M_winsorized") if len(d) else None,
                    "risk_mae_rank": pooled_forecast(d, "log_mae", "M_rank") if len(d) else None,
                    "risk_rv_rank": pooled_forecast(d, "log_rv", "M_rank") if len(d) else None,
                    "curve": curve,
                    "z_slope_positive": sum((v["z_slope"] or 0) > 0 for v in ev.values() if np.isfinite(v["z_slope"])),
                    "median_z_slope": float(np.nanmedian([v["z_slope"] for v in ev.values()])),
                    "decided_first_105_days": sum(v["first_105"]["decided"] for v in ev.values()),
                    "same_decision_without_feedback": sum(v["sign"] == v["sign_nofeedback"] for v in ev.values()),
                    "feedback_negative": sum(v["kappa_Phi"] < 0 for v in ev.values()),
                    "safe": sum(v["sign"] == "safe" for v in ev.values()),
                    "unsafe": sum(v["sign"] == "unsafe" for v in ev.values())}})
    return out


def numbers_tex(e):
    if e["void"]:
        return "% generated by f1_flagship.py\n\\newcommand{\\FoneVoid}{void}\n"
    v = lambda k: "passed" if e[k] else "failed"
    r = e["risk"]
    L = ["% generated by f1_flagship.py; do not edit",
         f"\\newcommand{{\\FoneSymbols}}{{{e['n_evaluable']}}}\\newcommand{{\\FoneNeed}}{{{e['threshold_count']}}}",
         f"\\newcommand{{\\FoneDecided}}{{{e['decided']}}}\\newcommand{{\\FoneIdentified}}{{{e['identified']}}}",
         f"\\newcommand{{\\FoneB}}{{{e['mcnemar_b']}}}\\newcommand{{\\FoneC}}{{{e['mcnemar_c']}}}",
         f"\\newcommand{{\\FoneRiskT}}{{{r.get('clark_west_t_by_date', float('nan')):.2f}}}",
         f"\\newcommand{{\\FonePone}}{{{v('P1_pass')}}}\\newcommand{{\\FonePtwo}}{{{v('P2_pass')}}}",
         f"\\newcommand{{\\FonePthree}}{{{v('P3_pass')}}}"]
    return "\n".join(L) + "\n"


def gate(skip=False):
    if skip:
        return None, None, None
    assert SPEC.exists(), "Test F1 is a draft and is not registered; it cannot be run"
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    spec = json.loads(SPEC.read_text())
    for key, f in (("f1_sha256", "f1_flagship.py"), ("c3_sha256", "c3_margin_more_days.py"),
                   ("c2_sha256", "c2_margin_vs_identify.py"), ("pilot4_sha256", "pilot4_curve_and_risk.py"),
                   ("binance_vision_sha256", "binance_vision.py")):
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
            assert c["opens"] == 0, "Test F1 was already opened; it runs once"
            COUNTER.write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": reg,
                                           "opened_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
    syms = json.loads(UNIVERSE.read_text())["symbols"] if (resume and UNIVERSE.exists()) else universe()
    days_by = load(cache_dir, syms, C3.dates(), threads)
    per, rows = {}, []
    for j, s in enumerate(syms):
        days = days_by.get(s, [])
        if len(days) < C3.MIN_VALID_DAYS:
            per[s] = {"n_days": len(days), "excluded": "fewer than 200 valid days"}; continue
        per[s] = symbol_eval(days, j); rows += risk_rows(s, days)
        print(f"  {s}: valid days={len(days)} margin={per[s]['sign']} identified={per[s]['identified']}", flush=True)
    res = {"test": "F1", "spec_sha256": sha, "registration_commit": reg, "run_utc": datetime.now(timezone.utc).isoformat(),
           "symbols": syms, "per_symbol": per, "evaluation": evaluate(per, rows)}
    RESULT.write_text(json.dumps(res, indent=1, default=float) + "\n")
    NUMBERS.write_text(numbers_tex(res["evaluation"]))
    DLLOG.write_text(json.dumps(bv.DL_LOG, indent=0) + "\n")
    print(json.dumps(res["evaluation"], indent=1, default=float))
    return res


def selftest():
    rng = np.random.default_rng(6); per, rows = {}, []
    dates = pd.date_range("2025-01-01", periods=230).strftime("%Y-%m-%d")
    for j in range(20):
        days = []
        for d in range(230):
            T = 1440; p = np.cumsum(rng.normal(0, 3, T)); fl = rng.normal(0, 1, T) * 0.01
            p = p - 0.5 * (p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy())
            r = P4.day_record(pd.DataFrame({"close": 100 * np.exp(p / 1e4), "flow": fl}))
            if r is not None:
                r["date"] = dates[d]; days.append(r)
        per[f"S{j}"] = symbol_eval(days, j); rows += risk_rows(f"S{j}", days)
    e = evaluate(per, rows)
    print(json.dumps({k: e[k] for k in ("n_evaluable", "decided", "identified", "P1_pass", "P2_pass", "P3_pass")}),
          "risk:", json.dumps(e["risk"]))
    assert e["n_evaluable"] == 20 and e["P1_pass"] and not e["P3_pass"]          # no risk signal in noise
    # a planted signal must be detected, with dates shared across symbols
    rr = []
    for j in range(20):
        M = rng.normal(0, 1, 300).cumsum() * 0.05; v = rng.normal(0, 1, 300)
        for t in range(300):
            rr.append({"symbol": f"S{j}", "t": t, "date": str(t), "M": M[t], "log_rv_lag": v[t],
                       "log_rv_trail": 0.5 * v[t] + 0.5 * rng.normal(), "log_rv": 0.0,
                       "log_mae": 0.3 * v[t] - 0.4 * (M[t] - M.mean()) / (M.std() + 1e-9) + rng.normal(0, 1)})
    rk = pooled_forecast(pd.DataFrame(rr), "log_mae", "M_winsorized")
    print("planted signal:", json.dumps(rk))
    assert rk["p"] < 0.01 and rk["coef_X"] < 0
    assert numbers_tex(e).startswith("%")
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
