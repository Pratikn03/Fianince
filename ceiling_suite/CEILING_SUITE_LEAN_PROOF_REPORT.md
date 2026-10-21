# Ceiling Suite — Complete Lean 4 Formal Verification Report

- **Status**: every environment mapped to a kernel-checked declaration (0 `sorry`, 0 `admit`, 0 `native_decide`, 0 unapproved axioms); how much of each statement is formalized is in `COVERAGE.md`
- **Lean Toolchain**: `leanprover/lean4:v4.34.1`
- **Paper 1 (`ceiling_suite/paper1/`)**: 26 / 26 formal environments mapped (see COVERAGE.md for full / conditional / arithmetic)
- **Paper 2 (`ceiling_suite/paper2/`)**: 26 / 26 formal environments mapped (see COVERAGE.md for full / conditional / arithmetic)
- **Total Ceiling Suite Environments**: 52 / 52 mapped to kernel-checked declarations in Mathlib (`ℝ`) and Core Lean 4 (`Rat`); mapping is not semantic equivalence

## Paper 1 — Auditable Memory and Financial Identification Limits (`paper1/`)

| # | Environment | Label | Title | LaTeX Source | Mathlib (`ℝ`) Theorem | Core Lean (`Rat`) Theorem |
|---|---|---|---|---|---|---|
| 1 | `lemma` | `lem:micro` | Filtering and learning microfoundations | `p1_front.tex:146` | `CurrentMM.p1_prop_kalman_memory, CurrentMM.p1_prop_ogd_memory` (L46) | `MachineMarkets.p1_prop_kalman_memory, MachineMarkets.p1_prop_ogd_memory` (L13) |
| 2 | `lemma` | `lem:cm` | Positive price-response geometry | `p1_front.tex:160` | `CurrentMM.p1_lem_cm_positive_response` (L96) | `MachineMarkets.p1_lem_cm_positive_geometry` (L29) |
| 3 | `theorem` | `thm:merged` | Merged rate--weight equivalence | `p1_ident.tex:5` | `CurrentMM.p1_thm_merged_equivalence_and_resolvent` (L123) | `MachineMarkets.p1_thm_merged_equivalence` (L38) |
| 4 | `theorem` | `thm:quantity` | Sharp probing-resource orders for a known symmetric pair | `p1_ident.tex:33` | `CurrentMM.p1_thm_quantity_sharp_orders` (L143) | `MachineMarkets.p1_thm_quantity_orders` (L44) |
| 5 | `lemma` | `lem:toeplitz` | Fair execution | `p1_ident.tex:87` | `CurrentMM.p1_lem_toeplitz_fair_execution` (L161) | `MachineMarkets.p1_lem_toeplitz_fair_execution` (L53) |
| 6 | `theorem` | `thm:cap` | Sharp robust quantity cap from cash and margin | `p1_ident.tex:99` | `CurrentMM.p1_thm_cap_counterparty_margin` (L191) | `MachineMarkets.p1_thm_cap_robust_quantity` (L60) |
| 7 | `proposition` | `prop:disclosure` | Exact financial disclosure changes the experiment | `p1_ident.tex:114` | `CurrentMM.p1_prop_disclosure_third_mark` (L221) | `MachineMarkets.p1_prop_disclosure_changes_experiment` (L66) |
| 8 | `lemma` | `thm:capital` | Time-domain Toeplitz coercivity: capital order for funded probes | `p1_ident.tex:122` | `CurrentMM.p1_thm_capital_funded_probes` (L235) | `MachineMarkets.p1_thm_capital_order` (L74) |
| 9 | `proposition` | `prop:tri` | Tri-region partition and finite-session resolution floor | `p1_account.tex:13` | `CurrentMM.p1_prop_tri_region_partition` (L285) | `MachineMarkets.p1_prop_tri_region_floor` (L93) |
| 10 | `theorem` | `thm:spectral` | Spectral dissipation lower bound | `p1_account.tex:65` | `CurrentMM.p1_thm_spectral_dissipation_bound` (L299) | `MachineMarkets.p1_thm_spectral_dissipation` (L99) |
| 11 | `theorem` | `thm:adaptive` | Adaptive and sequential probing | `p1_account.tex:92` | `CurrentMM.p1_thm_adaptive_sequential_bound` (L319) | `MachineMarkets.p1_thm_adaptive_sequential` (L107) |
| 12 | `theorem` | `thm:rh` | Finite-horizon Rayleigh--H\"older duality | `p1_account.tex:122` | `CurrentMM.p1_thm_rh_duality, CurrentMM.is_rh_radius_bound, CurrentMM.is_rh_chain` (L338) | `MachineMarkets.p1_thm_rayleigh_holder_duality` (L113) |
| 13 | `corollary` | `cor:garch` | Invariance under impact-induced heteroskedasticity | `p1_account.tex:164` | `CurrentMM.p1_cor_garch_heteroskedastic_invariance` (L371) | `MachineMarkets.p1_cor_garch_invariance` (L119) |
| 14 | `proposition` | `prop:crb` | Cram\'er--Rao benchmark | `p1_mixture.tex:11` | `CurrentMM.p1_prop_crb_benchmark` (L383) | `MachineMarkets.p1_prop_crb_benchmark` (L127) |
| 15 | `theorem` | `thm:twocohort` | Global two-point bound and matching upper bound, $K=2$ | `p1_mixture.tex:45` | `CurrentMM.p1_thm_twocohort_hankel_and_moment_gap` (L399) | `MachineMarkets.p1_thm_twocohort_hankel` (L136) |
| 16 | `theorem` | `thm:kcohort` | $K$-cohort two-point lower bound | `p1_mixture.tex:100` | `CurrentMM.p1_thm_kcohort_lower_bound` (L438) | `MachineMarkets.p1_thm_kcohort_lower_bound` (L145) |
| 17 | `theorem` | `prop:esprit` | Matching upper bound for every $K$ | `p1_mixture.tex:147` | `CurrentMM.p1_thm_esprit_matching_upper_bound` (L453) | `MachineMarkets.p1_prop_esprit_upper_bound` (L151) |
| 18 | `lemma` | `lem:altpair` | Moment-matched cohort pairs | `p1_mixture.tex:184` | `CurrentMM.p1_lem_altpair_moment_matched_wasserstein` (L490) | `MachineMarkets.p1_lem_altpair_moment_matched` (L162) |
| 19 | `theorem` | `thm:general` | Minimax rate for general memory | `p1_mixture.tex:190` | `CurrentMM.p1_thm_general_memory_minimax` (L506) | `MachineMarkets.p1_thm_general_memory_minimax` (L177) |
| 20 | `theorem` | `thm:minphase` | Passive identification: minimum phase | `p1_mixture.tex:244` | `CurrentMM.p1_thm_minphase_passive_identification` (L528) | `MachineMarkets.p1_thm_minphase_identification` (L183) |
| 21 | `theorem` | `prop:passive` | Passive cost | `p1_mixture.tex:250` | `CurrentMM.p1_thm_passive_cost` (L544) | `MachineMarkets.p1_prop_passive_cost` (L189) |
| 22 | `proposition` | `prop:tagged` | Tagged flow removes the barrier | `p1_disclosure.tex:38` | `CurrentMM.p1_prop_tagged_flow_removes_barrier, CurrentMM.is_iv_det_pos` (L565) | `MachineMarkets.p1_prop_tagged_flow_ident` (L195) |
| 23 | `theorem` | `thm:discvalue` | Value of class-tagged disclosure | `p1_disclosure.tex:56` | `CurrentMM.p1_thm_discvalue_ratio` (L574) | `MachineMarkets.p1_thm_disclosure_value` (L203) |
| 24 | `theorem` | `thm:blind` | Spectral blindness | `p1_disclosure.tex:136` | `CurrentMM.p1_thm_blind_spectral_blindness` (L590) | `MachineMarkets.p1_thm_spectral_blindness` (L211) |
| 25 | `theorem` | `thm:abstain` | Finite-window abstention | `p1_appendix.tex:157` | `CurrentMM.p1_thm_abstain_finite_window` (L640) | `MachineMarkets.p1_thm_abstain_finite_window` (L228) |
| 26 | `proposition` | `prop:passive0` | Passive distinction with zero controlled quantity | `p1_appendix.tex:173` | `CurrentMM.p1_prop_passive0_three_step_blocks` (L254) | `MachineMarkets.p1_prop_passive0_distinction` (L79) |

