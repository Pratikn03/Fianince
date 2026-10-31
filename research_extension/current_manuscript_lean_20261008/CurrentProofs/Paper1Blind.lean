import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FinCases

/-!
# Paper 1, Theorem `thm:blind` (spectral blindness)

For `0 < λ₂ < λ₁ < 1`, one-step price variance `s₁ > 0` and stationary price variance `V > s₁/(1-λ₁²)`, the
two-state markets `J_θ = [[λ₁, θ], [0, λ₂]]` with shock covariance `diag(s₁, s₂(θ))`, `θ ≠ 0`, all have
eigenvalues `λ₁, λ₂`, one-step price variance `s₁`, and stationary price variance exactly `V` (the Lyapunov
equation `Σ = J Σ Jᵀ + S` has a unique solution, given explicitly), while the price row of `J_θ` has an entry
`θ`, so the worst-case transient gain is unbounded in `θ`.
-/

namespace CurrentMM

open Matrix

/-- The spectral-blindness family. -/
def blindJ (l1 l2 θ : ℝ) : Matrix (Fin 2) (Fin 2) ℝ := !![l1, θ; 0, l2]

/-- The shock variance of the second state that keeps the stationary price variance at `V`. -/
noncomputable def blindS2 (l1 l2 s1 V θ : ℝ) : ℝ :=
  (V * (1 - l1 ^ 2) - s1) * (1 - l2 ^ 2) * (1 - l1 * l2) / (θ ^ 2 * (1 + l1 * l2))

/-- Shock covariance `diag(s₁, s₂(θ))`. -/
noncomputable def blindS (l1 l2 s1 V θ : ℝ) : Matrix (Fin 2) (Fin 2) ℝ :=
  !![s1, 0; 0, blindS2 l1 l2 s1 V θ]

/-- Stationary variance of the second state. -/
noncomputable def blindVy (l1 l2 s1 V θ : ℝ) : ℝ := blindS2 l1 l2 s1 V θ / (1 - l2 ^ 2)

/-- Stationary covariance of price and second state. -/
noncomputable def blindC (l1 l2 s1 V θ : ℝ) : ℝ := θ * l2 * blindVy l1 l2 s1 V θ / (1 - l1 * l2)

/-- The stationary covariance, explicitly. -/
noncomputable def blindSigma (l1 l2 s1 V θ : ℝ) : Matrix (Fin 2) (Fin 2) ℝ :=
  !![V, blindC l1 l2 s1 V θ; blindC l1 l2 s1 V θ, blindVy l1 l2 s1 V θ]

/-- The Lyapunov equation for a symmetric `2 × 2` matrix reduces to three scalar equations. -/
theorem p1_blind_lyapunov_of_scalar (l1 l2 θ s1 s2 V c vy : ℝ)
    (e00 : V = l1 ^ 2 * V + 2 * l1 * θ * c + θ ^ 2 * vy + s1)
    (e01 : c = l1 * l2 * c + θ * l2 * vy) (e11 : vy = l2 ^ 2 * vy + s2) :
    !![V, c; c, vy] = blindJ l1 l2 θ * !![V, c; c, vy] * (blindJ l1 l2 θ)ᵀ + !![s1, 0; 0, s2] := by
  ext i j
  fin_cases i <;> fin_cases j <;> simp [blindJ, mul_apply, Matrix.vecMul, dotProduct, Fin.sum_univ_two, Matrix.transpose_apply] <;> linarith

theorem p1_blind_eigenvalues (l1 l2 θ z : ℝ) :
    (blindJ l1 l2 θ - z • (1 : Matrix (Fin 2) (Fin 2) ℝ)).det = (l1 - z) * (l2 - z) := by
  simp [blindJ, det_fin_two]

theorem p1_blind_one_step_variance (l1 l2 s1 V θ : ℝ) : blindS l1 l2 s1 V θ 0 0 = s1 := by
  simp [blindS]

theorem p1_blind_s2_nonneg (l1 l2 s1 V θ : ℝ) (h2 : 0 < l2) (h21 : l2 < l1) (h1 : l1 < 1)
    (hV : s1 / (1 - l1 ^ 2) ≤ V) : 0 ≤ blindS2 l1 l2 s1 V θ := by
  have hl1 : 0 < 1 - l1 ^ 2 := by nlinarith
  have hR : 0 ≤ V * (1 - l1 ^ 2) - s1 := by
    rw [div_le_iff₀ hl1] at hV; linarith
  unfold blindS2
  apply div_nonneg
  · apply mul_nonneg (mul_nonneg hR (by nlinarith)) (by nlinarith)
  · exact mul_nonneg (sq_nonneg _) (by nlinarith)

/-- **The explicit covariance solves the Lyapunov equation**, and its price entry is `V`. -/
theorem p1_blind_lyapunov (l1 l2 s1 V θ : ℝ) (h2 : 0 < l2) (h21 : l2 < l1) (h1 : l1 < 1) (hθ : θ ≠ 0) :
    blindSigma l1 l2 s1 V θ = blindJ l1 l2 θ * blindSigma l1 l2 s1 V θ * (blindJ l1 l2 θ)ᵀ +
      blindS l1 l2 s1 V θ ∧ blindSigma l1 l2 s1 V θ 0 0 = V := by
  have hl2 : 1 - l2 ^ 2 ≠ 0 := by nlinarith
  have hl12 : 1 - l1 * l2 ≠ 0 := by nlinarith
  have hp : 1 + l1 * l2 ≠ 0 := by nlinarith
  have hθ2 : θ ^ 2 ≠ 0 := pow_ne_zero 2 hθ
  have hl21 : 1 - l2 * l1 ≠ 0 := by nlinarith
  refine ⟨?_, by simp [blindSigma]⟩
  have e11 : blindVy l1 l2 s1 V θ = l2 ^ 2 * blindVy l1 l2 s1 V θ + blindS2 l1 l2 s1 V θ := by
    unfold blindVy; field_simp; ring
  have e01 : blindC l1 l2 s1 V θ = l1 * l2 * blindC l1 l2 s1 V θ + θ * l2 * blindVy l1 l2 s1 V θ := by
    unfold blindC; field_simp; ring
  have e00 : V = l1 ^ 2 * V + 2 * l1 * θ * blindC l1 l2 s1 V θ + θ ^ 2 * blindVy l1 l2 s1 V θ + s1 := by
    unfold blindC blindVy blindS2; field_simp; ring
  exact p1_blind_lyapunov_of_scalar l1 l2 θ s1 _ V _ _ e00 e01 e11

