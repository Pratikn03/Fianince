# Ceiling Suite — Lean declaration mapping audit

- **Status**: MAPPING_AUDIT_INCOMPLETE. Existing declaration references checked; no fresh Lean build or full semantic equivalence is claimed.
- **Unmapped labels**: none
- **Revised statements requiring semantic review**: prop:endogenous_kappa, prop:esprit, thm:minphase, prop:strategic, prop:target, prop:inventory_S, thm:window, thm:certcost, thm:forward, prop:driftguard
- **Lean Toolchain**: `leanprover/lean4:v4.34.1`
- **Paper 1**: 49 / 49 current formal environments have an existing name mapping.
- **Paper 2**: 33 / 33 current formal environments have an existing name mapping.
- Run with `--require-complete` to fail if unmapped or revised statements remain. A successful default run means the audit was generated, not that manuscript formalization is complete.

## Paper 1 — Auditable Memory and Financial Identification Limits (`paper1/`)

| # | Environment | Label | Title | LaTeX Source | Mathlib (`ℝ`) Theorem | Core Lean (`Rat`) Theorem |
|---|---|---|---|---|---|---|
| 1 | `lemma` | `lem:micro` | Two motivating examples: filtering and learning | `p1_front.tex:339` | `CurrentMM.p1_prop_kalman_memory, CurrentMM.p1_prop_ogd_memory` (L52) | `MachineMarkets.p1_prop_kalman_memory, MachineMarkets.p1_prop_ogd_memory` (L13) |
| 2 | `lemma` | `lem:cm` | Positive price-response geometry | `p1_front.tex:357` | `CurrentMM.p1_lem_cm_positive_response` (L102) | `MachineMarkets.p1_lem_cm_positive_geometry` (L29) |
| 3 | `theorem` | `thm:merged` | Merged rate--weight equivalence | `p1_ident.tex:5` | `CurrentMM.p1_thm_merged_equivalence_and_resolvent` (L129) | `MachineMarkets.p1_thm_merged_equivalence` (L38) |
| 4 | `proposition` | `prop:endogenous_kappa` | Conditional endogenous-pricing invariance | `p1_ident.tex:30` | `CurrentMM.p1_endogenous_contraction_sensitivity` (L6) | `NOT_SEPARATELY_FORMALIZED` (LNone) |
| 5 | `theorem` | `thm:inventory` | Price impact and persistence in an inventory equilibrium | `p1_ident.tex:64` | `CurrentMM.p1_inventory_foc, CurrentMM.p1_inventory_innovation, CurrentMM.p1_inventory_benchmark, CurrentMM.p1_inventory_small_feedback` (L55) | `NOT_SEPARATELY_FORMALIZED` (LNone) |
| 6 | `theorem` | `thm:eqreduced` | The equilibrium is the paper's closed loop | `p1_ident.tex:98` | `CurrentMM.p1_eq_realize_D, CurrentMM.p1_eq_realize_dealer, CurrentMM.p1_eq_scaled_cohort` (L67) | `NOT_SEPARATELY_FORMALIZED` (LNone) |
| 7 | `corollary` | `cor:eqdisclosure` | Disclosure in equilibrium | `p1_ident.tex:130` | `CurrentMM.p1_prop_tagged_flow_removes_barrier, CurrentMM.p1_thm_discvalue_ratio` (L571) | `NOT_SEPARATELY_FORMALIZED` (LNone) |
| 8 | `theorem` | `thm:fragility` | Fragility: where liquidity disappears | `p1_ident.tex:140` | `CurrentMM.p1_fragility_feedback_bound, CurrentMM.p1_fragility_benchmark_bound, CurrentMM.p1_fragility_K_bound` (L99) | `NOT_SEPARATELY_FORMALIZED` (LNone) |
| 9 | `theorem` | `thm:eqinv` | Equilibrium invariance | `p1_ident.tex:179` | `CurrentMM.p1_eqAggFlow_kernel, CurrentMM.p1_eqAggFlow_of_kernel, CurrentMM.p1_kernel_of_eqAggFlow, CurrentMM.p1_eq_market_invariance, CurrentMM.p1_eq_insider_profit_invariance, CurrentMM.p1_eq_group_level_differs` (L64) | `NOT_SEPARATELY_FORMALIZED` (LNone) |
| 10 | `theorem` | `thm:insider` | A strategic insider in the inventory equilibrium | `p1_ident.tex:198` | `CurrentMM.p1_insider_reduced_form, CurrentMM.p1_insider_best_response, CurrentMM.p1_insider_kyle_limit, CurrentMM.p1_insider_posterior_variance` (L31) | `NOT_SEPARATELY_FORMALIZED` (LNone) |
| 11 | `theorem` | `thm:quantity` | Sharp probing-resource orders for a known symmetric pair | `p1_ident.tex:250` | `CurrentMM.p1_thm_quantity_sharp_orders` (L149) | `MachineMarkets.p1_thm_quantity_orders` (L44) |
| 12 | `lemma` | `lem:toeplitz` | Fair execution | `p1_ident.tex:307` | `CurrentMM.p1_lem_toeplitz_fair_execution` (L167) | `MachineMarkets.p1_lem_toeplitz_fair_execution` (L53) |
| 13 | `theorem` | `thm:cap` | Sharp robust quantity cap from cash and margin | `p1_ident.tex:321` | `CurrentMM.p1_thm_cap_counterparty_margin` (L197) | `MachineMarkets.p1_thm_cap_robust_quantity` (L60) |
| 14 | `proposition` | `prop:disclosure` | Exact financial disclosure changes the experiment | `p1_ident.tex:339` | `CurrentMM.p1_prop_disclosure_third_mark` (L227) | `MachineMarkets.p1_prop_disclosure_changes_experiment` (L66) |
| 15 | `lemma` | `thm:capital` | Time-domain Toeplitz coercivity: capital order for funded probes | `p1_ident.tex:349` | `CurrentMM.p1_thm_capital_funded_probes` (L241) | `MachineMarkets.p1_thm_capital_order` (L74) |
| 16 | `proposition` | `prop:primitives` | Identification in economic primitives | `p1_ident.tex:377` | `CurrentMM.p1_prop_primitives` (L662) | `MachineMarkets.p1_prop_primitives` (L240) |
| 17 | `proposition` | `prop:tied` | Intensity tied to information quality | `p1_ident.tex:397` | `CurrentMM.p1_prop_tied` (L672) | `MachineMarkets.p1_prop_tied` (L245) |
| 18 | `proposition` | `prop:tri` | Tri-region partition and finite-session resolution floor | `p1_account.tex:15` | `CurrentMM.p1_prop_tri_region_partition` (L291) | `MachineMarkets.p1_prop_tri_region_floor` (L93) |
| 19 | `theorem` | `thm:spectral` | Spectral dissipation lower bound | `p1_account.tex:69` | `CurrentMM.p1_thm_spectral_dissipation_bound` (L305) | `MachineMarkets.p1_thm_spectral_dissipation` (L99) |
| 20 | `theorem` | `thm:adaptive` | Adaptive and sequential probing | `p1_account.tex:101` | `CurrentMM.p1_thm_adaptive_sequential_bound` (L325) | `MachineMarkets.p1_thm_adaptive_sequential` (L107) |
| 21 | `theorem` | `thm:rh` | Finite-horizon Rayleigh--H\"older duality | `p1_account.tex:133` | `CurrentMM.p1_thm_rh_duality, CurrentMM.is_rh_radius_bound, CurrentMM.is_rh_chain` (L344) | `MachineMarkets.p1_thm_rayleigh_holder_duality` (L113) |
| 22 | `corollary` | `cor:garch` | Invariance under impact-induced heteroskedasticity | `p1_account.tex:177` | `CurrentMM.p1_cor_garch_heteroskedastic_invariance` (L377) | `MachineMarkets.p1_cor_garch_invariance` (L119) |
| 23 | `proposition` | `prop:crb` | Cram\'er--Rao benchmark | `p1_mixture.tex:11` | `CurrentMM.p1_prop_crb_benchmark` (L389) | `MachineMarkets.p1_prop_crb_benchmark` (L127) |
| 24 | `theorem` | `thm:twocohort` | Global two-point bound and matching upper bound, $K=2$ | `p1_mixture.tex:52` | `CurrentMM.p1_thm_twocohort_hankel_and_moment_gap` (L405) | `MachineMarkets.p1_thm_twocohort_hankel` (L136) |
| 25 | `theorem` | `thm:kcohort` | $K$-cohort two-point lower bound | `p1_mixture.tex:109` | `CurrentMM.p1_thm_kcohort_lower_bound` (L444) | `MachineMarkets.p1_thm_kcohort_lower_bound` (L145) |
| 26 | `theorem` | `prop:esprit` | Matching upper bound for every $K$ | `p1_mixture.tex:162` | `CurrentMM.p1_thm_esprit_matching_upper_bound` (L459) | `MachineMarkets.p1_prop_esprit_upper_bound` (L151) |
| 27 | `corollary` | `cor:unknown_primitives` | Unknown primitives cost nothing in the rate | `p1_mixture.tex:178` | `CurrentMM.p1_cor_unknown_primitives` (L801) | `MachineMarkets.p1_cor_unknown_primitives` (L309) |
| 28 | `theorem` | `thm:uniformw1` | Uniform rate without separation | `p1_mixture.tex:246` | `CurrentMM.p1_thm_uniformw1` (L686) | `MachineMarkets.p1_thm_uniformw1` (L250) |
| 29 | `lemma` | `lem:altpair` | Moment-matched cohort pairs | `p1_mixture.tex:270` | `CurrentMM.p1_lem_altpair_moment_matched_wasserstein` (L496) | `MachineMarkets.p1_lem_altpair_moment_matched` (L162) |
| 30 | `theorem` | `thm:general` | Minimax rate for general memory | `p1_mixture.tex:276` | `CurrentMM.p1_thm_general_memory_minimax` (L512) | `MachineMarkets.p1_thm_general_memory_minimax` (L177) |
| 31 | `theorem` | `thm:minphase` | Passive identification: minimum phase | `p1_mixture.tex:335` | `CurrentMM.p1_thm_minphase_passive_identification` (L534) | `MachineMarkets.p1_thm_minphase_identification` (L183) |
| 32 | `theorem` | `prop:passive` | Passive cost | `p1_mixture.tex:347` | `CurrentMM.p1_thm_passive_cost` (L550) | `MachineMarkets.p1_prop_passive_cost` (L189) |
| 33 | `proposition` | `prop:tagged` | Tagged flow removes the barrier | `p1_disclosure.tex:38` | `CurrentMM.p1_prop_tagged_flow_removes_barrier, CurrentMM.is_iv_det_pos` (L571) | `MachineMarkets.p1_prop_tagged_flow_ident` (L195) |
| 34 | `theorem` | `thm:discvalue` | Value of class-tagged disclosure | `p1_disclosure.tex:59` | `CurrentMM.p1_thm_discvalue_ratio` (L580) | `MachineMarkets.p1_thm_disclosure_value` (L203) |
| 35 | `proposition` | `prop:strategic` | Conditional limits of three evasion arguments | `p1_disclosure.tex:76` | `CurrentMM.p1_sybil_share_count_bound, CurrentMM.p1_camouflage_unprofitable` (L16) | `NOT_SEPARATELY_FORMALIZED` (LNone) |
| 36 | `proposition` | `prop:choice` | When an audit trail is chosen | `p1_disclosure.tex:134` | `CurrentMM.p1_prop_choice` (L716) | `MachineMarkets.p1_prop_choice` (L266) |
| 37 | `proposition` | `prop:target` | Supervisory separation: market-wide versus targeted intervention | `p1_disclosure.tex:147` | `CurrentMM.p1_prop_target` (L725) | `MachineMarkets.p1_prop_target` (L271) |
| 38 | `proposition` | `prop:robust_gate` | A robust scalar disclosure gate | `p1_disclosure.tex:218` | `CurrentMM.p1_supervisory_gaussian_unsafe_halt, CurrentMM.p1_supervisory_gaussian_unsafe_halt_budget` (L34) | `NOT_SEPARATELY_FORMALIZED` (LNone) |
| 39 | `proposition` | `prop:priced_decision` | No-data action and information purchase | `p1_disclosure.tex:248` | `CurrentMM.p1_no_data_throttle_optimal, CurrentMM.p1_no_data_capped_halt_optimal, CurrentMM.p1_information_purchase_break_even, CurrentMM.p1_optional_information_value_nonnegative` (L65) | `NOT_SEPARATELY_FORMALIZED` (LNone) |
| 40 | `theorem` | `thm:blind` | Spectral blindness | `p1_disclosure.tex:409` | `CurrentMM.p1_thm_blind_spectral_blindness` (L596) | `MachineMarkets.p1_thm_spectral_blindness` (L211) |
| 41 | `theorem` | `thm:abstain` | Finite-window abstention | `p1_appendix.tex:232` | `CurrentMM.p1_thm_abstain_finite_window` (L646) | `MachineMarkets.p1_thm_abstain_finite_window` (L228) |
| 42 | `proposition` | `prop:passive0` | Passive distinction with zero controlled quantity | `p1_appendix.tex:248` | `CurrentMM.p1_prop_passive0_three_step_blocks` (L260) | `MachineMarkets.p1_prop_passive0_distinction` (L79) |
| 43 | `theorem` | `thm:rents` | Rents from a misjudged aggregate response | `p1_appendix.tex:394` | `CurrentMM.p1_rents_symmetrize, CurrentMM.p1_rents_optimum, CurrentMM.p1_rents_value` (L101) | `NOT_SEPARATELY_FORMALIZED` (LNone) |
| 44 | `theorem` | `thm:eqhalt` | Targeted intervention in equilibrium | `p1_appendix.tex:408` | `CurrentMM.p1_halt_kernel_gap, CurrentMM.p1_halt_kernel_bound` (L153) | `NOT_SEPARATELY_FORMALIZED` (LNone) |
| 45 | `lemma` | `fhc:capacity` | Sharp prior bounds and exact prefunded capacity | `p1_appendix.tex:1145` | `CurrentMM.p1_fhc_capacity` (L749) | `MachineMarkets.p1_fhc_capacity` (L279) |
| 46 | `lemma` | `fhc:nodata-chance` | No data at the same error budget | `p1_appendix.tex:1198` | `CurrentMM.p1_fhc_nodata_chance` (L761) | `MachineMarkets.p1_fhc_nodata_chance` (L284) |
| 47 | `theorem` | `fhc:decision` | Uniform cost-aware finite-horizon decision | `p1_appendix.tex:1223` | `CurrentMM.p1_fhc_decision` (L773) | `MachineMarkets.p1_fhc_decision` (L291) |
| 48 | `theorem` | `fhc:pair` | A two-cohort identification obstruction under the same observations | `p1_appendix.tex:1302` | `CurrentMM.p1_fhc_pair` (L781) | `MachineMarkets.p1_fhc_pair` (L296) |
| 49 | `corollary` | `fhc:priced` | A priced separation | `p1_appendix.tex:1372` | `CurrentMM.p1_fhc_priced` (L794) | `MachineMarkets.p1_fhc_priced` (L304) |

