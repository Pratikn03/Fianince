# Machine Markets: Audited Tails, Observation Budgets, and Binding Constraints

Version 0.5 — research-development release, 18 September 2026.

## Read first
The integrated paper (47 pages) is `paper/Machine_Markets_Audited_Integrated_Paper.pdf` (self-contained TeX alongside it). It preserves v0.4 and adds three distinct claims:
- A memory tail bound conditional on truthful, complete implementation/configuration disclosure.
- Classical terminal-row confidence intervals conditional on public rates, an exact reset and exact observed prices.
- Finite-horizon event-probability intervals for a constrained synthetic market; **not asymptotic stability**.

No trained neural agents, exchange calibration, live trades, real customer records, authenticated external source audit, external replication, or established scientific priority are claimed. A self-issued manifest can lie. All outside-replication fields remain pending.

## Main findings
Endpoint diversity increases definite decisions at 32/128 episodes in a held-out synthetic comparison, but loses at 512. The smaller-budget benefit includes errors: 2 of 240 panels at 32 episodes and 1 at 128. The original repeated small round trips perform worse than a single impulse at equal within-window gross volume; energy and inventory differ.

Binding cash, inventory, leverage and dealer limits are implemented. A preloaded dealer can halt even for a locally stable isolated signal-feedback model. The primary event-probability settings are easy near-zero/near-one cases; their high decisiveness does not establish general small-budget practicality.

## Information contracts and experimental status
`docs/PROTOCOL.md` precedes primary execution in this session but is not externally preregistered. `docs/EXPLORATORY_AND_CONFIRMATION.md` records later pilots and the fresh-seed endpoint confirmation. Public source disclosure is additional information relative to v0.4, so comparisons across versions are NOT equal-information estimator contests.

## Reproduce in a clean copy
Python 3.11+ with matching supported package versions is expected; this execution used Python 3.13 (see environment.json). CPU only. Install from requirements.txt, then:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python -m pytest -q tests
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

The financial runner checkpoints completed settings and rejects stale source hashes. A fresh rerun requires a fresh copy without results/finance_checkpoints; otherwise completed settings are intentionally reused. Never treat a checkpoint-only invocation as a full independent rerun. Generator seeds and all terminal inference rows are released. Selected full observed price trajectories and financial ledgers are included; others regenerate from seeds. No network or model API is used by experiments.

Compile paper (optional; PDF already supplied):
```bash
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=paper paper/Machine_Markets_Audited_Integrated_Paper.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=paper paper/Machine_Markets_Audited_Integrated_Paper.tex
```

## Folder guide
- `src/`: source contract, observable-only inference, linear experiments, funded settlement.
- `scripts/`: primary/follow-up studies, controls, tail reanalysis, artifact builder.
- `tests/`: 24 new tests. Deliberately failing development-stage logs document test-first checks; final log is green.
- `data/`: regression rows, public-price examples, per-episode financial outcomes, full sample ledgers.
- `results/`: every primary/confirmation/control row, summaries, source-audit failures, statistical calibration and verification records.
- `replication/`: verifier with no project imports, public challenges, separately stored answers, external reviewer form.
- `provenance/`: unchanged v0.4 integrated paper and its original complete package.
- `docs/`: protocols, contribution/assumption ledger, data dictionary and primary literature notes.

## Counts are not all independent
The linear primary has 645,120 episode rows. The endpoint confirmation evaluates two methods on the same 161,280 fresh episodes. The financial primary has 491,520 setting-trajectories but 163,840 unique exogenous tapes shared across three funding regimes. Nested budgets reuse observations. Tail reanalysis reuses the linear data. Do not add decision rows and call them independent experiments.

## Reuse / authorship
These are AI-assisted research-development materials. Prospective human authors must review correctness, literature priority, economic assumptions, data permissions and submission rules. No author, institution, approval, or endorsement is implied. Third-party papers are referenced, not redistributed, except the user's prior project manuscripts.

## Fresh-run verification record
The actual clean rerun matched 19 scientific CSV files byte for byte and all 566 arrays in 82 archives exactly. See `results/clean_reproduction.json`. `replication/clean_source_snapshot.zip` is the computational source snapshot used for that run; extract into an empty directory before rerunning. It does not contain manuscript provenance and is not intended to rebuild the PDF. After running the experimental commands, compare with:

```bash
python scripts/compare_release.py . /path/to/fresh_run
```

See `docs/FINDINGS_AND_OPEN_REQUIREMENTS.md` for the findings and unresolved requirements. `results/release_checks.json` records final tests and PDF checks.
