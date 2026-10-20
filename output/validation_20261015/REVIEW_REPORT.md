# Local validation and coverage reconciliation — October 15, 2026

Canonical source: `paper/Machine_Markets_JF_Submission.tex`.
Canonical PDF: `paper/Machine_Markets_JF_Submission.pdf` (117 pages).
Base Git commit: `004931b1e174cc7b6e158a654a02e29aaf990d5b`. This package includes uncommitted local revisions; nothing was committed or pushed.

## Validation

- Python 3.11 (same major/minor version as CI), macOS: 664 passed, 12 skipped. See `pytest_python311.log` for every skip. Linux CI has not been rerun on this local revision.
- Ruff and `git diff --check`: pass.
- Lean 4.34.1, pinned Mathlib `d13f23b723b8a846827a245b89c10fc7d3f11612`: build and strict axiom audit pass, 324 named declarations. Only standard foundations `propext`, `Classical.choice`, `Quot.sound` observed.
- Independent oracle/falsification checks: pass.
- Full-domain outward-rounded certificate: pass; lower bound 64.74290629918269 USDT exceeds 64.7423, all 1,800 angular intervals and declared tail regions covered.
- Manuscript compiled twice; the changed coverage pages were rendered and visually checked. Existing overfull-box warnings elsewhere in the manuscript remain; this is not a full typographic redesign.

## Reconciled claim boundaries

- 20 existing kernel-result mappings, 2 kernel cores with external dependencies (S13/S20), and S21 subresults with an open estimator-level obligation. Mapping counts are not an independent certification of semantic equivalence for all statements.
- S13: the general-dimensional Spijker upper factor remains an explicit hypothesis. The stated lower bound and two-dimensional Jordan core are kernel checked.
- S20: Lean checks the symbolic core and worst-interval rational certificate; the complete 1,800-interval Decimal sweep remains an external executable certificate.
- S21: the Vandermonde moment perturbation coefficients use the true rates. The proof does not cover errors in estimated poles, root selection or a uniform finite-sample guarantee for the fully parameter-blind estimator. Local conditioning and finite-configuration simulation results retain that scope.
- Removed the blanket 23/23 complete-formalization claim from the current manuscript and current coverage summary; the verification receipt now explicitly records incomplete manuscript-level formalization.
- The draft CLAIMS.yaml had mismatched IDs and references. It is now generated from the checked registry. The earlier draft is retained as `CLAIMS_before_reconciliation.yaml` for provenance, not as current evidence.
- Updated regression checks retain numerical tests and enforce the external/estimator boundaries instead of requiring all statements to be labelled FULL.

## Environment and limitations

The current Lean runtime and shared Mathlib cache previously pointed to an unmounted T9 volume. A local pinned runtime was restored; the previous project link is preserved at `tmp/t9_runtime_link`. No external-drive data was modified.

Skipped raw-data and optional Torch tests are not validated by this local run. No new empirical identification, data-provenance closure, novelty claim or uniform blind-estimator proof follows from these checks. Historical delivery receipts and earlier PDFs are not the canonical output of this reconciliation.

The ZIP is a review overlay against the base commit, not a standalone raw-data distribution. It contains the current source/proof/PDF inputs, changed files, a binary Git patch, validation evidence, and SHA256 manifests. Restore a checkout at the base commit before applying `local_changes.patch`; copy `snapshot/` files as needed. Install declared dependencies and retrieve pinned Mathlib independently. The test datasets omitted from the repository are also omitted from this package.
