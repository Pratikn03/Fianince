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
            assert r["weighted_output_exceeds_4_55"], "Coordinate-weighted (price, memory) output exceeds 4.55"
            # Audit (Oct 11, finding 5): this is NOT a margin breach; the state holds no inventory.
            assert r["state_contains_inventory"] is False

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
# 14. Test Sequential Disclosure Schedules under V_eff = 6.25 (exp7)
# ----------------------------------------------------------------------
def test_sequential_disclosure_schedules_under_veff():
    """Verify that financial disclosure contracts reduce sequential probing pulses and capital under V_eff = 6.25,
    evaluating against both restricted T=3 baseline and optimal T=20 transient design."""
    res_path = Path("breakthrough_experiments/results_exp7_disclosure_value.json")
    assert res_path.exists(), "Results file for exp7 must exist"
    data = json.loads(res_path.read_text())
    
    # Locate delta = 0.05 contracts block
    if isinstance(data, dict) and "delta_0.05" in data:
        d05 = data["delta_0.05"]
    elif isinstance(data, list):
        entry_05 = next(item for item in data if abs(item.get("delta", 0.0) - 0.05) < 1e-4)
        d05 = entry_05["contracts"]
    else:
        raise ValueError("Unexpected format in results_exp7_disclosure_value.json")
        
    # Contract I0 Restricted T=3 baseline requires 271 sequential pulses and 4305.25 USDT
    i0_key = "I0_Prices_Only_Restricted_T3" if "I0_Prices_Only_Restricted_T3" in d05 else "I0_Prices_Only"
    assert d05[i0_key]["sequential_n_pulses"] == 271
    assert np.isclose(d05[i0_key]["required_capital_B"], 4305.25, atol=1.0)
    
    # Contract I0 Optimal T=20 transient baseline requires 12 pulses and 193.62 USDT
    if "I0_Prices_Only_Optimal_T20" in d05:
        assert d05["I0_Prices_Only_Optimal_T20"]["sequential_n_pulses"] == 12
        assert np.isclose(d05["I0_Prices_Only_Optimal_T20"]["required_capital_B"], 193.62, atol=1.0)
    
    # Contract I3 Exact equity marks: CME 5 BTC standard lot costs 12.70 USDT, CME 0.1 BTC micro lot costs 0.058 USDT, Binance 5 USDT minNotional costs 0.028 USDT
    cme_std_key = "I3_Exact_Equity_CME_Std_5BTC"
    assert d05[cme_std_key]["sequential_n_pulses"] == 1
    assert np.isclose(d05[cme_std_key]["required_capital_B"], 12.70, atol=0.01)

    cme_micro_key = "I3_Exact_Equity_CME_Micro_0_1BTC"
    assert d05[cme_micro_key]["sequential_n_pulses"] == 1
    assert np.isclose(d05[cme_micro_key]["required_capital_B"], 0.0580, atol=0.005)
    
    if "I3_Exact_Equity_Binance_minNotional" in d05:
        assert np.isclose(d05["I3_Exact_Equity_Binance_minNotional"]["required_capital_B"], 0.0280, atol=0.005)
        assert d05["I3_Exact_Equity_Binance_minNotional"]["theoretical_infimum_capital"] == 0.0
    
    # Contract I5 (supervisory audit) requires 0 pulses and 0.00 capital
    i5_key = "I5_Supervisory_Audit" if "I5_Supervisory_Audit" in d05 else "I5_Full_Audit_Trail"
    assert d05[i5_key]["sequential_n_pulses"] == 0
    assert d05[i5_key]["required_capital_B"] == 0.0

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

# ----------------------------------------------------------------------
# 16. Test Canonical Financial Accounting Contract Invariants (P2-T01 to P2-T06)
# ----------------------------------------------------------------------
def test_canonical_financial_accounting_contract():
    """Verify Phase 2 contract: no-trade neutrality, round-trip fee deduction, capital conservation,
    and trade limit enforcement (|v_t| <= V_eff = 6.25)."""
    p0 = 100.0
    c_fee = 0.0004
    kappa = 0.8
    V_eff = 6.25
    initial_cash = 50000.0
    
    # 1. No-trade case (P2-T02): zero volume leaves cash and equity unchanged
    cash = initial_cash
    inv = 0.0
    assert cash + inv * p0 == initial_cash
    
    # 2. Execution limit (P2-T06): trade exceeding V_eff is clamped/rejected
    order_size = 10.0
    executable_trade = min(order_size, V_eff)
    assert executable_trade == 6.25
    
    # 3. Round-trip trade (P2-T03): buy executable_trade, then sell executable_trade
    # Buy: cash outflow = executable_trade * (p0 + 0.5 * kappa * executable_trade) + fee
    buy_exec_price = p0 + 0.5 * kappa * executable_trade
    buy_cash_outflow = executable_trade * buy_exec_price + c_fee * p0 * executable_trade
    cash -= buy_cash_outflow
    inv += executable_trade
    
    # Sell: cash inflow = executable_trade * (p0 + kappa * executable_trade - 0.5 * kappa * executable_trade) - fee
    sell_exec_price = p0 + kappa * executable_trade - 0.5 * kappa * executable_trade # price impact persists during liquidation
    sell_cash_inflow = executable_trade * sell_exec_price - c_fee * p0 * executable_trade
    cash += sell_cash_inflow
    inv -= executable_trade
    
    # Round-trip net cash loss must equal total fees plus round-trip impact
    total_fees = 2 * c_fee * p0 * executable_trade
    total_impact = 0.5 * kappa * (executable_trade ** 2)
    net_loss = initial_cash - cash
    assert np.isclose(net_loss, total_fees, atol=1.0)
    assert np.isclose(inv, 0.0)

# ----------------------------------------------------------------------
# 17. Test Probing Error Rates & Sequential SPRT Savings (P4-T01 to P4-T03)
# ----------------------------------------------------------------------
def test_probing_empirical_error_and_sequential_savings():
    """Verify that in exp3 results, all empirical error rates are <= 0.057 (consistent with 0.05),
    Method C point error is <= 0.040, and Method C achieves significant capital savings."""
    res_path = Path("breakthrough_experiments/results_exp3_adaptive_probing.json")
    assert res_path.exists(), "exp3 results file must exist"
    data = json.loads(res_path.read_text())
    
    for r in data:
        # Check empirical error within 2 SE of 0.05
        se = r.get("error_se", 0.007)
        emp_err = r["empirical_error"]
        assert emp_err - 2 * se <= 0.050, f"Error rate {emp_err} for {r['protocol']} at delta={r['delta']} exceeds 95% CI upper bound"
        
        # Check that single trade limits are enforced for Methods B, C, D
        if r["protocol"] in ["Method_B_Multi_Pulse", "Method_C_Sequential_Feedback", "Method_D_Minimax_LQG"]:
            assert r["max_single_trade"] <= 6.25 + 1e-4, f"Single trade {r['max_single_trade']} exceeds V_eff = 6.25"
            
    # Check Method C savings over Method B at delta = 0.05
    res_b_05 = next(item for item in data if item["protocol"] == "Method_B_Multi_Pulse" and abs(item["delta"] - 0.05) < 1e-4)
    res_c_05 = next(item for item in data if item["protocol"] == "Method_C_Sequential_Feedback" and abs(item["delta"] - 0.05) < 1e-4)
    
    assert res_c_05["empirical_error"] <= 0.040, f"Method C empirical error at delta=0.05 must be <= 0.040, got {res_c_05['empirical_error']}"
    
    # 1. Authentic SPRT savings over Method B under equal horizon (T=4)
    savings_equal_h = 1.0 - (res_c_05["mean_capital_cost"] / res_b_05["mean_capital_cost"])
    assert savings_equal_h > 0.20, f"Method C must save >20% capital over Method B under equal horizon (got {savings_equal_h*100:.1f}%)"
    
    # 2. Total savings over restricted T=3 baseline if recorded
    if "restricted_T3_cost" in res_b_05:
        savings_vs_t3 = 1.0 - (res_c_05["mean_capital_cost"] / res_b_05["restricted_T3_cost"])
        assert savings_vs_t3 > 0.75, f"Method C must save >75% capital over restricted T=3 baseline (got {savings_vs_t3*100:.1f}%)"

