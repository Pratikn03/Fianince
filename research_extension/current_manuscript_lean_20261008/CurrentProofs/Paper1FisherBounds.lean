import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.LinearAlgebra.Matrix.ToLinearEquiv
import Mathlib.LinearAlgebra.Matrix.DotProduct
import Mathlib.Algebra.Order.BigOperators.Ring.Finset

/-!
# Paper 1, Proposition S7.1 (iii), Phases 6–7: two-sided bounds on an inverse-Fisher entry

Let `J` be an `n × p` real observation Jacobian and `F = JᵀJ` (the Fisher matrix of `N(h(θ), σ² I)` up to the factor
`σ⁻²`). When `F` is invertible:

* `p1_fisher_entry_lower`: for every direction `x`, `x_k² ≤ [F⁻¹]_kk ‖J x‖²`. A direction that moves the responses by
  only a little while moving `θ_k` by one unit forces `[F⁻¹]_kk` to be large.
* `p1_fisher_entry_upper`: for every `b` with `Jᵀ b = e_k`, `[F⁻¹]_kk ≤ ‖b‖²`. An explicit linear combination of the
  observations that recovers `θ_k` to first order caps `[F⁻¹]_kk`.
* `p1_gram_isUnit`: `F` is invertible as soon as `J` is injective.

The two inequalities are the Cauchy–Schwarz inequality in `ℝⁿ` applied to `J F⁻¹ e_k`. Together they are the
variational characterization `[F⁻¹]_kk = sup_x x_k² / ‖Jx‖² = min_{Jᵀb = e_k} ‖b‖²`.
-/

namespace CurrentMM

open Matrix Finset

/-- Cauchy–Schwarz for the dot product. -/
theorem p1_dot_sq_le {n : ℕ} (x y : Fin n → ℝ) : (x ⬝ᵥ y) ^ 2 ≤ (x ⬝ᵥ x) * (y ⬝ᵥ y) := by
  have h := Finset.sum_mul_sq_le_sq_mul_sq Finset.univ x y
  simpa only [dotProduct, sq] using h

theorem p1_dot_self_nonneg {n : ℕ} (x : Fin n → ℝ) : 0 ≤ x ⬝ᵥ x := by
  simp only [dotProduct]
  exact Finset.sum_nonneg fun i _ => mul_self_nonneg _

/-- `(J a) ⬝ (J x) = ((JᵀJ) a) ⬝ x`. -/
theorem p1_gram_dot {n p : ℕ} (J : Matrix (Fin n) (Fin p) ℝ) (a x : Fin p → ℝ) :
    (J *ᵥ a) ⬝ᵥ (J *ᵥ x) = ((Jᵀ * J) *ᵥ a) ⬝ᵥ x := by
  rw [Matrix.dotProduct_mulVec, ← Matrix.mulVec_transpose, Matrix.mulVec_mulVec]

/-- The `k`-th column of `F⁻¹`. -/
theorem p1_fisher_col {n p : ℕ} (J : Matrix (Fin n) (Fin p) ℝ) (hJ : IsUnit (Jᵀ * J).det) (k : Fin p) :
    ((Jᵀ * J) *ᵥ ((Jᵀ * J)⁻¹ *ᵥ Pi.single k 1) = Pi.single k 1) ∧
    ((Jᵀ * J)⁻¹ *ᵥ Pi.single k 1) k = (Jᵀ * J)⁻¹ k k := by
  constructor
  · rw [Matrix.mulVec_mulVec, Matrix.mul_nonsing_inv _ hJ, Matrix.one_mulVec]
  · rw [Matrix.mulVec_single_one, Matrix.col_apply]

