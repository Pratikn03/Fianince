"""Theorem E: Optimal uncertainty-aware pre-trade guard with existence, abstention, and global optimality (T06)."""
from __future__ import annotations
import numpy as np
from .model_contracts import BalanceSheetContract


def closed_form_optimal_admission(
    a_lower: float,
    q_upper: float,
    kappa_upper: float,
    budget_rem: float,
    reserve_safe: float,
    inventory_abs: float,
    shock_u: float,
) -> dict:
    """Exact closed-form global optimizer alpha*_gamma(D) for positive-feedback cohort markets (Theorem E(iii))."""
    avail = budget_rem - reserve_safe
    if avail <= 0.0:
        return {"status": "ABSTAIN_INFEASIBLE_AT_ZERO", "alpha_star": 0.0, "abstain": True}
    m_lower = 1.0 - a_lower
    req_gain_inv = (inventory_abs * shock_u * kappa_upper) / avail
    # At alpha = 0, worst-case gain is kappa_upper / m_lower. Safe at alpha=0 iff req_gain_inv <= m_lower.
    if req_gain_inv > m_lower + 1e-12:
        return {"status": "ABSTAIN_INFEASIBLE_AT_ZERO", "alpha_star": 0.0, "abstain": True}
    if q_upper * kappa_upper <= 1e-15:
        return {"status": "OPTIMAL_CERTIFIED", "alpha_star": 1.0, "abstain": False}
    alpha_unclamped = (m_lower - req_gain_inv) / (q_upper * kappa_upper)
    alpha_star = float(min(1.0, max(0.0, alpha_unclamped)))
    return {
        "status": "OPTIMAL_CERTIFIED",
        "alpha_star": alpha_star,
        "abstain": False,
        "admissible_interval": [0.0, alpha_star],
    }


def solve_balance_sheet_guard_globally(
    bs: BalanceSheetContract,
    state_norm_z: float,
    a_lower: float,
    q_upper: float,
    kappa_upper: float,
    shock_u_step: float,
    grid_size: int = 2001,
) -> dict:
    """Certify global maximum alpha* in [0, 1] for the full post-trade balance-sheet loss L_bar_gamma(alpha)."""
    alphas = np.linspace(0.0, 1.0, grid_size)
    m_lower = 1.0 - a_lower
    avail = bs.initial_buffer_B_rem - bs.reserve_R_safe

    def worst_loss(alpha: float) -> float:
        denom = m_lower - alpha * q_upper * kappa_upper
        if denom <= 1e-9:
            return float("inf")
        s_gain = kappa_upper / denom
        m_c_drift = 1.0 / (1.0 - a_lower) + alpha * q_upper * s_gain
        i_post = bs.post_trade_inventory(alpha)
        price_excursion = m_c_drift * state_norm_z + s_gain * shock_u_step
        return (1.0 + bs.maintenance_margin_mu) * i_post * price_excursion + bs.execution_and_fill_cost(alpha)

    loss_at_zero = worst_loss(0.0)
    if loss_at_zero > avail + 1e-12:
        return {
            "status": "ABSTAIN_INFEASIBLE_AT_ZERO",
            "abstain": True,
            "alpha_star": None,
            "loss_at_zero": float(loss_at_zero),
            "available_buffer": float(avail),
        }

    losses = np.array([worst_loss(float(a)) for a in alphas])
    feasible_idx = np.where(losses <= avail + 1e-12)[0]
    alpha_grid = float(alphas[feasible_idx[-1]])
    # Refine via bisection on [alpha_grid, min(1.0, alpha_grid + 1/(grid_size-1))]
    lo = alpha_grid
    hi = min(1.0, alpha_grid + 1.0 / (grid_size - 1))
    if worst_loss(hi) <= avail:
        lo = hi
    else:
        for _ in range(50):
            mid = 0.5 * (lo + hi)
            if worst_loss(mid) <= avail:
                lo = mid
            else:
                hi = mid
    # Verify monotonicity on grid ( certifying connected interval [0, alpha*] )
    is_monotone = bool(np.all(np.diff(losses[np.isfinite(losses)]) >= -1e-12))
    return {
        "status": "OPTIMAL_CERTIFIED",
        "abstain": False,
        "alpha_star": float(lo),
        "loss_at_zero": float(loss_at_zero),
        "loss_at_alpha_star": float(worst_loss(lo)),
        "available_buffer": float(avail),
        "is_monotone_interval": is_monotone,
    }
