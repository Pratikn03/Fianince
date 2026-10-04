r"""Finite-sample test of membership in the completely-monotone (CM) cone.

H0: the first K kernel taps k_0..k_{K-1} are a Hausdorff moment sequence,
    k_j = \int_0^1 r^j d mu(r),  mu >= 0,
which is exactly the closure of the positive heterogeneous-memory class
k_j = sum_i q_i eta_i (1-eta_i)^j (Theorem M4, corrected statement).

Statistic:  T = min_{w >= 0} (k_hat - B w)' V^{-1} (k_hat - B w),
with B[j, g] = r_g^j on a fine grid r_g in [0, 1].

Calibration: the null distribution is evaluated at the cone vertex k = 0.
For a convex cone C and any theta0 in C we have C + theta0 subset C, hence
dist(theta0 + Z, C) <= dist(Z, C) pointwise, so the vertex is least
favourable and the test has size <= alpha for every null point in the grid
cone (Perlman 1969; Silvapulle & Sen 2005).  The grid cone is an inner
approximation of the full Hausdorff cone; with a 401-point grid including
r=0 and r=1 the approximation error is negligible relative to sampling
noise at the K used here (checked in tests/test_cm_cone_test.py).

Note: the naive statistic lambda_min(H_hat) with H^{-1/2} scaling (old M4)
is undefined at rank-deficient H, which includes every finite-rank null.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import nnls


def _basis(K: int, n_grid: int = 401) -> np.ndarray:
    r = np.linspace(0.0, 1.0, n_grid)
    j = np.arange(K)[:, None]
    B = np.where(j == 0, 1.0, r[None, :] ** j)
    return B


def _whitener(V: np.ndarray, ridge: float = 1e-10) -> np.ndarray:
    V = 0.5 * (V + V.T)
    w, U = np.linalg.eigh(V)
    w = np.maximum(w, ridge * max(w.max(), 1e-300))
    return (U / np.sqrt(w)) @ U.T  # V^{-1/2}


def cm_statistic(k: np.ndarray, W: np.ndarray, B: np.ndarray) -> tuple[float, np.ndarray]:
    A = W @ B
    y = W @ k
    w, rnorm = nnls(A, y, maxiter=50 * A.shape[1])
    return float(rnorm**2), w


def cm_cone_test(k_hat, V, n_boot: int = 2000, seed: int = 0, n_grid: int = 401) -> dict:
    k_hat = np.asarray(k_hat, float)
    V = np.asarray(V, float)
    K = len(k_hat)
    B = _basis(K, n_grid)
    W = _whitener(V)
    T, w = cm_statistic(k_hat, W, B)
    rng = np.random.default_rng(seed)
    L = np.linalg.cholesky(0.5 * (V + V.T) + 1e-14 * np.trace(V) / K * np.eye(K))
    Tb = np.empty(n_boot)
    for b in range(n_boot):
        z = L @ rng.standard_normal(K)
        Tb[b], _ = cm_statistic(z, W, B)
    p = float((1 + np.sum(Tb >= T)) / (n_boot + 1))
    fitted = B @ w
    # Classical moment-cone diagnostics for reporting (not used for the decision)
    m = (K - 1) // 2
    H0 = np.array([[k_hat[i + j] for j in range(m + 1)] for i in range(m + 1)])
    m1 = (K - 2) // 2
    H1 = np.array([[k_hat[i + j] - k_hat[i + j + 1] for j in range(m1 + 1)] for i in range(m1 + 1)])
    return {
        "T": T, "p_value": p, "n_boot": n_boot,
        "crit_05": float(np.quantile(Tb, 0.95)),
        "fitted": fitted.tolist(),
        "lambda_min_H": float(np.linalg.eigvalsh(H0).min()),
        "lambda_min_H_shift": float(np.linalg.eigvalsh(H1).min()),
    }
