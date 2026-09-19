from pathlib import Path

import numpy as np

from research_extension.observation_study import (
    ObservationConfig,
    generate_dataset,
    summarize_dataset,
)


def test_dataset_has_declared_observation_schema(tmp_path: Path):
    config = ObservationConfig(episodes=12, horizon=8, seed=11, dependent=True)
    output = tmp_path / "observations.npz"
    data = generate_dataset(config, output)
    expected = {
        "episode_id", "timestamp", "market_regime", "order_request",
        "filled_quantity", "quote", "execution_price", "slippage", "fees",
        "inventory", "cash", "margin", "reset_id", "observation_noise",
        "missingness", "event_label", "outcome",
    }
    assert set(data) == expected
    assert output.is_file()
    assert len(data["episode_id"]) == 12 * 8


def test_dependent_data_reuses_episode_regime(tmp_path: Path):
    config = ObservationConfig(episodes=10, horizon=10, seed=3, dependent=True)
    data = generate_dataset(config, tmp_path / "dependent.npz")
    for episode in range(config.episodes):
        rows = data["episode_id"] == episode
        assert np.unique(data["market_regime"][rows]).size == 1
        assert np.all(data["reset_id"][rows] == episode)


def test_summary_reports_cost_and_missingness(tmp_path: Path):
    config = ObservationConfig(episodes=16, horizon=12, seed=4, noise_sd=0.2, missing_rate=0.1)
    data = generate_dataset(config, tmp_path / "summary.npz")
    summary = summarize_dataset(data)
    assert summary["episodes"] == 16
    assert 0 < summary["missing_fraction"] < 1
    assert summary["total_cost"] >= 0
    assert summary["independent_episodes"] is True
