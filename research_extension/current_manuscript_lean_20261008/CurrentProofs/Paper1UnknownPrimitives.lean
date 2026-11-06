import CurrentProofs.Paper1MergedModel

/-!
# Paper 1, Corollary `cor:unknown_primitives` (i)–(ii): identification with unknown persistence and impact

In the paper's model the price response satisfies `h_0 = κ` and
`h_{t+1} = a h_t + κ ∑_{m ≤ t} k_m h_{t-m}` with `k_m = ∑_i w_i r_i^m`, `w_i = q_i η_i`, `r_i = 1 - η_i`.

* `p1_cor_unknown_primitives_recursion` (part (i)): with `k̃_0 = k_0 + a/κ` and `k̃_m = k_m` for `m ≥ 1`, the response is
  `h_{t+1} = κ ∑_{m ≤ t} k̃_m h_{t-m}`; the persistence `a` acts as a group with memory rate zero.
* `p1_cor_unknown_primitives_identification` (part (ii)): if two economies with **unknown and possibly different**
  `(a, κ)` and `(a', κ')`, `κ ≠ 0`, and memory rates `r_i ≠ 0`, have the same price response, then `κ = κ'`, `a = a'`,
  and the merged rate–weight measures are equal.

The rate statement (iii) of the corollary is proved on paper; it is not formalized here.
-/

namespace CurrentMM

open Finset

/-- The kernel with the persistence absorbed as a memory-rate-zero group. -/
noncomputable def absorbedKernel {n : ℕ} (a κ : ℝ) (q rate : Fin n → ℝ) (m : ℕ) : ℝ :=
  cohortKernel q rate m + if m = 0 then a / κ else 0

/-- **Part (i).** -/
theorem p1_cor_unknown_primitives_recursion {n : ℕ} (a κ : ℝ) (hκ : κ ≠ 0) (q rate : Fin n → ℝ) (t : ℕ) :
    actualCohortImpulse a κ q rate (t + 1) =
      0 * actualCohortImpulse a κ q rate t +
        κ * ∑ m ∈ range (t + 1), absorbedKernel a κ q rate m * actualCohortImpulse a κ q rate (t - m) := by
  rw [p1_impulse_closed_loop_recursion]
  unfold absorbedKernel
  simp only [add_mul, sum_add_distrib, ite_mul, zero_mul, Finset.sum_ite_eq', Finset.mem_range,
    Nat.zero_lt_succ, ↓reduceIte, Nat.sub_zero, zero_add]
  field_simp
  ring

/-- The merged weight of `w · r` at `ρ` is `ρ` times the merged weight of `w`. -/
theorem p1_mergedWeight_mul_rate {ι : Type*} (S : Finset ι) (r w : ι → ℝ) (ρ : ℝ) :
    mergedWeight S r (fun i => w i * r i) ρ = ρ * mergedWeight S r w ρ := by
  unfold mergedWeight
  rw [mul_sum]
  refine sum_congr rfl (fun i hi => ?_)
  rw [(mem_filter.mp hi).2]; ring

/-- Total mass as a sum of merged weights. -/
theorem p1_sum_eq_sum_mergedWeight {ι : Type*} (S : Finset ι) (r w : ι → ℝ) (R : Finset ℝ)
    (hR : ∀ i ∈ S, r i ∈ R) : ∑ i ∈ S, w i = ∑ ρ ∈ R, mergedWeight S r w ρ := by
  classical
  rw [← sum_fiberwise_of_maps_to (g := r) (t := R) hR]
  rfl

