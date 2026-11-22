"""Numerical check of Proposition 7.1(iii) of the JEDC main text (restriction by horizon), 22 November 2026.

The hard pair of Theorem 5.1 (K-point Gauss-Legendre and Gauss-Radau rules with fixed node -1, normalized to unit
mass) is placed on r_c + d[-1, 1] with r_c = r_hat + (1 + x_K) d / 2, where x_K is the largest Gauss node. The check
confirms, for K = 2..6 and several spacings d:
  * the merged measures match moments 0..2K-2 (relative to the scale of the moments);
  * every memory lies in [r_hat - d, r_hat + 2d];
  * the Gauss-Radau economy has weight W/K^2 below r_hat and the Gauss economy none;
  * the budgets differ by O(d^(2K-1)) (fitted slope), while the restriction removes at least kappa W / K^2 in one
    economy and nothing in the other, so a nonempty interval of ceilings separates the two after the restriction.
Writes horizon_check_output.json next to this file. Drafted with AI assistance.
"""
import json
from pathlib import Path

import numpy as np
from numpy.polynomial import legendre as L

A, KAPPA, W, R_HAT = 0.3, 0.5, 0.3, 0.5


def gauss(K):
    x, w = L.leggauss(K)
    return x, w / w.sum()


def radau(K):
    # nodes: -1 and the roots of (P_{K-1} + P_K)/(1 + x); weights 2/K^2 and (1 - x)/(K^2 P_{K-1}(x)^2)
    c = np.zeros(K + 1)
    c[K - 1] += 1
    c[K] += 1
    q, _ = L.legdiv(c, [1, 1])
    inner = np.sort(np.real(L.legroots(q)))
    x = np.concatenate([[-1.0], inner])
    pk1 = L.legval(inner, np.eye(K)[K - 1])
    w = np.concatenate([[2.0 / K ** 2], (1 - inner) / (K ** 2 * pk1 ** 2)])
    return x, w / w.sum()


def check(K, d):
    xg, wg = gauss(K)
    xr, wr = radau(K)
    xK = xg.max()
    rc = R_HAT + (1 + xK) * d / 2
    rg, rr = rc + d * xg, rc + d * xr
    mg, mr = W * wg, W * wr
    moments = [abs(np.sum(mg * (rg - rc) ** j) - np.sum(mr * (rr - rc) ** j)) / (W * d ** j) for j in range(2 * K - 1)]
    budget_g = A + KAPPA * np.sum(mg / (1 - rg))
    budget_r = A + KAPPA * np.sum(mr / (1 - rr))
    removed_g = KAPPA * np.sum(mg[rg < R_HAT] / (1 - rg[rg < R_HAT]))
    removed_r = KAPPA * np.sum(mr[rr < R_HAT] / (1 - rr[rr < R_HAT]))
    after_g, after_r = budget_g - removed_g, budget_r - removed_r
    return {
        'K': K, 'd': d,
        'max_scaled_moment_gap_0_to_2K-2': max(moments),
        'radau_endpoint_weight_times_K2': wr[0] * K ** 2,
        'memories_within_[r_hat-d, r_hat+2d]': bool(min(rg.min(), rr.min()) >= R_HAT - d - 1e-12
                                                     and max(rg.max(), rr.max()) <= R_HAT + 2 * d + 1e-12),
        'weight_below_r_hat_gauss': float(mg[rg < R_HAT].sum()),
        'weight_below_r_hat_radau_over_W_div_K2': float(mr[rr < R_HAT].sum() / (W / K ** 2)),
        'budget_gap': float(abs(budget_g - budget_r)),
        'removed_gauss': float(removed_g),
        'removed_radau_over_kappaW_div_K2': float(removed_r / (KAPPA * W / K ** 2)),
        'after_restriction_gap_over_kappaW_div_2K2': float(abs(after_g - after_r) / (KAPPA * W / (2 * K ** 2))),
    }


def budget_gap_mp(K, d, digits=60):
    """The budget gap in 60-digit arithmetic: in double precision it is lost below about 1e-16 for K >= 5."""
    import mpmath as mp
    mp.mp.dps = digits
    xg0, _ = gauss(K)
    xr0, _ = radau(K)
    PK = lambda n, x: mp.legendre(n, x)
    xg = [mp.findroot(lambda x: PK(K, x), mp.mpf(v)) for v in xg0]
    wg = [2 / ((1 - x ** 2) * mp.diff(lambda y: PK(K, y), x) ** 2) for x in xg]
    inner = [mp.findroot(lambda x: (PK(K - 1, x) + PK(K, x)) / (1 + x), mp.mpf(v)) for v in xr0[1:]]
    xr = [mp.mpf(-1)] + inner
    wr = [mp.mpf(2) / K ** 2] + [(1 - x) / (K ** 2 * PK(K - 1, x) ** 2) for x in inner]
    sg, sr = sum(wg), sum(wr)
    d = mp.mpf(d)
    rc = mp.mpf(R_HAT) + (1 + max(xg)) * d / 2
    bg = sum(mp.mpf(W) * w / sg / (1 - (rc + d * x)) for w, x in zip(wg, xg))
    br = sum(mp.mpf(W) * w / sr / (1 - (rc + d * x)) for w, x in zip(wr, xr))
    return float(abs(KAPPA * (bg - br)))


def main():
    rows = [check(K, d) for K in range(2, 7) for d in (0.1, 0.05, 0.025, 0.0125)]
    slopes = {}
    for K in range(2, 7):
        ds = np.array([r['d'] for r in rows if r['K'] == K])
        gaps = np.array([budget_gap_mp(K, d) for d in ds])
        for r, g in zip([r for r in rows if r['K'] == K], gaps):
            r['budget_gap_60_digits'] = float(g)
        slopes[K] = float(np.polyfit(np.log(ds), np.log(gaps), 1)[0])
    ok = all(r['max_scaled_moment_gap_0_to_2K-2'] < 1e-9 and r['memories_within_[r_hat-d, r_hat+2d]']
             and r['weight_below_r_hat_gauss'] == 0 and abs(r['weight_below_r_hat_radau_over_W_div_K2'] - 1) < 1e-9
             and r['removed_gauss'] == 0 and r['removed_radau_over_kappaW_div_K2'] >= 1
             and r['after_restriction_gap_over_kappaW_div_2K2'] >= 1 for r in rows)
    out = {'parameters': {'a': A, 'kappa': KAPPA, 'W': W, 'r_hat': R_HAT}, 'rows': rows,
           'budget_gap_slope_by_K (expected 2K-1)': slopes, 'all_checks_pass': ok}
    path = Path(__file__).with_name('horizon_check_output.json')
    path.write_text(json.dumps(out, indent=1))
    print('all checks pass:', ok)
    print('budget-gap slopes:', {k: round(v, 2) for k, v in slopes.items()})


if __name__ == '__main__':
    main()
