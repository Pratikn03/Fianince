#!/usr/bin/env python3
"""
Independent High-Precision Mathematical Verification for Paper 1 and Paper 2.
Implements Phase 1 (Task 1.1-1.4) and Phase 2 (Task 2.1-2.4) of the Master
Research Hardening and Publication Readiness Audit using 80-digit arbitrary-precision
arithmetic (`decimal.Decimal` from the Python standard library) alongside numpy cross-checks.

Outputs:
  ceiling_suite/papers/recomputed/R_independent_math_audit.json
"""

from __future__ import annotations

import json
import math
from decimal import Decimal, getcontext
from pathlib import Path
import numpy as np

getcontext().prec = 80  # 80 decimal digits of precision

OUT_PATH = Path(__file__).resolve().parent / "recomputed" / "R_independent_math_audit.json"


def D(val: str | int | float | Decimal) -> Decimal:
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))


def _pow_dec(x: Decimal, m: int) -> Decimal:
    if m == 0:
        return D(1)
    return x ** m


def _dec_cos(x: Decimal) -> Decimal:
    """80-digit cosine via Taylor series around reduced argument."""
    # Reduce x mod 2*pi
    term = D(1)
    s = D(1)
    x2 = x * x
    for k in range(1, 70):
        term = -term * x2 / D((2 * k - 1) * (2 * k))
        s += term
        if abs(term) < D("1e-78"):
            break
    return s


def _dec_pi() -> Decimal:
    """80-digit pi via Machin-like formula: pi/4 = 4*arctan(1/5) - arctan(1/239)."""
    def arctan_inv(m: int) -> Decimal:
        m_d = D(m)
        m2 = m_d * m_d
        term = D(1) / m_d
        s = term
        for k in range(1, 80):
            term = -term / m2
            add = term / D(2 * k + 1)
            s += add
            if abs(add) < D("1e-82"):
                break
        return s

    return D(4) * (D(4) * arctan_inv(5) - arctan_inv(239))


PI_80 = _dec_pi()


def _jacobi_sym_eigenvalues_dec(A: list[list[Decimal]], max_sweeps: int = 35) -> list[Decimal]:
    """Pure 80-digit Decimal Jacobi eigenvalue algorithm for a symmetric matrix A."""
    n = len(A)
    M = [[A[i][j] for j in range(n)] for i in range(n)]
    for _ in range(max_sweeps):
        max_off = D(0)
        for p in range(n):
            for q in range(p + 1, n):
                if abs(M[p][q]) > max_off:
                    max_off = abs(M[p][q])
        if max_off < D("1e-72"):
            break
        for p in range(n):
            for q in range(p + 1, n):
                apq = M[p][q]
                if abs(apq) < D("1e-75"):
                    continue
                app = M[p][p]
                aqq = M[q][q]
                tau = (aqq - app) / (D(2) * apq)
                if tau >= 0:
                    t = D(1) / (tau + (D(1) + tau * tau).sqrt())
                else:
                    t = -D(1) / (-tau + (D(1) + tau * tau).sqrt())
                c = D(1) / (D(1) + t * t).sqrt()
                s = t * c
                M[p][p] = app - t * apq
                M[q][q] = aqq + t * apq
                M[p][q] = D(0)
                M[q][p] = D(0)
                for r in range(n):
                    if r != p and r != q:
                        mrp = M[r][p]
                        mrq = M[r][q]
                        M[r][p] = c * mrp - s * mrq
                        M[p][r] = M[r][p]
                        M[r][q] = s * mrp + c * mrq
                        M[q][r] = M[r][q]
    return sorted(M[i][i] for i in range(n))


def _sigma_min_dec(mat: list[list[Decimal]]) -> Decimal:
    """Compute smallest singular value of a square/rectangular matrix in 80-digit Decimal."""
    m = len(mat)
    n = len(mat[0])
    ata = [[sum(mat[k][i] * mat[k][j] for k in range(m)) for j in range(n)] for i in range(n)]
    evals = _jacobi_sym_eigenvalues_dec(ata)
    min_ev = max(evals[0], D(0))
    return min_ev.sqrt()


