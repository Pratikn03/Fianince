"""Check of Supplement Theorem thm:relabelgeneral on random three-class economies with nonlinear primitives:
concave increasing private payoffs, a convex concealment cost C(z) = z^2/2 + z^4 (so C(z) >= z^2/2), and a social
welfare with an aggregate-feedback externality, U(e) = sum chi_j b_j e_j - (lam/2) (sum chi_j w_j e_j)^2.
Best responses are computed on a fine grid of shares for every channel; policies on a grid of retentions."""
import itertools
import numpy as np

rng = np.random.default_rng(20261121)
ZG = np.linspace(0, 1, 401)
C = ZG ** 2 / 2 + ZG ** 4
C1 = 1.5
kappa_C = 0.5


def respond(x, j, chan, pi, cbar, eps):
    best_val, best_e, best_cost = pi(j, x[j]), x[j], 0.0
    for k in chan[j]:
        d = x[k] - x[j]
        if d <= 0:
            continue
        val = pi(j, x[j] + ZG * d) - eps * cbar[j][k] * C
        i = int(np.argmax(val))
        if val[i] > best_val:
            best_val, best_e, best_cost = val[i], x[j] + ZG[i] * d, eps * cbar[j][k] * C[i]
    return best_e, best_cost


grid = np.linspace(0, 1, 11)
pols = [np.array(p) for p in itertools.product(grid, grid, grid)]
worst_cheap = worst_exp = 0.0
for trial in range(12):
    chi = rng.dirichlet(np.ones(3)); b = rng.uniform(-1, 1.5, 3); w = rng.uniform(0.2, 1, 3); lam = rng.uniform(0.5, 3)
    pb = rng.uniform(0.6, 2, 3); rho = rng.uniform(0, 0.5, 3)           # pi_j(e) = pb e - rho e^2/2, slope in [pb-rho, pb]
    beta, B = pb - rho, pb
    pi = lambda j, e: pb[j] * e - rho[j] * e ** 2 / 2
    U = lambda e: float(np.sum(chi * b * e) - lam / 2 * np.sum(chi * w * e) ** 2)
    L = chi * (np.abs(b) + lam * w * np.sum(chi * w))                    # Lipschitz weights of U on [0,1]^3
    chan = {0: [1], 1: [0, 2], 2: [1]}                                    # nearest-neighbour channels
    cbar = rng.uniform(0.5, 2, (3, 3))
    coarse = max(U(np.array([max(x[[k for k in chan[j] + [j]]]) for j in range(3)])) for x in pols)
    WA = max(U(np.array(e)) for e in itertools.product(grid, grid, grid))
    for eps in (1e-3, 1e-2):
        WC = -1e9
        for x in pols:
            es, cs = zip(*(respond(x, j, chan, pi, cbar, eps) for j in range(3)))
            WC = max(WC, U(np.array(es)) - float(np.sum(chi * np.array(cs))))
        bound = eps * sum(max(cbar[j][k] for k in chan[j]) * C1 * (L[j] / beta[j] + chi[j]) for j in range(3))
        bound += 1.0 / 400 * sum(L)            # grid resolution of shares
        assert abs(WC - coarse) <= bound + 1e-9, ("cheap", trial, eps, WC, coarse, bound)
        worst_cheap = max(worst_cheap, abs(WC - coarse) / bound)
    for eps in (1e2, 1e3):
        WC = -1e9
        for x in pols:
            es, cs = zip(*(respond(x, j, chan, pi, cbar, eps) for j in range(3)))
            WC = max(WC, U(np.array(es)) - float(np.sum(chi * np.array(cs))))
        bound = sum((L[j] * B[j] + chi[j] * B[j] ** 2) / (kappa_C * eps * min(cbar[j][k] for k in chan[j])) for j in range(3))
        assert abs(WC - WA) <= bound + 1e-9, ("expensive", trial, eps, WC, WA, bound)
        worst_exp = max(worst_exp, abs(WC - WA) / bound)
print(f"general theorem: bounds hold on 12 random nonlinear economies (largest gap/bound: cheap {worst_cheap:.2f}, expensive {worst_exp:.2f})")
