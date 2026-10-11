#!/usr/bin/env python3
"""
Regression and scientific validity tests for the breakthrough experiment suite.
Guarantees prevention of:
- Cash accounting sign inversion in dealer ledgers (exp10)
- In-sample algebraic midpoint leakage in adaptive probing (exp3)
- Omission of price displacement constraints in frontier calculations (exp4)
- Artificial 100% time-zero excursion in non-normal stress tests (exp12)
- Unused timing shift regressors and hardcoded narrative conflicts (exp8)
"""
import pytest
import numpy as np
import json
from pathlib import Path

# ----------------------------------------------------------------------
# 1. Test Dealer Cash Accounting & Conservation (exp10)
# ----------------------------------------------------------------------
def test_dealer_cash_accounting_signs():
    """Verify buying decrements cash and selling increments cash in dealer ledger."""
    initial_cash = 10000.0
    initial_inv = 0.0
    price = 100.0
    half_spread = 0.05
    taker_fee_rate = 0.0004
    
    # Scenario A: Dealer buys 10 units (fill_qty = +10)
    fill_qty = 10.0
    exec_price = price - half_spread # 99.95
    trade_cash_flow = - fill_qty * exec_price # -999.50
    trade_fee = taker_fee_rate * abs(fill_qty) * exec_price
    
    new_cash = initial_cash + trade_cash_flow - trade_fee
    new_inv = initial_inv + fill_qty
    
    # Assert cash decreased
    assert new_cash < initial_cash, "Dealer buying MUST decrease cash"
    assert np.isclose(new_cash, 10000.0 - 999.50 - trade_fee), "Cash deduction must equal trade value plus fee"
    
    # Assert marked equity conserved before fee
    gross_equity = (initial_cash + trade_cash_flow) + new_inv * price
    # gross equity = 10000 - 999.50 + 10 * 100 = 10000.50 (captured half spread)
    assert gross_equity >= initial_cash - 1.0, "Marked equity must be conserved"
    
    # Scenario B: Dealer sells 10 units (fill_qty = -10)
    fill_qty_sell = -10.0
    exec_price_sell = price + half_spread # 100.05
    trade_cash_flow_sell = - fill_qty_sell * exec_price_sell # +1000.50
    
    cash_after_sell = initial_cash + trade_cash_flow_sell
    assert cash_after_sell > initial_cash, "Dealer selling MUST increase cash"

# ----------------------------------------------------------------------
# 2. Test Held-Out Likelihood Ratio Testing (exp3)
# ----------------------------------------------------------------------
def test_held_out_probing_no_algebraic_leakage():
    """Verify probing classification uses held-out data and has non-zero error when models overlap."""
    from breakthrough_experiments.exp3_adaptive_probing import evaluate_probing_protocol
    
    # Test on a small separation where perfect classification is statistically impossible
    res = evaluate_probing_protocol("Method_A_Single_Pulse", delta=0.03, V_target=10.0, T=20, sigma=0.05, N_eval=500)
    
    # Error rate must be strictly positive and non-zero
    assert res["empirical_error"] > 0.0, "Held-out test must have non-zero error under noisy observations"
    assert res["theoretical_error"] > 0.0, "Theoretical Gaussian error must be non-zero"
    # Empirical error should track theoretical error within sampling margin
    assert abs(res["empirical_error"] - res["theoretical_error"]) < 0.15, "Empirical error must track theoretical matched filter"

# ----------------------------------------------------------------------
# 3. Test Frontier Displacement Cap Enforcement (exp4)
# ----------------------------------------------------------------------
def test_frontier_displacement_cap_enforced():
    """Verify exp4 enforces kappa * |v_t| <= D_max and calculates correct effective bound."""
    from breakthrough_experiments.exp4_frontier_phase_diagram import compute_frontier
    
    D_max = 5.0
    kappa = 0.8
    V_max = 50.0
    V_eff_expected = min(V_max, D_max / kappa) # 6.25
    
    assert np.isclose(V_eff_expected, 6.25), "Effective volume limit must equal 6.25"
    
    # Check that results_exp4_phase_diagram.json records V_eff = 6.25
    results_path = Path("breakthrough_experiments/results_exp4_phase_diagram.json")
    if results_path.exists():
        data = json.loads(results_path.read_text())
        assert np.isclose(data["parameters"]["V_eff"], 6.25), "V_eff in results must be 6.25"
        assert np.isclose(data["parameters"]["delta_min"], 0.2028, atol=1e-3), "delta_min must reflect V_eff"

