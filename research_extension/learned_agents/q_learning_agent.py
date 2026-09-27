"""
Tabular Q-Learning Agent with Active / Frozen Execution Modes
=============================================================
Machine Markets — Learned-Agent Transfer Layer
"""
from __future__ import annotations
import numpy as np
import json
from pathlib import Path
from typing import Optional
from research_extension.learned_agents.q_learning_env import N_STATES, N_ACTIONS, ACTIONS


class QLearningAgent:
    """Tabular Q-learning agent supporting training, frozen evaluation, and online adaptation."""

    def __init__(
        self,
        learning_rate: float = 0.05,
        discount_factor: float = 0.98,
        epsilon_start: float = 1.0,
        epsilon_min: float = 0.02,
        epsilon_decay: float = 0.99995,
        seed: int = 42,
    ):
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.rng = np.random.default_rng(seed)

        # Q-table: 6,125 states x 5 actions
        self.q_table = np.zeros((N_STATES, N_ACTIONS), dtype=np.float64)
        self.mode = "active"  # 'active' (updates allowed) or 'frozen' (read-only)
        self.updates_count = 0
        self.visit_counts = np.zeros((N_STATES, N_ACTIONS), dtype=np.int64)
        self.support_recorded = True

    def select_action(self, state: int, greedy: bool = False) -> int:
        """Epsilon-greedy action selection."""
        if not greedy and self.rng.random() < self.epsilon:
            return int(self.rng.integers(0, N_ACTIONS))
        # Greedy choice with random tie-breaking
        q_row = self.q_table[state]
        max_q = np.max(q_row)
        candidates = np.flatnonzero(q_row == max_q)
        return int(self.rng.choice(candidates))

    def update(self, state: int, action: int, reward: float, next_state: int, done: bool):
        """Perform Bellman temporal-difference update if active."""
        if self.mode != "active":
            return

        target = reward
        if not done:
            target += self.gamma * np.max(self.q_table[next_state])

        td_error = target - self.q_table[state, action]
        self.q_table[state, action] += self.lr * td_error
        self.updates_count += 1
        self.visit_counts[state, action] += 1

        # Decay exploration
        if self.epsilon > self.epsilon_min:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def set_mode(self, mode: str):
        assert mode in ("active", "frozen"), f"Invalid mode: {mode}"
        self.mode = mode

    def save(self, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            filepath,
            q_table=self.q_table,
            epsilon=self.epsilon,
            updates_count=self.updates_count,
            visit_counts=self.visit_counts,
            support_recorded=self.support_recorded,
            metadata=json.dumps({"lr": self.lr, "gamma": self.gamma,
                "epsilon_min": self.epsilon_min, "epsilon_decay": self.epsilon_decay,
                "rng_state": self.rng.bit_generator.state, "mode": self.mode}),
        )

    def load(self, filepath: Path):
        with np.load(filepath, allow_pickle=False) as data:
            self.q_table = data["q_table"].copy()
            self.epsilon = float(data["epsilon"])
            self.updates_count = int(data["updates_count"])
            self.support_recorded = bool(data['support_recorded']) if 'support_recorded' in data else False
            self.visit_counts = data['visit_counts'].copy() if 'visit_counts' in data else np.zeros_like(self.q_table, dtype=np.int64)
            if 'metadata' in data:
                metadata = json.loads(str(data['metadata']))
                for key in ('lr', 'gamma', 'epsilon_min', 'epsilon_decay', 'mode'):
                    setattr(self, key, metadata[key])
                self.rng.bit_generator.state = metadata['rng_state']
