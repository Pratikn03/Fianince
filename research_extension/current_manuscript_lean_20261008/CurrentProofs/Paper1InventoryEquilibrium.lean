import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Algebra.QuadraticDiscriminant
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Ring

/-!
# Paper 1, Theorem E4: equilibrium price impact with inventory-averse dealers

Dealers hold inventory `H`, lay off a share `1 - ā` each period, and are myopic CARA with risk aversion `A`. Their
first-order condition is `A V H_t = E_t x_{t+1} - x_t`. The cohorts trade `u_{i,t+1} = r_i u_{i,t} + w_i x_t`.

The candidate equilibrium price law is `x_t = -κ H_t + Σ_i β_i u_{i,t+1}`, with
`β_i = κ/(D - r_i)`, `D = 1 - Σ_i β_i w_i` and `κ (D - ā) = A V D`.

* `p1_inventory_price_law`: from the implicit form `D x = -κ H + Σ β_i r_i u_i` of the equilibrium price, the price
  satisfies `x = -κ H + Σ β_i u'_i`, where `u'_i = r_i u_i + w_i x`.
* `p1_inventory_foc`: with the next-period expected price, i.e. the same law with the next shock set to zero, the
  dealers' first-order condition `x' - x = A V H` holds **for every state**. So the candidate is an equilibrium of the
  stated class.
* `p1_inventory_innovation`: the next-period price moves with the next flow shock `ξ` with coefficient `κ/D`,
  which pins down `V = σ_F² + κ² σ_ξ²/D²`.
* `p1_inventory_benchmark`: without feedback (`D = 1`), `κ(1-ā) = A(σ_F² + κ² σ_ξ²)` has a real solution iff
  `(1-ā)² ≥ 4A²σ_F²σ_ξ²`.
-/

namespace CurrentMM

open Finset

/-- The equilibrium price, in implicit form, satisfies the conjectured law. -/
theorem p1_inventory_price_law {K : ℕ} (κ D : ℝ) (w r β u : Fin K → ℝ) (H x : ℝ)
    (hD : D = 1 - ∑ i, β i * w i) (hx : D * x = -κ * H + ∑ i, β i * r i * u i) :
    x = -κ * H + ∑ i, β i * (r i * u i + w i * x) := by
  have e : ∑ i, β i * (r i * u i + w i * x) = ∑ i, β i * r i * u i + (∑ i, β i * w i) * x := by
    rw [sum_mul, ← sum_add_distrib]; exact sum_congr rfl fun i _ => by ring
  rw [e]
  have h1 : (∑ i, β i * w i) = 1 - D := by linarith
  rw [h1]
  linear_combination hx

/-- Summation step used in `p1_inventory_foc`, stated for an arbitrary function `v` so that rewriting cannot look
inside a `let`-bound definition. -/
theorem p1_inventory_sum_aux {K : ℕ} (κ ab D H : ℝ) (r β v : Fin K → ℝ)
    (hc : ∀ i, κ * v i + β i * r i * v i = D * (β i * v i)) :
    -κ * (ab * H - ∑ i, v i) + ∑ i, β i * r i * v i = -κ * ab * H + D * ∑ i, β i * v i := by
  have hS : ∑ i, (κ * v i + β i * r i * v i) = D * ∑ i, β i * v i := by
    rw [mul_sum]; exact sum_congr rfl fun i _ => hc i
  have e : ∑ i, (κ * v i + β i * r i * v i) = κ * ∑ i, v i + ∑ i, β i * r i * v i := by
    rw [sum_add_distrib, mul_sum]
  linear_combination hS - e

/-- **The dealers' first-order condition holds in every state.** -/
theorem p1_inventory_foc {K : ℕ} (A V ab κ D : ℝ) (w r β u : Fin K → ℝ) (Hprev ξ : ℝ) (hDne : D ≠ 0)
    (hβ : ∀ i, β i * (D - r i) = κ) (hD : D = 1 - ∑ i, β i * w i) (hκ : κ * (D - ab) = A * V * D) :
    let H := ab * Hprev - ∑ i, u i - ξ
    let x := (-κ * H + ∑ i, β i * r i * u i) / D
    let u' := fun i => r i * u i + w i * x
    let H' := ab * H - ∑ i, u' i
    let x' := (-κ * H' + ∑ i, β i * r i * u' i) / D
    x' - x = A * V * H := by
  intro H x u' H' x'
  have hxD : D * x = -κ * H + ∑ i, β i * r i * u i := by
    show D * ((-κ * H + ∑ i, β i * r i * u i) / D) = _
    field_simp
  have hlaw := p1_inventory_price_law κ D w r β u H x hD hxD
  -- κ + β_i r_i = β_i D
  have hcomb : ∀ i, κ * u' i + β i * r i * u' i = D * (β i * u' i) := by
    intro i; have := hβ i; linear_combination (-(u' i)) * this
  have hx'D : D * x' = -κ * H' + ∑ i, β i * r i * u' i := by
    show D * ((-κ * H' + ∑ i, β i * r i * u' i) / D) = _
    field_simp
  have hsum : -κ * H' + ∑ i, β i * r i * u' i = -κ * ab * H + D * ∑ i, β i * u' i :=
    p1_inventory_sum_aux κ ab D H r β u' hcomb
  have hx'D2 : D * x' = -κ * ab * H + D * ∑ i, β i * u' i := hx'D.trans hsum
  have hlaw' : x = -κ * H + ∑ i, β i * u' i := hlaw
  have : D * (x' - x) = D * (A * V * H) := by
    rw [mul_sub, hx'D2, hlaw']
    linear_combination H * hκ
  exact mul_left_cancel₀ hDne this

/-- **Innovation of the next price.** The next-period price loads on the next flow shock with coefficient `κ/D`. -/
theorem p1_inventory_innovation {K : ℕ} (ab κ D : ℝ) (r β u' : Fin K → ℝ) (H ξ' : ℝ) (hDne : D ≠ 0) :
    (-κ * (ab * H - ∑ i, u' i - ξ') + ∑ i, β i * r i * u' i) / D
      - (-κ * (ab * H - ∑ i, u' i) + ∑ i, β i * r i * u' i) / D = κ / D * ξ' := by
  field_simp
  ring

/-- **No-feedback benchmark.** `κ(1-ā) = A(σ_F² + κ²σ_ξ²)` with `A σ_ξ² ≠ 0` has a real solution iff
`(1-ā)² ≥ 4A²σ_F²σ_ξ²`. -/
theorem p1_inventory_benchmark (A sF2 sX2 ab : ℝ) (h : A * sX2 ≠ 0) :
    (∃ κ : ℝ, κ * (1 - ab) = A * (sF2 + κ ^ 2 * sX2)) ↔ 4 * A ^ 2 * sF2 * sX2 ≤ (1 - ab) ^ 2 := by
  have key : ∀ κ : ℝ, κ * (1 - ab) = A * (sF2 + κ ^ 2 * sX2) ↔
      (A * sX2) * (κ * κ) + (-(1 - ab)) * κ + A * sF2 = 0 := by
    intro κ; constructor <;> intro hk <;> linear_combination (-1 : ℝ) * hk
  simp_rw [key]
  constructor
  · rintro ⟨κ, hk⟩
    have := discrim_eq_sq_of_quadratic_eq_zero hk
    unfold discrim at this
    nlinarith [sq_nonneg (2 * (A * sX2) * κ + -(1 - ab))]
  · intro hd
    have hdisc : 0 ≤ discrim (A * sX2) (-(1 - ab)) (A * sF2) := by
      unfold discrim; nlinarith
    obtain ⟨s, hs⟩ : ∃ s, discrim (A * sX2) (-(1 - ab)) (A * sF2) = s * s :=
      ⟨Real.sqrt _, (Real.mul_self_sqrt hdisc).symm⟩
    exact ⟨_, (quadratic_eq_zero_iff h hs _).mpr (Or.inl rfl)⟩

end CurrentMM
