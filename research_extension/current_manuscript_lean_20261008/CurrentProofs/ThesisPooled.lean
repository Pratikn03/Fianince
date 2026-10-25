import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp

/-!
# The pooled price-and-flow estimator of the margin (thesis, Theorem `thm:pooled`)

* `thesis_pooled_sq`: `(u + v)^2 ≤ 2 u^2 + 2 v^2`, which bounds the asymptotic variance of `M̂ - M`
  `= -(β̂ + κ̂ Φ + M) - κ̂ (Φ̂ - Φ)` by twice the sum of the two pieces' variances.
* `thesis_pooled_var`: if `V₁ ≤ A δ` and `κ^2 V₂ ≤ A δ` then `2 (V₁ + κ^2 V₂) ≤ 4 A δ`.
* `thesis_pooled_kl`: the divergence between the economies with margins `±μ` that differ only in the flow equation,
  `(2μ/κ)^2 / 2 · T · (κ^2 s_w^2 + s_ε^2) / (s_w^2 μ)`, equals `2 T μ (1 + s_ε^2 / (κ^2 s_w^2))`.
* `thesis_pooled_record`: if `2 (1 - 2α)^2 ≤ 2 T μ (1 + R)` with `μ > 0`, `R ≥ 0`, then `(1 - 2α)^2 / (μ (1 + R)) ≤ T`.
-/

namespace CurrentMM

theorem thesis_pooled_sq (u v : ℝ) : (u + v) ^ 2 ≤ 2 * u ^ 2 + 2 * v ^ 2 := by
  nlinarith [sq_nonneg (u - v)]

theorem thesis_pooled_var (V₁ V₂ κ A δ : ℝ) (h₁ : V₁ ≤ A * δ) (h₂ : κ ^ 2 * V₂ ≤ A * δ) :
    2 * (V₁ + κ ^ 2 * V₂) ≤ 4 * (A * δ) := by
  linarith

theorem thesis_pooled_kl (μ κ sw2 se2 T : ℝ) (hμ : 0 < μ) (hκ : 0 < κ) (hs : 0 < sw2) :
    (2 * μ / κ) ^ 2 / 2 * T * ((κ ^ 2 * sw2 + se2) / (sw2 * μ)) = 2 * T * μ * (1 + se2 / (κ ^ 2 * sw2)) := by
  field_simp

theorem thesis_pooled_record (α μ R T : ℝ) (hμ : 0 < μ) (hR : 0 ≤ R)
    (h : 2 * (1 - 2 * α) ^ 2 ≤ 2 * T * μ * (1 + R)) :
    (1 - 2 * α) ^ 2 / (μ * (1 + R)) ≤ T := by
  have hpos : 0 < μ * (1 + R) := by positivity
  rw [div_le_iff₀ hpos]
  nlinarith

end CurrentMM
