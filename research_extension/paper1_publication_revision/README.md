# Paper 1 revised research package

This is the 14 November 2026 author-review revision of **Observationally Equivalent Algorithms: What Prices Reveal About Trader Populations, and What Supervisors Need**. Read `pdfs/Paper1_ssrn_complete.pdf` for the combined paper, `pdfs/Paper1_Research_Audit.pdf` for the rating and 59-gap audit, and `P1F_candidate_amendment.md` for the unregistered empirical candidate.

The audit rates the supplied draft 68/100, this revision 83/100, and the conditional research ceiling 92/100. These are editorial judgments, not acceptance probabilities. The manuscript adds proofs and repairs claims, but does not claim completed market evidence, identification beyond the stated pooling rank certificate, full statistical mechanization, or independent author/referee approval.

## Provenance and contents

- `source/` is an isolated snapshot of the relevant sources at repository revision `9b7043f2a0c469b806fe2e30812ef2005ffc1f89`, plus explicitly named revision artifacts and regenerated numerical outputs. It is not the entire repository.
- `source/ceiling_suite/papers/paper1_note/paper1_ssrn.tex` is the unchanged baseline. `paper1_revised.tex` is the generated revision. `manuscript_changes.patch` compares them.
- `revision_blocks.tex`, `integrate_incoming.py` and `build_revision.py` contain the new manuscript content and exact assembly steps.
- `formal/` contains the larger pinned Lean project, its audit, and the ten new deterministic revision lemmas. `formal_core/` contains the smaller independent core project. Neither directory includes dependency caches.
- `historical_reviews/` preserves earlier review notes; the current assessment is `Research_Audit.md`.
- `validation/` contains test programs, raw logs, result JSON, proof receipts, and PDF checks. The complete calibration grid includes failed diagnostics. No failed cell is removed or retuned.
- `candidate_p1f_executor.py` is an **unregistered offline candidate**. `prepare_candidate.py` regenerates it from the frozen registered executor. Live execution through `run_all` is disabled. Do not substitute it into a registered notebook or reset a run counter.
- `P1F_A1_Schema_Review_Only.ipynb` repairs the registered notebook schema in a separate review copy. Every code cell is blocked; it was schema-validated, not executed as a study.
- Registered specifications, executors, notebooks, hashes and counters are retained under `source/ceiling_suite/p1_empirics/`. The A1 replacement counter remains unopened. The original void run is preserved.
- `MANIFEST.sha256` records package-file hashes. It excludes itself. The external ZIP checksum is recorded alongside the delivered ZIP.

## Python environment and offline checks

Python 3.12 was used. Exact package versions are in `requirements-validation.txt` and `validation/python_environment.json`. A TeX distribution, Pandoc, Poppler (`pdftoppm`), and Lean's `elan`/`lake` are separate system dependencies.

