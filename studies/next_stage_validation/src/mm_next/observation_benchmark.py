"""Synthetic coverage benchmark for noisy and dependent observations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .observation_estimators import bootstrap_slope_interval, fit_slope


@dataclass(frozen=True)
class ObservationBenchmarkConfig:
    theta: float = 0.75
    threshold: float = 0.50
    replicates: int = 100
    episodes: int = 64
    horizon: int = 8
    seed: int = 0

    def validate(self) -> None:
        if self.replicates <= 0 or self.episodes < 2 or self.horizon <= 0:
            raise ValueError("benchmark sizes must be positive")


def _simulate(
    config: ObservationBenchmarkConfig,
    rng: np.random.Generator,
    *,
    dependent: bool,
    noise_sd: float,
    missing_rate: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = config.episodes * config.horizon
    episode_ids = np.repeat(np.arange(config.episodes), config.horizon)
    latent = np.zeros(n)
    for index in range(n):
        if index == 0 or episode_ids[index] != episode_ids[index - 1]:
            latent[index] = rng.normal()
        elif dependent:
            latent[index] = 0.8 * latent[index - 1] + rng.normal(scale=0.6)
        else:
            latent[index] = rng.normal()
    response = config.theta * latent + rng.normal(scale=noise_sd, size=n)
    observed_x = latent + rng.normal(scale=noise_sd, size=n)
    observed_y = response + rng.normal(scale=noise_sd, size=n)
    missing = rng.random(n) < missing_rate
    observed_x[missing] = np.nan
    observed_y[missing] = np.nan
    return observed_x, observed_y, episode_ids


def run_condition(
    config: ObservationBenchmarkConfig,
    *,
    dependent: bool,
    noise_sd: float,
    missing_rate: float = 0.0,
) -> dict[str, Any]:
    config.validate()
    rng = np.random.default_rng(config.seed)
    covered = 0
    decisive = 0
    wrong_confident = 0
    estimates: list[float] = []
    for replicate in range(config.replicates):
        x, y, episodes = _simulate(
            config,
            rng,
            dependent=dependent,
            noise_sd=noise_sd,
            missing_rate=missing_rate,
        )
        estimate = fit_slope(x, y)
        lower, upper = bootstrap_slope_interval(
            x, y, episodes, seed=config.seed + replicate, repetitions=300
        )
        if np.isfinite(estimate):
            estimates.append(estimate)
        if np.isfinite(lower) and lower <= config.theta <= upper:
            covered += 1
        if np.isfinite(lower) and (lower > config.threshold or upper < config.threshold):
            decisive += 1
            if upper < config.threshold:
                wrong_confident += 1
    return {
        "replicates": config.replicates,
        "episodes": config.episodes,
        "horizon": config.horizon,
        "dependent": dependent,
        "noise_sd": noise_sd,
        "missing_rate": missing_rate,
        "coverage": covered / config.replicates,
        "decisive_fraction": decisive / config.replicates,
        "wrong_confident_fraction": wrong_confident / config.replicates,
        "unresolved_fraction": 1.0 - decisive / config.replicates,
        "mean_estimate": float(np.mean(estimates)) if estimates else float("nan"),
        "target": config.theta,
        "threshold": config.threshold,
        "counting_unit": "episode; block bootstrap resamples complete episodes",
    }
