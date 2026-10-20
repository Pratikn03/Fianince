import numpy as np
from scipy.optimize import minimize
from rh_bound import *
for L in (80, 120):
    d = 0.05; h0 = imp(np.array([q]), np.array([eta])); h1 = imp(np.array([q/2, q/2]), np.array([eta-d, eta+d]))
    n = L + 600; Q = 0.5 * toeplitz(h0[:L])
    Hd = np.array([np.r_[np.zeros(j), (h1 - h0)[:n - j]] for j in range(L)]).T
    E = np.eye(L)[:, :-1] - np.eye(L)[:, 1:]
    G = E.T @ Q @ E; M = E.T @ (Hd.T @ Hd) @ E
    lam, V = eigh(M, G)
    best = np.inf
    rng = np.random.default_rng(0)
    for trial in range(8):
        x0 = V[:, -1] + (0.3 * rng.standard_normal(L - 1) if trial else 0) * np.abs(V[:, -1]).max()
        x0 *= np.sqrt(creq / (x0 @ M @ x0))
        obj = lambda x: x @ G @ x + cfee * np.abs(E @ x).sum()
        res = minimize(obj, x0, constraints=[{"type": "ineq", "fun": lambda x: x @ M @ x - creq}], method="SLSQP", options={"maxiter": 1000, "ftol": 1e-12})
        if (res.x @ M @ res.x) >= creq * (1 - 1e-9): best = min(best, res.fun)
    print(L, "best L+fee found", round(best, 4), "C_RH", round(crh(L, nth=720)["C_RH"], 4))
