"""Temporal alignment utilities avoiding row-number matching and future quote lookahead."""
from typing import List, Dict, Any, Optional
import numpy as np
from research_extension.mm_revision.data.schemas import CanonicalTrade, CanonicalCandle, CanonicalL1Snapshot


def asof_join_trade_to_quote(
    trade_timestamp: float,
    quote_timestamps: np.ndarray,
    quote_values: np.ndarray
) -> Optional[float]:
    """Find the most recent quote available at or strictly before trade_timestamp.

    Rejects future quotes (lookahead bias).
    """
    valid_idx = np.where(quote_timestamps <= trade_timestamp)[0]
    if len(valid_idx) == 0:
        return None  # No prior quote exists
    latest_idx = valid_idx[-1]
    return float(quote_values[latest_idx])


def align_trades_to_candles_by_time(
    candles: List[CanonicalCandle],
    trades: List[CanonicalTrade],
    interval_seconds: float = 60.0
) -> List[Dict[str, Any]]:
    """Align trades to candle bars strictly by UTC time window [candle_t, candle_t + interval).

    NEVER aligns by array row index.
    """
    aligned = []
    trade_times = np.array([t.timestamp_utc for t in trades])
    trade_flows = np.array([t.signed_flow for t in trades])

    for c in candles:
        t_start = c.timestamp_utc
        t_end = t_start + interval_seconds
        
        in_window = np.where((trade_times >= t_start) & (trade_times < t_end))[0]
        window_flow = float(np.sum(trade_flows[in_window])) if len(in_window) > 0 else 0.0
        n_trades_window = len(in_window)

        aligned.append({
            "timestamp_utc": t_start,
            "close": c.close,
            "candle_volume": c.volume,
            "aggregated_signed_flow": window_flow,
            "trade_count": n_trades_window,
        })

    return aligned