## Paper 2 — Transient Amplification & Summed-Gain Guard (`paper2/`)

| # | Environment | Label | Title | LaTeX Source | Mathlib (`ℝ`) Theorem | Core Lean (`Rat`) Theorem |
|---|---|---|---|---|---|---|
| 1 | `proposition` | `prop:jury` | Stability with one cohort | `p2_theory1.tex:15` | `CurrentMM.p2_prop_jury_one_cohort` (L50) | `MachineMarkets.p2_prop_jury_one_cohort` (L13) |
| 2 | `proposition` | `prop:invariance` | Input--output invariance | `p2_theory1.tex:29` | `CurrentMM.p2_prop_input_output_invariance` (L71) | `MachineMarkets.p2_prop_input_output_invariance` (L24) |
| 3 | `proposition` | `prop:inventory_S` | Summed response with carried cohort inventory | `p2_theory1.tex:39` | `CurrentMM.p2_prop_inventory_S` (L868) | `MachineMarkets.p2_prop_inventory_S` (L398) |
| 4 | `proposition` | `prop:ambig` | Quote cost of ambiguity | `p2_theory1.tex:56` | `CurrentMM.p2_prop_ambig_quote_cost` (L80) | `MachineMarkets.p2_prop_ambig_quote_cost` (L32) |
| 5 | `theorem` | `thm:radius` | Safe radius, Kreiss bounds and the failure of the spectral radius | `p2_theory1.tex:74` | `CurrentMM.p2_thm_radius_kreiss` (L96) | `MachineMarkets.p2_thm_radius_kreiss` (L38) |
| 6 | `proposition` | `prop:multi` | Directed cross-impact shrinks the safe radius | `p2_theory1.tex:131` | `CurrentMM.p2_prop_multi_venue_cross_impact` (L145) | `MachineMarkets.p2_prop_multi_venue_cross_impact` (L60) |
| 7 | `theorem` | `thm:peak` | Peak overshoot: depletion versus momentum | `p2_t6.tex:24` | `CurrentMM.p2_thm_t6_amplification_condition, CurrentMM.p2_prop_shape_overshoot, CurrentMM.is_confluent_stationary, CurrentMM.p2_prop_t6m_one_period_margin, CurrentMM.p2_thm_nomom_no_overshoot, CurrentMM.is_momentum_residues, CurrentMM.p2_thm_noover_sufficient_condition` (L174) | `MachineMarkets.p2_thm_t6_amplification_condition, MachineMarkets.p2_prop_shape_overshoot, MachineMarkets.p2_prop_t6m_one_period_margin, MachineMarkets.p2_thm_nomom_no_overshoot, MachineMarkets.p2_thm_noover_sufficient_condition` (L66) |
| 8 | `theorem` | `thm:sum` | Summed response in closed form | `p2_t6.tex:73` | `CurrentMM.p2_prop_sum_closed_form, CurrentMM.is_summed_response_closed_form` (L257) | `MachineMarkets.p2_prop_sum_closed_form` (L108) |
| 9 | `example` | `ex:witness` | An exact ambiguity witness | `p2_infosafety.tex:20` | `CurrentMM.p2_ex_witness` (L718) | `MachineMarkets.p2_ex_witness` (L270) |
| 10 | `proposition` | `prop:twoworld` | Unavoidable loss of safe capacity | `p2_infosafety.tex:24` | `CurrentMM.p2_prop_twoworld, CurrentMM.is_two_world_capacity_loss, CurrentMM.is_two_world_attained` (L790) | `MachineMarkets.p2_prop_twoworld` (L308) |
| 11 | `theorem` | `thm:window` | Finite-window certification | `p2_infosafety.tex:42` | `CurrentMM.p2_thm_window` (L844) | `MachineMarkets.p2_thm_window` (L313) |
| 12 | `lemma` | `lem:certnum` | Certified endpoints | `p2_infosafety.tex:55` | `CurrentMM.is_upper_bound, CurrentMM.is_lower_bound` (L509) | `MachineMarkets.p2_lem_certnum` (L361) |
| 13 | `theorem` | `thm:certcost` | Certification cost of the summed response | `p2_infosafety.tex:63` | `CurrentMM.p2_thm_certcost, CurrentMM.is_iter_bound, CurrentMM.is_tail_bound` (L1021) | `MachineMarkets.p2_thm_certcost` (L323) |
| 14 | `proposition` | `prop:hotelling` | Certification with unknown covariance | `p2_infosafety.tex:100` | `CurrentMM.is_corrSum_ge, CurrentMM.is_o1_margin_too_small` (L681) | `MachineMarkets.p2_prop_hotelling` (L370) |
| 15 | `lemma` | `thm:guard` | Summed-gain guard is maximal | `p2_guard.tex:13` | `CurrentMM.p2_thm_guard_maximal, CurrentMM.is_per_period_upper, CurrentMM.is_per_period_attained, CurrentMM.is_budget_upper, CurrentMM.is_budget_attained` (L293) | `MachineMarkets.p2_thm_guard_maximal` (L118) |
| 16 | `lemma` | `lem:tail` | Contraction-block tail bound | `p2_guard.tex:31` | `CurrentMM.p2_lem_tail_contraction` (L348) | `MachineMarkets.p2_lem_tail_contraction` (L123) |
| 17 | `theorem` | `thm:robust` | Robust gain | `p2_guard.tex:49` | `CurrentMM.p2_thm_robust_gain` (L361) | `MachineMarkets.p2_thm_robust_gain` (L129) |
| 18 | `lemma` | `lem:sound` | Soundness of compatible-set guards | `p2_guard.tex:65` | `CurrentMM.p2_lem_sound` (L1065) | `MachineMarkets.p2_lem_sound` (L332) |
| 19 | `theorem` | `thm:robustguard` | Optimal uncertainty-aware admission | `p2_guard.tex:69` | `CurrentMM.p2_thm_robustguard, CurrentMM.is_robust_safe_set_eq, CurrentMM.is_alphaStar_isGreatest, CurrentMM.is_infeasible_of_cI_neg` (L1127) | `MachineMarkets.p2_thm_robustguard` (L338) |
| 20 | `proposition` | `prop:venue` | Venue mode | `p2_guard.tex:85` | `CurrentMM.is_unsafe_between, CurrentMM.is_worst_corner, CurrentMM.is_venue_example` (L358) | `MachineMarkets.p2_prop_venue` (L377) |
| 21 | `theorem` | `thm:venuebb` | Certified admission without monotonicity | `p2_guard.tex:97` | `CurrentMM.is_classify_safe_sound, CurrentMM.is_classify_unsafe_sound, CurrentMM.is_largest_safe_exists` (L441) | `MachineMarkets.p2_thm_venuebb` (L388) |
| 22 | `theorem` | `thm:forward` | Conditional bounded-shock forward solvency | `p2_guard.tex:154` | `CurrentMM.p2_thm_forward_solvency, CurrentMM.is_buffer_after_step, CurrentMM.is_scenario` (L390) | `MachineMarkets.p2_thm_forward_solvency` (L139) |
| 23 | `proposition` | `prop:driftguard` | Hidden-state drift and an invariant-box guard | `p2_guard.tex:172` | `CurrentMM.p2_prop_driftguard` (L888) | `MachineMarkets.p2_prop_driftguard` (L406) |
| 24 | `proposition` | `prop:dominance` | When an eigenvalue rule admits an uncertified level | `p2_guard.tex:196` | `CurrentMM.p2_prop_dominance_guard_vs_eigenvalue` (L405) | `MachineMarkets.p2_prop_dominance_guard_vs_eigenvalue` (L145) |
| 25 | `proposition` | `prop:lucas` | Strategic re-optimization reinforces the guard | `p2_guard.tex:205` | `CurrentMM.p2_prop_lucas_reinforces_guard` (L421) | `MachineMarkets.p2_prop_lucas_reinforces_guard` (L153) |
| 26 | `theorem` | `thm:disclosure` | Decision value of disclosure | `p2_disclosure.tex:5` | `CurrentMM.p2_thm_disclosure, CurrentMM.is_disclosure_monotone, CurrentMM.is_disclosure_strict, CurrentMM.is_intersection_admits_more` (L1181) | `MachineMarkets.p2_thm_disclosure` (L346) |
| 27 | `proposition` | `prop:equil` | Equilibrium transient risk | `p2_equil.tex:10` | `CurrentMM.p2_prop_equil_transient_risk, CurrentMM.is_depth_solution_increasing, CurrentMM.is_depth_eq_lt_sp, CurrentMM.is_depth_rebate_identified` (L449) | `MachineMarkets.p2_prop_equil_transient_risk` (L159) |
| 28 | `proposition` | `prop:probe` | Anytime-valid probing | `p2_appendix.tex:148` | `CurrentMM.is_sequential_rule_correct` (L704) | `MachineMarkets.p2_prop_probe` (L393) |
| 29 | `lemma` | `fhc:capacity` | Sharp prior bounds and exact prefunded capacity | `p2_appendix.tex:577` | `CurrentMM.p2_fhc_capacity` (L1228) | `MachineMarkets.p2_fhc_capacity` (L414) |
| 30 | `lemma` | `fhc:nodata-chance` | No data at the same error budget | `p2_appendix.tex:629` | `CurrentMM.p2_fhc_nodata_chance` (L1240) | `MachineMarkets.p2_fhc_nodata_chance` (L419) |
| 31 | `theorem` | `fhc:decision` | Uniform cost-aware finite-horizon decision | `p2_appendix.tex:654` | `CurrentMM.p2_fhc_decision` (L1252) | `MachineMarkets.p2_fhc_decision` (L426) |
| 32 | `theorem` | `fhc:pair` | A two-cohort identification obstruction under the same observations | `p2_appendix.tex:733` | `CurrentMM.p2_fhc_pair` (L1260) | `MachineMarkets.p2_fhc_pair` (L431) |
| 33 | `corollary` | `fhc:priced` | A priced separation | `p2_appendix.tex:803` | `CurrentMM.p2_fhc_priced` (L1273) | `MachineMarkets.p2_fhc_priced` (L439) |

## Phase 7 — Unified Foundational Bridge Theorems (Paper 1 ↔ Paper 2)

| # | Result | Title | Mathlib (`ℝ`) Theorem | Core Lean (`Rat`) Theorem |
|---|---|---|---|---|
| 1 | `Result A` | Result A: Impossibility of Cohort-Specific Risk Control from Public Data | `CurrentMM.foundational_result_A_impossibility` (L504) | `MachineMarkets.foundational_result_A_impossibility` (L167) |
| 2 | `Result B` | Result B: Disclosure-Enabled Control Improvement | `CurrentMM.foundational_result_B_disclosure_control` (L671) | `MachineMarkets.foundational_result_B_disclosure_control` (L258) |
| 3 | `Result C` | Result C: Active Probing vs. Transient Excursion Tradeoff | `CurrentMM.foundational_result_C_probing_control_tradeoff` (L697) | `MachineMarkets.foundational_result_C_probing_control_tradeoff` (L263) |
