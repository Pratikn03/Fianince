# Hidden Slow Learners
## A reproducible companion study to *From Human Markets to Machine Markets*

**Status:** model-specific mathematical results plus executed synthetic experiments. Candidate original contribution; global priority and external financial validity are not established. No real-market dataset, trained LLM/RL population, or independent human replication is claimed.

## Start here

- `paper/Hidden_Slow_Learners.pdf`: complete research note, proofs, actual results, and limitations.
- `paper/Hidden_Slow_Learners.tex`: self-contained source; figures and bibliography are embedded.
- `docs/Research_Findings_and_Next_Steps.docx`: findings, interpretation, and the remaining research gates.
- `results/summary.json`: machine-readable outcomes.
- `literature/LITERATURE_AUDIT.md`: closest predecessors and the novelty boundary.

## The result in one paragraph

For every fixed response horizon, the stated positive-feedback model admits a stable and an unstable market with identical early price responses. The construction matches the price-adjustment coefficient and the number of active adaptive agents; it changes the hidden distribution of learning responses. This is an explicit financial specialization of classical truncated-moment/realization ideas, not a new general systems theorem. A known lower bound on learning rates allows conservative bounds on total feedback. Those bounds sometimes identify stability or instability and otherwise return **inconclusive**. An invalid rate bound can cause an incorrect stable label.

## Executed evidence

112 exact matched pairs (224 model instances), 336 common-shock path comparisons, 108 eight-state measurement configurations, and 21,600 Gaussian-noise measurement datasets. Four horizons yield 86,400 decision rows. All original-to-this-project results are synthetic. The 128-replicate sample means are generated directly from their known Gaussian distribution; there were not 2.76 million independently executed market trials.

The standard-library rational verifier checks all 112 pairs plus the readable witness. A separate measurement verifier regenerates all 21,600 archived measurement datasets and recomputes all 86,400 rate-aware decisions without importing the primary package. A clean-directory numerical rerun reproduces 17 data files. These are internal reproducibility checks, not external independent replication.

## Reproduce

Before changing the delivered files, run `python scripts/verify_manifest.py` to check archive integrity. For an independent check, preserve `results/`, run with `--output reproduced_results`, and use `scripts/check_reproduction.py --candidate reproduced_results`. The external checklist is in `docs/EXTERNAL_REPRODUCTION_CHECKLIST.md`.

Use Python 3.11 or newer. The exact environment used is recorded in `results/environment.json` and `requirements-lock.txt`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/run_experiments.py
python scripts/verify_exact.py
python scripts/verify_measurements.py
python scripts/build_figures.py
```

On Windows, activate the environment with `.venv\Scripts\activate` instead of `source`.

A quick functional run is:

```bash
python scripts/run_experiments.py --smoke --output smoke_results
python scripts/verify_exact.py --results smoke_results
python scripts/verify_measurements.py --results smoke_results
```

`--smoke` checks execution only; it is not the full reported experiment.

Build the self-contained paper using pdfLaTeX (TeX Live packages include amsmath, amsthm, booktabs, pgfplots, natbib, hyperref, and listings):

```bash
cd paper
pdflatex -interaction=nonstopmode -halt-on-error Hidden_Slow_Learners.tex
pdflatex -interaction=nonstopmode -halt-on-error Hidden_Slow_Learners.tex
```

There is no external `.bib`, image dependency, shell escape, cloud API, paid dataset, or GPU requirement for the main experiment. Optional report-authoring dependencies are in `requirements-reports.txt`; `python scripts/build_report.py` rebuilds the editable findings report from the saved results. The delivered paper is 15 pages and the findings report is 7 pages.

## Data access matters

The exact non-identifiability theorem concerns a finite **price-response** window. The noisy certificate experiment assumes stronger **controlled loop-open kernel measurements** in a trusted shadow replay, with a valid architectural learning-rate floor. It is not a price-only crisis detector. The paper explains the distinction and does not apply Gaussian kernel intervals to deconvolved noisy stock returns.

## Important limitations

The model is linear, positive, fixed in time, and has constant price impact. It excludes inventory accounting, leverage, spreads, endogenous liquidity, strategic optimization, and model updates. “Unstable” means spectral radius above one in this model, not a measured crisis probability. The matrix-pencil comparator is a simple fixed-rank-selection implementation using at most 32 early taps, not an optimized state-of-the-art identification suite. No unconditional algorithmic superiority is claimed.

A bounded rate does not resolve every finite-horizon case; near-boundary systems may remain inconclusive. The confidence result is an unconditional bound on any wrong confident label across four predeclared horizons, not a conditional error guarantee among only decided cases or an indefinite online guarantee.

## File map

- `src/machine_markets/`: model, exact construction, and inference.
- `tests/`: unit and end-to-end smoke tests.
- `configs/main.json`: full fixed numerical design.
- `scripts/`: run, verification, figures, and report generation.
- `results/`: exact witnesses, CSV outcomes, measurement inputs, and verification logs.
- `figures/`: plots generated only from recorded outputs.
- `docs/`: protocol, execution plan, claim ledger, and next steps.
- `literature/`: source audit and bibliography.
- `provenance/`: unmodified original LaTeX framework and user concept note.

The files in `provenance/` are historical inputs, not revalidated current findings. Their larger research program remains prospective. Authorship, affiliations, disclosure, publication licensing, and submission readiness must be decided and verified by the human researcher before circulation.
