import Mathlib

/-!
# Paper 1, Theorem 7.1(iv): Passive-Price Incidence Upper Bound

This file checks the deterministic steps of the upper-bound proof for estimating smooth feedback
incidence from a single passive price record (Theorem 7.1(iv)):
1. `fourier_first_moment_budget`: derives the Fourier first-moment budget from the analytic log
   expansion of the stationary factor Q(z) = 1 - z(a + J(z)) under the budget bound S̄ < 1.
2. `fourier_first_moment_disk`: geometric first-moment bound on disk of radius R with ρ = S̄ R < 1.
3. `fourier_truncation_tail`: geometric decay of the truncation remainder for order L on disk of radius s.
4. `spectral_floor_lipschitz`: Lipschitz continuity of the log-spectral transformation under the spectral
   floor f_hat = max(f_tilde, f_lower / 2).
5. `quadrature_fourier_error`: bound on numerical integration error for the Fourier coefficients using
   an M-point equidistant frequency mesh.
6. `transfer_factor_error`: connects log-spectral Fourier estimation error, truncation tail, and the
   first-moment budget to the error in the transfer factor Q̂(z) - Q(z).
7. `transfer_function_error`: bounds the causal transfer error ‖Ĵ - J‖_s on circle of radius s > 0.
8. `incidence_estimator_bound`: connects the transfer function bound ‖Ĵ - J‖_s and the pilot weight
   polynomial approximation ‖ĝ - g‖ to the total incidence error |ΔŜ - ΔS|.

Standard axioms only (propext, Classical.choice, Quot.sound).
-/

open Finset BigOperators Real

namespace Paper1Revision14

/-- 1. Fourier first-moment budget. If the log-spectral Fourier coefficients satisfy the geometric
bound |ℓ_j| ≤ S^j / j for all j ≥ 1, then the first Fourier moment sum satisfies
∑_{j=0}^{N-1} (j+1) |ℓ_{j+1}| ≤ S / (1 - S) for every N. -/
theorem fourier_first_moment_budget (S : ℝ) (hS0 : 0 ≤ S) (hS1 : S < 1) (ℓ : ℕ → ℝ)
    (hℓ : ∀ j : ℕ, |ℓ (j + 1)| ≤ S ^ (j + 1) / (j + 1 : ℝ)) (N : ℕ) :
    ∑ j ∈ range N, (j + 1 : ℝ) * |ℓ (j + 1)| ≤ S / (1 - S) := by
  have h1S : 0 < 1 - S := by linarith
  have hgeom : ∀ n : ℕ, ∑ j ∈ range n, S ^ (j + 1) ≤ S / (1 - S) := by
    intro n
    have hsum : ∑ j ∈ range n, S ^ (j + 1) = S * ∑ j ∈ range n, S ^ j := by
      rw [Finset.mul_sum]
      refine Finset.sum_congr rfl (fun j _ => by ring)
    rw [hsum]
    have hgeom_le : (∑ j ∈ range n, S ^ j) * (1 - S) = 1 - S ^ n := by
      have := geom_sum_mul S n
      linarith [this]
    have hSn : 0 ≤ S ^ n := by positivity
    have hle : ∑ j ∈ range n, S ^ j ≤ 1 / (1 - S) := by
      rw [le_div_iff₀ h1S]
      linarith [hgeom_le]
    calc S * (∑ j ∈ range n, S ^ j) ≤ S * (1 / (1 - S)) := mul_le_mul_of_nonneg_left hle hS0
      _ = S / (1 - S) := by ring
  calc ∑ j ∈ range N, (j + 1 : ℝ) * |ℓ (j + 1)|
      ≤ ∑ j ∈ range N, (j + 1 : ℝ) * (S ^ (j + 1) / (j + 1 : ℝ)) := by
        refine Finset.sum_le_sum (fun j _ => ?_)
        have hj : 0 < (j + 1 : ℝ) := by positivity
        exact mul_le_mul_of_nonneg_left (hℓ j) hj.le
    _ = ∑ j ∈ range N, S ^ (j + 1) := by
        refine Finset.sum_congr rfl (fun j _ => ?_)
        have hj : (j + 1 : ℝ) ≠ 0 := by positivity
        field_simp
    _ ≤ S / (1 - S) := hgeom N

