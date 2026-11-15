import Mathlib.Basic.Real.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.LinearCombination

set_option linter.unusedVariables false

/-!
# Paper 1, Propositions 29 & 30: Economic Primitives and Tied Intensity

This module machine-checks:
1. Proposition 29 (`prop:primitives`): Identification in Economic Primitives
   - The Kalman gain function `η(s) = (√(s² + 4s) - s) / 2` for signal-to-noise ratio `s > 0`.
   - `kalmanGain_pos` and `kalmanGain_lt_one`: `0 < η(s) < 1` for all `s > 0`.
   - `kalmanGain_riccati_eq`: `η(s)² + s * η(s) = s`, solving the steady-state Riccati equation.
   - `kalmanGain_strict_mono`: `s₁ < s₂ → η(s₁) < η(s₂)`, proving strict monotonicity.
   - `kalmanGain_injective`: `η(s₁) = η(s₂) → s₁ = s₂`, proving strict invertibility.
   - `primitives_sample_complexity_transfer`: When rate recovery requires `N ≥ C * σ² * (Δη)^{-(4K-2)}`,
     and `Δη ≤ c_plus * Δs` by Lipschitz continuity, signal-to-noise ratio recovery requires
     `N ≥ C * c_plus^{-(4K-2)} * σ² * (Δs)^{-(4K-2)}`.

2. Proposition 30 (`prop:tied`): Intensity Tied to Information Quality
   - `intensity_tied_mass_inversion`: For any known weight function `w(η) > 0` and target atom mass `m ≥ 0`,
     setting desk population mass `n = m / w(η)` yields `n * w(η) = m` identically.
   - `intensity_tied_tap_difference`: The 3-point tap difference between 1 cohort of `2n` desks at `bar_η`
     and 2 cohorts of `n` desks each at `bar_η ± δ` is `n * (g(bar_η + δ) + g(bar_η - δ) - 2 * g(bar_η))`.
   - `quadratic_second_difference_identity` and `intensity_tied_quadratic_tap_gap`: For quadratic `g`,
     the second difference is exactly `2 * A * δ²`, giving a tap gap of `2 * A * n * δ² = O(n * δ²)`.
   - `intensity_tied_sample_bound`: Testing error `≤ 1/4` (requiring `KL ≥ 1/4`) under tap gap `L * n * δ²`
     forces sample size `N ≥ (σ² / (2 * L² * n²)) * δ⁻⁴ = Ω(σ² * δ⁻⁴)`.
-/

namespace CurrentMM

/-! ### Proposition 29: Identification in Economic Primitives (`prop:primitives`) -/

/-- Auxiliary strict monotonicity of the square-root difference function:
    `s₁ < s₂ → √(s₁² + 4s₁) - s₁ < √(s₂² + 4s₂) - s₂` for positive `s₁, s₂`. -/
