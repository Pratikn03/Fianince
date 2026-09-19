# Equal-information full-horizon comparison

Status: internal prospective execution protocol, not external preregistration. Written after reading the v1 code and papers but before running v2 comparisons. Any changes are recorded separately.

## Question
Does the v1 rate-aware summary bound provide evidence of a better stability diagnostic after comparison with conventional full-horizon nonnegative exponential-mixture least squares and confidence-set optimization? Or is the defensible contribution a restricted measurement/identification requirement?

## Fixed information contract
Every method receives exactly the same complete kernel-tap mean vector through its horizon, known direct persistence a, known Gaussian standard error, and the same valid rate floor. No estimator receives the number of generating components, exact component rates, component weights, class, or true total gain. Normalize responses by (1-a), making the stability boundary one. Both stable and unstable total gains are allowed.

The old archive saved only 32 early taps plus summary measurements. Regenerate full 256-tap vectors from its documented seeds and loop-open formula, then check every saved tap, partial sum, terminal tap, and standard error. Save the regenerated vectors in this package.

## Methods
1. Original summary certificate, family error budget 0.05.
2. Budget-matched summary certificate, summary budget 0.025. The other 0.025 is reserved for the full-data coordinates used by method 4.
3. Full-horizon nonnegative least squares (NNLS) over 129 logarithmically spaced learning-rate nodes between the supplied floor and one. All H observations are fitted, column-normalized; no upper bound on total gain or true-rate oracle. A point decision is NOT a confidence certificate. Solver failures remain unresolved.
4. Conventional set-membership positive-mixture bounds via linear-programming OUTER relaxation on 64 logarithmic rate bins. Analytic minima/maxima of each response feature over each entire bin cover off-grid true rates. Use all H coordinate intervals and all declared prefix sum/terminal intervals available through H. Use the same total family error budget 0.05; sum/terminal budget 0.025, coordinate budget 0.025 over all 256 taps. Record raw LP bounds and their intersection with valid budget-matched summary bounds separately. Dual feasibility repair, gaps, solver failures, and numerical guards are saved; numerical verification is not formal proof of floating-point arithmetic.

## Outcomes
Primary endpoint: all 21,600 original datasets at H=256, no selection. Secondary horizon sweep: the same 21,600 datasets at H=4,16,64 (86,400 total paired rows). Report confident error counts, false stable/false unstable counts, decision coverage, model conflicts, numerical failures, interval coverage, and conditional error among decided cases separately. Point and set-valued methods are not ranked by accuracy alone. Confidence is over independent noise replicas conditional on the 108 fixed synthetic configurations, not over a sampled population of markets.

## Sensitivity and controls
Predetermined repetitions 0,20,40,60,80 at H=256: 32/128/256 outer bins and 65/257 NNLS nodes, using the same inputs. Do not tune primary hyperparameters after labels are observed. Test off-grid interval inclusion, incorrect rate floors, exact finite-window ambiguous pairs, pure one-rate models, small/no noise and numerical failures. Add a simple Gaussian two-point lower bound with fixed-order hidden modes; identify classical ingredients and do not claim priority.

## Reproduction and novelty
Rerun v1 tests. Test-first implementation, direct analytic checks, LP primal/dual residual audit, alternate solver checks and clean-directory reproduction subset. Distinguish separate code paths in this environment from an external independent replication. A focused primary-source novelty review is not an external expert review and cannot prove priority. Do not contact anyone or upload files to public repositories without authorization.

## Decision rule for interpretation
A good conventional fit alone does not prove a stable label. If the full-moment interval improves decisiveness without sacrificing the declared error control, do not claim superiority for the old summary diagnostic. If exact pairs remain ambiguous for all methods, describe a measurement-identification limitation under the stated model. No result validates real-market crisis prediction, global economic laws, or a paradigm shift.
