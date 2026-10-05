"""Paired evaluation with common public market tapes."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np

from .agents import AdaptiveLinearAgent, FixedRuleAgent, NeuralPolicy
from .market import MarketConfig, MarketTape, SyntheticMarket, make_tape


def _run_episode(config: MarketConfig, agent: Any, tape: MarketTape) -> dict[str, Any]:
    environment = SyntheticMarket(config, tape=tape)
    observation = environment.reset()
    start_equity = environment.equity
    minimum_equity = start_equity
    actions = []
    while not environment.done:
        action = float(agent.act(observation))
        actions.append(action)
        result = environment.step(action)
        observation = result.observation
        minimum_equity = min(minimum_equity, result.mark_to_market_equity)
    return {
        "final_equity": float(environment.equity),
        "gain": float(environment.equity - start_equity),
        "max_drawdown": float((start_equity - minimum_equity) / max(start_equity, 1e-12)),
        "event": environment.last_event,
        "actions": actions,
    }


def evaluate_matched_agents(
    config: MarketConfig,
    frozen_policy: NeuralPolicy,
    *,
    episodes: int,
    seed: int,
) -> dict[str, Any]:
    if episodes <= 0:
        raise ValueError("episodes must be positive")
    agents = {
        "fixed_rule": FixedRuleAgent(),
        "adaptive_linear": AdaptiveLinearAgent(),
        "frozen_neural": frozen_policy,
    }
    rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for episode in range(episodes):
        tape = make_tape(config, seed + episode)
        for name, agent in agents.items():
            rows[name].append(_run_episode(config, agent, tape))
    aggregate: dict[str, dict[str, float]] = {}
    events: dict[str, dict[str, int]] = {}
    for name, agent_rows in rows.items():
        aggregate[name] = {
            "mean_gain": float(np.mean([row["gain"] for row in agent_rows])),
            "mean_final_equity": float(np.mean([row["final_equity"] for row in agent_rows])),
            "mean_max_drawdown": float(np.mean([row["max_drawdown"] for row in agent_rows])),
            "event_rate": float(np.mean([row["event"] not in {"terminal"} for row in agent_rows])),
        }
        counts: dict[str, int] = defaultdict(int)
        for row in agent_rows:
            counts[str(row["event"])] += 1
        events[name] = dict(counts)
    return {
        "episodes": episodes,
        "seed": seed,
        "paired_tape": True,
        "agents": aggregate,
        "event_counts": events,
        "episode_metrics": {
            name: [
                {
                    "gain": row["gain"],
                    "final_equity": row["final_equity"],
                    "max_drawdown": row["max_drawdown"],
                    "event": row["event"],
                }
                for row in agent_rows
            ]
            for name, agent_rows in rows.items()
        },
    }
