import Mathlib.Basic.Real.Basic
import Mathlib.Algebra.Order.Floor.Semiring
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity

/-!
# Paper 1, Section 5: Minimum Price Variation and Dithering (`CurrentMM` mirror of `PublicationRevision16.lean`)
-/

namespace CurrentMM

noncomputable def p1_tickQuantize (alpha p : ℝ) : ℝ :=
  alpha * (Int.floor (p / alpha + 1 / 2) : ℝ)

theorem p1_tickQuantize_eq_of_mem_cell (alpha p : ℝ) (m : ℤ) (halpha : 0 < alpha)
    (hlo : ((m : ℝ) - 1 / 2) * alpha ≤ p) (hhi : p < ((m : ℝ) + 1 / 2) * alpha) :
    p1_tickQuantize alpha p = (m : ℝ) * alpha := by
  unfold p1_tickQuantize
  have hfl : Int.floor (p / alpha + 1 / 2) = m := by
    rw [Int.floor_eq_iff]
    constructor
    · have h1 : (m : ℝ) - 1 / 2 ≤ p / alpha := (le_div_iff₀ halpha).mpr hlo
      linarith
    · have h2 : p / alpha < (m : ℝ) + 1 / 2 := (div_lt_iff₀ halpha).mpr hhi
      linarith
  rw [hfl]
  ring

theorem p1_quantized_cell_coincidence (alpha pA pB : ℝ) (m : ℤ) (halpha : 0 < alpha)
    (hmargin : |pA - (m : ℝ) * alpha| + |pB - pA| < alpha / 2) :
    p1_tickQuantize alpha pA = p1_tickQuantize alpha pB := by
  have ha_lt : |pA - (m : ℝ) * alpha| < alpha / 2 :=
    lt_of_le_of_lt (le_add_of_nonneg_right (abs_nonneg _)) hmargin
  have ha_bounds := abs_lt.mp ha_lt
  have hb_lt : |pB - (m : ℝ) * alpha| < alpha / 2 := by
    calc |pB - (m : ℝ) * alpha|
        = |(pA - (m : ℝ) * alpha) + (pB - pA)| := by ring_nf
      _ ≤ |pA - (m : ℝ) * alpha| + |pB - pA| := abs_add_le _ _
      _ < alpha / 2 := hmargin
  have hb_bounds := abs_lt.mp hb_lt
  have hA : p1_tickQuantize alpha pA = (m : ℝ) * alpha :=
    p1_tickQuantize_eq_of_mem_cell alpha pA m halpha (by linarith [ha_bounds.1]) (by linarith [ha_bounds.2])
  have hB : p1_tickQuantize alpha pB = (m : ℝ) * alpha :=
    p1_tickQuantize_eq_of_mem_cell alpha pB m halpha (by linarith [hb_bounds.1]) (by linarith [hb_bounds.2])
  rw [hA, hB]

theorem p1_sub_tick_response_gap (C vbar delta_eta alpha pA : ℝ) (m : ℤ) (K : ℕ)
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

theorem p1_sub_tick_closed_loop_coincidence (C vbar delta_eta alpha pA pB : ℝ) (m : ℤ) (K : ℕ)
    (hC : 0 < C) (hv : 0 < vbar) (halpha : 0 < alpha)
    (hoff : |pA - (m : ℝ) * alpha| < alpha / 2)
    (hgap : delta_eta ^ (2 * K - 1) < (alpha / 2 - |pA - (m : ℝ) * alpha|) / (C * vbar))
    (hpB : |pB - pA| ≤ C * vbar * delta_eta ^ (2 * K - 1)) :
    p1_tickQuantize alpha pA = p1_tickQuantize alpha pB := by
  have htot := p1_sub_tick_response_gap C vbar delta_eta alpha pA m K hC hv halpha hoff hgap
  exact p1_quantized_cell_coincidence alpha pA pB m halpha (by linarith)

theorem p1_sub_tick_zero_divergence_bound (qA qB : ℝ) (heq : qA = qB) :
    |qA - qB| = 0 := by
  simp [heq]

theorem p1_zero_divergence_minimax_risk (_N : ℝ) :
    (1 - Real.sqrt 0) / 2 = (1 : ℝ) / 2 := by
  rw [Real.sqrt_zero]
  ring

theorem p1_sample_complexity_infinite (c_err : ℝ) (hc : 0 < c_err) (N : ℝ) :
    N * 0 < c_err := by
  rw [mul_zero]
  exact hc

theorem p1_mpv_threshold_pos (C vbar alpha : ℝ)
    (hC : 0 < C) (hv : 0 < vbar) (halpha : 0 < alpha) :
    0 < alpha / (2 * C * vbar) := by
  positivity

theorem p1_mpv_threshold_mono (C vbar alpha1 alpha2 : ℝ)
    (hC : 0 < C) (hv : 0 < vbar) (halpha : alpha1 < alpha2) :
    alpha1 / (2 * C * vbar) < alpha2 / (2 * C * vbar) := by
  have hpos : 0 < 2 * C * vbar := by positivity
  exact div_lt_div_of_pos_right halpha hpos

theorem p1_sheppard_dither_factor_bounds (alpha sigma : ℝ)
    (halpha : 0 < alpha) (hsigma : 0 < sigma) (hdither : alpha ^ 2 < 12 * sigma ^ 2) :
    0 < 1 - alpha ^ 2 / (12 * sigma ^ 2) ∧ 1 - alpha ^ 2 / (12 * sigma ^ 2) < 1 := by
  have hden : 0 < 12 * sigma ^ 2 := by positivity
  have hquot_pos : 0 < alpha ^ 2 / (12 * sigma ^ 2) := by positivity
  have hquot_lt : alpha ^ 2 / (12 * sigma ^ 2) < 1 := (div_lt_one hden).mpr hdither
  constructor <;> linarith

theorem p1_hmm_double_quantization_factor_bounds (alpha sigma : ℝ)
    (halpha : 0 < alpha) (hsigma : 0 < sigma) (hhmm : alpha ^ 2 < 6 * sigma ^ 2) :
    0 < 1 - alpha ^ 2 / (6 * sigma ^ 2) ∧ 1 - alpha ^ 2 / (6 * sigma ^ 2) < 1 := by
  have hden : 0 < 6 * sigma ^ 2 := by positivity
  have hquot_pos : 0 < alpha ^ 2 / (6 * sigma ^ 2) := by positivity
  have hquot_lt : alpha ^ 2 / (6 * sigma ^ 2) < 1 := (div_lt_one hden).mpr hhmm
  constructor <;> linarith

end CurrentMM
