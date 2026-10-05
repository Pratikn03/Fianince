#!/usr/bin/env python3
"""Run all locally executable next-stage experiments."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
from run_calibration import run as run_calibration  # noqa: E402
from run_training import run as run_training  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE.parents[1] / "results")
    parser.add_argument("--episodes", type=int, default=64)
    args = parser.parse_args()
    output = args.output.resolve()
    run_training(output, training_seeds=[601, 602, 603], episodes=args.episodes)
    run_calibration(
        HERE.parents[3] / "research_extension/data/raw/binance/spot/klines",
        output,
    )
    print(f"wrote next-stage results to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
