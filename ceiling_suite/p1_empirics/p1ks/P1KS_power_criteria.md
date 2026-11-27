# P1KS power check: design and pass criteria (fixed 27 November 2026, before any KRX data are read)

Written by an AI system for the authors, at the author's request in chat ("Yes: Korea, read 2015–19"). These criteria
are committed **before** the development-window calibration is run and before the power simulation exists. If the
check fails, nothing is registered, the failure is recorded here, and no 2020–2025 data are read.

## The test the check is for (primary, draft)

- **Event.** The 3 May 2021 resumption of short selling, for KOSPI 200 and KOSDAQ 150 constituents only.
- **Groups.** Treated stocks are the constituents of KOSPI 200 or KOSDAQ 150 on 3 May 2021. Control stocks are other
  KOSPI or KOSDAQ stocks, which stayed under the ban.
- **Before window.** 2020-05-04 to 2021-04-30, during the ban, about 250 trading days.
- **After window.** 2021-05-03 to 2022-04-29, about 250 trading days.
- **Predictor.** c_s, stock s's foreign tagged feedback contribution, estimated on 2015–2019 when short selling was
  allowed: c = κ_F w_F / (1 − r_F). Here r_F and w_F come from the tagged rule
  u_{F,t} = α + r_F u_{F,t−1} + w_F x_{t−1} + e, and κ_F from x_t = const + Σ_{j≤5} a_j x_{t−j} + κ_F u_{F,t−1} + e.
- **Outcome.** ΔŜ_s, the change in the sum of coefficients of an AR(10) in x across the two windows, from prices alone.
  This is Theorem 5.2(i) with the persistence absorbed into the first lag.
- **Primary statistic.** The coefficient b on Treated × c_s in the cross-sectional regression
  ΔŜ_s = b0 + b1 Treated_s + b2 c_s + b Treated_s × c_s + e_s, with heteroskedasticity-robust standard errors.
- **Prediction.** b > 0, tested one-sided at 5%. The theory predicts b = θ, the share of the foreign contribution
  switched back on.

## The power simulation (to be written after the calibration numbers are back)

- **Inputs from the development window, 2015–2019:**
  - the cross-stock distribution of c_s, by group;
  - the noise covariance of (ΔŜ_s, Δĉ_s) across a placebo split at 2017-07-01, rescaled to 250-day windows;
  - the reliability of ĉ_s between the two halves;
  - the numbers of treated and control stocks.
- **Simulation.** True c_s is drawn from the calibrated distribution. ĉ_s carries the calibrated measurement error.
  ΔS_s = θ c_s in treated stocks and 0 in controls, plus calibrated noise. There are 2,000 replications per case, seed
  20261127.
- **Cases:** θ = 0, 0.5 and 1.

## Pass criteria (all three must hold)

| Case | Required |
|---|---|
| θ = 0 (no effect) | rejection rate between 3% and 7% |
| θ = 1 (all foreign feedback switched) | power at least 80% |
| θ = 0.5 (half switched) | power at least 50% |

If any row fails, the design fails. Its parameters are not adjusted to pass, and the result is recorded below.

## Development-window rules

- Only data dated before 2020-01-01 are read; the notebook asserts this.
- Prices from 2014-09-01 start the 60-day trailing mean.
- The notebook prints summary statistics only: quantiles, standard deviations and correlations across stocks, and
  counts. It prints no stock-level estimates.
- Index membership comes from KOSPI 200 and KOSDAQ 150 constituents on 2019-01-02, for calibration by group. The
  test's own treatment assignment uses 3 May 2021 membership, which is read only if the test is registered.

## Data-source change (27 November 2026, before any data were read)

KRX Data Marketplace sign-up requires Korean identity verification (i-PIN or a Korean mobile number), so the account
cannot be created. The planned source is now Naver Finance:
- foreign net buying by stock and day, from the per-stock foreign/institution page;
- prices from Naver's daily chart service;
- shares outstanding implied by foreign holdings divided by the foreign ownership ratio;
- stock lists, including delisted stocks, from FinanceDataReader.

Two schema probes were run (column names, counts and dates only):
- Naver's desktop flow page now redirects to a page with no tables.
- The mobile trend endpoint returns `foreignerPureBuyQuant`, `organPureBuyQuant`, `individualPureBuyQuant`,
  `accumulatedTradingVolume`, `closePrice` and `foreignerHoldRatio` by day, and pages back to January 2015.
