# Review 3 — market microstructure and historical L2 calibration

## Scope

This pass checked the downloaded public files, schemas, integrity checks, time
split, and whether the corpus supports the intended exchange simulator claims.

## Findings

1. **Critical boundary — `bookDepth` is not full order-level L2.** It exposes
   aggregate depth bands at percentage offsets. It cannot identify queue
   priority, cancellations, order arrivals, spread, or submitted-order fills.
2. **Medium — the aggregate-trade tape supports dependence diagnostics but not
   causal impact.** The signed impact quantity is a descriptive proxy and is
   labeled accordingly.
3. **Medium — one month and three symbols do not establish broad regime
   portability.** The chronological test split is useful for held-out
   description but not a multi-regime validation.
4. **High — the plan's full simulator-calibration acceptance criterion is not
   met by these files alone.** No replay has yet reproduced fill probability,
   spread, cancellation, or liquidation statistics.

## Implemented remediation

- Downloaded 93 `bookDepth` and 93 matched `aggTrades` archives for BTCUSDT,
  ETHUSDT, and SOLUSDT over January 2025.
- Verified every archive against the official adjacent SHA-256 sidecar: 93/93
  depth and 93/93 trade checksums.
- Added streaming parsers, schema checks, chronological 18/6/7-day splits,
  per-day outputs, and a machine-readable provenance manifest.
- Added `docs/L2_CALIBRATION_REPORT.md` and restricted the manuscript wording
  to depth-band/trade-tape calibration.

## Residual status

Queue-level/full-L2 replay calibration remains blocked. The paper must not call
this corpus a complete order-book or real-market simulator validation.
