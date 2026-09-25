"""Tests for Work Package 1: Mathematical contracts, exact witnesses, and identities."""
import pytest
import numpy as np
from research_extension.mm_revision.contracts import (
    CONTRACT_I0, CONTRACT_I1, CONTRACT_I2, InformationContractType
)
from research_extension.mm_revision.states import (
    build_transition_matrix,
    spectral_radius,
    total_feedback_gain,
    steady_state_multiplier,
    compute_impulse_response,
    compute_kernel_taps,
    simulate_discrete_trajectory,
)
from research_extension.mm_revision.identities import (
    verify_spectral_vs_gain_distinction,
    get_rational_finite_window_witness,
    verify_swapped_feedback_ambiguity,
    analyze_channel_experiment_map,
    compute_group_intervention,
)
from research_extension.mm_revision.decisions import (
    DecisionLabel,
    classify_interval,
    evaluate_decision_accuracy,
    aggregate_decision_metrics,
)


def test_information_contracts_distinctions():
    """Verify contracts I0, I1, I2 have mutually distinct assumptions."""
    assert CONTRACT_I0.contract_type == InformationContractType.I0
    assert CONTRACT_I1.contract_type == InformationContractType.I1
    assert CONTRACT_I2.contract_type == InformationContractType.I2

    # I0 cannot assume known internal states
    assert any("internal" in item.lower() for item in CONTRACT_I0.forbidden_assumptions)
    # I1 allows audited architecture but forbids unconstrained operational solvency
    assert any("solvency" in item.lower() for item in CONTRACT_I1.forbidden_assumptions)
    # I2 forbids claiming AI attribution or treating F as structural S
    assert any("ai" in item.lower() for item in CONTRACT_I2.forbidden_assumptions)


def test_spectral_vs_gain_numerical_distinction():
    """Verify S = a + Q is not numerically equal to rho(J) for the audited baseline."""
    res = verify_spectral_vs_gain_distinction()
    assert abs(res["S"] - 0.82) < 1e-12
    assert abs(res["rho"] - 0.99009025) < 1e-5
    assert not res["is_numerically_equal"]
    assert res["both_stable"]


def test_exact_rational_witness_finite_window_ambiguity():
    """Verify Theorem 8.2 / Table 8.1 witness produces exact match for h0..h3 and opposite stability."""
    wit = get_rational_finite_window_witness()
    assert wit["matches_up_to_lag3"]
    assert wit["diverges_at_lag4"]

    stable = wit["stable_member"]
    unstable = wit["unstable_member"]

    assert stable["S"] < 1.0 and stable["rho"] < 1.0
    assert unstable["S"] > 1.0 and unstable["rho"] > 1.0
    assert abs(stable["h"][0] - unstable["h"][0]) < 1e-12
    assert abs(stable["h"][1] - unstable["h"][1]) < 1e-12
    assert abs(stable["h"][2] - unstable["h"][2]) < 1e-12
    assert abs(stable["h"][3] - unstable["h"][3]) < 1e-12
    assert abs(stable["h"][4] - unstable["h"][4]) > 0.01


def test_swapped_feedback_proposition():
    """Verify Proposition G.1: Swapped feedback produces identical aggregate prices, divergent policy impact."""
    res = verify_swapped_feedback_ambiguity(a=0.4, eta_common=0.05, q_pair=(0.3, 0.1), H=50)
    assert res["is_observationally_identical"]
    assert abs(res["suppression_effect_ratio"] - 3.0) < 1e-12
    assert abs(res["economy_A"]["delta_G1"] - 0.50) < 1e-12
    assert abs(res["economy_B"]["delta_G1"] - (0.1 / 0.6)) < 1e-12


def test_channel_experiment_measurement_map_known_eta():
    """Verify Theorem G.2: Full column rank with known eta identifies q."""
    # 2 channels, 2 experiments
    U_full = np.array([[1.0, 0.0], [0.0, 1.0]])
    res_full = analyze_channel_experiment_map(U_full, eta=0.05, aggregate_Q_known=False)
    assert res_full["unique_identification"]
    assert res_full["rank_U"] == 2

    # 2 channels, 1 channel experiment, but aggregate Q is known!
    U_single = np.array([[1.0, 0.0]])
    res_aug = analyze_channel_experiment_map(U_single, eta=0.05, aggregate_Q_known=True)
    assert res_aug["unique_identification"]
    assert res_aug["rank_augmented"] == 2


def test_channel_experiment_unknown_eta_partial_identification():
    """Verify Theorem G.2: Unknown eta without Q leaves ray ambiguity; known Q recovers (eta, q)."""
    from research_extension.mm_revision.identities import recover_unknown_eta_and_q
    U = np.array([[1.0, 0.0], [0.0, 1.0]])
    # Case 4: No aggregate Q known -> ray ambiguity
    res = analyze_channel_experiment_map(U, eta=None, aggregate_Q_known=False)
    assert not res["unique_identification"]
    assert "partially identified" in res["status_reason"]

    # Case 3: Known aggregate Q > 0 -> exact recovery of eta and q
    b = np.array([0.06, 0.02])
    Q = 0.4
    eta_est, q_est = recover_unknown_eta_and_q(U, b, Q)
    assert abs(eta_est - 0.2) < 1e-12
    assert np.allclose(q_est, [0.3, 0.1])


def test_boundary_condition_S_equals_1():
    """Test boundary condition S = 1 is marginally stable and classifies as ABSTAIN."""
    a = 0.4
    q = 0.6
    eta = 0.1
    J = build_transition_matrix(a, eta, q)
    rho = spectral_radius(J)
    assert abs(rho - 1.0) < 1e-12
    assert abs(total_feedback_gain(a, q) - 1.0) < 1e-12

    # Interval centered at 1.0 must abstain
    decision = classify_interval(0.95, 1.05, threshold=1.0)
    assert decision == DecisionLabel.ABSTAIN


def test_zero_feedback_regime():
    """Test zero feedback Q = 0 yields pure AR(1) price responses h_j = a^j."""
    a = 0.5
    eta = 0.1
    q = 0.0
    h, beta = compute_impulse_response(a, eta, q, kappa=1.0, H=10)
    for j in range(len(h)):
        assert abs(h[j] - (a ** j)) < 1e-12


def test_decision_denominators_and_undefined_conditional_error():
    """Verify conditional error is properly None when no decisions are issued."""
    records = [
        {"is_covered": True, "is_issued": False, "is_wrong": False, "is_abstain": True, "is_conflict": False},
        {"is_covered": True, "is_issued": False, "is_wrong": False, "is_abstain": True, "is_conflict": False},
    ]
    metrics = aggregate_decision_metrics(records)
    assert metrics.total_panels == 2
    assert metrics.issued_decisions == 0
    assert metrics.decisiveness_pct == 0.0
    assert metrics.conditional_error_pct is None  # Undefined, not 0!

    # Now add one correct and one wrong issued decision
    records.append({"is_covered": True, "is_issued": True, "is_wrong": False, "is_abstain": False, "is_conflict": False})
    records.append({"is_covered": False, "is_issued": True, "is_wrong": True, "is_abstain": False, "is_conflict": False})
    metrics2 = aggregate_decision_metrics(records)
    assert metrics2.total_panels == 4
    assert metrics2.issued_decisions == 2
    assert metrics2.wrong_decisions == 1
    assert abs(metrics2.decisiveness_pct - 50.0) < 1e-12
    assert abs(metrics2.unconditional_error_pct - 25.0) < 1e-12
    assert abs(metrics2.conditional_error_pct - 50.0) < 1e-12
