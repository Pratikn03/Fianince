"""
Unit and Deep RL Tests for Frontier 3: Continuous Deep MARL Population
======================================================================
Tests multi-agent PPO Actor-Critic training, emergent predatory co-adaptation,
and systemic drawdown suppression under AMIP RFC-001.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

torch = pytest.importorskip("torch")

from research_extension.marl.train_marl_amip_population import (
    ActorCritic,
    ContinuousLOBEnv,
    train_marl_population,
    run_marl_amip_pipeline,
    OUTPUT_FILE
)


class TestDeepMARLPopulation:
    def test_actor_critic_forward_dimensions(self):
        """Verify ActorCritic neural architecture and continuous distribution outputs."""
        net = ActorCritic(obs_dim=5, act_dim=1, hidden_dim=32)
        batch_obs = torch.randn(4, 5)
        dist, value = net(batch_obs)

        # Output checks
        assert dist.mean.shape == (4, 1)
        assert dist.stddev.shape == (4, 1)
        assert value.shape == (4, 1)

        # Sampled actions must be bounded within [-5.0, 5.0]
        action = dist.sample()
        assert torch.all(action >= -5.0) and torch.all(action <= 5.0)

    def test_continuous_lob_env_guard_activation(self):
        """Verify that ContinuousLOBEnv transitions states and enforces Kreiss radius."""
        env = ContinuousLOBEnv(n_agents=4, base_price=1000.0, guard_enabled=True)
        obs = env.reset()
        assert obs.shape == (4, 5)

        # Submit large aggressive selling actions (-4.0) exceeding Kreiss radius (1.5)
        large_sells = -4.0 * torch.ones(4)
        next_obs, rewards, done, info = env.step(large_sells.numpy())

        # Guard must log rejections/clamps
        assert info["rejections"] > 0
        assert info["price"] < 1000.0

    def test_marl_training_convergence_and_suppression(self):
        """Verify that AMIP suppresses predatory liquidation drawdown by > 30%."""
        unprot = train_marl_population(guard_enabled=False, n_episodes=50)
        guarded = train_marl_population(guard_enabled=True, n_episodes=50)

        assert unprot["max_drawdown_pct"] > guarded["max_drawdown_pct"]
        assert guarded["max_drawdown_pct"] < 10.0

    def test_end_to_end_pipeline_and_provenance(self):
        """Verify full execution and JSON provenance artifact persistence."""
        res = run_marl_amip_pipeline()
        assert OUTPUT_FILE.exists()
        with open(OUTPUT_FILE) as f:
            data = json.load(f)
        assert data["frontier"] == "Frontier 3: Continuous Deep Multi-Agent RL (Deep MARL)"
        assert data["predatory_cascade_eliminated"] is True
        assert data["drawdown_suppression_pct"] > 30.0
