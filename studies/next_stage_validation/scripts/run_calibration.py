#!/usr/bin/env python3
"""Summarize public Binance kline pilot data with a chronological holdout."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mm_next.calibration import load_kline_zip, split_time_series, summarize_calibration  # noqa: E402


def run(data_dir: Path, output: Path) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    summaries: dict[str, object] = {}
    for archive in sorted(data_dir.glob("*-*.zip")):
        rows = load_kline_zip(archive)
        train, validation, test = split_time_series(rows)
        summaries[archive.stem] = {
            "source": str(archive),
            "summary": summarize_calibration(train, validation, test),
        }
    report = {
        "schema": "mm-next-public-kline-calibration-1",
        "data_dir": str(data_dir),
        "assets": summaries,
        "status": "descriptive_kline_pilot_only",
        "limitation": (
            "The pilot contains OHLCV klines and does not validate historical L2 depth, "
            "queue priority, cancellations, or fill probabilities."
        ),
    }
    (output / "kline_calibration_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[3] / "research_extension/data/raw/binance/spot/klines",
    )
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "results")
    args = parser.parse_args()
    report = run(args.data_dir.resolve(), args.output.resolve())
    print(json.dumps({"output": str(args.output.resolve()), "assets": len(report["assets"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
