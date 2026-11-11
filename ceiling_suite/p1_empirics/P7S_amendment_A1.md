# P7S amendment A1 (approved by the author; registered 11 November 2026)

**Status.** Drafted and approved by the author on 11 November 2026 ("i approve all of above work"). Registered the
same day by hashing this file and the code into `P7S_SHA256SUMS`, before any development or evaluation data were
read.
- The approval is read as covering the recommended choices: window option B, margin `E = 0.10`, and the universe
  rule. Section 10 lists the details fixed after the approval; they are within those choices.
- The availability check ran on 11 November (`results/p7s_availability_printed_output.txt`). It confirmed that
  files exist for the proposed dates, so the dates of option B stand unchanged.
- Before registration the only Binance futures files read for P7S were the schema-probe files for the burned day
  2024-01-02 (three symbols). The availability check downloaded no file content.
- The frozen files `P7S_stress_spec.md` and `p7s_executor.py` are unchanged and keep their hashes. The frozen
  executor has not been run on market data.
- The primary evaluation window is retrospective. The paper must say so (section 5).

This amendment was written by an AI system. It is not independent review.

## 1. Why an amendment is needed

The audit of 10 November (`papers/paper1/review/AUDIT_20261110_main_commits.md`, item 5) found that the frozen
executor does not implement the registered spec:

| Registered in the spec | In the frozen executor |
|---|---|
| Stationary block bootstrap by date, the same dates for every asset | The 30 asset-level estimates are resampled independently. The date bootstrap function is never called |
| Proximity Π = open-interest value over its trailing 30-day maximum; development thresholds | Not implemented. No data pipeline |
| Margin `E = 0.0015`, "calibrated from development standard error" | No calibration exists. No development data have been read |
| A universe of 30 symbols | Typed in by hand. It includes `FTMUSDT`, which exchanges delisted in 2025 |
| Four sensitivity checks | Not implemented |
| (not in the spec) | No fixed readout text and no unlock log |

## 2. What A1 changes

A new executor, `p7s_executor_A1.py`, replaces the frozen one. The hypotheses, the estimands, the event definitions
and the decision rule of spec section 4 stay as registered, except for the points below.

1. **Proximity Π** is implemented as registered. It needs 30 full days of history and uses no later data.
2. **Units.** The response is divided by the symbol's development-period standard deviation of 60-minute returns.
   The registered response was in raw return units, so volatile symbols would dominate the average.
3. **Margin.** `E = 0.10` standard deviations of the 60-minute return, fixed now, before any data. It replaces
   `0.0015`. The 90% interval for the calm difference is reported, so a reader can apply another margin.
   **This is a judgment call for the author.** A smaller margin is stricter.
4. **Calm bars after stress.** A calm bar must have no stress bar in the previous 60 minutes. Without this rule the
   "calm" response contains the aftermath of large moves.
5. **Test for H2.** The registered percentile bootstrap is replaced by a time-shift test (section 3). The reason
   is a simulation finding: the percentile bootstrap rejected a true linear null in 8% and 9% of simulated data sets
   at the 90-day and 540-day windows, against a nominal 5% (section 4). H1 keeps the registered date bootstrap,
   with the same resampled dates for every symbol.
6. **Universe by rule.** USDT-margined perpetuals with a 5-minute kline file and a metrics file on every day of
   the warm-up and development periods, ranked by total quote volume in the development period. The top 30 enter.
   Symbols quoted against another stablecoin and index products (`USDCUSDT`, `BTCDOMUSDT`, `DEFIUSDT` and similar)
   are excluded by name before ranking. The list is written to a file and hashed before any evaluation data are
   read. A symbol enters the statistic only with at least 20 events in each of the four cells.
7. **Readout fixed in advance** (section 6) and an **unlock log**, `P7S_unlocks.json`, as for P1T.
8. **Sensitivity checks**, all descriptive. None enters the verdict.
   - Volatility normalization: trailing one-day realized volatility in place of the development value.
   - Top-trader state: the absolute log top-trader long/short ratio in place of Π.
   - Volume: the DiD within each development tercile of 5-minute quote volume.
   - The registered 30-day lead placebo is read from the shift distribution, which is reported in full.

## 3. The time-shift test for H2

- The high/low state series of every symbol is shifted in time by the same `k` days against the returns, wrapping
  around the ends, for `k = s, 2s, …, n − s`. Here `n` is the number of evaluation days and `s` the step. The DiD is
  recomputed for each shift.
- `n` must be a multiple of `s`. The shifted series and the unshifted series then form a cyclic group, and the test
  is exact if the state series is independent of the return series and both are stationary.
