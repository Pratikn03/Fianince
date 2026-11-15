import CurrentProofs.Paper1GeneralLevel
import CurrentProofs.Paper1GeneralMemoryLower

/-!
# Paper 1, Theorem `thm:kcohort` with a constant that does not depend on the horizon

`p1_thm_kcohort_lower_bound_every_K_general` proves the `(Δη)^-(4K-2)` lower bound for `N` reset experiments of
`T` taps, with a constant that degrades with `T` (a factor `4^T C_T²`). The paper allows `T = ∞`. This file
proves the bound with a constant free of `T`, under exactly the paper's stability hypothesis
`|a| + |κ| W/(1 - r_max) ≤ s < 1`, where `r_max = c + d` is the largest memory rate (`r_c = c`, `Δη = d`).

* `p1_choose_geom_sum_le`: `Σ_{m<N} C(m, n) x^m ≤ x^n/(1 - x)^(n+1)` for `0 ≤ x < 1`.
* `p1_kc_kernel_gap_l1`: populations at rates `c + d s` (`|s| ≤ 1`) with equal weighted node moments below order
  `n` have kernels within `2 W dⁿ/(1 - (c + d))^(n+1)` in `ℓ₁` over all lags.
* `p1_thm_kcohort_lower_bound_uniform`: for the binomial grid pair with `K = L + 1` cohorts each, any test from `N`
  reset experiments of any length `T`, with error probabilities `α₀, β₀` (`α₀ + β₀ ≤ 1`), satisfies
  `4 σ² (1 - α₀ - β₀)² ≤ N (C d^(2K-1))²`, `C = 2 κ² W/((1 - (c + d))^(2K) (1 - s)²)`. So
  `N ≥ 4 (1 - α₀ - β₀)² σ² d^-(4K-2)/C²` for every `T`, including the limit `T → ∞`.
-/

namespace CurrentMM

open Finset MeasureTheory ProbabilityTheory InformationTheory
open scoped ENNReal NNReal

/-- **Negative-binomial partial sums.** `Σ_{m<N} C(m, n) x^m ≤ x^n/(1 - x)^(n+1)`. -/
theorem p1_choose_geom_sum_le (x : ℝ) (hx0 : 0 ≤ x) (hx1 : x < 1) :
    ∀ n N : ℕ, ∑ m ∈ range N, (m.choose n : ℝ) * x ^ m ≤ x ^ n / (1 - x) ^ (n + 1) := by
  have h1x : 0 < 1 - x := by linarith
  intro n
  induction n with
  | zero =>
    intro N
    have h := p1_geom_partial_le x hx0 hx1 N
    simpa using h
  | succ n ih =>
    intro N
    have hshift : ∑ m ∈ range (N + 1), (m.choose (n + 1) : ℝ) * x ^ m =
        x * ∑ m ∈ range N, (m.choose n : ℝ) * x ^ m + x * ∑ m ∈ range N, (m.choose (n + 1) : ℝ) * x ^ m := by
      rw [sum_range_succ', Nat.choose_zero_succ, Nat.cast_zero, zero_mul, add_zero, mul_sum, mul_sum,
        ← sum_add_distrib]
      refine sum_congr rfl (fun m _ => ?_)
      rw [Nat.choose_succ_succ, Nat.cast_add, pow_succ]
      ring
    have hmono : ∑ m ∈ range N, (m.choose (n + 1) : ℝ) * x ^ m ≤
        ∑ m ∈ range (N + 1), (m.choose (n + 1) : ℝ) * x ^ m := by
      rw [sum_range_succ]
      have : 0 ≤ ((N.choose (n + 1) : ℕ) : ℝ) * x ^ N := by positivity
      linarith
    have hih := mul_le_mul_of_nonneg_left (ih N) hx0
    have key : (1 - x) * ∑ m ∈ range N, (m.choose (n + 1) : ℝ) * x ^ m ≤ x * (x ^ n / (1 - x) ^ (n + 1)) := by
      nlinarith [hshift, hmono, hih]
    rw [le_div_iff₀ (pow_pos h1x _)]
    calc (∑ m ∈ range N, (m.choose (n + 1) : ℝ) * x ^ m) * (1 - x) ^ (n + 1 + 1)
        = ((1 - x) * ∑ m ∈ range N, (m.choose (n + 1) : ℝ) * x ^ m) * (1 - x) ^ (n + 1) := by ring
      _ ≤ (x * (x ^ n / (1 - x) ^ (n + 1))) * (1 - x) ^ (n + 1) :=
          mul_le_mul_of_nonneg_right key (pow_nonneg h1x.le _)
      _ = x ^ (n + 1) := by
          have : (1 - x) ^ (n + 1) ≠ 0 := (pow_pos h1x _).ne'
          field_simp
          ring

