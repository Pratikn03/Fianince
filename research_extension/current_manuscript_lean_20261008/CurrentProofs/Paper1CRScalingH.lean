import CurrentProofs.Paper1CRScaling

/-!
# Paper 1, Proposition S7.1 (iii), Phase 4: the cancellation reaches the price response

In the delay variable `x = 1/z`, the two-cohort price response is
`H(x) = κ / (1 - a x - κ x K(x))`, with `K(x) = w₁/(1 - r₁x) + w₂/(1 - r₂x)`. This is `tfTop/tfBottom` after the
reflection `x = 1/z` (`Paper1ModelLink`).

* `p1_H2_dirDeriv`: along `v = (1, -1, d/(2w₁), d/(2w₂))`, the response moves at rate `DH[v] = x H² DK[v]`, with the
  cubic `DK[v]` of `p1_K2_dirDeriv`.
* `p1_K2_norm_le`, `p1_H2_den_norm_ge`, `p1_H2_norm_le`: on the closed unit disk, with nonnegative weights,
  `|rᵢ| ≤ ρ < 1` and the stability margin `|a| + |κ|(w₁ + w₂)/(1 - ρ) ≤ s < 1`, we have
  `‖K‖ ≤ (w₁ + w₂)/(1 - ρ)` and `‖1 - ax - κxK‖ ≥ 1 - s`, so `‖H‖ ≤ M := |κ|/(1 - s)`. Here `M` is derived from the
  family's constants, not assumed.
* `p1_H2_dirDeriv_bound`: `‖DH[v](x)‖ ≤ M² |d|³ / (2(1 - ρ)⁴)` on the closed unit disk.
-/

namespace CurrentMM

/-- The quotient-rule algebra behind `p1_H2_dirDeriv`. -/
theorem p1_H2_deriv_alg (κ x X E : ℂ) (hX : X ≠ 0) :
    (0 - κ * -(κ * x * E)) / X ^ 2 = x * (κ / X) ^ 2 * E := by
  field_simp
  ring

/-- **The directional derivative of the price response.** -/
theorem p1_H2_dirDeriv (a κ w1 w2 r1 r2 x : ℂ) (hw1 : w1 ≠ 0) (hw2 : w2 ≠ 0) (hA : 1 - r1 * x ≠ 0)
    (hB : 1 - r2 * x ≠ 0) (hD : 1 - a * x - κ * x * (w1 / (1 - r1 * x) + w2 / (1 - r2 * x)) ≠ 0) :
    HasDerivAt (fun s : ℂ => κ / (1 - a * x - κ * x * ((w1 + s) / (1 - (r1 + s * ((r2 - r1) / (2 * w1))) * x) +
        (w2 - s) / (1 - (r2 + s * ((r2 - r1) / (2 * w2))) * x))))
      (x * (κ / (1 - a * x - κ * x * (w1 / (1 - r1 * x) + w2 / (1 - r2 * x)))) ^ 2 *
        ((r2 - r1) ^ 3 * x ^ 3 / (2 * (1 - r1 * x) ^ 2 * (1 - r2 * x) ^ 2))) 0 := by
  have hK := p1_K2_dirDeriv w1 w2 r1 r2 x hw1 hw2 hA hB
  have hden := HasDerivAt.const_sub (1 - a * x) (HasDerivAt.const_mul (κ * x) hK)
  have hD0 : 1 - a * x - κ * x * ((w1 + 0) / (1 - (r1 + 0 * ((r2 - r1) / (2 * w1))) * x) +
      (w2 - 0) / (1 - (r2 + 0 * ((r2 - r1) / (2 * w2))) * x)) ≠ 0 := by simpa using hD
  have h := HasDerivAt.fun_div (hasDerivAt_const (0 : ℂ) κ) hden hD0
  refine h.congr_deriv ?_
  simp only [add_zero, sub_zero, zero_mul]
  first
  | exact p1_H2_deriv_alg κ x _ _ hD
  | (generalize hX : 1 - a * x - κ * x * (w1 / (1 - r1 * x) + w2 / (1 - r2 * x)) = X at hD ⊢
     field_simp
     ring)

