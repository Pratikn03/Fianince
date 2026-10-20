"""Matching upper bound for K cohorts: Prony on noisy kernel power sums k_m = sum_i w_i r_i^m, m < 2K.
Rates r_i = r_c + D s_i (Gauss nodes on [-1,1]), weights W*omega_i. Find N* (experiments, each giving
the kernel with iid N(0, sigma^2) noise) at which the weight RMSE falls to 10% of the smallest weight."""
import numpy as np, json
from numpy.polynomial import legendre
def prony(k, K):
    # Hankel system for the characteristic polynomial, then Vandermonde for weights
    H = np.array([[k[i + j] for j in range(K)] for i in range(K)]); rhs = -np.array([k[K + i] for i in range(K)])
    c = np.linalg.solve(H, rhs)
    roots = np.roots(np.r_[1, c[::-1]])
    roots = np.real_if_close(roots, tol=1e6)
    V = np.vander(roots, 2 * K, increasing=True).T
    w = np.linalg.lstsq(V, k[:2 * K], rcond=None)[0]
    o = np.argsort(np.real(roots)); return np.real(roots[o]), np.real(w[o])
def rmse(K, D, n_eff_sd, reps=400, rng=None):
    s, om = legendre.leggauss(K); om = om / om.sum(); W = 0.1; rc = 0.7
    r = rc + D * s; w = W * om; k = np.array([np.sum(w * r ** m) for m in range(2 * K)])
    err = []
    for _ in range(reps):
        kn = k + rng.normal(0, n_eff_sd, 2 * K)
        try:
            rr, ww = prony(kn, K)
            if np.all(np.isfinite(ww)) and np.isrealobj(rr):
                err.append(np.sqrt(np.mean((ww - w) ** 2)))
            else:
                err.append(np.inf)
        except Exception:
            err.append(np.inf)
    return np.median(err), w.min()
rng = np.random.default_rng(0); out = {}
for K in [2, 3, 4]:
    Ds = np.geomspace(0.02, 0.15, 7); Ns = []
    for D in Ds:
        # linear regime: error = c / sqrt(N); find c at small noise, then N* = (c / (0.1 w_min))^2 * sigma^2 (sigma = 1)
        sd = 1e-9 * D ** (2 * K - 1)
        e, wmin = rmse(K, D, sd, rng=rng)
        c = e / sd
        Ns.append((c / (0.1 * wmin)) ** 2)
    slope = np.polyfit(np.log(Ds), np.log(Ns), 1)[0]
    out[K] = {"Delta": Ds.tolist(), "N_star": Ns, "slope": slope, "theory": -(4 * K - 2)}
    print(f"K={K}: fitted slope of N* in Delta = {slope:.2f}  (lower bound order {-(4*K-2)})")
json.dump(out, open("R_P1_kcohort_upper.json", "w"), indent=1)
