# Historical crypto depth-band and trade-tape calibration

## Scope

This report documents the historical public-data calibration completed on the
working branch. It does **not** certify a full queue-level limit-order-book
replay. The Binance `bookDepth` product exposes aggregate depth at percentage
offsets, while `aggTrades` exposes aggregated executions. Neither file supplies
submitted-order identifiers, cancellations, queue position, best bid/ask
spread, or the response of a submitted order.

The source archive is the official [Binance public data repository](https://github.com/binance/binance-public-data/),
with daily files downloaded from the [public futures archive](https://data.binance.vision/data/futures/um/daily/).
No live orders, exchange credentials, or market intervention were used.

## Corpus and provenance

| Field | Value |
|---|---|
| Venue/product | Binance USD-M futures public archive |
| Symbols | BTCUSDT, ETHUSDT, SOLUSDT |
| Period | 2025-01-01 through 2025-01-31 |
| Depth files | 93 daily `bookDepth` archives |
| Trade files | 93 daily `aggTrades` archives |
| Storage | `/Volumes/T9/machine_markets_datasets/binance/futures/um/daily/` |
| Split | Chronological 18/6/7 days per symbol (60/20/20 by day) |
| Raw data in Git | No; only manifests and derived summaries are versioned |
| Archive integrity | 93 depth and 93 trade SHA-256 sidecar checksums verified |

The machine-readable outputs are:

- `studies/next_stage_validation/results/l2_calibration_results.json`
- `studies/next_stage_validation/results/l2_calibration_manifest.json`

The manifest records every archive path, byte count, observed SHA-256 digest,
expected sidecar digest, source URL, date support, and calibration-script hash.
AppleDouble files created by macOS are excluded by the archive filename
parser and are not treated as data.

## Observable results

The depth files contain ten percentage-offset bands per snapshot. The trade
files contain aggregate trade identifiers, price, quantity, trade-id range,
transaction time, and buyer-maker flag. The pipeline reports depth, notional,
trade count, quantity and notional, a return-volatility proxy, signed quantity
imbalance, order-flow sign autocorrelation, and a signed impact proxy.

Held-out test summaries from the saved output are:

| Symbol | Test days | Depth snapshots/day | Aggregate trades | Flow-sign autocorrelation | Return-volatility proxy |
|---|---:|---:|---:|---:|---:|
| BTCUSDT | 7 | 2,880 | 10,725,827 | 0.5212 | 0.00002578 |
| ETHUSDT | 7 | 2,880 | 11,111,798 | 0.5609 | 0.00002857 |
| SOLUSDT | 7 | 2,880 | 3,443,026 | 0.2569 | 0.00006188 |

These statistics are descriptive calibration targets. The signed impact value
is explicitly a proxy, not causal identification. The chronological test split
prevents the summary from being an in-sample-only report, but the period is
still one month and is not a regime-complete empirical validation.

## Boundary and remaining gate

This completes the historical **depth-band and aggregate-trade calibration
layer**. It does not complete the plan's full calibrated exchange environment.
The following remain blocked until an authorized source provides the required
event history or an equivalent validated interface:

- spread and top-of-book reconstruction;
- order submissions, cancellations, queue priority, and latency;
- fill-probability and partial-fill calibration;
- liquidation and margin-event linkage;
- replay validation of the simulator against held-out exchange statistics.

The manuscript therefore uses this dataset only for an empirical transfer
boundary and does not call it full L2, a fill model, or a real-market safety
test.

## Reproduction

With the raw archives mounted at the recorded T9 paths:

```text
python3.11 studies/next_stage_validation/scripts/run_l2_calibration.py \
  --depth-root /Volumes/T9/machine_markets_datasets/binance/futures/um/daily/bookDepth/2025-01 \
  --trades-root /Volumes/T9/machine_markets_datasets/binance/futures/um/daily/aggTrades/2025-01 \
  --output studies/next_stage_validation/results
```

The command fails closed if a pair is missing, symbols do not share date
support, an archive digest differs from its `.CHECKSUM` file, or a CSV schema
changes.
