import Mathlib.Analysis.Calculus.InverseFunctionTheorem.ApproximatesLinearOn
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Analysis.Calculus.ContDiff.Basic
import Mathlib.Analysis.Normed.Module.FiniteDimension
import Mathlib.Topology.MetricSpace.Thickening
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

/-!
# Paper 1: a uniform inverse function theorem on a compact set

The step of `prop:esprit` (Theorem 5.4) that Mathlib does not supply directly: for a `C¹` map between
finite-dimensional spaces of equal dimension whose derivative is injective at every point of a compact set `Q`,
one radius `ρ₀` and one constant `L` work at every point of `Q`. Every target within `ρ₀` of `f x` is hit by
some point within `L · dist` of `x`.

* `p1_uniform_lower_bound_fderiv`: `‖f'(x) v‖ ≥ m ‖v‖` with one `m > 0` for all `x ∈ Q`;
* `p1_uniform_local_inverse`: the uniform local surjectivity with a Lipschitz radius.
-/

namespace CurrentMM

open Set Metric
open scoped NNReal

variable {E F : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [FiniteDimensional ℝ E]
  [NormedAddCommGroup F] [NormedSpace ℝ F] [FiniteDimensional ℝ F]

omit [FiniteDimensional ℝ F] in
/-- An injective derivative on a compact set is bounded below by one constant. -/
theorem p1_uniform_lower_bound_fderiv {f : E → F} (hf : ContDiff ℝ 1 f) {Q : Set E} (hQ : IsCompact Q)
    (hinj : ∀ x ∈ Q, Function.Injective (fderiv ℝ f x)) :
    ∃ m > 0, ∀ x ∈ Q, ∀ v, m * ‖v‖ ≤ ‖fderiv ℝ f x v‖ := by
  have hcont : Continuous fun p : E × E => ‖fderiv ℝ f p.1 p.2‖ := by
    have h1 : Continuous fun p : E × E => fderiv ℝ f p.1 :=
      (hf.continuous_fderiv one_ne_zero).comp continuous_fst
    exact (h1.clm_apply continuous_snd).norm
  by_cases hne : (Q ×ˢ sphere (0 : E) 1).Nonempty
  · obtain ⟨p, hp, hmin⟩ := (hQ.prod (isCompact_sphere 0 1)).exists_isMinOn hne hcont.continuousOn
    refine ⟨‖fderiv ℝ f p.1 p.2‖, ?_, ?_⟩
    · have hp2 : p.2 ≠ 0 := by
        intro h
        have := hp.2
        rw [h, mem_sphere_zero_iff_norm, norm_zero] at this
        exact zero_ne_one this
      show 0 < _
      rw [norm_pos_iff]
      intro h0
      exact hp2 (hinj p.1 hp.1 (by rw [h0, map_zero]))
    · intro x hx v
      rcases eq_or_ne v 0 with rfl | hv
      · simp
      · have hvn : 0 < ‖v‖ := norm_pos_iff.mpr hv
        have hmem : (x, ‖v‖⁻¹ • v) ∈ Q ×ˢ sphere (0 : E) 1 :=
          ⟨hx, by rw [mem_sphere_zero_iff_norm, norm_smul, norm_inv, norm_norm, inv_mul_cancel₀ hvn.ne']⟩
        have h := isMinOn_iff.mp hmin _ hmem
        simp only at h
        rw [map_smul, norm_smul, norm_inv, norm_norm] at h
        calc ‖fderiv ℝ f p.1 p.2‖ * ‖v‖ ≤ (‖v‖⁻¹ * ‖fderiv ℝ f x v‖) * ‖v‖ := by gcongr
          _ = ‖fderiv ℝ f x v‖ := by field_simp
  · refine ⟨1, one_pos, fun x hx v => ?_⟩
    rcases eq_or_ne v 0 with rfl | hv
    · simp
    · have hvn : 0 < ‖v‖ := norm_pos_iff.mpr hv
      exact absurd ⟨(x, ‖v‖⁻¹ • v), hx,
        by rw [mem_sphere_zero_iff_norm, norm_smul, norm_inv, norm_norm, inv_mul_cancel₀ hvn.ne']⟩ hne

/-- **Uniform inverse function theorem on a compact set.** A `C¹` map between spaces of equal finite dimension
whose derivative is injective on a compact set `Q` admits one radius `ρ₀ > 0` and one constant `L > 0` such that
every `y` within `ρ₀` of `f x`, `x ∈ Q`, equals `f z` for some `z` within `L · dist y (f x)` of `x`. -/
theorem p1_uniform_local_inverse {f : E → F} (hf : ContDiff ℝ 1 f)
    (hdim : Module.finrank ℝ E = Module.finrank ℝ F) {Q : Set E} (hQ : IsCompact Q)
    (hinj : ∀ x ∈ Q, Function.Injective (fderiv ℝ f x)) :
    ∃ ρ₀ > 0, ∃ L > 0, ∀ x ∈ Q, ∀ y, dist y (f x) ≤ ρ₀ →
      ∃ z, dist z x ≤ L * dist y (f x) ∧ f z = y := by
  obtain ⟨m, hm, hlow⟩ := p1_uniform_lower_bound_fderiv hf hQ hinj
  have hK : IsCompact (cthickening 1 Q) := hQ.cthickening
  have huc : UniformContinuousOn (fderiv ℝ f) (cthickening 1 Q) :=
    hK.uniformContinuousOn_of_continuous (hf.continuous_fderiv one_ne_zero).continuousOn
  obtain ⟨δ, hδ, hδc⟩ := Metric.uniformContinuousOn_iff_le.mp huc (m / 2) (by positivity)
  set r := min δ 1 with hr
  have hr0 : 0 < r := lt_min hδ one_pos
  refine ⟨m / 2 * r, by positivity, 2 / m, by positivity, ?_⟩
  intro x hx y hy
  have hball : closedBall x r ⊆ cthickening 1 Q :=
    (closedBall_subset_cthickening hx r).trans (cthickening_mono (min_le_right _ _) Q)
  have hxK : x ∈ cthickening 1 Q := hball (mem_closedBall_self hr0.le)
  have happrox : ApproximatesLinearOn f (fderiv ℝ f x) (closedBall x r) ⟨m / 2, by positivity⟩ := by
    intro u hu w hw
    set g : E → F := fun z => f z - fderiv ℝ f x z with hg
    have hgd : ∀ z, HasFDerivAt g (fderiv ℝ f z - fderiv ℝ f x) z := fun z =>
      ((hf.differentiable one_ne_zero) z).hasFDerivAt.sub (fderiv ℝ f x).hasFDerivAt
    have hbound : ∀ z ∈ closedBall x r, ‖fderiv ℝ g z‖ ≤ m / 2 := by
      intro z hz
      rw [(hgd z).fderiv]
      have := hδc z (hball hz) x hxK ((mem_closedBall.mp hz).trans (min_le_left _ _))
      rwa [dist_eq_norm] at this
    have hmv := (convex_closedBall x r).norm_image_sub_le_of_norm_fderiv_le
      (fun z _ => (hgd z).differentiableAt) hbound hw hu
    have e : g u - g w = f u - f w - fderiv ℝ f x (u - w) := by
      simp only [hg, map_sub]; abel
    rw [e] at hmv
    exact hmv
  have hsurj : Function.Surjective (fderiv ℝ f x) :=
    (LinearMap.injective_iff_surjective_of_finrank_eq_finrank hdim
      (f := (fderiv ℝ f x : E →ₗ[ℝ] F))).mp (hinj x hx)
  let R : (fderiv ℝ f x).NonlinearRightInverse :=
    { toFun := Function.surjInv hsurj
      nnnorm := ⟨1 / m, by positivity⟩
      bound' := fun y => by
        have h := hlow x hx (Function.surjInv hsurj y)
        rw [Function.surjInv_eq hsurj] at h
        show ‖Function.surjInv hsurj y‖ ≤ 1 / m * ‖y‖
        rw [div_mul_eq_mul_div, one_mul, le_div_iff₀ hm]
        linarith [mul_comm m ‖Function.surjInv hsurj y‖]
      right_inv' := fun y => Function.surjInv_eq hsurj y }
  set d := dist y (f x)
  have hd0 : 0 ≤ d := dist_nonneg
  have hεr : 2 / m * d ≤ r := by
    calc 2 / m * d ≤ 2 / m * (m / 2 * r) := by gcongr
      _ = r := by field_simp
  have hsub : closedBall x (2 / m * d) ⊆ closedBall x r := closedBall_subset_closedBall hεr
  have hrad : ((R.nnnorm : ℝ)⁻¹ - ((⟨m / 2, by positivity⟩ : ℝ≥0) : ℝ)) * (2 / m * d) = d := by
    show ((1 / m)⁻¹ - m / 2) * (2 / m * d) = d
    field_simp
    ring
  have hyb : y ∈ closedBall (f x) (((R.nnnorm : ℝ)⁻¹ - ((⟨m / 2, by positivity⟩ : ℝ≥0) : ℝ)) * (2 / m * d)) := by
    rw [hrad, mem_closedBall]
  obtain ⟨z, hz, hfz⟩ :=
    (happrox.mono_set hsub).surjOn_closedBall_of_nonlinearRightInverse R (by positivity) le_rfl hyb
  exact ⟨z, mem_closedBall.mp hz, hfz⟩

end CurrentMM
