# P1K3: do investor categories have a common memory across stocks? (KRX design 3)

Written 13 November 2026 by an AI system for the authors, at the author's request in chat ("lets do krx design and
colab if needed and if pass lets go"). The decision rules and the simulation acceptance criteria below were fixed
and committed **before the simulation check was run** and before any KRX data were read. This is not independent
review.

Status: **failed its simulation check on 13 November 2026 (section 8); not registered; must not be run on KRX data.**
Originally: draft until the simulation check passes. If it passes the criteria in section 7, the author's message
above is the approval to register: the spec, executor and notebook are then hashed and committed, and the data run
happens once. If it fails, nothing is registered and the failure is recorded here.

## 1. Question

Paper 1's pooling theorem (`thm:pool`) assumes that a trader class has the same memory in every market it trades,
with weights that may differ by market. Korea's exchange publishes, for every stock and day, net purchases by eleven
investor categories. P1K3 asks whether each category's memory is common across KOSPI 200 stocks.

Unlike P1X (cross-market, untagged) and P1K designs 1 and 2 (sufficiency through the kernel), each category's flow is
observed separately in each stock, so the memory is estimated from the category's own flow and there is no mixture
problem. Designs 1 and 2 failed their simulation checks for the sufficiency test; design 2 showed that pooled
memories are recovered well (error at most 0.024), which is what this design builds on.

## 2. Data