theorem p1_sqrt_diff_strict_mono (s₁ s₂ : ℝ) (hs₁ : 0 < s₁) (hlt : s₁ < s₂) :
    Real.sqrt (s₁ ^ 2 + 4 * s₁) - s₁ < Real.sqrt (s₂ ^ 2 + 4 * s₂) - s₂ := by
  have hs₂ : 0 < s₂ := by linarith
  have h_disc1 : 0 ≤ s₁ ^ 2 + 4 * s₁ := by positivity
  have h_disc2 : 0 ≤ s₂ ^ 2 + 4 * s₂ := by positivity
  have h_pos1 : 0 < Real.sqrt (s₁ ^ 2 + 4 * s₁) + s₁ := by
    have : 0 < Real.sqrt (s₁ ^ 2 + 4 * s₁) := Real.sqrt_pos.mpr (by positivity)
    linarith
  have h_pos2 : 0 < Real.sqrt (s₂ ^ 2 + 4 * s₂) + s₂ := by
    have : 0 < Real.sqrt (s₂ ^ 2 + 4 * s₂) := Real.sqrt_pos.mpr (by positivity)
    linarith
  have h_prod1 : (Real.sqrt (s₁ ^ 2 + 4 * s₁) - s₁) * (Real.sqrt (s₁ ^ 2 + 4 * s₁) + s₁) = 4 * s₁ := by
    have h_sq := Real.sq_sqrt h_disc1
    linear_combination h_sq
  have h_prod2 : (Real.sqrt (s₂ ^ 2 + 4 * s₂) - s₂) * (Real.sqrt (s₂ ^ 2 + 4 * s₂) + s₂) = 4 * s₂ := by
    have h_sq := Real.sq_sqrt h_disc2
    linear_combination h_sq
  have h_div1 : Real.sqrt (s₁ ^ 2 + 4 * s₁) - s₁ = 4 * s₁ / (Real.sqrt (s₁ ^ 2 + 4 * s₁) + s₁) := by
    exact eq_div_of_mul_eq (ne_of_gt h_pos1) h_prod1
  have h_div2 : Real.sqrt (s₂ ^ 2 + 4 * s₂) - s₂ = 4 * s₂ / (Real.sqrt (s₂ ^ 2 + 4 * s₂) + s₂) := by
    exact eq_div_of_mul_eq (ne_of_gt h_pos2) h_prod2
  rw [h_div1, h_div2]
  rw [div_lt_div_iff₀ h_pos1 h_pos2]
  suffices s₁ * (Real.sqrt (s₂ ^ 2 + 4 * s₂) + s₂) < s₂ * (Real.sqrt (s₁ ^ 2 + 4 * s₁) + s₁) by
    linarith
  suffices s₁ * Real.sqrt (s₂ ^ 2 + 4 * s₂) < s₂ * Real.sqrt (s₁ ^ 2 + 4 * s₁) by
    linarith
  have h_cross_pos1 : 0 ≤ s₁ * Real.sqrt (s₂ ^ 2 + 4 * s₂) := by positivity
  have h_cross_pos2 : 0 ≤ s₂ * Real.sqrt (s₁ ^ 2 + 4 * s₁) := by positivity
  rw [← sq_lt_sq₀ h_cross_pos1 h_cross_pos2]
  have h_sq_left : (s₁ * Real.sqrt (s₂ ^ 2 + 4 * s₂)) ^ 2 = s₁ ^ 2 * (s₂ ^ 2 + 4 * s₂) := by
    rw [mul_pow, Real.sq_sqrt h_disc2]
  have h_sq_right : (s₂ * Real.sqrt (s₁ ^ 2 + 4 * s₁)) ^ 2 = s₂ ^ 2 * (s₁ ^ 2 + 4 * s₁) := by
    rw [mul_pow, Real.sq_sqrt h_disc1]
  rw [h_sq_left, h_sq_right]
  calc s₁ ^ 2 * (s₂ ^ 2 + 4 * s₂) = s₁ ^ 2 * s₂ ^ 2 + 4 * s₁ ^ 2 * s₂ := by ring
  _ < s₁ ^ 2 * s₂ ^ 2 + 4 * s₁ * s₂ ^ 2 := by
    have : 4 * s₁ ^ 2 * s₂ < 4 * s₁ * s₂ ^ 2 := by
      calc 4 * s₁ ^ 2 * s₂ = (4 * s₁ * s₂) * s₁ := by ring
      _ < (4 * s₁ * s₂) * s₂ := by
        apply mul_lt_mul_of_pos_left hlt
        positivity
      _ = 4 * s₁ * s₂ ^ 2 := by ring
    linarith
  _ = s₂ ^ 2 * (s₁ ^ 2 + 4 * s₁) := by ring

/-- The steady-state Kalman gain as a function of the signal-to-noise ratio `s = σ_ζ² / σ_ν² > 0`:
    `η(s) = (√(s² + 4s) - s) / 2`. -/
noncomputable def kalmanGain (s : ℝ) : ℝ :=
  (Real.sqrt (s ^ 2 + 4 * s) - s) / 2

/-- For all `s > 0`, `0 < η(s)`. -/
theorem p1_kalmanGain_pos (s : ℝ) (hs : 0 < s) : 0 < kalmanGain s := by
  dsimp [kalmanGain]
  have h_disc : s ^ 2 < s ^ 2 + 4 * s := by linarith
  have hs2_nonneg : 0 ≤ s ^ 2 := by positivity
  have h_sqrt : s < Real.sqrt (s ^ 2 + 4 * s) := by
    calc s = Real.sqrt (s ^ 2) := (Real.sqrt_sq (le_of_lt hs)).symm
    _ < Real.sqrt (s ^ 2 + 4 * s) := Real.sqrt_lt_sqrt hs2_nonneg h_disc
  linarith

/-- For all `s > 0`, `η(s) < 1`. -/
theorem p1_kalmanGain_lt_one (s : ℝ) (hs : 0 < s) : kalmanGain s < 1 := by
  dsimp [kalmanGain]
  have h_sq : s ^ 2 + 4 * s < (s + 2) ^ 2 := by
    calc s ^ 2 + 4 * s < s ^ 2 + 4 * s + 4 := by linarith
    _ = (s + 2) ^ 2 := by ring
  have h_s2_pos : 0 ≤ s ^ 2 + 4 * s := by positivity
  have h_s2_plus : 0 ≤ s + 2 := by linarith
  have h_sqrt : Real.sqrt (s ^ 2 + 4 * s) < s + 2 := by
    rw [← Real.sqrt_sq h_s2_plus]
    exact Real.sqrt_lt_sqrt h_s2_pos h_sq
  linarith

