# Internal review of the second corrective revision

Date: 26 September 2026. These reviews were AI-assisted and internal. They do
not satisfy independent human proof, statistical, economic or novelty review.

## Findings and dispositions

| Finding | Disposition | Regression evidence |
|---|---|---|
| Pre-probe x0 used where beta0 requires the post-probe response | Corrected response alignment; original comparisons withdrawn | `test_observation_repairs.py` checks actual simulated response against 1,.4,.37 |
| Missing/NaN endpoints treated as coverage or silently removed from width means | Explicit invalid, unbounded and finite counts | Observation and statistical artifact tests |
| Optimizer nonconvergence not honored by naive point comparator | Retain failed status and inputs; no coverage or issued label | Injected `solver_failure` regression |
| Profile and sandwich outputs conflated; arbitrary SE fallback | Separate interval/status fields; unavailable inference; numerical local profile boundary search | `test_output_error_repairs.py` |
| Gauss--Newton bread omits residual-weighted curvature under persistent misspecification | No new full-Hessian claim: label covariance a local GN approximation in code and paper | Review found illustrative SE .00144496 vs full-derivative .00149246; this is a review diagnostic, not a new production result |
| Known and estimated covariance pivot contracts conflated | Known chi-square and estimated independent-Wishart F modes | Conic repair tests and separate 20,000-draw calibration |
| Conic final unsolved cuts and upper dual endpoint bookkeeping | Retain full solved constraints; correct both objectives | `test_conic_repairs.py`; full outward arithmetic still unverified |
| Sweep exception could discard earlier or failed panel | Incremental exclusive files and per-panel failure records | Injected fitter failure on attempt two |
| Singular covariance diagnostic could raise before retaining the failed panel | Preserve unavailable distance/event and exception diagnostics | Injected singular second covariance; all six attempted records survive |
| Python string escaped TeX textwidth as a tab | Raw TeX string and literal-output tests | `test_statistical_paper_artifacts.py` |
| Uniform rank theorem presented as pointwise necessary at nonnegative boundaries | Qualify uniform/interior scope and include boundary counterexample | `test_economic_contract_repairs.py`, mathematical repair fixtures |
| Appendix impulse normalization multiplied impact twice | Explicit H(z)=sum beta_j z^-(j+1)=kappa sum h_j z^-(j+1), h0=1 | State-space comparison at impacts .02,.5,2 |
| Known total and n-1 probes said never to identify rate | State lack of general joint identification; show total-probe rate-only identification | Exact rational U=(1,1) counterexample |
| Later funded scenario labeled stable by unused nominal a | Report actual a_eff=.8, S_eff1.22, full rho1.07409 and timing | Finite differences against real trajectories |
| Capacity described as added equity and hit flag as permanent halt | Correct capacity/inventory, equity, reverse-fill and margin-event language | Economic contract characterization tests |

The code reviewer confirmed the two rounds of failure-path fixes. The
mathematical reviewer checked a bounded selection of statements, not every
theorem or historical dataset. Reviews did not establish novelty.

## Run preservation

Two attempts were stopped while review found additional failure-handling bugs.
Their protocol and completed panel files remain under the top-level and
`final/` directories in `statistical_repair_20260926`; they are not final
evidence. Accepted, unchanged-design reruns use `verified/`. The first sweep
attempt lacked per-panel checkpointing, so its in-memory partial results were
not recovered. That defect is disclosed rather than claiming perfect retention.

## Remaining scientific boundaries

- Full outward construction of conic numerical constraints is not verified;
  certified classifications remain withheld.
- Profile and GN intervals remain local approximate calculations. The
  misspecified model is not repaired by a larger standard error alone.
- Five grid replicates per fixed cell support descriptive correction, not a
  prospective high-powered comparison or a general superiority claim.
- Independent human review, exact-model economic novelty, calibrated real
  execution, authorship/rights confirmation and publication remain separate.
