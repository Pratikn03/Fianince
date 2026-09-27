# Second corrective revision: statistical and mathematical alignment

This is a bounded correction of the current integrated paper, not a new
confirmatory training experiment or a claim to a 9.5/10 rating. The current
title and manuscript identity are preserved. `main` and historical experiment
files are not rewritten.

## Authoritative locations

- Main source/PDF: `paper/Machine_Markets_Final_Integrated_Paper.{tex,pdf}`.
- Supplement: `paper/Machine_Markets_Mathematical_Supplement.{tex,pdf}`.
- Accepted corrective runs: `research_extension/outputs/statistical_repair_20260926/verified/`.
- Generated paper blocks: `verified/artifacts/` beneath that output root.
- New receipt and integrity seal: `verified/verification/`, when the final
  verification command completes. An absent receipt means verification is pending.
- Protocol: `STATISTICAL_REPAIR_PROTOCOL.md`; exact claim links:
  `statistical_claims.json`; reviewer findings: `STATISTICAL_REPAIR_REVIEW.md`.
- Earlier complete and interrupted attempts outside `verified/` remain visible
  but are not the paper's final corrective evidence. `PRE_REVIEW_ATTEMPTS.md`
  and `final/SUPERSEDED.md` explain the stopped runs.

## What this revision changes

1. Corrects the price-response index, honors optimizer failure, retains all
   missing/unbounded intervals and makes summary denominators explicit.
2. Separates profile and Gauss--Newton sandwich calculations; removes invented
   standard errors and unavailable-fallback coverage. The approximation still
   lacks a general misspecification-robust covariance guarantee.
3. Separates known-covariance chi-square calibration from independently
   estimated-covariance F calibration. Conic dual/cut bookkeeping is repaired,
   but full outward constraint construction remains unverified. Numerical
   candidate labels are not certified decisions.
4. Corrects rank/scale degeneracies, impulse normalization and the distinction
   between recovering a common rate and jointly recovering labeled allocations.
5. Exposes the later funded scenario's actual unstable transition matrix,
   fixed-equity capacity changes, reversible fills and non-liquidating margin
   counts. It is not the original stable funded-engine counterexample.
6. Generates revised tables/figures directly from the new output files and
   checks literal source alignment against those generated blocks.

## Reproduction and acceptance

Use Python 3.11. Every study destination must be new. No network or paid compute
is required. Set `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, and
`VECLIB_MAXIMUM_THREADS=1` for these local numerical runs.

```
python3.11 -m research_extension.evidence_repair.statistical_repair --stage grid --workers 4 --output-dir NEW/grid
```

Repeat with stages `sweep_known`, `sweep_estimated`, `calibration`, `diagnostic`,
and `funded`, each using its own new directory. Then:

```
python3.11 -m research_extension.evidence_repair.render_statistical_artifacts --results-dir NEW --output-dir NEW/artifacts
python3.11 -m research_extension.evidence_repair.verify_statistical_repair
python3.11 -m pytest -q tests research_extension/tests reference_directory/test_mathematical_supplement.py
python3.11 tools/run_all_tests.py --log-dir NEW/native-tests
python3.11 reference_directory/run_checks.py
```

The renderer does not silently edit the manuscript. Its self-contained TeX
blocks are integrated into the selected source, then verified by exact text
binding. The recorder can run fresh checks, compare a clean-copy execution and
PDF extraction, and seal the listed current files:

```
python3.11 -m research_extension.evidence_repair.verify_statistical_repair --clean-root CLEAN --output-dir research_extension/outputs/statistical_repair_20260926/verified/verification
```

Clean copy here means a fresh `git archive HEAD` export plus explicit current
corrective sources and required preceding artifacts. Shallow local Git metadata
was added after a provenance-dependent CLI test failed without HEAD; no study
source or output was altered to resolve that environment requirement. It is not a published
corrective commit or external replication. Full numerical results are compared,
excluding only named runtime fields; PDF extracted text/layout is compared,
not asserted pixel- or byte-identical.

The bare root `pytest` command currently collects study-local `src` imports and
archived duplicate modules into one process and fails collection. The receipt
records that failure and the separate-process native study suites. The original
strict release seal also fails as expected after revision; it is preserved,
not silently resealed. A new scoped manifest does not repair historical files
or establish the completeness of unlisted evidence.

## Completed corrective analyses

The six accepted analyses reproduce numerically in the clean copy, excluding
only the declared timing fields. The current integrated document has 62 pages;
the mathematical supplement has 26. This is not an independent replication.

- Grid: 600 panels. Recurrence and interval deconvolution each contain truth in
  597/600, with no issued labels. Conic numerical bounds contain truth in
  600/600, including 128 unbounded intervals, and issue no candidate labels.
  No conic classification is certified.
- Output-error grid intervals contain truth in 193/600, with 204 wrong labels
  among 438 issued and unavailable inference on 31 panels. The old 47.7% and
  57.1% comparisons are superseded, not reused as evidence.
- Known and estimated response-region pivots cover 18,975/20,000 and
  19,000/20,000 draws, respectively. These are Gaussian/Wishart checks only.
- Separate covariance sweeps contain 300 panels each. Every solved sweep panel
  reaches the cut limit; endpoints remain finite-cut numerical candidates.
- The 202-attempt diagnostic distinguishes two deterministic cases from two
  groups of 100 noisy panels. Matched noisy profile/GN containment is 91/100
  and 93/100; both misspecified noisy intervals contain truth in 0/100.
- The 100-tape funded rerun retains the earlier trajectories and reports the
  actual unstable transition (spectral radius about 1.07409), fixed initial
  equity, reversible constraint-hit fills and separate paired contrasts.

## Next scientific gates

The numerical conic enclosure remains deliberately fail-closed. Formal outward
arithmetic, stronger matched economic experiments, independent human review,
priority/novelty, real execution calibration, author permissions and publication
are not completed by this correction. Existing negative findings remain.