/-- `‖K(x)‖ ≤ (w₁ + w₂)/(1 - ρ)` on the closed unit disk. -/
theorem p1_K2_norm_le (w1 w2 : ℝ) (hw1 : 0 ≤ w1) (hw2 : 0 ≤ w2) (r1 r2 x : ℂ) (ρ : ℝ) (hρ : ρ < 1)
    (h1 : ‖r1‖ ≤ ρ) (h2 : ‖r2‖ ≤ ρ) (hx : ‖x‖ ≤ 1) :
    ‖(w1 : ℂ) / (1 - r1 * x) + (w2 : ℂ) / (1 - r2 * x)‖ ≤ (w1 + w2) / (1 - ρ) := by
  have hA := p1_one_sub_mul_norm_ge r1 x ρ h1 hx
  have hB := p1_one_sub_mul_norm_ge r2 x ρ h2 hx
  have hρ0 : 0 < 1 - ρ := by linarith
  have e1 : ‖(w1 : ℂ) / (1 - r1 * x)‖ ≤ w1 / (1 - ρ) := by
    rw [norm_div, Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg hw1]
    exact div_le_div_of_nonneg_left hw1 hρ0 hA
  have e2 : ‖(w2 : ℂ) / (1 - r2 * x)‖ ≤ w2 / (1 - ρ) := by
    rw [norm_div, Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg hw2]
    exact div_le_div_of_nonneg_left hw2 hρ0 hB
  calc _ ≤ ‖(w1 : ℂ) / (1 - r1 * x)‖ + ‖(w2 : ℂ) / (1 - r2 * x)‖ := norm_add_le _ _
    _ ≤ w1 / (1 - ρ) + w2 / (1 - ρ) := add_le_add e1 e2
    _ = (w1 + w2) / (1 - ρ) := by ring

/-- The denominator of `H` stays at least `1 - s` away from zero on the closed unit disk. -/
theorem p1_H2_den_norm_ge (a κ w1 w2 : ℝ) (hw1 : 0 ≤ w1) (hw2 : 0 ≤ w2) (r1 r2 x : ℂ) (ρ s : ℝ)
    (hρ : ρ < 1) (h1 : ‖r1‖ ≤ ρ) (h2 : ‖r2‖ ≤ ρ) (hx : ‖x‖ ≤ 1)
    (hs : |a| + |κ| * ((w1 + w2) / (1 - ρ)) ≤ s) :
    1 - s ≤ ‖1 - (a : ℂ) * x - (κ : ℂ) * x * ((w1 : ℂ) / (1 - r1 * x) + (w2 : ℂ) / (1 - r2 * x))‖ := by
  have hK := p1_K2_norm_le w1 w2 hw1 hw2 r1 r2 x ρ hρ h1 h2 hx
  have hax : ‖(a : ℂ) * x‖ ≤ |a| := by
    rw [norm_mul, Complex.norm_real, Real.norm_eq_abs]
    exact mul_le_of_le_one_right (abs_nonneg a) hx
  have hkx : ‖(κ : ℂ) * x * ((w1 : ℂ) / (1 - r1 * x) + (w2 : ℂ) / (1 - r2 * x))‖ ≤
      |κ| * ((w1 + w2) / (1 - ρ)) := by
    rw [norm_mul, norm_mul, Complex.norm_real, Real.norm_eq_abs]
    calc |κ| * ‖x‖ * ‖(w1 : ℂ) / (1 - r1 * x) + (w2 : ℂ) / (1 - r2 * x)‖
        ≤ |κ| * 1 * ((w1 + w2) / (1 - ρ)) := by
          apply mul_le_mul (mul_le_mul_of_nonneg_left hx (abs_nonneg κ)) hK (norm_nonneg _)
          positivity
      _ = |κ| * ((w1 + w2) / (1 - ρ)) := by ring
  have t1 := norm_sub_norm_le (1 - (a : ℂ) * x) ((κ : ℂ) * x * ((w1 : ℂ) / (1 - r1 * x) + (w2 : ℂ) / (1 - r2 * x)))
  have t2 := norm_sub_norm_le (1 : ℂ) ((a : ℂ) * x)
  rw [norm_one] at t2
  linarith

