# Power analysis for the Taiwan tagged-flow test (7 November 2026; simulation only, no market data)

**Code:** `power_sim.py`, `targeted_sim.py`, `predictive_sim.py`, `sizing.py`.

**Results:** `power_results.json`, `targeted_results.json`, `predictive_results.json`, `sizing_results.json`.

**Data-generating process.** The paper's recursion with price-first ordering:
- x_{t+1} = a x_t + κ Σ_i u_{i,t} + ξ;
- u_{i,t+1} = r_i u_{i,t} + w_i x_{t+1};
- reported flow ũ = u + ε.

Optional nuisances and alternatives:
- i.i.d. structural flow shocks;
- a class formed by merging two cohorts (one exponential memory fails);
- a trend-chasing term.

## Three candidate primary tests

| Candidate | Size | Power | Verdict |
|---|---|---|---|
| A. Hansen J overidentification test of the class-flow equation, per stock, lagged-price instruments | 4–7.5% (nominal 5%) | Merged-cohort alternative: 14% at 1,000 days, 24% at 2,500 days. Trend-chasing: about 5%, i.e. none | **Rejected as primary.** A pass would carry almost no information. |
| B. Targeted Wald test (u_{t-2}, x_{t-1}) pooled across 300 stocks | **Invalid.** Per-stock t-statistics have mean ≈ 0.5 under the null (weak-instrument bias), so the pooled test rejects in 100% of null panels | — | **Rejected.** Pooling amplifies finite-sample bias. |
| C. Out-of-sample forecast gain: does x_t improve next-day class-flow forecasts beyond two own lags? Pooled across stocks | Conservative: mean gain −0.001 under w = 0; null rejection < 0.1% | See below | **Chosen as primary**, with the caveats below |

### Caveat on candidate C: reverse causality

With strong price impact (κ = −1.2) **and** heavy reporting noise (noise SD equal to flow SD), x_t predicts the flow
even with w = 0: mean gain 0.014, standard error 0.0005. The reason is that prices then reveal past true flow better
than the noisy reported flow does.

At the reporting-noise levels relevant to exchange tallies (≤ 0.1–0.5 of flow SD), the null gain is ≤ 0.0006.
Taiwan's T86 flows are exchange counts of executions. Probe 1 found that every accounting identity holds exactly, so
reporting noise is small by construction. The specification adds a placebo check (Section 7 of the spec) that
detects this confound.

## Sizing (candidate C, weak-feedback scenario: structural shocks, κ = −0.6, reporting noise 0.1)

| w | Fit / evaluation days | Mean relative gain | Power, N_eff = 20 | N_eff = 50 | N_eff = 300 |
|---|---|---|---|---|---|
| 0.05 | 1000 / 1000 | 0.00045 | 0.29 | 0.44 | 0.96 |
| 0.10 | 750 / 500 | 0.0034 | 0.85 | 1.00 | 1.00 |
| 0.10 | 750 / 750 | 0.0036 | 0.98 | 1.00 | 1.00 |
| 0.10 | 1000 / 1000 | 0.0037 | 0.98 | 1.00 | 1.00 |

N_eff is a conservative stand-in for cross-sectional dependence. The empirical test uses a date-block bootstrap
instead.

**Conclusion.** About 1,000 fitting days and at least 750 evaluation days detect a mean relative forecast gain of
about 0.0035 with power ≥ 0.98, even at N_eff = 20. A gain an order of magnitude smaller (about 0.0005) is detectable
only if the stocks are close to independent. Such an outcome is designated **inconclusive**, not supportive.

## Monte Carlo precision

The size runs used 300–400 replications per cell, so the Monte Carlo standard error of a 5% rejection rate is about
0.011–0.013. That is adequate for the decisions above (rejecting candidates A and B, and sizing C). It is not a
precise size estimate.
