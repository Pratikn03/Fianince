import CurrentProofs.GaussianInformation
import Mathlib.MeasureTheory.Measure.WithDensity
import Mathlib.MeasureTheory.Integral.Prod

namespace CurrentMM
noncomputable section
open MeasureTheory InformationTheory
open scoped ENNReal

theorem actual_product_rn_derivative {α β : Type*} [MeasurableSpace α] [MeasurableSpace β]
    (μ0 ν0 : Measure α) (μ1 ν1 : Measure β)
    [SigmaFinite μ0] [SigmaFinite ν0] [SigmaFinite μ1] [SigmaFinite ν1]
    (h0 : μ0 ≪ ν0) (h1 : μ1 ≪ ν1) :
    (μ0.prod μ1).rnDeriv (ν0.prod ν1) =ᵐ[ν0.prod ν1]
      fun p => μ0.rnDeriv ν0 p.1 * μ1.rnDeriv ν1 p.2 := by
  have hwd : (ν0.prod ν1).withDensity
      (fun p => μ0.rnDeriv ν0 p.1 * μ1.rnDeriv ν1 p.2) = μ0.prod μ1 := by
    rw [← prod_withDensity (Measure.measurable_rnDeriv μ0 ν0)
      (Measure.measurable_rnDeriv μ1 ν1),
      Measure.withDensity_rnDeriv_eq μ0 ν0 h0, Measure.withDensity_rnDeriv_eq μ1 ν1 h1]
  rw [← hwd]
  exact Measure.rnDeriv_withDensity _ (by fun_prop)

theorem actual_product_llr {α β : Type*} [MeasurableSpace α] [MeasurableSpace β]
    (μ0 ν0 : Measure α) (μ1 ν1 : Measure β)
    [SigmaFinite μ0] [SigmaFinite ν0] [SigmaFinite μ1] [SigmaFinite ν1]
    (h0 : μ0 ≪ ν0) (h1 : μ1 ≪ ν1) :
    llr (μ0.prod μ1) (ν0.prod ν1) =ᵐ[μ0.prod μ1]
      fun p => llr μ0 ν0 p.1 + llr μ1 ν1 p.2 := by
  have hprod := h0.prod h1
  have hpos0 := (Measure.quasiMeasurePreserving_fst (μ := μ0) (ν := μ1)).ae
    (Measure.rnDeriv_pos h0)
  have hpos1 := (Measure.quasiMeasurePreserving_snd (μ := μ0) (ν := μ1)).ae
    (Measure.rnDeriv_pos h1)
  have htop0 := (Measure.quasiMeasurePreserving_fst (μ := μ0) (ν := μ1)).ae
    (h0.ae_le (Measure.rnDeriv_lt_top μ0 ν0))
  have htop1 := (Measure.quasiMeasurePreserving_snd (μ := μ0) (ν := μ1)).ae
    (h1.ae_le (Measure.rnDeriv_lt_top μ1 ν1))
  filter_upwards [hprod.ae_le (actual_product_rn_derivative μ0 ν0 μ1 ν1 h0 h1),
    hpos0, hpos1, htop0, htop1] with p hp hp0 hp1 ht0 ht1
  unfold llr
  rw [hp, ENNReal.toReal_mul, Real.log_mul]
  · exact ENNReal.toReal_ne_zero.mpr ⟨hp0.ne', ht0.ne⟩
  · exact ENNReal.toReal_ne_zero.mpr ⟨hp1.ne', ht1.ne⟩

theorem actual_product_kl_additive {α β : Type*} [MeasurableSpace α] [MeasurableSpace β]
    (μ0 ν0 : Measure α) (μ1 ν1 : Measure β)
    [IsProbabilityMeasure μ0] [IsProbabilityMeasure ν0]
    [IsProbabilityMeasure μ1] [IsProbabilityMeasure ν1]
    (h0 : μ0 ≪ ν0) (h1 : μ1 ≪ ν1)
    (hi0 : Integrable (llr μ0 ν0) μ0) (hi1 : Integrable (llr μ1 ν1) μ1) :
    klDiv (μ0.prod μ1) (ν0.prod ν1) = klDiv μ0 ν0 + klDiv μ1 ν1 := by
  have hi : Integrable (llr (μ0.prod μ1) (ν0.prod ν1)) (μ0.prod μ1) :=
    ((hi0.comp_fst μ1).add (hi1.comp_snd μ0)).congr (actual_product_llr μ0 ν0 μ1 ν1 h0 h1).symm
  rw [klDiv_of_ac_of_integrable (h0.prod h1) hi,
    klDiv_of_ac_of_integrable h0 hi0, klDiv_of_ac_of_integrable h1 hi1]
  rw [integral_congr_ae (actual_product_llr μ0 ν0 μ1 ν1 h0 h1),
    integral_add (hi0.comp_fst μ1) (hi1.comp_snd μ0), integral_fun_fst, integral_fun_snd]
  simp only [probReal_univ, smul_eq_mul, one_mul, add_sub_cancel_right]
  rw [ENNReal.ofReal_add]
  · have h := integral_llr_add_sub_measure_univ_nonneg h0 hi0
    simpa only [probReal_univ, add_sub_cancel_right] using h
  · have h := integral_llr_add_sub_measure_univ_nonneg h1 hi1
    simpa only [probReal_univ, add_sub_cancel_right] using h

