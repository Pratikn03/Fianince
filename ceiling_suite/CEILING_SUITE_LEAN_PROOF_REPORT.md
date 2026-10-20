# Ceiling Suite — Complete Lean 4 Formal Verification Report

- **Status**: `VERIFIED_100_PERCENT_NO_SORRY` (0 `sorry`, 0 `admit`, 0 `native_decide`, 0 unapproved axioms)
- **Lean Toolchain**: `leanprover/lean4:v4.34.1`
- **Paper 1 (`ceiling_suite/paper1/`)**: 29 / 29 formal environments verified
- **Paper 2 (`ceiling_suite/paper2/`)**: 21 / 21 formal environments verified
- **Total Ceiling Suite Environments**: 50 / 50 verified in both Mathlib (`ℝ`) and Core Lean 4 (`Rat`)

## Paper 1 — Auditable Memory and Financial Identification Limits (`paper1/`)

| # | Environment | Label | Title | LaTeX Source | Mathlib (`ℝ`) Theorem | Core Lean (`Rat`) Theorem |
|---|---|---|---|---|---|---|
| 1 | `proposition` | `prop:kalman` | Kalman memory | `p1_front.tex:142` | `CurrentMM.p1_prop_kalman_memory` (L46) | `MachineMarkets.p1_prop_kalman_memory` (L13) |
| 2 | `proposition` | `prop:ogd` | Gradient memory | `p1_front.tex:149` | `CurrentMM.p1_prop_ogd_memory` (L83) | `MachineMarkets.p1_prop_ogd_memory` (L21) |
| 3 | `lemma` | `lem:cm` | Positive price-response geometry | `p1_front.tex:157` | `CurrentMM.p1_lem_cm_positive_response` (L96) | `MachineMarkets.p1_lem_cm_positive_geometry` (L29) |
| 4 | `theorem` | `thm:merged` | Merged rate--weight equivalence | `p1_ident.tex:5` | `CurrentMM.p1_thm_merged_equivalence_and_resolvent` (L123) | `MachineMarkets.p1_thm_merged_equivalence` (L38) |
| 5 | `theorem` | `thm:quantity` | Sharp probing-resource orders for a known symmetric pair | `p1_ident.tex:33` | `CurrentMM.p1_thm_quantity_sharp_orders` (L143) | `MachineMarkets.p1_thm_quantity_orders` (L44) |
| 6 | `lemma` | `lem:toeplitz` | Fair execution | `p1_ident.tex:87` | `CurrentMM.p1_lem_toeplitz_fair_execution` (L161) | `MachineMarkets.p1_lem_toeplitz_fair_execution` (L53) |
| 7 | `theorem` | `thm:cap` | Sharp robust quantity cap from cash and margin | `p1_ident.tex:99` | `CurrentMM.p1_thm_cap_counterparty_margin` (L191) | `MachineMarkets.p1_thm_cap_robust_quantity` (L60) |
| 8 | `proposition` | `prop:disclosure` | Exact financial disclosure changes the experiment | `p1_ident.tex:114` | `CurrentMM.p1_prop_disclosure_third_mark` (L221) | `MachineMarkets.p1_prop_disclosure_changes_experiment` (L66) |
| 9 | `theorem` | `thm:capital` | Matching capital order for funded deterministic probes | `p1_ident.tex:122` | `CurrentMM.p1_thm_capital_funded_probes` (L235) | `MachineMarkets.p1_thm_capital_order` (L74) |
| 10 | `proposition` | `prop:passive0` | Passive distinction with zero controlled quantity | `p1_ident.tex:144` | `CurrentMM.p1_prop_passive0_three_step_blocks` (L254) | `MachineMarkets.p1_prop_passive0_distinction` (L79) |
| 11 | `proposition` | `prop:ambiguity` | Conditional quote and allocation cost of ambiguity | `p1_ident.tex:154` | `CurrentMM.p1_prop_ambiguity_quote_and_surplus` (L269) | `MachineMarkets.p1_prop_ambiguity_quote_cost` (L87) |
| 12 | `proposition` | `prop:tri` | Tri-region partition and finite-session resolution floor | `p1_account.tex:13` | `CurrentMM.p1_prop_tri_region_partition` (L285) | `MachineMarkets.p1_prop_tri_region_floor` (L93) |
| 13 | `theorem` | `thm:spectral` | Spectral dissipation lower bound | `p1_account.tex:65` | `CurrentMM.p1_thm_spectral_dissipation_bound` (L299) | `MachineMarkets.p1_thm_spectral_dissipation` (L99) |
| 14 | `theorem` | `thm:adaptive` | Adaptive and sequential probing | `p1_account.tex:87` | `CurrentMM.p1_thm_adaptive_sequential_bound` (L319) | `MachineMarkets.p1_thm_adaptive_sequential` (L107) |
| 15 | `theorem` | `thm:rh` | Finite-horizon Rayleigh--H\"older duality | `p1_account.tex:117` | `CurrentMM.p1_thm_rh_duality` (L338) | `MachineMarkets.p1_thm_rayleigh_holder_duality` (L113) |
| 16 | `corollary` | `cor:garch` | Invariance under impact-induced heteroskedasticity | `p1_account.tex:147` | `CurrentMM.p1_cor_garch_heteroskedastic_invariance` (L371) | `MachineMarkets.p1_cor_garch_invariance` (L119) |
| 17 | `proposition` | `prop:crb` | Cram\'er--Rao benchmark | `p1_mixture.tex:11` | `CurrentMM.p1_prop_crb_benchmark` (L383) | `MachineMarkets.p1_prop_crb_benchmark` (L127) |
| 18 | `theorem` | `thm:twocohort` | Global two-point bound and matching upper bound, $K=2$ | `p1_mixture.tex:45` | `CurrentMM.p1_thm_twocohort_hankel_and_moment_gap` (L399) | `MachineMarkets.p1_thm_twocohort_hankel` (L136) |
| 19 | `theorem` | `thm:kcohort` | $K$-cohort two-point lower bound | `p1_mixture.tex:92` | `CurrentMM.p1_thm_kcohort_lower_bound` (L438) | `MachineMarkets.p1_thm_kcohort_lower_bound` (L145) |
| 20 | `theorem` | `prop:esprit` | Matching upper bound for every $K$ | `p1_mixture.tex:138` | `CurrentMM.p1_thm_esprit_matching_upper_bound` (L453) | `MachineMarkets.p1_prop_esprit_upper_bound` (L151) |
| 21 | `lemma` | `lem:altpair` | Moment-matched cohort pairs | `p1_mixture.tex:175` | `CurrentMM.p1_lem_altpair_moment_matched_wasserstein` (L490) | `MachineMarkets.p1_lem_altpair_moment_matched` (L162) |
| 22 | `theorem` | `thm:general` | Minimax rate for general memory | `p1_mixture.tex:181` | `CurrentMM.p1_thm_general_memory_minimax` (L506) | `MachineMarkets.p1_thm_general_memory_minimax` (L177) |
| 23 | `theorem` | `thm:minphase` | Passive identification: minimum phase | `p1_mixture.tex:235` | `CurrentMM.p1_thm_minphase_passive_identification` (L528) | `MachineMarkets.p1_thm_minphase_identification` (L183) |
| 24 | `theorem` | `prop:passive` | Passive cost | `p1_mixture.tex:241` | `CurrentMM.p1_thm_passive_cost` (L544) | `MachineMarkets.p1_prop_passive_cost` (L189) |
| 25 | `proposition` | `prop:tagged` | Tagged flow removes the barrier | `p1_disclosure.tex:38` | `CurrentMM.p1_prop_tagged_flow_removes_barrier` (L565) | `MachineMarkets.p1_prop_tagged_flow_ident` (L195) |
| 26 | `theorem` | `thm:discvalue` | Value of class-tagged disclosure | `p1_disclosure.tex:48` | `CurrentMM.p1_thm_discvalue_ratio` (L574) | `MachineMarkets.p1_thm_disclosure_value` (L203) |
| 27 | `theorem` | `thm:blind` | Spectral blindness | `p1_disclosure.tex:128` | `CurrentMM.p1_thm_blind_spectral_blindness` (L590) | `MachineMarkets.p1_thm_spectral_blindness` (L211) |
| 28 | `proposition` | `prop:mech` | Mechanical persistence under filtered random walks | `p1_empirics.tex:12` | `CurrentMM.p1_prop_mech_persistence` (L627) | `MachineMarkets.p1_prop_mechanical_persistence` (L219) |
| 29 | `theorem` | `thm:abstain` | Finite-window abstention | `p1_appendix.tex:154` | `CurrentMM.p1_thm_abstain_finite_window` (L640) | `MachineMarkets.p1_thm_abstain_finite_window` (L228) |

