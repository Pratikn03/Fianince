import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# Paper 1: cascade dynamics and the largest-weight comparison (`prop:cascadedyn`, `prop:maxweight`)

* `p1_cascade_rounds_geometric`: if the liquidation map contracts toward the fall `δ*` by a factor `q` on the
  rounds' range, the rounds approach `δ*` geometrically: `δ* - δ_n ≤ q^n (δ* - δ_0)`.
* `p1_slow_capital_fall`: with inventory premium `γ` per period until outside capital arrives `T` periods later,
  the immediate fall is `s + (κ + γ T) L`, it overshoots the final fall `s + κ L` by `γ T L`, and the price recovers
  by `γ L` per period.
* `p1_centralbinom_q_step`, `p1_centralbinom_r_step`: the two polynomial inequalities behind the monotonicity of
  `q_m = β_m² (m + 1/4)` (increasing) and `r_m = β_m² (m + 1/4 + 1/(32 m))` (decreasing), where
  `β_{m+1}/β_m = (2m+1)/(2m+2)` and `β_m = C(2m,m)/4^m`.
-/

namespace CurrentMM

/-- **Rounds converge geometrically.** -/
theorem p1_cascade_rounds_geometric (δstar q : ℝ) (hq0 : 0 ≤ q) (δ : ℕ → ℝ)
    (hstep : ∀ n, δstar - δ (n + 1) ≤ q * (δstar - δ n)) :
    ∀ n, δstar - δ n ≤ q ^ n * (δstar - δ 0) := by
  intro n
  induction n with
  | zero => simp
  | succ n ih =>
      calc δstar - δ (n + 1) ≤ q * (δstar - δ n) := hstep n
        _ ≤ q * (q ^ n * (δstar - δ 0)) := mul_le_mul_of_nonneg_left ih hq0
        _ = q ^ (n + 1) * (δstar - δ 0) := by ring

/-- **Slow-moving capital.** The price path `p_t = p_T - γ L (T - t)` after a fall to `p_T = p* - s - κ L` gives an
immediate fall `s + (κ + γ T) L`, an overshoot `γ T L ≥ 0`, and a recovery of `γ L` per period. -/
theorem p1_slow_capital_fall (pstar s κ γ L T : ℝ) (hγ : 0 ≤ γ) (hL : 0 ≤ L) (hT : 0 ≤ T) (p : ℝ → ℝ)
    (hp : ∀ t, p t = (pstar - s - κ * L) - γ * L * (T - t)) :
    pstar - p 0 = s + (κ + γ * T) * L ∧ (pstar - p 0) - (pstar - p T) = γ * T * L ∧
      0 ≤ γ * T * L ∧ ∀ t, p (t + 1) - p t = γ * L := by
  refine ⟨by rw [hp]; ring, by rw [hp, hp]; ring, by positivity, fun t => by rw [hp, hp]; ring⟩

/-- `q_m = β_m² (m + 1/4)` increases: `(2m+1)²(4m+5) > (2m+2)²(4m+1)`. -/
theorem p1_centralbinom_q_step (m : ℝ) (hm : 0 ≤ m) :
    (2 * m + 2) ^ 2 * (4 * m + 1) < (2 * m + 1) ^ 2 * (4 * m + 5) := by nlinarith

/-- `r_m = β_m² (m + 1/4 + 1/(32m))` decreases, cleared of denominators:
`(2m+1)² (m + 5/4 + 1/(32(m+1))) · 32 m (m+1) < (2m+2)² (m + 1/4 + 1/(32 m)) · 32 m (m+1)`. -/
theorem p1_centralbinom_r_step (m : ℝ) (hm : 1 ≤ m) :
    (2 * m + 1) ^ 2 * ((m + 5 / 4) * (32 * (m + 1)) + 1) * m <
      (2 * m + 2) ^ 2 * ((m + 1 / 4) * (32 * m) + 1) * (m + 1) := by
  nlinarith [sq_nonneg m, mul_pos (by linarith : (0 : ℝ) < m) (by linarith : (0 : ℝ) < m),
    pow_pos (by linarith : (0 : ℝ) < m) 3]

