# Information required for a financial decision

Exploratory, self-contained Colab package for the question: when can observations
support a specified exposure limit while trading strategies remain unidentified?
This package does not establish a publication rating or complete the existing papers.

## Current manuscript revision

The returned full-mode Colab run has now been checked and integrated into the
existing Paper 1, Paper 2, thesis, synthesis and journal-layout sources. See
`MANUSCRIPT_REVISION.md` for the locations, findings and proof boundaries.
Only unrun empirical result cells remain empty in those revisions. The older
blank template is superseded as the manuscript-editing route; it remains here
as an historical artifact. The pinned notebook and its embedded experiment
sources have not been changed by this editorial integration.

Open `Information_Decision_Run_and_Return.ipynb` in Colab. Use a CPU runtime.
Run all cells. Default is the full profile and a fresh standalone Lean check.
The last cell downloads `Information_Decision_Results_<UTC>.zip`. Upload that ZIP
for review. All code is embedded with a SHA-256 checksum: cloning the large
repository is unnecessary. Package versions and source hashes are exported.

The expected runtime depends on Colab; the first Lean install downloads about
344 MB plus extracted libraries. Formal failure is recorded and does not erase
simulation outputs. The eight new Lean lemmas cover conditional decision logic,
not statistical/minimax proofs or the entire manuscript. Existing broad Lean
receipts retain their previous limitations.

## Files

- `model.py`: finite candidate market, explicit flat-to-flat 60-minute account,
  round-trip costs and robust finite-horizon capacity.
- `experiments.py`: all profiles, information arms, strong comparison policies,
  paired contrasts and exploratory repetition-level intervals.
- `market.py`: optional supplied-CSV observational check, separate from certificates.
- `verify_lean.py`, `formal/`: pinned Lean source, compiler and axiom receipt.
- `THEORY.md`: derivations, assumptions and unresolved central theorem.
- `PAPER_CODE_MAP.csv`: theorem/experiment/paper-slot traceability.
- `PROTOCOL.md`, `LITERATURE.md`: design and primary-source comparison obligations.
- `integrate_existing_papers.py`: checks the returned archive and updates the
  existing manuscript sources without replacing their historical content.
- `paper/p1_existing_revision.tex`, `paper/p2_existing_revision.tex`: additions
  integrated into the existing papers, not standalone replacement manuscripts.
- `results/returned_20261029T225100/`: checked returned outputs, diagnostics,
  source-preservation record and narrowly scoped Lean receipt.
- `paper/Blank_Research_Papers.tex` and `.pdf`: superseded blank template.

## Local run

```
python -m pip install -r requirements.txt
python run.py --profile full --out /absolute/new/output --lean install
```

Optional: append `--market-csv /absolute/path.csv`. Columns: timestamp, market,
price, signed_flow; regular 1- or 5-minute bars. Do not rename simulations as
market observations. Document source, units and earlier sample use separately.

The main experiment assumes clean reset observations, a fixed finite class,
known plant and reading variance. It is NOT an ordinary public-data certificate.
The account is price-taking and unlevered, not a venue-wide gate or equilibrium.
No source change overwrites the prior manuscripts or historical results.
