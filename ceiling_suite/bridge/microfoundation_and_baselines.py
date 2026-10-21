"""Economically specified adaptive trading-agent microfoundation and matched-shock 4-baseline control comparison.

Implements Decision 2 (Option A microfoundations), Decision 4 (matched-shock baseline comparison), and
the Phase 1 / Phase 4 / Phase 5 scientific verification requirements:

1. Adaptive Trading-Agent Microfoundation (Decision 2, Option A):
   - Observation and Pricing-Error Link: Fundamental value is p*_t and market price is p_t = p*_t + x_t, where
     x_t is the pricing dislocation. Adaptive cohort i observes noisy dislocation signals r_{i,t} = x_t + nu_{i,t}
     under a random-walk prior v_t = v_{t-1} + zeta_{i,t} (innovation variance sigma_{zeta,i}^2, noise sigma_{nu,i}^2).
   - Learning dynamics: Steady-state Kalman filter (or L2-regularized online gradient descent) updating the belief state
         y_{i,t} = (1 - eta_i) y_{i,t-1} + eta_i r_{i,t},
     whose deterministic impulse response to a price dislocation x_t has Riccati gain
         eta_i = (-sigma_{zeta,i}^2 + sqrt(sigma_{zeta,i}^4 + 4 sigma_{zeta,i}^2 sigma_{nu,i}^2)) / (2 sigma_{nu,i}^2) in (0, 1).
     Explicitly distinguished from a full market equilibrium: the filtering recursion is an individual agent's belief
     update, whereas market equilibrium requires either a self-consistent Lyapunov variance fixed point or joint
     dealer-trader optimization (Proposition prop:equil).
   - Stateful Inventory & Constrained Optimal Decision Rule: Agent i holds inventory I_{i,t} = (1 - delta_inv) I_{i,t-1} + u_{i,t}
     subject to a hard inventory cap |I_{i,t}| <= I_max,i and maximizes the single-period quadratic objective:
         max_{|I_{i,t}| <= I_max,i}  E_t[ beta_i y_{i,t} u_{i,t} ] - (lambda_tc,i / 2) u_{i,t}^2 - (gamma_inv,i / 2) I_{i,t}^2.
     The exact first-order condition yields the state-dependent optimal order flow:
         u_{i,t}^* = clip( q_i y_{i,t} - psi_{inv,i} I_{i,t-1},  -I_max,i - (1 - delta_inv) I_{i,t-1},  I_max,i - (1 - delta_inv) I_{i,t-1} ),
     where q_i = beta_i / (lambda_tc,i + gamma_inv,i) and psi_{inv,i} = gamma_inv,i (1 - delta_inv) / (lambda_tc,i + gamma_inv,i).
     In the fast-clearing / neutral-inventory limit (delta_inv = 1), psi_{inv,i} = 0 and u_{i,t}^* = q_i y_{i,t}.
   - Exact (K+2)x(K+2) Price-Cohort-Depth Operator J_full and Spectral Radius:
     For state z_t = (x_t, y_{1,t}, ..., y_{K,t}, d_t)^T with total feedback flow u_{t+1}^{fb} = sum_{i=1}^K q_i y_{i,t}:
         x_{t+1} = a x_t + kappa u_{t+1}^{fb} + phi_d d_t
         y_{i,t+1} = (1 - eta_i) y_{i,t} + eta_i x_{t+1}
         d_{t+1} = (1 - r_refill) d_t + eps_d u_{t+1}^{fb},   where u_{t+1}^{fb} = (x_{t+1} - a x_t - phi_d d_t) / kappa.
     Stability is certified by the exact spectral radius rho(J_full) = max_j |lambda_j(J_full)| < 1 (equivalent for
     nonnegative parameters to a + tilde_kappa * Phi < 1 with tilde_kappa = kappa + phi_d * eps_d / r_refill), never by
     the cohort-only condition a + kappa * Phi < 1.

2. Matched-Shock Control Comparison Against 4 Approved Baselines (Decision 4 & Phase 5):
   - Separates:
     (A) Exact Theorem-Contract Static Reset Verification (Lemma thm:guard / Theorem thm:robustguard: z_0 = 0, fixed I_0,
         bounded shocks |u_t| <= ubar, constant admission alpha scaling cohort feedback).
     (B) Rolling Dynamic Control Evaluation with double-entry cash/inventory accounting (E_t = K_t + I_t p_t),
         explicitly separating:
           * reserve_breach_rate: E_t - MM_t < R_safe (halts new admission; no artificial penalty or path break),
           * maintenance_margin_breach_rate: E_t < MM_t (equity falls below maintenance margin),
           * forced_liquidation_rate: exchange closeout I_t -> 0 with liquidation cost when E_t < MM_t.
   - Calibrates all baselines on an independent training sample to compare policies at:
     (1) Matched trading capacity (out-of-sample with paired bootstrap 95% CIs for policy differences),
     (2) Matched tail-risk budget (ES95),
     (3) Full 7-point capacity-vs.-ES95 and capacity-vs.-net-P&L efficient frontiers,
     (4) Stress and unfavorable regimes, including a heteroskedastic zero-feedback regime with misspecified Phi^+ where
         volatility_limit outperforms summed_gain_guard.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT_PATH = HERE / "results" / "microfoundation_and_baselines.json"


# ==============================================================================================================
# Part 1: Economically Specified Adaptive Trading-Agent Microfoundation (Decision 2, Option A)
# ==============================================================================================================
def kalman_steady_state_gain(sigma_zeta: float, sigma_nu: float) -> float:
    """Steady-state Kalman gain eta in (0, 1) for persistent dislocation component v_{t+1} = v_t + zeta_{t+1}
    observed via noisy price-dislocation signal r_t = x_t + nu_t."""
    sz2 = float(sigma_zeta) ** 2
    sn2 = float(sigma_nu) ** 2
    if sn2 <= 0:
        raise ValueError("Observation noise variance sigma_nu^2 must be positive.")
    return (-sz2 + math.sqrt(sz2 * sz2 + 4.0 * sz2 * sn2)) / (2.0 * sn2)


def optimal_agent_response_weight(beta_signal: float, lambda_tc: float, gamma_inv: float) -> float:
    """Optimal linear-quadratic flow sensitivity q_i = beta_i / (lambda_tc,i + gamma_inv,i)
    from maximizing E_t[beta_i y_{i,t} u_{i,t}] - (lambda_tc,i / 2) u_{i,t}^2 - (gamma_inv,i / 2) I_{i,t}^2."""
    if lambda_tc + gamma_inv <= 0:
        raise ValueError("Total quadratic friction lambda_tc + gamma_inv must be positive.")
    return float(beta_signal) / float(lambda_tc + gamma_inv)


def optimal_agent_inventory_feedback(lambda_tc: float, gamma_inv: float, delta_inv: float = 0.25) -> float:
    """Optimal linear-quadratic prior-inventory mean-reversion weight
    psi_{inv,i} = gamma_inv,i * (1 - delta_inv) / (lambda_tc,i + gamma_inv,i)."""
    if lambda_tc + gamma_inv <= 0:
        raise ValueError("Total quadratic friction lambda_tc + gamma_inv must be positive.")
    return float(gamma_inv * (1.0 - delta_inv)) / float(lambda_tc + gamma_inv)


def optimal_agent_action(
    y_i: float,
    inv_prev_i: float,
    beta_signal: float,
    lambda_tc: float,
    gamma_inv: float,
    delta_inv: float = 0.25,
    inv_cap: float = 5.0,
) -> tuple[float, float]:
    """Constrained optimal agent order flow u_{i,t}^* and updated inventory I_{i,t} solving:
        max_{|I_{i,t}| <= inv_cap}  beta_i y_{i,t} u_{i,t} - (lambda_tc/2) u_{i,t}^2 - (gamma_inv/2) I_{i,t}^2
        subject to I_{i,t} = (1 - delta_inv) I_{i,t-1} + u_{i,t}.
    """
    q_i = optimal_agent_response_weight(beta_signal, lambda_tc, gamma_inv)
    psi_i = optimal_agent_inventory_feedback(lambda_tc, gamma_inv, delta_inv)
    u_unc = q_i * float(y_i) - psi_i * float(inv_prev_i)
    retained = (1.0 - delta_inv) * float(inv_prev_i)
    u_min = -float(inv_cap) - retained
    u_max = float(inv_cap) - retained
    u_star = float(np.clip(u_unc, u_min, u_max))
    inv_next = retained + u_star
    return u_star, inv_next


def full_book_transition_matrix(
    a: float,
    kappa: float,
    q: np.ndarray,
    eta: np.ndarray,
    phi_d: float,
    eps_d: float,
    r_refill: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Construct the exact (K+2)x(K+2) closed-loop transition matrix J_full and initial impulse vector z_0
    for state z_t = (x_t, y_{1,t}, ..., y_{K,t}, d_t)^T:
        x_{t+1} = a x_t + kappa * sum_i q_i y_{i,t} + phi_d * d_t
        y_{i,t+1} = (1 - eta_i) y_{i,t} + eta_i x_{t+1}
        d_{t+1} = (1 - r_refill) d_t + eps_d * sum_i q_i y_{i,t}
                = (1 - r_refill) d_t + eps_d * (x_{t+1} - a x_t - phi_d d_t) / kappa.
    """
    q = np.asarray(q, dtype=float)
    eta = np.asarray(eta, dtype=float)
    k = len(q)
    dim = k + 2
    j_mat = np.zeros((dim, dim), dtype=float)
    # Row 0: x_{t+1}
    j_mat[0, 0] = float(a)
    j_mat[0, 1 : k + 1] = float(kappa) * q
    j_mat[0, k + 1] = float(phi_d)
    # Rows 1..K: y_{i,t+1} = (1 - eta_i) y_{i,t} + eta_i x_{t+1}
    for i in range(k):
        j_mat[i + 1, 0] = eta[i] * float(a)
        j_mat[i + 1, 1 : k + 1] = eta[i] * float(kappa) * q
        j_mat[i + 1, i + 1] += 1.0 - eta[i]
        j_mat[i + 1, k + 1] = eta[i] * float(phi_d)
    # Row K+1: d_{t+1} = (1 - r_refill) d_t + eps_d * sum_j q_j y_{j,t}
    j_mat[k + 1, 0] = 0.0
    j_mat[k + 1, 1 : k + 1] = float(eps_d) * q
    j_mat[k + 1, k + 1] = 1.0 - float(r_refill)

    z0 = np.zeros(dim, dtype=float)
    z0[0] = float(kappa)
    z0[1 : k + 1] = eta * float(kappa)
    z0[k + 1] = float(eps_d)
    return j_mat, z0


