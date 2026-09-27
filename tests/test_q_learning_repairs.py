"""Regression checks for the 2026-09-26 accounting and inference correction."""
import copy
import numpy as np
import pytest

from research_extension.learned_agents.q_learning_env import DiscreteTradingEnv, MarketConfig
from research_extension.learned_agents.q_learning_agent import QLearningAgent
from research_extension.learned_agents.train_q_learning import evaluate_policy
from research_extension.learned_agents.evaluate_q_learning import estimate_local_jacobian, audit_model_class_validity
from research_extension.evidence_repair.run_learned_agents import run, mean_interval


def test_cash_and_shares_are_conserved_with_counterparties():
    env = DiscreteTradingEnv(MarketConfig(phi=0, sigma_noise=0))
    env.step(4)
    # Dealer sells two units at 100.04 plus a .005 half spread.
    assert env.dealer_cash == pytest.approx(10200.09)
    assert env.agent_cash == pytest.approx(9799.91)
    assert env.agent_inv + env.dealer_inv == 0


def test_background_orders_obey_same_capacity_and_halt_is_absorbing():
    env = DiscreteTradingEnv(MarketConfig(max_inventory=1, phi=2, sigma_noise=0, max_steps=4))
    env.x = -10
    _, _, done, _ = env.step(2)
    assert abs(env.dealer_inv) <= 1
    assert env.dealer_halted
    assert not done  # fixed horizon, including post-halt marks
    before = (env.agent_inv, env.dealer_inv, env.agent_cash, env.dealer_cash)
    for _ in range(3):
        _, _, done, info = env.step(4)
        assert info['net_flow'] == 0
    assert done
    assert before == (env.agent_inv, env.dealer_inv, env.agent_cash, env.dealer_cash)


def test_reversal_can_cross_zero_inventory_before_partial_fill():
    env = DiscreteTradingEnv(MarketConfig(max_inventory=1, phi=0, sigma_noise=0))
    env.step(1)  # customer sells one, dealer at +1
    _, _, _, info = env.step(4)  # buy two: dealer may reach -1
    assert info['agent_trade'] == 2
    assert env.dealer_inv == -1
    assert not env.dealer_halted


def test_validation_does_not_advance_training_random_stream():
    agent = QLearningAgent(seed=7)
    before = copy.deepcopy(agent.rng.bit_generator.state)
    evaluate_policy(agent, [901], n_episodes=1)
    assert agent.rng.bit_generator.state == before
    assert agent.mode == 'active'


def test_untrained_audit_abstains_and_does_not_consume_randomness():
    agent = QLearningAgent(seed=7)
    before = copy.deepcopy(agent.rng.bit_generator.state)
    jac = estimate_local_jacobian(agent, MarketConfig())
    audit = audit_model_class_validity(agent, jac)
    assert audit['classification'] == 'NON_CERTIFIABLE_SUPPORT'
    assert agent.rng.bit_generator.state == before
    assert jac['actions_chosen'] == [0.] * 6  # mean over tied greedy actions
    assert jac['dq_dx'] is None
    assert jac['effective_local_persistence'] is None


def test_checkpoint_roundtrip_retains_support_and_random_state(tmp_path):
    a = QLearningAgent(learning_rate=.03, discount_factor=.9, seed=5)
    a.update(100, 1, 2., 101, False)
    path = tmp_path / 'checkpoint.npz'
    a.save(path)
    b = QLearningAgent(seed=900)
    b.load(path)
    assert b.lr == .03 and b.gamma == .9
    assert b.visit_counts[100, 1] == 1
    assert b.rng.bit_generator.state == a.rng.bit_generator.state


def test_constant_supported_zero_response_is_not_class_violation():
    a = QLearningAgent()
    a.q_table[:, 2] = 1
    if hasattr(a, 'visit_counts'):
        a.visit_counts[:] = 20
    audit = audit_model_class_validity(a, estimate_local_jacobian(a, MarketConfig()))
    assert audit['classification'] == 'NON_CERTIFIABLE_ZERO_RESPONSE'
    assert audit['r_squared'] is None


def test_locked_run_directory_cannot_be_overwritten(tmp_path):
    with pytest.raises(FileExistsError):
        run(tmp_path)


def test_population_interval_uses_population_means():
    result = mean_interval([1., 2., 3.])
    assert result['mean'] == 2.
    assert result['populations'] == 3
    assert result['ci95'] == pytest.approx([-.484137711719545, 4.484137711719546])


def test_all_party_conservation_on_random_path():
    env = DiscreteTradingEnv(MarketConfig(max_inventory=3), seed=88)
    for i in range(128):
        _, _, _, info = env.step(i % 5, -2 if i == 16 else 0)
        assert abs(info['cash_residual']) < 1e-8
        assert abs(info['inventory_residual']) < 1e-10
        assert abs(env.dealer_inv) <= 3 + 1e-10
