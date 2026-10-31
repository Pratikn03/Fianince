import CurrentProofs.Paper1LowerBound
import Mathlib.Algebra.Group.ForwardDiff

/-!
# Paper 1, Theorem `thm:kcohort` for every K, with no hypothesis

A moment-matched pair of `K`-cohort populations exists for every `K`. Take the `2K` equally spaced nodes
`s_k = 2k/(2K-1) - 1`, `k = 0, …, 2K-1`, in `[-1, 1]` and the binomial weights `C(2K-1, k)`. Because the
`(2K-1)`-th forward difference of a polynomial of degree `< 2K-1` vanishes (Mathlib's
`Polynomial.fwdDiff_iter_eq_zero_of_degree_lt`), the odd-indexed and even-indexed halves have equal moments of every
order `≤ 2K-2`. Each half has `K` cohorts and total weight `2^(2K-2)`. (The Gauss and Gauss–Radau rules used in the
paper are another such pair; any pair gives the same lower-bound order.) Combined with `Paper1LowerBound.lean`, this
proves the finite-horizon `(Δη)^-(4K-2)` lower bound for every `K` with no unproved hypothesis.
-/

namespace CurrentMM

open Finset Polynomial

/-- Node `k` of the equally spaced grid with `2L+2` points on `[-1, 1]` (here `K = L + 1`). -/
noncomputable def gridNode (L k : ℕ) : ℝ := 2 * (k : ℝ) / (2 * L + 1) - 1

theorem p1_gridNode_abs_le (L k : ℕ) (hk : k ≤ 2 * L + 1) : |gridNode L k| ≤ 1 := by
  unfold gridNode
  have hpos : (0 : ℝ) < 2 * L + 1 := by positivity
  have hk' : (k : ℝ) ≤ 2 * L + 1 := by exact_mod_cast hk
  rw [abs_le]
  constructor
  · have : 0 ≤ 2 * (k : ℝ) / (2 * L + 1) := by positivity
    linarith
  · rw [sub_le_iff_le_add, div_le_iff₀ hpos]; nlinarith

/-- Alternating binomial sum of a low power of the grid nodes vanishes. -/
theorem p1_grid_alternating_sum_zero (L j : ℕ) (hj : j < 2 * L + 1) :
    ∑ k ∈ range (2 * L + 1 + 1),
      ((-1 : ℝ) ^ (2 * L + 1 - k) * ((2 * L + 1).choose k : ℝ)) * gridNode L k ^ j = 0 := by
  set α : ℝ := 2 / (2 * L + 1)
  have hdeg : ((C α * X + C (-1 : ℝ)) ^ j).natDegree < 2 * L + 1 := by
    have h1 : (C α * X + C (-1 : ℝ)).natDegree ≤ 1 := natDegree_linear_le
    have h2 := natDegree_pow_le_of_le j h1
    omega
  have h := congrFun (Polynomial.fwdDiff_iter_eq_zero_of_degree_lt (R := ℝ) hdeg) 0
  rw [fwdDiff_iter_eq_sum_shift, Pi.zero_apply] at h
  rw [← h]
  refine sum_congr rfl (fun k _ => ?_)
  rw [zsmul_eq_mul]
  push_cast
  congr 1
  simp only [eval_pow, eval_add, eval_mul, eval_C, eval_X, zero_add, nsmul_eq_mul, mul_one]
  unfold gridNode
  congr 1
  simp only [α]
  ring

/-- Splitting a sum over `0, …, 2L+1` into even and odd indices. -/
theorem p1_sum_range_even_odd (f : ℕ → ℝ) (L : ℕ) :
    ∑ k ∈ range (2 * L + 1 + 1), f k = ∑ i ∈ range (L + 1), (f (2 * i) + f (2 * i + 1)) := by
  induction L with
  | zero => simp [sum_range_succ]
  | succ L ih =>
    have e : 2 * (L + 1) + 1 + 1 = (2 * L + 1 + 1) + 1 + 1 := by ring
    rw [e, sum_range_succ, sum_range_succ, ih, sum_range_succ (n := L + 1)]
    have e1 : 2 * L + 1 + 1 = 2 * (L + 1) := by ring
    have e2 : 2 * L + 1 + 1 + 1 = 2 * (L + 1) + 1 := by ring
    rw [e1, e2]; ring

