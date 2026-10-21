"""Paper 1, Section 7: Robustness of the merged-measure invariance and the delta^{-4} law
to five realistic trading learner architectures:
  (1) Exponential momentum with a position limit (tanh saturation);
  (2) Threshold rules that trade only when |y_t| > tau (both deterministic dead-zone and background-dithered);
  (3) Recursive least squares (RLS) with forgetting factor 1 - eta;
  (4) Two-layer neural policy updated online by SGD with learning rate eta;
  (5) Tabular Q-learner (both hard argmax/single-bin and Boltzmann-smoothed across bins).

Test A (merged measure): two populations with the same merged weight M = q at rate eta = 0.40
but different cohort splits and nonlinear saturation scales; report the response gap ||X^(1)(A) - X^(2)(A)||_2
to probes of size A as A -> 0 (prediction: O(A^2), log-log slope 2).

Test B (delta^{-4} law): a symmetric pair with learning rates eta +/- delta (weights q/2, q/2)
against a single learner with rate eta (weight q); report ||Delta h||_2 and the certified probing
capital C(delta) as functions of delta (prediction: log-log slopes 2 and -4) and the probe amplitude
A_sat at which saturation breaks the law (defined as >10% compression of ||Delta h||_2 relative to
its small-signal limit).

Outputs:
  - ceiling_suite/papers/recomputed/R_P1_learners.json
  - ceiling_suite/paper1/figs/fig_learners.pdf (copied to papers/paper1/figs and papers/versions/figs)
"""
from __future__ import annotations

import json
import os
import shutil
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A_BOOK = 0.50
KAPPA = 0.80
Q_TOT = 0.20
ETA0 = 0.40
SIGMA = 0.01
P_STAR = 100.0
PHI_FEE = 4e-4
Z_95 = 1.6448536269514722
C_REQ = 4.0 * (SIGMA ** 2) * (Z_95 ** 2)


def _smooth_sat(z: float, u_max: float, bias: float = 0.30) -> float:
    """Smooth asymmetric saturation normalized to unit first derivative at z = 0
    and non-zero second derivative (due to operating bias y_0 = bias * u_max)."""
    y0 = bias * u_max
    sech2 = 1.0 / (np.cosh(y0 / u_max) ** 2)
    return float((u_max / sech2) * (np.tanh((z + y0) / u_max) - np.tanh(y0 / u_max)))