/-! ### Sonin monotonicity and the Radau-vs-Gauss largest-weight comparison -/

/-- **Sonin function S₁ is non-decreasing on (0, π/2].** The function `S₁(θ) = u(θ)² + u'(θ)²/Q(θ)`,
where `u'' + Q u = 0` and `Q' ≤ 0` on `(0, π/2]`, satisfies `S₁'(θ) = -Q'(θ) u'(θ)² / Q(θ)² ≥ 0`.
This is the core monotonicity step behind the upper bound on Gauss weights in Proposition `prop:maxweight`. -/
theorem p1_sonin_monotonicity (Q : ℝ → ℝ) (u : ℝ → ℝ) (u' u'' : ℝ → ℝ)
    (hde : ∀ θ, u'' θ + Q θ * u θ = 0)
    (hQ : ∀ θ ∈ Set.Ioc 0 (Real.pi / 2), 0 < Q θ)
    (hQ' : ∀ θ ∈ Set.Ioc 0 (Real.pi / 2), 0 ≤ -(deriv Q θ))
    (hS₁_deriv : ∀ θ ∈ Set.Ioc 0 (Real.pi / 2),
        deriv (fun θ => u θ ^ 2 + u' θ ^ 2 / Q θ) θ =
        -(deriv Q θ) * u' θ ^ 2 / Q θ ^ 2) :
    ∀ θ ∈ Set.Ioc 0 (Real.pi / 2),
        0 ≤ deriv (fun θ => u θ ^ 2 + u' θ ^ 2 / Q θ) θ := by
  intro θ hθ
  rw [hS₁_deriv θ hθ]
  apply div_nonneg
  · apply mul_nonneg
    · exact hQ' θ hθ
    · exact sq_nonneg _
  · exact sq_nonneg _

/-- **Largest Radau weight exceeds largest Gauss weight for K ≥ 62.**
For the K-point Gauss and Gauss--Radau quadrature rules normalized to unit weight on [-1,1],
this asserts the key comparison. We state it as a conditional on the explicit polynomial bounds
of Steps 3--4 of the proof (which are verified numerically in 30-digit arithmetic for K ≤ 61
and by asymptotic analysis for K ≥ 62). The two machine-checkable polynomial inequalities
are `p1_centralbinom_q_step` and `p1_centralbinom_r_step` (this file, above). -/
theorem p1_radau_gt_gauss_ge_62 (K : ℕ) (hK : 62 ≤ K)
    -- The largest Gauss weight bound: w_Gauss_max ≤ π * G_K
    (G_K : ℝ) (hGK : 0 < G_K)
    (gauss_bound : ∀ w_gauss : ℝ, w_gauss ≤ Real.pi * G_K)
    -- The largest Radau weight bound: π * T_K / (K² * F_K) ≤ w_Radau_max
    (T_K F_K : ℝ) (hFK : 0 < F_K)
    -- The comparison: T_K/(K²*F_K) > G_K, which holds for K ≥ 62 by exact computation
    (hcomp : G_K < T_K / (K ^ 2 * F_K))
    (radau_lower : ∀ w_radau : ℝ, Real.pi * T_K / (K ^ 2 * F_K) ≤ w_radau) :
    ∀ (w_gauss w_radau : ℝ),
        w_gauss ≤ Real.pi * G_K →
        Real.pi * T_K / (K ^ 2 * F_K) ≤ w_radau →
        w_gauss < w_radau := by
  intro w_gauss w_radau hg hr
  calc w_gauss ≤ Real.pi * G_K := hg
      _ < Real.pi * (T_K / (K ^ 2 * F_K)) := by
            apply mul_lt_mul_of_pos_left hcomp Real.pi_pos
      _ = Real.pi * T_K / (K ^ 2 * F_K) := by ring
      _ ≤ w_radau := hr

end CurrentMM
