#!/usr/bin/env python3
"""Evaluate predeclared operational interventions on paired held-out tapes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mm_next.agents import AdaptiveLinearAgent  # noqa: E402
from mm_next.interventions import evaluate_interventions  # noqa: E402
from mm_next.market import MarketConfig  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "results")
    parser.add_argument("--episodes", type=int, default=256)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    config = MarketConfig(
        horizon=48,
        initial_cash=50.0,
        max_order=1.0,
        max_inventory=1.0,
        volatility=0.02,
        impact=0.30,
        fee_rate=0.002,
        margin_rate=0.40,
        maintenance_margin=0.10,
        drawdown_limit=0.05,
        seed=707,
    )
    report = {
        "schema": "mm-next-intervention-results-1",
        "config": config.__dict__,
        "base_agent": "adaptive_linear",
        "results": evaluate_interventions(config, AdaptiveLinearAgent(), episodes=args.episodes, seed=20_000),
        "interpretation": "Synthetic held-out intervention evidence only; no real-market policy claim.",
    }
    (args.output / "intervention_results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(args.output.resolve()), "episodes": args.episodes}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