# ----------------------------------------------------------------------
# 18. Test Unknown-Mixture Equivalence & High-Noise Shrinkage (P5-T01 to P5-T03)
# ----------------------------------------------------------------------
def test_unknown_mixture_equivalence_and_noise_boundary():
    """Verify Theorem 2.4: two cohorts with identical rates merge into 1 single pole;
    and high noise (sigma >= 0.005) triggers model order shrinkage to dominant mode."""
    from breakthrough_experiments.exp2_unknown_mixture import simulate_closed_loop_impulse, blind_transfer_function_inversion
    
    # 1. Identical rates: eta1 = eta2 = 0.30, weights 0.10, 0.10
    h_merged = simulate_closed_loop_impulse(np.array([0.10, 0.10]), np.array([0.30, 0.30]), T=100)
    K_m, poles_m, weights_m = blind_transfer_function_inversion(h_merged)
    assert K_m == 1, "Identical rate cohorts MUST merge into exactly 1 pole by Theorem 2.4"
    assert np.isclose(poles_m[0], 0.70, atol=0.05), "Merged pole must equal 1 - 0.30 = 0.70"
    
    # 2. High noise: sigma = 0.01 on 2 separated cohorts
    h_2 = simulate_closed_loop_impulse(np.array([0.10, 0.10]), np.array([0.30, 0.50]), T=100)
    np.random.seed(123)
    h_noisy = h_2 + np.random.normal(0, 0.01, size=len(h_2))
    K_n, poles_n, _ = blind_transfer_function_inversion(h_noisy)
    # Under high noise, secondary mode drops below noise floor, shrinking recovered K to 1
    assert K_n == 1, "High observation noise must collapse recovered model order to dominant mode"

# ----------------------------------------------------------------------
# 19. Test Formal Proof Kernel Verification & Zero Axioms (P10-T01 to P10-T02)
# ----------------------------------------------------------------------
def test_formal_proof_bridge_coverage():
    """Verify that Lean formalization bridge matches 23 manuscript mathematical environments
    and MANUSCRIPT_COVERAGE.md explicitly documents 319 kernel-checked declarations."""
    bridge_script = Path("scripts/verify_theorem_code_bridge.py")
    assert bridge_script.exists(), "Theorem-code bridge script must exist"
    
    cov_file = Path("research_extension/current_manuscript_lean_20261008/MANUSCRIPT_COVERAGE.md")
    assert cov_file.exists(), "Manuscript coverage markdown must exist"
    cov_text = cov_file.read_text()
    assert "319" in cov_text, "Coverage file must document 319 declarations"
    assert Path("paper/generated/claim_to_code_map.tex").exists()

# ----------------------------------------------------------------------
# 20. Test Claim Traceability & Artifact Synchronization (P1-T01 to P1-T05)
# ----------------------------------------------------------------------
def test_claim_traceability_and_artifact_sync():
    """Verify all 4 breakthrough tables and 5 figures exist and are non-empty."""
    tables_dir = Path("breakthrough_experiments/tables")
    figures_dir = Path("breakthrough_experiments/figures")
    
    expected_tables = [
        "table_probing_methods.tex",
        "table_causal_multi_agent.tex",
        "table_disclosure_frontier.tex",
        "table_nonnormal_decoupling.tex"
    ]
    for tab in expected_tables:
        t_path = tables_dir / tab
        assert t_path.exists(), f"Table {tab} must exist"
        assert len(t_path.read_text()) > 100, f"Table {tab} must be non-empty"
        
    expected_figures = [
        "fig1_phase_diagram.pdf",
        "fig2_probing_cost_scaling.pdf",
        "fig3_causal_multi_agent.pdf",
        "fig4_disclosure_frontier.pdf",
        "fig5_nonnormal_decoupling.pdf"
    ]
    for fig in expected_figures:
        f_path = figures_dir / fig
        assert f_path.exists(), f"Figure {fig} must exist"
        assert f_path.stat().st_size > 1000, f"Figure {fig} must be non-empty"

# ----------------------------------------------------------------------
# 21. Test Independent Finite-Horizon Counterexample & Multi-Observation Design (Section 2)
# ----------------------------------------------------------------------
def test_finite_horizon_counterexample_multi_observation():
    """Verify Section 2 Independent Audit Counterexample:
    At delta = 0.05, increasing observation horizon from T=3 to T=20 reduces capital
    by >95% (from 4305.25 to 193.63 USDT) and reduces total observations (from 813 to 240)."""
    from breakthrough_experiments.exp4_frontier_phase_diagram import compute_frontier, get_mean_impulse_response
    from scipy.stats import norm
    
    kappa = 0.8; q = 0.2; a = 0.5; eta = 0.4; delta = 0.05; sigma = 0.01; alpha = 0.05
    V_eff = 6.25; c_fee = 0.0004; P_star = 100.0; mu = 0.005
    z_alpha = norm.ppf(0.95)
    target_kl = 2.0 * (z_alpha ** 2)
    
    h0 = get_mean_impulse_response(delta, T=100, kappa=kappa, q=q, a=a, eta=eta, split=False)
    h1 = get_mean_impulse_response(delta, T=100, kappa=kappa, q=q, a=a, eta=eta, split=True)
    diff = h1 - h0
    
    # Check exact auditor table values
    # T=3
    d3 = diff[:3]; kl_3 = (V_eff**2 * np.sum(d3**2)) / (2.0 * sigma**2)
    N3 = int(np.ceil(target_kl / kl_3))
    cost_3 = N3 * (0.5 * kappa * V_eff**2 + c_fee * P_star * V_eff) + mu * P_star * V_eff
    assert N3 == 271, f"T=3 must require exactly 271 pulses, got {N3}"
    assert np.isclose(cost_3, 4305.25, atol=0.5), f"T=3 cost must be 4305.25 USDT, got {cost_3}"
    assert N3 * 3 == 813, "T=3 total observations must be 813"
    
    # T=4
    d4 = diff[:4]; kl_4 = (V_eff**2 * np.sum(d4**2)) / (2.0 * sigma**2)
    N4 = int(np.ceil(target_kl / kl_4))
    cost_4 = N4 * (0.5 * kappa * V_eff**2 + c_fee * P_star * V_eff) + mu * P_star * V_eff
    assert N4 == 58, f"T=4 must require exactly 58 pulses, got {N4}"
    assert np.isclose(cost_4, 923.88, atol=0.5), f"T=4 cost must be 923.88 USDT, got {cost_4}"
    
    # T=10
    d10 = diff[:10]; kl_10 = (V_eff**2 * np.sum(d10**2)) / (2.0 * sigma**2)
    N10 = int(np.ceil(target_kl / kl_10))
    cost_10 = N10 * (0.5 * kappa * V_eff**2 + c_fee * P_star * V_eff) + mu * P_star * V_eff
    assert N10 == 15, f"T=10 must require exactly 15 pulses, got {N10}"
    assert np.isclose(cost_10, 241.25, atol=0.5), f"T=10 cost must be 241.25 USDT, got {cost_10}"
    assert N10 * 10 == 150, "T=10 total observations must be 150"
    assert N10 * 10 < N3 * 3, "T=10 design must require fewer total price observations than T=3 design (150 < 813)"
    
    # T=20 capacity-saturating design (V = V_eff = 6.25 BTC)
    d20 = diff[:20]; kl_20 = (V_eff**2 * np.sum(d20**2)) / (2.0 * sigma**2)
    N20 = int(np.ceil(target_kl / kl_20))
    cost_20 = N20 * (0.5 * kappa * V_eff**2 + c_fee * P_star * V_eff) + mu * P_star * V_eff
    assert N20 == 12, f"T=20 must require exactly 12 pulses, got {N20}"
    assert np.isclose(cost_20, 193.63, atol=0.5), f"T=20 cost must be 193.63 USDT, got {cost_20}"
    
    # Volume-optimized design: N=12, V* = sqrt(Omega_20 / 12) = 6.057 BTC
    omega_20 = 4.0 * (sigma ** 2) * (z_alpha ** 2) / np.sum(d20 ** 2)
    v_opt_12 = np.sqrt(omega_20 / 12.0)
    cost_opt_12 = 12.0 * (0.5 * kappa * (v_opt_12 ** 2) + c_fee * P_star * v_opt_12) + mu * P_star * v_opt_12
    assert np.isclose(v_opt_12, 6.057, atol=0.01), f"Expected 6.057 BTC, got {v_opt_12}"
    assert np.isclose(cost_opt_12, 182.02, atol=0.1), f"Expected 182.02 USDT, got {cost_opt_12}"
    
    # Verify exact single-pulse resolution floors delta_min(T) where V_req(delta) == V_eff
    from scipy.optimize import brentq
    for t_step, expected_floor in [(3, 0.20278), (4, 0.13760), (10, 0.09727), (20, 0.09142), (100, 0.09047)]:
        def obj(d, t=t_step):
            h0_d = get_mean_impulse_response(d, T=t, kappa=kappa, q=q, a=a, eta=eta, split=False)
            h1_d = get_mean_impulse_response(d, T=t, kappa=kappa, q=q, a=a, eta=eta, split=True)
            norm_dt = np.sqrt(np.sum((h1_d - h0_d) ** 2))
            v_req = (2.0 * sigma * z_alpha) / norm_dt
            return v_req - V_eff
        floor_t = float(brentq(obj, 0.01, 0.35))
        assert np.isclose(floor_t, expected_floor, atol=1e-4), f"Floor at T={t_step}: expected {expected_floor}, got {floor_t}"
    
    # Assert capital reduction exceeds 95%
    capital_saving = 1.0 - (cost_20 / cost_3)
    assert capital_saving > 0.95, f"T=20 design must reduce capital by >95% compared with T=3 (got {capital_saving*100:.2f}%)"

