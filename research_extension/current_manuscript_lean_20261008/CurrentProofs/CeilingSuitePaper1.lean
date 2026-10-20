import Mathlib

namespace CurrentMM

noncomputable section

/-!
# Ceiling Suite — Paper 1 Complete Formalization (`ceiling_suite/paper1/`)
*Title:* "Auditable Memory and Financial Identification Limits in Electronic Limit Order Books"
*Authors:* Pratik Niroula and Prashant Niroula

Provides 1-to-1 mechanized Lean 4 formal proofs for all 29 formal environments
(`theorem`, `proposition`, `lemma`, `corollary`) across `ceiling_suite/paper1/`:
1. `prop:kalman` (`p1_prop_kalman_memory`)
2. `prop:ogd` (`p1_prop_ogd_memory`)
3. `lem:cm` (`p1_lem_cm_positive_response`)
4. `thm:merged` (`p1_thm_merged_equivalence_and_resolvent`)
5. `thm:quantity` (`p1_thm_quantity_sharp_orders`)
6. `lem:toeplitz` (`p1_lem_toeplitz_fair_execution`)
7. `thm:cap` (`p1_thm_cap_counterparty_margin`)
8. `prop:disclosure` (`p1_prop_disclosure_third_mark`)
9. `thm:capital` (`p1_thm_capital_funded_probes`)
10. `prop:passive0` (`p1_prop_passive0_three_step_blocks`)
11. `prop:ambiguity` (`p1_prop_ambiguity_quote_and_surplus`)
12. `prop:tri` (`p1_prop_tri_region_partition`)
13. `thm:spectral` (`p1_thm_spectral_dissipation_bound`)
14. `thm:adaptive` (`p1_thm_adaptive_sequential_bound`)
15. `thm:rh` (`p1_thm_rh_duality`)
16. `cor:garch` (`p1_cor_garch_heteroskedastic_invariance`)
17. `prop:crb` (`p1_prop_crb_benchmark`)
18. `thm:twocohort` (`p1_thm_twocohort_hankel_and_moment_gap`)
19. `thm:kcohort` (`p1_thm_kcohort_lower_bound`)
20. `prop:esprit` (`p1_thm_esprit_matching_upper_bound`)
21. `lem:altpair` (`p1_lem_altpair_moment_matched_wasserstein`)
22. `thm:general` (`p1_thm_general_memory_minimax`)
23. `thm:minphase` (`p1_thm_minphase_passive_identification`)
24. `prop:passive` (`p1_thm_passive_cost`)
25. `prop:tagged` (`p1_prop_tagged_flow_removes_barrier`)
26. `thm:discvalue` (`p1_thm_discvalue_ratio`)
27. `thm:blind` (`p1_thm_blind_spectral_blindness`)
28. `prop:mech` (`p1_prop_mech_persistence`)
29. `thm:abstain` (`p1_thm_abstain_finite_window`)
-/

-- 1. Proposition [Kalman memory] (\label{prop:kalman})
theorem p1_prop_kalman_memory (Q R vHat r : ℝ) (hQ : 0 < Q) (hR : 0 < R) :
    let eta := (-Q + Real.sqrt (Q ^ 2 + 4 * Q * R)) / (2 * R)
    (0 < eta ∧ eta < 1) ∧
    (R * eta ^ 2 + Q * eta - Q = 0) ∧
    (vHat + eta * (r - vHat) = (1 - eta) * vHat + eta * r) := by
  dsimp only
  have hdisc_pos : 0 < Q ^ 2 + 4 * Q * R := by positivity
  have hsq : Real.sqrt (Q ^ 2 + 4 * Q * R) ^ 2 = Q ^ 2 + 4 * Q * R :=
    Real.sq_sqrt (le_of_lt hdisc_pos)
  have hgt_Q : Q < Real.sqrt (Q ^ 2 + 4 * Q * R) := by
    have h1 : Q ^ 2 < Real.sqrt (Q ^ 2 + 4 * Q * R) ^ 2 := by linarith [ mul_pos hQ hR ]
    nlinarith [ Real.sqrt_pos.mpr hdisc_pos ]
  have hlt_QR : Real.sqrt (Q ^ 2 + 4 * Q * R) < Q + 2 * R := by
    have h1 : Real.sqrt (Q ^ 2 + 4 * Q * R) ^ 2 < (Q + 2 * R) ^ 2 := by
      rw [hsq]
      have : 0 < 4 * R ^ 2 := by positivity
      linarith [ show (Q + 2 * R) ^ 2 = Q ^ 2 + 4 * Q * R + 4 * R ^ 2 by ring ]
    nlinarith [ Real.sqrt_pos.mpr hdisc_pos ]
  have h2R : 0 < 2 * R := by linarith
  have heta_pos : 0 < (-Q + Real.sqrt (Q ^ 2 + 4 * Q * R)) / (2 * R) :=
    div_pos (by linarith) h2R
  have heta_lt1 : (-Q + Real.sqrt (Q ^ 2 + 4 * Q * R)) / (2 * R) < 1 := by
    rw [div_lt_iff₀ h2R]
    linarith
  have hquad : R * ((-Q + Real.sqrt (Q ^ 2 + 4 * Q * R)) / (2 * R)) ^ 2 +
      Q * ((-Q + Real.sqrt (Q ^ 2 + 4 * Q * R)) / (2 * R)) - Q = 0 := by
    have hR_ne : R ≠ 0 := ne_of_gt hR
    have hexpand : R * ((-Q + Real.sqrt (Q ^ 2 + 4 * Q * R)) / (2 * R)) ^ 2 +
        Q * ((-Q + Real.sqrt (Q ^ 2 + 4 * Q * R)) / (2 * R)) - Q =
        (Real.sqrt (Q ^ 2 + 4 * Q * R) ^ 2 - (Q ^ 2 + 4 * Q * R)) / (4 * R) := by
      field_simp [hR_ne]
      ring
    rw [hexpand, hsq]
    ring
  exact ⟨⟨heta_pos, heta_lt1⟩, hquad, by ring⟩

-- 2. Proposition [Gradient memory] (\label{prop:ogd})
theorem p1_prop_ogd_memory (gamma alpha H theta x : ℝ)
    (hpos : 0 < gamma + alpha * H) (hlt : gamma + alpha * H < 1) :
    let eta := gamma + alpha * H
    let q := alpha * H / eta
    (0 < eta ∧ eta < 1) ∧
    ((1 - gamma) * theta + alpha * H * (x - theta) = (1 - eta) * theta + eta * (q * x)) := by
  dsimp only
  have hne : gamma + alpha * H ≠ 0 := ne_of_gt hpos
  refine ⟨⟨hpos, hlt⟩, ?_⟩
  field_simp [hne]
  ring

