import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Nat.Choose.Sum
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.IntervalCases
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/-!
# Paper 1, Theorem S28.2(i): the Gauss and Gauss–Radau kernels differ by `O(d³)`

On rates `c + d s`, the two-point Gauss rule (weights `W/2, W/2`, nodes `±σ`, `σ² = 1/3`) and the two-point
Gauss–Radau rule (weights `W/4, 3W/4`, nodes `-1, 1/3`) give kernels
`k^G_m = (W/2)(c + dσ)^m + (W/2)(c - dσ)^m` and `k^R_m = (W/4)(c - d)^m + (3W/4)(c + d/3)^m`.

* `p1_halt_moment_gap_le`: if two families of moments `M k`, `N k` agree for `k ≤ 2` and both are bounded by `W` in
  absolute value, then for every `m ≥ 3`,
  `|Σ_k C(m,k) c^{m-k} d^k (M k - N k)| ≤ 2 W C(m,3) |d|³ (|c| + |d|)^{m-3}`.
* `p1_halt_kernel_bound`: the kernel gap is that sum for the two rules, so
  `|k^G_m - k^R_m| ≤ 2 W C(m,3) |d|³ (|c| + |d|)^{m-3}`.
-/

namespace CurrentMM

open Finset

/-- `C(m,k) ≤ C(m,3) C(m-3,k-3)` for `3 ≤ k ≤ m`. -/
lemma p1_choose_le_mul (m k : ℕ) (hk : 3 ≤ k) (hkm : k ≤ m) :
    (m.choose k : ℝ) ≤ (m.choose 3 : ℝ) * ((m - 3).choose (k - 3) : ℝ) := by
  have h : m.choose k * k.choose 3 = m.choose 3 * (m - 3).choose (k - 3) := by
    first | exact Nat.choose_mul (n := m) hk | exact Nat.choose_mul hkm hk
  have hpos : 1 ≤ k.choose 3 := Nat.one_le_iff_ne_zero.mpr (Nat.choose_pos hk).ne'
  have : m.choose k ≤ m.choose 3 * (m - 3).choose (k - 3) := by
    calc m.choose k = m.choose k * 1 := (mul_one _).symm
      _ ≤ m.choose k * k.choose 3 := Nat.mul_le_mul_left _ hpos
      _ = m.choose 3 * (m - 3).choose (k - 3) := h
  exact_mod_cast this

/-- The tail of the binomial expansion from `k = 3` is at most `C(m,3) b³ (a + b)^{m-3}` for `a, b ≥ 0`. -/
lemma p1_binom_tail_le (a b : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b) (m : ℕ) (hm : 3 ≤ m) :
    ∑ k ∈ (range (m + 1)).filter (fun k => 3 ≤ k), (m.choose k : ℝ) * a ^ (m - k) * b ^ k
      ≤ (m.choose 3 : ℝ) * b ^ 3 * (a + b) ^ (m - 3) := by
  obtain ⟨n, rfl⟩ : ∃ n, m = n + 3 := ⟨m - 3, by omega⟩
  have hexp : (a + b) ^ n = ∑ j ∈ range (n + 1), (n.choose j : ℝ) * a ^ (n - j) * b ^ j := by
    rw [add_comm, add_pow]; exact sum_congr rfl fun j _ => by ring
  have hshift : ∑ k ∈ (range (n + 3 + 1)).filter (fun k => 3 ≤ k), ((n + 3).choose k : ℝ) * a ^ (n + 3 - k) * b ^ k
      = ∑ j ∈ range (n + 1), ((n + 3).choose (j + 3) : ℝ) * a ^ (n - j) * b ^ (j + 3) := by
    symm
    apply sum_nbij' (fun j => j + 3) (fun k => k - 3)
    · intro j hj; simp only [mem_filter, mem_range] at hj ⊢; omega
    · intro k hk; simp only [mem_filter, mem_range] at hk ⊢; omega
    · intro j _; simp
    · intro k hk; simp only [mem_filter, mem_range] at hk; omega
    · intro j hj
      simp only [mem_range] at hj
      have : n + 3 - (j + 3) = n - j := by omega
      rw [this]
  rw [hshift]
  calc ∑ j ∈ range (n + 1), ((n + 3).choose (j + 3) : ℝ) * a ^ (n - j) * b ^ (j + 3)
      ≤ ∑ j ∈ range (n + 1), ((n + 3).choose 3 : ℝ) * (n.choose j : ℝ) * a ^ (n - j) * b ^ (j + 3) := by
        apply sum_le_sum
        intro j hj
        simp only [mem_range] at hj
        have hc := p1_choose_le_mul (n + 3) (j + 3) (by omega) (by omega)
        have e1 : n + 3 - 3 = n := by omega
        have e2 : j + 3 - 3 = j := by omega
        rw [e1, e2] at hc
        have hab : 0 ≤ a ^ (n - j) * b ^ (j + 3) := by positivity
        nlinarith [mul_le_mul_of_nonneg_right hc hab]
    _ = ((n + 3).choose 3 : ℝ) * b ^ 3 * ∑ j ∈ range (n + 1), (n.choose j : ℝ) * a ^ (n - j) * b ^ j := by
        rw [mul_sum]; exact sum_congr rfl fun j _ => by ring
    _ = ((n + 3).choose 3 : ℝ) * b ^ 3 * (a + b) ^ (n + 3 - 3) := by
        rw [show n + 3 - 3 = n by omega, hexp]

