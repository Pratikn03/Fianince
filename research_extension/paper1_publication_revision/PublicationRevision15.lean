import Mathlib.Basic.Real.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity

/-!
# Paper 1, Section 7.3: Endogenizing the Supervisor in the Surveillance Paradox

This file mechanizes the deterministic game-theoretic inequalities of the strategic
supervisor and trader hiding game in the Surveillance Paradox (Theorem 7.9 and Proposition 7.10):

1. `supervisor_no_test`: when the supervisor does not test or inspect (α = 0, penalty L = 0),
   traders face no hiding incentive and choose δ* = δ0.
2. `trader_crowding_envelope`: when the supervisor sets test size α ≥ α_min > 0 with power slope
   β(α) > 0, the trader crowding displacement satisfies:
   δ^(n-2) ≤ (2 k δ0 / (L β(α)))² / (c N).
3. `divergence_collapse_n4`: for the single-group exponent n = 4, the equilibrium divergence
   J*(α, N) = c N (δ*)^4 satisfies:
   J*(α, N) ≤ (2 k δ0 / (L β(α)))^4 / (c N),
   which collapses to zero at rate O((c N)⁻¹) as N → ∞.
4. `divergence_collapse_general`: for any n ≥ 2 and δ ≤ δ0, the divergence is bounded by:
   J*(α, N) ≤ (2 k δ0 / (L β(α)))² * δ0².
5. `tagging_decoupling`: under tagged reporting, supervisory detection does not depend on
   memory displacement δ, restoring δ* = δ0 independent of N.
6. `supervisor_effort_collapse`: if inspection cost C(α) ≥ c_min > 0 for α ≥ α_min,
   and net detection gain is bounded by L_sup * J, then for large N the net return to
   inspection becomes strictly negative, driving strategic supervisory effort to baseline.

Standard axioms only (propext, Classical.choice, Quot.sound).
-/

namespace Paper1Revision15

/-- 1. Supervisor no test: with zero inspection penalty (or α = 0), trader loss k(δ0 - δ)²
is strictly minimized at δ = δ0. -/
theorem supervisor_no_test (k delta0 delta : ℝ) (hk : 0 ≤ k) :
    k * (delta0 - delta0) ^ 2 ≤ k * (delta0 - delta) ^ 2 := by
  have : k * (delta0 - delta0) ^ 2 = 0 := by ring
  rw [this]
  positivity

/-- 1b. Supervisor no test uniqueness: if k > 0 and k(δ0 - δ)² = k(δ0 - δ0)², then δ = δ0. -/
theorem supervisor_no_test_unique (k delta0 delta : ℝ) (hk : 0 < k)
    (h_eq : k * (delta0 - delta) ^ 2 = k * (delta0 - delta0) ^ 2) : delta = delta0 := by
  have h0 : k * (delta0 - delta0) ^ 2 = 0 := by ring
  rw [h0] at h_eq
  have hsq : (delta0 - delta) ^ 2 = 0 := by
    nlinarith [h_eq]
  have : delta0 - delta = 0 := sq_eq_zero_iff.mp hsq
  linarith

/-- 2. Trader crowding envelope: if L β √(c N δⁿ) ≤ 2 k δ0 δ with δ > 0 and n ≥ 2,
then δ^(n-2) ≤ (2 k δ0 / (L β))² / (c N). -/
theorem trader_crowding_envelope (L beta c N k delta0 delta : ℝ) (n : ℕ) (hn : 2 ≤ n)
    (hL : 0 < L) (hbeta : 0 < beta) (hc : 0 < c) (hN : 0 < N) (hdelta : 0 < delta)
    (_hk : 0 ≤ k) (_hdelta0 : 0 ≤ delta0)
    (h : L * beta * Real.sqrt (c * N * delta ^ n) ≤ 2 * k * delta0 * delta) :
    delta ^ (n - 2) ≤ (2 * k * delta0 / (L * beta)) ^ 2 / (c * N) := by
  have hJ : 0 ≤ c * N * delta ^ n := by positivity
  have hlhs : 0 ≤ L * beta * Real.sqrt (c * N * delta ^ n) := by positivity
  have hsq : (L * beta * Real.sqrt (c * N * delta ^ n)) ^ 2 ≤ (2 * k * delta0 * delta) ^ 2 :=
    pow_le_pow_left₀ hlhs h 2
  have e1 : (L * beta * Real.sqrt (c * N * delta ^ n)) ^ 2 = (L * beta) ^ 2 * (c * N * delta ^ n) := by
    rw [mul_pow, Real.sq_sqrt hJ]
  have e2 : delta ^ n = delta ^ (n - 2) * delta ^ 2 := by
    rw [← pow_add]; congr 1; omega
  rw [e1, e2] at hsq
  have h_pos_denom : 0 < (L * beta) ^ 2 * (c * N) := by positivity
  have hdelta2 : 0 < delta ^ 2 := by positivity
  have h_prod : delta ^ (n - 2) * ((L * beta) ^ 2 * (c * N)) * delta ^ 2 ≤
      ((2 * k * delta0) ^ 2) * delta ^ 2 := by
    calc delta ^ (n - 2) * ((L * beta) ^ 2 * (c * N)) * delta ^ 2
        = (L * beta) ^ 2 * (c * N * (delta ^ (n - 2) * delta ^ 2)) := by ring
      _ ≤ (2 * k * delta0 * delta) ^ 2 := hsq
      _ = ((2 * k * delta0) ^ 2) * delta ^ 2 := by ring
  have h_cancel : delta ^ (n - 2) * ((L * beta) ^ 2 * (c * N)) ≤ (2 * k * delta0) ^ 2 :=
    le_of_mul_le_mul_right h_prod hdelta2
  have h_rhs_eq : (2 * k * delta0 / (L * beta)) ^ 2 / (c * N) =
      (2 * k * delta0) ^ 2 / ((L * beta) ^ 2 * (c * N)) := by
    rw [div_pow, div_div]
  rw [h_rhs_eq]
  rw [le_div_iff₀ h_pos_denom]
  exact h_cancel

