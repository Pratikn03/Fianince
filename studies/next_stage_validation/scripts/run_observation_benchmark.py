#!/usr/bin/env python3
"""Run the noisy/dependent observation coverage benchmark."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mm_next.observation_benchmark import ObservationBenchmarkConfig, run_condition  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "results")
    parser.add_argument("--replicates", type=int, default=200)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    config = ObservationBenchmarkConfig(replicates=args.replicates, seed=808)
    hard_budget = ObservationBenchmarkConfig(
        replicates=args.replicates,
        episodes=16,
        horizon=4,
        threshold=0.70,
        seed=1808,
    )
    conditions = {
        "exact_independent": run_condition(config, dependent=False, noise_sd=0.0),
        "noisy_independent": run_condition(config, dependent=False, noise_sd=0.10),
        "noisy_dependent": run_condition(config, dependent=True, noise_sd=0.10),
        "noisy_dependent_missing": run_condition(config, dependent=True, noise_sd=0.10, missing_rate=0.15),
        "constrained_noisy_dependent": run_condition(
            hard_budget, dependent=True, noise_sd=0.30, missing_rate=0.20
        ),
    }
    report = {
        "schema": "mm-next-observation-benchmark-1",
        "conditions": conditions,
        "interpretation": "Coverage is simulation-calibrated for the declared observation law; it is not a theorem or real-market estimate.",
    }
    (args.output / "observation_benchmark.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(args.output.resolve()), "conditions": len(conditions)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