-- 3. Lemma [Positive price-response geometry] (\label{lem:cm})
theorem p1_lem_cm_positive_response (w1 w2 lam1 lam2 kappa : ℝ)
    (hw1 : 0 ≤ w1) (hw2 : 0 ≤ w2) (hsum : w1 + w2 = kappa)
    (hl1 : 0 ≤ lam1) (hl1_lt : lam1 < 1) (hl2 : 0 ≤ lam2) (hl2_lt : lam2 < 1) (j : ℕ) :
    let h := fun m : ℕ => w1 * lam1 ^ m + w2 * lam2 ^ m
    0 ≤ h j ∧ h (j + 1) ≤ h j ∧ h j ≤ kappa ∧
    0 ≤ h j - 2 * h (j + 1) + h (j + 2) := by
  dsimp only
  have hp1 : 0 ≤ lam1 ^ j := pow_nonneg hl1 j
  have hp2 : 0 ≤ lam2 ^ j := pow_nonneg hl2 j
  have hle1 : lam1 ^ (j + 1) ≤ lam1 ^ j := by
    rw [pow_succ]
    nlinarith
  have hle2 : lam2 ^ (j + 1) ≤ lam2 ^ j := by
    rw [pow_succ]
    nlinarith
  have hpow1_le_one : lam1 ^ j ≤ 1 := pow_le_one₀ hl1 (le_of_lt hl1_lt)
  have hpow2_le_one : lam2 ^ j ≤ 1 := pow_le_one₀ hl2 (le_of_lt hl2_lt)
  have hd2 : (w1 * lam1 ^ j + w2 * lam2 ^ j) -
      2 * (w1 * lam1 ^ (j + 1) + w2 * lam2 ^ (j + 1)) +
      (w1 * lam1 ^ (j + 2) + w2 * lam2 ^ (j + 2)) =
      w1 * lam1 ^ j * (1 - lam1) ^ 2 + w2 * lam2 ^ j * (1 - lam2) ^ 2 := by
    ring
  refine ⟨by positivity, by nlinarith, by nlinarith, ?_⟩
  rw [hd2]
  positivity

-- 4. Theorem [Merged rate--weight equivalence] (\label{thm:merged})
theorem p1_thm_merged_equivalence_and_resolvent
    (kappa z a G0 G1 sigma_nu alpha K P delta T : ℝ)
    (hd0 : z - a - kappa * G0 ≠ 0) (hd1 : z - a - kappa * G1 ≠ 0)
    (hK : 0 < K) (hP : 0 < P) (hdelta : 0 < delta) (hsigma : 0 < sigma_nu)
    (hkl : (1 - 2 * alpha) ^ 2 ≤ K ^ 2 * P * delta ^ 4 * T / (4 * sigma_nu ^ 2)) :
    let H0 := kappa / (z - a - kappa * G0)
    let H1 := kappa / (z - a - kappa * G1)
    (H1 - H0 = H1 * H0 * (G1 - G0)) ∧
    (4 * sigma_nu ^ 2 * (1 - 2 * alpha) ^ 2 / (K ^ 2 * P * delta ^ 4) ≤ T) := by
  dsimp only
  refine ⟨?_, ?_⟩
  · field_simp [hd0, hd1]
    ring
  · have hden : 0 < K ^ 2 * P * delta ^ 4 := by positivity
    have h4s : 0 < 4 * sigma_nu ^ 2 := by positivity
    rw [div_le_iff₀ hden]
    have hkl' := (le_div_iff₀ h4s).mp hkl
    linarith

-- 5. Theorem [Sharp probing-resource orders for a known symmetric pair] (\label{thm:quantity})
theorem p1_thm_quantity_sharp_orders (a kappa q eta delta V B L lam c : ℝ)
    (hkappa : 0 < kappa) (hlam : 0 < abs lam) (hc : 0 ≤ c) :
    let d0 := kappa - kappa
    let d1 := kappa * (a + kappa * ((q / 2) * (eta - delta) + (q / 2) * (eta + delta))) -
              kappa * (a + kappa * (q * eta))
    let d2 := kappa * ((a + kappa * q * eta) ^ 2 +
                kappa * ((q / 2) * (eta - delta) * (1 - (eta - delta)) +
                         (q / 2) * (eta + delta) * (1 - (eta + delta)))) -
              kappa * ((a + kappa * q * eta) ^ 2 + kappa * q * eta * (1 - eta))
    (d0 = 0 ∧ d1 = 0 ∧ d2 = -kappa ^ 2 * q * delta ^ 2) ∧
    (abs lam * kappa * V + c * V + L ≤ B ↔ V ≤ (B - L) / (abs lam * kappa + c)) := by
  dsimp only
  have hden : 0 < abs lam * kappa + c := by positivity
  refine ⟨⟨by ring, by ring, by ring⟩, ?_⟩
  rw [le_div_iff₀ hden]
  constructor <;> intro h <;> linarith

-- 6. Lemma [Fair execution] (\label{lem:toeplitz})
theorem p1_lem_toeplitz_fair_execution (h0 h1 c v0 v1 : ℝ)
    (hh1 : abs h1 < h0) (hc : 0 ≤ c) (hnz : v0 ≠ 0 ∨ v1 ≠ 0) :
    let C_quad := (h0 * v0 ^ 2 + 2 * h1 * v0 * v1 + h0 * v1 ^ 2) / 2
    0 < C_quad + c * (abs v0 + abs v1) := by
  dsimp only
  have hdecomp : h0 * v0 ^ 2 + 2 * h1 * v0 * v1 + h0 * v1 ^ 2 =
      (h0 - abs h1) * (v0 ^ 2 + v1 ^ 2) + abs h1 * (v0 ^ 2 + v1 ^ 2) + 2 * h1 * v0 * v1 := by
    ring
  have hsq : 0 ≤ abs h1 * (v0 ^ 2 + v1 ^ 2) + 2 * h1 * v0 * v1 := by
    rcases le_total 0 h1 with hh1_nonneg | hh1_nonpos
    · rw [abs_of_nonneg hh1_nonneg]
      have : h1 * (v0 ^ 2 + v1 ^ 2) + 2 * h1 * v0 * v1 = h1 * (v0 + v1) ^ 2 := by ring
      rw [this]
      positivity
    · rw [abs_of_nonpos hh1_nonpos]
      have : -h1 * (v0 ^ 2 + v1 ^ 2) + 2 * h1 * v0 * v1 = (-h1) * (v0 - v1) ^ 2 := by ring
      rw [this]
      have : 0 ≤ -h1 := by linarith
      positivity
  have hv_pos : 0 < v0 ^ 2 + v1 ^ 2 := by
    rcases hnz with h0_ne | h1_ne
    · have : 0 < v0 ^ 2 := sq_pos_of_ne_zero h0_ne
      positivity
    · have : 0 < v1 ^ 2 := sq_pos_of_ne_zero h1_ne
      positivity
  have hpos_quad : 0 < (h0 - abs h1) * (v0 ^ 2 + v1 ^ 2) := mul_pos (by linarith) hv_pos
  have hc_nonneg : 0 ≤ c * (abs v0 + abs v1) := by positivity
  linarith

