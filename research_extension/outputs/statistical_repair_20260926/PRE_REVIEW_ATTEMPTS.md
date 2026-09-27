# Preserved, superseded attempts

The first grid and two sweeps in this directory were intentionally stopped
during code review. Their protocol files and available panel files are retained;
they do not constitute completed production runs. The early sweep implementation
did not checkpoint each completed panel, so its in-memory partial output was
not recoverable when stopped. That persistence defect is repaired before restart.

The earlier completed calibration, output-error diagnostic and funded check
are preserved too. None of these top-level attempts is the paper's final
corrective result. Accepted reruns use the `final/` subdirectory, with new source
hashes and exclusive outputs. No parameter, seed, horizon, or outcome was tuned
in response to these attempts.

Review repairs: honor point-fit nonconvergence; retain each completed or failed
sweep attempt, its inputs and error; store before/after source hashes on run
failure. The Gauss--Newton covariance is explicitly labeled an approximation,
not a general misspecification-robust covariance.
