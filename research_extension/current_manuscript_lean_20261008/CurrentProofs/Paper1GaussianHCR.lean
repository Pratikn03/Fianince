import Mathlib.Probability.Moments.Variance
import Mathlib.Probability.Moments.Covariance
import Mathlib.Algebra.QuadraticDiscriminant
import Mathlib.Probability.Distributions.Gaussian.Real
import Mathlib.Probability.Moments.MGFAnalytic
import CurrentProofs.GaussianRecords

/-!
# Paper 1, Proposition S7.1, part 1: the Hammersley–Chapman–Robbins bound for the Gaussian probe record

This file proves, for the paper's Gaussian probe record `Y ~ N(m, v I_n)` (the averaged record of
Proposition S7.1, `gaussianRecordLaw n m v`), the Hammersley–Chapman–Robbins inequality

`(E_{m₁}[T] - E_{m₀}[T])² ≤ Var_{m₀}(T) · (exp(‖m₁ - m₀‖²/v) - 1)`

for **every** statistic `T` that is square-integrable under `m₀`. Nothing about `T` is assumed beyond this: no
differentiation under the integral sign and no "regularity" condition. The Cramér–Rao bound of Proposition S7.1 follows
by letting `m₁ → m₀` along a curve `m(θ₀ + t a)` (file `Paper1GaussianCR`).

* `p1_cov_sq_le`: covariance Cauchy–Schwarz, `Cov(X,Y)² ≤ Var X · Var Y`.
* `p1_hcr`: the abstract HCR bound for `Q = P.withDensity ρ`.
* `p1_gauss_withDensity`, `p1_gaussLR_integral_sq`: the one-dimensional likelihood ratio and its second moment.
* `p1_record_withDensity`, `p1_recordLR_integral_sq`: the same for the `n`-coordinate record (by induction).
* `p1_thm_gaussian_hcr`: the HCR bound for the Gaussian record.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory Real Finset
open scoped ENNReal NNReal

/-- Covariance Cauchy–Schwarz. -/
theorem p1_cov_sq_le {Ω : Type*} [MeasurableSpace Ω] {P : Measure Ω} [IsProbabilityMeasure P] {X Y : Ω → ℝ}
    (hX : MemLp X 2 P) (hY : MemLp Y 2 P) : cov[X, Y; P] ^ 2 ≤ variance X P * variance Y P := by
  have key : ∀ t : ℝ, 0 ≤ variance Y P * (t * t) + (-2 * cov[X, Y; P]) * t + variance X P := by
    intro t
    have h := variance_nonneg (X - t • Y) P
    rw [variance_sub hX (hY.const_smul t), covariance_smul_right, variance_smul] at h
    nlinarith [h]
  have hd := discrim_le_zero key
  unfold discrim at hd
  nlinarith [hd]

/-- If `ρ ≥ 0` is a probability density with respect to `P`, its integral is one. -/
theorem p1_integral_density_eq_one {Ω : Type*} [MeasurableSpace Ω] (P : Measure Ω) (ρ : Ω → ℝ)
    (hρm : Measurable ρ) (hρ0 : ∀ x, 0 ≤ ρ x)
    (hQ : IsProbabilityMeasure (P.withDensity fun x => ENNReal.ofReal (ρ x))) : ∫ x, ρ x ∂P = 1 := by
  rw [integral_eq_lintegral_of_nonneg_ae (ae_of_all _ hρ0) hρm.aestronglyMeasurable]
  have h := hQ.measure_univ
  rw [withDensity_apply _ MeasurableSet.univ, Measure.restrict_univ] at h
  rw [h]
  simp

