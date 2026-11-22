# P1A development window: result of the calibration run (22 November 2026)

The first author ran `P1A_Dev_Window_Colab.ipynb` (pipeline sha256 108af4d2…) on the development window,
2024-01-01 to 2024-06-30. No test-window data was read, nothing was registered, and composition's effect on depth was
not estimated.

## What the floors did
- 211 pools traded; 37 had at least 100 swaps in every week; all 37 had complete measures in all 26 weeks.
- Every pool's median basis was within ±20 bps, so the token and decimals mapping is correct.
- The draft's 90%-of-seconds Binance activity floor removed 36 of 37 pools: even ETHUSDT trades in only 85% of
  seconds, USDCUSDT in 71%. The floor was dropped for the calibration (stale prices show up in the reliability).
- Without it: 35 pools in 28 pairs at a $1M median weekly volume; 20 pools (14 pairs) at $5M; 14 (10) at $20M.

## Calibration (35 pools, 28 pairs)
| Quantity | Measured | Simulation's assumption |
|---|---|---|
| Correlation of the two response halves, within | −0.002 | 0.37–0.88 |
| Instrument's correlation with composition, within | 0.09 | 0.12–0.49 |
| Instrument's first-stage F (clustered by pair) | 1.3 | registered floor 10 |
| Residual SD of log depth, within | 0.69 | 0.30 |
| Residual AR(1) of log depth | 0.64 | 0.5 |
| Pairs | 28 | about 40 needed |

## Reading
- **The instrument fails the validity floor by a wide margin** (F = 1.3 against 10). Under the draft rule the test
  would be reported as not informative, whatever the response measure.
- **The response measure has no within reliability** as built (half-correlation about zero, within SD about 200,
  far larger than a basis-closing rate should be). Part of this may be the measure itself: flows scaled by post-swap
  in-range liquidity have extreme values for swaps that cross many ticks. That could be fixed, but it would not
  rescue the instrument.
- **Depth is about 2.3 times noisier than assumed**, which alone multiplies the standard error of the composition
  effect by about 2.3.

## Decision
The test is not worth registering on this design: it would almost surely be reported as not informative. P1A is
stopped here, before registration. The exploration window existed to find this out, and the finding is reported here
as it came out.
