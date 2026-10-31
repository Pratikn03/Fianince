# Ceiling Suite — Lean declaration mapping audit

- **Status**: MAPPING_AUDIT_INCOMPLETE. Existing declaration references checked; no fresh Lean build or full semantic equivalence is claimed.
- **Unmapped labels**: prop:primitives, prop:tied, thm:uniformw1, prop:choice, prop:target, fhc:capacity, fhc:nodata-chance, fhc:decision, fhc:pair, fhc:priced, fhc:capacity, fhc:nodata-chance, fhc:decision, fhc:pair, fhc:priced
- **Revised statements requiring semantic review**: prop:esprit, thm:minphase, prop:inventory_S, thm:window, thm:certcost, thm:forward, prop:driftguard
- **Lean Toolchain**: `leanprover/lean4:v4.34.1`
- **Paper 1**: 26 / 36 current formal environments have an existing name mapping.
- **Paper 2**: 28 / 33 current formal environments have an existing name mapping.
- Run with `--require-complete` to fail if unmapped or revised statements remain. A successful default run means the audit was generated, not that manuscript formalization is complete.

## Paper 1 — Auditable Memory and Financial Identification Limits (`paper1/`)

| # | Environment | Label | Title | LaTeX Source | Mathlib (`ℝ`) Theorem | Core Lean (`Rat`) Theorem |
|---|---|---|---|---|---|---|
| 1 | `lemma` | `lem:micro` | Two motivating examples: filtering and learning | `p1_front.tex:293` | `CurrentMM.p1_prop_kalman_memory, CurrentMM.p1_prop_ogd_memory` (L52) | `MachineMarkets.p1_prop_kalman_memory, MachineMarkets.p1_prop_ogd_memory` (L13) |
| 2 | `lemma` | `lem:cm` | Positive price-response geometry | `p1_front.tex:311` | `CurrentMM.p1_lem_cm_positive_response` (L102) | `MachineMarkets.p1_lem_cm_positive_geometry` (L29) |
| 3 | `theorem` | `thm:merged` | Merged rate--weight equivalence | `p1_ident.tex:5` | `CurrentMM.p1_thm_merged_equivalence_and_resolvent` (L129) | `MachineMarkets.p1_thm_merged_equivalence` (L38) |
| 4 | `theorem` | `thm:quantity` | Sharp probing-resource orders for a known symmetric pair | `p1_ident.tex:36` | `CurrentMM.p1_thm_quantity_sharp_orders` (L149) | `MachineMarkets.p1_thm_quantity_orders` (L44) |
| 5 | `lemma` | `lem:toeplitz` | Fair execution | `p1_ident.tex:93` | `CurrentMM.p1_lem_toeplitz_fair_execution` (L167) | `MachineMarkets.p1_lem_toeplitz_fair_execution` (L53) |
| 6 | `theorem` | `thm:cap` | Sharp robust quantity cap from cash and margin | `p1_ident.tex:105` | `CurrentMM.p1_thm_cap_counterparty_margin` (L197) | `MachineMarkets.p1_thm_cap_robust_quantity` (L60) |
| 7 | `proposition` | `prop:disclosure` | Exact financial disclosure changes the experiment | `p1_ident.tex:123` | `CurrentMM.p1_prop_disclosure_third_mark` (L227) | `MachineMarkets.p1_prop_disclosure_changes_experiment` (L66) |
| 8 | `lemma` | `thm:capital` | Time-domain Toeplitz coercivity: capital order for funded probes | `p1_ident.tex:133` | `CurrentMM.p1_thm_capital_funded_probes` (L241) | `MachineMarkets.p1_thm_capital_order` (L74) |
| 9 | `proposition` | `prop:primitives` | Identification in economic primitives | `p1_ident.tex:161` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |
| 10 | `proposition` | `prop:tied` | Intensity tied to information quality | `p1_ident.tex:181` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |
| 11 | `proposition` | `prop:tri` | Tri-region partition and finite-session resolution floor | `p1_account.tex:15` | `CurrentMM.p1_prop_tri_region_partition` (L291) | `MachineMarkets.p1_prop_tri_region_floor` (L93) |
| 12 | `theorem` | `thm:spectral` | Spectral dissipation lower bound | `p1_account.tex:69` | `CurrentMM.p1_thm_spectral_dissipation_bound` (L305) | `MachineMarkets.p1_thm_spectral_dissipation` (L99) |
| 13 | `theorem` | `thm:adaptive` | Adaptive and sequential probing | `p1_account.tex:101` | `CurrentMM.p1_thm_adaptive_sequential_bound` (L325) | `MachineMarkets.p1_thm_adaptive_sequential` (L107) |
| 14 | `theorem` | `thm:rh` | Finite-horizon Rayleigh--H\"older duality | `p1_account.tex:133` | `CurrentMM.p1_thm_rh_duality, CurrentMM.is_rh_radius_bound, CurrentMM.is_rh_chain` (L344) | `MachineMarkets.p1_thm_rayleigh_holder_duality` (L113) |
| 15 | `corollary` | `cor:garch` | Invariance under impact-induced heteroskedasticity | `p1_account.tex:177` | `CurrentMM.p1_cor_garch_heteroskedastic_invariance` (L377) | `MachineMarkets.p1_cor_garch_invariance` (L119) |
| 16 | `proposition` | `prop:crb` | Cram\'er--Rao benchmark | `p1_mixture.tex:11` | `CurrentMM.p1_prop_crb_benchmark` (L389) | `MachineMarkets.p1_prop_crb_benchmark` (L127) |
| 17 | `theorem` | `thm:twocohort` | Global two-point bound and matching upper bound, $K=2$ | `p1_mixture.tex:47` | `CurrentMM.p1_thm_twocohort_hankel_and_moment_gap` (L405) | `MachineMarkets.p1_thm_twocohort_hankel` (L136) |
| 18 | `theorem` | `thm:kcohort` | $K$-cohort two-point lower bound | `p1_mixture.tex:104` | `CurrentMM.p1_thm_kcohort_lower_bound` (L444) | `MachineMarkets.p1_thm_kcohort_lower_bound` (L145) |
| 19 | `theorem` | `prop:esprit` | Matching upper bound for every $K$ | `p1_mixture.tex:155` | `CurrentMM.p1_thm_esprit_matching_upper_bound` (L459) | `MachineMarkets.p1_prop_esprit_upper_bound` (L151) |
| 20 | `theorem` | `thm:uniformw1` | Uniform rate without separation | `p1_mixture.tex:219` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |
| 21 | `lemma` | `lem:altpair` | Moment-matched cohort pairs | `p1_mixture.tex:243` | `CurrentMM.p1_lem_altpair_moment_matched_wasserstein` (L496) | `MachineMarkets.p1_lem_altpair_moment_matched` (L162) |
| 22 | `theorem` | `thm:general` | Minimax rate for general memory | `p1_mixture.tex:249` | `CurrentMM.p1_thm_general_memory_minimax` (L512) | `MachineMarkets.p1_thm_general_memory_minimax` (L177) |
| 23 | `theorem` | `thm:minphase` | Passive identification: minimum phase | `p1_mixture.tex:306` | `CurrentMM.p1_thm_minphase_passive_identification` (L534) | `MachineMarkets.p1_thm_minphase_identification` (L183) |
| 24 | `theorem` | `prop:passive` | Passive cost | `p1_mixture.tex:312` | `CurrentMM.p1_thm_passive_cost` (L550) | `MachineMarkets.p1_prop_passive_cost` (L189) |
| 25 | `proposition` | `prop:tagged` | Tagged flow removes the barrier | `p1_disclosure.tex:38` | `CurrentMM.p1_prop_tagged_flow_removes_barrier, CurrentMM.is_iv_det_pos` (L571) | `MachineMarkets.p1_prop_tagged_flow_ident` (L195) |
| 26 | `theorem` | `thm:discvalue` | Value of class-tagged disclosure | `p1_disclosure.tex:59` | `CurrentMM.p1_thm_discvalue_ratio` (L580) | `MachineMarkets.p1_thm_disclosure_value` (L203) |
| 27 | `proposition` | `prop:choice` | When an audit trail is chosen | `p1_disclosure.tex:123` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |
| 28 | `proposition` | `prop:target` | Market-wide versus targeted intervention | `p1_disclosure.tex:136` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |
| 29 | `theorem` | `thm:blind` | Spectral blindness | `p1_disclosure.tex:273` | `CurrentMM.p1_thm_blind_spectral_blindness` (L596) | `MachineMarkets.p1_thm_spectral_blindness` (L211) |
| 30 | `theorem` | `thm:abstain` | Finite-window abstention | `p1_appendix.tex:208` | `CurrentMM.p1_thm_abstain_finite_window` (L646) | `MachineMarkets.p1_thm_abstain_finite_window` (L228) |
| 31 | `proposition` | `prop:passive0` | Passive distinction with zero controlled quantity | `p1_appendix.tex:224` | `CurrentMM.p1_prop_passive0_three_step_blocks` (L260) | `MachineMarkets.p1_prop_passive0_distinction` (L79) |
| 32 | `lemma` | `fhc:capacity` | Sharp prior bounds and exact prefunded capacity | `p1_appendix.tex:705` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |
| 33 | `lemma` | `fhc:nodata-chance` | No data at the same error budget | `p1_appendix.tex:757` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |
| 34 | `theorem` | `fhc:decision` | Uniform cost-aware finite-horizon decision | `p1_appendix.tex:782` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |
| 35 | `theorem` | `fhc:pair` | A two-cohort identification obstruction under the same observations | `p1_appendix.tex:861` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |
| 36 | `corollary` | `fhc:priced` | A priced separation | `p1_appendix.tex:931` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |

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
| 29 | `lemma` | `fhc:capacity` | Sharp prior bounds and exact prefunded capacity | `p2_appendix.tex:577` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |
| 30 | `lemma` | `fhc:nodata-chance` | No data at the same error budget | `p2_appendix.tex:629` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |
| 31 | `theorem` | `fhc:decision` | Uniform cost-aware finite-horizon decision | `p2_appendix.tex:654` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |
| 32 | `theorem` | `fhc:pair` | A two-cohort identification obstruction under the same observations | `p2_appendix.tex:733` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |
| 33 | `corollary` | `fhc:priced` | A priced separation | `p2_appendix.tex:803` | `UNMAPPED` (LNone) | `UNMAPPED` (LNone) |

## Phase 7 — Unified Foundational Bridge Theorems (Paper 1 ↔ Paper 2)

| # | Result | Title | Mathlib (`ℝ`) Theorem | Core Lean (`Rat`) Theorem |
|---|---|---|---|---|
| 1 | `Result A` | Result A: Impossibility of Cohort-Specific Risk Control from Public Data | `CurrentMM.foundational_result_A_impossibility` (L504) | `MachineMarkets.foundational_result_A_impossibility` (L167) |
| 2 | `Result B` | Result B: Disclosure-Enabled Control Improvement | `CurrentMM.foundational_result_B_disclosure_control` (L671) | `MachineMarkets.foundational_result_B_disclosure_control` (L258) |
| 3 | `Result C` | Result C: Active Probing vs. Transient Excursion Tradeoff | `CurrentMM.foundational_result_C_probing_control_tradeoff` (L697) | `MachineMarkets.foundational_result_C_probing_control_tradeoff` (L263) |
