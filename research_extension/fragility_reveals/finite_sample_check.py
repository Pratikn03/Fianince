"""Finite-sample check of the near-instability proposition (core prop:nearcrit, note n:nearcrit).

The proposition bounds the Whittle (per-observation) KL rate uniformly in the margin eps = 1 - S; a finite-sample
bound uniform in eps is not proved. This script computes the exact KL divergence between the laws of n consecutive
stationary observations of the two price processes (Gauss vs Gauss-Radau populations at a common budget 1 - eps),
from state-space autocovariances, and compares it with n times the Whittle rate. Numerical evidence, not a proof.
Run: python3 finite_sample_check.py -> finite_sample_check_results.json
"""
import json
import numpy as np
from scipy.linalg import solve_discrete_lyapunov, toeplitz, cho_factor, cho_solve
from fragility_scan import rules


def D(z, a, kappa, r, w):
    return z - a - kappa * np.sum(w[None, :] * z[:, None] / (z[:, None] - r[None, :]), axis=1)


def pops(K, dEta, eps, rc=0.5, W=0.3, kappa=0.5):
    (xg, wg), (xr, wr) = rules(K)
    out = []
    for x, w in ((xg, wg), (xr, wr)):
        r, ww = rc + dEta * x, W * w
        a = 1 - eps - kappa * np.sum(ww / (1 - r))
        out.append((a, kappa, r, ww))
    return out


def autocov(a, kappa, r, w, n):
    """x_t = a x_{t-1} + kappa sum_i q_i y_{i,t-1} + e_t, y_{i,t} = r_i y_{i,t-1} + eta_i x_t, q_i = w_i / eta_i."""
    eta = 1 - r; q = w / eta; K = len(r)
    A0 = np.zeros((K + 1, K + 1)); A0[0, 0] = a; A0[0, 1:] = kappa * q
    A = A0.copy()
    A[1:, :] = eta[:, None] * A0[0, :][None, :]           # y_t = r y_{t-1} + eta x_t, x_t from row 0
    A[1:, 1:] += np.diag(r)
    b = np.zeros(K + 1); b[0] = 1.0; b[1:] = eta
    P = solve_discrete_lyapunov(A, np.outer(b, b))
    g = np.empty(n); v = P[:, 0].copy()
    for h in range(n):
        g[h] = v[0]; v = A @ v
    return g


def kl_exact(gA, gB):
    SA, SB = toeplitz(gA), toeplitz(gB)
    cB = cho_factor(SB); M = cho_solve(cB, SA)
    sign, ldA = np.linalg.slogdet(SA); _, ldB = np.linalg.slogdet(SB)
    n = len(gA)
    return 0.5 * (np.trace(M) - n - (ldA - ldB))


def kl_rate(pA, pB, m=400001):
    om = np.concatenate([-np.logspace(-9, np.log10(np.pi), m // 2)[::-1], np.logspace(-9, np.log10(np.pi), m // 2)])
    z = np.exp(1j * om)
    u = np.abs(D(z, *pA)) ** 2 / np.abs(D(z, *pB)) ** 2
    return float(np.trapezoid(u - 1 - np.log(u), om) / (4 * np.pi))


rows = []
for K, d in ((2, 0.2), (2, 0.1)):
    for eps in (1e-1, 1e-2, 1e-3):
        pA, pB = pops(K, d, eps)
        rate = kl_rate(pA, pB)
        for n in (250, 1000, 4000):
            kl = kl_exact(autocov(*pA, n), autocov(*pB, n))
            rows.append({"K": K, "spacing": d, "eps": eps, "n": n, "kl_exact": kl, "n_times_rate": n * rate,
                         "ratio": kl / (n * rate)})
            print(f"K={K} d={d} eps={eps:g} n={n}: exact {kl:.3e}  n*rate {n * rate:.3e}  ratio {kl / (n * rate):.3f}", flush=True)
json.dump({"rows": rows, "note": "exact Gaussian KL of n stationary observations vs n x Whittle rate"},
          open("finite_sample_check_results.json", "w"), indent=1)
