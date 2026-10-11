#!/usr/bin/env python3
"""Public venue-rule calibration for the January 9--20, 2023 BTCUSDT perpetual sample.

STATUS: VENUE-RULE CALIBRATION, NOT ACCOUNT CALIBRATION.

Inputs are published venue rules only:
  * Binance USD(S)-M futures fee schedule, archived by the Internet Archive on
    2022-12-09 and 2023-01-22 (both snapshots bracket the sample and agree).
  * Binance USD(S)-M leverage/maintenance-margin brackets (public bapi endpoint),
    archived on 2023-01-09, 2023-01-17 and 2023-01-23.
  * Binance official monthly BTCUSDT funding-rate file for 2023-01
    (data.binance.vision), checksum-verified.
  * The paper's displayed-book calibration JSON (median midpoint, spread, sweeps).

No account, position, fill, margin-call or funding-payment record is used. All
position quantities (equity B = 10,000 USDT, leverage 10/20) are the paper's
hypothetical scenario inputs. Liquidation prices follow Binance's published
isolated-margin one-way formula and ignore fees, funding accrual and the
mark/last-price basis.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
ROOT = HERE.parents[1]
BOOK_JSON = ROOT / "research_extension/research_completion_20261008/displayed_book_calibration.json"

SAMPLE_START = datetime(2023, 1, 9, tzinfo=timezone.utc)
SAMPLE_END = datetime(2023, 1, 21, tzinfo=timezone.utc)  # exclusive: covers Jan 9--20
EQUITY = 10_000.0
LEVERAGES = (10, 20)

SOURCES = {
    "fee_2022_12_09": {
        "file": "wayback_futureFee_20221209203903.html",
        "url": "https://web.archive.org/web/20221209203903/https://www.binance.com/en/fee/futureFee",
    },
    "fee_2023_01_22": {
        "file": "wayback_futureFee_20230122031351.html",
        "url": "https://web.archive.org/web/20230122031351/https://www.binance.com/en/fee/futureFee",
    },
    "brackets_2023_01_09": {
        "file": "brackets_usdm_20230109204158.json",
        "url": "https://web.archive.org/web/20230109204158/https://www.binance.com/bapi/futures/v1/friendly/future/common/brackets",
    },
    "brackets_2023_01_17": {
        "file": "brackets_usdm_20230117130848.json",
        "url": "https://web.archive.org/web/20230117130848/https://www.binance.com/bapi/futures/v1/friendly/future/common/brackets",
    },
    "brackets_2023_01_23": {
        "file": "brackets_usdm_20230123011658.json",
        "url": "https://web.archive.org/web/20230123011658/https://www.binance.com/bapi/futures/v1/friendly/future/common/brackets",
    },
    "funding_2023_01": {
        "file": "BTCUSDT-fundingRate-2023-01.zip",
        "url": "https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2023-01.zip",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def maybe_gunzip(b: bytes) -> bytes:
    return gzip.decompress(b) if b[:2] == b"\x1f\x8b" else b


def parse_fee_table(path: Path) -> dict:
    html = maybe_gunzip(path.read_bytes()).decode("utf-8", "ignore")
    text = re.sub(r"<script.*?</script>", "", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " | ", text)
    text = re.sub(r"(\s*\|\s*)+", " | ", text)
    rows = {}
    for level in ["Regular User"] + [f"VIP {i}" for i in range(1, 10)]:
        i = text.find(level + " |")
        if i < 0:
            raise ValueError(f"{level} not found in {path.name}")
        pct = re.findall(r"(-?\d+\.\d+)%", text[i:i + 400])[:8]
        v = [float(p) for p in pct]
        rows[level] = {
            "usdt_maker_pct": v[0], "usdt_taker_pct": v[1],
            "usdt_maker_bnb_pct": v[2], "usdt_taker_bnb_pct": v[3],
            "busd_maker_pct": v[4], "busd_taker_pct": v[5],
        }
    return rows


def load_brackets(path: Path) -> dict:
    d = json.loads(maybe_gunzip(path.read_bytes()))
    assert d.get("success") is True and d.get("code") == "000000", path
    for item in d["data"]["brackets"]:
        if item["symbol"] == "BTCUSDT":
            return item
    raise ValueError("BTCUSDT not in brackets")


def tier_for(notional: float, brackets: list[dict]) -> dict:
    for b in brackets:
        if b["bracketNotionalFloor"] <= notional < b["bracketNotionalCap"]:
            return b
    raise ValueError(notional)


def max_notional(equity: float, brackets: list[dict]) -> float:
    """Largest notional N with N / maxLeverage(tier(N)) <= equity (initial margin only)."""
    best = 0.0
    for b in brackets:
        hi = min(b["bracketNotionalCap"], equity * b["maxOpenPosLeverage"])
        if hi > b["bracketNotionalFloor"]:
            # tier cap is exclusive; report the supremum within the tier
            best = max(best, hi)
    return best


def liquidation(equity: float, notional: float, entry: float, br: dict) -> dict:
    """Binance isolated one-way liquidation price (fees, funding and basis ignored)."""
    q = notional / entry
    mmr = br["bracketMaintenanceMarginRate"]
    cum = br["cumFastMaintenanceAmount"]
    lp_long = (equity + cum - q * entry) / (q * (mmr - 1.0))
    lp_short = (equity + cum + q * entry) / (q * (1.0 + mmr))
    mm_entry = notional * mmr - cum
    return {
        "maintenance_margin_at_entry_usdt": mm_entry,
        "initial_margin_rate_mu": 1.0 / br["maxOpenPosLeverage"],
        "initial_margin_usdt": notional / br["maxOpenPosLeverage"],
        "available_buffer_A0_usdt": equity - notional / br["maxOpenPosLeverage"],
        "loss_before_maintenance_breach_usdt_at_entry": equity - mm_entry,
        "long_liquidation_price": lp_long,
        "long_adverse_move_pct": 100.0 * (1.0 - lp_long / entry),
        "short_liquidation_price": lp_short,
        "short_adverse_move_pct": 100.0 * (lp_short / entry - 1.0),
    }


def main() -> None:
    hashes = {k: {"url": v["url"], "file": v["file"], "sha256": sha256(RAW / v["file"])} for k, v in SOURCES.items()}
    published = (RAW / "BTCUSDT-fundingRate-2023-01.zip.CHECKSUM").read_text().split()[0]
    assert published == hashes["funding_2023_01"]["sha256"], "funding checksum mismatch"
    hashes["funding_2023_01"]["published_checksum_match"] = True

    # ---- fees -------------------------------------------------------------
    fee_a = parse_fee_table(RAW / SOURCES["fee_2022_12_09"]["file"])
    fee_b = parse_fee_table(RAW / SOURCES["fee_2023_01_22"]["file"])
    assert fee_a == fee_b, "fee schedule changed between bracketing snapshots"
    reg, vip9 = fee_b["Regular User"], fee_b["VIP 9"]

    # ---- book frictions from the paper's calibration ----------------------
    book = json.loads(BOOK_JSON.read_text())["pooled_metrics"]
    mid = book["midpoint_quote_units"]["median"]
    spread = book["spread_quote_units"]["median"]
    spread_bps = book["spread_basis_points"]["median"]
    sweep_buy = book["buy_0.5_sweep_cost_per_reported_unit"]["p90"]
    sweep_sell = book["sell_0.5_sweep_cost_per_reported_unit"]["p90"]

    def bps(pct: float) -> float:
        return pct * 100.0

    fees = {
        "schedule_identical_in_both_snapshots": True,
        "regular_user_usdt": reg,
        "vip9_usdt": vip9,
        "regular_taker_round_trip_bps": 2 * bps(reg["usdt_taker_pct"]),
        "regular_maker_round_trip_bps": 2 * bps(reg["usdt_maker_pct"]),
        "vip9_taker_round_trip_bps": 2 * bps(vip9["usdt_taker_pct"]),
        "median_quoted_spread_bps": spread_bps,
        "regular_taker_fee_per_btc_at_median_mid_usdt": reg["usdt_taker_pct"] / 100 * mid,
        "median_half_spread_per_btc_usdt": spread / 2,
        "p90_half_side_sweep_cost_per_btc_usdt": {"buy": sweep_buy, "sell": sweep_sell},
        "p90_half_side_sweep_cost_bps": {"buy": sweep_buy / mid * 1e4, "sell": sweep_sell / mid * 1e4},
        "ratio_regular_taker_fee_to_half_spread": (reg["usdt_taker_pct"] / 100 * mid) / (spread / 2),
        "ratio_regular_taker_fee_to_p90_buy_sweep": (reg["usdt_taker_pct"] / 100 * mid) / sweep_buy,
    }

    # ---- funding ----------------------------------------------------------
    with zipfile.ZipFile(RAW / SOURCES["funding_2023_01"]["file"]) as z:
        name = z.namelist()[0]
        rows = list(csv.DictReader(z.read(name).decode().splitlines()))
    sample = []
    for r in rows:
        t = datetime.fromtimestamp(int(r["calc_time"]) / 1000, tz=timezone.utc)
        if SAMPLE_START <= t < SAMPLE_END:
            sample.append((t, int(r["funding_interval_hours"]), float(r["last_funding_rate"])))
    rates = [x[2] for x in sample]
    n = len(rates)
    mean = sum(rates) / n
    funding = {
        "window_utc": [SAMPLE_START.isoformat(), SAMPLE_END.isoformat()],
        "settlements": n,
        "interval_hours": sorted({x[1] for x in sample}),
        "mean_rate": mean,
        "min_rate": min(rates),
        "max_rate": max(rates),
        "positive_settlements": sum(r > 0 for r in rates),
        "cumulative_rate_sum": sum(rates),
        "annualized_mean_simple_pct": mean * 3 * 365 * 100,
        "per_leverage": {},
    }

    # ---- margin brackets --------------------------------------------------
    br = {k: load_brackets(RAW / SOURCES[k]["file"]) for k in ("brackets_2023_01_09", "brackets_2023_01_17", "brackets_2023_01_23")}
    pre, post = br["brackets_2023_01_09"]["riskBrackets"], br["brackets_2023_01_23"]["riskBrackets"]
    assert br["brackets_2023_01_09"] == br["brackets_2023_01_17"], "brackets changed inside Jan 9-17"
    mmr_unchanged = [(a["bracketMaintenanceMarginRate"], a["cumFastMaintenanceAmount"]) for a in pre] == \
                    [(b["bracketMaintenanceMarginRate"], b["cumFastMaintenanceAmount"]) for b in post]
    upd = lambda k: datetime.fromtimestamp(br[k]["updateTime"] / 1000, tz=timezone.utc).isoformat()

    margin = {
        "pre_update_time_utc": upd("brackets_2023_01_09"),
        "post_update_time_utc": upd("brackets_2023_01_23"),
        "maintenance_rates_unchanged_across_update": mmr_unchanged,
        "pre_brackets": pre,
        "post_brackets": post,
        "max_notional_for_equity": {
            "pre": max_notional(EQUITY, pre), "post": max_notional(EQUITY, post),
        },
        "scenarios": {},
    }
    for L in LEVERAGES:
        N = L * EQUITY
        out = {}
        for tag, table in (("pre", pre), ("post", post)):
            t = tier_for(N, table)
            out[tag] = {
                "tier": t["bracketSeq"], "tier_max_leverage": t["maxOpenPosLeverage"],
                "mmr": t["bracketMaintenanceMarginRate"], "cum": t["cumFastMaintenanceAmount"],
                "within_venue_limit": L <= t["maxOpenPosLeverage"],
                **liquidation(EQUITY, N, mid, t),
            }
        margin["scenarios"][f"L{L}"] = {"notional_usdt": N, **out}
        funding["per_leverage"][f"L{L}"] = {
            "cumulative_funding_paid_by_long_usdt": N * sum(rates),
            "as_pct_of_equity": 100 * N * sum(rates) / EQUITY,
            "regular_taker_round_trip_fee_usdt": N * fees["regular_taker_round_trip_bps"] / 1e4,
            "regular_taker_round_trip_fee_pct_of_equity": 100 * N * fees["regular_taker_round_trip_bps"] / 1e4 / EQUITY,
        }

    result = {
        "status": "VENUE_RULE_CALIBRATION_NOT_ACCOUNT_CALIBRATION",
        "disclaimer": (
            "Published venue rules applied to the paper's hypothetical scenario equity and leverage. "
            "No account, position, fill, margin-call or realized funding-payment record is used. "
            "Liquidation prices ignore fees, funding accrual, mark-price basis and insurance-fund/ADL mechanics."
        ),
        "scenario_equity_usdt": EQUITY,
        "median_midpoint_usdt": mid,
        "fees": fees,
        "funding": funding,
        "margin": margin,
        "sources": hashes,
        "book_calibration_source": {"path": str(BOOK_JSON.relative_to(ROOT)), "sha256": sha256(BOOK_JSON)},
    }
    (HERE / "venue_rule_calibration.json").write_text(json.dumps(result, indent=1))
    receipt = {
        "status": result["status"],
        "script_sha256": sha256(Path(__file__)),
        "output_sha256": sha256(HERE / "venue_rule_calibration.json"),
        "sources": hashes,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }
    (HERE / "venue_rule_receipt.json").write_text(json.dumps(receipt, indent=1))
    print(json.dumps({k: result[k] for k in ("fees", "funding")}, indent=1))
    print(json.dumps({k: v for k, v in margin.items() if k not in ("pre_brackets", "post_brackets")}, indent=1))


if __name__ == "__main__":
    main()
