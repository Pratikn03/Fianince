"""Unit tests for Q-Learning learned-agent transfer layer and model validity audit."""
from pathlib import Path
import json
import pytest
import numpy as np

from research_extension.learned_agents.q_learning_env import (
    DiscreteTradingEnv, MarketConfig, discretize_state, ACTIONS
)
from research_extension.learned_agents.q_learning_agent import QLearningAgent
from research_extension.learned_agents.evaluate_q_learning import (
    estimate_local_jacobian,
    audit_model_class_validity,
    run_paired_trial,
    RuleBasedChartist,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS_JSON = ROOT / "research_extension" / "outputs" / "learned_agents" / "q_learning_transfer_results.json"


def test_discretize_state_bounds():
    s_min = discretize_state(-10.0, -10.0, -100.0, 0.0, -10.0)
    s_max = discretize_state(10.0, 10.0, 100.0, 1.0, 10.0)
    assert 0 <= s_min < 6125
    assert 0 <= s_max < 6125


def test_env_dealer_constraints():
    cfg = MarketConfig(max_inventory=5.0)
    env = DiscreteTradingEnv(config=cfg, seed=123)
    env.reset()
    # Large buy orders should eventually halt dealer
    for _ in range(10):
        _, _, done, info = env.step(4) # action index 4 = +2.0 units
        if done:
            break
    assert env.dealer_halted is True
    assert abs(env.dealer_inv) <= cfg.max_inventory + 2.0


def test_agent_active_frozen_modes():
    agent = QLearningAgent(seed=42)
    s = 100
    a = 2
    agent.set_mode("active")
    agent.update(s, a, 1.0, 101, False)
    assert agent.updates_count == 1
    assert agent.q_table[s, a] != 0.0

    agent.set_mode("frozen")
    prev_q = agent.q_table[s, a]
    agent.update(s, a, 5.0, 101, False)
    assert agent.updates_count == 1
    assert agent.q_table[s, a] == prev_q


def test_model_validity_classifier():
    cfg = MarketConfig()
    agent = QLearningAgent(seed=99)
    jac = estimate_local_jacobian(agent, cfg)
    audit = audit_model_class_validity(agent, jac)
    assert audit["classification"] == "NON_CERTIFIABLE_SUPPORT"
    assert "r_squared" in audit
    assert "sign_consistent" in audit


def test_transfer_results_artifact_exists():
    assert RESULTS_JSON.exists(), f"Missing {RESULTS_JSON}"
    with open(RESULTS_JSON) as f:
        data = json.load(f)
    assert "rule_based_baseline" in data
    assert "learned_policies" in data
    assert "architecture_transfer_synthesis" in data
    assert len(data["learned_policies"]) == 10
    assert "baselines" in data
    assert "do_nothing" in data["baselines"]
    assert "turnover_matched_static" in data["baselines"]


def test_audit_calibration_study_artifact():
    cal_file = ROOT / "research_extension" / "outputs" / "learned_agents" / "audit_calibration_results.json"
    assert cal_file.exists(), f"Missing {cal_file}"
    with open(cal_file) as f:
        data = json.load(f)
    assert "standard_threshold_0_70" in data
    assert "threshold_sweep" in data
    std = data["standard_threshold_0_70"]
    # Exact linear must pass 100%
    assert std["pass_rates"]["exact_linear"] == 1.0
    # Contrarian negative feedback must fail 100% (pass rate 0.0%)
    assert std["pass_rates"]["contrarian_linear"] == 0.0


def test_multiscale_audit_artifact():
    multi_file = ROOT / "research_extension" / "outputs" / "learned_agents" / "multiscale_audit_results.json"
    assert multi_file.exists(), f"Missing {multi_file}"
    with open(multi_file) as f:
        data = json.load(f)
    assert "summary_by_radius" in data
    assert "policy_results" in data
    assert len(data["policy_results"]) == 10
    assert len(data["summary_by_radius"]) == 5
    # Smallest radius (r=0.05) has 100% support and mean R^2 == 0.0 across all policies
    r_005 = data["summary_by_radius"][0]
    assert r_005["radius"] == 0.05
    assert r_005["r_squared_mean"] == 0.0


def test_reward_sensitivity_artifact():
    reward_file = ROOT / "research_extension" / "outputs" / "learned_agents" / "reward_sensitivity_results.json"
    assert reward_file.exists(), f"Missing {reward_file}"
    with open(reward_file) as f:
        data = json.load(f)
    assert "reward_specs" in data
    assert len(data["reward_specs"]) == 4
    labels = [spec["label"] for spec in data["reward_specs"]]
    assert "A_main" in labels
    assert "B_no_inv" in labels
    assert "C_no_turn" in labels
    assert "D_low_penalty" in labels
    # Verify that in all specifications, 0 policies are classified as in-class
    for spec in data["reward_specs"]:
        assert spec["n_in_class"] == 0