- `p = (1 + number of shifts with |DiD_k| ≥ |DiD|) / (n / s)`. The smallest possible `p` is `s / n`.
- Step: `s = 5` days when `n ≥ 500`, and `s = 1` day for a 90-day window.

**A correction made while drafting.** A first version used every shift from 5 to `n − 5` days. It rejected a true
null in 10 of 100 simulated data sets at 90 days, because those shifts do not form a group. The version above
replaced it. The results file of that first run was not kept; the figure is from the printed output.

## 4. Simulation results (simulated markets only, `validate_p7s_A1.py`)

Each simulated data set has 30 symbols on a 5-minute grid, a common return factor, common jumps and a common slow
component in open interest. "Two-layer" caps feedback flow when open interest is near its 30-day maximum, and the
cap binds only after large moves. "Linear" and "flat cap" are nulls for the DiD. "Calm leak" makes the cap bind in
ordinary moves. All runs use `E = 0.10` and 999 bootstrap draws.

| Window, shift step | Case | Data sets | H2 rejects, shift test | H2 rejects, percentile bootstrap (not used) | H1 passes | Verdicts | Mean DiD | Mean calm difference | Calm difference: spread across data sets / reported bootstrap SE |
|---|---|---|---|---|---|---|---|---|---|
| 90 days, step 1 | Two-layer (effect present) | 40 | 11 (27.5%) | 21 (52.5%) | 40 | 11 supportive, 29 inconclusive | -0.201 | -0.0086 | 0.0115 / 0.0116 |
| 90 days, step 1 | Linear (null) | 200 | 7 (3.5%) | 16 (8.0%) | 200 | 7 supportive, 193 inconclusive | -0.001 | -0.0001 | 0.0122 / 0.0123 |
| 90 days, step 1 | Flat cap (null) | 40 | 2 (5.0%) | 2 (5.0%) | 40 | 2 supportive, 38 inconclusive | +0.006 | -0.0027 | 0.0107 / 0.0117 |
| 90 days, step 1 | Calm leak | 40 | 5 (12.5%) | 12 (30.0%) | 0 | 40 inconsistent | -0.147 | -0.1431 | 0.0231 / 0.0175 |
| 540 days, step 5 | Two-layer (effect present) | 30 | 28 (93.3%) | 29 (96.7%) | 30 | 28 supportive, 2 inconclusive | -0.166 | -0.0059 | 0.0061 / 0.0049 |
| 540 days, step 5 | Linear (null) | 200 | 13 (6.5%) | 18 (9.0%) | 200 | 13 supportive, 187 inconclusive | +0.000 | -0.0004 | 0.0051 / 0.0049 |
| 540 days, step 5 | Flat cap (null) | 30 | 2 (6.7%) | 2 (6.7%) | 30 | 2 supportive, 28 inconclusive | -0.005 | -0.0001 | 0.0036 / 0.0047 |
| 540 days, step 5 | Calm leak | 30 | 22 (73.3%) | 24 (80.0%) | 0 | 30 inconsistent | -0.139 | -0.1453 | 0.0147 / 0.0070 |
| 850 days, step 5 | Two-layer (effect present) | 12 | 12 (100.0%) | 12 (100.0%) | 12 | 12 supportive | -0.164 | -0.0057 | 0.0057 / 0.0039 |
| 850 days, step 5 | Linear (null) | 40 | 1 (2.5%) | 2 (5.0%) | 40 | 1 supportive, 39 inconclusive | +0.006 | -0.0003 | 0.0038 / 0.0039 |
| 850 days, step 5 | Flat cap (null) | 12 | 0 (0.0%) | 0 (0.0%) | 12 | 12 inconclusive | +0.002 | -0.0009 | 0.0032 / 0.0038 |
| 850 days, step 5 | Calm leak | 12 | 11 (91.7%) | 12 (100.0%) | 0 | 12 inconsistent | -0.132 | -0.1437 | 0.0114 / 0.0057 |

Pooled over the three windows, the shift test rejected in 21 of 440 linear data sets (4.8%) and in 4 of 82 flat-cap data sets (4.9%). The nominal rate is 5%.

What the simulations show:
- **The 90-day window is valid but weak.** The time-shift test keeps its size (3.5% and 5% in the two nulls). It
  finds the simulated two-layer effect in about one data set in four. If the theory is right and the effect has the
  simulated size, the most likely verdict from the registered 90-day window is "inconclusive".
- **A long window fixes the power, not the meaning.** The test found the simulated effect in 28 of 30 data sets at
  540 days and in 12 of 12 at 850 days. It rejected in 6.5% and 2.5% of the linear nulls at those lengths. A longer
  window does not change what a rejection means (section 7).
