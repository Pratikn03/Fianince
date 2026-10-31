import Mathlib.Data.Nat.Choose.Sum
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring
import Mathlib.Tactic.GCongr

/-!
# Paper 1, Theorem `thm:kcohort`: the deterministic core of the K-cohort lower bound

Two cohort populations with rates `c + d * s_i` (`d` is the spacing `Δη`, the nodes `s_i` lie in `[-1, 1]`)
whose weighted node moments agree up to order `n - 1` have kernel values `k_m = ∑ w_i (c + d s_i)^m` that differ
by at most `2 W · C(m, n) · d^n · (c + d)^(m - n)`. With `n = 2K - 1` (the Gauss and Gauss–Radau rules agree on
all moments of order at most `2K - 2`), every kernel value differs by `O(Δη^(2K-1))`, which is the moment-gap step
of the lower bound. What is *not* proved here: that the K-point Gauss and Gauss–Radau rules match moments up to
order `2K - 2` (a classical quadrature fact, taken as the hypothesis `hmom`), the passage from kernel values to the
closed-loop impulse response, and the Le Cam two-point step; those remain on paper.
-/

namespace CurrentMM

open Finset

/-- Kernel value `k_m = ∑_i w_i (c + d s_i)^m` of a finite cohort population. -/
def mgKernel {ι : Type*} (S : Finset ι) (w s : ι → ℝ) (c d : ℝ) (m : ℕ) : ℝ :=
  ∑ i ∈ S, w i * (c + d * s i) ^ m

/-- Weighted node moment `∑_i w_i s_i^j`. -/
def mgMoment {ι : Type*} (S : Finset ι) (w s : ι → ℝ) (j : ℕ) : ℝ :=
  ∑ i ∈ S, w i * s i ^ j

/-- Binomial expansion of a kernel value in the node moments. -/
theorem p1_mg_kernel_expand {ι : Type*} (S : Finset ι) (w s : ι → ℝ) (c d : ℝ) (m : ℕ) :
    mgKernel S w s c d m =
      ∑ j ∈ range (m + 1), (m.choose j : ℝ) * c ^ (m - j) * d ^ j * mgMoment S w s j := by
  unfold mgKernel mgMoment
  have h : ∀ i ∈ S, w i * (c + d * s i) ^ m =
      ∑ j ∈ range (m + 1), (m.choose j : ℝ) * c ^ (m - j) * d ^ j * (w i * s i ^ j) := by
    intro i _
    rw [add_comm c, add_pow, mul_sum]
    refine sum_congr rfl (fun j _ => ?_)
    rw [mul_pow]; ring
  rw [sum_congr rfl h, sum_comm]
  refine sum_congr rfl (fun j _ => ?_)
  rw [mul_sum]

/-- A weighted moment of nodes in `[-1, 1]` is bounded by the total weight. -/
theorem p1_mg_moment_abs_le {ι : Type*} (S : Finset ι) (w s : ι → ℝ) (W : ℝ) (j : ℕ)
    (hw : ∀ i ∈ S, 0 ≤ w i) (hs : ∀ i ∈ S, |s i| ≤ 1) (hW : ∑ i ∈ S, w i ≤ W) :
    |mgMoment S w s j| ≤ W := by
  unfold mgMoment
  calc |∑ i ∈ S, w i * s i ^ j| ≤ ∑ i ∈ S, |w i * s i ^ j| := abs_sum_le_sum_abs _ _
    _ ≤ ∑ i ∈ S, w i := by
        refine sum_le_sum (fun i hi => ?_)
        rw [abs_mul, abs_of_nonneg (hw i hi), abs_pow]
        have h1 : |s i| ^ j ≤ 1 := pow_le_one₀ (abs_nonneg _) (hs i hi)
        nlinarith [hw i hi]
    _ ≤ W := hW

/-- Tail of the binomial sum: `∑_{j=n}^{m} C(m,j) c^(m-j) d^j ≤ C(m,n) d^n (c+d)^(m-n)`. -/
theorem p1_mg_binomial_tail (c d : ℝ) (hc : 0 ≤ c) (hd : 0 ≤ d) (n m : ℕ) (hnm : n ≤ m) :
    ∑ j ∈ Ico n (m + 1), (m.choose j : ℝ) * c ^ (m - j) * d ^ j ≤
      (m.choose n : ℝ) * d ^ n * (c + d) ^ (m - n) := by
  rw [sum_Ico_eq_sum_range]
  have hlen : m + 1 - n = (m - n) + 1 := by omega
  rw [hlen, add_comm c d, add_pow, mul_sum]
  refine sum_le_sum (fun i hi => ?_)
  have hi' : i ≤ m - n := by simpa [Nat.lt_succ_iff] using hi
  have hch : (m.choose (n + i) : ℝ) ≤ (m.choose n : ℝ) * ((m - n).choose i : ℝ) := by
    have key := Nat.choose_mul (n := m) (k := n + i) (s := n) (by omega)
    have hpos : 1 ≤ (n + i).choose n := Nat.choose_pos (by omega)
    have : m.choose (n + i) ≤ m.choose n * (m - n).choose i := by
      have e : n + i - n = i := by omega
      rw [e] at key
      calc m.choose (n + i) = m.choose (n + i) * 1 := (mul_one _).symm
        _ ≤ m.choose (n + i) * (n + i).choose n := Nat.mul_le_mul_left _ hpos
        _ = m.choose n * (m - n).choose i := key
    exact_mod_cast this
  have e1 : m - (n + i) = m - n - i := by omega
  rw [e1, pow_add]
  have hp1 : 0 ≤ c ^ (m - n - i) := pow_nonneg hc _
  have hp2 : 0 ≤ d ^ n := pow_nonneg hd _
  have hp3 : 0 ≤ d ^ i := pow_nonneg hd _
  have hprod : 0 ≤ c ^ (m - n - i) * (d ^ n * d ^ i) := by positivity
  calc (m.choose (n + i) : ℝ) * c ^ (m - n - i) * (d ^ n * d ^ i)
      = (m.choose (n + i) : ℝ) * (c ^ (m - n - i) * (d ^ n * d ^ i)) := by ring
    _ ≤ ((m.choose n : ℝ) * ((m - n).choose i : ℝ)) * (c ^ (m - n - i) * (d ^ n * d ^ i)) :=
        mul_le_mul_of_nonneg_right hch hprod
    _ = (m.choose n : ℝ) * d ^ n * (d ^ i * c ^ (m - n - i) * ((m - n).choose i : ℝ)) := by ring

