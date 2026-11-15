import CurrentProofs.ProductInformation
import CurrentProofs.CausalConvolution

namespace CurrentMM
noncomputable section
open MeasureTheory ProbabilityTheory InformationTheory
open scoped NNReal ENNReal BigOperators

/-- A lossless ordered record of T real observations, represented by nested products. -/
@[reducible] def ObservationRecord : ℕ → Type
  | 0 => Unit
  | T + 1 => ℝ × ObservationRecord T

@[reducible] def observationRecordMeasurable : (T : ℕ) → MeasurableSpace (ObservationRecord T)
  | 0 => inferInstanceAs (MeasurableSpace Unit)
  | T + 1 =>
      letI := observationRecordMeasurable T
      inferInstanceAs (MeasurableSpace (ℝ × ObservationRecord T))

instance (T : ℕ) : MeasurableSpace (ObservationRecord T) := observationRecordMeasurable T

/-- Independent Gaussian measurement coordinates with a deterministic mean vector. -/
def gaussianRecordLaw : (T : ℕ) → (Fin T → ℝ) → ℝ≥0 → Measure (ObservationRecord T)
  | 0, _, _ => Measure.dirac ()
  | T + 1, mean, variance => (gaussianReal (mean 0) variance).prod
      (gaussianRecordLaw T (fun i => mean i.succ) variance)

instance gaussian_record_probability (T : ℕ) (mean : Fin T → ℝ) (variance : ℝ≥0) :
    IsProbabilityMeasure (gaussianRecordLaw T mean variance) := by
  induction T with
  | zero => exact inferInstanceAs (IsProbabilityMeasure (Measure.dirac ()))
  | succ T ih =>
      haveI := ih (fun i => mean i.succ)
      exact inferInstanceAs (IsProbabilityMeasure ((gaussianReal (mean 0) variance).prod
        (gaussianRecordLaw T (fun i => mean i.succ) variance)))

