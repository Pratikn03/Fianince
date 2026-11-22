"""Which exponent n belongs in Theorem n:paradox?  (Referee check, 21 November 2026.)

The theorem takes the supervisor's information to be J = c N D^n when one group sits at memory distance D from its
neighbour. This script computes, from the closed-form spectra, the Whittle Kullback--Leibler rate per observation
between the stationary price process of the economy in which the group sits at distance D and
  (a) the economy in which the group trades exactly like its neighbour (a simple null: the neighbour's memory and
      the two weights known),
  (b) the closest economy in which the group trades like its neighbour (a composite null: one group in place of the
      two, its memory and weight free; any other groups free too),
and fits the slope of log rate on log D. Model: x_t = a x_{t-1} + kappa sum_m k_m x_{t-1-m} + xi_t with
k_m = sum_c w_c r_c^m, so A(z) = 1 - a z - kappa z sum_c w_c / (1 - r_c z) and the spectral density is
sigma^2 / |A(e^{-i w})|^2. The rate is (1/4 pi) int [R - 1 - log R] dw with R = |A_null|^2 / |A_D|^2.
"""
import json
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

W_GRID = np.linspace(-np.pi, np.pi, 1 << 14, endpoint=False)
Z = np.exp(-1j * W_GRID)
A_PERS, KAPPA = 0.3, 0.5


def a_of(rates, weights):
    rates = np.asarray(rates, float)[:, None]
    weights = np.asarray(weights, float)[:, None]
    return 1 - A_PERS * Z - KAPPA * Z * np.sum(weights / (1 - rates * Z), axis=0)


def u_of(a_null, a_alt):
    # R - 1 with R = |A_null|^2/|A_alt|^2, computed as a difference to avoid cancellation
    return np.real((a_null - a_alt) * np.conj(a_null + a_alt)) / np.abs(a_alt) ** 2


def kl_rate(a_null, a_alt):
    u = u_of(a_null, a_alt)
    small = np.abs(u) < 1e-4
    val = np.where(small, u ** 2 / 2 - u ** 3 / 3 + u ** 4 / 4, u - np.log1p(np.where(small, 0.0, u)))
    return float(np.mean(val) / 2)          # (1/4pi) int over [-pi,pi] = mean / 2


def closest(alt_rates, alt_weights, start):
    """Minimize the rate over null economies with len(start)//2 groups (memories and weights free)."""
    a_alt = a_of(alt_rates, alt_weights)
    k = len(start) // 2

    def resid(p):
        return u_of(a_of(p[:k], p[k:]), a_alt) / 2          # sum of squares / len ~ rate to leading order

    best = None
    for jitter in (0.0, 1e-3, -1e-3):
        p0 = np.array(start, float); p0[:k] += jitter
        sol = least_squares(resid, p0, xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=20000, x_scale='jac')
        val = kl_rate(a_of(sol.x[:k], sol.x[k:]), a_alt)
        if best is None or val < best[0]:
            best = (val, sol.x)
    return best


def slope(ds, vals):
    return float(np.polyfit(np.log(ds), np.log(vals), 1)[0])


DS = 0.1 / 2 ** np.arange(0, 5)                     # D from 0.1 to 0.00625
out = {}

# Two groups: neighbour at 0.5 (weight 0.05), the group at 0.5 + D (weight 0.05).
simple, comp = [], []
for d in DS:
    alt_r, alt_w = [0.5, 0.5 + d], [0.05, 0.05]
    a_alt = a_of(alt_r, alt_w)
    simple.append(kl_rate(a_of([0.5], [0.10]), a_alt))
    comp.append(closest(alt_r, alt_w, [0.5 + d / 2, 0.10])[0])
out['two_groups'] = {'D': DS.tolist(), 'simple_null_rate': simple, 'composite_null_rate': comp,
                     'slope_simple': slope(DS, simple), 'slope_composite': slope(DS, comp)}

# Three groups: a third, separated group at 0.2 (weight 0.05) stays put; the null has two groups, all free.
comp3 = []
for d in DS:
    alt_r, alt_w = [0.2, 0.5, 0.5 + d], [0.05, 0.05, 0.05]
    comp3.append(closest(alt_r, alt_w, [0.2, 0.5 + d / 2, 0.05, 0.10])[0])
out['three_groups_one_moves'] = {'D': DS.tolist(), 'composite_null_rate': comp3, 'slope_composite': slope(DS, comp3)}

# For comparison only: a whole cluster of three at 0.5 + D(-1,0,1) against the closest two-group economy.
clus = []
for d in DS:
    alt_r, alt_w = [0.5 - d, 0.5, 0.5 + d], [0.05, 0.05, 0.05]
    clus.append(closest(alt_r, alt_w, [0.5 - 0.6 * d, 0.5 + 0.6 * d, 0.075, 0.075])[0])
out['cluster_of_three_shrinks'] = {'D': DS.tolist(), 'composite_null_rate': clus, 'slope_composite': slope(DS, clus)}

for key, v in out.items():
    line = ', '.join(f'{k}={v[k]:.3f}' for k in v if k.startswith('slope'))
    print(f'{key}: {line}')
    for name in [k for k in v if k.endswith('_rate')]:
        print('   ', name, ' '.join(f'{x:.3e}' for x in v[name]))
Path(__file__).with_name('exponent_check_output.json').write_text(json.dumps(out, indent=1))
