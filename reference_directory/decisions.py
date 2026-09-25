"""Directional decision rules, two-world abstention bounds, and solvency non-transfer.

Implements:
1. Theorem 10.1: Directionally valid classifications and conditional error bound.
2. Theorem 10.2: Two-world abstention bound c <= min(1, 2e + 2*Phi(d/2) - 1).
3. Proposition 11.1: Solvency non-transfer counterexample under stable linear signals.
"""
from typing import Dict, Any, List, Optional
import numpy as np
from scipy import stats


def classify_interval(L_S: float, U_S: float) -> str:
    """Issue directional stability classification (Theorem 10.1).

    Returns:
      'STABLE' if U_S < 1.0
      'UNSTABLE' if L_S > 1.0
      'ABSTAIN' otherwise
    """
    if L_S > U_S + 1e-9:
        return "CONFLICT"
    if U_S < 1.0:
        return "STABLE"
    elif L_S > 1.0:
        return "UNSTABLE"
    else:
        return "ABSTAIN"


def compute_two_world_abstention_bound(
    e: float,
    d: Optional[float] = None,
    tv: Optional[float] = None,
    p_star: Optional[float] = None,
) -> float:
    """Calculate the two-world decision coverage bound (Theorem 10.2).

    c <= min(1, 2 * e + TV(P_0, P_1))
    For equal-covariance Gaussians:
      TV = 2 * Phi(d/2) - 1 = 1 - 2 * p_star, where p_star = Phi(-d/2).
      c <= min(1, 2 * e + 1 - 2 * p_star).
    """
    if tv is not None:
        total_var = tv
    elif d is not None:
        total_var = float(2.0 * stats.norm.cdf(d / 2.0) - 1.0)
    elif p_star is not None:
        total_var = float(1.0 - 2.0 * p_star)
    else:
        raise ValueError("Must provide either tv, d, or p_star.")

    bound = float(min(1.0, 2.0 * e + total_var))
    return bound


def simulate_solvency_shock(
    r: float,
    E_0: float,
    I: float,
    P_0: float,
    pi: float,
    num_paths: int = 10000,
    seed: int = 240926,
) -> Dict[str, Any]:
    """Simulate the account solvency non-transfer counterexample (Proposition 11.1).

    Account holds I > 0 shares with initial equity E_0 > 0.
    Signal persistence r in [0, 1) is stable.
    Innovation at designated shock time is -2 * E_0 / I with probability pi, else 0.
    Insolvency occurs on shock event where equity becomes -E_0.
    """
    if not (0.0 <= r < 1.0):
        raise ValueError("Signal persistence r must be in [0, 1).")
    if E_0 <= 0 or I <= 0:
        raise ValueError("Initial equity and shares must be positive.")
    if P_0 <= 2.0 * E_0 / I:
        raise ValueError("P_0 must exceed 2 * E_0 / I to maintain positive price post-shock.")

    rng = np.random.default_rng(seed)
    shock_events = rng.uniform(0.0, 1.0, size=num_paths) < pi

    # Shock size
    shock_size = -2.0 * E_0 / I
    innovations = np.where(shock_events, shock_size, 0.0)

    # Prices and Equities
    prices = P_0 + innovations
    equities = E_0 + I * innovations

    insolvent_count = int(np.sum(equities <= 0.0))
    insolvency_rate = float(insolvent_count / num_paths)

    return {
        "signal_persistence_r": r,
        "is_signal_stable": bool(r < 1.0),
        "target_pi": pi,
        "observed_insolvency_rate": insolvency_rate,
        "empirical_insolvent_count": insolvent_count,
        "num_paths": num_paths,
        "min_equity_on_shock": float(np.min(equities)),
        "min_price_on_shock": float(np.min(prices)),
    }