/-- **Moment-gap bound.** Moments that agree up to order 2 and are bounded by `W` give the stated bound. -/
theorem p1_halt_moment_gap_le (W c d : ℝ) (M N : ℕ → ℝ) (m : ℕ) (hm : 3 ≤ m)
    (hagree : ∀ k, k ≤ 2 → M k = N k) (hM : ∀ k, |M k| ≤ W) (hN : ∀ k, |N k| ≤ W) :
    |∑ k ∈ range (m + 1), (m.choose k : ℝ) * c ^ (m - k) * d ^ k * (M k - N k)|
      ≤ 2 * W * (m.choose 3 : ℝ) * |d| ^ 3 * (|c| + |d|) ^ (m - 3) := by
  have hsplit : ∑ k ∈ range (m + 1), (m.choose k : ℝ) * c ^ (m - k) * d ^ k * (M k - N k)
      = ∑ k ∈ (range (m + 1)).filter (fun k => 3 ≤ k), (m.choose k : ℝ) * c ^ (m - k) * d ^ k * (M k - N k) := by
    rw [sum_filter]
    apply sum_congr rfl
    intro k _
    split_ifs with h
    · rfl
    · rw [hagree k (by omega), sub_self, mul_zero]
  rw [hsplit]
  have hW : 0 ≤ W := le_trans (abs_nonneg _) (hM 0)
  calc |∑ k ∈ (range (m + 1)).filter (fun k => 3 ≤ k), (m.choose k : ℝ) * c ^ (m - k) * d ^ k * (M k - N k)|
      ≤ ∑ k ∈ (range (m + 1)).filter (fun k => 3 ≤ k), |(m.choose k : ℝ) * c ^ (m - k) * d ^ k * (M k - N k)| :=
        abs_sum_le_sum_abs _ _
    _ ≤ ∑ k ∈ (range (m + 1)).filter (fun k => 3 ≤ k), 2 * W * ((m.choose k : ℝ) * |c| ^ (m - k) * |d| ^ k) := by
        apply sum_le_sum
        intro k _
        have hMN : |M k - N k| ≤ 2 * W := by
          have := abs_sub (M k) (N k); linarith [hM k, hN k]
        rw [abs_mul, abs_mul, abs_mul, abs_pow, abs_pow, Nat.abs_cast]
        have hnn : 0 ≤ (m.choose k : ℝ) * |c| ^ (m - k) * |d| ^ k := by positivity
        nlinarith [mul_le_mul_of_nonneg_left hMN hnn]
    _ = 2 * W * ∑ k ∈ (range (m + 1)).filter (fun k => 3 ≤ k), (m.choose k : ℝ) * |c| ^ (m - k) * |d| ^ k := by
        rw [mul_sum]
    _ ≤ 2 * W * ((m.choose 3 : ℝ) * |d| ^ 3 * (|c| + |d|) ^ (m - 3)) := by
        apply mul_le_mul_of_nonneg_left (p1_binom_tail_le |c| |d| (abs_nonneg _) (abs_nonneg _) m hm)
        linarith
    _ = 2 * W * (m.choose 3 : ℝ) * |d| ^ 3 * (|c| + |d|) ^ (m - 3) := by ring

/-- The kernel of a two-point rule on rates `c + d s`, expanded binomially in the moments of the rule. -/
lemma p1_two_point_kernel_expand (c d p q s t : ℝ) (m : ℕ) :
    p * (c + d * s) ^ m + q * (c + d * t) ^ m
      = ∑ k ∈ range (m + 1), (m.choose k : ℝ) * c ^ (m - k) * d ^ k * (p * s ^ k + q * t ^ k) := by
  rw [show c + d * s = d * s + c by ring, show c + d * t = d * t + c by ring, add_pow, add_pow, mul_sum, mul_sum,
    ← sum_add_distrib]
  exact sum_congr rfl fun k _ => by ring