/-- **Part (ii): identification with unknown `a` and `κ`.** -/
theorem p1_cor_unknown_primitives_identification {n n' : ℕ} (a κ a' κ' : ℝ) (hκ : κ ≠ 0)
    (q rate : Fin n → ℝ) (q' rate' : Fin n' → ℝ)
    (hr : ∀ i, 1 - rate i ≠ 0) (hr' : ∀ i, 1 - rate' i ≠ 0)
    (hsame : ∀ j, actualCohortImpulse a κ q rate j = actualCohortImpulse a' κ' q' rate' j) :
    κ = κ' ∧ a = a' ∧ ∀ ρ, mergedWeight univ (fun i => 1 - rate i) (fun i => q i * rate i) ρ =
      mergedWeight univ (fun i => 1 - rate' i) (fun i => q' i * rate' i) ρ := by
  classical
  have hκκ : κ = κ' := by
    have := hsame 0; rwa [p1_impulse_zero, p1_impulse_zero] at this
  subst hκκ
  -- the absorbed kernels coincide
  have hk := p1_thm_merged_deconvolution 0 κ hκ (absorbedKernel a κ q rate) (absorbedKernel a' κ q' rate')
    (actualCohortImpulse a κ q rate) (p1_impulse_zero a κ q rate)
    (p1_cor_unknown_primitives_recursion a κ hκ q rate)
    (fun t => by
      rw [hsame (t + 1), p1_cor_unknown_primitives_recursion a' κ hκ q' rate' t, ← hsame t]
      congr 2
      refine sum_congr rfl (fun m _ => by rw [hsame (t - m)]))
  -- moments of `w · r` agree in every order
  have hmom : ∀ m : ℕ, ∑ i, (q i * rate i * (1 - rate i)) * (1 - rate i) ^ m =
      ∑ i, (q' i * rate' i * (1 - rate' i)) * (1 - rate' i) ^ m := by
    intro m
    have := hk (m + 1)
    unfold absorbedKernel cohortKernel at this
    rw [if_neg (by omega : m + 1 ≠ 0), if_neg (by omega : m + 1 ≠ 0), add_zero, add_zero] at this
    rw [show (∑ i, q i * rate i * (1 - rate i) * (1 - rate i) ^ m) = ∑ i, q i * rate i * (1 - rate i) ^ (m + 1) by
      refine sum_congr rfl (fun i _ => by ring)]
    rw [show (∑ i, q' i * rate' i * (1 - rate' i) * (1 - rate' i) ^ m) =
      ∑ i, q' i * rate' i * (1 - rate' i) ^ (m + 1) by refine sum_congr rfl (fun i _ => by ring)]
    exact this
  have hmw := p1_thm_merged_measure_identified univ univ (fun i => 1 - rate i)
    (fun i => q i * rate i * (1 - rate i)) (fun i => 1 - rate' i) (fun i => q' i * rate' i * (1 - rate' i)) hmom
  -- divide by the memory rate (nonzero)
  have hw : ∀ ρ, mergedWeight univ (fun i => 1 - rate i) (fun i => q i * rate i) ρ =
      mergedWeight univ (fun i => 1 - rate' i) (fun i => q' i * rate' i) ρ := by
    intro ρ
    have e := hmw ρ
    rw [p1_mergedWeight_mul_rate univ (fun i => 1 - rate i) (fun i => q i * rate i) ρ,
      p1_mergedWeight_mul_rate univ (fun i => 1 - rate' i) (fun i => q' i * rate' i) ρ] at e
    by_cases hρ : ρ = 0
    · subst hρ
      have h1 : mergedWeight univ (fun i => 1 - rate i) (fun i => q i * rate i) 0 = 0 := by
        unfold mergedWeight
        rw [filter_eq_empty_iff.mpr (fun i _ h => hr i h), sum_empty]
      have h2 : mergedWeight univ (fun i => 1 - rate' i) (fun i => q' i * rate' i) 0 = 0 := by
        unfold mergedWeight
        rw [filter_eq_empty_iff.mpr (fun i _ h => hr' i h), sum_empty]
      rw [h1, h2]
    · exact mul_left_cancel₀ hρ e
  refine ⟨rfl, ?_, hw⟩
  -- the persistence from the order-zero absorbed kernel
  set R : Finset ℝ := univ.image (fun i => 1 - rate i) ∪ univ.image (fun i => 1 - rate' i)
  have hm1 := p1_sum_eq_sum_mergedWeight univ (fun i => 1 - rate i) (fun i => q i * rate i) R
    (fun i _ => mem_union_left _ (mem_image_of_mem _ (mem_univ i)))
  have hm2 := p1_sum_eq_sum_mergedWeight univ (fun i => 1 - rate' i) (fun i => q' i * rate' i) R
    (fun i _ => mem_union_right _ (mem_image_of_mem _ (mem_univ i)))
  have hmass : ∑ i, q i * rate i = ∑ i, q' i * rate' i := by
    rw [hm1, hm2]; exact sum_congr rfl (fun ρ _ => hw ρ)
  have h0 := hk 0
  unfold absorbedKernel cohortKernel at h0
  rw [if_pos rfl, if_pos rfl] at h0
  simp only [pow_zero, mul_one] at h0
  rw [hmass] at h0
  have : a / κ = a' / κ := by linarith
  field_simp at this
  exact this

end CurrentMM