## Paper 2 — Transient Amplification & Summed-Gain Guard (`paper2/`)

| # | Environment | Label | Title | LaTeX Source | Mathlib (`ℝ`) Theorem | Core Lean (`Rat`) Theorem |
|---|---|---|---|---|---|---|
| 1 | `proposition` | `prop:jury` | Stability with one cohort | `p2_theory1.tex:15` | `CurrentMM.p2_prop_jury_one_cohort` (L44) | `MachineMarkets.p2_prop_jury_one_cohort` (L13) |
| 2 | `proposition` | `prop:invariance` | Input--output invariance | `p2_theory1.tex:29` | `CurrentMM.p2_prop_input_output_invariance` (L65) | `MachineMarkets.p2_prop_input_output_invariance` (L24) |
| 3 | `proposition` | `prop:ambig` | Quote cost of ambiguity | `p2_theory1.tex:39` | `CurrentMM.p2_prop_ambig_quote_cost` (L74) | `MachineMarkets.p2_prop_ambig_quote_cost` (L32) |
| 4 | `theorem` | `thm:radius` | Safe radius, Kreiss bounds and the failure of the spectral radius | `p2_theory1.tex:57` | `CurrentMM.p2_thm_radius_kreiss` (L90) | `MachineMarkets.p2_thm_radius_kreiss` (L38) |
| 5 | `proposition` | `prop:blind` | Spectral blindness; companion paper | `p2_theory1.tex:94` | `CurrentMM.p2_prop_spectral_blindness_companion` (L109) | `MachineMarkets.p2_prop_spectral_blindness_companion` (L46) |
| 6 | `lemma` | `lem:cm` | No amplification without depth; companion paper | `p2_theory1.tex:105` | `CurrentMM.p2_lem_cm_no_amplification_without_depth` (L122) | `MachineMarkets.p2_lem_cm_no_amplification_without_depth` (L52) |
| 7 | `proposition` | `prop:multi` | Directed cross-impact shrinks the safe radius | `p2_theory1.tex:118` | `CurrentMM.p2_prop_multi_venue_cross_impact` (L139) | `MachineMarkets.p2_prop_multi_venue_cross_impact` (L60) |
| 8 | `theorem` | `thm:t6` | Amplification condition | `p2_theory2.tex:22` | `CurrentMM.p2_thm_t6_amplification_condition` (L168) | `MachineMarkets.p2_thm_t6_amplification_condition` (L66) |
| 9 | `proposition` | `prop:shape` | Shape of the overshoot | `p2_theory2.tex:42` | `CurrentMM.p2_prop_shape_overshoot` (L182) | `MachineMarkets.p2_prop_shape_overshoot` (L75) |
| 10 | `proposition` | `prop:t6m` | One-period amplification margin | `p2_theory2.tex:61` | `CurrentMM.p2_prop_t6m_one_period_margin` (L210) | `MachineMarkets.p2_prop_t6m_one_period_margin` (L84) |
| 11 | `theorem` | `thm:nomom` | Momentum alone cannot make a stable book amplify | `p2_theory2.tex:71` | `CurrentMM.p2_thm_nomom_no_overshoot` (L223) | `MachineMarkets.p2_thm_nomom_no_overshoot` (L93) |
| 12 | `theorem` | `thm:noover` | A sufficient condition for no overshoot | `p2_theory2.tex:79` | `CurrentMM.p2_thm_noover_sufficient_condition` (L239) | `MachineMarkets.p2_thm_noover_sufficient_condition` (L101) |
| 13 | `proposition` | `prop:sum` | Summed response in closed form | `p2_theory2.tex:95` | `CurrentMM.p2_prop_sum_closed_form` (L251) | `MachineMarkets.p2_prop_sum_closed_form` (L108) |
| 14 | `theorem` | `thm:guard` | Summed-gain guard is maximal | `p2_theory2.tex:121` | `CurrentMM.p2_thm_guard_maximal` (L279) | `MachineMarkets.p2_thm_guard_maximal` (L118) |
| 15 | `lemma` | `lem:tail` | Contraction-block tail bound | `p2_theory2.tex:139` | `CurrentMM.p2_lem_tail_contraction` (L296) | `MachineMarkets.p2_lem_tail_contraction` (L123) |
| 16 | `theorem` | `thm:robust` | Robust gain | `p2_theory2.tex:155` | `CurrentMM.p2_thm_robust_gain` (L309) | `MachineMarkets.p2_thm_robust_gain` (L129) |
| 17 | `proposition` | `prop:bridge` | No identification needed; numerical | `p2_theory2.tex:165` | `CurrentMM.p2_prop_bridge_no_identification` (L329) | `MachineMarkets.p2_prop_bridge_no_identification` (L134) |
| 18 | `theorem` | `thm:forward` | Conditional bounded-shock forward solvency | `p2_theory2.tex:216` | `CurrentMM.p2_thm_forward_solvency` (L338) | `MachineMarkets.p2_thm_forward_solvency` (L139) |
| 19 | `proposition` | `prop:dominance` | When the guard beats an eigenvalue rule | `p2_theory2.tex:230` | `CurrentMM.p2_prop_dominance_guard_vs_eigenvalue` (L353) | `MachineMarkets.p2_prop_dominance_guard_vs_eigenvalue` (L145) |
| 20 | `proposition` | `prop:lucas` | Strategic re-optimization reinforces the guard | `p2_theory2.tex:239` | `CurrentMM.p2_prop_lucas_reinforces_guard` (L369) | `MachineMarkets.p2_prop_lucas_reinforces_guard` (L153) |
| 21 | `proposition` | `prop:equil` | Equilibrium transient risk | `p2_equil.tex:10` | `CurrentMM.p2_prop_equil_transient_risk` (L397) | `MachineMarkets.p2_prop_equil_transient_risk` (L159) |
