# From Human Markets to Machine Markets — integrated release v0.4

## Start here

Read `paper/Machine_Markets_Integrated_Research_Paper.pdf` (38 pages). Its self-contained LaTeX source is beside it. The updated paper preserves the original framework, integrates both executed companion findings, and adds the observable-only price measurement experiment. The three original PDF/TeX pairs are preserved under `provenance/`.

**Finding:** A randomized filled-order / quoted-price protocol can estimate the relevant response without observing private adaptive states. Under the stated linear Gaussian independent-episode contract and a valid rate floor, uncertainty can be propagated into a model-conditioned stability interval. This is not a generally deployable financial-safety detector.

## What was executed

The primary panel has 12 generating configurations, four observation designs and 40 panels per configuration/design: 1,920 panels, 1,105,920 simulated episodes and 5,760 comparisons across three nested horizons. Each episode contains 66 observed price changes. All estimator inputs are signed filled probe quantities, those prices, and a public valid rate floor. Direct persistence, impact, noise scales, exact weights/rates and latent states are not provided to inference.

At lag 64, the strongest primary design (1,024 episodes and four-share pulses) gives 80 correct confident answers out of 480 panels (16.67%) and 400 inconclusive answers. There are no wrong confident recurrence-bound labels in the primary run. That zero is an observed count, not a zero-error guarantee. The unconditional confidence theorem is per measurement panel; it is not a conditional accuracy guarantee on selected answers.

An explicitly post-primary budget extension gives 15/60 and 25/60 definite answers with 8,192 and 32,768 episodes respectively. All slowest-class panels remain inconclusive. An incorrectly supplied minimum rate produces 20 false stable labels for an unstable model even though all 20 measured response confidence events hold. Nonrandom assignment and nonlinear impact controls are also preserved.

The newly calculated lower bound uses actual price observations, not the previous hidden-kernel observation law. It holds for its declared pulse family and finite budget; it does not establish a universal impossibility or explain every inconclusive result of a conservative solver.

## Reproduce the new experiment

Tested on Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, pandas 2.2.3, pytest 9.0.2. Use an isolated environment. No account, API key, network dataset or live trading is required after dependencies are installed.

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python run_study.py --out rerun_primary
python verify_release.py
```

`verify_release.py` checks the delivered primary data with an alternate group-means regression and an alternate LP algorithm. It does not import an outside researcher's implementation; it is an internal cross-check. `run_study.py --out rerun_primary` protects the delivered primary results. The two full primary runs produced byte-identical `panels.csv` and `comparison.csv` and identical arrays in all nine repeated NPZ files in this environment; timing is excluded. Other platforms should use stated numerical tolerances rather than expecting identical floating-point bytes.

```bash
# Run on a copied release folder because this script writes into its own folder:
python run_extensions.py
```

The extensions are deliberately separated from the frozen primary panel. Their result tables are not pooled into the primary percentages. The repository contains both the pre-primary protocol and a post-primary exploration declaration.

## Reproduce retained algebra and tests

```bash
python provenance/verify_original_algebra.py
(cd provenance/legacy_code/hidden && python -m pytest -q tests)
(cd provenance/legacy_code/full_horizon && python -m pytest -q tests)
```

There are 22 new tests, 29 first-companion tests and 23 audit tests. The original algebra script checks 625 scalar and 250 network cases. The lightweight legacy snapshots contain the original code/tests but not the complete old experiment data. To rerun those entire old studies, use the two previous full archives; their SHA-256 identities are in the source manifest. This release contains selected prior result summaries and the original manuscripts, not a claim to have regenerated all previous 86,400-row studies again in this integration.

## Compile the integrated paper

```bash
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=paper paper/Machine_Markets_Integrated_Research_Paper.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=paper paper/Machine_Markets_Integrated_Research_Paper.tex
```

A standard TeX Live installation with the packages named in the preamble is required. Bibliography and the original mathematical plot are embedded; no external figure or .bib file is required. The experiments are reproduced from the Python supplement, not by compiling LaTeX.

## File map

- `src/market.py`: stylized economic transactions, hidden memories, observable prices, evaluation-only analytical response.
- `src/observable.py`: regression, unknown-covariance response intervals, recurrence bounds and comparator estimators.
- `data/public_panel_statistics.npz`: all 1,920 measured response summaries; shape 1920 x 4 x 66.
- `data/public_example_*.npz`: four complete datasets containing only probes and observed price changes.
- `data/covariance_example_*.npz`: separately labeled evaluation covariance/truth; never an estimator input.
- `results/`: all decision rows, public-record hashes, negative controls, observation limits, primary/extension summaries and verification checks.
- `docs/`: protocols, assumptions, integration lineage, literature audit and data dictionary.
- `provenance/`: original artifacts, selected old results and lightweight legacy test/code snapshots.
- `logs/`: execution, tests and final compilation evidence.

## What remains open

The market has cash/share bookkeeping but unrestricted credit and short positions, fixed depth, no defaults, no funded order book and no trained neural agents. The protocol assumes independent repeatable episodes, fully filled exogenous probes, invariant linear Gaussian dynamics and a valid tail/rate class. Accurate prices do not verify those assumptions. Real-market observation, strong covariance-aware output-error competitors, binding economic constraints, architecture transfer, exhaustive novelty review and independent external reproduction remain open. No outside reviewer, institution or regulator has endorsed this work.

Use `SHA256SUMS.txt` to check delivered file integrity. It excludes itself. Do not mistake code reproducibility for external economic validity.