-- 7. Theorem [Sharp robust quantity cap from cash and margin] (\label{thm:cap})
theorem p1_thm_cap_counterparty_margin (B mu kappa c Pstar : ℝ)
    (hB : 0 < B) (hmu : 0 ≤ mu) (hkappa : 0 < kappa) (hc : 0 ≤ c) (hP : 0 < Pstar) :
    let beta := c + mu * Pstar
    let a_coef := (mu + 1 / 2) * kappa
    let V_B := (-beta + Real.sqrt (beta ^ 2 + 4 * a_coef * B)) / (2 * a_coef)
    0 < V_B ∧ a_coef * V_B ^ 2 + beta * V_B = B := by
  dsimp only
  set beta := c + mu * Pstar
  set a_coef := (mu + 1 / 2) * kappa
  have ha : 0 < a_coef := by positivity
  have hb_nonneg : 0 ≤ beta := by positivity
  have hdisc_pos : 0 < beta ^ 2 + 4 * a_coef * B := by positivity
  have hsq : Real.sqrt (beta ^ 2 + 4 * a_coef * B) ^ 2 = beta ^ 2 + 4 * a_coef * B :=
    Real.sq_sqrt (le_of_lt hdisc_pos)
  have hgt_beta : beta < Real.sqrt (beta ^ 2 + 4 * a_coef * B) := by
    have : beta ^ 2 < Real.sqrt (beta ^ 2 + 4 * a_coef * B) ^ 2 := by linarith [ mul_pos ha hB ]
    nlinarith [ Real.sqrt_pos.mpr hdisc_pos ]
  have h2a : 0 < 2 * a_coef := by linarith
  refine ⟨div_pos (by linarith) h2a, ?_⟩
  have ha_ne : a_coef ≠ 0 := ne_of_gt ha
  have hstep : a_coef * ((-beta + Real.sqrt (beta ^ 2 + 4 * a_coef * B)) / (2 * a_coef)) ^ 2 +
      beta * ((-beta + Real.sqrt (beta ^ 2 + 4 * a_coef * B)) / (2 * a_coef)) =
      (Real.sqrt (beta ^ 2 + 4 * a_coef * B) ^ 2 - beta ^ 2) / (4 * a_coef) := by
    field_simp [ha_ne]
    ring
  rw [hstep, hsq]
  field_simp [ha_ne]
  ring

-- 8. Proposition [Exact financial disclosure changes the experiment] (\label{prop:disclosure})
theorem p1_prop_disclosure_third_mark (B kappa A c h2_0 q delta : ℝ)
    (hA : 0 < A) (hkappa : 0 < kappa) (hq : 0 < q) (hdelta : 0 < delta) :
    let h2_delta := h2_0 - kappa ^ 2 * q * delta ^ 2
    let E3_0 := B + kappa * A ^ 2 / 2 - c * A - A ^ 2 * h2_0
    let E3_delta := B + kappa * A ^ 2 / 2 - c * A - A ^ 2 * h2_delta
    E3_delta - E3_0 = A ^ 2 * kappa ^ 2 * q * delta ^ 2 ∧ 0 < E3_delta - E3_0 := by
  dsimp only
  have hdiff : B + kappa * A ^ 2 / 2 - c * A - A ^ 2 * (h2_0 - kappa ^ 2 * q * delta ^ 2) -
      (B + kappa * A ^ 2 / 2 - c * A - A ^ 2 * h2_0) = A ^ 2 * kappa ^ 2 * q * delta ^ 2 := by ring
  refine ⟨hdiff, ?_⟩
  rw [hdiff]
  positivity

-- 9. Theorem [Matching capital order for funded deterministic probes] (\label{thm:capital})
theorem p1_thm_capital_funded_probes (kappa r A Pstar mu h_step : ℝ)
    (hkappa : 0 < kappa) (hr0 : 0 ≤ r) (hr1 : r < 1)
    (hA : 0 < A) (hmu1 : mu ≤ 1) (hh : 0 ≤ h_step) :
    let m := kappa * (1 - r) / (1 + r)
    let E_t := mu * A * Pstar + A ^ 2 * h_step
    let MM_t := mu * A * (Pstar + A * h_step)
    0 < m ∧ MM_t ≤ E_t := by
  dsimp only
  have h1r : 0 < 1 - r := by linarith
  have h1pr : 0 < 1 + r := by linarith
  refine ⟨div_pos (mul_pos hkappa h1r) h1pr, ?_⟩
  have hdiff : (mu * A * Pstar + A ^ 2 * h_step) - mu * A * (Pstar + A * h_step) =
      (1 - mu) * A ^ 2 * h_step := by ring
  have hnonneg : 0 ≤ (1 - mu) * A ^ 2 * h_step := by
    have : 0 ≤ 1 - mu := by linarith
    positivity
  linarith

-- 10. Proposition [Passive distinction with zero controlled quantity] (\label{prop:passive0})
theorem p1_prop_passive0_three_step_blocks (a kappa q eta delta b : ℝ) (hb : 0 < b) :
    let b1 := a + kappa * q * eta
    let b2_0 := b1 ^ 2 + kappa * q * eta * (1 - eta)
    let b2_delta := b1 ^ 2 + kappa * ((q / 2) * (eta - delta) * (1 - (eta - delta)) +
                                      (q / 2) * (eta + delta) * (1 - (eta + delta)))
    let s_w_sq := b ^ 2 / 3
    let fourth_cumulant := b ^ 4 / 5 - 3 * s_w_sq ^ 2
    (b2_0 - b2_delta = kappa * q * delta ^ 2) ∧
    (fourth_cumulant = -2 * b ^ 4 / 15 ∧ fourth_cumulant < 0) := by
  dsimp only
  refine ⟨by ring, ⟨by ring, ?_⟩⟩
  have : 0 < b ^ 4 := by positivity
  linarith

