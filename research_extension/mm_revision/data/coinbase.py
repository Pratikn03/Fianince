"""Coinbase Exchange data adapter and canonical ingestion.

Enforces correct maker/taker causality:
In Coinbase, 'side' represents the maker order side:
- maker side == 'sell' => aggressive taker is BUYING => signed flow = +size
- maker side == 'buy'  => aggressive taker is SELLING => signed flow = -size
"""
import json
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from research_extension.mm_revision.data.schemas import (
    CanonicalAssetPanel,
    CanonicalCandle,
    CanonicalTrade,
    CanonicalL1Snapshot,
    AggressiveSide,
)


def parse_coinbase_trade_direction(maker_side: str) -> Tuple[AggressiveSide, float]:
    """Convert Coinbase maker side to aggressive flow direction.

    Coinbase docs: 'side' indicates the maker order side.
    - If maker posted 'sell' (ask), incoming taker order was a BUY.
    - If maker posted 'buy' (bid), incoming taker order was a SELL.
    """
    s = str(maker_side).lower().strip()
    if s == "sell":
        return AggressiveSide.BUY, 1.0
    elif s == "buy":
        return AggressiveSide.SELL, -1.0
    return AggressiveSide.UNKNOWN, 0.0


def load_canonical_coinbase_panel(
    raw_dict: Dict[str, Any],
    symbol: str
) -> CanonicalAssetPanel:
    """Load a Coinbase asset record into a CanonicalAssetPanel."""
    # Closes and volumes
    closes = raw_dict.get("closes", [])
    volumes = raw_dict.get("volumes", [1.0] * len(closes))
    
    # Synthesize sequential candle timestamps if exact UTC not stored
    t0 = 1700000000.0
    candles = []
    for i, (c, v) in enumerate(zip(closes, volumes)):
        candles.append(CanonicalCandle(
            timestamp_utc=t0 + i * 60.0,
            open=float(c),
            high=float(c),
            low=float(c),
            close=float(c),
            volume=float(v),
        ))

    # Trades
    trades = []
    trade_prices = raw_dict.get("trade_prices", [])
    raw_signed_flow = raw_dict.get("signed_flow", [])
    
    # If raw trade items exist with maker side
    raw_trades = raw_dict.get("raw_trades", [])
    if raw_trades:
        for tr in raw_trades:
            agg_side, sign = parse_coinbase_trade_direction(tr.get("side", ""))
            sz = float(tr.get("size", 1.0))
            trades.append(CanonicalTrade(
                trade_id=str(tr.get("trade_id", len(trades))),
                timestamp_utc=float(tr.get("time_utc", t0)),
                price=float(tr.get("price", 0.0)),
                size=sz,
                aggressive_side=agg_side,
                signed_flow=sign * sz,
            ))
    elif trade_prices:
        for i, p in enumerate(trade_prices):
            flow = raw_signed_flow[i] if i < len(raw_signed_flow) else 0.0
            side = AggressiveSide.BUY if flow > 0 else (AggressiveSide.SELL if flow < 0 else AggressiveSide.UNKNOWN)
            trades.append(CanonicalTrade(
                trade_id=str(i),
                timestamp_utc=t0 + i * 0.5,
                price=float(p),
                size=abs(float(flow)) if abs(float(flow)) > 0 else 1.0,
                aggressive_side=side,
                signed_flow=float(flow),
            ))

    # L1 snapshot
    midpoint = float(raw_dict.get("midpoint", closes[-1] if closes else 1.0))
    spread_bps = float(raw_dict.get("rel_spread_bps", 1.0))
    half_spread = (spread_bps / 10000.0) * midpoint / 2.0
    snapshot = CanonicalL1Snapshot(
        timestamp_utc=t0 + len(candles) * 60.0 + 300.0, # Snapshot was taken at/after fetch time
        best_bid=midpoint - half_spread,
        best_ask=midpoint + half_spread,
        midpoint=midpoint,
        relative_spread_bps=spread_bps,
    )

    return CanonicalAssetPanel(
        venue="Coinbase",
        symbol=symbol,
        candles=candles,
        trades=trades,
        l1_snapshot=snapshot,
        metadata={"raw_keys": list(raw_dict.keys())}
    )
