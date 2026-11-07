import CurrentProofs.Paper1GaussianCR
import CurrentProofs.Paper1MergedModel

/-!
# Paper 1, Proposition S7.1 (i) for the actual closed-loop response

The parameter is `θ = (q, rate) ∈ ℝ^{n+n}` (cohort sizes and memory rates; anchor `a` and impact `κ` known). A probe of
size `V` from the reset state makes the averaged probe record `N(h(θ), σ_h² I_T)` with
`h(θ)_t = V · actualCohortImpulse a κ q rate t`, the actual price response of the cohort recursion
(`actual_reset_price_convolution`). This file proves that `h` is differentiable (every tap is a polynomial in `θ`, by
the closed-loop recursion `p1_impulse_closed_loop_recursion`) and applies the Cramér–Rao bound with `J` the true
Jacobian of the actual response:

`Var_θ₀(T) ≥ σ_h² [(JᵀJ)⁻¹]_kk` for every `L²` statistic unbiased for `θ_k` near `θ₀`, whenever `JᵀJ` is invertible.

The size of `[(JᵀJ)⁻¹]_kk` (the `(Δη)^{-6}` scaling of S7.1 (iii)) is not proved here.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory Filter Topology Matrix Finset
open scoped ENNReal NNReal

/-- Cohort sizes from the packed parameter. -/
def qOf {n : ℕ} (θ : Fin (n + n) → ℝ) : Fin n → ℝ := fun i => θ (Fin.castAdd n i)

/-- Memory rates from the packed parameter. -/
def rateOf {n : ℕ} (θ : Fin (n + n) → ℝ) : Fin n → ℝ := fun i => θ (Fin.natAdd n i)

theorem p1_cohortKernel_differentiable {n : ℕ} (m : ℕ) :
    Differentiable ℝ (fun θ : Fin (n + n) → ℝ => cohortKernel (qOf θ) (rateOf θ) m) := by
  unfold cohortKernel qOf rateOf
  fun_prop

/-- Every tap of the actual closed-loop response is differentiable in `θ = (q, rate)`. -/
theorem p1_impulse_differentiable {n : ℕ} (a κ : ℝ) (j : ℕ) :
    Differentiable ℝ (fun θ : Fin (n + n) → ℝ => actualCohortImpulse a κ (qOf θ) (rateOf θ) j) := by
  refine Nat.strong_induction_on j ?_
  intro j ih
  rcases j with _ | j
  · have e : (fun θ : Fin (n + n) → ℝ => actualCohortImpulse a κ (qOf θ) (rateOf θ) 0) = fun _ => κ := by
      funext θ; exact p1_impulse_zero a κ _ _
    rw [e]
    exact differentiable_const κ
  · have e : (fun θ : Fin (n + n) → ℝ => actualCohortImpulse a κ (qOf θ) (rateOf θ) (j + 1)) =
        fun θ => a * actualCohortImpulse a κ (qOf θ) (rateOf θ) j +
          κ * ∑ m ∈ range (j + 1),
            cohortKernel (qOf θ) (rateOf θ) m * actualCohortImpulse a κ (qOf θ) (rateOf θ) (j - m) := by
      funext θ; exact p1_impulse_closed_loop_recursion a κ _ _ j
    rw [e]
    refine ((ih j (Nat.lt_succ_self j)).const_mul a).add (Differentiable.const_mul ?_ κ)
    exact Differentiable.fun_sum fun m _ =>
      (p1_cohortKernel_differentiable m).mul (ih (j - m) (by omega))

/-- The averaged probe record's mean: `V h_t(θ)` for `t < T`. -/
noncomputable def p1ProbeMean {n : ℕ} (a κ V : ℝ) (T : ℕ) (θ : Fin (n + n) → ℝ) : Fin T → ℝ :=
  fun t => V * actualCohortImpulse a κ (qOf θ) (rateOf θ) t.val

/-- The Jacobian of the actual averaged response at `θ₀`. -/
noncomputable def p1ProbeJac {n : ℕ} (a κ V : ℝ) (T : ℕ) (θ0 : Fin (n + n) → ℝ) :
    Matrix (Fin T) (Fin (n + n)) ℝ :=
  fun t j => fderiv ℝ (fun θ => p1ProbeMean a κ V T θ t) θ0 (Pi.single j 1)

theorem p1_probeMean_line_deriv {n : ℕ} (a κ V : ℝ) (T : ℕ) (θ0 : Fin (n + n) → ℝ)
    (d : Fin (n + n) → ℝ) (t : Fin T) :
    HasDerivAt (fun s : ℝ => p1ProbeMean a κ V T (θ0 + s • d) t) ((p1ProbeJac a κ V T θ0 *ᵥ d) t) 0 := by
  have hf : Differentiable ℝ (fun θ : Fin (n + n) → ℝ => p1ProbeMean a κ V T θ t) :=
    (p1_impulse_differentiable a κ t.val).const_mul V
  have hL := (hf θ0).hasFDerivAt
  have hγ : HasDerivAt (fun s : ℝ => θ0 + s • d) ((1 : ℝ) • d) 0 :=
    ((hasDerivAt_id' (0 : ℝ)).smul_const d).const_add θ0
  have hc := hL.comp_hasDerivAt_of_eq hγ (by simp)
  refine hc.congr_deriv ?_
  rw [one_smul]
  conv_lhs => rw [pi_eq_sum_univ' d]
  rw [map_sum]
  simp only [map_smul, smul_eq_mul, Matrix.mulVec, dotProduct, p1ProbeJac]
  exact Finset.sum_congr rfl fun j _ => mul_comm _ _

/-- **Proposition S7.1 (i) for the actual model.** For the averaged probe record of the actual closed-loop market,
every statistic that is square-integrable at `θ₀` and unbiased for `θ_k` on a neighbourhood of `θ₀` has
`Var ≥ σ_h² [(JᵀJ)⁻¹]_kk`, with `J` the Jacobian of the actual response, whenever `JᵀJ` is invertible. -/
theorem p1_thm_cramer_rao_actual {n : ℕ} (a κ V : ℝ) (T : ℕ) (θ0 : Fin (n + n) → ℝ)
    (hJ : IsUnit ((p1ProbeJac a κ V T θ0)ᵀ * p1ProbeJac a κ V T θ0).det) (v : ℝ≥0) (hv : v ≠ 0)
    (S : ObservationRecord T → ℝ) (hS : MemLp S 2 (gaussianRecordLaw T (p1ProbeMean a κ V T θ0) v))
    (k : Fin (n + n)) (hU : ∀ᶠ θ in 𝓝 θ0, ∫ x, S x ∂(gaussianRecordLaw T (p1ProbeMean a κ V T θ) v) = θ k) :
    (v : ℝ) * ((p1ProbeJac a κ V T θ0)ᵀ * p1ProbeJac a κ V T θ0)⁻¹ k k ≤
      variance S (gaussianRecordLaw T (p1ProbeMean a κ V T θ0) v) :=
  p1_thm_gaussian_cramer_rao (p1ProbeMean a κ V T) θ0 (p1ProbeJac a κ V T θ0) hJ v hv S hS k hU
    (fun d t => p1_probeMean_line_deriv a κ V T θ0 d t)

end CurrentMM
