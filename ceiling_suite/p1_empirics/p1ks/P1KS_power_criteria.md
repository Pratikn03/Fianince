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

## Results

(Filled in after the calibration and the simulation are run.)