/-- **Matched pair for every K.** The odd-indexed and even-indexed grid populations (`K = L+1` cohorts each,
binomial weights) have equal moments of every order `≤ 2K - 2 = 2L`. -/
theorem p1_grid_matched_moments (L j : ℕ) (hj : j < 2 * L + 1) :
    ∑ i ∈ range (L + 1), ((2 * L + 1).choose (2 * i + 1) : ℝ) * gridNode L (2 * i + 1) ^ j =
      ∑ i ∈ range (L + 1), ((2 * L + 1).choose (2 * i) : ℝ) * gridNode L (2 * i) ^ j := by
  have h := p1_grid_alternating_sum_zero L j hj
  rw [p1_sum_range_even_odd] at h
  have hsign : ∀ i ∈ range (L + 1),
      ((-1 : ℝ) ^ (2 * L + 1 - 2 * i) * ((2 * L + 1).choose (2 * i) : ℝ)) * gridNode L (2 * i) ^ j +
      ((-1 : ℝ) ^ (2 * L + 1 - (2 * i + 1)) * ((2 * L + 1).choose (2 * i + 1) : ℝ)) *
        gridNode L (2 * i + 1) ^ j =
      ((2 * L + 1).choose (2 * i + 1) : ℝ) * gridNode L (2 * i + 1) ^ j -
        ((2 * L + 1).choose (2 * i) : ℝ) * gridNode L (2 * i) ^ j := by
    intro i hi
    have hi' : i ≤ L := Nat.lt_succ_iff.mp (mem_range.mp hi)
    have o1 : 2 * L + 1 - 2 * i = 2 * (L - i) + 1 := by omega
    have o2 : 2 * L + 1 - (2 * i + 1) = 2 * (L - i) := by omega
    rw [o1, o2, pow_succ, pow_mul]
    norm_num
    ring
  rw [sum_congr rfl hsign, sum_sub_distrib, sub_eq_zero] at h
  exact h

/-- Each half of the binomial row carries weight `2^(2L)`. -/
theorem p1_grid_half_weight (L : ℕ) :
    ∑ i ∈ range (L + 1), ((2 * L + 1).choose (2 * i + 1) : ℝ) = 2 ^ (2 * L) ∧
      ∑ i ∈ range (L + 1), ((2 * L + 1).choose (2 * i) : ℝ) = 2 ^ (2 * L) := by
  have h0 := p1_grid_matched_moments L 0 (by omega)
  simp only [pow_zero, mul_one] at h0
  have htot : ∑ k ∈ range (2 * L + 1 + 1), ((2 * L + 1).choose k : ℝ) = 2 ^ (2 * L + 1) := by
    have := Nat.sum_range_choose (2 * L + 1)
    exact_mod_cast this
  rw [p1_sum_range_even_odd, sum_add_distrib] at htot
  have e : (2 : ℝ) ^ (2 * L + 1) = 2 * 2 ^ (2 * L) := by rw [pow_succ]; ring
  rw [e] at htot
  constructor <;> linarith

