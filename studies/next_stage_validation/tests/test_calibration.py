from __future__ import annotations

import csv
from pathlib import Path

from mm_next.calibration import load_kline_csv, split_time_series, summarize_calibration


def test_calibration_loader_has_time_ordered_holdout(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["open_time", "open", "high", "low", "close", "volume"])
        for i in range(10):
            writer.writerow([i, 100 + i, 101 + i, 99 + i, 100.5 + i, 10 + i])
    frame = load_kline_csv(path)
    train, validation, test = split_time_series(frame, train_fraction=0.6, validation_fraction=0.2)
    summary = summarize_calibration(train, validation, test)
    assert len(train) == 6 and len(validation) == 2 and len(test) == 2
    assert summary["time_ordered"] is True
    assert summary["targets"]["close"] > 0
