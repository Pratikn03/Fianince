import CurrentProofs.Paper1GaussianHCR
import Mathlib.Analysis.Calculus.Deriv.Slope
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

/-!
# Paper 1, Proposition S7.1 (i): the Cramér–Rao bound for the Gaussian probe record

The statistical experiment is the averaged probe record `Y ~ N(h(θ), σ_h² I_n)` (`gaussianRecordLaw n (h θ) v` with
`v = σ_h²`), where `θ ∈ ℝ^p` collects the unknown market parameters and `h` is the mean response. An estimator is any
statistic `T` of the record that is square-integrable under `θ₀` and unbiased for the coordinate `θ_k` on a
neighbourhood of `θ₀`. Nothing else is assumed about `T`: the proof goes through the Hammersley–Chapman–Robbins
inequality (`p1_thm_gaussian_hcr`) and a limit along lines, so no differentiation under the integral sign is needed.

The mean response is assumed differentiable along lines at `θ₀` with Jacobian `J`:
`d/dt h(θ₀ + t a)ᵢ |_{t=0} = (J a)ᵢ` for every direction `a` (implied by Fréchet differentiability), and `JᵀJ` is
invertible (full column rank, which needs at least `p` informative taps).

* `p1_exp_sub_one_le`: `eᵘ - 1 ≤ u eᵘ`.
* `p1_cr_direction`: for every direction `a`, `a_k² ≤ Var_{θ₀}(T) ‖J a‖² / σ_h²`.
* `p1_thm_gaussian_cramer_rao`: `Var_{θ₀}(T) ≥ σ_h² [(JᵀJ)⁻¹]_{kk}`, i.e. `Var ≥ [I(θ₀)⁻¹]_{kk}` with Fisher information
  `I = σ_h⁻² JᵀJ`.

Outside this file: the inverse-sixth-power scaling of `[(JᵀJ)⁻¹]_{kk}` for the actual closed-loop response
(Proposition S7.1 (iii)), the 95% interval benchmark (S7.1 (ii)), and attainment.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory Filter Topology Matrix Finset
open scoped ENNReal NNReal

theorem p1_exp_sub_one_le (u : ℝ) : Real.exp u - 1 ≤ u * Real.exp u := by
  have h := Real.add_one_le_exp (-u)
  have he : Real.exp (-u) * Real.exp u = 1 := by rw [← Real.exp_add]; simp
  have hm := mul_le_mul_of_nonneg_right h (Real.exp_pos u).le
  rw [he] at hm
  linarith

