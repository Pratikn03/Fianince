# P1M: the identification barrier measured in a real market (protocol, fixed before the run)

- **Written:** 21 November 2026 (UTC), before any P1M number was computed. Code: `p1m_core.py`; notebook builder
  `make_p1m_notebook.py`; simulation checks `test_p1m_core.py` (all pass) and `test_p1m_notebook.py`.
- **Kind:** a measurement, not a hypothesis test. No verdict, no p-value decides anything. The numbers go into the main
  text of Paper 1 as the paragraph "The barrier in a real market", whatever they show (template in section 7).
- **Data:** the TWSE files already stored on Drive (`P1T_raw`: T86, MI, TWT49U, FMTQIK) for the P1T **development
  period, 2013-01-02 to 2016-12-30**. The P1T spec designates that period for free exploration. The notebook asserts
  that no date after 2016-12-30 is loaded, so the P1T validation and holdout periods are not touched.

## 1. Panel (unchanged from P1T)

`p1t_executor.build_panel` and `p1t_executor.prepare` with the development mask covering every loaded day. The executor
file is checked by SHA-256 and is not edited. This gives: the universe (top 300 four-digit stocks by development
turnover, P1T exclusions), the market-reference basis x (log price adjusted for events, minus β̂ times log TAIEX,
minus its trailing 60-day mean), class flows scaled by each stock's development average daily volume, and the
usable-day mask.

Classes: **Foreign** (including foreign dealers), **Trust** (investment trusts), **Dealers** (dealer total, own account
plus hedging, the only dealer series reported in every development schema era). The residual (all other investors)
is the counterparty to the three classes and is not a class here.

## 2. Estimation

With stock fixed effects, pooled over the universe, on usable days:

- **Rule of class c:** u_{c,t} = r_c u_{c,t-1} + w_c x_{t-1} + η_{c,t}. The class responds to yesterday's deviation
  (delay d = 1), because a same-day regression would pick up the price impact of the day's own flow. So the class's
  feedback kernel is w_c r_c^m on x_{t-1-m}.
- **Prices:** x_t = Σ_{j=1}^{5} a_j x_{t-j} + κ U_{t-1} + ε_t, with U = u_Foreign + u_Trust + u_Dealers. There is one
  impact coefficient κ, as in the paper's model. The class-specific impacts are reported as a diagnostic only.
- **Derived quantities:**
  - H_c = κ w_c / (1 − r_c): class c's contribution to the feedback budget, which is the fall in S when class c's
    feedback is halted.
  - U = Σ_c H_c: the fall in S from cutting all feedback. A uniform cut by a fraction λ lowers S by λU.
  - S = Σ_j a_j + U.
- **Uncertainty:** a stationary bootstrap over dates (mean block 20, B = 999, seed 20261121). Every equation uses the
  same resampled dates. Intervals are 95% percentile intervals. Fixed effects are not re-estimated within draws.

## 3. The price-only experiment

The composition is the three rules (r_c, w_c). Everything else is held at its estimate: the a_j, κ, the delay, and
the law of each class's non-feedback flow. This gives the price-only supervisor every advantage. The ranges below are
therefore the *least* ambiguity such a supervisor faces.

Under these assumptions:
- the spectral density of x is g/|A(e^{-iω})|², where g is the same under every composition and
  A(z) = 1 − Σ_j a_j z^j − κ z^{1+d} Σ_c w_c/(1 − r_c z);
- prices depend on the composition only through the aggregate kernel Σ_c w_c r_c^m;
- the divergence rate per observation between the estimated composition θ̂ and an alternative θ′ is Whittle's
  (1/4π)∫[R − 1 − log R]dω, with R = |A_θ′|²/|A_θ̂|². This is computed on 8,192 frequencies.

**Two records:**
- the whole development panel, n = all usable stock-days of the price equation, treated as independent stocks
  (generous to prices);
