import Mathlib.LinearAlgebra.Vandermonde
import Mathlib.Basic.Real.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
# Paper 1, Theorem `thm:merged` (i): prices identify the merged measure and nothing finer

The closed-loop price response to a unit probe satisfies `h₀ = κ`,
`h_{t+1} = a h_t + κ ∑_{j ≤ t} k_j h_{t-j}`, where `k_m = ∑_i w_i r_i^m` is the feedback kernel of the cohort
population (rates `r_i`, merged weights `w_i = q_i η_i`). This file proves, for known `a` and `κ ≠ 0`:

* `p1_thm_merged_deconvolution`: the price response determines every kernel value (the loop can be inverted);
* `p1_thm_merged_kernel_from_measure`: equal kernels give equal price responses;
* `p1_thm_merged_measure_identified`: equal kernels force equal merged measures, i.e. equal total weight at every
  rate (Vandermonde argument), so two populations give the same price response **iff** their merged measures agree.

Not proved here: that the state-space impulse `actualCohortImpulse` satisfies the scalar recursion above (stated in
the paper as the transfer function `H(z)`), and the McMillan-degree count of part (i).
-/

namespace CurrentMM

open Finset

/-- **Deconvolution.** If one price response `h` (with `h 0 = κ ≠ 0`) is produced by two kernels `k` and `k'`
through the closed-loop recursion, the kernels coincide. -/
theorem p1_thm_merged_deconvolution (a κ : ℝ) (hκ : κ ≠ 0) (k k' h : ℕ → ℝ) (h0 : h 0 = κ)
    (hrec : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), k j * h (t - j))
    (hrec' : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), k' j * h (t - j)) :
    ∀ m, k m = k' m := by
  intro m
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    have e := (hrec m).symm.trans (hrec' m)
    have e2 : ∑ j ∈ range (m + 1), k j * h (m - j) = ∑ j ∈ range (m + 1), k' j * h (m - j) := by
      have := add_left_cancel e
      exact mul_left_cancel₀ hκ this
    rw [sum_range_succ, sum_range_succ] at e2
    have hlow : ∑ j ∈ range m, k j * h (m - j) = ∑ j ∈ range m, k' j * h (m - j) :=
      sum_congr rfl (fun j hj => by rw [ih j (mem_range.mp hj)])
    rw [hlow, Nat.sub_self, h0] at e2
    exact mul_right_cancel₀ hκ (add_left_cancel e2)

/-- **Converse.** Equal kernels and the same `a`, `κ` give the same price response. -/
theorem p1_thm_merged_kernel_from_measure (a κ : ℝ) (k h h' : ℕ → ℝ) (h0 : h 0 = κ) (h0' : h' 0 = κ)
    (hrec : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), k j * h (t - j))
    (hrec' : ∀ t, h' (t + 1) = a * h' t + κ * ∑ j ∈ range (t + 1), k j * h' (t - j)) :
    ∀ t, h t = h' t := by
  intro t
  induction t using Nat.strong_induction_on with
  | _ t ih =>
    cases t with
    | zero => rw [h0, h0']
    | succ s =>
      rw [hrec s, hrec' s, ih s (Nat.lt_succ_self s)]
      congr 2
      refine sum_congr rfl (fun j hj => ?_)
      rw [ih (s - j) (by omega)]

/-- Exponential sums over finitely many distinct rates are linearly independent. -/
theorem p1_merged_exp_sums_independent (R : Finset ℝ) (c : ℝ → ℝ)
    (h : ∀ m : ℕ, ∑ ρ ∈ R, c ρ * ρ ^ m = 0) : ∀ ρ ∈ R, c ρ = 0 := by
  classical
  set n := R.card
  let e : R ≃ Fin n := R.equivFin
  let r : Fin n → ℝ := fun i => (e.symm i : ℝ)
  have hr : Function.Injective r := by
    intro i j hij
    have : e.symm i = e.symm j := Subtype.ext hij
    exact e.symm.injective this
  have hsum : ∀ m : ℕ, ∑ i : Fin n, c (r i) * r i ^ m = 0 := by
    intro m
    have h1 : ∑ i : Fin n, c (r i) * r i ^ m = ∑ x : R, c x * (x : ℝ) ^ m :=
      Fintype.sum_equiv e.symm _ _ (fun i => rfl)
    rw [h1, sum_coe_sort R (fun x => c x * x ^ m)]
    exact h m
  have hdet : (Matrix.vandermonde r).det ≠ 0 := Matrix.det_vandermonde_ne_zero_iff.mpr hr
  have hz : (fun i => c (r i)) = 0 := by
    apply Matrix.eq_zero_of_vecMul_eq_zero hdet
    funext m
    simp only [Matrix.vecMul, dotProduct, Matrix.vandermonde_apply, Pi.zero_apply]
    exact hsum m
  intro ρ hρ
  have := congrFun hz (e ⟨ρ, hρ⟩)
  simpa [r] using this

/-- Merged weight of a finite population at rate `ρ`: the total weight of its cohorts with that rate. -/
noncomputable def mergedWeight {ι : Type*} (S : Finset ι) (r w : ι → ℝ) (ρ : ℝ) : ℝ :=
  ∑ i ∈ S.filter (fun i => r i = ρ), w i

/-- **Merged measure identified.** Two finite cohort populations with the same kernel values
`∑ w_i r_i^m` for every `m` have the same merged weight at every rate. -/
theorem p1_thm_merged_measure_identified {ι κ : Type*} (S : Finset ι) (T : Finset κ)
    (r w : ι → ℝ) (r' w' : κ → ℝ)
    (hk : ∀ m : ℕ, ∑ i ∈ S, w i * r i ^ m = ∑ i ∈ T, w' i * r' i ^ m) :
    ∀ ρ, mergedWeight S r w ρ = mergedWeight T r' w' ρ := by
  classical
  set R : Finset ℝ := S.image r ∪ T.image r'
  have fib : ∀ m : ℕ, ∑ i ∈ S, w i * r i ^ m = ∑ ρ ∈ R, mergedWeight S r w ρ * ρ ^ m := by
    intro m
    rw [← sum_fiberwise_of_maps_to (g := r) (t := R) (fun i hi => mem_union_left _ (mem_image_of_mem r hi))]
    refine sum_congr rfl (fun ρ _ => ?_)
    unfold mergedWeight
    rw [sum_mul]
    refine sum_congr rfl (fun i hi => ?_)
    rw [(mem_filter.mp hi).2]
  have fib' : ∀ m : ℕ, ∑ i ∈ T, w' i * r' i ^ m = ∑ ρ ∈ R, mergedWeight T r' w' ρ * ρ ^ m := by
    intro m
    rw [← sum_fiberwise_of_maps_to (g := r') (t := R) (fun i hi => mem_union_right _ (mem_image_of_mem r' hi))]
    refine sum_congr rfl (fun ρ _ => ?_)
    unfold mergedWeight
    rw [sum_mul]
    refine sum_congr rfl (fun i hi => ?_)
    rw [(mem_filter.mp hi).2]
  have hzero := p1_merged_exp_sums_independent R (fun ρ => mergedWeight S r w ρ - mergedWeight T r' w' ρ)
    (fun m => by
      simp only [sub_mul, sum_sub_distrib]
      rw [← fib, ← fib', hk, sub_self])
  intro ρ
  by_cases hρ : ρ ∈ R
  · exact sub_eq_zero.mp (hzero ρ hρ)
  · have hS : S.filter (fun i => r i = ρ) = ∅ := by
      refine filter_eq_empty_iff.mpr (fun i hi hri => hρ ?_)
      exact mem_union_left _ (hri ▸ mem_image_of_mem r hi)
    have hT : T.filter (fun i => r' i = ρ) = ∅ := by
      refine filter_eq_empty_iff.mpr (fun i hi hri => hρ ?_)
      exact mem_union_right _ (hri ▸ mem_image_of_mem r' hi)
    simp [mergedWeight, hS, hT]

end CurrentMM
