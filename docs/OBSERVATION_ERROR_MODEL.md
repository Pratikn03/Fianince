# Observation-error model

The next-stage benchmark generates a latent episode process, adds independent
measurement noise to the regressor and response, optionally introduces within-
episode AR dependence, and masks records at a declared missingness rate. The
estimator fits an intercept-plus-slope model to observed rows. Its interval is
formed by resampling complete episode IDs, not individual rows.

The reported coverage is therefore a simulation-calibrated property of the
implemented observation law. It is not a proof of exact coverage under market
data, and it does not reuse the independent-episode theorem when dependence is
present. The constrained condition is deliberately retained to expose
unresolved and wrong-confident calls.
