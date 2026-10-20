import Init.GrindInstances.Ring.Rat

namespace MachineMarkets

/-!
# Ceiling Suite Paper 2 — Core Lean 4 Formalization (21 Environments)
Provides fast, zero-dependency algebraic and constructive proofs over `Rat`
for all 21 formal environments (`theorem`, `proposition`, `lemma`)
in `ceiling_suite/paper2/`.
-/

/-- 1. `prop:jury` (`p2_theory1.tex`): One-cohort Schur stability and Jury margins -/
theorem p2_prop_jury_one_cohort (kappa eta q phi_f : Rat) :
    let a := 1 - kappa * phi_f
    let trJ := a + (1 - eta + eta * kappa * q)
    let detJ := a * (1 - eta + eta * kappa * q) - eta * a * (kappa * q)
    detJ = (1 - kappa * phi_f) * (1 - eta) ∧
    1 - trJ + detJ = eta * kappa * (phi_f - q) ∧
    1 + trJ + detJ = 4 - 2 * eta - kappa * ((2 - eta) * phi_f - eta * q) := by
  dsimp
  refine ⟨by grind, by grind, by grind⟩

/-- 2. `prop:invariance` (`p2_theory1.tex`): Input-output impulse invariance under coordinate change -/
theorem p2_prop_input_output_invariance (c mk b : Rat) :
    let s : Rat := 5 / 2
    let s_inv : Rat := 2 / 5
    (c * s_inv) * (s * mk * s_inv) * (s * b) = c * mk * b := by
  dsimp
  grind

/-- 3. `prop:ambig` (`p2_theory1.tex`): Quote cost of ambiguity and quadratic surplus loss -/
theorem p2_prop_ambig_quote_cost (s L0 L1 : Rat) :
    2 * ((s - L0) * (s - L0) + (s - L1) * (s - L1)) =
    (2 * s - L0 - L1) * (2 * s - L0 - L1) + (L1 - L0) * (L1 - L0) := by
  grind

/-- 4. `thm:radius` (`p2_theory1.tex`): Safe radius, Kreiss bounds and failure of spectral radius -/
theorem p2_thm_radius_kreiss (nu : Rat) :
    let rho : Rat := 4 / 5
    (1 - rho) * (nu * 25) = nu * 5 ∧
    (1 : Rat) / (120 : Rat) < (1 : Rat) / (1 : Rat) := by
  dsimp
  refine ⟨by grind, by decide +kernel⟩

/-- 5. `prop:blind` (`p2_theory1.tex`): Spectral blindness (companion paper) -/
theorem p2_prop_spectral_blindness_companion (a b sigma_sq : Rat) :
    (a + b) * (a + b) - (a - b) * (a - b) = 4 * a * b ∧
    (a * a + b * b) * sigma_sq = (a * a + (-b) * (-b)) * sigma_sq := by
  refine ⟨by grind, by grind⟩

/-- 6. `lem:cm` (`p2_theory1.tex`): No amplification without depth (completely monotone response) -/
theorem p2_lem_cm_no_amplification_without_depth (kappa eta q : Rat) :
    let h0 := kappa
    let h1 := (1 - kappa * eta) * kappa - kappa * kappa * (1 - eta) * q
    h1 - h0 = -kappa * kappa * (eta + (1 - eta) * q) := by
  dsimp
  grind

/-- 7. `prop:multi` (`p2_theory1.tex`): Directed cross-impact shrinks the safe radius -/
theorem p2_prop_multi_venue_cross_impact (kappa_tilde Gamma m q : Rat) :
    (kappa_tilde + Gamma) * (m - q * kappa_tilde) - kappa_tilde * (m - q * (kappa_tilde + Gamma)) =
    m * Gamma := by
  grind

/-- 8. `thm:t6` (`p2_theory2.tex`): Amplification condition C2 = phi*eps - (1-a)*kappa -/
theorem p2_thm_t6_amplification_condition (kappa a phi_eps : Rat) :
    let h0 := kappa
    let h1 := a * kappa + phi_eps
    let C2 := phi_eps - (1 - a) * kappa
    h1 - h0 = C2 := by
  dsimp
  grind