/-- **The Lyapunov equation has only one solution**, so `V` is *the* stationary price variance. -/
theorem p1_blind_lyapunov_unique (l1 l2 θ : ℝ) (S M1 M2 : Matrix (Fin 2) (Fin 2) ℝ)
    (h2 : 0 < l2) (h21 : l2 < l1) (h1 : l1 < 1)
    (hs1 : M1 = blindJ l1 l2 θ * M1 * (blindJ l1 l2 θ)ᵀ + S)
    (hs2 : M2 = blindJ l1 l2 θ * M2 * (blindJ l1 l2 θ)ᵀ + S) : M1 = M2 := by
  set D := M1 - M2 with hD
  have hDeq : D = blindJ l1 l2 θ * D * (blindJ l1 l2 θ)ᵀ := by
    rw [hD, Matrix.mul_sub, Matrix.sub_mul]
    conv_lhs => rw [hs1, hs2]
    abel
  have e : ∀ i j, D i j = (blindJ l1 l2 θ * D * (blindJ l1 l2 θ)ᵀ) i j := fun i j => by
    rw [← hDeq]
  have e11 := e 1 1
  have e01 := e 0 1
  have e10 := e 1 0
  have e00 := e 0 0
  simp [blindJ, mul_apply, Matrix.vecMul, dotProduct, Fin.sum_univ_two, Matrix.transpose_apply] at e11 e01 e10 e00
  have d11 : D 1 1 = 0 := by
    have : D 1 1 * (1 - l2 ^ 2) = 0 := by nlinarith
    rcases mul_eq_zero.mp this with h | h
    · exact h
    · nlinarith
  rw [d11] at e01 e10 e00
  have d01 : D 0 1 = 0 := by
    have : D 0 1 * (1 - l1 * l2) = 0 := by nlinarith
    rcases mul_eq_zero.mp this with h | h
    · exact h
    · nlinarith
  have d10 : D 1 0 = 0 := by
    have : D 1 0 * (1 - l1 * l2) = 0 := by nlinarith
    rcases mul_eq_zero.mp this with h | h
    · exact h
    · nlinarith
  rw [d01, d10] at e00
  have d00 : D 0 0 = 0 := by
    have : D 0 0 * (1 - l1 ^ 2) = 0 := by nlinarith
    rcases mul_eq_zero.mp this with h | h
    · exact h
    · nlinarith
  have hDz : D = 0 := by
    ext i j; fin_cases i <;> fin_cases j <;> simp [d00, d01, d10, d11]
  rw [hD] at hDz
  exact sub_eq_zero.mp hDz

/-- **Theorem `thm:blind`.** Every member of the family (for `θ ≠ 0`) has eigenvalues `λ₁, λ₂`, one-step price
variance `s₁` and unique stationary price variance `V`, with a valid (nonnegative) shock covariance, while the
price row of `J_θ` contains `θ`: the transient gain exceeds any bound `M` once `|θ| > M`. -/
theorem p1_thm_blind (l1 l2 s1 V : ℝ) (h2 : 0 < l2) (h21 : l2 < l1) (h1 : l1 < 1)
    (hV : s1 / (1 - l1 ^ 2) ≤ V) (M : ℝ) :
    ∃ θ : ℝ, θ ≠ 0 ∧
      (∀ z, (blindJ l1 l2 θ - z • (1 : Matrix (Fin 2) (Fin 2) ℝ)).det = (l1 - z) * (l2 - z)) ∧
      blindS l1 l2 s1 V θ 0 0 = s1 ∧ 0 ≤ blindS2 l1 l2 s1 V θ ∧
      (∀ M' : Matrix (Fin 2) (Fin 2) ℝ,
        M' = blindJ l1 l2 θ * M' * (blindJ l1 l2 θ)ᵀ + blindS l1 l2 s1 V θ → M' 0 0 = V) ∧
      M < |(blindJ l1 l2 θ ^ 1) 0 1| := by
  refine ⟨|M| + 1, by positivity, fun z => p1_blind_eigenvalues _ _ _ z,
    p1_blind_one_step_variance _ _ _ _ _, p1_blind_s2_nonneg _ _ _ _ _ h2 h21 h1 hV, ?_, ?_⟩
  · intro M' hM'
    have hθ : |M| + 1 ≠ 0 := by positivity
    obtain ⟨hly, hV'⟩ := p1_blind_lyapunov l1 l2 s1 V (|M| + 1) h2 h21 h1 hθ
    rw [p1_blind_lyapunov_unique l1 l2 (|M| + 1) _ M' _ h2 h21 h1 hM' hly, hV']
  · simp only [pow_one, blindJ, of_apply, cons_val', cons_val_zero, cons_val_one, empty_val',
      cons_val_fin_one, head_cons]
    rw [abs_of_pos (by positivity)]
    linarith [le_abs_self M]

end CurrentMM
