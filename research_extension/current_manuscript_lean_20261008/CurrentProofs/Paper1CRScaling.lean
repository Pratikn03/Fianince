import Mathlib.Analysis.Calculus.Deriv.Add
import Mathlib.Analysis.Calculus.Deriv.Mul
import Mathlib.Analysis.Calculus.Deriv.Pow
import Mathlib.Analysis.Calculus.Deriv.Inv
import Mathlib.Analysis.Complex.RealDeriv
import Mathlib.Analysis.Complex.Basic

/-!
# Paper 1, Proposition S7.1 (iii), Phase 3: the cubic cancellation along the weak direction

Let `K(λ) = w₁/(1 - r₁λ) + w₂/(1 - r₂λ)` be the generating function of the two-cohort kernel `k_m = w₁r₁^m + w₂r₂^m`
(merged weights `w`, memory rates `r`). Let `d = r₂ - r₁` and take the direction `v = (1, -1, d/(2w₁), d/(2w₂))` in
the parameter `θ = (w₁, w₂, r₁, r₂)`.

* `p1_K2_dirDeriv`: the derivative of `s ↦ K(θ + s v)(λ)` at `s = 0` is
  `DK[v](λ) = d³λ³ / (2(1 - r₁λ)²(1 - r₂λ)²)`. The derivative is computed from the quotient rule, not assumed.
* `p1_K2_dirDeriv_real`: the same for real directions, i.e. for the actual real parameter map.
* `p1_K2_moment_dirDeriv`: the derivative of the kernel moment `k_m(θ + s v)` at `s = 0` is
  `r₁^m - r₂^m + (d/2) m (r₁^{m-1} + r₂^{m-1})`.
* `p1_K2_moment_cancel`: this vanishes for `m = 0, 1, 2`, and equals `d³/2` for `m = 3`.
* `p1_one_sub_mul_norm_ge`, `p1_K2_dirDeriv_bound`: on the closed unit disk, with `|rᵢ| ≤ ρ < 1`, the denominators
  satisfy `‖1 - rᵢλ‖ ≥ 1 - ρ`, and `‖DK[v](λ)‖ ≤ |d|³/(2(1-ρ)⁴)`.
-/

namespace CurrentMM

