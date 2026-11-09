# P7S Schema Probe (Binance USDT-Margined Perpetuals), declared 8 November 2026

**Purpose.** Learn and lock the exact field layout, column headers, units, timestamps, and row counts of Binance USD-M futures public archives (5-minute klines and 5-minute metrics) before finalizing and freezing the P7S registration.

**What it is NOT:**
- It is NOT a test of hypotheses H1 or H2.
- NO estimator is run.
- NO returns, price impacts, open interest terciles, or DiD statistics are computed.
- NO outcome data from the development window (2026-08-01 to 2026-10-31) or holdout window (2026-11-16 to 2027-02-14) are touched.

**Declared Burned Date.**
- Date: `2024-01-02` (UTC).
- This date was already declared a burned date during the Phase 2 schema probes (`SCHEMA_PROBE.md`) and lies entirely outside the P7S development and prospective holdout periods.
- Probed symbols: `BTCUSDT`, `ETHUSDT`, `SOLUSDT`.

**Target Datasets:**
1. **5-Minute Klines:**
   `https://data.binance.vision/data/futures/um/daily/klines/{sym}/5m/{sym}-5m-{date}.zip`
   Expected fields: `open_time`, `open`, `high`, `low`, `close`, `volume`, `close_time`, `quote_volume`, `count`, `taker_buy_volume`, `taker_buy_quote_volume`, `ignore`.
2. **5-Minute Metrics:**
   `https://data.binance.vision/data/futures/um/daily/metrics/{sym}/{sym}-metrics-{date}.zip`
   Expected fields: `create_time`, `symbol`, `sum_open_interest`, `sum_open_interest_value`, `count_toptrader_long_short_ratio`, `sum_toptrader_long_short_ratio`, `count_long_short_ratio`, `sum_taker_long_short_vol_ratio`.

**Outputs:**
- `p7s_schema_probe_results.zip` containing:
  - `schema_klines_5m.json`
  - `schema_metrics.json`
  - `probe_log.json`
