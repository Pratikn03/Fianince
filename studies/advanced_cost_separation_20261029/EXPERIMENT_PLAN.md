# Advanced deep research plan

This is exploratory work designed after the preceding returned experiments,
not independent preregistration. Freeze this file, configuration and source
hash before executing. Preserve all rows, failed tests and negative results.

Default DEEP: 24 seed clusters x 12 independently generated cohort cases =
288 economies; 4,096 reading repetitions per case and N; N=8,32,128;
three cost multipliers; horizons 10,60,240 model minutes. Seven measurement
rules plus the same-error oracle are compared against the analytically optimal
same-error no-data benchmark. Rows reuse readings and are not independent
market experiments. Every statistic needed to replay decisions is saved.

Declare known a, kappa, a total-feedback cap and the noise contract per case.
Vary the UNKNOWN number of cohorts, weights, adaptation rates and merged/shared
memories continuously. Include rates as small as 1e-6. Include independent
Gaussian noise, correlated Gaussian taps, finite-variance t3 reset totals,
biased readings and changed future feedback. No hidden truth enters any
non-oracle estimator: it sees reset totals and declared contract inputs only.
Fixed-horizon positivity and reset assumptions remain substantive.

The measurement bill is N times multiplier*(0.0005+0.000025*H), explicitly
charging longer observation horizons. Execution, carry and information fees
remain in profit and capital. Prices and fees are illustrative, not observed
reporting costs. If the information purchase exceeds the budget, do not buy:
use the same-error no-data fallback and keep the unaffordable row.

Methods: Gaussian iid, Gaussian declared variance bound, projected Student-t
unknown-variance interval, median of means with a DECLARED finite-variance
bound, full-response iid ellipsoid, uncertified point estimate, and a
conservative rational Gaussian margin. The projected Student-t method is exact
only for independent Gaussian reset totals; median of means needs independent
resets and a valid externally supplied variance bound. Neither fixes mean bias
or changing future dynamics. These are established estimators, not new ones.

Report by scenario and method. Use seed-cluster paired bootstrap intervals for
the prespecified simulator averages. Apply Holm correction to all one-sided
binomial exceedance checks for declared-valid purchased certificates. A lack
of rejection does not prove validity. Do not interpret an invalid method's
extra profit as a fair improvement. No test result proves novelty.

Proof audit: retain the old exact moment matching and accounting checks; add
a rational positive-value witness and Lean integer certificates for its
concrete scalar inequalities. The Gaussian tail/model implications remain
written analysis, not a complete Lean formalization. All axiom output and
compiler/download hashes are saved. Failure or skipped Lean is not a pass.

Optional real-data stage requires declared event-level best-quote data and
metadata. It uses past-only response scores and purged chronological
train/validation/test folds with volatility, HAR and OFI/depth benchmarks.
The real-data stage is observational and does not inherit the reset theorem.
Without suitable supplied data, mark it NOT_RUN; do not download klines and
rename them an order-book experiment. External specialist review, novelty
assessment and independent implementation remain requirements.