/-- `‖J F⁻¹ e_k‖² = [F⁻¹]_kk`. -/
theorem p1_fisher_col_norm {n p : ℕ} (J : Matrix (Fin n) (Fin p) ℝ) (hJ : IsUnit (Jᵀ * J).det) (k : Fin p) :
    (J *ᵥ ((Jᵀ * J)⁻¹ *ᵥ Pi.single k 1)) ⬝ᵥ (J *ᵥ ((Jᵀ * J)⁻¹ *ᵥ Pi.single k 1)) = (Jᵀ * J)⁻¹ k k := by
  obtain ⟨h1, h2⟩ := p1_fisher_col J hJ k
  rw [p1_gram_dot, h1, single_dotProduct, one_mul, h2]

/-- **Lower bound.** `x_k² ≤ [F⁻¹]_kk ‖J x‖²` for every direction `x`. -/
theorem p1_fisher_entry_lower {n p : ℕ} (J : Matrix (Fin n) (Fin p) ℝ) (hJ : IsUnit (Jᵀ * J).det) (k : Fin p)
    (x : Fin p → ℝ) : x k ^ 2 ≤ (Jᵀ * J)⁻¹ k k * ((J *ᵥ x) ⬝ᵥ (J *ᵥ x)) := by
  have h1 := (p1_fisher_col J hJ k).1
  have e1 : (J *ᵥ ((Jᵀ * J)⁻¹ *ᵥ Pi.single k 1)) ⬝ᵥ (J *ᵥ x) = x k := by
    rw [p1_gram_dot, h1, single_dotProduct, one_mul]
  have cs := p1_dot_sq_le (J *ᵥ ((Jᵀ * J)⁻¹ *ᵥ Pi.single k 1)) (J *ᵥ x)
  rw [e1, p1_fisher_col_norm J hJ k] at cs
  exact cs

/-- **Upper bound.** `[F⁻¹]_kk ≤ ‖b‖²` for every `b` with `Jᵀ b = e_k`. -/
theorem p1_fisher_entry_upper {n p : ℕ} (J : Matrix (Fin n) (Fin p) ℝ) (hJ : IsUnit (Jᵀ * J).det) (k : Fin p)
    (b : Fin n → ℝ) (hb : Jᵀ *ᵥ b = Pi.single k 1) : (Jᵀ * J)⁻¹ k k ≤ b ⬝ᵥ b := by
  have h2 := (p1_fisher_col J hJ k).2
  have e2 := p1_fisher_col_norm J hJ k
  have e3 : (J *ᵥ ((Jᵀ * J)⁻¹ *ᵥ Pi.single k 1)) ⬝ᵥ b = (Jᵀ * J)⁻¹ k k := by
    rw [dotProduct_comm, Matrix.dotProduct_mulVec, ← Matrix.mulVec_transpose, hb, single_dotProduct, one_mul, h2]
  have cs := p1_dot_sq_le (J *ᵥ ((Jᵀ * J)⁻¹ *ᵥ Pi.single k 1)) b
  rw [e3, e2] at cs
  have hnn : 0 ≤ (Jᵀ * J)⁻¹ k k := by
    rw [← e2]; exact p1_dot_self_nonneg _
  have hbb := p1_dot_self_nonneg b
  rcases hnn.eq_or_lt with h0 | hpos
  · rw [← h0]; exact hbb
  · exact le_of_mul_le_mul_left (by rw [← pow_two]; exact cs) hpos

/-- **`JᵀJ` is invertible when `J` is injective.** -/
theorem p1_gram_isUnit {n p : ℕ} (J : Matrix (Fin n) (Fin p) ℝ) (hinj : ∀ x, J *ᵥ x = 0 → x = 0) :
    IsUnit (Jᵀ * J).det := by
  rw [isUnit_iff_ne_zero]
  intro hdet
  obtain ⟨x, hx, hFx⟩ := (Matrix.exists_mulVec_eq_zero_iff (M := Jᵀ * J)).mpr hdet
  apply hx
  apply hinj
  have h : (J *ᵥ x) ⬝ᵥ (J *ᵥ x) = 0 := by rw [p1_gram_dot, hFx, zero_dotProduct]
  exact dotProduct_self_eq_zero.mp h

end CurrentMM
