"""Dependency-light loader and held-out summary for public kline data."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Sequence
import zipfile

import numpy as np


KLINE_FIELDS = (
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "trade_count", "taker_buy_base", "taker_buy_quote", "ignored",
)


def _parse_rows(rows: Iterable[Sequence[str]]) -> list[dict[str, float]]:
    parsed: list[dict[str, float]] = []
    for row in rows:
        if not row or row[0] == "open_time":
            continue
        if len(row) < 6:
            raise ValueError("kline rows need at least six columns")
        values = {name: float(row[index]) for index, name in enumerate(KLINE_FIELDS[:len(row)])}
        parsed.append(values)
    if not parsed:
        raise ValueError("no kline rows found")
    return parsed


def load_kline_csv(path: Path) -> list[dict[str, float]]:
    with Path(path).open(newline="") as handle:
        return _parse_rows(csv.reader(handle))


def load_kline_zip(path: Path) -> list[dict[str, float]]:
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(names) != 1:
            raise ValueError(f"expected exactly one CSV in {path}, found {names}")
        with archive.open(names[0]) as handle:
            lines = (line.decode("utf-8") for line in handle)
            return _parse_rows(csv.reader(lines))


def split_time_series(
    rows: Sequence[dict[str, float]],
    *,
    train_fraction: float = 0.6,
    validation_fraction: float = 0.2,
) -> tuple[list[dict[str, float]], list[dict[str, float]], list[dict[str, float]]]:
    if not 0 < train_fraction < 1 or not 0 <= validation_fraction < 1:
        raise ValueError("invalid split fractions")
    if train_fraction + validation_fraction >= 1:
        raise ValueError("train and validation fractions must leave a test set")
    rows = list(rows)
    n_train = int(len(rows) * train_fraction)
    n_validation = int(len(rows) * validation_fraction)
    if min(n_train, n_validation, len(rows) - n_train - n_validation) <= 0:
        raise ValueError("each split must contain at least one row")
    return rows[:n_train], rows[n_train:n_train + n_validation], rows[n_train + n_validation:]


def summarize_calibration(
    train: Sequence[dict[str, float]],
    validation: Sequence[dict[str, float]],
    test: Sequence[dict[str, float]],
) -> dict[str, object]:
    all_rows = [*train, *validation, *test]
    timestamps = [row["open_time"] for row in all_rows]
    close = np.asarray([row["close"] for row in all_rows], dtype=float)
    volume = np.asarray([row["volume"] for row in all_rows], dtype=float)
    log_returns = np.diff(np.log(close))
    return {
        "rows": {"train": len(train), "validation": len(validation), "test": len(test)},
        "time_ordered": bool(np.all(np.diff(timestamps) >= 0)),
        "targets": {
            "close": float(np.mean(close)),
            "close_return_volatility": float(np.std(log_returns)) if len(log_returns) else 0.0,
            "mean_volume": float(np.mean(volume)),
            "median_volume": float(np.median(volume)),
            "mean_intrabar_range": float(np.mean([
                (row["high"] - row["low"]) / max(row["close"], 1e-12) for row in all_rows
            ])),
        },
        "split_policy": "chronological 60/20/20; no shuffling",
    }
