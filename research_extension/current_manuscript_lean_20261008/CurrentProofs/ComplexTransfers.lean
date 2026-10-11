import CurrentProofs.CohortAlgebra
import Mathlib.Analysis.Complex.Basic

namespace CurrentMM
noncomputable section

def complexSingleTransfer (q rate : ℂ) (z : ℂ) : ℂ := q * rate * z / (z - 1 + rate)
def complexSplitTransfer (q rate delta z : ℂ) : ℂ :=
  q / 2 * ((rate - delta) * z / (z - 1 + rate - delta) +
    (rate + delta) * z / (z - 1 + rate + delta))

theorem complex_split_transfer_difference (q rate delta z : ℂ)
    (h0 : z - 1 + rate ≠ 0) (hm : z - 1 + rate - delta ≠ 0)
    (hp : z - 1 + rate + delta ≠ 0) :
    complexSplitTransfer q rate delta z - complexSingleTransfer q rate z =
      -q * z * (z - 1) * delta ^ 2 /
        ((z - 1 + rate) * ((z - 1 + rate) ^ 2 - delta ^ 2)) := by
  have hd : (z - 1 + rate) ^ 2 - delta ^ 2 ≠ 0 := by
    have heq : (z - 1 + rate) ^ 2 - delta ^ 2 =
        (z - 1 + rate - delta) * (z - 1 + rate + delta) := by ring
    rw [heq]
    exact mul_ne_zero hm hp
  unfold complexSplitTransfer complexSingleTransfer
  field_simp <;> ring

def complexPriceTransfer (a impact G z : ℂ) : ℂ := impact / (z - a - impact * G)

theorem complex_price_transfer_difference (a impact G0 G1 z : ℂ)
    (h0 : z - a - impact * G0 ≠ 0) (h1 : z - a - impact * G1 ≠ 0) :
    complexPriceTransfer a impact G1 z - complexPriceTransfer a impact G0 z =
      complexPriceTransfer a impact G1 z * complexPriceTransfer a impact G0 z * (G1 - G0) := by
  unfold complexPriceTransfer
  field_simp <;> ring

theorem unit_circle_rate_denominator_lower (z : ℂ) (rate : ℝ)
    (hz : ‖z‖ = 1) (hrate : rate ≤ 1) :
    rate ≤ ‖z - 1 + (rate : ℂ)‖ := by
  have hcast : ((1 - rate : ℝ) : ℂ) = 1 - (rate : ℂ) := by push_cast; rfl
  calc
    rate = ‖z‖ - ‖((1 - rate : ℝ) : ℂ)‖ := by
      rw [hz, Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg (by linarith)]
      ring
    _ ≤ ‖z - ((1 - rate : ℝ) : ℂ)‖ := norm_sub_norm_le _ _
    _ = ‖z - 1 + (rate : ℂ)‖ := by rw [hcast]; congr 1; ring

theorem unit_circle_single_transfer_bound (z : ℂ) (q rate : ℝ)
    (hz : ‖z‖ = 1) (hq : 0 ≤ q) (hrpos : 0 < rate) (hrate : rate ≤ 1) :
    ‖complexSingleTransfer (q : ℂ) (rate : ℂ) z‖ ≤ q := by
  have hd := unit_circle_rate_denominator_lower z rate hz hrate
  have hdp : 0 < ‖z - 1 + (rate : ℂ)‖ := lt_of_lt_of_le hrpos hd
  unfold complexSingleTransfer
  rw [norm_div, norm_mul, norm_mul, Complex.norm_real, Complex.norm_real,
    Real.norm_eq_abs, Real.norm_eq_abs, abs_of_nonneg hq, abs_of_pos hrpos, hz, mul_one]
  apply (div_le_iff₀ hdp).2
  exact mul_le_mul_of_nonneg_left hd hq

