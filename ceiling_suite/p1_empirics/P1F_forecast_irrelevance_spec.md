# P1F: Is trader composition irrelevant for forecasting prices? (registered 14 November 2026)

**Status: REGISTERED.** Approved by the author on 14 November 2026 ("lets test and find if it workw e will add in
the paper"; "give me colab run to test on real data"). The author's request to run on real data now is read as
approving the draft's recommended choices: margin δ = 0.005 primary and 0.002 secondary, and a retrospective
window (option R), because the prospective option cannot give a result now. This specification, the executor
`p1f_executor.py`, the notebook `P1F_Forecast_Irrelevance_Colab.ipynb` and `P1F_unlocks.json` (opens = 0) are
pushed in a commit of their own before any data in the window are downloaded. Their SHA-256 hashes are in
`P1F_spec.json`. The test runs once. Written by an AI system for the authors.

**Window and data reuse, disclosed.**
- **Window.** The window is retrospective: 1 March 2022 to 29 April 2022, 60 UTC days. Training is 1–30 March;
  test is 31 March–29 April.
- **Binance futures metrics files for 2022 have not been read by any earlier test in this project.** P7S read
  July 2024 to October 2026. E8–E16 used 2023–2026. C2, C3, F1, E1 and D1 used 2025–2026.
- **Two earlier tests touched 2022 data:**
  - O1 read futures prices around scheduled macro releases in 2022–2024, a few minutes on each release date.
  - The spot feedback panel read Binance spot klines on the 10th and 24th of each month in 2021–2024.

  Both asked different questions about different files or seconds. They are disclosed here, and the window is not
  changed.
- **Readers will know 2022.** The period is public history, including the market events of that spring.

## 1. Question and theory

Theorem 1 of `ceiling_suite/papers/paper1/irrelevance/irrelevance_theorem_draft.pdf` says composition data cannot
improve a price forecast when traders' flows are functions of public prices. The exceptions are informed classes,
exogenous flows with different persistence, and position limits under stress. The test asks two things:

- **A1 (invisible):** do public prices and anonymous flow fail to reveal how class positions move?
- **A2 (irrelevant):** do class positions fail to improve price forecasts beyond public prices and anonymous flow?

Together, a pass on both is the empirical form of "composition is invisible and irrelevant".

**Design history, disclosed.** This test was designed after the following results were known:
- E15: class memory states did not improve 30-minute post-shock return forecasts. It was registered with the
  opposite hypothesis.
- E16: class data track class positions far better than prices do.
- P7S: the stress test was inconclusive.

P1F asks a different question, with different features, a different sample and a new window.

## 2. Data

- **Venue.** Binance USD-M perpetual futures, public archive `data.binance.vision`, checksum-verified.
- **Files:**
  - 5-minute klines, giving close and taker-buy base volume;
  - daily `metrics` files, giving `sum_toptrader_long_short_ratio` (top-trader positions),
    `count_toptrader_long_short_ratio` (top-trader accounts), `count_long_short_ratio` (all accounts) and
    `sum_open_interest`.
- **Bars.** 30 minutes, built from the 5-minute files: last close; summed signed taker flow, buy minus sell;
  last metrics row.
- **Universe.** The 30 USDT-margined perpetuals with the largest February 2022 quote volume (monthly 1-day klines)
  among symbols that have a metrics file and a 5-minute kline file on both 1 March and 29 April 2022. The choice
  uses volume and file listings only.
- **Window.** 1 March to 29 April 2022, as above.
- **Files.** Every zip is checked against its published `.CHECKSUM`.
- **Bars.** 30-minute bars on a complete UTC grid:
  - close: the last 5-minute close;
  - flow: the sum of signed taker quote volume, 2 × taker-buy quote − quote volume;
  - metrics: the last snapshot strictly before the bar's end and inside the bar.

  A bar with fewer than six 5-minute klines has no price or flow.

## 3. Variables

- **Target.** Next-bar log return, $r_{t+1}$.
- **Baseline features (public prices and anonymous flow):**
  - $r_t, r_{t-1}, r_{t-2}$;
  - signed taker flow $A_t, A_{t-1}, A_{t-2}$;
  - change in open interest at $t$, $t-1$, $t-2$;
  - exponential moving averages of $r$ and of $A$ at half-lives of 2, 8, 32 and 128 bars.
- **Class features.** For each class ratio $R$, use $n=(R-1)/(R+1)$. Take its 1-bar change, its 8-bar change, and
  its level minus its 48-bar moving average. Three classes times three features gives 9 features.
- **Standardization.** Every feature and the target is standardized per symbol, using the mean and standard
  deviation of the training half only.

## 4. Estimation

- **Model.** Pooled panel least squares with common coefficients and an intercept, fitted on the training half.
  There are two models: baseline, and baseline plus class features.
- **Gain.** $\Delta R^2=\sum(\text{MSE}_{\text{base}}-\text{MSE}_{\text{aug}})/\sum\text{Var}(r_{\text{test}})$,
  pooled over symbols and test bars.
- **Uncertainty.** A block bootstrap over test days, with 2,000 draws and seed 20261114, gives the one-sided 90%
  lower and upper bounds.

## 5. Hypotheses and verdicts

**A2 (primary), margin $\delta=0.005$** (half a percentage point of $R^2$; a forecast correlation of about 0.07):

| Outcome | Condition | Registered wording |
|---|---|---|
| Irrelevant | upper bound $<\delta$ | "Class positions did not improve price forecasts by $\delta$ or more beyond public prices and anonymous flow." |
| Relevant | lower bound $>0$ and $\Delta R^2\ge\delta$ | "Class positions improved price forecasts beyond public prices and anonymous flow; the irrelevance prediction is rejected." |
| Inconclusive | otherwise | "The test could not tell whether class positions improve price forecasts by $\delta$." |

**A1 (invisible), primary:**
- **Measure.** For each symbol, the out-of-sample $R^2$ of the 8-bar change in the top-trader position measure,
  forecast from the baseline features with symbol-specific least squares.
- **Pass.** $R^2<0.5$ in at least 75% of symbols.
- **Wording.** "Prices and anonymous flow did not reveal how top-trader positions moved." On a fail: "Prices and
  anonymous flow revealed how top-trader positions moved."

**Joint reading.** The supportive result is A1 pass together with A2 "irrelevant". Every other combination is
reported as it comes.

**A3 (power gate), on the training half only, before the test half is read:**
- Split the training half in two and add a synthetic feature whose true $\Delta R^2$ is $2\delta$.
- Run the same pipeline with 200 noise draws.
- If it calls "relevant" in fewer than 80% of draws, the test is declared uninformative and the test half is not
  read.

**Secondary results (reported, no verdict):**
- A2 at $\delta=0.002$.
- A2 with each class alone.
- A2 at a 5-minute horizon.
- A4, the drift prediction: the Spearman correlation across symbols between composition drift (the standard
  deviation of daily changes in the top-trader measure) and the symbol-level $\Delta R^2$, with a bootstrap
  interval. The theory predicts it is positive.

## 6. Rules

- **Coverage.** A symbol is excluded before outcomes are computed if either half has under 90% of bars with all
  files present. Bars with a missing file are dropped from both models. These rules use coverage only.
- **No changes after data are read.** No winsorizing, no outlier removal, no substitute estimators.
- **One run.** The test runs once. `P1F_unlocks.json` must read `opens = 0` before the run and is committed with
  the outputs.
- **Labelling.** Anything not listed here is labelled exploratory.

## 7. Simulation check (`research_extension/irrelevance/p1f_design_sim.py`)

Each simulated data set has 30 symbols and 60 days of 30-minute bars from the paper's model, with three classes.
The worlds are:
- **NULL:** feedback trading plus uninformed exogenous flows with different persistence, so the aggregation channel
  is present.
- **PURE:** feedback trading with one persistence.
- **INFORMED:** one class trades on next-bar value news.
- **Harsh:** Student-t(3) shocks, volatility clustering and a common market factor.

| World (δ = 0.005) | Data sets | Irrelevant | Relevant | Inconclusive | Mean ΔR² |
|---|---|---|---|---|---|
| NULL | 40 | 100% | 0% | 0% | +0.11% |
| PURE | 40 | 100% | 0% | 0% | −0.03% |
| INFORMED (ΔR² ≈ 1.5%) | 40 | 0% | 100% | 0% | +1.47% |
| NULL, harsh | 20 | 100% | 0% | 0% | +0.10% |
| INFORMED, harsh | 20 | 0% | 100% | 0% | +1.38% |
| INFORMED, weak (ΔR² ≈ 0.24%) | 20 | 100% | 0% | 0% | +0.24% |

At $\delta=0.002$:
- NULL harsh: 80% irrelevant, 20% inconclusive.
- Weak informed: 70% relevant, 30% inconclusive (harsh: 65% relevant, 5% irrelevant, 30% inconclusive).

A1 passed in every simulated data set. The A3 gate detected the injected gain in at least 99.5% of draws.

**What the simulation does not cover.**
- Real class ratios are reported positions, not flows, and may be revised or lagged.
- Real crypto returns have jumps, funding cycles and regime changes beyond the harsh case.
- The weak-informed case shows that $\delta=0.005$ calls an effect of 0.24% "irrelevant". That follows from the
  margin's definition, and the paper must state the margin plainly.

## 8. Executor and checks

- **`p1f_executor.py`** implements sections 2–6. It was tested offline on synthetic files in the archive's format
  (`research_extension/irrelevance/executor_test/`), with:
  - checksum files;
  - kline files with and without headers;
  - a missing metrics file;
  - a two-page archive listing.
- **On those files it returned:**
  - in the null world: "irrelevant", ΔR² = −0.013%;
  - in the informed world: "relevant", ΔR² = +0.75%;
  - in both worlds: A1 passed and the power gate was 1.00.
- **The universe rule picked the 30 largest eligible symbols** and excluded those missing a file.
- **Results.** The notebook writes `p1f_results.json`, `p1f_universe.json`, `p1f_coverage.json` and
  `p1f_log.txt`, and zips them for download. After the run, the result is reported here as it came out, and
  `P1F_unlocks.json` is set to opens = 1.
