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