- one stock, n = the median number of usable days per stock.

## 4. The three outcomes

**Q1, separating the classes.** The closest single-memory population has every class with the same decay R and
free weights. Compute:
- the smallest price-record divergence rate from θ̂ to such a population (over R ∈ [−0.99, 0.99] and the total
  weight);
- the same for the tagged record: prices plus the three class flows. Its rate is ½E[d′Ω⁻¹d], where
  d_c = w_c x_{t-1} − W_c q_c(R)_t, q_c = (1 − r_c L)/(1 − R L) x_{t-1}, and Ω is the residual covariance of the
  three rule equations;
- the ratio of the two rates;
- Pinsker's necessary record length for any 5% test to reach 80% power, 2(0.80 − 0.05)²/rate observations,
  converted to years. One development year is a quarter of the development trading days. This is reported for one
  stock's prices, for the whole panel's prices, and for one stock's tagged record. These are lower bounds ("at least").

**Q2, the targeted halt.**
- Compute the minimum and maximum of the foreign-halt effect H′_Foreign over every alternative θ′ that meets three
  conditions:
  - (a) n·rate(θ̂, θ′) ≤ J₀ = 0.02. Then, by Pinsker, no test of any size has power more than 0.10 above its size;
  - (b) each class's contribution satisfies |H′_c| ≤ h̄ = 1 − Σ_j â_j, the stability margin. If h̄ < 0.01, then
    h̄ = 0.01 and the floor is flagged;
  - (c) the alternative price process is stationary.
- Optimizer: SLSQP from θ̂, its five relabelings, and 40 seeded random starts pulled into the set. The relabelings
  have rate exactly 0, so H′_Foreign ∈ {Ĥ_Foreign, Ĥ_Trust, Ĥ_Dealers} at every record length. That set is reported
  separately as the exact barrier.
- **Sensitivity:** the same ranges with the tight box h̄ = 2·max_c |Ĥ_c|.
- These are compared with the tagged estimate Ĥ_Foreign and its bootstrap interval.

**Q3, the uniform cut.** The minimum and maximum of U′ = Σ_c H′_c over the same set, compared with the width of the
Q2 range.

Both Q2 and Q3 are reported for the whole-panel record and for the one-stock record. The ranges are the extremes the
search found. The search can only miss values, so the true ranges contain the reported ones.

## 5. Pre-specified sensitivity runs (all reported)

