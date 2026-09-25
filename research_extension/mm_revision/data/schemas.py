"""Canonical data schemas for observational microstructure records in Machine Markets.

Enforces:
- Common UTC timestamp representation
- Explicit separation between tick trades, candle bars, and order-book snapshots
- Signed aggressive flow based on exchange causality rules
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
import numpy as np


class AggressiveSide(str, Enum):
    BUY = "BUY"     # Aggressive buyer taking liquidity
    SELL = "SELL"   # Aggressive seller taking liquidity
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class CanonicalTrade:
    trade_id: str
    timestamp_utc: float
    price: float
    size: float
    aggressive_side: AggressiveSide
    signed_flow: float  # +size if BUY, -size if SELL


@dataclass(frozen=True)
class CanonicalCandle:
    timestamp_utc: float
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class CanonicalL1Snapshot:
    timestamp_utc: float
    best_bid: float
    best_ask: float
    midpoint: float
    relative_spread_bps: float


@dataclass
class CanonicalAssetPanel:
    venue: str
    symbol: str
    candles: List[CanonicalCandle]
    trades: List[CanonicalTrade] = field(default_factory=list)
    l1_snapshot: Optional[CanonicalL1Snapshot] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