- The chart service reaches September 2014.

The calibration therefore uses the following, all fixed before any data were read:
- **Flows.** u = foreign net buying in shares / trailing 60-day mean volume. The contribution c = κ w/(1−r) does not
  depend on how u is scaled, because κ is estimated in the same units.
- **Prices.** Naver adjusted closes requested up to 2019-12-30. A stock with any daily move beyond the ±30% price limit
  is dropped as an unadjusted split.
- **Groups.** 'Large' is the top quarter of a 700-stock random sample by 2015–2019 traded value, a proxy for index
  membership that Naver does not keep. Membership on 3 May 2021 for the test itself must come from another public
  source before registration.

The first schema probe was `P1KS_Naver_Probe_Colab.ipynb`. It prints column names, row counts and the earliest
reachable date only. The test design and the pass criteria above are unchanged; only the data source changes.

## Open item before registration: treatment assignment

The treated set is the KOSPI 200 and KOSDAQ 150 constituents on 3 May 2021. Naver keeps no history of constituents,
and KRX requires a login. Candidate sources, in order:
1. KRX periodic-review announcements (June and December), chained from a dated full list.
2. Archived daily portfolio files of KOSPI 200 and KOSDAQ 150 index ETFs.
3. Treatment inferred from which stocks show any short-selling volume in May 2021, since the others were still
   banned. This uses test-window data for the treatment indicator only, and only after registration.

The choice is fixed in the spec before registration.

## Power simulation

`p1ks_power.py` (tests in `test_p1ks_power.py`) implements the simulation above. It takes the calibration JSON as its
only input. It was written and tested on synthetic inputs on 27 November 2026, before the calibration output existed.

## Results (27 November 2026)

**Calibration.** `P1KS_Dev_Window_Naver_Colab.ipynb` was run once by the author. Its code hash, `032cced2...`, matches
the committed `p1ks_dev.py`. It read only data dated before 2020. The output is
`results/p1ks_dev_calibration_20261127.json`:
- 700 sampled; 439 estimated;
- 178 failed on short history;
- 83 dropped for unadjusted split jumps;
- all prices came from siseJson;
- trend page size 60.

| Quantity | Large (top quarter by traded value) | Other |
|---|---|---|
| Stocks with full-window estimates | 110 | 324 |
| Foreign contribution c, median [5%, 95%] | −0.00012 [−0.0023, 0.0023] | −0.00006 [−0.0020, 0.0036] |
| Between-half correlation of ĉ | −0.007 | 0.20 |
| s.d. of placebo change in Ŝ (prices only) | 0.018 | 0.019 |
| Aggregate budget Ŝ, median | 0.966 | 0.964 |

**Power simulation.** `p1ks_power.py` was run once, at commit `e898299`, with 2,000 replications per case and seed
20261127. Output: `p1ks_power_results.json`.

| Case | Required | Result | Met? |
|---|---|---|---|
| θ = 0 | rejection 3–7% | 5.4% | Yes |
| θ = 1 | power ≥ 80% | 5.3% | **No** |
| θ = 0.5 | power ≥ 50% | 4.5% | **No** |

**Verdict: the design fails. It is not registered, and no 2020–2025 data will be read for it.**

**Why it fails.** There are two reasons, and either one is enough.
1. **The predictor is not reliable.** The two-half estimates of the foreign contribution are uncorrelated among large
   stocks (−0.007). The reliability of the full-window estimate is therefore floored at zero, and the predictor carries
   no stock-level information about the true contribution.
2. **The effect is too small.** Even with a perfectly measured predictor, the predicted effect is tiny relative to the
   noise in the outcome. The spread of c is about 0.0015, while the 250-day noise in ΔŜ is about 0.029. With 350
   treated stocks, the slope's standard error is about 0.029 / (0.0015 · √350) ≈ 1.0 against a predicted slope of
   θ ≤ 1, so power at θ = 1 would be about 26%.

**What the development window describes (not a test).** At daily frequency, foreign feedback adds about ±0.002 to a
budget near 0.965, the same order as in Taiwan (0.0014 of 0.97). This is the paper's own point: at daily frequency
the stakes of targeting by class are small, and the gap is informational rather than economic. A causal test of the
separation would need a market or frequency in which class feedback is a material share of the budget.

The design parameters are not adjusted to pass. Any new design is a new test, with its own committed criteria and the
author's approval.
