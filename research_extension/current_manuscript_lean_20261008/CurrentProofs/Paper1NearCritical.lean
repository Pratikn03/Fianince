import Mathlib.Analysis.SpecialFunctions.Log.Deriv
import Mathlib.MeasureTheory.Integral.IntervalIntegral.Basic
import Mathlib.Analysis.Complex.Basic
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic

/-!
# Paper 1: the barrier near instability (core `prop:nearcrit`, Steps 2 and 3)

The proof of `prop:nearcrit` bounds the Kullback-Leibler rate of the passive price records of two economies whose
characteristic functions are `D_A` and `D_B = D_A + Δ` on the unit circle. This file formalizes Steps 2 and 3:

* `p1_nearcrit_lower`: a complex number `D` with `|Im D| ≥ c₁ |ω|` and `Re D ≥ -C₂ ω²`, for `|ω| ≤ δ`, satisfies
  `|D + ε| ≥ c₃ (ε + |ω|)` for every `ε ≥ 0`, with an explicit `c₃` (the case analysis of Step 2).
* `p1_ratio_bound`: if moreover `|Δ| ≤ M |ω|`, then `|Δ / (D + ε)| ≤ M / c₃`, uniformly in `ε` (Step 3).
* `p1_spectral_ratio_close`: `u = |1 + z|^{-2}` satisfies `|u - 1| ≤ 4 |z|` when `|z| ≤ 1/8`.
* `p1_kl_integrand_le`: `u - 1 - log u ≤ 2 (u - 1)²` when `|u - 1| ≤ 1/2`.
* `p1_nearcrit_kl_bound`: if the Kullback-Leibler rate is given by Whittle's formula
  `(1/4π) ∫_{-π}^{π} (u - 1 - log u)` and `|z(ω)| ≤ ρ ≤ 1/8` on the circle, the rate is at most `16 ρ²`.
Whittle's formula for the rate, Step 1 (the bound on the kernel gap) and the local properties of `D*` near the
unit root (from primitivity) are hypotheses here; they are proved on paper.
-/

namespace CurrentMM

open Complex Real MeasureTheory intervalIntegral

/-- **Step 2: the lower bound on the characteristic function near the unit root.** -/
theorem p1_nearcrit_lower (D : ℂ) (ω ε c₁ C₂ δ : ℝ) (hc₁ : 0 < c₁) (hC₂ : 0 ≤ C₂) (hδ : 0 ≤ δ)
    (hω : |ω| ≤ δ) (hε : 0 ≤ ε) (him : c₁ * |ω| ≤ |D.im|) (hre : -C₂ * ω ^ 2 ≤ D.re) :
    min (min (1 / 2) c₁ / 2) (c₁ / (2 * C₂ * δ + 1)) * (ε + |ω|) ≤ ‖D + ε‖ := by
  set c₃ := min (min (1 / 2) c₁ / 2) (c₁ / (2 * C₂ * δ + 1)) with hc₃
  have hden : 0 < 2 * C₂ * δ + 1 := by positivity
  have hIm : |D.im| ≤ ‖D + ε‖ := by
    have := Complex.abs_im_le_norm (D + ε)
    simpa using this
  have hRe : |D.re + ε| ≤ ‖D + ε‖ := by
    have := Complex.abs_re_le_norm (D + ε)
    simpa using this
  have hω0 : 0 ≤ |ω| := abs_nonneg ω
  by_cases hcase : 2 * C₂ * ω ^ 2 ≤ ε
  · -- the real part is at least ε/2
    have hre2 : ε / 2 ≤ D.re + ε := by nlinarith
    have hRe2 : ε / 2 ≤ ‖D + ε‖ := hre2.trans ((le_abs_self _).trans hRe)
    have hIm2 : c₁ * |ω| ≤ ‖D + ε‖ := him.trans hIm
    have hm : min (1 / 2) c₁ ≤ 1 / 2 := min_le_left _ _
    have hm' : min (1 / 2) c₁ ≤ c₁ := min_le_right _ _
    have hm0 : 0 < min (1 / 2) c₁ := lt_min (by norm_num) hc₁
    calc c₃ * (ε + |ω|) ≤ min (1 / 2) c₁ / 2 * (ε + |ω|) := by
          gcongr; exact min_le_left _ _
      _ = (min (1 / 2) c₁ * ε + min (1 / 2) c₁ * |ω|) / 2 := by ring
      _ ≤ (ε / 2 + c₁ * |ω|) / 2 := by gcongr <;> nlinarith
      _ ≤ ‖D + ε‖ := by linarith
  · push_neg at hcase
    -- ε < 2 C₂ ω² ≤ 2 C₂ δ |ω|, so ε + |ω| ≤ (2 C₂ δ + 1) |ω|
    have hωsq : ω ^ 2 ≤ δ * |ω| := by
      rw [← sq_abs]; nlinarith
    have hsum : ε + |ω| ≤ (2 * C₂ * δ + 1) * |ω| := by nlinarith
    calc c₃ * (ε + |ω|) ≤ c₁ / (2 * C₂ * δ + 1) * (ε + |ω|) := by
          gcongr; exact min_le_right _ _
      _ ≤ c₁ / (2 * C₂ * δ + 1) * ((2 * C₂ * δ + 1) * |ω|) := by gcongr
      _ = c₁ * |ω| := by field_simp
      _ ≤ ‖D + ε‖ := him.trans hIm

