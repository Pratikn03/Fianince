#!/usr/bin/env python3
"""Run the matched synthetic agent experiment with saved weights and metrics."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mm_next.agents import TrainingConfig, train_neural_policy  # noqa: E402
from mm_next.evaluation import evaluate_matched_agents  # noqa: E402
from mm_next.market import MarketConfig  # noqa: E402


def run(output: Path, *, training_seeds: list[int], episodes: int) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for seed in training_seeds:
        market = MarketConfig(seed=seed, horizon=48)
        training = train_neural_policy(
            market,
            TrainingConfig(iterations=8, population=24, episodes_per_candidate=3, seed=seed + 500),
        )
        weights_path = output / f"neural_policy_seed_{seed}.npz"
        import numpy as np

        np.savez_compressed(weights_path, weights=training.policy.vector())
        try:
            stored_weights_path = str(weights_path.relative_to(ROOT))
        except ValueError:
            stored_weights_path = str(weights_path)
        evaluation = evaluate_matched_agents(
            market,
            training.policy,
            episodes=episodes,
            seed=10_000 + seed,
        )
        rows.append(
            {
                "training_seed": seed,
                "weights_path": stored_weights_path,
                "weights_digest": training.weights_digest,
                "training_history": list(training.history),
                "evaluation": evaluation,
            }
        )
    report = {
        "schema": "mm-next-matched-agent-results-1",
        "experiment": "matched synthetic non-AI and trained-neural policies",
        "training_seeds": training_seeds,
        "evaluation_episodes_per_seed": episodes,
        "market_config": MarketConfig(horizon=48).__dict__,
        "results": rows,
        "interpretation": (
            "Controlled synthetic evidence only. The trained policy is not an AI-specific "
            "causal population and cannot support real-market or universal claims."
        ),
    }
    (output / "matched_agent_results.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "results")
    parser.add_argument("--episodes", type=int, default=64)
    parser.add_argument("--seeds", type=int, nargs="+", default=[101, 102, 103])
    args = parser.parse_args()
    report = run(args.output.resolve(), training_seeds=args.seeds, episodes=args.episodes)
    print(json.dumps({"output": str(args.output.resolve()), "runs": len(report["results"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
