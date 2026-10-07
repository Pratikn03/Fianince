# Machine Markets paper revision — October 6, 2026

Review candidate, with open scientific gates. Original root PDFs are preserved. Read the root `REVISED_PLAN.md`, `GAPS.md`, `FULL_48_PAGE_AUDIT.md` and `RESULTS_REANALYSIS.md` first. The full candidate retains all original study questions and appends actual methods/results and a disposition of every original page.

## Files

- `baseline/` and `baseline_manifest.json`: preserved source/PDF authority.
- `results/`: fresh local computations, explicitly scoped; no historical output replacement.
- `existing_evidence_search.json`: bounded text/archive inventory, hashes and candidate leads. A text match is not verified lineage.
- `search_locations.json`, `agent_candidate_paths.txt`: location and agent scratch discovery.
- `claim_evidence_map.json`: fresh result-to-generator map; the comprehensive original-claim acceptance ledger remains open.
- `original_page_disposition.csv`: all48 original pages.
- `full_scope_appendix.tex`: generated methods, full ledgers, induced-gain proof and page map.
- `logs/`, `qa/`, `delivery_receipt.json`: compiler/test/render/geometry/visual and hash receipts.

## Reproduction

From the repository root, use `/opt/homebrew/bin/python3.11`. The named raw local files are required. These commands do not download data or train new learners. Do not infer that another dated dataset substitutes for the original sample.

```sh
/opt/homebrew/bin/python3.11 research_extension/paper_revision_20261006/verify_raw_inputs.py
/opt/homebrew/bin/python3.11 research_extension/paper_revision_20261006/revise_evidence.py
/opt/homebrew/bin/python3.11 research_extension/paper_revision_20261006/diagnostics.py
/opt/homebrew/bin/python3.11 research_extension/paper_revision_20261006/holdout_reanalysis.py
/opt/homebrew/bin/python3.11 research_extension/paper_revision_20261006/sampling_grid.py
/opt/homebrew/bin/python3.11 research_extension/paper_revision_20261006/recovered_timing_check.py
/opt/homebrew/bin/python3.11 -m pytest -o addopts='' -q research_extension/paper_revision_20261006/test_revision_evidence.py
```

The recovered timing script changes only the output path from the agent scratch original. `write_revision_reports.py` creates the initial reports; the root plan/gap register also contains delivery updates. Preserve those updates when regenerating. Reproduction can take minutes and depends on local raw-data availability. Some revision output files are rewritten by their own generators; copy a prior revision result if comparison is needed. Historical `results/provenance/` files are not overwritten.

Run `build_revised.sh` from this folder or any working directory to regenerate appendices, guarded source and isolated PDF. The source guard rejects unrelated concurrent manuscript changes; do not bypass it. The original freeze/submission-bundle PDFs are not replaced. The review PDF is not a declaration of causal validity, authenticated provider identity, original raw Binance replication or external mathematical review.

New large datasets, new complex learning-agent experiments and extra market modules stay deferred until existing evidence is reliable. Existing artifacts remain in scope for recovery. T9 access returned;458 research files were inventoried and small outputs read/hashed. The original one-second directory is empty and located2025 archives are another sample. Large data-archive payload verification is not claimed. See the T9 inventory/archive audit.