def _closed_loop_impulse_dec(a: Decimal, kappa: Decimal, rates: list[Decimal], weights: list[Decimal], T: int) -> list[Decimal]:
    """Compute exact closed-loop impulse response h_0, ..., h_{T-1} in 80-digit Decimal."""
    k = [sum(w * _pow_dec(r, m) for r, w in zip(rates, weights)) for m in range(T)]
    h = [D(0)] * T
    h[0] = kappa
    for t in range(1, T):
        conv = sum(k[m] * h[t - 1 - m] for m in range(t))
        h[t] = a * h[t - 1] + kappa * conv
    return h


def audit_task_1_1_known_pair() -> dict:
    """Verify Task 1.1: Known-pair identification, quantity scaling, committed capital vs. dissipation."""
    a = D("0.5")
    kappa = D("0.8")
    q = D("0.2")
    eta0 = D("0.4")
    r0 = D(1) - eta0
    sigma = D("0.01")
    mu_margin = D("0.25")
    c_cost = D("0.001")
    P_star = D("100.0")
    T = 60

    deltas = [D(s) for s in ["0.12", "0.08", "0.05", "0.03", "0.01", "0.005", "0.001"]]
    h0 = _closed_loop_impulse_dec(a, kappa, [r0], [q * eta0], T)

    rows = []
    for d in deltas:
        r_minus = D(1) - (eta0 - d)
        r_plus = D(1) - (eta0 + d)
        w_minus = (q / D(2)) * (eta0 - d)
        w_plus = (q / D(2)) * (eta0 + d)
        hd = _closed_loop_impulse_dec(a, kappa, [r_minus, r_plus], [w_minus, w_plus], T)
        diff = [hd[t] - h0[t] for t in range(T)]

        d0_err = abs(diff[0])
        d1_err = abs(diff[1])
        d2_exact = -(kappa ** 2) * q * (d ** 2)
        d2_err = abs(diff[2] - d2_exact)

        norm_d = sum(x * x for x in diff).sqrt()
        z_95 = D("1.6448536269514722")
        V_single_pulse = D(2) * sigma * z_95 / norm_d
        B_committed_single = (mu_margin + D("0.5")) * kappa * (V_single_pulse ** 2) + (c_cost + mu_margin * P_star) * V_single_pulse
        B_quad_single = (mu_margin + D("0.5")) * kappa * (V_single_pulse ** 2)

        # Repeated flat round-trip cycles with per-cycle pulse v_cap = 1.0 (capital reuse across cycles)
        diff_rt = [diff[0]] + [diff[t] - diff[t - 1] for t in range(1, T)]
        norm_d_rt = sum(x * x for x in diff_rt).sqrt()
        v_cap = D("1.0")
        N_cycles_cont = ((D(2) * sigma * z_95) / (norm_d_rt * v_cap)) ** 2
        loss_per_cycle = (v_cap ** 2) * (h0[0] - h0[1])
        total_dissipation_reused = N_cycles_cont * loss_per_cycle
        peak_margin_per_cycle = (mu_margin + D("0.5")) * kappa * (v_cap ** 2) + (c_cost + mu_margin * P_star) * v_cap
        total_volume_reused = N_cycles_cont * (D(2) * v_cap)

        rows.append({
            "delta": float(d),
            "tap0_abs_err": float(d0_err),
            "tap1_abs_err": float(d1_err),
            "tap2_abs_err": float(d2_err),
            "norm_d_T": float(norm_d),
            "norm_d_T_over_delta2": float(norm_d / (d ** 2)),
            "V_single_pulse": float(V_single_pulse),
            "V_times_delta2": float(V_single_pulse * (d ** 2)),
            "B_quad_single": float(B_quad_single),
            "B_quad_times_delta4": float(B_quad_single * (d ** 4)),
            "B_committed_single_total": float(B_committed_single),
            "reused_capital_N_cycles": float(N_cycles_cont),
            "reused_capital_peak_margin": float(peak_margin_per_cycle),
            "reused_capital_total_dissipation": float(total_dissipation_reused),
            "reused_dissipation_times_delta4": float(total_dissipation_reused * (d ** 4)),
            "reused_total_volume": float(total_volume_reused),
        })

    log_d = np.log([r["delta"] for r in rows])
    slope_V = float(np.polyfit(log_d, np.log([r["V_single_pulse"] for r in rows]), 1)[0])
    slope_B_quad = float(np.polyfit(log_d, np.log([r["B_quad_single"] for r in rows]), 1)[0])
    slope_dissip = float(np.polyfit(log_d, np.log([r["reused_capital_total_dissipation"] for r in rows]), 1)[0])
    slope_V_reused = float(np.polyfit(log_d, np.log([r["reused_total_volume"] for r in rows]), 1)[0])

    return {
        "rows": rows,
        "fitted_slopes": {
            "single_pulse_volume_slope": slope_V,
            "single_pulse_quadratic_capital_slope": slope_B_quad,
            "repeated_cycle_irrevocable_dissipation_slope": slope_dissip,
            "repeated_cycle_total_volume_slope": slope_V_reused,
        },
        "max_tap2_identity_error_80dps": max(r["tap2_abs_err"] for r in rows),
    }


