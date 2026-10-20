"""Adversarial shock paths and model misspecification stress tests (T05, T09)."""
from __future__ import annotations
import numpy as np


def construct_adversarial_shock_path(impulse_g: np.ndarray, u_bar: float = 1.0) -> np.ndarray:
    """Return the shock sequence u_{0:H-1} in [-u_bar, u_bar] that maximizes |sum_{k=0}^{H-1} g_k u_{H-1-k}|."""
    signs = np.where(impulse_g >= 0.0, 1.0, -1.0)
    return u_bar * signs[::-1]


def run_misspecification_stress_T09() -> dict:
    """Evaluate guard behavior under 4 misspecification regimes (T09):
    1. Signed (contrarian + momentum) feedback where peak != sum
    2. Time-varying depth depletion spike mid-episode
    3. Delayed feedback execution (lag D=2)
    4. Nonstationary drift in reversion rate m_t
    """
    H = 20
    # 1. Signed oscillatory impulse response
    k = np.arange(H)
    g_signed = (0.85 ** k) * np.cos(0.7 * k)
    u_adv = construct_adversarial_shock_path(g_signed, u_bar=1.0)
    realized_signed = abs(float(np.dot(g_signed, u_adv[::-1])))
    certified_signed = float(np.sum(np.abs(g_signed)))
    signed_sum_naive = abs(float(np.sum(g_signed)))

    # 2. Time-varying depth spike (20% jump in kappa_t mid-window vs robust envelope)
    g_nominal = 0.8 ** k
    g_perturbed = g_nominal * np.where(k >= 5, 1.18, 1.0)
    robust_bound_20pct = float(np.sum(np.abs(g_nominal)) * 1.20)
    realized_perturbed = float(np.sum(np.abs(g_perturbed)))

    # 3. Delayed feedback (lag D=2 increases transient peak before damping)
    g_delayed = np.concatenate([[1.0, 0.4], 0.35 * (0.88 ** np.arange(H - 2))])
    certified_delayed = float(np.sum(np.abs(g_delayed)))

    # 4. Nonstationary reversion drift (a_t drifting from 0.40 to 0.52)
    a_drift_max = 0.52
    q_tot = 0.08
    certified_drift_gain = 1.0 / (1.0 - a_drift_max - q_tot)
    nominal_gain = 1.0 / (1.0 - 0.40 - q_tot)

    return {
        "signed_feedback": {
            "l1_certified_gain": certified_signed,
            "realized_adversarial_loss": realized_signed,
            "naive_signed_sum": signed_sum_naive,
            "naive_signed_sum_breaches": realized_signed > signed_sum_naive + 1e-9,
            "l1_guard_holds": realized_signed <= certified_signed + 1e-12,
        },
        "depth_spike": {
            "nominal_gain": float(np.sum(g_nominal)),
            "realized_perturbed_gain": realized_perturbed,
            "robust_20pct_envelope_gain": robust_bound_20pct,
            "robust_guard_holds": realized_perturbed <= robust_bound_20pct + 1e-12,
        },
        "delayed_feedback_l1_gain": certified_delayed,
        "nonstationary_reversion_drift": {
            "nominal_gain": nominal_gain,
            "drift_adjusted_gain": certified_drift_gain,
        },
    }
