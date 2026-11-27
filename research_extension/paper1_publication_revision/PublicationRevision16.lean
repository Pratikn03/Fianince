import Mathlib.Basic.Real.Basic
import Mathlib.Algebra.Order.Floor.Semiring
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity

/-!
# Paper 1, Section 5 & Supplement Section S24.3: Minimum Price Variation (MPV) and Dithering

This file mechanizes the deterministic analytical steps of Theorem 5.2 (`thm:mpv`):

1. `tickQuantize_eq_of_mem_cell`: for `p ∈ [(m - 1/2) * α, (m + 1/2) * α)`, nearest-tick floor
   quantization `α * ⌊p / α + 1/2⌋` evaluates to `m * α`.
2. `quantized_cell_coincidence`: when `|pA - m * α| + |pB - pA| < α / 2` with `α > 0`, both
   `pA` and `pB` fall strictly inside tick cell `m` and satisfy `tickQuantize α pA = tickQuantize α pB`.
3. `sub_tick_response_gap` & `sub_tick_closed_loop_coincidence`: with baseline cell-center offset
   `|pA - m α| < α / 2`, when `(Δη)^(2K - 1) < (α/2 - |pA - m α|) / (C v̄)`, the offset plus
   perturbation stays strictly under `α / 2` and forces `tickQuantize α pA = tickQuantize α pB`.
4. `sub_tick_zero_divergence_bound`: if quantized cell probabilities coincide (`qA = qB`),
   pointwise absolute cell discrepancy `|qA - qB|` vanishes identically.
5. `zero_divergence_minimax_risk` & `sample_complexity_infinite`: at `J = 0`, testing risk
   equals `1 / 2` and `N * 0 < c_err` for all `N`.
6. `mpv_threshold_pos`, `mpv_threshold_mono`, `sheppard_dither_factor_bounds`, and
   `hmm_double_quantization_factor_bounds`: positivity and monotonicity of the sub-cell budget ratio,
   plus `(0, 1)` bounds for the high-resolution Sheppard asymptotic factor `1 - α² / (12 σ²)`
   (`α² < 12 σ²`) and passive AR(1) HMM two-step double-loss factor `1 - α² / (6 σ²)` (`α² < 6 σ²`).

Standard axioms only (propext, Classical.choice, Quot.sound).
-/

namespace Paper1Revision16

/-- Nearest-tick grid rounding operator `Q_α(p) = α * ⌊p / α + 1/2⌋`. -/
noncomputable def tickQuantize (alpha p : ℝ) : ℝ :=
  alpha * (Int.floor (p / alpha + 1 / 2) : ℝ)

/-- 1. Membership in the half-open tick cell `[(m - 1/2)α, (m + 1/2)α)` pins down `tickQuantize`. -/
theorem tickQuantize_eq_of_mem_cell (alpha p : ℝ) (m : ℤ) (halpha : 0 < alpha)
    (hlo : ((m : ℝ) - 1 / 2) * alpha ≤ p) (hhi : p < ((m : ℝ) + 1 / 2) * alpha) :
    tickQuantize alpha p = (m : ℝ) * alpha := by
  unfold tickQuantize
  have hfl : Int.floor (p / alpha + 1 / 2) = m := by
    rw [Int.floor_eq_iff]
    constructor
    · have h1 : (m : ℝ) - 1 / 2 ≤ p / alpha := (le_div_iff₀ halpha).mpr hlo
      linarith
    · have h2 : p / alpha < (m : ℝ) + 1 / 2 := (div_lt_iff₀ halpha).mpr hhi
      linarith
  rw [hfl]
  ring

