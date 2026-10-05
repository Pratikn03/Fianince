# Withdrawn code (audit of 2026-10-03)

The code in this folder produced results that were removed from the paper.
It is kept only for transparency. **Do not cite any number it produces.**

| Path | Why it was withdrawn |
|---|---|
| `empirical_pipeline/causal_inference_2sls*.py` | The "latency instrument" was simulated inside the script (`np.random`) and injected into OFI. The 2SLS table (FI-2010 S=-0.3796, F=89.6–112.45) was therefore not an estimate from market data. FI-2010 and cross-venue timestamp data are not in the repository. |
| `empirical_pipeline/robustness_check.py`, `btc_robustness.py` | Belonged to the withdrawn 2SLS pipeline. |
| `tests/test_crypto_panel_regression.py` | The panel β=-0.0124 was the synthetic generator's `true_beta`. The real-data test was always skipped (the loader scanned `.zip`, but the data are `.csv`). It regressed same-day return on same-day imbalance, not next-day return on S. |
| `tests/test_solvency_phase_diagram.py` | Price was an exogenous AR(1), and the `S` argument never entered price dynamics. The "non-AI" benchmark was random noise, not Avellaneda–Stoikov. The DQN updated only its output layer. Several asserts were trivial (`assert True`, `assert 30 == 30`). Replaced by `simulations/feedback_dealer.py`. |
| `tests/test_continuous_rl_audit.py` | The "continuous actor-critic >70% support" result came from an untrained Gaussian sampler. |
| `tests/test_cross_simulator_validation.py` | The classifier used a hand-calibrated growth-rate threshold (0.03), not the paper's certificate. The simulated prices were integrated, so S=1 was not their boundary. "Kyle CDA" was mislabeled (Kyle 1985 is a batch auction). |
| `tests/test_decisiveness_tradeoff.py` | The "our method" it tested was the same growth-rate heuristic, not the LP certificate. |
| `prose_patch_scripts/*` | One-off scripts that wrote text and numbers directly into the `.tex`, including literals with no computational source (e.g. `run_full_audit.py` contains the F-statistics as a string literal). `generate_plots.py` drew `ci_width = c/sqrt(eta_0)`, a schematic curve that was not computed from any estimator. |

The replacement analyses are listed in `results/provenance/ledger.md`.
| `tests/test_econometric_robustness.py` | Its "FI-2010 2SLS" test simulated data with `s_true = -0.3796` and checked that 2SLS recovered it. That is the source of the number formerly reported as an FI-2010 estimate. |
| `tests/test_statistical_hygiene.py` | Its "multiple-testing" and "effect-size" checks ran on p-values and outcomes drawn from `rng.uniform` / `rng.binomial` and chosen so that they would pass. It tested nothing in the paper. |