- **The calm-leak case is always caught.** H1 failed in every calm-leak data set, at every window length.
- **The bootstrap standard error of the calm difference is accurate under the nulls and too small when an effect
  is present.** Under the linear null it matches the spread across data sets at every window. In the two-layer case
  at 540 and 850 days it is 20 to 30% too small, and in the calm-leak case about half the true spread at the long windows. No H1 result
  changed in simulation, because the calm difference was either far inside the margin or far outside it. A calm
  difference close to the margin should be read with that in mind.
- **The bootstrap standard error of the DiD is too small at 90 days** (0.10 to 0.11 reported, 0.12 across data
  sets). That is one reason H2 does not use it.
- **Limits of this evidence.** The size of the simulated effect was chosen by us. Power in real data is unknown.
  Real open interest may be more or less persistent than the simulated series.

## 5. The window: a decision for the author

| Option | Evaluation window | For | Against |
|---|---|---|---|
| **A. As registered** | 2026-11-16 to 2027-02-14, prospective. The spec calls this 90 days; counted inclusively it is 91 | Data do not exist yet. The cleanest design | Low power (about 1 in 4 in simulation). Result in February 2027 |
| **B. Retrospective primary, prospective replication** | Primary: 2024-07-01 to 2026-10-28 (850 days). Development: 2024-01-03 to 2024-06-30 (180 days). Warm-up: the 30 days before it, which include the burned schema-probe day and enter no test sample. The registered 90-day window is kept and reported as a replication | Enough data for a test with power. Result within days | Not prospective. Prices on some dates in this period were used earlier in the project for other statistics (30 perpetuals on 90 dates in 2023 to 2026; the stress guard on 76 dates in 2024 to 2026). Earlier tests also read Binance open interest on some dates, as a control variable and as a liquidation proxy. A search of the repository finds no earlier code that conditions on open interest relative to its trailing maximum. Must be disclosed in the paper |
| **C. Longer prospective window** | 2026-11-16 onward for about 18 months | Clean and powered | Result in mid-2028 |

- Option B depends on the files existing. `P7S_Availability_Colab.ipynb` checks that with listing and HEAD requests
  only. It downloads no file content. If metrics files are missing for the proposed dates, the window moves to the
  first date with complete files, and that is written into the amendment before it is hashed.
- Under option B the paper must say: "The sample is retrospective. The test was specified on [date], after the
  sample period, and run once."
- Under any option the test is run once. A failed or inconclusive result is reported as it comes out.

**Decision.** Option B, approved by the author on 11 November 2026. The dates are final (section 10).

## 6. Readout fixed in advance

Exactly one of these goes into the paper, with numbers from the results file.

- **Supportive.** "In a pre-specified test on Binance perpetual futures, the response to ordinary price moves did
  not depend on how close open interest was to its 30-day maximum (difference [x] standard deviations, 90% interval
  [a, b], inside the margin of ±0.10), and the response to large moves did (difference-in-differences [d], p = [p]).
  This is the pattern Section 7 predicts. Open interest is a proxy for proximity to position limits. The test does
  not identify the mechanism, and it does not test the identification theorem."
- **Inconsistent.** "In a pre-specified test on Binance perpetual futures, the response to ordinary price moves
  depended on how close open interest was to its 30-day maximum (difference [x] standard deviations, at or beyond
  the margin of 0.10). This is against the calm-silence prediction of Section 7."
- **Inconclusive.** "A pre-specified test on Binance perpetual futures was inconclusive (calm difference [x], 90%
  interval [a, b]; difference-in-differences [d], p = [p]). It neither supports nor contradicts the prediction of
  Section 7."

Any further sentence about the result is limited to stating numbers from the results file.

## 7. What a supportive result would and would not mean

- It would be evidence for the two-layer pattern: silence in calm markets, dependence under stress.
- It would not show that the cause is position limits. Liquidation cascades when open interest is high are a
  known feature of crypto futures, and they predict the same sign under stress.
- The equivalence margin is a choice. A reader who wants a stricter margin can read the interval.

## 8. Order of work

1. Done: approval, availability check, registration (this file and the code hashed and committed).
2. The author runs `P7S_A1_Development_Colab.ipynb` once. It reads warm-up and development data only.
3. The development outputs are committed with their SHA-256, and `P7S_unlocks.json` is updated.
4. `P7S_A1_Evaluation_Colab.ipynb` is then built for exactly those outputs and run once.
5. The result is reported as it comes out, with the readout of section 6.

## 9. Files

- `p7s_executor_A1.py`: the amended executor. Downloads nothing.
- `p7s_data.py`: archive addresses, the cached downloader, the parsers and the grid. Computes no statistic.
- `p7s_pipeline_A1.py`: the development stage and the evaluation stage, and the two window configurations.
- `make_p7s_A1_notebooks.py`: builds the notebooks. Each notebook carries the three code files and checks their
  SHA-256 before it runs.
