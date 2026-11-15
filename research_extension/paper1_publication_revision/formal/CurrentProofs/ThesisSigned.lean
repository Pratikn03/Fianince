import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp

/-!
# Contrarian agents: signed merged measures (thesis, Proposition `prop:signed`)

* `thesis_signed_psi_bounds`: for a function with supremum `s` and infimum `i ≤ s`, the positive-class bias term
  `ψ = s₊ + (-i)₊` lies between the sup norm `max s (-i)` and twice it (part (i)).
* `thesis_signed_modulus_sandwich`: hence, for every coefficient vector, the signed objective `2 B ‖h‖∞ + δ‖c‖`
  lies between the positive objective `B ψ + δ‖c‖` and twice it (part (i)).
* `thesis_signed_geom_mul`: the finite geometric identity `(∑_{t<H} x^t)(x - 1) = x^H - 1`.
* `thesis_signed_alternating_sum`: for `0 ≤ q < 1`, the partial sums of `(-q)^t` lie in `[0, 2]`
  (the summed response of a contrarian memory-zero economy stays bounded, part (ii)).
* `thesis_signed_abs_sum`: the partial sums of `q^t` equal `(1 - q^H) / (1 - q)`, which grows without bound as
  `q → 1` for large `H` (the absolute response does not, part (ii)).
-/

namespace CurrentMM

open scoped BigOperators

theorem thesis_signed_psi_bounds (s i : ℝ) (h : i ≤ s) :
    max s (-i) ≤ max s 0 + max (-i) 0 ∧ max s 0 + max (-i) 0 ≤ 2 * max s (-i) := by
  constructor
  · rcases le_total 0 s with hs | hs <;> rcases le_total 0 (-i) with hi | hi
    · rw [max_eq_left hs, max_eq_left hi]; exact max_le (by linarith) (by linarith)
    · rw [max_eq_left hs, max_eq_right hi]; exact max_le (by linarith) (by linarith)
    · rw [max_eq_right hs, max_eq_left hi]; exact max_le (by linarith) (by linarith)
    · rw [max_eq_right hs, max_eq_right hi]; exact max_le (by linarith) (by linarith)
  · have h1 : max s 0 ≤ max s (-i) := max_le (le_max_left _ _) (by
      rcases le_total 0 s with hs | hs
      · exact le_trans hs (le_max_left _ _)
      · have : 0 ≤ -i := by linarith
        exact le_trans this (le_max_right _ _))
    have h2 : max (-i) 0 ≤ max s (-i) := max_le (le_max_right _ _) (by
      rcases le_total 0 s with hs | hs
      · exact le_trans hs (le_max_left _ _)
      · have : 0 ≤ -i := by linarith
        exact le_trans this (le_max_right _ _))
    linarith

theorem thesis_signed_modulus_sandwich (B δn ψ m : ℝ) (hB : 0 ≤ B) (hδ : 0 ≤ δn)
    (hlo : m ≤ ψ) (hhi : ψ ≤ 2 * m) :
    B * ψ + δn ≤ 2 * B * m + δn ∧ 2 * B * m + δn ≤ 2 * (B * ψ + δn) := by
  constructor
  · nlinarith
  · nlinarith

theorem thesis_signed_geom_mul (x : ℝ) (H : ℕ) :
    (∑ t ∈ Finset.range H, x ^ t) * (x - 1) = x ^ H - 1 := by
  induction H with
  | zero => simp
  | succ n ih => rw [Finset.sum_range_succ, add_mul, ih]; ring

theorem thesis_signed_alternating_sum (q : ℝ) (hq0 : 0 ≤ q) (hq1 : q < 1) (H : ℕ) :
    0 ≤ ∑ t ∈ Finset.range H, (-q) ^ t ∧ ∑ t ∈ Finset.range H, (-q) ^ t ≤ 2 := by
  have hg := thesis_signed_geom_mul (-q) H
  have hpow : |(-q) ^ H| ≤ 1 := by
    rw [abs_pow, abs_neg, abs_of_nonneg hq0]
    exact pow_le_one₀ hq0 (le_of_lt hq1)
  have hlo : -1 ≤ (-q) ^ H := by linarith [neg_abs_le ((-q) ^ H)]
  have hhi : (-q) ^ H ≤ 1 := by linarith [le_abs_self ((-q) ^ H)]
  set S := ∑ t ∈ Finset.range H, (-q) ^ t with hS
  have hmul : S * (1 + q) = 1 - (-q) ^ H := by linarith
  constructor
  · nlinarith
  · nlinarith

theorem thesis_signed_abs_sum (q : ℝ) (hq1 : q < 1) (H : ℕ) :
    ∑ t ∈ Finset.range H, q ^ t = (1 - q ^ H) / (1 - q) := by
  have hg := thesis_signed_geom_mul q H
  have h2 : 1 - q ≠ 0 := by intro h; linarith
  rw [eq_div_iff h2]
  linarith

end CurrentMM