/-- **Cramér–Rao along one direction.** -/
theorem p1_cr_direction {n p : ℕ} (h : (Fin p → ℝ) → (Fin n → ℝ)) (θ0 : Fin p → ℝ)
    (J : Matrix (Fin n) (Fin p) ℝ) (v : ℝ≥0) (hv : v ≠ 0) (T : ObservationRecord n → ℝ)
    (hT : MemLp T 2 (gaussianRecordLaw n (h θ0) v)) (k : Fin p)
    (hU : ∀ᶠ θ in 𝓝 θ0, ∫ x, T x ∂(gaussianRecordLaw n (h θ) v) = θ k) (a : Fin p → ℝ)
    (hd : ∀ i, HasDerivAt (fun t : ℝ => h (θ0 + t • a) i) ((J *ᵥ a) i) 0) :
    a k ^ 2 ≤ variance T (gaussianRecordLaw n (h θ0) v) * ((∑ i, (J *ᵥ a) i ^ 2) / v) := by
  set V := variance T (gaussianRecordLaw n (h θ0) v) with hVdef
  have hV0 : 0 ≤ V := variance_nonneg _ _
  have hU0 : ∫ x, T x ∂(gaussianRecordLaw n (h θ0) v) = θ0 k := hU.self_of_nhds
  have hslope : ∀ i, Tendsto (fun t : ℝ => t⁻¹ * (h (θ0 + t • a) i - h θ0 i)) (𝓝[≠] 0)
      (𝓝 ((J *ᵥ a) i)) := by
    intro i
    refine (hd i).tendsto_slope_zero.congr fun t => ?_
    simp only [smul_eq_mul, zero_add, zero_smul, add_zero]
  have hcont : ∀ i, Tendsto (fun t : ℝ => h (θ0 + t • a) i - h θ0 i) (𝓝[≠] 0) (𝓝 0) := by
    intro i
    have c : Tendsto (fun t : ℝ => h (θ0 + t • a) i - h θ0 i) (𝓝[≠] 0)
        (𝓝 (h (θ0 + (0 : ℝ) • a) i - h θ0 i)) :=
      ((hd i).continuousAt.tendsto.mono_left (nhdsWithin_le_nhds (s := {(0 : ℝ)}ᶜ))).sub_const _
    simpa using c
  have hr : Tendsto (fun t : ℝ => ∑ i, (t⁻¹ * (h (θ0 + t • a) i - h θ0 i)) ^ 2) (𝓝[≠] 0)
      (𝓝 (∑ i, (J *ᵥ a) i ^ 2)) :=
    tendsto_finsetSum _ fun i _ => (hslope i).pow 2
  have hq : Tendsto (fun t : ℝ => ∑ i, (h (θ0 + t • a) i - h θ0 i) ^ 2) (𝓝[≠] 0)
      (𝓝 (∑ _i : Fin n, (0 : ℝ) ^ 2)) :=
    tendsto_finsetSum _ fun i _ => (hcont i).pow 2
  have hG : Tendsto (fun t : ℝ => V * ((∑ i, (t⁻¹ * (h (θ0 + t • a) i - h θ0 i)) ^ 2) / v) *
      Real.exp ((∑ i, (h (θ0 + t • a) i - h θ0 i) ^ 2) / v)) (𝓝[≠] 0)
      (𝓝 (V * ((∑ i, (J *ᵥ a) i ^ 2) / v) * Real.exp ((∑ _i : Fin n, (0 : ℝ) ^ 2) / v))) :=
    (tendsto_const_nhds.mul (hr.div_const _)).mul (hq.div_const _).rexp
  simp only [ne_eq, OfNat.ofNat_ne_zero, not_false_eq_true, zero_pow, Finset.sum_const_zero, zero_div,
    Real.exp_zero, mul_one] at hG
  have hline : Tendsto (fun t : ℝ => θ0 + t • a) (𝓝[≠] 0) (𝓝 θ0) := by
    have c := ((by fun_prop : Continuous fun t : ℝ => θ0 + t • a).tendsto 0).mono_left
      (nhdsWithin_le_nhds (s := {(0 : ℝ)}ᶜ))
    simpa using c
  refine ge_of_tendsto hG ?_
  filter_upwards [hline.eventually hU, eventually_mem_nhdsWithin] with t ht htne
  have ht0 : t ≠ 0 := htne
  have hcr := p1_thm_gaussian_hcr n (h θ0) (h (θ0 + t • a)) v hv T hT
  rw [ht, hU0] at hcr
  have e1 : (θ0 + t • a) k - θ0 k = t * a k := by simp
  rw [e1] at hcr
  set Q := ∑ i, (h (θ0 + t • a) i - h θ0 i) ^ 2 with hQdef
  set R := ∑ i, (t⁻¹ * (h (θ0 + t • a) i - h θ0 i)) ^ 2 with hRdef
  have hQR : Q = t ^ 2 * R := by
    rw [hQdef, hRdef, Finset.mul_sum]
    refine Finset.sum_congr rfl fun i _ => ?_
    rw [mul_pow, ← mul_assoc, ← mul_pow, mul_inv_cancel₀ ht0, one_pow, one_mul]
  have key : ∀ X : ℝ, V * ((Q / v) * X) = t ^ 2 * (V * (R / v) * X) := fun X => by rw [hQR]; ring
  have ht2 : 0 < t ^ 2 := lt_of_le_of_ne (sq_nonneg t) (Ne.symm (pow_ne_zero 2 ht0))
  have h1 : t ^ 2 * a k ^ 2 ≤ t ^ 2 * (V * (R / v) * Real.exp (Q / v)) := by
    calc t ^ 2 * a k ^ 2 = (t * a k) ^ 2 := by ring
      _ ≤ V * (Real.exp (Q / v) - 1) := hcr
      _ ≤ V * ((Q / v) * Real.exp (Q / v)) := mul_le_mul_of_nonneg_left (p1_exp_sub_one_le _) hV0
      _ = t ^ 2 * (V * (R / v) * Real.exp (Q / v)) := key _
  exact le_of_mul_le_mul_left h1 ht2