## Paper 2 — Transient Amplification & Summed-Gain Guard (`paper2/`)

| # | Environment | Label | Title | LaTeX Source | Mathlib (`ℝ`) Theorem | Core Lean (`Rat`) Theorem |
|---|---|---|---|---|---|---|
| 1 | `proposition` | `prop:jury` | Stability with one cohort | `p2_theory1.tex:15` | `CurrentMM.p2_prop_jury_one_cohort` (L50) | `MachineMarkets.p2_prop_jury_one_cohort` (L13) |
| 2 | `proposition` | `prop:invariance` | Input--output invariance | `p2_theory1.tex:29` | `CurrentMM.p2_prop_input_output_invariance` (L71) | `MachineMarkets.p2_prop_input_output_invariance` (L24) |
| 3 | `proposition` | `prop:ambig` | Quote cost of ambiguity | `p2_theory1.tex:39` | `CurrentMM.p2_prop_ambig_quote_cost` (L80) | `MachineMarkets.p2_prop_ambig_quote_cost` (L32) |
| 4 | `theorem` | `thm:radius` | Safe radius, Kreiss bounds and the failure of the spectral radius | `p2_theory1.tex:57` | `CurrentMM.p2_thm_radius_kreiss` (L96) | `MachineMarkets.p2_thm_radius_kreiss` (L38) |
| 5 | `proposition` | `prop:multi` | Directed cross-impact shrinks the safe radius | `p2_theory1.tex:114` | `CurrentMM.p2_prop_multi_venue_cross_impact` (L145) | `MachineMarkets.p2_prop_multi_venue_cross_impact` (L60) |
| 6 | `theorem` | `thm:peak` | Peak overshoot: depletion versus momentum | `p2_t6.tex:24` | `CurrentMM.p2_thm_t6_amplification_condition, CurrentMM.p2_prop_shape_overshoot, CurrentMM.is_confluent_stationary, CurrentMM.p2_prop_t6m_one_period_margin, CurrentMM.p2_thm_nomom_no_overshoot, CurrentMM.is_momentum_residues, CurrentMM.p2_thm_noover_sufficient_condition` (L174) | `MachineMarkets.p2_thm_t6_amplification_condition, MachineMarkets.p2_prop_shape_overshoot, MachineMarkets.p2_prop_t6m_one_period_margin, MachineMarkets.p2_thm_nomom_no_overshoot, MachineMarkets.p2_thm_noover_sufficient_condition` (L66) |
| 7 | `theorem` | `thm:sum` | Summed response in closed form | `p2_t6.tex:73` | `CurrentMM.p2_prop_sum_closed_form, CurrentMM.is_summed_response_closed_form` (L257) | `MachineMarkets.p2_prop_sum_closed_form` (L108) |
| 8 | `example` | `ex:witness` | An exact ambiguity witness | `p2_infosafety.tex:20` | `CurrentMM.p2_ex_witness` (L718) | `MachineMarkets.p2_ex_witness` (L270) |
| 9 | `proposition` | `prop:twoworld` | Unavoidable loss of safe capacity | `p2_infosafety.tex:24` | `CurrentMM.p2_prop_twoworld, CurrentMM.is_two_world_capacity_loss, CurrentMM.is_two_world_attained` (L790) | `MachineMarkets.p2_prop_twoworld` (L308) |
| 10 | `theorem` | `thm:window` | Finite-window certification | `p2_infosafety.tex:42` | `CurrentMM.p2_thm_window` (L844) | `MachineMarkets.p2_thm_window` (L313) |
| 11 | `lemma` | `lem:certnum` | Certified endpoints | `p2_infosafety.tex:55` | `CurrentMM.is_upper_bound, CurrentMM.is_lower_bound` (L509) | `MachineMarkets.p2_lem_certnum` (L361) |
| 12 | `theorem` | `thm:certcost` | Certification at the parametric rate | `p2_infosafety.tex:63` | `CurrentMM.p2_thm_certcost, CurrentMM.is_iter_bound, CurrentMM.is_tail_bound` (L1021) | `MachineMarkets.p2_thm_certcost` (L323) |
| 13 | `proposition` | `prop:hotelling` | Certification with unknown covariance | `p2_infosafety.tex:99` | `CurrentMM.is_corrSum_ge, CurrentMM.is_o1_margin_too_small` (L681) | `MachineMarkets.p2_prop_hotelling` (L370) |
| 14 | `lemma` | `thm:guard` | Summed-gain guard is maximal | `p2_guard.tex:13` | `CurrentMM.p2_thm_guard_maximal, CurrentMM.is_per_period_upper, CurrentMM.is_per_period_attained, CurrentMM.is_budget_upper, CurrentMM.is_budget_attained` (L293) | `MachineMarkets.p2_thm_guard_maximal` (L118) |
| 15 | `lemma` | `lem:tail` | Contraction-block tail bound | `p2_guard.tex:31` | `CurrentMM.p2_lem_tail_contraction` (L348) | `MachineMarkets.p2_lem_tail_contraction` (L123) |
| 16 | `theorem` | `thm:robust` | Robust gain | `p2_guard.tex:49` | `CurrentMM.p2_thm_robust_gain` (L361) | `MachineMarkets.p2_thm_robust_gain` (L129) |
| 17 | `lemma` | `lem:sound` | Soundness of compatible-set guards | `p2_guard.tex:65` | `CurrentMM.p2_lem_sound` (L1065) | `MachineMarkets.p2_lem_sound` (L332) |
| 18 | `theorem` | `thm:robustguard` | Optimal uncertainty-aware admission | `p2_guard.tex:69` | `CurrentMM.p2_thm_robustguard, CurrentMM.is_robust_safe_set_eq, CurrentMM.is_alphaStar_isGreatest, CurrentMM.is_infeasible_of_cI_neg` (L1127) | `MachineMarkets.p2_thm_robustguard` (L338) |
| 19 | `proposition` | `prop:venue` | Venue mode | `p2_guard.tex:85` | `CurrentMM.is_unsafe_between, CurrentMM.is_worst_corner, CurrentMM.is_venue_example` (L358) | `MachineMarkets.p2_prop_venue` (L377) |
| 20 | `theorem` | `thm:venuebb` | Certified admission without monotonicity | `p2_guard.tex:97` | `CurrentMM.is_classify_safe_sound, CurrentMM.is_classify_unsafe_sound, CurrentMM.is_largest_safe_exists` (L441) | `MachineMarkets.p2_thm_venuebb` (L388) |
| 21 | `theorem` | `thm:forward` | Conditional bounded-shock forward solvency | `p2_guard.tex:154` | `CurrentMM.p2_thm_forward_solvency, CurrentMM.is_buffer_after_step, CurrentMM.is_scenario` (L390) | `MachineMarkets.p2_thm_forward_solvency` (L139) |
| 22 | `proposition` | `prop:dominance` | When an eigenvalue rule admits an uncertified level | `p2_guard.tex:170` | `CurrentMM.p2_prop_dominance_guard_vs_eigenvalue` (L405) | `MachineMarkets.p2_prop_dominance_guard_vs_eigenvalue` (L145) |
| 23 | `proposition` | `prop:lucas` | Strategic re-optimization reinforces the guard | `p2_guard.tex:179` | `CurrentMM.p2_prop_lucas_reinforces_guard` (L421) | `MachineMarkets.p2_prop_lucas_reinforces_guard` (L153) |
| 24 | `theorem` | `thm:disclosure` | Decision value of disclosure | `p2_disclosure.tex:5` | `CurrentMM.p2_thm_disclosure, CurrentMM.is_disclosure_monotone, CurrentMM.is_disclosure_strict, CurrentMM.is_intersection_admits_more` (L1181) | `MachineMarkets.p2_thm_disclosure` (L346) |
| 25 | `proposition` | `prop:equil` | Equilibrium transient risk | `p2_equil.tex:10` | `CurrentMM.p2_prop_equil_transient_risk, CurrentMM.is_depth_solution_increasing, CurrentMM.is_depth_eq_lt_sp, CurrentMM.is_depth_rebate_identified` (L449) | `MachineMarkets.p2_prop_equil_transient_risk` (L159) |
| 26 | `proposition` | `prop:probe` | Anytime-valid probing | `p2_appendix.tex:137` | `CurrentMM.is_sequential_rule_correct` (L704) | `MachineMarkets.p2_prop_probe` (L393) |

## Phase 7 — Unified Foundational Bridge Theorems (Paper 1 ↔ Paper 2)

| # | Result | Title | Mathlib (`ℝ`) Theorem | Core Lean (`Rat`) Theorem |
|---|---|---|---|---|
| 1 | `Result A` | Result A: Impossibility of Cohort-Specific Risk Control from Public Data | `CurrentMM.foundational_result_A_impossibility` (L504) | `MachineMarkets.foundational_result_A_impossibility` (L167) |
| 2 | `Result B` | Result B: Disclosure-Enabled Control Improvement | `CurrentMM.foundational_result_B_disclosure_control` (L671) | `MachineMarkets.foundational_result_B_disclosure_control` (L258) |
| 3 | `Result C` | Result C: Active Probing vs. Transient Excursion Tradeoff | `CurrentMM.foundational_result_C_probing_control_tradeoff` (L697) | `MachineMarkets.foundational_result_C_probing_control_tradeoff` (L263) |
