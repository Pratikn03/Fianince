import Mathlib.Probability.Distributions.Gaussian.Real
import Mathlib.Probability.Moments.Variance
import Mathlib.MeasureTheory.Measure.Lebesgue.EqHaar
import Mathlib.MeasureTheory.Integral.Pi
import Mathlib.InformationTheory.KullbackLeibler.Basic
import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

/-!
# A unit-triangular linear image of i.i.d. Gaussians: its Kullback–Leibler divergence

Foundational step for Paper 1, Theorem 5.8 (passive data). With `P` the law of `n` i.i.d. `N(0, v)` variables and
`B` a lower-triangular matrix with unit diagonal,

  `KL(B_* P ‖ P) = ½ ∑_{i,j} (B - 1)_{ij}²`,

independently of `v`. Ingredients built here (not in Mathlib):
* `p1_iidGauss_eq_withDensity`: the product of Gaussian laws has the product density;
* `p1_map_withDensity_det_one`: a determinant-one linear change of variables moves a density by composition;
* `p1_map_triangular_eq_withDensity`: `B_* P = P.withDensity ρ` with an explicit likelihood ratio;
* `p1_kl_triangular_gaussian`: the divergence formula.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory InformationTheory Real Finset Matrix
open scoped ENNReal NNReal

/-- `n` i.i.d. centred Gaussian coordinates with variance `v`. -/
noncomputable def iidGauss (n : ℕ) (v : ℝ≥0) : Measure (Fin n → ℝ) := Measure.pi fun _ => gaussianReal 0 v

instance (n : ℕ) (v : ℝ≥0) : IsProbabilityMeasure (iidGauss n v) := by
  unfold iidGauss; infer_instance

/-- The product density. -/
noncomputable def iidDens {n : ℕ} (v : ℝ≥0) (x : Fin n → ℝ) : ℝ := ∏ i, gaussianPDFReal 0 v (x i)

theorem p1_iidDens_pos {n : ℕ} (v : ℝ≥0) (hv : v ≠ 0) (x : Fin n → ℝ) : 0 < iidDens v x :=
  prod_pos (fun i _ => gaussianPDFReal_pos 0 v (x i) hv)

theorem p1_measurable_iidDens {n : ℕ} (v : ℝ≥0) : Measurable (iidDens (n := n) v) :=
  Finset.measurable_prod _ (fun i _ => (measurable_gaussianPDFReal 0 v).comp (measurable_pi_apply i))

/-- The product density in closed form: `c^n exp(-‖x‖²/(2v))`. -/
theorem p1_iidDens_eq {n : ℕ} (v : ℝ≥0) (x : Fin n → ℝ) :
    iidDens v x = (√(2 * π * v))⁻¹ ^ n * exp (-(∑ i, x i ^ 2) / (2 * v)) := by
  unfold iidDens
  simp only [gaussianPDFReal_def, sub_zero]
  rw [prod_mul_distrib, prod_const, card_univ, Fintype.card_fin, ← Real.exp_sum, ← sum_div, sum_neg_distrib]

