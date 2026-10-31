import CurrentProofs.Paper1MergedModel

/-!
# Paper 1: finitely many noise-free observations identify the economy

Strengthens `thm:merged` (i) and supplies the uniqueness step used by `prop:esprit`:
* `p1_finite_exp_sums_independent`: exponential sums over `n` distinct rates vanish at the first `n` powers only if
  every coefficient vanishes (a square Vandermonde system);
* `p1_thm_measure_from_finitely_many_moments`: two populations with `n` and `n'` cohorts and equal kernel values
  `k_0, …, k_{n+n'-1}` have equal merged weights at every rate — in particular a measure with `K` atoms is
  determined by its first `2K` moments, the injectivity used in the proof of Theorem 5.4;
* `p1_thm_merged_deconvolution_finite`: equal price taps `h_0, …, h_m` give equal kernel values `k_0, …, k_{m-1}`;
* `p1_thm_merged_model_finite_identification`: for the paper's state-space model with known `a` and `κ ≠ 0`, two
  economies with `n` and `n'` cohorts whose noise-free price responses agree for `n + n' + 1` periods have the same
  merged measure. For two `K`-cohort economies, `2K + 1` periods suffice.
-/

namespace CurrentMM

open Finset

/-- Square Vandermonde: the first `card R` powers already force every coefficient to vanish. -/
theorem p1_finite_exp_sums_independent (R : Finset ℝ) (c : ℝ → ℝ)
    (h : ∀ m : ℕ, m < R.card → ∑ ρ ∈ R, c ρ * ρ ^ m = 0) : ∀ ρ ∈ R, c ρ = 0 := by
  classical
  set n := R.card
  let e : R ≃ Fin n := R.equivFin
  let r : Fin n → ℝ := fun i => (e.symm i : ℝ)
  have hr : Function.Injective r := by
    intro i j hij
    have : e.symm i = e.symm j := Subtype.ext hij
    exact e.symm.injective this
  have hsum : ∀ m : Fin n, ∑ i : Fin n, c (r i) * r i ^ (m : ℕ) = 0 := by
    intro m
    have h1 : ∑ i : Fin n, c (r i) * r i ^ (m : ℕ) = ∑ x : R, c x * (x : ℝ) ^ (m : ℕ) :=
      Fintype.sum_equiv e.symm _ _ (fun i => rfl)
    rw [h1, sum_coe_sort R (fun x => c x * x ^ (m : ℕ))]
    exact h m m.isLt
  have hdet : (Matrix.vandermonde r).det ≠ 0 := Matrix.det_vandermonde_ne_zero_iff.mpr hr
  have hz : (fun i => c (r i)) = 0 := by
    apply Matrix.eq_zero_of_vecMul_eq_zero hdet
    funext m
    simp only [Matrix.vecMul, dotProduct, Matrix.vandermonde_apply, Pi.zero_apply]
    exact hsum m
  intro ρ hρ
  have := congrFun hz (e ⟨ρ, hρ⟩)
  simpa [r] using this

/-- **Finitely many moments identify the merged measure.** Populations indexed by `S` and `T` with equal kernel
values for every order below `card S + card T` have equal merged weights at every rate. -/
theorem p1_thm_measure_from_finitely_many_moments {ι κ : Type*} (S : Finset ι) (T : Finset κ)
    (r w : ι → ℝ) (r' w' : κ → ℝ)
    (hk : ∀ m : ℕ, m < S.card + T.card → ∑ i ∈ S, w i * r i ^ m = ∑ i ∈ T, w' i * r' i ^ m) :
    ∀ ρ, mergedWeight S r w ρ = mergedWeight T r' w' ρ := by
  classical
  set R : Finset ℝ := S.image r ∪ T.image r'
  have hcard : R.card ≤ S.card + T.card :=
    le_trans (card_union_le _ _) (add_le_add card_image_le card_image_le)
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
  have hzero := p1_finite_exp_sums_independent R
    (fun ρ => mergedWeight S r w ρ - mergedWeight T r' w' ρ)
    (fun m hm => by
      simp only [sub_mul, sum_sub_distrib]
      rw [← fib, ← fib', hk m (lt_of_lt_of_le hm hcard), sub_self])
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

/-- **Finite deconvolution.** If two responses obey the closed loop with the same `a`, `κ ≠ 0`, both start at `κ`,
and agree for `t ≤ m`, their kernels agree below order `m`. -/
theorem p1_thm_merged_deconvolution_finite (a κ : ℝ) (hκ : κ ≠ 0) (k k' h h' : ℕ → ℝ) (m : ℕ)
    (h0 : h 0 = κ)
    (hrec : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), k j * h (t - j))
    (hrec' : ∀ t, h' (t + 1) = a * h' t + κ * ∑ j ∈ range (t + 1), k' j * h' (t - j))
    (hsame : ∀ t, t ≤ m → h t = h' t) :
    ∀ j, j < m → k j = k' j := by
  intro j
  induction j using Nat.strong_induction_on with
  | _ j ih =>
    intro hj
    have e1 := hrec j
    have e2 := hrec' j
    rw [← hsame (j + 1) (by omega), ← hsame j (by omega)] at e2
    have hh : ∀ i ∈ range (j + 1), h' (j - i) = h (j - i) := fun i _ => (hsame (j - i) (by omega)).symm
    rw [sum_congr rfl (fun i hi => by rw [hh i hi])] at e2
    have e := e1.symm.trans e2
    have e3 : ∑ i ∈ range (j + 1), k i * h (j - i) = ∑ i ∈ range (j + 1), k' i * h (j - i) :=
      mul_left_cancel₀ hκ (add_left_cancel e)
    rw [sum_range_succ, sum_range_succ] at e3
    have hlow : ∑ i ∈ range j, k i * h (j - i) = ∑ i ∈ range j, k' i * h (j - i) :=
      sum_congr rfl (fun i hi => by rw [ih i (mem_range.mp hi) (by have := mem_range.mp hi; omega)])
    rw [hlow, Nat.sub_self, h0] at e3
    exact mul_right_cancel₀ hκ (add_left_cancel e3)

/-- **Finite identification for the model.** With known `a` and `κ ≠ 0`, two cohort economies with `n` and `n'`
cohorts whose noise-free price responses agree for periods `0, …, n + n'` have the same merged weight at every
memory rate. For two `K`-cohort economies, `2K + 1` periods of noise-free prices suffice. -/
theorem p1_thm_merged_model_finite_identification {n n' : ℕ} (a impact : ℝ) (himpact : impact ≠ 0)
    (q rate : Fin n → ℝ) (q' rate' : Fin n' → ℝ)
    (hsame : ∀ j, j ≤ n + n' → actualCohortImpulse a impact q rate j = actualCohortImpulse a impact q' rate' j) :
    ∀ ρ, mergedWeight univ (fun i => 1 - rate i) (fun i => q i * rate i) ρ =
      mergedWeight univ (fun i => 1 - rate' i) (fun i => q' i * rate' i) ρ := by
  have hk := p1_thm_merged_deconvolution_finite a impact himpact (cohortKernel q rate) (cohortKernel q' rate')
    (actualCohortImpulse a impact q rate) (actualCohortImpulse a impact q' rate') (n + n')
    (p1_impulse_zero a impact q rate) (p1_impulse_closed_loop_recursion a impact q rate)
    (p1_impulse_closed_loop_recursion a impact q' rate') hsame
  apply p1_thm_measure_from_finitely_many_moments
  intro m hm
  have := hk m (by simpa using hm)
  simpa [cohortKernel] using this

end CurrentMM
