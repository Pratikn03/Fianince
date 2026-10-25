"""Test B1 (DRAFT until registered): supervising a market of learning agents and a vendor model from public data.

Simulation study for the thesis chapter and Paper B. Market and agents: ailoop_sim.py (unchanged after registration).
Designed after an exploratory pilot on seeds 101-110 and one inspection of seed 105 (reported as such). The registered run
uses seeds 1001-1100, never used before, and runs once.

Scenarios, each on seeds 1001-1100 (120 simulated days of 288 bars; 50 agents; window 10 days; 12 lags):
  control  no adoption (s_max = 0);
  fast     vendor model with memory r_D = 0.9 adopted by up to 80% of agents between days 24 and 96;
  slow     the same with a slow vendor model, r_D = 0.995.
Crisis day: first day whose largest |x| exceeds 10 times the standard deviation of x before adoption (or before day 24).
Warning rules on the daily rolling estimate (day-bootstrap interval, 100 draws):
  lost      the interval's lower end is at or below 0;
  buffer    the lower end is at or below 0.1;
  t2z       time to zero: the estimate is falling over the last 5 days and estimate / (-slope) < 10 days.
Estimators: standard (price and flow equations, 12 lags) and disclosed (flow equation augmented with EMA_rbar(x) at a
disclosed memory bound rbar = 0.995). Lead = crisis day - warning day (a warning after the crisis or none gives no lead).

Primaries (Holm across P2-P4 at 0.05; P1 is a pass/fail criterion):
  P1  specificity: in the 100 control runs the standard estimator's t2z rule fires in at most 5 runs;
  P2  early warning: over the 200 fast and slow runs with a crisis, the standard t2z rule fires before the crisis in at
      least 80% (one-sided binomial p against 1/2 below 0.05) and the median lead is at least 5 days;
  P3  value of disclosing a memory bound: in the slow runs, the disclosed estimator's buffer warning comes earlier than
      the standard estimator's buffer warning (exact one-sided sign test on the paired difference, p < 0.05) with a
      median gain of at least 5 days;
  P4  learning accelerates monoculture: in the fast and slow runs with a crisis, the adoption share at the crisis is
      below the static threshold of Proposition prop:monoculture computed with the learners frozen at the start of
      adoption, in at least 75% of runs (one-sided binomial p against 1/2 below 0.05).
Secondary: lead distributions for every rule and estimator; false alarms of every rule in the controls; tracking error
median |M_hat - M_true| on days with M_true > 0.2; median share at crisis and median static threshold.
"""
import argparse
import hashlib
import json
import math
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ailoop_sim as A  # noqa: E402

THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/B1_ailoop.json"
COUNTER = THESIS / "checks/prereg/B1_unlock.json"
RESULT = HERE / "B1_results.json"
NUMBERS = THESIS / "checks/B1_numbers.tex"
SEEDS = range(1001, 1101)
SCEN = {"control": dict(s_max=0.0), "fast": dict(r_D=0.9), "slow": dict(r_D=0.995)}
RBAR, BUF, K, H, ALPHA = 0.995, 0.1, 5, 10, 0.05


def warnings(track, disc=False):
    key, lo = ("M_hat_disc", "lo_disc") if disc else ("M_hat", "lo")
    lost = next((t["day"] for t in track if t[lo] <= 0), None)
    buf = next((t["day"] for t in track if t[lo] <= BUF), None)
    t2z = None
    for i in range(K, len(track)):
        slope = (track[i][key] - track[i - K][key]) / K
        if slope < 0 and track[i][key] / (-slope) < H:
            t2z = track[i]["day"]; break
    return {"lost": lost, "buffer": buf, "t2z": t2z}