/-- **Moment-gap bound** (deterministic core of `thm:kcohort`). If two cohort populations with nodes in `[-1,1]`,
nonnegative weights of total at most `W`, and rates `c + d s` agree on all weighted node moments of order `< n`,
then for every `m ≥ n` their kernel values differ by at most `2 W C(m,n) d^n (c+d)^(m-n)`. -/
theorem p1_thm_kcohort_kernel_moment_gap {ι κ : Type*} (S : Finset ι) (T : Finset κ)
    (w s : ι → ℝ) (w' s' : κ → ℝ) (c d W : ℝ) (n m : ℕ)
    (hc : 0 ≤ c) (hd : 0 ≤ d)
    (hw : ∀ i ∈ S, 0 ≤ w i) (hw' : ∀ i ∈ T, 0 ≤ w' i)
    (hs : ∀ i ∈ S, |s i| ≤ 1) (hs' : ∀ i ∈ T, |s' i| ≤ 1)
    (hW : ∑ i ∈ S, w i ≤ W) (hW' : ∑ i ∈ T, w' i ≤ W)
    (hmom : ∀ j < n, mgMoment S w s j = mgMoment T w' s' j) (hnm : n ≤ m) :
    |mgKernel S w s c d m - mgKernel T w' s' c d m| ≤
      2 * W * ((m.choose n : ℝ) * d ^ n * (c + d) ^ (m - n)) := by
  rw [p1_mg_kernel_expand, p1_mg_kernel_expand, ← sum_sub_distrib]
  have hsplit := sum_range_add_sum_Ico
    (fun j => (m.choose j : ℝ) * c ^ (m - j) * d ^ j * mgMoment S w s j -
      (m.choose j : ℝ) * c ^ (m - j) * d ^ j * mgMoment T w' s' j) (show n ≤ m + 1 by omega)
  rw [← hsplit]
  have hzero : ∑ j ∈ range n, ((m.choose j : ℝ) * c ^ (m - j) * d ^ j * mgMoment S w s j -
      (m.choose j : ℝ) * c ^ (m - j) * d ^ j * mgMoment T w' s' j) = 0 := by
    refine sum_eq_zero (fun j hj => ?_)
    rw [hmom j (mem_range.mp hj)]; ring
  rw [hzero, zero_add]
  have hW0 : 0 ≤ W := le_trans (sum_nonneg hw) hW
  calc |∑ j ∈ Ico n (m + 1), ((m.choose j : ℝ) * c ^ (m - j) * d ^ j * mgMoment S w s j -
        (m.choose j : ℝ) * c ^ (m - j) * d ^ j * mgMoment T w' s' j)|
      ≤ ∑ j ∈ Ico n (m + 1), |(m.choose j : ℝ) * c ^ (m - j) * d ^ j * mgMoment S w s j -
        (m.choose j : ℝ) * c ^ (m - j) * d ^ j * mgMoment T w' s' j| := abs_sum_le_sum_abs _ _
    _ ≤ ∑ j ∈ Ico n (m + 1), (m.choose j : ℝ) * c ^ (m - j) * d ^ j * (2 * W) := by
        refine sum_le_sum (fun j _ => ?_)
        have hA := p1_mg_moment_abs_le S w s W j hw hs hW
        have hB := p1_mg_moment_abs_le T w' s' W j hw' hs' hW'
        have hcoef : 0 ≤ (m.choose j : ℝ) * c ^ (m - j) * d ^ j := by positivity
        rw [← mul_sub, abs_mul, abs_of_nonneg hcoef]
        refine mul_le_mul_of_nonneg_left ?_ hcoef
        calc |mgMoment S w s j - mgMoment T w' s' j|
            ≤ |mgMoment S w s j| + |mgMoment T w' s' j| := abs_sub _ _
          _ ≤ 2 * W := by linarith
    _ = 2 * W * ∑ j ∈ Ico n (m + 1), (m.choose j : ℝ) * c ^ (m - j) * d ^ j := by
        rw [mul_sum]; refine sum_congr rfl (fun j _ => by ring)
    _ ≤ 2 * W * ((m.choose n : ℝ) * d ^ n * (c + d) ^ (m - n)) :=
        mul_le_mul_of_nonneg_left (p1_mg_binomial_tail c d hc hd n m hnm) (by positivity)

/-- Below the matching order the kernel values coincide exactly. -/
theorem p1_thm_kcohort_kernel_low_orders_equal {ι κ : Type*} (S : Finset ι) (T : Finset κ)
    (w s : ι → ℝ) (w' s' : κ → ℝ) (c d : ℝ) (n m : ℕ)
    (hmom : ∀ j < n, mgMoment S w s j = mgMoment T w' s' j) (hmn : m < n) :
    mgKernel S w s c d m = mgKernel T w' s' c d m := by
  rw [p1_mg_kernel_expand, p1_mg_kernel_expand]
  refine sum_congr rfl (fun j hj => ?_)
  rw [hmom j (by have := mem_range.mp hj; omega)]

end CurrentMM