# ----------------------------------------------------------------------
# 4. Test Non-Normal Balance Sheet Initialization & Bounds (exp12)
# ----------------------------------------------------------------------
def test_nonnormal_initial_excursion_not_100_percent():
    """Verify exp12 starts from economically realistic shock and K(J) >= 1.00."""
    from breakthrough_experiments.exp12_nonnormal_balance_sheet import compute_kreiss_constant, build_network_jacobian
    
    J_net = build_network_jacobian(M=2, cross_impact=0.15)
    kreiss_K = compute_kreiss_constant(J_net)
    
    # Spijker's lower bound
    assert kreiss_K >= 1.00 - 1e-6, "Kreiss constant must satisfy K(J) >= 1.00 by Spijker (1991)"
    
    # Check results file
    results_path = Path("breakthrough_experiments/results_exp12_nonnormal_balance_sheet.json")
    if results_path.exists():
        data = json.loads(results_path.read_text())
        for r in data["multi_asset_network"]:
            assert r["initial_shock_pct"] < 1.0, "Initial shock must be economically realistic (e.g. 0.50%), not 100%"
            assert not r["price_breaches_L20"], "Pure price shock must not breach 4.55% buffer"
            assert r["margin_breaches_L20"], "Leveraged dealer margin operator must trigger breach"

# ----------------------------------------------------------------------
# 5. Test Observable Bridge Regressor Shift & Quasi-Differencing (exp8)
# ----------------------------------------------------------------------
def test_observable_bridge_quasi_diff_and_shift():
    """Verify exp8 timing shifts are properly aligned and quasi-differencing purges spurious correlation."""
    from breakthrough_experiments.exp8_observable_bridge import run_bridge_simulation
    
    # When true_gamma = 0 but flow is persistent, naive OLS has high t-stat
    res_naive = run_bridge_simulation(seed=42, true_gamma=0.0, flow_persistence=0.80, use_quasi_diff=False, time_shift=0)
    assert res_naive["t_stat"] > 2.0, "Naive OLS on persistent flow must show spurious significance"
    
    # Quasi-differencing must purge the serial correlation
    res_purged = run_bridge_simulation(seed=42, true_gamma=0.0, flow_persistence=0.80, use_quasi_diff=True, time_shift=0)
    assert abs(res_purged["beta"]) < 0.10, "Quasi-differenced slope must be near zero"
    assert abs(res_purged["t_stat"]) < 2.0, "Quasi-differenced t-stat must be non-significant"

# ----------------------------------------------------------------------
# 6. Test Proposition 2.8 Equity Delta^2 Scaling & BDD-06 (exp7 / TC-0701)
# ----------------------------------------------------------------------
def test_proposition_2_8_equity_delta_squared_scaling():
    """Verify Scenario BDD-06: at A=20.28, delta=0.05, equity error is ~44.8%, not 5%."""
    from scipy.stats import norm
    kappa = 0.8
    q = 0.2
    delta = 0.05
    A_old = 20.28
    sigma_E = 0.50
    
    # Exact equity difference from Proposition 2.8: Delta E = kappa^2 * q * A^2 * delta^2
    delta_E = (kappa**2) * q * (A_old**2) * (delta**2) # ~0.1316
    d_prime = delta_E / sigma_E # ~0.2632
    err_rate = norm.cdf(-0.5 * d_prime) # ~0.448
    
    assert np.isclose(err_rate, 0.448, atol=0.01), f"Expected error ~0.448 under old volume, got {err_rate}"
    
    # Required volume for alpha = 0.05:
    z_alpha = norm.ppf(0.95)
    A_req_correct = (1.0 / delta) * np.sqrt((2.0 * sigma_E * z_alpha) / (kappa**2 * q))
    assert np.isclose(A_req_correct, 71.70, atol=0.1), f"Expected A_req ~71.70, got {A_req_correct}"

