import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
# Paper 1, equilibrium section: stability, necessity, rents optimum, post-halt kernels

* `p1_eq_stability_K`: with positive weights and `D > max r_i`, the equilibrium cohort equation
  `κ Σ g_i = 1 - D` (`g_i = w_i/(D - r_i) > 0`, `D < 1`) gives `κ Σ g_i/(1 - r_i) < 1`. Together with the Perron–Frobenius
  criterion for the positive closed loop (on paper), this is the stability of every such equilibrium (Theorem 4.3(iv)).
* `p1_eq_effective_stability_iff`: that inequality is exactly the closed-loop criterion
  `a* + κ* Σ w̃_i/(1 - r_i) < 1` at the effective parameters of Theorem 4.2.
* `p1_inventory_necessity`: if the conjectured price law satisfies the dealers' first-order condition for **every**
  state, its coefficients satisfy `β_i (D - r_i) = κ` and `κ (D - ā) = A V D` (the necessity direction of
  Theorem 4.1(i)).
* `p1_rents_symmetrize`, `p1_rents_optimum`, `p1_rents_value`: Theorem S28.1(i). The insider's objective depends on `A`
  only through `Q = (A + Aᵀ)/2`; if `Q` is positive semidefinite and `Q b* = ½ 1`, then `b*` is optimal and the value
  is `½ 1ᵀ b* = ¼ 1ᵀ Q⁻¹ 1`.
* `p1_halt_kernel_gap`: Theorem S28.2(iii), the post-halt kernels differ by `W/4` at lag 0 for every spacing.
-/

namespace CurrentMM

open Finset

