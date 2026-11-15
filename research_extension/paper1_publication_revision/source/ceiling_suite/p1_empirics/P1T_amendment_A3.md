# P1T amendment A3: repairing the reverse-causality check and S3 (8 November 2026)

**Status.**
- Approved by the author on 8 November 2026 ("Build A3"), after the A2 diagnostics were run on the validation period
  and before the holdout is opened. The holdout counter is 0.
- **Unchanged:** the hypothesis, the primary statistic and its criteria, `run_period`, and every function on the
  primary path. The A3 notebook checks that the validation primary `D = 0.04045892959202791` is reproduced exactly.

## What the validation run found (logged as it came out, `P1T_unlocks.json`)

1. **Reverse-causality check.** `D = −2.01 [−2.95, −1.17]`, while the median stock had `d = +0.0016`. Two
   investigations on the validation period only (`results/p1t_A3_investigation*_validation.zip`) found the cause.
   - **Collinearity.** The five flow regressors (Foreign, Trust, DealerOwn, Residual, Hedge) are exactly collinear
     in all 300 stocks, because Residual is minus the sum of the others. Least squares already discards that
     direction, so this is not what drives the explosion.
   - **The cause: dealer-hedging flow.** It is essentially zero in 2014–16 for the worst stocks and active in
     2017–18. Its fit-period coefficient comes from a handful of nonzero days and is extrapolated. For example, code
     8112 has a hedging coefficient of −10 and a residualized basis of 14.1 on 2017-08-24. Two stocks, with
     `d = −386` and `−176`, decide the mean.
2. **S3.** Eq. (ivvar) is defined only for `|r| < 1`. The fit-period tagged IV `r̂_F` lies outside (−1, 1) for 92.7%
   of stocks (5–95%: −18.6 to 14.5), so the formula overflowed.
   - This is a finding about the tagged IV in Taiwan daily data, not only a code defect. Its instrument is weak there.

## Changes (fixed before the holdout)

1. **Residual is not a regressor** in the reverse-causality regression. It adds no column space wherever the dealer
   split is reported, and the holdout fit window, 2015–18, has the split throughout.
2. **Zero-share screen.** A class whose flow is exactly zero on more than half of the stock's fit-period days is not
   a regressor for that stock. Its coefficient cannot be estimated stably, and it would be extrapolated.
3. **S3** is computed only for stocks with `|r̂_F| < 1` in the fit period. The number excluded
   (`n_excluded_abs_r_ge_1`) is reported next to the median.
4. **The per-stock median of `d`** for the reverse-causality check is reported as a descriptive statistic. The
   verdict stays on `D`.

Executor sha256: recorded in `P1T_unlocks.json` and `P1T_SHA256SUMS` at the commit of this amendment.

## Simulation validation, reported as it came out

The primary is unchanged by A3, so its simulated values are A2's. Only the check changes.

| Case | Primary (A2 = A3) | Check, A2 | Check, A3 |
|---|---|---|---|
| (a) Feedback, w = 0.1 | supportive (0.0102, 0.0133) | supportive (0.0051, 0.0077) | supportive (0.0061, 0.0085): **as expected** |
| (b) Null, w = 0 | inconsistent | not supportive | not supportive (−0.0009, −0.0016): **as expected** |
| (c) Confound, noisy reports | supportive (0.0133, 0.0116) | supportive (known failure) | supportive (0.0089, 0.0068): **same known failure** |
| (d) Long-memory confound, exact flows | supportive in 1 of 3: seed 1, `D = 0.0015 [0.0003, 0.0028]` | not supportive in 3 of 3 | **supportive in 1 of 3** (seed 1): `D = 0.0011 [0.0005, 0.0017]`. Not supportive for seeds 2 and 3 (0.0006, 0.0005). |

Files: `validate_executor_A3_results.json` for (a)–(c) and `validate_executor_A3_longmemory_results.json` for (d).
They were produced by the unchanged scripts `validate_executor_A2.py` and `validate_executor_A2_longmemory.py` run with
the A3 executor. The A2 result files are kept unchanged.

**The change in (d) corrects A2's account of that case.**
- In the simulated validation period the dealer split is missing for 2013–14 (era E1).
- Under A2, the regressors were all-zero dealer columns that are NaN in E1. So the check fitted on 2014-12 to 2016
  only, about half the primary's sample. The out-of-sample cost of that shorter fit pushed the residualized gain
  below zero (−0.0007, −0.0015, −0.0004).
- A2's "as expected" for (d) was therefore partly an artifact of sample truncation.
- Under A3 the check uses the same fit sample as the primary.
- What remains is that a long-memory confound can leave a small, statistically significant gain. Here it is about a
  third of `D*`, in the same run in which the primary was itself supportive with an interval wholly below `D*`. The 60-day trailing mean in `x_t` carries slow-flow information that the regression on `x_{t−1}`
  and two flow lags does not remove.

The validation-period truncation cannot arise in the holdout, whose trailing 1,000-day fit window lies entirely in
eras E2–E3.

**Not simulated:** a hedging flow that switches on between periods. The A3 notebook shows on the validation period
whether the explosion is gone.

## Reading of the check, fixed now (adds to `P1T_HOLDOUT_READOUT.md` §2; the readout file itself is not edited)

If the reverse-causality check is "supportive" by the §6 rule but its 95% interval lies entirely below
`D* = 0.0035`, the paper says three things:
1. The surviving gain is smaller than the minimum effect of interest.
2. In simulation, a long-memory confound with no feedback left a gain of that size (A3, case d).
3. Such a result does not distinguish feedback from that confound.

The first column of the "Gain survives" row in readout §2 cites A2 case (d). Whatever the interval, the paper adds:
"In simulation, a long-memory confound with no feedback left a residualized gain of about 0.001 (amendment A3)."

The primary verdict is unaffected.

## Proposed addition on the primary (needs the author's approval; not in force until it is logged)

Case (d) also shows the **primary** can be supportive under §6 with no feedback. Its interval then lies wholly below
`D*` (seed 1: `[0.0003, 0.0028]`). A2 reported this, but the readout does not address it.

Proposed rule: if the holdout primary is supportive and its upper bound is below `D* = 0.0035`, then:
- the verdict stays "supportive";
- readings A and B gain the sentence "The gain is smaller than the minimum effect of interest, and in simulation a
  long-memory confound with no feedback produced a supportive result of this size (amendments A2 and A3)";
- the abstract says "a small gain, below the registered minimum effect of interest" instead of "responds as the
  model's flow equation requires".
