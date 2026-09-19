from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import zipfile

from mm_next.l2_calibration import (
    iter_agg_trade_rows,
    iter_book_depth_rows,
    pair_daily_archives,
    summarize_trade_rows,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_l2_calibration import run  # noqa: E402


def _zip(path: Path, name: str, content: str) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(name, content)


def test_depth_and_trade_zip_parsers_extract_public_schema(tmp_path: Path) -> None:
    depth = tmp_path / "BTCUSDT-bookDepth-2025-01-01.zip"
    _zip(depth, "depth.csv", "timestamp,percentage,depth,notional\n2025-01-01 00:00:00,-1,10,100\n")
    trades = tmp_path / "BTCUSDT-aggTrades-2025-01-01.zip"
    _zip(trades, "trades.csv", "agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker\n1,100,2,1,1,1000,false\n2,101,1,2,2,2000,true\n")

    depth_rows = list(iter_book_depth_rows(depth))
    trade_rows = list(iter_agg_trade_rows(trades))
    assert depth_rows[0]["percentage"] == -1
    assert trade_rows[1]["is_buyer_maker"] is True
    summary = summarize_trade_rows(trade_rows)
    assert summary["trade_count"] == 2
    assert summary["total_quantity"] == 3.0


def test_daily_archives_pair_by_symbol_and_date(tmp_path: Path) -> None:
    depth = tmp_path / "BTCUSDT-bookDepth-2025-01-01.zip"
    trades = tmp_path / "BTCUSDT-aggTrades-2025-01-01.zip"
    _zip(depth, "depth.csv", "timestamp,percentage,depth,notional\n2025-01-01 00:00:00,-1,10,100\n")
    _zip(trades, "trades.csv", "agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker\n1,100,2,1,1,1000,false\n")
    pairs = pair_daily_archives(tmp_path, tmp_path, ["BTCUSDT"])
    assert len(pairs) == 1
    assert pairs[0]["date"] == "2025-01-01"


def test_runner_records_verified_manifest_and_code_digest(tmp_path: Path) -> None:
    depth_root = tmp_path / "depth"
    trades_root = tmp_path / "trades"
    output = tmp_path / "results"
    depth_root.mkdir()
    trades_root.mkdir()
    for day in range(1, 6):
        date = f"2025-01-0{day}"
        depth = depth_root / f"BTCUSDT-bookDepth-{date}.zip"
        _zip(
            depth,
            "depth.csv",
            f"timestamp,percentage,depth,notional\n{date} 00:00:00,-1,10,100\n"
            f"{date} 00:00:00,1,11,110\n",
        )
        trades = trades_root / f"BTCUSDT-aggTrades-{date}.zip"
        _zip(
            trades,
            "trades.csv",
            "agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker\n"
            f"{day},100,2,{day},{day},{day * 1000},false\n",
        )
        for path in (depth, trades):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            path.with_name(path.name + ".CHECKSUM").write_text(f"{digest}  {path.name}\n", encoding="utf-8")

    result = run(depth_root, trades_root, output, ["BTCUSDT"], expected_days=5)
    assert result["symbols_results"]["BTCUSDT"]["rows"] == 5
    manifest = json.loads((output / "l2_calibration_manifest.json").read_text())
    assert manifest["pair_count"] == 5
    assert len(manifest["files"]) == 10
    assert manifest["script_sha256"]
    assert all(item["sha256"] == item["expected_sha256"] for item in manifest["files"])