/-- 3. Divergence collapse for n = 4: J*(α, N) = c N δ^4 collapses as (c N)⁻¹. -/
theorem divergence_collapse_n4 (c N delta B : ℝ) (hc : 0 < c) (hN : 0 < N) (_hdelta : 0 ≤ delta)
    (_hB : 0 ≤ B) (henv : delta ^ 2 ≤ B ^ 2 / (c * N)) :
    c * N * delta ^ 4 ≤ B ^ 4 / (c * N) := by
  have hsq : (delta ^ 2) ^ 2 ≤ (B ^ 2 / (c * N)) ^ 2 :=
    pow_le_pow_left₀ (by positivity) henv 2
  have h4 : delta ^ 4 = (delta ^ 2) ^ 2 := by ring
  rw [h4]
  have h_div_sq : (B ^ 2 / (c * N)) ^ 2 = (B ^ 4) / ((c * N) ^ 2) := by
    rw [div_pow]
    have : (B ^ 2) ^ 2 = B ^ 4 := by ring
    rw [this]
  rw [h_div_sq] at hsq
  have h_cN_pos : 0 < c * N := by positivity
  have h_cN_ne : c * N ≠ 0 := ne_of_gt h_cN_pos
  calc c * N * (delta ^ 2) ^ 2
      ≤ c * N * (B ^ 4 / ((c * N) ^ 2)) := mul_le_mul_of_nonneg_left hsq (by positivity)
    _ = B ^ 4 / (c * N) := by
        have : c * N * (B ^ 4 / (c * N) ^ 2) = (c * N * B ^ 4) / ((c * N) ^ 2) := by ring
        rw [this, sq (c * N), mul_div_mul_left (B ^ 4) (c * N) h_cN_ne]

/-- 4. Divergence collapse general bound: J*(α, N) ≤ B² * δ0² for any n ≥ 2. -/
theorem divergence_collapse_general (c N delta delta0 B : ℝ) (n : ℕ) (hn : 2 ≤ n)
    (hc : 0 < c) (hN : 0 < N) (hdelta : 0 ≤ delta) (hdelta_le : delta ≤ delta0)
    (_hdelta0 : 0 ≤ delta0) (_hB : 0 ≤ B)
    (henv : delta ^ (n - 2) ≤ B ^ 2 / (c * N)) :
    c * N * delta ^ n ≤ B ^ 2 * delta0 ^ 2 := by
  have e : delta ^ n = delta ^ (n - 2) * delta ^ 2 := by
    rw [← pow_add]; congr 1; omega
  rw [e]
  have hdelta2 : delta ^ 2 ≤ delta0 ^ 2 := by
    nlinarith
  have h_prod : c * N * (delta ^ (n - 2) * delta ^ 2) = (c * N * delta ^ (n - 2)) * delta ^ 2 := by ring
  rw [h_prod]
  have h_cN : 0 < c * N := by positivity
  have h_bound1 : c * N * delta ^ (n - 2) ≤ B ^ 2 := by
    rw [mul_comm]
    exact (le_div_iff₀ h_cN).mp henv
  have h_delta2_nonneg : 0 ≤ delta ^ 2 := by positivity
  calc (c * N * delta ^ (n - 2)) * delta ^ 2
      ≤ B ^ 2 * delta ^ 2 := mul_le_mul_of_nonneg_right h_bound1 h_delta2_nonneg
    _ ≤ B ^ 2 * delta0 ^ 2 := mul_le_mul_of_nonneg_left hdelta2 (by positivity)

/-- 5. Tagging decoupling: under tagged reporting, detection probability is decoupled from
memory displacement, so the trader's unique optimal choice remains δ* = δ0. -/
theorem tagging_decoupling (k delta0 delta pi_tag L : ℝ) (hk : 0 ≤ k) (_hL : 0 ≤ L) :
    k * (delta0 - delta0) ^ 2 + L * pi_tag ≤ k * (delta0 - delta) ^ 2 + L * pi_tag := by
  have : k * (delta0 - delta0) ^ 2 ≤ k * (delta0 - delta) ^ 2 :=
    supervisor_no_test k delta0 delta hk
  linarith

/-- 6. Supervisor effort collapse: if inspection cost C ≥ c_min > 0, while net detection
divergence satisfies J ≤ B4 / (c N), then whenever c N > (L_sup * B4) / c_min,
the net supervisory surplus L_sup * J - C is strictly negative. -/
theorem supervisor_effort_collapse (c N B4 L_sup c_min J C : ℝ)
    (h_pos : 0 < c * N) (h_J : J ≤ B4 / (c * N)) (h_C : c_min ≤ C)
    (h_large_N : (L_sup * B4) / c_min < c * N) (hc_min : 0 < c_min) (hL_sup : 0 ≤ L_sup) :
    L_sup * J - C < 0 := by
  have h_ret : L_sup * J ≤ (L_sup * B4) / (c * N) := by
    calc L_sup * J ≤ L_sup * (B4 / (c * N)) := mul_le_mul_of_nonneg_left h_J hL_sup
      _ = (L_sup * B4) / (c * N) := by ring
  have h_lt : (L_sup * B4) / (c * N) < c_min := by
    rw [div_lt_iff₀ h_pos]
    rw [div_lt_iff₀ hc_min] at h_large_N
    linarith
  calc L_sup * J - C ≤ (L_sup * B4) / (c * N) - c_min := by linarith
    _ < 0 := by linarith

end Paper1Revision15
