# Switching-regression repair: implementation verified, empirical study open

The original `empirical_pipeline/markov_switching_var.py` is preserved as historical evidence. It is a scalar regression for differenced USD EMA deviation on lagged deviation and base-unit flow, not a two-equation VAR. It does not supply structural identification.

Named defects in the preserved generator:

1. Transition updates multiply marginal smoothed probabilities at adjacent times. Those products generally differ from the posterior probability of a state transition conditional on the whole observed sequence.
2. Hard persistence bounds are imposed without statistical/economic justification.
3. Gaussian densities are floored at 1e-15, changing the likelihood for tail observations.
4. The reported likelihood can precede the final coefficient/transition update; iteration count is labeled convergence without checking terminal status.
5. State persistence plus ten times a dimensional flow slope is called a stability index. Changing flow units changes this index.
6. Posterior state durations are called seconds despite absent verification of deduplication, missing seconds and date boundaries in this fit.
7. Latent switching is interpreted as endogenous causal feedback bifurcation without identifying information.

The new `switching_regression.py` uses log-domain forward/backward calculations, exact pair posterior transition counts, separate segment starts, free fitted initial-state probabilities, explicit convergence/iteration-limit status and final-parameter likelihood matching. A declared variance floor prevents mixture variance collapse; empirical sensitivity to that floor remains required. Shared-mean/variance-switching and full coefficient-switching specifications are available for comparison.

Independent checks: exhaustive enumeration of all 16 paths in a four-observation/two-state example matches likelihood, state posteriors and transition posteriors; segment resets exclude boundary transitions; simulated conditional-regression tests verify likelihood ascent, row-stochastic transitions and final likelihood consistency. Three tests pass. These verify computation, not market fit or scientific conclusions.

## Empirical study and inference review — October 7, 2026

The completed study uses ten-second states from the existing April 7–19, 2021 caches. Evaluation dates are April 13–19, 2021; the prior 2022 date list and one-second return label were incorrect.

All 264 stored fits have their final likelihood independently recalculated. All 96 full-sample starts converge; 12 of 168 forecast starts and four selected forecasts reach their iteration limit. All cases are retained. BTC's lower variance binds at both fixed variance floors: full-switching EMA SD ratio changes from 1103.44 to112.22 and return ratio from1112.62 to113.14. ETH/ADA full-sample lower variances do not bind. These are constrained conditional fits, not identified crisis multipliers.

All baseline MSE comparison intervals include zero. BTC/ETH switching density scores improve under exploratory seven-date references; ADA intervals include zero. Every full-switching versus variance-only comparison interval includes zero for both loss measures. This provides no clear forecast advantage for additional coefficient switching, and does not prove regime absence, equal forecasts or absence of adaptive trading. The old62.7 ratio remains unsupported; its exact historical origin is not proved by non-rejection.

Six focused tests cover exhaustive hidden paths, segment resets, likelihood ascent/final parameter consistency, C/Python tail agreement, independent Gaussian predictive score and training-only scale. `market_verification.json` records fit-level numerical checks, source hashes and receipt contradictions. Provider, model adequacy, serially justified parameter inference and causal interpretation remain open.

The revised standalone LaTeX supplement includes every fixed floor/specification case and all three forecast comparisons. The earlier29-table ledger applies to an earlier manuscript source and cannot certify the subsequently edited48-page manuscript.

Method reference: Rabiner (1989), equations37–40, https://doi.org/10.1109/5.18626 (primary article: https://web.mit.edu/6.435/www/Rabiner89.pdf).
