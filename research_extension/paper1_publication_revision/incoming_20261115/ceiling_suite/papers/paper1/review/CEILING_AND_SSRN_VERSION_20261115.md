# Paper 1: the ceiling, and what the SSRN version adds (15 November 2026)

Written by an AI system for the authors. This is one reader's judgement, not independent review.

## What the literature check found

| Claim in our paper | What already exists | What follows for us |
|---|---|---|
| Cost exponent (spacing)^-(4K-2) | Mixtures with near-colliding components: Heinrich and Kahn (2018, Ann. Stat.), Wu and Yang (2020). Super-resolution of near-colliding point sources: Batenkov, Goldman and Yomdin (2021, Information and Inference 10(2)), error amplification SRF^(2p-1) | The rate is known mathematics. Our version applies it to any smooth family of trading rules inside a feedback loop, with one proof for passive and probing observers. We cite this and do not claim the rate |
| "Universal law" (T3) | Heinrich–Kahn's strong identifiability (linearly independent derivatives) is exactly the condition for attainment | We prove the lower bound for every smooth family. Attainment is conditional (Proposition n:univup); we do not claim the transfer of Heinrich–Kahn's inverse bound |
| Forecast irrelevance | Part (i) is elementary. Forecasting aggregates from components: Lütkepohl (1987), Hendry and Hubrich (2011, JBES) | New in the market: feedback parts drop out, so only informed or exogenous flows of different persistence can carry information. The contrast "cost explodes, forecast value does not move" is the new idea |
| Estimating trader shares from prices | Brock–Hommes models fitted by Boswijk, Hommes and Manzan (2007, JEDC) and others. Lux and Zwinkels (2018, Handbook vol. 4) report near-collinear parameters, insignificant switching parameters and start-dependent estimates. They also note that the market-maker coefficient cannot be separated from the reaction coefficients | Our theory explains this fragility: shares are identified only through the kernel, at a cost that explodes. This is the strongest hook for a JEDC readership |
| Positions do not forecast returns | Sanders, Irwin and Merrin (2009, JARE): large traders follow trends, but their positions show very little evidence of leading returns | Consistent with forecast irrelevance. Weekly positions, not flows, so this is consistency, not a test |

## The ceiling, stated plainly

- **The core mathematics is known.** A paper whose novelty is the rate cannot reach the top of the field. Its novelty has to be the economic object and the three-way split: invisible, irrelevant, needed only for targeting.
- **Theory alone, written well:** about 74–77. It is a JEDC, Journal of Financial Markets or Finance and Stochastics paper.
- **With H1 passing** (account records separate memories that prices do not): high 70s.
- **With H1 and P1F-A1 passing, plus a measured exponent in account data (E3):** about 82–86. RFS or Management Science become realistic.
- **Above about 88:** needs an economic consequence measured in money or in a policy outcome, for example a regime change in which tagging changed what supervisors could do. No such data exist in this project.
- **95 is not reachable with this core.** That level requires a new idea that changes how a field thinks, with evidence to match. The invisible/irrelevant split is a good idea, but it rests on known rates.

## What the SSRN version (paper1_ssrn) adds

1. **A new introduction.** It opens with three findings from separate literatures (fragile share estimates, positions that do not forecast, regulators requiring identifiers) and answers them with one idea, in three consequences.
2. **Theorem 4.5:** the lower bound for any smooth family of rules, proved in full in Supplement S28.
3. **Proposition 4.6:** attainment under an inverse bound, proved, with the condition marked as not proved here.
4. **Section 5:** forecast irrelevance.
   - Theorem 5.1: part (i) proved; part (ii) via Ing and Wei (2003), for a fixed population.
   - Remark 5.2: drift; not proved, simulation only.
   - Proposition 5.3: exceptions; proved.
5. **Evidence paragraph:** P1F void and its replacement window, and H1 collection, both stated as they are.
6. **Title-page disclosure:** says that the proofs of the four new results are being checked by the authors. Delete that sentence only after the check.

## Before posting

- Check the proofs of S28 (about five pages).
- Read Ing and Wei (2003). Confirm their conditions on the news and on the growth of L, and confirm that their result is for same-realization prediction.
- Confirm the Gauss–Radau facts: positive weights, exact to degree 2K-2. These are standard.
- Then edit the disclosure sentence and post.

## Update, later on 15 November: three gaps closed, and the other tool's branch

**The branch `paper1-focused-validation-2026-11-14`.** It holds no work. Its tip is commit `1f7180f`, an older commit
of `main`; it is 0 commits ahead of `main` and 10 behind. Whatever the other tool wrote was never pushed. The same is
true of the two older `claude/` branches (0 ahead). Nothing could be merged.

**Gaps closed in the SSRN version (all in `ssrn_parts.tex`, proofs in Supplement S28).**

| Gap before | What was done | Status |
|---|---|---|
| "Invisible" and "irrelevant" were two separate results | **Theorem 5.1 (detection equals forecast loss).** For any two populations, the information a price record carries about which one is trading equals the cumulative forecast loss from confusing them, divided by twice the news variance. No test separates them until that loss exceeds one period's news variance | Proved (a few lines; the mathematics is the standard chain rule, and the paper says so). Checked by simulation on 64 cases; Figure 2 |
| The upper bound for general rules was conditional on an inverse bound we did not prove | **Theorem 4.6.** For linear rules of any memory shape, the cost is of order spread^-(4K-2) above and below, in the paper's own experiment model, under a rank condition on the derivatives of the memory shape. The condition is proved for exponential and power-law memory and checked numerically for two more shapes | Proved in full. Estimator simulated: slopes -3.05 and -3.08 against -3 |
| Forecast irrelevance relied on a cited expansion for one fixed population | **Theorem 5.2(iii).** A bound on the value of composition to a forecaster that holds at every horizon and uniformly over the number of groups and the spacing of memories (Bayesian autoregression, log-likelihood units) | Proved in full. Simulated: 44.4 and 44.1 against a bound of 66.5 |

**Still open, and not closable by writing.**
- No direct evidence on real accounts until H1 opens (mid-December at the earliest) and P1F-A1 runs (16 January 2027).
- No upper bound for nonlinear rules.
- The drift rate in Remark 5.3 is not proved.
- The proofs of S28 have not been checked by the authors.

**Effect on the level.** Theory only: about 76 to 78. The paper now has one idea that a reader can repeat (a market
hides exactly those features of its traders that do not matter for its prices), with matched bounds that no longer
depend on exponential memory. The ceiling table above is unchanged: evidence, not theory, is what moves it past 80.
