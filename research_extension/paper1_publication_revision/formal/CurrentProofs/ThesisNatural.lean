import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Algebra.BigOperators.NatAntidiagonal
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
# Natural experiments and horizon-limited amplification (thesis, Propositions `prop:natural`, `prop:horizon`)

Index the impulse response as in `ThesisPeak`: `g 0 = κ`, `g (s+1) = a * g s + κ * ∑_{m ≤ s} k m * g (s - m)`.

* `thesis_natural_displacement`: a displacement `x 0 = d` that adds no order flow evolves by the same recursion, and
  `κ * x t = d * g t` for every `t` (Proposition `prop:natural` (i)).
* `thesis_natural_double_sum`: `∑_{t<H} ∑_{m ≤ t} k m * x (t-m) = ∑_{s<H} x s * ∑_{m < H-s} k m` (the exchange of sums
  in the proof of part (iv)).
* `thesis_natural_finite_margin`: `x 0 - x H = (1 - a) ∑_{t<H} x t - κ ∑_{s<H} x s ∑_{m<H-s} k m`, the finite-horizon
  identity behind part (iv).
* `thesis_horizon_worst_case`: for shocks bounded by `w̄`, a response `∑_{s<H} g s * w s` is at most `w̄ ∑_{s<H} |g s|`
  in absolute value (Proposition `prop:horizon` (i)).
-/

namespace CurrentMM

open scoped BigOperators

theorem thesis_natural_displacement (a κ d : ℝ) (k g x : ℕ → ℝ)
    (hg0 : g 0 = κ)
    (hg : ∀ s, g (s + 1) = a * g s + κ * ∑ m ∈ Finset.range (s + 1), k m * g (s - m))
    (hx0 : x 0 = d)
    (hx : ∀ t, x (t + 1) = a * x t + κ * ∑ m ∈ Finset.range (t + 1), k m * x (t - m)) :
    ∀ t, κ * x t = d * g t := by
  intro t
  induction t using Nat.strong_induction_on with
  | _ t ih =>
    cases t with
    | zero => rw [hx0, hg0]; ring
    | succ s =>
      have hsum : ∑ m ∈ Finset.range (s + 1), k m * (κ * x (s - m))
          = ∑ m ∈ Finset.range (s + 1), k m * (d * g (s - m)) := by
        apply Finset.sum_congr rfl
        intro m hm
        have hlt : s - m < s + 1 := by omega
        rw [ih (s - m) hlt]
      have hs : κ * x s = d * g s := ih s (Nat.lt_succ_self s)
      calc κ * x (s + 1) = a * (κ * x s) + κ * ∑ m ∈ Finset.range (s + 1), k m * (κ * x (s - m)) := by
              rw [hx s, mul_add, Finset.mul_sum, Finset.mul_sum, Finset.mul_sum]
              congr 1
              · ring
              · apply Finset.sum_congr rfl; intro m _; ring
        _ = a * (d * g s) + κ * ∑ m ∈ Finset.range (s + 1), k m * (d * g (s - m)) := by rw [hs, hsum]
        _ = d * (a * g s + κ * ∑ m ∈ Finset.range (s + 1), k m * g (s - m)) := by
              rw [mul_add, Finset.mul_sum, Finset.mul_sum, Finset.mul_sum]
              congr 1
              · ring
              · apply Finset.sum_congr rfl; intro m _; ring
        _ = d * g (s + 1) := by rw [hg s]

theorem thesis_natural_double_sum (k x : ℕ → ℝ) (H : ℕ) :
    ∑ t ∈ Finset.range H, ∑ m ∈ Finset.range (t + 1), k m * x (t - m)
      = ∑ s ∈ Finset.range H, x s * ∑ m ∈ Finset.range (H - s), k m := by
  induction H with
  | zero => simp
  | succ H ih =>
    rw [Finset.sum_range_succ, ih]
    have hsplit : ∑ s ∈ Finset.range (H + 1), x s * ∑ m ∈ Finset.range (H + 1 - s), k m
        = ∑ s ∈ Finset.range H, x s * ∑ m ∈ Finset.range (H - s), k m
          + ∑ s ∈ Finset.range (H + 1), x s * k (H - s) := by
      rw [Finset.sum_range_succ (fun s => x s * ∑ m ∈ Finset.range (H + 1 - s), k m)]
      rw [Finset.sum_range_succ (fun s => x s * k (H - s))]
      have hinner : ∀ s ∈ Finset.range H, x s * ∑ m ∈ Finset.range (H + 1 - s), k m
          = x s * ∑ m ∈ Finset.range (H - s), k m + x s * k (H - s) := by
        intro s hs
        have hle : s ≤ H := le_of_lt (Finset.mem_range.mp hs)
        have : H + 1 - s = (H - s) + 1 := by omega
        rw [this, Finset.sum_range_succ, mul_add]
      rw [Finset.sum_congr rfl hinner, Finset.sum_add_distrib]
      simp
      ring
    rw [hsplit]
    congr 1
    have e1 := Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk (fun p : ℕ × ℕ => k p.1 * x p.2) H
    have e2 := Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk (fun p : ℕ × ℕ => x p.1 * k p.2) H
    have e3 := Finset.Nat.sum_antidiagonal_swap (n := H) (f := fun p : ℕ × ℕ => x p.1 * k p.2)
    simp only [Prod.fst_swap, Prod.snd_swap] at e1 e2 e3
    rw [← e1, ← e2, ← e3]
    apply Finset.sum_congr rfl
    intro p _
    ring

theorem thesis_natural_finite_margin (a κ : ℝ) (k x : ℕ → ℝ)
    (hx : ∀ t, x (t + 1) = a * x t + κ * ∑ m ∈ Finset.range (t + 1), k m * x (t - m)) (H : ℕ) :
    x 0 - x H = (1 - a) * ∑ t ∈ Finset.range H, x t
      - κ * ∑ s ∈ Finset.range H, x s * ∑ m ∈ Finset.range (H - s), k m := by
  have htel : x H - x 0 = ∑ t ∈ Finset.range H, (x (t + 1) - x t) := by
    rw [Finset.sum_range_sub (fun t => x t)]
  have hstep : ∑ t ∈ Finset.range H, (x (t + 1) - x t)
      = (a - 1) * ∑ t ∈ Finset.range H, x t
        + κ * ∑ t ∈ Finset.range H, ∑ m ∈ Finset.range (t + 1), k m * x (t - m) := by
    rw [Finset.mul_sum, Finset.mul_sum, ← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro t _
    rw [hx t]; ring
  rw [thesis_natural_double_sum] at hstep
  linarith

theorem thesis_horizon_worst_case (g w : ℕ → ℝ) (wbar : ℝ) (H : ℕ)
    (hw : ∀ s, |w s| ≤ wbar) :
    |∑ s ∈ Finset.range H, g s * w s| ≤ wbar * ∑ s ∈ Finset.range H, |g s| := by
  calc |∑ s ∈ Finset.range H, g s * w s| ≤ ∑ s ∈ Finset.range H, |g s * w s| := Finset.abs_sum_le_sum_abs _ _
    _ = ∑ s ∈ Finset.range H, |g s| * |w s| := by
          apply Finset.sum_congr rfl; intro s _; rw [abs_mul]
    _ ≤ ∑ s ∈ Finset.range H, |g s| * wbar := by
          apply Finset.sum_le_sum; intro s _
          exact mul_le_mul_of_nonneg_left (hw s) (abs_nonneg _)
    _ = wbar * ∑ s ∈ Finset.range H, |g s| := by rw [Finset.mul_sum]; apply Finset.sum_congr rfl; intro s _; ring

end CurrentMM
