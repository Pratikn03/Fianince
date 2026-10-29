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
  This local check did not exercise the hosted Google Colab service; the later author-returned run is documented below. A separate Jupyter-kernel
  startup was blocked by this environment's socket restrictions; cell execution
  was therefore checked directly in a shared Python namespace.
* Optional real-data code was tested with synthetic CSV fixtures, including
  future-feature invariance and invalid timestamp rejection. No new public-data
  result, causal identification, GPU result or prospective study is claimed.
* Updated PDF delivery: all six working/journal/synthesis/thesis variants were rebuilt from the corrected sources. Oversized result-map tables, the all-tests table, the forest figure and long thesis formulas were repaired. The delivered builds have no undefined references, overfull boxes or oversized-float warnings.
* The author returned a completed full notebook archive from the pinned published source. Ten exported-file hashes and four analytical source modules were verified. E1/E2/E3/E4/E6 completed; no CSV was supplied and E5/E7 were not run. A development appendix in the PDFs reports the outcomes as a same-code seeded execution reproduction, not independent scientific validation. See `results/colab_return_20261029/verification.json`.
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
