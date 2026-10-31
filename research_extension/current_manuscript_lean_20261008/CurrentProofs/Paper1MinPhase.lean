import CurrentProofs.Paper1PoleCount
import Mathlib.Analysis.Complex.Basic
import Mathlib.Algebra.Polynomial.Eval.Coeff

/-!
# Paper 1, Theorem `thm:minphase` (passive identification): zeros of `H` and minimum phase

For distinct memory rates `0 < r_i < 1`, nonzero merged weights, `a ≠ 0` and `κ ≠ 0`, the complex zeros of the
numerator `κ z D(z)` of `H` are exactly `0` and the `r_i`; none of them is a root of the denominator, so these are
exactly the zeros of `H` (no cancellation, over `ℂ`); and all of them lie strictly inside the unit disk, so `H` is
minimum phase when it is stable. The spectral-factorization step (the price spectrum determines a minimum-phase
`H` up to scale) is not formalized.
-/

namespace CurrentMM

open Polynomial Finset

theorem p1_tfTop_map_eval {K : ℕ} (κ : ℝ) (r : Fin K → ℝ) (z : ℂ) :
    ((tfTop κ r).map (algebraMap ℝ ℂ)).eval z = κ * z * ∏ i, (z - r i) := by
  simp [tfTop, tfDen, Polynomial.map_prod, eval_prod]

/-- **Zeros of `H`.** Over `ℂ`, the numerator's zeros are exactly `0` and the memory rates; at each of them the
denominator does not vanish; and each has modulus below one. -/
theorem p1_thm_minphase_zeros {K : ℕ} (a κ : ℝ) (w r : Fin K → ℝ) (ha : a ≠ 0) (hκ : κ ≠ 0)
    (hr : Function.Injective r) (hr0 : ∀ i, 0 < r i) (hr1 : ∀ i, r i < 1) (hw : ∀ i, w i ≠ 0) :
    (∀ z : ℂ, ((tfTop κ r).map (algebraMap ℝ ℂ)).eval z = 0 ↔ z = 0 ∨ ∃ i, z = (r i : ℂ)) ∧
    (∀ z : ℂ, ((tfTop κ r).map (algebraMap ℝ ℂ)).eval z = 0 →
      ((tfBottom a κ w r).map (algebraMap ℝ ℂ)).eval z ≠ 0) ∧
    (∀ z : ℂ, ((tfTop κ r).map (algebraMap ℝ ℂ)).eval z = 0 → ‖z‖ < 1) := by
  have hzeros : ∀ z : ℂ, ((tfTop κ r).map (algebraMap ℝ ℂ)).eval z = 0 ↔ z = 0 ∨ ∃ i, z = (r i : ℂ) := by
    intro z
    rw [p1_tfTop_map_eval]
    have hκc : (κ : ℂ) ≠ 0 := by exact_mod_cast hκ
    constructor
    · intro h
      rcases mul_eq_zero.mp h with h1 | h1
      · rcases mul_eq_zero.mp h1 with h2 | h2
        · exact absurd h2 hκc
        · exact Or.inl h2
      · obtain ⟨i, _, hi⟩ := prod_eq_zero_iff.mp h1
        exact Or.inr ⟨i, sub_eq_zero.mp hi⟩
    · rintro (h | ⟨i, h⟩)
      · simp [h]
      · rw [prod_eq_zero (mem_univ i) (by rw [h, sub_self]), mul_zero]
  have hreal : ∀ z : ℂ, ((tfTop κ r).map (algebraMap ℝ ℂ)).eval z = 0 → ∃ x : ℝ, z = x ∧ (tfTop κ r).eval x = 0 := by
    intro z hz
    rcases (hzeros z).mp hz with h | ⟨i, h⟩
    · refine ⟨0, by simp [h], ?_⟩; simp [tfTop]
    · refine ⟨r i, h, ?_⟩
      simp [tfTop, tfDen, eval_prod, prod_eq_zero (mem_univ i)]
  refine ⟨hzeros, fun z hz => ?_, fun z hz => ?_⟩
  · obtain ⟨x, rfl, hx⟩ := hreal z hz
    have hne := (p1_thm_merged_pole_count a κ w r ha hκ hr (fun i => (hr0 i).ne') hw).1 x hx
    rw [eval_map]
    intro h
    apply hne
    have e := Polynomial.eval₂_at_apply (algebraMap ℝ ℂ) x (p := tfBottom a κ w r)
    simp only [Complex.coe_algebraMap] at e
    rw [e] at h
    exact_mod_cast h
  · rcases (hzeros z).mp hz with h | ⟨i, h⟩
    · simp [h]
    · rw [h, Complex.norm_real, Real.norm_eq_abs, abs_of_pos (hr0 i)]; exact hr1 i

end CurrentMM
