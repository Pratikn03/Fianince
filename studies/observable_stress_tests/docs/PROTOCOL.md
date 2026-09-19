# Observable stress-test protocol — version 0.4

## Scope frozen before the primary experiment
Extend the original framework and both executed companion studies. Use only randomized probe quantities and resulting quoted prices for estimation. Latent agent states, generating rates, demand coefficients, fundamentalist strength, impact and noise parameters are withheld from inference. The permitted rate floor is public design-side information; it is not learned from short price records.

## Measurement design
Independent episodes of a stylized dealer/excess-demand market; balanced random probe signs with one filled pulse at the first step. Prices are observed for 66 steps. Regress each observed price change on signed pulse size and an intercept. Estimate variance from residuals, with no oracle noise covariance. Exact marginal Student-t intervals and Bonferroni give 95% simultaneous coverage over all 66 response coefficients under the stated linear Gaussian independent-episode contract. Arbitrary correlation within an episode is allowed.

## Primary panel
- Direct persistence 0.4; price impact 0.02 dollars per share.
- Normalized gains 0.70, 0.95, 1.05, 1.30.
- Two memory rates: 0.5 and one of 0.002, 0.02, 0.10.
- Feedback allocation: 60% fast, 40% slow.
- Public minimum rate is the slowest permitted rate in each declared class.
- Probe sizes: 1 and 4 shares; episode counts: 128 and 1024.
- Horizons: 8, 24 and 64 response coefficients after the initial coefficient.
- 40 measurement panels per configuration/design. Total 1,920 panels, 5,760 horizon rows.
- Gaussian background flow standard deviation 0.10 shares; quote measurement error 0.002 dollars; initial hidden memory standard deviation 0.01 dollars.
- Fixed source seeds; no model selection on evaluation labels.

## Primary inference
Positive-response recurrence outer bounds with 64 continuous rate bins, estimating direct persistence jointly. Student-t response rectangles are propagated through the recurrence; no assumption of independent recovered kernel taps is made. Fit outcomes: stable, unstable, inconclusive, model conflict, or numerical failure. A dual-guarded LP estimates the range of a+Q; positivity and true-rate containment imply the true value is inside on the simultaneous event.

## Comparators
Conservative interval deconvolution followed by a rate-aware tail bound; and an uncalibrated nonnegative recurrence least-squares point estimate using all observations. The point estimator is explicitly errors-in-variables, not an optimal output-error baseline and not a certificate. No claim of superiority over all conventional estimators is planned.

## Failure tests and audits
Incorrect rate floor; nonrandom probe assignment correlated with background flow; nonlinear impact/amplitude dependence. Audit cash and share conservation, analytic response recovery, conditional coverage, unknown-parameter access, full seeded reproduction, and off-grid positive mixtures. Negative controls are reported separately, not discarded.

## Evidence boundary
Synthetic, account-consistent dealer model. Not ABIDES, not an order book, not calibrated to a named exchange, no trained neural agents, no live orders, no external replication or novel-priority certification. Linear Gaussian validity cannot be inferred solely because the LP is feasible.