/-- **The product of Gaussian laws has the product density.** -/
theorem p1_iidGauss_eq_withDensity (n : ℕ) (v : ℝ≥0) (hv : v ≠ 0) :
    iidGauss n v = volume.withDensity (fun x => ENNReal.ofReal (iidDens v x)) := by
  unfold iidGauss
  refine Measure.pi_eq (fun s hs => ?_)
  rw [withDensity_apply _ (MeasurableSet.univ_pi hs)]
  have hind : ∀ x : Fin n → ℝ, (Set.univ.pi s).indicator (fun x => ENNReal.ofReal (iidDens v x)) x =
      ENNReal.ofReal (∏ i, (s i).indicator (gaussianPDFReal 0 v) (x i)) := by
    intro x
    by_cases hx : x ∈ Set.univ.pi s
    · rw [Set.indicator_of_mem hx]
      congr 1
      exact prod_congr rfl (fun i _ => (Set.indicator_of_mem (hx i (Set.mem_univ i)) _).symm)
    · rw [Set.indicator_of_notMem hx]
      obtain ⟨i, hi⟩ : ∃ i, x i ∉ s i := by
        by_contra h; push Not at h; exact hx (fun i _ => h i)
      rw [prod_eq_zero (mem_univ i) (Set.indicator_of_notMem hi _), ENNReal.ofReal_zero]
  rw [← lintegral_indicator (MeasurableSet.univ_pi hs)]
  simp_rw [hind]
  have hint : ∀ i, Integrable ((s i).indicator (gaussianPDFReal 0 v)) := fun i =>
    (integrable_gaussianPDFReal 0 v).indicator (hs i)
  have hprod_int : Integrable (fun x : Fin n → ℝ => ∏ i, (s i).indicator (gaussianPDFReal 0 v) (x i))
      (Measure.pi fun _ => volume) := Integrable.fintype_prod hint
  rw [volume_pi, ← ofReal_integral_eq_lintegral_ofReal hprod_int
    (ae_of_all _ (fun x => prod_nonneg (fun i _ => Set.indicator_nonneg
      (fun y _ => (gaussianPDFReal_pos 0 v y hv).le) _))),
    integral_fintype_prod_eq_prod, ENNReal.ofReal_prod_of_nonneg
      (fun i _ => integral_nonneg (fun y => Set.indicator_nonneg (fun y _ => (gaussianPDFReal_pos 0 v y hv).le) _))]
  refine prod_congr rfl (fun i _ => ?_)
  rw [gaussianReal_apply 0 hv, integral_indicator (hs i),
    ofReal_integral_eq_lintegral_ofReal ((integrable_gaussianPDFReal 0 v).integrableOn)
      (ae_of_all _ (fun y => (gaussianPDFReal_pos 0 v y hv).le))]
  rfl

