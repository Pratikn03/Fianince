> **29 October source-revision boundary:** this table predates the economic-review corrections. In particular, revised `prop:driftguard`, the sufficiency scope of `thm:forward`, and other changed statements do not inherit full formalization from their labels. The committed receipt records 520 named theorems and incomplete full-manuscript coverage; no new Lean rebuild or proof of these revisions is claimed. See [the current audit ledger](studies/economic_review_20261029/CLAIM_LEDGER.csv).

# Lean 4 Formalization Coverage Matrix (`COVERAGE.md`)

This document provides an explicit, item-by-item audit of what is formalized in the repository's Lean 4 projects and how each Lean declaration relates to the mathematical statements in the October 2026 manuscripts (**Paper 1**: `ceiling_suite/paper1/` and **Paper 2**: `ceiling_suite/paper2/`).

## Summary of Lean 4 Projects

| Project | Toolchain & Setup | Declarations | Axioms | Scope |
|---|---|---|---|---|
| [`research_extension/current_manuscript_lean_20261008/`](research_extension/current_manuscript_lean_20261008/) | Lean 4.34.1 + Mathlib (`d13f23b7`) | **445** named theorems across 33 modules in `CurrentProofs/` | `propext`, `Classical.choice`, `Quot.sound` (`0 sorry`) | Primary formalization over `ℝ` (`MeasureTheory`, `Matrix`, `EuclideanSpace`, `InformationTheory.klDiv`, `IsGreatest`, `sSup`). |
| [`lean_proofs/`](lean_proofs/) | Plain Lean 4.34.1 (no Mathlib, over `Rat`) | **166** named theorems across 14 modules in `Proofs/` (401 audited declarations in `MachineMarkets`) | Standard axioms (`0 sorry`) | Exact rational arithmetic, polynomial identities, and numerical witness checks (`decide +kernel`, `grind`). |
| [`research_extension/mechanism_formal_v1/`](research_extension/mechanism_formal_v1/) | Plain Lean 4.29.1 | **26** named theorems | Standard axioms (`0 sorry`) | Finite-game exact arithmetic checks (`decide +kernel`) for a worked disclosure example. |

---

## Classification Tags

Every numbered formal environment in **Paper 2** (28 items) and **Paper 1** (26 items) of the October 2026 hardened manuscripts is tagged below as one of:

