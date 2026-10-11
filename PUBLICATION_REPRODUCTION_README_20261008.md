# Current Machine Markets review reproduction

This package is a local scientific-review candidate. It contains the current sources, code, protocols, numerical outputs, receipts and PDFs. It does not certify novelty, causal identification, real financial calibration, independent review or publication/reuse permissions. Raw data, private credentials, signed download tokens and unrelated third-party Fairdata frontend/backend source copies are excluded.

## Exact authority

The current main source is `paper/Machine_Markets_JF_Submission.tex`; its four imported central-result bodies are under `research_extension/gap_closure_20261006/publication_completion/`. The root original PDF names remain untouched. Current delivery hashes/pages are in `publication_delivery_receipt.json` under that directory. The local review ZIP path, hash, file count and content manifest are in `publication_package_receipt.json`.

The package records an uncommitted working snapshot. Git HEAD is context, not a claim that the edits are committed or published. No push or external upload was performed.

## Environment and local checks

Use Python3.11 with the exact versions in `review_environment.json`. NumPy, pandas, SciPy, SymPy, matplotlib, Pillow and pytest are used. PyArrow21 is needed only to repeat primary January conversion authentication; the existing isolated copy is on T9 and was not installed into the main environment. Poppler and pdfLaTeX are used for PDF exports/QA. Native standalone compilation has also succeeded in the Codex LaTeX editor.

From the extracted package/repository root:

```sh
python3.11 research_extension/gap_closure_20261006/publication_completion/run_review_checks.py
python3.11 research_extension/gap_closure_20261006/publication_completion/verify_evidence_supplement.py
python3.11 research_extension/gap_closure_20261006/publication_completion/build_publication_pdfs.py
```

The first command runs the87-check suite. The second verifies all10 current-supplement tables,233 rows and1,515 cells against named outputs, plus specific main prose and maintained covariance identities. The third exports the same saved sources and preserves original root freeze hashes. PDF binary hashes may vary across TeX distributions/timestamps; compare the saved source, values and rendering rather than assuming cross-environment binary identity.

## Data-dependent reproduction

The existing raw/cache files are required for these commands. They are not bundled merely to bypass provider rights. `required_input_manifest.json` lists local logical/backing paths, SHA256 and source/licence status. The BTC logical CSV now points to a verified T9 copy. Keep T9 mounted for backing files, primary source comparisons, January forecast cache and QA; update explicit cache paths if moved.

```sh
python3.11 research_extension/gap_closure_20261006/publication_completion/verify_current_empirical.py
python3.11 research_extension/gap_closure_20261006/input_gate/verify_recorded_table.py
python3.11 research_extension/gap_closure_20261006/regime_model/verify_current_repairs.py
python3.11 research_extension/gap_closure_20261006/publication_completion/verify_january_forecasts.py
```

These verify named independent arithmetic/refit chains. They do not turn date-Student/HAC references into guaranteed confidence coverage or authenticate unobserved market execution primitives.

Full existing-sample recomputation commands, where desired:

```sh
python3.11 research_extension/gap_closure_20261006/cross_venue/reproduce_original_panel.py
python3.11 research_extension/gap_closure_20261006/publication_completion/recompute_panel_lags.py
python3.11 research_extension/gap_closure_20261006/publication_completion/calendar_inference_sensitivity.py
python3.11 research_extension/gap_closure_20261006/publication_completion/audit_recorder_bin_completeness.py
python3.11 research_extension/gap_closure_20261006/publication_completion/compute_remaining_diagnostics.py
python3.11 research_extension/gap_closure_20261006/publication_completion/audit_funded_accounting.py
python3.11 research_extension/gap_closure_20261006/publication_completion/reconstruct_january_forecasts.py
```

These use existing samples/protocols, with declared retrospective choices; no new large dataset, complex policy training or market module is requested. Original-panel archive locations and checksums are in the preserved restoration manifests. Primary authenticity scripts may acquire large *existing-source comparison files* and should use a configured external output drive; their receipts already document the completed checks.

`rebuild_current_empirical.py` is a historical frozen recipe that starts from `baseline_current_source.tex`. **Do not run it on a subsequently edited manuscript without preserving those edits.** Current numerical displays, source/ledger hashes and the finalizer are supplied; the finalizer's idempotence was verified. Source edits should be made in the current main or standalone files, not by replaying an older manuscript updater.

## PDF QA

```sh
python3.11 research_extension/gap_closure_20261006/publication_completion/render_publication_qa.py /Volumes/T9/machine_markets_data/reviewer_qa
```

This renders every delivered page and creates contact sheets. Detailed visual inspection is a separate action; rendering alone is not visual approval. The final delivery receipt states the actual inspection scope. Original freezes and historical unfavorable results are retained.

## Open dependencies

Read `PUBLICATION_WORK_STATUS_20261008.md`, `GAPS.md`, the current acceptance matrix and specialist-review packet. Primary equity archive/transformation, January venue/contract metadata, derivative rights, substantive uncertainty/calibration, independent novelty/proof review and target-journal submission checks remain explicit gates. No all-gap,9+ or submission-ready declaration is made.