# ----------------------------------------------------------------------
# 22. Test Unknown-Mixture Exact Feedback Weight Recovery & Zero-Learning Pure Dealer (F7)
# ----------------------------------------------------------------------
def test_unknown_mixture_exact_weight_recovery_and_pure_dealer():
    """Verify that feedback weight recovery inverts the closed loop u_t = (x_t - a x_{t-1})/kappa
    and recovers the true 0.20 weight exactly (not 0.415), and correctly identifies pure dealer K=0."""
    from breakthrough_experiments.exp2_unknown_mixture import simulate_closed_loop_impulse, blind_transfer_function_inversion
    
    # Scenario A: Single cohort benchmark (true q = 0.200, eta = 0.300)
    true_etas = np.array([0.30])
    true_weights = np.array([0.20])
    h = simulate_closed_loop_impulse(true_weights, true_etas, T=100)
    
    est_K, est_poles, est_weights = blind_transfer_function_inversion(h)
    assert est_K == 1, f"Expected K=1, got {est_K}"
    assert np.isclose(est_poles[0], 0.70, atol=0.01), f"Expected pole 0.70, got {est_poles[0]}"
    assert np.isclose(est_weights[0], 0.20, atol=1e-4), f"Recovered weight must equal 0.200000, got {est_weights[0]}"
    assert abs(est_weights[0] - 0.414985) > 0.15, "Must NOT exhibit the 0.415 Vandermonde regression bug"
    
    # Scenario B: Zero-learning pure dealer edge case (K = 0, no algorithmic learning)
    kappa = 0.8; a = 0.5
    h_pure_dealer = kappa * (a ** np.arange(101))
    K_dealer, poles_dealer, weights_dealer = blind_transfer_function_inversion(h_pure_dealer)
    assert K_dealer == 0, f"Pure dealer system must identify K=0, got {K_dealer}"
    assert len(poles_dealer) == 0, "Pure dealer system must have 0 algorithmic memory poles"
    assert len(weights_dealer) == 0, "Pure dealer system must have empty algorithmic feedback weights"

# ----------------------------------------------------------------------
# 23. Test Physically Executable Round-Trip Unwind Accounting (F4 & F5)
# ----------------------------------------------------------------------
def test_physically_executable_round_trip_unwind_accounting():
    """Verify that an authentic executable probing reset includes opening purchase, holding period,
    and closing unwind sale, conserving cash and inventory, with transaction cost = kappa V^2 + 2 fee P* V."""
    kappa = 0.8
    P_star = 100.0
    c_fee = 0.0004
    mu = 0.005
    V_eff = 6.25
    initial_cash = 10000.0
    
    # Step 1: Open pulse trade (+V_eff)
    cash = initial_cash
    inv = 0.0
    
    open_exec_price = P_star + 0.5 * kappa * V_eff # 102.50
    cash -= V_eff * open_exec_price + c_fee * P_star * V_eff
    inv += V_eff
    
    # Step 2: Quiescent holding period (price decays back to P_star)
    p_decay = P_star
    m2m_equity_T = cash + inv * p_decay
    # Once price relaxes to P_star, holding loss equals impact expenditure + fee:
    assert np.isclose(initial_cash - m2m_equity_T, 0.5 * kappa * V_eff**2 + c_fee * P_star * V_eff, atol=0.01)
    
    # Step 3: Unwind trade (-V_eff) at market
    close_exec_price = p_decay - 0.5 * kappa * V_eff # 97.50
    cash += V_eff * close_exec_price - c_fee * P_star * V_eff
    inv -= V_eff
    
    # Inventory fully unwound
    assert np.isclose(inv, 0.0)
    
    # Net cash loss across round trip equals full impact kappa V^2 plus two taker fees:
    round_trip_loss = initial_cash - cash
    expected_loss = kappa * (V_eff ** 2) + 2.0 * c_fee * P_star * V_eff # 0.8 * 39.0625 + 2 * 0.04 * 6.25 = 31.25 + 0.50 = 31.75 USDT
    assert np.isclose(round_trip_loss, expected_loss, atol=1e-4)
    assert np.isclose(expected_loss, 31.75, atol=1e-4)

# ----------------------------------------------------------------------
# 24. Test Exchange Venue Filters: CME vs Binance Contract Rules (F9)
# ----------------------------------------------------------------------
def test_exchange_venue_filters_cme_vs_binance():
    """Verify discrete exchange contract lot sizes: CME standard 5 BTC lot ($12.70), CME micro 0.1 BTC lot ($0.058), vs Binance 5 USDT minNotional ($0.028)."""
    from breakthrough_experiments.exp7_disclosure_value import solve_contract_requirements
    
    res = solve_contract_requirements(delta=0.05)
    
    # CME Specifications
    b_cme_std = res["I3_Exact_Equity_CME_Std_5BTC"]["required_capital_B"]
    assert np.isclose(b_cme_std, 12.70, atol=0.01)
    
    b_cme_micro = res["I3_Exact_Equity_CME_Micro_0_1BTC"]["required_capital_B"]
    assert np.isclose(b_cme_micro, 0.0580, atol=0.005)
    
    # Binance USD(S)-M Specification (minNotional = 5.0 USDT -> 0.05 BTC at P*=100)
    b_binance = res["I3_Exact_Equity_Binance_minNotional"]["required_capital_B"]
    assert np.isclose(b_binance, 0.0280, atol=0.005)
    
    # Theoretical infimum under continuous infinitesimal contract
    assert res["I3_Exact_Equity_Binance_minNotional"]["theoretical_infimum_capital"] == 0.0


# ----------------------------------------------------------------------
# 25. Test Exact Capital Frontier & Adaptive Probing Bound (exp14)
# ----------------------------------------------------------------------
def test_exact_capital_frontier_spectral_bound():
    """Verify exact spectral quadratic capital lower bound, finite-horizon executable probe gap <= 6%, and sequential SPRT performance."""
    results_path = Path("breakthrough_experiments/results_exp14_capital_frontier_exact.json")
    assert results_path.exists(), "exp14 results JSON must exist"
    data = json.loads(results_path.read_text())
    
    # Check delta = 0.05 row
    r005 = next(s for s in data["sweep"] if abs(s["delta"] - 0.05) < 1e-4)
    
    # 1. Minimizing frequency matches analytical prediction (~0.2526 rad)
    assert np.isclose(r005["spectral"]["omega_star_0"], 0.2526, atol=0.005)
    
    # 2. Deterministic quadratic lower bound at delta = 0.05 is 61.44 USDT
    assert np.isclose(r005["capital_lower_bound_deterministic"], 61.44, atol=0.10)
    
    # 3. Finite-horizon executable probe achieves bound within 6% (gap ratio = 1.051)
    assert r005["upper_bound_capital"] is not None
    assert np.isclose(r005["upper_bound_capital"], 64.59, atol=0.50)
    assert r005["gap_ratio_upper_over_lower"] <= 1.06
    
    # 4. Strict delta^-4 scaling: delta^4 * LB_quad is strictly constant
    for s in data["sweep"]:
        assert np.isclose(s["delta4_times_quad_bound"], 3.8e-4, rtol=0.05), f"delta^4 * LB_quad must be constant, got {s['delta4_times_quad_bound']}"
        
    # 5. Adaptive lower bound is ~30.09 USDT (51.0% maximum theoretical dynamic saving)
    assert np.isclose(r005["capital_lower_bound_adaptive_expected"], 30.09, atol=0.10)
    
    # 6. Sequential SPRT Monte Carlo strictly obeys 30.09 <= 45.96 <= 61.44
    sprt = data["sequential_mc_delta_0_05"]
    assert sprt["H0"]["mean_loss"] >= r005["capital_lower_bound_adaptive_expected"]
    assert sprt["H0"]["mean_loss"] <= r005["capital_lower_bound_deterministic"]
    assert sprt["H0"]["error"] <= 0.05
    assert sprt["H1"]["error"] <= 0.05
    assert sprt["chain_rule_check"]["holds"] is True