/-- **Directional derivative of the two-cohort kernel along `v`, with the cubic cancellation.** -/
theorem p1_K2_dirDeriv (w1 w2 r1 r2 x : ℂ) (hw1 : w1 ≠ 0) (hw2 : w2 ≠ 0) (hA : 1 - r1 * x ≠ 0)
    (hB : 1 - r2 * x ≠ 0) :
    HasDerivAt (fun s : ℂ => (w1 + s) / (1 - (r1 + s * ((r2 - r1) / (2 * w1))) * x) +
        (w2 - s) / (1 - (r2 + s * ((r2 - r1) / (2 * w2))) * x))
      ((r2 - r1) ^ 3 * x ^ 3 / (2 * (1 - r1 * x) ^ 2 * (1 - r2 * x) ^ 2)) 0 := by
  have hA0 : 1 - (r1 + 0 * ((r2 - r1) / (2 * w1))) * x ≠ 0 := by simpa using hA
  have hB0 : 1 - (r2 + 0 * ((r2 - r1) / (2 * w2))) * x ≠ 0 := by simpa using hB
  have n1 : HasDerivAt (fun s : ℂ => w1 + s) 1 0 := HasDerivAt.const_add w1 (hasDerivAt_id' (0 : ℂ))
  have n2 : HasDerivAt (fun s : ℂ => w2 - s) (-1) 0 := HasDerivAt.const_sub w2 (hasDerivAt_id' (0 : ℂ))
  have d1 : HasDerivAt (fun s : ℂ => 1 - (r1 + s * ((r2 - r1) / (2 * w1))) * x)
      (-(1 * ((r2 - r1) / (2 * w1)) * x)) 0 :=
    HasDerivAt.const_sub 1 (HasDerivAt.mul_const
      (HasDerivAt.const_add r1 (HasDerivAt.mul_const (hasDerivAt_id' (0 : ℂ)) ((r2 - r1) / (2 * w1)))) x)
  have d2 : HasDerivAt (fun s : ℂ => 1 - (r2 + s * ((r2 - r1) / (2 * w2))) * x)
      (-(1 * ((r2 - r1) / (2 * w2)) * x)) 0 :=
    HasDerivAt.const_sub 1 (HasDerivAt.mul_const
      (HasDerivAt.const_add r2 (HasDerivAt.mul_const (hasDerivAt_id' (0 : ℂ)) ((r2 - r1) / (2 * w2)))) x)
  have h1 := HasDerivAt.fun_div n1 d1 hA0
  have h2 := HasDerivAt.fun_div n2 d2 hB0
  refine (HasDerivAt.fun_add h1 h2).congr_deriv ?_
  simp only [add_zero, sub_zero, zero_mul, one_mul]
  first
  | (field_simp; ring)
  | field_simp

/-- The same derivative along real directions, for real parameters. -/
theorem p1_K2_dirDeriv_real (w1 w2 r1 r2 : ℝ) (x : ℂ) (hw1 : w1 ≠ 0) (hw2 : w2 ≠ 0)
    (hA : 1 - (r1 : ℂ) * x ≠ 0) (hB : 1 - (r2 : ℂ) * x ≠ 0) :
    HasDerivAt (fun s : ℝ => ((w1 + s : ℝ) : ℂ) / (1 - ((r1 + s * ((r2 - r1) / (2 * w1)) : ℝ) : ℂ) * x) +
        ((w2 - s : ℝ) : ℂ) / (1 - ((r2 + s * ((r2 - r1) / (2 * w2)) : ℝ) : ℂ) * x))
      (((r2 - r1 : ℝ) : ℂ) ^ 3 * x ^ 3 / (2 * (1 - (r1 : ℂ) * x) ^ 2 * (1 - (r2 : ℂ) * x) ^ 2)) 0 := by
  have hw1' : (w1 : ℂ) ≠ 0 := by exact_mod_cast hw1
  have hw2' : (w2 : ℂ) ≠ 0 := by exact_mod_cast hw2
  have h := p1_K2_dirDeriv (w1 : ℂ) (w2 : ℂ) (r1 : ℂ) (r2 : ℂ) x hw1' hw2' hA hB
  rw [show (0 : ℂ) = ((0 : ℝ) : ℂ) by simp] at h
  have h' := h.comp_ofReal
  push_cast at h' ⊢
  exact h'

/-- **Directional derivative of each kernel moment.** -/
theorem p1_K2_moment_dirDeriv (w1 w2 r1 r2 : ℝ) (m : ℕ) (hw1 : w1 ≠ 0) (hw2 : w2 ≠ 0) :
    HasDerivAt (fun s : ℝ => (w1 + s) * (r1 + s * ((r2 - r1) / (2 * w1))) ^ m +
        (w2 - s) * (r2 + s * ((r2 - r1) / (2 * w2))) ^ m)
      (r1 ^ m - r2 ^ m + (r2 - r1) / 2 * m * (r1 ^ (m - 1) + r2 ^ (m - 1))) 0 := by
  have e1 : HasDerivAt (fun s : ℝ => r1 + s * ((r2 - r1) / (2 * w1))) (1 * ((r2 - r1) / (2 * w1))) 0 :=
    HasDerivAt.const_add r1 (HasDerivAt.mul_const (hasDerivAt_id' (0 : ℝ)) ((r2 - r1) / (2 * w1)))
  have e2 : HasDerivAt (fun s : ℝ => r2 + s * ((r2 - r1) / (2 * w2))) (1 * ((r2 - r1) / (2 * w2))) 0 :=
    HasDerivAt.const_add r2 (HasDerivAt.mul_const (hasDerivAt_id' (0 : ℝ)) ((r2 - r1) / (2 * w2)))
  have g1 := HasDerivAt.fun_pow e1 m
  have g2 := HasDerivAt.fun_pow e2 m
  have n1 : HasDerivAt (fun s : ℝ => w1 + s) 1 0 := HasDerivAt.const_add w1 (hasDerivAt_id' (0 : ℝ))
  have n2 : HasDerivAt (fun s : ℝ => w2 - s) (-1) 0 := HasDerivAt.const_sub w2 (hasDerivAt_id' (0 : ℝ))
  have h1 := HasDerivAt.fun_mul n1 g1
  have h2 := HasDerivAt.fun_mul n2 g2
  refine (HasDerivAt.fun_add h1 h2).congr_deriv ?_
  simp only [add_zero, sub_zero, zero_mul, one_mul, mul_one]
  first
  | (field_simp; ring)
  | field_simp

/-- **The cancellation in moment form.** Along `v`, the moments of orders `0, 1, 2` are stationary and the third moment
moves at rate `d³/2`. -/
theorem p1_K2_moment_cancel (r1 r2 : ℝ) :
    (r1 ^ 0 - r2 ^ 0 + (r2 - r1) / 2 * (0 : ℕ) * (r1 ^ (0 - 1) + r2 ^ (0 - 1)) = 0) ∧
    (r1 ^ 1 - r2 ^ 1 + (r2 - r1) / 2 * (1 : ℕ) * (r1 ^ (1 - 1) + r2 ^ (1 - 1)) = 0) ∧
    (r1 ^ 2 - r2 ^ 2 + (r2 - r1) / 2 * (2 : ℕ) * (r1 ^ (2 - 1) + r2 ^ (2 - 1)) = 0) ∧
    (r1 ^ 3 - r2 ^ 3 + (r2 - r1) / 2 * (3 : ℕ) * (r1 ^ (3 - 1) + r2 ^ (3 - 1)) = (r2 - r1) ^ 3 / 2) := by
  refine ⟨by simp, by norm_num <;> ring, by norm_num <;> ring, by norm_num <;> ring⟩

/-- `‖1 - rλ‖ ≥ 1 - ρ` when `‖r‖ ≤ ρ` and `‖λ‖ ≤ 1`. -/
theorem p1_one_sub_mul_norm_ge (r x : ℂ) (ρ : ℝ) (hr : ‖r‖ ≤ ρ) (hx : ‖x‖ ≤ 1) : 1 - ρ ≤ ‖1 - r * x‖ := by
  have h := norm_sub_norm_le (1 : ℂ) (r * x)
  rw [norm_one, norm_mul] at h
  have h2 : ‖r‖ * ‖x‖ ≤ ρ := by
    calc ‖r‖ * ‖x‖ ≤ ‖r‖ * 1 := mul_le_mul_of_nonneg_left hx (norm_nonneg r)
      _ = ‖r‖ := mul_one _
      _ ≤ ρ := hr
  linarith

/-- **The weak direction moves the kernel by at most `|d|³/(2(1-ρ)⁴)` on the closed unit disk.** -/
theorem p1_K2_dirDeriv_bound (r1 r2 x : ℂ) (ρ : ℝ) (hρ : ρ < 1) (h1 : ‖r1‖ ≤ ρ) (h2 : ‖r2‖ ≤ ρ)
    (hx : ‖x‖ ≤ 1) :
    ‖(r2 - r1) ^ 3 * x ^ 3 / (2 * (1 - r1 * x) ^ 2 * (1 - r2 * x) ^ 2)‖ ≤ ‖r2 - r1‖ ^ 3 / (2 * (1 - ρ) ^ 4) := by
  have hA := p1_one_sub_mul_norm_ge r1 x ρ h1 hx
  have hB := p1_one_sub_mul_norm_ge r2 x ρ h2 hx
  have hρ0 : 0 < 1 - ρ := by linarith
  rw [norm_div, norm_mul, norm_mul, norm_mul, norm_pow, norm_pow, norm_pow, norm_pow]
  have hnum : ‖r2 - r1‖ ^ 3 * ‖x‖ ^ 3 ≤ ‖r2 - r1‖ ^ 3 :=
    mul_le_of_le_one_right (by positivity) (pow_le_one₀ (norm_nonneg x) hx)
  have hden : 2 * (1 - ρ) ^ 4 ≤ ‖(2 : ℂ)‖ * ‖1 - r1 * x‖ ^ 2 * ‖1 - r2 * x‖ ^ 2 := by
    rw [show ‖(2 : ℂ)‖ = 2 by simp]
    have hA2 : (1 - ρ) ^ 2 ≤ ‖1 - r1 * x‖ ^ 2 := pow_le_pow_left₀ hρ0.le hA 2
    have hB2 : (1 - ρ) ^ 2 ≤ ‖1 - r2 * x‖ ^ 2 := pow_le_pow_left₀ hρ0.le hB 2
    nlinarith [mul_le_mul hA2 hB2 (by positivity) (by positivity)]
  have hpos : 0 < 2 * (1 - ρ) ^ 4 := by positivity
  calc ‖r2 - r1‖ ^ 3 * ‖x‖ ^ 3 / (‖(2 : ℂ)‖ * ‖1 - r1 * x‖ ^ 2 * ‖1 - r2 * x‖ ^ 2)
      ≤ ‖r2 - r1‖ ^ 3 / (‖(2 : ℂ)‖ * ‖1 - r1 * x‖ ^ 2 * ‖1 - r2 * x‖ ^ 2) :=
        div_le_div_of_nonneg_right hnum (by positivity)
    _ ≤ ‖r2 - r1‖ ^ 3 / (2 * (1 - ρ) ^ 4) := div_le_div_of_nonneg_left (by positivity) hpos hden

end CurrentMM
