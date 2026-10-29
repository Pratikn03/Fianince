# Machine Markets: Auditable Memory, Financial Identification Limits, and Pre-Trade Safety Under Feedback

[![CI](https://github.com/Pratikn03/Fianince/actions/workflows/ci.yml/badge.svg)](https://github.com/Pratikn03/Fianince/actions/workflows/ci.yml)
[![Lean 4](https://img.shields.io/badge/Lean_4-recorded_receipt-blue.svg)](research_extension/current_manuscript_lean_20261008/formal_verification_receipt.json)

> **29 October review branch:** supported source corrections and exploratory experiments are documented in [the research plan](studies/economic_review_20261029/RESEARCH_PLAN.md). Start with [the Colab notebook](studies/economic_review_20261029/Economic_Review_Experiments.ipynb). The current modular sources are `ceiling_suite/papers/paper1/` and `ceiling_suite/papers/paper2/`; historical PDFs and registered results are snapshots, not evidence for revised statements.
>
> **Formalization boundary:** the committed 25 October receipt records 520 named theorems and explicitly reports `full_manuscript_formalization_complete: false`. It is a historical build receipt, not an independent rebuild in this branch. Existing name mappings do not establish semantic coverage of revised propositions. See [COVERAGE.md](COVERAGE.md) and the new [claim ledger](studies/economic_review_20261029/CLAIM_LEDGER.csv) for their distinct purposes.

---

## October 2026 Manuscripts (`ceiling_suite/`)

This repository contains the LaTeX sources, replication code, pre-registered notebooks, and Lean 4 formalizations for two companion working papers:

1. **Paper 1 — *Auditable Memory and Financial Identification Limits in Electronic Limit Order Books***  
   - **Working Paper PDF**: [`ceiling_suite/paper1/paper1.pdf`](ceiling_suite/paper1/paper1.pdf) (80 pp., with appendices)  
   - ***Quantitative Economics* submission format**: [`ceiling_suite/papers/versions/Paper1_QE.pdf`](ceiling_suite/papers/versions/Paper1_QE.pdf) (89 pp., with supplement)  
   - **Core Contribution**: Establishes what an observer can and cannot learn about hidden adaptive trading cohorts from price and order-flow records, including merged rate-weight equivalence, minimax $(\Delta\eta)^{-(4K-2)}$ cohort-separation sample complexity, spectral dissipation lower bounds, and finite-window abstention limits.

2. **Paper 2 — *From Human Markets to Machine Markets: Transient Amplification, an Exact Depth Condition, and a Maximal Pre-Trade Guard*** (Niroula, Alkhushayni, Chen, Bhavsar and Niroula)  
   - **Working Paper PDF**: [`ceiling_suite/paper2/paper2.pdf`](ceiling_suite/paper2/paper2.pdf) (114 pp., with appendices)  
   - ***Journal of Finance* submission format**: [`ceiling_suite/papers/versions/Paper2_JF.pdf`](ceiling_suite/papers/versions/Paper2_JF.pdf) (106 pp.: 60-page main text, Internet Appendix from p. IA-1)  
   - **Core Contribution**: Connects closed-loop limit-order-book feedback and partial identification to financial safety:
     - **Transient Amplification (Sections 3–4)**: Non-normal Kreiss bounds, the peak-overshoot theorem (depletion versus momentum, with the confluent peak lag), and the closed-form summed response $S = \tilde\kappa / (m - q\tilde\kappa)$.
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
│   │   ├── versions/                               # Paper1_QE.pdf (89 pp.) & Paper2_JF.pdf (106 pp.)
│   │   ├── hardening/                              # Numerical checks behind the October 2026 theorem hardening
│   │   └── research_extension/information_safety/  # Python verification & simulation suite for Sections 5–7 (T01–T15)
│   ├── Part15_InfoSafety_Untouched.ipynb           # Pre-registered Part 15 untouched-days empirical notebook
│   ├── Part16_Untouched_Symbols.ipynb              # Pre-registered Part 16 untouched-symbols empirical notebook
│   ├── Part17_NewVenue_Coinbase.ipynb              # Pre-registered Part 17 new-venue (Coinbase) notebook
│   ├── Part18_PostHoc_Placebo_Baselines.ipynb      # Post-hoc Part 18 placebo and guard baselines
│   ├── REPLICATION_README.md                       # Guide to Parts 1–18 replication notebooks and scripts
│   └── verify_ceiling_suite_lean_proofs.py         # Verifies the LaTeX label to Lean 4 declaration mapping
│
├── research_extension/
│   └── current_manuscript_lean_20261008/           # Primary Lean 4.34.1 + Mathlib formalization (see recorded receipt and coverage boundary)
│       ├── CurrentProofs/                          # 33 Mathlib proof modules over ℝ (InfoSafetyExtensions.lean: Sections 5–8 and the hardening results)
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

# 2. Verify the label-to-declaration mapping across Paper 1 and Paper 2:
python3 ceiling_suite/verify_ceiling_suite_lean_proofs.py
# Optional strict gate (currently fails until missing/revised coverage is resolved):
# python3 ceiling_suite/verify_ceiling_suite_lean_proofs.py --require-complete

# 3. Run the Information-Safety unit tests and all data-free results (T01–T15):
pytest ceiling_suite/papers/research_extension/information_safety/tests -q
(cd ceiling_suite/papers/research_extension/information_safety && python3 run_all.py)

# 4. Run the full repository pytest suite:
pytest tests/ -v

# 5. Recompile Paper 1 and Paper 2 PDFs (working papers + QE/JF versions):
sh ceiling_suite/papers/build_p1.sh && sh ceiling_suite/papers/build_p2.sh && python3 ceiling_suite/papers/versions/build_versions.py

# 6. End-to-end clean reproduction (fresh venv, tests, results, LaTeX, ledger audit; Lean optional):
SKIP_LEAN=1 sh reproduce_paper_suite.sh
```

---

## License

Apache 2.0 License. See [`COVERAGE.md`](COVERAGE.md) and [`ceiling_suite/REPLICATION_README.md`](ceiling_suite/REPLICATION_README.md) for detailed formalization and empirical replication documentation.