def _legendre_eval_and_deriv(K: int, x: Decimal) -> tuple[Decimal, Decimal]:
    """Evaluate P_K(x) and P'_K(x) in 80-digit Decimal."""
    if K == 0:
        return D(1), D(0)
    if K == 1:
        return x, D(1)
    p_prev = D(1)
    p_curr = x
    for n in range(1, K):
        p_next = (D(2 * n + 1) * x * p_curr - D(n) * p_prev) / D(n + 1)
        p_prev, p_curr = p_curr, p_next
    deriv = D(K) * (x * p_curr - p_prev) / (x * x - D(1))
    return p_curr, deriv


def _gauss_legendre_rule_dec(K: int) -> tuple[list[Decimal], list[Decimal]]:
    """K-point Gauss-Legendre rule on [-1, 1] normalized to unit mass in 80-digit Decimal."""
    nodes = []
    weights = []
    for i in range(1, K + 1):
        # Initial guess
        x = -_dec_cos(PI_80 * D(4 * i - 1) / D(4 * K + 2))
        for _ in range(30):
            val, der = _legendre_eval_and_deriv(K, x)
            dx = -val / der
            x += dx
            if abs(dx) < D("1e-76"):
                break
        _, der = _legendre_eval_and_deriv(K, x)
        # Weight on [-1, 1] for dx is 2 / ((1 - x^2) * (P'_K(x))^2); normalize by 1/2 for unit mass
        w = D(1) / ((D(1) - x * x) * der * der)
        nodes.append(x)
        weights.append(w)
    return nodes, weights


def _radau_poly_eval_and_deriv(K: int, x: Decimal) -> tuple[Decimal, Decimal]:
    """Evaluate R_K(x) = (P_{K-1}(x) + P_K(x)) / (1 + x) and its derivative in 80-digit Decimal.
    Wait: the roots of P_{K-1}(x) + P_K(x) = 0 are x = -1 and the K-1 interior Gauss-Radau nodes!
    """
    p_km1, d_km1 = _legendre_eval_and_deriv(K - 1, x)
    p_k, d_k = _legendre_eval_and_deriv(K, x)
    return p_km1 + p_k, d_km1 + d_k


