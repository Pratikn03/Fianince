# Reproduction and verification

## A. Preserve the reference release
Unzip into a short path. Keep an untouched copy. Use a fresh working copy for experimental
scripts because some intentionally write to their own `results/` directories. Checksums cover
the distributed state, not newly generated outputs. Do not delete the reference outputs merely
to satisfy a changed checksum. No outside service, model API or financial account is required.

The calculation environment recorded in the releases is Python 3.13.5. The master tests were
run with the runtime versions in `requirements-runtime.txt`. Other versions/platforms may yield
floating-point differences and require explicit investigation, not an automatic assertion of equality.

## B. Verify the archive contents
From the master root (standard library only):
```bash
python tools/verify_master.py --strict
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
python tools/run_all_tests.py
```
The launcher runs four suites in separate processes (24 + 29 + 23 + 22 = 98 scientific tests),
then six package-verifier tests. Logs go to a temporary directory printed by the launcher.
To retain them elsewhere:
```bash
python tools/run_all_tests.py --log-dir ../machine_markets_test_logs
```
A `.venv` inside the reference directory will be reported as unlisted by strict checksum checking;
verify before creating it, or create the environment outside the package. No study files need change.

## D. Rebuild the main PDF
A precompiled PDF is supplied. Rebuilding additionally requires a TeX distribution with the
packages listed in `paper/README.md`:
```bash
python tools/build_paper.py --output ../Machine_Markets_Rebuilt.pdf
```
The helper uses a temporary build directory and refuses to overwrite an existing output.
It runs three LaTeX passes for the table of contents and references. PDF metadata can differ
between builds; a new PDF's byte hash is not an experimental equality criterion.

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

### Audited constraints (current study)
Root: `studies/audited_constraints/` in a fresh copied study folder.
```bash
# Set these variables appropriately for your shell to limit BLAS threads:
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
**Checkpoint warning:** delete only the working copy's `results/finance_checkpoints/` before a
fresh financial rerun, or start from `replication/clean_source_snapshot.zip`. Otherwise the runner
will reuse completed settings. It rejects stale source hashes. Three eight-setting invocations
compute all 24 settings only when the working directory starts without completed checkpoints.
The clean source snapshot is computational, not a complete paper/provenance bundle.

Compare the new study directory against the preserved study:
```bash
python scripts/compare_release.py /path/to/reference_study /path/to/fresh_study
```
The study README explains which arrays/CSVs are compared and which runtime metadata is excluded.

## G. What was rerun for the master package
Fresh: all 98 scientific tests, six packaging tests, the 875 original algebra checks, and the current
standalone verifier (4,320 regressions, 2,880 tail intervals, 2,880 binomial intervals, 500 fill checks,
24 public reconstructions and 64 example ledgers). Source archives were checked member by member.
Historical: full simulation reruns documented in each study's original release reports. They were
not rerun simply to assemble this package. Those files remain unchanged and clearly versioned.

## H. External reproduction is a distinct activity
Use `studies/audited_constraints/replication/EXTERNAL_REPLICATION.md`. Independently written code,
a separate person and a documented external report are required before saying that outside
replication occurred. All currently released verification is internal.
