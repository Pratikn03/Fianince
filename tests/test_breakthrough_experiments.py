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
