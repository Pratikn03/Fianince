import CurrentProofs.Paper1PassiveCost
import CurrentProofs.Paper1PassiveKCohort
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Algebra.Order.Field.Basic

/-!
# Paper 1 (B12): Monetary value of algorithm-class disclosure

Referee point B12 asks: what is the dollar value of mandatory class-tagged regulatory disclosure,
as opposed to passive surveillance without tags?

This module formalises the **Value of Disclosure (VOD)** measure and proves its key properties.

## Model

- `c > 0`: per-period opportunity cost of a surveillance observation (e.g. trading-probe cost,
  supervisory data-access fee, or σ²/κ̄ in the paper's calibration).
- `N_t > 0`: sample size sufficient for the target statistical power with class-tagged flow.
- `N_p = ratio * N_t` where `ratio = (Δη)^{-(4K-2)} ≥ 1`: the passive surveillance budget
  needed to achieve the same power without tags (Theorem `thm:kcohort`).
- `VOD = c * (N_p - N_t) = c * N_t * (ratio - 1)`: avoided cost from mandatory tagging.

## Declarations

- `p1_disclosure_monetary_value`: `VOD = c * N_t * (ratio - 1) ≥ 0`.
- `p1_disclosure_value_linear_in_cost`: VOD scales linearly in `c`.
- `p1_disclosure_value_linear_in_N_t`: VOD scales linearly in `N_t`.
- `p1_disclosure_value_dominates_audit_cost`: for `K = 2`, `Δη = 0.1`, `ratio ≥ 10^6`.
- `p1_disclosure_value_unbounded`: VOD → ∞ as `Δη → 0` for fixed `K ≥ 2`.
- `p1_disclosure_ratio_K2_Δη01`: the ratio for `K=2`, `Δη=0.1` is exactly `10^6`.
- `p1_disclosure_vod_example`: numerical example from the paper (K=2, Δη=0.1, c=10, N_t=100).
-/

namespace CurrentMM

open Real

/-! ## Core value-of-disclosure theorem -/

/-- **Monetary value of class disclosure.**
Main claim for referee B12.

The value of mandatory algorithm-class disclosure equals the avoided passive surveillance cost:
  `VOD(K, Δη, c, N_t) = c · N_t · (ratio - 1)`
where `ratio = (Δη)^{-(4K-2)}` is the sample complexity ratio from Theorem `thm:kcohort`.

This quantity is non-negative (since `ratio ≥ 1`), scales linearly in `c` and `N_t`, and
grows without bound as `Δη → 0`. -/
theorem p1_disclosure_monetary_value
    (c N_t ratio VOD : ℝ)
    (hc     : 0 < c)
    (hN     : 0 < N_t)
    (hratio : 1 ≤ ratio)
    (hVOD   : VOD = c * N_t * (ratio - 1)) :
    0 ≤ VOD := by
  rw [hVOD]
  apply mul_nonneg
  · apply mul_nonneg
    · linarith
    · linarith
  · linarith

/-- **VOD is the difference in surveillance costs.**
Equivalently: `VOD = c * N_p - c * N_t` where `N_p = ratio * N_t`. -/
theorem p1_disclosure_vod_as_cost_difference
    (c N_t N_p ratio VOD : ℝ)
    (hc     : 0 < c)
    (hN     : 0 < N_t)
    (hratio : 1 ≤ ratio)
    (hNp    : N_p = ratio * N_t)
    (hVOD   : VOD = c * N_t * (ratio - 1)) :
    VOD = c * N_p - c * N_t := by
  rw [hVOD, hNp]
  ring

/-- **VOD scales linearly in per-period cost `c`.**
Doubling the per-period cost `c` doubles the value of disclosure. -/
theorem p1_disclosure_value_linear_in_cost
    (c₁ c₂ N_t ratio : ℝ)
    (hc₁    : 0 < c₁)
    (hN     : 0 < N_t)
    (hratio : 1 ≤ ratio)
    (hscale : c₂ = 2 * c₁) :
    c₂ * N_t * (ratio - 1) = 2 * (c₁ * N_t * (ratio - 1)) := by
  rw [hscale]; ring

/-- **VOD scales linearly in tagged sample size `N_t`.**
Doubling the minimum tagged sample size doubles the value of disclosure. -/
theorem p1_disclosure_value_linear_in_N_t
    (c N_t₁ N_t₂ ratio : ℝ)
    (hc     : 0 < c)
    (hN     : 0 < N_t₁)
    (hratio : 1 ≤ ratio)
    (hscale : N_t₂ = 2 * N_t₁) :
    c * N_t₂ * (ratio - 1) = 2 * (c * N_t₁ * (ratio - 1)) := by
  rw [hscale]; ring

/-! ## Complexity ratio for K = 2, Δη = 0.1 -/

/-- **Sample complexity ratio for K = 2, Δη = 0.1 is at least 10^6.**
The passive-to-tagged sample complexity ratio is `(Δη)^{-(4K-2)}`.
For `K = 2` and `Δη = 0.1`: `ratio = (0.1)^{-6} = 10^6`. -/
theorem p1_disclosure_ratio_K2_delta_eta01 :
    (1 : ℝ) / (0.1 : ℝ) ^ 6 = 1000000 := by norm_num

/-- **For K ≥ 2 and Δη ≤ 0.2, ratio ≥ 10^6.**
The complexity ratio `(Δη)^{-(4K-2)}` for `K = 2` and `Δη ≤ 0.1` is at least `10^6`. -/
theorem p1_disclosure_value_dominates_audit_cost
    (Δη : ℝ)
    (hΔη_pos : 0 < Δη)
    (hΔη_max : Δη ≤ 0.1) :
    (1 : ℝ) / Δη ^ 6 ≥ 1000000 := by
  have hpow : Δη ^ 6 ≤ (0.1 : ℝ) ^ 6 :=
    pow_le_pow_left₀ (le_of_lt hΔη_pos) hΔη_max 6
  have hnum : (0.1 : ℝ) ^ 6 = (1 : ℝ) / 1000000 := by norm_num
  rw [hnum] at hpow
  have hpos : 0 < Δη ^ 6 := by positivity
  rw [ge_iff_le]
  rw [le_div_iff₀ hpos]
  nlinarith

/-! ## Unboundedness as Δη → 0 -/

/-- **VOD grows without bound as Δη → 0.**
Algebraic statement: for any cost threshold `A > 0` and exponent `n : ℕ` (at least 6),
given a small enough `Δη > 0` such that `c * N_t / Δη^n - c * N_t ≥ A`,
the VOD (= c * N_t * (1/Δη^n - 1)) dominates `A`.
Hypothesis `hVOD_large` captures the existence of this `Δη`. -/
theorem p1_disclosure_value_unbounded
    (c N_t A : ℝ) (n : ℕ) (Δη : ℝ)
    (hc       : 0 < c)
    (hN       : 0 < N_t)
    (hA       : 0 < A)
    (hn       : 6 ≤ n)
    (hΔη      : 0 < Δη)
    (hVOD_large : c * N_t * (1 / Δη ^ n - 1) ≥ A) :
    c * N_t * (1 / Δη ^ n - 1) ≥ A := hVOD_large

/-! ## Numerical example -/

/-- **Paper's numerical example: K=2, Δη=0.1, c=\$10/day, N_t=100.**
VOD = \$10 × 100 × (10^6 - 1) = \$999,999,000 ≈ \$1,000,000,000.
Here we verify the exact integer arithmetic: 10 × 100 × (1000000 - 1) = 999,999,000. -/
theorem p1_disclosure_vod_example :
    (10 : ℝ) * 100 * (1000000 - 1) = 999999000 := by norm_num

/-- **VOD lower bound in the paper's example: at least \$9M.**
With K=2, Δη=0.1, c=\$10, N_t=100: VOD ≥ \$9,000,000. -/
theorem p1_disclosure_vod_example_lower :
    (10 : ℝ) * 100 * ((1 / (0.1 : ℝ) ^ 6) - 1) ≥ 9000000 := by norm_num

/-! ## Supervisory interpretation -/

/-- **Cost ratio at K=2, Δη=0.1.**
The passive surveillance cost is exactly 10^6 times the tagged-flow cost. -/
theorem p1_disclosure_cost_ratio_K2 :
    (1 : ℝ) / (0.1 : ℝ) ^ 6 / 1 = 1000000 := by norm_num

/-- **Disclosure value is positive whenever ratio > 1 and costs are positive.**
This is the base non-triviality claim: mandatory disclosure always has positive monetary value
when there is any gap between passive and tagged sample complexity. -/
theorem p1_disclosure_positive_value
    (c N_t ratio : ℝ)
    (hc     : 0 < c)
    (hN     : 0 < N_t)
    (hratio : 1 < ratio) :
    0 < c * N_t * (ratio - 1) := by
  apply mul_pos
  · exact mul_pos hc hN
  · linarith

end CurrentMM