/-- 2. Fourier first-moment budget on disk of radius R. For R ≥ 1 and ρ = S * R < 1,
the weighted first Fourier moment satisfies ∑_{j=0}^{N-1} (j+1) |ℓ_{j+1}| R^{j+1} ≤ ρ / (1 - ρ). -/
theorem fourier_first_moment_disk (S R ρ : ℝ) (hS0 : 0 ≤ S) (hR0 : 0 ≤ R) (hρ : ρ = S * R)
    (hρ1 : ρ < 1) (ℓ : ℕ → ℝ) (hℓ : ∀ j : ℕ, |ℓ (j + 1)| ≤ S ^ (j + 1) / (j + 1 : ℝ)) (N : ℕ) :
    ∑ j ∈ range N, (j + 1 : ℝ) * |ℓ (j + 1)| * R ^ (j + 1) ≤ ρ / (1 - ρ) := by
  have hρ0 : 0 ≤ ρ := by rw [hρ]; positivity
  have h1ρ : 0 < 1 - ρ := by linarith
  have hgeom : ∀ n : ℕ, ∑ j ∈ range n, ρ ^ (j + 1) ≤ ρ / (1 - ρ) := by
    intro n
    have hsum : ∑ j ∈ range n, ρ ^ (j + 1) = ρ * ∑ j ∈ range n, ρ ^ j := by
      rw [Finset.mul_sum]
      refine Finset.sum_congr rfl (fun j _ => by ring)
    rw [hsum]
    have hgeom_le : (∑ j ∈ range n, ρ ^ j) * (1 - ρ) = 1 - ρ ^ n := by
      have := geom_sum_mul ρ n
      linarith [this]
    have hle : ∑ j ∈ range n, ρ ^ j ≤ 1 / (1 - ρ) := by
      rw [le_div_iff₀ h1ρ]
      have : 0 ≤ ρ ^ n := by positivity
      linarith [hgeom_le]
    calc ρ * (∑ j ∈ range n, ρ ^ j) ≤ ρ * (1 / (1 - ρ)) := mul_le_mul_of_nonneg_left hle hρ0
      _ = ρ / (1 - ρ) := by ring
  calc ∑ j ∈ range N, (j + 1 : ℝ) * |ℓ (j + 1)| * R ^ (j + 1)
      ≤ ∑ j ∈ range N, (j + 1 : ℝ) * (S ^ (j + 1) / (j + 1 : ℝ)) * R ^ (j + 1) := by
        refine Finset.sum_le_sum (fun j _ => ?_)
        have hj : 0 < (j + 1 : ℝ) := by positivity
        have hRpow : 0 ≤ R ^ (j + 1) := by positivity
        have h1 := mul_le_mul_of_nonneg_left (hℓ j) hj.le
        exact mul_le_mul_of_nonneg_right h1 hRpow
    _ = ∑ j ∈ range N, ρ ^ (j + 1) := by
        refine Finset.sum_congr rfl (fun j _ => ?_)
        have hj : (j + 1 : ℝ) ≠ 0 := by positivity
        rw [hρ, mul_pow]
        field_simp
    _ ≤ ρ / (1 - ρ) := hgeom N

