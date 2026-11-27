# Observationally Equivalent Algorithms & Machine Markets

[![CI](https://github.com/Pratikn03/Fianince/actions/workflows/ci.yml/badge.svg)](https://github.com/Pratikn03/Fianince/actions/workflows/ci.yml)
[![Lean 4.34.1](https://img.shields.io/badge/Lean_4.34.1-1%2C289_theorems_(0_sorry)-blue.svg)](research_extension/current_manuscript_lean_20261008/formal_verification_receipt.json)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)

Public replication archive, LaTeX manuscript sources, pre-registered empirical pipelines, and Lean 4 formalizations for the **Machine Markets** research program by **Pratik Niroula**, **Prashant Niroula**, **Sujan Khatiwada**, and coauthors.

---

## Primary Manuscripts (`pdf_delivered/`)

### 1. Paper 1 (*JEDC* Submission) — *Observationally Equivalent Algorithms: What Prices Reveal About Trader Populations, and What Supervisors Need*
**Authors:** Pratik Niroula, Prashant Niroula, and Sujan Khatiwada (November 2026)

- **Main Manuscript (35 pp.):** [`pdf_delivered/Paper1_JEDC_main.pdf`](pdf_delivered/Paper1_JEDC_main.pdf)
- **Online Supplement (83 pp.):** [`pdf_delivered/Paper1_JEDC_online_supplement.pdf`](pdf_delivered/Paper1_JEDC_online_supplement.pdf)
- **Combined Manuscript + Supplement (118 pp.):** [`pdf_delivered/Paper1_JEDC_main_and_supplement.pdf`](pdf_delivered/Paper1_JEDC_main_and_supplement.pdf)
- **Companion Working Papers:**
  - Extended SSRN Working Paper: [`pdf_delivered/Paper1_ssrn_complete.pdf`](pdf_delivered/Paper1_ssrn_complete.pdf)
  - Full Archival Working Paper: [`pdf_delivered/Paper1_full_working_paper.pdf`](pdf_delivered/Paper1_full_working_paper.pdf)
  - Companion Note (Breach Cascades & Nonlinear Rules): [`pdf_delivered/paper1b_companion.pdf`](pdf_delivered/paper1b_companion.pdf)

**Summary:** Characterizes the exact statistical and decision-theoretic boundary between what public market prices reveal about heterogeneous feedback-trading populations and what requires class-tagged or beneficial-owner-linked supervisory reporting. Establishes kernel sufficiency in both reduced-form and endogenous CARA-normal overlapping-generations inventory-dealer equilibria, proves the $(\Delta\eta)^{-(4K-2)}$ minimax sample-complexity barrier for separating colliding trader types alongside $O(\sigma^2\epsilon^{-2})$ parametric estimation of smooth market-wide functionals, proves Hunt–Stein minimax optimality of uniform cuts over unknown labelings, solves the strategic account-relabeling and surveillance-paradox games, and calibrates the identification gap to daily class-tagged institutional flows on the Taiwan Stock Exchange (TWSE).

---

### 2. Paper 2 — *From Human Markets to Machine Markets: Transient Amplification, an Exact Depth Condition, and a Maximal Pre-Trade Guard*
**Authors:** Pratik Niroula, S. Alkhushayni, Y. Chen, M. Bhavsar, and Prashant Niroula

- **Working Paper:** [`ceiling_suite/paper2/paper2.pdf`](ceiling_suite/paper2/paper2.pdf) | [`ceiling_suite/papers/versions/Paper2_JF.pdf`](ceiling_suite/papers/versions/Paper2_JF.pdf)
- **Summary:** Connects non-normal transient amplification and partial identification in closed-loop limit order books to pre-trade solvency guards, proving Kreiss/overshoot bounds, parametric safety certification $N = O(\sigma^2\epsilon^{-2}\log(1/\epsilon))$, and maximal uncertainty-aware admission rules.

---

### 3. Doctoral Thesis & Standalone Software Package

- **Consolidated Thesis:** [`thesis/thesis.pdf`](thesis/thesis.pdf) (source: [`thesis/thesis.tex`](thesis/thesis.tex); readiness & scope: [`thesis/READINESS.md`](thesis/READINESS.md))
- **Python Package (`margin_monitor`):** [`margin_monitor/`](margin_monitor/README.md) — standalone conditional margin-sign diagnostic library with unit tests.

---

## Lean 4 Formal Verification Scope

Deterministic algebraic, combinatorial, game-theoretic, and spectral-approximation steps are machine-checked in **Lean 4.34.1** against pinned Mathlib (`d13f23b723b8a846827a245b89c10fc7d3f11612`), recorded in [`formal_verification_receipt.json`](research_extension/current_manuscript_lean_20261008/formal_verification_receipt.json):

- **Audited Proof Inventory:** `1289 named theorems` across `CurrentProofs/` and 17 `PublicationRevision*.lean` modules (`3,178` project constants scanned; zero `sorry`; standard Lean axioms `propext`, `Classical.choice`, and `Quot.sound` only).
- **Explicit Coverage Boundary:** [`COVERAGE.md`](COVERAGE.md) classifies 76 environments across the baseline suite (30 `full`, 27 `conditional`, 19 `arithmetic`), and Paper 1 Online Supplement Table S2 documents the exact division between machine-checked deterministic lemmas and paper-proved probabilistic steps (Gaussian KL chain rule, Whittle asymptotics, Pinsker's inequality, and central limit theorems).

---

## Repository Layout

```text
.
├── pdf_delivered/                                  # Canonical compiled PDFs & Colab replication notebook
│   ├── Paper1_JEDC_main.pdf                        # Paper 1 JEDC main manuscript (35 pp.)
│   ├── Paper1_JEDC_online_supplement.pdf           # Paper 1 JEDC Online Supplement (83 pp.)
│   ├── Paper1_JEDC_main_and_supplement.pdf         # Combined main + supplement (118 pp.)
│   └── P1_Round3_Referee_Sensitivity_Colab.ipynb   # Self-contained TWSE sensitivity & regime-split notebook
├── ceiling_suite/
│   ├── papers/paper1_jedc_short/                   # Paper 1 JEDC builders (make_short.py, build_short.py) & 57-check audit
│   ├── p1_empirics/                                # TWSE T86/MI_INDEX executors, pre-registered specs, & unit tests
│   ├── paper1/ & paper2/                           # Modular working-paper LaTeX sources
│   └── REPLICATION_README.md                       # Guide to empirical notebooks and archived outputs
├── research_extension/
│   ├── current_manuscript_lean_20261008/           # Primary Lean 4.34.1 + Mathlib project & strict axiom auditor
│   └── paper1_publication_revision/                # PublicationRevision1–17.lean & passive/paradox numerical suites
├── lean_proofs/                                    # Plain-Lean exact rational arithmetic verification suite
├── margin_monitor/                                 # Standalone Python package & pytest suite
├── thesis/                                         # Thesis LaTeX sources & provenance verification scripts
└── tests/                                          # Repository-wide automated pytest suite
```

---

## Quick-Start Reproduction Commands

```bash
# 1. Build Paper 1 JEDC Main (35 pp.) + Online Supplement (83 pp.) and run all 57 audit checks:
.venv/bin/python ceiling_suite/papers/paper1_jedc_short/build_short.py
.venv/bin/python ceiling_suite/papers/paper1_jedc_short/test_jedc_audit_runner.py

# 2. Run Paper 1 empirical & numerical verification suites (TWSE synthetic panels, passive incidence, paradox):
.venv/bin/python ceiling_suite/p1_empirics/test_round2_fixes.py
.venv/bin/python research_extension/paper1_publication_revision/paradox/endogenous_supervisor_check.py
(cd research_extension/paper1_publication_revision/passive_tax_followup && ../../../.venv/bin/python -m unittest test_passive_incidence)
(cd ceiling_suite/p1_empirics && ../../.venv/bin/python test_p1m_core.py && ../../.venv/bin/python test_p1m_a1_core.py)

# 3. Build all Lean 4.34.1 + Mathlib proofs and regenerate formal_verification_receipt.json:
(cd research_extension/current_manuscript_lean_20261008 && python3 verify_formalization.py)

# 4. Run repository pytest & thesis verification gates:
.venv/bin/python scripts/verify_thesis_release.py
.venv/bin/pytest tests/ -q
```

---

## Citation & License

Licensed under the [Apache License 2.0](LICENSE). See [`CITATION.cff`](CITATION.cff) for BibTeX/CFF citation metadata.
