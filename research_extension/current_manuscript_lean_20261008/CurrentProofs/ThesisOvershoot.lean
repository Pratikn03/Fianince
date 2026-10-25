import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity

/-!
# An overshoot certifies contrarian feedback (thesis, Proposition `prop:overshoot`)

The displacement after an outside event that adds no order flow follows
`x (t+1) = a * x t + κ * ∑_{m ≤ t} k m * x (t - m)` with `x 0 = d` (Proposition `prop:natural`).

* `thesis_overshoot_positive_class`: with `a ≥ 0`, `κ ≥ 0` and a non-negative kernel, `d * x t ≥ 0` for every `t`:
  the displacement never changes sign (part (i)).
* `thesis_overshoot_certifies_contrarian`: if the displacement ever has the opposite sign to `d`, some kernel tap is
  negative (part (ii)); nothing about which agent, its memory or its weight is used or recovered.
* `thesis_overshoot_realizable`: one contrarian cohort with memory zero (`k 0 = q`, `k (m+1) = 0`) gives
  `x t = d * (a + κ q)^t`, which alternates in sign when `a + κ q < 0` (part (iii)).
* `thesis_overshoot_alternates`: in that example, `d * x 1 < 0` whenever `a + κ q < 0` and `d ≠ 0`.
-/

namespace CurrentMM

open scoped BigOperators

theorem thesis_overshoot_positive_class (a κ d : ℝ) (k x : ℕ → ℝ)
    (ha : 0 ≤ a) (hκ : 0 ≤ κ) (hk : ∀ m, 0 ≤ k m)
    (hx0 : x 0 = d)
    (hx : ∀ t, x (t + 1) = a * x t + κ * ∑ m ∈ Finset.range (t + 1), k m * x (t - m)) :
    ∀ t, 0 ≤ d * x t := by
  intro t
  induction t using Nat.strong_induction_on with
  | _ t ih =>
    cases t with
    | zero => rw [hx0]; exact mul_self_nonneg d
    | succ s =>
      have hs : 0 ≤ d * x s := ih s (Nat.lt_succ_self s)
      have hsum : 0 ≤ ∑ m ∈ Finset.range (s + 1), k m * (d * x (s - m)) := by
        apply Finset.sum_nonneg
        intro m hm
        have hlt : s - m < s + 1 := by omega
        exact mul_nonneg (hk m) (ih (s - m) hlt)
      have heq : d * x (s + 1) = a * (d * x s) + κ * ∑ m ∈ Finset.range (s + 1), k m * (d * x (s - m)) := by
        rw [hx s, mul_add, Finset.mul_sum, Finset.mul_sum, Finset.mul_sum]
        congr 1
        · ring
        · apply Finset.sum_congr rfl; intro m _; ring
      rw [heq]
      exact add_nonneg (mul_nonneg ha hs) (mul_nonneg hκ hsum)

theorem thesis_overshoot_certifies_contrarian (a κ d : ℝ) (k x : ℕ → ℝ)
    (ha : 0 ≤ a) (hκ : 0 ≤ κ)
    (hx0 : x 0 = d)
    (hx : ∀ t, x (t + 1) = a * x t + κ * ∑ m ∈ Finset.range (t + 1), k m * x (t - m))
    (s : ℕ) (hover : d * x s < 0) :
    ∃ m, k m < 0 := by
  by_contra h
  simp only [not_exists, not_lt] at h
  have := thesis_overshoot_positive_class a κ d k x ha hκ h hx0 hx s
  linarith

theorem thesis_overshoot_realizable (a κ d q : ℝ) (k x : ℕ → ℝ)
    (hk0 : k 0 = q) (hk : ∀ m, k (m + 1) = 0)
    (hx0 : x 0 = d)
    (hx : ∀ t, x (t + 1) = a * x t + κ * ∑ m ∈ Finset.range (t + 1), k m * x (t - m)) :
    ∀ t, x t = d * (a + κ * q) ^ t := by
  intro t
  induction t with
  | zero => rw [hx0]; ring
  | succ s ih =>
    have hsum : ∑ m ∈ Finset.range (s + 1), k m * x (s - m) = q * x s := by
      rw [Finset.sum_range_succ']
      have hz : ∑ m ∈ Finset.range s, k (m + 1) * x (s - (m + 1)) = 0 := by
        apply Finset.sum_eq_zero; intro m _; rw [hk m]; ring
      rw [hz, hk0]; simp
    rw [hx s, hsum, ih]; ring

theorem thesis_overshoot_alternates (a κ d q : ℝ) (k x : ℕ → ℝ)
    (hk0 : k 0 = q) (hk : ∀ m, k (m + 1) = 0)
    (hx0 : x 0 = d)
    (hx : ∀ t, x (t + 1) = a * x t + κ * ∑ m ∈ Finset.range (t + 1), k m * x (t - m))
    (hc : a + κ * q < 0) (hd : d ≠ 0) :
    d * x 1 < 0 := by
  rw [thesis_overshoot_realizable a κ d q k x hk0 hk hx0 hx 1, pow_one]
  have hdd : 0 < d * d := mul_self_pos.mpr hd
  nlinarith

end CurrentMM