theorem split_transfer_as_sum (q rate delta : ℝ) (z : ℂ) :
    complexSplitTransfer (q : ℂ) (rate : ℂ) (delta : ℂ) z =
      complexSingleTransfer ((q / 2 : ℝ) : ℂ) ((rate - delta : ℝ) : ℂ) z +
      complexSingleTransfer ((q / 2 : ℝ) : ℂ) ((rate + delta : ℝ) : ℂ) z := by
  unfold complexSplitTransfer complexSingleTransfer
  push_cast
  ring

theorem unit_circle_split_transfer_bound (z : ℂ) (q rate delta : ℝ)
    (hz : ‖z‖ = 1) (hq : 0 ≤ q)
    (hm : 0 < rate - delta ∧ rate - delta ≤ 1)
    (hp : 0 < rate + delta ∧ rate + delta ≤ 1) :
    ‖complexSplitTransfer (q : ℂ) (rate : ℂ) (delta : ℂ) z‖ ≤ q := by
  rw [split_transfer_as_sum]
  calc
    _ ≤ ‖complexSingleTransfer ((q / 2 : ℝ) : ℂ) ((rate - delta : ℝ) : ℂ) z‖ +
        ‖complexSingleTransfer ((q / 2 : ℝ) : ℂ) ((rate + delta : ℝ) : ℂ) z‖ := norm_add_le _ _
    _ ≤ q / 2 + q / 2 := add_le_add
      (unit_circle_single_transfer_bound z (q / 2) (rate - delta) hz (by positivity) hm.1 hm.2)
      (unit_circle_single_transfer_bound z (q / 2) (rate + delta) hz (by positivity) hp.1 hp.2)
    _ = q := by ring

theorem positive_price_denominator_lower (z G : ℂ) (a impact q : ℝ)
    (hz : ‖z‖ = 1) (ha : 0 ≤ a) (hk : 0 ≤ impact) (hG : ‖G‖ ≤ q) :
    1 - a - impact * q ≤ ‖z - (a : ℂ) - (impact : ℂ) * G‖ := by
  have hfeedback : ‖(a : ℂ) + (impact : ℂ) * G‖ ≤ a + impact * q := by
    calc
      _ ≤ ‖(a : ℂ)‖ + ‖(impact : ℂ) * G‖ := norm_add_le _ _
      _ = a + impact * ‖G‖ := by
        rw [norm_mul, Complex.norm_real, Complex.norm_real,
          Real.norm_eq_abs, Real.norm_eq_abs, abs_of_nonneg ha, abs_of_nonneg hk]
      _ ≤ a + impact * q := add_le_add (le_refl a) (mul_le_mul_of_nonneg_left hG hk)
  have hreverse := norm_sub_norm_le z ((a : ℂ) + (impact : ℂ) * G)
  have halgebra : z - ((a : ℂ) + (impact : ℂ) * G) =
      z - (a : ℂ) - (impact : ℂ) * G := by ring
  rw [hz, halgebra] at hreverse
  linarith

theorem positive_price_transfer_uniform_bound (z G : ℂ) (a impact q : ℝ)
    (hz : ‖z‖ = 1) (ha : 0 ≤ a) (hk : 0 ≤ impact) (hG : ‖G‖ ≤ q)
    (hstable : a + impact * q < 1) :
    ‖complexPriceTransfer (a : ℂ) (impact : ℂ) G z‖ ≤ impact / (1 - a - impact * q) := by
  have hden := positive_price_denominator_lower z G a impact q hz ha hk hG
  have hdpos : 0 < 1 - a - impact * q := by linarith
  unfold complexPriceTransfer
  rw [norm_div, Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg hk]
  exact div_le_div_of_nonneg_left hk hdpos hden