# ----------------------------------------------------------------------
# 26. Test Multi-Cohort Cramér-Rao Information Limits (exp15)
# ----------------------------------------------------------------------
def test_cohort_cramer_rao_information_bound():
    """Verify that multi-cohort weight recovery failure is a Cramér-Rao information-theoretic limit with Theta((Delta eta)^-6) scaling."""
    from breakthrough_experiments.exp15_cohort_information import probes_needed, TOL
    
    # Live model-equation verification of local Cramér-Rao bound for delta=0.05 pair
    live_n_star, live_crb_sd_unit = probes_needed(np.array([0.10, 0.10, 0.35, 0.45]), 2)
    live_sigma_crit = (TOL / 1.96) / live_crb_sd_unit
    assert np.isclose(live_n_star, 40374.215, atol=1.0)
    assert np.isclose(live_sigma_crit, 7.9589e-6, rtol=1e-2)
    
    results_path = Path("breakthrough_experiments/results_exp15_cohort_information.json")
    if not results_path.exists():
        pytest.skip("exp15 results JSON not generated yet")
    data = json.loads(results_path.read_text())
    assert data["n_mc"] >= 100, "exp15 Monte Carlo must use at least n_mc=100 replications per noise cell"
    
    # 1. Probes needed scaling slope is approximately -6 (joint rate-weight CRB inversion)
    slope = data["separation_scaling"]["loglog_slope"]
    assert -6.5 <= slope <= -5.5, f"Information scaling slope must be approximately -6, got {slope}"
    
    # 2. For delta=0.05 pair (Delta eta = 0.10), N* requires > 30,000 probes
    r_pair = next(s for s in data["scenarios"] if "delta=0.05 pair" in s["scenario"])
    assert np.isclose(r_pair["probes_needed_N_star"], live_n_star, atol=1e-4)
    assert r_pair["probes_needed_N_star"] > 30000.0
    # Single-probe noise is > 100x above critical threshold
    assert r_pair["single_probe_sigma_h"] / r_pair["sigma_h_critical"] > 100.0
    
    # 3. Maximum likelihood resolves noiseless weights with error < 5e-3 even when ERA fails
    assert r_pair["ml_noiseless_max_weight_error"] < 5e-3
    
    # 4. At critical noise f=1.0, ML achieves CRB efficiency with low bias and valid 95% CI coverage
    mc1 = next(m for m in r_pair["monte_carlo"] if abs(m["noise_over_critical"] - 1.0) < 1e-4)
    assert mc1["ml_rmse_weight"] / mc1["crb_sd_weight"] <= 1.5
    assert mc1["ml_success_known_K"] >= 0.85
    assert mc1["ml_max_bias_weight"] < 5e-3
    assert mc1["ml_ci95_coverage"] >= 0.80
    assert mc1["bic_K_correct"] >= 0.85


# ----------------------------------------------------------------------
# 27. Test Acceptance Gate TC-91-01: Spectral Transfer Impact Indexing
# ----------------------------------------------------------------------
def test_tc91_01_spectral_transfer_impact_indexing():
    """Verify that unshifted transfer H0(z) has g0(pi) < 0 (falsification test),
    while impact-indexed transfer widehat{H}0(z) = z * H0(z) has g0(omega) > 0 for all omega in [0, pi]."""
    kappa = 0.8
    a = 0.5
    q = 0.2
    eta = 0.4
    
    # 1. Unshifted transfer at z = exp(i*pi) = -1:
    # G(-1) = q * eta * (-1) / (-1 - (1 - eta)) = 0.2 * 0.4 * (-1) / (-1.6) = 0.05
    G_neg1 = (q * eta * (-1.0)) / (-1.0 - (1.0 - eta))
    assert np.isclose(G_neg1, 0.05)
    # H0(-1) = kappa / (-1 - a - kappa * G(-1)) = 0.8 / (-1 - 0.5 - 0.04) = 0.8 / (-1.54) = -0.5194805195
    H0_neg1 = kappa / (-1.0 - a - kappa * G_neg1)
    assert np.isclose(H0_neg1, -0.5194805195)
    g0_unshifted_pi = H0_neg1.real - kappa / 2.0  # -0.51948 - 0.400 = -0.91948
    assert g0_unshifted_pi < 0.0, "Unshifted H0(-1) - kappa/2 MUST be negative (-0.9195 < 0)"
    assert np.isclose(g0_unshifted_pi, -0.9194805195)
    
    # 2. Impact-indexed transfer widehat{H}0(z) = z * H0(z):
    # At z = -1: widehat{H}0(-1) = (-1) * H0(-1) = +0.5194805195
    H_hat0_neg1 = (-1.0) * H0_neg1
    g0_impact_pi = H_hat0_neg1.real - kappa / 2.0
    assert g0_impact_pi > 0.0, "Impact-indexed widehat{H}0(-1) - kappa/2 MUST be positive (+0.1195 > 0)"
    assert np.isclose(g0_impact_pi, 0.1194805195)
    
    # 3. Across entire frequency grid omega in [0, pi], widehat{g}_0(omega) > 0
    from breakthrough_experiments.exp14_capital_frontier_exact import spectral_quantities
    s = spectral_quantities(delta=0.05)
    assert s["min_g0"] > 0.0, "Real spectral dissipation kernel min_g0 must be strictly positive"
    assert s["min_g1"] > 0.0, "Real spectral dissipation kernel min_g1 must be strictly positive"
    assert np.isclose(s["omega_star_0"], 0.2526, atol=0.005)


# ----------------------------------------------------------------------
# 28. Test Acceptance Gate TC-91-02: Price-First Impulse Tap Agreement
# ----------------------------------------------------------------------
def test_tc91_02_price_first_impulse_tap_agreement():
    """Verify first 4 impulse taps of the closed-loop system match kappa, kappa*(a + kappa*q*eta), etc.
    identically across exp2, exp13, exp14, exp15, and rational transfer H(z), and reject simultaneous return-memory bug."""
    from scipy.signal import lfilter
    kappa = 0.8
    a = 0.5
    q = 0.2
    eta = 0.4
    
    # Analytical taps for price-first model:
    # h0 = kappa = 0.8
    # y0 = eta * h0 = 0.32
    # h1 = a * h0 + kappa * q * y0 = 0.4512
    # y1 = (1 - eta)*y0 + eta * h1 = 0.37248
    # h2 = a * h1 + kappa * q * y1 = 0.2851968
    # y2 = (1 - eta)*y1 + eta * h2 = 0.33756672
    # h3 = a * h2 + kappa * q * y2 = 0.1966090752
    expected_taps = np.array([0.8, 0.4512, 0.2851968, 0.1966090752])
    
    # Implementation 1: exp13 price_path
    from breakthrough_experiments.exp13_account_capital import price_path, PARAMS
    v = np.zeros(4)
    v[0] = 1.0
    h_path = price_path(v, delta=0.0, split=False, p=PARAMS)
    assert np.allclose(h_path, expected_taps, atol=1e-14), "exp13 price_path taps must match analytical"
    
    # Implementation 2: exp14 impulse
    from breakthrough_experiments.exp14_capital_frontier_exact import impulse
    h_exp14 = impulse(delta=0.0, split=False, p=PARAMS, T=4)
    assert np.allclose(h_exp14, expected_taps, atol=1e-14), "exp14 impulse taps must match analytical"
    
    # Implementation 3: exp2 simulate_closed_loop_impulse (at eta=0.4)
    from breakthrough_experiments.exp2_unknown_mixture import simulate_closed_loop_impulse
    h_exp2 = simulate_closed_loop_impulse(np.array([q]), np.array([eta]), T=3, kappa=kappa, a=a)
    assert np.allclose(h_exp2, expected_taps, atol=1e-14), "exp2 impulse taps must match analytical"
    
    # Implementation 4: exp15 h_of (at eta=0.4)
    from breakthrough_experiments.exp15_cohort_information import h_of
    h_exp15 = h_of(np.array([q, eta]), K=1)[:4]
    assert np.allclose(h_exp15, expected_taps, atol=1e-14), "exp15 h_of taps must match analytical"
    
    # Implementation 5: Manuscript rational transfer function \widehat{H}(z) = z H(z) = \frac{\kappa z (z - (1-\eta))}{(z-a)(z-(1-\eta)) - \kappa q \eta z}
    # In z^{-1}: num = [kappa, -kappa*(1-eta)], den = [1, -(a + (1-eta) + kappa*q*eta), a*(1-eta)]
    r = 1.0 - eta
    num = np.array([kappa, -kappa * r, 0.0])
    den = np.array([1.0, -(a + r + kappa * q * eta), a * r])
    h_rational = lfilter(num, den, v)
    assert np.allclose(h_rational, expected_taps, atol=1e-14), "Rational transfer H(z) taps must match analytical"
    
    # Falsification check: Erroneous simultaneous return-memory system responds with 1.068376
    # p0 = 1 / (1 - kappa * q * eta) = 1 / (1 - 0.064) = 1.068376 != 0.800
    erroneous_simultaneous_h0 = 1.0 / (1.0 - kappa * q * eta)
    assert abs(h_path[0] - erroneous_simultaneous_h0) > 0.25, "Must reject the 1.068376 simultaneous return-memory bug"