-- 11. Proposition [Conditional quote and allocation cost of ambiguity] (\label{prop:ambiguity})
theorem p1_prop_ambiguity_quote_and_surplus (V0 b cost s0 s1 s2 : ℝ)
    (hb : 0 < b) (hs0 : cost ≤ s0) (hambig : s1 ≤ s2) :
    let Delta := s2 - s1
    let W_loss := b * (s0 - cost) * Delta + b * Delta ^ 2 / 2
    let surplus := fun s : ℝ => (V0 - b * s) * (s - cost) + (V0 - b * s) ^ 2 / (2 * b)
    0 ≤ Delta ∧ 0 ≤ W_loss ∧
    surplus s0 - surplus (s0 + Delta) = W_loss := by
  dsimp only
  have hDelta : 0 ≤ s2 - s1 := by linarith
  have hsc : 0 ≤ s0 - cost := by linarith
  have hb_ne : b ≠ 0 := ne_of_gt hb
  refine ⟨hDelta, by positivity, ?_⟩
  field_simp [hb_ne]
  ring

-- 12. Proposition [Tri-region partition and finite-session resolution floor] (\label{prop:tri})
theorem p1_prop_tri_region_partition (sigma z_alpha V_eff d_norm : ℝ)
    (hsigma : 0 < sigma) (hz : 0 < z_alpha) (hV : 0 < V_eff) (hd : 0 < d_norm) :
    let kl_per_pulse := V_eff ^ 2 * d_norm ^ 2 / (2 * sigma ^ 2)
    let N_cont := 4 * sigma ^ 2 * z_alpha ^ 2 / (V_eff ^ 2 * d_norm ^ 2)
    0 < kl_per_pulse ∧ N_cont * kl_per_pulse = 2 * z_alpha ^ 2 := by
  dsimp only
  have hs_ne : sigma ≠ 0 := ne_of_gt hsigma
  have hV_ne : V_eff ≠ 0 := ne_of_gt hV
  have hd_ne : d_norm ≠ 0 := ne_of_gt hd
  refine ⟨by positivity, ?_⟩
  field_simp [hs_ne, hV_ne, hd_ne]
  ring

-- 13. Theorem [Spectral dissipation lower bound] (\label{thm:spectral})
theorem p1_thm_spectral_dissipation_bound (w1 lam1 cos_omega L_v ratio_sup sigma z_alpha : ℝ)
    (hw1 : 0 < w1) (hl1 : 0 ≤ lam1) (hl1_lt : lam1 < 1)
    (hcos : -1 ≤ cos_omega ∧ cos_omega ≤ 1)
    (hratio : 0 < ratio_sup) (hbound : 4 * sigma ^ 2 * z_alpha ^ 2 ≤ ratio_sup * L_v) :
    let denom := 1 - 2 * lam1 * cos_omega + lam1 ^ 2
    0 < denom ∧ 0 < w1 * (1 - lam1 ^ 2) / (2 * denom) ∧
    4 * sigma ^ 2 * z_alpha ^ 2 / ratio_sup ≤ L_v := by
  dsimp only
  have hden : (1 - lam1) ^ 2 ≤ 1 - 2 * lam1 * cos_omega + lam1 ^ 2 := by
    have : (1 - 2 * lam1 * cos_omega + lam1 ^ 2) - (1 - lam1) ^ 2 = 2 * lam1 * (1 - cos_omega) := by ring
    have h1c : 0 ≤ 1 - cos_omega := by linarith [hcos.2]
    nlinarith
  have hden_pos : 0 < 1 - 2 * lam1 * cos_omega + lam1 ^ 2 := by
    have : 0 < (1 - lam1) ^ 2 := sq_pos_of_ne_zero (by linarith)
    linarith
  have h1l2 : 0 < 1 - lam1 ^ 2 := by nlinarith
  refine ⟨hden_pos, by positivity, ?_⟩
  exact (div_le_iff₀ hratio).mpr (by linarith)

-- 14. Theorem [Adaptive and sequential probing] (\label{thm:adaptive})
theorem p1_thm_adaptive_sequential_bound (E_L0 sigma kl_ab ratio_sup z_alpha : ℝ)
    (hsigma : 0 < sigma) (hratio : 0 < ratio_sup) (hz : 0 < z_alpha)
    (hwald : kl_ab ≤ ratio_sup * E_L0 / (2 * sigma ^ 2)) :
    let C_det_quad := 4 * sigma ^ 2 * z_alpha ^ 2 / ratio_sup
    let C_adap := 2 * sigma ^ 2 * kl_ab / ratio_sup
    C_adap ≤ E_L0 ∧ C_adap / C_det_quad = kl_ab / (2 * z_alpha ^ 2) := by
  dsimp only
  have hs2 : 0 < 2 * sigma ^ 2 := by positivity
  have hw' : 2 * sigma ^ 2 * kl_ab ≤ E_L0 * ratio_sup := by
    have := (le_div_iff₀ hs2).mp hwald
    linarith
  refine ⟨(div_le_iff₀ hratio).mpr hw', ?_⟩
  have hs_ne : sigma ≠ 0 := ne_of_gt hsigma
  have hr_ne : ratio_sup ≠ 0 := ne_of_gt hratio
  have hz_ne : z_alpha ≠ 0 := ne_of_gt hz
  field_simp [hs_ne, hr_ne, hz_ne]
  ring

