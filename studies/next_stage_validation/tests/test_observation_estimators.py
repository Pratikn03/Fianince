from __future__ import annotations

import numpy as np

from mm_next.observation_estimators import bootstrap_slope_interval, fit_slope


def test_episode_bootstrap_interval_uses_episode_units() -> None:
    x = np.asarray([1.0, 1.0, 2.0, 2.0, 3.0, 3.0])
    y = 0.5 * x
    episodes = np.asarray([0, 0, 1, 1, 2, 2])
    estimate = fit_slope(x, y)
    interval = bootstrap_slope_interval(x, y, episodes, seed=4, repetitions=200)
    assert abs(estimate - 0.5) < 1e-12
    assert interval[0] <= estimate <= interval[1]