theorem unit_circle_symmetric_transfer_difference_bound (z : ℂ) (q rate delta eps : ℝ)
    (hz : ‖z‖ = 1) (hq : 0 ≤ q) (heps : 0 < eps)
    (h0 : eps ≤ rate ∧ rate ≤ 1)
    (hm : eps ≤ rate - delta ∧ rate - delta ≤ 1)
    (hp : eps ≤ rate + delta ∧ rate + delta ≤ 1) :
    ‖complexSplitTransfer (q : ℂ) (rate : ℂ) (delta : ℂ) z -
      complexSingleTransfer (q : ℂ) (rate : ℂ) z‖ ≤ 2 * q * delta ^ 2 / eps ^ 3 := by
  have hden0 : eps ≤ ‖z - 1 + (rate : ℂ)‖ :=
    le_trans h0.1 (unit_circle_rate_denominator_lower z rate hz h0.2)
  have hcastm : z - 1 + ((rate - delta : ℝ) : ℂ) =
      z - 1 + (rate : ℂ) - (delta : ℂ) := by push_cast; ring
  have hcastp : z - 1 + ((rate + delta : ℝ) : ℂ) =
      z - 1 + (rate : ℂ) + (delta : ℂ) := by push_cast; ring
  have hdenm : eps ≤ ‖z - 1 + (rate : ℂ) - (delta : ℂ)‖ := by
    rw [← hcastm]
    exact le_trans hm.1 (unit_circle_rate_denominator_lower z (rate - delta) hz hm.2)
  have hdenp : eps ≤ ‖z - 1 + (rate : ℂ) + (delta : ℂ)‖ := by
    rw [← hcastp]
    exact le_trans hp.1 (unit_circle_rate_denominator_lower z (rate + delta) hz hp.2)
  have hn0 : z - 1 + (rate : ℂ) ≠ 0 := norm_pos_iff.mp (lt_of_lt_of_le heps hden0)
  have hnm : z - 1 + (rate : ℂ) - (delta : ℂ) ≠ 0 :=
    norm_pos_iff.mp (lt_of_lt_of_le heps hdenm)
  have hnp : z - 1 + (rate : ℂ) + (delta : ℂ) ≠ 0 :=
    norm_pos_iff.mp (lt_of_lt_of_le heps hdenp)
  have hfactor : (z - 1 + (rate : ℂ)) *
      ((z - 1 + (rate : ℂ)) ^ 2 - (delta : ℂ) ^ 2) =
      (z - 1 + (rate : ℂ)) * (z - 1 + (rate : ℂ) - (delta : ℂ)) *
        (z - 1 + (rate : ℂ) + (delta : ℂ)) := by ring
  have hden : eps ^ 3 ≤ ‖(z - 1 + (rate : ℂ)) *
      ((z - 1 + (rate : ℂ)) ^ 2 - (delta : ℂ) ^ 2)‖ := by
    rw [hfactor, norm_mul, norm_mul]
    calc
      eps ^ 3 = eps * eps * eps := by ring
      _ ≤ ‖z - 1 + (rate : ℂ)‖ * eps * eps :=
        mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_right hden0 heps.le) heps.le
      _ ≤ ‖z - 1 + (rate : ℂ)‖ * ‖z - 1 + (rate : ℂ) - (delta : ℂ)‖ * eps :=
        mul_le_mul_of_nonneg_right
          (mul_le_mul_of_nonneg_left hdenm (norm_nonneg _)) heps.le
      _ ≤ _ := mul_le_mul_of_nonneg_left hdenp (mul_nonneg (norm_nonneg _) (norm_nonneg _))
  have hzsub : ‖z - 1‖ ≤ 2 := by
    have h := norm_sub_le z (1 : ℂ)
    rw [hz, norm_one] at h
    linarith
  have hnum : ‖-(q : ℂ) * z * (z - 1) * (delta : ℂ) ^ 2‖ ≤ 2 * q * delta ^ 2 := by
    simp only [norm_mul, norm_neg, norm_pow, Complex.norm_real, Real.norm_eq_abs,
      abs_of_nonneg hq, hz, mul_one, sq_abs]
    have h := mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left hzsub hq)
      (sq_nonneg delta)
    nlinarith
  rw [complex_split_transfer_difference _ _ _ _ hn0 hnm hnp, norm_div]
  calc
    _ ≤ (2 * q * delta ^ 2) /
        ‖(z - 1 + (rate : ℂ)) * ((z - 1 + (rate : ℂ)) ^ 2 - (delta : ℂ) ^ 2)‖ :=
      div_le_div_of_nonneg_right hnum (norm_nonneg _)
    _ ≤ _ := div_le_div_of_nonneg_left (by positivity) (by positivity) hden

