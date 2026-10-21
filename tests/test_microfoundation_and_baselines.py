"""Regression tests for Decision 2 (Option A microfoundations) and Decision 4 (matched-shock 4-baseline comparison)."""

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


def test_option_a_microfoundation_mapping_and_four_regimes():
    res = mb.run_microfoundation_analysis()
    regimes = {r["regime"]: r for r in res["regimes"]}

    # 1. High cost / tight inventory -> amplification disappears
    r_high = regimes["high_cost_amplification_disappears"]
    assert r_high["schur_stable"] is True
    assert r_high["peak_overshoot_occurs"] is False
    assert r_high["C3_one_step_margin"] < 0.0

    # 2. Moderate cost, pure positive cohort (eps = 0) -> S rises above kappa/(1-a), but no peak overshoot
    r_mod = regimes["moderate_cost_positive_cohort_no_overshoot"]
    assert r_mod["schur_stable"] is True
    assert r_mod["peak_overshoot_occurs"] is False
    assert r_mod["summed_response_S"] == pytest.approx(5.0, abs=1e-9)

    # 3. Moderate cost with book depletion (eps > 0) -> C_3 > 0 and peak overshoot h_1 > h_0 appears
    r_dep = regimes["moderate_cost_with_depletion_overshoot_appears"]
    assert r_dep["C3_one_step_margin"] > 0.0
    assert r_dep["peak_overshoot_occurs"] is True
    assert r_dep["h1_next_step"] > r_dep["h0_impact"]

    # 4. Low cost / loose inventory -> feedback instability (a + kappa * Phi >= 1)
    r_inst = regimes["low_cost_feedback_instability"]
    assert r_inst["schur_stable"] is False
    assert 0.40 + 1.0 * r_inst["Phi"] >= 1.0


def test_fixed_vs_adaptive_reoptimization_benchmark():
    res = mb.run_microfoundation_analysis()
    benches = res["fixed_vs_adaptive_benchmarks"]
    assert len(benches) == 4
    for row in benches:
        assert row["reoptimization_reinforces_guard"] is True
        if row["alpha"] < 1.0:
            assert row["adaptive_policy_S_H30"] < row["fixed_policy_S_H30"]
            assert row["adaptive_policy_S_inf"] < row["fixed_policy_S_inf"]


def test_decision_4_matched_shock_four_baselines():
    out = mb.simulate_matched_baselines(n_paths=400, horizon=40)
    proto = out["protocol"]
    assert proto["matched_shocks"] is True
    assert proto["matched_initial_conditions"] is True
    assert proto["matched_transaction_costs"] is True
    assert proto["matched_margin_rules"] is True

    comp = out["baseline_comparison"]
    required_policies = {"no_control", "inventory_cap", "volatility_limit", "margin_rule", "summed_gain_guard"}
    assert set(comp.keys()) == required_policies

    guard = comp["summed_gain_guard"]
    assert guard["forced_liquidation_rate"] == 0.0
    for baseline in ["no_control", "inventory_cap", "volatility_limit", "margin_rule"]:
        b = comp[baseline]
        assert guard["forced_liquidation_rate"] <= b["forced_liquidation_rate"]
        assert guard["max_drawdown_mean"] < b["max_drawdown_mean"]
        assert guard["tail_loss_es95"] < b["tail_loss_es95"]
        assert guard["net_pnl_mean"] > b["net_pnl_mean"]

    assert len(out["sensitivity_analysis"]) == 4
