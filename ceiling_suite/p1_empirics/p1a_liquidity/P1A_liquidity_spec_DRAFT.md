# P1A (DRAFT, not registered): does AMM liquidity depend on arbitrageurs only through their aggregate response?

A liquidity-side bridge test of Theorem 4.1(iii) of Paper 1.

**Status.** Draft and power simulation of 22 November 2026. No data has been read and nothing is registered. Before
registration:
1. Explore the development window.
2. Rerun the simulation at what that exploration measures.
3. Pass the power check in section 7.
4. Obtain the authors' approval.

Drafted by an AI system for the authors; this is not independent review.

## 1. What the theory says, and the bridge to an AMM

**The theorem.** Theorem 4.1(iii) concerns an inventory economy in which competitive dealers supply liquidity. In
equilibrium, price impact, persistence and the price process depend on the trader population only through G, the
Stieltjes transform of the merged measure. That is the aggregate feedback response. How that response is split among
traders does not matter.

**The bridge.** Three assumptions carry the theorem to a Uniswap v3 pool:
- **B1, LPs as dealers.** Passive liquidity providers (LPs) play the dealers' role. A pool's depth at its current
  price is the inverse of its price impact. LPs choose depth by weighing expected fees against expected losses to
  arbitrage ("loss-versus-rebalancing").
- **B2, arbitrageurs as feedback traders.** Arbitrageurs are the feedback traders. Their flow responds to the basis
  x = log(pool price) − log(Binance price).
- **B3, LPs see only the aggregate.** The arbitrage population affects LPs only through the aggregate response of
  arbitrage flow to the basis. LPs lose to price moves, whoever makes them.

**Prediction.** Given B1–B3, a pool's depth depends on its arbitrage population only through the aggregate response.
Composition adds nothing once that response is held fixed. Composition here means the concentration of arbitrage
volume across addresses, the number of active bots, or the replacement of a dominant bot.

**Why it is a bridge, not a direct test.**
- LPs are not the theorem's dealers: they hold no inventory with risk aversion A.
- Some arbitrage bots also supply liquidity just in time (JIT), within a single block.
- Block builders take part of arbitrage profits.

A failure could therefore reflect the bridge rather than the theorem, and the paper would say so. A success supports
the theorem's liquidity-side content in a market it was not built for.

## 2. Data (public)

**Sources.**
- **Uniswap v3 events** on Ethereum mainnet, from the BigQuery public blockchain datasets:
  - Swap: sender, recipient, amounts, sqrtPriceX96, liquidity, tick;
  - Mint and Burn;
  - each swap's transaction sender (`from_address`, the bot's address).

  Arbitrum and Base can be added if their datasets cover the windows. Section 5 suggests they will be needed.
- **Binance spot one-second klines** from the public archive (data.binance.vision). Their coverage of the windows is
  checked in the exploration.

**Pools.** Every Uniswap v3 pool whose two tokens map to a Binance USDT or USDC pair and that meets the activity floors
in the development window:
- the candidates are the 55 tokens in `p1a_dev.py` (`TOKENS`), each against WETH, USDC, USDT and WBTC, at all four fee
  tiers: 840 pools in 210 pairs. Their addresses are computed by CREATE2, and the code checks the method against five
  known pools;
- at least 100 swaps in every week;
- each Binance leg trades in at least 90% of seconds;
- pool volume above a floor, set in the exploration; counts are reported at $1M, $5M and $20M of median weekly volume;
- a data check: the median basis lies within ±50 bps, which catches a wrong token or decimals mapping.

Tokens that migrated or merged during 2024–2026 (MATIC, RNDR, OCEAN, AGIX) are left out, so that the list can be used
on the test window. The list is fixed from the development window before the test window is read.

**Independence.** Pools of one token pair, at different fee tiers or on different chains, share their arbitrageurs and
their Binance price, so they are not independent. Standard errors are therefore clustered by pair, and the
simulation's "pools" should be read as pairs. The simulation says the test needs about 40 of them observed for two
years (section 5). Mainnet alone may not have that many pairs with active arbitrage.

**Windows.**
- **Development window:** 2024-01-01 to 2024-06-30 (26 weeks). It may be explored freely, to calibrate and to fix the
  pool list.
- **Test window:** 2024-07-01 to 2026-06-28 (104 weeks). It is read only after registration, and only by the
  registered code, once. The simulation shows that one year would have almost no power.

**Cost.** BigQuery scans may exceed the free monthly allowance. They are estimated (dry run) before any query runs,
and run in the first author's Colab with his Google account.

