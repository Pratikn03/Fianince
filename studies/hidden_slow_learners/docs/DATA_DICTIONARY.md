# Data dictionary and interpretation

All model time steps and price responses are synthetic and dimensionless. No row is an observed financial institution, security, or human participant.

## Exact construction

- `exact_witnesses.json`: 112 rational constructions. `K` is the number of matched kernel terms. `a`, nodes, signed barycentric weights, scale, and weights are rational strings. `Q_minus` and `Q_plus` straddle `1-a`. Zero weights are removed and active agents are split only when forming equal-count model representations.
- `exact_pairs.csv`: one row per pair. `agents_each` is the active count after splitting. `rho_minus` and `rho_plus` are eigenvalue radii, not risk probabilities. Matched price coefficients are h[0] through h[K+1] inclusive; `next_price_difference` is at K+2.
- `matched_pair_baselines.csv`: one row per pair member, fitted from the common short kernel prefix. It includes nondecisions; these must not be removed to exaggerate coverage.
- `matched_shock_paths.csv`: three common-shock tests per pair. Finite path variances are equal up to numerical error because the paths are matched. They are not stationary variances.
- `readable_witness.json`: the separate a=2/5, nodes={0,1/2,19/20} example, including exact rational parameters, rounded eigenvalues, and response coefficients.
- `witness_impulses.csv`: t=0,...,200; stable, unstable, and frozen-learning responses to the initial unit price shock. Frozen learning starts with zero adaptive memory.
- `witness_horizon_recovery.csv`: noiseless estimator and bound behavior at longer horizons for the readable pair.

## Measurement panel

- `configurations.json`: 108 fixed cases. `q` and `eta` each have eight slots; some q values are zero in the no-slow-feedback condition. `loop_ratio = Q/(1-a)`. The panel has equal numbers of stable and unstable cases by design, not as an estimate of prevalence.
- `true_kernels.npz`: array `kernels`, shape (108,256), containing noiseless loop-open response kernels.
- `measurement_inputs.npz`: 21,600 independent observation-noise datasets. `first_tap_means` has shape (21600,32); `partial_sums` and `terminal_taps` each have shape (21600,4); `horizons` is [4,16,64,256]. `case_ids`, `noise_ids`, `repetition_ids`, and `tap_standard_errors` link each row to the model and noise design. The remaining tap means can be exactly regenerated from the seeds and configurations.
- Tap noise is independent Gaussian with standard error `relative_sigma*(1-a)/sqrt(128)`. Sample means are directly simulated from that distribution. These are not 128 actual repeated market runs per saved mean.
- `decisions.csv`: 86,400 dataset-horizon rows. `true_label` is computed from hidden parameters. `lower` and `upper` are rate-aware feedback bounds. The six named methods contain stable, unstable, inconclusive, or model_conflict. `interval_event` and `feedback_covered` are ground-truth auditing fields; they are not inputs to the diagnostic.
- `measurement_dataset_checks.csv`: one row per independent dataset. Any-error and all-horizon-coverage events use all four correlated horizon evaluations within that dataset.
- `noiseless_bounds.csv`: 432 configuration-horizon rows. All true feedback values are contained by these exact-information bounds.
- `comparison_summary.csv`: aggregate results by noise condition, horizon, and method. Each group has 10,800 datasets, of which 5,400 are truly unstable.

## Denominators and missing values

`decision_fraction = decided / n_datasets`. `unconditional_error_fraction = incorrect / n_datasets`. `wrong_stable_fraction = wrong_stable_count / true_unstable_count`. `wrong_unstable_fraction = wrong_unstable_count / true_stable_count`. `error_among_decisions = incorrect / decided` when any decision exists.

NaN point estimates mean the estimator failed its admissibility checks; their labels are inconclusive, not correct by default. NaN bounds are model/measurement conflicts. A reversed or negative interval is not silently repaired into a stability certificate. CSV string booleans are `True`/`False`.

The 86,400 rows are not independent samples: each group of four shares a noise realization. Statistical uncertainty about any-error events must use the 21,600 independent datasets. The reported Hoeffding interval applies to the design-average probability across the fixed heterogeneous panel.

## Audit records

`summary.json` aggregates actual numerical outputs. `negative_controls.json` documents out-of-contract examples. `environment.json` records executed software versions and runtime. `executed_config.json` is the run's configuration snapshot. `exact_verification.json`, `measurement_verification.json`, and `clean_reproduction_check.json` record internal checks; none asserts independent human replication.