/-- The Kalman gain Riccati identity: `η(s)² + s * η(s) = s`. -/
theorem p1_kalmanGain_riccati_eq (s : ℝ) (hs : 0 ≤ s) :
    (kalmanGain s) ^ 2 + s * (kalmanGain s) = s := by
  dsimp [kalmanGain]
  have h_disc : 0 ≤ s ^ 2 + 4 * s := by positivity
  have h_sq := Real.sq_sqrt h_disc
  linear_combination 1/4 * h_sq

/-- Kalman gain strict monotonicity: For `0 < s₁ < s₂`, `η(s₁) < η(s₂)`. -/
theorem p1_kalmanGain_strict_mono (s₁ s₂ : ℝ) (hs₁ : 0 < s₁) (hlt : s₁ < s₂) :
    kalmanGain s₁ < kalmanGain s₂ := by
  dsimp [kalmanGain]
  have h_mono := p1_sqrt_diff_strict_mono s₁ s₂ hs₁ hlt
  linarith

/-- Kalman gain injectivity: For `s₁, s₂ > 0`, `η(s₁) = η(s₂) → s₁ = s₂`. -/
theorem p1_kalmanGain_injective {s₁ s₂ : ℝ} (hs₁ : 0 < s₁) (hs₂ : 0 < s₂)
    (h : kalmanGain s₁ = kalmanGain s₂) : s₁ = s₂ := by
  rcases lt_trichotomy s₁ s₂ with hlt | heq | hgt
  · have := p1_kalmanGain_strict_mono s₁ s₂ hs₁ hlt
    linarith
  · exact heq
  · have := p1_kalmanGain_strict_mono s₂ s₁ hs₂ hgt
    linarith

/-- Transformed sample complexity in economic primitives (Proposition 29):
    If rate recovery requires `N ≥ C * σ² / (Δη)^(4K-2)`, and `Δη ≤ c_plus * Δs`,
    then signal-to-noise ratio recovery requires `N ≥ C * (c_plus)^(4K-2)⁻¹ * σ² / (Δs)^(4K-2)`. -/
theorem p1_prop_primitives_sample_transfer
    (C σ Δs Δη c_plus N : ℝ) (K : ℕ) (hK : 1 ≤ K)
    (hC : 0 < C) (hσ : 0 < σ) (hΔs : 0 < Δs) (hc : 0 < c_plus)
    (h_step : Δη ≤ c_plus * Δs) (hΔη : 0 < Δη)
    (h_rate_bound : C * σ ^ 2 / (Δη ^ (4 * K - 2)) ≤ N) :
    C * (c_plus ^ (4 * K - 2))⁻¹ * σ ^ 2 / (Δs ^ (4 * K - 2)) ≤ N := by
  have h_pos_step : 0 ≤ Δη := le_of_lt hΔη
  have h_pow_le : Δη ^ (4 * K - 2) ≤ (c_plus * Δs) ^ (4 * K - 2) :=
    pow_le_pow_left₀ h_pos_step h_step (4 * K - 2)
  have h_prod : (c_plus * Δs) ^ (4 * K - 2) = c_plus ^ (4 * K - 2) * Δs ^ (4 * K - 2) :=
    mul_pow c_plus Δs (4 * K - 2)
  have h_pos_denom1 : 0 < Δη ^ (4 * K - 2) := by positivity
  have h_pos_denom2 : 0 < (c_plus * Δs) ^ (4 * K - 2) := by positivity
  have h_inv_le : ((c_plus * Δs) ^ (4 * K - 2))⁻¹ ≤ (Δη ^ (4 * K - 2))⁻¹ :=
    (inv_le_inv₀ h_pos_denom2 h_pos_denom1).mpr h_pow_le
  have h_num_pos : 0 ≤ C * σ ^ 2 := by positivity
  calc C * (c_plus ^ (4 * K - 2))⁻¹ * σ ^ 2 / (Δs ^ (4 * K - 2))
      = (C * σ ^ 2) * ((c_plus ^ (4 * K - 2))⁻¹ * (Δs ^ (4 * K - 2))⁻¹) := by ring
    _ = (C * σ ^ 2) * (c_plus ^ (4 * K - 2) * Δs ^ (4 * K - 2))⁻¹ := by rw [mul_inv]
    _ = (C * σ ^ 2) * ((c_plus * Δs) ^ (4 * K - 2))⁻¹ := by rw [← h_prod]
    _ ≤ (C * σ ^ 2) * (Δη ^ (4 * K - 2))⁻¹ := mul_le_mul_of_nonneg_left h_inv_le h_num_pos
    _ = C * σ ^ 2 / (Δη ^ (4 * K - 2)) := by ring
    _ ≤ N := h_rate_bound

/-! ### Proposition 30: Intensity Tied to Information Quality (`prop:tied`) -/