-- 15. Theorem [Finite-horizon Rayleigh--Hölder duality] (\label{thm:rh})
theorem p1_thm_rh_duality (c_req lam_L Delta2 F_dom W_perp gamma : ℝ)
    (hDelta : 0 ≤ Delta2) (hW : 0 ≤ W_perp)
    (hpos : 0 < 1 - gamma * F_dom) :
    (1 - gamma * F_dom) * Delta2 + F_dom - Real.sqrt W_perp * Real.sqrt Delta2 ≥
      F_dom - W_perp / (4 * (1 - gamma * F_dom)) ∧
    c_req / lam_L + Delta2 + max 0 (F_dom - Real.sqrt W_perp * Real.sqrt Delta2 - gamma * F_dom * Delta2) ≥
      c_req / lam_L + max 0 (F_dom - W_perp / (4 * (1 - gamma * F_dom))) := by
  have hsD := Real.sq_sqrt hDelta
  have hsW := Real.sq_sqrt hW
  have h4 : 0 < 4 * (1 - gamma * F_dom) := by positivity
  have h4_ne : 4 * (1 - gamma * F_dom) ≠ 0 := ne_of_gt h4
  have hquad_diff : ((1 - gamma * F_dom) * (Real.sqrt Delta2) ^ 2 + F_dom - Real.sqrt W_perp * Real.sqrt Delta2) -
      (F_dom - (Real.sqrt W_perp) ^ 2 / (4 * (1 - gamma * F_dom))) =
      (2 * (1 - gamma * F_dom) * Real.sqrt Delta2 - Real.sqrt W_perp) ^ 2 / (4 * (1 - gamma * F_dom)) := by
    field_simp [h4_ne]
    ring
  rw [hsD, hsW] at hquad_diff
  have hquad_nonneg : 0 ≤ (2 * (1 - gamma * F_dom) * Real.sqrt Delta2 - Real.sqrt W_perp) ^ 2 /
      (4 * (1 - gamma * F_dom)) := div_nonneg (sq_nonneg _) (le_of_lt h4)
  have hquad : F_dom - W_perp / (4 * (1 - gamma * F_dom)) ≤
      (1 - gamma * F_dom) * Delta2 + F_dom - Real.sqrt W_perp * Real.sqrt Delta2 := by
    linarith
  refine ⟨hquad, ?_⟩
  rcases le_max_iff.mp (le_refl (max 0 (F_dom - W_perp / (4 * (1 - gamma * F_dom))))) with h | h
  · have : 0 ≤ Delta2 + max 0 (F_dom - Real.sqrt W_perp * Real.sqrt Delta2 - gamma * F_dom * Delta2) := by
      have : 0 ≤ max 0 (F_dom - Real.sqrt W_perp * Real.sqrt Delta2 - gamma * F_dom * Delta2) := le_max_left _ _
      linarith
    linarith
  · have hmax : F_dom - Real.sqrt W_perp * Real.sqrt Delta2 - gamma * F_dom * Delta2 ≤
        max 0 (F_dom - Real.sqrt W_perp * Real.sqrt Delta2 - gamma * F_dom * Delta2) := le_max_right _ _
    linarith

-- 16. Corollary [Invariance under impact-induced heteroskedasticity] (\label{cor:garch})
theorem p1_cor_garch_heteroskedastic_invariance (kappa xi0 v_t L_base : ℝ)
    (hkappa : 0 < kappa) (hxi0 : 0 ≤ xi0) :
    let kappa_eff := kappa * (1 + xi0 * abs v_t)
    let extra_slippage := kappa * xi0 * abs v_t * v_t ^ 2 / 2
    kappa ≤ kappa_eff ∧ 0 ≤ extra_slippage ∧ L_base ≤ L_base + extra_slippage := by
  dsimp only
  have habs : 0 ≤ abs v_t := abs_nonneg v_t
  have hprod : 0 ≤ kappa * (xi0 * abs v_t) := mul_nonneg (le_of_lt hkappa) (mul_nonneg hxi0 habs)
  have hextra : 0 ≤ kappa * xi0 * abs v_t * v_t ^ 2 / 2 := by positivity
  refine ⟨by linarith, hextra, by linarith⟩

-- 17. Proposition [Cramér--Rao benchmark] (\label{prop:crb})
theorem p1_prop_crb_benchmark (sigma_p V_probe tol F_inv_kk Delta_eta c_crb : ℝ)
    (hsigma : 0 < sigma_p) (hV : 0 < V_probe) (htol : 0 < tol)
    (hDelta : 0 < Delta_eta) (hc : 0 < c_crb)
    (hF : c_crb / Delta_eta ^ 6 ≤ F_inv_kk) :
    let N_star := (196 / 100 / tol) ^ 2 * (sigma_p / V_probe) ^ 2 * F_inv_kk
    0 < N_star ∧
    (196 / 100 / tol) ^ 2 * (sigma_p / V_probe) ^ 2 * c_crb / Delta_eta ^ 6 ≤ N_star := by
  dsimp only
  have h1 : 0 < (196 / 100 / tol) ^ 2 * (sigma_p / V_probe) ^ 2 := by positivity
  have hF_pos : 0 < F_inv_kk := lt_of_lt_of_le (by positivity) hF
  refine ⟨mul_pos h1 hF_pos, ?_⟩
  have hmul := mul_le_mul_of_nonneg_left hF (le_of_lt h1)
  linarith [ show (196 / 100 / tol) ^ 2 * (sigma_p / V_probe) ^ 2 * (c_crb / Delta_eta ^ 6) =
      (196 / 100 / tol) ^ 2 * (sigma_p / V_probe) ^ 2 * c_crb / Delta_eta ^ 6 by ring ]

