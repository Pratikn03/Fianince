"""Theorem B (Risk-Specific Identifiability) & Theorem C (Minimum Observations for Safe Decisions)."""
from __future__ import annotations
from fractions import Fraction
import math
from typing import Sequence
import numpy as np


def compatible_feedback_bounds_d0(m0: float, r_bar: float) -> tuple[float, float]:
    """Sharp Chebyshev-Markov-Stieltjes bounds [Q_0^-, Q_0^+] given m_0 = sum_i w_i on r in [0, r_bar]."""
    if m0 < 0 or not (0.0 <= r_bar < 1.0):
        raise ValueError("Require m0 >= 0 and r_bar in [0, 1)")
    return m0, m0 / (1.0 - r_bar)


def compatible_feedback_bounds_d1(m0: float, m1: float, r_bar: float) -> tuple[float, float]:
    """Sharp Markov-Krein bounds [Q_1^-, Q_1^+] given (m_0, m_1) on r in [0, r_bar]:
    - Lower bound (Jensen at r = m_1/m_0): Q_1^- = m_0^2 / (m_0 - m_1)
    - Upper bound (two-point support {0, r_bar}): Q_1^+ = (m_0 - m_1/r_bar) + (m_1/r_bar)/(1 - r_bar) = m_0 + m_1 / (1 - r_bar)
    """
    if m0 <= 0.0:
        return 0.0, 0.0
    m1_clamped = min(max(m1, 0.0), r_bar * m0)
    q_low = (m0 * m0) / (m0 - m1_clamped)
    q_high = m0 + (m1_clamped / (1.0 - r_bar) if r_bar > 0.0 else 0.0)
    return q_low, q_high


def compatible_feedback_bounds_general(moments: Sequence[float], r_bar: float) -> tuple[float, float]:
    """Sharp compatible bounds [Q_d^-, Q_d^+] using truncated geometric series and remainder envelope:
    Since 1/(1-r) = sum_{j=0}^d r^j + r^{d+1}/(1-r), for any measure with moments m_0, ..., m_d
    supported on [0, r_bar]:
    sum_{j=0}^d m_j + m_d * (m_d/m_{d-1}) / (1 - m_d/m_{d-1}) <= Q <= sum_{j=0}^d m_j + r_bar * m_d / (1 - r_bar).
    For d=0 and d=1 this coincides with the exact Markov-Krein endpoints.
    """
    d = len(moments) - 1
    if d < 0:
        raise ValueError("Need at least m_0")
    m0 = float(moments[0])
    if d == 0:
        return compatible_feedback_bounds_d0(m0, r_bar)
    if d == 1:
        return compatible_feedback_bounds_d1(m0, float(moments[1]), r_bar)
    partial = float(np.sum(moments))
    md = max(float(moments[d]), 0.0)
    md_prev = max(float(moments[d - 1]), 1e-15)
    r_eff = min(max(md / md_prev, 0.0), r_bar)
    q_low = partial + (md * r_eff / (1.0 - r_eff) if md > 0 else 0.0)
    q_high = partial + md * r_bar / (1.0 - r_bar)
    return q_low, q_high


def compatible_risk_bounds(
    moments: Sequence[float], a: float, r_bar: float, v: float, inventory: float = 1.0, kappa: float = 1.0
) -> tuple[float, float]:
    """Return (R^-(D, v), R^+(D, v)) over the compatible model set Theta(D)."""
    q_low, q_high = compatible_feedback_bounds_general(moments, r_bar)
    denom_low = 1.0 - a - kappa * q_low
    denom_high = 1.0 - a - kappa * q_high
    r_minus = abs(inventory) * v * kappa / denom_low if denom_low > 0 else float("inf")
    r_plus = abs(inventory) * v * kappa / denom_high if denom_high > 0 else float("inf")
    return r_minus, r_plus


def classify_safety_decision(r_minus: float, r_plus: float, budget_B: float) -> str:
    """Theorem B trichotomy: SAFE, UNSAFE, or INSUFFICIENT_INFORMATION."""
    if r_plus <= budget_B:
        return "CERTIFIED_SAFE"
    if r_minus > budget_B:
        return "CERTIFIED_UNSAFE"
    return "INSUFFICIENT_INFORMATION"


def theorem_C_minimum_observations(
    delta_h: np.ndarray, sigma_cov: np.ndarray, beta: float = 0.05, epsilon_loss_frac: float = 0.45
) -> float:
    """Minimum sample size N_min^safe(theta_0, theta_1; beta, epsilon) from Theorem C:
    KL(P_0^N || P_1^N) = (N/2) delta_h^T Sigma^{-1} delta_h,
    TV <= sqrt(KL / 2) => N >= 4 (1 - beta - epsilon)^2 / (delta_h^T Sigma^{-1} delta_h).
    """
    snr_per_obs = float(delta_h.T @ np.linalg.solve(sigma_cov, delta_h))
    if snr_per_obs <= 0.0:
        return float("inf")
    margin = max(0.0, 1.0 - beta - epsilon_loss_frac)
    return 4.0 * (margin ** 2) / snr_per_obs


def theorem_C_horizon_for_safety_margin(m0: float, r_bar: float, delta_safe: float) -> int:
    """Lag horizon L*(Delta_safe) sufficient to shrink compatible feedback width below Delta_safe."""
    if delta_safe <= 0 or not (0.0 < r_bar < 1.0):
        raise ValueError("Require delta_safe > 0 and r_bar in (0, 1)")
    ratio = m0 / ((1.0 - r_bar) ** 2 * delta_safe)
    if ratio <= 1.0:
        return 2
    d_needed = math.ceil(math.log(ratio) / math.log(1.0 / r_bar))
    return 2 + max(0, d_needed - 1)