/-- Proposition 2.10: Three-step passive reset block price expansion and second-lag coefficient gap. -/
theorem passive_three_step_price_expansion (a kappa q eta delta w1 w2 w3 : ℝ) :
    let b1 := a + kappa * q * eta
    let b2_0 := b1 ^ 2 + kappa * q * eta * (1 - eta)
    let b2_d := b1 ^ 2 + kappa * (q / 2) * ((eta - delta) * (1 - (eta - delta)) +
      (eta + delta) * (1 - (eta + delta)))
    b2_0 - b2_d = kappa * q * delta ^ 2 ∧
    (b2_0 * w1 + b1 * w2 + w3) - (b2_d * w1 + b1 * w2 + w3) =
      kappa * q * delta ^ 2 * w1 := by
  dsimp only
  constructor <;> ring

/-- Proposition 2.10: Bounded innovations keep three-step passive block price marks positive when `3b < P*`. -/
theorem passive_block_price_mark_positive (P_star b b1 b2 w1 w2 w3 : ℝ)
    (hb1_0 : 0 ≤ b1) (hb1_1 : b1 ≤ 1) (hb2_0 : 0 ≤ b2) (hb2_1 : b2 ≤ 1)
    (hw1 : |w1| ≤ b) (hw2 : |w2| ≤ b) (hw3 : |w3| ≤ b) (hP : 3 * b < P_star) :
    |b2 * w1 + b1 * w2 + w3| ≤ 3 * b ∧ 0 < P_star + (b2 * w1 + b1 * w2 + w3) := by
  have hb : 0 ≤ b := le_trans (abs_nonneg w1) hw1
  have h1 : |b2 * w1| ≤ b := by
    rw [abs_mul, abs_of_nonneg hb2_0]
    nlinarith
  have h2 : |b1 * w2| ≤ b := by
    rw [abs_mul, abs_of_nonneg hb1_0]
    nlinarith
  have htri : |b2 * w1 + b1 * w2 + w3| ≤ |b2 * w1| + |b1 * w2| + |w3| := by
    calc |b2 * w1 + b1 * w2 + w3| ≤ |b2 * w1 + b1 * w2| + |w3| := abs_add_le _ _
      _ ≤ |b2 * w1| + |b1 * w2| + |w3| := by linarith [abs_add_le (b2 * w1) (b1 * w2)]
  have habs : |b2 * w1 + b1 * w2 + w3| ≤ 3 * b := by linarith
  refine ⟨habs, ?_⟩
  have hlow := neg_le_of_abs_le habs
  linarith

/-- Proposition 2.10: Uniform innovation fourth cumulant is nonpositive, so the envelope `R` bounds product variance. -/
theorem passive_uniform_fourth_cumulant_nonpos (b sigma_sq b1 b2 : ℝ) :
    let sw_sq := b ^ 2 / 3
    let m4_unif := b ^ 4 / 5
    let R := (sw_sq + sigma_sq) * (sw_sq * (1 + b1 ^ 2 + b2 ^ 2) + sigma_sq) + sw_sq ^ 2 * b2 ^ 2
    m4_unif - 3 * sw_sq ^ 2 = -2 * b ^ 4 / 15 ∧
    R + b2 ^ 2 * (m4_unif - 3 * sw_sq ^ 2) ≤ R := by
  dsimp only
  refine ⟨by ring, ?_⟩
  have hcum : b ^ 4 / 5 - 3 * (b ^ 2 / 3) ^ 2 = -(2 / 15) * (b ^ 2) ^ 2 := by ring
  have hnonpos : b2 ^ 2 * (b ^ 4 / 5 - 3 * (b ^ 2 / 3) ^ 2) ≤ 0 := by
    rw [hcum]
    nlinarith [sq_nonneg b2, sq_nonneg (b ^ 2)]
  linarith

/-- Proposition 2.10: Covariance separation and Chebyshev midpoint-test sample complexity bound. -/
theorem passive_covariance_gap_and_chebyshev_sample_bound
    (kappa q sw_sq delta R alpha n : ℝ)
    (hR : 0 < R) (halpha : 0 < alpha) (hdelta : 0 < kappa * q * sw_sq * delta ^ 2)
    (hn : 4 * R / (alpha * (kappa * q * sw_sq * delta ^ 2) ^ 2) ≤ n) :
    let Delta := kappa * q * sw_sq * delta ^ 2
    0 < n ∧ 4 * (R / n) / Delta ^ 2 ≤ alpha := by
  dsimp only
  set Delta := kappa * q * sw_sq * delta ^ 2
  have hD2 : 0 < Delta ^ 2 := sq_pos_of_pos hdelta
  have hn_pos : 0 < n := lt_of_lt_of_le (by positivity) hn
  refine ⟨hn_pos, ?_⟩
  rw [div_le_iff₀ hD2]
  have h1 : 4 * R / (alpha * Delta ^ 2) * (alpha * Delta ^ 2) ≤ n * (alpha * Delta ^ 2) :=
    mul_le_mul_of_nonneg_right hn (by positivity)
  rw [div_mul_cancel₀ _ (by positivity)] at h1
  have h2 : 4 * (R / n) = 4 * R / n := by ring
  rw [h2, div_le_iff₀ hn_pos]
  linarith

end
end CurrentMM