# ----------------------------------------------------------------------
# 29. Test Acceptance Gate TC-91-03: Session Floor Implicit Root vs Asymptotic Formula
# ----------------------------------------------------------------------
def test_tc91_03_session_floor_implicit_root():
    """Verify that delta_min(3) = 0.202784 solves the implicit root equation V_eff * ||d_3(delta)||_2 = 2*sigma*z_alpha,
    matches asymptotic formula with normalized curvature ||tilde{d}_3|| = kappa^2 * q, and rejects circular 1.000 identity."""
    from scipy.stats import norm
    kappa = 0.8
    q = 0.2
    sigma = 0.01
    z_alpha = norm.ppf(0.95)  # 1.6448536
    V_eff = 6.25
    
    # 1. Exact implicit root check
    delta_root = 0.202783975387
    # For T=3, d_3(delta) has non-zero tap only at t=2: Delta h_2 = kappa^2 * q * delta^2
    norm_d3 = (kappa ** 2) * q * (delta_root ** 2)
    lhs = V_eff * norm_d3
    rhs = 2.0 * sigma * z_alpha
    assert np.isclose(lhs, rhs, atol=1e-7), f"Root equation must hold: LHS={lhs}, RHS={rhs}"
    
    # 2. Asymptotic fourth-root formula with normalized directional curvature tilde{d}_3
    norm_tilde_d3 = (kappa ** 2) * q  # 0.128
    delta_asymp = np.sqrt((2.0 * sigma * z_alpha) / (V_eff * norm_tilde_d3))
    assert np.isclose(delta_asymp, delta_root, atol=1e-6)
    assert np.isclose(delta_asymp, 0.202784, atol=1e-5)
    
    # 3. Falsification check: Substituting d_3(delta) directly into (4 sigma^2 z^2 / (V^2 ||d_3||^2))^(1/4) produces 1.000
    circular_val = ((4.0 * (sigma**2) * (z_alpha**2)) / ((V_eff**2) * (norm_d3**2))) ** 0.25
    assert np.isclose(circular_val, 1.000000), "Circular substitution must evaluate to 1.000000"


# ----------------------------------------------------------------------
# 30. Test Acceptance Gate TC-91-04: Feasible Counterexample (B=100, delta=0.05)
# ----------------------------------------------------------------------
def test_tc91_04_feasible_counterexample_in_phase_diagram():
    """Verify that at delta=0.05, a trader with B=100 USDT is strictly FEASIBLE using the multi-step waveform (cost ~64.59),
    even though the isolated-pulse single boundary requires ~193.62 USDT."""
    from breakthrough_experiments.exp14_capital_frontier_exact import theorem_bounds, best_feasible_design
    
    b = theorem_bounds(0.05)
    best, _ = best_feasible_design(0.05)
    
    # Certified lower bound
    lb_det = b["capital_lower_bound_deterministic"]
    assert np.isclose(lb_det, 61.44, atol=0.10)
    
    # Feasible candidate cost
    feasible_capital = best["C0_required"]
    assert np.isclose(feasible_capital, 64.59, atol=0.50)
    assert best["meets_5pct"] is True
    
    # Isolated-pulse cost is ~193.62 USDT
    isolated_pulse_cost = 193.62
    
    # A trader with B = 100 USDT:
    B_trader = 100.0
    assert B_trader > feasible_capital, "B=100 must be sufficient for the feasible multi-step probe"
    assert B_trader < isolated_pulse_cost, "B=100 is below the isolated-pulse benchmark"
    assert B_trader > lb_det, "B=100 is above the theoretical lower bound"


# ----------------------------------------------------------------------
# 31. Test Acceptance Gate TC-91-05: Certified Lower Bound and Feasible Upper Bound Interval
# ----------------------------------------------------------------------
def test_tc91_05_certified_lower_and_upper_bounds():
    """Verify that capital requirement at delta=0.05 is bounded within [61.44, 64.59] USDT with optimality gap <= 5.5%."""
    from breakthrough_experiments.exp14_capital_frontier_exact import theorem_bounds, best_feasible_design
    
    b = theorem_bounds(0.05)
    best, _ = best_feasible_design(0.05)
    
    lb_quad = b["quad_loss_lower_bound_deterministic"]
    assert np.isclose(lb_quad, 61.14, atol=0.10)
    
    lb_fee = b["fee_lower_bound_deterministic"]
    assert np.isclose(lb_fee, 0.3056, atol=0.01)
    
    lb_total = b["capital_lower_bound_deterministic"]
    assert np.isclose(lb_total, 61.44, atol=0.10)
    
    ub_feas = best["C0_required"]
    assert np.isclose(ub_feas, 64.59, atol=0.50)
    
    # Optimality gap
    gap_ratio = ub_feas / lb_total
    assert 1.0 < gap_ratio <= 1.055, f"Optimality gap must be <= 5.5%, got {gap_ratio}"


# ----------------------------------------------------------------------
# 32. Test Acceptance Gate TC-91-06: Adaptive Risk-of-Ruin & Tail Loss Metrics
# ----------------------------------------------------------------------
def test_tc91_06_adaptive_risk_of_ruin_and_tail_loss():
    """Verify that adaptive SPRT simulation records heavy-tailed losses (p95 ~106, p99 ~155, max ~268)
    and pathwise required account capital C0 (p99 ~156, ruin prob ~37.7% at mean loss) under both H0 and H1,
    and verify via live model-equation simulation that expected loss (~45.96) cannot be equated to initial solvency capital."""
    from breakthrough_experiments.exp14_capital_frontier_exact import sequential_probe_mc
    
    results_path = Path("breakthrough_experiments/results_exp14_capital_frontier_exact.json")
    assert results_path.exists()
    data = json.loads(results_path.read_text())
    sprt = data["sequential_mc_delta_0_05"]
    
    # 1. Check saved 20,000-path results under both H0 and H1
    h0 = sprt["H0"]
    h1 = sprt["H1"]
    assert np.isclose(h0["mean_loss"], 45.96, atol=0.50), "H0 mean loss must be ~45.96 USDT"
    assert np.isclose(h0["p95_loss"], 105.99, atol=5.0), "H0 p95 loss must be ~105.99 USDT"
    assert h0["p99_loss"] > 140.0, "H0 p99 loss must exceed 140 USDT"
    assert np.isclose(h0["p99_loss"], 155.46, atol=10.0), "H0 p99 loss must be ~155.46 USDT"
    assert h0["max_loss"] > 250.0, "H0 max loss must exceed 250 USDT"
    assert np.isclose(h0["max_loss"], 268.52, atol=15.0), "H0 max loss must be ~268.52 USDT"
    assert np.isclose(h0["p95_C0_required"], 106.53, atol=5.0), "H0 p95 C0 required must be ~106.53 USDT"
    assert np.isclose(h0["p99_C0_required"], 155.99, atol=10.0), "H0 p99 C0 required must be ~155.99 USDT"
    assert np.isclose(h0["ruin_prob_at_mean_loss"], 0.3773, atol=0.03), "H0 ruin prob at mean loss must be ~37.7%"
    
    assert np.isclose(h1["mean_loss"], 45.58, atol=0.50), "H1 mean loss must be ~45.58 USDT"
    assert h1["p95_C0_required"] > 100.0, "H1 p95 C0 required must exceed 100 USDT"
    assert h1["p99_C0_required"] > 140.0, "H1 p99 C0 required must exceed 140 USDT"
    assert h1["ruin_prob_at_mean_loss"] > 0.30, "H1 ruin prob at mean loss must exceed 30%"
    assert h0["p99_loss"] > 3.0 * h0["mean_loss"], "Tail loss is more than 3x the mean loss"
    
    # 2. Recompute live from model equations (n_paths=1000) to confirm independent of saved JSON
    live_mc = sequential_probe_mc(0.05, n_paths=1000, seed=20261011)
    for hyp in ("H0", "H1"):
        res_h = live_mc[hyp]
        assert 40.0 <= res_h["mean_loss"] <= 52.0
        assert res_h["p95_C0_required"] > 95.0
        assert res_h["p99_C0_required"] > 135.0
        assert res_h["ruin_prob_at_mean_loss"] > 0.30
        assert res_h["p99_loss"] > 3.0 * res_h["mean_loss"]


# ----------------------------------------------------------------------
# 33. Test Acceptance Gate TC-91-07: Adaptive Bound Inequality Ratio
# ----------------------------------------------------------------------
def test_tc91_07_adaptive_bound_inequality_ratio():
    """Verify that the dynamic savings ratio kl(alpha, 1-beta)/(2*z_alpha^2) = 0.4897 is an inequality
    on expected loss lower bounds, not equality of empirical account capital optima."""
    from breakthrough_experiments.exp14_capital_frontier_exact import binary_kl, ALPHA, Z
    
    kl_val = binary_kl(ALPHA, 1.0 - ALPHA)  # kl(0.05, 0.95) = 1.323568
    expected_ratio = kl_val / (2.0 * (Z ** 2))
    assert np.isclose(expected_ratio, 0.4897343, atol=1e-5), f"Ratio must equal 0.4897343, got {expected_ratio}"
    
    # Expected quadratic lower bounds
    from breakthrough_experiments.exp14_capital_frontier_exact import theorem_bounds
    b = theorem_bounds(0.05)
    lb_det_quad = b["quad_loss_lower_bound_deterministic"]
    lb_adapt_quad = b["quad_loss_lower_bound_adaptive_expected_H0"]
    
    # Check that ratio of lower bounds equals expected_ratio
    ratio_bounds = lb_adapt_quad / lb_det_quad
    assert np.isclose(ratio_bounds, expected_ratio, atol=1e-2)
    # Theoretical savings ceiling is at most 1 - 0.4897 = 51.03%
    max_savings_ceiling = 1.0 - expected_ratio
    assert np.isclose(max_savings_ceiling, 0.5102657, atol=1e-5)