/-- (i) Unknown numbers of desks:
    For any known positive desk weight function `w(η) > 0` and desired atom mass `m ≥ 0`,
    setting population mass `n = m / w(η)` attains exactly `n * w(η) = m`. -/
theorem p1_intensity_tied_mass_inversion (w_η m : ℝ) (hw : 0 < w_η) :
    let n := m / w_η
    n * w_η = m := by
  intro n
  dsimp [n]
  exact div_mul_cancel₀ m (ne_of_gt hw)

/-- (ii) Known numbers of desks:
    Tap difference between 1 cohort of `2n` desks at `bar_η` and 2 cohorts of `n` desks each at `bar_η ± δ`:
    `n * g(bar_η + δ) + n * g(bar_η - δ) - 2 * n * g(bar_η) = n * (g(bar_η + δ) + g(bar_η - δ) - 2 * g(bar_η))`. -/
theorem p1_intensity_tied_tap_difference (g : ℝ → ℝ) (n bar_η δ : ℝ) :
    n * g (bar_η + δ) + n * g (bar_η - δ) - 2 * n * g bar_η =
      n * (g (bar_η + δ) + g (bar_η - δ) - 2 * g bar_η) := by
  ring

/-- Exact quadratic second-difference identity:
    For any quadratic `g(x) = A x² + B x + C`,
    `g(bar_η + δ) + g(bar_η - δ) - 2 g(bar_η) = 2 * A * δ²`. -/
theorem p1_quadratic_second_difference_identity (A B C bar_η δ : ℝ) :
    let g := fun x => A * x ^ 2 + B * x + C
    g (bar_η + δ) + g (bar_η - δ) - 2 * g bar_η = 2 * A * δ ^ 2 := by
  intro g
  dsimp [g]
  ring

/-- Combining tap difference and quadratic second-difference:
    The tap gap for `2n` desks vs two `n` desks is exactly `2 * A * n * δ² = O(n δ²)`. -/
theorem p1_intensity_tied_quadratic_tap_gap (A B C n bar_η δ : ℝ) :
    let g := fun x => A * x ^ 2 + B * x + C
    n * g (bar_η + δ) + n * g (bar_η - δ) - 2 * n * g bar_η = 2 * A * n * δ ^ 2 := by
  intro g
  dsimp [g]
  ring

/-- Sample complexity lower bound for tied intensity (Proposition 30):
    If the tap gap is bounded by `|Δg| ≤ L * n * δ²`, so `N` experiments have KL divergence
    bounded by `N * (L * n * δ²)² / (2 * σ²)`, then any test with error `≤ 1/4` (requiring `KL ≥ 1/4`)
    forces `N ≥ (σ² / (2 * L² * n²)) / δ⁴ = Ω(σ² * δ⁻⁴)`. -/
theorem p1_prop_tied_sample_bound
    (L n δ σ N : ℝ) (hL : 0 < L) (hn : 0 < n) (hδ : 0 < δ) (hσ : 0 < σ)
    (hKL_bound : (1 : ℝ) / 4 ≤ (N * (L * n * δ ^ 2) ^ 2) / (2 * σ ^ 2)) :
    (σ ^ 2 / (2 * L ^ 2 * n ^ 2)) / (δ ^ 4) ≤ N := by
  have h_den_pos : 0 < 2 * σ ^ 2 := by positivity
  have h_term_pos : 0 < (L * n * δ ^ 2) ^ 2 := by positivity
  have h_mult : (1 : ℝ) / 4 * (2 * σ ^ 2) ≤ N * (L * n * δ ^ 2) ^ 2 := by
    exact (le_div_iff₀ h_den_pos).mp hKL_bound
  have h_N : (1 : ℝ) / 4 * (2 * σ ^ 2) / ((L * n * δ ^ 2) ^ 2) ≤ N := by
    exact (div_le_iff₀ h_term_pos).mpr (by linarith)
  have h_pow4 : (δ ^ 2) ^ 2 = δ ^ 4 := by ring
  have h_alg : (1 : ℝ) / 4 * (2 * σ ^ 2) / ((L * n * δ ^ 2) ^ 2) =
      (σ ^ 2 / (2 * L ^ 2 * n ^ 2)) / (δ ^ 4) := by
    calc (1 : ℝ) / 4 * (2 * σ ^ 2) / ((L * n * δ ^ 2) ^ 2)
        = (σ ^ 2 / 2) / ((L * n) ^ 2 * (δ ^ 2) ^ 2) := by ring
      _ = (σ ^ 2 / 2) / (L ^ 2 * n ^ 2 * δ ^ 4) := by rw [h_pow4]; ring
      _ = (σ ^ 2 / (2 * L ^ 2 * n ^ 2)) / (δ ^ 4) := by ring
  rw [← h_alg]
  exact h_N

end CurrentMM