def one(args):
    scen, seed = args
    cfg = A.Config(days=120, seed=seed, window=10, **SCEN[scen])
    r = A.run(cfg, rbar=RBAR)
    tr = r["track"]
    err = [abs(t["M_hat"] - t["M_true"]) for t in tr if t["M_true"] > 0.2]
    return {"scenario": scen, "seed": seed, "crisis": r["crisis_day"], "true0": r["true_margin_cross_day"],
            "share_at_crisis": r["share_at_crisis"], "s_star_static": r["s_star_static"],
            "std": warnings(tr), "disc": warnings(tr, True),
            "tracking_error_median": float(np.median(err)) if err else None}


def lead(r, est, rule):
    w, c = r[est][rule], r["crisis"]
    if c is None:
        return None
    return c - w if (w is not None and w < c) else 0


def evaluate(runs):
    ctrl = [r for r in runs if r["scenario"] == "control"]
    ramp = [r for r in runs if r["scenario"] != "control" and r["crisis"] is not None]
    slow = [r for r in ramp if r["scenario"] == "slow"]
    out = {"n_control": len(ctrl), "n_ramp_with_crisis": len(ramp), "n_ramp": sum(r["scenario"] != "control" for r in runs)}
    fa = sum(r["std"]["t2z"] is not None for r in ctrl)
    early = [lead(r, "std", "t2z") for r in ramp]; n_early = sum(x > 0 for x in early)
    p2 = float(stats.binom.sf(n_early - 1, len(ramp), 0.5)) if ramp else 1.0
    gain = [lead(r, "disc", "buffer") - lead(r, "std", "buffer") for r in slow]
    pos, neg = sum(g > 0 for g in gain), sum(g < 0 for g in gain)
    p3 = float(stats.binom.sf(pos - 1, pos + neg, 0.5)) if pos + neg else 1.0
    below = [r for r in ramp if r["s_star_static"] is not None and r["share_at_crisis"] is not None]
    n_below = sum(r["share_at_crisis"] < r["s_star_static"] for r in below)
    p4 = float(stats.binom.sf(n_below - 1, len(below), 0.5)) if below else 1.0
    adj = dict(zip(("P2", "P3", "P4"), _holm([p2, p3, p4])))
    out.update({
        "P1": {"false_alarms": fa, "pass": bool(fa <= 5)},
        "P2": {"early": n_early, "n": len(ramp), "share": n_early / len(ramp) if ramp else None,
               "median_lead": float(np.median(early)) if early else None, "p": p2, "p_holm": adj["P2"],
               "pass": bool(ramp and n_early >= math.ceil(0.8 * len(ramp)) and adj["P2"] < ALPHA and np.median(early) >= 5)},
        "P3": {"positive": pos, "negative": neg, "median_gain": float(np.median(gain)) if gain else None, "p": p3,
               "p_holm": adj["P3"], "pass": bool(gain and adj["P3"] < ALPHA and np.median(gain) >= 5)},
        "P4": {"below": n_below, "n": len(below), "share": n_below / len(below) if below else None, "p": p4,
               "p_holm": adj["P4"], "pass": bool(below and n_below >= math.ceil(0.75 * len(below)) and adj["P4"] < ALPHA)}})
    sec = {"false_alarms": {f"{e}_{k}": sum(r[e][k] is not None for r in ctrl) for e in ("std", "disc") for k in ("lost", "buffer", "t2z")},
           "median_leads": {f"{s}_{e}_{k}": float(np.median([lead(r, e, k) for r in ramp if r["scenario"] == s]))
                            for s in ("fast", "slow") for e in ("std", "disc") for k in ("lost", "buffer", "t2z")
                            if any(r["scenario"] == s for r in ramp)},
           "median_tracking_error": float(np.median([r["tracking_error_median"] for r in runs if r["tracking_error_median"] is not None])),
           "median_share_at_crisis": float(np.median([r["share_at_crisis"] for r in below])) if below else None,
           "median_static_threshold": float(np.median([r["s_star_static"] for r in below])) if below else None,
           "crisis_rate_ramp": len(ramp) / out["n_ramp"] if out["n_ramp"] else None}
    out["secondary"] = sec
    return out


