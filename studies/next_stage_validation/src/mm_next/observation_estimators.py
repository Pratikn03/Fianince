"""Observation-law estimators with episode-level resampling."""
from __future__ import annotations

import numpy as np


def fit_slope(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    valid = np.isfinite(x) & np.isfinite(y)
    if valid.sum() < 2:
        return float("nan")
    x_valid = x[valid]
    y_valid = y[valid]
    centered = x_valid - x_valid.mean()
    denominator = float(centered @ centered)
    if denominator <= 1e-15:
        return float("nan")
    return float(centered @ (y_valid - y_valid.mean()) / denominator)


def bootstrap_slope_interval(
    x: np.ndarray,
    y: np.ndarray,
    episodes: np.ndarray,
    *,
    seed: int,
    repetitions: int = 2000,
) -> tuple[float, float]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    episodes = np.asarray(episodes)
    unique = np.unique(episodes)
    if unique.size < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    estimates: list[float] = []
    for _ in range(repetitions):
        selected = rng.choice(unique, size=unique.size, replace=True)
        masks = [episodes == episode for episode in selected]
        estimate = fit_slope(np.concatenate([x[mask] for mask in masks]), np.concatenate([y[mask] for mask in masks]))
        if np.isfinite(estimate):
            estimates.append(estimate)
    if not estimates:
        return (float("nan"), float("nan"))
    quantiles = np.quantile(np.asarray(estimates), [0.025, 0.975])
    return float(quantiles[0]), float(quantiles[1])
