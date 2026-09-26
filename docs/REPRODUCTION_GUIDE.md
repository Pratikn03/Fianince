# Reproduction and Verification Guide

## A. Preserve the reference release
Unzip into a short path. Keep an untouched copy. Use a fresh working copy for experimental
scripts because some intentionally write to their own `results/` directories. Checksums cover
the distributed state, not newly generated outputs. Do not delete the reference outputs merely
to satisfy a changed checksum. No outside service, model API or financial account is required.

The calculation environment recorded in the releases is Python 3.12/3.13. The master tests were
run with the runtime versions in `requirements-runtime.txt`. Other versions/platforms may yield
floating-point differences and require explicit investigation, not an automatic assertion of equality.

## B. Verify the archive contents
From the master root (standard library only):
```bash
python tools/verify_master.py
```
It verifies every checksum and reports missing, changed and unlisted files. A SHA-256 match is
an integrity check, not authentication of an untrusted issuer or a proof of scientific validity.
`verification/SOURCE_ARCHIVE_MEMBERS.csv` maps every original archive member to its preserved path.

## C. Install and test
```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell alternative:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements-runtime.txt

# 1. Run all native test suites (104 tests):
python tools/run_all_tests.py

# 2. Run master revision pytest suite (88 tests):
PYTHONPATH=. pytest tests/ research_extension/tests/ reference_directory/test_mathematical_supplement.py

# 3. Run standalone zero-dependency verifier (24 gates):
python independent_verifier/verifier.py

# 4. Run mathematical supplement numerical checks:
python reference_directory/run_checks.py
```
The test launcher runs all native suites in separate processes (24 + 29 + 23 + 22 = 98 scientific tests),
then six package-verifier tests, followed by the revision, verifier, and mathematical suites (220 tests total: 104 native + 88 pytest + 24 verifier gates + 4 supplement verification suites).

## D. Rebuild PDFs
The package provides three synchronized PDF documents:
1. `paper/Machine_Markets_Final_Integrated_Paper.pdf` (68-page main manuscript)
2. `paper/Machine_Markets_Mathematical_Supplement.pdf` (25-page mathematical supplement)
3. `Machine_Markets_Combined_Master.pdf` (93-page combined master document)

To rebuild from LaTeX sources:
```bash
# Main Manuscript:
pdflatex -interaction=nonstopmode -output-directory=paper paper/Machine_Markets_Final_Integrated_Paper.tex
pdflatex -interaction=nonstopmode -output-directory=paper paper/Machine_Markets_Final_Integrated_Paper.tex

# Mathematical Supplement:
pdflatex -interaction=nonstopmode -output-directory=paper paper/Machine_Markets_Mathematical_Supplement.tex
pdflatex -interaction=nonstopmode -output-directory=paper paper/Machine_Markets_Mathematical_Supplement.tex

# Unite to 92-page Combined Master:
pdfunite paper/Machine_Markets_Final_Integrated_Paper.pdf paper/Machine_Markets_Mathematical_Supplement.pdf paper/Machine_Markets_Combined_Master.pdf
cp paper/Machine_Markets_Combined_Master.pdf Machine_Markets_Combined_Master.pdf
```
Both documents compile with **0 overfull `\hbox` warnings, 0 undefined references, and 0 undefined citations**.

## E. Original algebra
```bash
python studies/observable_stress_tests/provenance/verify_original_algebra.py
```
The output contains 625 scalar and 250 small-network checks, not a market validation experiment.

## F. Reproduce a complete study
Use each study's README for authoritative commands. Change to that study's root before executing
its commands; do not import all four `src/` trees into a common process.

### Hidden Slow Learners
Root: `studies/hidden_slow_learners/`.
Run `scripts/run_experiments.py` using its documented configuration/output arguments, then the exact
and measurement verifiers. The original README supplies the complete command sequence and
figure/report regeneration. Its complete saved decisions are under `results/decisions.csv`.

### Full-horizon audit
Root: `studies/full_horizon_audit/`.
For an independent output directory:
```bash
python scripts/reproduce_clean.py --output ../full_horizon_fresh_run --datasets 21600 --workers 1
```
A smaller `--datasets 100` run is a smoke test, not a reproduction of the headline totals.
The full audit/sensitivity/alternate-solver sequence is in that study's README.

### Observable stress tests
Root: `studies/observable_stress_tests/`.
```bash
python run_study.py --out ../observable_primary_fresh_run
python verify_release.py
```
`verify_release.py` verifies the delivered data; its source specifies which files it reads.
`run_extensions.py` writes within the study folder and should only run on a working copy.

### Audited constraints (v0.5 study)
Root: `studies/audited_constraints/` in a fresh copied study folder.
```bash
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
python scripts/run_linear.py
python scripts/run_finance.py --max-new 8
python scripts/run_finance.py --max-new 8
python scripts/run_finance.py --max-new 8
python scripts/run_followup.py
python scripts/run_controls.py
python scripts/measure_tail.py
python scripts/prepare_replication.py
python replication/verify_without_project_imports.py
```

### Master Revision Studies (v2.0)
Root: `research_extension/mm_revision/studies/`
```bash
# 1. Broadened 120-cell Comparator Grid:
python -m research_extension.mm_revision.studies.run_broadened_comparator_grid

# 2. Conic Informativeness Contraction Curve:
python -m research_extension.mm_revision.studies.conic_informativeness_curve

# 3. Output-Error Misspecification Diagnostic (C1-C4):
python -m research_extension.mm_revision.studies.output_error_misspecification_diagnostic

# 4. Funded Scenario-Risk Smooth Surface:
python -m research_extension.mm_revision.studies.funded_smooth_surface

# 5. Binance Robustness Audit:
python -m research_extension.mm_revision.studies.binance_robustness
```

## G. What was rerun for the master package
Fresh: all 177 automated tests (104 native, 37 revision, 15 research extension, 21 mathematical supplement), the 875 original algebra checks, the standalone zero-dependency verifier (24 gates), and all newly introduced computational experiments (conic contraction sweep, C1–C4 output-error diagnostics, smooth funded risk surface, Binance sensitivity). Source archives were checked member by member.
Historical: full simulation reruns documented in each study's original release reports remain unchanged and clearly versioned.

## H. External reproduction is a distinct activity
Use `studies/audited_constraints/replication/EXTERNAL_REPLICATION.md`. Independently written code,
a separate person and a documented external report are required before saying that outside
replication occurred. All currently released verification is internal.
