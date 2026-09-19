# Data dictionary

## Units and interpretation

All primary responses are synthetic dimensionless open-loop impulse-response coefficients. A step is an abstract model tick, not a day, millisecond, or regulatory horizon. Stability means spectral radius below one for a fixed positive linear state matrix, not the probability of a crash.

## data/full_measurements.npz

`taps`: (21600,256) complete noisy mean response vectors in the original, unnormalized units.
`case_ids`, `noise_ids`, `repetition_ids`: length-21600 identifiers.
`tap_standard_errors`: known standard error of each averaged tap.
`true_kernels`: (108,256) noiseless responses, for evaluation only. Estimators do not receive these.

Normalize taps and standard errors by 1-a from `configurations.json`. Stability boundary is normalized total gain one. Noise IDs 0/1 use original single-probe noise scales 0.002/0.02 times (1-a), each averaged over 128 independent probes. Averaged normalized standard errors are 0.002/sqrt(128) and 0.02/sqrt(128).

`configurations.json` has 108 fixed cases: 3 direct persistences, 3 valid rate floors, 3 slow-feedback shares and 4 gain ratios. Eight states are used in each generating model; zero weights are allowed. Estimators are not told the count, actual rates, weights, slow share, or truth.

## results/paired_comparison.csv

86,400 rows = 21,600 independent noise vectors x four horizons. Rows at different horizons share data and are not independent.

`legacy_*`: original summary bound at total alpha 0.05.
`budget_*`: summary bound at alpha 0.025, matching the summary component of the LP event.
`nnls_*`: full-horizon positive-mixture point fit on 129 rate nodes. Its label is not a confidence certificate.
`lp_*`: raw continuous-bin LP outer bound on 64 bins, using the complete available data and total alpha 0.05.
`combined_*`: LP interval intersected with the budget-matched summary interval.

`stable`: upper bound/point < 1-1e-8. `unstable`: lower bound/point > 1+1e-8. `inconclusive`: cannot make either call. `model_conflict`: incompatible/empty assumed-model confidence constraints; NOT a safe label. Solver or numerical failures are separately recorded and remain unresolved.

`truth` and `true_gain_ratio` are evaluation-only.
`lp_primal_violation`, `lp_dual_violation`, `lp_max_gap`, `lp_max_repair`: saved floating-point audit quantities. They do not constitute formal exact arithmetic.
`*_seconds`: local elapsed measurements, not portable runtime guarantees.

## Aggregate outputs

`aggregate_comparison.csv`: labels, errors, conflicts, interval coverage by method/noise/horizon.
`family_errors.csv`: any wrong decision across the four horizons per independent vector.
`paired_changes.csv`: primary H=256 gains/losses on matched vectors.
`resolution_sensitivity.csv`: 5,400 additional estimator runs on 1,080 predetermined vectors; not new independent measurements.
`confidence_event_audit.json`: independent checks against the actual simulated noise event; includes every wrong LP decision.
`testing_limits.csv`: exact Gaussian two-point risk and projected likelihood-ratio simulations. The 12,000,000 draws are one-dimensional sufficient statistics, not 12,000,000 market simulations.
`exact_recheck.json`: rational-arithmetic recheck of 112 old pairs plus one readable witness.
`alternate_solver_rows.csv`: 216 same-input checks with separately assembled constraints and HiGHS interior point.
`clean_reproduction.json`: fresh-directory same-environment rerun, not external replication.
