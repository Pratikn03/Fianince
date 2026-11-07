# P1T amendment A2: implementing the pre-specified diagnostics (7 November 2026)

**Status.** Approved by the author on 7 November 2026 ("Yes, build A2"), after validation pass 1 and before the holdout
is opened. Validation found that spec §7 (diagnostics) and §8 (S2, S3) had not been implemented in the executor. A2
implements them as written.
- **Unchanged:** the hypothesis, the primary statistic and the criteria. `run_period` is untouched, and the
  notebook checks that it reproduces the validation D exactly.
- **Executor:** sha256 `529a26c7f7ff49def539da1e108f199249f1f8f515a307b8f3c93ff801255a17`. The commit is recorded
  in `P1T_unlocks.json`.

## Implementation clarifications (fixed now, before the diagnostics see any data)

1. **Reverse-causality check (§7.1).**
   - Per stock, OLS of x_t on a constant, x_{t−1} and the flows u_{c,t}, u_{c,t−1} of Foreign, Investment trusts,
     Dealers' own, Residual and Hedging.
   - The OLS is fitted on fit-period days where all of these are finite.
   - x_t and x_{t−1} are replaced by the residuals in M1, and D is recomputed.
   - In the validation pass, the fit uses days from 2014-12-01 only, because E1 lacks the dealer split. The
     holdout fit window lies entirely in E2–E3.
2. **Stability (§7.3).** D by calendar year of the evaluation period, plus 2020-02-01 to 2020-06-30 for COVID.
3. **Sensitivity (§7.4).**
   - *Hedging included in the dealer class:* the dealer-total class.
   - *Net value / market-cap scaling:* **not computable.** Shares outstanding are not in the registered sources.
   - *Limit days dropped:* an origin is dropped if t−1, t or t+1 is a limit day or the day after one.
   - *2-day and 5-day periods:* non-overlapping blocks. Flows are summed, x is taken at the block's last day, and a
     block is a limit block if any of its days is a limit day. A stock enters if ≥ 80% of its evaluation blocks are
     usable. The bootstrap mean block is max(2, round(20/k)) blocks.
4. **Bootstrap for diagnostics.**
   - B = 1,999, using a vectorized stationary bootstrap with the same law and a different random stream.
   - The primary (B = 9,999) and S1 (registered B = 9,999) use the frozen bootstrap.
5. **S2 (§8).**
   - Per stock and class: IV of u_t on (1, u_{t−1}, x_t) with instruments (1, x_{t−1}, x_t).
   - Newey–West HAC with lag ⌊4(T/100)^{2/9}⌋.
   - Reported: medians and IQRs of r̂ and ŵ, and the shares of ŵ significantly positive and significantly negative.
   - For Foreign, also the share of stocks whose evaluation-period r̂_F lies in its fit-period 95% interval.
   - No p-value: pooled IV tests were rejected in the power analysis as biased.
6. **S3 (§8).**
   - Per stock, the eq. (ivvar) standard error of r̂_F, predicted from fit-period estimates for the evaluation
     sample size. σ_f² = Var(ê)/(1 + r̂²), and γ_x is truncated at lag 200.
   - This is divided by a stationary-bootstrap SE of r̂_F over evaluation equations (B = 199 per stock).
   - The outcome is the median ratio, with agreement if it lies in [0.67, 1.5].
7. **Holm (§8).** Applied to the two S1 one-sided p-values (Investment trusts, Dealers' own). S2 has no p-value,
   and S3 has a fixed agreement criterion.

## Simulation validation, reported as it came out

| Case | Primary | Reverse-causality check | Expected |
|---|---|---|---|
| (a) Feedback, w = 0.1 | supportive (D = 0.0102, 0.0133) | supportive (0.0051, 0.0077) | both supportive: **as expected** |
| (b) Null, w = 0 | inconsistent | inconsistent | neither supportive: **as expected** |
| (c) Confound: w = 0, strong impact, reporting noise SD = flow SD | supportive (0.0133, 0.0116) | **supportive** (0.0069, 0.0052) | check not supportive: **failed** |
| (d) Confound: w = 0, long-memory Foreign flow observed exactly | supportive in 1 of 3 runs (D ≤ 0.0015) | not supportive in 3 of 3 | check not supportive: **as expected** |

Files: `validate_executor_A2_results.json` for (a)–(c) and `validate_executor_A2_longmemory_results.json` for (d).

**What this means, stated before the diagnostics are run on data.**
- The registered reverse-causality check removes the gain that comes from the price level standing in for flow lags
  the forecasting model omits (case d).
- It **cannot** remove the gain that comes from prices revealing true flow better than noisy *reported* flow does
  (case c). It residualizes on the reported flows, so whatever the reports miss survives. No residualization on noisy
  reports can remove that channel. A supportive check therefore does not rule it out.
- This confound needs substantial reporting noise. The power analysis found a null gain ≤ 0.0006 for noise up to
  half the flow SD.
- TWSE T86 flows are exchange counts. Every accounting identity holds on 100% of stock-days in all three schema eras,
  but identities cannot detect misclassification between account types. So the paper must state the remaining
  confound and what it would take: misattributed foreign flow of roughly the size of the flow itself.
- S3 in simulation: the formula-to-bootstrap ratio was about 0.53 under feedback. The simulated flow errors are
  structural shocks, while eq. (ivvar) assumes pure measurement error. So S3 is a test of that error structure, and
  can fail for that reason alone.

## Run

`P1T_Diagnostics_A2_Colab.ipynb` makes no new downloads and never requests the holdout. It:
1. checks that the validation primary D = 0.04045892959202791 is reproduced;
2. runs every diagnostic on the validation period;
3. returns `p1t_A2_diagnostics_validation.zip`.

The run is labelled exploratory. The holdout runs the same diagnostics once, together with the primary.
