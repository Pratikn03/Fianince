from __future__ import annotations

import sys
from pathlib import Path

from mm_next.agents import TrainingConfig, train_neural_policy
from mm_next.evaluation import evaluate_matched_agents
from mm_next.market import MarketConfig

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_training import run as run_training  # noqa: E402


def test_training_is_seed_reproducible_and_evaluation_is_paired() -> None:
    market = MarketConfig(horizon=12, seed=11)
    config = TrainingConfig(iterations=3, population=6, seed=19)
    first = train_neural_policy(market, config)
    second = train_neural_policy(market, config)
    assert first.weights_digest == second.weights_digest

    report = evaluate_matched_agents(market, first.policy, episodes=4, seed=23)
    assert report["episodes"] == 4
    assert set(report["agents"]) == {"fixed_rule", "adaptive_linear", "frozen_neural"}
    assert report["paired_tape"] is True
    assert len(report["episode_metrics"]["fixed_rule"]) == 4


def test_training_report_accepts_output_outside_repository(tmp_path: Path) -> None:
    report = run_training(tmp_path, training_seeds=[3], episodes=2)
    assert report["results"][0]["weights_path"].startswith("/")
