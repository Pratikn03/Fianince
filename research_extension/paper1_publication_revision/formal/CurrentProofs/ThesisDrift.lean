import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp

/-!
# Certifying a drifting margin (thesis, Proposition `prop:drift`)

* `thesis_drift_sum_succ`: `∑_{j<W} (j+1) = W (W+1) / 2`.
* `thesis_drift_bias`: if each of the last `W` daily margins differs from today's by at most `d (j+1)`, the window
  average differs from today's margin by at most `d (W+1)/2` (part (i), bias).
* `thesis_drift_amgm`: for non-negative `a, b, c`, `27 a b c ≤ (a + b + c)^3`.
* `thesis_drift_window`: for `d, q, u > 0`, `27 d q^2 ≤ (d u^2 + 2 q / u)^3`; with `u = √W` and `q = z s` this is the
  optimal-window bound `d W + 2 z s / √W ≥ 3 (z s)^{2/3} d^{1/3}` of part (i).
* `thesis_drift_squares`: `∑_{j<k} (c (j+1))^2 ≤ c^2 k^3`, the divergence bound of part (ii).
-/

namespace CurrentMM

open scoped BigOperators

theorem thesis_drift_sum_succ (W : ℕ) :
    ∑ j ∈ Finset.range W, ((j : ℝ) + 1) = (W : ℝ) * (W + 1) / 2 := by
  induction W with
  | zero => simp
  | succ n ih => rw [Finset.sum_range_succ, ih]; push_cast; ring

theorem thesis_drift_bias (W : ℕ) (hW : 0 < W) (d MT : ℝ) (m : ℕ → ℝ)
    (h : ∀ j, |m j - MT| ≤ d * ((j : ℝ) + 1)) :
    |(∑ j ∈ Finset.range W, m j) / W - MT| ≤ d * ((W : ℝ) + 1) / 2 := by
  have hWr : (0 : ℝ) < W := by exact_mod_cast hW
  have hsplit : (∑ j ∈ Finset.range W, m j) / W - MT = (∑ j ∈ Finset.range W, (m j - MT)) / W := by
    rw [Finset.sum_sub_distrib, Finset.sum_const, Finset.card_range, nsmul_eq_mul]
    field_simp
  rw [hsplit, abs_div, abs_of_pos hWr, div_le_iff₀ hWr]
  calc |∑ j ∈ Finset.range W, (m j - MT)| ≤ ∑ j ∈ Finset.range W, |m j - MT| := Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ j ∈ Finset.range W, d * ((j : ℝ) + 1) := Finset.sum_le_sum (fun j _ => h j)
    _ = d * ((W : ℝ) * (W + 1) / 2) := by rw [← Finset.mul_sum, thesis_drift_sum_succ]
    _ = d * ((W : ℝ) + 1) / 2 * W := by ring

theorem thesis_drift_amgm (a b c : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) :
    27 * a * b * c ≤ (a + b + c) ^ 3 := by
  nlinarith [sq_nonneg (a - b), sq_nonneg (b - c), sq_nonneg (a - c), mul_nonneg ha hb, mul_nonneg hb hc,
    mul_nonneg ha hc, mul_nonneg (mul_nonneg ha hb) hc, sq_nonneg (a + b - 2 * c), sq_nonneg (a + c - 2 * b),
    sq_nonneg (b + c - 2 * a), mul_nonneg ha (sq_nonneg (b - c)), mul_nonneg hb (sq_nonneg (a - c)),
    mul_nonneg hc (sq_nonneg (a - b))]

theorem thesis_drift_window (d q u : ℝ) (hd : 0 < d) (hq : 0 < q) (hu : 0 < u) :
    27 * d * q ^ 2 ≤ (d * u ^ 2 + 2 * q / u) ^ 3 := by
  have ha : 0 ≤ d * u ^ 2 := by positivity
  have hb : 0 ≤ q / u := by positivity
  have h := thesis_drift_amgm (d * u ^ 2) (q / u) (q / u) ha hb hb
  have hprod : 27 * (d * u ^ 2) * (q / u) * (q / u) = 27 * d * q ^ 2 := by field_simp
  have hsum : d * u ^ 2 + q / u + q / u = d * u ^ 2 + 2 * q / u := by ring
  rw [hprod, hsum] at h
  exact h

theorem thesis_drift_squares (c : ℝ) (k : ℕ) :
    ∑ j ∈ Finset.range k, (c * ((j : ℝ) + 1)) ^ 2 ≤ c ^ 2 * (k : ℝ) ^ 3 := by
  have hj : ∀ j ∈ Finset.range k, (c * ((j : ℝ) + 1)) ^ 2 ≤ c ^ 2 * (k : ℝ) ^ 2 := by
    intro j hj
    have hjk : (j : ℝ) + 1 ≤ k := by exact_mod_cast Finset.mem_range.mp hj
    have hj0 : (0 : ℝ) ≤ (j : ℝ) + 1 := by positivity
    have : ((j : ℝ) + 1) ^ 2 ≤ (k : ℝ) ^ 2 := by nlinarith
    calc (c * ((j : ℝ) + 1)) ^ 2 = c ^ 2 * ((j : ℝ) + 1) ^ 2 := by ring
      _ ≤ c ^ 2 * (k : ℝ) ^ 2 := mul_le_mul_of_nonneg_left this (sq_nonneg c)
  calc ∑ j ∈ Finset.range k, (c * ((j : ℝ) + 1)) ^ 2 ≤ ∑ j ∈ Finset.range k, c ^ 2 * (k : ℝ) ^ 2 := Finset.sum_le_sum hj
    _ = c ^ 2 * (k : ℝ) ^ 3 := by rw [Finset.sum_const, Finset.card_range, nsmul_eq_mul]; ring

end CurrentMM
