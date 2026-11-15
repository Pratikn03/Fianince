import CurrentProofs.Paper1GeneralLevel

/-!
# Paper 1: the pooling-markets lower bound on joint records (core `thm:pool`(i))

`D` markets, each with its own persistence `a j`, impact `κ j` and kernel. The record of one experiment is the
concatenation of the `D` price impulse responses, `T` dates each. If, in every market, the two economies' node moments
agree below order `n` (the same memory nodes in all markets, market-specific weights), then any test with errors
`α₀, β₀` satisfies `4σ²(1 - α₀ - β₀)² ≤ N D T (max_j ε C_{T,j})²` with `ε = 2 W 2^T d^n`, so `N ≥ c d^(-2n)`.
With `n = l* = K - 1 + ⌈K/D⌉` this is the lower bound of the theorem. The existence of such matched pairs near
generic configurations (the constant-rank step) is proved on paper; the counting that makes it possible is
`p1_pool_rows_lt`.
-/

namespace CurrentMM

open Finset MeasureTheory ProbabilityTheory InformationTheory Real
open scoped ENNReal NNReal

/-- Concatenated record mean of `D` markets, `T` dates each: date `t` belongs to market `t / T`. -/
def multiMean (T : ℕ) (h : ℕ → ℕ → ℝ) (t : ℕ) : ℝ := h (t / T) (t % T)

