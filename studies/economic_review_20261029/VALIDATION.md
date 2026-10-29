# Validation record

29 October 2026. This is a scoped development check, not independent replication.

* **190 selected tests passed**: 18 new model/analysis tests, 125 existing
  mathematical/economic/conic contract tests, 19 bridge/microfoundation/monitor
  tests, and 28 information-safety tests. The monitor's nested package directory
  was included in PYTHONPATH. This is not a full repository test-suite claim.
* **76 manuscript number checks passed**, using the separately named repaired
  hidden-state result. Historical result files remain unchanged.
* The corrected recomputation checks 500 positive cohort economies and compares
  the cumulative identity with an independently evaluated resolvent. Box safety
  follows from induction; a finite simulation does not prove it.
* The new package's smoke and full modes completed. Full uses 1,000 repetitions
  where specified, 512 response taps, and 200 filtering replications. See the
  saved configuration for the exact study-specific sizes.
* Notebook schema and all Python cells were checked. Every code cell executed
  in local validation mode, including tests, simulations, plots and ZIP export.
  The hosted Google Colab service was not exercised. A separate Jupyter-kernel
  startup was blocked by this environment's socket restrictions; cell execution
  was therefore checked directly in a shared Python namespace.
* Optional real-data code was tested with synthetic CSV fixtures, including
  future-feature invariance and invalid timestamp rejection. No new public-data
  result, causal identification, GPU result or prospective study is claimed.
* Working Paper 1, Working Paper 2 and the synthesis compile in three LaTeX
  passes with no undefined references or overfull boxes in the tested builds.
  The thesis compiles with no undefined references; seven layout overflow
  warnings remain in inherited long formulas/tables/URLs. Compiled PDFs were
  build-check intermediates. Committed older PDFs remain labeled snapshots;
  revised TeX sources are authoritative in this branch.
* The name-mapping audit now reports **54 of 57** formal environments with
  existing mappings, **3 unmapped**, and **7 revised** statements requiring
  semantic review. Default exit success means the audit was generated. The
  `--require-complete` gate fails until those obligations are resolved. No new
  Lean build or new kernel-checked proof is claimed.

## Reading the exploratory full run

The independent-Gaussian interval covered in approximately 94.6% of 1,000
replications, with Monte Carlo uncertainty spanning 95%. Correlated tap errors,
biased readings and an invalid memory floor degraded coverage substantially.
Heavy-tailed readings did not fail in this particular configuration; that is not
a general robustness theorem. The synthetic control comparisons do not establish
universal superiority over volatility controls. All regimes and negative results
are retained.

The committed local-run manifest records the pre-commit checkout and source
hashes. It is an executed development snapshot, not a run of a clean released
commit. Colab runs after publication will record the actual checked-out commit.
