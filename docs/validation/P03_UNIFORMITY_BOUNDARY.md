# P0-3: estimator and formalization boundary

S21 includes kernel-checked algebraic subresults, a known-family inversion bound, and local Prony conditioning evidence. The Vandermonde coefficients use the true eta_1 and eta_2; their perturbation bound is not an error bound for estimated poles. A uniform finite-sample guarantee for the fully parameter-blind nonlinear estimator remains unproved. S13 retains the explicit general-dimensional hSpijker hypothesis. S20 uses an external 1,800-interval Decimal certificate; its full numerical sweep is not checked by the Lean kernel.

## Verified mathematical content

- Exact moment-matched cubic-gap algebra and known-family inversion scaling.
- Positive separated-class Hankel determinant. The theorem named `prony_blind_four_moment_uniform_upper_bound` also assumes a deconvolution error bound and a weight-error formula involving `p_minus` and `p_plus`; its name is not a statement of estimator-level coverage.
- `prony_four_moment_confluent_vandermonde_and_toeplitz_deconv_bound` proves recovery and moment perturbation bounds with coefficients evaluated at the true rates, plus two-lag deconvolution inequalities.

## Outstanding obligation

Control estimated poles, nonlinear root selection, admissibility and weight errors uniformly over the declared class, then connect finite-sample moment concentration to the actual blind estimator. Six tested configurations and empirical slopes are diagnostic evidence, not a uniform proof. The abstract retains the narrower local-conditioning description.
