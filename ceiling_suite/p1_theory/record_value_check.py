"""Numerical check of Theorem 7.12(ii) (27 November 2026): in the Gaussian one-sided shift experiment of Theorem 7.11,
the crowding equilibrium's divergence J* = c N delta*^4 satisfies J* <= 16 k^4 delta0^4 / (L^4 beta^4 c N), so the
price record's value of information is at most V* sqrt(J*/2) <= 2 sqrt2 k^2 delta0^2 V* / (L^2 beta^2 sqrt(cN))."""
import json
from pathlib import Path

import numpy as np
from scipy.stats import norm

ALPHA, K, D0, L, C = 0.05, 1.0, 0.2, 1.0, 1.0
Z = norm.ppf(1 - ALPHA)
BETA = np.sqrt(2) * norm.pdf(Z)
JBAR = Z ** 2 / 2
assert L * BETA * np.sqrt(JBAR) > K * D0 ** 2, 'high stakes'

grid = np.linspace(1e-6, D0, 400001)
rows = []
for N in [1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8]:
    J = C * N * grid ** 4
    cost = K * (D0 - grid) ** 2 + L * norm.cdf(np.sqrt(2 * J) - Z)
    d = grid[np.argmin(cost)]
    Jstar = C * N * d ** 4
    bound_J = 16 * K ** 4 * D0 ** 4 / (L ** 4 * BETA ** 4 * C * N)
    tv_exact = 2 * norm.cdf(np.sqrt(Jstar / 2)) - 1          # TV of two unit-variance Gaussians at KL = Jstar
    tv_pinsker = np.sqrt(Jstar / 2)
    tv_bound = 2 * np.sqrt(2) * K ** 2 * D0 ** 2 / (L ** 2 * BETA ** 2 * np.sqrt(C * N))
    rows.append({'N': N, 'delta_star': float(d), 'J_star': float(Jstar), 'J_bound': float(bound_J),
                 'TV_exact': float(tv_exact), 'TV_pinsker': float(tv_pinsker), 'TV_bound': float(tv_bound),
                 'J_ok': bool(Jstar <= bound_J * (1 + 1e-9)), 'TV_ok': bool(tv_exact <= tv_pinsker <= tv_bound * (1 + 1e-9))})
    print(f"N={N:8.0e} delta*={d:.5f} J*={Jstar:.3e} <= {bound_J:.3e}  TV={tv_exact:.3e} <= {tv_pinsker:.3e} <= {tv_bound:.3e}")
lN = np.log([r['N'] for r in rows[3:]]); lT = np.log([r['TV_exact'] for r in rows[3:]])
slope = float(np.polyfit(lN, lT, 1)[0])
print('all bounds hold:', all(r['J_ok'] and r['TV_ok'] for r in rows), ' fitted slope of TV in log N (theory -1/2):', round(slope, 3))
Path(__file__).with_name('record_value_check_results.json').write_text(json.dumps(
    {'params': {'alpha': ALPHA, 'k': K, 'delta0': D0, 'L': L, 'c': C, 'beta': BETA}, 'rows': rows, 'tv_slope': slope}, indent=1))