theorem p1_measurable_mulVec {n : ℕ} (B : Matrix (Fin n) (Fin n) ℝ) : Measurable (B.mulVec) :=
  (Matrix.toLin' B).continuous_of_finiteDimensional.measurable

/-- **Determinant-one change of variables.** -/
theorem p1_map_withDensity_det_one {n : ℕ} (B : Matrix (Fin n) (Fin n) ℝ) (hB : B.det = 1)
    (f : (Fin n → ℝ) → ℝ≥0∞) (hf : Measurable f) :
    (volume.withDensity f).map B.mulVec = volume.withDensity (fun y => f (B⁻¹.mulVec y)) := by
  have hunit : IsUnit B.det := by rw [hB]; exact isUnit_one
  have hvol : Measure.map B.mulVec (volume : Measure (Fin n → ℝ)) = volume := by
    have h := Measure.map_linearMap_addHaar_eq_smul_addHaar (μ := (volume : Measure (Fin n → ℝ)))
      (f := Matrix.toLin' B) (by rw [LinearMap.det_toLin', hB]; norm_num)
    rw [LinearMap.det_toLin', hB] at h
    have hc : ⇑(Matrix.toLin' B) = B.mulVec := by funext x; simp [Matrix.toLin'_apply']
    rw [hc] at h
    simpa using h
  ext S hS
  rw [Measure.map_apply (p1_measurable_mulVec B) hS, withDensity_apply _ ((p1_measurable_mulVec B) hS),
    withDensity_apply _ hS]
  conv_rhs => rw [← hvol]
  rw [setLIntegral_map (f := fun a => f (B⁻¹ *ᵥ a)) hS (hf.comp (p1_measurable_mulVec B⁻¹))
    (p1_measurable_mulVec B)]
  refine setLIntegral_congr_fun ((p1_measurable_mulVec B) hS) (fun x _ => ?_)
  simp only [Matrix.mulVec_mulVec, Matrix.nonsing_inv_mul B hunit, Matrix.one_mulVec]

/-- The likelihood ratio of `B_* P` against `P`. -/
noncomputable def triRatio {n : ℕ} (v : ℝ≥0) (B : Matrix (Fin n) (Fin n) ℝ) (y : Fin n → ℝ) : ℝ≥0∞ :=
  ENNReal.ofReal (iidDens v (B⁻¹.mulVec y) / iidDens v y)

theorem p1_measurable_triRatio {n : ℕ} (v : ℝ≥0) (B : Matrix (Fin n) (Fin n) ℝ) :
    Measurable (triRatio v B) :=
  ENNReal.measurable_ofReal.comp
    (((p1_measurable_iidDens v).comp (p1_measurable_mulVec B⁻¹)).div (p1_measurable_iidDens v))

/-- **`B_* P` has an explicit density with respect to `P`.** -/
theorem p1_map_triangular_eq_withDensity {n : ℕ} (v : ℝ≥0) (hv : v ≠ 0) (B : Matrix (Fin n) (Fin n) ℝ)
    (hB : B.det = 1) :
    (iidGauss n v).map B.mulVec = (iidGauss n v).withDensity (triRatio v B) := by
  rw [p1_iidGauss_eq_withDensity n v hv,
    p1_map_withDensity_det_one B hB (fun x => ENNReal.ofReal (iidDens v x))
      (ENNReal.measurable_ofReal.comp (p1_measurable_iidDens v)),
    ← withDensity_mul (f := fun x => ENNReal.ofReal (iidDens v x)) _
      (ENNReal.measurable_ofReal.comp (p1_measurable_iidDens v)) (p1_measurable_triRatio v B)]
  congr 1
  funext y
  simp only [Pi.mul_apply, triRatio]
  rw [← ENNReal.ofReal_mul (p1_iidDens_pos v hv y).le]
  congr 1
  field_simp [(p1_iidDens_pos v hv y).ne']

/-- Second moment of a linear combination of i.i.d. centred Gaussians. -/
theorem p1_iidGauss_sq_linear {n : ℕ} (v : ℝ≥0) (c : Fin n → ℝ) :
    ∫ ξ, (∑ j, c j * ξ j) ^ 2 ∂(iidGauss n v) = v * ∑ j, c j ^ 2 := by
  have hmem : ∀ j : Fin n, MemLp (fun t : ℝ => c j * t) 2 (gaussianReal 0 v) := fun j =>
    (memLp_id_gaussianReal 2).const_mul (c j)
  have hvar := variance_sum_pi (μ := fun _ : Fin n => gaussianReal 0 v) (X := fun j t => c j * t) hmem
  have hfun : (∑ j, fun ω : Fin n → ℝ => c j * ω j) = fun ξ => ∑ j, c j * ξ j := by
    funext ξ; simp
  rw [hfun] at hvar
  have hcoord : ∀ j : Fin n, ∫ ξ, ξ j ∂(iidGauss n v) = 0 := fun j => by
    have hm := measurePreserving_eval (fun _ : Fin n => gaussianReal 0 v) j
    have h := integral_map (μ := iidGauss n v) (φ := Function.eval j) (f := fun y : ℝ => y)
      (measurable_pi_apply j).aemeasurable aestronglyMeasurable_id
    rw [iidGauss] at h ⊢
    rw [hm.map_eq, integral_id_gaussianReal] at h
    exact h.symm
  have hint : ∀ j : Fin n, Integrable (fun ξ : Fin n → ℝ => ξ j) (iidGauss n v) := fun j =>
    ((memLp_id_gaussianReal 1).comp_measurePreserving (measurePreserving_eval _ j)).integrable le_rfl
  have hmean : ∫ ξ, ∑ j, c j * ξ j ∂(iidGauss n v) = 0 := by
    rw [integral_finsetSum _ (fun j _ => (hint j).const_mul (c j))]
    exact sum_eq_zero (fun j _ => by rw [integral_const_mul, hcoord j, mul_zero])
  have hmeas : AEMeasurable (fun ξ : Fin n → ℝ => ∑ j, c j * ξ j) (iidGauss n v) :=
    (by fun_prop : Measurable fun ξ : Fin n → ℝ => ∑ j, c j * ξ j).aemeasurable
  rw [← variance_of_integral_eq_zero hmeas hmean]
  unfold iidGauss
  rw [hvar, mul_sum]
  refine sum_congr rfl (fun j _ => ?_)
  rw [variance_const_mul, variance_fun_id_gaussianReal]
  ring

theorem p1_memLp_linear {n : ℕ} (v : ℝ≥0) (c : Fin n → ℝ) :
    MemLp (fun ξ : Fin n → ℝ => ∑ j, c j * ξ j) 2 (iidGauss n v) := by
  have h : ∀ j : Fin n, MemLp (fun ξ : Fin n → ℝ => c j * ξ j) 2 (iidGauss n v) := fun j =>
    ((memLp_id_gaussianReal 2).comp_measurePreserving (measurePreserving_eval _ j)).const_mul (c j)
  have := memLp_finsetSum' (s := univ) (fun j _ => h j)
  convert this using 1
  funext ξ; simp

/-- The log likelihood ratio of `B_* P` against `P` in closed form. -/
theorem p1_log_dens_ratio {n : ℕ} (v : ℝ≥0) (x y : Fin n → ℝ) :
    log (iidDens v y / iidDens v x) = ((∑ i, x i ^ 2) - ∑ i, y i ^ 2) / (2 * v) := by
  rw [p1_iidDens_eq, p1_iidDens_eq]
  have hc : 0 < (√(2 * π * v))⁻¹ ^ n ∨ (√(2 * π * v))⁻¹ ^ n = 0 := by
    rcases (pow_nonneg (inv_nonneg.mpr (Real.sqrt_nonneg (2 * π * v))) n).lt_or_eq with h | h
    · exact Or.inl h
    · exact Or.inr h.symm
  rcases hc with hc | hc
  · rw [mul_div_mul_left _ _ hc.ne', ← Real.exp_sub, Real.log_exp]
    ring
  · -- `v = 0`: both sides vanish
    have hv : (v : ℝ) = 0 := by
      by_contra hv0
      have : 0 < √(2 * π * v) := Real.sqrt_pos.mpr (by positivity)
      exact absurd hc (pow_ne_zero n (inv_ne_zero this.ne'))
    rw [hc]; simp [hv]

/-- **Kullback–Leibler divergence of a unit-triangular image of i.i.d. Gaussians.** -/
theorem p1_kl_triangular_gaussian {n : ℕ} (v : ℝ≥0) (hv : v ≠ 0) (B : Matrix (Fin n) (Fin n) ℝ)
    (hlow : B.IsLowerTriangular) (hdiag : ∀ i, B i i = 1) :
    klDiv ((iidGauss n v).map B.mulVec) (iidGauss n v) =
      ENNReal.ofReal (1 / 2 * ∑ i, ∑ j, (B - 1) i j ^ 2) := by
  have hdet : B.det = 1 := by rw [det_of_isLowerTriangular B hlow]; simp [hdiag]
  have hunit : IsUnit B.det := by rw [hdet]; exact isUnit_one
  set ν := iidGauss n v
  set μ := ν.map B.mulVec with hμdef
  have : IsProbabilityMeasure μ := by rw [hμdef]; infer_instance
  have hμ : μ = ν.withDensity (triRatio v B) := p1_map_triangular_eq_withDensity v hv B hdet
  have hac : μ ≪ ν := by rw [hμ]; exact withDensity_absolutelyContinuous _ _
  have hrn : μ.rnDeriv ν =ᵐ[ν] triRatio v B := by
    rw [hμ]; exact Measure.rnDeriv_withDensity ν (p1_measurable_triRatio v B)
  set g : (Fin n → ℝ) → ℝ := fun x => log (iidDens v (B⁻¹.mulVec x) / iidDens v x) with hg
  have hllr : llr μ ν =ᵐ[μ] g := by
    filter_upwards [hac.ae_le hrn] with x hx
    simp only [llr, hx, triRatio, hg]
    rw [ENNReal.toReal_ofReal (div_nonneg (p1_iidDens_pos v hv _).le (p1_iidDens_pos v hv _).le)]
  have hgB : ∀ ξ, g (B.mulVec ξ) = ((∑ i, (B.mulVec ξ) i ^ 2) - ∑ i, ξ i ^ 2) / (2 * v) := by
    intro ξ
    simp only [hg, Matrix.mulVec_mulVec, Matrix.nonsing_inv_mul B hunit, Matrix.one_mulVec]
    exact p1_log_dens_ratio v (B.mulVec ξ) ξ
  have hrow : ∀ (A : Matrix (Fin n) (Fin n) ℝ) (ξ : Fin n → ℝ) i, (A.mulVec ξ) i = ∑ j, A i j * ξ j := by
    intro A ξ i; simp [Matrix.mulVec, dotProduct]
  have hsqint : ∀ (A : Matrix (Fin n) (Fin n) ℝ) i,
      Integrable (fun ξ : Fin n → ℝ => (A.mulVec ξ) i ^ 2) ν := by
    intro A i
    have := (p1_memLp_linear v (fun j => A i j)).integrable_sq
    simpa [hrow] using this
  have hintB : Integrable (fun ξ => g (B.mulVec ξ)) ν := by
    simp_rw [hgB]
    refine Integrable.div_const (Integrable.sub (integrable_finsetSum _ (fun i _ => hsqint B i)) ?_) _
    have : ∀ i, Integrable (fun ξ : Fin n → ℝ => ξ i ^ 2) ν := by
      intro i; have := hsqint 1 i; simpa using this
    exact integrable_finsetSum _ (fun i _ => this i)
  have hgmeas : AEStronglyMeasurable g μ := by
    refine (Measurable.aestronglyMeasurable ?_)
    exact Real.measurable_log.comp (((p1_measurable_iidDens v).comp (p1_measurable_mulVec B⁻¹)).div
      (p1_measurable_iidDens v))
  have hint : Integrable g μ := by
    rw [hμdef, integrable_map_measure (hμdef ▸ hgmeas) (p1_measurable_mulVec B).aemeasurable]
    exact hintB
  have hint_llr : Integrable (llr μ ν) μ := hint.congr hllr.symm
  rw [klDiv_of_ac_of_integrable hac hint_llr, integral_congr_ae hllr, probReal_univ,
    probReal_univ, add_sub_cancel_right, hμdef,
    integral_map (p1_measurable_mulVec B).aemeasurable (hμdef ▸ hgmeas)]
  simp_rw [hgB]
  rw [integral_div, integral_sub (integrable_finsetSum _ (fun i _ => hsqint B i))
      (integrable_finsetSum _ (fun i _ => by have := hsqint 1 i; simpa using this)),
    integral_finsetSum _ (fun i _ => hsqint B i),
    integral_finsetSum _ (fun i _ => by have := hsqint 1 i; simpa using this)]
  have hB2 : ∀ i, ∫ ξ, (B.mulVec ξ) i ^ 2 ∂ν = v * ∑ j, B i j ^ 2 := by
    intro i; simp only [hrow]; exact p1_iidGauss_sq_linear v (fun j => B i j)
  have h12 : ∀ i, ∫ ξ, ξ i ^ 2 ∂ν = v * 1 := by
    intro i
    have := p1_iidGauss_sq_linear v (fun j => (1 : Matrix (Fin n) (Fin n) ℝ) i j)
    simpa [Matrix.one_apply] using this
  simp only [hB2, h12]
  congr 1
  have hvr : (v : ℝ) ≠ 0 := by exact_mod_cast hv
  have hpt : ∀ i, ∑ j, B i j ^ 2 - 1 = ∑ j, (B - 1) i j ^ 2 := by
    intro i
    have hone : ∑ j, (1 : Matrix (Fin n) (Fin n) ℝ) i j ^ 2 = 1 := by simp [Matrix.one_apply]
    have hpw : ∀ j, B i j ^ 2 - (1 : Matrix (Fin n) (Fin n) ℝ) i j ^ 2 = (B - 1) i j ^ 2 := by
      intro j
      by_cases h : i = j
      · subst h; simp [hdiag]
      · simp [Matrix.one_apply_ne h, Matrix.sub_apply]
    rw [← hone, ← sum_sub_distrib]
    exact sum_congr rfl (fun j _ => hpw j)
  rw [← sum_sub_distrib]
  have e : ∀ i, (v : ℝ) * ∑ j, B i j ^ 2 - v * 1 = v * ∑ j, (B - 1) i j ^ 2 := fun i => by
    rw [← mul_sub, hpt i]
  rw [sum_congr rfl (fun i _ => e i), ← mul_sum]
  field_simp

end CurrentMM
