import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
# Paper 1, Theorems 4.2 and 4.3: the inventory equilibrium is the paper's closed loop; fragility

Notation as in `Paper1InventoryEquilibrium.lean`. The equilibrium price law is `x_t = -κ H_t + Σ_i β_i u_{i,t+1}`,
with `β_i (D - r_i) = κ`, implicit form `D x_t = -κ H_t + Σ_i β_i r_i u_{i,t}`, and inventory
`H_t = ā H_{t-1} - Σ_i u_{i,t} - ξ_t`.

* `p1_eq_reduced_form`: **pathwise**, `x_t = (ā/D) x_{t-1} + (κ/D) (ξ_t + Σ_i (D-ā)/(D-r_i) u_{i,t})`. Since the scaled
  flows `ũ_i = (D-ā)/(D-r_i) u_i` follow `ũ_{i,t+1} = r_i ũ_{i,t} + w̃_i x_t` with `w̃_i = (D-ā) w_i/(D-r_i)`, the
  equilibrium price is the paper's closed loop with persistence `ā/D`, impact `κ/D` and merged weights `w̃_i`, at
  the same memory rates.
* `p1_eq_scaled_cohort`: the scaled flows obey the cohort recursion with weights `w̃_i`.
* `p1_eq_realize_D`, `p1_eq_realize_dealer`: any reduced form `(a*, κ*, w̃, r)` with total weight `W` is realized by
  an inventory equilibrium with `D = 1 - κ* W/(1-a*)`, `ā = a* D`, `κ = κ* D`, `w_i = w̃_i (D - r_i)/(D - ā)` and
  `A = κ* D (1-a*)/V`. Two reduced forms with the same `(a*, κ*, W)` are therefore realized with identical primitives.
* `p1_fragility_feedback_bound`, `p1_fragility_benchmark_bound`: necessary conditions for a positive-impact
  equilibrium with one cohort, `A σ_F² w D ≤ (1-D)(D-r)(D-ā)` and `4 A² σ_F² σ_ξ² ≤ (D-ā)²`.
-/

namespace CurrentMM

open Finset

/-- **The equilibrium price is the paper's closed loop (pathwise).** -/
theorem p1_eq_reduced_form {K : ℕ} (ab κ D Hprev ξ xprev x : ℝ) (r β u : Fin K → ℝ) (hDne : D ≠ 0)
    (hDr : ∀ i, D - r i ≠ 0) (hβ : ∀ i, β i * (D - r i) = κ)
    (hxprev : xprev = -κ * Hprev + ∑ i, β i * u i)
    (hx : D * x = -κ * (ab * Hprev - ∑ i, u i - ξ) + ∑ i, β i * r i * u i) :
    x = ab / D * xprev + κ / D * (ξ + ∑ i, (D - ab) / (D - r i) * u i) := by
  have h1 : ∀ i, κ * ((D - ab) / (D - r i) * u i) = β i * (D - ab) * u i := by
    intro i
    calc κ * ((D - ab) / (D - r i) * u i) = β i * (D - r i) * ((D - ab) / (D - r i) * u i) := by rw [hβ i]
      _ = β i * (D - ab) * u i * ((D - r i) / (D - r i)) := by ring
      _ = β i * (D - ab) * u i := by rw [div_self (hDr i), mul_one]
  have hS : κ * ∑ i, (D - ab) / (D - r i) * u i = ∑ i, β i * (D - ab) * u i := by
    rw [mul_sum]; exact sum_congr rfl fun i _ => h1 i
  have h2 : ∑ i, (κ * u i + β i * r i * u i) = D * ∑ i, β i * u i := by
    rw [mul_sum]; exact sum_congr rfl fun i _ => by have := hβ i; linear_combination (-(u i)) * this
  have e1 : ∑ i, (κ * u i + β i * r i * u i) = κ * ∑ i, u i + ∑ i, β i * r i * u i := by
    rw [sum_add_distrib, mul_sum]
  have e2 : ∑ i, β i * (D - ab) * u i = D * ∑ i, β i * u i - ab * ∑ i, β i * u i := by
    rw [mul_sum, mul_sum, ← sum_sub_distrib]; exact sum_congr rfl fun i _ => by ring
  have key : D * x = ab * xprev + κ * ξ + ∑ i, β i * (D - ab) * u i := by
    rw [hx, hxprev]
    linear_combination h2 - e1 - e2
  have hx2 : x = (ab * xprev + κ * ξ + κ * ∑ i, (D - ab) / (D - r i) * u i) / D := by
    rw [eq_div_iff hDne]
    linear_combination key - hS
  rw [hx2]
  ring

/-- The scaled flows follow the cohort recursion with the effective merged weights. -/
theorem p1_eq_scaled_cohort (ab D r w u x : ℝ) :
    (D - ab) / (D - r) * (r * u + w * x) = r * ((D - ab) / (D - r) * u) + ((D - ab) * w / (D - r)) * x := by
  ring

