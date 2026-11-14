# P1F: Is trader composition irrelevant for forecasting prices? (DRAFT specification, 14 November 2026)

**Status: DRAFT. Not registered.** Written by an AI system for the authors. It becomes a registration only when the
authors approve it, the executor is written and hashed, and the specification is pushed in a commit of its own
before any data in its window exist or are read. Nothing in this file has touched market data.

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
- **Universe (fixed at registration from volume only).** The 30 USDT-margined perpetuals with the largest 24-hour
  quote volume on the registration date, excluding those listed less than 90 days before it, read from the public
  ticker. No return, flow or metrics data enter this choice.
- **Window. The authors choose one before registration:**
  - **Option P (recommended):** the 60 UTC days starting the day after the specification is pushed. Training is
    the first 30 days, test the last 30. These data do not exist at registration.
  - **Option R:** a retrospective window of 60 days that no earlier test has read. Binance metrics from July 2024
    to October 2026 are spent (P7S), as are 2023–2024 training days and the 2nd, 9th, 10th, 22nd and 24th of months
    in several tests. Option R needs an audit of the ledger by the authors first, and the paper must say it is
    retrospective.
- **Independence.** Under option P the window overlaps the P7S replication window (16 November 2026 to
  14 February 2027) on related symbols. The two tests ask different questions but are not independent.

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

## 8. Decisions needed from the authors

1. Approve or change the margin: 0.005 primary, with 0.002 as a secondary result.
2. Choose option P or option R for the window.
3. Approve the universe rule.
4. Then the executor is written, tested on synthetic files in the archive's format, and hashed. After that, this
   file is renamed without "DRAFT", the hashes are added, and it is pushed in a commit of its own.
