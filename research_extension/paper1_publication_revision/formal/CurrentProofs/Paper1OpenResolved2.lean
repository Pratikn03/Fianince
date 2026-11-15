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

end CurrentMM
