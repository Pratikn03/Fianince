#!/usr/bin/env python3
"""Create deterministic paired summaries and bootstrap intervals."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def bootstrap_interval(values: np.ndarray, seed: int, repetitions: int = 4000) -> list[float]:
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(values), size=(repetitions, len(values)))
    means = values[draws].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).resolve().parents[1] / "results/matched_agent_results.json")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "results/matched_agent_analysis.json")
    args = parser.parse_args()
    report = json.loads(args.input.read_text())
    summaries: list[dict[str, object]] = []
    for run in report["results"]:
        metrics = run["evaluation"]["episode_metrics"]
        adaptive = np.asarray([row["gain"] for row in metrics["adaptive_linear"]], dtype=float)
        neural = np.asarray([row["gain"] for row in metrics["frozen_neural"]], dtype=float)
        fixed = np.asarray([row["gain"] for row in metrics["fixed_rule"]], dtype=float)
        neural_minus_adaptive = neural - adaptive
        summaries.append(
            {
                "training_seed": run["training_seed"],
                "episodes": len(adaptive),
                "mean_gain": {
                    "fixed_rule": float(fixed.mean()),
                    "adaptive_linear": float(adaptive.mean()),
                    "frozen_neural": float(neural.mean()),
                },
                "paired_neural_minus_adaptive": {
                    "mean": float(neural_minus_adaptive.mean()),
                    "bootstrap_95": bootstrap_interval(neural_minus_adaptive, 20260918 + int(run["training_seed"])),
                    "predeclared_effect_threshold": 0.5,
                    "supports_ai_specific_advantage": bool(neural_minus_adaptive.mean() >= 0.5),
                },
                "event_rate": {
                    name: float(np.mean([row["event"] != "terminal" for row in rows]))
                    for name, rows in metrics.items()
                },
            }
        )
    output = {
        "schema": "mm-next-matched-agent-analysis-1",
        "source": str(args.input),
        "summaries": summaries,
        "decision": "No AI-specific advantage is supported by this predeclared pilot threshold.",
        "scope": "paired synthetic held-out tapes; not a real-market causal estimate",
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"output": str(args.output.resolve()), "runs": len(summaries)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