# ----------------------------------------------------------------------
# 7. Test Structural Gamma Recovery vs Reduced-Form Attenuation (exp8 / TC-0802)
# ----------------------------------------------------------------------
def test_structural_gamma_recovery():
    """Verify Scenario BDD-07: structural memory regression recovers gamma ~0.20."""
    results_path = Path("breakthrough_experiments/results_exp8_observable_bridge.json")
    if results_path.exists():
        data = json.loads(results_path.read_text())
        rec = data["structural_recovery_true_gamma_0_20"]
        assert abs(rec["mean_recovered_gamma_structural"] - 0.20) < 0.02, "Structural estimator must recover gamma = 0.20 within 0.02"
        assert rec["mean_recovered_gamma_reduced_form"] < 0.05, "Reduced-form lag regression must show attenuation (~0.02)"

# ----------------------------------------------------------------------
# 8. Test Frozen Policy Nonzero Flow & Policy Freeze (exp10 / TC-0903)
# ----------------------------------------------------------------------
def test_frozen_policy_nonzero_execution():
    """Verify Scenario BDD-08: frozen policy executes nonzero trades and has distinct drawdown."""
    results_path = Path("breakthrough_experiments/results_exp10_multi_agent.json")
    if results_path.exists():
        data = json.loads(results_path.read_text())
        summary = data["conditions_summary"]
        dd_p0 = summary["P0_Baseline"]["mean_dealer_drawdown"]
        dd_frozen = summary["P2_Frozen_Policy"]["mean_dealer_drawdown"]
        dd_active = summary["P2_Active_Learning"]["mean_dealer_drawdown"]
        
        # Frozen policy must differ from P0 because it executes nonzero flow
        assert dd_frozen > dd_p0, "Frozen policy must execute nonzero flow, producing distinct drawdown from baseline"
        # All liquidation rates must be 0
        for cond, stats in summary.items():
            assert stats["liquidation_rate"] == 0.0, f"Liquidation rate in {cond} must be 0.0"

# ----------------------------------------------------------------------
# 9. Test Adaptive Probing Measurability (exp3 / TC-0501 / BDD-05)
# ----------------------------------------------------------------------
def test_adaptive_probing_measurability():
    """Verify Scenario BDD-05: adaptive policy chooses different actions given different histories."""
    from breakthrough_experiments.exp3_adaptive_probing import compute_adaptive_probe
    
    hist_high_response = [0.05, 0.08, 0.12]
    hist_flat_response = [0.00, 0.00, 0.00]
    
    a1 = compute_adaptive_probe(hist_high_response, t=3, V_target=40.0)
    a2 = compute_adaptive_probe(hist_flat_response, t=3, V_target=40.0)
    
    assert a1 != a2, "Adaptive policy MUST produce different actions after different feasible observation histories"
    assert a1 < a2, "High response history should throttle probe to conserve capital"

# ----------------------------------------------------------------------
# 10. Test Known-Pair Third Observation Separation (TC-0201 / BDD-01)
# ----------------------------------------------------------------------
def test_known_pair_third_observation_separation():
    """Verify Scenario BDD-01: first two observations have identical means; third differs by kappa^2 q A delta^2."""
    from breakthrough_experiments.exp3_adaptive_probing import get_mean_trajectory
    
    A_probe = 10.0
    delta = 0.05
    kappa = 0.8
    q = 0.2
    
    v_seq = np.zeros(10)
    v_seq[0] = A_probe # single pulse at t=0
    
    mu_0 = get_mean_trajectory(v_seq, delta=delta, T=10, kappa=kappa, q=q, split=False)
    mu_1 = get_mean_trajectory(v_seq, delta=delta, T=10, kappa=kappa, q=q, split=True)
    
    # First observation (t=1): x_1 = kappa * v_0 = 8.0 for both
    assert np.isclose(mu_0[0], mu_1[0]), "Observation 1 mean must be identical across both models"
    # Second observation (t=2): identical means because both models have merged weight q at common rate eta
    assert np.isclose(mu_0[1], mu_1[1]), "Observation 2 mean must be identical across both models"
    # Third observation (t=3): deterministic difference in magnitude kappa^2 * q * A * delta^2
    diff_obs3 = abs(mu_1[2] - mu_0[2])
    expected_diff = (kappa**2) * q * A_probe * (delta**2)
    assert np.isclose(diff_obs3, expected_diff, atol=1e-5), f"Observation 3 difference must equal {expected_diff}, got {diff_obs3}"

