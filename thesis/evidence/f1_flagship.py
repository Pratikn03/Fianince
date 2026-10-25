"""Test F1 (DRAFT until registered): the flagship test of "certify, don't identify" on symbols never used.

One universe, one estimator, four registered predictions (Holm across them):
  P1  certification works: the stability margin M = 1 - a - kappa*Phi is decided (95% day-bootstrap interval excludes 0)
      in at least 75% of evaluable symbols (one-sided binomial p < 0.05);
  P2  identification fails where certification succeeds: b = #(decided, not identified) > c = #(identified, not
      decided), exact one-sided McNemar p < 0.05;
  P3  the learning curve of Theorem thm:passivecert: the standardized margin |z| grows with the sample, i.e. the slope of
      log|z| on log n over nested samples of 60, 120, 240 and all valid days is positive in at least 75% of evaluable
      symbols (binomial p < 0.05), while memories are identified in at most 20% of evaluable symbols with all days;
  P4  the certificate carries information about risk: in rolling windows of W valid days, the within-symbol rank of the
      estimated margin forecasts the next valid day's outcome Y beyond trailing volatility. Out of sample (first 60% of
      each symbol's days to fit, the rest to test), the pooled squared-error loss falls when the margin rank is added
      (one-sided Clark-West test across all test days, p < 0.05), and the pooled panel coefficient on the margin rank
      has the sign theory predicts (lower margin, higher risk: negative).
W, Y and the exact form of P4 are set from the exploratory Pilot 4 on the spent C3 symbols before registration.

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
W_RISK, Y_RISK = 60, "log_mae"          # set from Pilot 4 before registration
SHARE, ALPHA, MAX_ID_SHARE = 0.75, 0.05, 0.20


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


def symbol_eval(days, j):
    full = C3.symbol_eval([{k: d[k] for k in ("k_ret", "price", "k_x")} for d in days], j)
    zs, ns = [], []
    for n in CURVE_NS + (len(days),):
        if n <= len(days):
            st = P4.stats_of(days[:n], j, salt=n)
            if np.isfinite(st["z"]) and st["z"] != 0:
                ns.append(n); zs.append(abs(st["z"]))
    slope = float(np.polyfit(np.log(ns), np.log(zs), 1)[0]) if len(ns) >= 3 else np.nan
    return {**full, "z_curve": dict(zip(map(str, ns), zs)), "z_slope": slope}


def risk_rows(sym, days):
    S = C3.stack([{k: d[k] for k in ("k_ret", "price", "k_x")} for d in days])
    rows = []
    for t in range(W_RISK, len(days)):
        M, rev, kphi = P4.point_margin(S, t - W_RISK, t)
        past = [days[s]["y"]["rv"] for s in range(t - W_RISK, t)]
        rows.append({"symbol": sym, "t": t, "M": M, "y": np.log1p(days[t]["y"]["mae" if Y_RISK == "log_mae" else "rv"]),
                     "log_rv_lag": np.log1p(days[t - 1]["y"]["rv"]), "log_rv_trail": np.log1p(np.mean(past))})
    return rows


def risk_test(rows):
    d = pd.DataFrame(rows).dropna()
    if d.empty:
        return {"evaluable": False}
    d["M_rk"] = d.groupby("symbol")["M"].rank(pct=True)
    base = ["log_rv_lag", "log_rv_trail"]
    cw, n_test, sse0, sse1 = [], 0, 0.0, 0.0
    for _, g in d.groupby("symbol"):
        g = g.sort_values("t"); k = int(P4.FIT_SHARE * len(g))
        if k < 30 or len(g) - k < 20:
            continue
        tr, te = g.iloc[:k], g.iloc[k:]

        def pred(cols):
            X = np.column_stack([np.ones(len(tr))] + [tr[c] for c in cols]); b = np.linalg.lstsq(X, tr["y"], rcond=None)[0]
            return np.column_stack([np.ones(len(te))] + [te[c] for c in cols]) @ b
        f0, f1 = pred(base), pred(base + ["M_rk"]); y = te["y"].to_numpy()
        cw += list((y - f0) ** 2 - ((y - f1) ** 2 - (f0 - f1) ** 2)); n_test += len(te)
        sse0 += float(((y - f0) ** 2).sum()); sse1 += float(((y - f1) ** 2).sum())
    cw = np.asarray(cw)
    if len(cw) < 50:
        return {"evaluable": False}
    t_cw = float(cw.mean() / (cw.std(ddof=1) / np.sqrt(len(cw)))); p_cw = float(stats.norm.sf(t_cw))
    try:
        panel = P4.panel_fit(d.rename(columns={"y": "Y"}), "Y", base + ["M_rk"])
    except np.linalg.LinAlgError:
        panel = None
    coef = panel["coef"]["M_rk"] if panel else np.nan
    return {"evaluable": True, "n_test_days": n_test, "clark_west_t": t_cw, "p": p_cw,
            "oos_mse_ratio": sse1 / sse0 if sse0 > 0 else np.nan, "panel": panel, "coef_margin_rank": coef}


def evaluate(per, risk):
    ev = {s: v for s, v in per.items() if v.get("n_days", 0) >= C3.MIN_VALID_DAYS and "M" in v}
    n = len(ev); out = {"n_evaluable": n, "void": n < C3.MIN_SYMBOLS}
    if out["void"]:
        return out
    dec = sum(v["decided"] for v in ev.values()); ident = sum(v["identified"] for v in ev.values())
    b = sum(v["decided"] and not v["identified"] for v in ev.values())
    c = sum(v["identified"] and not v["decided"] for v in ev.values())
    pos = sum((v["z_slope"] or 0) > 0 for v in ev.values() if np.isfinite(v["z_slope"]))
    p1 = float(stats.binom.sf(dec - 1, n, 0.5))
    p2 = float(stats.binom.sf(b - 1, b + c, 0.5)) if b + c > 0 else 1.0
    p3 = float(stats.binom.sf(pos - 1, n, 0.5))
    p4 = risk["p"] if risk.get("evaluable") else 1.0
    adj = C2.holm([p1, p2, p3, p4]); need = math.ceil(SHARE * n)
    out.update({"threshold_count": need, "decided": dec, "identified": ident, "mcnemar_b": b, "mcnemar_c": c,
                "z_slope_positive": pos, "median_z_slope": float(np.nanmedian([v["z_slope"] for v in ev.values()])),
                "p_raw": [p1, p2, p3, p4], "p_holm": adj,
                "P1_pass": bool(dec >= need and adj[0] < ALPHA),
                "P2_pass": bool(b > c and adj[1] < ALPHA),
                "P3_pass": bool(pos >= need and adj[2] < ALPHA and ident <= MAX_ID_SHARE * n),
                "P4_pass": bool(risk.get("evaluable") and adj[3] < ALPHA and risk["coef_margin_rank"] < 0),
                "risk": risk,
                "secondary": {"same_decision_without_feedback": sum(v["sign"] == v["sign_nofeedback"] for v in ev.values()),
                              "feedback_negative": sum(v["kappa_Phi"] < 0 for v in ev.values()),
                              "safe": sum(v["sign"] == "safe" for v in ev.values()),
                              "decided_first_105_days": sum(v["first_105"]["decided"] for v in ev.values())}})
    return out


def numbers_tex(e):
    if e["void"]:
        return "% generated by f1_flagship.py\n\\newcommand{\\FoneVoid}{void}\n"
    v = lambda k: "passed" if e[k] else "failed"
    L = ["% generated by f1_flagship.py; do not edit",
         f"\\newcommand{{\\FoneSymbols}}{{{e['n_evaluable']}}}\\newcommand{{\\FoneNeed}}{{{e['threshold_count']}}}",
         f"\\newcommand{{\\FoneDecided}}{{{e['decided']}}}\\newcommand{{\\FoneIdentified}}{{{e['identified']}}}",
         f"\\newcommand{{\\FoneB}}{{{e['mcnemar_b']}}}\\newcommand{{\\FoneC}}{{{e['mcnemar_c']}}}",
         f"\\newcommand{{\\FoneSlopePos}}{{{e['z_slope_positive']}}}\\newcommand{{\\FoneSlope}}{{{e['median_z_slope']:.2f}}}",
         f"\\newcommand{{\\FonePone}}{{{v('P1_pass')}}}\\newcommand{{\\FonePtwo}}{{{v('P2_pass')}}}",
         f"\\newcommand{{\\FonePthree}}{{{v('P3_pass')}}}\\newcommand{{\\FonePfour}}{{{v('P4_pass')}}}"]
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
    days_by = P4.load(cache_dir, syms, C3.dates(), threads)
    per, rows = {}, []
    for j, s in enumerate(syms):
        days = days_by.get(s, [])
        if len(days) < C3.MIN_VALID_DAYS:
            per[s] = {"n_days": len(days), "excluded": "fewer than 200 valid days"}; continue
        per[s] = symbol_eval(days, j); rows += risk_rows(s, days)
        print(f"  {s}: valid days={len(days)} margin={per[s]['sign']} identified={per[s]['identified']} "
              f"z-slope={per[s]['z_slope']:.2f}", flush=True)
    res = {"test": "F1", "spec_sha256": sha, "registration_commit": reg, "run_utc": datetime.now(timezone.utc).isoformat(),
           "symbols": syms, "per_symbol": per, "evaluation": evaluate(per, risk_test(rows))}
    RESULT.write_text(json.dumps(res, indent=1, default=float) + "\n")
    NUMBERS.write_text(numbers_tex(res["evaluation"]))
    DLLOG.write_text(json.dumps(bv.DL_LOG, indent=0) + "\n")
    print(json.dumps(res["evaluation"], indent=1, default=float))
    return res


def selftest():
    rng = np.random.default_rng(6); per, rows = {}, []
    for j in range(20):
        days = []
        for d in range(260):
            T = 1440; p = np.cumsum(rng.normal(0, 3, T)); fl = rng.normal(0, 1, T) * 0.01
            p = p - 0.5 * (p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy())
            r = P4.day_record(pd.DataFrame({"close": 100 * np.exp(p / 1e4), "flow": fl}))
            if r is not None:
                days.append(r)
        per[f"S{j}"] = symbol_eval(days, j); rows += risk_rows(f"S{j}", days)
    e = evaluate(per, risk_test(rows))
    print(json.dumps({k: e[k] for k in ("n_evaluable", "decided", "identified", "z_slope_positive", "median_z_slope",
                                        "P1_pass", "P2_pass", "P3_pass", "P4_pass")}), "risk p:", e["risk"]["p"])
    assert e["n_evaluable"] == 20 and e["P1_pass"] and e["P3_pass"] and not e["P4_pass"]   # no risk signal in noise
    assert numbers_tex(e).startswith("%")
    # a planted risk signal must be detected: Y falls with the margin beyond volatility
    rr = []
    for j in range(20):
        M = rng.normal(0, 1, 300).cumsum() * 0.05; v = rng.normal(0, 1, 300)
        for t in range(300):
            rr.append({"symbol": f"S{j}", "t": t, "M": M[t], "log_rv_lag": v[t], "log_rv_trail": 0.5 * v[t] + 0.5 * rng.normal(),
                       "y": 0.3 * v[t] - 0.4 * (M[t] - M.mean()) / (M.std() + 1e-9) + rng.normal(0, 1)})
    rk = risk_test(rr)
    print("planted signal: p =", rk["p"], "coef =", rk["coef_margin_rank"])
    assert rk["p"] < 0.01 and rk["coef_margin_rank"] < 0
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
