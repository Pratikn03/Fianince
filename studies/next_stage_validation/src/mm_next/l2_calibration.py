"""Streaming diagnostics for Binance public depth-band and aggregate-trade archives.

The public ``bookDepth`` files contain depth bands, not order-level queue
updates. This module measures what the files expose and keeps queue-priority or
fill-probability claims explicitly outside the calibration scope.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re
from typing import Iterable, Iterator
import zipfile

import numpy as np


def _csv_member(archive: zipfile.ZipFile) -> str:
    names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
    if len(names) != 1:
        raise ValueError(f"expected one CSV member, found {names}")
    return names[0]


def _split_csv(line: str) -> list[str]:
    return line.rstrip("\r\n").split(",")


def iter_book_depth_rows(path: Path) -> Iterator[dict[str, object]]:
    with zipfile.ZipFile(path) as archive:
        with archive.open(_csv_member(archive)) as handle:
            header = _split_csv(handle.readline().decode("utf-8"))
            expected = ["timestamp", "percentage", "depth", "notional"]
            if header != expected:
                raise ValueError(f"unexpected bookDepth header: {header}")
            for raw in handle:
                values = _split_csv(raw.decode("utf-8"))
                if len(values) != 4:
                    raise ValueError("malformed bookDepth row")
                yield {
                    "timestamp": values[0],
                    "percentage": int(values[1]),
                    "depth": float(values[2]),
                    "notional": float(values[3]),
                }


def iter_agg_trade_rows(path: Path) -> Iterator[dict[str, object]]:
    with zipfile.ZipFile(path) as archive:
        with archive.open(_csv_member(archive)) as handle:
            header = _split_csv(handle.readline().decode("utf-8"))
            expected = [
                "agg_trade_id", "price", "quantity", "first_trade_id",
                "last_trade_id", "transact_time", "is_buyer_maker",
            ]
            if header != expected:
                raise ValueError(f"unexpected aggTrades header: {header}")
            for raw in handle:
                values = _split_csv(raw.decode("utf-8"))
                if len(values) != 7:
                    raise ValueError("malformed aggTrades row")
                yield {
                    "agg_trade_id": int(values[0]),
                    "price": float(values[1]),
                    "quantity": float(values[2]),
                    "first_trade_id": int(values[3]),
                    "last_trade_id": int(values[4]),
                    "transact_time": int(values[5]),
                    "is_buyer_maker": values[6].lower() == "true",
                }


def summarize_book_depth_rows(rows: Iterable[dict[str, object]]) -> dict[str, object]:
    current_timestamp: str | None = None
    current_levels: dict[int, tuple[float, float]] = {}
    snapshots: list[dict[int, tuple[float, float]]] = []

    def flush() -> None:
        if current_levels:
            snapshots.append(dict(current_levels))

    for row in rows:
        timestamp = str(row["timestamp"])
        if current_timestamp is not None and timestamp != current_timestamp:
            flush()
            current_levels.clear()
        current_timestamp = timestamp
        current_levels[int(row["percentage"])] = (float(row["depth"]), float(row["notional"]))
    flush()
    if not snapshots:
        raise ValueError("bookDepth archive has no snapshots")

    def mean_level(level: int, field: int) -> float | None:
        values = [snapshot[level][field] for snapshot in snapshots if level in snapshot]
        return float(np.mean(values)) if values else None

    coverage = {
        str(level): float(np.mean([level in snapshot for snapshot in snapshots]))
        for level in (-5, -1, 1, 5)
    }
    return {
        "snapshot_count": len(snapshots),
        "mean_levels_per_snapshot": float(np.mean([len(snapshot) for snapshot in snapshots])),
        "coverage": coverage,
        "mean_depth_minus_5pct": mean_level(-5, 0),
        "mean_depth_minus_1pct": mean_level(-1, 0),
        "mean_depth_plus_1pct": mean_level(1, 0),
        "mean_depth_plus_5pct": mean_level(5, 0),
        "mean_notional_minus_1pct": mean_level(-1, 1),
        "mean_notional_plus_1pct": mean_level(1, 1),
        "mean_notional_minus_5pct": mean_level(-5, 1),
        "mean_notional_plus_5pct": mean_level(5, 1),
        "source_units": "aggregate depth bands at percentage offsets",
    }


def summarize_trade_rows(rows: Iterable[dict[str, object]]) -> dict[str, object]:
    count = 0
    total_quantity = 0.0
    total_notional = 0.0
    signed_quantity = 0.0
    return_square_sum = 0.0
    return_count = 0
    impact_sum = 0.0
    flow_autocorrelation_sum = 0.0
    pair_count = 0
    previous_price: float | None = None
    previous_sign: float | None = None
    notional_sample: list[float] = []
    first_timestamp: int | None = None
    last_timestamp: int | None = None
    for row in rows:
        price = float(row["price"])
        quantity = float(row["quantity"])
        sign = -1.0 if bool(row["is_buyer_maker"]) else 1.0
        notional = price * quantity
        count += 1
        total_quantity += quantity
        total_notional += notional
        signed_quantity += sign * quantity
        timestamp = int(row["transact_time"])
        first_timestamp = timestamp if first_timestamp is None else first_timestamp
        last_timestamp = timestamp
        if len(notional_sample) < 100_000:
            notional_sample.append(notional)
        if previous_price is not None and previous_sign is not None and previous_price > 0 and price > 0:
            log_return = float(np.log(price / previous_price))
            return_square_sum += log_return * log_return
            impact_sum += previous_sign * log_return
            flow_autocorrelation_sum += previous_sign * sign
            return_count += 1
            pair_count += 1
        previous_price = price
        previous_sign = sign
    if count == 0:
        raise ValueError("aggTrades archive has no rows")
    return {
        "trade_count": count,
        "total_quantity": total_quantity,
        "total_notional": total_notional,
        "signed_quantity_imbalance": signed_quantity / max(total_quantity, 1e-12),
        "trade_notional_median_sample": float(np.median(notional_sample)),
        "trade_return_volatility_proxy": float(np.sqrt(return_square_sum / max(return_count, 1))),
        "signed_impact_proxy": impact_sum / max(pair_count, 1),
        "order_flow_sign_autocorrelation": flow_autocorrelation_sum / max(pair_count, 1),
        "first_timestamp_ms": first_timestamp,
        "last_timestamp_ms": last_timestamp,
        "source_units": "aggregate trades; signed impact is a descriptive proxy, not causal identification",
    }


_DEPTH_RE = re.compile(r"^(?P<symbol>[A-Z0-9_]+)-bookDepth-(?P<date>\d{4}-\d{2}-\d{2})\.zip$")
_TRADES_RE = re.compile(r"^(?P<symbol>[A-Z0-9_]+)-aggTrades-(?P<date>\d{4}-\d{2}-\d{2})\.zip$")


def _archive_index(root: Path, pattern: re.Pattern[str]) -> dict[tuple[str, str], Path]:
    index: dict[tuple[str, str], Path] = {}
    for path in Path(root).glob("*.zip"):
        match = pattern.match(path.name)
        if match:
            index[(match.group("symbol"), match.group("date"))] = path
    return index


def pair_daily_archives(depth_root: Path, trades_root: Path, symbols: list[str]) -> list[dict[str, object]]:
    depths = _archive_index(depth_root, _DEPTH_RE)
    trades = _archive_index(trades_root, _TRADES_RE)
    keys = sorted(set(depths) & set(trades))
    return [
        {"symbol": symbol, "date": date, "depth_path": depths[(symbol, date)], "trades_path": trades[(symbol, date)]}
        for symbol, date in keys
        if symbol in symbols
    ]
