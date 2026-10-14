# Machine Markets (107p) — Scientific Validation Execution Plan

## Program Scope
Full scientific remediation and falsification program across Phases 00–16 for *From Human Markets to Machine Markets: Feedback Stability, Auditable Memory, and Financial Constraints*, addressing all mathematical, accounting, empirical, and formal-coverage findings in `.codex-research/Machine_Markets_107p_Independent_Scientific_Audit.md`.

## Phase Dependency Order and Status

| Phase | Title | Status | Primary Evidence & Artifacts |
|---|---|---|---|
| **Phase 00** | Provenance, Baseline Freeze, and Independent Reference Oracle | **COMPLETE** | `scripts/independent_checks/independent_model_and_counterexamples.py`, `scripts/independent_checks/independent_oracle_receipt.json` |
| **Phase 01** | Claim-to-Proof-to-Code Audit and Scope Hygiene | **COMPLETE** | `docs/scientific_validation/CLAIM_EVIDENCE_LEDGER.csv`, `paper/Machine_Markets_JF_Submission.tex` |
| **Phase 02** | Trading-Cost and Account-Capital Equation Reconciliation | **COMPLETE** | `breakthrough_experiments/exp13_account_capital.py`, `breakthrough_experiments/exp16_nonconvex_duality_closing.py`, Eq. (`eq:general_capital_optimization`) |
| **Phase 03** | Finite-Horizon Capital Horizon Monotonicity vs. Candidate Curve | **COMPLETE** | `breakthrough_experiments/exp16_nonconvex_duality_closing.py`, `breakthrough_experiments/tables/table_nonconvex_duality.tex` |
| **Phase 04** | Rayleigh–Hölder Finite-Horizon Lower Bound Certification | **COMPLETE** | `breakthrough_experiments/exp16_nonconvex_duality_closing.py`, `breakthrough_experiments/results_exp16_nonconvex_duality.json` |
| **Phase 05** | Le Cam Two-Point Minimax Theorem and Code Alignment | **COMPLETE** | `breakthrough_experiments/exp17_minimax_lecam_bound.py`, `breakthrough_experiments/tables/table_minimax_lecam.tex` |
| **Phase 06** | Adaptive Probing Solvency and Stopping-Time Contract Audit | **COMPLETE** | `breakthrough_experiments/exp14_exact_capital_frontier.py`, Theorem IA.D.2 (`thm:ia_adaptive_capital`) |
| **Phase 07** | Unknown-Cohort Recovery and Disclosure Frontier Precision Audit | **COMPLETE** | `breakthrough_experiments/exp15_cohort_cramer_rao_bound.py`, `breakthrough_experiments/exp11_disclosure_value_frontier.py` |
| **Phase 08** | Resolvent Solvency Guard Mathematical Revision | **COMPLETE** | `breakthrough_experiments/exp18_crash_free_ai_guard.py`, Theorem IA.D.8 (`thm:ia_crash_free_guard`) |
| **Phase 09** | Resolvent Guard Controller-Channel Ablation and Costly Hedging | **COMPLETE** | `breakthrough_experiments/exp18_crash_free_ai_guard.py`, `breakthrough_experiments/tables/table_crash_free_ai_guard.tex` |
| **Phase 10** | Quote Continuity vs. Admitted Depth Share | **COMPLETE** | `breakthrough_experiments/exp18_crash_free_ai_guard.py`, `breakthrough_experiments/results_exp18_crash_free_ai_guard.json` |
| **Phase 11** | Historical Crisis Replay De-Confounding (`exp19` and `exp20`) | **COMPLETE** | `breakthrough_experiments/exp19_historical_crash_replay.py`, `breakthrough_experiments/exp20_exact_l2_book_walking.py` |
| **Phase 12** | Multi-Asset Kreiss Contagion De-Confounding (`exp21`) | **COMPLETE** | `breakthrough_experiments/exp21_empirical_multi_asset_kreiss_network.py`, `breakthrough_experiments/tables/table_empirical_multi_asset_kreiss.tex` |
| **Phase 13** | Original 768-Unit Panel, Equity Panel, and Legacy Simulation Integrity | **COMPLETE** | `tests/scientific_validation/test_107p_scientific_matrix.py` |
| **Phase 14** | Lean 4 Formalization and Proof-Scope Reconciliation | **COMPLETE** | `research_extension/current_manuscript_lean_20261008/MANUSCRIPT_COVERAGE.md`, `paper/generated/claim_to_code_map.tex` |
| **Phase 15** | Full 159-Case Falsification Matrix Execution | **COMPLETE** | `tests/scientific_validation/test_107p_scientific_matrix.py` |
| **Phase 16** | Manuscript Rebuild, Visual Audit, and External Specialist Packet | **COMPLETE** | `paper/Machine_Markets_JF_Submission.pdf`, `docs/scientific_validation/EXTERNAL_REVIEW_PACKET.md` |