def _gauss_radau_rule_dec(K: int) -> tuple[list[Decimal], list[Decimal]]:
    """K-point Gauss-Radau rule on [-1, 1] with fixed node at -1, normalized to unit mass."""
    nodes = [D(-1)]
    weights = [D(1) / D(K * K)]
    # Interior roots of P_{K-1}(x) + P_K(x) = 0
    # Use numpy Jacobi(0,1) roots as initial guesses, then refine to 80 digits via Newton
    m = K - 1
    J_np = np.zeros((m, m))
    for k in range(m):
        J_np[k, k] = 1.0 / ((2 * k + 1) * (2 * k + 3))
        if k + 1 < m:
            j = k + 1
            J_np[k, k + 1] = 2.0 * j * (j + 1) / ((2 * j + 1) * math.sqrt((2 * j) * (2 * j + 2)))
            J_np[k + 1, k] = J_np[k, k + 1]
    init_roots = np.sort(np.linalg.eigvalsh(J_np))
    for r0 in init_roots:
        x = D(float(r0))
        for _ in range(35):
            val, der = _radau_poly_eval_and_deriv(K, x)
            dx = -val / der
            x += dx
            if abs(dx) < D("1e-76"):
                break
        p_km1, _ = _legendre_eval_and_deriv(K - 1, x)
        # Standard Gauss-Radau weight on [-1, 1] for dx is (1 - x) / (K^2 * P_{K-1}(x)^2); divide by 2 for unit mass
        w = (D(1) - x) / (D(2) * D(K * K) * p_km1 * p_km1)
        nodes.append(x)
        weights.append(w)
    return nodes, weights


def audit_task_1_2_general_k() -> dict:
    """Verify Task 1.2: General-K Gauss vs Gauss-Radau lower bound and Prony/confluent-Vandermonde upper bound."""
    a = D("0.5")
    kappa = D("0.8")
    W = D("0.08")
    r_c = D("0.6")
    T = 40

    k_results = []
    for K in [2, 3, 4, 5]:
        sA, wA = _gauss_legendre_rule_dec(K)
        sB, wB = _gauss_radau_rule_dec(K)

        mom_diffs = []
        for deg in range(2 * K):
            mA = sum(wA[i] * _pow_dec(sA[i], deg) for i in range(K))
            mB = sum(wB[i] * _pow_dec(sB[i], deg) for i in range(K))
            mom_diffs.append(abs(mA - mB))

        max_matched_err = max(mom_diffs[: 2 * K - 1])
        gap_2K_minus_1 = mom_diffs[2 * K - 1]

        min_sep_A = min(abs(sA[i] - sA[j]) for i in range(K) for j in range(i + 1, K))
        min_sep_B = min(abs(sB[i] - sB[j]) for i in range(K) for j in range(i + 1, K))
        min_w = min(min(wA), min(wB))

        spacings = [D(s) for s in ["0.1", "0.05", "0.02", "0.01", "0.005"]]
        norms_h = []
        sigma_mins_jac_unscaled = []
        sigma_mins_jac_scaled = []
        hankel_mins = []

        for de in spacings:
            rA = [r_c + de * s for s in sA]
            rB = [r_c + de * s for s in sB]
            weights_A = [W * w for w in wA]
            weights_B = [W * w for w in wB]

            hA = _closed_loop_impulse_dec(a, kappa, rA, weights_A, T)
            hB = _closed_loop_impulse_dec(a, kappa, rB, weights_B, T)
            nh = sum((hA[t] - hB[t]) ** 2 for t in range(T)).sqrt()
            norms_h.append(float(nh))

            # Unscaled Confluent Vandermonde Jacobian wrt (w_i, r_i): smallest singular value scales as (Delta_eta)^{2K-1}
            J_unscaled = [[D(0)] * (2 * K) for _ in range(2 * K)]
            # Scale-matched Jacobian wrt (w_i * W / de, r_i): columns for dw are multiplied by de / W so both blocks scale as (Delta_eta)^{2K-2}
            J_scaled = [[D(0)] * (2 * K) for _ in range(2 * K)]
            for m in range(2 * K):
                for i in range(K):
                    J_unscaled[m][i] = _pow_dec(rA[i], m)
                    J_unscaled[m][K + i] = weights_A[i] * D(m) * _pow_dec(rA[i], m - 1) if m >= 1 else D(0)
                    J_scaled[m][i] = (W / de) * _pow_dec(rA[i], m)
                    J_scaled[m][K + i] = weights_A[i] * D(m) * _pow_dec(rA[i], m - 1) if m >= 1 else D(0)
            sigma_mins_jac_unscaled.append(float(_sigma_min_dec(J_unscaled)))
            sigma_mins_jac_scaled.append(float(_sigma_min_dec(J_scaled)))

            # K x K Hankel matrix of moments k_0, ..., k_{2K-2}
            k_moms = [sum(weights_A[i] * _pow_dec(rA[i], m) for i in range(K)) for m in range(2 * K)]
            H_mat = [[k_moms[i + j] for j in range(K)] for i in range(K)]
            hankel_mins.append(float(_sigma_min_dec(H_mat)))

        log_de = np.log([float(d) for d in spacings])
        slope_h = float(np.polyfit(log_de, np.log(norms_h), 1)[0])
        slope_jac_unscaled = float(np.polyfit(log_de, np.log(sigma_mins_jac_unscaled), 1)[0])
        slope_jac_scaled = float(np.polyfit(log_de, np.log(sigma_mins_jac_scaled), 1)[0])
        slope_hankel = float(np.polyfit(log_de, np.log(hankel_mins), 1)[0])

        k_results.append({
            "K": K,
            "theoretical_h_slope": 2 * K - 1,
            "fitted_h_slope": slope_h,
            "theoretical_N_minimax_exponent": -(4 * K - 2),
            "theoretical_unscaled_jacobian_sigma_min_slope": 2 * K - 1,
            "fitted_unscaled_jacobian_sigma_min_slope": slope_jac_unscaled,
            "theoretical_scaled_jacobian_sigma_min_slope": 2 * K - 2,
            "fitted_scaled_jacobian_sigma_min_slope": slope_jac_scaled,
            "theoretical_hankel_sigma_min_slope": 2 * K - 2,
            "fitted_hankel_sigma_min_slope": slope_hankel,
            "max_matched_moment_err_80dps": float(max_matched_err),
            "moment_2K_minus_1_gap": float(gap_2K_minus_1),
            "min_rule_node_sep": float(min(min_sep_A, min_sep_B)),
            "min_rule_weight": float(min_w),
        })

    return {"k_cohort_results": k_results}