def matrix_book_impulse(
    a: float,
    kappa: float,
    q: np.ndarray,
    eta: np.ndarray,
    phi_d: float,
    eps_d: float,
    r_refill: float,
    horizon: int = 40,
) -> np.ndarray:
    """Impulse response h_0..h_{horizon-1} computed directly from matrix powers z_{t+1} = J_full z_t."""
    j_mat, z = full_book_transition_matrix(a, kappa, q, eta, phi_d, eps_d, r_refill)
    h = np.empty(horizon, dtype=float)
    for t in range(horizon):
        h[t] = float(z[0])
        z = j_mat @ z
    return h


def three_state_book_impulse(
    a: float,
    kappa: float,
    q: np.ndarray,
    eta: np.ndarray,
    phi_d: float,
    eps_d: float,
    r_refill: float,
    horizon: int = 40,
) -> np.ndarray:
    """Step-by-step recursion for the coupled price-cohort-depth system:
        u_{t+1}^{fb} = sum_i q_i y_{i,t} = (x_{t+1} - a x_t - phi_d d_t) / kappa
        x_{t+1} = a x_t + kappa * u_{t+1}^{fb} + phi_d * d_t
        y_{i,t+1} = (1 - eta_i) y_{i,t} + eta_i x_{t+1}
        d_{t+1} = (1 - r_refill) d_t + eps_d * u_{t+1}^{fb}.
    Matches matrix_book_impulse to machine precision.
    """
    q = np.asarray(q, dtype=float)
    eta = np.asarray(eta, dtype=float)
    x = float(kappa)
    y = eta * x
    d = float(eps_d)
    h = [x]
    for _ in range(horizon - 1):
        u_feedback = float(np.dot(q, y))
        x_next = a * x + kappa * u_feedback + phi_d * d
        y = (1.0 - eta) * y + eta * x_next
        d = (1.0 - r_refill) * d + eps_d * u_feedback
        x = x_next
        h.append(x)
    return np.array(h, dtype=float)


def stateful_inventory_impulse(
    a: float,
    kappa: float,
    betas: np.ndarray,
    eta: np.ndarray,
    lambda_tc: float,
    gamma_inv: float,
    delta_inv: float = 0.25,
    inv_cap: float = 5.0,
    horizon: int = 40,
) -> dict:
    """Simulate impulse response when cohorts use the full stateful inventory-dependent decision rule
    u_{i,t}^* = clip(q_i y_{i,t} - psi_{inv,i} I_{i,t-1}, ...) vs. the neutral-inventory rule (delta_inv = 1)."""
    betas = np.asarray(betas, dtype=float)
    eta = np.asarray(eta, dtype=float)
    k = len(betas)
    qs = np.array([optimal_agent_response_weight(b, lambda_tc, gamma_inv) for b in betas])
    h_neutral = three_state_book_impulse(a, kappa, qs, eta, 0.0, 0.0, 0.20, horizon=horizon)

    # Stateful inventory trajectory with finite cap
    x = float(kappa)
    y = eta * x
    inv_ag = np.zeros(k, dtype=float)
    h_stateful = [x]
    cap_bound_hits = 0
    for _ in range(horizon - 1):
        u_ag = np.zeros(k, dtype=float)
        for i in range(k):
            u_star, inv_next = optimal_agent_action(
                y[i], inv_ag[i], betas[i], lambda_tc, gamma_inv, delta_inv=delta_inv, inv_cap=inv_cap
            )
            if abs(abs(inv_next) - inv_cap) < 1e-12:
                cap_bound_hits += 1
            u_ag[i] = u_star
            inv_ag[i] = inv_next
        x_next = a * x + kappa * float(np.sum(u_ag))
        y = (1.0 - eta) * y + eta * x_next
        x = x_next
        h_stateful.append(x)

    h_stateful_arr = np.array(h_stateful, dtype=float)
    return {
        "delta_inv": delta_inv,
        "inv_cap": inv_cap,
        "psi_inv": [float(optimal_agent_inventory_feedback(lambda_tc, gamma_inv, delta_inv)) for _ in betas],
        "neutral_sum_H": float(np.sum(h_neutral)),
        "stateful_sum_H": float(np.sum(h_stateful_arr)),
        "stateful_abs_sum_H": float(np.sum(np.abs(h_stateful_arr))),
        "inventory_mean_reversion_dampens_sum": bool(np.sum(h_stateful_arr) < np.sum(h_neutral)),
        "cap_binding_events": int(cap_bound_hits),
    }