- **`full`**: The Lean theorem in `CurrentProofs/` formalizes the mathematical objects and full statement of the manuscript (e.g., probability measures `Measure Ω` and Bochner integrals, `IsGreatest` over admissible sets/paths, inductive bounds on the state-space recursion `actualCohortImpulse`, or `sSup` monotonicity over compatible sets `Θ_O' ⊆ Θ_O`).
- **`conditional`**: The Lean theorem proves the substantive mathematical conclusion while taking an external analytical theorem or statistical concentration step as an explicit hypothesis (e.g., taking Spijker's constant `hSpijker` in `kreiss_bilateral_radius`, taking the residual moment-cone representation on `[0,1)` in `p2_thm_window`(iii), or proving the inductive state-space decay $0 \le h_t \le \kappa\bar\lambda^t$ and geometric tail sum in `p2_thm_certcost`(i) while leaving the Gaussian concentration/Pinsker step separate).
- **`arithmetic`**: The Lean theorem verifies the algebraic identity, closed-form rearrangement, or rational numerical witness of the paper statement rather than formalizing the underlying analytic/probabilistic space.

---

> **October 2026 hardening.** Declarations prefixed `is_` are in `CurrentProofs/InfoSafetyExtensions.lean` (49 theorems).
> Tags for results unchanged by the revision are carried over from the October 20 audit after checking that the cited
> declarations still exist; tags for new or restated results were assigned in this revision. Tags for Paper 1 rows whose
> Lean core in `CeilingSuitePaper1.lean` takes scalar parameters are `arithmetic`, even where an earlier version of this file
> said `full`. Removed environments: Paper 1 `prop:kalman`, `prop:ogd` (merged into `lem:micro`), `prop:ambiguity` (kept in
> Paper 2 as `prop:ambig`), `prop:mech` (now an inline equation); Paper 2 `prop:blind`, `lem:cm` (cited from Paper 1),
> `prop:bridge` (now a sentence), and the five Section 4 results, which are parts of `thm:peak`.

## Paper 2 Coverage Table (`ceiling_suite/paper2/`, 28 Environments)

| # | Label | Environment & Title | Source File | Lean declarations (`CurrentProofs/`) | Tag | What is proved in Lean |
|---|---|---|---|---|---|---|
| 1 | `prop:jury` | Proposition: Stability with one cohort | `p2_theory1.tex` | `p2_prop_jury_one_cohort`, `one_cohort_jury_stability_iff` | **`full`** | Necessary and sufficient Jury conditions for the 2×2 one-cohort operator. |
| 2 | `prop:invariance` | Proposition: Input–output invariance | `p2_theory1.tex` | `p2_prop_input_output_invariance`, `actual_monetary_coordinate_invariance` | **`full`** | Invariance of $C(TJT^{-1})^t(Tz)=CJ^tz$ under linear equivalences. |
| 2b | `prop:inventory_S` | Proposition: Summed response with carried cohort inventory | `p2_theory1.tex` | `p2_prop_inventory_S` | **`arithmetic`** | Effective long-run feedback attenuation $\Phi_{\mathrm{eff}}=(\delta/(\delta+\psi))\Phi\le\Phi$ and $S(\psi)\le S(0)$ over $\mathbb{R}$ (`InfoSafetyExtensions.lean`) and calibrated rational witness (`CeilingSuitePaper2.lean`); full state-space transfer function and nonnegativity threshold $\psi_i\le 1-\delta_{\mathrm{inv}}, \delta_{\mathrm{inv}}\ge\eta_i$ are proved on paper (`p2_appendix.tex`). |
| 3 | `prop:ambig` | Proposition: Quote cost of ambiguity | `p2_theory1.tex` | `p2_prop_ambig_quote_cost`, `gaussian_cara_certainty_equivalent`, `robust_quote_iff` | **`full`** | Gaussian CARA certainty equivalent, robust quote and surplus loss. (Paper 1's duplicate was removed; this is now the only statement.) |
| 4 | `thm:radius` | Theorem: Safe radius, Kreiss bounds, failure of the spectral radius | `p2_theory1.tex` | `p2_thm_radius_kreiss`, `exact_safe_radius_isGreatest`, `kreiss_bilateral_radius`, `defective_exact_radius_tendsto_zero` | **`conditional`** | (i), (iii) full; (ii) upper Kreiss bound takes Spijker's constant as hypothesis `hSpijker`. |
| 5 | `prop:multi` | Proposition: Directed cross-impact shrinks the safe radius | `p2_theory1.tex` | `p2_prop_multi_venue_cross_impact`, `cross_impact_exact_radius_contraction` | **`full`** | Entrywise power monotonicity and safe-radius contraction. |
| 6 | `thm:peak` | Theorem: Peak overshoot — depletion versus momentum (parts i–v) | `p2_t6.tex` | `p2_thm_t6_amplification_condition`, `p2_prop_shape_overshoot`, `is_confluent_stationary`, `p2_prop_t6m_one_period_margin`, `p2_thm_nomom_no_overshoot`, `is_momentum_residues`, `p2_thm_noover_sufficient_condition` | **`conditional`** | (i) one-step equivalence full; (ii) modal decomposition, cumulative sum and the confluent stationary point $k^*=1/\log(1/a)-a\kappa/(\varphi\varepsilon)$ (algebra, with $L=\log(1/a)$ as a variable); unimodality of the real-variable response is not formalized; (iii) full; (iv) residue shares in $[0,1]$ (arithmetic core; Perron–Frobenius step not formalized); (v) envelope bound given the modal bound. |
| 7 | `thm:sum` | Theorem: Summed response in closed form | `p2_t6.tex` | `p2_prop_sum_closed_form`, `is_summed_response_closed_form` | **`full`** | 3×3 resolvent determinant and the closed form $S=\tilde\kappa/(m-q\tilde\kappa)$ from the stationary sum equations. |
| 8 | `ex:witness` | Example: Exact ambiguity witness | `p2_infosafety.tex` | `p2_ex_witness` | **`full`** | Rational computation of the two markets' responses and summed responses. |
| 9 | `prop:twoworld` | Proposition: Unavoidable loss of safe capacity | `p2_infosafety.tex` | `p2_prop_twoworld`, `is_two_world_capacity_loss`, `is_two_world_attained` | **`full`** | Measure-theoretic version (`p2_prop_twoworld`) and a finite-space version with TV defined as a supremum over events, plus attainment. |
| 10 | `thm:window` | Theorem: Finite-window certification | `p2_infosafety.tex` | `p2_thm_window` | **`conditional`** | Markov–Krein bounds and part (iii) unboundedness; Achieser's best-approximation formula in (ii) is cited, not formalized. The interior moment-cone condition added in this revision is a hypothesis of the statement. |
| 11 | `lem:certnum` | Lemma: Certified endpoints | `p2_infosafety.tex` | `is_upper_bound`, `is_lower_bound`, `is_coeff_moment_eq`, `is_slack_shift` | **`conditional`** | Weak duality (any polynomial envelope bounds Φ) and the slack shift are full; the Hermite-interpolant sign condition and IEEE outward rounding are not formalized. |
| 12 | `thm:certcost` | Theorem: Certification at the parametric rate | `p2_infosafety.tex` | `p2_thm_certcost`, `is_iter_bound`, `is_tail_bound`, `is_cohort_row_bound` | **`conditional`** | Deterministic decay $0\le h_t\le\kappa\bar\lambda^t$ and the geometric tail are full; Gaussian concentration and the two-point lower bound are not. |
| 13 | `prop:hotelling` | Proposition: Certification with unknown covariance | `p2_infosafety.tex` | `is_corrSum_ge`, `is_o1_margin_too_small` | **`conditional`** | Deterministic core of (iii) only ($\mathbf 1^\top R\mathbf 1\ge T$, so the (O1) margin is too small); Student-t and Hotelling distribution theory are not formalized. |
| 14 | `thm:guard` | Lemma: Summed-gain guard is maximal | `p2_guard.tex` | `p2_thm_guard_maximal`, `is_per_period_upper`, `is_per_period_attained`, `is_budget_upper`, `is_budget_attained` | **`full`** | Worst case and attainment under per-period and total budgets. Demoted from theorem to lemma in this revision (Hölder's inequality). |
| 15 | `lem:tail` | Lemma: Contraction-block tail bound | `p2_guard.tex` | `p2_lem_tail_contraction` | **`conditional`** | Geometric remainder given the block contraction. |
| 16 | `thm:robust` | Theorem: Robust gain | `p2_guard.tex` | `p2_thm_robust_gain` | **`conditional`** | Small-gain inflation identity under $\epsilon S<1$. |
| 17 | `lem:sound` | Lemma: Soundness of compatible-set guards | `p2_guard.tex` | `p2_lem_sound`, `is_sound` | **`full`** | Dominance on the coverage event. |
| 18 | `thm:robustguard` | Theorem: Optimal uncertainty-aware admission | `p2_guard.tex` | `p2_thm_robustguard`, `is_robust_safe_set_eq`, `is_alphaStar_isGreatest`, `is_infeasible_of_cI_neg` | **`conditional`** | (i)–(iv) full; (v) minimax capacity loss is not formalized. |
| 19 | `prop:venue` | Proposition: Venue mode | `p2_guard.tex` | `is_Dv_convex`, `is_unsafe_between`, `is_worst_corner`, `is_venue_example`, `is_venue_example_box` | **`full`** | Convexity, unsafe set is an interval, worst corner of the box, and the two-component example. |
| 20 | `thm:venuebb` | Theorem: What branch and bound certifies | `p2_guard.tex` | `is_classify_safe_sound`, `is_classify_unsafe_sound`, `is_robustSafeSet_closed`, `is_largest_safe_exists` | **`conditional`** | Soundness of both classifications and existence of the largest safe level are full, given the floating-point enclosure property (Rump 2010) as hypothesis `hencl`. |
| 21 | `thm:forward` | Theorem: Conditional bounded-shock forward solvency | `p2_guard.tex` | `p2_thm_forward_solvency`, `is_buffer_after_step`, `is_scenario` | **`full`** | One-step buffer inequality and the Section 6 scenario numbers. |
| 21b | `prop:driftguard` | Proposition: Uniformly safe guard under interval-bounded unknown hidden drift | `p2_guard.tex` | `p2_prop_driftguard` | **`arithmetic`** | Capacity-cost identity $\alpha^*-\alpha^*_{\mathrm{drift}}=\alpha^*\frac{|I|\bar y_0}{\mathcal B+|I|\bar y_0}$ over $\mathbb{R}$ (`InfoSafetyExtensions.lean`) and calibrated rational witness (`CeilingSuitePaper2.lean`); the $\ell_\infty$ drift envelope $\sup_{\|y_0\|_\infty\le\bar y_0}\sum_{t\ge 1}|e_x^\top J(\alpha)^t z_0|=(a|x_0|+\alpha\kappa\Phi\bar y_0)/(1-a-\alpha\kappa\Phi)$ and interval characterization are proved on paper (`p2_appendix.tex`). |
| 22 | `prop:dominance` | Proposition: When an eigenvalue rule admits an uncertified level | `p2_guard.tex` | `p2_prop_dominance_guard_vs_eigenvalue` | **`full`** | Margin deficit identity. |
| 23 | `prop:lucas` | Proposition: Strategic re-optimization reinforces the guard | `p2_guard.tex` | `p2_prop_lucas_reinforces_guard`, `tracking_gain_unit_interval` | **`conditional`** | (i) Riccati monotonicity full; (ii) the renewal-coupling monotonicity of every finite-horizon sum (new in this revision) is proved on paper and checked numerically, not formalized. |
| 24 | `thm:disclosure` | Theorem: Decision value of disclosure | `p2_disclosure.tex` | `p2_thm_disclosure`, `is_disclosure_monotone`, `is_disclosure_strict`, `is_intersection_admits_more` | **`conditional`** | (i)–(iv) full; (v) the intersection of two certificates admits at least as much as either (full); the delta-method standard error is not formalized. |
| 25 | `prop:equil` | Proposition: Equilibrium transient risk | `p2_equil.tex` | `p2_prop_equil_transient_risk`, `is_depth_solution_increasing`, `is_depth_eq_lt_sp`, `is_depth_rebate_identified` | **`full`** | (i)–(iv) as before; (v) endogenous depth: fixed points are increasing in the number of dealers, equilibrium depth is below the planner's, and the depth rebate equals $S\tilde\kappa$ times the wedge. |
| 26 | `prop:probe` | Proposition: Anytime-valid probing (Internet Appendix) | `p2_appendix.tex` | `is_sequential_rule_correct` | **`conditional`** | Deterministic core: on the time-uniform event the sequential rule never decides wrongly; Ville's inequality is not formalized. |

---

## Paper 1 Coverage Table (`ceiling_suite/paper1/`, 26 Environments)

| # | Label | Environment & Title | Source File | Lean declarations (`CurrentProofs/`) | Tag | What is proved in Lean |
|---|---|---|---|---|---|---|
| 1 | `lem:micro` | Lemma: Filtering and learning microfoundations | `p1_front.tex` | `p1_prop_kalman_memory`, `p1_prop_ogd_memory`, `tracking_prior_variance_unique_positive`, `actual_quadratic_ogd_update` | **`full`** | Riccati root and gain; OGD update. Merges the former Propositions on Kalman and gradient memory. |
| 2 | `lem:cm` | Lemma: Positive price-response geometry | `p1_front.tex` | `p1_lem_cm_positive_response`, `actual_nonnegative_anchor_impulse_mixture`, `actual_physical_impulse_completely_monotone` | **`full`** | Nonnegative spectral mixture and complete monotonicity. |
| 3 | `thm:merged` | Theorem: Merged rate–weight equivalence | `p1_ident.tex` | `p1_thm_merged_equivalence_and_resolvent`, `symmetric_price_transfer_difference_uniform_bound` | **`conditional`** | Equivalence and the uniform transfer-difference bound; the McMillan-degree count (now $1+|{\rm supp}\,M|$ for $a>0$ and $|{\rm supp}\,M|$ for $a=0$) is not formalized. |
| 4 | `thm:quantity` | Theorem: Sharp probing-resource orders | `p1_ident.tex` | `p1_thm_quantity_sharp_orders`, `actual_pair_quantity_kl_bound`, `actual_pair_first_pulse_attains_kl` | **`full`** | KL bound and pulse attainment. |
| 5 | `lem:toeplitz` | Lemma: Fair execution | `p1_ident.tex` | `p1_lem_toeplitz_fair_execution`, `actual_all_anchor_execution_coercive` | **`full`** | Toeplitz cost identity and positive definiteness. |
| 6 | `thm:cap` | Theorem: Sharp robust quantity cap | `p1_ident.tex` | `p1_thm_cap_counterparty_margin`, `actual_physical_counterparty_robust_cap` | **`full`** | Robust cap from cash and margin. |
| 7 | `prop:disclosure` | Proposition: Exact financial disclosure changes the experiment | `p1_ident.tex` | `p1_prop_disclosure_third_mark`, `arbitrarily_small_solvent_exact_disclosure` | **`full`** | Third-mark separation. |
| 8 | `thm:capital` | Lemma: Time-domain Toeplitz coercivity (capital order) | `p1_ident.tex` | `p1_thm_capital_funded_probes`, `actual_all_anchor_trader_energy_bound` | **`full`** | Solvency energy bound. Demoted from theorem to lemma in this revision (its constant scales as $\epsilon^7(1-S)^5$). |
| 9 | `prop:tri` | Proposition: Tri-region partition | `p1_account.tex` | `p1_prop_tri_region_partition`, `actual_physical_perpetual_fee_reserve_cap` | **`arithmetic`** | Pulse-count and floor algebra. |
| 10 | `thm:spectral` | Theorem: Spectral dissipation lower bound | `p1_account.tex` | `p1_thm_spectral_dissipation_bound`, `parseval_toep_quadratic_ratio_bound` | **`conditional`** | (i)–(ii) Parseval ratio bound; (iii) numbers are computed; (iv) process noise (new) is proved on paper, not formalized. |
| 11 | `thm:adaptive` | Theorem: Adaptive and sequential probing | `p1_account.tex` | `p1_thm_adaptive_sequential_bound`, `wald_sequential_kl_chain_rule_capital_bound` | **`full`** | Wald/KL chain-rule capital bound. |
| 12 | `thm:rh` | Theorem: Finite-horizon Rayleigh–Hölder duality | `p1_account.tex` | `p1_thm_rh_duality`, `rayleigh_holder_closed_form_analytic_lower_bound`, `is_rh_radius_bound`, `is_rh_chain` | **`conditional`** | The scalar chain behind the new explicit $F_{\rm dom}$, $W_\perp$, $\gamma$ bound is full; the generalized eigen-decomposition and Hölder/Cauchy–Schwarz steps are on paper. |
| 13 | `cor:garch` | Corollary: Invariance under impact-induced heteroskedasticity | `p1_account.tex` | `p1_cor_garch_heteroskedastic_invariance` | **`arithmetic`** | Scalar core. |
| 14 | `prop:crb` | Proposition: Cramér–Rao benchmark | `p1_mixture.tex` | `p1_prop_crb_benchmark`, `cramer_rao_two_cohort_confluent_vandermonde_exact_bound` | **`conditional`** | Confluent Vandermonde bound; the Θ-order statement is on paper. |
| 15 | `thm:twocohort` | Theorem: Global two-point bound, K=2 | `p1_mixture.tex` | `p1_thm_twocohort_hankel_and_moment_gap` | **`arithmetic`** | Moment-gap and Hankel identities; Le Cam step and the new permutation-invariant loss are on paper. |
| 16 | `thm:kcohort` | Theorem: K-cohort two-point lower bound | `p1_mixture.tex` | `p1_thm_kcohort_lower_bound` | **`arithmetic`** | Scalar core. |
| 17 | `prop:esprit` | Theorem: Matching upper bound for every K | `p1_mixture.tex` | `p1_thm_esprit_matching_upper_bound` | **`arithmetic`** | Scalar core; inverse-function-theorem argument on paper. |
| 18 | `lem:altpair` | Lemma: Moment-matched cohort pairs | `p1_mixture.tex` | `p1_lem_altpair_moment_matched_wasserstein` | **`arithmetic`** | Scalar core. |
| 19 | `thm:general` | Theorem: Minimax rate for general memory | `p1_mixture.tex` | `p1_thm_general_memory_minimax` | **`arithmetic`** | Scalar core. |
| 20 | `thm:minphase` | Theorem: Passive identification, minimum phase | `p1_mixture.tex` | `p1_thm_minphase_passive_identification` | **`arithmetic`** | Scalar core. |
| 21 | `prop:passive` | Theorem: Passive cost (now for every K) | `p1_mixture.tex` | `p1_thm_passive_cost` | **`arithmetic`** | Scalar core; the Whittle expansion and the new all-$K$ part (iii) are on paper. |
| 22 | `prop:tagged` | Proposition: Tagged flow removes the barrier | `p1_disclosure.tex` | `p1_prop_tagged_flow_removes_barrier`, `is_iv_det_pos` | **`conditional`** | Positivity of the IV Jacobian determinant is full; the CLT for $m$-dependent scores is on paper. |
| 23 | `thm:discvalue` | Theorem: Value of class-tagged disclosure | `p1_disclosure.tex` | `p1_thm_discvalue_ratio` | **`arithmetic`** | Ratio algebra. |
| 24 | `thm:blind` | Theorem: Spectral blindness | `p1_disclosure.tex` | `p1_thm_blind_spectral_blindness` | **`arithmetic`** | Scalar core. |
| 25 | `thm:abstain` | Theorem: Finite-window abstention (supplement) | `p1_appendix.tex` | `p1_thm_abstain_finite_window`, `scalar_ar1_path_kl_bound`, `finite_window_abstention_lower_bound` | **`full`** | AR(1) path KL and abstention bound. |
| 26 | `prop:passive0` | Proposition: Passive distinction of a known pair (supplement) | `p1_appendix.tex` | `p1_prop_passive0_three_step_blocks`, `passive_covariance_gap_and_chebyshev_sample_bound` | **`full`** | Covariance gap and Chebyshev sample bound. Moved to the supplement in this revision. |

---

## Reproducing the Formal Verification Audit

```bash
# 1. Verify the Mathlib formalization (443 named theorems, 0 sorry) and generate axiom_audit.jsonl:
python3 research_extension/current_manuscript_lean_20261008/verify_formalization.py

# 2. Verify the label-to-declaration mapping across Paper 1 and Paper 2:
python3 ceiling_suite/verify_ceiling_suite_lean_proofs.py
```
