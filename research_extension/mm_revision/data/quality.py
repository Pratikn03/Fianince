"""Data quality assurance and integrity checks for observational market records."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np
from research_extension.mm_revision.data.schemas import CanonicalAssetPanel, AggressiveSide


@dataclass
class DataQualityReport:
    venue: str
    symbol: str
    total_candles: int
    total_trades: int
    has_l1_snapshot: bool
    timestamps_monotonic: bool
    has_nonpositive_prices: bool
    has_nan_or_inf: bool
    candle_gaps_count: int
    trade_gaps_count: int
    is_historically_synchronized: bool
    quality_status: str
    warnings: List[str] = field(default_factory=list)


def audit_asset_panel_quality(panel: CanonicalAssetPanel) -> DataQualityReport:
    """Inspect a canonical asset panel for missing data, unaligned feeds, and anomalies."""
    warnings = []
    
    # 1. Candles inspection
    n_candles = len(panel.candles)
    c_times = [c.timestamp_utc for c in panel.candles]
    c_monotonic = all(x <= y for x, y in zip(c_times[:-1], c_times[1:])) if n_candles > 1 else True
    if not c_monotonic:
        warnings.append("Candle timestamps are not strictly non-decreasing.")

    c_gaps = 0
    if n_candles > 1:
        diffs = np.diff(c_times)
        # Expected 60s for 1m candles
        c_gaps = int(np.sum(diffs > 120))
        if c_gaps > 0:
            warnings.append(f"Detected {c_gaps} time gaps (>2 min) in 1-minute candle bars.")

    has_nonpos_c = any(c.close <= 0 or c.open <= 0 or c.high <= 0 or c.low <= 0 for c in panel.candles)
    has_nan_inf_c = any(not np.isfinite([c.open, c.high, c.low, c.close, c.volume]).all() for c in panel.candles)

    # 2. Trades inspection
    n_trades = len(panel.trades)
    t_times = [t.timestamp_utc for t in panel.trades]
    t_monotonic = all(x <= y for x, y in zip(t_times[:-1], t_times[1:])) if n_trades > 1 else True
    if not t_monotonic:
        warnings.append("Trade timestamps are not strictly non-decreasing.")

    has_nonpos_t = any(t.price <= 0 or t.size <= 0 for t in panel.trades)
    has_nan_inf_t = any(not np.isfinite([t.price, t.size, t.signed_flow]).all() for t in panel.trades)

    # 3. L1 Snapshot synchronicity audit
    # A single order-book snapshot cannot provide historical depth or spread across earlier candle periods
    has_l1 = panel.l1_snapshot is not None
    is_sync = False
    if has_l1 and n_candles > 0:
        # Check if snapshot timestamp coincides with candle range
        snap_time = panel.l1_snapshot.timestamp_utc
        candle_start = panel.candles[0].timestamp_utc
        candle_end = panel.candles[-1].timestamp_utc
        if snap_time > candle_end + 3600:
            warnings.append(
                "L1 order-book snapshot was captured after the candle series. "
                "Current snapshot spread cannot serve as a historical Period A control."
            )
    else:
        warnings.append("No synchronized continuous historical quote archive present.")

    quality_status = "PASS_WITH_CAVEATS" if warnings else "PASS_CLEAN"
    if has_nonpos_c or has_nan_inf_c:
        quality_status = "REJECT_INVALID_VALUES"

    return DataQualityReport(
        venue=panel.venue,
        symbol=panel.symbol,
        total_candles=n_candles,
        total_trades=n_trades,
        has_l1_snapshot=has_l1,
        timestamps_monotonic=bool(c_monotonic and t_monotonic),
        has_nonpositive_prices=bool(has_nonpos_c or has_nonpos_t),
        has_nan_or_inf=bool(has_nan_inf_c or has_nan_inf_t),
        candle_gaps_count=c_gaps,
        trade_gaps_count=0,
        is_historically_synchronized=is_sync,
        quality_status=quality_status,
        warnings=warnings,
    )