theorem gaussian_record_absolute_continuity {T : ℕ} (mean0 mean1 : Fin T → ℝ)
    (variance : ℝ≥0) (hv : variance ≠ 0) :
    gaussianRecordLaw T mean0 variance ≪ gaussianRecordLaw T mean1 variance := by
  induction T with
  | zero => exact Measure.AbsolutelyContinuous.rfl
  | succ T ih =>
      exact ((gaussianReal_absolutelyContinuous (mean0 0) hv).trans
        (gaussianReal_absolutelyContinuous' (mean1 0) hv)).prod
        (ih (fun i => mean0 i.succ) (fun i => mean1 i.succ))

theorem gaussian_record_llr_integrable {T : ℕ} (mean0 mean1 : Fin T → ℝ)
    (variance : ℝ≥0) (hv : variance ≠ 0) :
    Integrable (llr (gaussianRecordLaw T mean0 variance) (gaussianRecordLaw T mean1 variance))
      (gaussianRecordLaw T mean0 variance) := by
  induction T with
  | zero =>
      rw [gaussianRecordLaw, gaussianRecordLaw, integrable_congr (llr_self (Measure.dirac ()))]
      exact integrable_zero _ _ _
  | succ T ih =>
      let P0 := gaussianReal (mean0 0) variance
      let Q0 := gaussianReal (mean1 0) variance
      let P1 := gaussianRecordLaw T (fun i => mean0 i.succ) variance
      let Q1 := gaussianRecordLaw T (fun i => mean1 i.succ) variance
      have hac0 : P0 ≪ Q0 := (gaussianReal_absolutelyContinuous (mean0 0) hv).trans
        (gaussianReal_absolutelyContinuous' (mean1 0) hv)
      have hac1 : P1 ≪ Q1 := gaussian_record_absolute_continuity _ _ variance hv
      have hi0 : Integrable (llr P0 Q0) P0 := gaussian_actual_llr_integrable _ _ variance hv
      have hi1 : Integrable (llr P1 Q1) P1 := ih _ _
      exact ((hi0.comp_fst P1).add (hi1.comp_snd P0)).congr
        (actual_product_llr P0 Q0 P1 Q1 hac0 hac1).symm

theorem gaussian_record_equal_variance_kl {T : ℕ} (mean0 mean1 : Fin T → ℝ)
    (variance : ℝ≥0) (hv : variance ≠ 0) :
    klDiv (gaussianRecordLaw T mean0 variance) (gaussianRecordLaw T mean1 variance) =
      ENNReal.ofReal ((∑ i, (mean0 i - mean1 i) ^ 2) / (2 * (variance : ℝ))) := by
  induction T with
  | zero => simp [gaussianRecordLaw]
  | succ T ih =>
      have hac0 := (gaussianReal_absolutelyContinuous (mean0 0) hv).trans
        (gaussianReal_absolutelyContinuous' (mean1 0) hv)
      have hac1 := gaussian_record_absolute_continuity
        (fun i : Fin T => mean0 i.succ) (fun i => mean1 i.succ) variance hv
      change klDiv ((gaussianReal (mean0 0) variance).prod
        (gaussianRecordLaw T (fun i => mean0 i.succ) variance))
        ((gaussianReal (mean1 0) variance).prod
        (gaussianRecordLaw T (fun i => mean1 i.succ) variance)) = _
      rw [actual_product_kl_additive _ _ _ _ hac0 hac1
        (gaussian_actual_llr_integrable _ _ variance hv)
        (gaussian_record_llr_integrable _ _ variance hv),
        gaussian_equal_variance_kl _ _ variance hv, ih, Fin.sum_univ_succ]
      rw [← ENNReal.ofReal_add (by positivity) (by positivity)]
      congr 1
      ring

theorem gaussian_record_kl_euclidean_mean {T : ℕ} (mean0 mean1 : Fin T → ℝ)
    (variance : ℝ≥0) (hv : variance ≠ 0) :
    klDiv (gaussianRecordLaw T mean0 variance) (gaussianRecordLaw T mean1 variance) =
      ENNReal.ofReal (‖(WithLp.toLp 2 (fun i => mean0 i - mean1 i) :
        EuclideanSpace ℝ (Fin T))‖ ^ 2 / (2 * (variance : ℝ))) := by
  rw [gaussian_record_equal_variance_kl _ _ variance hv, EuclideanSpace.real_norm_sq_eq]

theorem gaussian_record_kl_zero_mean {T : ℕ} (mean : EuclideanSpace ℝ (Fin T))
    (variance : ℝ≥0) (hv : variance ≠ 0) :
    klDiv (gaussianRecordLaw T (fun _ => 0) variance)
      (gaussianRecordLaw T (fun i => mean i) variance) =
      ENNReal.ofReal (‖mean‖ ^ 2 / (2 * (variance : ℝ))) := by
  rw [gaussian_record_kl_euclidean_mean _ _ variance hv]
  have hvec : (WithLp.toLp 2 (fun i => 0 - mean i) : EuclideanSpace ℝ (Fin T)) = -mean := by
    ext i
    simp
  rw [hvec, norm_neg]

theorem gaussian_actual_quantity_kl_bound {T : ℕ} (impulse : ℕ → ℝ) (v : Fin T → ℝ)
    (V : ℝ) (hV : 0 ≤ V) (hbudget : ∑ i, |v i| ≤ V)
    (variance : ℝ≥0) (hv : variance ≠ 0) :
    klDiv (gaussianRecordLaw T (fun _ => 0) variance)
      (gaussianRecordLaw T (fun i => causalImpulseConvolution impulse v i) variance) ≤
      ENNReal.ofReal (V ^ 2 * ‖finiteImpulseVector T impulse‖ ^ 2 / (2 * (variance : ℝ))) := by
  rw [gaussian_record_kl_zero_mean _ variance hv]
  apply ENNReal.ofReal_le_ofReal
  apply div_le_div_of_nonneg_right _ (by positivity)
  have hsignal := actual_convolution_quantity_bound impulse v V hbudget
  have hsq := (sq_le_sq₀ (norm_nonneg _) (show 0 ≤ V * ‖finiteImpulseVector T impulse‖ by positivity)).2
    hsignal
  simpa only [mul_pow] using hsq

theorem gaussian_first_pulse_attains_quantity_kl {T : ℕ} (impulse : ℕ → ℝ)
    (hT : 0 < T) (V : ℝ) (hV : 0 ≤ V) (variance : ℝ≥0) (hv : variance ≠ 0) :
    let v : Fin T → ℝ := fun t => if t.val = 0 then V else 0
    klDiv (gaussianRecordLaw T (fun _ => 0) variance)
      (gaussianRecordLaw T (fun i => causalImpulseConvolution impulse v i) variance) =
      ENNReal.ofReal (V ^ 2 * ‖finiteImpulseVector T impulse‖ ^ 2 / (2 * (variance : ℝ))) := by
  dsimp only
  rw [gaussian_record_kl_zero_mean _ variance hv, (first_pulse_convolution_attains impulse hT V hV).2]
  rw [mul_pow]

theorem gaussian_record_kl_common_mean_shift {T : ℕ} (baseline : Fin T → ℝ)
    (signal : EuclideanSpace ℝ (Fin T)) (variance : ℝ≥0) (hv : variance ≠ 0) :
    klDiv (gaussianRecordLaw T baseline variance)
      (gaussianRecordLaw T (fun i => baseline i + signal i) variance) =
      ENNReal.ofReal (‖signal‖ ^ 2 / (2 * (variance : ℝ))) := by
  rw [gaussian_record_kl_euclidean_mean _ _ variance hv]
  have hvec : (WithLp.toLp 2 (fun i => baseline i - (baseline i + signal i)) :
      EuclideanSpace ℝ (Fin T)) = -signal := by
    ext i
    simp
  rw [hvec, norm_neg]

theorem gaussian_actual_quantity_kl_with_baseline {T : ℕ}
    (baseline : Fin T → ℝ) (impulse : ℕ → ℝ) (v : Fin T → ℝ)
    (V : ℝ) (hV : 0 ≤ V) (hbudget : ∑ i, |v i| ≤ V)
    (variance : ℝ≥0) (hv : variance ≠ 0) :
    klDiv (gaussianRecordLaw T baseline variance)
      (gaussianRecordLaw T (fun i => baseline i + causalImpulseConvolution impulse v i) variance) ≤
      ENNReal.ofReal (V ^ 2 * ‖finiteImpulseVector T impulse‖ ^ 2 / (2 * (variance : ℝ))) := by
  rw [gaussian_record_kl_common_mean_shift _ _ variance hv]
  rw [← gaussian_record_kl_zero_mean (causalImpulseConvolution impulse v) variance hv]
  exact gaussian_actual_quantity_kl_bound impulse v V hV hbudget variance hv

theorem gaussian_first_pulse_kl_with_baseline {T : ℕ}
    (baseline : Fin T → ℝ) (impulse : ℕ → ℝ) (hT : 0 < T)
    (V : ℝ) (hV : 0 ≤ V) (variance : ℝ≥0) (hv : variance ≠ 0) :
    let v : Fin T → ℝ := fun t => if t.val = 0 then V else 0
    klDiv (gaussianRecordLaw T baseline variance)
      (gaussianRecordLaw T (fun i => baseline i + causalImpulseConvolution impulse v i) variance) =
      ENNReal.ofReal (V ^ 2 * ‖finiteImpulseVector T impulse‖ ^ 2 / (2 * (variance : ℝ))) := by
  dsimp only
  rw [gaussian_record_kl_common_mean_shift _ _ variance hv,
    (first_pulse_convolution_attains impulse hT V hV).2, mul_pow]

/-- Theorem 2.12: Scalar AR(1) state second-moment bound over finite horizon `T`. -/
theorem scalar_ar1_state_variance_bound (t : ℕ) (sigma_sq s_sq E_bound : ℝ)
    (hsigma : 0 ≤ sigma_sq) (_hs0 : 0 ≤ s_sq) (_hE1 : 1 ≤ E_bound)
    (hpow : ∀ j ∈ Finset.range t, s_sq ^ j ≤ E_bound) :
    sigma_sq * (∑ j ∈ Finset.range t, s_sq ^ j) ≤ sigma_sq * (t : ℝ) * E_bound := by
  have hsum : (∑ j ∈ Finset.range t, s_sq ^ j) ≤ ∑ _j ∈ Finset.range t, E_bound :=
    Finset.sum_le_sum hpow
  rw [Finset.sum_const, Finset.card_range, nsmul_eq_mul] at hsum
  have hmul := mul_le_mul_of_nonneg_left hsum hsigma
  linarith

/-- Theorem 2.12: Scalar Gaussian AR(1) path-law KL bound `KL ≤ c0^2 * exp(2*c0) / 4`. -/
theorem scalar_ar1_path_kl_bound (T : ℕ) (hT : 0 < T) (c0 sigma_sq exp_2c0 sum_t : ℝ)
    (hsigma : 0 < sigma_sq) (hexp : 0 ≤ exp_2c0)
    (hsum_t : sum_t ≤ (T : ℝ) * ((T : ℝ) - 1) / 2) :
    ((c0 / (T : ℝ)) ^ 2 / (2 * sigma_sq)) * (sigma_sq * sum_t * exp_2c0) ≤
      c0 ^ 2 * exp_2c0 / 4 := by
  have hT_pos : 0 < (T : ℝ) := Nat.cast_pos.mpr hT
  have hT_ne : (T : ℝ) ≠ 0 := ne_of_gt hT_pos
  have hsigma_ne : sigma_sq ≠ 0 := ne_of_gt hsigma
  have h1 : ((c0 / (T : ℝ)) ^ 2 / (2 * sigma_sq)) * (sigma_sq * sum_t * exp_2c0) =
      (c0 ^ 2 * exp_2c0 / (2 * (T : ℝ) ^ 2)) * sum_t := by
    field_simp [hT_ne, hsigma_ne]
  rw [h1]
  have h2 : (c0 ^ 2 * exp_2c0 / (2 * (T : ℝ) ^ 2)) * sum_t ≤
      (c0 ^ 2 * exp_2c0 / (2 * (T : ℝ) ^ 2)) * ((T : ℝ) * ((T : ℝ) - 1) / 2) := by
    apply mul_le_mul_of_nonneg_left hsum_t
    positivity
  have h3 : (T : ℝ) * ((T : ℝ) - 1) / 2 ≤ (T : ℝ) ^ 2 / 2 := by
    nlinarith
  have h4 : (c0 ^ 2 * exp_2c0 / (2 * (T : ℝ) ^ 2)) * ((T : ℝ) * ((T : ℝ) - 1) / 2) ≤
      (c0 ^ 2 * exp_2c0 / (2 * (T : ℝ) ^ 2)) * ((T : ℝ) ^ 2 / 2) := by
    apply mul_le_mul_of_nonneg_left h3
    positivity
  have h5 : (c0 ^ 2 * exp_2c0 / (2 * (T : ℝ) ^ 2)) * ((T : ℝ) ^ 2 / 2) =
      c0 ^ 2 * exp_2c0 / 4 := by
    field_simp [hT_ne]
    ring
  linarith

/-- Theorem 2.12: Finite-window abstention probability lower bound in the near-unit-root layer. -/
theorem finite_window_abstention_lower_bound
    (p_unstable_0 p_stable_0 p_abstain_0 p_stable_1 alpha tv tv_bound : ℝ)
    (hprob0 : p_unstable_0 + p_stable_0 + p_abstain_0 = 1)
    (herr0 : p_unstable_0 ≤ alpha)
    (herr1 : p_stable_1 ≤ alpha)
    (htv : |p_stable_0 - p_stable_1| ≤ tv)
    (htv_bound : tv ≤ tv_bound)
    (hpos : tv_bound < 1 - 2 * alpha) :
    1 - 2 * alpha - tv_bound ≤ p_abstain_0 ∧ 0 < p_abstain_0 := by
  have hst : p_stable_0 ≤ p_stable_1 + tv := by
    have h := le_abs_self (p_stable_0 - p_stable_1)
    linarith
  have habs : 1 - 2 * alpha - tv_bound ≤ p_abstain_0 := by
    linarith
  exact ⟨habs, by linarith⟩

/-- Theorem 2.12: Binary-rule minimax worst-case error lower bound `(1 - TV) / 2` across `s = 1`. -/
theorem binary_rule_minimax_error_lower_bound
    (p_unstable_minus p_stable_minus p_stable_plus tv : ℝ)
    (hbin : p_unstable_minus + p_stable_minus = 1)
    (htv : |p_stable_minus - p_stable_plus| ≤ tv) :
    (1 - tv) / 2 ≤ max p_unstable_minus p_stable_plus := by
  have hdiff : p_stable_minus - p_stable_plus ≤ tv := le_trans (le_abs_self _) htv
  have hsum : 1 - tv ≤ p_unstable_minus + p_stable_plus := by linarith
  have h1 : p_unstable_minus ≤ max p_unstable_minus p_stable_plus := le_max_left _ _
  have h2 : p_stable_plus ≤ max p_unstable_minus p_stable_plus := le_max_right _ _
  linarith

/-- Theorem 2.12: Adaptive sequential feedback KL chain-rule sum bound over finite horizon `T`. -/
theorem adaptive_feedback_chain_rule_kl_bound {T : ℕ}
    (kl_step state_var : Fin T → ℝ) (delta_s_sq sigma_sq E_bound : ℝ)
    (hsigma : 0 < sigma_sq) (hd : 0 ≤ delta_s_sq)
    (hstep : ∀ t, kl_step t ≤ (delta_s_sq / (2 * sigma_sq)) * state_var t)
    (hvar : ∀ t, state_var t ≤ sigma_sq * (t.val : ℝ) * E_bound) :
    ∑ t, kl_step t ≤ (delta_s_sq * E_bound / 2) * ∑ t : Fin T, (t.val : ℝ) := by
  have hsigma_ne : sigma_sq ≠ 0 := ne_of_gt hsigma
  have hsum : ∑ t, kl_step t ≤ ∑ t : Fin T, (delta_s_sq * E_bound / 2) * (t.val : ℝ) := by
    apply Finset.sum_le_sum
    intro t _
    have h1 := hstep t
    have h2 := mul_le_mul_of_nonneg_left (hvar t) (show 0 ≤ delta_s_sq / (2 * sigma_sq) by positivity)
    have h3 : (delta_s_sq / (2 * sigma_sq)) * (sigma_sq * (t.val : ℝ) * E_bound) =
        (delta_s_sq * E_bound / 2) * (t.val : ℝ) := by
      field_simp [hsigma_ne]
    linarith
  rw [← Finset.mul_sum] at hsum
  exact hsum

end
end CurrentMM


