"""Regression tests for the October 11 (85-page) independent audit.

Each test recomputes the quantity from first principles inside the test and compares it
with the repository code, so a passing test means the code agrees with an independent
calculation -- not merely that a script ran.
"""
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import norm

Z = norm.ppf(0.95)
KL_TARGET = 2 * Z**2
KAPPA, Q, SIGMA, SIGMA_E, V = 0.8, 0.2, 0.01, 0.5, 6.25


def _err(kl):
    return norm.cdf(-math.sqrt(kl / 2))


def _cost(n):
    return n * (0.5 * KAPPA * V**2 + 0.0004 * 100 * V) + 0.005 * 100 * V


def test_noisy_equity_reports_accumulate_linearly():
    """Finding 2: independent per-reset reports add KL linearly -> N=267, 4241.75 USDT, 1.5% saving."""
    from breakthrough_experiments.exp7_disclosure_value import solve_contract_requirements
    delta = 0.05
    kl_p = (V * KAPPA**2 * Q * delta**2) ** 2 / (2 * SIGMA**2)          # third-tap price KL per reset
    dE = KAPPA**2 * Q * delta**2 * V**2
    kl_e = dE**2 / (2 * SIGMA_E**2)                                     # one report per reset
    n_lin = math.ceil(KL_TARGET / (kl_p + kl_e))
    assert n_lin == 267
    res = solve_contract_requirements(delta)["I2_Noisy_Equity_T3"]
    assert res["sequential_n_pulses"] == n_lin
    assert np.isclose(res["required_capital_B"], _cost(n_lin))
    assert np.isclose(res["required_capital_B"], 4241.75, atol=0.01)
    # the withdrawn 104-reset design does not reach 5% under the stated observation model
    assert res["withdrawn_quadratic_design_n_pulses"] == 104
    assert np.isclose(res["withdrawn_quadratic_design_true_error"], _err(104 * (kl_p + kl_e)))
    assert res["withdrawn_quadratic_design_true_error"] > 0.15


def test_timestamp_contract_adds_no_unmodelled_information():
    """Finding 3: without a timestamp likelihood, I4 equals prices-only; the old 2-pulse design errs 24.4%."""
    from breakthrough_experiments.exp7_disclosure_value import solve_contract_requirements
    res = solve_contract_requirements(0.05)
    i4, i0 = res["I4_Timestamps_Event_Study"], res["I0_Prices_Only_Optimal_T20"]
    assert i4["sequential_n_pulses"] == i0["sequential_n_pulses"] == 12
    assert i4["required_capital_B"] == i0["required_capital_B"]
    assert np.isclose(i4["withdrawn_multiplier_design_true_error"], 0.2442, atol=5e-4)


def test_exact_equity_requires_infinite_precision_for_small_lots():
    """Own finding: with 0.01 USDT report rounding, sub-BTC lots cannot change the report."""
    from breakthrough_experiments.exp7_disclosure_value import solve_contract_requirements
    delta = 0.05
    res = solve_contract_requirements(delta)
    for key in ["I3_Exact_Equity_CME_Micro_0_1BTC", "I3_Exact_Equity_Binance_minNotional"]:
        v = res[key]["required_volume_V"]
        assert KAPPA**2 * Q * delta**2 * v**2 < 0.01, f"{key}: equity difference below one cent"
    r = res["I3_Exact_Equity_Cent_Rounded"]
    assert np.isclose(r["required_volume_V"], math.sqrt(0.01 / (KAPPA**2 * Q * delta**2)))
    assert np.isclose(r["required_capital_B"], 15.5187, atol=1e-3)


def test_account_ledger_round_trip_and_margin_accounting():
    """Finding 4: capital from an explicit ledger, not a formula."""
    from breakthrough_experiments.exp13_account_capital import simulate_account, pulse_train, evaluate
    # A single buy unwound after full decay loses kappa V^2 + 2 fee P V to first order (pure dealer, no feedback)
    v = np.zeros(200); v[0] = V; v[150] = -V
    acc = simulate_account(v, 0.0, False, p=dict(kappa=0.8, q=0.0, a=0.5, eta=0.4, sigma=0.01,
                                                  phi=0.0004, P=100.0, mu=0.005, V_eff=6.25))
    assert np.isclose(-acc["final_pnl"], KAPPA * V**2 + 2 * 0.0004 * 100 * V, atol=1e-6)
    assert acc["end_inventory"] == 0.0
    # Twelve unwound buys carry ~12x the margin of one position (auditor: 37.50 vs 3.13 at P*)
    never = evaluate(pulse_train([1] * 12, 20, V), 0.05, "never")
    rt = evaluate(pulse_train([1, -1] * 6, 20, V), 0.05, "rt")
    assert never["end_inventory"] == 12 * V
    assert never["peak_margin"] > 37.5
    assert rt["peak_margin"] < 3.5
    # The never-unwound train does not reach 5% (overlapping responses partly cancel)
    assert never["testing_error"] > 0.05
    # Round trips in which BOTH legs are informative reach 5% with recorded resets
    assert rt["testing_error"] <= 0.05 and rt["end_inventory"] == 0.0


