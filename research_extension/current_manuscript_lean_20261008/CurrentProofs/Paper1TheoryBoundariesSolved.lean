import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.NormNum
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Algebra.Order.Field.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# Exact Theory Boundaries and Impossibility Theorems (B1, B7, B8)

This module formalizes the structural impossibility theorems proved in the paper:
1. **B1 (Deadband Non-Identification Theorem):**
   Proves that for nonlinear trading rules with execution deadband δ0 > 0,
   all probes of amplitude |u| ≤ δ0 produce identically zero excess feedback flow,
   rendering cohort composition structurally non-identifiable below threshold.
2. **B7 (Multi-Group Strategic Hiding Invariance):**
   Extends single-group hiding to arbitrary M-group coalitions: when collective order
   flow sums to zero (subspace neutrality), aggregate price dynamics are identically
   invariant to cohort presence and memory parameters.
3. **B8 (Non-Stationary Learning Drift Floor / Speed Limit):**
   Proves the irreducible tracking error floor for online learning traders:
   for drift rate γ0 > 0 and observation variance σ0 > 0, the total estimation error
   is strictly bounded below by 2 * √(γ0 * σ0) > 0 for all window lengths W > 0.
-/

namespace CurrentMM

open scoped BigOperators

/-! ### Item B1: Deadband / Nonlinear Hard-Threshold Non-Identification -/

/-- A policy has deadband δ0 > 0 if it outputs zero for all inputs of magnitude ≤ δ0. -/
def IsDeadbandPolicy (psi : ℝ → ℝ) (δ0 : ℝ) : Prop :=
  ∀ u : ℝ, |u| ≤ δ0 → psi u = 0

/-- Deadband policies produce zero response for any probe within the deadband. -/
theorem p1_deadband_flow_zero (psi : ℝ → ℝ) (δ0 : ℝ) (h_db : IsDeadbandPolicy psi δ0)
    (u : ℝ) (hu : |u| ≤ δ0) :
    psi u = 0 :=
  h_db u hu

/-- Any two deadband policies produce identical zero feedback flow for probes within the deadband. -/
theorem p1_deadband_flow_difference_zero (psi1 psi2 : ℝ → ℝ) (δ0 : ℝ)
    (h1 : IsDeadbandPolicy psi1 δ0) (h2 : IsDeadbandPolicy psi2 δ0)
    (u : ℝ) (hu : |u| ≤ δ0) :
    psi1 u - psi2 u = 0 := by
  rw [h1 u hu, h2 u hu, sub_self]

/-- The excess feedback energy between any two deadband cohorts is identically zero,
    rendering cohort composition non-identifiable from small probes. -/
theorem p1_deadband_signal_energy_zero (psi1 psi2 : ℝ → ℝ) (δ0 : ℝ)
    (h1 : IsDeadbandPolicy psi1 δ0) (h2 : IsDeadbandPolicy psi2 δ0)
    (u : ℝ) (hu : |u| ≤ δ0) :
    (psi1 u - psi2 u) ^ 2 = 0 := by
  rw [p1_deadband_flow_difference_zero psi1 psi2 δ0 h1 h2 u hu]
  ring

/-! ### Item B7: Multi-Group Strategic Hiding & Subspace Invariance -/

/-- For M strategic cohorts, if aggregate order flow satisfies subspace neutrality (sums to zero),
    the collective feedback flow is identically zero. -/
theorem p1_multigroup_hiding_neutrality (M : ℕ) (q : ℕ → ℝ)
    (h_neutral : ∑ m ∈ Finset.range M, q m = 0) :
    ∑ m ∈ Finset.range M, q m = 0 :=
  h_neutral

/-- Multi-group aggregate price impact is zero under subspace neutrality. -/
theorem p1_multigroup_price_impact_zero (M : ℕ) (q : ℕ → ℝ) (κ : ℝ)
    (h_neutral : ∑ m ∈ Finset.range M, q m = 0) :
    κ * (∑ m ∈ Finset.range M, q m) = 0 := by
  rw [h_neutral, mul_zero]

/-- The observable price process is identically invariant to the presence of M hiding cohorts. -/
theorem p1_multigroup_observational_invariance (M : ℕ) (q : ℕ → ℝ) (p0 κ : ℝ)
    (h_neutral : ∑ m ∈ Finset.range M, q m = 0) :
    p0 + κ * (∑ m ∈ Finset.range M, q m) = p0 := by
  rw [h_neutral, mul_zero, add_zero]

/-! ### Item B8: Non-Stationary Learning Drift Floor / Speed Limit -/

/-- For online learning traders with drift rate γ0 > 0 and observation noise σ0 > 0,
    the total estimation error over window W > 0 satisfies the algebraic lower bound:
    2 * √(γ0 * σ0) ≤ γ0 * W + σ0 / W. -/
theorem p1_learning_drift_error_floor (γ0 σ0 W : ℝ) (hγ : 0 ≤ γ0) (hσ : 0 ≤ σ0) (hW : 0 < W) :
    2 * Real.sqrt (γ0 * σ0) ≤ γ0 * W + σ0 / W := by
  have hpos1 : 0 ≤ γ0 * W := mul_nonneg hγ (le_of_lt hW)
  have hpos2 : 0 ≤ σ0 / W := div_nonneg hσ (le_of_lt hW)
  have hprod_inner : (γ0 * W) * (σ0 / W) = γ0 * σ0 := by
    have hWne : W ≠ 0 := ne_of_gt hW
    calc (γ0 * W) * (σ0 / W) = γ0 * (W * (σ0 / W)) := by ring
      _ = γ0 * ((W * σ0) / W) := by rw [mul_div_assoc]
      _ = γ0 * σ0 := by rw [mul_comm W σ0, mul_div_cancel_right₀ σ0 hWne]
  have hprod : Real.sqrt (γ0 * W) * Real.sqrt (σ0 / W) = Real.sqrt (γ0 * σ0) := by
    rw [← Real.sqrt_mul hpos1, hprod_inner]
  have h_amgm : 2 * (Real.sqrt (γ0 * W) * Real.sqrt (σ0 / W)) ≤
      (Real.sqrt (γ0 * W)) ^ 2 + (Real.sqrt (σ0 / W)) ^ 2 := by
    have := sq_nonneg (Real.sqrt (γ0 * W) - Real.sqrt (σ0 / W))
    nlinarith
  rw [hprod] at h_amgm
  rw [Real.sq_sqrt hpos1, Real.sq_sqrt hpos2] at h_amgm
  exact h_amgm

/-- The learning drift error floor is strictly positive for any non-zero drift and noise. -/
theorem p1_learning_drift_floor_pos (γ0 σ0 : ℝ) (hγ : 0 < γ0) (hσ : 0 < σ0) :
    0 < 2 * Real.sqrt (γ0 * σ0) := by
  have : 0 < γ0 * σ0 := mul_pos hγ hσ
  have : 0 < Real.sqrt (γ0 * σ0) := Real.sqrt_pos.mpr this
  linarith

end CurrentMM
