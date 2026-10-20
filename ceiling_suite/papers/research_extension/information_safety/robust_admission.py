"""Theorem E: robust admission in the cohort throttle model. Admitting a fraction alpha of algorithmic flow scales the merged
measure by alpha, so S(alpha) = kappa / (1 - a - kappa alpha Phi). Worst-case loss over an unbounded horizon for inventory I
and per-period shocks |u| <= ubar is |I| ubar S(alpha) (all h_t >= 0)."""
import numpy as np


def alpha_star(a, kappa, Phi_up, I, ubar, B):
    """Largest alpha in [0,1] safe for every Phi <= Phi_up; None if even alpha = 0 is unsafe (halt, reduce inventory)."""
    if abs(I) * ubar * kappa / (1 - a) > B:
        return None
    if Phi_up <= 0:
        return 1.0
    return float(min(1.0, max(0.0, (1 - a - kappa * abs(I) * ubar / B) / (kappa * Phi_up))))


def S_alpha(a, kappa, Phi, alpha):
    den = 1 - a - kappa * alpha * Phi
    return np.inf if den <= 0 else kappa / den


def Phi_from_S(a, kappa, S):
    return (1 - a - kappa / S) / kappa