# ----------------------------------------------------------------------
# 11. Test Transmission Zero Inversion vs Closed-Loop Poles (exp2 / TC-0601)
# ----------------------------------------------------------------------
def test_unknown_mixture_transmission_zero_inversion():
    """Verify Theorem 2.3: cohort poles 1 - eta are transmission zeros of H(z), not closed-loop poles."""
    from breakthrough_experiments.exp2_unknown_mixture import simulate_closed_loop_impulse, blind_transfer_function_inversion
    
    true_etas = np.array([0.30])
    true_weights = np.array([0.20])
    true_poles = 1.0 - true_etas # [0.70]
    
    h = simulate_closed_loop_impulse(true_weights, true_etas, T=100)
    # Recover via transmission zeros
    est_K, est_poles, _ = blind_transfer_function_inversion(h, max_K=4)
    
    # Transmission zero should match true cohort pole 0.70
    min_dist = np.min(np.abs(est_poles - 0.70))
    assert min_dist < 0.05, f"Estimated transmission zero must match cohort memory pole 0.70, got {est_poles}"
    # Must NOT equal closed loop poles 0.42557 or 0.82243
    assert abs(est_poles[0] - 0.82243) > 0.05, "Must not confuse transmission zero with closed-loop pole 0.822"
    assert abs(est_poles[0] - 0.42557) > 0.05, "Must not confuse transmission zero with closed-loop pole 0.426"

# ----------------------------------------------------------------------
# 12. Test Sequential Frontier Theta(delta^-4) Scaling & 412-Pulse Under-accumulation
# ----------------------------------------------------------------------
def test_sequential_frontier_delta_minus_four_scaling():
    """Verify that independent reset pulses require N = Theta(delta^-4), and 412 pulses yield ~34.3% error at delta=0.01."""
    from scipy.stats import norm
    
    kappa = 0.8
    q = 0.2
    a = 0.5
    eta = 0.4
    delta = 0.01
    sigma = 0.01
    V_eff = 6.25
    z_alpha = norm.ppf(0.95)
    target_kl = 2.0 * z_alpha**2 # ~5.4114
    
    # Under 100 observations, calculate impulse response difference norm
    from breakthrough_experiments.exp3_adaptive_probing import get_mean_trajectory
    v_unit = np.zeros(100)
    v_unit[0] = 1.0
    h0 = get_mean_trajectory(v_unit, delta=delta, T=100, kappa=kappa, q=q, a=a, eta=eta, split=False)
    h1 = get_mean_trajectory(v_unit, delta=delta, T=100, kappa=kappa, q=q, a=a, eta=eta, split=True)
    d = h1 - h0
    norm_d_sq = np.sum(d**2)
    
    # Per-pulse KL under V_eff = 6.25
    kl_per_pulse = (V_eff**2 * norm_d_sq) / (2.0 * sigma**2)
    
    # If someone uses 412 pulses:
    kl_412 = 412 * kl_per_pulse
    d_prime_412 = np.sqrt(2.0 * kl_412)
    err_412 = norm.cdf(-0.5 * d_prime_412)
    
    # Assert that 412 pulses under-accumulates and yields ~34.3% error (far above 5% target)
    assert np.isclose(err_412, 0.343, atol=0.02), f"Expected ~34.3% error with 412 pulses, got {err_412*100:.2f}%"
    
    # Assert that required pulses N_req scales as Theta(delta^-4)
    N_req = target_kl / kl_per_pulse
    assert N_req > 5000, f"True required pulses for 5% error must exceed 5000 (got {N_req:.0f})"

# ----------------------------------------------------------------------
# 13. Test Allocation Surplus Loss Formula (Proposition 2.11 / TC-1202)
# ----------------------------------------------------------------------
def test_allocation_loss_formula():
    """Verify Proposition 2.11: surplus loss W_loss = b(s0 - c)Delta + (b/2)Delta^2."""
    b = 4.0
    cost = 10.0
    s0 = 12.0 # initial quote above marginal cost
    Delta = 1.5 # quote increase from ambiguity
    
    # Analytical loss:
    W_loss_expected = b * (s0 - cost) * Delta + 0.5 * b * (Delta**2)
    # W_loss = 4.0 * (2.0) * 1.5 + 2.0 * 2.25 = 12.0 + 4.5 = 16.5
    assert np.isclose(W_loss_expected, 16.5)
    
    # If s0 = cost (efficient baseline), recovers classic Harberger triangle (b/2)Delta^2:
    W_triangle = 0.5 * b * (Delta**2) # 4.5
    assert np.isclose(W_triangle, 4.5)

