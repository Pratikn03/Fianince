# P1T: frozen primary-test specification (DRAFT, needs author approval; not yet registered)

- **Status:** DRAFT, 7 November 2026.
- **Registration:** when approved, this file and `P1T_taiwan_spec.json` are committed with their SHA-256 before any
  test-period data are requested. Each period is opened once and the unlock counters are recorded.
- **Basis:** `OBSERVATION_DESIGN.md` (universe, classes, prices, model link), `DATA_DICTIONARY.md` (sources, burned
  days) and `power/POWER_ANALYSIS.md` (why this primary test, and the period lengths).

## 1. Single primary question

Does a class's own tagged daily flow respond to the price deviation, as the model's flow equation
u_{i,t} = r_i u_{i,t-1} + w_i x_t requires (w_i ≠ 0)?

The measure is whether the market-reference basis improves out-of-sample next-day forecasts of that class's flow
beyond the flow's own two lags. The primary class is **Foreign**.

### Scope

This tests the feedback premise of the model on tagged flow. It does **not** test the identification theorem
("prices alone cannot separate the classes"); that is a mathematical result. A supportive outcome means the class
flow channel that Proposition 6.1 exploits is present in real data. A failure means it is undetectable at the
pre-specified effect size.

## 2. Data and periods (TWSE common stocks)

| Period | Dates | Approx. trading days | Use |
|---|---|---|---|
| Development | 2013-01-02 to 2016-12-30 | ≈ 985 | Universe filter, scale constants, β̂, model fits; free exploration |
| Validation | 2017-01-03 to 2018-12-28 | ≈ 490 | One pass of the frozen pipeline end to end; may fix bugs, not change the hypothesis or criteria |
| Holdout | 2019-01-02 to 2023-12-29 | ≈ 1,230 | Opened once for the primary and secondary results |
| Reserved | 2024-01-01 onward | — | Not used. Contains the burned days. Kept for a later extension. |

- **Burned and excluded:** 2024-01-02, 2024-01-03 (TWSE/TPEx); 2026-11-06 (TPEx).
- **Fitting inside the holdout:** each stock's forecast coefficients are fitted on the trailing 1,000 days available
  at the start of the holdout (development plus validation), then held fixed. No refitting inside the holdout.

## 3. Variables

As in `OBSERVATION_DESIGN.md`:
- Classes: Foreign (including foreign dealers), Investment trusts, Dealers' own account, Residual. Dealer hedging is
  a control only.
- Flow u_{i,t} = net shares / development-period average daily volume.
- x_t = log P_t − β̂ log TAIEX_t − trailing 60-day mean. This is the market-reference basis.
- Universe: top 300 four-digit common stocks by development-period turnover, with the event, listing and suspension
  exclusions.
- Limit days: an indicator in the forecast regression.

## 4. Estimator and statistic

For each stock s, two OLS forecasting models of ũ_{F,t+1} with an intercept and a limit-day indicator:
- **M0:** ũ_{F,t}, ũ_{F,t-1}.
- **M1:** M0 plus x_t, x_{t-1}.

d_s = [MSE₀ − MSE₁] / Var_fit(ũ_F) over holdout days.

**Primary statistic:** D = the mean of d_s over the universe.

## 5. Uncertainty and dependence

- Stationary block bootstrap over **dates**: the same dates are resampled for all stocks, preserving cross-sectional
  dependence.
- Mean block length 20 trading days; 9,999 resamples; seed 20261107.
- One-sided p-value for D > 0, and a two-sided 95% percentile interval.
- Robustness checks (reported, not decisive): block lengths 10 and 60.

## 6. Criteria (minimum effect of interest D* = 0.0035, from the sizing study)

| Outcome | Rule |
|---|---|
| **Supportive** | p < 0.05 **and** D > 0 **and** the lower 95% bound > 0 |
| **Inconsistent with the model's feedback at the effect of interest** | upper 95% bound < D* |
| **Inconclusive** | anything else, including significant but tiny gains whose interval includes values below D* and above 0 |

## 7. Pre-specified diagnostics (reported whatever the outcome)

1. **Reverse-causality check:** recompute D with x_t replaced by its residual from a fit-period regression of x_t on
   x_{t-1} and the lagged reported flows of all four classes and of dealer hedging. If prices merely reveal past flow
   (the confound found in the power analysis), the gain disappears with the residual. A gain that survives is not
   explained by that channel.
2. Per-stock share of d_s > 0.
3. Stability: D by calendar year within the holdout, including the 2020 COVID period separately.
4. Sensitivity:
   - hedging included in the dealer class;
   - net value / market cap scaling;
   - limit days and the following day dropped;
   - two-day and five-day periods.

## 8. Secondary outcomes (Holm adjustment across the three)

- S1: the same test for Investment trusts and Dealers' own account.
- S2: Proposition 6.1 tagged IV estimates (r_i, w_i) per class with HAC intervals, and the share of stocks where the
  holdout estimate of r_F lies in the development 95% interval.
- S3: the holdout prediction of the formula-based standard error of r̂_F (eq. `eq:ivvar` with development estimates)
  against the bootstrap standard error in the holdout. Agreement criterion: ratio in [0.67, 1.5].

## 9. Recorded before data

- Candidates A (Hansen J) and B (pooled targeted Wald) were considered and rejected for lack of power and validity
  (`power/POWER_ANALYSIS.md`). If they are run, they are labelled exploratory.
- Executor: `p1t_executor.py`, still to be written. It is validated on simulated data from `power_sim.py`
  (recovering D ≈ 0 under w = 0 and D > D* under w = 0.1) **before** the validation period is downloaded.
