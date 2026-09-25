"""Exact calculation and clarification of Theorem 8.4 (Price-Response Ambiguity).

Compares two distinct observation noise structures for Y_{r,j} = P_{r,j+1} - P_{r,0}:
1. Independent difference-level error: Cov(Y_r) = sigma^2 * I
   Under this model, d^2 = (R * delta^2 / sigma^2) * sum_{j=0}^H (beta_j^{(1)} - beta_j^{(0)})^2
2. Level quote observation error: P_{r,t} = p_{r,t} + epsilon_{r,t} with epsilon_{r,t} ~ i.i.d. N(0, sigma^2)
   Differencing relative to noisy baseline P_{r,0} induces:
   Cov(Y_r) = sigma^2 * (I + 1 1^T)
   By the Sherman-Morrison formula:
   (I + 1 1^T)^{-1} = I - (1 / (H + 2)) * 1 1^T
   Then d^2 = (R * delta^2 / sigma^2) * (Delta beta)^T (I + 1 1^T)^{-1} (Delta beta)

Both models yield finite-budget ambiguity, but the exact forced-classification error differs.
"""

import json
import numpy as np
from scipy.stats import norm


def get_heterogeneous_matrices(a, rates, weights):
    """Construct (H+1, H+1) system transition matrix in pressure coordinates."""
    rates = np.asarray(rates, dtype=float)
    weights = np.asarray(weights, dtype=float)
    d = 1
    n = len(rates)
    # J = [[a, 1^T], [diag(eta)*q, diag(1-eta)]]
    dim = 1 + n
    J = np.zeros((dim, dim), dtype=float)
    J[0, 0] = a
    J[0, 1:] = 1.0
    for i in range(n):
        J[1 + i, 0] = rates[i] * weights[i]
        J[1 + i, 1 + i] = 1.0 - rates[i]
    return J


def compute_impulse_response(a, rates, weights, kappa, H):
    """Compute price response beta_j = kappa * e_1^T J^j e_1 for j = 0, ..., H."""
    J = get_heterogeneous_matrices(a, rates, weights)
    dim = J.shape[0]
    e1 = np.zeros(dim, dtype=float)
    e1[0] = 1.0

    beta = np.zeros(H + 1, dtype=float)
    state = e1.copy()
    for j in range(H + 1):
        beta[j] = kappa * state[0]
        state = J @ state
    return beta


def analyze_noise_models():
    # Parameters matching Section 8.4 / 11.4 of the manuscript
    a = 0.4
    kappa = 0.02
    R = 1024
    delta = 4.0
    sigma = 0.002
    H = 64  # horizons: lags 0 to 64 -> 65 coefficients

    results = []

    for eta in [1e-7, 1e-6, 1e-5, 1e-4]:
        rates0 = [0.5, eta]
        weights0 = 0.6 * np.array([0.7, 0.2])  # Gain G = 0.9

        rates1 = [0.5, eta]
        weights1 = 0.6 * np.array([0.7, 0.4])  # Gain G = 1.1

        beta0 = compute_impulse_response(a, rates0, weights0, kappa, H)
        beta1 = compute_impulse_response(a, rates1, weights1, kappa, H)
        delta_beta = beta1 - beta0

        # Model 1: Stacked covariance is sigma^2 * I (independent differences)
        d_sq_diff = (R * (delta**2) / (sigma**2)) * np.sum(delta_beta**2)
        d_diff = np.sqrt(d_sq_diff)
        oracle_error_diff = norm.cdf(-d_diff / 2.0)

        # Model 2: Level quote errors (noisy baseline induces (I + 1 1^T))
        M = H + 1  # 65 elements
        # (I + 1 1^T)^{-1} v = v - (sum(v) / (M + 1)) * 1
        inv_cov_v = delta_beta - (np.sum(delta_beta) / (M + 1.0))
        d_sq_level = (R * (delta**2) / (sigma**2)) * np.dot(delta_beta, inv_cov_v)
        d_level = np.sqrt(max(0.0, d_sq_level))
        oracle_error_level = norm.cdf(-d_level / 2.0)

        results.append({
            "eta": eta,
            "d_diff": float(d_diff),
            "oracle_error_diff_pct": float(oracle_error_diff * 100.0),
            "d_level": float(d_level),
            "oracle_error_level_pct": float(oracle_error_level * 100.0),
        })

    return results


if __name__ == "__main__":
    res = analyze_noise_models()
    print(json.dumps(res, indent=2))