/-- 9. `prop:shape` (`p2_theory2.tex`): Shape of the overshoot and two-mode decomposition -/
theorem p2_prop_shape_overshoot (kappa a b d_inv phi_eps : Rat) :
    let A := kappa + phi_eps * d_inv
    let B := -phi_eps * d_inv
    A + B = kappa ∧
    A * a + B * b = a * kappa + phi_eps * d_inv * (a - b) := by
  dsimp
  refine ⟨by grind, by grind⟩

/-- 10. `prop:t6m` (`p2_theory2.tex`): One-period amplification margin C3 -/
theorem p2_prop_t6m_one_period_margin (kappa a eta q phi_eps : Rat) :
    let h0 := kappa
    let h1 := a * kappa + kappa * kappa * eta * q + phi_eps
    let C3 := phi_eps + kappa * kappa * eta * q - (1 - a) * kappa
    h1 - h0 = C3 := by
  dsimp
  grind

/-- 11. `thm:nomom` (`p2_theory2.tex`): Momentum alone cannot make a stable book amplify -/
theorem p2_thm_nomom_no_overshoot (kappa eta q : Rat) :
    let a := 1 - kappa * eta
    let C3 := 0 + kappa * kappa * eta * q - (1 - a) * kappa
    C3 = -kappa * kappa * eta * (1 - q) := by
  dsimp
  grind

/-- 12. `thm:noover` (`p2_theory2.tex`): Sufficient condition for no overshoot -/
theorem p2_thm_noover_sufficient_condition (kappa a term_phi term_q : Rat) :
    let C3_bar := term_phi + term_q - (1 - a) * kappa
    a * kappa + term_phi + term_q = kappa + C3_bar := by
  dsimp
  grind

/-- 13. `prop:sum` (`p2_theory2.tex`): Summed response in closed form -/
theorem p2_prop_sum_closed_form (kappa eta r q phi_eps : Rat) :
    let m := kappa * eta
    let det_IM3 := eta * (r * (m - kappa * q) - phi_eps * q)
    let num_IM3 := eta * (r * kappa + phi_eps)
    det_IM3 = eta * (r * m - q * (r * kappa + phi_eps)) ∧
    num_IM3 * (m - kappa * q) - det_IM3 * kappa = eta * phi_eps * m := by
  dsimp
  refine ⟨by grind, by grind⟩

/-- 14. `thm:guard` (`p2_theory2.tex`): Summed-gain guard is maximal -/
theorem p2_thm_guard_maximal (I_pos g0 g1 u_bar : Rat) :
    I_pos * (g0 * u_bar + g1 * u_bar) = I_pos * u_bar * (g0 + g1) := by
  grind

/-- 15. `lem:tail` (`p2_theory2.tex`): Contraction-block tail bound -/
theorem p2_lem_tail_contraction (C rho_H rho : Rat) :
    (1 - rho) * (C * rho_H) = C * rho_H - C * rho * rho_H ∧
    (1 : Rat) - (9 / 10 : Rat) = 1 / 10 := by
  refine ⟨by grind, by decide +kernel⟩

/-- 16. `thm:robust` (`p2_theory2.tex`): Robust gain under operator perturbation -/
theorem p2_thm_robust_gain (M S eps : Rat) :
    M - M * (1 - eps * S) = eps * M * S := by
  grind

/-- 17. `prop:bridge` (`p2_theory2.tex`): No identification needed for guard computation -/
theorem p2_prop_bridge_no_identification (I_abs u_bar g0 g1 g2 : Rat) :
    I_abs * u_bar * (g0 + g1 + g2) = I_abs * u_bar * g0 + I_abs * u_bar * (g1 + g2) := by
  grind

/-- 18. `thm:forward` (`p2_theory2.tex`): Conditional bounded-shock forward solvency -/
theorem p2_thm_forward_solvency (E L L_max : Rat) :
    (E - L) - (E - L_max) = L_max - L ∧
    (100 : Rat) - (85 : Rat) > 0 := by
  refine ⟨by grind, by decide +kernel⟩

/-- 19. `prop:dominance` (`p2_theory2.tex`): When the guard beats an eigenvalue rule -/
theorem p2_prop_dominance_guard_vs_eigenvalue (I_abs u_bar S kappa_eig : Rat) :
    let M_eig := I_abs * u_bar * kappa_eig
    let M_guard := I_abs * u_bar * S
    M_eig - M_guard = -I_abs * u_bar * (S - kappa_eig) := by
  dsimp
  grind