theorem p1_pool_lower_bound_joint (D N T : ℕ) (a κ B H ε : ℕ → ℝ) (C : ℝ)
    (k k' h h' : ℕ → ℕ → ℝ) (variance : ℝ≥0) (hv : variance ≠ 0) (hT : 0 < T)
    (hB : ∀ j, 0 ≤ B j) (hH : ∀ j, 0 ≤ H j) (hε : ∀ j, 0 ≤ ε j)
    (h0 : ∀ j, h j 0 = κ j) (h0' : ∀ j, h' j 0 = κ j)
    (hrec : ∀ j t, h j (t + 1) = a j * h j t + κ j * ∑ i ∈ range (t + 1), k j i * h j (t - i))
    (hrec' : ∀ j t, h' j (t + 1) = a j * h' j t + κ j * ∑ i ∈ range (t + 1), k' j i * h' j (t - i))
    (hkB : ∀ j i, |k j i| ≤ B j) (hh' : ∀ j s, s < T → |h' j s| ≤ H j)
    (hgap : ∀ j i, i < T → |k j i - k' j i| ≤ ε j)
    (hC : ∀ j, j < D → ε j * p1GapConst (a j) |κ j| (B j) (H j) T ≤ C)
    (α₀ β₀ : ℝ) (hab : α₀ + β₀ ≤ 1) (A : Set (ObservationRecord (N * (D * T)))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * (D * T)) (p1RepeatedMean N (D * T) (multiMean T h)) variance).real A ≤ α₀)
    (herr1 : (gaussianRecordLaw (N * (D * T)) (p1RepeatedMean N (D * T) (multiMean T h')) variance).real Aᶜ ≤ β₀) :
    4 * (variance : ℝ) * (1 - α₀ - β₀) ^ 2 ≤ N * (D * T) * C ^ 2 := by
  have hvpos : 0 < (variance : ℝ) := by positivity
  have htest := p1_test_error_kl_lower_bound_general _ _ hA α₀ β₀ hab herr0 herr1
  rw [p1_repeated_record_kl N (D * T) _ _ variance hv] at htest
  have hmono : ∀ j u v, u ≤ v → p1GapConst (a j) |κ j| (B j) (H j) u ≤ p1GapConst (a j) |κ j| (B j) (H j) v := by
    intro j u v huv
    induction v with
    | zero => have : u = 0 := by omega
              subst this; exact le_rfl
    | succ v ihv =>
      rcases Nat.lt_or_ge u (v + 1) with h1 | h1
      · exact le_trans (ihv (by omega)) (p1GapConst_mono (a j) |κ j| (B j) (H j) (abs_nonneg _) (hB j) (hH j) v)
      · have : u = v + 1 := by omega
        subst this; exact le_rfl
  have hpt : ∀ t, t < D * T → (multiMean T h t - multiMean T h' t) ^ 2 ≤ C ^ 2 := by
    intro t ht
    have hj : t / T < D := by rw [Nat.div_lt_iff_lt_mul hT]; linarith [Nat.mul_comm D T]
    have hu : t % T < T := Nat.mod_lt _ hT
    set j := t / T
    have hg := p1_impulse_gap_finite_horizon (a j) (κ j) (B j) (H j) (ε j) (k j) (k' j) (h j) (h' j) T (hB j) (hH j)
      (hε j) (h0 j) (h0' j) (hrec j) (hrec' j) (hkB j) (hh' j) (hgap j) (t % T) hu
    have h1 : |multiMean T h t - multiMean T h' t| ≤ C := by
      unfold multiMean
      exact le_trans hg (le_trans (mul_le_mul_of_nonneg_left (hmono j _ _ hu.le) (hε j)) (hC j hj))
    rw [← sq_abs]
    have hC0 : 0 ≤ C := le_trans (abs_nonneg _) h1
    exact pow_le_pow_left₀ (abs_nonneg _) h1 2
  have hsq : ∑ t ∈ range (D * T), (multiMean T h t - multiMean T h' t) ^ 2 ≤ (D * T : ℕ) * C ^ 2 := by
    calc _ ≤ ∑ t ∈ range (D * T), C ^ 2 := sum_le_sum (fun t ht => hpt t (mem_range.mp ht))
      _ = _ := by rw [sum_const, card_range, nsmul_eq_mul]
  have hle := (ENNReal.ofReal_le_ofReal_iff (by positivity)).mp htest
  rw [le_div_iff₀ (by positivity)] at hle
  have hN : (0 : ℝ) ≤ N := Nat.cast_nonneg N
  push_cast at hsq ⊢
  nlinarith [mul_le_mul_of_nonneg_left hsq hN]

/-- **Pooling markets, matched pair.** Same memory nodes `s` (resp. `s'`) in every market, market-specific weights
`w j` (resp. `w' j`), node moments agreeing below order `n` in every market. -/
theorem p1_pool_lower_bound_matched {ι ι' : Type*} (S : Finset ι) (S' : Finset ι')
    (w : ℕ → ι → ℝ) (s : ι → ℝ) (w' : ℕ → ι' → ℝ) (s' : ι' → ℝ)
    (D N T n : ℕ) (a κ B H : ℕ → ℝ) (c d W C : ℝ)
    (k k' h h' : ℕ → ℕ → ℝ) (variance : ℝ≥0) (hv : variance ≠ 0) (hT : 0 < T)
    (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd : c + d ≤ 1)
    (hw : ∀ j, ∀ i ∈ S, 0 ≤ w j i) (hw' : ∀ j, ∀ i ∈ S', 0 ≤ w' j i)
    (hs : ∀ i ∈ S, |s i| ≤ 1) (hs' : ∀ i ∈ S', |s' i| ≤ 1)
    (hW : ∀ j, ∑ i ∈ S, w j i ≤ W) (hW' : ∀ j, ∑ i ∈ S', w' j i ≤ W)
    (hmom : ∀ j, ∀ l < n, mgMoment S (w j) s l = mgMoment S' (w' j) s' l)
    (hk : ∀ j m, k j m = mgKernel S (w j) s c d m) (hk' : ∀ j m, k' j m = mgKernel S' (w' j) s' c d m)
    (hB : ∀ j, 0 ≤ B j) (hH : ∀ j, 0 ≤ H j)
    (h0 : ∀ j, h j 0 = κ j) (h0' : ∀ j, h' j 0 = κ j)
    (hrec : ∀ j t, h j (t + 1) = a j * h j t + κ j * ∑ i ∈ range (t + 1), k j i * h j (t - i))
    (hrec' : ∀ j t, h' j (t + 1) = a j * h' j t + κ j * ∑ i ∈ range (t + 1), k' j i * h' j (t - i))
    (hkB : ∀ j i, |k j i| ≤ B j) (hh' : ∀ j s, s < T → |h' j s| ≤ H j)
    (hC : ∀ j, j < D → (2 * W * 2 ^ T * d ^ n) * p1GapConst (a j) |κ j| (B j) (H j) T ≤ C)
    (α₀ β₀ : ℝ) (hab : α₀ + β₀ ≤ 1) (A : Set (ObservationRecord (N * (D * T)))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * (D * T)) (p1RepeatedMean N (D * T) (multiMean T h)) variance).real A ≤ α₀)
    (herr1 : (gaussianRecordLaw (N * (D * T)) (p1RepeatedMean N (D * T) (multiMean T h')) variance).real Aᶜ ≤ β₀) :
    4 * (variance : ℝ) * (1 - α₀ - β₀) ^ 2 ≤ N * (D * T) * C ^ 2 := by
  have hW0 : 0 ≤ W := le_trans (sum_nonneg (hw 0)) (hW 0)
  refine p1_pool_lower_bound_joint D N T a κ B H (fun _ => 2 * W * 2 ^ T * d ^ n) C k k' h h' variance hv hT hB hH
    (fun _ => by positivity) h0 h0' hrec hrec' hkB hh' (fun j i hi => ?_) hC α₀ β₀ hab A hA herr0 herr1
  rw [hk j i, hk' j i]
  exact p1_mg_kernel_gap_uniform S S' (w j) s (w' j) s' c d W n T hc hd hcd (hw j) (hw' j) hs hs' (hW j) (hW' j)
    (hmom j) i hi

/-- **An explicit matched pair for two algorithms in two markets.** Nodes `(-1, 1)` with market weights
`(1/2, 1/2)` and `(7/10, 3/10)`, against nodes `(-1/2, 1)` with weights `(2/3, 1/3)` and `(14/15, 1/15)`: in both
markets the moments of order 0 and 1 agree and those of order 2 differ, so `n = l* = 2` and `N ≥ c d^-4`
(against `d^-6` for the hardest one-market pair). -/
theorem p1_pool_explicit_pair_K2D2 :
    (1/2 : ℝ) + 1/2 = 2/3 + 1/3 ∧ (1/2 : ℝ) * (-1) + 1/2 * 1 = 2/3 * (-1/2) + 1/3 * 1 ∧
    (7/10 : ℝ) + 3/10 = 14/15 + 1/15 ∧ (7/10 : ℝ) * (-1) + 3/10 * 1 = 14/15 * (-1/2) + 1/15 * 1 ∧
    (1/2 : ℝ) * (-1) ^ 2 + 1/2 * 1 ^ 2 ≠ 2/3 * (-1/2) ^ 2 + 1/3 * 1 ^ 2 ∧
    (7/10 : ℝ) * (-1) ^ 2 + 3/10 * 1 ^ 2 ≠ 14/15 * (-1/2) ^ 2 + 1/15 * 1 ^ 2 := by
  norm_num

end CurrentMM
