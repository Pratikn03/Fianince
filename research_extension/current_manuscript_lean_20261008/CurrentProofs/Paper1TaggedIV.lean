import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.GCongr
import Mathlib.Tactic.Linarith

/-!
# Paper 1, Proposition 6.1 (`prop:tagged`): the instrument matrix is uniformly nonsingular

With the price autocovariance a nonnegative spectral mixture `γ(s) = ∑_ℓ c_ℓ λ_ℓ^s` (Lemma 2.3), `0 ≤ λ_ℓ ≤ λ̄ < 1`,
and class memory rate `0 ≤ r < 1`, the instrument moment matrix of class `i` is
`Σ_i = [[w A₀, γ₁], [w A₁, γ₀]]` (rows: instruments `x_{t-1}, x_t`; columns: regressors `ũ_{t-1}, x_t`) with `A₀ = ∑_ℓ c_ℓ/(1 - r λ_ℓ)` and `A₁ = ∑_ℓ c_ℓ λ_ℓ/(1 - r λ_ℓ)` (steps S5–S7 of
the proof), and `det Σ_i = w (γ₀ A₀ - γ₁ A₁) ≥ w_min (1 - λ̄²) γ₀²` (steps S8 and S12): the bound depends on neither
the class's rate nor the other classes, so identification is uniform in the rate spacing. The ergodic law of
large numbers and the martingale central limit theorem (S4, S11) are not formalized.
-/

namespace CurrentMM

open Finset

/-- **Uniform lower bound on the instrument determinant.** -/
theorem p1_tagged_iv_determinant_bound {L : ℕ} (c lam : Fin L → ℝ) (lbar r w wmin : ℝ)
    (hc : ∀ l, 0 ≤ c l) (hl0 : ∀ l, 0 ≤ lam l) (hl : ∀ l, lam l ≤ lbar) (hlbar : lbar < 1)
    (hr0 : 0 ≤ r) (hr1 : r < 1) (hwmin : 0 ≤ wmin) (hw : wmin ≤ w) :
    (!![w * ∑ l, c l / (1 - r * lam l), ∑ l, c l * lam l; w * ∑ l, c l * lam l / (1 - r * lam l), ∑ l, c l]).det
      = w * ((∑ l, c l) * (∑ l, c l / (1 - r * lam l)) - (∑ l, c l * lam l) * (∑ l, c l * lam l / (1 - r * lam l)))
    ∧ wmin * (1 - lbar ^ 2) * (∑ l, c l) ^ 2 ≤
      w * ((∑ l, c l) * (∑ l, c l / (1 - r * lam l)) - (∑ l, c l * lam l) * (∑ l, c l * lam l / (1 - r * lam l))) := by
  refine ⟨by rw [Matrix.det_fin_two_of]; ring, ?_⟩
  have hden : ∀ m, 0 < 1 - r * lam m := fun m => by
    have : r * lam m < 1 := by
      calc r * lam m ≤ r * 1 := mul_le_mul_of_nonneg_left (by linarith [hl m]) hr0
        _ < 1 := by linarith
    linarith
  set G := (∑ l, c l) * (∑ l, c l / (1 - r * lam l)) -
    (∑ l, c l * lam l) * (∑ l, c l * lam l / (1 - r * lam l)) with hG
  have hid : G = ∑ l, ∑ m, c l * c m * (1 - lam l * lam m) / (1 - r * lam m) := by
    rw [hG, sum_mul_sum, sum_mul_sum, ← sum_sub_distrib]
    refine sum_congr rfl (fun l _ => ?_)
    rw [← sum_sub_distrib]
    refine sum_congr rfl (fun m _ => ?_)
    have := (hden m).ne'
    field_simp
  have hterm : ∀ l m, c l * c m * (1 - lbar ^ 2) ≤ c l * c m * (1 - lam l * lam m) / (1 - r * lam m) := by
    intro l m
    have hll : lam l * lam m ≤ lbar ^ 2 := by
      rw [sq]; exact mul_le_mul (hl l) (hl m) (hl0 m) (le_trans (hl0 l) (hl l))
    have hcc : 0 ≤ c l * c m := mul_nonneg (hc l) (hc m)
    rw [le_div_iff₀ (hden m)]
    have hd1 : 1 - r * lam m ≤ 1 := by nlinarith [hl0 m]
    have hlb0 : 0 ≤ lbar := le_trans (hl0 l) (hl l)
    have hlb : 0 ≤ 1 - lbar ^ 2 := by nlinarith
    have hstep : 1 - lbar ^ 2 ≤ 1 - lam l * lam m := by linarith
    calc c l * c m * (1 - lbar ^ 2) * (1 - r * lam m) ≤ c l * c m * (1 - lbar ^ 2) * 1 :=
          mul_le_mul_of_nonneg_left hd1 (mul_nonneg hcc hlb)
      _ ≤ c l * c m * (1 - lam l * lam m) := by
          rw [mul_one]; exact mul_le_mul_of_nonneg_left hstep hcc
  have hGlo : (1 - lbar ^ 2) * (∑ l, c l) ^ 2 ≤ G := by
    rw [hid, pow_two (∑ l, c l), sum_mul_sum, mul_sum]
    refine sum_le_sum (fun l _ => ?_)
    rw [mul_sum]
    refine sum_le_sum (fun m _ => ?_)
    linarith [hterm l m]
  have hG0 : 0 ≤ G := by
    rw [hid]
    refine sum_nonneg (fun l _ => sum_nonneg (fun m _ => ?_))
    have h1 : lam l * lam m ≤ 1 * 1 :=
      mul_le_mul (by linarith [hl l]) (by linarith [hl m]) (hl0 m) zero_le_one
    exact div_nonneg (mul_nonneg (mul_nonneg (hc l) (hc m)) (by linarith)) (hden m).le
  calc wmin * (1 - lbar ^ 2) * (∑ l, c l) ^ 2 = wmin * ((1 - lbar ^ 2) * (∑ l, c l) ^ 2) := by ring
    _ ≤ wmin * G := mul_le_mul_of_nonneg_left hGlo hwmin
    _ ≤ w * G := mul_le_mul_of_nonneg_right hw hG0

end CurrentMM
