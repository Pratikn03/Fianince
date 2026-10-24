import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.GCongr
import Mathlib.Tactic.Positivity

/-!
# The impulse response of the cohort economy (thesis, Corollary `cor:peak`)

Index the response to a unit shock from zero: `g 0 = κ` and
`g (s+1) = a * g s + κ * ∑_{m ≤ s} k m * g (s - m)`, which is `h_{s+1}` of the thesis.

* `thesis_peak_le_first`: with non-negative taps and `a + κ ∑_{m ≤ s} k m ≤ 1` for all `s`
  (the stable class), every response lies in `[0, κ]`: the peak is the first response.
* `thesis_peak_locality`: `g (s+1)` depends only on the taps `k 0, …, k s`.
* `thesis_peak_monotone`: the response is monotone in the taps.
-/

namespace CurrentMM

open scoped BigOperators

theorem thesis_peak_le_first (a κ : ℝ) (k g : ℕ → ℝ) (ha : 0 ≤ a) (hκ : 0 ≤ κ)
    (hk : ∀ m, 0 ≤ k m) (hmargin : ∀ s, a + κ * ∑ m ∈ Finset.range (s + 1), k m ≤ 1)
    (h0 : g 0 = κ)
    (hstep : ∀ s, g (s + 1) = a * g s + κ * ∑ m ∈ Finset.range (s + 1), k m * g (s - m)) :
    ∀ s, 0 ≤ g s ∧ g s ≤ κ := by
  intro s
  induction s using Nat.strong_induction_on with
  | _ s ih =>
    cases s with
    | zero => exact ⟨by rw [h0]; exact hκ, by rw [h0]⟩
    | succ s =>
      have hb : ∀ m ∈ Finset.range (s + 1), 0 ≤ g (s - m) ∧ g (s - m) ≤ κ :=
        fun m _ => ih (s - m) (by omega)
      have hsum_nn : 0 ≤ ∑ m ∈ Finset.range (s + 1), k m * g (s - m) :=
        Finset.sum_nonneg (fun m hm => mul_nonneg (hk m) (hb m hm).1)
      have hsum_le : ∑ m ∈ Finset.range (s + 1), k m * g (s - m)
          ≤ κ * ∑ m ∈ Finset.range (s + 1), k m := by
        rw [Finset.mul_sum]
        apply Finset.sum_le_sum
        intro m hm
        have := mul_le_mul_of_nonneg_left (hb m hm).2 (hk m)
        linarith
      have hgs := ih s (by omega)
      rw [hstep s]
      constructor
      · have := mul_nonneg ha hgs.1
        have := mul_nonneg hκ hsum_nn
        linarith
      · have h1 : a * g s ≤ a * κ := mul_le_mul_of_nonneg_left hgs.2 ha
        have h2 : κ * ∑ m ∈ Finset.range (s + 1), k m * g (s - m)
            ≤ κ * (κ * ∑ m ∈ Finset.range (s + 1), k m) := mul_le_mul_of_nonneg_left hsum_le hκ
        have h3 : κ * (a + κ * ∑ m ∈ Finset.range (s + 1), k m) ≤ κ * 1 :=
          mul_le_mul_of_nonneg_left (hmargin s) hκ
        nlinarith

theorem thesis_peak_locality (a κ : ℝ) (k k' g g' : ℕ → ℝ) (n : ℕ)
    (hkk : ∀ m, m ≤ n → k m = k' m) (h0 : g 0 = κ) (h0' : g' 0 = κ)
    (hstep : ∀ s, g (s + 1) = a * g s + κ * ∑ m ∈ Finset.range (s + 1), k m * g (s - m))
    (hstep' : ∀ s, g' (s + 1) = a * g' s + κ * ∑ m ∈ Finset.range (s + 1), k' m * g' (s - m)) :
    ∀ s, s ≤ n + 1 → g s = g' s := by
  intro s
  induction s using Nat.strong_induction_on with
  | _ s ih =>
    intro hs
    cases s with
    | zero => rw [h0, h0']
    | succ s =>
      rw [hstep s, hstep' s, ih s (by omega) (by omega)]
      congr 2
      apply Finset.sum_congr rfl
      intro m hm
      have hm' : m < s + 1 := Finset.mem_range.mp hm
      rw [hkk m (by omega), ih (s - m) (by omega) (by omega)]

theorem thesis_peak_monotone (a κ : ℝ) (k k' g g' : ℕ → ℝ) (ha : 0 ≤ a) (hκ : 0 ≤ κ)
    (hk : ∀ m, 0 ≤ k m) (hkk : ∀ m, k m ≤ k' m) (h0 : g 0 = κ) (h0' : g' 0 = κ)
    (hstep : ∀ s, g (s + 1) = a * g s + κ * ∑ m ∈ Finset.range (s + 1), k m * g (s - m))
    (hstep' : ∀ s, g' (s + 1) = a * g' s + κ * ∑ m ∈ Finset.range (s + 1), k' m * g' (s - m)) :
    ∀ s, 0 ≤ g s ∧ g s ≤ g' s := by
  intro s
  induction s using Nat.strong_induction_on with
  | _ s ih =>
    cases s with
    | zero => exact ⟨by rw [h0]; exact hκ, by rw [h0, h0']⟩
    | succ s =>
      have hb : ∀ m ∈ Finset.range (s + 1), 0 ≤ g (s - m) ∧ g (s - m) ≤ g' (s - m) :=
        fun m _ => ih (s - m) (by omega)
      have hgs := ih s (by omega)
      have hsum_nn : 0 ≤ ∑ m ∈ Finset.range (s + 1), k m * g (s - m) :=
        Finset.sum_nonneg (fun m hm => mul_nonneg (hk m) (hb m hm).1)
      have hsum_le : ∑ m ∈ Finset.range (s + 1), k m * g (s - m)
          ≤ ∑ m ∈ Finset.range (s + 1), k' m * g' (s - m) := by
        apply Finset.sum_le_sum
        intro m hm
        exact mul_le_mul (hkk m) (hb m hm).2 (hb m hm).1 (le_trans (hk m) (hkk m))
      rw [hstep s, hstep' s]
      constructor
      · have := mul_nonneg ha hgs.1
        have := mul_nonneg hκ hsum_nn
        linarith
      · have h1 : a * g s ≤ a * g' s := mul_le_mul_of_nonneg_left hgs.2 ha
        have h2 := mul_le_mul_of_nonneg_left hsum_le hκ
        linarith

end CurrentMM
