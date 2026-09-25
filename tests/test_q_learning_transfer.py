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
    assert audit["classification"] in ("CERTIFIED_MODEL_CLASS", "OUTSIDE_CERTIFIED_MODEL_CLASS")
    assert "r_squared" in audit
    assert "sign_consistent" in audit


def test_transfer_results_artifact_exists():
    assert RESULTS_JSON.exists(), f"Missing {RESULTS_JSON}"
    with open(RESULTS_JSON) as f:
        data = json.load(f)
    assert "rule_based_baseline" in data
    assert "learned_policies" in data
    assert "architecture_transfer_synthesis" in data
    assert len(data["learned_policies"]) >= 1