/-- **Kernel gap in `ℓ₁` over all lags, for moment-matched populations.** -/
theorem p1_kc_kernel_gap_l1 {ι κι : Type*} (S : Finset ι) (T' : Finset κι) (w s : ι → ℝ) (w' s' : κι → ℝ)
    (c d W : ℝ) (n : ℕ) (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd0 : 0 < c + d) (hcd : c + d < 1)
    (hw : ∀ i ∈ S, 0 ≤ w i) (hw' : ∀ i ∈ T', 0 ≤ w' i)
    (hs : ∀ i ∈ S, |s i| ≤ 1) (hs' : ∀ i ∈ T', |s' i| ≤ 1)
    (hW : ∑ i ∈ S, w i ≤ W) (hW' : ∑ i ∈ T', w' i ≤ W)
    (hmom : ∀ j < n, mgMoment S w s j = mgMoment T' w' s' j) (N : ℕ) :
    ∑ m ∈ range N, |mgKernel S w s c d m - mgKernel T' w' s' c d m| ≤ 2 * W * d ^ n / (1 - (c + d)) ^ (n + 1) := by
  have hW0 : 0 ≤ W := le_trans (sum_nonneg hw) hW
  have hxn : (c + d) ^ n ≠ 0 := pow_ne_zero n hcd0.ne'
  have h1x : 0 < 1 - (c + d) := by linarith
  have hpt : ∀ m, |mgKernel S w s c d m - mgKernel T' w' s' c d m| ≤
      2 * W * (d ^ n / (c + d) ^ n) * ((m.choose n : ℝ) * (c + d) ^ m) := by
    intro m
    rcases Nat.lt_or_ge m n with hmn | hnm
    · rw [p1_thm_kcohort_kernel_low_orders_equal S T' w s w' s' c d n m hmom hmn, sub_self, abs_zero,
        Nat.choose_eq_zero_of_lt hmn, Nat.cast_zero]
      simp
    · refine le_trans (p1_thm_kcohort_kernel_moment_gap S T' w s w' s' c d W n m hc hd hw hw' hs hs' hW hW'
        hmom hnm) (le_of_eq ?_)
      rw [pow_sub₀ (c + d) hcd0.ne' hnm]
      field_simp
  calc ∑ m ∈ range N, |mgKernel S w s c d m - mgKernel T' w' s' c d m|
      ≤ ∑ m ∈ range N, 2 * W * (d ^ n / (c + d) ^ n) * ((m.choose n : ℝ) * (c + d) ^ m) :=
        sum_le_sum (fun m _ => hpt m)
    _ = 2 * W * (d ^ n / (c + d) ^ n) * ∑ m ∈ range N, (m.choose n : ℝ) * (c + d) ^ m := by rw [mul_sum]
    _ ≤ 2 * W * (d ^ n / (c + d) ^ n) * ((c + d) ^ n / (1 - (c + d)) ^ (n + 1)) :=
        mul_le_mul_of_nonneg_left (p1_choose_geom_sum_le (c + d) hcd0.le hcd n N) (by positivity)
    _ = 2 * W * d ^ n / (1 - (c + d)) ^ (n + 1) := by
        have : (1 - (c + d)) ^ (n + 1) ≠ 0 := (pow_pos h1x _).ne'
        field_simp

/-- **Theorem `thm:kcohort`, uniformly in the horizon.** The binomial grid pair with `K = L + 1` cohorts each, at
memory rates `c + d s` (`r_c = c`, `Δη = d`), under the paper's stability hypothesis
`|a| + |κ| W/(1 - (c + d)) ≤ s < 1`. For every number of taps `T` and every test with error probabilities
`α₀, β₀`, `4 σ² (1 - α₀ - β₀)² ≤ N (C d^(2K-1))²` with `C = 2 κ² W/((1 - (c + d))^(2K) (1 - s)²)`. -/
theorem p1_thm_kcohort_lower_bound_uniform (L : ℕ) (a κ c d W s : ℝ) (N T : ℕ)
    (q rate q' rate' : Fin (L + 1) → ℝ) (variance : NNReal) (hv : variance ≠ 0)
    (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd0 : 0 < c + d) (hcd : c + d < 1) (hW : 0 ≤ W)
    (hs : |a| + |κ| * (W / (1 - (c + d))) ≤ s) (hs1 : s < 1)
    (hr : ∀ i : Fin (L + 1), 1 - rate i = c + d * gridNode L (2 * (i : ℕ) + 1))
    (hr' : ∀ i : Fin (L + 1), 1 - rate' i = c + d * gridNode L (2 * (i : ℕ)))
    (hq : ∀ i : Fin (L + 1), q i * rate i = W * ((2 * L + 1).choose (2 * (i : ℕ) + 1) : ℝ) / 2 ^ (2 * L))
    (hq' : ∀ i : Fin (L + 1), q' i * rate' i = W * ((2 * L + 1).choose (2 * (i : ℕ)) : ℝ) / 2 ^ (2 * L))
    (α₀ β₀ : ℝ) (hab : α₀ + β₀ ≤ 1) (A : Set (ObservationRecord (N * T))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate))
      variance).real A ≤ α₀)
    (herr1 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate'))
      variance).real Aᶜ ≤ β₀) :
    4 * (variance : ℝ) * (1 - α₀ - β₀) ^ 2 ≤
      N * (2 * κ ^ 2 * W / ((1 - (c + d)) ^ (2 * L + 2) * (1 - s) ^ 2) * d ^ (2 * L + 1)) ^ 2 := by
  set w : Fin (L + 1) → ℝ := fun i => q i * rate i with hwdef
  set w' : Fin (L + 1) → ℝ := fun i => q' i * rate' i with hw'def
  set sn : Fin (L + 1) → ℝ := fun i => gridNode L (2 * (i : ℕ) + 1) with hsndef
  set sn' : Fin (L + 1) → ℝ := fun i => gridNode L (2 * (i : ℕ)) with hsn'def
  obtain ⟨hmA, hmB⟩ := p1_gm_pair_mass L W
  have hw : ∀ i, 0 ≤ w i := fun i => by simp only [w]; rw [hq i]; positivity
  have hw' : ∀ i, 0 ≤ w' i := fun i => by simp only [w']; rw [hq' i]; positivity
  have hsumE : ∑ i, w i = W := by simp only [w, hq]; exact hmA
  have hsumE' : ∑ i, w' i = W := by simp only [w', hq']; exact hmB
  have hsn : ∀ i, |sn i| ≤ 1 := fun i => p1_gridNode_abs_le L _ (by omega)
  have hsn' : ∀ i, |sn' i| ≤ 1 := fun i => p1_gridNode_abs_le L _ (by omega)
  have hmom : ∀ j < 2 * L + 1, mgMoment univ w sn j = mgMoment univ w' sn' j := by
    intro j hj
    simp only [mgMoment, w, w', sn, sn', hq, hq']
    exact p1_gm_pair_moments L W j hj
  have hk : ∀ m, cohortKernel q rate m = mgKernel univ w sn c d m := fun m =>
    p1_cohortKernel_eq_mgKernel q rate sn c d hr m
  have hk' : ∀ m, cohortKernel q' rate' m = mgKernel univ w' sn' c d m := fun m =>
    p1_cohortKernel_eq_mgKernel q' rate' sn' c d hr' m
  set K1 := W / (1 - (c + d)) with hK1def
  have hK1 : ∀ n, ∑ m ∈ range n, |cohortKernel q rate m| ≤ K1 := fun n => by
    simp only [hk, mgKernel]
    exact p1_population_kernel_l1 w sn c d W hc hd hcd hw hsumE.le hsn n
  have hK1' : ∀ n, ∑ m ∈ range n, |cohortKernel q' rate' m| ≤ K1 := fun n => by
    simp only [hk', mgKernel]
    exact p1_population_kernel_l1 w' sn' c d W hc hd hcd hw' hsumE'.le hsn' n
  set E := 2 * W * d ^ (2 * L + 1) / (1 - (c + d)) ^ (2 * L + 1 + 1) with hEdef
  have hE : ∀ n, ∑ m ∈ range n, |cohortKernel q rate m - cohortKernel q' rate' m| ≤ E := fun n => by
    simp only [hk, hk']
    exact p1_kc_kernel_gap_l1 univ univ w sn w' sn' c d W (2 * L + 1) hc hd hcd0 hcd (fun i _ => hw i)
      (fun i _ => hw' i) (fun i _ => hsn i) (fun i _ => hsn' i) hsumE.le hsumE'.le hmom n
  have hH1 := p1_response_l1 a κ K1 s (cohortKernel q' rate') _ (p1_impulse_zero a κ q' rate')
    (p1_impulse_closed_loop_recursion a κ q' rate') hK1' hs hs1
  have hD := p1_response_diff_l1 a κ K1 s E (|κ| / (1 - s)) (cohortKernel q rate) (cohortKernel q' rate') _ _
    (p1_impulse_zero a κ _ _) (p1_impulse_zero a κ _ _)
    (p1_impulse_closed_loop_recursion a κ _ _) (p1_impulse_closed_loop_recursion a κ _ _)
    hK1 hs hs1 hE hH1
  have h1s : 0 < 1 - s := by linarith
  have h1x : 0 < 1 - (c + d) := by linarith
  have hne1 : 1 - s ≠ 0 := h1s.ne'
  have hne2 : 1 - (c + d) ≠ 0 := h1x.ne'
  have hDval : |κ| * E * (|κ| / (1 - s)) / (1 - s) =
      2 * κ ^ 2 * W / ((1 - (c + d)) ^ (2 * L + 2) * (1 - s) ^ 2) * d ^ (2 * L + 1) := by
    rw [hEdef, ← sq_abs κ]
    first
    | (field_simp; done)
    | (field_simp; ring)
  set hIA := actualCohortImpulse a κ q rate
  set hIB := actualCohortImpulse a κ q' rate'
  have hsq : ∑ t ∈ range T, (hIA t - hIB t) ^ 2 ≤
      (2 * κ ^ 2 * W / ((1 - (c + d)) ^ (2 * L + 2) * (1 - s) ^ 2) * d ^ (2 * L + 1)) ^ 2 := by
    refine (p1_sq_sum_le_sq_abs_sum _ _).trans (pow_le_pow_left₀ (sum_nonneg (fun _ _ => abs_nonneg _)) ?_ 2)
    have := hD T
    rwa [hDval] at this
  have htest := p1_test_error_kl_lower_bound_general _ _ hA α₀ β₀ hab herr0 herr1
  rw [p1_repeated_record_kl N T hIA hIB variance hv] at htest
  have hvpos : 0 < (variance : ℝ) := by positivity
  have hle := (ENNReal.ofReal_le_ofReal_iff (by positivity)).mp htest
  rw [le_div_iff₀ (by positivity)] at hle
  have hN : (0 : ℝ) ≤ N := Nat.cast_nonneg N
  nlinarith [mul_le_mul_of_nonneg_left hsq hN]

end CurrentMM
