# Bounded empirical evidence repair — 2026-09-26

All inputs are frozen local artifacts. No new data, paper edits, or historical result replacements.

## Coinbase evidence reconciliation

| Evidence and specification | n / df | F coefficient | SE | t | p (two sided) | R² |
|---|---:|---:|---:|---:|---:|---:|
| Legacy paper bivariate (unreproduced) | 10 / 8 | 0.6866 | 0.2778 | 2.47 | 0.039 | 0.4330 |
| Serialized rows, bivariate | 10 / 8 | 0.518781819485 | 0.272815008616 | 1.901588267145 | 0.093738292833 | 0.311297015137 |
| Serialized rows, with spread + volatility | 10 / 6 | 0.370952992405 | 0.300894316568 | 1.232834825982 | 0.263746920310 | 0.518494330750 |
| Frozen cache, bivariate | 10 / 8 | 0.686638812316 | 0.283025244787 | 2.426069140341 | 0.041455688572 | 0.423872345153 |
| Frozen cache, with spread + volatility | 10 / 6 | 0.958333680272 | 0.387885377993 | 2.470662042560 | 0.048414233378 | 0.549207850403 |

The saved full-model coefficients and R² reproduce from the serialized rows. The claimed historical bivariate combination does not. The cached full-model t=2.470662 and p=0.048414 belong to its controlled specification (6 df), not its bivariate specification (8 df). This numerical resemblance does not establish the origin of the legacy claim.

Each cached Coinbase asset has 350 closes and 349 returns: A=[0,244), B=[244,349). The ten symbols and exact row order are serialized in coinbase_audit.json. Historical serialized rows lack recoverable source-window indices. All ten cache rows differ from their saved counterparts. No sample is selected on significance.

Period B does not enter F, but it does enter the cross-sectional slope estimates. The fitted residual comparisons are descriptive in-sample reductions; adding regressors mechanically reduces training SSE. These results do not establish forecast performance. Conventional standard errors assume homoskedastic, independent cross-asset residuals and are exploratory with n=10.

The Coinbase cache has 1,000 tick flows versus 350 candle closes per asset, with no alignment timestamps. All ten S_model estimates are explicitly unavailable. Snapshot spread timing is also unverified. No F-for-S fallback or invented flow is used.

## Corrected chronological Binance run

All ten fixed markets and all five seeds (42, 101, 777, 1234, 2026), ten fixed epochs each. Each 500-price tick path has 499 transitions: training=[0,349), validation=[349,499). Every epoch uses the entire ordered training prefix. Exact two-state recursion retains all memory and carries state into validation. The zero initial state, original positive parameter bounds, absolute price-change target, and Q² penalty (0.01) are maintained assumptions; no validation-based tuning or seed selection.

| Asset | Status | Mean S | Seed SD | Mean conditional validation R² | Failed seeds |
|---|---|---:|---:|---:|---:|
| BTCUSDT | ok | 0.118111514283 | 1.15509474464e-05 | -0.0682968813452 | 0 |
| ETHUSDT | ok | 0.541084008508 | 4.81423372732e-07 | -0.0105816804806 | 0 |
| SOLUSDT | ok | 0.307989561438 | 0.00924638654394 | -0.0444962020681 | 0 |
| DOGEUSDT | ok | 0.02 | 0 | -3784.32201859 | 0 |
| NEARUSDT | ok | 0.469673360181 | 0.00266093992685 | -0.0100593729946 | 0 |
| ADAUSDT | ok | 0.02 | 0 | -5.99857625684 | 0 |
| AVAXUSDT | failed_seed_panel | unavailable | unavailable | unavailable | 3 |
| LTCUSDT | failed_seed_panel | unavailable | unavailable | unavailable | 1 |
| LINKUSDT | failed_seed_panel | unavailable | unavailable | unavailable | 4 |
| DOTUSDT | ok | 0.02 | 0 | -0.021153631131 | 0 |

Corrected cross-asset regression unavailable: At least one requested seed failed; no survivor regression.

Conditional validation R² uses realized validation flow and the validation-mean denominator; negative values are not clipped. Seed SD measures initialization sensitivity, not sampling uncertainty. Optimizer success is not identification, causal validity, or a market-stability certificate. Boundary hits, spectral radii, losses, parameters, predictions and optimizer diagnostics are saved for every accepted seed; failures stay in the requested panel and suppress aggregate claims.

The cache preserves array order but omits tick/candle timestamps and IDs. Chronology is conditional on the stored order; alignment of tick Period A to candle Period B cannot be verified. The repaired fit therefore cannot support a cross-window forecast claim. The legacy Binance result is retained in legacy_binance.json and superseded only as an implementation result, not overwritten.

## Safe manuscript wording

> “Reanalysis distinguishes two frozen empirical samples. The ten serialized Coinbase rows yield an exploratory bivariate association between the Period-A persistence proxy and Period-B autocorrelation (t=1.901588, p=0.093738, R²=0.311297); adding spread and volatility gives t=1.232835, p=0.263747, R²=0.518494. Independently reconstructing the frozen price cache gives bivariate t=2.426069, p=0.041456, R²=0.423872 and controlled-model t=2.470662, p=0.048414, R²=0.549208. These samples differ, and neither reproduces the historical bivariate claim t=2.47, p=0.039, R²=0.4330. Regression slopes are estimated using the same assets’ Period-B outcomes, so results are in-sample explanatory associations rather than out-of-sample forecast evidence. The corrected Binance fits preserve chronological state recursion and report all requested seeds; timestamp limitations and initialization sensitivity preclude a claim of identified market feedback or certified stability.”

## Reproduction and provenance

Run from the repository root with Python 3.11:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3.11 -m research_extension.evidence_repair.empirical_report --output-dir research_extension/outputs/evidence_repair_20260926/empirical/fresh-run
```

The generator refuses an existing output directory and exclusively creates each artifact, blocking differing overwrites. Choose a fresh --output-dir under the authorized empirical directory for each rerun. It blocks network connections and verifies fixed input and source hashes before sealing. samples.json preserves exact input arrays/rows and canonical per-asset hashes. manifest.json binds source files, inputs, generated artifacts and available test receipts. OLS is checked independently with scipy.linregress and QR; cache features are independently reconstructed from prices. tests_red.txt records the pre-fix failures; subsequent test receipts report verification separately from empirical validity.
