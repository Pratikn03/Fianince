"""Matched non-AI and trained-policy agents for controlled evaluation."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Protocol

import numpy as np

from .market import MarketConfig, MarketTape, SyntheticMarket, make_tape


class Agent(Protocol):
    def act(self, observation: np.ndarray) -> float: ...


class FixedRuleAgent:
    """Non-adaptive null policy with no hidden state or training."""

    def act(self, observation: np.ndarray) -> float:
        del observation
        return 0.0


class AdaptiveLinearAgent:
    """Non-neural adaptive controller using the current public observation."""

    def __init__(self, return_gain: float = 3.0, inventory_gain: float = 1.5) -> None:
        self.return_gain = float(return_gain)
        self.inventory_gain = float(inventory_gain)

    def act(self, observation: np.ndarray) -> float:
        value = self.return_gain * float(observation[0]) - self.inventory_gain * float(observation[1])
        return float(np.tanh(value))


@dataclass(frozen=True)
class TrainingConfig:
    iterations: int = 8
    population: int = 24
    elite_fraction: float = 0.25
    mutation_sd: float = 0.15
    episodes_per_candidate: int = 3
    seed: int = 0

    def validate(self) -> None:
        if self.iterations <= 0 or self.population < 2 or self.episodes_per_candidate <= 0:
            raise ValueError("training sizes must be positive")
        if not 0 < self.elite_fraction <= 0.5 or self.mutation_sd <= 0:
            raise ValueError("elite_fraction or mutation_sd is invalid")


class NeuralPolicy:
    """Small deterministic tanh MLP used as a genuinely trained policy."""

    input_dim = 7
    hidden_dim = 8

    def __init__(self, vector: np.ndarray) -> None:
        expected = self.input_dim * self.hidden_dim + self.hidden_dim + self.hidden_dim + 1
        vector = np.asarray(vector, dtype=float)
        if vector.shape != (expected,):
            raise ValueError(f"policy vector must have shape {(expected,)}")
        self._vector = vector.copy()

    @classmethod
    def random(cls, seed: int) -> "NeuralPolicy":
        rng = np.random.default_rng(seed)
        size = cls.input_dim * cls.hidden_dim + cls.hidden_dim + cls.hidden_dim + 1
        return cls(rng.normal(0.0, 0.1, size=size))

    @classmethod
    def from_vector(cls, vector: np.ndarray) -> "NeuralPolicy":
        return cls(vector)

    def vector(self) -> np.ndarray:
        return self._vector.copy()

    @property
    def weights_digest(self) -> str:
        return hashlib.sha256(self._vector.astype("<f8").tobytes()).hexdigest()

    def act(self, observation: np.ndarray) -> float:
        vector = self._vector
        split1 = self.input_dim * self.hidden_dim
        split2 = split1 + self.hidden_dim
        split3 = split2 + self.hidden_dim
        weights = vector[:split1].reshape(self.input_dim, self.hidden_dim)
        bias = vector[split1:split2]
        output_weights = vector[split2:split3]
        output_bias = vector[split3]
        hidden = np.tanh(np.asarray(observation, dtype=float) @ weights + bias)
        return float(np.tanh(hidden @ output_weights + output_bias))


@dataclass(frozen=True)
class TrainingResult:
    policy: NeuralPolicy
    weights_digest: str
    history: tuple[dict[str, float], ...]


def _rollout_score(config: MarketConfig, policy: NeuralPolicy, tape: MarketTape) -> float:
    environment = SyntheticMarket(config, tape=tape)
    observation = environment.reset()
    start_equity = environment.equity
    minimum_equity = start_equity
    while not environment.done:
        result = environment.step(policy.act(observation))
        observation = result.observation
        minimum_equity = min(minimum_equity, result.mark_to_market_equity)
    terminal_gain = environment.equity - start_equity
    drawdown_penalty = max(0.0, start_equity - minimum_equity) * 0.5
    event_penalty = 2.0 if environment.last_event in {"default", "margin_breach", "drawdown_halt", "halt"} else 0.0
    return float(terminal_gain - drawdown_penalty - event_penalty)


def train_neural_policy(market: MarketConfig, config: TrainingConfig) -> TrainingResult:
    """Train with a deterministic cross-entropy population search.

    This is intentionally small and CPU-only. It is a trained neural policy,
    but the resulting experiment remains a synthetic controlled study.
    """
    config.validate()
    rng = np.random.default_rng(config.seed)
    mean = NeuralPolicy.random(config.seed).vector()
    history: list[dict[str, float]] = []
    elite_count = max(1, int(round(config.population * config.elite_fraction)))
    for iteration in range(config.iterations):
        candidates = rng.normal(mean, config.mutation_sd, size=(config.population, mean.size))
        scores = np.zeros(config.population)
        for index, candidate in enumerate(candidates):
            policy = NeuralPolicy.from_vector(candidate)
            scores[index] = np.mean(
                [
                    _rollout_score(market, policy, make_tape(market, config.seed + 1000 * iteration + episode))
                    for episode in range(config.episodes_per_candidate)
                ]
            )
        elite_indices = np.argsort(scores)[-elite_count:]
        mean = candidates[elite_indices].mean(axis=0)
        history.append(
            {
                "iteration": float(iteration),
                "best_score": float(scores.max()),
                "elite_mean": float(scores[elite_indices].mean()),
            }
        )
    policy = NeuralPolicy.from_vector(mean)
    return TrainingResult(policy=policy, weights_digest=policy.weights_digest, history=tuple(history))