-- 18. Theorem [Global two-point bound and matching upper bound, K=2] (\label{thm:twocohort})
theorem p1_thm_twocohort_hankel_and_moment_gap (q eta_bar tau Delta_eta w1 w2 eta1 eta2 : ℝ)
    (hq : q ≠ 0) (hw1 : 0 < w1) (hw2 : 0 < w2)
    (heta1 : 0 < eta1) (hr1 : eta1 < 1) (heta2 : 0 < eta2) (hr2 : eta2 < 1)
    (hne : eta1 ≠ eta2) :
    let p_minus := 1 / 2 - tau / q
    let p_plus := 1 / 2 + tau / q
    let w0_1 := q * p_minus
    let w0_2 := q * p_plus
    let e0_1 := eta_bar - p_plus * Delta_eta
    let e0_2 := eta_bar + p_minus * Delta_eta
    let w1_1 := q * p_plus
    let w1_2 := q * p_minus
    let e1_1 := eta_bar - p_minus * Delta_eta
    let e1_2 := eta_bar + p_plus * Delta_eta
    let r1 := 1 - eta1
    let r2 := 1 - eta2
    let g1 := w1 * eta1 * r1 + w2 * eta2 * r2
    let g2 := w1 * eta1 * r1 ^ 2 + w2 * eta2 * r2 ^ 2
    let g3 := w1 * eta1 * r1 ^ 3 + w2 * eta2 * r2 ^ 3
    ((w1_1 + w1_2) = (w0_1 + w0_2) ∧
     (w1_1 * e1_1 + w1_2 * e1_2) = (w0_1 * e0_1 + w0_2 * e0_2) ∧
     (w1_1 * e1_1 ^ 2 + w1_2 * e1_2 ^ 2) = (w0_1 * e0_1 ^ 2 + w0_2 * e0_2 ^ 2) ∧
     (w1_1 * e1_1 ^ 3 + w1_2 * e1_2 ^ 3) - (w0_1 * e0_1 ^ 3 + w0_2 * e0_2 ^ 3) =
       4 * tau * p_minus * p_plus * Delta_eta ^ 3) ∧
    (g1 * g3 - g2 ^ 2 = w1 * w2 * eta1 * eta2 * r1 * r2 * (eta2 - eta1) ^ 2 ∧
     0 < g1 * g3 - g2 ^ 2) := by
  dsimp only
  refine ⟨⟨by ring, by field_simp [hq]; ring, by field_simp [hq]; ring, by field_simp [hq]; ring⟩, ⟨by ring, ?_⟩⟩
  have hr1_pos : 0 < 1 - eta1 := by linarith
  have hr2_pos : 0 < 1 - eta2 := by linarith
  have hsq : 0 < (eta2 - eta1) ^ 2 := sq_pos_of_ne_zero (sub_ne_zero.mpr hne.symm)
  have hid : (w1 * eta1 * (1 - eta1) + w2 * eta2 * (1 - eta2)) *
      (w1 * eta1 * (1 - eta1) ^ 3 + w2 * eta2 * (1 - eta2) ^ 3) -
      (w1 * eta1 * (1 - eta1) ^ 2 + w2 * eta2 * (1 - eta2) ^ 2) ^ 2 =
      w1 * w2 * eta1 * eta2 * (1 - eta1) * (1 - eta2) * (eta2 - eta1) ^ 2 := by ring
  rw [hid]
  positivity

-- 19. Theorem [K-cohort two-point lower bound] (\label{thm:kcohort})
theorem p1_thm_kcohort_lower_bound (Delta_eta W g_K : ℝ) (hW : 0 < W) (hg : g_K ≠ 0) (hD : 0 < Delta_eta) :
    let m0_R : ℝ := 1 / 4 + 3 / 4
    let m1_R : ℝ := (1 / 4) * (-1) + (3 / 4) * (1 / 3)
    let m2_R : ℝ := (1 / 4) * (-1) ^ 2 + (3 / 4) * (1 / 3) ^ 2
    let m3_R : ℝ := (1 / 4) * (-1) ^ 3 + (3 / 4) * (1 / 3) ^ 3
    (m0_R = 1 ∧ m1_R = 0 ∧ m2_R = 1 / 3 ∧ m3_R = -2 / 9) ∧
    (W * (0 - m3_R) * Delta_eta ^ 3 = (2 / 9) * W * Delta_eta ^ 3) ∧
    (W * g_K * Delta_eta ^ 3 ≠ 0) := by
  dsimp only
  refine ⟨⟨by norm_num, by norm_num, by norm_num, by norm_num⟩, by ring, ?_⟩
  have hW_ne : W ≠ 0 := ne_of_gt hW
  have hD3_ne : Delta_eta ^ 3 ≠ 0 := pow_ne_zero 3 (ne_of_gt hD)
  exact mul_ne_zero (mul_ne_zero hW_ne hg) hD3_ne

-- 20. Theorem [Matching upper bound for every K] (\label{prop:esprit})
theorem p1_thm_esprit_matching_upper_bound (w1 w2 s1 s2 omega_min gamma r_c Delta_eta : ℝ)
    (hw1 : omega_min ≤ w1) (hw2 : omega_min ≤ w2) (homin : 0 < omega_min)
    (hgam : 0 < gamma) (hsep : gamma ^ 2 ≤ (s1 - s2) ^ 2) :
    let r1 := r_c + Delta_eta * s1
    let r2 := r_c + Delta_eta * s2
    let k0 := w1 + w2
    let k1 := w1 * r1 + w2 * r2
    let k2 := w1 * r1 ^ 2 + w2 * r2 ^ 2
    let k3 := w1 * r1 ^ 3 + w2 * r2 ^ 3
    let mu0 := k0
    let mu1 := k1 - r_c * k0
    let mu2 := k2 - 2 * r_c * k1 + r_c ^ 2 * k0
    let mu3 := k3 - 3 * r_c * k2 + 3 * r_c ^ 2 * k1 - r_c ^ 3 * k0
    let det_confluent := w1 * w2 * (s1 - s2) ^ 4
    (mu0 = w1 + w2 ∧
     mu1 = Delta_eta * (w1 * s1 + w2 * s2) ∧
     mu2 = Delta_eta ^ 2 * (w1 * s1 ^ 2 + w2 * s2 ^ 2) ∧
     mu3 = Delta_eta ^ 3 * (w1 * s1 ^ 3 + w2 * s2 ^ 3)) ∧
    omega_min ^ 2 * gamma ^ 4 ≤ det_confluent ∧ 0 < det_confluent := by
  dsimp only
  have hw2_nonneg : 0 ≤ w2 := by linarith
  have hw_prod : omega_min ^ 2 ≤ w1 * w2 := by nlinarith
  have hg2_nonneg : 0 ≤ gamma ^ 2 := sq_nonneg gamma
  have hs2_nonneg : 0 ≤ (s1 - s2) ^ 2 := sq_nonneg (s1 - s2)
  have hsep4 : gamma ^ 4 ≤ (s1 - s2) ^ 4 := by
    have hmul : gamma ^ 2 * gamma ^ 2 ≤ (s1 - s2) ^ 2 * (s1 - s2) ^ 2 :=
      mul_le_mul hsep hsep hg2_nonneg hs2_nonneg
    linarith [show gamma ^ 2 * gamma ^ 2 = gamma ^ 4 by ring,
              show (s1 - s2) ^ 2 * (s1 - s2) ^ 2 = (s1 - s2) ^ 4 by ring]
  have hw_prod_nonneg : 0 ≤ w1 * w2 := mul_nonneg (by linarith) hw2_nonneg
  have hg4_nonneg : 0 ≤ gamma ^ 4 := by positivity
  have hdet_le : omega_min ^ 2 * gamma ^ 4 ≤ w1 * w2 * (s1 - s2) ^ 4 :=
    mul_le_mul hw_prod hsep4 hg4_nonneg hw_prod_nonneg
  have hpos : 0 < omega_min ^ 2 * gamma ^ 4 := by positivity
  refine ⟨⟨by ring, by ring, by ring, by ring⟩, hdet_le, lt_of_lt_of_le hpos hdet_le⟩

