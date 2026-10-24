import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity

/-!
# Deterministic half of Theorem `thm:dich`(iv): weak duality and the affine interval's bias

Measures are finite positive atomic measures: atoms `r j` with masses `m j ≥ 0`.  The taps of a
measure are `k t = ∑ⱼ m j * r j ^ t`, the question is `F = ∑ⱼ m j * g (r j)`, and a coefficient
vector `c : Fin L → ℝ` defines the polynomial `p r = ∑ₜ c t * r ^ t` and the residual `h = g - p`.

* `thesis_modulus_tap_identity`: `F - ∑ₜ c t * k t = ∑ⱼ m j * h (r j)`.
* `thesis_modulus_weak_duality`: for two measures of mass at most `B`, with `h ≤ U` on the atoms of
  the first and `-h ≤ V` on the atoms of the second (`U, V ≥ 0`), and with `∑ c² ≤ R²` and
  `∑ (Δk)² ≤ D²`, the answers differ by at most `B (U + V) + R D`.  This is the inequality
  `ω_L(δ) ≤ δ ‖c‖₂ + B ψ(g - p_c)` of the thesis, for atomic measures.
* `thesis_modulus_affine_bias`: the affine estimate `∑ₜ c t * k t + B (U - V) / 2` is within
  `B (U + V) / 2` of the answer for every measure of mass at most `B` whose residual lies in `[-V, U]`.

Sion's minimax theorem (the reverse inequality), Gaussian coverage and the lower bound are written
proofs.
-/

namespace CurrentMM

open scoped BigOperators

