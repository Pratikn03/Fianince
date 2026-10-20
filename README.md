# Machine Markets: Auditable Memory, Financial Identification Limits, and Pre-Trade Safety Under Feedback

[![CI](https://github.com/Pratikn03/Fianince/actions/workflows/ci.yml/badge.svg)](https://github.com/Pratikn03/Fianince/actions/workflows/ci.yml)
[![Lean 4](https://img.shields.io/badge/Lean_4-396_declarations_kernel--checked%3B_see_COVERAGE.md-blue.svg)](COVERAGE.md)
[![Pytest Suite](https://img.shields.io/badge/Pytest-Passing-brightgreen.svg)](tests/)

> **Lean 4 Formalization Status**: 396 declarations kernel-checked in [`research_extension/current_manuscript_lean_20261008/`](research_extension/current_manuscript_lean_20261008/) (`0 sorry`, standard axioms `propext`, `Classical.choice`, `Quot.sound`); see [`COVERAGE.md`](COVERAGE.md) for which paper statements are fully formalized (`full`), conditional on explicit analytical hypotheses (`conditional`), or algebraic/numerical checks (`arithmetic`).

---

## October 2026 Manuscripts (`ceiling_suite/`)

This repository contains the LaTeX sources, replication code, pre-registered notebooks, and Lean 4 formalizations for two companion working papers:

1. **Paper 1 — *Auditable Memory and Financial Identification Limits in Electronic Limit Order Books***  
   - **Working Paper PDF**: [`ceiling_suite/paper1/paper1.pdf`](ceiling_suite/paper1/paper1.pdf) (31 pp.)  
   - **Extended Version (*Quantitative Economics* format)**: [`ceiling_suite/papers/versions/Paper1_QE.pdf`](ceiling_suite/papers/versions/Paper1_QE.pdf) (85 pp.)  
   - **Core Contribution**: Establishes what an observer can and cannot learn about hidden adaptive trading cohorts from price and order-flow records, including merged rate-weight equivalence, minimax $(\Delta\eta)^{-(4K-2)}$ cohort-separation sample complexity, spectral dissipation lower bounds, and finite-window abstention limits.

2. **Paper 2 — *From Human Markets to Machine Markets: Transient Amplification, the Summed-Gain Guard, and the Equilibrium Under-Supply of Fragility Absorption***  
   - **Working Paper PDF**: [`ceiling_suite/paper2/paper2.pdf`](ceiling_suite/paper2/paper2.pdf) (40 pp.)  
   - **Extended Version (*Journal of Finance* format)**: [`ceiling_suite/papers/versions/Paper2_JF.pdf`](ceiling_suite/papers/versions/Paper2_JF.pdf) (86 pp.)  
   - **Core Contribution**: Connects closed-loop limit-order-book feedback and partial identification to financial safety:
     - **Transient Amplification (Sections 3–4)**: Non-normal Kreiss bounds, depth-mediated amplification margins ($C_2, C_3$), and closed-form summed responses $S = \tilde\kappa / (m - q\tilde\kappa)$.
     - **Information Limits for Safety (Section 5)**: Constructive two-market ambiguity witness (`ex:witness`), total-variation capacity-loss bound (`prop:twoworld`), Markov–Krein finite-window bounds and unboundedness without a memory bound (`thm:window`), and parametric-rate safety certification $N = O(\sigma^2\epsilon^{-2}\log(1/\epsilon))$ (`thm:certcost`).
     - **Identification-Free & Uncertainty-Aware Pre-Trade Guard (Section 6)**: Quantity-gate duality (`eq:gate` & `thm:guard`), compatible-set soundness (`lem:sound`), optimal uncertainty-aware admission $\alpha^* = \min\{1, c_I/(\kappa\Phi^+)\}$ (`thm:robustguard`), and multi-step balance-sheet forward solvency (`thm:forward`).
     - **Decision Value of Disclosure & Equilibrium Fragility (Sections 7–8)**: Monotonicity and strictness of optimal admission under disclosure refinement $\Theta_{O'} \subseteq \Theta_O$ (`thm:disclosure`) and equilibrium under-supply of fragility absorption (`prop:equil`).

---

## Repository Structure

```text
.
├── COVERAGE.md                                     # Item-by-item Lean 4 coverage table (full / conditional / arithmetic)
├── ceiling_suite/
│   ├── paper1/                                     # Paper 1 modular LaTeX sources & paper1.pdf
│   ├── paper2/                                     # Paper 2 modular LaTeX sources & paper2.pdf
│   ├── papers/
│   │   ├── versions/                               # Paper1_QE.pdf (85 pp.) & Paper2_JF.pdf (86 pp.)
│   │   └── research_extension/information_safety/  # Python verification & simulation suite for Sections 5–7 (T01–T12)
│   ├── Part15_InfoSafety_Untouched.ipynb           # Pre-registered Part 15 untouched-days empirical notebook
│   ├── Part16_Untouched_Symbols.ipynb              # Pre-registered Part 16 untouched-symbols empirical notebook
│   ├── REPLICATION_README.md                       # Guide to Parts 1–16 replication notebooks and scripts
│   └── verify_ceiling_suite_lean_proofs.py         # Verifies 1-to-1 LaTeX label to Lean 4 mapping
│
├── research_extension/
│   └── current_manuscript_lean_20261008/           # Primary Lean 4.29 + Mathlib formalization (396 theorems, 0 sorry)
│       ├── CurrentProofs/                          # 33 Mathlib proof modules over ℝ
│       ├── AxiomAudit.lean                         # Kernel axiom auditor
│       ├── axiom_audit.jsonl                       # Kernel-checked theorem types and axiom footprints
│       └── verify_formalization.py                 # Builds Mathlib project and writes formal_verification_receipt.json
│
├── lean_proofs/                                    # Companion plain-Lean rational arithmetic checks (0 sorry)
└── tests/                                          # Automated pytest verification suite
```

---

## Reproduction & Verification Commands

```bash
# 1. Run the Lean 4 + Mathlib build and strict axiom audit:
python3 research_extension/current_manuscript_lean_20261008/verify_formalization.py

# 2. Verify 1-to-1 theorem coverage across Paper 1 and Paper 2:
python3 ceiling_suite/verify_ceiling_suite_lean_proofs.py

# 3. Run the Information-Safety numerical and unit-test suite (T01–T12):
pytest ceiling_suite/papers/research_extension/information_safety/tests/test_information_safety.py -v

# 4. Run the full repository pytest suite:
pytest tests/ -v

# 5. Recompile Paper 1 and Paper 2 PDFs (working papers + QE/JF versions):
python3 ceiling_suite/papers/versions/build_versions.py
```

---

## License

Apache 2.0 License. See [`COVERAGE.md`](COVERAGE.md) and [`ceiling_suite/REPLICATION_README.md`](ceiling_suite/REPLICATION_README.md) for detailed formalization and empirical replication documentation.