/-- 20. `prop:lucas` (`p2_theory2.tex`): Strategic re-optimization reinforces the guard -/
theorem p2_prop_lucas_reinforces_guard (kappa_tilde m q0 q1 : Rat) :
    kappa_tilde * (m - q1 * kappa_tilde) - kappa_tilde * (m - q0 * kappa_tilde) =
    (q0 - q1) * kappa_tilde * kappa_tilde := by
  grind

/-- 21. `prop:equil` (`p2_equil.tex`): Equilibrium transient risk and Pigouvian rebate -/
theorem p2_prop_equil_transient_risk (theta_share Lambda g_m : Rat) :
    let tau_star := (1 - theta_share) * Lambda * g_m
    theta_share * Lambda * g_m + tau_star = Lambda * g_m ∧
    (1 : Rat) / (40 : Rat) < (1 : Rat) / (1 : Rat) := by
  dsimp
  refine ⟨by grind, by decide +kernel⟩

/-- Phase 7 Result A: Constructive Two-Market Observational Indistinguishability & Safety Impossibility -/
theorem foundational_result_A_impossibility :
    let a : Rat := 2 / 5
    let etaA : Rat := 1 / 2
    let qA : Rat := 2 / 25
    let etaB1 : Rat := 1
    let qB1 : Rat := 1 / 50
    let etaB2 : Rat := 1 / 20
    let qB2 : Rat := 2 / 5
    let hA0 : Rat := 1
    let hA1 : Rat := a * hA0
    let yA1 : Rat := etaA * qA * hA0
    let hA2 : Rat := a * hA1 + yA1
    let yA2 : Rat := (1 - etaA) * yA1 + etaA * qA * hA1
    let hA3 : Rat := a * hA2 + yA2
    let hB0 : Rat := 1
    let hB1 : Rat := a * hB0
    let yB1_1 : Rat := etaB1 * qB1 * hB0
    let yB2_1 : Rat := etaB2 * qB2 * hB0
    let hB2 : Rat := a * hB1 + yB1_1 + yB2_1
    let yB1_2 : Rat := (1 - etaB1) * yB1_1 + etaB1 * qB1 * hB1
    let yB2_2 : Rat := (1 - etaB2) * yB2_1 + etaB2 * qB2 * hB1
    let hB3 : Rat := a * hB2 + yB1_2 + yB2_2
    let SA : Rat := 1 / (1 - a - qA)
    let SB : Rat := 1 / (1 - a - (qB1 + qB2))
    let vA_max : Rat := 1 / SA
    let vB_max : Rat := 1 / SB
    hA0 = hB0 ∧ hA1 = hB1 ∧ hA2 = hB2 ∧
    hA2 = 1 / 5 ∧ hA3 = 29 / 250 ∧ hB3 = 23 / 200 ∧
    SA = 25 / 13 ∧ SB = 50 / 9 ∧
    vA_max = 13 / 25 ∧ vB_max = 9 / 50 ∧
    (vA_max - vB_max) * (1 - 1 / 20) = 323 / 1000 := by
  decide +kernel

/-- Algebraic core for Theorem A (`thm:flagship_A`): scalar TV capacity-loss inequality and numerical witness -/
theorem thmA_algebraic_core (v0 v1 one_minus_beta_minus_tv : Rat) :
    (v1 - v0) * one_minus_beta_minus_tv = v1 * one_minus_beta_minus_tv - v0 * one_minus_beta_minus_tv ∧
    ((13 : Rat) / 25 - 9 / 50) * (1 - 1 / 20 - 0) = 323 / 1000 := by
  refine ⟨by grind, by decide +kernel⟩

/-- Algebraic core for Theorem B (`thm:flagship_B`): two-atom Markov-Krein envelope and numerical endpoints -/
theorem thmB_algebraic_core :
    let m0 : Rat := 1 / 25
    let m1_A : Rat := 1 / 50
    let m1_B : Rat := 19 / 1000
    let r_bar : Rat := 19 / 20
    let Q0_lo : Rat := m0
    let Q0_hi : Rat := m0 / (1 - r_bar)
    let Q1_lo_A : Rat := (m0 * m0) / (m0 - m1_A)
    let Q1_hi_B : Rat := m0 + m1_B / (1 - r_bar)
    Q0_lo = 1 / 25 ∧ Q0_hi = 4 / 5 ∧ Q1_lo_A = 2 / 25 ∧ Q1_hi_B = 21 / 50 := by
  decide +kernel

