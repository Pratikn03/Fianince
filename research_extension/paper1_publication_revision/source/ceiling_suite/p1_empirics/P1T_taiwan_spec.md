# P1T: frozen primary-test specification (REGISTERED)

- **Status:** REGISTERED. Approved by the author (Pratik Niroula) on 2026-11-07 at 10:29 America/Chicago
  (16:29 UTC), before any development, validation or holdout data were requested.
- **Record:** this file, `P1T_taiwan_spec.json` and `P1T_unlocks.json` are committed together, with SHA-256 values in
  `P1T_SHA256SUMS`. Each period is opened once, and its unlock counter is recorded in `P1T_unlocks.json`.
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

## 10. Implementation clarifications (fixed at registration, before any data)

These make the approved definitions computable. They do not change the question, the statistic or the criteria.

1. **Price level across corporate events.**
   - The log price level is the cumulative sum of close-to-close log returns.
   - On an event day (change sign `X`, or listed in `TWT49U`) the stock's return is replaced by β̂ times the index
     return. Without this, ex-dividend price drops would enter x_t as pricing errors.
   - Event days and the following day are still excluded from every sample.
2. **β̂.**
   - OLS of daily stock log return on TAIEX log return over development days, excluding event days, the following
     days and limit days.
   - Fixed per stock thereafter.
3. **Trailing mean.**
   - m_t is the mean of (log P̃ − β̂ log TAIEX) over days t−60 … t−1.
   - It needs 60 prior valid days; x_t is missing until then.
4. **Classes from T86 fields.**
   - Foreign = `外陸資買賣超股數(不含外資自營商)` + `外資自營商買賣超股數`.
   - Investment trusts = `投信買賣超股數`.
   - Dealers' own account = `自營商買賣超股數(自行買賣)`.
   - Hedging control = `自營商買賣超股數(避險)`.
   - Residual = minus the sum of all five reported net series.
5. **Turnover rank.** Mean daily traded value (`成交金額`) over development days. Ties are broken by code.
6. **Missing days.**
   - A stock-day enters the forecast sample only if the stock traded on t, t−1 and t+1 and none of these is an
     excluded day.
   - A stock is dropped from a period if fewer than 95% of the period's trading days are usable.
7. **Fit period for the validation pass.** Development days. For the holdout, the trailing 1,000 trading days before
   2019-01-02.
8. **Request integrity.**
   - Every request is checked against the requested date.
   - A mismatch stops the run.
   - Raw responses are stored with their SHA-256.
9. **Executor.** `p1t_executor.py`, at the commit that records its simulation validation. That commit hash is
   entered in `P1T_unlocks.json` before the validation download.
