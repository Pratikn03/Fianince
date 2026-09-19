#!/usr/bin/env python3
"""Calibrate observable depth-band and trade-tape targets on held-out days."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mm_next.l2_calibration import (  # noqa: E402
    pair_daily_archives,
    summarize_book_depth_rows,
    summarize_trade_rows,
    iter_agg_trade_rows,
    iter_book_depth_rows,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _expected_checksum(path: Path) -> str | None:
    checksum = path.with_name(path.name + ".CHECKSUM")
    if not checksum.is_file():
        return None
    token = checksum.read_text(encoding="utf-8").strip().split()[0]
    return token or None


def _period_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("period must contain at least one day")
    sum_keys = {"trade_count", "total_quantity", "total_notional"}
    result: dict[str, Any] = {"days": len(rows)}
    for section in ("depth", "trades"):
        section_rows = [row[section] for row in rows]
        section_out: dict[str, Any] = {}
        keys = set().union(*(item.keys() for item in section_rows))
        for key in sorted(keys):
            values = [item[key] for item in section_rows if isinstance(item.get(key), (int, float))]
            if not values:
                continue
            if section == "trades" and key in sum_keys:
                section_out[key] = float(np.sum(values))
            else:
                section_out[key] = float(np.mean(values))
        result[section] = section_out
    return result


def _split(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    rows = sorted(rows, key=lambda row: row["date"])
    train_end = int(len(rows) * 0.6)
    validation_end = train_end + int(len(rows) * 0.2)
    return {
        "train": rows[:train_end],
        "validation": rows[train_end:validation_end],
        "test": rows[validation_end:],
    }


def run(
    depth_root: Path,
    trades_root: Path,
    output: Path,
    symbols: list[str],
    expected_days: int = 31,
) -> dict[str, Any]:
    pairs = pair_daily_archives(depth_root, trades_root, symbols)
    expected = len(symbols) * expected_days
    if len(pairs) != expected:
        raise RuntimeError(f"expected {expected} paired days, found {len(pairs)}")
    dates_by_symbol = {
        symbol: sorted({str(pair["date"]) for pair in pairs if pair["symbol"] == symbol})
        for symbol in symbols
    }
    if any(len(dates) != expected_days for dates in dates_by_symbol.values()):
        raise RuntimeError(f"each symbol must have {expected_days} distinct dates: {dates_by_symbol}")
    if len({tuple(dates) for dates in dates_by_symbol.values()}) != 1:
        raise RuntimeError(f"symbols do not share the same date support: {dates_by_symbol}")
    output.mkdir(parents=True, exist_ok=True)
    manifest_files: list[dict[str, Any]] = []
    by_symbol: dict[str, list[dict[str, Any]]] = {symbol: [] for symbol in symbols}
    for index, pair in enumerate(pairs, start=1):
        depth_path = Path(pair["depth_path"])
        trades_path = Path(pair["trades_path"])
        depth_digest = _sha256(depth_path)
        trade_digest = _sha256(trades_path)
        expected_depth = _expected_checksum(depth_path)
        expected_trade = _expected_checksum(trades_path)
        if expected_depth != depth_digest or expected_trade != trade_digest:
            raise RuntimeError(f"checksum mismatch for {pair['symbol']} {pair['date']}")
        daily = {
            "symbol": pair["symbol"],
            "date": pair["date"],
            "depth": summarize_book_depth_rows(iter_book_depth_rows(depth_path)),
            "trades": summarize_trade_rows(iter_agg_trade_rows(trades_path)),
        }
        by_symbol[str(pair["symbol"])].append(daily)
        manifest_files.extend([
            {"kind": "bookDepth", "symbol": pair["symbol"], "date": pair["date"], "path": str(depth_path), "bytes": depth_path.stat().st_size, "sha256": depth_digest, "expected_sha256": expected_depth},
            {"kind": "aggTrades", "symbol": pair["symbol"], "date": pair["date"], "path": str(trades_path), "bytes": trades_path.stat().st_size, "sha256": trade_digest, "expected_sha256": expected_trade},
        ])
        if index % 15 == 0 or index == len(pairs):
            print(f"processed_pairs={index}/{len(pairs)}", flush=True)

    result_symbols: dict[str, Any] = {}
    for symbol, rows in by_symbol.items():
        splits = _split(rows)
        result_symbols[symbol] = {
            "rows": len(rows),
            "date_range": [rows[0]["date"], rows[-1]["date"]],
            "splits": {name: _period_summary(value) for name, value in splits.items()},
            "daily": rows,
        }
    result = {
        "schema": "mm-next-historical-depth-calibration-1",
        "market": "Binance USD-M futures",
        "source": "https://data.binance.vision/data/futures/um/daily/",
        "period": f"{pairs[0]['date']} through {pairs[-1]['date']}",
        "symbols": symbols,
        "split_policy": "chronological 60/20/20 by day; no shuffling",
        "symbols_results": result_symbols,
        "calibration_targets": {
            "depth_profile": "observed and held-out",
            "trade_size_and_volume": "observed and held-out",
            "volatility_proxy": "observed and held-out",
            "order_flow_dependence": "observed and held-out",
            "spread": "not available in bookDepth/aggTrades pair",
            "fill_probability": "not identifiable without submitted-order or queue data",
            "cancellations_and_queue_priority": "not available",
            "status": "historical depth-band and trade-tape calibration complete; queue-level replay calibration incomplete",
        },
        "interpretation": "The archive is a public depth-band product, not full order-level L2 event history. No fill or spread claim is promoted from these files.",
    }
    (output / "l2_calibration_results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema": "mm-next-binance-l2-manifest-1",
        "source": "https://data.binance.vision/data/futures/um/daily/",
        "download_date": "2026-09-18",
        "storage": "T9 external dataset; raw archives are not copied into GitHub",
        "pair_count": len(manifest_files) // 2,
        "symbols": symbols,
        "dates": sorted({str(pair["date"]) for pair in pairs}),
        "checksum_verification": "sha256 archive digest matched the adjacent .CHECKSUM file for every archive",
        "script": str(Path(__file__).resolve()),
        "script_sha256": _sha256(Path(__file__).resolve()),
        "files": manifest_files,
    }
    (output / "l2_calibration_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--depth-root", type=Path, required=True)
    parser.add_argument("--trades-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "results")
    parser.add_argument("--symbols", nargs="+", default=["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    parser.add_argument("--expected-days", type=int, default=31)
    args = parser.parse_args()
    result = run(
        args.depth_root.resolve(),
        args.trades_root.resolve(),
        args.output.resolve(),
        args.symbols,
        expected_days=args.expected_days,
    )
    print(json.dumps({"output": str(args.output.resolve()), "symbols": len(result["symbols_results"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