1. Dealers as own account only (dealer own-account series, available from 2014-12-01).
2. Same-day timing, d = 0.
3. One price lag, p = 1 (the paper's AR(1) form).

## 6. Rules

- The notebook computes everything once and saves `p1m_results.json` (and a zip) to Drive. A rerun loads it and does
  not recompute.
- A failure before any number exists (loading, parsing, a crash) is a bug. It is fixed, the fix is noted in this file,
  and the run is repeated.
- Once numbers exist, they are the result. A later error is reported next to the original numbers.
- **What this is not:**
  - The P1T holdout found that tagged foreign flow is predicted by prices, but its pre-specified check attributed the
    gain to prices revealing past flow (D = −0.0065 after residualizing). The estimated w_c are therefore tagged
    responses, not established causal feedback.
  - The measurement calibrates the paper's theorems at those responses. It does not test the theorems or the
    feedback premise.

## 7. The text for the paper (placeholders filled from `p1m_results.json`)

Numbers are rounded to two significant digits. Years are rounded to whole years above 10. The paragraph is placed in
the main text before "Scope and conclusion", with a table of the estimates.

> **The barrier in a real market.** Taiwan's exchange reports each day's net buying in every listed stock by three
> classes: foreign investors, investment trusts and dealers. Over 2013–2016 ({N} stocks, {n} stock-days) we estimate
> each class's rule from its own flow and the market's response to flow from prices (Table~\ref{tab:barrier}). We then
> ask what a supervisor who sees only prices could learn. We grant that supervisor the market's impact function and
> the law of non-feedback order flow, so that only the composition is unknown.
>
> Three numbers follow. *First, prices separate the classes slowly.* The closest single-memory population is one in
> which all three classes share one decay. Against it, a stock-day of prices carries {rate_p} nats and a stock-day of
> tagged flows {rate_t}, which is {ratio} times more. Before any 5% test could reach 80% power, prices alone need at
> least {yrs_stock} years of one stock, or {yrs_panel} years of all {N} stocks treated as independent. The tagged
> record needs at least {yrs_tag} years of one stock.
>
> *Second, prices cannot fix a targeted halt.* With tags, foreign feedback contributes {H} to the feedback budget
> (95% interval [{lo}, {hi}]), so halting it changes the budget by minus that amount. Consider the compositions that
> the whole panel record cannot tell apart, in the sense that no test exceeds its size by more than 0.10. They imply
> contributions from {Hmin} to {Hmax}; even with each class's contribution capped at twice the largest estimated one,
> the range is {Hmin_t} to {Hmax_t}. However long the
> record, relabeling alone leaves {H_F}, {H_T} and {H_D} all possible.
>
> *Third, the uniform cut is fixed by prices.* Over the same compositions, the effect of cutting all feedback lies
> between {Umin} and {Umax}.
>
> These are calibrations of Theorems~\ref{n:cost} and~\ref{n:dual} at the tagged responses, not tests. The
> registered Taiwan test (Supplement Section~\ref{sec:scope}) did not establish that those responses are feedback
> rather than prices revealing past flow.

If an outcome goes the other way (for example, the uniform range is not narrower than the targeted range, or the
targeted range lies inside the tagged interval), the paragraph says so in place of the corresponding sentence. Its
heading and position do not change. The template is implemented, word for word, in
`research_extension/paper1_publication_revision/t6/round6.py`, which fills it from `p1m_results.json` and adds Table
`tab:barrier` and the supplement subsection `app:barrier` (all four runs, and the one-stock ranges).

## 8. Post-result notes (21 November 2026, after the run; nothing above this section was changed)

- **Run:** computed 2026-11-21T20:44:23Z in the authors' Colab, once.
  - `results/p1m_results.json` has SHA-256 `b7ad67bb…`. Its copy inside `results/p1m_results.zip` is identical.
  - Hashes recorded in the file: core `50df914b…`, which matches the committed `p1m_core.py`; executor `8d8a70a3…`.
- **Section 7 direction checks: all three predicted directions hold, so the template's default sentences apply.**
  1. A stock-day of tagged flows carries 4.7×10^5 times the information of a stock-day of prices.
  2. The targeted range is the whole box in both boxes: ±0.028, and ±0.0027 in the tight box. The tagged 95% interval is [0.0012, 0.0016].
  3. The uniform range over the whole panel is [0.00145, 0.00189]. That is 127 times narrower than the targeted range, and close to the tagged interval for U, [0.00138, 0.00199].
- **Added after the run, with no template sentence and no number changed:**
  1. **Clarification after the paragraph:** both record lengths compare feedback rules with each class's non-feedback flow held at its estimated law; with tags, each class's contribution is estimated directly.
  2. **On size:** κ = 0.0038, so the three classes together contribute 0.0017 to a feedback budget of 0.97.
  3. **One abstract sentence:** prices pin down the uniform cut but cannot attribute feedback to classes.
  4. **Layout:** the estimates table is set at `\footnotesize`, and the supplement subsection is moved to its own section before the machine-check sections.
- **Reading note:** "at least 5,738 years of one stock" for the tagged record is a statement about separating feedback rules with non-feedback flow held fixed. For the 300-stock panel it is about 19 years. The bootstrap intervals for r_c come from the regression in which flow and rule share one decay, and there Foreign and Trust separate (0.31–0.38 against 0.39–0.43). These are different questions, and the paper reports both.