- Source: KRX Data Marketplace through `pykrx==1.2.9`, with the author's free KRX account (Colab Secrets
  `KRX_ID`, `KRX_PW`). Adjusted daily close (pykrx's adjusted series), market capitalization, and daily net purchase
  value (`순매수`, `거래대금`) by detailed investor category.
- Categories (pykrx column, English): 금융투자 financial investment, 보험 insurance, 투신 investment trusts, 사모 private
  equity, 은행 banks, 기타금융 other financial, 연기금 pension funds, 기타법인 other corporations, 개인 individuals,
  외국인 foreigners, 기타외국인 other foreigners. If the downloaded columns are not exactly these plus `전체`, the
  notebook stops before computing anything.
- Universe: stocks in the KOSPI 200 on the first trading day of each year 2015 to 2025; a stock-year is included if
  the stock is a constituent on that day. (pykrx gives constituents only from 2 May 2014, so the sample starts in 2015.)
- Flows: 2015-01-02 to 2025-12-30. Prices and capitalization from 2014-09-01, used only to start the 60-day mean.
- The burned day 2012-01-02 is outside this sample.

## 3. Variables

- `x_{s,t}`: log adjusted close minus its trailing 60-trading-day mean, divided by the stock's standard deviation of
  daily log returns over 2015-2025.
- `u_{c,s,t}`: net purchase value of category `c` divided by market capitalization at `t-1`, winsorized within each
  stock-year at its 0.5% and 99.5% quantiles.

## 4. Estimation

For a memory `r` on the grid `0.00, 0.01, ..., 0.99`, let `m_{t-1}(r) = sum_{j>=1} r^(j-1) x_{t-j}` (started at zero,
first 20 usable days of each stock-year dropped; a day is usable if `x` and all eleven flows are finite; a stock-year
enters if at least 150 usable days remain). In each stock-year, regress `u_t` on `(1, x_t, m_{t-1}(r))` by OLS (Paper 1's
tagged-flow model `u_t = r u_{t-1} + w x_t`; same-day reverse causality biases only the `x_t` coefficient). Let
`SSE_{s,y}(r)` be the residual sum of squares divided by the stock-year's total sum of squares of `u`.

- Pooled memory: `r_c = argmin_r sum_{s,y} SSE_{s,y}(r)`.
- Per-stock, per-half memory: `r_{s,c,h} = argmin_r sum_{y in h} SSE_{s,y}(r)`, with halves odd years
  (2015, 2017, ..., 2025) and even years (2016, ..., 2024). A stock enters if it has at least 2 included stock-years in
  each half. `l_{s,c,h} = log(1 - r_{s,c,h})`.

## 5. Decision rules

**Identification of a category (all stock-years).** Category `c` is identified if (a) `0 < r_c < 0.99`, and (b) the
signs of `b_s = sum_y n_{s,y} beta_{s,y}`, where `beta_{s,y}` is the coefficient on `m_{t-1}(r_c)`, agree for at
least 65% of stocks and a two-sided binomial test of equal signs gives `p < 0.001`. `I` is the set of identified
categories.

**Between-stock spread.** For `c` in `I`: `tau2_c` = sample covariance across stocks of `l_{s,c,odd}` and
`l_{s,c,even}` (estimation noise is independent across halves, so this estimates the between-stock variance of the
log memory speed); `tau_c = sqrt(max(tau2_c, 0))`. Bootstrap over stocks, 999 draws, seed 20261113: `U_c` and `L_c`
are the 95th and 5th percentiles of the bootstrap `tau_c`.

Margin `delta = 0.25`: a category is **common** if `U_c < delta` (its memory speed varies across stocks by less than
about 25%), **heterogeneous** if `L_c > delta`.

**Verdict (primary).**
- not testable, if `|I| < 4`;
- **supportive**, if at least `ceil(2|I|/3)` categories in `I` are common;
- **inconsistent**, if more than `|I|/2` categories in `I` are heterogeneous;
- **inconclusive**, otherwise.

**Secondary, descriptive.** (S1) pooled log memory speed per category with a 95% stock-bootstrap interval, and the
pairs of identified categories whose intervals are disjoint (do the tags carry different memories?); (S2) the
table of `tau_c`, `L_c`, `U_c`, `|I|` and stock counts.

## 6. What a result would mean

Supportive: evidence, on real tagged flows at daily frequency, that investor categories trade every stock with the
same memory, the premise of the pooling theorem at the category level. Inconsistent: categories' effective memories
differ across stocks. This does not refute the algorithm-level premise, because a category mixes many traders and
its mix can differ by stock. Either way it is not a test of intraday algorithmic feedback.

Reporting: Supplement S7 gets a paragraph and the main-text Evidence paragraph counts three registered tests,
whatever the verdict, stated as registered.

## 7. Simulation check (criteria fixed before running)

Simulated panels of 250 stocks and 11 categories over the same calendar, with category memories common up to a
stock-level spread `tau_true` in log memory speed, yearly changes in category activity, a market-wide component in
prices, flow noise that also moves the same day's price, and stock entry and exit. Cases and acceptance criteria:

| Case | Truth | Required |
|---|---|---|
| common | `tau_true = 0` | supportive in at least 80% of runs |
| boundary | `tau_true = delta = 0.25` | supportive in at most 10% of runs |
| heterogeneous | `tau_true = 0.5` | supportive in at most 5% of runs |
| null | no feedback | no supportive and no inconsistent verdict |
| mixture | each category two sub-groups, memories `e^(+-0.7)` apart, stock-specific shares | reported only |
| weak | common, feedback weights halved | reported only |

The design passes only if all four required rows hold. The results are recorded in section 8 whatever they are.

## 8. Simulation check results

### Design iterations before the official runs (smoke tests on seeds outside the official set)

1. First simulator: the feedback component explained about 99% of each category's flow, far more than real daily
   flows. Changed: other trading is added so that feedback explains a share `R2_c` of each category's flow,
   log-uniform on [1%, 20%] across categories, and other trading also moves prices.
2. With that noise and the regressor `x_t`, the no-feedback case identified 4 of 11 categories: flows that move the
   same day's price make the coefficient on `m_{t-1}(r)` take the same sign in every stock. Changed: the regressor is
   `k_t` (past prices only), as in section 4. The no-feedback case then identified none.
3. With both changes, one smoke run of the common case found 3 of 11 categories common (7 needed), and the
   heterogeneous case had categories whose per-stock estimates sit at one grid value, giving a spread of zero.
   Nothing else was changed; the official runs below use the rules as written.

### Official runs (13 November 2026; 250 stocks, 499 bootstrap draws; `validate_p1k3_results.json`)

| Case | Runs | Verdicts | Categories common (of identified), per run | Required | Met? |
|---|---|---|---|---|---|
| common (`tau_true = 0`) | 20 | 20 inconclusive | median 3 of 11 (range 1 to 7) | supportive in >= 80% | **No (0%)** |
| boundary (`tau_true = 0.25`) | 20 | 20 inconclusive | median 1 of 11 | supportive in <= 10% | Yes (0%) |
| heterogeneous (`tau_true = 0.5`) | 20 | 20 inconclusive | median 1 of 11 | supportive in <= 5% | Yes (0%) |
| null (no feedback) | 20 | 20 not testable | 0 identified | no supportive or inconsistent | Yes |
| mixture | 10 | 10 inconclusive | median 0 of 11 | reported only | |
| weak | 10 | 10 inconclusive | median 1 of 9 | reported only | |

**Verdict: the design fails.** It never wrongly returns "supportive" and the identification step is no longer fooled
when there is no feedback, but it has no power: with daily flows in which feedback explains 1-20% of each category's
flow, one stock's memory is estimated too imprecisely (median upper bound 0.41 against a margin of 0.25), so it
cannot show commonality even when memories are exactly common. The spread estimate is also biased toward zero
(median 0.23 when the truth is 0.48), from estimates piling up at grid values. The design is not registered and must
not be run on KRX data. The power depends on the assumed share of flow explained by feedback, which was fixed before
the official runs and cannot be checked without reading data.