/-- **Hammersley–Chapman–Robbins.** If `Q = P.withDensity ρ` with `ρ ≥ 0` measurable, `∫ ρ dP = 1` and
`ρ ∈ L²(P)`, then every `T ∈ L²(P)` satisfies `(E_Q T - E_P T)² ≤ Var_P(T) · (∫ ρ² dP - 1)`. -/
theorem p1_hcr {Ω : Type*} [MeasurableSpace Ω] (P : Measure Ω) [IsProbabilityMeasure P] (ρ T : Ω → ℝ)
    (hρm : Measurable ρ) (hρ0 : ∀ x, 0 ≤ ρ x) (hρ1 : ∫ x, ρ x ∂P = 1) (hρ : MemLp ρ 2 P)
    (hT : MemLp T 2 P) :
    (∫ x, T x ∂(P.withDensity fun x => ENNReal.ofReal (ρ x)) - ∫ x, T x ∂P) ^ 2 ≤
      variance T P * (∫ x, ρ x ^ 2 ∂P - 1) := by
  have hQ : ∫ x, T x ∂(P.withDensity fun x => ENNReal.ofReal (ρ x)) = ∫ x, T x * ρ x ∂P := by
    have h := integral_withDensity_eq_integral_smul (μ := P) (f := fun x => (ρ x).toNNReal)
      hρm.real_toNNReal T
    refine h.trans (integral_congr_ae (ae_of_all _ fun x => ?_))
    show ((ρ x).toNNReal : ℝ) • T x = T x * ρ x
    rw [Real.coe_toNNReal _ (hρ0 x), smul_eq_mul, mul_comm]
  have hcov := covariance_eq_sub hT hρ
  have hvar := variance_eq_sub hρ
  have hcs := p1_cov_sq_le hT hρ
  rw [hcov, hvar] at hcs
  simp only [Pi.mul_apply, Pi.pow_apply, hρ1, mul_one, one_pow] at hcs
  rw [hQ]
  linarith [hcs]

/-! ### One coordinate -/

/-- The likelihood ratio `dN(m₁, v)/dN(m₀, v)`. -/
noncomputable def gaussLR (m0 m1 : ℝ) (v : ℝ≥0) (x : ℝ) : ℝ :=
  exp (((x - m0) * (m1 - m0) - (m1 - m0) ^ 2 / 2) / v)

theorem p1_gaussLR_pos (m0 m1 : ℝ) (v : ℝ≥0) (x : ℝ) : 0 < gaussLR m0 m1 v x := exp_pos _

theorem p1_gaussLR_measurable (m0 m1 : ℝ) (v : ℝ≥0) : Measurable (gaussLR m0 m1 v) := by
  unfold gaussLR
  fun_prop

theorem p1_gaussLR_pdf (m0 m1 : ℝ) (v : ℝ≥0) (hv : v ≠ 0) (x : ℝ) :
    gaussianPDFReal m0 v x * gaussLR m0 m1 v x = gaussianPDFReal m1 v x := by
  have hv' : (v : ℝ) ≠ 0 := NNReal.coe_ne_zero.mpr hv
  unfold gaussianPDFReal gaussLR
  rw [mul_assoc, ← Real.exp_add]
  congr 2
  field_simp
  ring

/-- `N(m₁, v) = N(m₀, v).withDensity (dN(m₁, v)/dN(m₀, v))`. -/
theorem p1_gauss_withDensity (m0 m1 : ℝ) (v : ℝ≥0) (hv : v ≠ 0) :
    gaussianReal m1 v = (gaussianReal m0 v).withDensity fun x => ENNReal.ofReal (gaussLR m0 m1 v x) := by
  rw [gaussianReal_of_var_ne_zero m1 hv, gaussianReal_of_var_ne_zero m0 hv,
    ← withDensity_mul _ (measurable_gaussianPDF m0 v) (p1_gaussLR_measurable m0 m1 v).ennreal_ofReal]
  congr 1
  funext x
  simp only [Pi.mul_apply, gaussianPDF]
  rw [← ENNReal.ofReal_mul (gaussianPDFReal_nonneg m0 v x), p1_gaussLR_pdf m0 m1 v hv x]

theorem p1_gaussLR_sq (m0 m1 : ℝ) (v : ℝ≥0) (hv : v ≠ 0) (x : ℝ) :
    gaussLR m0 m1 v x ^ 2 =
      exp (-((m1 - m0) ^ 2 / v) - 2 * (m1 - m0) * m0 / v) * exp (2 * (m1 - m0) / v * x) := by
  have hv' : (v : ℝ) ≠ 0 := NNReal.coe_ne_zero.mpr hv
  unfold gaussLR
  rw [← Real.exp_nat_mul, ← Real.exp_add]
  congr 1
  push_cast
  field_simp
  ring

theorem p1_gaussLR_sq_integrable (m0 m1 : ℝ) (v : ℝ≥0) (hv : v ≠ 0) :
    Integrable (fun x => gaussLR m0 m1 v x ^ 2) (gaussianReal m0 v) := by
  have e : (fun x => gaussLR m0 m1 v x ^ 2) =
      fun x => exp (-((m1 - m0) ^ 2 / v) - 2 * (m1 - m0) * m0 / v) * exp (2 * (m1 - m0) / v * x) :=
    funext (p1_gaussLR_sq m0 m1 v hv)
  rw [e]
  exact (integrable_exp_mul_gaussianReal _).const_mul _

