# Public data acquisition status

The files under `raw/binance/` are a small public pilot, not the complete empirical
dataset required for the paper.

Downloaded and checksum-verified:

- BTCUSDT spot 1-minute klines for January 2025
- ETHUSDT spot 1-hour klines for January 2025
- SOLUSDT spot 1-hour klines for January 2025
- One current 100-level depth snapshot for each symbol

Historical klines/trades are available from Binance Public Data. A separate T9
corpus now contains 93 daily `bookDepth` and 93 matched `aggTrades` archives for
three USD-M futures symbols in January 2025. Those files are aggregate depth bands
and trades, not full queue-level L2, and are documented in
`docs/L2_CALIBRATION_REPORT.md` rather than copied into this Git checkout.

The acquisition record is in `acquisition_manifest.json`. Every downloaded archive has
an accompanying official `.CHECKSUM` file; the snapshots have local SHA-256 values in
that manifest.