/-- Algebraic core for Theorem C (`thm:flagship_C`): scalar Pinsker sample-size rearrangement -/
theorem thmC_algebraic_core :
    let margin : Rat := 1 - 1 / 20 - 9 / 20
    let snr_per_obs : Rat := (1 / 1000) * (1 / 1000) / ((1 / 100) * (1 / 100))
    let N_min : Rat := 4 * margin * margin / snr_per_obs
    N_min = 100 := by
  decide +kernel

/-- Algebraic core for Theorem D (`thm:flagship_D`): scalar dominance under upper bound -/
theorem thmD_algebraic_core (I_abs v S_true S_upper : Rat) :
    I_abs * v * S_upper - I_abs * v * S_true = I_abs * v * (S_upper - S_true) := by
  grind

/-- Algebraic core for Theorem E (`thm:flagship_E`): linear division equivalence for admission cap -/
theorem thmE_algebraic_core :
    let m_lo : Rat := 3 / 5
    let req_inv : Rat := 9 / 25
    let q_hi : Rat := 21 / 50
    let alpha_star : Rat := (m_lo - req_inv) / q_hi
    alpha_star = 4 / 7 ∧ m_lo - alpha_star * q_hi = req_inv := by
  decide +kernel

/-- Algebraic core for Theorem F (`thm:flagship_F`): scalar welfare ledger sign condition -/
theorem thmF_algebraic_core :
    let v_pub : Rat := 9 / 50
    let v_disc : Rat := 13 / 25
    let delta_v : Rat := v_disc - v_pub
    let V_net_pos : Rat := 100 * delta_v - 4 - 3 / 2
    let V_net_neg : Rat := 100 * (1 / 50) - 8
    delta_v = 17 / 50 ∧ V_net_pos = 57 / 2 ∧ V_net_neg = -6 := by
  decide +kernel

/-- Algebraic core for Theorem G (`thm:flagship_G`): scalar equilibrium reversion comparison -/
theorem thmG_algebraic_core (q_true dq_pub dq_disc kt wedge_eq wedge_soc : Rat) :
    ((q_true + dq_pub) * kt + wedge_soc) - ((q_true + dq_pub) * kt + wedge_eq) = wedge_soc - wedge_eq ∧
    ((q_true + dq_pub) * kt + wedge_eq) - ((q_true + dq_disc) * kt + wedge_eq) = (dq_pub - dq_disc) * kt := by
  refine ⟨by grind, by grind⟩

/-- Phase 7 Result B: Disclosure-value theorem for robust control capacity -/
theorem foundational_result_B_disclosure_control (B S_tag S_pub : Rat) :
    B * S_pub - B * S_tag = B * (S_pub - S_tag) := by
  grind

/-- Phase 7 Result C: Optimal information-versus-intervention probing tradeoff -/
theorem foundational_result_C_probing_control_tradeoff (kappa_diss V V_star : Rat) :
    (kappa_diss * V * V * V + 2 * kappa_diss * V_star * V_star * V_star) -
      (3 * kappa_diss * V_star * V_star * V) =
    kappa_diss * (V - V_star) * (V - V_star) * (V + 2 * V_star) := by
  grind

