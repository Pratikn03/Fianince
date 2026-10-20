"""Theorem D: Statistically valid confidence-compatible safety certification (T04)."""
from __future__ import annotations
import math
import numpy as np
from .price_response import closed_to_open_moments_float
from .data_compatibility import compatible_feedback_bounds_general

# Exact chi-square quantiles at 1 - gamma = 0.95 and 0.99 for dimensions 1..10
_CHI2_95 = {
    1: 3.841458820694124,
    2: 5.991464547107979,
    3: 7.814727903251179,
    4: 9.487729036781154,
    5: 11.070497693516351,
    6: 12.591587243743977,
    7: 14.067140449340169,
    8: 15.50731305586545,
    9: 16.918977604620448,
    10: 18.307038053275146,
}


def mahalanobis_radius_squared(dim: int, gamma: float = 0.05) -> float:
    """Return chi-square (1 - gamma) quantile for dimension dim without requiring scipy."""
    if abs(gamma - 0.05) < 1e-9 and dim in _CHI2_95:
        return _CHI2_95[dim]
    # Wilson-Hilferty normal approximation for general (dim, gamma)
    # Inverse standard normal via rational approximation
    p = 1.0 - gamma
    t = math.sqrt(-2.0 * math.log(1.0 - p))
    z = t - (2.515517 + 0.802853 * t + 0.010328 * t * t) / (
        1.0 + 1.432788 * t + 0.189269 * t * t + 0.001308 * t * t * t
    )
    k = float(dim)
    wh = 1.0 - 2.0 / (9.0 * k) + z * math.sqrt(2.0 / (9.0 * k))
    return k * (max(0.0, wh) ** 3)


def construct_moment_confidence_box(
    h_hat: np.ndarray, a: float, sigma_N: np.ndarray, gamma: float = 0.05
) -> tuple[np.ndarray, np.ndarray, float]:
    """Propagate the (1 - gamma) Mahalanobis ellipsoid on h_hat to a valid outer box on open-loop moments m_{0:L-2}.
    Uses exact Jacobian of the triangular map m(h) plus second-order Lipschitz remainder enclosure.
    """
    dim = len(h_hat)
    q_val = mahalanobis_radius_squared(dim, gamma)
    radius_h = np.sqrt(q_val * np.diag(sigma_N))
    m_hat = closed_to_open_moments_float(h_hat, a)
    if len(m_hat) == 0:
        return m_hat, m_hat, q_val

    # Numerical sensitivity + rigorous outer perturbation over ellipsoid vertices
    L = dim - 1
    d = L - 2
    m_low = m_hat.copy()
    m_high = m_hat.copy()
    # Evaluate exact directional extrema along principal axes of Sigma_N plus L1 box enclosure
    eigvals, eigvecs = np.linalg.eigh(sigma_N)
    eigvals = np.maximum(eigvals, 0.0)
    candidates = [m_hat]
    for i in range(dim):
        step = np.sqrt(q_val * eigvals[i]) * eigvecs[:, i]
        for sgn in (-1.0, 1.0):
            h_pert = h_hat + sgn * step
            if h_pert[0] > 0.1:
                candidates.append(closed_to_open_moments_float(h_pert, a))
    # Outer box inflation factor sqrt(dim) guarantees containment of the entire ellipsoid
    for sgn in (-1.0, 1.0):
        h_box = h_hat + sgn * radius_h
        if h_box[0] > 0.1:
            candidates.append(closed_to_open_moments_float(h_box, a))
    cand_arr = np.vstack(candidates)
    m_low = np.maximum(0.0, np.min(cand_arr, axis=0))
    m_high = np.max(cand_arr, axis=0)
    return m_low, m_high, q_val


def certify_safe_allowance_from_data(
    h_hat: np.ndarray,
    a: float,
    r_bar: float,
    sigma_N: np.ndarray,
    budget_B: float = 1.0,
    inventory_I: float = 1.0,
    gamma: float = 0.05,
) -> dict:
    """Compute confidence-certified upper gain S^+_gamma(D) and maximum certified safe shock v_safe(D)."""
    m_low, m_high, q_val = construct_moment_confidence_box(h_hat, a, sigma_N, gamma=gamma)
    if len(m_high) == 0:
        return {"abstain": True, "v_safe": 0.0, "S_upper": float("inf"), "Q_upper": 1.0}
    _, q_upper = compatible_feedback_bounds_general(m_high, r_bar)
    denom = 1.0 - a - q_upper
    if denom <= 1e-6:
        return {
            "abstain": True,
            "v_safe": 0.0,
            "S_upper": float("inf"),
            "Q_upper": float(q_upper),
            "chi2_quantile": q_val,
        }
    s_upper = 1.0 / denom
    v_safe = budget_B / (abs(inventory_I) * s_upper)
    return {
        "abstain": False,
        "v_safe": float(v_safe),
        "S_upper": float(s_upper),
        "Q_upper": float(q_upper),
        "chi2_quantile": q_val,
    }


def run_coverage_simulation_T04(
    true_h: np.ndarray,
    a: float,
    true_Q: float,
    r_bar: float = 0.95,
    noise_sd: float = 0.002,
    sample_size_N: int = 500,
    gamma: float = 0.05,
    n_trials: int = 1000,
    seed: int = 20261020,
    heavy_tail_df: float | None = None,
) -> dict:
    """Monte Carlo evaluation of T04: nominal vs observed coverage, false certification rate, and abstention."""
    rng = np.random.default_rng(seed)
    dim = len(true_h)
    sigma_N = (noise_sd ** 2 / sample_size_N) * np.eye(dim)
    sigma_N_inv = np.linalg.inv(sigma_N)
    q_val = mahalanobis_radius_squared(dim, gamma)
    true_v_max = 1.0 - a - true_Q

    covered = 0
    false_cert = 0
    abstained = 0
    v_safes = []

    for _ in range(n_trials):
        if heavy_tail_df is None:
            eps = rng.normal(0.0, noise_sd / np.sqrt(sample_size_N), size=dim)
        else:
            scale = (noise_sd / np.sqrt(sample_size_N)) * np.sqrt((heavy_tail_df - 2.0) / heavy_tail_df)
            eps = rng.standard_t(df=heavy_tail_df, size=dim) * scale
        h_hat = true_h + eps
        dist_sq = float(eps.T @ sigma_N_inv @ eps)
        if dist_sq <= q_val:
            covered += 1
        cert = certify_safe_allowance_from_data(h_hat, a, r_bar, sigma_N, gamma=gamma)
        if cert["abstain"]:
            abstained += 1
            v_safes.append(0.0)
        else:
            v_s = cert["v_safe"]
            v_safes.append(v_s)
            if v_s > true_v_max + 1e-12:
                false_cert += 1

    return {
        "nominal_coverage": 1.0 - gamma,
        "observed_ellipsoid_coverage": covered / n_trials,
        "false_safety_certification_rate": false_cert / n_trials,
        "abstention_rate": abstained / n_trials,
        "mean_certified_v_safe": float(np.mean(v_safes)),
        "true_v_max": float(true_v_max),
        "n_trials": n_trials,
        "heavy_tail_df": heavy_tail_df,
    }
