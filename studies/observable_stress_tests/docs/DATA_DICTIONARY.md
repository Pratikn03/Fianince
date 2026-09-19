# Data dictionary and information boundary

## Models / design
`configs/models.json` contains 12 evaluation configurations. `a` is direct persistence; `impact` is dollars per share; `rates` are private first-order update rates; `q` are nonnegative feedback weights; `G=sum(q)/(1-a)`. `gain_a_plus_Q=a+sum(q)` is the main stability target. Stability is below one, instability above one. These truth fields are evaluation-only except the declared lower support bound `rate_floor`. That floor is exogenous design information, not estimated from prices.

## Raw public example files
`probes`: shape R, signed fully filled first-step pulse in shares.
`prices`: shape R x 66, observed post-step quote minus initial quote, in dollars. Columns j=0,...,65 correspond to response coefficients beta_j. The final observed lag 65 is included in the simultaneous confidence family but not in the largest fit, which ends at lag 64.

Hidden initial states are independent random draws, not observed or reset to known values by inference. Main covariance is estimated from the public arrays; generating noise scales are not estimator arguments.

## Public summaries
`public_panel_statistics.npz`: `statistics` is (1920,4,66), ordered by panel_id; fields are estimate, lower, upper, standard_error. Units are dollars/share. Each lower/upper interval belongs to a per-panel 95% simultaneous family. Unknown temporal covariance is permitted. Full covariance examples are saved separately. Four raw example IDs are configurations 0,7,8,11 at R=1024, delta=4, replicate=0.

## Primary tables
`panels.csv`: one row per panel, with design, seed, public_sha256, coverage event evaluated against analytic truth, response RMSE, mean absolute adjacent estimation-error correlation, conservation errors, simulated volumes and exposure checks. True response coverage is not supplied to the estimator.

`comparison.csv`: one row per panel/horizon. recurrence_lower/upper are conservative bounds for S; recurrence_label is stable/unstable/inconclusive/model_conflict. Numerical issues are separately status-coded; never turned into a favorable label. The `*_wrong` fields count stable/unstable labels opposite the true fixed linear model. `recurrence_contains` permits the reported 1e-7 numerical tolerance. Deconvolution uses the same response rectangle. Point fitting is an uncalibrated errors-in-variables recurrence fit, not the strongest possible output-error baseline.

Horizon rows from one panel reuse data and are dependent. Their count must not be used as an independent effective sample size. Unconditional error guarantees do not imply conditional error control among decisive labels. Numerically infinite bounds are explicitly possible for weak observations.

## Exploration and failure tables
`budget_extension.csv`: 120 explicitly post-primary panels, five per configuration and each larger budget. `negative_controls.csv`: four controls, 20 panels each. `reference_linear_S` means the original local linear model, not the global stability of nonlinear dynamics. A mismatch with this reference in nonlinear experiments is not automatically a false theorem claim. The false-rate-floor control is a genuine violated-side-information false stable label.

`price_observation_limits.json`: six oracle calculations for a separate Gaussian quote-only pulse experiment, zero initial states, no process noise, two memory states, fixed gains .9/1.1. Rates may become arbitrarily small; not a limit with a fixed positive lower support bound. `price_limit_mc.json`: 100,000 scalar sufficient-score draws verifying one oracle-error value.

## Integrity and storage
Every primary raw dataset has a seed and SHA-256 hash; only four full datasets are stored. Regenerate the remaining raw episodes with the declared source/configurations. Do not claim all 72,990,720 raw quote observations are stored in this archive. All primary measured response summaries and all comparison rows are stored. Legacy source counts belong to different observation laws and must not be pooled with the new data.