/-- **Proposition S7.1 (i): the Cramér–Rao bound.** For the Gaussian probe record with variance `σ_h² = v`, every
statistic that is square-integrable at `θ₀` and unbiased for `θ_k` on a neighbourhood of `θ₀` has
`Var_{θ₀}(T) ≥ σ_h² [(JᵀJ)⁻¹]_{kk}`. -/
theorem p1_thm_gaussian_cramer_rao {n p : ℕ} (h : (Fin p → ℝ) → (Fin n → ℝ)) (θ0 : Fin p → ℝ)
    (J : Matrix (Fin n) (Fin p) ℝ) (hJ : IsUnit (Jᵀ * J).det) (v : ℝ≥0) (hv : v ≠ 0)
    (T : ObservationRecord n → ℝ) (hT : MemLp T 2 (gaussianRecordLaw n (h θ0) v)) (k : Fin p)
    (hU : ∀ᶠ θ in 𝓝 θ0, ∫ x, T x ∂(gaussianRecordLaw n (h θ) v) = θ k)
    (hd : ∀ (a : Fin p → ℝ) (i : Fin n), HasDerivAt (fun t : ℝ => h (θ0 + t • a) i) ((J *ᵥ a) i) 0) :
    (v : ℝ) * (Jᵀ * J)⁻¹ k k ≤ variance T (gaussianRecordLaw n (h θ0) v) := by
  set a : Fin p → ℝ := (Jᵀ * J)⁻¹ *ᵥ Pi.single k 1 with ha
  have hak : a k = (Jᵀ * J)⁻¹ k k := by
    rw [ha, Matrix.mulVec_single_one, Matrix.col_apply]
  have hae : (Jᵀ * J) *ᵥ a = Pi.single k 1 := by
    rw [ha, Matrix.mulVec_mulVec, Matrix.mul_nonsing_inv _ hJ, Matrix.one_mulVec]
  have hL : ∑ i, (J *ᵥ a) i ^ 2 = (Jᵀ * J)⁻¹ k k := by
    have e1 : ∑ i, (J *ᵥ a) i ^ 2 = (J *ᵥ a) ⬝ᵥ (J *ᵥ a) := by simp only [dotProduct, sq]
    rw [e1, Matrix.dotProduct_mulVec, ← Matrix.mulVec_transpose, Matrix.mulVec_mulVec, hae,
      single_dotProduct, one_mul, hak]
  have hdir := p1_cr_direction h θ0 J v hv T hT k hU a (hd a)
  rw [hak, hL] at hdir
  set b := (Jᵀ * J)⁻¹ k k with hb
  set V := variance T (gaussianRecordLaw n (h θ0) v) with hV
  have hV0 : 0 ≤ V := variance_nonneg _ _
  have hv' : (0 : ℝ) < v := lt_of_le_of_ne v.coe_nonneg (Ne.symm (NNReal.coe_ne_zero.mpr hv))
  have hb0 : 0 ≤ b := by
    rw [← hL]; exact Finset.sum_nonneg fun i _ => sq_nonneg _
  rcases hb0.eq_or_lt with hb' | hb'
  · rw [← hb', mul_zero]; exact hV0
  · have h2 : (v : ℝ) * b ^ 2 ≤ V * b := by
      have hm := mul_le_mul_of_nonneg_left hdir hv'.le
      have e : (v : ℝ) * (V * (b / v)) = V * b := by
        first
        | (field_simp; ring)
        | field_simp
      rwa [e] at hm
    exact le_of_mul_le_mul_left (by linarith : b * ((v : ℝ) * b) ≤ b * V) hb'

end CurrentMM
