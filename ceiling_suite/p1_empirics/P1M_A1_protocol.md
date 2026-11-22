# P1M-A1: the Taiwan ranges on the theory's class, and rules with feedback decoupled from flow persistence

**Status.** Protocol fixed before the run. The first author approved both analyses on 22 November 2026, 04:25 UTC
("YEAH RUN IT IF NNED I CAN RUN TEST IN COLAB TOO").

**Written.** 22 November 2026, 04:45 UTC, before any P1M-A1 number was computed, either on the Taiwan estimate or on
the Taiwan data. The code was tested only on simulated markets. Drafted by an AI system for the authors; this is not
independent review.

**Kind.** Two measurements, not hypothesis tests. No verdict and no p-value decides anything. The numbers go into the
paper's Taiwan section by the templates in section 5, whatever they show.

**Why.** Two simulated referees (`ceiling_suite/papers/paper1/review/REFEREE_REPORTS_SIMULATED_20261121.md`, Referee
A §3.6(a)–(b)) asked for these. The paper discloses both issues and has not computed either.
- **(a) Part A.** P1M's targeted range of ±0.028 fills its box by construction. Two classes can share one memory with
  large weights of opposite sign, and that leaves the aggregate kernel unchanged. Part A recomputes the range on the
  class of compositions the theory covers.
- **(b) Part B.** The tagged interval for foreign feedback, 0.0014 [0.0012, 0.0016], ties each class's feedback decay
  to the persistence of its own flow. The price-only comparisons drop that tie. Part B re-estimates the tagged rules
  with the tie removed.

**Data.**
- Part A loads no data. Its input is the P1M primary estimate in `results/p1m_results.json`, whose SHA-256 starts
  `b7ad67bb`; the runner checks this.
- Part B uses the TWSE files on the first author's Drive (`P1T_raw`). As in P1M, it uses the P1T development period
  only, 2013-01-02 to 2016-12-30, and asserts that no later date is loaded. Panel, universe, price deviation x, flow
  scaling and usable-day mask are P1M's: `p1t_executor.build_panel` and `prepare`, file checked by SHA-256 and not
  edited. Data-loading code is the P1M notebook's, unchanged.

## 1. Part A: the targeted halt and the uniform cut on the theory's class

**What stays as in P1M (section 4):**
- **The estimate θ̂.** a_j, κ, r_c, w_c, with delay 1 and five price lags.
- **The Whittle divergence rate.** Computed on 8,192 frequencies.
- **The indistinguishable set.** n·rate(θ̂, θ′) ≤ J₀ = 0.02, so by Pinsker no test exceeds its size by more than 0.10.
- **The box.** |H′_c| ≤ h̄, with H′_c = κ w′_c / (1 − r′_c).
- **Stationarity** of the alternative price process.
- **The effects.** The foreign-halt effect H′_Foreign and the uniform-cut effect U′ = Σ_c H′_c.

**What is added: the alternative compositions θ′ must lie in a class.**
- **Memories.** r′_c ∈ [0, 0.99]. P1M's search allowed [−0.99, 0.99].
- **Signs of the weights, two variants:**
  - **P (the positive class of the lower bounds):** w′_c ≥ 0 for all three classes.
  - **T (signs of the tagged estimates):** w′_Foreign ≥ 0, w′_Trust ≥ 0, w′_Dealers ≤ 0.
- **Separation of memories.** Any two classes' memories are at least γ apart, for γ ∈ {0, 0.01, 0.02, 0.05, 0.10}.
  The estimate's closest pair, Foreign and Dealers, is 0.014 apart.

**Configurations (28, all reported):**
1. **Main grid (20).** Variants P and T × γ ∈ {0, 0.01, 0.02, 0.05, 0.10} × the two P1M boxes: h̄ = 1 − Σ_j â_j
   (0.0280) and the tight box h̄ = 2·max_c |Ĥ_c| (0.00274). Record: the whole development panel, n = 270,060
   stock-days treated as independent, as in P1M.
