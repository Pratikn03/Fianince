"""Tests for the Phase 1 through Phase 7A research extensions.

Verifies:
1. Swapped-feedback non-identifiability proposition (Proposition G.1)
2. Minimal separation theorem (Theorem G.2)
3. Noise model clarification (differenced vs level quote error)
4. Comprehensive 4-metric error calculation (including conditional error)
5. Economic mechanism and learning-frozen controls
"""

import numpy as np
import pytest
from research_extension.group_identification import (
    verify_swapped_feedback_proposition,
    verify_separation_theorem,
    verify_pbh_unobservability,
)
from research_extension.price_distance_clarification import analyze_noise_models
from research_extension.error_metrics_audit import compute_metrics, audit_table_benchmark
from research_extension.group_market import TwoGroupMarketSimulator, generate_group_study_dataset
from research_extension.group_inference import (
    estimate_channel_response,
    compute_group_intervals_lp,
    covariance_aware_output_error,
)
from research_extension.group_comparisons import evaluate_intervention_comparisons
from research_extension.economic_mechanism import FundedEconomicMarket


def test_swapped_feedback_proposition():
    res = verify_swapped_feedback_proposition(H=50)
    assert res["is_observationally_identical"]
    assert res["max_aggregate_price_response_diff"] < 1e-12
    # Verify suppression effects differ significantly:
    assert res["suppression_effect_difference"] > 0.15


def test_pbh_unobservability_rank_drop():
    res = verify_pbh_unobservability()
    assert res["rank_deficient"]
    assert res["rank_drop"] == 1
    assert res["is_unobservable_mode"]
    assert res["eigenvector_residual"] < 1e-14
    assert res["output_residual"] < 1e-14


def test_targeted_separation_theorem():
    res = verify_separation_theorem(H=50)
    assert res["is_separated"]
    # Ratio should be approximately 3:
    assert abs(res["target_response_peak_A"] / res["target_response_peak_B"] - 3.0) < 1e-4


def test_noise_models_clarification():
    results = analyze_noise_models()
    # At eta = 1e-4, check difference error vs level error match the documented numbers
    r_1e4 = [r for r in results if abs(r["eta"] - 1e-4) < 1e-8][0]
    assert abs(r_1e4["oracle_error_diff_pct"] - 7.45) < 0.1
    assert abs(r_1e4["oracle_error_level_pct"] - 27.02) < 0.1


def test_error_metrics_conditional_calculation():
    # Test Reviewer-cited Table 12 edge benchmark:
    m = compute_metrics(n_total=200, n_decisive=19, n_wrong=15)
    assert m["decisiveness_pct"] == 9.5
    assert m["unconditional_error_pct"] == 7.5
    assert abs(m["conditional_error_pct"] - 78.95) < 0.05


def test_group_market_and_split():
    ds = generate_group_study_dataset(n_panels=10, episodes_per_panel=16, T=16)
    assert ds["n_total"] == 10
    assert ds["n_discovery"] == 7
    assert ds["n_evaluation"] == 3


def test_group_inference_lp():
    sim = TwoGroupMarketSimulator(q_A=0.30, q_B=0.10, seed=42)
    episodes = [
        sim.run_episode(T=32, probe_mode="group_A", probe_sign=(1 if i % 2 == 0 else -1))
        for i in range(64)
    ]
    resp = estimate_channel_response(episodes)
    lp = compute_group_intervals_lp(resp)
    assert lp["q_lower"] <= 0.30 <= lp["q_upper"]


def test_favorable_homogeneous_comparison():
    homo = evaluate_intervention_comparisons(n_trials=10, episodes_per_trial=32, setting="homogeneous")
    # In homogeneous setting, all methods remove identical feedback on average
    assert abs(homo["response_based"]["mean_feedback_removed"] - homo["centrality_based"]["mean_feedback_removed"]) < 1e-5


def test_economic_mechanism_frozen_control():
    m = FundedEconomicMarket(q_A=0.15, q_B=0.03, phi=10.0, seed=123)
    r_learn = m.run_shock_trajectory(shock_magnitude=0.8, learning_enabled=True)
    r_froz = m.run_shock_trajectory(shock_magnitude=0.8, learning_enabled=False)
    # Learning-frozen trajectory must reduce cumulative price dislocation
    assert r_froz["cumulative_dislocation"] <= r_learn["cumulative_dislocation"]


def test_binance_multi_epoch_study():
    import json
    import os
    from research_extension.binance_multi_epoch_study import train_asset_multi_seed_multi_epoch

    results_file = "research_extension/outputs/binance_multi_epoch_results.json"
    cache_file = "research_extension/data/binance_market_data.json"
    
    assert os.path.exists(results_file), "Binance results file must exist"
    assert os.path.exists(cache_file), "Binance cache file must exist"

    with open(results_file, "r") as f:
        res = json.load(f)

    assert res["exchange"] == "Binance US"
    assert res["n_assets"] == 10
    assert res["n_seeds_per_asset"] == 5
    assert res["n_epochs_per_seed"] == 10
    assert res["total_optimization_runs"] == 500
    assert "mean_s_hat (Structural Feedback)" in res["coefficients"]
    assert len(res["asset_summary"]) == 10

    for a in res["asset_summary"]:
        assert a["mean_s_hat"] >= 0.0
        assert a["ci_95"][0] <= a["ci_95"][1]
        assert a["vol_bps_A"] > 0.0

    # Fast offline training test using cached data (2 seeds x 2 epochs)
    with open(cache_file, "r") as f:
        cached_data = json.load(f)
    assert "BTCUSDT" in cached_data
    fast_run = train_asset_multi_seed_multi_epoch(cached_data["BTCUSDT"], seeds=[42, 101], n_epochs=2)
    assert fast_run["n_seeds"] == 2
    assert fast_run["n_epochs"] == 2
    assert 0.0 < fast_run["mean_s_hat"] < 2.0