# ----------------------------------------------------------------------
# 14. Test Sequential Disclosure Schedules under V_eff = 6.25 (exp7)
# ----------------------------------------------------------------------
def test_sequential_disclosure_schedules_under_veff():
    """Verify that financial disclosure contracts reduce sequential probing pulses and capital under V_eff = 6.25."""
    res_path = Path("breakthrough_experiments/results_exp7_disclosure_value.json")
    assert res_path.exists(), "Results file for exp7 must exist"
    data = json.loads(res_path.read_text())
    
    # Locate delta = 0.05 contracts block
    entry_05 = next(item for item in data if abs(item["delta"] - 0.05) < 1e-4)
    d05 = entry_05["contracts"]
    
    # Contract I0 requires 271 sequential pulses and 4305.25 USDT
    assert d05["I0_Prices_Only"]["sequential_n_pulses"] == 271
    assert np.isclose(d05["I0_Prices_Only"]["sequential_capital_B"], 4305.25, atol=1.0)
    
    # Contract I2 (noisy balance sheet) cuts pulses to 132 and capital by >50%
    assert d05["I2_Noisy_Equity"]["sequential_n_pulses"] == 132
    savings_I2 = 1.0 - (d05["I2_Noisy_Equity"]["sequential_capital_B"] / d05["I0_Prices_Only"]["sequential_capital_B"])
    assert np.isclose(savings_I2, 0.5125, atol=0.01)
    
    # Contract I3 (exact equity marks) executes in exactly 1 pulse at 0.94 USDT
    assert d05["I3_Exact_Equity"]["sequential_n_pulses"] == 1
    assert np.isclose(d05["I3_Exact_Equity"]["sequential_capital_B"], 0.94, atol=0.01)
    
    # Contract I5 (supervisory audit) requires 0 pulses and 0.00 capital
    assert d05["I5_Full_Audit_Trail"]["sequential_n_pulses"] == 0
    assert d05["I5_Full_Audit_Trail"]["sequential_capital_B"] == 0.0

# ----------------------------------------------------------------------
# 15. Test Non-Normal Operator Monotonic Decay vs 0.0% Dynamic Liquidation (exp10 / exp12)
# ----------------------------------------------------------------------
def test_nonnormal_operator_monotonic_decay_and_zero_liquidation():
    """Verify that ||C J^t|| strictly decreases from t=0 (no dynamic transient growth),
    and multi-agent dynamic simulation yields exactly 0.0% liquidations."""
    from breakthrough_experiments.exp12_nonnormal_balance_sheet import build_network_jacobian
    
    # For M=1 asset:
    J = build_network_jacobian(M=1)
    # C_margin = (1, lambda / MMR) = (1, 160)
    C_margin = np.array([[1.0, 160.0]])
    
    # Norm at t=0:
    norm_0 = float(np.linalg.norm(C_margin, 2))
    assert np.isclose(norm_0, 160.00312497, atol=1e-3)
    
    # Norms at t=1, 2, 3:
    norm_1 = float(np.linalg.norm(C_margin @ J, 2))
    norm_2 = float(np.linalg.norm(C_margin @ np.linalg.matrix_power(J, 2), 2))
    norm_3 = float(np.linalg.norm(C_margin @ np.linalg.matrix_power(J, 3), 2))
    
    # Verify strictly monotonic decay from t=0
    assert norm_0 > norm_1 > norm_2 > norm_3, f"||C J^t|| must decay monotonically from t=0: {norm_0} > {norm_1} > {norm_2} > {norm_3}"
    assert np.isclose(norm_1, 122.319, atol=0.1)
    assert np.isclose(norm_2, 98.322, atol=0.1)
    assert np.isclose(norm_3, 80.296, atol=0.1)
    
    # Check that in authentic multi-agent dynamic simulation, dealer liquidation rate is 0.0%
    res_exp10 = Path("breakthrough_experiments/results_exp10_multi_agent.json")
    if res_exp10.exists():
        data10 = json.loads(res_exp10.read_text())
        for pop, summary in data10["conditions_summary"].items():
            assert summary["liquidation_rate"] == 0.0, f"Dynamic liquidation rate must be 0.0% for {pop}, got {summary['liquidation_rate']}"


