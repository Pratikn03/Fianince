# Hidden Slow Learners: Full-horizon identification audit (v2)

**Main conclusion:** the evidence supports a restricted measurement requirement, not superiority of the original rate-aware summary diagnostic. Full-horizon conventional positive-mixture bounds make more decisions on the same information. This is a synthetic, model-specific research artifact—not a real-market crisis predictor, established global novelty, or independent external replication.

Start with `paper/Full_Horizon_Identification_Audit.pdf` or `Full_Horizon_Findings_and_Next_Steps.docx`. Exact research assumptions and outcome limitations are in `docs/CLAIM_AND_PROOF_AUDIT.md`.

## What was executed

- Reconstructed **21,600 complete 256-tap vectors** (5,529,600 taps). Every previously saved input matched exactly.
- Compared original summary bounds, budget-matched summary bounds, full-horizon NNLS, full-moment positive-mixture outer LP bounds, and the LP/summary intersection.
- Executed **86,400 paired rows** across H = 4, 16, 64, 256.
- Executed **5,400 predetermined resolution checks** on 1,080 of those vectors.
- Rechecked **112 exact rational pairs plus one readable witness**.
- Checked **216 cases** with separately assembled constraints and a different HiGHS algorithm.
- Checked all confidence events: all **82,364 on-event LP intervals** contain the true gain. Four higher-noise confident errors occur off-event.
- Derived a fixed-two-state Gaussian measurement limit and tested 60 settings with **12,000,000 projected likelihood-ratio draws**, not that many simulated markets.
- Repeated the full 86,400-row comparison in a clean directory. All **33 non-timing fields** match; numeric fields are exactly equal in this environment.

## Primary H=256 results

Each noise level has 10,800 vectors. Conflicts remain unresolved and are included in the denominator.

| Method | Lower-noise decisions | Lower-noise wrong calls | Higher-noise decisions | Higher-noise wrong calls |
|---|---:|---:|---:|---:|
| Original summary bound | 8,930 (82.69%) | 0 | 7,150 (66.20%) | 0 |
| Full-horizon NNLS point fit | 10,800 (100%) | 24 | 10,800 (100%) | 306 |
| Full-moment outer LP bound | 9,508 (88.04%) | 0 | 8,278 (76.65%) | 4 |

NNLS labels are **not confidence certificates**. The LP and summary procedures use the same nominal 0.05 family error budget, allocated differently. The LP is not pointwise better: some previous decisions become conflicts. It is an outer relaxation, not a proved optimal continuous estimator or a replication of every cited identification method.

## Reproduction

Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0 were used. No network, GPU, model API, private financial account, or paid data is required after dependencies are installed.

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows alternative: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/verify_exact.py --results data
python scripts/verify_confidence_events.py
python scripts/run_testing_limits.py
python scripts/verify_alternate_solver.py
```

To rerun the entire primary study without overwriting its saved results, choose a **new** directory:

```bash
python scripts/reproduce_clean.py --output ../mmfh-independent-run --datasets 21600 --workers 4
```

A smaller smoke run can use `--datasets 100`; this does not reproduce headline totals. `--workers 1` is supported on smaller computers. Runtimes vary; no runtime guarantee is made. Full arrays and CSV files require disk and memory space. Cross-platform numerical variation is possible; do not silently relax checks when classifications differ.

To regenerate all input taps from the original recorded seeds:

```bash
python scripts/regenerate_inputs.py
```

To intentionally recompute primary/sensitivity outputs in this folder, after keeping an unchanged copy:

```bash
python scripts/run_comparison.py --workers 4
python scripts/run_sensitivity.py
python scripts/analyze_results.py
python scripts/verify_confidence_events.py
```

The complete paper is one self-contained `.tex` file with its bibliography embedded:

```bash
cd paper
pdflatex -interaction=nonstopmode -halt-on-error Full_Horizon_Identification_Audit.tex
pdflatex -interaction=nonstopmode -halt-on-error Full_Horizon_Identification_Audit.tex
```

## Directory map

- `src/mmfh/`: estimators and analytic testing limits.
- `tests/`: test-first regression and mathematical checks.
- `scripts/`: execution, regeneration, analysis and separate verification.
- `configs/`: fixed design and sensitivity choices.
- `data/`: complete measurements, original compact inputs, true configurations and exact witnesses.
- `results/`: all paired rows, complete summaries, failure cases and verification logs.
- `docs/`: protocol, data dictionary, proof/claim audit, deviations and external review checklist.
- `literature/`: primary-source review with explicit depth and novelty limitations; no redistributed paper PDFs.
- `paper/`: current manuscript PDF and self-contained LaTeX.
- `provenance/`: selected unchanged v1 files and original archive hash.

## Research and attribution boundaries

The previous archive is not modified. This release is AI-assisted research development. There has been no outside expert approval, independently authored external reproduction, real-market validation, or demonstration of a new finance paradigm. The named prior authors did not participate in or endorse this study. The hypotheses, limitations, numerical failures and unfavorable outcomes are retained. Resolve authorship, attribution and any venue disclosure requirements before submission.
