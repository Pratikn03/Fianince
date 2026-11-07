"""Theorem thm:fragility(iv): several positive-feedback cohorts. Every positive-impact equilibrium with
D > max r_i has kappa = (1 - D)/G(D), so it is a solution D in (m, 1), m = max(abar, max r_i), of Psi(D) = A with
Psi(D) = kappa (D - abar) D / (sF2 D^2 + kappa^2 sX2). The threshold A*_K = max Psi is compared with the bound
min{(1 - abar)/(2 sF sX), (1 - sqrt(abar))^2 / (sF2 G(1))}, and the stability of the equilibria on the threshold
curve is checked numerically (spectral radius of the transition of Theorem thm:inventory)."""
import json
import numpy as np
from e4_inventory import transition

sF2, sX2, abar = 1.0, 0.25, 0.6

def scan(w, r, n=200001):
    w, r = np.array(w, float), np.array(r, float)
    m = max(abar, r.max())
    Ds = np.linspace(m + 1e-9, 1 - 1e-9, n)
    G = (w[None, :] / (Ds[:, None] - r[None, :])).sum(1)
    k = (1 - Ds) / G
    psi = k * (Ds - abar) * Ds / (sF2 * Ds ** 2 + k ** 2 * sX2)
    return Ds, k, psi

rows = []
configs = [("two cohorts 0.5/0.85", [0.5, 0.85]), ("three cohorts 0.3/0.6/0.8", [0.3, 0.6, 0.8]),
           ("Gauss pair", [0.6 - 0.2 / np.sqrt(3), 0.6 + 0.2 / np.sqrt(3)])]
for name, r in configs:
    for scale in [0.005, 0.02, 0.05, 0.2, 1.0]:
        w = [scale] * len(r)
        Ds, k, psi = scan(w, r)
        j = int(np.argmax(psi)); Astar = float(psi[j])
        G1 = float(sum(wi / (1 - ri) for wi, ri in zip(w, r)))
        bound = min((1 - abar) / (2 * np.sqrt(sF2 * sX2)), (1 - np.sqrt(abar)) ** 2 / (sF2 * G1))
        # stability along the equilibrium curve (every D on the grid is an equilibrium for A = psi(D))
        idx = np.linspace(0, len(Ds) - 1, 400).astype(int)
        rho = max(max(abs(np.linalg.eigvals(transition(k[i], Ds[i], abar, w, r)[0]))) for i in idx)
        rows.append({"config": name, "w_each": scale, "G1": G1, "A_star": Astar, "D_at_max": float(Ds[j]),
                     "bound": float(bound), "bound_holds": bool(Astar < bound),
                     "spectral_radius_at_threshold": float(max(abs(np.linalg.eigvals(transition(k[j], Ds[j], abar, w, r)[0])))), "max_spectral_radius_on_curve": float(rho)})
        print(rows[-1], flush=True)
json.dump({"sF2": sF2, "sX2": sX2, "abar": abar, "rows": rows}, open("e4_fragility_K_results.json", "w"), indent=1)
