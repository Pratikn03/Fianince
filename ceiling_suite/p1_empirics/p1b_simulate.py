"""P1B simulation check (draft). Criteria are fixed here and in P1B_spec_DRAFT.md section 8 before any official run.

Usage:
  python p1b_simulate.py --preliminary            # literature prior, smoke seeds (not the official check)
  python p1b_simulate.py --calibration P1B_calibration.json   # official check, calibrated to pre-ban data only

The official run uses seeds SeedSequence([20261121, case_index, run]) and writes P1B_simulation_results.json.
"""
import argparse
import collections
import copy
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1b_core as B  # noqa: E402

warnings.filterwarnings("ignore", category=RuntimeWarning)

SESOI = 0.03     # smallest effect of interest: change in the 5-lag autocorrelation sum per s.d. of the class kernel
CONFOUND = 0.004  # per-lag change in other classes' feedback per s.d. of log size (0.02 in A per s.d.)

# name, kappa rule, kwargs, runs, requirement (None = reported only)
CASES = [
    ("null", 0.0, {}, 400, ("supportive", "<=", 0.07)),
    ("null_wrong_sign", 0.0, {}, 0, ("contradicted", "<=", 0.07)),     # same runs as 'null'
    ("null_size_confound", 0.0, {"confound": CONFOUND}, 400, ("supportive", "<=", 0.07)),
    ("sesoi", SESOI, {}, 400, ("supportive", ">=", 0.80)),
    ("sesoi_lag1", SESOI, {"lag_profile": "lag1"}, 100, None),
    ("sesoi_size_confound", SESOI, {"confound": CONFOUND}, 100, None),
    ("half_sesoi", SESOI / 2, {}, 100, None),
    ("double_sesoi", 2 * SESOI, {}, 100, None),
    ("late_lags_6_10", SESOI, {"lag_profile": "late"}, 100, None),
    ("treated_shift", 0.0, {"shift_sd": 0.01}, 100, None),
]


def params_from_calibration(path):
    P = copy.deepcopy(B.PRIOR)
    cal = json.loads(Path(path).read_text())["simulator"]
    for k, v in cal.items():
        if k == "days":
            P["days"].update(v)
        else:
            P[k] = tuple(v) if k == "garch" else v
    return P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calibration")
    ap.add_argument("--preliminary", action="store_true")
    ap.add_argument("--scale", type=float, default=1.0, help="fraction of runs (smoke tests only)")
    a = ap.parse_args()
    if bool(a.calibration) == bool(a.preliminary):
        raise SystemExit("choose --calibration FILE (official) or --preliminary")
    P = params_from_calibration(a.calibration) if a.calibration else copy.deepcopy(B.PRIOR)
    base = 20261121 if a.calibration else 777
    if a.calibration and a.scale != 1.0:
        raise SystemExit("the official check runs every case in full")
    results, rows = {}, []
    for ci, (name, theta, kw, runs, req) in enumerate(CASES):
        if runs == 0:
            continue
        kappa = theta / (5 * P["gamma_sd"]) if theta else 0.0
        n = max(5, int(runs * a.scale))
        verdicts, ts = collections.Counter(), []
        t0 = time.time()
        for i in range(n):
            rng = np.random.default_rng(np.random.SeedSequence([base, ci, i]))
            panel, W, _ = B.simulate(rng, P, kappa, **kw)
            st = B.run_statistics(panel, W)
            verdicts[st["verdict"]] += 1
            ts.append(st["t_K"])
        share = {k: v / n for k, v in verdicts.items()}
        results[name] = dict(runs=n, kappa=kappa, theta_true_per_sd=theta, verdict_shares=share,
                             mean_t=float(np.mean(ts)), sd_t=float(np.std(ts)), seconds=round(time.time() - t0, 1))
        print(name, results[name], flush=True)
    checks = []
    for name, theta, kw, runs, req in CASES:
        if req is None:
            continue
        src = "null" if name == "null_wrong_sign" else name
        val = results[src]["verdict_shares"].get(req[0], 0.0)
        ok = val <= req[2] if req[1] == "<=" else val >= req[2]
        checks.append(dict(case=name, statistic=f"share {req[0]}", value=val, required=f"{req[1]} {req[2]}", met=ok))
    passed = all(c["met"] for c in checks)
    out = dict(mode="official" if a.calibration else "preliminary (literature prior, smoke seeds; not the check)",
               params=P, sesoi=SESOI, results=results, checks=checks, design_passes=passed)
    name = "P1B_simulation_results.json" if a.calibration else "P1B_simulation_preliminary.json"
    Path(__file__).resolve().parent.joinpath(name).write_text(json.dumps(out, indent=1, default=float))
    print("\n".join(f"{c['case']}: {c['statistic']} = {c['value']:.3f} (required {c['required']}) "
                    f"{'met' if c['met'] else 'NOT MET'}" for c in checks))
    print("DESIGN", "PASSES" if passed else "FAILS")


if __name__ == "__main__":
    main()