def audit_task_1_3_general_cm_memory() -> dict:
    """Verify Task 1.3: General completely monotone memory O(1/log N) lower and upper bounds
    and dependence on boundary parameter rho -> 1."""
    a = D("0.5")
    kappa = D("0.8")
    W = D("0.1")
    T = 60

    pairs_summary = []
    for rho_str in ["0.5", "0.9", "0.99"]:
        rho = D(rho_str)
        for n in [2, 4, 6, 8, 10]:
            N_pts = 2 * n
            t_nodes = [-_dec_cos(PI_80 * D(i) / D(N_pts - 1)) for i in range(N_pts)]
            raw_w = []
            for i in range(N_pts):
                prod = D(1)
                for j in range(N_pts):
                    if i != j:
                        prod *= (t_nodes[i] - t_nodes[j])
                raw_w.append(D(1) / prod)

            pos_idx = [i for i in range(N_pts) if raw_w[i] > 0]
            neg_idx = [i for i in range(N_pts) if raw_w[i] < 0]
            pos_mass = sum(raw_w[i] for i in pos_idx)
            neg_mass = sum(-raw_w[i] for i in neg_idx)

            rA = [rho * (t_nodes[i] + D(1)) / D(2) for i in pos_idx]
            wA = [W * raw_w[i] / pos_mass for i in pos_idx]
            rB = [rho * (t_nodes[i] + D(1)) / D(2) for i in neg_idx]
            wB = [W * (-raw_w[i]) / neg_mass for i in neg_idx]

            max_mom_err = max(
                abs(sum(wA[k] * _pow_dec(rA[k], m) for k in range(n)) - sum(wB[k] * _pow_dec(rB[k], m) for k in range(n)))
                for m in range(2 * n - 1)
            )
            all_r = sorted(set(rA + rB))
            w1 = D(0)
            cdf_diff = D(0)
            for idx_r in range(len(all_r) - 1):
                r_curr = all_r[idx_r]
                for k in range(n):
                    if rA[k] == r_curr:
                        cdf_diff += wA[k]
                    if rB[k] == r_curr:
                        cdf_diff -= wB[k]
                w1 += abs(cdf_diff) * (all_r[idx_r + 1] - r_curr)

            hA = _closed_loop_impulse_dec(a, kappa, rA, wA, T)
            hB = _closed_loop_impulse_dec(a, kappa, rB, wB, T)
            h_diff_norm = sum((hA[t] - hB[t]) ** 2 for t in range(T)).sqrt()

            pairs_summary.append({
                "rho": float(rho),
                "n_atoms": n,
                "max_moment_err_up_to_2n_minus_2": float(max_mom_err),
                "W1_distance": float(w1),
                "n_times_W1_over_rhoW": float(D(n) * w1 / (rho * W)),
                "closed_loop_h_diff_norm": float(h_diff_norm),
                "theoretical_kernel_bound": float(D(2) * W * (rho ** (2 * n - 1)) / (D(1) - rho)),
            })

    return {"cm_memory_pairs": pairs_summary}