/-- **Realization, cohort equation.** With `D = 1 - κ* W/(1-a*)`, `ā = a* D`, `κ = κ* D` and
`w_i = w̃_i (D - r_i)/(D - ā)`, the equilibrium condition `D + κ Σ w_i/(D - r_i) = 1` holds. -/
theorem p1_eq_realize_D {K : ℕ} (as ks W D : ℝ) (wt r : Fin K → ℝ) (hW : ∑ i, wt i = W) (ha : 1 - as ≠ 0)
    (hD0 : D ≠ 0) (hDdef : D = 1 - ks * W / (1 - as)) (hDr : ∀ i, D - r i ≠ 0) :
    D + (ks * D) * ∑ i, (wt i * (D - r i) / (D - as * D)) / (D - r i) = 1 := by
  have hDa : D - as * D ≠ 0 := by
    have : D - as * D = D * (1 - as) := by ring
    rw [this]; exact mul_ne_zero hD0 ha
  have hterm : ∀ i, (wt i * (D - r i) / (D - as * D)) / (D - r i) = wt i / (D - as * D) := by
    intro i
    rw [div_div, div_eq_div_iff (mul_ne_zero hDa (hDr i)) hDa]
    ring
  rw [sum_congr rfl fun i _ => hterm i, ← sum_div, hW]
  have hfac : D - as * D = D * (1 - as) := by ring
  rw [hfac]
  have hkW : ks * W / (1 - as) = 1 - D := by rw [hDdef]; ring
  have hc : ks * D * (W / (D * (1 - as))) = ks * W / (1 - as) := by
    calc ks * D * (W / (D * (1 - as))) = ks * W / (1 - as) * (D / D) := by ring
      _ = ks * W / (1 - as) := by rw [div_self hD0, mul_one]
  rw [hc, hkW]
  ring

/-- **Realization, dealer equation.** With `A = κ* D (1-a*)/V`, `κ (D - ā) = A V D` holds. -/
theorem p1_eq_realize_dealer (as ks D V : ℝ) (hV : V ≠ 0) :
    (ks * D) * (D - as * D) = (ks * D * (1 - as) / V) * V * D := by
  calc (ks * D) * (D - as * D) = (ks * D * (1 - as)) * D * (V / V) := by rw [div_self hV]; ring
    _ = (ks * D * (1 - as) / V) * V * D := by ring

/-- **Fragility, feedback bound.** One cohort with weight `w > 0`. In the multiplied forms
`(D-1)(D-r) + κ w = 0` (that is, `D + κ w/(D-r) = 1`) and `κ (D-ā) D = A (σ_F² D² + κ² σ_ξ²)`, a positive-impact
equilibrium satisfies `A σ_F² w D ≤ (1-D)(D-r)(D-ā)`. -/
theorem p1_fragility_feedback_bound (A sF2 sX2 ab w r κ D : ℝ) (hw : 0 < w) (hD : 0 < D) (hA : 0 ≤ A)
    (hsX : 0 ≤ sX2) (hDeq : (D - 1) * (D - r) + κ * w = 0)
    (hdealer : κ * (D - ab) * D = A * (sF2 * D ^ 2 + κ ^ 2 * sX2)) :
    A * sF2 * w * D ≤ (1 - D) * (D - r) * (D - ab) := by
  have hkw : κ * w = (1 - D) * (D - r) := by linear_combination hDeq
  have hpos : 0 ≤ A * (κ ^ 2 * sX2) := mul_nonneg hA (mul_nonneg (sq_nonneg κ) hsX)
  have h1 : A * sF2 * D ^ 2 ≤ κ * (D - ab) * D := by nlinarith [hdealer, hpos]
  have h2 : A * sF2 * D ^ 2 * w ≤ κ * w * (D - ab) * D := by nlinarith [mul_le_mul_of_nonneg_right h1 hw.le]
  rw [hkw] at h2
  have h3 : (A * sF2 * w * D) * D ≤ ((1 - D) * (D - r) * (D - ab)) * D := by linarith [h2]
  exact le_of_mul_le_mul_right h3 hD

/-- **Fragility, benchmark bound.** Any equilibrium with `κ D ≠ 0` and nonnegative primitives satisfies
`4 A² σ_F² σ_ξ² ≤ (D-ā)²`; at `D = 1` this is the no-feedback existence condition. -/
theorem p1_fragility_benchmark_bound (A sF2 sX2 ab κ D : ℝ) (hκD : κ * D ≠ 0) (hsF : 0 ≤ sF2) (hsX : 0 ≤ sX2)
    (hdealer : κ * (D - ab) * D = A * (sF2 * D ^ 2 + κ ^ 2 * sX2)) :
    4 * A ^ 2 * sF2 * sX2 ≤ (D - ab) ^ 2 := by
  have e : (κ * (D - ab) * D) ^ 2 = A ^ 2 * (sF2 * D ^ 2 + κ ^ 2 * sX2) ^ 2 := by rw [hdealer]; ring
  have amgm : 4 * (sF2 * D ^ 2) * (κ ^ 2 * sX2) ≤ (sF2 * D ^ 2 + κ ^ 2 * sX2) ^ 2 := by
    nlinarith [sq_nonneg (sF2 * D ^ 2 - κ ^ 2 * sX2)]
  have h0 := mul_le_mul_of_nonneg_left amgm (sq_nonneg A)
  have h : (4 * A ^ 2 * sF2 * sX2) * (κ * D) ^ 2 ≤ (D - ab) ^ 2 * (κ * D) ^ 2 := by
    have l : (4 * A ^ 2 * sF2 * sX2) * (κ * D) ^ 2 = A ^ 2 * (4 * (sF2 * D ^ 2) * (κ ^ 2 * sX2)) := by ring
    have rr : (D - ab) ^ 2 * (κ * D) ^ 2 = (κ * (D - ab) * D) ^ 2 := by ring
    rw [l, rr, e]; exact h0
  have hp : 0 < (κ * D) ^ 2 := lt_of_le_of_ne (sq_nonneg _) (Ne.symm (pow_ne_zero 2 hκD))
  exact le_of_mul_le_mul_right h hp

end CurrentMM
