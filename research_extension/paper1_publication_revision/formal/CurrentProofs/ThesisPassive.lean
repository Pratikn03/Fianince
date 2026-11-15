import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp

/-!
# Passive certification costs the inverse margin (thesis, Theorem `thm:passivecert`)

For the memory-zero economy `x (t+1) = ρ x t + e (t+1)` started at `x 0 = 0` with unit-variance innovations, the
variance `v t = E x_t^2` satisfies `v 0 = 0`, `v (t+1) = ρ^2 v t + 1`. The lower bound of part (i) compares two such
economies whose roots differ by `Δ`; the Kullback--Leibler divergence over `T` steps is `Δ^2/2 * ∑_{t<T} v t`.

* `thesis_passive_variance_le_inv`: if `ρ^2 < 1` then `v t ≤ 1/(1 - ρ^2)` for every `t`.
* `thesis_passive_variance_le_t`: if `ρ^2 ≤ 1` then `v t ≤ t`.
* `thesis_passive_kl_sum`: if `ρ^2 < 1` then `∑_{t<T} v t ≤ T/(1 - ρ^2)`.
* `thesis_passive_kl_margin`: with `ρ = 1 - μ`, `0 < μ ≤ 1`, the divergence between roots `1 - μ` and `1 + μ` over
  `T` steps, `(2μ)^2/2 * ∑_{t<T} v t`, is at most `2 T μ`.
-/

namespace CurrentMM

open scoped BigOperators

theorem thesis_passive_variance_le_inv (ρ : ℝ) (v : ℕ → ℝ) (hρ : ρ ^ 2 < 1)
    (hv0 : v 0 = 0) (hv : ∀ t, v (t + 1) = ρ ^ 2 * v t + 1) :
    ∀ t, v t ≤ 1 / (1 - ρ ^ 2) := by
  have hpos : 0 < 1 - ρ ^ 2 := by linarith
  have hinv : 0 ≤ 1 / (1 - ρ ^ 2) := le_of_lt (one_div_pos.mpr hpos)
  intro t
  induction t with
  | zero => rw [hv0]; exact hinv
  | succ s ih =>
    rw [hv s]
    have hsq : 0 ≤ ρ ^ 2 := sq_nonneg ρ
    have h1 : ρ ^ 2 * v s ≤ ρ ^ 2 * (1 / (1 - ρ ^ 2)) := mul_le_mul_of_nonneg_left ih hsq
    have h2 : ρ ^ 2 * (1 / (1 - ρ ^ 2)) + 1 = 1 / (1 - ρ ^ 2) := by
      field_simp
      ring
    linarith

theorem thesis_passive_variance_le_t (ρ : ℝ) (v : ℕ → ℝ) (hρ : ρ ^ 2 ≤ 1)
    (hv0 : v 0 = 0) (hv : ∀ t, v (t + 1) = ρ ^ 2 * v t + 1) :
    ∀ t, v t ≤ t := by
  have hnn : ∀ t, 0 ≤ v t := by
    intro t
    induction t with
    | zero => rw [hv0]
    | succ s ih => rw [hv s]; have := sq_nonneg ρ; positivity
  intro t
  induction t with
  | zero => rw [hv0]; simp
  | succ s ih =>
    rw [hv s]
    have h1 : ρ ^ 2 * v s ≤ v s := by
      have := hnn s
      nlinarith
    push_cast
    linarith

theorem thesis_passive_kl_sum (ρ : ℝ) (v : ℕ → ℝ) (hρ : ρ ^ 2 < 1)
    (hv0 : v 0 = 0) (hv : ∀ t, v (t + 1) = ρ ^ 2 * v t + 1) (T : ℕ) :
    ∑ t ∈ Finset.range T, v t ≤ T / (1 - ρ ^ 2) := by
  have hb := thesis_passive_variance_le_inv ρ v hρ hv0 hv
  calc ∑ t ∈ Finset.range T, v t ≤ ∑ t ∈ Finset.range T, 1 / (1 - ρ ^ 2) :=
        Finset.sum_le_sum (fun t _ => hb t)
    _ = T / (1 - ρ ^ 2) := by
        rw [Finset.sum_const, Finset.card_range, nsmul_eq_mul]; ring

theorem thesis_passive_kl_margin (μ : ℝ) (v : ℕ → ℝ) (hμ0 : 0 < μ) (hμ1 : μ ≤ 1)
    (hv0 : v 0 = 0) (hv : ∀ t, v (t + 1) = (1 - μ) ^ 2 * v t + 1) (T : ℕ) :
    (2 * μ) ^ 2 / 2 * ∑ t ∈ Finset.range T, v t ≤ 2 * T * μ := by
  have hρ : (1 - μ) ^ 2 < 1 := by nlinarith
  have hs := thesis_passive_kl_sum (1 - μ) v hρ hv0 hv T
  have hden : 0 < 1 - (1 - μ) ^ 2 := by linarith
  have hge : μ ≤ 1 - (1 - μ) ^ 2 := by nlinarith
  have hT : (0 : ℝ) ≤ T := Nat.cast_nonneg T
  have hfrac : (T : ℝ) / (1 - (1 - μ) ^ 2) ≤ T / μ := div_le_div_of_nonneg_left hT hμ0 hge
  have hcoef : 0 ≤ (2 * μ) ^ 2 / 2 := by positivity
  calc (2 * μ) ^ 2 / 2 * ∑ t ∈ Finset.range T, v t ≤ (2 * μ) ^ 2 / 2 * (T / μ) :=
        mul_le_mul_of_nonneg_left (le_trans hs hfrac) hcoef
    _ = 2 * T * μ := by field_simp

end CurrentMM