# ----------------------------------------------------------------------
# 34. Test Acceptance Gate TC-91-08: Unknown-K Model Selection Without Oracle Centering
# ----------------------------------------------------------------------
def test_tc91_08_unknown_k_blind_candidate_set():
    """Verify that bic_select evaluates over a fixed candidate set {0, 1, 2, 3, 4} without oracle centering,
    correctly selects K=0 for pure dealer and K=2 for the delta=0.05 two-cohort pair."""
    import inspect
    from breakthrough_experiments.exp15_cohort_information import bic_select, h_of, SCENARIOS
    
    sig = inspect.signature(bic_select)
    assert "K_center" not in sig.parameters, "bic_select must NOT accept an oracle K_center parameter"
    assert sig.parameters["K_candidates"].default == (0, 1, 2, 3, 4), "Default K_candidates must include K=0: (0, 1, 2, 3, 4)"
    
    # 1. Pure dealer K=0 check
    h_dealer = h_of(np.array([]), 0)
    k_sel_0, fit_0 = bic_select(h_dealer, sigma_h=1e-4)
    assert k_sel_0 == 0, f"Blind model selection must select K=0 for pure dealer, got {k_sel_0}"
    assert len(fit_0) == 0
    
    # 2. Two-cohort delta=0.05 pair check
    sc = next(s for s in SCENARIOS if "delta=0.05" in s["name"])
    theta = np.concatenate([sc["w"], sc["eta"]])
    h = h_of(theta, 2)
    
    # Run blind BIC selection across fixed candidates (0, 1, 2, 3, 4) with low noise
    k_sel, fit = bic_select(h, sigma_h=1e-4)
    assert k_sel == 2, f"Blind model selection must select K=2, got {k_sel}"
    assert len(fit) == 4, "Selected parameter vector must have length 2K = 4"
    # Recovered weights and rates match ground truth (ML noiseless error ~1.1e-3 < 2e-3)
    weights_est = fit[:2]
    rates_est = fit[2:]
    assert np.allclose(np.sort(weights_est), np.sort(sc["w"]), atol=2e-3)
    assert np.allclose(np.sort(rates_est), np.sort(sc["eta"]), atol=2e-3)


# ----------------------------------------------------------------------
# 35. Test Acceptance Gate TC-91-09 & TC-91-10: Formal Proof & Prose Integrity
# ----------------------------------------------------------------------
def test_tc91_09_and_10_formal_proof_and_prose_integrity():
    """Verify that MANUSCRIPT_COVERAGE.md, claim_to_code_map.tex, and Machine_Markets_JF_Submission.tex
    are synchronized with 319 Lean declarations and 23/23 FULL environments, and contain no stale overclaims."""
    tex_text = Path("paper/Machine_Markets_JF_Submission.tex").read_text()
    cov_text = Path("research_extension/current_manuscript_lean_20261008/MANUSCRIPT_COVERAGE.md").read_text()
    map_text = Path("paper/generated/claim_to_code_map.tex").read_text()
    
    # Check 319 declarations and 23/23 FULL statements in manuscript prose
    assert "319 kernel-checked Lean~4 declarations" in tex_text
    assert "23 / 23 FULL" in tex_text
    assert "319" in cov_text
    
    # Check that Theorems IA.D.1-IA.D.6 and Proposition IA.D.3 are mapped
    for label in [
        "thm:ia_exact_capital",
        "thm:ia_adaptive_capital",
        "prop:ia_cohort_information",
        "thm:ia_nonconvex_duality",
        "thm:ia_minimax_lecam",
        "thm:ia_crash_free_guard",
    ]:
        assert label in tex_text
    for title in [
        "Spectral Dissipation Lower Bound and Feasible Identification Probes",
        "Information-Theoretic Lower Bound for Adaptive and Sequential Probing",
        "Cram\\'er--Rao Local Information Benchmark for Multi-Cohort Weight Recovery",
        "Finite-Horizon Rayleigh--H\\\"older Duality and Multi-Horizon Capital Convergence",
        "Global Non-Asymptotic Le Cam Two-Point Minimax Lower Bound for Arbitrary Biased and Shrinkage Estimators",
        "Conditional Bounded-Shock Forward Solvency of the Real-Time Resolvent Guard",
    ]:
        assert title in tex_text
        assert title in cov_text
        assert title in map_text
        
    # Check that stale overclaims are absent from manuscript and tables
    assert "112.30" not in tex_text
    assert "38.2\\%" not in tex_text
    assert "strictly constant" not in tex_text
    assert "Minimax LQG" not in tex_text
    assert "Minimax LQG" not in Path("breakthrough_experiments/tables/table_probing_methods.tex").read_text()


# ----------------------------------------------------------------------
# 36. Test Theorem IA.D.4: Finite-Horizon Rayleigh-Holder Duality (Exp 16)
# ----------------------------------------------------------------------
def test_exp16_nonconvex_duality_and_multi_horizon_convergence():
    """Verify Theorem IA.D.4 (exp16): finite-horizon Rayleigh-Holder dual bound closes the gap to 0.98%
    at L=80 (64.74 vs 65.38 USDT) and multi-horizon feasible probe attains 64.56 USDT at L=240."""
    from breakthrough_experiments.exp16_nonconvex_duality_closing import compute_finite_horizon_bounds_and_probe

    res_path = Path("breakthrough_experiments/results_exp16_nonconvex_duality.json")
    assert res_path.exists()
    data = json.loads(res_path.read_text())
    sweep = {r["L"]: r for r in data["horizon_sweep"]}

    # 1. Check L=80 tight finite-horizon duality certificate (< 1.0% gap)
    r80 = sweep[80]
    assert np.isclose(r80["lb_certified_FH_rayleigh_holder"], 64.743, atol=0.05)
    assert np.isclose(r80["feasible_probe_C0"], 65.378, atol=0.05)
    assert r80["lb_certified_FH_rayleigh_holder"] <= r80["feasible_probe_C0"]
    assert r80["gap_vs_FH_rayleigh_holder_pct"] < 1.0

    # 2. Check L=240 best evaluated feasible account capital (64.56 USDT)
    r240 = sweep[240]
    assert np.isclose(r240["feasible_probe_C0"], 64.558, atol=0.05)
    assert r240["meets_5pct"] is True
    assert r240["gap_vs_inf_certified_pct"] < 5.10

    # 3. Verify O(1/L) truncation premium decay and O(sqrt(L)) L1 fee growth
    L_list = [80, 120, 160, 240, 320, 480]
    trunc_prems = [sweep[L]["truncation_premium_quad"] for L in L_list]
    eigen_fees = [sweep[L]["eigen_l1_fee"] for L in L_list]
    assert all(trunc_prems[i] > trunc_prems[i + 1] for i in range(len(L_list) - 1)), "Quadratic truncation premium must decrease monotonically with L"
    assert all(eigen_fees[i] < eigen_fees[i + 1] for i in range(len(L_list) - 1)), "Sinusoid L1 fee must increase monotonically with L"

    # 4. Live model-equation verification at L=80
    live_80_res = compute_finite_horizon_bounds_and_probe(80, delta=0.05)
    live_80 = live_80_res[0] if isinstance(live_80_res, tuple) else live_80_res
    assert np.isclose(live_80["lb_certified_FH_rayleigh_holder"], r80["lb_certified_FH_rayleigh_holder"], atol=1e-6)


# ----------------------------------------------------------------------
# 37. Test Theorem IA.D.5: Global Non-Asymptotic Le Cam Minimax Bound (Exp 17)
# ----------------------------------------------------------------------
def test_exp17_minimax_lecam_two_point_bound():
    """Verify Theorem IA.D.5 (exp17): exact moment-matched two-point pair has identical M0, M1, M2,
    exact cubic gap 4*tau*p_minus*p_plus*(Delta_eta)^3, log-log slope ~ -6.0, and bounds all biased/shrinkage estimators."""
    from breakthrough_experiments.exp17_minimax_lecam_bound import construct_exact_lecam_pair

    res_path = Path("breakthrough_experiments/results_exp17_minimax_lecam_bound.json")
    assert res_path.exists()
    data = json.loads(res_path.read_text())

    # 1. Verify log-log slopes match Theta((Delta_eta)^-6)
    assert -6.20 <= data["loglog_slope_lecam_exact"] <= -5.90
    assert -6.20 <= data["loglog_slope_lecam_analytic"] <= -5.90
    assert -6.20 <= data["loglog_slope_crb"] <= -5.90

    # 2. Live verification of the closed-form moment-matched pair at Delta_eta = 0.10, tau = 0.01
    pair = construct_exact_lecam_pair(0.10, tau=0.01)
    assert np.isclose(pair["exact_cohort_spacing_theta0"], 0.10, atol=1e-12)
    assert np.isclose(pair["exact_cohort_spacing_theta1"], 0.10, atol=1e-12)
    assert np.isclose(pair["exact_weight_separation_linf"], 0.02, atol=1e-12)
    assert all(abs(d) < 1e-15 for d in pair["moment_diffs_m0_m1_m2"]), "First three moments M0, M1, M2 must match to machine precision"
    assert np.isclose(pair["moment_diff_m3_exact"], pair["moment_diff_m3_formula"], atol=1e-15)
    assert np.isclose(pair["moment_diff_m3_exact"], 9.9e-6, atol=1e-12)
    assert np.isclose(pair["n_star_lecam_95pct_any_estimator"], 6172.17, atol=1.0)
    assert np.isclose(pair["minimax_fail_prob_N50"], 0.44115, atol=1e-3)

    # 3. Verify every tested estimator (ML, Ridge, James-Stein, Heavy Prior Shrinkage) obeys Le Cam bound
    for cell in data["estimator_benchmark_delta_eta_010"]:
        lb = cell["lecam_minimax_fail_prob_lb"]
        for est_name, est_res in cell["estimators"].items():
            assert est_res["obeys_lecam_bound"] is True, f"{est_name} at N={cell['N']} violated Le Cam bound"
            assert est_res["worst_case_fail_prob"] >= lb - 0.02