/-- **Theorem S28.2(i).** The Gauss and Gauss–Radau kernels differ by at most `2 W C(m,3) |d|³ (|c|+|d|)^{m-3}`. -/
theorem p1_halt_kernel_bound (W c d σ : ℝ) (hW : 0 ≤ W) (hσ : σ ^ 2 = 1 / 3) (hσ0 : 0 ≤ σ) (m : ℕ) (hm : 3 ≤ m) :
    |(W / 2 * (c + d * σ) ^ m + W / 2 * (c + d * (-σ)) ^ m) - (W / 4 * (c + d * (-1)) ^ m + 3 * W / 4 * (c + d * (1 / 3)) ^ m)|
      ≤ 2 * W * (m.choose 3 : ℝ) * |d| ^ 3 * (|c| + |d|) ^ (m - 3) := by
  have hσ1 : σ ≤ 1 := by nlinarith
  rw [p1_two_point_kernel_expand, p1_two_point_kernel_expand, ← sum_sub_distrib]
  have e : ∀ k ∈ range (m + 1),
      (m.choose k : ℝ) * c ^ (m - k) * d ^ k * (W / 2 * σ ^ k + W / 2 * (-σ) ^ k)
        - (m.choose k : ℝ) * c ^ (m - k) * d ^ k * (W / 4 * (-1) ^ k + 3 * W / 4 * (1 / 3) ^ k)
      = (m.choose k : ℝ) * c ^ (m - k) * d ^ k
        * ((W / 2 * σ ^ k + W / 2 * (-σ) ^ k) - (W / 4 * (-1) ^ k + 3 * W / 4 * (1 / 3) ^ k)) := by
    intro k _; ring
  rw [sum_congr rfl e]
  apply p1_halt_moment_gap_le W c d (fun k => W / 2 * σ ^ k + W / 2 * (-σ) ^ k)
    (fun k => W / 4 * (-1) ^ k + 3 * W / 4 * (1 / 3) ^ k) m hm
  · intro k hk
    interval_cases k
    · norm_num; ring
    · norm_num; ring
    · simp only [neg_sq]; rw [hσ]; ring
  · intro k
    have h1 : |σ ^ k| ≤ 1 := by rw [abs_pow, abs_of_nonneg hσ0]; exact pow_le_one₀ hσ0 hσ1
    have h2 : |(-σ) ^ k| ≤ 1 := by rw [abs_pow, abs_neg, abs_of_nonneg hσ0]; exact pow_le_one₀ hσ0 hσ1
    calc |W / 2 * σ ^ k + W / 2 * (-σ) ^ k| ≤ |W / 2 * σ ^ k| + |W / 2 * (-σ) ^ k| := abs_add_le _ _
      _ = W / 2 * |σ ^ k| + W / 2 * |(-σ) ^ k| := by rw [abs_mul, abs_mul, abs_of_nonneg (by linarith : 0 ≤ W / 2)]
      _ ≤ W / 2 * 1 + W / 2 * 1 := by gcongr
      _ = W := by ring
  · intro k
    have h1 : |((-1 : ℝ)) ^ k| ≤ 1 := by rw [abs_pow, abs_neg, abs_one, one_pow]
    have h2 : |((1 / 3 : ℝ)) ^ k| ≤ 1 := by
      rw [abs_pow, abs_of_nonneg (by norm_num : (0 : ℝ) ≤ 1 / 3)]; exact pow_le_one₀ (by norm_num) (by norm_num)
    calc |W / 4 * (-1) ^ k + 3 * W / 4 * (1 / 3) ^ k| ≤ |W / 4 * (-1) ^ k| + |3 * W / 4 * (1 / 3) ^ k| := abs_add_le _ _
      _ = W / 4 * |((-1 : ℝ)) ^ k| + 3 * W / 4 * |((1 / 3 : ℝ)) ^ k| := by
          rw [abs_mul, abs_mul, abs_of_nonneg (by linarith : 0 ≤ W / 4), abs_of_nonneg (by linarith : 0 ≤ 3 * W / 4)]
      _ ≤ W / 4 * 1 + 3 * W / 4 * 1 := by gcongr
      _ = W := by ring

end CurrentMM