def audit_phase_2_paper2_theorems() -> dict:
    """Verify Phase 2 (Tasks 2.1-2.4):
    1. Bridge identity S = kappa / (1 - a - kappa * Phi) vs ||h||_1 in positive vs contrarian/inventory-overshoot economies.
    2. Hidden-state drift envelope (prop:driftguard) when initial cohort state y_0 != 0.
    3. Markov-Krein finite-window moment bounds [Phi_-, Phi_+] and unboundedness at bar_r = 1.
    """
    a = D("0.5")
    kappa = D("0.8")

    # 1. Positive economy: exact bridge S == sum h_t == ||h||_1
    rates_pos = [D("0.3"), D("0.7"), D("0.9")]
    etas_pos = [D(1) - r for r in rates_pos]
    qs_pos = [D("0.10"), D("0.15"), D("0.10")]
    ws_pos = [q * eta for q, eta in zip(qs_pos, etas_pos)]
    Phi_pos = sum(qs_pos)
    S_exact_pos = kappa / (D(1) - a - kappa * Phi_pos)
    h_pos = _closed_loop_impulse_dec(a, kappa, rates_pos, ws_pos, 400)
    sum_h_pos = sum(h_pos)
    l1_h_pos = sum(abs(x) for x in h_pos)

    # 2. Contrarian/mixed-sign economy where h_t changes sign so ||h||_1 > |S|
    rates_mix = [D("0.2"), D("0.85")]
    etas_mix = [D(1) - r for r in rates_mix]
    qs_mix = [D("0.35"), D("-0.45")]
    ws_mix = [q * eta for q, eta in zip(qs_mix, etas_mix)]
    Phi_mix = sum(qs_mix)
    S_signed_mix = kappa / (D(1) - a - kappa * Phi_mix)
    h_mix = _closed_loop_impulse_dec(a, kappa, rates_mix, ws_mix, 400)
    sum_h_mix = sum(h_mix)
    l1_h_mix = sum(abs(x) for x in h_mix)

    # 3. Non-zero initial state drift envelope (prop:driftguard)
    alpha = D("0.8")
    x0 = D("0.02")
    y0_bar = D("0.05")
    x_cur = x0
    y_cur = [eta * y0_bar for eta in etas_pos]
    unforced_sum = D(0)
    for _ in range(400):
        x_next = a * x_cur + alpha * kappa * sum(q * y for q, y in zip(qs_pos, y_cur))
        y_next = [(D(1) - eta) * y + eta * x_next for eta, y in zip(etas_pos, y_cur)]
        unforced_sum += x_next
        x_cur, y_cur = x_next, y_next
    theo_drift_env = (a * abs(x0) + alpha * kappa * Phi_pos * y0_bar) / (D(1) - a - alpha * kappa * Phi_pos)

    # 4. Markov-Krein window uncertainty width decay vs bar_r -> 1
    mk_rows = []
    k0_val = sum(ws_pos)
    for bar_r_str in ["0.80", "0.90", "0.95", "0.99"]:
        bar_r = D(bar_r_str)
        x0_cheb = D(2) / bar_r - D(1)
        rho_cheb = D(1) / (x0_cheb + (x0_cheb * x0_cheb - D(1)).sqrt())
        for n_win in [2, 4, 8, 16]:
            m_deg = n_win - 1
            cheb_E = (D(2) / bar_r) * (rho_cheb ** m_deg) / (x0_cheb * x0_cheb - D(1))
            mk_rows.append({
                "bar_r": float(bar_r),
                "window_n": n_win,
                "chebyshev_decay_factor": float(rho_cheb),
                "worst_case_Phi_width_bound": float(D(2) * k0_val * cheb_E),
            })

    return {
        "positive_economy_bridge": {
            "S_formula": float(S_exact_pos),
            "sum_h_400": float(sum_h_pos),
            "l1_norm_h_400": float(l1_h_pos),
            "bridge_abs_err": float(abs(S_exact_pos - l1_h_pos)),
        },
        "mixed_sign_contrarian_economy": {
            "S_signed_formula": float(S_signed_mix),
            "sum_h_400": float(sum_h_mix),
            "l1_norm_h_400": float(l1_h_mix),
            "l1_minus_signed_S": float(l1_h_mix - S_signed_mix),
        },
        "hidden_drift_guard_check": {
            "simulated_unforced_sum_400": float(unforced_sum),
            "theoretical_drift_envelope": float(theo_drift_env),
            "abs_err": float(abs(unforced_sum - theo_drift_env)),
        },
        "markov_krein_window_bounds": mk_rows,
    }


