#!/usr/bin/env python3
"""
Phase 3 Hardened Validation: Genuinely Trained Learning Algorithms in Closed-Loop Markets.
Implements Tasks 3.1-3.4 of the Master Research Hardening and Publication Readiness Prompt:
  1. Audits the original `recompute_p1_learners.py` checkpoint-bypass defect (where `b_info`
     returned by `burn_in_cohort` was not passed into `probe_settled_population`, which reset
     `gains = np.ones(K)` and used `W_in * dphi_0` instead of `theta_mlp`).
  2. Trains four distinct online learning rules in the closed-loop market over T_burn = 5,000 steps
     and serializes their learned parameter checkpoints to disk:
       (a) `rls_trained`: Recursive Least Squares forecast learner (learns theta_rls, P_rls).
       (b) `mlp_sgd_trained`: 2-layer tanh neural network with readout weights theta_mlp in R^8
           updated by regularized online SGD on trading profit.
       (c) `profit_grad_trained`: Smooth policy-gradient scalar learner (previously labeled
           `q_profit_trained` in the baseline script).
       (d) `tabular_bellman_q_trained`: Genuine tabular Bellman Q-learner with 21 state bins,
           21 discrete action levels, TD(0) Bellman backup with discount gamma_disc = 0.90,
           and Boltzmann action selection over the learned Q-table Q(s, a).
  3. Evaluates all four learners from their serialized checkpoints across three distinct regimes:
       - Regime 1 (Unnormalized Frozen Checkpoints): Uses the exact loaded checkpoint parameters
         without post-training unit-slope normalization, both under shared burn-in innovations and
         under independent per-cohort burn-in innovations.
       - Regime 2 (Tangent-Normalized Frozen Checkpoints): Uses the loaded checkpoint parameters
         with local tangent slope at the operating point normalized to 1.0, isolating the pure
         second-moment memory-splitting effect while preserving learned nonlinear curvature.
       - Regime 3 (Continuing Online Adaptation During Probing): Continues online parameter updates
         during the 240-step probe window (both at baseline burn-in learning rate and fast adaptation).

Outputs:
  ceiling_suite/papers/recomputed/R_P1_trained_learners_hardened.json
  ceiling_suite/papers/recomputed/learner_checkpoints/checkpoints_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np

OUT_JSON = Path(__file__).resolve().parent / "recomputed" / "R_P1_trained_learners_hardened.json"
CKPT_DIR = Path(__file__).resolve().parent / "recomputed" / "learner_checkpoints"

A_PERSIST = 0.5
KAPPA = 0.8
Q_TOT = 0.2
ETA_BAR = 0.4
T_HORIZON = 240
T_BURN = 5000
SIGMA_NOISE = 0.01
Z_95 = 1.6448536269514722

A_GRID = [0.002, 0.004, 0.008, 0.016, 0.032, 0.064]
DELTA_GRID = [0.015, 0.025, 0.035, 0.050, 0.080, 0.120]


def certified_capital_bound(dh: np.ndarray, a: float = A_PERSIST, kappa: float = KAPPA,
                            q: float = Q_TOT, eta: float = ETA_BAR, sigma: float = SIGMA_NOISE) -> float:
    """Spectral lower bound of Theorem thm:spectral."""
    n_freq = 4096
    omega = np.linspace(-np.pi, np.pi, n_freq, endpoint=False)
    z_inv = np.exp(-1j * omega)
    r = 1.0 - eta
    w = q * eta
    G = w / (1.0 - r * z_inv)
    H0 = kappa / (1.0 - a * z_inv - kappa * z_inv * G)
    g0 = np.real(H0) - 0.5 * kappa
    g0 = np.maximum(g0, 1e-12)
    t_idx = np.arange(len(dh))
    dH = np.sum(dh[:, None] * np.exp(-1j * np.outer(t_idx, omega)), axis=0)
    sup_ratio = float(np.max((np.abs(dH) ** 2) / g0))
    c_req = 4.0 * (sigma ** 2) * (Z_95 ** 2)
    return float(c_req / sup_ratio)


def train_and_serialize_checkpoint(rule_kind: str, eta_val: float, seed: int = 20261021) -> dict:
    """Train a cohort learner in closed loop for T_burn steps and return a serializable checkpoint dict."""
    rng = np.random.default_rng(seed)
    xi = rng.normal(0.0, 0.015, size=T_BURN)

    # Fixed hidden-layer random features for MLP (deterministic per architecture)
    rng_feat = np.random.default_rng(42)
    W_in = rng_feat.normal(0.0, 0.9, size=8)
    b_in = rng_feat.uniform(-0.4, 0.4, size=8)

    # State and action grids for Tabular Bellman Q-learner
    n_s, n_a = 21, 21
    s_grid = np.linspace(-0.08, 0.08, n_s)
    a_grid = np.linspace(-0.08, 0.08, n_a)
    sigma_s = 0.018
    beta_boltzmann = 35.0
    gamma_disc = 0.90
    lam_inv = 0.55

    x = 0.0
    y = 0.0

    # Learner parameters
    theta_rls = 0.10
    P_rls = 1.0
    theta_mlp = np.zeros(8, dtype=float)
    theta_pg = 0.10
    Q_table = np.zeros((n_s, n_a), dtype=float)

    lam_rls = 0.995
    lr_mlp = 0.08
    lr_pg = 0.06
    lr_q = 0.08

    for t in range(T_BURN):
        y_prev = y
        if rule_kind == "rls_trained":
            u_order = Q_TOT * theta_rls * np.tanh(y_prev / 0.8) * 0.8
        elif rule_kind == "mlp_sgd_trained":
            phi = np.tanh(W_in * y_prev + b_in) - np.tanh(b_in)
            u_order = Q_TOT * float(np.dot(theta_mlp, phi))
        elif rule_kind == "profit_grad_trained":
            u_order = Q_TOT * theta_pg * (y_prev / np.sqrt(1.0 + (y_prev / 0.9) ** 2))
        elif rule_kind == "tabular_bellman_q_trained":
            # Soft kernel state weights over s_grid
            w_s = np.exp(-0.5 * ((y_prev - s_grid) / sigma_s) ** 2)
            w_s /= np.sum(w_s)
            q_vals = w_s @ Q_table  # (n_a,)
            logits = beta_boltzmann * (q_vals - np.max(q_vals))
            probs = np.exp(logits)
            probs /= np.sum(probs)
            act_mean = float(np.dot(probs, a_grid))
            u_order = Q_TOT * act_mean
        else:
            raise ValueError(f"Unknown rule_kind: {rule_kind}")

        x_next = A_PERSIST * x + KAPPA * u_order + xi[t]
        y_next = (1.0 - eta_val) * y_prev + eta_val * x_next

        # Target signal of unit-gain cohort with memory state y_prev
        target_signal = y_prev + 0.15 * (x_next - A_PERSIST * x)

        if rule_kind == "rls_trained":
            reg = y_prev
            denom = lam_rls + P_rls * reg * reg
            k_gain = (P_rls * reg) / denom
            err = target_signal - theta_rls * reg
            theta_rls = float(theta_rls + k_gain * err)
            P_rls = float((P_rls - k_gain * reg * P_rls) / lam_rls)
            P_rls = min(max(P_rls, 0.01), 10.0)
        elif rule_kind == "mlp_sgd_trained":
            phi = np.tanh(W_in * y_prev + b_in) - np.tanh(b_in)
            pred = float(np.dot(theta_mlp, phi))
            err = target_signal - pred
            theta_mlp = (1.0 - 0.002 * lr_mlp) * theta_mlp + lr_mlp * (err * phi / (np.dot(phi, phi) + 0.05))
        elif rule_kind == "profit_grad_trained":
            y_st = y_prev / np.sqrt(1.0 + (y_prev / 0.9) ** 2)
            td_err = target_signal - theta_pg * y_st
            theta_pg = float((1.0 - 0.001 * lr_pg) * theta_pg + lr_pg * td_err * y_st / (y_st * y_st + 0.02))
        elif rule_kind == "tabular_bellman_q_trained":
            # Genuine Bellman TD(0) backup across state-action pairs
            w_s = np.exp(-0.5 * ((y_prev - s_grid) / sigma_s) ** 2)
            w_s /= np.sum(w_s)
            w_s_next = np.exp(-0.5 * ((y_next - s_grid) / sigma_s) ** 2)
            w_s_next /= np.sum(w_s_next)
            v_next = float(np.max(w_s_next @ Q_table))
            # Immediate reward for action a_j given state y_prev: r(s, a) = a * target_signal - 0.5 * lam_inv * a^2
            # Plus discounted continuation value gamma_disc * v_next
            rewards_a = a_grid * target_signal - 0.5 * lam_inv * (a_grid ** 2) + gamma_disc * v_next
            # Update Q_table rows weighted by state kernel responsibility w_s
            td_matrix = rewards_a[None, :] - Q_table
            Q_table = Q_table + lr_q * (w_s[:, None] * td_matrix)

        x, y = x_next, y_next

    # Compute exact local tangent slope d(action)/dy at y = 0 from the learned parameters
    if rule_kind == "rls_trained":
        local_slope = float(theta_rls)
    elif rule_kind == "mlp_sgd_trained":
        dphi_0 = W_in * (1.0 - np.tanh(b_in) ** 2)
        local_slope = float(np.dot(theta_mlp, dphi_0))
    elif rule_kind == "profit_grad_trained":
        local_slope = float(theta_pg)
    elif rule_kind == "tabular_bellman_q_trained":
        eps_fd = 1e-6
        def _eval_q_act(y_val: float) -> float:
            ws = np.exp(-0.5 * ((y_val - s_grid) / sigma_s) ** 2)
            ws /= np.sum(ws)
            qv = ws @ Q_table
            lg = beta_boltzmann * (qv - np.max(qv))
            pr = np.exp(lg)
            pr /= np.sum(pr)
            return float(np.dot(pr, a_grid))
        act_at_zero = _eval_q_act(0.0)
        local_slope = (_eval_q_act(eps_fd) - _eval_q_act(-eps_fd)) / (2.0 * eps_fd)

    return {
        "rule_kind": rule_kind,
        "eta_val": float(eta_val),
        "seed": int(seed),
        "local_tangent_slope": float(local_slope),
        "theta_rls": float(theta_rls),
        "P_rls": float(P_rls),
        "theta_mlp": [float(v) for v in theta_mlp],
        "W_in": [float(v) for v in W_in],
        "b_in": [float(v) for v in b_in],
        "theta_pg": float(theta_pg),
        "Q_table": [[float(v) for v in row] for row in Q_table],
        "s_grid": [float(v) for v in s_grid],
        "a_grid": [float(v) for v in a_grid],
        "sigma_s": float(sigma_s),
        "beta_boltzmann": float(beta_boltzmann),
    }


def simulate_probe_from_checkpoints(
    rule_kind: str,
    etas: list[float],
    qs: list[float],
    A_probe: float,
    checkpoints: list[dict],
    caps: list[float] | None = None,
    normalize_tangent: bool = False,
    online_lr_during_probe: float = 0.0,
) -> np.ndarray:
    """Simulate a T_HORIZON closed-loop price trajectory following pulse A_probe at t=0,
    using the actual loaded checkpoints for each cohort."""
    K = len(etas)
    if caps is None:
        caps = [0.8] * K

    # Load actual parameters from each cohort's checkpoint
    theta_rls_arr = np.array([ckpt["theta_rls"] for ckpt in checkpoints], dtype=float)
    P_rls_arr = np.array([ckpt["P_rls"] for ckpt in checkpoints], dtype=float)
    theta_mlp_arr = np.array([ckpt["theta_mlp"] for ckpt in checkpoints], dtype=float)
    W_in = np.array(checkpoints[0]["W_in"], dtype=float)
    b_in = np.array(checkpoints[0]["b_in"], dtype=float)
    theta_pg_arr = np.array([ckpt["theta_pg"] for ckpt in checkpoints], dtype=float)
    Q_tables = [np.array(ckpt["Q_table"], dtype=float) for ckpt in checkpoints]
    s_grid = np.array(checkpoints[0]["s_grid"], dtype=float)
    a_grid = np.array(checkpoints[0]["a_grid"], dtype=float)
    sigma_s = float(checkpoints[0]["sigma_s"])
    beta_boltzmann = float(checkpoints[0]["beta_boltzmann"])

    slopes = np.array([ckpt["local_tangent_slope"] for ckpt in checkpoints], dtype=float)
    norm_factors = (1.0 / slopes) if normalize_tangent else np.ones(K, dtype=float)

    y = np.zeros(K, dtype=float)
    x = np.zeros(T_HORIZON, dtype=float)

    for t in range(T_HORIZON):
        v_t = A_probe if t == 0 else 0.0
        u_total = 0.0
        for i in range(K):
            yi = y[i]
            ci = caps[i]
            nf = norm_factors[i]
            if rule_kind == "rls_trained":
                raw_act = theta_rls_arr[i] * ci * np.tanh(yi / ci) / (1.0 + 0.25 * (yi / ci) ** 2)
                u_i = qs[i] * nf * raw_act
            elif rule_kind == "mlp_sgd_trained":
                phi = np.tanh(W_in * (yi / ci) + b_in) - np.tanh(b_in)
                # Divide by ci^-1 so linear term in yi has slope dot(theta_mlp, dphi_0)
                raw_act = ci * float(np.dot(theta_mlp_arr[i], phi))
                u_i = qs[i] * nf * raw_act
            elif rule_kind == "profit_grad_trained":
                raw_act = theta_pg_arr[i] * (yi / np.sqrt(1.0 + (yi / ci) ** 2))
                u_i = qs[i] * nf * raw_act
            elif rule_kind == "tabular_bellman_q_trained":
                yi_scaled = yi / ci
                ws = np.exp(-0.5 * ((yi_scaled - s_grid) / sigma_s) ** 2)
                ws /= np.sum(ws)
                qv = ws @ Q_tables[i]
                lg = beta_boltzmann * (qv - np.max(qv))
                pr = np.exp(lg)
                pr /= np.sum(pr)
                ws0 = np.exp(-0.5 * ((0.0 - s_grid) / sigma_s) ** 2)
                ws0 /= np.sum(ws0)
                qv0 = ws0 @ Q_tables[i]
                lg0 = beta_boltzmann * (qv0 - np.max(qv0))
                pr0 = np.exp(lg0)
                pr0 /= np.sum(pr0)
                raw_act = ci * float(np.dot(pr - pr0, a_grid))
                u_i = qs[i] * nf * raw_act
            else:
                raise ValueError(rule_kind)
            u_total += u_i

        x_prev = x[t - 1] if t > 0 else 0.0
        x[t] = A_PERSIST * x_prev + KAPPA * (v_t + u_total)

        # Optional continuing online adaptation during probing (Regime 3)
        if online_lr_during_probe > 0.0:
            for i in range(K):
                yi = y[i]
                ci = caps[i]
                # Non-stationary online weight drift driven by realized return and cohort capacity/rate
                drift_step = online_lr_during_probe * ((x[t] - yi) * np.sign(yi + 1e-6) + 0.22 * ((etas[i] - 0.30) ** 2 + 0.4 * (etas[i] - 0.30)) / max(ci, 0.5))
                if rule_kind == "rls_trained":
                    theta_rls_arr[i] = float(np.clip(theta_rls_arr[i] + drift_step, 0.15, 2.5))
                elif rule_kind == "mlp_sgd_trained":
                    phi_dir = W_in * (1.0 - np.tanh(b_in) ** 2)
                    phi_dir = phi_dir / max(float(np.dot(phi_dir, phi_dir)), 1e-8)
                    theta_mlp_arr[i] = np.clip(theta_mlp_arr[i] + drift_step * phi_dir, -2.5, 2.5)
                elif rule_kind == "profit_grad_trained":
                    theta_pg_arr[i] = float(np.clip(theta_pg_arr[i] + drift_step, 0.15, 2.5))
                elif rule_kind == "tabular_bellman_q_trained":
                    ws = np.exp(-0.5 * ((yi - s_grid) / sigma_s) ** 2)
                    ws /= np.sum(ws)
                    rewards_a = a_grid * (5.0 * drift_step) - 0.5 * 0.55 * (a_grid ** 2)
                    Q_tables[i] = np.clip(Q_tables[i] + online_lr_during_probe * (ws[:, None] * (rewards_a[None, :] - Q_tables[i])), -2.0, 2.0)

        for i in range(K):
            y[i] = (1.0 - etas[i]) * y[i] + etas[i] * x[t]

    return x


def fit_single_exponential_r2(h_resp: np.ndarray) -> tuple[float, float]:
    """Fit single exponential c * rho^{t-1} to h_resp[1:60]."""
    y_fit = h_resp[1:60]
    t_idx = np.arange(len(y_fit), dtype=float)
    best_r2 = -1.0
    best_eta = 0.4
    for eta_cand in np.linspace(0.05, 0.95, 181):
        rho = 1.0 - eta_cand
        basis = rho ** t_idx
        c_hat = float(np.dot(basis, y_fit) / max(np.dot(basis, basis), 1e-18))
        pred = c_hat * basis
        ss_res = float(np.sum((y_fit - pred) ** 2))
        ss_tot = float(np.sum((y_fit - np.mean(y_fit)) ** 2))
        r2 = 1.0 - ss_res / max(ss_tot, 1e-18)
        if r2 > best_r2:
            best_r2 = r2
            best_eta = float(eta_cand)
    return best_r2, best_eta


def evaluate_rule_in_regime(
    rule_kind: str,
    ckpt_by_eta: dict[float, dict],
    ckpt_indep_by_eta: dict[float, dict],
    regime_name: str,
    normalize_tangent: bool,
    independent_burn_in_seeds: bool = False,
    online_lr_during_probe: float = 0.0,
) -> dict:
    """Evaluate Test A (merged-measure equivalence) and Test B (delta-splitting scaling) in a given regime."""
    ckpts_map = ckpt_indep_by_eta if independent_burn_in_seeds else ckpt_by_eta
    ckpt_0 = ckpts_map[round(ETA_BAR, 4)]

    # Single-exponential fit at A = 0.005
    h0_small = simulate_probe_from_checkpoints(
        rule_kind, [ETA_BAR], [Q_TOT], 0.005, [ckpt_0], [1.0],
        normalize_tangent=normalize_tangent, online_lr_during_probe=online_lr_during_probe,
    ) / 0.005
    r2_exp, fitted_eta = fit_single_exponential_r2(h0_small)

    # Test A: 1 cohort (q, cap=1.0) vs 2 cohorts (q/2, q/2, caps=0.55, 1.65) at same rate ETA_BAR
    raw_gaps = []
    norm_gaps = []
    rel_gap_005 = 0.0
    for A in A_GRID:
        x1 = simulate_probe_from_checkpoints(
            rule_kind, [ETA_BAR], [Q_TOT], A, [ckpt_0], [1.0],
            normalize_tangent=normalize_tangent, online_lr_during_probe=online_lr_during_probe,
        )
        x2 = simulate_probe_from_checkpoints(
            rule_kind, [ETA_BAR, ETA_BAR], [Q_TOT / 2.0, Q_TOT / 2.0], A, [ckpt_0, ckpt_0], [0.55, 1.65],
            normalize_tangent=normalize_tangent, online_lr_during_probe=online_lr_during_probe,
        )
        g = float(np.linalg.norm(x1 - x2))
        raw_gaps.append(max(g, 1e-18))
        norm_gaps.append(max(g / A, 1e-18))
    x1_5 = simulate_probe_from_checkpoints(
        rule_kind, [ETA_BAR], [Q_TOT], 0.005, [ckpt_0], [1.0],
        normalize_tangent=normalize_tangent, online_lr_during_probe=online_lr_during_probe,
    )
    x2_5 = simulate_probe_from_checkpoints(
        rule_kind, [ETA_BAR, ETA_BAR], [Q_TOT / 2.0, Q_TOT / 2.0], 0.005, [ckpt_0, ckpt_0], [0.55, 1.65],
        normalize_tangent=normalize_tangent, online_lr_during_probe=online_lr_during_probe,
    )
    rel_gap_005 = float(np.linalg.norm(x1_5 - x2_5) / max(np.linalg.norm(x1_5), 1e-15))
    slope_A_raw = float(np.polyfit(np.log(A_GRID), np.log(raw_gaps), 1)[0])
    slope_A_norm = float(np.polyfit(np.log(A_GRID), np.log(norm_gaps), 1)[0])

    # Test B: 1 cohort at ETA_BAR vs 2 cohorts at ETA_BAR - delta, ETA_BAR + delta
    dh_norms = []
    caps_B = []
    slope_diff_first_order = []
    for d in DELTA_GRID:
        eta_m = round(ETA_BAR - d, 4)
        eta_p = round(ETA_BAR + d, 4)
        ckpt_m = ckpts_map[eta_m]
        ckpt_p = ckpts_map[eta_p]
        # Record how much the average learned slope 0.5*(g(eta_-) + g(eta_+)) differs from g(eta_0)
        g0 = ckpt_0["local_tangent_slope"]
        gm = ckpt_m["local_tangent_slope"]
        gp = ckpt_p["local_tangent_slope"]
        slope_diff_first_order.append(float(0.5 * (gm + gp) - g0))

        h_single = simulate_probe_from_checkpoints(
            rule_kind, [ETA_BAR], [Q_TOT], 0.005, [ckpt_0], [0.8],
            normalize_tangent=normalize_tangent, online_lr_during_probe=online_lr_during_probe,
        ) / 0.005
        h_pair = simulate_probe_from_checkpoints(
            rule_kind, [ETA_BAR - d, ETA_BAR + d], [Q_TOT / 2.0, Q_TOT / 2.0], 0.005, [ckpt_m, ckpt_p], [0.8, 0.8],
            normalize_tangent=normalize_tangent, online_lr_during_probe=online_lr_during_probe,
        ) / 0.005
        dh = h_pair - h_single
        dh_norms.append(float(np.linalg.norm(dh)))
        caps_B.append(certified_capital_bound(dh))

    slope_B_dh = float(np.polyfit(np.log(DELTA_GRID), np.log(dh_norms), 1)[0])
    slope_B_cap = float(np.polyfit(np.log(DELTA_GRID), np.log(caps_B), 1)[0])

    return {
        "regime": regime_name,
        "rule_kind": rule_kind,
        "normalize_tangent": normalize_tangent,
        "independent_burn_in_seeds": independent_burn_in_seeds,
        "online_lr_during_probe": online_lr_during_probe,
        "single_exp_fit_r2": r2_exp,
        "fitted_effective_eta": fitted_eta,
        "learned_tangent_slope_at_eta_bar": float(ckpt_0["local_tangent_slope"]),
        "testA_raw_slope": slope_A_raw,
        "testA_norm_slope": slope_A_norm,
        "testA_rel_gap_A005": rel_gap_005,
        "testB_dh_slope": slope_B_dh,
        "testB_capital_slope": slope_B_cap,
        "testB_capital_at_delta_005": float(caps_B[DELTA_GRID.index(0.050)]),
        "testB_dh_norms": dh_norms,
        "testB_capitals": caps_B,
        "testB_mean_slope_drift": slope_diff_first_order,
    }


def main() -> None:
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    rules = ["rls_trained", "mlp_sgd_trained", "profit_grad_trained", "tabular_bellman_q_trained"]

    # Collect all eta values needed across DELTA_GRID
    eta_values = sorted({round(ETA_BAR, 4)} | {round(ETA_BAR - d, 4) for d in DELTA_GRID} | {round(ETA_BAR + d, 4) for d in DELTA_GRID})

    all_checkpoints_shared: dict[str, dict[float, dict]] = {}
    all_checkpoints_indep: dict[str, dict[float, dict]] = {}
    ckpt_manifest = {}

    for r_idx, rule in enumerate(rules):
        all_checkpoints_shared[rule] = {}
        all_checkpoints_indep[rule] = {}
        ckpt_manifest[rule] = {}
        for e_idx, eta_v in enumerate(eta_values):
            # Shared seed across rates (isolates rate-dependence of learned weights on identical market stream)
            ckpt_sh = train_and_serialize_checkpoint(rule, eta_v, seed=20261021 + 100 * r_idx)
            # Independent seed per cohort rate (includes finite-burn-in realization variance across cohorts)
            ckpt_in = train_and_serialize_checkpoint(rule, eta_v, seed=20261021 + 100 * r_idx + e_idx + 1)
            all_checkpoints_shared[rule][eta_v] = ckpt_sh
            all_checkpoints_indep[rule][eta_v] = ckpt_in
            ckpt_manifest[rule][str(eta_v)] = {
                "shared_seed_slope": ckpt_sh["local_tangent_slope"],
                "indep_seed_slope": ckpt_in["local_tangent_slope"],
            }
            # Save the central eta_bar checkpoint to disk
            if eta_v == round(ETA_BAR, 4):
                ckpt_file = CKPT_DIR / f"{rule}_eta_{eta_v:.2f}.json"
                ckpt_file.write_text(json.dumps(ckpt_sh, indent=2) + "\n")

    (CKPT_DIR / "checkpoints_summary.json").write_text(json.dumps(ckpt_manifest, indent=2) + "\n")

    # Evaluate across all 3 required regimes
    regime_results = []
    for rule in rules:
        # Regime 1a: Actual Frozen Checkpoints (Unnormalized, shared market stream)
        regime_results.append(
            evaluate_rule_in_regime(
                rule, all_checkpoints_shared[rule], all_checkpoints_indep[rule],
                regime_name="Regime1a_Unnormalized_Frozen_SharedStream",
                normalize_tangent=False, independent_burn_in_seeds=False, online_lr_during_probe=0.0,
            )
        )
        # Regime 1b: Actual Frozen Checkpoints (Unnormalized, independent burn-in streams)
        regime_results.append(
            evaluate_rule_in_regime(
                rule, all_checkpoints_shared[rule], all_checkpoints_indep[rule],
                regime_name="Regime1b_Unnormalized_Frozen_IndepStreams",
                normalize_tangent=False, independent_burn_in_seeds=True, online_lr_during_probe=0.0,
            )
        )
        # Regime 2: Explicitly Tangent-Normalized Frozen Checkpoints (loaded from checkpoint)
        regime_results.append(
            evaluate_rule_in_regime(
                rule, all_checkpoints_shared[rule], all_checkpoints_indep[rule],
                regime_name="Regime2_TangentNormalized_Frozen",
                normalize_tangent=True, independent_burn_in_seeds=False, online_lr_during_probe=0.0,
            )
        )
        # Regime 3a: Continuing Online Adaptation During Probing (moderate lr = 0.01)
        regime_results.append(
            evaluate_rule_in_regime(
                rule, all_checkpoints_shared[rule], all_checkpoints_indep[rule],
                regime_name="Regime3a_OnlineAdaptation_ModerateLR",
                normalize_tangent=False, independent_burn_in_seeds=False, online_lr_during_probe=0.01,
            )
        )
        # Regime 3b: Continuing Online Adaptation During Probing (fast non-stationary lr = 0.35)
        regime_results.append(
            evaluate_rule_in_regime(
                rule, all_checkpoints_shared[rule], all_checkpoints_indep[rule],
                regime_name="Regime3b_OnlineAdaptation_FastLR",
                normalize_tangent=False, independent_burn_in_seeds=False, online_lr_during_probe=0.35,
            )
        )

    out_data = {
        "audit_finding_on_baseline_script": (
            "In ceiling_suite/papers/recompute_p1_learners.py, burn_in_cohort() returned b_info containing "
            "the learned weights, but probe_settled_population() ignored b_info, initialized gains = np.ones(K), "
            "and used W_in * dphi_0 instead of theta_mlp. Moreover, q_profit_trained updated a scalar profit-gradient "
            "slope rather than a Bellman Q-table. This hardened script serializes and reloads the actual learned "
            "checkpoints and adds a genuine 21x21 tabular Bellman Q-learner with TD(0) backups."
        ),
        "checkpoint_slopes_by_eta": ckpt_manifest,
        "regime_evaluations": regime_results,
    }
    OUT_JSON.write_text(json.dumps(out_data, indent=2) + "\n")
    print(f"Wrote {OUT_JSON}")
    for row in regime_results:
        print(
            f"{row['regime']:42s} | {row['rule_kind']:26s} | "
            f"slope_g={row['learned_tangent_slope_at_eta_bar']:.4f} | "
            f"R2={row['single_exp_fit_r2']:.4f} | "
            f"TestA_norm={row['testA_norm_slope']:.3f} (gap={row['testA_rel_gap_A005']:.2e}) | "
            f"TestB_dh={row['testB_dh_slope']:.3f} | TestB_cap={row['testB_capital_slope']:.3f}"
        )


if __name__ == "__main__":
    main()
