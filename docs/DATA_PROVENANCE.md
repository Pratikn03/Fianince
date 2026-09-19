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

The branch also uses an external T9 corpus of official Binance USD-M futures
daily archives for BTCUSDT, ETHUSDT, and SOLUSDT over January 2025:

- 93 `bookDepth` archives, with aggregate depth at percentage offsets;
- 93 matched `aggTrades` archives, with aggregate executions;
- 93/93 SHA-256 sidecar checksums verified for each product;
- chronological 18/6/7-day train/validation/test splits per symbol.

The raw corpus is not copied into GitHub. Its paths, bytes, observed and
expected hashes, date support, and script digest are recorded in
`studies/next_stage_validation/results/l2_calibration_manifest.json`; derived
statistics are in `l2_calibration_results.json`, and the interpretation is in
`docs/L2_CALIBRATION_REPORT.md`.

The depth-band/trade-tape calibration layer is complete internally. WP13
remains `BLOCKED_EXTERNAL` for full crypto-exchange calibration because these
files do not identify spread, cancellations, queue priority, submitted-order
fills, or liquidation linkage. The output is not a calibrated real-market
queue replay.