/-- The answer minus the coefficient-weighted taps is the residual integrated against the measure. -/
theorem thesis_modulus_tap_identity {n L : ℕ} (g : ℝ → ℝ) (c : Fin L → ℝ) (r m : Fin n → ℝ) :
    (∑ j, m j * g (r j)) - ∑ t, c t * (∑ j, m j * r j ^ (t : ℕ))
      = ∑ j, m j * (g (r j) - ∑ t, c t * r j ^ (t : ℕ)) := by
  have hswap : ∑ t, c t * (∑ j, m j * r j ^ (t : ℕ)) = ∑ j, m j * ∑ t, c t * r j ^ (t : ℕ) := by
    simp_rw [Finset.mul_sum]
    rw [Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro j _
    apply Finset.sum_congr rfl
    intro t _
    ring
  rw [hswap, ← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro j _
  ring

/-- Cauchy–Schwarz in the form used for the noise term: `∑ c Δ ≤ R D`. -/
theorem thesis_modulus_cs {L : ℕ} (c d : Fin L → ℝ) (R D : ℝ) (hR : 0 ≤ R) (hD : 0 ≤ D)
    (hc : ∑ t, c t ^ 2 ≤ R ^ 2) (hd : ∑ t, d t ^ 2 ≤ D ^ 2) :
    ∑ t, c t * d t ≤ R * D := by
  have hcs := Finset.sum_mul_sq_le_sq_mul_sq Finset.univ c d
  have hprod : (∑ t, c t ^ 2) * (∑ t, d t ^ 2) ≤ R ^ 2 * D ^ 2 :=
    mul_le_mul hc hd (Finset.sum_nonneg (fun t _ => sq_nonneg (d t))) (sq_nonneg R)
  have hsq : (∑ t, c t * d t) ^ 2 ≤ (R * D) ^ 2 := by nlinarith
  have hRD : 0 ≤ R * D := mul_nonneg hR hD
  nlinarith [sq_nonneg (∑ t, c t * d t - R * D), sq_nonneg (∑ t, c t * d t + R * D)]

/-- Weak duality for the modulus of continuity, finite atomic measures. -/
theorem thesis_modulus_weak_duality {n₁ n₀ L : ℕ} (g : ℝ → ℝ) (c : Fin L → ℝ)
    (r₁ m₁ : Fin n₁ → ℝ) (r₀ m₀ : Fin n₀ → ℝ) (B U V R D : ℝ)
    (hm₁ : ∀ j, 0 ≤ m₁ j) (hm₀ : ∀ j, 0 ≤ m₀ j)
    (hB₁ : ∑ j, m₁ j ≤ B) (hB₀ : ∑ j, m₀ j ≤ B) (hU : 0 ≤ U) (hV : 0 ≤ V)
    (hup : ∀ j, g (r₁ j) - ∑ t, c t * r₁ j ^ (t : ℕ) ≤ U)
    (hlo : ∀ j, -(g (r₀ j) - ∑ t, c t * r₀ j ^ (t : ℕ)) ≤ V)
    (hR : 0 ≤ R) (hD : 0 ≤ D) (hc : ∑ t, c t ^ 2 ≤ R ^ 2)
    (hd : ∑ t : Fin L, (∑ j, m₁ j * r₁ j ^ (t : ℕ) - ∑ j, m₀ j * r₀ j ^ (t : ℕ)) ^ 2 ≤ D ^ 2) :
    (∑ j, m₁ j * g (r₁ j)) - (∑ j, m₀ j * g (r₀ j)) ≤ B * (U + V) + R * D := by
  have e₁ := thesis_modulus_tap_identity g c r₁ m₁
  have e₀ := thesis_modulus_tap_identity g c r₀ m₀
  have h₁ : ∑ j, m₁ j * (g (r₁ j) - ∑ t, c t * r₁ j ^ (t : ℕ)) ≤ B * U := by
    calc
      ∑ j, m₁ j * (g (r₁ j) - ∑ t, c t * r₁ j ^ (t : ℕ)) ≤ ∑ j, m₁ j * U :=
        Finset.sum_le_sum (fun j _ => mul_le_mul_of_nonneg_left (hup j) (hm₁ j))
      _ = (∑ j, m₁ j) * U := by rw [Finset.sum_mul]
      _ ≤ B * U := mul_le_mul_of_nonneg_right hB₁ hU
  have h₀ : -(∑ j, m₀ j * (g (r₀ j) - ∑ t, c t * r₀ j ^ (t : ℕ))) ≤ B * V := by
    calc
      -(∑ j, m₀ j * (g (r₀ j) - ∑ t, c t * r₀ j ^ (t : ℕ)))
          = ∑ j, m₀ j * (-(g (r₀ j) - ∑ t, c t * r₀ j ^ (t : ℕ))) := by
            rw [← Finset.sum_neg_distrib]
            apply Finset.sum_congr rfl
            intro j _
            ring
      _ ≤ ∑ j, m₀ j * V := Finset.sum_le_sum (fun j _ => mul_le_mul_of_nonneg_left (hlo j) (hm₀ j))
      _ = (∑ j, m₀ j) * V := by rw [Finset.sum_mul]
      _ ≤ B * V := mul_le_mul_of_nonneg_right hB₀ hV
  have hnoise := thesis_modulus_cs c
    (fun t => ∑ j, m₁ j * r₁ j ^ (t : ℕ) - ∑ j, m₀ j * r₀ j ^ (t : ℕ)) R D hR hD hc hd
  have hsplit : ∑ t, c t * (∑ j, m₁ j * r₁ j ^ (t : ℕ) - ∑ j, m₀ j * r₀ j ^ (t : ℕ))
      = ∑ t, c t * (∑ j, m₁ j * r₁ j ^ (t : ℕ)) - ∑ t, c t * (∑ j, m₀ j * r₀ j ^ (t : ℕ)) := by
    rw [← Finset.sum_sub_distrib]
    apply Finset.sum_congr rfl
    intro t _
    ring
  linarith

/-- The affine interval's estimate has bias at most `B (U + V) / 2` for every admissible measure. -/
theorem thesis_modulus_affine_bias {n L : ℕ} (g : ℝ → ℝ) (c : Fin L → ℝ) (r m : Fin n → ℝ)
    (B U V : ℝ) (hm : ∀ j, 0 ≤ m j) (hB : ∑ j, m j ≤ B) (hU : 0 ≤ U) (hV : 0 ≤ V)
    (hup : ∀ j, g (r j) - ∑ t, c t * r j ^ (t : ℕ) ≤ U)
    (hlo : ∀ j, -(g (r j) - ∑ t, c t * r j ^ (t : ℕ)) ≤ V) :
    |(∑ j, m j * g (r j)) - (∑ t, c t * (∑ j, m j * r j ^ (t : ℕ)) + B * (U - V) / 2)|
      ≤ B * (U + V) / 2 := by
  have e := thesis_modulus_tap_identity g c r m
  have hmass : 0 ≤ ∑ j, m j := Finset.sum_nonneg (fun j _ => hm j)
  have hi : ∑ j, m j * (g (r j) - ∑ t, c t * r j ^ (t : ℕ)) ≤ (∑ j, m j) * U := by
    rw [Finset.sum_mul]
    exact Finset.sum_le_sum (fun j _ => mul_le_mul_of_nonneg_left (hup j) (hm j))
  have hj : -((∑ j, m j) * V) ≤ ∑ j, m j * (g (r j) - ∑ t, c t * r j ^ (t : ℕ)) := by
    rw [Finset.sum_mul, ← Finset.sum_neg_distrib]
    apply Finset.sum_le_sum
    intro j _
    have := mul_le_mul_of_nonneg_left (hlo j) (hm j)
    linarith
  have hU' : (∑ j, m j) * U ≤ B * U := mul_le_mul_of_nonneg_right hB hU
  have hV' : (∑ j, m j) * V ≤ B * V := mul_le_mul_of_nonneg_right hB hV
  rw [abs_le]
  constructor <;> linarith

end CurrentMM