theorem symmetric_price_transfer_difference_uniform_bound
    (z : ℂ) (a impact q rate delta eps : ℝ)
    (hz : ‖z‖ = 1) (ha : 0 ≤ a) (hk : 0 ≤ impact) (hq : 0 ≤ q)
    (hstable : a + impact * q < 1) (heps : 0 < eps)
    (h0 : eps ≤ rate ∧ rate ≤ 1)
    (hm : eps ≤ rate - delta ∧ rate - delta ≤ 1)
    (hp : eps ≤ rate + delta ∧ rate + delta ≤ 1) :
    ‖complexPriceTransfer (a : ℂ) (impact : ℂ)
        (complexSplitTransfer (q : ℂ) (rate : ℂ) (delta : ℂ) z) z -
      complexPriceTransfer (a : ℂ) (impact : ℂ)
        (complexSingleTransfer (q : ℂ) (rate : ℂ) z) z‖ ≤
      (2 * impact ^ 2 * q / (eps ^ 3 * (1 - a - impact * q) ^ 2)) * delta ^ 2 := by
  let G0 := complexSingleTransfer (q : ℂ) (rate : ℂ) z
  let G1 := complexSplitTransfer (q : ℂ) (rate : ℂ) (delta : ℂ) z
  have hG0 : ‖G0‖ ≤ q := unit_circle_single_transfer_bound z q rate hz hq
    (lt_of_lt_of_le heps h0.1) h0.2
  have hG1 : ‖G1‖ ≤ q := unit_circle_split_transfer_bound z q rate delta hz hq
    ⟨lt_of_lt_of_le heps hm.1, hm.2⟩ ⟨lt_of_lt_of_le heps hp.1, hp.2⟩
  have hD : 0 < 1 - a - impact * q := by linarith
  have hn0 : z - (a : ℂ) - (impact : ℂ) * G0 ≠ 0 :=
    norm_pos_iff.mp (lt_of_lt_of_le hD
      (positive_price_denominator_lower z G0 a impact q hz ha hk hG0))
  have hn1 : z - (a : ℂ) - (impact : ℂ) * G1 ≠ 0 :=
    norm_pos_iff.mp (lt_of_lt_of_le hD
      (positive_price_denominator_lower z G1 a impact q hz ha hk hG1))
  have hH0 := positive_price_transfer_uniform_bound z G0 a impact q hz ha hk hG0 hstable
  have hH1 := positive_price_transfer_uniform_bound z G1 a impact q hz ha hk hG1 hstable
  have hGdiff : ‖G1 - G0‖ ≤ 2 * q * delta ^ 2 / eps ^ 3 :=
    unit_circle_symmetric_transfer_difference_bound z q rate delta eps hz hq heps h0 hm hp
  change ‖complexPriceTransfer (a : ℂ) (impact : ℂ) G1 z -
      complexPriceTransfer (a : ℂ) (impact : ℂ) G0 z‖ ≤ _
  rw [complex_price_transfer_difference _ _ _ _ _ hn0 hn1, norm_mul, norm_mul]
  calc
    _ ≤ (impact / (1 - a - impact * q)) * (impact / (1 - a - impact * q)) *
        (2 * q * delta ^ 2 / eps ^ 3) :=
      mul_le_mul (mul_le_mul hH1 hH0 (norm_nonneg _) (by positivity)) hGdiff
        (norm_nonneg _) (by positivity)
    _ = _ := by
      field_simp [ne_of_gt heps, ne_of_gt hD]
      <;> ring

end
end CurrentMM