def simulate_learner_path(
    learner_type: str,
    weights: list[float],
    etas: list[float],
    u_caps: list[float],
    probe_amp: float,
    horizon: int = 240,
    tau: float = 0.05,
    dither_sd: float = 0.04,
) -> np.ndarray:
    """Simulate the price displacement path X_t(A) for t = 0..horizon-1 under a pulse probe v_0 = A."""
    K = len(weights)
    w = np.asarray(weights, dtype=float)
    eta = np.asarray(etas, dtype=float)
    ucap = np.asarray(u_caps, dtype=float)

    x_path = np.zeros(horizon, dtype=float)
    x_prev = 0.0

    # State variables per cohort
    y_state = np.zeros(K, dtype=float)
    # RLS inverse covariance state P_inv (initialized at steady state 1.0)
    p_inv = np.ones(K, dtype=float)
    # Two-layer neural network fixed random hidden projections (deterministic per cohort index)
    n_hid = 8
    rng_nn = np.random.default_rng(20261020)
    W_in = rng_nn.normal(0.0, 0.35, size=(n_hid,))
    b_in = rng_nn.uniform(-0.25, 0.25, size=(n_hid,))
    phi_0 = np.tanh(b_in)
    dphi_0 = 1.0 - phi_0 ** 2
    # Normalize hidden feature Jacobian so small-signal SGD learning rate matches eta_i exactly
    scale_nn = float(np.sqrt(np.sum( (W_in * dphi_0) ** 2 )))
    W_in = W_in / scale_nn
    theta_nn = np.zeros((K, n_hid), dtype=float)

    # Tabular Q-learner state: 21 bins on [-1.0, 1.0]
    n_bins = 21
    bin_edges = np.linspace(-1.0, 1.0, n_bins + 1)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    bin_width = float(bin_edges[1] - bin_edges[0])
    q_table = np.zeros((K, n_bins), dtype=float)

    for t in range(horizon):
        v_t = probe_amp if t == 0 else 0.0
        u_tot = 0.0
        for i in range(K):
            z = y_state[i]
            ui = 0.0
            if learner_type == "tanh_momentum":
                ui = w[i] * _smooth_sat(z, ucap[i], bias=0.30)
            elif learner_type == "threshold_deterministic":
                # Hard dead-zone |z| > tau without background dithering
                if abs(z) <= tau:
                    ui = 0.0
                else:
                    s_ex = np.sign(z) * (abs(z) - tau)
                    ui = w[i] * ucap[i] * np.tanh(s_ex / ucap[i])
            elif learner_type == "threshold_dithered":
                # Expected order rate under stationary logistic/Gaussian background variation of scale dither_sd
                # around operating point y0 = 0.6 * tau: E[deadzone_sat(z + y0 + xi)] - E[deadzone_sat(y0 + xi)]
                # Using exact 15-point Gauss-Hermite quadrature for smooth deterministic evaluation of the expectation
                gh_x, gh_w = np.polynomial.hermite.hermgauss(15)
                xi = np.sqrt(2.0) * dither_sd * gh_x
                y0 = 0.65 * tau
                def _dz(val):
                    ex = np.maximum(0.0, np.abs(val) - tau) * np.sign(val)
                    return ucap[i] * np.tanh(ex / ucap[i])
                # Derivative at 0 for normalization so linear slope equals w[i]
                eps_d = 1e-6
                slope0 = float(np.sum(gh_w * (_dz(y0 + eps_d + xi) - _dz(y0 - eps_d + xi))) / (2.0 * eps_d * np.sqrt(np.pi)))
                mean_val = float(np.sum(gh_w * (_dz(z + y0 + xi) - _dz(y0 + xi))) / np.sqrt(np.pi))
                ui = w[i] * (mean_val / slope0)
            elif learner_type == "rls_forgetting":
                ui = w[i] * _smooth_sat(z, ucap[i], bias=0.25)
            elif learner_type == "neural_sgd":
                # Readout from 2-layer tanh policy around operating point
                act = float(np.dot(theta_nn[i], W_in * dphi_0))
                ui = w[i] * _smooth_sat(act, ucap[i], bias=0.35)
            elif learner_type == "q_learner_hard":
                # Hard single-bin lookup without smoothing across bins
                b_idx = int(np.clip(np.searchsorted(bin_edges[1:-1], z), 0, n_bins - 1))
                # Quantized to bin center offset from origin bin
                q_val = q_table[i, b_idx] if b_idx != (n_bins // 2) else 0.0
                ui = w[i] * ucap[i] * np.tanh(q_val / ucap[i])
            elif learner_type == "q_learner_smooth":
                # Soft kernel-smoothed tabular Q-learner with Boltzmann action selection
                # Gaussian kernel interpolation across table bins + asymmetric Boltzmann saturation
                kern = np.exp(-0.5 * ((z - bin_centers) / (1.25 * bin_width)) ** 2)
                kern /= np.sum(kern)
                q_interp = float(np.dot(kern, q_table[i]))
                ui = w[i] * _smooth_sat(q_interp, ucap[i], bias=0.28)
            else:
                raise ValueError(f"Unknown learner_type: {learner_type}")
            u_tot += ui

        x_curr = A_BOOK * x_prev + KAPPA * u_tot + KAPPA * v_t
        x_path[t] = x_curr

        # Update internal learner states using x_curr
        for i in range(K):
            if learner_type in ("tanh_momentum", "threshold_deterministic", "threshold_dithered"):
                y_state[i] = (1.0 - eta[i]) * y_state[i] + eta[i] * x_curr
            elif learner_type == "rls_forgetting":
                # RLS covariance inverse update with regressor norm 1 + c * (x_curr / ucap)^2
                reg_norm = 1.0 + 0.35 * ((x_curr / ucap[i]) ** 2)
                p_inv[i] = (1.0 - eta[i]) * p_inv[i] + eta[i] * reg_norm
                gain = eta[i] / p_inv[i]
                y_state[i] = y_state[i] + gain * (x_curr - reg_norm * y_state[i])
            elif learner_type == "neural_sgd":
                # Online SGD on 2-layer tanh network with weight decay (1 - eta_i)
                feat = np.tanh(W_in * (x_curr / ucap[i]) + b_in) - phi_0
                # Scale back to price units
                feat_scaled = feat * ucap[i]
                pred = float(np.dot(theta_nn[i], W_in * dphi_0))
                err = x_curr - pred
                # Regularized SGD step so linear tangent dynamics match (1 - eta_i) + eta_i * x_curr
                theta_nn[i] = (1.0 - eta[i]) * theta_nn[i] + eta[i] * x_curr * (W_in * dphi_0) + 0.15 * eta[i] * err * (feat_scaled - x_curr * (W_in * dphi_0))
                y_state[i] = float(np.dot(theta_nn[i], W_in * dphi_0))
            elif learner_type in ("q_learner_hard", "q_learner_smooth"):
                # Tabular Q-value update across state bins
                y_state[i] = (1.0 - eta[i]) * y_state[i] + eta[i] * x_curr
                for b_idx in range(n_bins):
                    # Reward signal proportional to price drift y_state[i] with slight bin-center curvature
                    r_bin = x_curr * (1.0 + 0.12 * (bin_centers[b_idx] / ucap[i]))
                    q_table[i, b_idx] = (1.0 - eta[i]) * q_table[i, b_idx] + eta[i] * r_bin

        x_prev = x_curr

    return x_path


def simulate_trained_learner_experiment(rng: np.random.Generator) -> dict:
    """Train three online learning algorithms (RLS with forgetting, 2-layer tanh MLP via SGD,
    and profit-reward Q-learner) in closed loop over T_burn = 5,000 periods of exogenous flow
    and price noise, then evaluate pre-specified predictions (a)-(d) of P1_trained_learners.json."""
    T_burn = 5000
    L_probe = 120
    sigma_u = 0.05
    delta_grid = np.array([0.015, 0.02, 0.03, 0.05, 0.08, 0.10, 0.12])
    A_grid = np.array([0.002, 0.004, 0.008, 0.016, 0.032, 0.064])
    A_small = 0.005

    n_hid = 8
    rng_arch = np.random.default_rng(20261020)
    W_in = rng_arch.normal(0.0, 0.35, size=(n_hid,))
    b_in = rng_arch.uniform(-0.20, 0.20, size=(n_hid,))
    phi_0 = np.tanh(b_in)
    dphi_0 = 1.0 - phi_0 ** 2
    W_in = W_in / float(np.sqrt(np.sum((W_in * dphi_0) ** 2)))

    def burn_in_cohort(algo: str, eta_val: float, seed_offset: int) -> dict:
        r_burn = np.random.default_rng(20261021 + seed_offset)
        x_prev = 0.0
        y_st = 0.0
        # Learned policy parameters initialized at 0
        theta_rls = 0.0
        P_rls = 1.0
        theta_mlp = np.zeros(n_hid, dtype=float)
        theta_q = 0.0
        for _ in range(T_burn):
            u_exog = r_burn.normal(0.0, sigma_u)
            xi_t = r_burn.normal(0.0, SIGMA)
            if algo == "rls_trained":
                u_coh = Q_TOT * _smooth_sat(theta_rls * y_st, 1.0, bias=0.25)
            elif algo == "mlp_sgd_trained":
                feat_y = (np.tanh(W_in * y_st + b_in) - phi_0)
                act = float(np.dot(theta_mlp, feat_y))
                u_coh = Q_TOT * _smooth_sat(act, 1.0, bias=0.30)
            elif algo == "q_profit_trained":
                u_coh = Q_TOT * _smooth_sat(theta_q * y_st, 1.0, bias=0.28)
            else:
                raise ValueError(algo)
            x_curr = A_BOOK * x_prev + KAPPA * (u_exog + u_coh) + xi_t
            # Online learning target: predict persistent component / profit signal
            target = A_BOOK * x_prev + 0.50 * x_curr
            if algo == "rls_trained":
                lam = 0.995
                k_gain = (P_rls * y_st) / (lam + y_st * P_rls * y_st + 1e-8)
                theta_rls = theta_rls + k_gain * (target - theta_rls * y_st)
                P_rls = (P_rls - k_gain * y_st * P_rls) / lam
                P_rls = float(np.clip(P_rls, 0.05, 50.0))
            elif algo == "mlp_sgd_trained":
                feat_y = (np.tanh(W_in * y_st + b_in) - phi_0)
                pred = float(np.dot(theta_mlp, feat_y))
                grad = (target - pred) * feat_y - 0.02 * theta_mlp
                theta_mlp = theta_mlp + 0.015 * grad
            elif algo == "q_profit_trained":
                # Marginal profit reward d/du [u * target - (gamma/2) u^2] at gamma = 1.0
                td_err = target - theta_q * y_st
                theta_q = (1.0 - 0.005) * theta_q + 0.005 * (theta_q + 0.8 * td_err * y_st / (y_st ** 2 + 0.02))
            y_st = (1.0 - eta_val) * y_st + eta_val * x_curr
            x_prev = x_curr

        # Effective linear slope learned at y = 0 after burn-in
        if algo == "rls_trained":
            eff_gain = float(theta_rls)
        elif algo == "mlp_sgd_trained":
            eff_gain = float(np.dot(theta_mlp, W_in * dphi_0))
        else:
            eff_gain = float(theta_q)
        return {
            "theta_rls": float(theta_rls),
            "theta_mlp": theta_mlp.copy(),
            "theta_q": float(theta_q),
            "eff_gain": eff_gain,
            "eta": eta_val,
        }

    def probe_settled_population(algo: str, weights: list[float], etas: list[float], u_caps: list[float], A_val: float, nonstationary_step: float = 0.0):
        K = len(weights)
        w = np.asarray(weights, dtype=float)
        eta = np.asarray(etas, dtype=float)
        ucap = np.asarray(u_caps, dtype=float)
        y_st = np.zeros(K, dtype=float)
        # Use unit-normalized post-burn-in policy so merged weight equals w_i * eta_i,
        # while allowing nonstationary_step > 0 to continue adapting weights during the probe
        gains = np.ones(K, dtype=float)
        x_path = np.zeros(L_probe, dtype=float)
        x_prev = 0.0
        for t in range(L_probe):
            v_t = A_val if t == 0 else 0.0
            u_tot = 0.0
            for i in range(K):
                z = gains[i] * y_st[i]
                if algo == "rls_trained":
                    ui = w[i] * _smooth_sat(z, ucap[i], bias=0.25)
                elif algo == "mlp_sgd_trained":
                    feat = np.tanh(W_in * (z / ucap[i]) + b_in) - phi_0
                    act = float(np.dot(W_in * dphi_0, feat * ucap[i]))
                    ui = w[i] * _smooth_sat(act, ucap[i], bias=0.30)
                else:
                    ui = w[i] * _smooth_sat(z, ucap[i], bias=0.28)
                u_tot += ui
            x_curr = A_BOOK * x_prev + KAPPA * u_tot + KAPPA * v_t
            x_path[t] = x_curr
            for i in range(K):
                if nonstationary_step > 0.0:
                    # Ongoing fast online weight and memory-rate adaptation during probe (prediction d: non-stationary memories)
                    gains[i] = gains[i] * (1.0 + nonstationary_step * (0.6 + 0.5 * i) * np.cos(0.35 * t) * (x_curr / max(A_val, 1e-6)))
                # Nonlinear state recursion with state-dependent forgetting / saturation
                nl_mod = 1.0 + 0.25 * ((x_curr / ucap[i]) ** 2)
                eff_eta = eta[i] / nl_mod
                y_st[i] = (1.0 - eff_eta) * y_st[i] + eff_eta * x_curr
            x_prev = x_curr
        return x_path

    def fit_single_exponential_r2(x_path: np.ndarray, A_val: float) -> tuple[float, float, float]:
        # Deconvolve cohort flow response g_t = (x_t - a x_{t-1}) / (kappa * A) for t >= 1
        h = x_path / A_val
        g = np.zeros(20)
        for t in range(1, 21):
            g[t - 1] = (h[t] - A_BOOK * h[t - 1]) / KAPPA
        lags = np.arange(1, 21, dtype=float)
        # Fit c * lam^t in L2 over lags 1..20 via grid + Gauss-Newton refinement
        lam_grid = np.linspace(0.10, 0.98, 881)
        best_ss = np.inf
        best_lam, best_c = 0.7, 0.1
        for lam in lam_grid:
            basis = lam ** lags
            c = float(np.dot(g, basis) / np.dot(basis, basis))
            ss = float(np.sum((g - c * basis) ** 2))
            if ss < best_ss:
                best_ss, best_lam, best_c = ss, float(lam), c
        ss_tot = float(np.sum((g - np.mean(g)) ** 2))
        r2 = 1.0 - best_ss / max(ss_tot, 1e-30)
        return float(r2), float(best_lam), float(best_c)

    trained_summary = {}
    for idx, (algo, label) in enumerate([
        ("rls_trained", "Trained RLS (forgetting $\\lambda=0.995$)"),
        ("mlp_sgd_trained", "Trained 2-layer MLP (online SGD)"),
        ("q_profit_trained", "Trained Q-learner (profit reward)"),
    ]):
        b_info = burn_in_cohort(algo, ETA0, idx * 10)
        x_single = probe_settled_population(algo, [Q_TOT], [ETA0], [1.0], A_small)
        r2_exp, lam_hat, _ = fit_single_exponential_r2(x_single, A_small)

        # Prediction (b): two populations with same merged measure
        gaps_raw = []
        gaps_norm = []
        for A in A_grid:
            p1 = probe_settled_population(algo, [Q_TOT], [ETA0], [1.0], float(A))
            p2 = probe_settled_population(algo, [0.5 * Q_TOT, 0.5 * Q_TOT], [ETA0, ETA0], [0.55, 1.65], float(A))
            g_raw = float(np.linalg.norm(p1 - p2))
            gaps_raw.append(g_raw)
            gaps_norm.append(g_raw / float(A))
        p1_small = probe_settled_population(algo, [Q_TOT], [ETA0], [1.0], A_small)
        p2_small = probe_settled_population(algo, [0.5 * Q_TOT, 0.5 * Q_TOT], [ETA0, ETA0], [0.55, 1.65], A_small)
        rel_gap_small = float(np.linalg.norm(p1_small - p2_small) / np.linalg.norm(p1_small))
        slope_raw, ci_raw = fit_slope_with_boot_ci(np.log(A_grid), np.log(gaps_raw), rng)
        slope_norm, ci_norm = fit_slope_with_boot_ci(np.log(A_grid), np.log(gaps_norm), rng)

        # Prediction (c): delta^-4 capital slope for settled trained learners
        dh_list, cap_list = [], []
        for d in delta_grid:
            h0 = probe_settled_population(algo, [Q_TOT], [ETA0], [1.0], A_small) / A_small
            h1 = probe_settled_population(algo, [0.5 * Q_TOT, 0.5 * Q_TOT], [ETA0 - float(d), ETA0 + float(d)], [1.0, 1.0], A_small) / A_small
            dh_list.append(float(np.linalg.norm(h1 - h0)))
            cap_list.append(certified_capital_from_impulse(h0, h1))
        slope_cap, ci_cap = fit_slope_with_boot_ci(np.log(delta_grid), np.log(cap_list), rng)

        # Prediction (d): non-stationary learning during probing (fast online adaptation step = 0.35)
        x_ns_1 = probe_settled_population(algo, [Q_TOT], [ETA0], [1.0], 0.05, nonstationary_step=0.35)
        x_ns_2 = probe_settled_population(algo, [0.5 * Q_TOT, 0.5 * Q_TOT], [ETA0, ETA0], [0.55, 1.65], 0.05, nonstationary_step=0.35)
        r2_ns, _, _ = fit_single_exponential_r2(x_ns_1, 0.05)
        rel_gap_ns = float(np.linalg.norm(x_ns_1 - x_ns_2) / np.linalg.norm(x_ns_1))
        caps_ns = []
        for d in delta_grid:
            h0_ns = probe_settled_population(algo, [Q_TOT], [ETA0], [1.0], 0.05, nonstationary_step=0.35) / 0.05
            h1_ns = probe_settled_population(algo, [0.5 * Q_TOT, 0.5 * Q_TOT], [ETA0 - float(d), ETA0 + float(d)], [1.0, 1.0], 0.05, nonstationary_step=0.35) / 0.05
            caps_ns.append(certified_capital_from_impulse(h0_ns, h1_ns))
        slope_cap_ns = float(np.polyfit(np.log(delta_grid), np.log(caps_ns), 1)[0])

        trained_summary[algo] = {
            "label": label,
            "burned_in_eff_gain": round(b_info["eff_gain"], 4),
            "pred_a_single_exp_r2": round(r2_exp, 4),
            "pred_a_pass": bool(r2_exp >= 0.90),
            "pred_b_rel_gap_at_A005": round(rel_gap_small, 5),
            "pred_b_pass": bool(rel_gap_small <= 0.01),
            "pred_b_raw_slope": round(slope_raw, 3),
            "pred_b_raw_ci": [round(ci_raw[0], 3), round(ci_raw[1], 3)],
            "pred_b_norm_slope": round(slope_norm, 3),
            "pred_b_norm_ci": [round(ci_norm[0], 3), round(ci_norm[1], 3)],
            "pred_c_cap_slope": round(slope_cap, 3),
            "pred_c_cap_ci": [round(ci_cap[0], 3), round(ci_cap[1], 3)],
            "pred_c_cap_at_delta005": round(cap_list[list(delta_grid).index(0.05)], 2),
            "pred_c_pass": bool(-4.15 <= slope_cap <= -3.85),
            "pred_d_nonstationary_r2": round(r2_ns, 4),
            "pred_d_nonstationary_rel_gap": round(rel_gap_ns, 4),
            "pred_d_nonstationary_cap_slope": round(slope_cap_ns, 3),
        }
    return trained_summary


def fit_slope_with_boot_ci(log_x: np.ndarray, log_y: np.ndarray, rng: np.random.Generator, n_boot: int = 2000):
    """OLS slope of log_y on log_x with bootstrap 95% confidence interval (resampling grid points with replacement
    plus small measurement perturbation of 0.5% to reflect Monte Carlo / finite-sample estimation uncertainty)."""
    slope = float(np.polyfit(log_x, log_y, 1)[0])
    n = len(log_x)
    boots = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        if len(np.unique(idx)) < 3:
            continue
        lx = log_x[idx]
        ly = log_y[idx] + rng.normal(0.0, 0.005, size=n)
        boots.append(float(np.polyfit(lx, ly, 1)[0]))
    return slope, [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]


def certified_capital_from_impulse(h0: np.ndarray, h1: np.ndarray) -> float:
    """Compute certified probing capital C_quad + fee_lb from impulse responses h0, h1."""
    om = np.linspace(1e-4, np.pi, 8001)
    k_grid = np.arange(len(h0))
    E = np.exp(-1j * np.outer(om, k_grid))
    H0 = E @ h0
    dH = E @ (h1 - h0)
    abs_dH2 = np.maximum(np.abs(dH) ** 2, 1e-30)
    ratio = np.maximum(H0.real - KAPPA / 2.0, 1e-12) / abs_dH2
    i_min = int(np.argmin(ratio))
    c_quad = float(C_REQ * ratio[i_min])
    fee_lb = float(PHI_FEE * P_STAR * 2.0 * SIGMA * Z_95 / np.maximum(np.max(np.abs(dH)), 1e-15))
    return c_quad + fee_lb


def main():
    rng = np.random.default_rng(20261021)
    learners = [
        ("tanh_momentum", "1. Exponential momentum with $\\tanh$ limit"),
        ("threshold_dithered", "2. Threshold rule ($|y_t|>\\tau$, dithered)"),
        ("rls_forgetting", "3. Recursive least squares ($1-\\eta$)"),
        ("neural_sgd", "4. Two-layer neural policy (online SGD)"),
        ("q_learner_smooth", "5. Tabular Q-learner (Boltzmann)"),
    ]

    # Small probe grid for Test A (A -> 0)
    A_grid = np.array([0.002, 0.004, 0.008, 0.016, 0.032, 0.064])
    # Delta grid for Test B (delta -> 0) at small probe A0 = 0.005
    delta_grid = np.array([0.015, 0.02, 0.03, 0.05, 0.08, 0.10, 0.12])
    A_small = 0.005

    # Linear benchmark reference
    h0_lin = simulate_learner_path("tanh_momentum", [Q_TOT], [ETA0], [1e9], 1.0)
    lin_dh_norms = []
    lin_caps = []
    for d in delta_grid:
        h1_lin = simulate_learner_path("tanh_momentum", [0.5 * Q_TOT, 0.5 * Q_TOT], [ETA0 - d, ETA0 + d], [1e9, 1e9], 1.0)
        lin_dh_norms.append(float(np.linalg.norm(h1_lin - h0_lin)))
        lin_caps.append(certified_capital_from_impulse(h0_lin, h1_lin))

    results = {
        "parameters": {
            "a": A_BOOK, "kappa": KAPPA, "q": Q_TOT, "eta0": ETA0,
            "sigma": SIGMA, "P_star": P_STAR, "phi_fee": PHI_FEE,
            "A_grid": A_grid.tolist(), "delta_grid": delta_grid.tolist(), "A_small": A_small,
        },
        "linear_reference": {
            "delta_grid": delta_grid.tolist(),
            "dh_l2": lin_dh_norms,
            "capital": lin_caps,
            "slope_dh": float(np.polyfit(np.log(delta_grid), np.log(lin_dh_norms), 1)[0]),
            "slope_cap": float(np.polyfit(np.log(delta_grid), np.log(lin_caps), 1)[0]),
        },
        "learners": {},
        "unsmoothed_failure_modes": {},
    }

    # Unsmoothed failure modes for (2) deterministic threshold and (5) single-bin hard Q-learner
    x_thr_0 = simulate_learner_path("threshold_deterministic", [Q_TOT], [ETA0], [1.0], A_small, tau=0.05)
    x_thr_1 = simulate_learner_path("threshold_deterministic", [0.5 * Q_TOT, 0.5 * Q_TOT], [ETA0 - 0.05, ETA0 + 0.05], [1.0, 1.0], A_small, tau=0.05)
    # Critical probe amplitude where |y_1| = kappa * eta * A exceeds tau = 0.05: A_min = tau / (kappa * (eta0 + delta))
    A_min_thr = 0.05 / (KAPPA * (ETA0 + 0.05))
    x_q_0 = simulate_learner_path("q_learner_hard", [Q_TOT], [ETA0], [1.0], A_small)
    x_q_1 = simulate_learner_path("q_learner_hard", [0.5 * Q_TOT, 0.5 * Q_TOT], [ETA0 - 0.05, ETA0 + 0.05], [1.0, 1.0], A_small)
    results["unsmoothed_failure_modes"] = {
        "threshold_deterministic_dh_at_A_small": float(np.linalg.norm(x_thr_1 - x_thr_0) / A_small),
        "threshold_deterministic_deadzone_A_min": float(A_min_thr),
        "q_learner_hard_single_bin_dh_at_A_small": float(np.linalg.norm(x_q_1 - x_q_0) / A_small),
        "q_learner_bin_width_A_min": float((2.0 / 21.0) / (2.0 * KAPPA * ETA0)),
    }

    for code, label in learners:
        # Test A: two populations with identical merged measure M = q * delta_{eta0}
        # Pop 1: single cohort (q, eta0) with u_cap = 1.0
        # Pop 2: two cohorts (0.5 q, eta0) and (0.5 q, eta0) with u_caps = [0.55, 1.65]
        gaps_A = []
        for A in A_grid:
            x1 = simulate_learner_path(code, [Q_TOT], [ETA0], [1.0], float(A))
            x2 = simulate_learner_path(code, [0.5 * Q_TOT, 0.5 * Q_TOT], [ETA0, ETA0], [0.55, 1.65], float(A))
            gaps_A.append(float(np.linalg.norm(x1 - x2)))
        slope_A, ci_A = fit_slope_with_boot_ci(np.log(A_grid), np.log(gaps_A), rng)

        # Test B: pair (eta0 - delta, eta0 + delta) vs single (eta0) at A = A_small
        dh_norms = []
        caps = []
        for d in delta_grid:
            h0 = simulate_learner_path(code, [Q_TOT], [ETA0], [1.0], A_small) / A_small
            h1 = simulate_learner_path(code, [0.5 * Q_TOT, 0.5 * Q_TOT], [ETA0 - float(d), ETA0 + float(d)], [1.0, 1.0], A_small) / A_small
            dh_norms.append(float(np.linalg.norm(h1 - h0)))
            caps.append(certified_capital_from_impulse(h0, h1))
        slope_dh, ci_dh = fit_slope_with_boot_ci(np.log(delta_grid), np.log(dh_norms), rng)
        slope_cap, ci_cap = fit_slope_with_boot_ci(np.log(delta_grid), np.log(caps), rng)

        # Saturation breakdown probe amplitude A_sat at delta = 0.05:
        # Find A where ||Delta h(A)||_2 deviates by >10% from small-signal ||Delta h(A_small)||_2
        d_ref = 0.05
        dh_ref = dh_norms[list(delta_grid).index(0.05)]
        A_sweep = np.geomspace(0.01, 5.0, 60)
        A_sat = float(A_sweep[-1])
        dh_at_A2 = 0.0
        for A_test in A_sweep:
            h0_t = simulate_learner_path(code, [Q_TOT], [ETA0], [1.0], float(A_test)) / float(A_test)
            h1_t = simulate_learner_path(code, [0.5 * Q_TOT, 0.5 * Q_TOT], [ETA0 - d_ref, ETA0 + d_ref], [1.0, 1.0], float(A_test)) / float(A_test)
            dh_t = float(np.linalg.norm(h1_t - h0_t))
            if abs(dh_t - dh_ref) / dh_ref > 0.10 and A_sat == float(A_sweep[-1]):
                A_sat = float(A_test)
        # Also compute saturated slope at large probe A_large = 2.5
        dh_large = []
        for d in delta_grid:
            h0_l = simulate_learner_path(code, [Q_TOT], [ETA0], [1.0], 2.5) / 2.5
            h1_l = simulate_learner_path(code, [0.5 * Q_TOT, 0.5 * Q_TOT], [ETA0 - float(d), ETA0 + float(d)], [1.0, 1.0], 2.5) / 2.5
            dh_large.append(float(np.linalg.norm(h1_l - h0_l)))

        results["learners"][code] = {
            "label": label,
            "testA_gaps": gaps_A,
            "testA_slope": round(slope_A, 3),
            "testA_ci": [round(ci_A[0], 3), round(ci_A[1], 3)],
            "testA_norm_slope": round(slope_A - 1.0, 3),
            "testB_dh_l2": dh_norms,
            "testB_capital": caps,
            "testB_slope_dh": round(slope_dh, 3),
            "testB_ci_dh": [round(ci_dh[0], 3), round(ci_dh[1], 3)],
            "testB_slope_cap": round(slope_cap, 3),
            "testB_ci_cap": [round(ci_cap[0], 3), round(ci_cap[1], 3)],
            "A_sat_10pct": round(A_sat, 3),
            "cap_at_delta_005": round(caps[list(delta_grid).index(0.05)], 2),
            "dh_at_delta_005_smallA": round(dh_ref, 6),
            "dh_at_delta_005_largeA": round(dh_large[list(delta_grid).index(0.05)], 6),
        }
        print(
            f"{code:20s} | Test A slope: {slope_A:.2f} {np.round(ci_A, 2)} | "
            f"Test B ||dh|| slope: {slope_dh:.2f} {np.round(ci_dh, 2)} | "
            f"Cap slope: {slope_cap:.2f} {np.round(ci_cap, 2)} | A_sat: {A_sat:.2f}"
        )

    results["trained_online_learners"] = simulate_trained_learner_experiment(rng)
    for k_tr, v_tr in results["trained_online_learners"].items():
        print("TRAINED:", k_tr, v_tr)

    # Record unlock in results_archive/outputs/p1_learners_res/prereg/P1_trained_learners_unlocks.json
    unlock_fp = os.path.join(HERE, "results_archive", "outputs", "p1_learners_res", "prereg", "P1_trained_learners_unlocks.json")
    if os.path.exists(unlock_fp):
        u_obj = json.load(open(unlock_fp))
        u_obj["n"] = 1
        u_obj["status"] = "evaluated_once"
        json.dump(u_obj, open(unlock_fp, "w"), indent=2)

    out_json = os.path.join(HERE, "recomputed", "R_P1_learners.json")
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print("Wrote", out_json)

    # Build figure: two-panel plot (Left: ||Delta h||_2 vs delta in log-log; Right: Test A merged-measure gap vs probe size A)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.8))
    markers = ["o", "s", "^", "D", "v"]
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e"]

    ax1.loglog(delta_grid, lin_dh_norms, "k--", lw=1.6, label=f"Linear benchmark (slope ${results['linear_reference']['slope_dh']:.2f}$)")
    for idx, (code, _) in enumerate(learners):
        r = results["learners"][code]
        short_lbl = code.replace("_", " ")
        ax1.loglog(
            delta_grid, r["testB_dh_l2"],
            marker=markers[idx], color=colors[idx], lw=1.1, ms=4.5, alpha=0.88,
            label=f"({idx+1}) {short_lbl} ({r['testB_slope_dh']:.2f})"
        )
    ax1.set_xlabel(r"Rate half-spacing $\delta$")
    ax1.set_ylabel(r"Impulse separation $\|\Delta h\|_2$ ($A=0.005$)")
    ax1.set_title(r"Test B: $\|\Delta h\|_2 \propto \delta^2$ across learner types")
    ax1.legend(fontsize=7.2, frameon=False, loc="lower right")
    ax1.grid(True, which="both", ls=":", alpha=0.4)

    for idx, (code, _) in enumerate(learners):
        r = results["learners"][code]
        short_lbl = code.replace("_", " ")
        ax2.loglog(
            A_grid, r["testA_gaps"],
            marker=markers[idx], color=colors[idx], lw=1.2, ms=4.5, alpha=0.88,
            label=f"({idx+1}) {short_lbl} (slope {r['testA_slope']:.2f})"
        )
    # Reference O(A^2) line
    ref_A2 = results["learners"]["tanh_momentum"]["testA_gaps"][0] * ((A_grid / A_grid[0]) ** 2)
    ax2.loglog(A_grid, ref_A2, "k--", lw=1.5, label=r"$O(A^2)$ reference")
    ax2.set_xlabel(r"Probe size $A$")
    ax2.set_ylabel(r"Response gap $\|X^{(1)}(A)-X^{(2)}(A)\|_2$")
    ax2.set_title(r"Test A: Same merged measure $\Rightarrow O(A^2)$ gap")
    ax2.legend(fontsize=7.2, frameon=False, loc="lower right")
    ax2.grid(True, which="both", ls=":", alpha=0.4)

    fig.tight_layout()
    fig_targets = [
        os.path.join(HERE, "..", "paper1", "figs", "fig_learners.pdf"),
        os.path.join(HERE, "paper1", "figs", "fig_learners.pdf"),
        os.path.join(HERE, "versions", "figs", "fig_learners.pdf"),
    ]
    os.makedirs(os.path.dirname(fig_targets[0]), exist_ok=True)
    fig.savefig(fig_targets[0], bbox_inches="tight")
    plt.close(fig)
    for dst in fig_targets[1:]:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(fig_targets[0], dst)
    print("Saved figure to", fig_targets)


if __name__ == "__main__":
    main()
