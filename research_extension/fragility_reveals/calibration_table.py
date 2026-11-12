"""Calibration of the passive barrier for Paper 1 (theory version): how much price data separates two populations
with the same kernel up to order 2K-2 (the Gauss / Gauss-Radau pair), at the parameters of the figure
(centre memory rate 0.5, total weight 0.3, impact 0.5), at a common feedback budget.

Lower bound used (Bretagnolle-Huber): for any test, P(error | A) + P(error | B) >= exp(-n KL) / 2, with KL the
per-observation Kullback-Leibler rate. Keeping both errors at 5% (sum 0.10) therefore needs n >= ln(5) / KL.
Run: python3 calibration_table.py -> calibration_table_results.json
"""
import json
import numpy as np
from fragility_scan import rules


def D(z, a, kappa, r, w):
    return z - a - kappa * np.sum(w[None, :] * z[:, None] / (z[:, None] - r[None, :]), axis=1)


def kl_rate(K, dEta, eps, rc=0.5, W=0.3, kappa=0.5, n=400001):
    """Same computation as make_barrier_figure.kl_rate (copied: that module draws the figure on import)."""
    (xg, wg), (xr, wr) = rules(K)
    rA, wA, rB, wB = rc + dEta * xg, W * wg, rc + dEta * xr, W * wr
    aA = 1 - eps - kappa * np.sum(wA / (1 - rA)); aB = 1 - eps - kappa * np.sum(wB / (1 - rB))
    om = np.concatenate([-np.logspace(-9, np.log10(np.pi), n // 2)[::-1], np.logspace(-9, np.log10(np.pi), n // 2)])
    z = np.exp(1j * om)
    u = np.abs(D(z, aA, kappa, rA, wA)) ** 2 / np.abs(D(z, aB, kappa, rB, wB)) ** 2
    return float(np.trapezoid(u - 1 - np.log(u), om) / (4 * np.pi))



BARS_DAILY, BARS_5MIN = 252, 288 * 365          # trading days a year; 5-minute bars a year in a 24-hour market
rows = []
for K in (2, 3):
    for d in (0.2, 0.1, 0.05):
        for margin in (0.1, 1e-6):
            kl = kl_rate(K, d, margin)
            n = np.log(5) / kl
            rows.append({"K": K, "spacing": d, "margin_1_minus_S": margin, "kl_per_obs": kl, "n_obs_5pct": n,
                         "years_daily": n / BARS_DAILY, "years_5min_24h": n / BARS_5MIN})
            print(f"K={K} spacing={d:<5} margin={margin:<6g} KL={kl:.3e} n={n:.3e} "
                  f"years(daily)={n / BARS_DAILY:.3e} years(5-min)={n / BARS_5MIN:.3e}")
json.dump({"parameters": {"rc": 0.5, "W": 0.3, "kappa": 0.5}, "rule": "n >= ln(5)/KL (Bretagnolle-Huber, both errors 5%)",
           "rows": rows}, open("calibration_table_results.json", "w"), indent=1)