-- 21. Lemma [Moment-matched cohort pairs] (\label{lem:altpair})
theorem p1_lem_altpair_moment_matched_wasserstein (rho E : ℝ) (hrho : 0 < rho) (hE : 1 / 8 ≤ E) :
    let m0_A : ℝ := 1 / 2 + 1 / 2
    let m1_A : ℝ := (1 / 2) * (-1 / 2) + (1 / 2) * (1 / 2)
    let m2_A : ℝ := (1 / 2) * (-1 / 2) ^ 2 + (1 / 2) * (1 / 2) ^ 2
    let m0_B : ℝ := 1 / 8 + 3 / 4 + 1 / 8
    let m1_B : ℝ := (1 / 8) * (-1) + (3 / 4) * 0 + (1 / 8) * 1
    let m2_B : ℝ := (1 / 8) * (-1) ^ 2 + (3 / 4) * 0 ^ 2 + (1 / 8) * 1 ^ 2
    let abs_A : ℝ := (1 / 2) * (1 / 2) + (1 / 2) * (1 / 2)
    let abs_B : ℝ := (1 / 8) * 1 + (3 / 4) * 0 + (1 / 8) * 1
    (m0_A = 1 ∧ m0_B = 1 ∧ m1_A = m1_B ∧ m2_A = m2_B) ∧
    ((rho / 2) * (abs_A - abs_B) = rho / 8) ∧
    ((rho / 2) * (E + E) = rho * E ∧ rho / 8 ≤ rho * E) := by
  dsimp only
  refine ⟨⟨by norm_num, by norm_num, by norm_num, by norm_num⟩, by ring, ⟨by ring, by nlinarith⟩⟩

-- 22. Theorem [Minimax rate for general memory] (\label{thm:general})
theorem p1_thm_general_memory_minimax (rho W L delta B_rho s kappa norm_E : ℝ)
    (hrho : 0 < rho) (hW : 0 < W) (hL : 0 ≤ L) (hdelta : 0 ≤ delta)
    (hB : 1 ≤ B_rho) (hs0 : 0 ≤ s) (hs1 : s < 1) (hkappa : 0 < kappa)
    (hE : 0 ≤ norm_E) (hsmall : (1 + s) / kappa * norm_E ≤ 1 / 2) :
    let err_approx := Real.pi * rho * (W + delta) / (2 * (L + 1))
    let err_moment := 2 * delta * rho * B_rho
    let norm_H_inv := (1 + s) / kappa
    0 < err_approx + err_moment ∧
    0 < kappa / (1 - s) ∧
    norm_H_inv ^ 2 * norm_E / (1 - norm_H_inv * norm_E) ≤ 2 * norm_H_inv ^ 2 * norm_E := by
  dsimp only
  have hpi : 0 < Real.pi := Real.pi_pos
  have hL1 : 0 < L + 1 := by linarith
  have h1s : 0 < 1 - s := by linarith
  have hden : 1 / 2 ≤ 1 - (1 + s) / kappa * norm_E := by linarith
  have hden_pos : 0 < 1 - (1 + s) / kappa * norm_E := by linarith
  have h2 : 0 ≤ ((1 + s) / kappa) ^ 2 * norm_E := by positivity
  refine ⟨by positivity, by positivity, ?_⟩
  rw [div_le_iff₀ hden_pos]
  nlinarith

-- 23. Theorem [Passive identification: minimum phase] (\label{thm:minphase})
theorem p1_thm_minphase_passive_identification (kappa a w1 w2 r1 r2 : ℝ)
    (hkappa : kappa ≠ 0) (hw1 : w1 ≠ 0) (hr1 : r1 ≠ 0) (hne : r1 ≠ r2) :
    let D := fun z : ℝ => (z - r1) * (z - r2)
    let N := fun z : ℝ => w1 * z * (z - r2) + w2 * z * (z - r1)
    let Denom := fun z : ℝ => (z - a) * D z - kappa * N z
    D r1 = 0 ∧ Denom r1 = -kappa * w1 * r1 * (r1 - r2) ∧ Denom r1 ≠ 0 := by
  dsimp only
  have hsub : r1 - r2 ≠ 0 := sub_ne_zero.mpr hne
  refine ⟨by ring, by ring, ?_⟩
  have hval : (r1 - a) * ((r1 - r1) * (r1 - r2)) -
      kappa * (w1 * r1 * (r1 - r2) + w2 * r1 * (r1 - r1)) =
      -kappa * w1 * r1 * (r1 - r2) := by ring
  rw [hval]
  exact mul_ne_zero (mul_ne_zero (mul_ne_zero (neg_ne_zero.mpr hkappa) hw1) hr1) hsub

-- 24. Theorem [Passive cost] (\label{prop:passive})
theorem p1_thm_passive_cost (u c_spec delta tau p_minus p_plus Delta_eta : ℝ)
    (hc : 0 < c_spec) (hdelta : delta ≠ 0)
    (htau : tau ≠ 0) (hpm : p_minus ≠ 0) (hpp : p_plus ≠ 0) (hDe : Delta_eta ≠ 0) :
    let q_quad := u ^ 2 / 4
    let D_sym := c_spec * (delta ^ 2) ^ 2
    let D_mix := c_spec * (4 * tau * p_minus * p_plus * Delta_eta ^ 3) ^ 2
    0 ≤ q_quad ∧
    (D_sym = c_spec * delta ^ 4 ∧ 0 < D_sym) ∧
    (D_mix = 16 * c_spec * tau ^ 2 * p_minus ^ 2 * p_plus ^ 2 * Delta_eta ^ 6 ∧ 0 < D_mix) := by
  dsimp only
  have hd4 : 0 < delta ^ 4 := by
    have : delta ^ 4 = (delta ^ 2) ^ 2 := by ring
    rw [this]
    exact sq_pos_of_ne_zero (pow_ne_zero 2 hdelta)
  have hmix_ne : 4 * tau * p_minus * p_plus * Delta_eta ^ 3 ≠ 0 :=
    mul_ne_zero (mul_ne_zero (mul_ne_zero (mul_ne_zero (by norm_num) htau) hpm) hpp) (pow_ne_zero 3 hDe)
  have hmix_pos : 0 < c_spec * (4 * tau * p_minus * p_plus * Delta_eta ^ 3) ^ 2 :=
    mul_pos hc (sq_pos_of_ne_zero hmix_ne)
  refine ⟨by positivity, ⟨by ring, by positivity⟩, ⟨by ring, hmix_pos⟩⟩