/-- `∫ (dN(m₁,v)/dN(m₀,v))² dN(m₀,v) = exp((m₁ - m₀)²/v)`. -/
theorem p1_gaussLR_integral_sq (m0 m1 : ℝ) (v : ℝ≥0) (hv : v ≠ 0) :
    ∫ x, gaussLR m0 m1 v x ^ 2 ∂(gaussianReal m0 v) = exp ((m1 - m0) ^ 2 / v) := by
  have hv' : (v : ℝ) ≠ 0 := NNReal.coe_ne_zero.mpr hv
  simp only [p1_gaussLR_sq m0 m1 v hv]
  rw [integral_const_mul]
  have hm := congrFun (mgf_id_gaussianReal (μ := m0) (v := v)) (2 * (m1 - m0) / v)
  have hm' : ∫ x, exp (2 * (m1 - m0) / v * x) ∂(gaussianReal m0 v) =
      exp (m0 * (2 * (m1 - m0) / v) + v * (2 * (m1 - m0) / v) ^ 2 / 2) := hm
  rw [hm', ← Real.exp_add]
  congr 1
  field_simp
  ring

/-! ### The `n`-coordinate record -/

/-- The likelihood ratio of two Gaussian records with common variance. -/
noncomputable def recordLR : (n : ℕ) → (Fin n → ℝ) → (Fin n → ℝ) → ℝ≥0 → ObservationRecord n → ℝ
  | 0, _, _, _ => fun _ => 1
  | n + 1, m0, m1, v => fun x =>
      gaussLR (m0 0) (m1 0) v x.1 * recordLR n (fun i => m0 i.succ) (fun i => m1 i.succ) v x.2

theorem p1_recordLR_measurable : (n : ℕ) → (m0 m1 : Fin n → ℝ) → (v : ℝ≥0) →
    Measurable (recordLR n m0 m1 v)
  | 0, _, _, _ => measurable_const
  | n + 1, m0, m1, v =>
      ((p1_gaussLR_measurable (m0 0) (m1 0) v).comp measurable_fst).mul
        ((p1_recordLR_measurable n (fun i => m0 i.succ) (fun i => m1 i.succ) v).comp measurable_snd)

theorem p1_recordLR_nonneg : (n : ℕ) → (m0 m1 : Fin n → ℝ) → (v : ℝ≥0) → (x : ObservationRecord n) →
    0 ≤ recordLR n m0 m1 v x
  | 0, _, _, _, _ => zero_le_one
  | n + 1, m0, m1, v, x =>
      mul_nonneg (p1_gaussLR_pos _ _ _ _).le (p1_recordLR_nonneg n _ _ v x.2)

theorem p1_record_withDensity (v : ℝ≥0) (hv : v ≠ 0) : (n : ℕ) → (m0 m1 : Fin n → ℝ) →
    gaussianRecordLaw n m1 v =
      (gaussianRecordLaw n m0 v).withDensity fun x => ENNReal.ofReal (recordLR n m0 m1 v x)
  | 0, m0, m1 => by
      simp only [gaussianRecordLaw, recordLR, ENNReal.ofReal_one]
      exact (withDensity_one).symm
  | n + 1, m0, m1 => by
      show (gaussianReal (m1 0) v).prod (gaussianRecordLaw n (fun i => m1 i.succ) v) =
        ((gaussianReal (m0 0) v).prod (gaussianRecordLaw n (fun i => m0 i.succ) v)).withDensity
          fun x => ENNReal.ofReal (gaussLR (m0 0) (m1 0) v x.1 *
            recordLR n (fun i => m0 i.succ) (fun i => m1 i.succ) v x.2)
      rw [p1_gauss_withDensity (m0 0) (m1 0) v hv,
        p1_record_withDensity v hv n (fun i => m0 i.succ) (fun i => m1 i.succ),
        prod_withDensity (p1_gaussLR_measurable _ _ v).ennreal_ofReal
          (p1_recordLR_measurable n _ _ v).ennreal_ofReal]
      congr 1
      funext x
      rw [ENNReal.ofReal_mul (p1_gaussLR_pos _ _ _ _).le]

theorem p1_recordLR_sq_integrable (v : ℝ≥0) (hv : v ≠ 0) : (n : ℕ) → (m0 m1 : Fin n → ℝ) →
    Integrable (fun x => recordLR n m0 m1 v x ^ 2) (gaussianRecordLaw n m0 v)
  | 0, m0, m1 => by
      simp only [recordLR, one_pow]
      haveI : IsProbabilityMeasure (gaussianRecordLaw 0 m0 v) := gaussian_record_probability 0 m0 v
      exact integrable_const 1
  | n + 1, m0, m1 => by
      have h := (p1_gaussLR_sq_integrable (m0 0) (m1 0) v hv).mul_prod
        (p1_recordLR_sq_integrable v hv n (fun i => m0 i.succ) (fun i => m1 i.succ))
      have e : (fun x : ObservationRecord (n + 1) => recordLR (n + 1) m0 m1 v x ^ 2) =
          fun x => gaussLR (m0 0) (m1 0) v x.1 ^ 2 *
            recordLR n (fun i => m0 i.succ) (fun i => m1 i.succ) v x.2 ^ 2 := by
        funext x
        show (gaussLR (m0 0) (m1 0) v x.1 * recordLR n (fun i => m0 i.succ) (fun i => m1 i.succ) v x.2) ^ 2 = _
        ring
      rw [e]
      exact h

theorem p1_recordLR_integral_sq (v : ℝ≥0) (hv : v ≠ 0) : (n : ℕ) → (m0 m1 : Fin n → ℝ) →
    ∫ x, recordLR n m0 m1 v x ^ 2 ∂(gaussianRecordLaw n m0 v) = exp ((∑ i, (m1 i - m0 i) ^ 2) / v)
  | 0, m0, m1 => by
      simp [recordLR, gaussianRecordLaw]
  | n + 1, m0, m1 => by
      have e : (fun x : ObservationRecord (n + 1) => recordLR (n + 1) m0 m1 v x ^ 2) =
          fun x => gaussLR (m0 0) (m1 0) v x.1 ^ 2 *
            recordLR n (fun i => m0 i.succ) (fun i => m1 i.succ) v x.2 ^ 2 := by
        funext x
        show (gaussLR (m0 0) (m1 0) v x.1 * recordLR n (fun i => m0 i.succ) (fun i => m1 i.succ) v x.2) ^ 2 = _
        ring
      have hI := integral_prod_mul (μ := gaussianReal (m0 0) v)
        (ν := gaussianRecordLaw n (fun i => m0 i.succ) v)
        (fun y : ℝ => gaussLR (m0 0) (m1 0) v y ^ 2)
        (fun r => recordLR n (fun i => m0 i.succ) (fun i => m1 i.succ) v r ^ 2)
      rw [p1_gaussLR_integral_sq _ _ v hv,
        p1_recordLR_integral_sq v hv n (fun i => m0 i.succ) (fun i => m1 i.succ)] at hI
      have hlaw : gaussianRecordLaw (n + 1) m0 v =
          (gaussianReal (m0 0) v).prod (gaussianRecordLaw n (fun i => m0 i.succ) v) := rfl
      rw [e, hlaw, hI, ← Real.exp_add, Fin.sum_univ_succ]
      congr 1
      ring

/-- **HCR for the Gaussian record.** For every statistic `T` that is square-integrable under `N(m₀, v I)`,
`(E_{m₁} T - E_{m₀} T)² ≤ Var_{m₀}(T) · (exp(‖m₁ - m₀‖²/v) - 1)`. -/
theorem p1_thm_gaussian_hcr (n : ℕ) (m0 m1 : Fin n → ℝ) (v : ℝ≥0) (hv : v ≠ 0)
    (T : ObservationRecord n → ℝ) (hT : MemLp T 2 (gaussianRecordLaw n m0 v)) :
    (∫ x, T x ∂(gaussianRecordLaw n m1 v) - ∫ x, T x ∂(gaussianRecordLaw n m0 v)) ^ 2 ≤
      variance T (gaussianRecordLaw n m0 v) * (exp ((∑ i, (m1 i - m0 i) ^ 2) / v) - 1) := by
  have hρm := p1_recordLR_measurable n m0 m1 v
  have hρ0 := p1_recordLR_nonneg n m0 m1 v
  have hQ : IsProbabilityMeasure ((gaussianRecordLaw n m0 v).withDensity
      fun x => ENNReal.ofReal (recordLR n m0 m1 v x)) := by
    rw [← p1_record_withDensity v hv n m0 m1]
    infer_instance
  have hρ1 := p1_integral_density_eq_one _ _ hρm hρ0 hQ
  have hρ : MemLp (recordLR n m0 m1 v) 2 (gaussianRecordLaw n m0 v) :=
    (memLp_two_iff_integrable_sq hρm.aestronglyMeasurable).2 (p1_recordLR_sq_integrable v hv n m0 m1)
  have h := p1_hcr _ _ T hρm hρ0 hρ1 hρ hT
  rw [← p1_record_withDensity v hv n m0 m1, p1_recordLR_integral_sq v hv n m0 m1] at h
  exact h

end CurrentMM