## 3. Measurements (pool-week)

- **Basis.** For each block b, x_b = log(pool price after the block's last swap) − log(Binance close of the second
  before the block's timestamp), in basis points.
- **Aggregate response R (the control).**
  - Each week, regress net pool flow over the next three blocks on the basis x_b. Flow is buyer-initiated minus
    seller-initiated swap volume in units of the pool's in-range liquidity, 2·Δy/(L·√P), which is the move in log price
    the flow would cause. R is minus the slope, so a larger R means arbitrage closes the basis faster. The basis is
    winsorized at the 1st and 99th percentiles within each pool-week-half.
  - It is computed separately on odd and even UTC hours, giving R1 and R2, the two halves used against errors in
    variables. A basis observation whose three-block window reaches into the next hour is dropped, so the halves share
    no flows. (The first draft split odd and even blocks. Neighbouring blocks' windows overlap, so those halves would
    have shared flows and correlated errors.)
  - The three individual lags are also reported.
- **Composition C (primary).** The Herfindahl index, across sending addresses, of the week's arbitrage volume.
  Arbitrage volume is swaps that move the pool price toward the Binance price. Secondary measures:
  - the top address's share;
  - the number of addresses with at least 1% of the volume;
  - whether the top address changed from the previous week.
- **Depth D.** The log of the time-weighted mean USD depth within ±1% of the pool price.
  - In-range liquidity L is replayed event by event: each swap reports it, and mints and burns whose range contains
    the current tick move it. Depth is L·√P·(√1.01 − 1/√1.01) in token1, valued in USD. This treats L as constant
    across the ±1% band; the full tick profile would need every position since 2021.
  - The state is taken after each block's last event, so liquidity minted and burned within the same block (JIT) is
    excluded in the primary measure. A secondary measure, taken at each swap, includes it; the calibration does not
    need it.
- **Controls.**
  - log Binance realized volatility (one-second returns) and log Binance volume;
  - median gas base fee;
  - pool and week fixed effects.

## 4. Estimator and decision rule

**Estimator.** Two-way fixed-effects 2SLS, with standard errors clustered by token pair.
- **Model.** D = pool FE + week FE + β·R1 + γ·C + controls + error.
- **Instrument for the response.** R1 is instrumented by R2. The two halves measure the same response with independent
  errors.
- **Instrument for composition.** C is instrumented by a leave-one-out shift-share of bots' activity elsewhere:
  - Z_{p,w} = Σ_b s_{b,p} · A_{b,−p,w};
  - s_{b,p} is bot b's share of pool p's arbitrage volume in the development window;
  - A_{b,−p,w} is bot b's standardized log arbitrage volume in all other pools in week w.

  The idea: when a bot scales up or exits across the market, the composition of pools it serves changes for reasons
  that have nothing to do with those pools' depth.
- **Comparison.** OLS is reported beside the IV estimate but decides nothing.

**Decision rule** (δ = 0.05, that is, 5% of depth per standard deviation of C). Critical values come from the t
distribution with P − 1 degrees of freedom, where P is the number of clusters (section 5, Table D).
- **Validity.** The cluster-robust first-stage F for C must be at least 10. Otherwise the test is reported as **not
  informative**, and there is no switch to OLS. This guards against bias only. Precision is checked before
  registration (section 7).
- **Positive control.** The response must predict depth (|β̂| > t_{0.975, P−1} se, two-sided). The bridge does not
  fix the sign. The theory's negative feedback lowers impact, while faster arbitrage raises losses to arbitrage.
- **Supportive.** The positive control holds and the 90% interval for γ, γ̂ ± t_{0.95, P−1} se, lies inside [−δ, δ].
  This is an equivalence test (TOST) at 5%.
- **Contrary.** The 90% interval for γ lies entirely beyond δ in either direction.
- **Inconclusive.** Anything else.

The secondary composition measures are reported, Holm-adjusted, and decide nothing.

## 5. The power simulation (no data)

Code: `power_sim.py` (main grid, 400 draws per cell) and `power_checks.py` (critical values and the margin, 2,000
draws per cell). Results: `power_sim_results.json`, `power_checks_results.json`.

The simulation draws pool-week panels in which the truth is known, and runs both estimators under the decision rule.
It varies:
- **panel size:** 20 pools × 52 weeks, 30 × 104, or 40 × 104;
- **the response estimate's reliability:** 0.6, 0.8 or 0.95;
- **ψ, how strongly composition moves with the true response:** 0 or 0.5;
- **λ, same-week feedback from depth to composition:** 0 or 0.3;
- **the instrument's strength:** 0.15, 0.3 or 0.6 SD;
- **the truth:** γ = 0, δ or 2δ.

**Assumed values,** which the development window replaces:
- the response's effect β = 0.30 log points of depth per SD;
- depth residuals with SD 0.30, serially correlated within pools (AR 0.5);
- 15 bots, with exposures to pools that differ widely (Dirichlet 0.5).

The precision of γ̂ scales with the residual SD of depth, so power depends heavily on that number.

### Table A. The threats: how often each estimator wrongly rejects a true theory

P(contrary | gamma = 0), 30 pools x 104 weeks, instrument strength 0.3; normal critical values, 400 draws per cell.

| Response reliability | Composition tied to response (psi) | Depth feeds composition (lambda) | OLS | IV |
|---|---|---|---|---|
| 0.6 | 0.0 | 0.0 | 0% | 0% |
| 0.6 | 0.0 | 0.3 | 0% | 0% |
| 0.6 | 0.5 | 0.0 | 72% | 1% |
| 0.6 | 0.5 | 0.3 | 100% | 1% |
| 0.8 | 0.0 | 0.0 | 0% | 0% |
| 0.8 | 0.0 | 0.3 | 0% | 1% |
| 0.8 | 0.5 | 0.0 | 0% | 0% |
| 0.8 | 0.5 | 0.3 | 98% | 0% |
| 0.95 | 0.0 | 0.0 | 0% | 1% |
| 0.95 | 0.0 | 0.3 | 0% | 0% |
| 0.95 | 0.5 | 0.0 | 0% | 0% |
| 0.95 | 0.5 | 0.3 | 2% | 0% |

### Table B. IV: power to support a true theory, and the size of the support claim

Worst realistic case: psi = 0.5, lambda = 0.3. Cells: P(supportive | gamma = 0) / P(supportive | gamma = delta) / P(contrary | gamma = 2 delta). Normal critical values, 400 draws per cell (Monte Carlo standard error at most 2.5 points).

| Pools x weeks | Reliability | Instrument 0.15 | Instrument 0.3 | Instrument 0.6 |
|---|---|---|---|---|
| 20 x 52 | 0.6 | 0% / 0% / 15% | 0% / 0% / 22% | 2% / 0% / 40% |
| 20 x 52 | 0.8 | 0% / 0% / 16% | 0% / 0% / 22% | 7% / 1% / 51% |
| 20 x 52 | 0.95 | 0% / 0% / 17% | 0% / 0% / 25% | 12% / 2% / 54% |
| 30 x 104 | 0.6 | 0% / 0% / 19% | 0% / 0% / 37% | 46% / 4% / 74% |
| 30 x 104 | 0.8 | 0% / 0% / 16% | 1% / 0% / 42% | 64% / 7% / 84% |
| 30 x 104 | 0.95 | 0% / 0% / 18% | 2% / 0% / 43% | 73% / 7% / 83% |
| 40 x 104 | 0.6 | 0% / 0% / 18% | 1% / 0% / 42% | 67% / 4% / 86% |
| 40 x 104 | 0.8 | 0% / 0% / 21% | 3% / 0% / 43% | 83% / 8% / 92% |
| 40 x 104 | 0.95 | 0% / 0% / 26% | 9% / 1% / 52% | 90% / 7% / 96% |

### Table C. IV first-stage strength (median cluster-robust F for composition)

| Pools x weeks | Instrument 0.15 | Instrument 0.3 | Instrument 0.6 |
|---|---|---|---|
| 20 x 52 | 15 | 66 | 384 |
| 30 x 104 | 47 | 199 | 1154 |
| 40 x 104 | 59 | 267 | 1509 |

Across all 108 designs: the IV support claim's size at the boundary is at most 8%; IV's false-contrary rate at most 5%; OLS's at most 100%.

### Table D. Size of the support claim at its boundary: normal against t critical values

P(supportive | gamma = delta = 0.05), instrument strength 0.6, 2,000 draws per cell (Monte Carlo standard error 0.5 points at 5%). Cells: normal / t(P - 1).

| Pools x weeks | Reliability | psi 0, lambda 0 | psi 0, lambda 0.3 | psi 0.5, lambda 0 | psi 0.5, lambda 0.3 |
|---|---|---|---|---|---|
| 30 x 104 | 0.6 | 6.2% / 5.8% | 5.9% / 5.2% | 5.5% / 4.9% | 4.9% / 4.5% |
| 30 x 104 | 0.8 | 6.2% / 5.7% | 5.3% / 4.8% | 5.3% / 4.8% | 5.8% / 5.1% |
| 30 x 104 | 0.95 | 5.7% / 4.7% | 6.5% / 5.7% | 5.1% / 4.3% | 6.3% / 5.7% |
| 40 x 104 | 0.6 | 5.6% / 5.3% | 5.7% / 5.3% | 4.5% / 4.2% | 4.7% / 4.3% |
| 40 x 104 | 0.8 | 5.7% / 5.1% | 6.1% / 5.6% | 5.5% / 5.0% | 5.2% / 5.0% |
| 40 x 104 | 0.95 | 6.0% / 5.7% | 5.5% / 5.2% | 6.2% / 5.8% | 5.2% / 4.9% |

Average over the 24 cells: normal 5.6%, t 5.1%. Largest cell: normal 6.5%, t 5.8%.

### Table E. What the t correction costs (psi = 0.5, lambda = 0.3)

Cells: normal / t(P - 1). Power to support a true theory, P(supportive | gamma = 0), and to reject a false one, P(contrary | gamma = 2 delta = 0.10).

| Pools x weeks | Reliability | Support, instrument 0.3 | Support, instrument 0.6 | Reject, instrument 0.3 | Reject, instrument 0.6 |
|---|---|---|---|---|---|
| 30 x 104 | 0.6 | 0.1% / 0.1% | 46.0% / 42.1% | 35.1% / 33.2% | 75.1% / 73.0% |
| 30 x 104 | 0.8 | 1.1% / 0.5% | 66.2% / 63.2% | 40.4% / 38.4% | 81.6% / 79.8% |
| 30 x 104 | 0.95 | 3.1% / 2.1% | 74.1% / 71.2% | 45.5% / 43.0% | 87.2% / 86.2% |
| 40 x 104 | 0.6 | 0.9% / 0.7% | 66.7% / 64.6% | 38.3% / 36.6% | 81.7% / 80.8% |
| 40 x 104 | 0.8 | 4.1% / 3.2% | 80.7% / 79.7% | 47.5% / 46.0% | 91.6% / 90.9% |
| 40 x 104 | 0.95 | 7.6% / 6.2% | 87.8% / 87.0% | 51.7% / 50.2% | 93.7% / 93.1% |

### Table F. A wider margin: delta = 0.10 (t critical values; reliability 0.8; psi = 0.5, lambda = 0.3)

Cells: P(supportive | gamma = 0) / P(supportive | gamma = 0.10) / P(contrary | gamma = 0.20).

| Pools x weeks | Instrument 0.15 | Instrument 0.3 | Instrument 0.6 |
|---|---|---|---|
| 20 x 52 | 0.1% / 0.0% / 23.4% | 4.9% / 0.9% / 47.3% | 73.6% / 4.8% / 89.5% |
| 30 x 104 | 1.4% / 0.1% / 41.5% | 59.8% / 4.2% / 82.0% | 99.8% / 5.1% / 100.0% |
| 40 x 104 | 3.3% / 0.3% / 46.5% | 80.0% / 4.7% / 90.9% | 100.0% / 4.2% / 100.0% |

**What the simulation says**

1. **OLS cannot decide this test.**
   - When the response is measured with noise and composition moves with the true response, or depth feeds back on
     composition within the week, OLS finds a composition effect that is not there. At 30 pools × 104 weeks this
     happens in up to 100% of draws (Table A).
   - IV's false-contrary rate is at most 5% in all 108 designs.
   - OLS is two to three times as precise as IV with the strong instrument, and far more with weaker ones, which
     makes it tempting. Under these threats it is precisely wrong.
2. **Supporting the theory needs a strong instrument and a large panel.** In the worst realistic case (ψ = 0.5,
   λ = 0.3), IV supports a true theory:
   - in about 80–87% of draws at 40 pools × 104 weeks, with an instrument of strength 0.6 and reliability of at least
     0.8 (Table E, t critical values);
   - in 42–71% at 30 × 104 with that instrument (Table E);
   - in at most 12% at 20 × 52 (Table B).

   With an instrument of strength 0.3, power is at most 9% (Table B), although its median first-stage F is about
   200–270 (Table C). The F ≥ 10 rule guards against bias, not imprecision. What binds is the standard error of γ̂:
   80% power needs se(γ̂) below about 0.017, so that a 90% interval fits inside ±0.05.
3. **A false theory is usually caught when the design is strong.** With γ = 2δ = 0.10, IV says contrary:
   - in 73–93% of draws with the strong instrument at 30–40 pools (Table E);
   - in 15–54% in the other designs (Table B).
4. **Normal critical values are slightly too liberal; t critical values fix this.**
   - With normal critical values, the support claim's size at its boundary averages 5.6% in the strong designs, and
     reaches 6.5% in one cell (Table D).
   - With t critical values on P − 1 degrees of freedom, it averages 5.1%, and no cell is more than 1.6 Monte Carlo
     standard errors above 5%.
   - The correction costs up to 4 points of power (Table E). The draft rule therefore uses t critical values.
5. **The margin matters as much as the panel.**
   - With δ = 0.10, that is 10% of depth per SD of composition, the test supports a true theory in 60% of draws at
     30 × 104 and in 80% at 40 × 104, even with an instrument of strength 0.3. With the strong instrument it does so
     in nearly all draws (Table F).
   - The size stays at or below 5.1%.
   - The price is a weaker claim: composition moves depth by less than 10% per SD, rather than 5%.
6. **What this means for the design.**
   - The test window must be two years. At δ = 0.05, with one year and 20 pairs, the test has almost no power.
   - It needs about 40 independent pairs, so Arbitrum and Base pools are likely needed.
   - In the development window, after pool and week effects:
     - the correlation of composition with the instrument must be about 0.5, the strongest case simulated. At about
       0.23, power is at most 9%;
     - the correlation of the two response halves must be at least about 0.6.
   - If these conditions fail, the test would almost surely come out inconclusive at δ = 0.05, and it is not worth
     registering at that margin.
   - All of this rests on the assumed values above. The residual SD of log depth, in particular, is unknown until the
     exploration.

## 6. Threats and how the design meets them

| Threat | Effect if ignored | Design |
|---|---|---|
| The response is estimated with noise, and composition is correlated with the true response | OLS loads the missing response onto C and wrongly rejects a true theory (Table A) | Split-sample IV for R |
| Depth attracts or repels bots in the same week (simultaneity) | Bias in γ | Shift-share IV for C |
| G is a function, but R summarizes it | Composition may stand in for omitted features of G | Three lags of the response as controls (secondary); the reading in section 1 |
| Few independent pairs; serially correlated weeks | Over-confident intervals | Clustering by pair; t(P − 1) critical values; the simulation checks the size |
| The response's two effects on depth cancel (fees against losses to arbitrage) | The positive control fails | The test is then reported as not informative, by design |
| JIT liquidity by the same bots | Composition affects depth through JIT, outside the theorem | Depth without JIT (primary) and with it (secondary) |
| Builders and private order flow | Arbitrage profits split with builders | Discussed as part of the bridge; not tested |

## 7. Steps, and who does what

1. **Development extraction.** `P1A_Dev_Window_Colab.ipynb` (built by `make_p1a_dev_notebook.py` from `p1a_dev.py`,
   tested on synthetic data by `test_p1a_dev.py`):
   - it runs dry-run cost estimates first and stops unless the total is below 950 GB, within the BigQuery sandbox's
     free 1 TB a month; each query is capped at its estimate;
   - the first author runs it once in Colab. The code refuses any date after 2024-06-30;
   - it computes no estimate of composition's effect on depth.
2. **Exploration of the development window only.** The same notebook measures four things:
   - the correlation of R1 and R2 after removing pool and week effects. The simulation's reliabilities 0.6, 0.8 and
     0.95 correspond to correlations of about 0.37, 0.61 and 0.88;
   - the correlation of C and the instrument Z after removing pool and week effects. The instrument strengths 0.15,
     0.3 and 0.6 correspond to correlations of about 0.12, 0.23 and 0.49;
   - the residual SD and serial correlation of log depth, and the response's effect β;
   - the number of independent pairs that pass the activity floors.
3. **Calibrated power check.** Rerun the simulation at the measured values. Register only if, there,
   P(supportive | γ = 0) is at least 0.80, the support claim's size is at most 0.05 and the false-contrary rate is at
   most 0.05.

   If the check fails at δ = 0.05, the test is not worth registering: it would almost surely come out inconclusive.
   The authors would then drop it or choose a wider margin. δ is an economic choice, the composition effect the
   authors would call negligible. A wider δ makes the test feasible and the support claim weaker (Table F). It must be
   chosen before the test window is read.
4. **Authors' approval, then registration.** The specification and code are pushed with hashes before the test window
   is read.
5. **One run on the test window.** The result is reported as it comes out, in the paper beside the Taiwan
   calibration, whatever it shows.