/-- **`thm:kcohort` for every `K = L + 1`, formal, with no matching hypothesis.** Place the odd-indexed grid
population and the even-indexed one at memory rates `c + d s` (`c, d ≥ 0`, `c + d ≤ 1`), with merged weights
`W · C(2L+1, k) / 2^(2L)`. Any test from `N` reset experiments of `T` taps with noise variance `σ²` and both error
probabilities at most `1/4` satisfies `σ² ≤ 2 N T (2 W 2^T d^(2K-1) C_T)²`, i.e.
`N ≥ σ² d^-(4K-2) / (8 T W² 4^T C_T²)`. -/
theorem p1_thm_kcohort_lower_bound_every_K (L : ℕ) (a κ c d W H : ℝ) (N T : ℕ)
    (q rate q' rate' : Fin (L + 1) → ℝ) (variance : NNReal) (hv : variance ≠ 0)
    (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd : c + d ≤ 1) (hH : 0 ≤ H) (hW : 0 ≤ W)
    (hr : ∀ i : Fin (L + 1), 1 - rate i = c + d * gridNode L (2 * i + 1))
    (hr' : ∀ i : Fin (L + 1), 1 - rate' i = c + d * gridNode L (2 * i))
    (hq : ∀ i : Fin (L + 1), q i * rate i = W * ((2 * L + 1).choose (2 * i + 1) : ℝ) / 2 ^ (2 * L))
    (hq' : ∀ i : Fin (L + 1), q' i * rate' i = W * ((2 * L + 1).choose (2 * i) : ℝ) / 2 ^ (2 * L))
    (hh' : ∀ t, t < T → |actualCohortImpulse a κ q' rate' t| ≤ H)
    (A : Set (ObservationRecord (N * T))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate))
      variance).real A ≤ 1 / 4)
    (herr1 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate'))
      variance).real Aᶜ ≤ 1 / 4) :
    (variance : ℝ) ≤ 2 * N * T * ((2 * W * 2 ^ T * d ^ (2 * L + 1)) * p1GapConst a |κ| W H T) ^ 2 := by
  have hpow : (0 : ℝ) < 2 ^ (2 * L) := by positivity
  obtain ⟨hodd, heven⟩ := p1_grid_half_weight L
  have hw : ∀ i, 0 ≤ q i * rate i := fun i => by rw [hq i]; positivity
  have hw' : ∀ i, 0 ≤ q' i * rate' i := fun i => by rw [hq' i]; positivity
  have hsum : ∑ i, q i * rate i ≤ W := by
    simp only [hq]
    rw [Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i + 1) : ℝ) / 2 ^ (2 * L)),
      ← sum_div, ← mul_sum, hodd, mul_div_assoc, div_self hpow.ne', mul_one]
  have hsum' : ∑ i, q' i * rate' i ≤ W := by
    simp only [hq']
    rw [Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i) : ℝ) / 2 ^ (2 * L)),
      ← sum_div, ← mul_sum, heven, mul_div_assoc, div_self hpow.ne', mul_one]
  refine p1_thm_kcohort_lower_bound_formal a κ c d W H (2 * L + 1) N T q rate
    (fun i => gridNode L (2 * i + 1)) q' rate' (fun i => gridNode L (2 * i)) variance hv hc hd hcd hH hr hr'
    (fun i => p1_gridNode_abs_le L _ (by omega)) (fun i => p1_gridNode_abs_le L _ (by omega))
    hw hw' hsum hsum' (fun j hj => ?_) hh' A hA herr0 herr1
  unfold mgMoment
  simp only [hq, hq']
  rw [Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i + 1) : ℝ) / 2 ^ (2 * L) *
      gridNode L (2 * i + 1) ^ j),
    Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i) : ℝ) / 2 ^ (2 * L) *
      gridNode L (2 * i) ^ j)]
  have hm := p1_grid_matched_moments L j hj
  have e : ∀ (f : ℕ → ℝ), ∑ i ∈ range (L + 1), W * f i / 2 ^ (2 * L) * gridNode L (2 * i + 1) ^ j =
      W / 2 ^ (2 * L) * ∑ i ∈ range (L + 1), f i * gridNode L (2 * i + 1) ^ j := by
    intro f; rw [mul_sum]; refine sum_congr rfl (fun i _ => by ring)
  have e' : ∀ (f : ℕ → ℝ), ∑ i ∈ range (L + 1), W * f i / 2 ^ (2 * L) * gridNode L (2 * i) ^ j =
      W / 2 ^ (2 * L) * ∑ i ∈ range (L + 1), f i * gridNode L (2 * i) ^ j := by
    intro f; rw [mul_sum]; refine sum_congr rfl (fun i _ => by ring)
  rw [e (fun i => ((2 * L + 1).choose (2 * i + 1) : ℝ)), e' (fun i => ((2 * L + 1).choose (2 * i) : ℝ)), hm]

end CurrentMM
