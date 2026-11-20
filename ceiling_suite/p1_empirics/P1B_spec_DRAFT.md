# P1B: does removing one class of traders change prices through its feedback kernel only? Korea's short-selling ban

Written 20 November 2026 by an AI system for the authors, at the author's request in chat ("lets do ... a real
regulation aimed at one class of traders that the theory predicts correctly"). This is not independent review.

**Status: draft, not registered.** The theory's prediction, the statistics, the decision rules and the simulation
acceptance criteria below are fixed in this commit, before any Korean market data are read for this test. The
simulation check is then calibrated to pre-ban data only (section 8). If the check passes, the spec, estimator,
executor and notebook are hashed and registered with the author's explicit approval, and the data run happens once.
If it fails, nothing is registered and the failure is recorded here, as for P1K3.

What has and has not been seen. Nobody in this project has read Korean return or short-selling data from after
3 November 2023. Public news about the ban (its dates and rules) has been read. One web search on 20 November 2026
returned the titles of studies of the ban's market effects; none was opened, and none will be before the data run.

## 1. Question

Paper 1's sufficiency theorem (`thm:eqinv`) says a feedback group affects prices only through its kernel `k`, and
kernels add across groups. A regulation that removes one class of traders should therefore change price dynamics by
exactly that class's kernel, whatever else the class does. Korea's short-selling ban is such a regulation, and
Korea's exchange publishes the class's trades stock by stock: daily short-selling volume. P1B asks whether the change
in each stock's return dynamics when short sellers were removed (6 November 2023), and again when they returned
(31 March 2025), is predicted by the short sellers' own pre-ban response to past prices.

## 2. The theory's prediction

Take the sufficiency theorem with the public price statistic `s_t` equal to the day's return and a linear dealer,
`p_t = p_{t-1} + kappa y_t`. Part (i) gives the feedback flow `f_t = sum_m k_m r_{t-1-m}`, so returns follow

    r_t = kappa sum_m k_m r_{t-1-m} + kappa (other flow)_t ,       k = sum over classes c of k^(c).

Removing class `S`, with the other classes' rules unchanged (the paper's assumption that algorithms do not change
their rules), changes the autoregressive coefficients by exactly `-kappa k^(S)`. For small coefficients the lag-`j`
autocorrelation of returns is `kappa k_{j-1}` plus terms of second order, so the sum of the first five
autocorrelations, `A`, changes by

    Delta A = -kappa sum_{m<5} k^(S)_m  + second order.

