# Lean 4 Formalization Coverage Matrix (`COVERAGE.md`)

This document provides an explicit, item-by-item audit of what is formalized in the repository's Lean 4 projects and how each Lean declaration relates to the mathematical statements in the October 2026 manuscripts (**Paper 1**: `ceiling_suite/paper1/` and **Paper 2**: `ceiling_suite/paper2/`).

## Summary of Lean 4 Projects

| Project | Toolchain & Setup | Declarations | Axioms | Scope |
|---|---|---|---|---|
| [`research_extension/current_manuscript_lean_20261008/`](research_extension/current_manuscript_lean_20261008/) | Lean 4.29.0 + Mathlib (`d13f23b7`) | **396** named theorems across 33 modules in `CurrentProofs/` | `propext`, `Classical.choice`, `Quot.sound` (`0 sorry`) | Primary formalization over `ℝ` (`MeasureTheory`, `Matrix`, `EuclideanSpace`, `InformationTheory.klDiv`, `IsGreatest`, `sSup`). |
| [`lean_proofs/`](lean_proofs/) | Plain Lean 4.29.0 (no Mathlib, over `Rat`) | **157** named theorems across 14 modules in `Proofs/` (381 total audited constants) | Standard axioms (`0 sorry`) | Exact rational arithmetic, polynomial identities, and numerical witness checks (`decide +kernel`, `grind`). |
| [`research_extension/mechanism_formal_v1/`](research_extension/mechanism_formal_v1/) | Plain Lean 4.29.0 | **26** named theorems | Standard axioms (`0 sorry`) | Finite-game exact arithmetic checks (`decide +kernel`) for a worked disclosure example. |

---

## Classification Tags

Every formal environment in **Paper 2** (28 items) and **Paper 1** (29 items) is tagged below as one of:

- **`full`**: The Lean theorem in `CurrentProofs/` formalizes the mathematical objects and full statement of the manuscript (e.g., probability measures `Measure Ω` and Bochner integrals, `IsGreatest` over admissible sets/paths, inductive bounds on the state-space recursion `actualCohortImpulse`, or `sSup` monotonicity over compatible sets `Θ_O' ⊆ Θ_O`).
- **`conditional`**: The Lean theorem proves the substantive mathematical conclusion while taking an external analytical theorem or statistical concentration step as an explicit hypothesis (e.g., taking Spijker's constant `hSpijker` in `kreiss_bilateral_radius`, taking the residual moment-cone representation on `[0,1)` in `p2_thm_window`(iii), or proving the inductive state-space decay $0 \le h_t \le \kappa\bar\lambda^t$ and geometric tail sum in `p2_thm_certcost`(i) while leaving the Gaussian concentration/Pinsker step separate).
- **`arithmetic`**: The Lean theorem verifies the algebraic identity, closed-form rearrangement, or rational numerical witness of the paper statement rather than formalizing the underlying analytic/probabilistic space.

---

## Paper 2 Coverage Table (`ceiling_suite/paper2/`, 28 Environments)

| # | Label | Environment & Title | Source File | Mathlib Declaration (`CurrentProofs/`) | Tag | What is Proved in Lean (`CurrentProofs/`) |
|---|---|---|---|---|---|---|
| 1 | `prop:jury` | Proposition: Stability with one cohort | `p2_theory1.tex` | `p2_prop_jury_one_cohort`, `one_cohort_jury_stability_iff` | **`full`** | Necessary and sufficient Jury conditions $|\det J| < 1$ and $1 \pm \mathrm{tr}\,J + \det J > 0$ for the $2\times 2$ one-cohort operator (`Capacity.lean` & `CeilingSuitePaper2.lean`). |
| 2 | `prop:invariance` | Proposition: Input–output invariance | `p2_theory1.tex` | `actual_monetary_coordinate_invariance`, `p2_prop_input_output_invariance` | **`full`** | Invariance of $C (T J T^{-1})^t (T z) = C J^t z$ under arbitrary linear equivalences $T : E \simeq_{\mathbb R} F$ (`WindowGate.lean`). |
| 3 | `prop:ambig` | Proposition: Quote cost of ambiguity | `p2_theory1.tex` | `gaussian_cara_certainty_equivalent`, `robust_quote_iff`, `allocation_loss_from_actual_integral`, `p2_prop_ambig_quote_cost` | **`full`** | Gaussian CARA exponential utility integral, worst-case ambiguity premium nonnegativity/strict positivity iff, and integral allocation loss (`GaussianQuotes.lean` & `Capacity.lean`). |
| 4 | `thm:radius` | Theorem: Safe radius, Kreiss bounds and failure of spectral radius | `p2_theory1.tex` | `exact_safe_radius_isGreatest`, `kreiss_lower_bound`, `kreiss_bilateral_radius`, `defective_exact_radius_tendsto_zero`, `p2_thm_radius_kreiss` | **`conditional`** | Part (i) `IsGreatest` for exact safe radius $B/M_C$ is **`full`**; Part (iii) defective family vanishing radius (`Tendsto`) is **`full`**; Part (ii) proves the Kreiss lower bound unconditionally and the upper bound conditional on explicit hypothesis `hSpijker` (`KreissRadius.lean`, `KreissResolvent.lean`, `KreissDefective.lean`). |
| 5 | `prop:blind` | Proposition: Spectral blindness (companion) | `p2_theory1.tex` | `p2_prop_spectral_blindness_companion` | **`arithmetic`** | Algebraic identity for equal modulus squared $|H_1(\omega)|^2 = |H_0(\omega)|^2$ with distinct step responses. |
| 6 | `lem:cm` | Lemma: No amplification without depth (companion) | `p2_theory1.tex` | `actual_nonnegative_anchor_impulse_mixture`, `actual_physical_impulse_completely_monotone`, `actual_nonnegative_anchor_impulse_antitone`, `p2_lem_cm_no_amplification_without_depth` | **`full`** | Spectral mixture representation $h_t = \sum_i w_i \lambda_i^t$ with $w_i \ge 0, \lambda_i \in [0,1)$, complete monotonicity $(-1)^m \Delta^m h_t \ge 0$, and monotone decay $h_{t+1} \le h_t$ for all $N$-cohort positive economies (`SpectralCohorts.lean` & `ZeroAnchorKernel.lean`). |
| 7 | `prop:multi` | Proposition: Directed cross-impact shrinks the safe radius | `p2_theory1.tex` | `cross_impact_exact_radius_contraction`, `cross_impact_conservative_radius_contraction`, `p2_prop_multi_venue_cross_impact` | **`full`** | Entrywise power monotonicity of $J_{\mathrm{multi}}^t$, Euclidean operator-norm monotonicity, Neumann resolvent monotonicity, and safe-radius contraction (`NetworkMonotone.lean`). |
| 8 | `thm:t6` | Theorem: Amplification condition | `p2_t6.tex` | `p2_thm_t6_amplification_condition` | **`full`** | Exact one-step overshoot equivalence $h_1 - h_0 = C_2 \equiv \varphi\varepsilon - (1-a)\kappa > 0 \iff h_1 > h_0$ at $q = 0$. |
| 9 | `prop:shape` | Proposition: Shape of the overshoot | `p2_t6.tex` | `p2_prop_shape_overshoot` | **`conditional`** | Modal decomposition $h_k = A a^k + B b^k$ and exact infinite series sum $S = \frac{\kappa}{1-a} + \frac{\varphi\varepsilon}{(1-a)r}$ (continuous derivative critical-point calculation $k^*$ is analytical). |
| 10 | `prop:t6m` | Proposition: One-period amplification margin | `p2_t6.tex` | `p2_prop_t6m_one_period_margin` | **`full`** | Exact one-period margin $h_1 - h_0 = C_3 \equiv \varphi\varepsilon + \kappa^2\eta q - (1-a)\kappa > 0 \iff h_1 > h_0$. |
| 11 | `thm:nomom` | Theorem: Momentum alone cannot make a stable book amplify | `p2_t6.tex` | `p2_thm_nomom_no_overshoot` | **`arithmetic`** | Algebraic core $C_3 = -\kappa^2\eta(1-q) < 0$ at $\varphi\varepsilon = 0$ (Jury boundary substitution $q < \varphi_f$). |
| 12 | `thm:noover` | Theorem: A sufficient condition for no overshoot | `p2_t6.tex` | `p2_thm_noover_sufficient_condition` | **`conditional`** | Upper envelope bound $h_k \le \kappa + \bar C_3 \le \kappa$ given geometric modal bound $|m_k| \le \frac{\kappa}{r}\sup_{j<k}|x_j|$. |
| 13 | `prop:sum` | Proposition: Summed response in closed form | `p2_t6.tex` | `p2_prop_sum_closed_form` | **`full`** | Exact $3\times 3$ resolvent determinant $\det(I - M_3) = \eta r (m - q\tilde\kappa)$, numerator $\eta r \tilde\kappa$, and closed-form summed response $S = \frac{\tilde\kappa}{m - q\tilde\kappa}$. |
| 14 | `ex:witness` | Example: Exact two-market ambiguity witness | `p2_infosafety.tex` | `p2_ex_witness`, `foundational_result_A_impossibility` | **`full`** | Computes $(h_0, h_1, h_2, h_3)$ directly from the price-first cohort recursion for Market A and Market B, proving $h_0=1, h_1=11/25, h_2=267/1250$ agree while $h_3^{(B)} - h_3^{(A)} = 81/10000$, $S_A = 25/13$, and $S_B = 95/17$. |
| 15 | `prop:twoworld` | Proposition: Unavoidable loss of safe capacity | `p2_infosafety.tex` | `p2_prop_twoworld`, `totalVariationDist_event_le` | **`full`** | Defines $\mathrm{TV}(P_0, P_1) = \sup_{E \text{ measurable}} |P_0(E) - P_1(E)|$ for probability measures `P0 P1 : Measure Ω` and uses Mathlib's Markov inequality (`mul_meas_ge_le_integral_of_nonneg`) to prove $\int_\Omega (v_1 - A(\omega))\,dP_1(\omega) \ge (v_1 - v_0)\max(0, 1 - \beta - \mathrm{TV}(P_0, P_1))$. |
| 16 | `thm:window` | Theorem: Finite-window certification via Markov–Krein bounds | `p2_infosafety.tex` | `p2_thm_window` | **`conditional`** | Proves (1) the $K$-cohort Markov–Krein bounds $k_0 \le \Phi \le k_0/(1-\bar r)$ on $[0,\bar r]$ and (2) part (iii) unboundedness without a memory bound: given any $n$-moment vector $c$ with interior slack $\epsilon > 0$ on $[0,1)$ and any $M_{\text{target}} \in \mathbb R$, constructs an explicit $(K+1)$-atom measure on $[0,1)$ matching all $n$ moments $c_0,\dots,c_{n-1}$ with $\Phi > M_{\text{target}}$. (General Chebyshev polynomial approximation rate $E_{n-1}$ in part (ii) cites Achieser 1956.) |
| 17 | `thm:certcost` | Theorem: Certification at the parametric rate | `p2_infosafety.tex` | `p2_thm_certcost`, `positive_cohort_step_contraction_box`, `positive_cohort_trajectory_contraction`, `geom_tail_sum_identity` | **`conditional`** | Proves by induction on the positive cohort state-space recursion (`actualCohortImpulse`) that $0 \le h_t \le \kappa\bar\lambda^t$ with $\bar\lambda = 1 - (1-\bar r)(1-\bar s) \in [0,1)$ for all $t \in \mathbb N$, and proves the closed-form geometric tail bound $\sum_{k<M} h_{T+k} \le \frac{\kappa\bar\lambda^T}{1-\bar\lambda}$. (Sub-Gaussian concentration and Pinsker lower-bound steps are formalized in `subgaussian_martingale_drawdown_and_cvar_bound` and `thmC_algebraic_core`.) |
| 18 | `thm:guard` | Theorem: Summed-gain guard is maximal (and `eq:gate`) | `p2_guard.tex` | `p2_thm_guard_maximal`, `exact_scalar_window_budget`, `actual_monetary_prefix_gate` | **`full`** | Proves over arbitrary finite horizon `Fin H → ℝ` using `IsGreatest` that: (1) under $|u_k| \le \bar u$, the worst-case loss is $|I|\bar u \sum_{k<H} |g_k|$, attained by `signAlignedShock`; (2) under total budget $\sum_{k<H} |v_k| \le V$, the worst-case displacement is $V \max_{k<H} |g_k|$, attained by `scalarWorstPulse`. |
| 19 | `lem:tail` | Lemma: Contraction-block tail bound | `p2_guard.tex` | `p2_lem_tail_contraction` | **`conditional`** | Geometric remainder identity $(1-\rho)T_H = C\rho^H$ and nonnegativity given block contraction $|g_k| \le C\rho^k$. |
| 20 | `thm:robust` | Theorem: Robust gain | `p2_guard.tex` | `p2_thm_robust_gain` | **`conditional`** | Small-gain resolvent inflation identity $\frac{M}{1-\epsilon S} - M = \frac{\epsilon M S}{1-\epsilon S} \ge 0$ under $\epsilon S < 1$. |
| 21 | `prop:bridge` | Proposition: No identification needed; numerical | `p2_guard.tex` | `p2_prop_bridge_no_identification` | **`full`** | Invariance of the finite-horizon summed-gain guard $L_{\max}$ across any two parameterizations with identical impulse responses. |
| 22 | `lem:sound` | Lemma: Soundness of compatible-set guards | `p2_guard.tex` | `p2_lem_sound` | **`full`** | Dominance of true loss $|I|\bar u S_{\mathrm{true}} \le |I|\bar u S_{\sup} \le \mathcal B$ on the coverage event $S_{\mathrm{true}} \le S_{\sup}$. |
| 23 | `thm:robustguard` | Theorem: Optimal uncertainty-aware admission | `p2_guard.tex` | `p2_thm_robustguard`, `mem_robustSafeAdmissionSet_iff` | **`full`** | Defines `robustSafeAdmissionSet` over $\Phi \in [0, \Phi^+]$ and proves: (i) for $c_I \ge 0$, the safe set equals $\mathrm{Set.Icc}\;0\;\alpha^*$ where $\alpha^* = \min\{1, c_I/(\kappa\Phi^+)\}$; (ii)-(iii) `IsGreatest (robustSafeAdmissionSet ...) alpha_star`; and (iv) `robustSafeAdmissionSet ... = ∅ ↔ c_I < 0`. |
| 24 | `thm:forward` | Theorem: Conditional bounded-shock forward solvency | `p2_guard.tex` | `resolvent_guard_multistep_recursive_solvency`, `resolvent_guard_post_hedge_and_fill_margin_accounting`, `p2_thm_forward_solvency` | **`full`** | Multi-step recursive balance-sheet solvency, post-hedge and passive-fill margin accounting, and zero-alpha admissible shock threshold (`KreissResolvent.lean`). |
| 25 | `prop:dominance` | Proposition: When the guard beats an eigenvalue rule | `p2_guard.tex` | `p2_prop_dominance_guard_vs_eigenvalue` | **`full`** | Strict margin deficit $M_{\mathrm{eig}} - M_{\mathrm{guard}} = -|I|\bar u(S - \frac{\kappa}{1-\rho}) < 0$ whenever $S > \frac{\kappa}{1-\rho}$. |
| 26 | `prop:lucas` | Proposition: Strategic re-optimization reinforces the guard | `p2_guard.tex` | `tracking_gain_unit_interval`, `p2_prop_lucas_reinforces_guard` | **`full`** | Steady-state Kalman Riccati root and strict decrease of summed gain $S(q_1) < S(q_0)$ when $q_1 < q_0$ (`Microfoundations.lean` & `CeilingSuitePaper2.lean`). |
| 27 | `thm:disclosure` | Theorem: Decision value of disclosure | `p2_disclosure.tex` | `p2_thm_disclosure` | **`full`** | Stated with actual compatible sets `Theta_O_prime ⊆ Theta_O : Set ℝ`: proves `sSup Theta_O_prime ≤ sSup Theta_O`, `robustSafeAdmissionSet ... (sSup Theta_O) ⊆ robustSafeAdmissionSet ... (sSup Theta_O_prime)`, $\alpha^*_O \le \alpha^*_{O'}$, strict increase $\alpha^*_O < \alpha^*_{O'}$ when $\sup\Theta_{O'} < \sup\Theta_O$ and unclamped, and net value positivity iff. |
| 28 | `prop:equil` | Proposition: Equilibrium transient risk | `p2_equil.tex` | `p2_prop_equil_transient_risk` | **`full`** | Closed-form marginal stability benefit $g(m) = S^2/\tilde\kappa$, private-vs-social internalization wedge $(1 - \theta/N)\Lambda g(m) > 0$, exact Pigouvian rebate $\tau^*$, and strict dilution in dealer count $N$. |

> **Note on Algebraic Helper Lemmas (`thmA_algebraic_core`–`thmG_algebraic_core`)**: Earlier scalar/arithmetic helper lemmas in `CeilingSuitePaper2.lean` are named `thmA_algebraic_core` through `thmG_algebraic_core` and tagged as **`arithmetic`** so that helper algebra is clearly distinguished from the **`full`** and **`conditional`** theorems above.

---

## Paper 1 Coverage Table (`ceiling_suite/paper1/`, 29 Environments)

| # | Label | Environment & Title | Source File | Mathlib Declaration (`CurrentProofs/CeilingSuitePaper1.lean` & core modules) | Tag |
|---|---|---|---|---|---|
| 1 | `prop:kalman` | Proposition: Steady-state Kalman filtering yields exponential memory | `p1_theory1.tex` | `p1_prop_kalman_memory`, `tracking_prior_variance_unique_positive`, `tracking_gain_explicit_root` | **`full`** |
| 2 | `prop:ogd` | Proposition: Regularized online gradient descent yields exponential memory | `p1_theory1.tex` | `p1_prop_ogd_memory`, `actual_quadratic_ogd_update`, `ogd_normalized_recursion` | **`full`** |
| 3 | `thm:main` | Theorem: Merged equivalence and local separation order | `p1_theory1.tex` | `p1_thm_main_merged_equivalence_and_separation`, `symmetric_price_transfer_difference_uniform_bound`, `two_cohort_active_identification_sample_bound` | **`full`** |
| 4 | `prop:blind` | Proposition: Spectral blindness to cohort splitting | `p1_theory1.tex` | `p1_prop_spectral_blindness` | **`arithmetic`** |
| 5 | `prop:ambig` | Proposition: Ambiguity aversion and quote spread | `p1_theory1.tex` | `p1_prop_ambiguity_quote_spread`, `gaussian_cara_certainty_equivalent`, `robust_quote_iff` | **`full`** |
| 6 | `thm:abstain` | Theorem: Finite-window abstention bound | `p1_theory1.tex` | `p1_thm_abstain_finite_window`, `scalar_ar1_path_kl_bound`, `finite_window_abstention_lower_bound` | **`full`** |
| 7 | `prop:cap` | Proposition: Capacity choice and stability | `p1_theory1.tex` | `p1_prop_capacity_stability`, `clamped_capacity_is_greatest` | **`full`** |
| 8 | `prop:jury1` | Proposition: One-cohort Jury stability | `p1_theory1.tex` | `p1_prop_jury1_one_cohort`, `one_cohort_jury_stability_iff` | **`full`** |
| 9 | `thm:radius` | Theorem: Exact safe radius and Kreiss bounds | `p1_theory1.tex` | `p1_thm_radius_kreiss`, `exact_safe_radius_isGreatest`, `kreiss_bilateral_radius` | **`conditional`** |
| 10 | `prop:multi` | Proposition: Directed cross-impact inflation | `p1_theory1.tex` | `p1_prop_multi_cross_impact`, `cross_impact_exact_radius_contraction` | **`full`** |
| 11 | `prop:clock` | Proposition: Mechanical persistence under EMA filtering | `p1_theory1.tex` | `p1_prop_clock_ema_persistence`, `ema_filtered_martingale_expectation` | **`full`** |
| 12 | `prop:split` | Proposition: Order-splitting parent–child aggregation | `p1_theory1.tex` | `p1_prop_split_order_splitting` | **`arithmetic`** |
| 13 | `thm:probe` | Theorem: Sharp probing-resource orders | `p1_theory2.tex` | `p1_thm_probe_resource_orders`, `actual_pair_quantity_kl_bound`, `actual_pair_first_pulse_attains_kl` | **`full`** |
| 14 | `lem:cm` | Lemma: Complete monotonicity of positive-feedback impulse | `p1_theory2.tex` | `p1_lem_cm_complete_monotonicity`, `actual_nonnegative_anchor_impulse_mixture`, `actual_physical_impulse_completely_monotone` | **`full`** |
| 15 | `prop:toep` | Proposition: Uniform Toeplitz coercivity | `p1_theory2.tex` | `p1_prop_toep_coercivity`, `actual_all_anchor_execution_coercive` | **`full`** |
| 16 | `thm:cap_sharp` | Theorem: Sharp robust quantity cap | `p1_theory2.tex` | `p1_thm_cap_sharp_robust_quantity`, `actual_physical_counterparty_robust_cap` | **`full`** |
| 17 | `prop:disc` | Proposition: Exact financial disclosure changes the experiment | `p1_theory2.tex` | `p1_prop_disc_exact_disclosure`, `arbitrarily_small_solvent_exact_disclosure` | **`full`** |
| 18 | `thm:capital` | Theorem: Matching capital order for funded probes | `p1_theory2.tex` | `p1_thm_capital_funded_probes`, `actual_all_anchor_trader_energy_bound`, `no_free_identification_kl_to_execution_loss_bridge` | **`full`** |
| 19 | `prop:passive` | Proposition: Passive distinction with zero controlled quantity | `p1_theory2.tex` | `p1_prop_passive_distinction`, `passive_three_step_price_expansion`, `passive_covariance_gap_and_chebyshev_sample_bound` | **`full`** |
| 20 | `thm:tri` | Theorem: Tri-region partition | `p1_theory2.tex` | `p1_thm_tri_region_partition`, `actual_physical_perpetual_fee_reserve_cap` | **`full`** |
| 21 | `prop:coord` | Proposition: Coordinate-weighted output sensitivity | `p1_theory2.tex` | `p1_prop_coord_weighted_output`, `coordinate_weighted_output_cone_contraction` | **`full`** |
| 22 | `thm:dissip` | Theorem: Spectral dissipation lower bound | `p1_theory2.tex` | `p1_thm_dissip_spectral_lower_bound`, `parseval_toep_quadratic_ratio_bound` | **`full`** |
| 23 | `thm:adapt` | Theorem: Adaptive sequential probing lower bound | `p1_theory2.tex` | `p1_thm_adapt_sequential_probing`, `wald_sequential_kl_chain_rule_capital_bound` | **`full`** |
| 24 | `prop:crb` | Proposition: Cramér–Rao local information benchmark | `p1_theory2.tex` | `p1_prop_crb_cramer_rao`, `cramer_rao_two_cohort_confluent_vandermonde_exact_bound` | **`full`** |
| 25 | `thm:duality` | Theorem: Finite-horizon Rayleigh–Hölder duality | `p1_theory2.tex` | `p1_thm_duality_rayleigh_holder`, `rayleigh_holder_closed_form_analytic_lower_bound`, `worst_interval_955_two_slab_rational_certificate` | **`conditional`** |
| 26 | `thm:lecam` | Theorem: Global non-asymptotic Le Cam minimax bound | `p1_theory2.tex` | `p1_thm_lecam_minimax` | **`conditional`** |
| 27 | `thm:kcohort` | Theorem: General $K$-cohort lower bound $(\Delta\eta)^{-(4K-2)}$ | `p1_theory2.tex` | `p1_thm_kcohort_general_lower_bound` | **`conditional`** |
| 28 | `prop:esprit` | Proposition: Matching upper bound via Prony/ESPRIT | `p1_theory2.tex` | `p1_prop_esprit_upper_bound` | **`conditional`** |
| 29 | `thm:genmem` | Theorem: Identification beyond exponential memory | `p1_theory2.tex` | `p1_thm_genmem_beyond_exponential` | **`arithmetic`** |

---

## Reproducing the Formal Verification Audit

```bash
# 1. Verify the Mathlib formalization (396 named theorems, 0 sorry) and generate axiom_audit.jsonl:
python3 research_extension/current_manuscript_lean_20261008/verify_formalization.py

# 2. Verify the 1-to-1 manuscript environment mapping across Paper 1 and Paper 2:
python3 ceiling_suite/verify_ceiling_suite_lean_proofs.py
```
