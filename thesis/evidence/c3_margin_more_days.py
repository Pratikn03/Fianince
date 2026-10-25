"""Test C3 (DRAFT until registered): is the safety margin decided once the sample is long enough?

Designed after Test C2 (registered, run once on 24 October 2026; Chapter 5). On 30 symbols never used before and 105 days
each, C2's Primary 1 failed by one symbol: the margin 1 - a - kappa*Phi was decided in 22 of 30 (23 needed). The theory
says the certificate's precision improves at the parametric rate, so the same question should be decided in more symbols
with more days. C3 asks it again, once, on 30 further symbols never used in this project and about 430 days each, with
the number of days chosen by a power calculation from C2's own results (in the specification). C2's Primary 2
(decided-but-not-identified outnumbers identified-but-not-decided) is replicated as a second primary.

Universe (fixed before any data are downloaded and written to C3_universe.json): Binance USD-M USDT perpetuals in the
public archive whose symbol string appears in no text file of the repository (this excludes every symbol of E1v2, D1,
the pilots and C2); klines must exist on 2025-01-04 and 2026-09-23; 30 drawn in a seeded random order (seed 20261103).
Dates: every day from 2025-01-01 to 2026-09-30 whose day of the month is not divisible by 3 (430 dates).
Valid day (new in C3, after C2 drew a symbol whose price did not move): at least half of the 287 five-minute returns are
non-zero and the day's taker flow is not identically zero. A symbol is evaluable with at least 200 valid days; the test
is void if fewer than 20 symbols are evaluable.

Estimators (C2's, unchanged): five-minute marks, pooled over days with day-demeaning; day bootstrap, 200 draws,
seed 20261103 + 101 j.
    price:    ret_t = kappa flow_t + beta x_{t-1},  x = p - EWMA(p, span 12 bars)
    kernel:   flow_t = sum_{m=1..12} k_m x_{t-m},   Phi = sum k_m;  margin M = -beta - kappa Phi
              DECIDED if its 95% interval excludes zero
    memories: two exponentials fitted to the 12-tap return kernel, rates in [0, 0.99]; IDENTIFIED if the interval of
              r_slow - r_fast excludes zero and no rate interval reaches 0.005 or 0.985
Primary 1: the margin is decided in at least 75% of evaluable symbols; one-sided binomial p (null 1/2) below 0.05.
Primary 2: b = #(decided, not identified) > c = #(identified, not decided), exact one-sided McNemar p below 0.05.
Holm across the two at 0.05.
Secondary: the same decision on each symbol's first 105 valid days (C2's sample size); the decision without the feedback
term and its agreement with the primary decision; contrarian feedback count; safe and unsafe counts.
What is mechanical: in C2 the decision rested mainly on the reversion term (same decision without feedback in 26 of 30).
A pass shows that the theory's safety question is decidable from public data with enough days while the memories are not;
it does not show that the feedback term is measured precisely.
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
import c2_margin_vs_identify as C2  # noqa: E402  (archive listing, repository scan and estimators, unchanged)

THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/C3_margin_more_days.json"
COUNTER = THESIS / "checks/prereg/C3_unlock.json"
RESULT = HERE / "C3_results.json"
NUMBERS = THESIS / "checks/C3_numbers.tex"
DLLOG = HERE / "C3_download_log.json"
UNIVERSE = HERE / "C3_universe.json"

SEED, N_SYMBOLS, L, SPAN, B_BOOT = 20261103, 30, 12, 12, 200
START, END = "2025-01-01", "2026-09-30"
MIN_VALID_DAYS, MIN_SYMBOLS, SHARE, ALPHA, C2_DAYS = 200, 20, 0.75, 0.05, 105
BLO, BHI = 0.005, 0.985


def dates():
    return [d.strftime("%Y-%m-%d") for d in pd.date_range(START, END, freq="D") if d.day % 3 != 0]


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


def day_stats(df):
    p1 = np.log(df["close"].to_numpy(float)) * 1e4
    fl = np.nan_to_num(df["flow"].to_numpy(float)); cf = np.concatenate([[0.0], np.cumsum(fl)])
    m = np.arange(5, 1440, 5)
    p, ret, flow = p1[m], p1[m] - p1[m - 5], cf[m + 1] - cf[m - 4]
    if not np.isfinite(p).all():
        return None
    if np.mean(ret != 0) < 0.5 or not np.any(flow != 0):          # valid-day rule
        return None
    x = p - pd.Series(p).ewm(span=SPAN, adjust=False).mean().to_numpy(); x[:SPAN] = np.nan
    out = {"k_ret": C2.ss(C2.lags(ret, L), flow), "price": C2.ss(np.column_stack([flow, np.r_[np.nan, x[:-1]]]), ret),
           "k_x": C2.ss(C2.lags(x, L), flow)}
    return out if all(v is not None for v in out.values()) else None


def stack(days):
    return {k: (np.stack([d[k][0] for d in days]), np.stack([d[k][1] for d in days])) for k in days[0]}


def decide(days, j, salt=0):
    rng = np.random.default_rng(SEED + 101 * j + salt); n = len(days); S = stack(days)
    W = np.vstack([np.ones(n)] + [np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(B_BOOT)]).astype(float)
    pr, kx, kr = C2.solve_w(S, "price", W), C2.solve_w(S, "k_x", W), C2.solve_w(S, "k_ret", W)
    kappa, beta = pr[:, 0], pr[:, 1]; Phi = kx.sum(1)
    M, M0 = -beta - kappa * Phi, -beta
    m_ci, m0_ci = C2.ci(M[1:]), C2.ci(M0[1:])
    sign = lambda c: "safe" if c[0] > 0 else "unsafe" if c[1] < 0 else "undecided"
    out = {"n_days": n, "M": float(M[0]), "M_ci": m_ci, "decided": bool(m_ci[0] > 0 or m_ci[1] < 0), "sign": sign(m_ci),
           "M_nofeedback_ci": m0_ci, "sign_nofeedback": sign(m0_ci), "kappa_Phi": float(kappa[0] * Phi[0])}
    return out, kr


def symbol_eval(days, j):
    out, kr = decide(days, j)
    rr = np.array([C2.exp_fit(k) for k in kr])
    rf, rs, dr = C2.ci(rr[1:, 0]), C2.ci(rr[1:, 1]), C2.ci(rr[1:, 1] - rr[1:, 0])
    inside = all(np.isfinite(v) and BLO < v < BHI for v in rf + rs)
    out.update({"r_fast_ci": rf, "r_slow_ci": rs, "delta_r_ci": dr, "inside_bounds": inside,
                "identified": bool(np.isfinite(dr[0]) and (dr[0] > 0 or dr[1] < 0) and inside)})
    first, _ = decide(days[:C2_DAYS], j, salt=7)
    out["first_105"] = {"decided": first["decided"], "sign": first["sign"], "M_ci": first["M_ci"]}
    return out


def evaluate(per):
    ev = {s: v for s, v in per.items() if v.get("n_days", 0) >= MIN_VALID_DAYS and "M" in v}
    n = len(ev); out = {"n_evaluable": n, "void": n < MIN_SYMBOLS}
    if out["void"]:
        return out
    dec = sum(v["decided"] for v in ev.values())
    b = sum(v["decided"] and not v["identified"] for v in ev.values())
    c = sum(v["identified"] and not v["decided"] for v in ev.values())
    p1 = float(stats.binom.sf(dec - 1, n, 0.5))
    p2 = float(stats.binom.sf(b - 1, b + c, 0.5)) if b + c > 0 else 1.0
    adj = C2.holm([p1, p2]); need = math.ceil(SHARE * n)
    out.update({"threshold_count": need, "decided": dec, "identified": sum(v["identified"] for v in ev.values()),
                "mcnemar_b": b, "mcnemar_c": c, "p_raw": [p1, p2], "p_holm": adj,
                "P1_pass": bool(dec >= need and adj[0] < ALPHA), "P2_pass": bool(b > c and adj[1] < ALPHA),
                "secondary": {"decided_first_105_days": sum(v["first_105"]["decided"] for v in ev.values()),
                              "same_decision_without_feedback": sum(v["sign"] == v["sign_nofeedback"] for v in ev.values()),
                              "feedback_negative": sum(v["kappa_Phi"] < 0 for v in ev.values()),
                              "safe": sum(v["sign"] == "safe" for v in ev.values()),
                              "unsafe": sum(v["sign"] == "unsafe" for v in ev.values()),
                              "median_valid_days": float(np.median([v["n_days"] for v in ev.values()]))}})
    return out


def numbers_tex(e):
    if e["void"]:
        return "% generated by c3_margin_more_days.py\n\\newcommand{\\CthreeVoid}{void}\n"
    L_ = ["% generated by c3_margin_more_days.py; do not edit",
          f"\\newcommand{{\\CthreeSymbols}}{{{e['n_evaluable']}}}\\newcommand{{\\CthreeNeed}}{{{e['threshold_count']}}}",
          f"\\newcommand{{\\CthreeDecided}}{{{e['decided']}}}\\newcommand{{\\CthreeIdentified}}{{{e['identified']}}}",
          f"\\newcommand{{\\CthreeB}}{{{e['mcnemar_b']}}}\\newcommand{{\\CthreeC}}{{{e['mcnemar_c']}}}",
          f"\\newcommand{{\\CthreeFirst}}{{{e['secondary']['decided_first_105_days']}}}",
          f"\\newcommand{{\\CthreePoneVerdict}}{{{'passed' if e['P1_pass'] else 'failed'}}}",
          f"\\newcommand{{\\CthreePtwoVerdict}}{{{'passed' if e['P2_pass'] else 'failed'}}}"]
    return "\n".join(L_) + "\n"


def gate(skip=False):
    if skip:
        return None, None, None
    assert SPEC.exists(), "Test C3 is a draft and is not registered; it cannot be run"
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    spec = json.loads(SPEC.read_text())
    for key, f in (("c3_sha256", "c3_margin_more_days.py"), ("c2_sha256", "c2_margin_vs_identify.py"),
                   ("binance_vision_sha256", "binance_vision.py")):
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == spec[key], f"{f} changed after registration"
    reg = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", str(SPEC.relative_to(ROOT))], cwd=ROOT, text=True).strip()
    assert reg, "the specification is not committed"
    return spec, sha, reg


def run(cache_dir=None, threads=16, resume=False, skip_gate=False, symbols=None, day_list=None):
    spec, sha, reg = gate(skip_gate)
    if not skip_gate:
        c = json.loads(COUNTER.read_text())
        if resume:
            assert c["opens"] == 1, "nothing to resume"
        else:
            assert c["opens"] == 0, "Test C3 was already opened; it runs once"
            COUNTER.write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": reg,
                                           "opened_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
    syms = symbols or (json.loads(UNIVERSE.read_text())["symbols"] if (resume and UNIVERSE.exists()) else universe())
    ds = day_list or dates()
    frames = {}
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(bv.get_day, s, d, cache_dir, False): (s, d) for s in syms for d in ds}
        for i, f in enumerate(as_completed(futs)):
            s, d = futs[f]
            try:
                df, _ = f.result()
            except Exception as err:
                print("  download error", s, d, repr(err)[:100], flush=True); df = None
            if df is not None:
                st = day_stats(df)
                if st is not None:
                    frames.setdefault(s, []).append((d, st))
            if (i + 1) % 500 == 0:
                print(f"  {i + 1}/{len(futs)} symbol-days", flush=True)
    per = {}
    for j, s in enumerate(syms):
        days = [st for _, st in sorted(frames.get(s, []), key=lambda t: t[0])]
        per[s] = symbol_eval(days, j) if len(days) >= MIN_VALID_DAYS else {"n_days": len(days),
                                                                           "excluded": "fewer than 200 valid days"}
        if "M" in per[s]:
            print(f"  {s}: valid days={len(days)} margin={per[s]['sign']} identified={per[s]['identified']} "
                  f"(first 105 days: {per[s]['first_105']['sign']})", flush=True)
    res = {"test": "C3", "spec_sha256": sha, "registration_commit": reg, "run_utc": datetime.now(timezone.utc).isoformat(),
           "symbols": syms, "dates": ds, "per_symbol": per, "evaluation": evaluate(per)}
    RESULT.write_text(json.dumps(res, indent=1, default=float) + "\n")
    NUMBERS.write_text(numbers_tex(res["evaluation"]))
    DLLOG.write_text(json.dumps(bv.DL_LOG, indent=0) + "\n")
    print(json.dumps(res["evaluation"], indent=1))
    return res


def selftest():
    rng = np.random.default_rng(3)
    per = {}
    for j in range(22):
        days = []
        for d in range(210 if j else 40):
            T = 1440; p = np.cumsum(rng.normal(0, 3, T)); fl = rng.normal(0, 1, T) * 0.01
            p = p - 0.5 * (p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy())
            if j == 1 and d % 2:
                p = np.zeros(T)                                   # a dead day must be dropped
            st = day_stats(pd.DataFrame({"close": 100 * np.exp(p / 1e4), "flow": fl}))
            if st is not None:
                days.append(st)
        per[f"S{j}"] = symbol_eval(days, j) if len(days) >= MIN_VALID_DAYS else {"n_days": len(days), "excluded": "few"}
    e = evaluate(per)
    print(json.dumps({k: e[k] for k in ("n_evaluable", "decided", "identified", "mcnemar_b", "mcnemar_c", "P1_pass", "P2_pass")}),
          json.dumps(e["secondary"]))
    assert e["n_evaluable"] == 20 and per["S1"].get("excluded") and per["S0"].get("excluded")
    assert len(dates()) == 430 and numbers_tex(e).startswith("%")
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
