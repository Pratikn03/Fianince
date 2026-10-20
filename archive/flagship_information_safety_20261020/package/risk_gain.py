"""Cumulative convolution gain vs peak gain and exhaustive sign enumeration (T05)."""
from __future__ import annotations
import itertools
import numpy as np


def cumulative_convolution_gain(impulse_g: np.ndarray, horizon_H: int | None = None) -> float:
    """Return G_{cum,H} = sum_{k=0}^{H-1} |g_k|."""
    g = impulse_g if horizon_H is None else impulse_g[:horizon_H]
    return float(np.sum(np.abs(g)))


def single_shock_peak_gain(impulse_g: np.ndarray, horizon_H: int | None = None) -> float:
    """Return G_{single,H} = max_{k < H} |g_k|."""
    g = impulse_g if horizon_H is None else impulse_g[:horizon_H]
    return float(np.max(np.abs(g))) if len(g) > 0 else 0.0


def exhaustive_worst_case_disturbance(impulse_g: np.ndarray, v_bound: float = 1.0) -> tuple[float, np.ndarray]:
    """Enumerate all 2^H sign combinations u_k in {-v_bound, +v_bound} for H <= 12 to verify exact attainment."""
    H = len(impulse_g)
    if H > 12:
        raise ValueError("Exhaustive enumeration restricted to H <= 12")
    best_val = -1.0
    best_u = np.zeros(H, dtype=float)
    for signs in itertools.product((-1.0, 1.0), repeat=H):
        u = v_bound * np.array(signs, dtype=float)
        # Convolution at final step H-1: sum_{k=0}^{H-1} g_k * u_{H-1-k}
        val = abs(float(np.dot(impulse_g, u[::-1])))
        if val > best_val:
            best_val = val
            best_u = u
    return best_val, best_u


def repeated_vs_peak_gate_counterexample(
    impulse_g: np.ndarray, budget_B: float = 1.0, drift_b: float = 0.0, c_exec: float = 0.0
) -> dict:
    """Demonstrate that admitting v*_single = (B - |b|) / G_single under repeated trades breaches budget B."""
    g_cum = cumulative_convolution_gain(impulse_g)
    g_single = single_shock_peak_gain(impulse_g)
    avail = max(0.0, budget_B - abs(drift_b))
    v_repeated = avail / (g_cum + c_exec)
    v_single = avail / (g_single + c_exec)
    realized_loss_under_peak_gate = abs(drift_b) + v_single * (g_cum + c_exec)
    return {
        "G_cum": g_cum,
        "G_single": g_single,
        "v_star_repeated": v_repeated,
        "v_star_single": v_single,
        "budget_B": budget_B,
        "realized_loss_under_peak_gate": realized_loss_under_peak_gate,
        "breach_ratio": realized_loss_under_peak_gate / budget_B if budget_B > 0 else float("inf"),
        "repeated_gate_is_safe": (abs(drift_b) + v_repeated * (g_cum + c_exec)) <= budget_B + 1e-12,
        "peak_gate_breaches": realized_loss_under_peak_gate > budget_B + 1e-12,
    }
