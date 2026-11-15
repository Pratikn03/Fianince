# Unregistered candidate amendment: implementation and inference repairs

This document records proposed changes for author review. It is not an approved or published registration. The original A1 specification, notebook, executor, hash record and unlock counter are preserved in `source/ceiling_suite/p1_empirics/`. All four registered hashes match, and the replacement counter remains at zero. The candidate executor refuses live execution.

The candidate implements the following changes:

1. Purge training origins whose one-step A2 or eight-step A1 target enters the evaluation half. Inner power-gate training has the same purge.
2. Restrict the power gate to a copy of the training half. Estimate the baseline on the inner training sample, construct residuals, and calibrate synthetic signal strength using inner-training residual and target variances. This is estimated calibration, not knowledge of the population incremental effect.
3. Score every eligible evaluation row, including the partial final UTC day. Report scored days and row counts from the same mask.
4. Use a circular moving-block bootstrap over common cross-symbol daily loss contributions, with a three-day candidate primary length and one- and five-day sensitivity. This choice needs the simulation gate below; it is not automatically valid for arbitrary long dependence.
5. Require the lower one-sided 90% confidence limit to exceed the economic margin for “relevant,” and the upper one-sided limit to fall below it for “irrelevant.” Otherwise report “inconclusive.” The interval between those endpoints has central coverage 80%, not 90%.
6. Use quantity open interest, matching the field named in the original specification. Use a trailing 48-bar arithmetic average for the class-level feature. These choices resolve ambiguities and differ from the registered code.
7. Produce the missing five-minute secondary comparison. It uses the primary eligible-symbol universe, five-minute bars, and the listed half-lives measured in bars; its horizon is one five-minute step. Report its own eligible rows.
8. Select metrics strictly before the bar end using `searchsorted(..., side="left")`, with no one-nanosecond subtraction; enforce snapshot age within the bar and complete underlying candle coverage.
9. Describe a favorable joint result as supporting the specified learners and margin. Do not call it a proof of structural invisibility, observed pricing errors, or a particular causal mechanism.

The output uses `A2_candidate_wording` and `A1_candidate_wording` and identifies itself as an unregistered offline candidate. These are proposed statements for author review, not an approved replacement for the registered readout.

The two 30-market, 60-day synthetic worlds were rerun through checksummed archive-format files, alternating kline layouts and a missing metric file. The gate used its full 200 draws. The feedback-only world returned an A2 gain of approximately -0.0052 percentage points and an irrelevant verdict; the informed world returned approximately +0.7920 percentage points and a relevant verdict. Both five-minute comparisons returned the corresponding verdict. These are simulation outcomes, not Binance results.

The full calibration requirement remains open. The package also runs a frozen 3,200-replication diagnostic grid at population-oracle gains of zero, half the margin, the margin and twice the margin, with persistence, common factors, heavy tails and missing reports. Its criteria and results are recorded without retuning. The finite fitted learner's conditional risk differs from the population-oracle gain, so this grid is not a size theorem for that conditional estimand. Measurement-error and changing-volatility scenarios, a precise estimand-specific coverage calculation, and a complete gate evaluation are additional requirements. Then publish the exact amended files, readout rules, hashes and run-state policy before held-out data access. Do not reset or reinterpret the void original run.

The manuscript's empirical status remains pending regardless of the synthetic outcomes above.

The completed frozen grid failed 7 of its 12 non-descriptive diagnostic cells. At the population-oracle margin, irrelevant verdicts occurred in 55, 80, 68 and 82 of 200 repetitions for iid, persistent-common, heavy-common and missing-report scenarios, respectively. Twice-margin relevance power also missed the declared criterion in the latter three scenarios. These failures are retained; this candidate is not cleared for confirmatory use. See the audit for every cell, Monte Carlo intervals and the distinction between oracle and fitted-learner estimands.

The registered notebook also fails current notebook-schema validation because its Markdown cell includes an `outputs` field. `P1F_A1_Schema_Review_Only.ipynb` repairs that format in a separate copy and blocks every code cell before execution. It is not registered, is not a live study runner, and does not change the original hash. Integrating any corrected notebook and executor remains part of the documented amendment obligation.
