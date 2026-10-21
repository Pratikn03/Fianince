"""Regression tests for Decision 2 (Option A microfoundations), Decision 4 (matched-shock 4-baseline comparison),
and Priority 1 / Priority 2 scientific verification requirements."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "microfoundation_and_baselines",
    ROOT / "ceiling_suite" / "bridge" / "microfoundation_and_baselines.py",
)
mb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mb)


def test_option_a_microfoundation_mapping_and_full_operator_stability():
    res = mb.run_microfoundation_analysis()
    regimes = {r["regime"]: r for r in res["regimes"]}

    # Every regime must verify matrix-power vs. step-by-step recursion equivalence to machine precision
    for r in res["regimes"]:
        assert r["recursion_vs_matrix_max_err"] < 1e-12
        assert r["schur_stable"] is (r["spectral_radius_J_full"] < 1.0 - 1e-12)
        if r["schur_stable"]:
            assert r["exact_stability_margin_1_minus_a_minus_tilde_kappa_Phi"] > 0.0
            assert r["summed_response_S_closed_form"] == pytest.approx(
                r["summed_response_S_resolvent"], rel=1e-12
            )
        else:
            assert r["exact_stability_margin_1_minus_a_minus_tilde_kappa_Phi"] <= 0.0

    # 1. High cost / tight inventory -> amplification disappears
    r_high = regimes["high_cost_amplification_disappears"]
    assert r_high["schur_stable"] is True
    assert r_high["spectral_radius_J_full"] < 0.85
    assert r_high["peak_overshoot_occurs"] is False
    assert r_high["C3_one_step_margin"] < 0.0

    # 2. Moderate cost, pure positive cohort (eps = 0) -> S rises above kappa/(1-a), but no peak overshoot
    r_mod = regimes["moderate_cost_positive_cohort_no_overshoot"]
    assert r_mod["schur_stable"] is True
    assert r_mod["spectral_radius_J_full"] < 0.95
    assert r_mod["peak_overshoot_occurs"] is False
    assert r_mod["summed_response_S"] == pytest.approx(5.0, abs=1e-9)

    # 3. Moderate cost with book depletion (eps > 0) -> genuinely Schur-stable (rho(J_full) < 1) AND peak overshoot h_1 > h_0
    r_dep = regimes["moderate_cost_with_depletion_overshoot_appears"]
    assert r_dep["schur_stable"] is True
    assert r_dep["spectral_radius_J_full"] < 1.0
    assert r_dep["C3_one_step_margin"] > 0.0
    assert r_dep["peak_overshoot_occurs"] is True
    assert r_dep["h1_next_step"] > r_dep["h0_impact"]
    assert r_dep["summed_response_S_closed_form"] == pytest.approx(1.90 / (1.0 - 0.40 - 1.90 * 0.24), rel=1e-12)

    # 4. Depletion-induced spectral instability -> cohort-only condition a + kappa * Phi < 1 holds,
    #    yet depth depletion drives rho(J_full) > 1 and schur_stable is False
    r_dep_inst = regimes["depletion_induced_spectral_instability"]
    assert r_dep_inst["cohort_only_condition_a_plus_kappa_Phi_lt_1"] is True
    assert r_dep_inst["spectral_radius_J_full"] > 1.0
    assert r_dep_inst["schur_stable"] is False

    # 5. Low cost / loose inventory -> cohort feedback instability (a + kappa * Phi >= 1)
    r_inst = regimes["low_cost_feedback_instability"]
    assert r_inst["schur_stable"] is False
    assert r_inst["spectral_radius_J_full"] > 1.0
    assert 0.40 + 1.0 * r_inst["Phi"] >= 1.0

    # Stateful inventory mean-reversion dampens cumulative response relative to neutral inventory
    st = res["stateful_inventory_and_cap_dynamics"]
    assert st["inventory_mean_reversion_dampens_sum"] is True
    assert st["stateful_sum_H"] < st["neutral_sum_H"]


def test_fixed_vs_adaptive_and_equilibrium_reoptimization_benchmarks():
    res = mb.run_microfoundation_analysis()
    benches = res["fixed_vs_adaptive_benchmarks"]
    assert len(benches) == 4
    for row in benches:
        assert row["reoptimization_reinforces_guard"] is True
        if row["alpha"] < 1.0:
            assert row["adaptive_policy_S_H30"] < row["fixed_policy_S_H30"]
            assert row["adaptive_policy_S_inf"] < row["fixed_policy_S_inf"]
            assert row["equilibrium_policy_S_H30"] < row["fixed_policy_S_H30"]
        else:
            assert row["equilibrium_policy_S_H30"] == pytest.approx(row["fixed_policy_S_H30"], rel=1e-9)


def test_decision_4_matched_capacity_and_risk_baselines():
    out = mb.simulate_matched_baselines(n_paths=400, horizon=40)
    proto = out["protocol"]
    assert proto["matched_shocks"] is True
    assert proto["matched_initial_conditions"] is True
    assert proto["matched_transaction_costs"] is True
    assert proto["matched_margin_rules"] is True
    assert proto["calibrated_on_independent_training_set"] is True

    # 1. Exact static theorem contract check
    static_ver = out["theorem_contract_static_verification"]
    assert static_ver["guard_at_alpha_star"]["reserve_breach_rate"] == 0.0
    assert static_ver["guard_at_alpha_star"]["maintenance_margin_breach_rate"] == 0.0
    assert static_ver["guard_at_alpha_star"]["max_loss_across_paths"] <= static_ver["budget_B"] + 1e-9
    assert static_ver["no_control_at_alpha_1"]["max_loss_across_paths"] > static_ver["budget_B"]

    # 2. Out-of-sample matched-capacity comparison
    comp = out["baseline_comparison"]
    required_policies = {"no_control", "inventory_cap", "volatility_limit", "margin_rule", "summed_gain_guard"}
    assert set(comp.keys()) == required_policies

    guard = comp["summed_gain_guard"]
    assert guard["reserve_breach_rate"] == 0.0
    assert guard["maintenance_margin_breach_rate"] == 0.0
    assert guard["forced_liquidation_rate"] == 0.0
    assert guard["double_entry_max_err"] < 1e-12

    for baseline in ["inventory_cap", "volatility_limit", "margin_rule"]:
        b = comp[baseline]
        assert b["double_entry_max_err"] < 1e-12
        # All calibrated active baselines must match the guard's mean trading capacity within 2%
        assert abs(b["trading_capacity_mean"] - guard["trading_capacity_mean"]) < 0.02
        # At matched capacity, the guard has lower max drawdown and lower tail loss ES95
        assert guard["max_drawdown_mean"] < b["max_drawdown_mean"]
        assert guard["tail_loss_es95"] < b["tail_loss_es95"]
        assert b["paired_diff_vs_guard"]["max_drawdown"]["ci95"][0] > 0.0
        assert b["paired_diff_vs_guard"]["tail_loss_es95"]["ci95"][0] > 0.0

    # 3. Matched-risk comparison: at matched ES95, guard admits strictly higher trading capacity and net P&L
    m_risk = out["matched_risk_comparison"]
    for baseline in ["inventory_cap", "volatility_limit", "margin_rule"]:
        assert m_risk["summed_gain_guard"]["trading_capacity_mean"] > m_risk[baseline]["trading_capacity_mean"]
        assert m_risk["summed_gain_guard"]["net_pnl_mean"] > m_risk[baseline]["net_pnl_mean"]

    # 4. Unfavorable heteroskedastic zero-feedback scenario: volatility_limit outperforms misspecified static-Phi^+ guard
    unfav = out["unfavorable_and_stress_scenarios"]["unfavorable_heteroskedastic_no_feedback"]
    assert unfav["volatility_limit_beats_guard_in_es95"] is True
    assert unfav["volatility_limit_beats_guard_in_pnl"] is True

    assert len(out["sensitivity_analysis"]) == 4