/-- 2. Interior sub-cell coincidence: if `|pA - m α| + |pB - pA| < α / 2`, quantized prices coincide. -/
theorem quantized_cell_coincidence (alpha pA pB : ℝ) (m : ℤ) (halpha : 0 < alpha)
    (hmargin : |pA - (m : ℝ) * alpha| + |pB - pA| < alpha / 2) :
    tickQuantize alpha pA = tickQuantize alpha pB := by
  have ha_abs := abs_le.mp (le_of_lt (lt_of_le_of_lt (le_add_of_nonneg_right (abs_nonneg _)) hmargin))
  have ha_lt : |pA - (m : ℝ) * alpha| < alpha / 2 :=
    lt_of_le_of_lt (le_add_of_nonneg_right (abs_nonneg _)) hmargin
  have ha_bounds := abs_lt.mp ha_lt
  have hb_lt : |pB - (m : ℝ) * alpha| < alpha / 2 := by
    calc |pB - (m : ℝ) * alpha|
        = |(pA - (m : ℝ) * alpha) + (pB - pA)| := by ring_nf
      _ ≤ |pA - (m : ℝ) * alpha| + |pB - pA| := abs_add_le _ _
      _ < alpha / 2 := hmargin
  have hb_bounds := abs_lt.mp hb_lt
  have hA : tickQuantize alpha pA = (m : ℝ) * alpha := by
    apply tickQuantize_eq_of_mem_cell alpha pA m halpha
    · linarith [ha_bounds.1]
    · linarith [ha_bounds.2]
  have hB : tickQuantize alpha pB = (m : ℝ) * alpha := by
    apply tickQuantize_eq_of_mem_cell alpha pB m halpha
    · linarith [hb_bounds.1]
    · linarith [hb_bounds.2]
  rw [hA, hB]

/-- 3. Sub-tick `(2K - 1)`-exponent response gap bound including baseline cell-center offset `|pA - m α|`. -/
theorem sub_tick_response_gap (C vbar delta_eta alpha pA : ℝ) (m : ℤ) (K : ℕ)
    (hC : 0 < C) (hv : 0 < vbar) (_halpha : 0 < alpha)
    (_hoff : |pA - (m : ℝ) * alpha| < alpha / 2)
    (hgap : delta_eta ^ (2 * K - 1) < (alpha / 2 - |pA - (m : ℝ) * alpha|) / (C * vbar)) :
    |pA - (m : ℝ) * alpha| + C * vbar * delta_eta ^ (2 * K - 1) < alpha / 2 := by
  have hpos : 0 < C * vbar := by positivity
  have hne : C * vbar ≠ 0 := ne_of_gt hpos
  have h1 : C * vbar * delta_eta ^ (2 * K - 1) <
      C * vbar * ((alpha / 2 - |pA - (m : ℝ) * alpha|) / (C * vbar)) :=
    mul_lt_mul_of_pos_left hgap hpos
  have h2 : C * vbar * ((alpha / 2 - |pA - (m : ℝ) * alpha|) / (C * vbar)) =
      alpha / 2 - |pA - (m : ℝ) * alpha| := by
    field_simp [hne]
  linarith [h1, h2]

/-- 3b. Combined sub-cell coincidence: baseline offset + `(2K - 1)` gap preserves quantized price. -/
theorem sub_tick_closed_loop_coincidence (C vbar delta_eta alpha pA pB : ℝ) (m : ℤ) (K : ℕ)
    (hC : 0 < C) (hv : 0 < vbar) (halpha : 0 < alpha)
    (hoff : |pA - (m : ℝ) * alpha| < alpha / 2)
    (hgap : delta_eta ^ (2 * K - 1) < (alpha / 2 - |pA - (m : ℝ) * alpha|) / (C * vbar))
    (hpB : |pB - pA| ≤ C * vbar * delta_eta ^ (2 * K - 1)) :
    tickQuantize alpha pA = tickQuantize alpha pB := by
  have htot := sub_tick_response_gap C vbar delta_eta alpha pA m K hC hv halpha hoff hgap
  exact quantized_cell_coincidence alpha pA pB m halpha (by linarith)

/-- 4. Arithmetic only: equal cell probabilities contribute zero difference. -/
theorem sub_tick_zero_divergence_bound (qA qB : ℝ) (heq : qA = qB) :
    |qA - qB| = 0 := by
  simp [heq]