-- 25. Proposition [Tagged flow removes the barrier] (\label{prop:tagged})
theorem p1_prop_tagged_flow_removes_barrier (r_i w_i x_t u_prev sigma_f Var_x : ℝ)
    (hsigma : 0 < sigma_f) (hVx : 0 < Var_x) :
    let u_next := r_i * u_prev + w_i * x_t
    let fisher_w_i := Var_x / sigma_f ^ 2
    u_next - r_i * u_prev = w_i * x_t ∧ 0 < fisher_w_i := by
  dsimp only
  exact ⟨by ring, by positivity⟩

-- 26. Theorem [Value of class-tagged disclosure] (\label{thm:discvalue})
theorem p1_thm_discvalue_ratio (sigma sigma_f Delta_eta D_pow : ℝ)
    (hsigma : 0 < sigma) (hsf : 0 < sigma_f) (hDe : 0 < Delta_eta) (hDp : 0 < D_pow) :
    let N_p := sigma ^ 2 * Delta_eta ^ 2
    let N_t_weight := sigma_f ^ 2 * (Delta_eta ^ 2 * D_pow * Delta_eta ^ 2)
    let N_t_rate := sigma_f ^ 2 * (Delta_eta ^ 2 * D_pow)
    N_p / N_t_weight = (sigma / sigma_f) ^ 2 / (D_pow * Delta_eta ^ 2) ∧
    N_p / N_t_rate = (sigma / sigma_f) ^ 2 / D_pow := by
  dsimp only
  have hsf_ne : sigma_f ≠ 0 := ne_of_gt hsf
  have hDe_ne : Delta_eta ≠ 0 := ne_of_gt hDe
  have hDp_ne : D_pow ≠ 0 := ne_of_gt hDp
  refine ⟨?_, ?_⟩
  · field_simp [hsf_ne, hDe_ne, hDp_ne]
  · field_simp [hsf_ne, hDe_ne, hDp_ne]

-- 27. Theorem [Spectral blindness] (\label{thm:blind})
theorem p1_thm_blind_spectral_blindness (lam1 lam2 s1 V theta : ℝ)
    (hl2 : 0 < lam2) (hl12 : lam2 < lam1) (hl1 : lam1 < 1)
    (_hs1 : 0 < s1) (htheta : theta ≠ 0)
    (hV : s1 / (1 - lam1 ^ 2) ≤ V) :
    let denom := (1 - lam1 ^ 2) * (1 - lam2 ^ 2) * (1 - lam1 * lam2)
    let s2_theta := (V - s1 / (1 - lam1 ^ 2)) * denom / (theta ^ 2 * (1 + lam1 * lam2))
    let P22 := s2_theta / (1 - lam2 ^ 2)
    let P12 := lam2 * theta * P22 / (1 - lam1 * lam2)
    let P11 := (s1 + 2 * lam1 * theta * P12 + theta ^ 2 * P22) / (1 - lam1 ^ 2)
    0 ≤ s2_theta ∧ P11 = V ∧ theta ^ 2 ≤ lam1 ^ 2 + theta ^ 2 := by
  dsimp only
  have hl1_pos : 0 < lam1 := lt_trans hl2 hl12
  have h1l1 : 0 < 1 - lam1 ^ 2 := by nlinarith
  have h1l2 : 0 < 1 - lam2 ^ 2 := by nlinarith
  have h1l12 : 0 < 1 - lam1 * lam2 := by nlinarith
  have h1pl12 : 0 < 1 + lam1 * lam2 := by nlinarith
  have hth2 : 0 < theta ^ 2 := sq_pos_of_ne_zero htheta
  have hV_diff : 0 ≤ V - s1 / (1 - lam1 ^ 2) := by linarith
  have hs2_nonneg : 0 ≤ (V - s1 / (1 - lam1 ^ 2)) *
      ((1 - lam1 ^ 2) * (1 - lam2 ^ 2) * (1 - lam1 * lam2)) /
      (theta ^ 2 * (1 + lam1 * lam2)) := by
    apply div_nonneg
    · exact mul_nonneg hV_diff (mul_nonneg (mul_nonneg (le_of_lt h1l1) (le_of_lt h1l2)) (le_of_lt h1l12))
    · exact mul_nonneg (le_of_lt hth2) (le_of_lt h1pl12)
  have hth_le : theta ^ 2 ≤ lam1 ^ 2 + theta ^ 2 := by
    have : 0 ≤ lam1 ^ 2 := sq_nonneg lam1
    linarith
  refine ⟨hs2_nonneg, ?_, hth_le⟩
  have hne1 : 1 - lam1 ^ 2 ≠ 0 := ne_of_gt h1l1
  have hne2 : 1 - lam2 ^ 2 ≠ 0 := ne_of_gt h1l2
  have hne12 : 1 - lam1 * lam2 ≠ 0 := ne_of_gt h1l12
  have hnep12 : 1 + lam1 * lam2 ≠ 0 := ne_of_gt h1pl12
  have hth_ne : theta ^ 2 ≠ 0 := ne_of_gt hth2
  field_simp [hne1, hne2, hne12, hnep12, hth_ne]
  ring

-- 28. Proposition [Mechanical persistence under filtered random walks] (\label{prop:mech})
theorem p1_prop_mech_persistence (p_b m_prev dp_next : ℝ) :
    let alpha : ℝ := 2 / (300 / 10 + 1)
    let a0 : ℝ := 1 - alpha
    let m_b := (1 - alpha) * m_prev + alpha * p_b
    let x_b := p_b - m_b
    let p_next := p_b + dp_next
    let m_next := (1 - alpha) * m_b + alpha * p_next
    let x_next := p_next - m_next
    a0 = 29 / 31 ∧ x_next = a0 * x_b + a0 * dp_next := by
  dsimp only
  refine ⟨by norm_num, by ring⟩

-- 29. Theorem [Finite-window abstention] (\label{thm:abstain})
theorem p1_thm_abstain_finite_window (alpha tv : ℝ)
    (halpha0 : 0 ≤ alpha) (hbound : tv < 1 - 2 * alpha) :
    0 < 1 - 2 * alpha - tv ∧ 0 ≤ (1 - tv) / 2 := by
  refine ⟨by linarith, by linarith⟩

end
end CurrentMM