2. **Box scan (6).** Variant T, γ ∈ {0, 0.05}, h̄ ∈ {1, 5, 10} × max_c |Ĥ_c|. With the grid's tight (2×) and primary
   (20.4×) boxes, this shows how the range scales with h̄.
3. **One stock (2).** Variants P and T, γ = 0, primary box, n = 900 (the median days per stock).

**Search** (`p1m_a1_core.constrained_ranges`):
- **Starts (46).** The estimate's six relabelings and 40 random rules, drawn as in P1M with seed 20261121. Each is
  projected onto the class: memories clipped to [0, 0.99], weights clipped to their signs, and the sorted memories
  spread to spacing γ.
- **Phase 1.** From each start, SLSQP minimizes n·rate within the class: bounds, the separation constraints in that
  start's ordering of memories, and the box. A start that reaches n·rate ≤ J₀, with a stationary price process, is
  kept.
- **Phase 2.** From each kept start, SLSQP finds the minimum and the maximum of H′_Foreign and of U′ under all the
  constraints.
- **Pooling.** Every feasible point visited, whether a kept start or a feasible phase-2 outcome of either search, is
  pooled. Both effects are extremized over the pool.
- **Guarantee.** Every pooled point belongs to the set, so the reported extremes are attained values, and the true
  range contains them.
- **Empty sets.** If no start reaches the set, the set is reported empty, with the smallest n·rate found. The true set
  may still be nonempty.
- **Exact barrier within the class.** Also reported: the halt effects of the estimate's relabelings that lie in the
  class. Their rate is exactly 0. Whether the estimate itself lies in the class is reported too.

**Runner.** `run_p1m_a1_part_a.py` computes all 28 configurations once and writes `results/p1m_a1_partA_results.json`.
It refuses to run again if that file exists.

## 2. Part B: decoupled tagged rules

**Rule of class c,** with stock fixed effects:

u_{c,t} = α_{c,s} + Σ_{j=1}^{J} β_{c,j} x_{t−j} + e_{c,t},  e_{c,t} = Σ_{l=1}^{p} φ_{c,l} e_{c,t−l} + η_{c,t}.

- The feedback kernel β_{c,j} is free. The class's non-feedback flow follows its own autoregression. The feedback
  decay is therefore no longer the flow's persistence.
- The first lag is x_{t−1} (delay 1), as in P1M.
- The errors are autoregressive, not moving-average. With price impact on the same day, x_{t−1} depends on η_{c,t−1},
  so an MA term would make the regressors endogenous. The AR(p) quasi-differenced equation is free of that problem.

**Estimation.** Iterated Cochrane–Orcutt:
- Given φ, run OLS of the quasi-differenced flow on the quasi-differenced lags of x.
- Given β, run OLS of the residual on its own p lags.
- Start from φ = 0 and iterate until max|Δφ| < 10⁻¹².
- All regressions use within-stock demeaned variables on rows where every lag is finite and usable. Stocks with fewer
  than 50 such rows are dropped, as in P1M. The fit uses per-date cross-moment matrices.

**Price equation.** P1M's: x_t = Σ_{j=1}^{5} a_j x_{t−j} + κ U_{t−1} + ε_t. Its κ must equal P1M's to 10⁻¹² on the
same panel; the notebook reports the check.

**Effects.**
- H_c = κ Σ_{j=1}^{J} β_{c,j}, the fall in the feedback budget when class c's feedback is halted.
- U = Σ_c H_c.

**Uncertainty.** P1M's stationary bootstrap over dates: mean block 20, B = 999, seed 20261121, the same resampled dates
for every equation, and 95% percentile intervals. Within each draw, Cochrane–Orcutt restarts from the full-sample φ.

**Runs (all reported):**
- primary: J = 10, p = 2;
- J = 5, p = 2;
- J = 20, p = 2;
- J = 10, p = 1.

The dealer series is the dealer total, as in P1M's primary run.

**Notebook.** `P1M_A1_Decoupled_Colab.ipynb`, built by `make_p1m_a1_notebook.py`, has one code cell. Run it once. It
saves `p1m_a1_partB_results.json` and a zip to Drive. A rerun loads the saved result and does not recompute.