def _holm(p):
    order = np.argsort(p); m = len(p); adj = np.empty(m); run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * p[i])); adj[i] = run
    return adj.tolist()


def numbers_tex(e):
    v = lambda k: "passed" if e[k]["pass"] else "failed"
    s = e["secondary"]
    return "\n".join(["% generated by b1_ailoop.py; do not edit",
                      f"\\newcommand{{\\BoneControl}}{{{e['n_control']}}}\\newcommand{{\\BoneRamp}}{{{e['n_ramp_with_crisis']}}}",
                      f"\\newcommand{{\\BoneFA}}{{{e['P1']['false_alarms']}}}",
                      "\\newcommand{\\BoneEarly}{%d}\\newcommand{\\BoneEarlyShare}{%.0f}\\newcommand{\\BoneLead}{%.1f}" % (
                          e["P2"]["early"], 100 * e["P2"]["share"], e["P2"]["median_lead"]),
                      "\\newcommand{\\BoneGain}{%.1f}\\newcommand{\\BonePos}{%d}\\newcommand{\\BoneNeg}{%d}" % (
                          e["P3"]["median_gain"], e["P3"]["positive"], e["P3"]["negative"]),
                      "\\newcommand{\\BoneBelow}{%d}\\newcommand{\\BoneBelowN}{%d}" % (e["P4"]["below"], e["P4"]["n"]),
                      "\\newcommand{\\BoneShareCrisis}{%.2f}\\newcommand{\\BoneStatic}{%.2f}" % (
                          s["median_share_at_crisis"], s["median_static_threshold"]),
                      f"\\newcommand{{\\BonePone}}{{{v('P1')}}}\\newcommand{{\\BonePtwo}}{{{v('P2')}}}"
                      f"\\newcommand{{\\BonePthree}}{{{v('P3')}}}\\newcommand{{\\BonePfour}}{{{v('P4')}}}"]) + "\n"


PIPELINE = (("b1_sha256", "b1_ailoop.py"), ("sim_sha256", "ailoop_sim.py"))


def gate(skip=False):
    if skip:
        return None, None, None
    assert SPEC.exists(), "Test B1 is a draft and is not registered"
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    spec = json.loads(SPEC.read_text())
    for key, f in PIPELINE:
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == spec[key], f"{f} changed after registration"
    reg = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", str(SPEC.relative_to(ROOT))], cwd=ROOT, text=True).strip()
    assert reg, "the specification is not committed"
    return spec, sha, reg


def run(workers=8, skip_gate=False, seeds=SEEDS):
    spec, sha, reg = gate(skip_gate)
    if not skip_gate:
        c = json.loads(COUNTER.read_text()); assert c["opens"] == 0, "Test B1 was already opened; it runs once"
        COUNTER.write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": reg,
                                       "opened_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
    jobs = [(s, seed) for seed in seeds for s in SCEN]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        runs = list(ex.map(one, jobs))
    res = {"test": "B1", "spec_sha256": sha, "registration_commit": reg, "run_utc": datetime.now(timezone.utc).isoformat(),
           "seeds": [min(seeds), max(seeds)], "runs": runs, "evaluation": evaluate(runs)}
    if not skip_gate:
        RESULT.write_text(json.dumps(res, indent=1, default=float) + "\n")
        NUMBERS.write_text(numbers_tex(res["evaluation"]))
    print(json.dumps({k: v for k, v in res["evaluation"].items() if k != "secondary"}, indent=1, default=float))
    return res


def selftest():
    res = run(workers=4, skip_gate=True, seeds=range(1, 3))        # seeds outside both the pilot and the registered set
    assert res["evaluation"]["n_control"] == 2 and numbers_tex(res["evaluation"]).startswith("%")
    try:
        gate(); raise SystemExit("gate should refuse an unregistered draft")
    except AssertionError as err:
        print("gate refuses as expected:", err)
    print("selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.run:
        run()