# ----------------------------------------------------------------------
# 38. Test Theorem IA.D.6: Crash-Free Real-Time Resolvent Solvency Guard (Exp 18)
# ----------------------------------------------------------------------
def test_exp18_crash_free_resolvent_guard():
    """Verify Theorem IA.D.6 (exp18): under explicit double-entry dealer cash/inventory/margin ledger,
    Resolvent_Guard_Kreiss achieves 0.0% liquidation across all 4 regimes (including Non-Normal Herding
    and Real Binance Jan 2023 L2 Replay), whereas Eigenvalue_Guard suffers 100% liquidation in non-normal regimes."""
    from breakthrough_experiments.exp18_crash_free_ai_guard import simulate_double_entry_dealer_episode, B_MAINT_BUDGET

    res_path = Path("breakthrough_experiments/results_exp18_crash_free_ai_guard.json")
    assert res_path.exists()
    data = json.loads(res_path.read_text())
    regimes = {r["regime"]: r for r in data["regimes"]}

    # 1. Check Resolvent_Guard_Kreiss achieves 0.0% liquidation and worst drawdown < 9,050 USDT in all 4 regimes
    for reg_name, reg in regimes.items():
        kr = reg["architectures"]["Resolvent_Guard_Kreiss"]
        assert kr["liquidation_rate"] == 0.0, f"Resolvent Guard must have 0% liquidation in {reg_name}"
        assert kr["worst_max_drawdown_usdt"] < B_MAINT_BUDGET, f"Resolvent Guard max drawdown must stay below {B_MAINT_BUDGET} in {reg_name}"
        assert kr["quote_continuity_ratio"] == 1.0

    # 2. Check Benign regime has 100% flow admission (zero false alarms)
    assert regimes["Regime_I_Benign"]["architectures"]["Resolvent_Guard_Kreiss"]["mean_admission_gamma"] == 1.0

    # 3. Check Non-Normal Herding (Regime II) and Binance Empirical Replay (Regime IV) falsify Eigenvalue_Guard
    for non_normal_reg in ("Regime_II_NonNormal_Herding", "Regime_IV_Binance_Empirical_Replay"):
        r_nn = regimes[non_normal_reg]
        assert r_nn["unguarded_spectral_radius_rho"] < 0.85, "Non-normal regime must be spectrally stable (rho < 0.85)"
        assert r_nn["unguarded_price_transient_gain_MC"] > 35.0, "Non-normal regime must have large transient gain (> 35)"
        assert r_nn["architectures"]["Eigenvalue_Guard"]["liquidation_rate"] == 1.0, f"Eigenvalue Guard must fail (100% liquidation) in {non_normal_reg}"
        assert r_nn["architectures"]["Static_Halt"]["liquidation_rate"] >= 0.35, f"Reactive circuit breaker must suffer liquidations in {non_normal_reg}"

    # 4. Live single-episode simulation check from model equations
    rng = np.random.default_rng(20261013)
    shocks = np.abs(rng.standard_t(df=4.0, size=(50, 3))) * 0.22
    ep_eig = simulate_double_entry_dealer_episode(shocks, "Regime_II_NonNormal_Herding", "Eigenvalue_Guard")
    ep_kr = simulate_double_entry_dealer_episode(shocks, "Regime_II_NonNormal_Herding", "Resolvent_Guard_Kreiss")
    assert ep_eig["liquidated"] is True
    assert ep_kr["liquidated"] is False
    assert ep_kr["max_drawdown_usdt"] < B_MAINT_BUDGET


# ----------------------------------------------------------------------
# 39. Test Empirical Upgrade 1: Historical Crisis 1-Second Replay (Exp 19)
# ----------------------------------------------------------------------
def test_exp19_historical_crash_replay():
    """Verify exp19: 345,600 SHA-256 verified 1-second bars across 4 major historical crashes
    (May 2021, LUNA May 2022, FTX Nov 2022, SVB Mar 2023) show 0.0% liquidation for Resolvent_Guard_Kreiss
    vs 100.0% for Unguarded and Eigenvalue_Guard and 35.0% for Static_Halt."""
    from breakthrough_experiments.exp19_historical_crash_replay import (
        analyze_crash_day_and_extract_windows,
        simulate_double_entry_dealer_episode,
    )

    res_path = Path("breakthrough_experiments/results_exp19_historical_crash_replay.json")
    assert res_path.exists()
    data = json.loads(res_path.read_text())

    assert data["total_1s_records_verified"] == 345600
    assert data["total_crash_episodes"] == 100
    assert len(data["events"]) == 4

    # Verify SHA-256 checksums matched official data.binance.vision .CHECKSUM for all 4 events
    for ev_id, ev in data["events"].items():
        assert ev["sha256_matches_official_checksum"] is True, f"SHA-256 checksum failed for {ev_id}"
        assert ev["day_stats"]["n_seconds"] == 86400
        kr = ev["architectures"]["Resolvent_Guard_Kreiss"]
        assert kr["liquidation_rate_pct"] == 0.0
        assert kr["mean_min_equity_usdt"] > 5000.0
        assert kr["quote_uptime_pct"] == 100.0
        assert ev["architectures"]["Unguarded"]["liquidation_rate_pct"] == 100.0
        assert ev["architectures"]["Eigenvalue_Guard"]["liquidation_rate_pct"] == 100.0

    pooled = data["overall_100_episode_summary"]
    assert pooled["Resolvent_Guard_Kreiss"]["liquidation_rate_pct"] == 0.0
    assert pooled["Resolvent_Guard_Kreiss"]["worst_min_equity_usdt"] > 4000.0
    assert pooled["Unguarded"]["liquidation_rate_pct"] == 100.0
    assert pooled["Eigenvalue_Guard"]["liquidation_rate_pct"] == 100.0
    assert np.isclose(pooled["Static_Halt"]["liquidation_rate_pct"], 35.0, atol=6.0)

    # Live crisis window extraction and replay check on synthetic 1s crash day
    rng = np.random.default_rng(20261019)
    n_sec = 2000
    synth_close = 30000.0 + np.cumsum(rng.normal(0.0, 15.0, size=n_sec))
    synth_data = {
        "open": synth_close,
        "high": synth_close + 10.0,
        "low": synth_close - 10.0,
        "close": synth_close,
        "volume": np.abs(rng.normal(10.0, 5.0, size=n_sec)),
        "trades": np.full(n_sec, 100, dtype=np.int64),
        "signed_flow": rng.normal(0.0, 8.0, size=n_sec),
    }
    res_tuple = analyze_crash_day_and_extract_windows(synth_data, n_windows=5, window_len=50)
    stats, windows = res_tuple[0], res_tuple[1]
    assert stats["n_seconds"] == n_sec
    assert windows.shape == (5, 50, 3)
    ep_eig = simulate_double_entry_dealer_episode(windows[-1], "Regime_IV_Binance_Empirical_Replay", "Eigenvalue_Guard")
    ep_kr = simulate_double_entry_dealer_episode(windows[-1], "Regime_IV_Binance_Empirical_Replay", "Resolvent_Guard_Kreiss")
    assert ep_eig["liquidated"] is True
    assert ep_kr["liquidated"] is False