## 3. Checks before the run (simulated markets only)

- **`test_p1m_a1_core.py`, all checks pass:**
  - Decoupled rules recover free kernels and AR(2) non-feedback flow in a market where flows move prices on the same
    day and the next. Kernel sums are within three bootstrap standard errors, and each lag is within 0.03.
  - On the paper's restricted model, they recover the geometric kernel's sum and φ₁ = r.
  - The constrained ranges satisfy every constraint and stay inside [0, U′] for the positive class. Under the tagged
    signs the foreign effect is nonnegative. The in-class relabelings are right.
- **`test_p1m_a1_notebook.py`, all checks pass.** The notebook's analysis runs end to end on simulated TWSE files
  covering both schema eras, saves its results, and loads them on a rerun. Its κ equals P1M's, and the cell compiles.

## 4. Rules

- **Each part is computed once.**
- **A failure before any number exists** (loading, parsing, a crash) is a bug. It is fixed, the fix is noted in
  section 6, and the run is repeated.
- **Once numbers exist, they are the result.** A later error is reported next to the original numbers.
- **Code and this file are frozen at the hashes in `P1M_A1_SHA256SUMS`,** committed before the run.
- **What this is not.** The estimated w_c and β_{c,j} are tagged responses, not established causal feedback. The P1T
  holdout's pre-specified diagnostic could not separate them from prices revealing past flow. Part B does not change
  that.

## 5. Text for the paper (placeholders filled from the result files)

Numbers are rounded to two significant digits, as in P1M.

### Part A

**Placement.** The first Taiwan qualification ends: "Weights restricted to one sign would exclude these compositions;
we have not computed the range under that restriction." That sentence is replaced by:

> On the class the lower bounds cover, with every weight nonnegative and memories in [0, 0.99], the compositions the
> panel cannot tell apart imply contributions from {P0min} to {P0max}, against a uniform cut between {P0Umin} and
> {P0Umax}; with memories at least 0.05 apart, the range is {P5min} to {P5max}. Holding each class's weight to the sign
> of its tagged estimate gives {T0min} to {T0max}, and {T5min} to {T5max} at spacing 0.05.

Each value comes from the primary box and the whole-panel record.

**Conditional clauses,** each added after that passage when its condition holds:
- **P0 span.** If the variant-P range at γ = 0 covers at least 90% of [0, its uniform-cut maximum P0Umax]: "So even on
  that class, prices leave foreign feedback anywhere between none and nearly all of the total."
- **Box at γ = 0.** If the variant-T maximum at γ = 0 is at least 0.99·h̄: "Where weights of opposite sign may sit at
  equal memories, the cap again sets the range."
- **Narrowing.** If the variant-P range at γ = 0.05 is narrower than at γ = 0 by more than half: "Requiring the
  classes' memories to be apart narrows it, as the composition barrier predicts."

**Empty sets.** If a cell is empty, the passage says "no composition in that class lies within the panel's reach"
in place of its range.

**Supplement.** The table of all 28 configurations goes in the Taiwan section (`app:barrier`). It reports H′_Foreign
and U′ ranges, feasible starts, and the in-class relabeling values.

### Part B

**Placement.** The second Taiwan qualification reads: "the tagged intervals assume that each class's feedback decays
at the persistence of its own flow, while the price-only comparisons let feedback memory vary with non-feedback flow
held fixed." The following is added after it:

> With feedback decoupled from each class's flow persistence (a free ten-day distributed lag of x, with second-order
> autoregressive non-feedback flow), foreign feedback contributes {Hd} (95% interval [{lo}, {hi}]).

It is followed by one of two clauses:
- if Ĥ_Foreign of Table 3 (0.00137) lies in [{lo}, {hi}]: "which contains the estimate of Table 3."
- otherwise: "which does not contain the estimate of Table 3; that estimate rests on tying feedback to flow
  persistence."

**Supplement.** A table with the four runs: H_Foreign, H_Trust, H_Dealers and U with intervals, φ, and the κ check.

## 6. Post-result notes

(Added after each run; nothing above this section changes.)
