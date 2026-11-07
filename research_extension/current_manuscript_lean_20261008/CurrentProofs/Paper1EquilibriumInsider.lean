import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
# Paper 1, Theorem 4.6: a strategic insider inside the inventory equilibrium

A short-lived insider observes `θ_t` (the next fundamental innovation) and trades `d_t = b θ_t`. Unexpected flow is
`ν_t = ξ_t + d_t`. Dealers set `p_t = F_t + λ ν_t + x_t` with `x_t = -κ H_t + Σ β_i u_{i,t+1}`, and the cohorts trade on
the observed deviation `s_t = p_t - F_t = x_t + λ ν_t`.

* `p1_insider_reduced_form`: **pathwise**,
  `D s_t - ā s_{t-1} = Σ β_i (D - ā) u_{i,t} + (κ + λ) ν_t - ā λ ν_{t-1}`. With `β_i = κ/(D - r_i)` this is the paper's
  closed loop at the effective parameters of Theorem 4.2, driven by the known moving-average input
  `((κ + λ) ν_t - ā λ ν_{t-1})/D`.
* `p1_insider_best_response`: with price impact `c > 0` of its own trade, the insider's expected profit
  `(θ - c d) d` is at most `θ²/(4c)`, attained at `d = θ/(2c)`.
* `p1_insider_kyle_limit`: without inventory risk (`κ = 0`, `D = 1`), `b = 1/(2λ)` and `λ = b σ_θ²/(σ_ξ² + b² σ_θ²)` give
  `4 λ² σ_ξ² = σ_θ²`, Kyle's one-period `λ = σ_θ/(2σ_ξ)`.
* `p1_insider_posterior_variance`: `σ_θ² - λ² σ_ν² = σ_θ² σ_ξ²/σ_ν²` for `λ = b σ_θ²/σ_ν²`, `σ_ν² = σ_ξ² + b² σ_θ²`.
-/

namespace CurrentMM

open Finset

/-- **Observer's reduced form with an insider (pathwise).** -/
theorem p1_insider_reduced_form {K : ℕ} (ab κ D lam H Hprev ν νprev x xprev s sprev : ℝ) (r w β u : Fin K → ℝ)
    (hβ : ∀ i, β i * (D - r i) = κ) (hD : D = 1 - ∑ i, β i * w i)
    (hs : s = x + lam * ν) (hsp : sprev = xprev + lam * νprev)
    (hH : H = ab * Hprev - ∑ i, u i - ν)
    (hx : x = -κ * H + ∑ i, β i * (r i * u i + w i * s))
    (hxp : xprev = -κ * Hprev + ∑ i, β i * u i) :
    D * s - ab * sprev = ∑ i, β i * (D - ab) * u i + (κ + lam) * ν - ab * lam * νprev := by
  have e0 : ∑ i, β i * (r i * u i + w i * s) = ∑ i, β i * r i * u i + (∑ i, β i * w i) * s := by
    rw [sum_mul, ← sum_add_distrib]; exact sum_congr rfl fun i _ => by ring
  have h2 : ∑ i, (κ * u i + β i * r i * u i) = D * ∑ i, β i * u i := by
    rw [mul_sum]; exact sum_congr rfl fun i _ => by have := hβ i; linear_combination (-(u i)) * this
  have e1 : ∑ i, (κ * u i + β i * r i * u i) = κ * ∑ i, u i + ∑ i, β i * r i * u i := by
    rw [sum_add_distrib, mul_sum]
  have e2 : ∑ i, β i * (D - ab) * u i = D * ∑ i, β i * u i - ab * ∑ i, β i * u i := by
    rw [mul_sum, mul_sum, ← sum_sub_distrib]; exact sum_congr rfl fun i _ => by ring
  have hW : ∑ i, β i * w i = 1 - D := by linarith [hD]
  rw [e0, hW] at hx
  linear_combination hs + hx - κ * hH - ab * hsp - ab * hxp + h2 - e1 - e2

/-- **Insider's best response.** For price impact `c > 0`, `(θ - c d) d ≤ θ²/(4c)` with equality at `d = θ/(2c)`. -/
theorem p1_insider_best_response (θ c d : ℝ) (hc : 0 < c) :
    (θ - c * d) * d ≤ θ ^ 2 / (4 * c) ∧ (θ - c * (θ / (2 * c))) * (θ / (2 * c)) = θ ^ 2 / (4 * c) := by
  constructor
  · rw [le_div_iff₀ (by positivity)]
    nlinarith [sq_nonneg (2 * c * d - θ)]
  · field_simp
    ring

/-- **Kyle limit.** With `κ = 0` and `D = 1`: `b = 1/(2λ)` and `λ (σ_ξ² + b² σ_θ²) = b σ_θ²` give `4 λ² σ_ξ² = σ_θ²`. -/
theorem p1_insider_kyle_limit (lam b sT2 sX2 : ℝ) (hlam : lam ≠ 0) (hb : b = 1 / (2 * lam))
    (hproj : lam * (sX2 + b ^ 2 * sT2) = b * sT2) : 4 * lam ^ 2 * sX2 = sT2 := by
  subst hb
  field_simp at hproj
  nlinarith [hproj]

/-- **Posterior variance.** `σ_θ² - λ² σ_ν² = σ_θ² σ_ξ²/σ_ν²` when `λ = b σ_θ²/σ_ν²` and `σ_ν² = σ_ξ² + b² σ_θ²`. -/
theorem p1_insider_posterior_variance (b sT2 sX2 sN2 lam : ℝ) (hN : sN2 = sX2 + b ^ 2 * sT2) (hpos : sN2 ≠ 0)
    (hlam : lam = b * sT2 / sN2) : sT2 - lam ^ 2 * sN2 = sT2 * sX2 / sN2 := by
  subst hlam
  rw [eq_div_iff hpos]
  field_simp
  rw [hN]; ring

end CurrentMM