/-- **`‖H‖ ≤ M = |κ|/(1 - s)` on the closed unit disk.** -/
theorem p1_H2_norm_le (a κ w1 w2 : ℝ) (hw1 : 0 ≤ w1) (hw2 : 0 ≤ w2) (r1 r2 x : ℂ) (ρ s : ℝ)
    (hρ : ρ < 1) (hs1 : s < 1) (h1 : ‖r1‖ ≤ ρ) (h2 : ‖r2‖ ≤ ρ) (hx : ‖x‖ ≤ 1)
    (hs : |a| + |κ| * ((w1 + w2) / (1 - ρ)) ≤ s) :
    ‖(κ : ℂ) / (1 - (a : ℂ) * x - (κ : ℂ) * x * ((w1 : ℂ) / (1 - r1 * x) + (w2 : ℂ) / (1 - r2 * x)))‖ ≤
      |κ| / (1 - s) := by
  have hD := p1_H2_den_norm_ge a κ w1 w2 hw1 hw2 r1 r2 x ρ s hρ h1 h2 hx hs
  have hs0 : 0 < 1 - s := by linarith
  rw [norm_div, Complex.norm_real, Real.norm_eq_abs]
  exact div_le_div_of_nonneg_left (abs_nonneg κ) hs0 hD

/-- **The response moves by at most `M²|d|³/(2(1-ρ)⁴)` along the weak direction.** -/
theorem p1_H2_dirDeriv_bound (a κ w1 w2 : ℝ) (hw1 : 0 ≤ w1) (hw2 : 0 ≤ w2) (r1 r2 x : ℂ) (ρ s : ℝ)
    (hρ : ρ < 1) (hs1 : s < 1) (h1 : ‖r1‖ ≤ ρ) (h2 : ‖r2‖ ≤ ρ) (hx : ‖x‖ ≤ 1)
    (hs : |a| + |κ| * ((w1 + w2) / (1 - ρ)) ≤ s) :
    ‖x * ((κ : ℂ) / (1 - (a : ℂ) * x - (κ : ℂ) * x * ((w1 : ℂ) / (1 - r1 * x) + (w2 : ℂ) / (1 - r2 * x)))) ^ 2 *
        ((r2 - r1) ^ 3 * x ^ 3 / (2 * (1 - r1 * x) ^ 2 * (1 - r2 * x) ^ 2))‖ ≤
      (|κ| / (1 - s)) ^ 2 * (‖r2 - r1‖ ^ 3 / (2 * (1 - ρ) ^ 4)) := by
  have hH := p1_H2_norm_le a κ w1 w2 hw1 hw2 r1 r2 x ρ s hρ hs1 h1 h2 hx hs
  have hK := p1_K2_dirDeriv_bound r1 r2 x ρ hρ h1 h2 hx
  rw [norm_mul, norm_mul, norm_pow]
  have hH2 := pow_le_pow_left₀ (norm_nonneg _) hH 2
  calc ‖x‖ * ‖(κ : ℂ) / (1 - (a : ℂ) * x - (κ : ℂ) * x * ((w1 : ℂ) / (1 - r1 * x) + (w2 : ℂ) / (1 - r2 * x)))‖ ^ 2 *
        ‖(r2 - r1) ^ 3 * x ^ 3 / (2 * (1 - r1 * x) ^ 2 * (1 - r2 * x) ^ 2)‖
      ≤ 1 * (|κ| / (1 - s)) ^ 2 * (‖r2 - r1‖ ^ 3 / (2 * (1 - ρ) ^ 4)) := by
        apply mul_le_mul (mul_le_mul hx hH2 (by positivity) zero_le_one) hK (norm_nonneg _)
        positivity
    _ = (|κ| / (1 - s)) ^ 2 * (‖r2 - r1‖ ^ 3 / (2 * (1 - ρ) ^ 4)) := by ring

end CurrentMM