/-- 5. Arithmetic only: `(1 - √0)/2 = 1/2`, the value at `J = 0` of the two-point risk bound `(1 - √(J/2))/2`.
The risk bound itself is proved on paper. -/
theorem zero_divergence_minimax_risk (_N : ℝ) :
    (1 - Real.sqrt 0) / 2 = (1 : ℝ) / 2 := by
  rw [Real.sqrt_zero]
  ring

/-- 6. Arithmetic only: with zero divergence per sample, `N` samples carry total divergence `N * 0`, below any
positive threshold. The step to unbounded sample complexity is proved on paper. -/
theorem sample_complexity_infinite (c_err : ℝ) (hc : 0 < c_err) (N : ℝ) :
    N * 0 < c_err := by
  rw [mul_zero]
  exact hc

/-- 7. Positivity of the critical power-law spacing ratio `α / (2 C v̄)`. -/
theorem mpv_threshold_pos (C vbar alpha : ℝ)
    (hC : 0 < C) (hv : 0 < vbar) (halpha : 0 < alpha) :
    0 < alpha / (2 * C * vbar) := by
  positivity

/-- 8. Strict monotonicity of the sub-cell spacing budget with respect to tick size `α`. -/
theorem mpv_threshold_mono (C vbar alpha1 alpha2 : ℝ)
    (hC : 0 < C) (hv : 0 < vbar) (halpha : alpha1 < alpha2) :
    alpha1 / (2 * C * vbar) < alpha2 / (2 * C * vbar) := by
  have hpos : 0 < 2 * C * vbar := by positivity
  exact div_lt_div_of_pos_right halpha hpos

/-- 9. High-resolution small-tick Sheppard asymptotic Fisher factor lies strictly in `(0, 1)` when `α² < 12 σ²`
(exact Gaussian quantized Fisher information `I_Q > 0` holds for every `α > 0`). -/
theorem sheppard_dither_factor_bounds (alpha sigma : ℝ)
    (halpha : 0 < alpha) (hsigma : 0 < sigma) (hdither : alpha ^ 2 < 12 * sigma ^ 2) :
    0 < 1 - alpha ^ 2 / (12 * sigma ^ 2) ∧ 1 - alpha ^ 2 / (12 * sigma ^ 2) < 1 := by
  have hden : 0 < 12 * sigma ^ 2 := by positivity
  have hquot_pos : 0 < alpha ^ 2 / (12 * sigma ^ 2) := by positivity
  have hquot_lt : alpha ^ 2 / (12 * sigma ^ 2) < 1 := (div_lt_one hden).mpr hdither
  constructor <;> linarith

/-- 10. Passive stationary AR(1) HMM double-quantization first-order Whittle factor for `a`:
`1 - (1 - a²) α² / (6 σ²)` lies strictly in `(0, 1)` whenever `a² < 1` and `(1 - a²) α² < 6 σ²`. -/
theorem hmm_double_quantization_factor_bounds (alpha sigma a : ℝ)
    (halpha : 0 < alpha) (hsigma : 0 < sigma) (ha : a ^ 2 < 1)
    (hhmm : (1 - a ^ 2) * alpha ^ 2 < 6 * sigma ^ 2) :
    0 < 1 - (1 - a ^ 2) * alpha ^ 2 / (6 * sigma ^ 2) ∧
    1 - (1 - a ^ 2) * alpha ^ 2 / (6 * sigma ^ 2) < 1 := by
  have hden : 0 < 6 * sigma ^ 2 := by positivity
  have h1ma : 0 < 1 - a ^ 2 := by linarith
  have hquot_pos : 0 < (1 - a ^ 2) * alpha ^ 2 / (6 * sigma ^ 2) := by positivity
  have hquot_lt : (1 - a ^ 2) * alpha ^ 2 / (6 * sigma ^ 2) < 1 := (div_lt_one hden).mpr hhmm
  constructor <;> linarith

end Paper1Revision16