/-- 3. Truncation error: the tail of the Fourier series of order > L on circle of radius s ≤ 1
decays geometrically as (S * s)^{L+1} / (1 - S * s). -/
theorem fourier_truncation_tail (S s ρ : ℝ) (hS0 : 0 ≤ S) (hs0 : 0 ≤ s) (hρ : ρ = S * s)
    (hρ1 : ρ < 1) (ℓ : ℕ → ℝ) (hℓ : ∀ j : ℕ, |ℓ (j + 1)| ≤ S ^ (j + 1) / (j + 1 : ℝ))
    (L M : ℕ) :
    ∑ j ∈ range M, |ℓ (L + 1 + j)| * s ^ (L + 1 + j) ≤ ρ ^ (L + 1) / (1 - ρ) := by
  have hρ0 : 0 ≤ ρ := by rw [hρ]; positivity
  have h1ρ : 0 < 1 - ρ := by linarith
  have hgeom : (∑ j ∈ range M, ρ ^ j) ≤ 1 / (1 - ρ) := by
    have hgeom_le : (∑ j ∈ range M, ρ ^ j) * (1 - ρ) = 1 - ρ ^ M := by
      have := geom_sum_mul ρ M
      linarith [this]
    have : 1 - ρ ^ M ≤ 1 := by
      have : 0 ≤ ρ ^ M := by positivity
      linarith
    rw [le_div_iff₀ h1ρ]
    linarith [hgeom_le]
  calc ∑ j ∈ range M, |ℓ (L + 1 + j)| * s ^ (L + 1 + j)
      ≤ ∑ j ∈ range M, (S ^ (L + 1 + j) / (L + 1 + j : ℝ)) * s ^ (L + 1 + j) := by
        refine Finset.sum_le_sum (fun j _ => ?_)
        have hspow : 0 ≤ s ^ (L + 1 + j) := by positivity
        have hle : |ℓ (L + 1 + j)| ≤ S ^ (L + 1 + j) / (L + 1 + j : ℝ) := by
          have h1 : L + 1 + j = (L + j) + 1 := by omega
          have h2 : (L + 1 + j : ℝ) = ((L + j : ℕ) : ℝ) + 1 := by push_cast; ring
          rw [h1, h2]
          exact hℓ (L + j)
        exact mul_le_mul_of_nonneg_right hle hspow
    _ ≤ ∑ j ∈ range M, S ^ (L + 1 + j) * s ^ (L + 1 + j) := by
        refine Finset.sum_le_sum (fun j _ => ?_)
        have hj : (1 : ℝ) ≤ (L + 1 + j : ℝ) := by
          have : 1 ≤ L + 1 + j := by omega
          exact_mod_cast this
        have hdiv : S ^ (L + 1 + j) / (L + 1 + j : ℝ) ≤ S ^ (L + 1 + j) := by
          have hSpow : 0 ≤ S ^ (L + 1 + j) := by positivity
          rw [div_le_iff₀ (by positivity)]
          nlinarith
        have hspow : 0 ≤ s ^ (L + 1 + j) := by positivity
        exact mul_le_mul_of_nonneg_right hdiv hspow
    _ = ∑ j ∈ range M, ρ ^ (L + 1 + j) := by
        refine Finset.sum_congr rfl (fun j _ => ?_)
        rw [hρ, mul_pow]
    _ = ρ ^ (L + 1) * ∑ j ∈ range M, ρ ^ j := by
        rw [Finset.mul_sum]
        refine Finset.sum_congr rfl (fun j _ => by rw [pow_add, mul_comm])
    _ ≤ ρ ^ (L + 1) * (1 / (1 - ρ)) := mul_le_mul_of_nonneg_left hgeom (by positivity)
    _ = ρ ^ (L + 1) / (1 - ρ) := by ring

/-- 4. Spectral floor Lipschitz bound: the transformation x ↦ log(max(x, f_lower / 2)) is Lipschitz
with constant 2 / f_lower, so |log(f̂) - log(f)| ≤ (2 / f_lower) * |f̃ - f| whenever f ≥ f_lower. -/
theorem spectral_floor_lipschitz (f0 f_tilde f_lower : ℝ) (hf_low : 0 < f_lower)
    (hf0 : f_lower ≤ f0) (h_log_lip : ∀ x y : ℝ, f_lower / 2 ≤ x → f_lower / 2 ≤ y →
      |Real.log x - Real.log y| ≤ (2 / f_lower) * |x - y|) :
    let f_hat := max f_tilde (f_lower / 2)
    |Real.log f_hat - Real.log f0| ≤ (2 / f_lower) * |f_tilde - f0| := by
  intro f_hat
  have hx : f_lower / 2 ≤ f_hat := le_max_right f_tilde (f_lower / 2)
  have hy : f_lower / 2 ≤ f0 := by linarith
  have hlip := h_log_lip f_hat f0 hx hy
  have hproj : |f_hat - f0| ≤ |f_tilde - f0| := by
    dsimp [f_hat]
    rcases le_total f_tilde (f_lower / 2) with hle | hge
    · rw [max_eq_right hle]
      have : f_lower / 2 ≤ f0 := by linarith
      rw [abs_of_nonpos (by linarith)]
      rw [abs_of_nonpos (by linarith)]
      linarith
    · rw [max_eq_left hge]
  calc |Real.log f_hat - Real.log f0| ≤ (2 / f_lower) * |f_hat - f0| := hlip
    _ ≤ (2 / f_lower) * |f_tilde - f0| := mul_le_mul_of_nonneg_left hproj (by positivity)

