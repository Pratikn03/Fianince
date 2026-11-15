import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp

/-!
# Passive certification with finite memory and any number of cohorts (thesis, Theorem `thm:passivemulti`)

The closed-loop polynomial factors as `f(z) = (1 - ρ z) g(z)`, the margin is `M = (1 - ρ) g(1)`.

* `thesis_pm_one_sub_le`: for `0 ≤ ρ ≤ 1`, `1 - ρ ≤ 1 - ρ^2`.
* `thesis_pm_kl`: with `ρ = 1 - μ/g`, the divergence `(2μ/g)^2/2 · T/(1-ρ^2)` between the economies with margins
  `±μ` is at most `2 T μ / g` (part (i)).
* `thesis_pm_factor`: for roots of modulus at least `1 + γ`, each factor `1 - 1/r` is at least `γ/(1+γ)`.
* `thesis_pm_prod_lower`: a product of factors each at least `b ≥ 0` is at least `b^L`.
* `thesis_pm_christoffel_cases`: if `I ≥ π/(8δ)` or `I ≥ 1/(4 K δ^2)` with `0 < δ ≤ 1`, `K > 0`, then
  `I ≥ min (π/8) (1/(4K)) / δ` (the weighted-integral bound of part (ii); `p` stands for `π`, any positive constant).
* `thesis_pm_variance`: from `τ² ≥ σ² c / (2π G² δ)` and `δ = M/g`, the asymptotic variance `σ²/τ²` is at most
  `2π G² M / (c g)` (part (ii)).
-/

namespace CurrentMM

open scoped BigOperators

theorem thesis_pm_one_sub_le (ρ : ℝ) (h0 : 0 ≤ ρ) (h1 : ρ ≤ 1) : 1 - ρ ≤ 1 - ρ ^ 2 := by
  nlinarith

theorem thesis_pm_kl (μ g T : ℝ) (hμ : 0 < μ) (hg : 0 < g) (hT : 0 ≤ T) (hle : μ ≤ g) :
    (2 * μ / g) ^ 2 / 2 * (T / (1 - (1 - μ / g) ^ 2)) ≤ 2 * T * μ / g := by
  have hx : 0 < μ / g := div_pos hμ hg
  have hx1 : μ / g ≤ 1 := (div_le_one hg).mpr hle
  have hden : μ / g ≤ 1 - (1 - μ / g) ^ 2 := by nlinarith
  have hdpos : 0 < 1 - (1 - μ / g) ^ 2 := lt_of_lt_of_le hx hden
  have key : T / (1 - (1 - μ / g) ^ 2) ≤ T / (μ / g) := div_le_div_of_nonneg_left hT hx hden
  have hsq : 0 ≤ (2 * μ / g) ^ 2 / 2 := by positivity
  calc (2 * μ / g) ^ 2 / 2 * (T / (1 - (1 - μ / g) ^ 2)) ≤ (2 * μ / g) ^ 2 / 2 * (T / (μ / g)) :=
        mul_le_mul_of_nonneg_left key hsq
    _ = 2 * T * μ / g := by field_simp

theorem thesis_pm_factor (r γ : ℝ) (hγ : 0 < γ) (hr : 1 + γ ≤ r) : γ / (1 + γ) ≤ 1 - 1 / r := by
  have hr0 : 0 < r := by linarith
  have h1 : 1 / r ≤ 1 / (1 + γ) := one_div_le_one_div_of_le (by linarith) hr
  have h2 : γ / (1 + γ) = 1 - 1 / (1 + γ) := by field_simp; ring
  linarith

theorem thesis_pm_prod_lower (L : ℕ) (b : ℝ) (a : ℕ → ℝ) (hb : 0 ≤ b) (ha : ∀ j, b ≤ a j) :
    b ^ L ≤ ∏ j ∈ Finset.range L, a j := by
  induction L with
  | zero => simp
  | succ n ih =>
    rw [Finset.prod_range_succ, pow_succ]
    have hn : 0 ≤ b ^ n := pow_nonneg hb n
    exact mul_le_mul ih (ha n) hb (le_trans hn ih)

theorem thesis_pm_christoffel_cases (I δ K p : ℝ) (hδ : 0 < δ) (hδ1 : δ ≤ 1) (hK : 0 < K)
    (h : p / (8 * δ) ≤ I ∨ 1 / (4 * K * δ ^ 2) ≤ I) :
    min (p / 8) (1 / (4 * K)) / δ ≤ I := by
  rcases h with h | h
  · have : min (p / 8) (1 / (4 * K)) / δ ≤ p / 8 / δ :=
      div_le_div_of_nonneg_right (min_le_left _ _) hδ.le
    have e : p / 8 / δ = p / (8 * δ) := by field_simp
    linarith
  · have h1 : min (p / 8) (1 / (4 * K)) / δ ≤ 1 / (4 * K) / δ :=
      div_le_div_of_nonneg_right (min_le_right _ _) hδ.le
    have h2 : 1 / (4 * K) / δ ≤ 1 / (4 * K * δ ^ 2) := by
      rw [div_div, div_le_div_iff₀ (by positivity) (by positivity)]
      nlinarith [mul_pos hK hδ]
    linarith

theorem thesis_pm_variance (σ2 τ2 c G2 δ M g p : ℝ) (hp : 0 < p) (hσ : 0 < σ2) (hc : 0 < c) (hG : 0 < G2) (hδ : 0 < δ)
    (hg : 0 < g) (hM : δ = M / g) (hτ : σ2 * c / (2 * p * G2 * δ) ≤ τ2) :
    σ2 / τ2 ≤ 2 * p * G2 * M / (c * g) := by
  have hlow : 0 < σ2 * c / (2 * p * G2 * δ) := by positivity
  have hτpos : 0 < τ2 := lt_of_lt_of_le hlow hτ
  have step : σ2 / τ2 ≤ σ2 / (σ2 * c / (2 * p * G2 * δ)) := div_le_div_of_nonneg_left hσ.le hlow hτ
  have e : σ2 / (σ2 * c / (2 * p * G2 * δ)) = 2 * p * G2 * M / (c * g) := by
    rw [hM]; field_simp
  linarith

end CurrentMM