def main() -> None:
    res = {
        "dps": getcontext().prec,
        "task_1_1_known_pair": audit_task_1_1_known_pair(),
        "task_1_2_general_k": audit_task_1_2_general_k(),
        "task_1_3_general_cm_memory": audit_task_1_3_general_cm_memory(),
        "phase_2_paper2_theorems": audit_phase_2_paper2_theorems(),
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(res, indent=2) + "\n")
    print(f"Wrote {OUT_PATH}")
    print("Task 1.1 slopes:", res["task_1_1_known_pair"]["fitted_slopes"])
    for kr in res["task_1_2_general_k"]["k_cohort_results"]:
        print(
            f"K={kr['K']}: h_slope={kr['fitted_h_slope']:.4f} (theo {kr['theoretical_h_slope']}), "
            f"jac_scaled_slope={kr['fitted_scaled_jacobian_sigma_min_slope']:.4f} (theo {kr['theoretical_scaled_jacobian_sigma_min_slope']}), "
            f"jac_unscaled_slope={kr['fitted_unscaled_jacobian_sigma_min_slope']:.4f} (theo {kr['theoretical_unscaled_jacobian_sigma_min_slope']}), "
            f"mom_err={kr['max_matched_moment_err_80dps']:.2e}"
        )
    print("Phase 2 bridge err:", res["phase_2_paper2_theorems"]["positive_economy_bridge"]["bridge_abs_err"])
    print("Phase 2 contrarian ||h||_1 - S:", res["phase_2_paper2_theorems"]["mixed_sign_contrarian_economy"]["l1_minus_signed_S"])
    print("Phase 2 drift envelope err:", res["phase_2_paper2_theorems"]["hidden_drift_guard_check"]["abs_err"])


if __name__ == "__main__":
    main()