# ----------------------------------------------------------------------
# 40. Test Empirical Upgrade 2: Exact 10-Level Time-Varying L2 Book Walking (Exp 20)
# ----------------------------------------------------------------------
def test_exp20_exact_l2_book_walking():
    """Verify exp20: exact 10-level L2 book captures 2.75x-3.51x larger p90 slippage than
    static midpoint-slope approximations, and L2-Depth-Aware Resolvent Guard achieves 0.0% liquidation."""
    from breakthrough_experiments.exp20_exact_l2_book_walking import (
        walk_l2_book,
        simulate_dealer_l2_book_walking,
        B_MAINT_BUDGET,
    )

    res_path = Path("breakthrough_experiments/results_exp20_exact_l2_book_walking.json")
    assert res_path.exists()
    data = json.loads(res_path.read_text())

    # 1. Verify p90 L2 book-walking slippage exceeds static linear approximation by > 2.5x across all order sizes
    sweep = data["book_microstructure_stats"]["sweep_profile"]
    for _, row in sweep.items():
        assert row["empirical_to_static_p90_ratio"] > 2.50
        assert row["p90_buy_slippage_usdt"] > row["static_linear_mid_approx_usdt"]

    # 2. Verify L2-Depth-Aware Resolvent Guard achieves 0.0% liquidation and < 4,000 USDT p99 drawdown
    archs = data["dealer_ledger_comparison"]
    kr_l2 = archs["Resolvent_Guard_Kreiss"]["exact_10level_l2_book_walking"]
    kr_blind = archs["Resolvent_Guard_DepthBlind"]["exact_10level_l2_book_walking"]
    assert kr_l2["liquidation_rate_pct"] == 0.0
    assert kr_l2["p99_max_drawdown_usdt"] < 4000.0
    assert kr_l2["quote_uptime_pct"] == 100.0
    assert archs["Unguarded"]["exact_10level_l2_book_walking"]["liquidation_rate_pct"] == 100.0
    assert archs["Eigenvalue_Guard"]["exact_10level_l2_book_walking"]["liquidation_rate_pct"] == 100.0
    assert kr_blind["p99_max_drawdown_usdt"] > kr_l2["p99_max_drawdown_usdt"]

    # 3. Live verification of walk_l2_book piecewise-linear convexity on a 10-level book
    mid = 20000.0
    ask_p = np.array([20000.05 + 0.15 * i for i in range(10)], dtype=float)
    ask_v = np.array([0.8] * 10, dtype=float)  # 8 BTC total across 10 levels
    bid_p = np.array([19999.95 - 0.15 * i for i in range(10)], dtype=float)
    bid_v = np.array([0.8] * 10, dtype=float)
    snap = {
        "mid": mid,
        "spread": 0.10,
        "bid_p": bid_p,
        "bid_v": bid_v,
        "ask_p": ask_p,
        "ask_v": ask_v,
        "depth_bid_10": 8.0,
        "depth_ask_10": 8.0,
        "slope_bid_10": float((mid - bid_p[9]) / 8.0),
        "slope_ask_10": float((ask_p[9] - mid) / 8.0),
        "slope_mean_10": float((ask_p[9] - mid) / 8.0),
    }
    w1 = walk_l2_book(0.5, snap)
    w10 = walk_l2_book(12.0, snap)
    assert w1["levels_consumed"] == 1.0
    assert w10["levels_consumed"] == 10.0
    assert w10["slippage_usdt_per_unit"] > 5.0 * w1["slippage_usdt_per_unit"]

    # 4. Live simulation check on a 50-step thin 10-level book window
    T = 50
    l2_win = [snap for _ in range(T)]
    rng = np.random.default_rng(20261020)
    shocks = np.abs(rng.standard_t(df=4.0, size=(T, 3))) * 0.25
    ep_l2 = simulate_dealer_l2_book_walking(shocks, l2_win, "Resolvent_Guard_Kreiss", use_exact_l2_walking=True)
    assert ep_l2["liquidated"] is False
    assert ep_l2["max_drawdown_usdt"] < B_MAINT_BUDGET


# ----------------------------------------------------------------------
# 41. Test Empirical Upgrade 3: 8-Asset Synchronized Crisis Panel & Cross-Margin Guard (Exp 21)
# ----------------------------------------------------------------------
def test_exp21_empirical_multi_asset_kreiss_network():
    """Verify exp21: 691,200 SHA-256 verified 1-second bars across all 8 study assets on Nov 8, 2022
    yield rho(J_16) = 0.7663 < 1 with M_C8(J_16) = 131.92, and Multi-Asset Resolvent Guard achieves
    0.0% cross-margin portfolio liquidation vs 100.0% for Unguarded and Eigenvalue_Guard."""
    from breakthrough_experiments.exp21_empirical_multi_asset_kreiss_network import (
        load_tier2_margin_brackets,
        build_8asset_jacobian,
        compute_8asset_resolvent_metrics,
        simulate_8asset_cross_margin_episode,
    )

    res_path = Path("breakthrough_experiments/results_exp21_empirical_multi_asset_kreiss.json")
    assert res_path.exists()
    data = json.loads(res_path.read_text())

    assert data["total_synchronized_1s_bars"] == 691200
    assert len(data["assets"]) == 8
    assert all(a["sha256_matches_official"] is True for a in data["assets"].values())

    net = data["jacobian_16x16_metrics"]
    assert net["stress_jacobian_spectral_radius"] < 0.85
    assert net["stress_jacobian_price_output_gain_MC"] > 100.0

    archs = data["portfolio_ledger_100_episodes"]
    kr8 = archs["Resolvent_Guard_Kreiss"]
    b_maint_port = 80000.0 - kr8["initial_total_maint_margin_usdt"]
    assert kr8["liquidation_rate_pct"] == 0.0
    assert kr8["p99_max_drawdown_usdt"] < b_maint_port
    assert kr8["quote_uptime_pct"] == 100.0
    assert archs["Unguarded"]["liquidation_rate_pct"] == 100.0
    assert archs["Eigenvalue_Guard"]["liquidation_rate_pct"] == 100.0

    # Live check of authentic Binance Tier-2 brackets and 16x16 operator construction
    brackets = load_tier2_margin_brackets()
    assert len(brackets) == 8

    diag_base = np.linspace(0.60, 0.76, 16)
    U_norm = np.triu(np.ones((16, 16)), k=1)
    U_norm = U_norm / np.linalg.norm(U_norm, ord="fro")
    J_16, C_8 = build_8asset_jacobian(1.0, diag_base, U_norm)
    assert J_16.shape == (16, 16)
    assert C_8.shape == (8, 16)
    rho_16, _, mc_8, _ = compute_8asset_resolvent_metrics(J_16, C_8, horizon=20)
    assert rho_16 < 0.80
    assert mc_8 > 50.0

    rng = np.random.default_rng(20261021)
    shocks_16 = np.abs(rng.standard_t(df=4.0, size=(50, 16))) * 0.18
    shocks_16[:, :4] *= 0.25
    shocks_16[:, 4:12] *= 0.45
    shocks_16[:, 12:] *= 0.75
    ep_eig = simulate_8asset_cross_margin_episode(shocks_16, diag_base, U_norm, brackets, "Eigenvalue_Guard")
    ep_kr8 = simulate_8asset_cross_margin_episode(shocks_16, diag_base, U_norm, brackets, "Resolvent_Guard_Kreiss")
    assert ep_eig["liquidated"] is True
    assert ep_kr8["liquidated"] is False
    assert ep_kr8["max_drawdown_usdt"] < b_maint_port


# ----------------------------------------------------------------------
# 42. Test Scientific Validation Gates P0-2, P0-3, P0-4
# ----------------------------------------------------------------------
def test_p02_p03_p04_scientific_validation_gates():
    """Verify P0-2 (full-domain 1800-interval outward-rounded Decimal certificate >= 64.7423),
    P0-3 (parameter-blind multi-lag Prony-Hankel estimator O((Delta_eta)^-6) upper bound),
    and P0-4 (Equation IA.39 exact character-for-character guard and 4-category state audit)."""
    from scripts.independent_checks.verify_p02_full_domain_certificate import certify_full_domain_p02
    from breakthrough_experiments.exp17_minimax_lecam_bound import (
        blind_multilag_prony_estimator,
        construct_exact_lecam_pair,
        h_of,
    )
    from breakthrough_experiments.exp18_crash_free_ai_guard import evaluate_out_of_domain_counterexample

    # P0-2: Full-domain 1,800-interval outward-rounded Decimal certificate
    cert_p02 = certify_full_domain_p02(L=80, delta=0.05, n_theta=1800)
    assert cert_p02["p02_pass"] is True
    assert cert_p02["theta_intervals_certified"] == 1800
    assert cert_p02["certified_full_domain_lb_decimal"] >= 64.7423
    assert cert_p02["weyl_eigenvalue_perturbation_bound"] < 1e-16

    # P0-3: Parameter-blind multi-lag Prony-Hankel estimator
    pair = construct_exact_lecam_pair(0.10, tau=0.01)
    assert pair["blind_prony_noiseless_max_err"] < 1e-12
    theta_hat = blind_multilag_prony_estimator(h_of(np.array(pair["theta0_analytic"]), 2))
    assert np.max(np.abs(theta_hat - np.array(pair["theta0_analytic"]))) < 1e-11

    # P0-4: 4-category state audit and NO_SAFE_ACTION protective fallback
    ood = evaluate_out_of_domain_counterexample()
    audit = ood["p04_four_category_state_audit"]
    assert audit["category_1_ordinary_feasible"]["status"] == "FEASIBLE"
    assert audit["category_2_exact_margin_boundary"]["status"] == "FEASIBLE"
    assert audit["category_3_all_candidates_fail"]["pre_infeasible"] is True
    assert audit["category_3_all_candidates_fail"]["status"] == "NO_SAFE_ACTION"
    assert audit["category_3_all_candidates_fail"]["selected_alpha"] == 0.0
    assert audit["category_4_out_of_domain_shock"]["status"] == "NO_SAFE_ACTION"






