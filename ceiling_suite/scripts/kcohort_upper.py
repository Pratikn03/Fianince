"""Matching upper bound for K cohorts: Prony on noisy kernel power sums k_m = sum_i w_i r_i^m, m < 2K.
Rates r_i = r_c + D s_i (Gauss nodes on [-1,1]), weights W*omega_i. Find N* (experiments, each giving
the kernel with iid N(0, sigma^2) noise) at which the weight RMSE falls to 10% of the smallest weight.
Evaluates K in {2, 3, 4, 5} in centred and rescaled coordinates: mu_hat = mu + T_rc @ eps, t_hat_m = mu_hat_m / D^m."""
import os, json
from math import comb
import numpy as np
from numpy.polynomial import legendre

def prony_centred(t, K):
    """Prony recovery in centred/rescaled coordinates s_i = (r_i - r_c)/D in [-1, 1] (ordered s_1 < ... < s_K)."""
    H = np.array([[t[i + j] for j in range(K)] for i in range(K)], dtype=float)
    rhs = -np.array([t[K + i] for i in range(K)], dtype=float)
    c = np.linalg.solve(H, rhs)
    roots = np.roots(np.r_[1.0, c[::-1]])
    roots = np.real_if_close(roots, tol=1e6)
    V = np.vander(roots, 2 * K, increasing=True).T
    w = np.linalg.lstsq(V, t[:2 * K], rcond=None)[0]
    o = np.argsort(np.real(roots))
    return np.real(roots[o]), np.real(w[o])

def rmse(K, D, n_eff_sd, reps=400, rng=None):
    s, om = legendre.leggauss(K)
    om = om / om.sum()
    W = 0.1
    rc = 0.7
    w = W * om
    M = 2 * K
    # Exact centred moments mu_m = sum_i w_i (D s_i)^m and binomial centring matrix T_rc
    mu = np.array([np.sum(w * ((D * s) ** m)) for m in range(M)])
    T_rc = np.array([[comb(m, j) * ((-rc) ** (m - j)) if j <= m else 0.0 for j in range(M)] for m in range(M)])
    scales = np.array([D ** m for m in range(M)])
    err = []
    for _ in range(reps):
        eps = rng.normal(0.0, n_eff_sd, M)
        mun = mu + T_rc @ eps
        try:
            tn = mun / scales
            ss, ww = prony_centred(tn, K)
            if np.all(np.isfinite(ww)) and np.isrealobj(ss):
                err.append(np.sqrt(np.mean((ww - w) ** 2)))
            else:
                err.append(np.inf)
        except Exception:
            err.append(np.inf)
    return float(np.median(err)), float(w.min())

if __name__ == "__main__":
    rng = np.random.default_rng(0)
    out = {}
    for K in [2, 3, 4, 5]:
        Ds = np.geomspace(0.03, 0.20, 7)
        Ns = []
        for D in Ds:
            sd = 1e-9 * (D ** (2 * K - 1))
            e, wmin = rmse(K, D, sd, rng=rng)
            c = e / sd
            Ns.append(float((c / (0.1 * wmin)) ** 2))
        slope = float(np.polyfit(np.log(Ds), np.log(Ns), 1)[0])
        out[str(K)] = {"Delta": Ds.tolist(), "N_star": Ns, "slope": slope, "theory": -(4 * K - 2)}
        print(f"K={K}: fitted slope of N* in Delta = {slope:.2f}  (lower bound order {-(4*K-2)})")
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(out, open(os.path.join(here, "R_P1_kcohort_upper.json"), "w"), indent=1)
