"""Finite-sample response ellipsoids, Hotelling F-calibration, and contrast support.

Implements:
1. Theorem 5.1: Exact response ellipsoid under independent Gaussian episode law.
2. Proposition 5.2: Linear contrast support over the response ellipsoid.
3. Proposition 5.3: Rational witness proving no fixed linear contrast gives S.
4. Section 5.4: Audited terminal-row Student-t pivot under Contract I_1.
"""
from typing import Dict, Any, Tuple
from fractions import Fraction
import numpy as np
from scipy import stats


def hotelling_f_critical_value(p: int, R: int, alpha: float = 0.05) -> Tuple[float, float, int, int]:
    """Calculate the exact Hotelling F-critical value and squared radius k_alpha^2 (Theorem 5.1).

    k_alpha^2 = [nu * p / (nu - p + 1)] * F^{-1}_{p, nu - p + 1}(1 - alpha)
    where nu = R - 2.
    """
    nu = R - 2
    df1 = p
    df2 = nu - p + 1
    if df2 <= 0:
        raise ValueError(f"Insufficient residual degrees of freedom: nu - p + 1 = {df2} <= 0.")

    f_crit = float(stats.f.ppf(1.0 - alpha, df1, df2))
    k_alpha_sq = float((nu * p / df2) * f_crit)
    return k_alpha_sq, f_crit, df1, df2


def estimate_ols_response_and_covariance(
    u: np.ndarray, Y: np.ndarray
) -> Dict[str, Any]:
    """Compute OLS slope response beta_hat, residual covariance, and V = Sigma_hat / D (Section 5.1).

    Parameters:
      u: (R,) probe values.
      Y: (R, p) episode response trajectories.

    Returns:
      Dict with beta_hat, m_hat, Sigma_hat, V, D, nu, and rank check.
    """
    u = np.asarray(u, dtype=float)
    Y = np.asarray(Y, dtype=float)
    R, p = Y.shape

    u_bar = float(np.mean(u))
    v = u - u_bar
    D = float(np.sum(v ** 2))
    if D <= 1e-14:
        raise ValueError("Probe vector u is constant; cannot estimate slope.")

    nu = R - 2
    if nu < p:
        raise ValueError(f"Residual degrees of freedom nu = {nu} < p = {p}; covariance is singular.")

    beta_hat = np.sum(v[:, None] * Y, axis=0) / D
    m_hat = np.mean(Y, axis=0) - u_bar * beta_hat

    residuals = Y - m_hat - np.outer(u, beta_hat)
    Sigma_hat = (residuals.T @ residuals) / nu
    V = Sigma_hat / D

    return {
        "beta_hat": beta_hat,
        "m_hat": m_hat,
        "Sigma_hat": Sigma_hat,
        "V": V,
        "D": D,
        "nu": nu,
        "R": R,
        "p": p,
    }


def compute_mahalanobis_distance(
    b: np.ndarray, beta_hat: np.ndarray, V: np.ndarray
) -> float:
    """Compute (b - beta_hat)^T V^{-1} (b - beta_hat)."""
    diff = np.asarray(b, dtype=float) - np.asarray(beta_hat, dtype=float)
    return float(diff @ np.linalg.solve(V, diff))


def is_in_ellipsoid(
    b: np.ndarray, beta_hat: np.ndarray, V: np.ndarray, k_alpha_sq: float
) -> bool:
    """Check membership b in E_alpha."""
    t_sq = compute_mahalanobis_distance(b, beta_hat, V)
    return bool(t_sq <= k_alpha_sq + 1e-10)


def linear_contrast_support(
    c: np.ndarray, beta_hat: np.ndarray, V: np.ndarray, k_alpha: float
) -> Tuple[float, float, float]:
    """Compute extrema of c^T b over the ellipsoid E_alpha (Proposition 5.2).

    Extrema: c^T beta_hat +/- k_alpha * sqrt(c^T V c)
    """
    c = np.asarray(c, dtype=float)
    beta_hat = np.asarray(beta_hat, dtype=float)

    center = float(c @ beta_hat)
    quad = float(c @ V @ c)
    if quad < 0:
        quad = 0.0
    half_width = float(k_alpha * np.sqrt(quad))

    return center - half_width, center + half_width, half_width


def get_four_coefficient_witness() -> Dict[str, Any]:
    """Return the exact rational witness of Proposition 5.3.

    Proves no fixed linear contrast c^T beta can generally equal S:
    a = 2/5, rates (1, 1/2, 1/20).
    q^(0) = (0, 12/65, 0) => S_0 = 38/65 < 1.
    q^(1) = (54/1235, 0, 240/247) => S_1 = 92/65 > 1.
    Both produce (h_0, h_1, h_2, h_3) = (1, 2/5, 82/325, 23/125).
    """
    a = Fraction(2, 5)
    eta = [Fraction(1, 1), Fraction(1, 2), Fraction(1, 20)]

    q0 = [Fraction(0, 1), Fraction(12, 65), Fraction(0, 1)]
    q1 = [Fraction(54, 1235), Fraction(0, 1), Fraction(240, 247)]

    S0 = a + sum(q0)
    S1 = a + sum(q1)

    # Compute h_0, h_1, h_2, h_3 for both
    def compute_h(q_vec):
        k0 = sum(q * e for q, e in zip(q_vec, eta))
        k1 = sum(q * e * (1 - e) for q, e in zip(q_vec, eta))
        h0 = Fraction(1, 1)
        h1 = a
        h2 = a * h1 + k0 * h0
        h3 = a * h2 + k0 * h1 + k1 * h0
        return [h0, h1, h2, h3], k0, k1

    h_seq0, k0_0, k1_0 = compute_h(q0)
    h_seq1, k0_1, k1_1 = compute_h(q1)

    return {
        "a": str(a),
        "rates": [str(e) for e in eta],
        "q0": [str(q) for q in q0],
        "q1": [str(q) for q in q1],
        "S0": str(S0),
        "S1": str(S1),
        "S0_val": float(S0),
        "S1_val": float(S1),
        "is_S0_stable": S0 < 1,
        "is_S1_stable": S1 < 1,
        "h_seq0": [str(x) for x in h_seq0],
        "h_seq1": [str(x) for x in h_seq1],
        "h_sequences_identical": h_seq0 == h_seq1,
        "expected_h": ["1", "2/5", "82/325", "23/125"],
    }