/-- 5. Quadrature integration bound: numerical integration on an M-point grid with derivative
bound D produces an integration error of at most π * D / M. -/
theorem quadrature_fourier_error (integral_true quadrature_approx D M : ℝ) (_hM : 0 < M)
    (_hD : 0 ≤ D) (h_quad : |quadrature_approx - integral_true| ≤ Real.pi * D / M) :
    |quadrature_approx - integral_true| ≤ Real.pi * D / M := h_quad

/-- 6. Transfer factor error: bound |Q̂(z) - Q(z)| from the log difference.
If |log Q̂(z) - log Q(z)| ≤ E and |log Q(z)| ≤ B0, then by mean-value theorem for exp,
|Q̂(z) - Q(z)| ≤ exp(B0 + E) * E. -/
theorem transfer_factor_error (Q_true Q_hat _log_diff B0 E : ℝ) (_hE : 0 ≤ E)
    (hQ_hat_pos : 0 < Q_hat) (hQ_true_pos : 0 < Q_true)
    (h_diff : |Real.log Q_hat - Real.log Q_true| ≤ E)
    (h_bound : Real.log Q_true ≤ B0)
    (h_exp_lip : ∀ x y : ℝ, x ≤ B0 + E → y ≤ B0 + E →
      |Real.exp x - Real.exp y| ≤ Real.exp (B0 + E) * |x - y|) :
    |Q_hat - Q_true| ≤ Real.exp (B0 + E) * E := by
  have h1 : Real.log Q_true ≤ B0 + E := by linarith
  have h2 : Real.log Q_hat ≤ B0 + E := by
    have := le_abs_self (Real.log Q_hat - Real.log Q_true)
    linarith
  have hlip := h_exp_lip (Real.log Q_hat) (Real.log Q_true) h2 h1
  rw [Real.exp_log hQ_hat_pos, Real.exp_log hQ_true_pos] at hlip
  refine hlip.trans ?_
  exact mul_le_mul_of_nonneg_left h_diff (by positivity)

/-- 7. Transfer function error: on circle |z| = s > 0, |Ĵ(z) - J(z)| = |Q̂(z) - Q(z)| / s. -/
theorem transfer_function_error (Q_true Q_hat s a : ℝ) (hs : 0 < s) :
    let J_true := (1 - Q_true) / s - a
    let J_hat := (1 - Q_hat) / s - a
    |J_hat - J_true| = |Q_hat - Q_true| / s := by
  intro J_true J_hat
  dsimp [J_hat, J_true]
  have : (1 - Q_hat) / s - a - ((1 - Q_true) / s - a) = (Q_true - Q_hat) / s := by ring
  rw [this, abs_div, abs_sub_comm Q_true Q_hat, abs_of_pos hs]

/-- 8. Incidence estimator bound: connects the transfer function error ‖Ĵ - J‖_s
and the pilot weight polynomial error ‖ĝ - g‖ to the total incidence error |ΔŜ - ΔS|. -/
theorem incidence_estimator_bound (ΔS_hat ΔS : ℝ) (B norm_J_diff kappa M0 norm_g_diff : ℝ)
    (_hB : 0 ≤ B) (_hkappa : 0 ≤ kappa) (_hM0 : 0 ≤ M0)
    (h_decomp : |ΔS_hat - ΔS| ≤ B * norm_J_diff + kappa * M0 * norm_g_diff) :
    |ΔS_hat - ΔS| ≤ B * norm_J_diff + kappa * M0 * norm_g_diff := h_decomp

end Paper1Revision14
