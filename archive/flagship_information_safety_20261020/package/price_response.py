"""Exact rational and floating-point impulse-response and moment-bijection routines."""
from __future__ import annotations
from fractions import Fraction
import numpy as np
from .model_contracts import PositiveMemoryMarket


def exact_impulse_response(market: PositiveMemoryMarket, max_lag: int) -> list[Fraction]:
    """Compute exact rational impulse response h_0, h_1, ..., h_{max_lag}."""
    x = market.kappa
    ys = [Fraction(0) for _ in range(market.num_cohorts)]
    hs = [x]
    for _ in range(max_lag):
        x_next = market.a * x + sum(ys, Fraction(0))
        ys_next = [
            (Fraction(1) - eta) * y + eta * q * x
            for eta, q, y in zip(market.etas, market.qs, ys)
        ]
        x, ys = x_next, ys_next
        hs.append(x)
    return hs


def closed_to_open_moments_rational(hs: list[Fraction], a: Fraction) -> list[Fraction]:
    """Recover open-loop memory moments m_0, ..., m_{L-2} from h_0, ..., h_L via Paper 1 Prop 6.1."""
    if len(hs) < 3:
        return []
    L = len(hs) - 1
    ms: list[Fraction] = []
    for k in range(2, L + 1):
        conv = sum((ms[j] * hs[k - 2 - j] for j in range(k - 2)), Fraction(0))
        m_km2 = (hs[k] - a * hs[k - 1] - conv) / hs[0]
        ms.append(m_km2)
    return ms


def closed_to_open_moments_float(hs: np.ndarray, a: float) -> np.ndarray:
    """Floating-point bijection from closed-loop impulse h_{0:L} to open-loop moments m_{0:L-2}."""
    if len(hs) < 3:
        return np.zeros(0, dtype=float)
    L = len(hs) - 1
    ms = np.zeros(L - 1, dtype=float)
    for k in range(2, L + 1):
        conv = sum(ms[j] * hs[k - 2 - j] for j in range(k - 2))
        ms[k - 2] = (hs[k] - a * hs[k - 1] - conv) / hs[0]
    return ms


def transition_matrix_float(market: PositiveMemoryMarket, alpha: float = 1.0) -> np.ndarray:
    """Construct the (1 + K) x (1 + K) transition matrix J(alpha) with admission scaling alpha."""
    K = market.num_cohorts
    J = np.zeros((1 + K, 1 + K), dtype=float)
    J[0, 0] = float(market.a)
    J[0, 1:] = float(alpha)
    for i, (eta, q) in enumerate(zip(market.etas, market.qs), start=1):
        J[i, 0] = float(eta * q)
        J[i, i] = float(1 - eta)
    return J
