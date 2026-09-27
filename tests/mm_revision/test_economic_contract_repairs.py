"""Economic contract repairs and characterization of retained funded trajectories."""
import numpy as np
import pytest

from research_extension.mm_revision.identities import (
    analyze_channel_experiment_map,
    recover_unknown_eta_and_q,
)
from research_extension.mm_revision.studies.funded_stress import (
    DealerBalanceSheet,
    FundedScenarioMarket,
    run_paired_mechanism_controls,
)


def test_default_diagnostics_describe_implemented_new_price_memory_dynamics():
    diagnostics = FundedScenarioMarket().dynamics_diagnostics()
    assert diagnostics["nominal_a"] == pytest.approx(0.4)
    assert diagnostics["effective_a"] == pytest.approx(0.8)
    assert diagnostics["Q"] == pytest.approx(0.42)
    assert diagnostics["nominal_S"] == pytest.approx(0.82)
    assert diagnostics["effective_S"] == pytest.approx(1.22)
    assert diagnostics["parameter_mismatch"] is True
    matrix = np.array(diagnostics["transition_matrix"])
    np.testing.assert_allclose(matrix, [
        [0.8, 0.252, 0.168],
        [0.4, 0.626, 0.084],
        [0.016, 0.00504, 0.98336],
    ])
    assert diagnostics["spectral_radius"] == pytest.approx(max(abs(np.linalg.eigvals(matrix))))
    assert diagnostics["spectral_radius"] > 1
    assert diagnostics["state_order"] == ["x", "y_fast", "y_slow"]
    assert diagnostics["memory_timing"] == "x_next"
    assert diagnostics["units"]["shock_tape"] == "shares_per_step"
    assert diagnostics["units"]["mean_repricing_shock"] == "price"


def test_matching_nominal_a_reports_no_parameter_mismatch():
    diagnostics = FundedScenarioMarket(a=0.8).dynamics_diagnostics()
    assert diagnostics["parameter_mismatch"] is False


@pytest.mark.parametrize("regime", ["adaptive", "frozen", "zero_feedback"])
@pytest.mark.parametrize("horizon", [1, 2, 3])
def test_matrix_predicts_real_trajectory_finite_differences(regime, horizon):
    """Catch incorrect price persistence, feedback, or memory-update timing."""
    market = FundedScenarioMarket(unlimited_funding=True)
    diagnostics = market.dynamics_diagnostics(learning_regime=regime)
    matrix = np.array(diagnostics["transition_matrix"])
    # Frozen regime is evaluated after the freeze boundary (shock_step=0).
    if regime == "frozen":
        matrix = np.array(diagnostics["post_freeze_transition_matrix"])
    derivatives = []
    epsilon = 1e-5
    for column in range(3):
        prices = []
        for sign in [-1, 1]:
            state = np.zeros(3)
            state[column] = sign * epsilon
            actual = FundedScenarioMarket(unlimited_funding=True)
            actual.run_trajectory(
                np.zeros(horizon), mean_repricing_shock=state[0],
                shock_step=0, initial_memory=state[1:], learning_regime=regime,
            )
            # Price impact telescopes exactly when no inventory clipping occurs.
            prices.append(state[0] - actual.kappa * actual.dealer.inventory)
        derivatives.append((prices[1] - prices[0]) / (2 * epsilon))
    np.testing.assert_allclose(derivatives, np.linalg.matrix_power(matrix, horizon)[0], atol=1e-11)


def test_no_shock_trajectory_preserves_historical_price_and_balance_sheet():
    market = FundedScenarioMarket()
    result = market.run_trajectory(np.zeros(2))
    # x1=.021, yf1=.0355, ys1=.04942, x2=.03404856.
    assert result["mean_dislocation"] == pytest.approx(0.02752428, abs=1e-12)
    assert market.dealer.inventory == pytest.approx(-1.702428, abs=1e-12)
    assert result["final_equity"] == pytest.approx(9999.986299012, abs=1e-10, rel=0)
    assert result["dealer_halt"] is False


@pytest.mark.parametrize("regime", ["adaptive", "frozen", "zero_feedback"])
def test_trajectory_reports_regime_specific_diagnostics(regime):
    market = FundedScenarioMarket()
    result = market.run_trajectory(np.zeros(2), learning_regime=regime)
    assert result["dynamics_diagnostics"] == market.dynamics_diagnostics(learning_regime=regime)
    if regime == "zero_feedback":
        assert result["dynamics_diagnostics"]["Q"] == 0


def test_paired_controls_expose_top_level_diagnostics_for_each_regime():
    result = run_paired_mechanism_controls(n_replicates=2)
    diagnostics = result["dynamics_diagnostics"]
    assert set(diagnostics) == set(result["summary"])
    assert diagnostics["adaptive"]["effective_S"] == pytest.approx(1.22)
    assert diagnostics["zero_feedback"]["effective_S"] == pytest.approx(0.8)
    assert diagnostics["unlimited_funding"]["transition_matrix"] == diagnostics["adaptive"]["transition_matrix"]
    assert "post_freeze_transition_matrix" in diagnostics["frozen"]


