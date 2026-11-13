"""Check of the proposition 'the barrier does not lift near instability': for budget-matched Gauss/Radau pairs,
the passive Gaussian KL rate is bounded by C (spacing)^(4K-2) uniformly as the margin 1-S -> 0.
Computes the Whittle KL rate directly from the closed-form spectra on a fine frequency grid."""
import json, numpy as np
from fragility_scan import rules
def D(z, a, kappa, r, w):
    return z - a - kappa * np.sum(w[None, :] * z[:, None] / (z[:, None] - r[None, :]), axis=1)
def kl_rate(K, dEta, eps, rc=0.5, W=0.3, kappa=0.5, n=400001):
    (xg, wg), (xr, wr) = rules(K)
    rA, wA, rB, wB = rc + dEta * xg, W * wg, rc + dEta * xr, W * wr
    aA = 1 - eps - kappa * np.sum(wA / (1 - rA)); aB = 1 - eps - kappa * np.sum(wB / (1 - rB))
    om = np.concatenate([-np.logspace(-9, np.log10(np.pi), n // 2)[::-1], np.logspace(-9, np.log10(np.pi), n // 2)])
    z = np.exp(1j * om)
    u = np.abs(D(z, aA, kappa, rA, wA)) ** 2 / np.abs(D(z, aB, kappa, rB, wB)) ** 2   # f_B / f_A
    g = u - 1 - np.log(u)
    return float(np.trapezoid(g, om) / (4 * np.pi)), aA, aB
out = {}
for K in (2, 3):
    rows = []
    for dEta in (0.1, 0.05, 0.025):
        for eps in (1e-1, 1e-2, 1e-3, 1e-4, 1e-6):
            v, aA, aB = kl_rate(K, dEta, eps)
            rows.append({"spacing": dEta, "margin": eps, "kl_rate": v, "scaled": v / dEta ** (4 * K - 2), "aA": aA, "aB": aB})
    out[K] = rows
    print(f"K={K}: KL rate / spacing^(4K-2)")
    for dEta in (0.1, 0.05, 0.025):
        print("   spacing %.3f:" % dEta, "  ".join("margin %.0e -> %.4g" % (r["margin"], r["scaled"]) for r in rows if r["spacing"] == dEta))
json.dump(out, open("fragility_uniform_check_results.json", "w"), indent=1)
