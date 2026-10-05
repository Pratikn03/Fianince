from __future__ import annotations

import numpy as np

from mm_next.agents import AdaptiveLinearAgent, FixedRuleAgent, NeuralPolicy


def test_matched_agents_obey_the_same_action_contract() -> None:
    observation = np.array([0.01, -0.02, 0.0, 0.1, 0.2, 0.05, 0.0])
    agents = [FixedRuleAgent(), AdaptiveLinearAgent(), NeuralPolicy.random(seed=3)]
    actions = [agent.act(observation) for agent in agents]
    assert all(np.isfinite(action) and -1.0 <= action <= 1.0 for action in actions)