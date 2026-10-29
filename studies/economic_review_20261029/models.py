"""Price-first positive-cohort model, with initial memories in their original units."""
from __future__ import annotations

import numpy as np


def validate(a, kappa, q, eta, alpha=1.0):
    q, eta = np.asarray(q, dtype=float), np.asarray(eta, dtype=float)
    if q.ndim != 1 or q.size == 0 or q.shape != eta.shape:
        raise ValueError("q and eta must be nonempty vectors of equal length")
    if not np.all(np.isfinite(np.r_[a, kappa, alpha, q, eta])):
        raise ValueError("parameters must be finite")
    if not (0 <= a < 1 and kappa > 0 and 0 <= alpha <= 1):
        raise ValueError("require 0 <= a < 1, kappa > 0, 0 <= alpha <= 1")
    if np.any(q < 0) or np.any(eta <= 0) or np.any(eta > 1):
        raise ValueError("positive class requires q >= 0 and 0 < eta <= 1")
    return q, eta


def state_matrix(a, kappa, q, eta, alpha=1.0):
    q, eta = validate(a, kappa, q, eta, alpha)
    price = np.r_[a, alpha * kappa * q]
    memory = eta[:, None] * price[None, :]
    memory[:, 1:] += np.diag(1 - eta)
    return np.vstack([price, memory])


def impulse(a, kappa, q, eta, horizon, alpha=1.0):
    """h[0]=kappa, memories after the impact equal eta*kappa."""
    if not isinstance(horizon, int) or horizon < 1:
        raise ValueError("horizon must be a positive integer")
    J = state_matrix(a, kappa, q, eta, alpha)
    z = np.r_[kappa, np.asarray(eta) * kappa]
    h = np.empty(horizon)
    for t in range(horizon):
        h[t], z = z[0], J @ z
    return h


def cumulative_drift(a, kappa, q, eta, x0, y0, alpha=1.0):
    """Signed future sum; also the absolute sum for aligned nonnegative states."""
    q, eta = validate(a, kappa, q, eta, alpha)
    y0 = np.asarray(y0, dtype=float)
    if y0.shape != q.shape or not np.all(np.isfinite(np.r_[x0, y0])):
        raise ValueError("invalid initial state")
    margin = 1 - a - alpha * kappa * q.sum()
    if margin <= 0:
        raise ValueError("cumulative formula requires strict stability")
    return float((a * x0 + alpha * kappa * np.sum(q * y0 / eta)) / margin)


def box_admission(a, kappa, phi_upper, budget, inventory, shock_bound, x0, memory_bound):
    """Sufficient invariant-box admission for fixed mark-to-market exposure.

    None means this box argument gives no certificate, not that no safe action exists.
    No fills, changing inventory, fundamental-value uncertainty or maintenance margin.
    """
    vals = np.array([a, kappa, phi_upper, budget, inventory, shock_bound, x0, memory_bound])
    if not np.all(np.isfinite(vals)) or not (0 <= a < 1 and kappa > 0):
        raise ValueError("invalid plant or nonfinite input")
    if min(phi_upper, budget, shock_bound, memory_bound) < 0:
        raise ValueError("bounds must be nonnegative")
    if inventory == 0:
        return 1.0
    L = budget / abs(inventory)
    if L <= 0 or max(abs(x0), memory_bound) > L:
        return None
    slack = (1 - a) * L - kappa * shock_bound
    if slack < 0:
        return None
    if phi_upper == 0:
        return 1.0
    alpha = min(1.0, slack / (kappa * phi_upper * L))
    if a + alpha * kappa * phi_upper >= 1:
        return None  # no strict-stability certificate at an unforced boundary
    return float(alpha)


def finite_peak_envelope(a, kappa, q, eta, x0, memory_bound, shock_bound, horizon, alpha=1.0):
    """Exact maximum |x_t|, 0<=t<=H, for fixed positive model and a memory box.

    Positivity makes the triangle bound simultaneously attainable by aligned memories
    and constant shocks of the sign of x0 (either sign when x0=0).
    """
    J = state_matrix(a, kappa, q, eta, alpha)
    if min(memory_bound, shock_bound) < 0 or horizon < 0:
        raise ValueError("bounds and horizon must be nonnegative")
    z = np.r_[abs(x0), np.full(len(q), memory_bound)]
    b = np.r_[kappa, np.asarray(eta) * kappa]
    path = [float(z[0])]
    for _ in range(horizon):
        z = J @ z + b * shock_bound
        path.append(float(z[0]))
    return np.asarray(path)


def uniform_tail(a, kappa, phi_upper, eta_floor, horizon):
    """A conservative rigorous class bound: ||J||_infinity <= lambda < 1."""
    if not (0 <= a < 1 and kappa > 0 and phi_upper >= 0 and 0 < eta_floor <= 1):
        raise ValueError("invalid class envelope")
    s = a + kappa * phi_upper
    if s >= 1 or horizon < 1:
        raise ValueError("require a strict class stability envelope and H>=1")
    lam = 1 - eta_floor * (1 - s)
    return float(kappa * lam**horizon / (1 - lam))