From the extracted package directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-validation.txt
.venv/bin/python prepare_candidate.py
.venv/bin/python prepare_review_notebook.py
.venv/bin/python -m pytest validation/test_revision.py validation/test_incoming.py validation/test_notebook_candidate.py -q
.venv/bin/python validation/high_precision_information.py
.venv/bin/python validation/forecast_check.py
.venv/bin/python validation/pooling_certificate_check.py
.venv/bin/python validation/intervention_figure.py
.venv/bin/python validation/synthetic_pipeline_check.py
.venv/bin/python validation/calibration_grid.py
.venv/bin/python source/research_extension/theorem_checks/run_all_checks.py --slow
```

The last command's inherited global-search assertion reads an archived truncated extended-search result. To examine **fresh full extended-search output**, also run from `source/research_extension/cross_market/` with the same Python environment:

```sh
../../../.venv/bin/python global_fibres_extended.py
```

Then return to the package root and run:

```sh
.venv/bin/python validation/validate_fresh_global_search.py
```

All listed candidate tests use synthetic inputs. Do not run other inherited empirical notebooks as part of this reproduction. The 707-pass/15-skip repository-suite log is a check of the broader working repository, not an additional self-contained suite in this smaller package. The audit records that distinction.

The calibration script exits normally after recording both passing and failing diagnostics. Read `all_diagnostic_criteria_pass` in its JSON; a completed run is not a passing statistical validation. Population-oracle gains and conditional fitted-predictor gains are different estimands. The new projection proposition explains the distinction; it does not automatically repair confidence coverage.

## Lean reproduction

In `formal/`:

```sh
lake exe cache get
lake build
lake env lean AxiomAudit.lean
lake env lean PublicationRevision.lean
```

The first command downloads the pinned Mathlib dependency cache. The audit checks 1,235 named declarations and scans 3,011 project constants. The new revision file checks ten deterministic lemmas separately. Statistical likelihood arguments, Pinsker's theorem, Gaussian concentration, the conditional projection identity, full inverse-map argument, uniform Gaussian log-loss theorem, and the AR risk expansion remain paper-level or cited ingredients as stated in the supplement.

In `formal_core/`:

```sh
lake build
lake env lean AxiomAudit.lean
```

That independent audit covers 439 theorems. Counts from the two projects should not be added to measure manuscript coverage.

## Rebuild the PDFs

Inside the full repository, the canonical command is `.venv/bin/python ceiling_suite/papers/paper1_note/build_ssrn.py --pdf`. It generates the reconciled source, compiles the companion and main paper, checks the final LaTeX log, and writes the current reading copies under `pdf_delivered/`. The older `ssrn_parts.tex` is a preserved incoming version, not the active source. The standalone commands below rebuild the extracted revision package without the rest of the repository.

From the package root, after the numerical JSON inputs and intervention figure are present:

```sh
.venv/bin/python build_revision.py
```

In `source/ceiling_suite/papers/paper1_note/`, build the companion first, then the revised paper:

```sh
pdflatex -interaction=nonstopmode -halt-on-error paper1b_companion.tex
pdflatex -interaction=nonstopmode -halt-on-error paper1b_companion.tex
pdflatex -interaction=nonstopmode -halt-on-error paper1_revised.tex
pdflatex -interaction=nonstopmode -halt-on-error paper1_revised.tex
pdflatex -interaction=nonstopmode -halt-on-error paper1_revised.tex
```

Back in the package root:

```sh
.venv/bin/python prepare_pdf_delivery.py --output-dir pdfs
pandoc Research_Audit.md --standalone --pdf-engine=pdflatex -V fontfamily=lmodern -V fontsize=10pt -V geometry:margin=0.75in -V colorlinks=true -o pdfs/Paper1_Research_Audit.pdf
```

Keep `paper1b_companion.pdf` beside the combined PDF for external companion links. The combined PDF preserves main-to-supplement references; the split reading copies may not retain every cross-part link. Source hashes provide the exact delivered content even if a different TeX installation changes pagination or PDF bytes.

## Remaining research obligations

See the audit's acceptance tests, not a calendar schedule. They include a uniform feasible-forecast result, attainability in the same observation experiment, pooling results beyond the proved rank certificate, an intervention design with a defensible counterfactual, report-cost and decision-loss calibration, an estimand-specific empirical validation, measurement assumptions, and independent proof review. No favorable empirical outcome is promised or required; negative results must be retained.

## Canonical build, 20 November 2026

`python ceiling_suite/papers/paper1_note/build_ssrn.py --pdf` now runs, in order:
1. `build_note.py`, which regenerates `paper1_focus.tex` from `paper1_core` (this carries the 18 November inventory-equilibrium section, Section 4);
2. `make_base.py`, which applies the 15 November SSRN blocks (`base_ssrn_parts_20261115.tex`) to that focus text;
3. `build_revision.py` and `integrate_incoming.py`, which apply the scoped revision and the later 15 November results (Theorems 5.5, 5.7, 6.1–6.3).

Changes on 20 November:
- a new abstract and an equilibrium paragraph in the introduction;
- the 18 November main-text equilibrium section is kept;
- two citations that could not be verified were removed or replaced (a 2026 arXiv preprint on ESPRIT stability, and a 2026 IRFA article, replaced by Frino, Johnstone and Zheng 2010); Roy and Kailath (1989) and Hua and Sarkar (1990) are cited for the matrix-pencil identity;
- the Nash "guaranteed unique" overclaim now reads as a grid evaluation;
- positivity of h(r) in the equilibrium boundary now states its condition;
- the evidence paragraph gives the dated status of P1F and H1;
- the AI-use declaration names the results whose proofs are still under the authors' check.

The 142-page public-data revision of 16 November (Supplement S31) is archived in `research_extension/paper1_public_data_study_20261116/` and is not part of the canonical Paper 1. Its gate study belongs with Paper 2, and its address study does not test a Paper 1 result.