/-- **Step 3: the ratio is bounded uniformly in the margin.** If `|Δ| ≤ M |ω|` and `|D + ε| ≥ c₃ (ε + |ω|)` with
`ε ≥ 0`, then `|Δ| ≤ (M / c₃) |D + ε|`. -/
theorem p1_ratio_bound (Δ D : ℂ) (ω ε M c₃ : ℝ) (hc₃ : 0 < c₃) (hM : 0 ≤ M) (hε : 0 ≤ ε)
    (hΔ : ‖Δ‖ ≤ M * |ω|) (hD : c₃ * (ε + |ω|) ≤ ‖D + ε‖) :
    ‖Δ‖ ≤ M / c₃ * ‖D + ε‖ := by
  have h1 : M * |ω| ≤ M * (ε + |ω|) := by nlinarith
  calc ‖Δ‖ ≤ M * (ε + |ω|) := hΔ.trans h1
    _ = M / c₃ * (c₃ * (ε + |ω|)) := by field_simp
    _ ≤ M / c₃ * ‖D + ε‖ := by gcongr

/-- `u = |1 + z|^{-2}` is within `4 |z|` of one when `|z| ≤ 1/8`. -/
theorem p1_spectral_ratio_close (z : ℂ) (hz : ‖z‖ ≤ 1 / 8) :
    |(‖1 + z‖ ^ 2)⁻¹ - 1| ≤ 4 * ‖z‖ := by
  set ρ := ‖z‖ with hρ
  have hρ0 : 0 ≤ ρ := norm_nonneg z
  have hlo : 1 - ρ ≤ ‖1 + z‖ := by
    have := norm_sub_norm_le (1 : ℂ) (-z)
    simp only [norm_one, norm_neg, sub_neg_eq_add] at this
    linarith
  have hhi : ‖1 + z‖ ≤ 1 + ρ := by
    have := norm_add_le (1 : ℂ) z
    simpa using this
  have hpos : 0 < 1 - ρ := by linarith
  have hs_lo : (1 - ρ) ^ 2 ≤ ‖1 + z‖ ^ 2 := by gcongr
  have hs_hi : ‖1 + z‖ ^ 2 ≤ (1 + ρ) ^ 2 := by gcongr
  have hs_pos : 0 < ‖1 + z‖ ^ 2 := lt_of_lt_of_le (by positivity) hs_lo
  rw [abs_le]
  constructor
  · -- (‖1+z‖²)⁻¹ ≥ (1+ρ)⁻², and 1 - (1+ρ)⁻² ≤ 2ρ ≤ 4ρ
    have h1 : ((1 + ρ) ^ 2)⁻¹ ≤ (‖1 + z‖ ^ 2)⁻¹ := inv_anti₀ hs_pos hs_hi
    have h2 : 1 - 2 * ρ ≤ ((1 + ρ) ^ 2)⁻¹ := by
      rw [le_inv_comm₀ (by nlinarith) (by positivity)]
      · have : 0 < 1 - 2 * ρ := by linarith
        rw [inv_eq_one_div, le_div_iff₀ this]
        nlinarith [sq_nonneg ρ, mul_nonneg hρ0 (sq_nonneg ρ)]
    linarith
  · -- (‖1+z‖²)⁻¹ ≤ (1-ρ)⁻², and (1-ρ)⁻² - 1 ≤ 4ρ for ρ ≤ 1/8
    have h1 : (‖1 + z‖ ^ 2)⁻¹ ≤ ((1 - ρ) ^ 2)⁻¹ := inv_anti₀ (by positivity) hs_lo
    have h2 : ((1 - ρ) ^ 2)⁻¹ ≤ 1 + 4 * ρ := by
      rw [inv_eq_one_div, div_le_iff₀ (by positivity)]
      nlinarith [mul_nonneg hρ0 (show 0 ≤ 2 - 7 * ρ by linarith), pow_nonneg hρ0 3]
    linarith