/-- **Stability of every positive multi-cohort equilibrium (inequality core).** -/
theorem p1_eq_stability_K {K : ℕ} (κ D : ℝ) (r g : Fin K → ℝ) (hκ : 0 < κ) (hD1 : D < 1)
    (hr : ∀ i, r i < D) (hg : ∀ i, 0 < g i) (heq : κ * ∑ i, g i = 1 - D) :
    κ * ∑ i, g i / (1 - r i) < 1 := by
  rcases Nat.eq_zero_or_pos K with hK | hK
  · subst hK; simp
  · have h1 : 0 < 1 - D := by linarith
    have hlt : ∑ i, g i / (1 - r i) < ∑ i, g i / (1 - D) := by
      apply Finset.sum_lt_sum_of_nonempty ⟨⟨0, hK⟩, Finset.mem_univ _⟩
      intro i _
      have h2 : 1 - D < 1 - r i := by linarith [hr i]
      have h3 : 0 < 1 - r i := by linarith
      first | rw [div_lt_div_iff₀ h3 h1] | rw [div_lt_div_iff h3 h1]
      nlinarith [hg i]
    have hs : ∑ i, g i / (1 - D) = (∑ i, g i) / (1 - D) := by
      simp only [div_eq_mul_inv]; rw [← sum_mul]
    have hfin : κ * ((∑ i, g i) / (1 - D)) = 1 := by
      rw [mul_div_assoc', heq, div_self (ne_of_gt h1)]
    calc κ * ∑ i, g i / (1 - r i) < κ * ∑ i, g i / (1 - D) := mul_lt_mul_of_pos_left hlt hκ
      _ = 1 := by rw [hs, hfin]

/-- The inequality of `p1_eq_stability_K` is the closed-loop stability criterion at the effective parameters
`a* = ā/D`, `κ* = κ/D`, `w̃_i = (D - ā) g_i` (with `g_i = w_i/(D - r_i)`). -/
theorem p1_eq_effective_stability_iff {K : ℕ} (κ D ab : ℝ) (r g : Fin K → ℝ) (hD : 0 < D) (hDa : ab < D)
    (hr : ∀ i, 1 - r i ≠ 0) :
    (ab / D + κ / D * ∑ i, (D - ab) * g i / (1 - r i) < 1) ↔ κ * ∑ i, g i / (1 - r i) < 1 := by
  have hsum : ∑ i, (D - ab) * g i / (1 - r i) = (D - ab) * ∑ i, g i / (1 - r i) := by
    rw [mul_sum]; exact sum_congr rfl fun i _ => by ring
  rw [hsum]
  set S := ∑ i, g i / (1 - r i)
  have hpos : 0 < D - ab := by linarith
  constructor
  · intro h
    have h' : ab + κ * ((D - ab) * S) < D := by
      have := mul_lt_mul_of_pos_left h hD
      have e : D * (ab / D + κ / D * ((D - ab) * S)) = ab + κ * ((D - ab) * S) := by
        first | (field_simp; done) | (field_simp; ring)
      linarith [e]
    nlinarith
  · intro h
    have e : D * (ab / D + κ / D * ((D - ab) * S)) = ab + κ * ((D - ab) * S) := by
      first | (field_simp; done) | (field_simp; ring)
    have h2 : ab + κ * ((D - ab) * S) < D := by nlinarith
    by_contra hc
    push_neg at hc
    have := mul_le_mul_of_nonneg_left hc hD.le
    linarith

/-- **Necessity in Theorem 4.1(i).** If, for every inventory `H` and every vector of next cohort trades `v`, the
expected next price `(-κ ā H + Σ (κ + β_i r_i) v_i)/D` minus the current price `-κ H + Σ β_i v_i` equals `A V H`, then
`κ (D - ā) = A V D` and `β_i (D - r_i) = κ` for every `i`. -/
theorem p1_inventory_necessity {K : ℕ} (A V ab κ D : ℝ) (r β : Fin K → ℝ) (hD : D ≠ 0)
    (hall : ∀ (H : ℝ) (v : Fin K → ℝ),
      (-κ * ab * H + ∑ i, (κ + β i * r i) * v i) / D - (-κ * H + ∑ i, β i * v i) = A * V * H) :
    κ * (D - ab) = A * V * D ∧ ∀ i, β i * (D - r i) = κ := by
  constructor
  · have h := hall 1 0
    simp only [Pi.zero_apply, mul_zero, sum_const_zero, add_zero, mul_one] at h
    field_simp at h
    linarith
  · intro i
    have h := hall 0 (Pi.single i 1)
    simp only [Pi.single_apply, mul_ite, mul_one, mul_zero, sum_ite_eq', mem_univ, if_true, zero_add,
      neg_zero, zero_mul, mul_zero] at h
    field_simp at h
    linarith

/-- Quadratic form `vᵀ M v` written with explicit sums. -/
def p1Quad {T : ℕ} (M : Fin T → Fin T → ℝ) (v : Fin T → ℝ) : ℝ := ∑ i, ∑ j, v i * M i j * v j

/-- **Theorem S28.1(i), symmetrization.** `bᵀ A b = bᵀ Q b` with `Q = (A + Aᵀ)/2`. -/
theorem p1_rents_symmetrize {T : ℕ} (A : Fin T → Fin T → ℝ) (b : Fin T → ℝ) :
    p1Quad A b = p1Quad (fun i j => (A i j + A j i) / 2) b := by
  unfold p1Quad
  have hsw : ∑ i, ∑ j, b i * A j i * b j = ∑ i, ∑ j, b i * A i j * b j := by
    rw [Finset.sum_comm]; exact sum_congr rfl fun i _ => sum_congr rfl fun j _ => by ring
  have term : ∀ i j, b i * ((A i j + A j i) / 2) * b j
      = (1 / 2) * (b i * A i j * b j) + (1 / 2) * (b i * A j i * b j) := by
    intro i j; ring
  simp_rw [term, sum_add_distrib, ← mul_sum]
  rw [hsw]; ring

/-- **Theorem S28.1(i), optimum.** If `Q` is symmetric and positive semidefinite and `Q b* = ½ 1`, then `b*`
maximizes `1ᵀ b - bᵀ Q b`. -/
theorem p1_rents_optimum {T : ℕ} (Q : Fin T → Fin T → ℝ) (hsym : ∀ i j, Q i j = Q j i)
    (hpsd : ∀ v, 0 ≤ p1Quad Q v) (bs : Fin T → ℝ) (hb : ∀ i, ∑ j, Q i j * bs j = 1 / 2) (b : Fin T → ℝ) :
    ∑ i, b i - p1Quad Q b ≤ ∑ i, bs i - p1Quad Q bs := by
  have hcross : ∑ i, ∑ j, b i * Q i j * bs j = (∑ i, b i) / 2 := by
    have : ∀ i, ∑ j, b i * Q i j * bs j = b i * (1 / 2) := by
      intro i; rw [← hb i, mul_sum]; exact sum_congr rfl fun j _ => by ring
    rw [sum_congr rfl fun i _ => this i, ← sum_mul]; ring
  have hcross' : ∑ i, ∑ j, bs i * Q i j * b j = (∑ i, b i) / 2 := by
    rw [Finset.sum_comm, ← hcross]
    exact sum_congr rfl fun i _ => sum_congr rfl fun j _ => by rw [hsym j i]; ring
  have hss : p1Quad Q bs = (∑ i, bs i) / 2 := by
    unfold p1Quad
    have : ∀ i, ∑ j, bs i * Q i j * bs j = bs i * (1 / 2) := by
      intro i; rw [← hb i, mul_sum]; exact sum_congr rfl fun j _ => by ring
    rw [sum_congr rfl fun i _ => this i, ← sum_mul]; ring
  have hexp : p1Quad Q (fun i => b i - bs i)
      = p1Quad Q b - ∑ i, ∑ j, b i * Q i j * bs j - ∑ i, ∑ j, bs i * Q i j * b j + p1Quad Q bs := by
    unfold p1Quad
    have : ∀ i j, (b i - bs i) * Q i j * (b j - bs j)
        = b i * Q i j * b j - b i * Q i j * bs j - bs i * Q i j * b j + bs i * Q i j * bs j := by
      intro i j; ring
    simp_rw [this, sum_add_distrib, sum_sub_distrib]
  have h0 := hpsd (fun i => b i - bs i)
  rw [hexp, hcross, hcross', hss] at h0
  rw [hss]
  linarith

/-- **Theorem S28.1(i), value.** At `b*`, the objective equals `½ 1ᵀ b*`. -/
theorem p1_rents_value {T : ℕ} (Q : Fin T → Fin T → ℝ) (bs : Fin T → ℝ) (hb : ∀ i, ∑ j, Q i j * bs j = 1 / 2) :
    ∑ i, bs i - p1Quad Q bs = (∑ i, bs i) / 2 := by
  have hss : p1Quad Q bs = (∑ i, bs i) / 2 := by
    unfold p1Quad
    have : ∀ i, ∑ j, bs i * Q i j * bs j = bs i * (1 / 2) := by
      intro i; rw [← hb i, mul_sum]; exact sum_congr rfl fun j _ => by ring
    rw [sum_congr rfl fun i _ => this i, ← sum_mul]; ring
  rw [hss]; ring

/-- **Theorem S28.2(iii).** After the largest cohort is halted, the Gauss kernel is `(W/2)(c - dσ)^m` and the Radau
kernel `(W/4)(c - d)^m`; at lag 0 they differ by `W/4`, whatever the spacing `d`. -/
theorem p1_halt_kernel_gap (W c d σ : ℝ) :
    W / 2 * (c - d * σ) ^ 0 - W / 4 * (c - d) ^ 0 = W / 4 := by
  simp only [pow_zero]; ring

end CurrentMM
