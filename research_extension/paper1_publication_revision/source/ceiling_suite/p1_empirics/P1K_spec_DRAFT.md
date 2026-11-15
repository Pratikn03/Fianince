# P1K: Korea multi-class tagged flows (DRAFT: not approved, not registered)

Drafted 11 November 2026 by an AI system for the author's approval. Nothing here is in force. No KRX data have been
read. This is not independent review.

## 1. Purpose

Paper 1's theorems are about trader classes whose flows are tagged. Public data with many tagged classes exist for
Korea: KRX reports, for each stock and day, net purchases by about eleven investor categories (financial investment,
insurance, investment trusts, private equity, banks, other financial institutions, pension funds, other
corporations, individuals, foreigners, other foreigners). P1K uses them for the first direct test of three claims of
the paper. It cannot test them at the frequency of algorithmic trading; daily data test the daily version.

## 2. Data and samples

- **Source.** KRX Data Marketplace through the `pykrx` package (version pinned at registration), with the author's
  free KRX account. Daily net purchase value by detailed investor category, daily close and market capitalization.
- **Universe.** KOSPI 200 constituents on the first trading day of each calendar year, kept for that year.
  Survivorship: a stock leaves the sample when it stops trading.
- **Development sample:** 2012-01-01 to 2018-12-31. **Holdout:** 2019-01-01 to 2025-12-31, opened once.
- **Burned day:** 2012-01-02, used only by the schema probe.

## 3. Variables

- Pricing-error proxy `x_{s,t}`: log close minus its trailing 60-day mean, divided by the stock's development-period
  standard deviation of daily log returns.
- Class flow `u_{i,s,t}`: net purchase value of class `i` divided by the stock's market capitalization at `t-1`.

## 4. Estimation (Paper 1, Proposition 6.2, with lagged instruments)

For each stock-year and class: `u_{i,t} = r_i u_{i,t-1} + w_i x_t + e_{i,t}`, estimated by IV with instruments
`(x_{t-1}, x_{t-2})`. Same-day price is not an instrument, because flow moves the same day's price (the reverse
causality found by P1T). Stock-year kernel: `k_m = sum_i w_i r_i^m` for `m = 0..9`, using classes with estimated
`r_i` in `[0, 0.99]`.

## 5. Hypotheses (decision rules fixed before any data)

- **H1, tags identify memories.** The median across stock-years of each class's `r_i` differs between classes:
  Kruskal-Wallis test across classes on holdout stock-years, `p < 0.01`.
- **H2, sufficiency.** Outcome `Y`: the stock-year's daily return autocorrelations at lags 1-10. Two out-of-sample
  predictors fitted on development stock-years: (A) kernel `k_0..k_9`; (B) kernel plus class composition (each
  class's share of `sum_i |w_i|`). H2 supportive if, on holdout stock-years, (A) beats the year-and-size baseline by
  a block-bootstrap 95% interval excluding zero, and the gain of (B) over (A) has a 90% interval inside
  `(-E, E)`, with `E` = 10% of (A)'s gain over the baseline.
- **H3, prices alone do not recover the tags.** Descriptive: the correlation between memory rates fitted to price
  autocorrelations alone and the tagged estimates, reported with its interval.

Verdict for the paper: supportive if H1 and H2; inconsistent if (B) beats (A) by more than `E`; else
inconclusive. Each is reported as it comes out.

## 6. Before registration

1. The author approves or changes this draft (universe, years, `E`, instruments).
2. Schema probe (`P1K_Probe_Colab.ipynb`): one burned day, three stocks, column names only.
3. A simulation check of the estimators on simulated markets, like P7S, to measure size and power.
4. Executor, notebooks and this spec hashed and committed before any development data are read.

## 7. What a supportive result would and would not mean

It would be the first evidence, on real tagged flows, that price dynamics depend on trader classes through the
kernel. It would not test intraday algorithmic feedback, and daily flows mix many motives besides feedback.

## 8. Simulation check of this draft (11-12 November 2026): the design is not ready

`p1k_executor.py` implements sections 3-5; `validate_p1k.py` simulates markets with 11 tagged classes in which the
sufficiency theorem holds exactly ("sufficient"), and markets in which it fails ("composition": one class trades
on the price five days back).

| Outcome measure | Case | Runs | Verdicts |
|---|---|---|---|
| Return autocorrelations, lags 1-10 | sufficient | 2 | 2 inconclusive |
| Return autocorrelations, lags 1-10 | composition (theorem false) | 2 | 1 **supportive**, 1 inconclusive |
| Autocorrelations of x, lags 1, 2, 5, 10, 20 | sufficient | 3 | 3 inconclusive |
| Autocorrelations of x, lags 1, 2, 5, 10, 20 | composition (theorem false) | 3 | 3 inconclusive |

Reading: per stock-year IV estimates for 11 classes, with lagged instruments, are too noisy for the estimated
kernel to predict anything, even when the theorem is true by construction. And one run returned "supportive" in
a market where the theorem is false. The draft must not be registered or run on KRX data in this form.

What a workable design needs (not yet done): class memories estimated by pooling across stocks rather than per
stock-year; an outcome the kernel moves strongly; and a simulation showing low false "supportive" rates when the
theorem is false and real power when it is true, before anything is registered.

## 9. Design 2 and its simulation check (12 November 2026): still not ready

`p1k_executor_v2.py` changes three things from design 1: one memory per class pooled across stocks (grid search
over r of the stock-year regressions of u_t on (1, x_t, m_{t-1}(r)), so that same-day reverse causality touches
only the x_t coefficient); x autocorrelations at lags 1, 2, 5, 10, 20 as the outcome; and each stock's own
development-period mean outcome as an offset. `validate_p1k_v2.py` simulates 120 stocks with 11 classes whose
memories are common across stocks (jitter 0.1), class activity that drifts year to year, and traders who update on
the same public price statistic the executor computes. Three runs per case, 299 bootstrap draws
(`validate_p1k_v2_results.json`).

| Case | Verdicts | Kernel gain G_A, 95% interval excludes zero | Largest memory error |
|---|---|---|---|
| sufficient (theorem true) | 3 inconclusive | 1 of 3 | 0.018 |
| composition (theorem false) | 3 inconclusive | 1 of 3 | 0.024 |
| null (no feedback) | 3 inconclusive | 0 of 3 | not defined (no memory to find) |

Reading.
- **Memories: solved.** Pooling recovers every class's memory to within 0.024 when feedback is present. A test of
  "investor classes have different memories" (H1) would have power.
- **Sufficiency (H2): not solved.** The kernel predicts the outcome reliably in only one of three runs where the
  theorem holds, so the test has little power.
- **A hazard.** With no feedback at all, composition shares still "predict" the outcome (G_BA up to 0.0016,
  interval excluding zero in two of three runs), because estimated weights then measure noise that differs across
  stocks. Had the kernel also shown a gain, the rule would have returned a false "inconsistent".
- **A rule problem.** The equivalence rule asks the 90% interval of G_BA to lie inside (-E, E). Composition that
  makes forecasts worse (G_BA below -E) is not evidence against sufficiency; a one-sided rule (upper bound below E)
  is the right form. This alone would not fix the power.

Neither design may be registered or run on KRX data. A design 3, if pursued, would test sufficiency where it bites,
in the pooled price equation (whether lagged class flows enter the price response only through their sum), and
must pass the same three-case simulation, including the null case, before the author is asked to approve it.
