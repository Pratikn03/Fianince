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

end
end CurrentMM
