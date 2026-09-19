"""Small reproducible noisy/dependent observation dataset generator."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ObservationConfig:
    episodes: int = 128
    horizon: int = 64
    seed: int = 0
    dependent: bool = False
    noise_sd: float = 0.05
    missing_rate: float = 0.0
    partial_fill_rate: float = 0.15
    fee_rate: float = 0.001

    def validate(self) -> None:
        if self.episodes <= 0 or self.horizon <= 0:
            raise ValueError("episodes and horizon must be positive")
        if self.noise_sd < 0 or not 0 <= self.missing_rate < 1:
            raise ValueError("noise and missingness rates must be nonnegative and bounded")
        if not 0 <= self.partial_fill_rate <= 1 or self.fee_rate < 0:
            raise ValueError("fill and fee rates are invalid")


def generate_dataset(config: ObservationConfig, output: Path) -> dict[str, np.ndarray]:
    config.validate()
    rng = np.random.default_rng(config.seed)
    n = config.episodes * config.horizon
    episode_id = np.repeat(np.arange(config.episodes), config.horizon)
    timestamp = np.tile(np.arange(config.horizon), config.episodes)
    reset_id = episode_id.copy()
    regime_by_episode = rng.integers(0, 3, size=config.episodes)
    market_regime = regime_by_episode[episode_id]
    request = rng.choice(np.array([-1.0, 1.0]), size=n) * 0.25
    fill_fraction = rng.uniform(1.0 - config.partial_fill_rate, 1.0, size=n)
    filled = request * fill_fraction
    quote = np.empty(n)
    quote[0] = 100.0
    innovations = rng.normal(0.0, 0.02, size=n)
    for row in range(1, n):
        previous = quote[row - 1]
        if episode_id[row] != episode_id[row - 1]:
            previous = 100.0
        persistence = 0.85 if config.dependent else 0.0
        quote[row] = 100.0 + persistence * (previous - 100.0) + innovations[row]
    impact = 0.01 * filled
    execution_price = quote + impact + rng.normal(0.0, config.noise_sd, size=n)
    slippage = np.abs(execution_price - quote)
    fees = config.fee_rate * np.abs(filled) * execution_price
    inventory = np.zeros(n)
    cash = np.zeros(n)
    margin = np.zeros(n)
    for row in range(n):
        previous_inventory = inventory[row - 1] if row and episode_id[row] == episode_id[row - 1] else 0.0
        previous_cash = cash[row - 1] if row and episode_id[row] == episode_id[row - 1] else 0.0
        inventory[row] = previous_inventory + filled[row]
        cash[row] = previous_cash - filled[row] * execution_price[row] - fees[row]
        margin[row] = np.abs(inventory[row] * quote[row]) * 0.1
    missingness = rng.random(n) < config.missing_rate
    observed_execution = execution_price.copy()
    observed_execution[missingness] = np.nan
    event_label = (margin > 0.5).astype(np.int8)
    outcome = cash + inventory * quote
    data: dict[str, np.ndarray] = {
        "episode_id": episode_id,
        "timestamp": timestamp,
        "market_regime": market_regime,
        "order_request": request,
        "filled_quantity": filled,
        "quote": quote,
        "execution_price": observed_execution,
        "slippage": slippage,
        "fees": fees,
        "inventory": inventory,
        "cash": cash,
        "margin": margin,
        "reset_id": reset_id,
        "observation_noise": np.full(n, config.noise_sd),
        "missingness": missingness,
        "event_label": event_label,
        "outcome": outcome,
    }
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output, **data)
    return data


def summarize_dataset(data: dict[str, np.ndarray]) -> dict[str, Any]:
    episode_ids = np.asarray(data["episode_id"])
    episodes = int(np.unique(episode_ids).size)
    missing = np.asarray(data["missingness"], dtype=bool)
    return {
        "episodes": episodes,
        "rows": int(len(episode_ids)),
        "horizon": int(len(episode_ids) // episodes),
        "missing_fraction": float(missing.mean()),
        "total_cost": float(np.nansum(np.asarray(data["slippage"]) + data["fees"])),
        "independent_episodes": bool(np.all(np.diff(np.unique(episode_ids)) == 1)),
        "dependent_rows_within_episode": bool(np.unique(data["market_regime"]).size <= 3),
    }

