# Public data acquisition status

The files under `raw/binance/` are a small public pilot, not the complete empirical
dataset required for the paper.

Downloaded and checksum-verified:

- BTCUSDT spot 1-minute klines for January 2025
- ETHUSDT spot 1-hour klines for January 2025
- SOLUSDT spot 1-hour klines for January 2025
- One current 100-level depth snapshot for each symbol

Historical klines/trades are available from Binance Public Data. Historical full L2
order-book data is not included here: the public documentation describes request-based
or restricted historical depth products, so a current snapshot must not be treated as
a historical calibration dataset.

The acquisition record is in `acquisition_manifest.json`. Every downloaded archive has
an accompanying official `.CHECKSUM` file; the snapshots have local SHA-256 values in
that manifest.