/-- `u - 1 - log u ≤ 2 (u - 1)²` when `|u - 1| ≤ 1/2`. -/
theorem p1_kl_integrand_le (u : ℝ) (hu : |u - 1| ≤ 1 / 2) : u - 1 - Real.log u ≤ 2 * (u - 1) ^ 2 := by
  set x := 1 - u with hx
  have hx1 : |x| < 1 := by
    rw [hx, abs_sub_comm]; linarith
  have h := Real.abs_log_sub_add_sum_range_le hx1 1
  simp only [Finset.sum_range_one, zero_add, pow_one, Nat.cast_zero, div_one] at h
  have hux : 1 - x = u := by rw [hx]; ring
  rw [hux] at h
  have hxa : |x| ≤ 1 / 2 := by rw [hx, abs_sub_comm]; exact hu
  have hden : 1 / 2 ≤ 1 - |x| := by linarith
  have hb : |x| ^ 2 / (1 - |x|) ≤ 2 * x ^ 2 := by
    rw [div_le_iff₀ (by linarith), sq_abs]
    nlinarith [sq_nonneg x]
  have hl := (abs_le.mp (h.trans hb)).1
  have : (u - 1) ^ 2 = x ^ 2 := by rw [hx]; ring
  rw [this]
  have : u - 1 = -x := by rw [hx]; ring
  rw [this]
  linarith

/-- **The Kullback-Leibler rate near instability (Step 3).** Suppose the rate between the two passive records is given
by Whittle's formula `KL = (1/(4π)) ∫_{-π}^{π} (u - 1 - log u)` with `u(ω) = |1 + z(ω)|^{-2}` and
`z = Δ / D_A`, and that `|z(ω)| ≤ ρ ≤ 1/8` on the circle. Then `KL ≤ 16 ρ²`. With
`ρ = κ C₁ (Δη)^{2K-1} / c₃` from `p1_nearcrit_lower` and `p1_ratio_bound`, this is the bound of `prop:nearcrit`,
uniform in the stability margin. -/
theorem p1_nearcrit_kl_bound (z : ℝ → ℂ) (ρ KL : ℝ) (hρ0 : 0 ≤ ρ) (hρ : ρ ≤ 1 / 8)
    (hz : ∀ ω, ‖z ω‖ ≤ ρ)
    (hKL : KL = 1 / (4 * π) *
      ∫ ω in (-π)..π, ((‖1 + z ω‖ ^ 2)⁻¹ - 1 - Real.log ((‖1 + z ω‖ ^ 2)⁻¹))) :
    KL ≤ 16 * ρ ^ 2 := by
  have hpt : ∀ ω, ‖(‖1 + z ω‖ ^ 2)⁻¹ - 1 - Real.log ((‖1 + z ω‖ ^ 2)⁻¹)‖ ≤ 2 * (4 * ρ) ^ 2 := by
    intro ω
    set u := (‖1 + z ω‖ ^ 2)⁻¹ with hu
    have hclose : |u - 1| ≤ 4 * ρ := (p1_spectral_ratio_close (z ω) ((hz ω).trans hρ)).trans (by gcongr; exact hz ω)
    have hhalf : |u - 1| ≤ 1 / 2 := hclose.trans (by linarith)
    have hupos : 0 < u := by
      have := abs_le.mp hhalf; linarith
    have hnn : 0 ≤ u - 1 - Real.log u := by
      have := Real.log_le_sub_one_of_pos hupos; linarith
    rw [Real.norm_eq_abs, abs_of_nonneg hnn]
    calc u - 1 - Real.log u ≤ 2 * (u - 1) ^ 2 := p1_kl_integrand_le u hhalf
      _ = 2 * |u - 1| ^ 2 := by rw [sq_abs]
      _ ≤ 2 * (4 * ρ) ^ 2 := by gcongr
  have hint := intervalIntegral.norm_integral_le_of_norm_le_const (a := -π) (b := π)
    (fun ω _ => hpt ω)
  have hlen : |π - -π| = 2 * π := by rw [sub_neg_eq_add, abs_of_pos (by linarith [Real.pi_pos])]; ring
  rw [hlen] at hint
  have hpi : 0 < π := Real.pi_pos
  calc KL = 1 / (4 * π) * ∫ ω in (-π)..π, ((‖1 + z ω‖ ^ 2)⁻¹ - 1 - Real.log ((‖1 + z ω‖ ^ 2)⁻¹)) := hKL
    _ ≤ 1 / (4 * π) * ‖∫ ω in (-π)..π, ((‖1 + z ω‖ ^ 2)⁻¹ - 1 - Real.log ((‖1 + z ω‖ ^ 2)⁻¹))‖ := by
        gcongr; exact le_abs_self _
    _ ≤ 1 / (4 * π) * (2 * (4 * ρ) ^ 2 * (2 * π)) := by gcongr
    _ = 16 * ρ ^ 2 := by field_simp; ring

end CurrentMM
