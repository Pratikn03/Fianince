"""Economically specified adaptive trading-agent microfoundation and matched-shock 4-baseline control comparison.

Implements Decision 2 (Option A microfoundations) and Decision 4 (matched-shock baseline comparison):

1. Adaptive Trading-Agent Microfoundation (Decision 2, Option A):
   - Observation: noisy price-trend signal r_t = v_t + nu_t, where v_t = v_{t-1} + zeta_t is a latent drift/signal
     and x_t = p_t - p*_t is the pricing error.
   - Learning dynamics: Bayesian steady-state Kalman filter (or L2-regularized online gradient descent) updating the
     belief state y_{i,t} = (1 - eta_i) y_{i,t-1} + eta_i x_t, where eta_i in (0, 1) is the Riccati gain
     eta_i = (-sigma_zeta^2 + sqrt(sigma_zeta^4 + 4 sigma_zeta^2 sigma_nu^2)) / (2 sigma_nu^2).
     Explicitly distinguished from a full economic equilibrium: the filtering recursion is an individual agent's belief
     update, whereas market equilibrium requires joint dealer-trader optimization (Proposition prop:equil).
   - Action, objective, costs, and inventory constraints: Agent i chooses order flow u_{i,t} subject to inventory cap
     |I_{i,t}| <= I_max,i (with I_{i,t} = (1 - delta_inv) I_{i,t-1} + u_{i,t}) to maximize expected single-period
     quadratic-cost-adjusted objective:
         max_{u_{i,t}}  E_t[ beta_i y_{i,t} u_{i,t} ] - (lambda_tc,i / 2) u_{i,t}^2 - (gamma_inv,i / 2) I_{i,t}^2
     Interior optimal decision rule (at neutral prior inventory):
         u_{i,t}^* = q_i(lambda_tc,i, gamma_inv,i) * y_{i,t},   where   q_i = beta_i / (lambda_tc,i + gamma_inv,i).
   - Mapping to market-response coefficients and regime boundaries:
     * Aggregate feedback: Phi = sum_{i=1}^K q_i = sum_{i=1}^K beta_i / (lambda_tc,i + gamma_inv,i).
     * Cumulative price response: S = kappa / (1 - a - kappa * Phi).
     * Regime 1 (No peak overshoot in pure cohort economy): When depth depletion eps = 0 and q_i >= 0, S > kappa/(1-a)
       rises with Phi, but peak impulse response remains h_0 = kappa (no peak overshoot).
     * Regime 2 (Transient peak amplification): With order-book depth depletion eps > 0 and price- sensitivity phi_d > 0,
       peak overshoot h_1 > h_0 appears iff C_3 = phi_d * eps + kappa * sum_i q_i * eta_i - (1 - a) * kappa > 0.
     * Regime 3 (Amplification disappears under high costs/tight inventory): As execution cost lambda_tc,i or inventory
       penalty gamma_inv,i increases, q_i -> 0, so C_3 < 0 and Phi -> 0.
     * Regime 4 (Instability): When costs/penalties are low enough that a + kappa * Phi >= 1, the closed-loop spectral
       radius reaches 1 and S diverges.
   - Benchmarks: Compares (a) Fixed-policy benchmark (constant eta_i, q_i) vs. (b) Adaptive/equilibrium benchmark
     where agents re-optimize Kalman gain eta_i^*(alpha) and order intensity q_i^*(alpha) under admission throttling
     and endogenous dealer depth D^*(N).

2. Matched-Shock Control Comparison Against 4 Approved Baselines (Decision 4):
   - Policies compared on identical exogenous shock paths, initial conditions, transaction costs, margin rules, and horizons:
     (1) no_control: full admission alpha_t = 1.0
     (2) inventory_cap: admits flow up to a hard dealer inventory ceiling |I_t| <= I_cap
     (3) volatility_limit: scales admission inversely with trailing realized volatility sigma_hat_t
     (4) margin_rule: scales admission by remaining maintenance-margin buffer relative to exchange scanning range
     (5) summed_gain_guard: certified uncertainty-aware summed-response guard alpha^* = min(1, c_I / (kappa * Phi^+))
   - Reports all 7 required metrics with 95% confidence intervals and sensitivity sweeps:
     forced liquidations, max drawdown, tail loss (ES95), trading capacity, fee/spread revenue, admitted depth,
     and net economic performance (net P&L).
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
    """Steady-state Kalman gain eta in (0, 1) for random-walk signal v_{t+1} = v_t + zeta_{t+1}
    observed in noise r_t = v_t + nu_t."""
    sz2 = float(sigma_zeta) ** 2
    sn2 = float(sigma_nu) ** 2
    return (-sz2 + math.sqrt(sz2 * sz2 + 4.0 * sz2 * sn2)) / (2.0 * sn2)


def optimal_agent_response_weight(beta_signal: float, lambda_tc: float, gamma_inv: float) -> float:
    """Optimal linear-quadratic flow sensitivity q_i = beta_i / (lambda_tc,i + gamma_inv,i)
    from maximizing E_t[beta_i y_{i,t} u_{i,t}] - (lambda_tc,i / 2) u_{i,t}^2 - (gamma_inv,i / 2) I_{i,t}^2."""
    if lambda_tc + gamma_inv <= 0:
        raise ValueError("Total quadratic friction lambda_tc + gamma_inv must be positive.")
    return float(beta_signal) / float(lambda_tc + gamma_inv)


def three_state_book_impulse(a: float, kappa: float, q: np.ndarray, eta: np.ndarray, phi_d: float, eps_d: float, r_refill: float, horizon: int = 40) -> np.ndarray:
    """Impulse response h_0..h_{horizon-1} of the coupled price-cohort-depth system:
        x_{t+1} = a x_t + kappa * sum_i q_i y_{i,t} + phi_d * d_t
        y_{i,t+1} = (1 - eta_i) y_{i,t} + eta_i x_{t+1}
        d_{t+1} = (1 - r_refill) d_t + eps_d * (x_{t+1} - a x_t) / kappa
    """
    q = np.asarray(q, dtype=float)
    eta = np.asarray(eta, dtype=float)
    x = float(kappa)
    y = eta * x
    d = float(eps_d)  # initial unit flow shock depletes book by eps_d
    h = [x]
    for _ in range(horizon - 1):
        u_feedback = float(np.dot(q, y))
        x_next = a * x + kappa * u_feedback + phi_d * d
        y = (1.0 - eta) * y + eta * x_next
        d = (1.0 - r_refill) * d + eps_d * u_feedback
        x = x_next
        h.append(x)
    return np.array(h, dtype=float)


def run_microfoundation_analysis() -> dict:
    """Derive the mapping from agent primitives (sigma_zeta, sigma_nu, beta, lambda_tc, gamma_inv)
    to market-response coefficients (a, kappa, q_i, eta_i, Phi, S, C_3) across all four regimes
    and compare the fixed-policy benchmark with the adaptive/equilibrium re-optimizing benchmark."""
    a, kappa = 0.40, 1.00
    # Two adaptive trader cohorts with distinct signal-to-noise priors and inventory constraints
    betas = np.array([0.36, 0.24])
    sigma_zetas = np.array([0.15, 0.05])
    sigma_nus = np.array([0.20, 0.20])
    etas_base = np.array([kalman_steady_state_gain(sz, sn) for sz, sn in zip(sigma_zetas, sigma_nus)])

    regimes = []
    # Sweep friction scale (execution cost + inventory penalty) and depth depletion eps_d
    specs = [
        ("high_cost_amplification_disappears", 4.0, 1.0, 0.00, 0.25, 0.20),
        ("moderate_cost_positive_cohort_no_overshoot", 1.2, 0.3, 0.00, 0.25, 0.20),
        ("moderate_cost_with_depletion_overshoot_appears", 1.2, 0.3, 0.90, 0.60, 0.15),
        ("low_cost_feedback_instability", 0.6, 0.2, 0.00, 0.25, 0.20),
    ]
    for label, lam_tc, gam_inv, eps_d, phi_d, r_ref in specs:
        qs = np.array([optimal_agent_response_weight(b, lam_tc, gam_inv) for b in betas])
        phi_val = float(np.sum(qs))
        k0_val = float(np.sum(qs * etas_base))
        c3_val = phi_d * eps_d + kappa * k0_val - (1.0 - a) * kappa
        stable = (a + kappa * phi_val < 1.0) and (eps_d == 0.0 or c3_val < 0.25)
        h = three_state_book_impulse(a, kappa, qs, etas_base, phi_d, eps_d, r_ref, horizon=40)
        s_val = float(kappa / (1.0 - a - kappa * phi_val)) if (a + kappa * phi_val < 1.0 and eps_d == 0.0) else float(np.sum(h))
        regimes.append(
            {
                "regime": label,
                "lambda_tc": lam_tc,
                "gamma_inv": gam_inv,
                "eps_depletion": eps_d,
                "derived_q": [float(x) for x in qs],
                "derived_eta": [float(x) for x in etas_base],
                "Phi": phi_val,
                "C3_one_step_margin": c3_val,
                "h0_impact": float(h[0]),
                "h1_next_step": float(h[1]),
                "peak_response": float(np.max(h)),
                "peak_overshoot_occurs": bool(np.max(h) > h[0] * (1.0 + 1e-9)),
                "summed_response_S": s_val,
                "schur_stable": bool(a + kappa * phi_val < 1.0),
            }
        )

    # Fixed-policy vs. Adaptive/Equilibrium Re-optimizing Benchmark across admission alpha in {0.25, 0.50, 0.75, 1.00}
    lam_tc, gam_inv = 1.2, 0.3
    qs_fixed = np.array([optimal_agent_response_weight(b, lam_tc, gam_inv) for b in betas])
    benchmarks = []
    for alpha in [0.25, 0.50, 0.75, 1.00]:
        # Under fixed policy: agents keep eta_base and q_fixed; effective flow weight is alpha * q_fixed
        h_fixed = three_state_book_impulse(a, kappa, alpha * qs_fixed, etas_base, 0.0, 0.0, 0.20, horizon=30)
        s_fixed_H = float(np.sum(h_fixed))
        s_fixed_inf = float(kappa / (1.0 - a - kappa * alpha * float(np.sum(qs_fixed))))

        # Under adaptive re-optimization (Prop prop:lucas): throttling scales signal innovation sigma_zeta(alpha) = alpha * sigma_zeta
        # and raises effective execution shadow cost lambda_tc / alpha, lowering both eta^*(alpha) and q^*(alpha)
        etas_adapt = np.array([kalman_steady_state_gain(alpha * sz, sn) for sz, sn in zip(sigma_zetas, sigma_nus)])
        qs_adapt = np.array([optimal_agent_response_weight(b, lam_tc / max(alpha, 0.1), gam_inv) for b in betas])
        h_adapt = three_state_book_impulse(a, kappa, alpha * qs_adapt, etas_adapt, 0.0, 0.0, 0.20, horizon=30)
        s_adapt_H = float(np.sum(h_adapt))
        s_adapt_inf = float(kappa / (1.0 - a - kappa * alpha * float(np.sum(qs_adapt))))

        benchmarks.append(
            {
                "alpha": alpha,
                "fixed_policy_eta": [float(x) for x in etas_base],
                "adaptive_policy_eta": [float(x) for x in etas_adapt],
                "fixed_policy_S_H30": s_fixed_H,
                "adaptive_policy_S_H30": s_adapt_H,
                "fixed_policy_S_inf": s_fixed_inf,
                "adaptive_policy_S_inf": s_adapt_inf,
                "reoptimization_reinforces_guard": bool(s_adapt_H <= s_fixed_H + 1e-12 and s_adapt_inf <= s_fixed_inf + 1e-12),
            }
        )

    return {
        "note": "Filtering/learning recursion specifies individual agent belief updates; market equilibrium requires joint dealer-trader optimization.",
        "regimes": regimes,
        "fixed_vs_adaptive_benchmarks": benchmarks,
    }


# ==============================================================================================================
# Part 2: Matched-Shock Comparison Against 4 Approved Baselines (Decision 4)
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


def _bootstrap_es95_ci(losses: np.ndarray, n_boot: int = 500, seed: int = 42) -> tuple[float, list[float]]:
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


def simulate_matched_baselines(
    n_paths: int = 1000,
    horizon: int = 40,
    a: float = 0.55,
    kappa: float = 1.0,
    Phi_true: float = 0.32,
    Phi_cert_upper: float = 0.35,
    ubar: float = 0.35,
    initial_inventory: float = -12.0,
    initial_equity: float = 42.0,
    maint_margin_rate: float = 0.015,
    spread_fee_per_unit: float = 0.14,
    exec_cost_per_unit: float = 0.03,
    liquidation_penalty: float = 4.0,
    base_depth: float = 100.0,
    seed: int = 20261021,
) -> dict:
    """Evaluate 5 control rules under identical exogenous shock sequences, initial conditions,
    transaction costs, maintenance margin rules, and evaluation periods:
      1. no_control
      2. inventory_cap
      3. volatility_limit
      4. margin_rule
      5. summed_gain_guard
    """
    rng = np.random.default_rng(seed)
    # Two-cohort positive economy with total feedback Phi_true
    q_base = np.array([0.60 * Phi_true, 0.40 * Phi_true])
    eta = np.array([0.35, 0.75])
    p0 = 100.0
    mm_initial = maint_margin_rate * abs(initial_inventory) * p0
    # Loss budget B is remaining buffer above maintenance margin and safety reserve R_safe = 4.5
    r_safe = 4.5
    budget_B = initial_equity - mm_initial - r_safe

    # Pre-generate identical exogenous flow shocks u_{p, t} in [-ubar, ubar] for all policies
    # Include both persistent bursts (adversarial-like sign runs) and turbulent Gaussian-clipped shocks
    raw = rng.standard_normal((n_paths, horizon))
    shocks = np.zeros((n_paths, horizon), dtype=float)
    for p in range(n_paths):
        # AR(1) flow clusters + occasional stress bursts, strictly bounded by ubar
        s_t = 0.0
        for t in range(horizon):
            s_t = 0.65 * s_t + 0.75 * raw[p, t]
            shocks[p, t] = float(np.clip(s_t * ubar, -ubar, ubar))

    policies = ["no_control", "inventory_cap", "volatility_limit", "margin_rule", "summed_gain_guard"]
    results = {}

    # Precompute certified guard admission alpha^* from Theorem thm:robustguard:
    # c_I = 1 - a - kappa * |I_0| * ubar / B
    c_I = 1.0 - a - kappa * abs(initial_inventory) * ubar / budget_B
    alpha_guard_const = float(np.clip(c_I / (kappa * Phi_cert_upper), 0.0, 1.0)) if c_I >= 0 else 0.0

    for pol in policies:
        liquidated = np.zeros(n_paths, dtype=bool)
        max_drawdowns = np.zeros(n_paths, dtype=float)
        terminal_losses = np.zeros(n_paths, dtype=float)
        mean_alphas = np.zeros(n_paths, dtype=float)
        fee_revenues = np.zeros(n_paths, dtype=float)
        admitted_depths = np.zeros(n_paths, dtype=float)
        net_pnls = np.zeros(n_paths, dtype=float)

        for p in range(n_paths):
            x = 0.0
            y = np.zeros(2, dtype=float)
            inv = float(initial_inventory)
            eq = float(initial_equity)
            peak_eq = eq
            max_dd = 0.0
            alphas_p = []
            fees_p = 0.0
            costs_p = 0.0
            liq_p = False
            ret_window = [0.12] * 6  # calm prior volatility window

            for t in range(horizon):
                u_t = shocks[p, t]
                mm_t = maint_margin_rate * abs(inv) * (p0 + x)
                buf_t = eq - mm_t

                if pol == "no_control":
                    alpha_t = 1.0
                elif pol == "inventory_cap":
                    # Hard inventory cap |I_t| <= 12.18: throttles admission as passive fills push |I_t| toward the cap
                    rem_cap = max(0.0, 12.18 - abs(inv))
                    alpha_t = float(np.clip(rem_cap / (0.10 * abs(u_t) + 1e-9), 0.0, 1.0))
                elif pol == "volatility_limit":
                    # Trailing 6-bar realized volatility rule: alpha_t = min(1, sigma_target / sigma_hat_t)
                    sigma_hat = max(float(np.std(ret_window[-6:])), 1e-4)
                    alpha_t = float(np.clip(0.18 / sigma_hat, 0.0, 1.0))
                elif pol == "margin_rule":
                    # Margin-based rule: scales by excess buffer above 1.25x maintenance margin relative to 1-step scanning range
                    scan_range = 1.65 * max(float(np.std(ret_window[-6:])), 0.12) * abs(inv)
                    alpha_t = float(np.clip((eq - 1.25 * mm_t) / max(scan_range, 1e-4), 0.0, 1.0))
                elif pol == "summed_gain_guard":
                    # Certified summed-gain guard using Theorem thm:robustguard with dynamic inventory check
                    c_I_dyn = 1.0 - a - kappa * abs(inv) * ubar / max(buf_t - r_safe, 1e-6)
                    alpha_t = float(np.clip(c_I_dyn / (kappa * Phi_cert_upper), 0.0, 1.0)) if (buf_t > r_safe and c_I_dyn >= 0) else 0.0
                else:
                    raise ValueError(pol)

                alphas_p.append(alpha_t)
                # Closed-loop price update under admission alpha_t
                x_next = a * x + kappa * alpha_t * float(np.dot(q_base, y)) + kappa * u_t
                y = (1.0 - eta) * y + eta * x_next
                dp = x_next - x
                ret_window.append(dp)

                # Dealer mark-to-market, spread fee revenue on admitted flow, and execution/hedging cost
                admitted_vol = alpha_t * abs(u_t)
                fee_step = spread_fee_per_unit * admitted_vol
                cost_step = exec_cost_per_unit * admitted_vol
                # Passive fill adds a small fraction of admitted flow against dealer inventory
                inv_next = inv - 0.10 * alpha_t * u_t
                mtm_step = inv * dp
                eq = eq + mtm_step + fee_step - cost_step
                fees_p += fee_step
                costs_p += cost_step
                x = x_next
                inv = inv_next

                peak_eq = max(peak_eq, eq)
                max_dd = max(max_dd, peak_eq - eq)

                # Check maintenance margin breach (forced liquidation)
                mm_next = maint_margin_rate * abs(inv) * (p0 + x)
                if eq - mm_next < r_safe and not liq_p:
                    liq_p = True
                    eq -= liquidation_penalty
                    max_dd = max(max_dd, peak_eq - eq)
                    break

            liquidated[p] = liq_p
            max_drawdowns[p] = max_dd
            net_pnl = eq - initial_equity
            net_pnls[p] = net_pnl
            terminal_losses[p] = max(0.0, -net_pnl)
            mean_alphas[p] = float(np.mean(alphas_p))
            fee_revenues[p] = fees_p
            admitted_depths[p] = base_depth * float(np.mean(alphas_p))

        es95, es95_ci = _bootstrap_es95_ci(terminal_losses)
        liq_count = int(np.sum(liquidated))
        results[pol] = {
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
        }

    # Sensitivity analysis across shock bound ubar and transaction cost exec_cost_per_unit
    sensitivity = []
    for u_val, tc_val in [(0.25, 0.03), (0.35, 0.03), (0.45, 0.03), (0.35, 0.06)]:
        sub = _run_sensitivity_point(u_val, tc_val)
        sensitivity.append({"ubar": u_val, "exec_cost_per_unit": tc_val, "policies": sub})

    return {
        "protocol": {
            "n_paths": n_paths,
            "horizon": horizon,
            "matched_shocks": True,
            "matched_initial_conditions": True,
            "matched_transaction_costs": True,
            "matched_margin_rules": True,
            "a": a,
            "kappa": kappa,
            "Phi_true": Phi_true,
            "Phi_cert_upper": Phi_cert_upper,
            "ubar": ubar,
            "initial_inventory": initial_inventory,
            "initial_equity": initial_equity,
            "maint_margin_rate": maint_margin_rate,
            "reserve_R_safe": r_safe,
        },
        "baseline_comparison": results,
        "sensitivity_analysis": sensitivity,
    }


def _run_sensitivity_point(ubar: float, exec_cost: float, n_paths: int = 300) -> dict:
    """Compact sensitivity evaluation at (ubar, exec_cost)."""
    res = simulate_matched_baselines_core(n_paths=n_paths, ubar=ubar, exec_cost_per_unit=exec_cost)
    return {
        k: {
            "forced_liquidation_rate": v["forced_liquidation_rate"],
            "tail_loss_es95": v["tail_loss_es95"],
            "trading_capacity_mean": v["trading_capacity_mean"],
            "net_pnl_mean": v["net_pnl_mean"],
        }
        for k, v in res.items()
    }


def simulate_matched_baselines_core(
    n_paths: int = 300,
    horizon: int = 40,
    a: float = 0.55,
    kappa: float = 1.0,
    Phi_true: float = 0.32,
    Phi_cert_upper: float = 0.35,
    ubar: float = 0.35,
    initial_inventory: float = -12.0,
    initial_equity: float = 42.0,
    maint_margin_rate: float = 0.015,
    spread_fee_per_unit: float = 0.14,
    exec_cost_per_unit: float = 0.03,
    liquidation_penalty: float = 4.0,
    base_depth: float = 100.0,
    seed: int = 20261021,
) -> dict:
    rng = np.random.default_rng(seed)
    q_base = np.array([0.60 * Phi_true, 0.40 * Phi_true])
    eta = np.array([0.35, 0.75])
    p0 = 100.0
    r_safe = 4.5
    raw = rng.standard_normal((n_paths, horizon))
    shocks = np.zeros((n_paths, horizon), dtype=float)
    for p in range(n_paths):
        s_t = 0.0
        for t in range(horizon):
            s_t = 0.65 * s_t + 0.75 * raw[p, t]
            shocks[p, t] = float(np.clip(s_t * ubar, -ubar, ubar))

    out = {}
    for pol in ["no_control", "inventory_cap", "volatility_limit", "margin_rule", "summed_gain_guard"]:
        liq = 0
        losses = np.zeros(n_paths, dtype=float)
        alphas = np.zeros(n_paths, dtype=float)
        pnls = np.zeros(n_paths, dtype=float)
        for p in range(n_paths):
            x = 0.0
            y = np.zeros(2, dtype=float)
            inv = float(initial_inventory)
            eq = float(initial_equity)
            alphas_p = []
            ret_window = [0.12] * 6
            for t in range(horizon):
                u_t = shocks[p, t]
                mm_t = maint_margin_rate * abs(inv) * (p0 + x)
                buf_t = eq - mm_t
                if pol == "no_control":
                    alpha_t = 1.0
                elif pol == "inventory_cap":
                    rem_cap = max(0.0, 12.18 - abs(inv))
                    alpha_t = float(np.clip(rem_cap / (0.10 * abs(u_t) + 1e-9), 0.0, 1.0))
                elif pol == "volatility_limit":
                    sigma_hat = max(float(np.std(ret_window[-6:])), 1e-4)
                    alpha_t = float(np.clip(0.18 / sigma_hat, 0.0, 1.0))
                elif pol == "margin_rule":
                    scan_range = 1.65 * max(float(np.std(ret_window[-6:])), 0.12) * abs(inv)
                    alpha_t = float(np.clip((eq - 1.25 * mm_t) / max(scan_range, 1e-4), 0.0, 1.0))
                else:
                    c_I_dyn = 1.0 - a - kappa * abs(inv) * ubar / max(buf_t - r_safe, 1e-6)
                    alpha_t = float(np.clip(c_I_dyn / (kappa * Phi_cert_upper), 0.0, 1.0)) if (buf_t > r_safe and c_I_dyn >= 0) else 0.0
                alphas_p.append(alpha_t)
                x_next = a * x + kappa * alpha_t * float(np.dot(q_base, y)) + kappa * u_t
                y = (1.0 - eta) * y + eta * x_next
                dp = x_next - x
                ret_window.append(dp)
                admitted_vol = alpha_t * abs(u_t)
                eq += inv * dp + (spread_fee_per_unit - exec_cost_per_unit) * admitted_vol
                inv -= 0.10 * alpha_t * u_t
                x = x_next
                if eq - maint_margin_rate * abs(inv) * (p0 + x) < r_safe:
                    liq += 1
                    eq -= liquidation_penalty
                    break
            pnl = eq - initial_equity
            pnls[p] = pnl
            losses[p] = max(0.0, -pnl)
            alphas[p] = float(np.mean(alphas_p))
        q95 = float(np.quantile(losses, 0.95))
        tail = losses[losses >= q95]
        out[pol] = {
            "forced_liquidation_rate": float(liq / n_paths),
            "tail_loss_es95": float(np.mean(tail)) if len(tail) > 0 else q95,
            "trading_capacity_mean": float(np.mean(alphas)),
            "net_pnl_mean": float(np.mean(pnls)),
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
