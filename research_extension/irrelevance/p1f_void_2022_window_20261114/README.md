# P1F void run — 2022 retrospective window, 14 November 2026

**Status: VOID. No outcomes were computed. The P1F specification is still a DRAFT and is not registered.**

## What happened

A P1F executor run was attempted on a retrospective window of 60 UTC days starting
2022-03-01 (train: first 30 days; test: last 30 days) over the 30 USDT-margined
perpetuals with the largest February 2022 quote volume (`p1f_universe.json`).

All 3,600 daily files (5-minute klines and metrics, 30 symbols x 60 days x 2 file
types) were downloaded and checksum-verified (`verified: 3600, unverified: 0,
missing: 0`). Bar coverage was nevertheless 0.000 in both halves for every symbol,
so the registered coverage rule excluded all 30 symbols and the executor halted
with:

> VOID: fewer than 20 symbols meet the coverage rule

## Why coverage was zero

The companion data probe (`data_probe_2022-02-27_28.txt`) shows that in early 2022
the Binance USD-M `metrics` files exist but the class-ratio columns are empty:

- `sum_toptrader_long_short_ratio`: 0% non-null
- `count_toptrader_long_short_ratio`: 0% non-null
- `sum_taker_long_short_vol_ratio`: 0% non-null
- populated: `sum_open_interest`, `sum_open_interest_value`, `count_long_short_ratio`

The top-trader position/account ratios that P1F needs as class features were not
published in the 2022 metrics files. The coverage gate therefore did its job: it
refused to compute outcomes rather than silently dropping the class features.

## Consequences for the design

1. **No outcome information was obtained.** No estimator ran on class features and
   no ΔR², bootstrap bound, A1, A2 or A4 quantity was computed. The 2022 window is
   spent only for *coverage* purposes; it contains no usable P1F observations.
2. **The retrospective window must move forward in time.** Any Option R window
   needs a coverage-only probe showing the top-trader columns are populated for
   the full 60 days before the specification is registered. The spec's spent-ledger
   audit (P7S: July 2024 to October 2026; 2023-2024 training days) still applies.
3. **Option P (prospective, recommended in the draft spec) is unaffected** and
   remains the cleanest route.
4. The spec remains `ceiling_suite/p1_empirics/P1F_forecast_irrelevance_spec_DRAFT.md`
   (DRAFT, not registered). This run does not constitute registration, and
   `P1F_unlocks.json` was not created or incremented here.

## Files

- `p1f_results.json` — executor result, status VOID.
- `p1f_coverage.json` — per-symbol coverage (all 0.000) and file verification counts.
- `p1f_universe.json` — the 30-symbol universe and February 2022 quote volumes.
- `p1f_printed_summary.json` — the summary the executor printed.
- `p1f_log.txt` — full executor log.
- `data_probe_2022-02-27_28.txt` — the coverage-only probe of klines/metrics columns
  for BTCUSDT and ETHUSDT on 2022-02-27 and 2022-02-28.