@pytest.mark.parametrize("multiplier,limit", [(0.5, 12.5), (1.0, 25.0), (4.0, 100.0)])
def test_capacity_multiplier_changes_limit_at_fixed_initial_equity(multiplier, limit):
    market = FundedScenarioMarket(dealer_capital_multiplier=multiplier, initial_utilization=0.5)
    assert market.dealer.max_inventory == limit
    assert market.dealer.initial_equity == 10000
    assert market.dealer.cash + market.dealer.inventory * market.p_star == 10000


def test_halt_occurrence_flag_allows_later_reverse_fill():
    market = FundedScenarioMarket(phi=0, q_fast=0, q_slow=0, base_inventory_limit=1)
    result = market.run_trajectory(np.array([2.0, -0.5]), initial_memory=(0, 0))
    assert result["dealer_halt"] is True
    assert result["unfilled_volume"] == 1
    assert market.dealer.inventory == -0.5  # Reverse fill occurs after hitting -1.
    assert market.dealer.cash == pytest.approx(10050.015)
    assert result["final_equity"] == pytest.approx(10000.01)


def test_margin_breaches_are_counted_without_liquidation():
    dealer = DealerBalanceSheet(cash=-90, inventory=1, initial_cash=-90,
                               initial_inventory=1, max_inventory=25, initial_equity=10)
    dealer.mark_to_market(100)
    dealer.mark_to_market(100)
    assert dealer.margin_calls_count == 2
    assert (dealer.cash, dealer.inventory) == (-90, 1)
    assert dealer.defaulted is False


def test_channel_rank_result_has_uniform_scope_at_nonnegative_boundary():
    # With b=0 and q>=0, U=[1,1] has singleton fiber {0} despite rank deficiency.
    result = analyze_channel_experiment_map(np.array([[1.0, 1.0]]), eta=0.5)
    assert result["unique_identification"] is False
    assert result["identification_scope"] == "uniform_generic_rank_not_pointwise_boundary"


@pytest.mark.parametrize("eta", [0, -0.1, 1.01, np.nan, np.inf])
def test_channel_map_rejects_invalid_known_learning_rate(eta):
    with pytest.raises(ValueError, match="eta"):
        analyze_channel_experiment_map(np.eye(2), eta=eta)


@pytest.mark.parametrize("U,b,Q,reason", [
    ([[1, 1], [2, 2]], [0.2, 0.4], 1, "rank"),
    ([[1, 0], [0, 1], [1, 1]], [0.1, 0.2, 0.9], 1, "compatible"),
    ([[1, 0], [0, 1]], [-0.1, 0.3], 1, "nonnegative"),
    ([[1, 0], [0, 1]], [0, 0], 1, "eta"),
    ([[1, 0], [0, 1]], [0.8, 0.8], 1, "eta"),
    ([[1, 0], [0, 1]], [-0.1, -0.2], 1, "nonnegative|eta"),
    ([[1, 0], [0, 1]], [0.1, 0.2], 0, "Q"),
    ([[1, 0], [0, 1]], [0.1, 0.2], np.nan, "Q"),
    ([[1, 0], [0, 1]], [0.1, 0.2], np.inf, "Q"),
    ([[1, 0], [0, 1]], [np.nan, 0.2], 1, "finite"),
    ([[1, 0], [0, 1]], [np.inf, 0.2], 1, "finite"),
    ([[1, 0], [0, np.nan]], [0.1, 0.2], 1, "finite"),
    ([[1, 0], [0, 1], [1, 1]], [1e-12, 2e-12, 9e-12], 1, "compatible"),
    ([[1, 0], [0, 1]], [-1e-12, 3e-12], 1, "nonnegative"),
    ([1, 2], [0.1, 0.2], 1, "matrix"),
    ([[1, 0], [0, 1]], [0.1], 1, "rows"),
])
def test_unknown_rate_recovery_rejects_invalid_contract(U, b, Q, reason):
    with pytest.raises(ValueError, match=reason):
        recover_unknown_eta_and_q(np.array(U), np.array(b), Q)


@pytest.mark.parametrize("b,Q,eta,q", [
    ([0.06, 0.02, 0.08], 0.4, 0.2, [0.3, 0.1]),
    ([0, 0.4, 0.4], 0.4, 1, [0, 0.4]),
    ([3e-13, 1e-13, 4e-13], 0.4, 1e-12, [0.3, 0.1]),
])
def test_unknown_rate_recovery_accepts_compatible_nonnegative_boundary(b, Q, eta, q):
    U = np.array([[1, 0], [0, 1], [1, 1]])
    actual_eta, actual_q = recover_unknown_eta_and_q(U, b, Q)
    assert actual_eta == pytest.approx(eta)
    np.testing.assert_allclose(actual_q, q, atol=1e-14)
    assert np.all(actual_q >= 0)
    np.testing.assert_allclose(actual_eta * U @ actual_q, b, atol=1e-14)
