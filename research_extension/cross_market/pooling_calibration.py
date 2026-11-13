"""Calibration for the cross-market result: years of daily prices needed to tell two populations apart, one market
versus two markets in which the same two algorithms (same memories) trade with different weights.
Parameters as in Table 1, row 'memory rates 0.9 +/- 0.025' (half-lives 5.2-8.9 days): kappa = 0.5, feedback share
0.3 (total weight 0.06), common feedback budget S = 1 - 0.1. Bound n >= ln 5 / (sum of per-market KL rates)."""
import json
import numpy as np
from fragility_scan import rules

KAPPA, RC, D_ETA, WTOT, MARGIN = 0.5, 0.9, 0.025, 0.06, 0.1


def Dz(z, a, r, w):
    return z - a - KAPPA * np.sum(w[None, :] * z[:, None] / (z[:, None] - r[None, :]), axis=1)


def kl_rate(rA, wA, rB, wB, n=400001):
    aA = 1 - MARGIN - KAPPA * np.sum(wA / (1 - rA)); aB = 1 - MARGIN - KAPPA * np.sum(wB / (1 - rB))
    om = np.concatenate([-np.logspace(-9, np.log10(np.pi), n // 2)[::-1], np.logspace(-9, np.log10(np.pi), n // 2)])
    z = np.exp(1j * om)
    u = np.abs(Dz(z, aA, rA, wA)) ** 2 / np.abs(Dz(z, aB, rB, wB)) ** 2
    return float(np.trapezoid(u - 1 - np.log(u), om) / (4 * np.pi))


def years(kl):
    return np.log(5) / kl / 252


if __name__ == "__main__":
    out = {}
    # 1. One market, the hardest pair (Gauss vs Gauss-Radau, K = 2): Table 1
    (xg, wg), (xr, wr) = rules(2)
    kl1 = kl_rate(RC + D_ETA * xg, WTOT * wg, RC + D_ETA * xr, WTOT * wr)
    out["one_market_gauss_radau"] = {"kl": kl1, "years": years(kl1)}
    # 2. Two markets, the hardest pair for two markets: moments of order 0 and 1 matched in both markets
    sA = np.array([-1.0, 1.0]); sB = np.array([-0.5, 1.0])
    W_A = np.array([[0.5, 0.5], [0.7, 0.3]])          # rows: markets; columns: algorithms (shares of WTOT)
    W_B = []
    for wa in W_A:
        m0, m1 = wa.sum(), wa @ sA
        M = np.array([[1, 1], sB]); W_B.append(np.linalg.solve(M, [m0, m1]))
    W_B = np.array(W_B)
    assert (W_B > 0).all()
    kls = [kl_rate(RC + D_ETA * sA, WTOT * W_A[j], RC + D_ETA * sB, WTOT * W_B[j]) for j in range(2)]
    out["two_markets_pair"] = {"W_A": W_A.tolist(), "W_B": W_B.tolist(), "s_A": sA.tolist(), "s_B": sB.tolist(),
                               "kl_per_market": kls, "years_both_markets": years(sum(kls)),
                               "years_market1_alone": years(kls[0])}
    # 3. Same pair, but participation proportional in the two markets (no diversity): it is a one-market problem
    print(json.dumps(out, indent=1))
    json.dump(out, open("pooling_calibration_results.json", "w"), indent=1)