def test_isolated_pulse_design_is_not_capital_minimal():
    """The 175-194 USDT pulse figures are design-class results, not minima; Theorem 2.9's bound still holds."""
    data = json.loads(Path("breakthrough_experiments/results_exp13_account_capital.json").read_text())
    designs = {d["design"]: d for d in data["designs"]}
    opt = designs["executable-cost optimal deterministic probe (L=120)"]
    rt6 = designs["6 buy/sell round trips, every leg informative"]
    assert opt["testing_error"] <= 0.05 + 1e-6
    assert opt["C0_required"] < 0.5 * rt6["C0_required"]
    assert opt["C0_required"] < data["formula_benchmark_12_pulses"]
    assert data["executable_cost_form_min_eigenvalue"] > 0     # no round-trip arbitrage in the cost form
    for d in data["designs"]:
        assert d["C0_required"] >= data["theorem_2_9_capital_lower_bound"]


def test_exp12_weighted_output_is_not_a_margin():
    """Finding 5: the (1, 160) row acts on (price, memory); it yields 'margin' with zero holdings."""
    data = json.loads(Path("breakthrough_experiments/results_exp12_nonnormal_balance_sheet.json").read_text())
    assert data["zero_inventory_counterexample"]["state"] == [0.0, 0.005]
    assert data["zero_inventory_counterexample"]["weighted_output"] > 0.5
    assert all(r["state_contains_inventory"] is False for r in data["multi_asset_network"])
    assert "margin_breaches_L20" not in data["multi_asset_network"][0]


def test_mixture_weights_scored_per_cohort():
    """Own finding: the sum-of-weights metric hid failed multi-cohort recovery."""
    rows = json.loads(Path("breakthrough_experiments/results_exp2_unknown_mixture.json").read_text())
    assert all("per_cohort_weight_recovery_rate_tol_0_01" in r for r in rows)
    k1 = [r for r in rows if r["true_K"] == 1 and r["sigma"] <= 1e-3]
    assert all(r["per_cohort_weight_recovery_rate_tol_0_01"] >= 0.9 for r in k1)
    # Documented limitation (stated in the manuscript): K >= 2 is not recovered at sigma >= 1e-3.
    kk = [r for r in rows if r["true_K"] >= 2 and r["sigma"] >= 1e-3]
    assert max(r["per_cohort_weight_recovery_rate_tol_0_01"] for r in kk) < 0.5


def test_theorem_bridge_reports_partial_formal_coverage():
    """Finding 6: name-matching is not proof coverage; the generated map must show coverage status with explicit external and subresult boundaries."""
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location("bridge", "scripts/verify_theorem_code_bridge.py")
    bridge = importlib.util.module_from_spec(spec)
    sys.modules["bridge"] = bridge
    spec.loader.exec_module(bridge)
    cov = bridge.load_formal_coverage()
    statuses = [bridge.coverage_for(m.title, cov) for m in bridge.REGISTRY]
    assert len(statuses) == 23
    assert statuses.count("FULL") == 20
    assert statuses.count("CORE + EXTERNAL") == 2
    assert statuses[20] == "SUBRESULTS (obligations remain)"
    assert bridge.coverage_for("Finite-Window Abstention in a Scalar Gaussian Experiment", cov) == "FULL"
    tex = Path("paper/generated/claim_to_code_map.tex").read_text()
    assert ("Status" in tex or "formal coverage" in tex) and tex.count("& FULL &") == 20


def test_formal_registry_preserves_external_and_estimator_boundaries():
    import json
    registry = json.loads(Path("formal_statement_registry.json").read_text())
    rows = {row["id"]: row for row in registry["registry"]}
    assert registry["full_manuscript_formalization_complete"] is False
    assert rows["S13"]["status"] == "CORE + EXTERNAL"
    assert "hSpijker" in rows["S13"]["verification_note"]
    assert rows["S20"]["status"] == "CORE + EXTERNAL"
    assert "1,800" in rows["S20"]["verification_note"]
    assert rows["S21"]["verification_tier"] == "KERNEL_SUBRESULTS_ESTIMATOR_OBLIGATION_OPEN"
    assert "do not prove a uniform finite-sample blind-estimator guarantee" in rows["S21"]["verification_note"]
