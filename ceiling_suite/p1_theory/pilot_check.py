"""Numerical check of the pilot theorem (27 November 2026).

K = 2 groups at r_c -+ Delta (weights w1, w2). A restriction removes the group below the cutoff r_c. Reset contract:
each experiment records the first two kernel taps with N(0, sigma^2) noise, N_0 experiments before and N_1 under
the restriction. Pilot estimator: one-atom formulas w = k0, r = k1/k0 on the post taps (retained group) and on the
pre-minus-post taps (removed group). Benchmark: Prony on pre-restriction taps k0..k3 only (no pilot).
Prediction: pilot errors flat in Delta; no-pilot errors grow like Delta^-3.
"""
import json
from pathlib import Path

import numpy as np

RC, W1, W2, SIGMA, N = 0.5, 0.09, 0.11, 0.01, 4000
REPS = 400
rng = np.random.default_rng(20261127)


def taps(w, r, m):
    return np.array([np.sum(np.asarray(w) * np.asarray(r) ** j) for j in range(m)])


def prony2(k, d):
    from math import comb
    m = np.zeros(4)
    for j in range(4):
        m[j] = (k[j] - sum(comb(j, l) * RC ** (j - l) * d ** l * m[l] for l in range(j))) / d ** j
    H = np.array([[m[0], m[1]], [m[1], m[2]]])
    c = np.linalg.solve(H, -np.array([m[2], m[3]]))
    s = np.sort(np.roots([1.0, c[1], c[0]]).real)
    return np.linalg.solve(np.vstack([s ** 0, s ** 1]), m[:2])


rows = []
for d in [0.2, 0.1, 0.05, 0.02, 0.01]:
    r1, r2 = RC - d, RC + d
    pre, post = taps([W1, W2], [r1, r2], 4), taps([W2], [r2], 4)
    e_pilot, e_pre = [], []
    for _ in range(REPS):
        kpre = pre + SIGMA / np.sqrt(N) * rng.standard_normal(4)
        kpost = post + SIGMA / np.sqrt(N) * rng.standard_normal(4)
        diff = kpre - kpost
        w2h, w1h = kpost[0], diff[0]
        r2h, r1h = kpost[1] / kpost[0], diff[1] / diff[0]
        e_pilot.append(max(abs(w1h - W1), abs(w2h - W2)))
        try:
            wh = prony2(kpre, d)
            e_pre.append(min(1.0, max(abs(wh[0] - W1), abs(wh[1] - W2))))
        except np.linalg.LinAlgError:
            e_pre.append(1.0)
    rows.append({'delta': d, 'pilot_median_err': float(np.median(e_pilot)), 'no_pilot_median_err': float(np.median(e_pre))})
    print(f"Delta={d:5.2f}  pilot weight error {np.median(e_pilot):.2e}   prices-only Prony error {np.median(e_pre):.2e}")
ld = np.log([r['delta'] for r in rows])
sp = float(np.polyfit(ld, np.log([r['pilot_median_err'] for r in rows]), 1)[0])
ok = [r for r in rows if r['no_pilot_median_err'] < 0.05]
sn = float(np.polyfit(np.log([r['delta'] for r in ok]), np.log([r['no_pilot_median_err'] for r in ok]), 1)[0]) if len(ok) > 1 else None
print(f"slope in log Delta: pilot {sp:.2f} (theory 0); prices only {sn} (theory -3, before saturation)")
Path(__file__).with_name('pilot_check_results.json').write_text(json.dumps(
    {'params': {'r_c': RC, 'w': [W1, W2], 'sigma': SIGMA, 'N_each': N, 'reps': REPS}, 'rows': rows,
     'slope_pilot': sp, 'slope_no_pilot': sn}, indent=1))