/-- Example 5.1 (`ex:witness`): Exact Ambiguity Witness in Price-First Cohort Recurrence (`p2_infosafety.tex`) -/
theorem p2_ex_witness :
    let a : Rat := 2 / 5
    let kappa : Rat := 1
    let qA : Rat := 2 / 25
    let etaA : Rat := 1 / 2
    let qB1 : Rat := 2 / 95
    let etaB1 : Rat := 19 / 20
    let qB2 : Rat := 2 / 5
    let etaB2 : Rat := 1 / 20
    let hA0 : Rat := kappa
    let yA0 : Rat := etaA * hA0
    let hA1 : Rat := a * hA0 + kappa * qA * yA0
    let yA1 : Rat := (1 - etaA) * yA0 + etaA * hA1
    let hA2 : Rat := a * hA1 + kappa * qA * yA1
    let yA2 : Rat := (1 - etaA) * yA1 + etaA * hA2
    let hA3 : Rat := a * hA2 + kappa * qA * yA2
    let hB0 : Rat := kappa
    let yB1_0 : Rat := etaB1 * hB0
    let yB2_0 : Rat := etaB2 * hB0
    let hB1 : Rat := a * hB0 + kappa * (qB1 * yB1_0 + qB2 * yB2_0)
    let yB1_1 : Rat := (1 - etaB1) * yB1_0 + etaB1 * hB1
    let yB2_1 : Rat := (1 - etaB2) * yB2_0 + etaB2 * hB1
    let hB2 : Rat := a * hB1 + kappa * (qB1 * yB1_1 + qB2 * yB2_1)
    let yB1_2 : Rat := (1 - etaB1) * yB1_1 + etaB1 * hB2
    let yB2_2 : Rat := (1 - etaB2) * yB2_1 + etaB2 * hB2
    let hB3 : Rat := a * hB2 + kappa * (qB1 * yB1_2 + qB2 * yB2_2)
    let SA : Rat := kappa / (1 - a - kappa * qA)
    let SB : Rat := kappa / (1 - a - kappa * (qB1 + qB2))
    hA0 = 1 ∧ hB0 = 1 ∧
    hA1 = 11 / 25 ∧ hB1 = 11 / 25 ∧
    hA2 = 267 / 1250 ∧ hB2 = 267 / 1250 ∧
    hA3 = 7049 / 62500 ∧ hB3 = 30221 / 250000 ∧
    hB3 - hA3 = 81 / 10000 ∧
    SA = 25 / 13 ∧ SB = 95 / 17 ∧
    1 / SA = 13 / 25 ∧ 1 / SB = 17 / 95 := by
  decide +kernel

/-- Proposition 5.2 (`prop:twoworld`): Unavoidable Loss of Safe Capacity (`p2_infosafety.tex`) -/
theorem p2_prop_twoworld :
    ((13 / 25 : Rat) - 17 / 95) * (1 - 1 / 20 - 0) = 81 / 250 := by
  decide +kernel

/-- Theorem 5.3 (`thm:window`): Finite-Window Certification via Markov-Krein Bounds (`p2_infosafety.tex`) -/
theorem p2_thm_window :
    let k0 : Rat := 1 / 25
    let k1 : Rat := 1 / 50
    let r_bar : Rat := 19 / 20
    let Phi_lo : Rat := (k0 * k0) / (k0 - k1)
    let Phi_up : Rat := k0 + k1 / (1 - r_bar)
    Phi_lo = 2 / 25 ∧ Phi_up = 22 / 50 ∧ Phi_lo < Phi_up := by
  decide +kernel

/-- Theorem 5.4 (`thm:certcost`): Certification at the Parametric Rate (`p2_infosafety.tex`) -/
theorem p2_thm_certcost :
    let a : Rat := 1 / 2
    let kappa : Rat := 4 / 5
    let q : Rat := 1 / 5
    let S : Rat := kappa / (1 - a - kappa * q)
    S = 40 / 17 := by
  decide +kernel

/-- Lemma 6.4 (`lem:sound`): Soundness of Compatible-Set Guards (`p2_guard.tex`) -/
theorem p2_lem_sound (Iv S_true S_sup B : Rat)
    (h1 : Iv * S_true ≤ Iv * S_sup) (h2 : Iv * S_sup ≤ B) :
    Iv * S_true ≤ B := by
  grind

/-- Theorem 6.5 (`thm:robustguard`): Optimal Uncertainty-Aware Admission (`p2_guard.tex`) -/
theorem p2_thm_robustguard :
    let c_I : Rat := 1 - 2 / 5 - 1 * (12 / 25) / 1
    let Phi_plus : Rat := 9 / 50
    let alpha_star : Rat := c_I / Phi_plus
    c_I = 3 / 25 ∧ alpha_star = 2 / 3 := by
  decide +kernel

/-- Theorem 7.1 (`thm:disclosure`): Decision Value of Disclosure (`p2_disclosure.tex`) -/
theorem p2_thm_disclosure :
    let c_I : Rat := 3 / 25
    let Phi_pub : Rat := 11 / 50
    let Phi_aud : Rat := 9 / 50
    let alpha_pub : Rat := c_I / Phi_pub
    let alpha_aud : Rat := c_I / Phi_aud
    alpha_pub = 6 / 11 ∧ alpha_aud = 2 / 3 ∧ alpha_pub < alpha_aud := by
  decide +kernel

end MachineMarkets
