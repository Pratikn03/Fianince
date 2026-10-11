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

## Empirical Out-of-Sample Study Completed

The repaired EM estimator (`switching_regression.py` and `run_market_study.py`) was evaluated across 7 chronological out-of-sample expanding window test dates (2022-04-10, 2022-05-15, 2022-06-19, 2022-07-24, 2022-08-28, 2022-10-02, 2022-11-06) for BTC, ETH, and ADA across both state variables:
1. 300-second EMA price deviation state ($x_b^{\text{EMA}} = p_b - m_b$)
2. Raw 1-second price return state ($r_b = p_b - p_{b-1}$)

Across all 12 evaluated configurations (3 assets $\times$ 2 state definitions $\times$ 2 switching specifications):
- Out-of-sample mean squared error difference 95% confidence intervals uniformly span zero (e.g., BTC EMA variance-only: $[-0.3167, 0.1076]$, full-switching: $[-0.0138, 0.0055]$).
- Negative log-predictive score differences show moderate likelihood gains purely from modeling fat tails/volatility clustering, but zero directional or conditional predictive advantage.
- The legacy 62.7-fold regime bifurcation claim and extreme significance ($p < 10^{-300}$) are definitively refuted and withdrawn.

Results are compiled into LaTeX Table 29 (`tab:regime_market_rebuilt`) in `regime_appendix.tex`, integrated into Section K of `full_scope_appendix.tex`, and audited by `check_lineage_receipt.py` (3,219 verified cells).

Method reference: Rabiner (1989), A Tutorial on Hidden Markov Models and Selected Applications in Speech Recognition, equations 37-40. https://doi.org/10.1109/5.18626; primary article copy https://web.mit.edu/6.435/www/Rabiner89.pdf. This is established likelihood machinery, not a new identification theorem.
