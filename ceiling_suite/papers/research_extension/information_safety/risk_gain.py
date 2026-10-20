"""Risk gains of a fixed linear market (blueprint D1; Paper 2, corrected quantity gate and Theorem thm:guard).

For z_{t+1} = J z_t + H v_t, y_t = C z_t and independent scalar shocks |v_j| <= V, the worst price excursion at horizon t is
    sup |C J^t z_0 + sum_{j<t} C J^{t-1-j} H v_j| = |C J^t z_0| + V sum_{k<t} |C J^k H|        (attained by aligned signs).
With a total budget sum |v_j| <= W it is |C J^t z_0| + W max_k |C J^k H|; with both, see adversarial_paths.support_joint.
The peak gain max_k |C J^k H| is the right allowance only for a single shock, not for repeated per-period trading.
"""
import numpy as np


def impulse_coeffs(C, J, H, T):
    C, J, H = np.asarray(C, float), np.asarray(J, float), np.asarray(H, float)
    g, P = [], np.eye(len(J))
    for _ in range(T):
        g.append(float(C @ P @ H)); P = J @ P
    return np.array(g)


def worst_excursion_per_period(C, J, H, z0, V, t):
    drift = abs(float(np.asarray(C) @ np.linalg.matrix_power(np.asarray(J, float), t) @ np.asarray(z0, float)))
    return drift + V * np.abs(impulse_coeffs(C, J, H, t)).sum()


def worst_excursion_total_budget(C, J, H, z0, W, t):
    drift = abs(float(np.asarray(C) @ np.linalg.matrix_power(np.asarray(J, float), t) @ np.asarray(z0, float)))
    g = impulse_coeffs(C, J, H, t)
    return drift + W * (np.abs(g).max() if len(g) else 0.0)


def worst_over_horizons(C, J, H, z0, V, T):
    """Maximum over t <= T of the per-time support functions (the worst time is part of the adversary's choice)."""
    return max(worst_excursion_per_period(C, J, H, z0, V, t) for t in range(1, T + 1))


def peak_gain(C, J, H, T):
    return float(np.abs(impulse_coeffs(C, J, H, T)).max())


def summed_gain(C, J, H, T):
    return float(np.abs(impulse_coeffs(C, J, H, T)).sum())
