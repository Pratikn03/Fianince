# Data provenance

The empirical pilot uses public Binance monthly kline archives already stored
under `research_extension/data/raw/binance/spot/klines/`:

- BTCUSDT 1-minute, January 2025;
- ETHUSDT 1-hour, January 2025;
- SOLUSDT 1-hour, January 2025.

The acquisition manifest records the source URLs, checksums, retrieval date,
license/access note, and file sizes. The calibration script reads the archive
without shuffling and reports chronological 60/20/20 splits.

These files contain OHLCV klines. They do not provide historical level-2
queue state, cancellations, order priority, or a validated fill simulator.
Therefore WP13 remains `BLOCKED_EXTERNAL` for full crypto-exchange calibration.
The output is a descriptive public-data pilot, not a calibrated real-market
environment.
