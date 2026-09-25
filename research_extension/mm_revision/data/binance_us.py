"""Binance US data adapter and canonical ingestion.

Enforces correct buyer-maker causality:
In Binance, isBuyerMaker indicates who provided liquidity:
- isBuyerMaker == True  => buyer was maker (resting bid was hit) => aggressive taker is SELLING => signed flow = -qty
- isBuyerMaker == False => seller was maker (resting ask was lifted) => aggressive taker is BUYING => signed flow = +qty
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


def parse_binance_trade_direction(is_buyer_maker: bool) -> Tuple[AggressiveSide, float]:
    """Convert Binance isBuyerMaker flag to aggressive flow direction."""
    if is_buyer_maker:
        return AggressiveSide.SELL, -1.0
    else:
        return AggressiveSide.BUY, 1.0


def load_canonical_binance_panel(
    raw_dict: Dict[str, Any],
    symbol: str
) -> CanonicalAssetPanel:
    """Load a Binance US asset record into a CanonicalAssetPanel."""
    closes = raw_dict.get("closes", [])
    volumes = raw_dict.get("volumes", [1.0] * len(closes))
    
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

    trades = []
    prices = raw_dict.get("prices", [])
    raw_signed_flow = raw_dict.get("signed_flow", [])
    for i, p in enumerate(prices):
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

    midpoint = float(raw_dict.get("midpoint", closes[-1] if closes else 1.0))
    spread_bps = float(raw_dict.get("rel_spread_bps", 1.0))
    half_spread = (spread_bps / 10000.0) * midpoint / 2.0
    snapshot = CanonicalL1Snapshot(
        timestamp_utc=t0 + len(candles) * 60.0 + 300.0,
        best_bid=midpoint - half_spread,
        best_ask=midpoint + half_spread,
        midpoint=midpoint,
        relative_spread_bps=spread_bps,
    )

    return CanonicalAssetPanel(
        venue="BinanceUS",
        symbol=symbol,
        candles=candles,
        trades=trades,
        l1_snapshot=snapshot,
        metadata={"raw_keys": list(raw_dict.keys())}
    )