Short sales are sales, so the class's buying is minus its short volume. If `gamma` is the slope of a stock's
short-selling share of volume on its return over the previous five days (in units of the stock's daily s.d.), then
`sum_{m<5} k^(S)_m` is proportional to `-gamma` times volume over volatility, and

    Delta A_i = theta * gamma_i ,   theta > 0 ,

where `theta` is the price impact of a day's volume in units of the stock's daily s.d., common across stocks to
first order (the normalization behind Amihud's measure; size and turnover controls absorb its variation).

Predictions, each fixed here before data:
- **P1 (ban).** Removing a contrarian class (`gamma > 0`: it shorts after rises) raises `A`; a momentum class lowers
  it. Across stocks, the change in `A` rises with `gamma`.
- **P2 (reinstatement).** When the class returns, the change reverses: across stocks, the change in `A` falls with
  `gamma`.
- **P3 (sufficiency, reported).** Given `gamma`, the class's trading intensity (mean short share) does not predict
  the change. **P4 (reported).** The two slopes have equal magnitude. **P5 (reported).** `gamma`, which needs the
  class tag, adds to the price-only predictor `A` before the ban.

Equilibrium. In Section 4's equilibrium the dealer's depth re-optimizes when a class leaves; the change in depth is
of the order of the removed kernel and multiplies the remaining kernel, so it enters `Delta A` at second order.

Limits. (a) Market makers and liquidity providers were exempt from the 2023 ban, so the removed class is the other
short sellers, while pre-ban `gamma` includes all short sales: this attenuates P1. (b) The class returned in 2025
under new rules (pre-borrowing checks, repayment limits), so its kernel may differ: this weakens P2 and is why P4 is
reported only. (c) Literature on short-selling bans (Beber and Pagano 2013; Saffi and Sigurdsson 2011; Boehmer and Wu
2013) links short sellers to price efficiency through their intensity; P3 and the use of `gamma`, not intensity, are
what distinguish the sufficiency prediction. Diether, Lee and Werner (2009) report contrarian daily shorting in US
stocks, so P1's likely sign is a rise in `A`, but the test does not assume the sign of `gamma`.

## 3. Events and regime

- 16 March 2020: short selling banned in all Korean stocks. 3 May 2021: resumed for KOSPI 200 and KOSDAQ 150
  constituents only.
- 5 November 2023 (Sunday): ban on all listed stocks announced, effective 6 November 2023; market makers and
  liquidity providers exempt. Extended to 30 March 2025.
- 31 March 2025: full reinstatement for all stocks.
Sources: Financial Services Commission press releases of 5 November 2023, 16 November 2023 and 24 March 2025.

Treated stocks had short selling throughout the pre-ban window; control stocks (non-constituents) had none from March
2020 to March 2025. Controls are used only for the reported difference in differences (K1).

## 4. Data

KRX Data Marketplace through `pykrx==1.2.9`, with the author's free KRX account (Colab Secrets `KRX_ID`, `KRX_PW`):
adjusted daily close, volume and trading value per stock; daily short-selling volume per stock; KOSPI (1001) and
KOSDAQ (2001) index closes; KOSPI 200 (1028) and KOSDAQ 150 (2203) constituent lists; sector classification and
market capitalization on 3 November 2023.

## 5. Samples and windows

- W0a 2021-06-01 to 2022-08-31 (kernel `gamma`); W0b 2022-09-01 to 2023-11-03 (baseline `A`). Pre-ban.
- W1 2023-12-04 to 2025-03-28 (ban; the first four weeks, which include short covering, are dropped).
- W2 2025-05-02 to 2026-10-30 (reinstated; the first month dropped).
- Treated: common stocks in the KOSPI 200 or KOSDAQ 150 on each of 1 June 2021, 1 December 2021, 2 June 2022,
  1 December 2022, 1 June 2023 and 3 November 2023 (first trading day on or after each date), listed on the first
  and last pre-ban days. Preferred shares, SPACs and REITs excluded.
- Control: for each treated stock in descending size, the nearest common non-constituent of the same market by log
  market capitalization on 3 November 2023, without replacement, never a constituent on the six dates.
- The lists are fixed by the calibration notebook from pre-ban data and saved with a hash; registration records it.

## 6. Variables and statistics (`p1b_core.py`)

- Return `r`: daily log change of the adjusted close; missing on a day with zero volume and on the day after.
- `z` in each window: residual of `r` on its market index return, minus the leave-one-out mean of the same residual in
  the stock's sector (sectors with at least 3 sample stocks), winsorized at 0.5% and 99.5%, divided by an EWMA
  volatility forecast (decay 0.94) built from earlier days only, winsorized again, demeaned and standardized.
- `A_i(W)` = sum over `j = 1..5` of the lag-`j` autocorrelation of `z` in window `W`.
- `gamma_i`: in W0a, OLS slope of the short share `s_t` (short volume over volume, winsorized) on
  `R_{t-1} = z_{t-1} + ... + z_{t-5}`, with an intercept. The same-day return is not a regressor: it is moved by the
  same day's short sales.
- A stock-window is valid if at least 80% of its trading days have a return; a stock enters if all four windows are
  valid.

Cross-sectional regressions over treated stocks, OLS with HC3 standard errors, regressors: standardized `gamma_i`,
standardized mean short share in W0a, log market capitalization, log turnover, KOSDAQ dummy:
- **K (primary):** `D_i = A_i(W1) - [A_i(W0b) + A_i(W2)]/2` on the regressors; `theta_K` is the coefficient on `gamma`.
- K2: `A_i(W1) - A_i(W0b)`; K3: `A_i(W2) - A_i(W1)` (same regressors).
- Reported only: K1 difference in differences of `A(W1) - A(W0b)`, treated against controls; K4 `theta_K2 + theta_K3
  = 0`; K5 coefficient on mean short share in K (P3: zero); K6 coefficient on `gamma` in K2 with `A(W0b)` added (P5).

## 7. Decision rule (one-sided, alpha = 0.05, normal approximation)

- **supportive:** `theta_K > 0` with one-sided p < 0.05, and `theta_K2 > 0` and `theta_K3 < 0` (both events agree in
  sign);
- **contradicted:** `theta_K < 0` with one-sided p < 0.05;
- **inconclusive:** otherwise.

What a result would mean. Supportive: in a regulation that removed one class of traders and then let it back, each
stock's price dynamics moved in proportion to the class's own pre-ban response to past prices, in the direction the
sufficiency theorem predicts, and back again. It does not show that only the kernel matters (P3 is reported, not
tested as a null), and it is a daily-horizon result about short sellers, not about intraday algorithms. Contradicted:
the changes went against the kernel; the sufficiency theorem's linear, rule-invariant reading does not describe this
regulation. Inconclusive: the data do not separate the prediction from noise. Whatever the verdict, Supplement S7
reports it as registered, and the main-text Evidence paragraph counts it.

## 8. Simulation check (criteria fixed before calibration)

`p1b_simulate.py` simulates panels of treated and control stocks over the same windows: returns with GARCH(1,1)
volatility and Student-t innovations, a market factor, sector shocks, other classes' feedback that differs by stock,
trading halts; a short-selling class whose share of volume responds to past returns with stock-specific `gamma`
(correlated with size and sector), persistent noise and a same-day response; its flow moves prices with impact
`kappa` while short selling is allowed (treated: W0a, W0b, W2; controls: W2 only). The statistics are computed by
`p1b_core.run_statistics`, the function the data run would use. `theta` per s.d. of the kernel is `5 kappa sd(gamma)`.

Smallest effect of interest: `theta = 0.03` per s.d. of `gamma` (a one-s.d. difference in the class's kernel moves
each of the first five autocorrelations by 0.006). It is fixed here and not changed after calibration.

| Case | Truth | Runs | Required |
|---|---|---|---|
| null | `kappa = 0` | 400 | supportive in at most 7% |
| null, wrong sign | same runs | | contradicted in at most 7% |
| null, size confound | `kappa = 0`; other classes' feedback changes with size at both events, `gamma` loads on size | 400 | supportive in at most 7% |
| SESOI | `theta = 0.03` | 400 | supportive in at least 80% |
| reported | SESOI with lag-1 kernel; SESOI with size confound; half and double SESOI; kernel on lags 6-10 (invisible to `A`); common post-ban shift for treated stocks | 100 each | |

The design passes only if all four required rows hold. Seeds: `SeedSequence([20261121, case, run])`.

Calibration (official runs only). `P1B_PreBan_Calibration_Colab.ipynb` downloads 1 June 2021 to 3 November 2023
only; a guard refuses any later date. `p1b_core.calibrate` sets the simulator's parameters from W0a and W0b: number
of stocks; mean short share (log-normal); `gamma` mean, its between-stock s.d. (covariance of estimates from the two
halves of W0a) and its sector share; short-share noise and persistence; other classes' feedback s.d. (covariance of
`A` across W0a and W0b); GARCH parameters from the autocorrelation of `z^2`; the t degrees of freedom matched to the
sample kurtosis; sector count and within-sector correlation; halt rates. The lengths of W1 and W2 are calendar
estimates (329 and 373 trading days), not read from data.

### Preliminary run (literature prior; smoke seeds; not the check)

Recorded in section 8a below after the run, whatever it shows.

## 9. Registration and data run (only if the check passes)

With the author's explicit approval: hash this spec, `p1b_core.py`, the executor and its notebook, and the treated and
control lists; create `P1B_unlocks.json` with `opens: 0`; push in a commit of its own. The notebook then downloads
1 June 2021 to 30 October 2026 for the listed stocks, runs `run_statistics` once, increments the counter, and prints
the verdict and every K statistic. No rerun, no change of windows, controls or lists.
