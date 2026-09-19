"""Paired operational-risk interventions for the independent environment."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np

from .market import MarketConfig, MarketTape, SyntheticMarket, make_tape


class _IntervenedPolicy:
    def __init__(self, base: Any, mode: str) -> None:
        self.base = base
        self.mode = mode

    def act(self, observation: np.ndarray) -> float:
        action = float(self.base.act(observation))
        if self.mode == "none":
            return action
        if self.mode == "throttle":
            return 0.5 * action
        if self.mode == "liquidate":
            inventory = float(observation[1])
            if inventory > 0.10:
                return -min(0.8, inventory)
            if inventory < -0.10:
                return min(0.8, -inventory)
            return action
        raise ValueError(f"unknown intervention mode: {self.mode}")


def _run(config: MarketConfig, policy: _IntervenedPolicy, tape: MarketTape) -> dict[str, float | str]:
    environment = SyntheticMarket(config, tape=tape)
    observation = environment.reset()
    start_equity = environment.equity
    minimum_equity = start_equity
    while not environment.done:
        result = environment.step(policy.act(observation))
        observation = result.observation
        minimum_equity = min(minimum_equity, result.mark_to_market_equity)
    return {
        "gain": float(environment.equity - start_equity),
        "max_drawdown": float((start_equity - minimum_equity) / max(start_equity, 1e-12)),
        "event": str(environment.last_event),
    }


def evaluate_interventions(
    config: MarketConfig,
    base_agent: Any,
    *,
    episodes: int,
    seed: int,
) -> dict[str, Any]:
    if episodes <= 0:
        raise ValueError("episodes must be positive")
    modes = ("none", "throttle", "liquidate")
    rows: dict[str, list[dict[str, float | str]]] = defaultdict(list)
    for episode in range(episodes):
        tape = make_tape(config, seed + episode)
        for mode in modes:
            rows[mode].append(_run(config, _IntervenedPolicy(base_agent, mode), tape))
    policies: dict[str, dict[str, float]] = {}
    metrics: dict[str, list[dict[str, float | str]]] = {}
    for mode, mode_rows in rows.items():
        policies[mode] = {
            "mean_gain": float(np.mean([float(row["gain"]) for row in mode_rows])),
            "mean_max_drawdown": float(np.mean([float(row["max_drawdown"]) for row in mode_rows])),
            "event_rate": float(np.mean([row["event"] != "terminal" for row in mode_rows])),
        }
        metrics[mode] = mode_rows
    return {
        "episodes": episodes,
        "seed": seed,
        "paired_tape": True,
        "policies": policies,
        "episode_metrics": metrics,
        "operational_target": "nonterminal event rate with mean drawdown as a guardrail",
    }