- `test_p7s_executor_A1.py` (7 tests) and `test_p7s_pipeline_A1.py` (9 tests, including both stages run end to
  end on simulated markets served by a fake archive and compared with a direct computation).
- `validate_p7s_A1.py`, `validate_p7s_A1_results_hold90.json`, `…_hold540.json`, `…_hold850.json`: the simulations.
  The executor changed after those runs in two ways that do not alter any statistic (the shift test also returns
  its null values; bootstrap draws with an empty cell for every symbol are dropped). A rerun of 18 data sets with
  the final executor reproduced the stored p-values exactly.
- `make_p7s_availability_notebook.py`, `P7S_Availability_Colab.ipynb`: the listing-only availability check.
- `P7S_unlocks.json`: the unlock log.

## 10. Final specification (fixed at registration)

**Primary test (retrospective).**
- Warm-up: 2023-12-04 to 2024-01-02 (30 days). It includes the burned schema-probe day and enters no sample.
- Development: 2024-01-03 to 2024-06-30 (180 days).
- Evaluation: 2024-07-01 to 2026-10-28 (850 days). Shift step 5 days, so the test has 170 group elements and the
  smallest possible p is 0.0059. Bootstrap draws: 9,999. Seed: 20261108.

**Replication (prospective).** The registered window, 2026-11-16 to 2027-02-14 (91 days, shift step 1 day), with
development 2026-08-01 to 2026-10-31 and warm-up from 2026-07-02. Same code, universe drawn by the same rule from
its own development period. It is run once after the window closes and reported next to the primary result. It is
a replication; the verdict of P7S is the primary test's.

**Details fixed after the approval** (all within the approved rules):
1. *Exclusions by name.* Bases `USDC`, `BUSD`, `TUSD`, `FDUSD`, `USDP`, `DAI`, `EUR` (stablecoins and fiat) and
   `BTCDOM`, `DEFI`, `FOOTBALL`, `BLUEBIRD` (index products). Dated contracts (a `_` in the name), symbols not
   ending in `USDT` and names with non-ASCII characters are not candidates.
2. *Complete files.* A symbol is complete if the archive has its 5-minute kline file and its metrics file for
   every day of the warm-up and development periods. The top 30 complete symbols by development quote volume
   enter. "Not found" means a 404 answer, or a 403 answer for a file the bucket listing does not name. A download that
   fails for any other reason stops the run; it is never read as missing.
3. *Timing of the state.* The bar that opens at time t carries the return over the next five minutes. Its state
   is the metrics snapshot stamped t, which precedes that return. A missing snapshot is filled forward for at
   most 30 minutes.
4. *Missing data in the evaluation window.* The universe is fixed. A symbol with missing files or bars (for
   example after a delisting) contributes no events on those bars.
5. *Gate before any statistic.* The evaluation first downloads every file. It then counts events. If fewer than
   20 symbols have 20 events in every cell, it stops and reports "not evaluable" without computing a statistic.
6. *Sensitivity checks* use 999 bootstrap draws. The volume check uses the 5-minute quote volume of the event bar.
7. *One run.* The evaluation notebook accepts only the development outputs whose SHA-256 it carries, and it
   refuses to compute a second time in the same session. A run that stops during downloads is resumed, not rerun.

## 11. Addendum of 11 November 2026, after the development stage and before any evaluation data were read

- **Development stage run.** The author ran `P7S_A1_Development_Colab.ipynb`. The printed output is in
  `results/p7s_dev_printed_output.txt`. The development outputs have SHA-256 `7330ef3d…beae43`. The universe has 30
  symbols; `NEARUSDT`, `SUIUSDT` and `WLDUSDT` ranked high enough but were skipped by the rule because a warm-up or
  development file is missing. The universe includes `MATICUSDT` and `FTMUSDT`, which stop trading during the
  evaluation window; by section 10, item 4, they contribute no events after that.
- **A format gate was added to the evaluation notebook.** Before the evaluation it checks the layout of a sample
  of evaluation files: one day a month, and the first and last day, for the two largest symbols. It checks that the
  files exist and parse, that time stamps lie on the day's 5-minute grid, and that prices and metrics are present.
  If more than 10% of the sampled files fail, the run stops before any statistic. The gate can only stop the run.
  It computes no statistic and prints no price or open-interest value. The reason is that file layouts may have
  changed after the development period, and a layout change would otherwise lose data silently.
- **What changed in the hashed files.** `make_p7s_A1_notebooks.py` (the gate) and this file (this section). The
  executor, the data layer, the pipeline and the development notebook are unchanged, and their hashes are the
  registered ones. `P7S_SHA256SUMS` lists the old and new hashes.