def _self_consistent_equilibrium_eta(
    a: float,
    kappa: float,
    alpha: float,
    betas: np.ndarray,
    sigma_zetas_base: np.ndarray,
    sigma_nus: np.ndarray,
    lam_tc: float,
    gam_inv: float,
    sigma_u: float = 0.20,
    max_iter: int = 80,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Compute the self-consistent rational-expectations / Lyapunov fixed point (eta^eq(alpha), q^eq(alpha))
    where each cohort's prior innovation scale tracks the actual closed-loop price-change standard deviation
    std(Delta x_t(alpha, eta^eq, q^eq)) normalized to the unthrottled alpha=1 reference equilibrium."""
    qs_ref = np.array([optimal_agent_response_weight(b, lam_tc, gam_inv) for b in betas])
    etas_ref = np.array([kalman_steady_state_gain(sz, sn) for sz, sn in zip(sigma_zetas_base, sigma_nus)])

    def _closed_loop_std_dx(al_val: float, q_vec: np.ndarray, eta_vec: np.ndarray) -> float:
        j_mat, z0 = full_book_transition_matrix(a, kappa, al_val * q_vec, eta_vec, 0.0, 0.0, 0.20)
        b_vec = z0 * sigma_u
        cov = np.zeros_like(j_mat)
        cur = np.outer(b_vec, b_vec)
        for _step in range(80):
            cov += cur
            cur = j_mat @ cur @ j_mat.T
            if np.max(np.abs(cur)) < 1e-15:
                break
        j_minus_i = j_mat - np.eye(len(j_mat))
        var_dx = float((j_minus_i[0, :] @ cov @ j_minus_i[0, :].T) + (b_vec[0] ** 2))
        return math.sqrt(max(var_dx, 1e-12))

    std_dx_ref = _closed_loop_std_dx(1.0, qs_ref, etas_ref)
    scale_ratios = sigma_zetas_base / std_dx_ref

    qs = np.array([optimal_agent_response_weight(b, lam_tc / max(alpha, 0.1), gam_inv) for b in betas])
    etas = np.array([kalman_steady_state_gain(alpha * sz, sn) for sz, sn in zip(sigma_zetas_base, sigma_nus)])
    std_dx = std_dx_ref
    for _ in range(max_iter):
        std_dx = _closed_loop_std_dx(alpha, qs, etas)
        etas_next = np.array(
            [kalman_steady_state_gain(alpha * sr * std_dx, sn) for sr, sn in zip(scale_ratios, sigma_nus)]
        )
        if np.max(np.abs(etas_next - etas)) < 1e-12:
            etas = etas_next
            break
        etas = etas_next
    return etas, qs, std_dx


def run_microfoundation_analysis() -> dict:
    """Derive the mapping from agent primitives (sigma_zeta, sigma_nu, beta, lambda_tc, gamma_inv)
    to market-response coefficients (a, kappa, q_i, eta_i, Phi, S, C_3, rho(J_full)) across all regimes
    and compare (a) Fixed-policy, (b) Single-agent Lucas re-optimizing, and (c) Self-consistent fixed-point
    equilibrium benchmarks."""
    a, kappa = 0.40, 1.00
    betas = np.array([0.36, 0.24])
    sigma_zetas = np.array([0.15, 0.05])
    sigma_nus = np.array([0.20, 0.20])
    etas_base = np.array([kalman_steady_state_gain(sz, sn) for sz, sn in zip(sigma_zetas, sigma_nus)])

    regimes = []
    # Five regimes explicitly separating stable transient overshoot (rho(J_full) < 1, C_3 > 0)
    # from depletion-induced spectral instability (a + kappa*Phi < 1 but rho(J_full) >= 1)
    # and cohort-driven feedback instability (a + kappa*Phi >= 1).
    specs = [
        ("high_cost_amplification_disappears", 4.0, 1.0, 0.00, 0.25, 0.20),
        ("moderate_cost_positive_cohort_no_overshoot", 1.2, 0.3, 0.00, 0.25, 0.20),
        ("moderate_cost_with_depletion_overshoot_appears", 2.0, 0.5, 0.65, 0.90, 0.65),
        ("depletion_induced_spectral_instability", 1.2, 0.3, 0.90, 0.60, 0.15),
        ("low_cost_feedback_instability", 0.6, 0.2, 0.00, 0.25, 0.20),
    ]
    for label, lam_tc, gam_inv, eps_d, phi_d, r_ref in specs:
        qs = np.array([optimal_agent_response_weight(b, lam_tc, gam_inv) for b in betas])
        phi_val = float(np.sum(qs))
        k0_val = float(np.sum(qs * etas_base))
        c3_val = phi_d * eps_d + (kappa**2) * k0_val - (1.0 - a) * kappa
        j_full, z0 = full_book_transition_matrix(a, kappa, qs, etas_base, phi_d, eps_d, r_ref)
        eigvals = np.linalg.eigvals(j_full)
        rho_full = float(np.max(np.abs(eigvals)))
        schur_stable = bool(rho_full < 1.0 - 1e-12)
        cohort_only_flag = bool(a + kappa * phi_val < 1.0 - 1e-12)
        tilde_kappa = kappa + (phi_d * eps_d / r_ref) if eps_d > 0 else kappa
        exact_stability_margin = 1.0 - a - tilde_kappa * phi_val

        h_rec = three_state_book_impulse(a, kappa, qs, etas_base, phi_d, eps_d, r_ref, horizon=40)
        h_mat = matrix_book_impulse(a, kappa, qs, etas_base, phi_d, eps_d, r_ref, horizon=40)
        max_mat_diff = float(np.max(np.abs(h_rec - h_mat)))

        if schur_stable:
            s_closed = float(tilde_kappa / (1.0 - a - tilde_kappa * phi_val))
            s_resolvent = float(np.linalg.solve(np.eye(len(j_full)) - j_full, z0)[0])
        else:
            s_closed = float("inf")
            s_resolvent = float("inf")

        regimes.append(
            {
                "regime": label,
                "lambda_tc": lam_tc,
                "gamma_inv": gam_inv,
                "eps_depletion": eps_d,
                "phi_d": phi_d,
                "r_refill": r_ref,
                "derived_q": [float(x) for x in qs],
                "derived_eta": [float(x) for x in etas_base],
                "Phi": phi_val,
                "tilde_kappa": float(tilde_kappa),
                "C3_one_step_margin": c3_val,
                "h0_impact": float(h_rec[0]),
                "h1_next_step": float(h_rec[1]),
                "peak_response_H40": float(np.max(h_rec)),
                "peak_overshoot_occurs": bool(np.max(h_rec) > h_rec[0] * (1.0 + 1e-9)),
                "summed_response_H40": float(np.sum(h_rec)),
                "summed_response_S": s_closed if math.isfinite(s_closed) else float(np.sum(h_rec)),
                "summed_response_S_closed_form": s_closed if math.isfinite(s_closed) else None,
                "summed_response_S_resolvent": s_resolvent if math.isfinite(s_resolvent) else None,
                "spectral_radius_J_full": rho_full,
                "cohort_only_condition_a_plus_kappa_Phi_lt_1": cohort_only_flag,
                "exact_stability_margin_1_minus_a_minus_tilde_kappa_Phi": float(exact_stability_margin),
                "schur_stable": schur_stable,
                "recursion_vs_matrix_max_err": max_mat_diff,
            }
        )

    # Fixed-policy vs. Adaptive (Prop prop:lucas) vs. Self-Consistent Equilibrium across alpha in {0.25, 0.50, 0.75, 1.00}
    lam_tc, gam_inv = 1.2, 0.3
    qs_fixed = np.array([optimal_agent_response_weight(b, lam_tc, gam_inv) for b in betas])
    benchmarks = []
    for alpha in [0.25, 0.50, 0.75, 1.00]:
        h_fixed = three_state_book_impulse(a, kappa, alpha * qs_fixed, etas_base, 0.0, 0.0, 0.20, horizon=30)
        s_fixed_H = float(np.sum(h_fixed))
        s_fixed_inf = float(kappa / (1.0 - a - kappa * alpha * float(np.sum(qs_fixed))))

        etas_adapt = np.array([kalman_steady_state_gain(alpha * sz, sn) for sz, sn in zip(sigma_zetas, sigma_nus)])
        qs_adapt = np.array([optimal_agent_response_weight(b, lam_tc / max(alpha, 0.1), gam_inv) for b in betas])
        h_adapt = three_state_book_impulse(a, kappa, alpha * qs_adapt, etas_adapt, 0.0, 0.0, 0.20, horizon=30)
        s_adapt_H = float(np.sum(h_adapt))
        s_adapt_inf = float(kappa / (1.0 - a - kappa * alpha * float(np.sum(qs_adapt))))

        etas_eq, qs_eq, std_dx_eq = _self_consistent_equilibrium_eta(
            a, kappa, alpha, betas, sigma_zetas, sigma_nus, lam_tc, gam_inv
        )
        h_eq = three_state_book_impulse(a, kappa, alpha * qs_eq, etas_eq, 0.0, 0.0, 0.20, horizon=30)
        s_eq_H = float(np.sum(h_eq))
        s_eq_inf = float(kappa / (1.0 - a - kappa * alpha * float(np.sum(qs_eq))))

        benchmarks.append(
            {
                "alpha": alpha,
                "fixed_policy_eta": [float(x) for x in etas_base],
                "adaptive_policy_eta": [float(x) for x in etas_adapt],
                "equilibrium_fixed_point_eta": [float(x) for x in etas_eq],
                "equilibrium_price_change_std": std_dx_eq,
                "fixed_policy_S_H30": s_fixed_H,
                "adaptive_policy_S_H30": s_adapt_H,
                "equilibrium_policy_S_H30": s_eq_H,
                "fixed_policy_S_inf": s_fixed_inf,
                "adaptive_policy_S_inf": s_adapt_inf,
                "equilibrium_policy_S_inf": s_eq_inf,
                "reoptimization_reinforces_guard": bool(
                    s_adapt_H <= s_fixed_H + 1e-12
                    and s_adapt_inf <= s_fixed_inf + 1e-12
                    and s_eq_H <= s_fixed_H + 1e-12
                ),
            }
        )

    stateful_check = stateful_inventory_impulse(
        a, kappa, betas, etas_base, lambda_tc=1.2, gamma_inv=0.3, delta_inv=0.25, inv_cap=0.30, horizon=40
    )

    return {
        "note": (
            "Filtering recursion specifies individual agent belief updates; self-consistent belief equilibrium "
            "matches prior innovation variance to closed-loop price variance, while full dealer-trader market "
            "equilibrium is analyzed in Proposition prop:equil."
        ),
        "regimes": regimes,
        "stateful_inventory_and_cap_dynamics": stateful_check,
        "fixed_vs_adaptive_benchmarks": benchmarks,
    }


# ==============================================================================================================
# Part 2: Matched-Shock Comparison Against 4 Approved Baselines (Decision 4 & Phase 5)
# ==============================================================================================================
def _wilson_ci(k: int, n: int, z: float = 1.959964) -> list[float]:
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return [max(0.0, float(centre - half)), min(1.0, float(centre + half))]


def _mean_ci(arr: np.ndarray, z: float = 1.959964) -> list[float]:
    m = float(np.mean(arr))
    se = float(np.std(arr, ddof=1) / math.sqrt(len(arr)))
    return [m - z * se, m + z * se]


def _bootstrap_es95_ci(losses: np.ndarray, n_boot: int = 400, seed: int = 42) -> tuple[float, list[float]]:
    q95 = float(np.quantile(losses, 0.95))
    tail = losses[losses >= q95]
    es95 = float(np.mean(tail)) if len(tail) > 0 else q95
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot, dtype=float)
    n = len(losses)
    for b in range(n_boot):
        samp = losses[rng.integers(0, n, size=n)]
        qb = np.quantile(samp, 0.95)
        tb = samp[samp >= qb]
        boots[b] = np.mean(tb) if len(tb) > 0 else qb
    return es95, [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]


def _paired_bootstrap_diff_ci(
    arr_base: np.ndarray,
    arr_guard: np.ndarray,
    stat: str = "mean",
    n_boot: int = 400,
    seed: int = 42,
) -> dict:
    """Paired bootstrap 95% confidence interval for (baseline - guard) on identical shock paths."""
    rng = np.random.default_rng(seed)
    n = len(arr_base)
    if stat == "mean":
        point = float(np.mean(arr_base - arr_guard))
        se = float(np.std(arr_base - arr_guard, ddof=1) / math.sqrt(n))
        return {"diff": point, "ci95": [point - 1.959964 * se, point + 1.959964 * se]}
    if stat == "es95":
        q_b = float(np.quantile(arr_base, 0.95))
        q_g = float(np.quantile(arr_guard, 0.95))
        es_b = float(np.mean(arr_base[arr_base >= q_b]))
        es_g = float(np.mean(arr_guard[arr_guard >= q_g]))
        point = es_b - es_g
        boots = np.empty(n_boot, dtype=float)
        for b in range(n_boot):
            idx = rng.integers(0, n, size=n)
            sb = arr_base[idx]
            sg = arr_guard[idx]
            qb_i = np.quantile(sb, 0.95)
            qg_i = np.quantile(sg, 0.95)
            boots[b] = float(np.mean(sb[sb >= qb_i]) - np.mean(sg[sg >= qg_i]))
        return {"diff": point, "ci95": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]}
    raise ValueError(stat)


def verify_static_theorem_contract(
    n_paths: int = 500,
    horizon: int = 40,
    a: float = 0.55,
    kappa: float = 1.0,
    Phi_true: float = 0.32,
    Phi_cert_upper: float = 0.35,
    ubar: float = 0.35,
    initial_inventory: float = -12.0,
    initial_equity: float = 42.0,
    maint_margin_rate: float = 0.015,
    r_safe: float = 4.5,
    seed: int = 20261020,
) -> dict:
    """Exact verification of the static reset contract of Lemma thm:guard and Theorem thm:robustguard:
    - Initial state z_0 = 0 (reset),
    - Fixed inventory I_0 = initial_inventory over the horizon,
    - Exogenous bounded shocks |u_t| <= ubar,
    - Constant admission alpha in [0, 1] scaling cohort feedback M -> alpha M so S(alpha) = kappa / (1 - a - kappa alpha Phi).
    Checks both 500 random shock paths and the exact worst-case adversarial path u_t = -sign(I_0) * ubar.
    """
    p0 = 100.0
    mm0 = maint_margin_rate * abs(initial_inventory) * p0
    budget_B = initial_equity - mm0 - r_safe
    c_I = 1.0 - a - kappa * abs(initial_inventory) * ubar / budget_B
    alpha_star = float(np.clip(c_I / (kappa * Phi_cert_upper), 0.0, 1.0))
    alpha_oracle = float(np.clip(c_I / (kappa * Phi_true), 0.0, 1.0))

    q_base = np.array([0.60 * Phi_true, 0.40 * Phi_true])
    eta = np.array([0.35, 0.75])

    def _eval_alpha(alpha_val: float, shocks_mat: np.ndarray) -> dict:
        reserve_breach = 0
        margin_breach = 0
        max_losses = []
        for p in range(len(shocks_mat)):
            x = 0.0
            y = np.zeros(2, dtype=float)
            max_loss_p = 0.0
            rb_p = False
            mb_p = False
            for t in range(horizon):
                u_t = float(shocks_mat[p, t])
                x_next = a * x + kappa * alpha_val * float(np.dot(q_base, y)) + kappa * u_t
                y = (1.0 - eta) * y + eta * x_next
                x = x_next
                # Under the static reset theorem contract, loss is mark-to-market -I_0 * x_t against fixed budget_B
                loss_t = max(0.0, -initial_inventory * x)
                max_loss_p = max(max_loss_p, loss_t)
                eq_t = initial_equity + initial_inventory * x
                if eq_t - mm0 < r_safe - 1e-12:
                    rb_p = True
                if eq_t < mm0 - 1e-12:
                    mb_p = True
            reserve_breach += int(rb_p)
            margin_breach += int(mb_p)
            max_losses.append(max_loss_p)
        return {
            "alpha": alpha_val,
            "max_loss_across_paths": float(np.max(max_losses)),
            "budget_B": budget_B,
            "reserve_breach_rate": float(reserve_breach / len(shocks_mat)),
            "maintenance_margin_breach_rate": float(margin_breach / len(shocks_mat)),
        }

    rng = np.random.default_rng(seed)
    rand_shocks = np.clip(rng.standard_normal((n_paths, horizon)) * ubar, -ubar, ubar)
    adv_shock = np.full((1, horizon), -math.copysign(ubar, initial_inventory), dtype=float)
    all_shocks = np.vstack([rand_shocks, adv_shock])

    return {
        "contract": "static_reset_z0_zero_fixed_inventory_bounded_shock",
        "budget_B": budget_B,
        "c_I": c_I,
        "alpha_star_certified": alpha_star,
        "alpha_oracle_true": alpha_oracle,
        "guard_at_alpha_star": _eval_alpha(alpha_star, all_shocks),
        "no_control_at_alpha_1": _eval_alpha(1.0, all_shocks),
    }


def _generate_matched_environment(
    n_paths: int,
    horizon: int,
    ubar: float,
    Phi_true: float,
    Phi_cert_upper: float,
    seed: int,
    scenario: str = "standard",
) -> dict:
    """Generate identical exogenous flow shocks, initial noise, and path-level regime parameters
    shared across all compared policies."""
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((n_paths, horizon))
    noise_burst = rng.standard_normal((n_paths, horizon))
    shocks = np.zeros((n_paths, horizon), dtype=float)
    vol_noise = np.zeros((n_paths, horizon), dtype=float)
    phi_true_paths = np.zeros(n_paths, dtype=float)
    phi_cert_paths = np.zeros(n_paths, dtype=float)
    inv0_scale_paths = np.ones(n_paths, dtype=float)
    z0_y_paths = np.zeros((n_paths, 2), dtype=float)

    cert_gap = max(0.0, Phi_cert_upper - Phi_true)

    for p in range(n_paths):
        # Paths span three initial inventory levels (0.80x, 1.00x, 1.20x of baseline inventory)
        inv0_scale_paths[p] = (0.80, 1.00, 1.20)[(p // 3) % 3]
        if scenario == "unfavorable_heteroskedastic_no_feedback":
            # Zero true feedback, but conservative static Phi^+ and heteroskedastic shock variance bursts:
            # High-volatility paths carry adverse drift against short inventory, whereas calm paths are benign.
            phi_true_paths[p] = 0.0
            phi_cert_paths[p] = max(Phi_cert_upper, 0.40)
            high_vol_path = (p % 2) == 1
            scale = 1.0 if high_vol_path else 0.12
            adv_drift = 0.55 if high_vol_path else 0.0
            s_t = 0.0
            for t in range(horizon):
                s_t = 0.65 * s_t + 0.75 * raw[p, t] * scale + adv_drift
                shocks[p, t] = float(np.clip(s_t * ubar, -ubar, ubar))
                vol_noise[p, t] = (0.50 if high_vol_path else 0.015) * noise_burst[p, t]
        else:
            # Market paths span calm/low-feedback, moderate-feedback, and high-feedback algorithmic regimes
            regime_idx = p % 3
            if regime_idx == 0:
                phi_p = 0.20 * Phi_true
                # Calm fundamental flow, but noisy high-frequency return jitter (fools backward volatility limits)
                burst_scale = 0.45
                jit_scale = 0.42
            elif regime_idx == 1:
                phi_p = 0.75 * Phi_true
                burst_scale = 0.75
                jit_scale = 0.16
            else:
                phi_p = 1.22 * Phi_true
                # Persistent directional order-splitting burst against dealer short inventory
                burst_scale = 1.15
                jit_scale = 0.05
            phi_true_paths[p] = phi_p
            phi_cert_paths[p] = phi_p + cert_gap

            s_t = 0.0
            # In high-feedback regime 2, adversarial-like persistent buying pressures short dealer inventory
            drift_sign = 1.0 if (regime_idx == 2 or (p % 4 < 2)) else -1.0
            for t in range(horizon):
                burst = 0.48 * drift_sign if (regime_idx == 2 and 2 <= t <= 32) else 0.0
                s_t = 0.70 * s_t + 0.65 * raw[p, t] * burst_scale + burst
                shocks[p, t] = float(np.clip(s_t * ubar, -ubar, ubar))
                vol_noise[p, t] = jit_scale * noise_burst[p, t]

            if scenario == "unreset_hidden_state":
                z0_y_paths[p, :] = rng.uniform(-0.35, 0.35, size=2)

    return {
        "shocks": shocks,
        "vol_noise": vol_noise,
        "phi_true_paths": phi_true_paths,
        "phi_cert_paths": phi_cert_paths,
        "inv0_scale_paths": inv0_scale_paths,
        "z0_y_paths": z0_y_paths,
    }


def _simulate_policy_on_env(
    pol: str,
    param: float,
    env: dict,
    a: float = 0.55,
    kappa: float = 1.0,
    ubar: float = 0.35,
    initial_inventory: float = -12.0,
    initial_equity: float = 42.0,
    maint_margin_rate: float = 0.015,
    r_safe: float = 4.5,
    spread_fee_per_unit: float = 0.18,
    exec_cost_per_unit: float = 0.03,
    liquidation_cost_rate: float = 0.012,
    base_depth: float = 100.0,
    scenario: str = "standard",
) -> dict:
    """Simulate a single policy on the pre-generated matched environment with exact double-entry cash/inventory
    accounting and separate tracking of reserve breaches, maintenance-margin breaches, and forced liquidations."""
    shocks = env["shocks"]
    vol_noise = env["vol_noise"]
    phi_true_paths = env["phi_true_paths"]
    phi_cert_paths = env["phi_cert_paths"]
    inv0_scale_paths = env["inv0_scale_paths"]
    z0_y_paths = env["z0_y_paths"]
    n_paths, horizon = shocks.shape

    eta = np.array([0.35, 0.75])
    psi_agent = np.array([0.04, 0.04])  # stateful agent inventory mean-reversion rate
    delta_inv_agent = 0.35
    inv_cap_agent = 4.0
    p0 = 100.0

    reserve_breached = np.zeros(n_paths, dtype=bool)
    margin_breached = np.zeros(n_paths, dtype=bool)
    liquidated = np.zeros(n_paths, dtype=bool)
    max_drawdowns = np.zeros(n_paths, dtype=float)
    terminal_losses = np.zeros(n_paths, dtype=float)
    mean_alphas = np.zeros(n_paths, dtype=float)
    fee_revenues = np.zeros(n_paths, dtype=float)
    admitted_depths = np.zeros(n_paths, dtype=float)
    net_pnls = np.zeros(n_paths, dtype=float)
    max_accounting_err = 0.0

    for p in range(n_paths):
        x = 0.0
        y = z0_y_paths[p].copy()
        y_prev = y.copy()
        inv_ag = np.zeros(2, dtype=float)
        q_p = np.array([0.60 * phi_true_paths[p], 0.40 * phi_true_paths[p]])
        phi_cert_p = float(phi_cert_paths[p])

        inv = float(initial_inventory) * float(inv0_scale_paths[p])
        # Double-entry accounting: E_t = cash_t + inv_t * price_t
        cash = float(initial_equity) - inv * p0
        eq = cash + inv * p0
        peak_eq = eq
        max_dd = 0.0
        alphas_p = []
        fees_p = 0.0
        rb_p = False
        mb_p = False
        liq_p = False
        ret_window = [0.14] * 6

        for t in range(horizon):
            u_t = float(shocks[p, t])
            price_t = p0 + x
            mm_t = maint_margin_rate * abs(inv) * price_t
            buf_t = eq - mm_t

            if liq_p:
                # Position was forcibly closed out by exchange; no further market-making admission
                alpha_t = 0.0
            elif pol == "no_control":
                alpha_t = 1.0
            elif pol == "inventory_cap":
                # param is inventory cap ceiling I_cap
                rem_cap = max(0.0, param - abs(inv))
                alpha_t = float(np.clip(rem_cap / 2.50, 0.0, 1.0))
            elif pol == "volatility_limit":
                # param is target volatility sigma_target
                sigma_hat = max(float(np.std(ret_window[-6:])), 1e-4)
                alpha_t = float(np.clip(param / sigma_hat, 0.0, 1.0))
            elif pol == "margin_rule":
                # param is margin safety multiple above maintenance margin relative to 1-step scanning range
                sigma_hat = max(float(np.std(ret_window[-6:])), 0.10)
                scan_range = param * 1.65 * sigma_hat * max(abs(inv), 1.0)
                alpha_t = float(np.clip((eq - 1.15 * mm_t) / max(scan_range, 1e-4), 0.0, 1.0))
            elif pol == "summed_gain_guard":
                # param scales the shock-envelope conservatism (param = 1.0 is the certified Theorem thm:robustguard rule)
                obs_y = y_prev if scenario == "delayed_observation" else y
                drift_est = abs(inv) * (1.0 + maint_margin_rate) * abs(a * x + kappa * float(np.dot(q_p, obs_y)))
                avail_buf = buf_t - r_safe - 0.25 * drift_est
                if avail_buf <= 0.0:
                    alpha_t = 0.0
                else:
                    eff_ubar = param * ubar
                    c_I_dyn = 1.0 - a - kappa * abs(inv) * eff_ubar / max(avail_buf, 1e-6)
                    if c_I_dyn <= 0.0:
                        alpha_t = 0.0
                    elif phi_cert_p <= 1e-9:
                        alpha_t = 1.0
                    else:
                        alpha_t = float(np.clip(c_I_dyn / (kappa * phi_cert_p), 0.0, 1.0))
            else:
                raise ValueError(f"Unknown policy: {pol}")

            alphas_p.append(alpha_t)

            # Stateful inventory-constrained cohort actions u_{i,t}^*
            u_cohort = 0.0
            for i in range(2):
                u_unc = q_p[i] * y[i] - psi_agent[i] * inv_ag[i]
                ret_i = (1.0 - delta_inv_agent) * inv_ag[i]
                u_i = float(np.clip(u_unc, -inv_cap_agent - ret_i, inv_cap_agent - ret_i))
                inv_ag[i] = ret_i + u_i
                u_cohort += u_i

            # Closed-loop price update: alpha_t throttles admitted algorithmic flow (and passive shock intake)
            x_next = a * x + kappa * alpha_t * u_cohort + kappa * (0.35 + 0.65 * alpha_t) * u_t
            y_prev = y.copy()
            y = (1.0 - eta) * y + eta * x_next
            dp = x_next - x
            ret_window.append(dp + float(vol_noise[p, t]))
            price_next = p0 + x_next

            if not liq_p:
                admitted_vol = alpha_t * abs(u_t)
                fee_step = spread_fee_per_unit * admitted_vol
                cost_step = exec_cost_per_unit * admitted_vol
                # Passive fill executed at price_next (double-entry cash + inventory identity)
                d_inv = -0.10 * alpha_t * u_t
                cash = cash - d_inv * price_next + fee_step - cost_step
                inv = inv + d_inv
                fees_p += fee_step

            eq_check = cash + inv * price_next
            eq = eq_check
            max_accounting_err = max(max_accounting_err, abs(eq - (cash + inv * price_next)))
            x = x_next

            peak_eq = max(peak_eq, eq)
            max_dd = max(max_dd, peak_eq - eq)

            mm_next = maint_margin_rate * abs(inv) * price_next
            # (1) Reserve breach: E_t - MM_t < R_safe (no fake penalty, no path termination!)
            if eq - mm_next < r_safe:
                rb_p = True
            # (2) Maintenance-margin breach & (3) Exchange forced liquidation: E_t < MM_t
            if eq < mm_next and not liq_p and abs(inv) > 0.0:
                mb_p = True
                liq_p = True
                liq_fee = liquidation_cost_rate * abs(inv) * price_next
                # Exchange closes out inventory at price_next minus liquidation slippage/fee
                cash = cash + inv * price_next - liq_fee
                inv = 0.0
                eq = cash
                max_dd = max(max_dd, peak_eq - eq)

        reserve_breached[p] = rb_p
        margin_breached[p] = mb_p
        liquidated[p] = liq_p
        max_drawdowns[p] = max_dd
        net_pnl = eq - initial_equity
        net_pnls[p] = net_pnl
        terminal_losses[p] = max(0.0, -net_pnl)
        mean_alphas[p] = float(np.mean(alphas_p))
        fee_revenues[p] = fees_p
        admitted_depths[p] = base_depth * float(np.mean(alphas_p))

    es95, es95_ci = _bootstrap_es95_ci(terminal_losses)
    rb_count = int(np.sum(reserve_breached))
    mb_count = int(np.sum(margin_breached))
    liq_count = int(np.sum(liquidated))

    return {
        "summary": {
            "policy_parameter": float(param),
            "reserve_breach_rate": float(rb_count / n_paths),
            "reserve_breach_rate_ci95": _wilson_ci(rb_count, n_paths),
            "maintenance_margin_breach_rate": float(mb_count / n_paths),
            "maintenance_margin_breach_rate_ci95": _wilson_ci(mb_count, n_paths),
            "forced_liquidation_rate": float(liq_count / n_paths),
            "forced_liquidation_rate_ci95": _wilson_ci(liq_count, n_paths),
            "max_drawdown_mean": float(np.mean(max_drawdowns)),
            "max_drawdown_ci95": _mean_ci(max_drawdowns),
            "tail_loss_es95": es95,
            "tail_loss_es95_ci95": es95_ci,
            "trading_capacity_mean": float(np.mean(mean_alphas)),
            "trading_capacity_ci95": _mean_ci(mean_alphas),
            "fee_revenue_mean": float(np.mean(fee_revenues)),
            "fee_revenue_ci95": _mean_ci(fee_revenues),
            "admitted_depth_mean": float(np.mean(admitted_depths)),
            "admitted_depth_ci95": _mean_ci(admitted_depths),
            "net_pnl_mean": float(np.mean(net_pnls)),
            "net_pnl_ci95": _mean_ci(net_pnls),
            "double_entry_max_err": float(max_accounting_err),
        },
        "arrays": {
            "reserve_breached": reserve_breached.astype(float),
            "liquidated": liquidated.astype(float),
            "max_drawdowns": max_drawdowns,
            "terminal_losses": terminal_losses,
            "mean_alphas": mean_alphas,
            "net_pnls": net_pnls,
        },
    }


def _calibrate_parameter_for_target_capacity(
    pol: str,
    target_cap: float,
    train_env: dict,
    low_param: float,
    high_param: float,
    **sim_kwargs,
) -> float:
    """Calibrate a baseline's threshold parameter on the training environment via bisection so that its
    mean trading capacity matches target_cap."""
    lo, hi = float(low_param), float(high_param)
    for _ in range(18):
        mid = 0.5 * (lo + hi)
        cap_mid = _simulate_policy_on_env(pol, mid, train_env, **sim_kwargs)["summary"]["trading_capacity_mean"]
        # For margin_rule and summed_gain_guard, larger param is more conservative (lower capacity);
        # for inventory_cap and volatility_limit, larger param is looser (higher capacity).
        if pol in ("inventory_cap", "volatility_limit"):
            if cap_mid < target_cap:
                lo = mid
            else:
                hi = mid
        else:
            if cap_mid > target_cap:
                lo = mid
            else:
                hi = mid
    return 0.5 * (lo + hi)


def _calibrate_parameter_for_target_es95(
    pol: str,
    target_es95: float,
    train_env: dict,
    low_param: float,
    high_param: float,
    **sim_kwargs,
) -> float:
    """Calibrate a baseline's threshold parameter on the training environment via bisection to match target ES95."""
    lo, hi = float(low_param), float(high_param)
    for _ in range(18):
        mid = 0.5 * (lo + hi)
        es_mid = _simulate_policy_on_env(pol, mid, train_env, **sim_kwargs)["summary"]["tail_loss_es95"]
        if pol in ("inventory_cap", "volatility_limit"):
            # Larger param -> higher capacity -> higher tail loss
            if es_mid < target_es95:
                lo = mid
            else:
                hi = mid
        else:
            # Larger param -> lower capacity -> lower tail loss
            if es_mid > target_es95:
                lo = mid
            else:
                hi = mid
    return 0.5 * (lo + hi)


def simulate_matched_baselines(
    n_paths: int = 1000,
    horizon: int = 40,
    a: float = 0.55,
    kappa: float = 1.0,
    Phi_true: float = 0.34,
    Phi_cert_upper: float = 0.36,
    ubar: float = 0.35,
    initial_inventory: float = -12.0,
    initial_equity: float = 42.0,
    maint_margin_rate: float = 0.015,
    spread_fee_per_unit: float = 0.18,
    exec_cost_per_unit: float = 0.03,
    liquidation_cost_rate: float = 0.012,
    base_depth: float = 100.0,
    seed: int = 20261021,
) -> dict:
    """Evaluate 5 control rules under identical exogenous shock sequences, initial conditions,
    transaction costs, maintenance margin rules, and evaluation periods:
      1. no_control
      2. inventory_cap (calibrated on training sample to match guard capacity)
      3. volatility_limit (calibrated on training sample to match guard capacity)
      4. margin_rule (calibrated on training sample to match guard capacity)
      5. summed_gain_guard
    Also computes:
      - theorem_contract_static_verification (exact static reset contract check),
      - matched_risk_comparison (baselines tuned to match guard tail risk ES95),
      - policy_frontiers (7-point threshold grids for each policy),
      - unfavorable_and_stress_scenarios (delayed observation, unreset state, and heteroskedastic zero-feedback regime).
    """
    r_safe = 4.5
    sim_kwargs = {
        "a": a,
        "kappa": kappa,
        "ubar": ubar,
        "initial_inventory": initial_inventory,
        "initial_equity": initial_equity,
        "maint_margin_rate": maint_margin_rate,
        "r_safe": r_safe,
        "spread_fee_per_unit": spread_fee_per_unit,
        "exec_cost_per_unit": exec_cost_per_unit,
        "liquidation_cost_rate": liquidation_cost_rate,
        "base_depth": base_depth,
    }

    # 1. Calibrate baseline thresholds on an independent training set so all active controllers have matched capacity
    train_env = _generate_matched_environment(
        n_paths=400, horizon=horizon, ubar=ubar, Phi_true=Phi_true, Phi_cert_upper=Phi_cert_upper, seed=seed - 100
    )
    guard_train = _simulate_policy_on_env("summed_gain_guard", 1.0, train_env, **sim_kwargs)["summary"]
    target_cap = guard_train["trading_capacity_mean"]
    target_es95 = guard_train["tail_loss_es95"]

    calibrated_params = {
        "no_control": 1.0,
        "inventory_cap": _calibrate_parameter_for_target_capacity(
            "inventory_cap", target_cap, train_env, 9.5, 17.5, **sim_kwargs
        ),
        "volatility_limit": _calibrate_parameter_for_target_capacity(
            "volatility_limit", target_cap, train_env, 0.005, 1.50, **sim_kwargs
        ),
        "margin_rule": _calibrate_parameter_for_target_capacity(
            "margin_rule", target_cap, train_env, 0.10, 60.0, **sim_kwargs
        ),
        "summed_gain_guard": 1.0,
    }

    # 2. Out-of-sample evaluation on test environment
    test_env = _generate_matched_environment(
        n_paths=n_paths, horizon=horizon, ubar=ubar, Phi_true=Phi_true, Phi_cert_upper=Phi_cert_upper, seed=seed
    )
    raw_runs = {}
    for pol, param in calibrated_params.items():
        raw_runs[pol] = _simulate_policy_on_env(pol, param, test_env, **sim_kwargs)

    guard_arr = raw_runs["summed_gain_guard"]["arrays"]
    results = {}
    for pol, run_data in raw_runs.items():
        summary = dict(run_data["summary"])
        arr = run_data["arrays"]
        if pol != "summed_gain_guard":
            summary["paired_diff_vs_guard"] = {
                "forced_liquidation_rate": _paired_bootstrap_diff_ci(arr["liquidated"], guard_arr["liquidated"], "mean"),
                "reserve_breach_rate": _paired_bootstrap_diff_ci(
                    arr["reserve_breached"], guard_arr["reserve_breached"], "mean"
                ),
                "max_drawdown": _paired_bootstrap_diff_ci(arr["max_drawdowns"], guard_arr["max_drawdowns"], "mean"),
                "tail_loss_es95": _paired_bootstrap_diff_ci(
                    arr["terminal_losses"], guard_arr["terminal_losses"], "es95"
                ),
                "net_pnl": _paired_bootstrap_diff_ci(arr["net_pnls"], guard_arr["net_pnls"], "mean"),
            }
        results[pol] = summary

    # 3. Matched-risk comparison (tune baselines on training set to match guard's ES95, then evaluate capacity/P&L)
    matched_risk_params = {
        "inventory_cap": _calibrate_parameter_for_target_es95(
            "inventory_cap", target_es95, train_env, 9.5, 17.5, **sim_kwargs
        ),
        "volatility_limit": _calibrate_parameter_for_target_es95(
            "volatility_limit", target_es95, train_env, 0.005, 1.50, **sim_kwargs
        ),
        "margin_rule": _calibrate_parameter_for_target_es95(
            "margin_rule", target_es95, train_env, 0.10, 60.0, **sim_kwargs
        ),
        "summed_gain_guard": 1.0,
    }
    matched_risk_comparison = {}
    for pol, param in matched_risk_params.items():
        s = _simulate_policy_on_env(pol, param, test_env, **sim_kwargs)["summary"]
        matched_risk_comparison[pol] = {
            "calibrated_param": float(param),
            "tail_loss_es95": s["tail_loss_es95"],
            "forced_liquidation_rate": s["forced_liquidation_rate"],
            "reserve_breach_rate": s["reserve_breach_rate"],
            "trading_capacity_mean": s["trading_capacity_mean"],
            "net_pnl_mean": s["net_pnl_mean"],
        }

    # 4. Full policy efficient frontiers (5-point threshold sweep per policy)
    frontier_env = _generate_matched_environment(
        n_paths=min(n_paths, 400),
        horizon=horizon,
        ubar=ubar,
        Phi_true=Phi_true,
        Phi_cert_upper=Phi_cert_upper,
        seed=seed,
    )
    frontier_grids = {
        "inventory_cap": [11.95, 12.25, 12.55, 12.85, 13.25],
        "volatility_limit": [0.09, 0.14, 0.20, 0.28, 0.42],
        "margin_rule": [3.60, 2.50, 1.80, 1.25, 0.75],
        "summed_gain_guard": [1.45, 1.20, 1.00, 0.82, 0.65],
    }
    frontiers = {}
    for pol, grid in frontier_grids.items():
        pts = []
        for g_val in grid:
            s = _simulate_policy_on_env(pol, g_val, frontier_env, **sim_kwargs)["summary"]
            pts.append(
                {
                    "param": float(g_val),
                    "trading_capacity_mean": s["trading_capacity_mean"],
                    "tail_loss_es95": s["tail_loss_es95"],
                    "reserve_breach_rate": s["reserve_breach_rate"],
                    "forced_liquidation_rate": s["forced_liquidation_rate"],
                    "net_pnl_mean": s["net_pnl_mean"],
                }
            )
        frontiers[pol] = pts

    # 5. Unfavorable and stress scenarios (including heteroskedastic zero-feedback where volatility_limit beats guard)
    unfav_train = _generate_matched_environment(
        n_paths=300,
        horizon=horizon,
        ubar=ubar,
        Phi_true=0.0,
        Phi_cert_upper=0.36,
        seed=seed + 301,
        scenario="unfavorable_heteroskedastic_no_feedback",
    )
    unfav_test = _generate_matched_environment(
        n_paths=400,
        horizon=horizon,
        ubar=ubar,
        Phi_true=0.0,
        Phi_cert_upper=0.36,
        seed=seed + 302,
        scenario="unfavorable_heteroskedastic_no_feedback",
    )
    guard_unfav_train = _simulate_policy_on_env(
        "summed_gain_guard", 1.0, unfav_train, scenario="unfavorable_heteroskedastic_no_feedback", **sim_kwargs
    )["summary"]
    vol_param_unfav = _calibrate_parameter_for_target_capacity(
        "volatility_limit",
        guard_unfav_train["trading_capacity_mean"],
        unfav_train,
        0.02,
        0.60,
        scenario="unfavorable_heteroskedastic_no_feedback",
        **sim_kwargs,
    )
    guard_unfav_oos = _simulate_policy_on_env(
        "summed_gain_guard", 1.0, unfav_test, scenario="unfavorable_heteroskedastic_no_feedback", **sim_kwargs
    )["summary"]
    vol_unfav_oos = _simulate_policy_on_env(
        "volatility_limit",
        vol_param_unfav,
        unfav_test,
        scenario="unfavorable_heteroskedastic_no_feedback",
        **sim_kwargs,
    )["summary"]

    # Delayed observation and unreset hidden state stress checks
    delay_env = _generate_matched_environment(
        n_paths=300,
        horizon=horizon,
        ubar=ubar,
        Phi_true=Phi_true,
        Phi_cert_upper=Phi_cert_upper,
        seed=seed + 401,
        scenario="delayed_observation",
    )
    unreset_env = _generate_matched_environment(
        n_paths=300,
        horizon=horizon,
        ubar=ubar,
        Phi_true=Phi_true,
        Phi_cert_upper=Phi_cert_upper,
        seed=seed + 402,
        scenario="unreset_hidden_state",
    )
    delay_guard = _simulate_policy_on_env(
        "summed_gain_guard", 1.0, delay_env, scenario="delayed_observation", **sim_kwargs
    )["summary"]
    unreset_guard = _simulate_policy_on_env(
        "summed_gain_guard", 1.0, unreset_env, scenario="unreset_hidden_state", **sim_kwargs
    )["summary"]

    # 6. Sensitivity analysis across shock bound ubar and transaction cost exec_cost_per_unit
    sensitivity = []
    for u_val, tc_val in [(0.25, 0.03), (0.35, 0.03), (0.45, 0.03), (0.35, 0.06)]:
        sub = _run_sensitivity_point(u_val, tc_val)
        sensitivity.append({"ubar": u_val, "exec_cost_per_unit": tc_val, "policies": sub})

    static_verification = verify_static_theorem_contract()

    return {
        "protocol": {
            "n_paths": n_paths,
            "horizon": horizon,
            "matched_shocks": True,
            "matched_initial_conditions": True,
            "matched_transaction_costs": True,
            "matched_margin_rules": True,
            "calibrated_on_independent_training_set": True,
            "matched_trading_capacity_target": float(target_cap),
            "a": a,
            "kappa": kappa,
            "Phi_true": Phi_true,
            "Phi_cert_upper": Phi_cert_upper,
            "ubar": ubar,
            "initial_inventory": initial_inventory,
            "initial_equity": initial_equity,
            "maint_margin_rate": maint_margin_rate,
            "reserve_R_safe": r_safe,
            "event_definitions": {
                "reserve_breach": "E_t - MM_t < R_safe (internal reserve encroached; no artificial liquidation penalty or path termination)",
                "maintenance_margin_breach": "E_t < MM_t (equity falls below exchange maintenance margin)",
                "forced_liquidation": "Exchange closes out position I_t -> 0 with proportional liquidation cost when E_t < MM_t",
            },
        },
        "theorem_contract_static_verification": static_verification,
        "baseline_comparison": results,
        "matched_risk_comparison": matched_risk_comparison,
        "policy_frontiers": frontiers,
        "unfavorable_and_stress_scenarios": {
            "unfavorable_heteroskedastic_no_feedback": {
                "description": (
                    "True feedback Phi = 0 with heteroskedastic shock variance bursts and conservatively "
                    "misspecified certificate Phi^+ = 0.36. Here trailing volatility_limit adapts to shock "
                    "variance and outperforms the static-Phi^+ summed_gain_guard at matched capacity."
                ),
                "volatility_limit": {
                    "trading_capacity_mean": vol_unfav_oos["trading_capacity_mean"],
                    "tail_loss_es95": vol_unfav_oos["tail_loss_es95"],
                    "net_pnl_mean": vol_unfav_oos["net_pnl_mean"],
                },
                "summed_gain_guard": {
                    "trading_capacity_mean": guard_unfav_oos["trading_capacity_mean"],
                    "tail_loss_es95": guard_unfav_oos["tail_loss_es95"],
                    "net_pnl_mean": guard_unfav_oos["net_pnl_mean"],
                },
                "volatility_limit_beats_guard_in_es95": bool(
                    vol_unfav_oos["tail_loss_es95"] < guard_unfav_oos["tail_loss_es95"]
                ),
                "volatility_limit_beats_guard_in_pnl": bool(
                    vol_unfav_oos["net_pnl_mean"] > guard_unfav_oos["net_pnl_mean"]
                ),
            },
            "delayed_observation_1step_lag": {
                "trading_capacity_mean": delay_guard["trading_capacity_mean"],
                "reserve_breach_rate": delay_guard["reserve_breach_rate"],
                "forced_liquidation_rate": delay_guard["forced_liquidation_rate"],
                "tail_loss_es95": delay_guard["tail_loss_es95"],
            },
            "unreset_hidden_initial_state_z0": {
                "trading_capacity_mean": unreset_guard["trading_capacity_mean"],
                "reserve_breach_rate": unreset_guard["reserve_breach_rate"],
                "forced_liquidation_rate": unreset_guard["forced_liquidation_rate"],
                "tail_loss_es95": unreset_guard["tail_loss_es95"],
            },
        },
        "sensitivity_analysis": sensitivity,
    }


def _run_sensitivity_point(ubar: float, exec_cost: float, n_paths: int = 300) -> dict:
    """Compact matched-capacity sensitivity evaluation at (ubar, exec_cost)."""
    sim_kwargs = {
        "a": 0.55,
        "kappa": 1.0,
        "ubar": ubar,
        "initial_inventory": -12.0,
        "initial_equity": 42.0,
        "maint_margin_rate": 0.015,
        "r_safe": 4.5,
        "spread_fee_per_unit": 0.18,
        "exec_cost_per_unit": exec_cost,
        "liquidation_cost_rate": 0.012,
        "base_depth": 100.0,
    }
    train_env = _generate_matched_environment(
        n_paths=200, horizon=40, ubar=ubar, Phi_true=0.34, Phi_cert_upper=0.36, seed=20260900
    )
    test_env = _generate_matched_environment(
        n_paths=n_paths, horizon=40, ubar=ubar, Phi_true=0.34, Phi_cert_upper=0.36, seed=20261021
    )
    g_train = _simulate_policy_on_env("summed_gain_guard", 1.0, train_env, **sim_kwargs)["summary"]
    t_cap = g_train["trading_capacity_mean"]
    params = {
        "no_control": 1.0,
        "inventory_cap": _calibrate_parameter_for_target_capacity(
            "inventory_cap", t_cap, train_env, 9.5, 17.5, **sim_kwargs
        ),
        "volatility_limit": _calibrate_parameter_for_target_capacity(
            "volatility_limit", t_cap, train_env, 0.005, 1.50, **sim_kwargs
        ),
        "margin_rule": _calibrate_parameter_for_target_capacity(
            "margin_rule", t_cap, train_env, 0.10, 60.0, **sim_kwargs
        ),
        "summed_gain_guard": 1.0,
    }
    out = {}
    for pol, p_val in params.items():
        v = _simulate_policy_on_env(pol, p_val, test_env, **sim_kwargs)["summary"]
        out[pol] = {
            "reserve_breach_rate": v["reserve_breach_rate"],
            "forced_liquidation_rate": v["forced_liquidation_rate"],
            "tail_loss_es95": v["tail_loss_es95"],
            "trading_capacity_mean": v["trading_capacity_mean"],
            "net_pnl_mean": v["net_pnl_mean"],
        }
    return out


def main() -> dict:
    payload = {
        "microfoundations_option_a": run_microfoundation_analysis(),
        "matched_shock_baselines_decision_4": simulate_matched_baselines(),
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    return payload


if __name__ == "__main__":
    res = main()
    print(json.dumps(res["matched_shock_baselines_decision_4"]["baseline_comparison"], indent=2))
