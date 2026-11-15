import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum

namespace CurrentMM

noncomputable section

def singlePriceTap1 (a impact q rate : ℝ) : ℝ := impact * (a + impact * q * rate)
def singlePriceTap2 (a impact q rate : ℝ) : ℝ :=
  (a + impact * q * rate) * singlePriceTap1 a impact q rate +
    impact ^ 2 * q * rate * (1 - rate)

def splitPriceTap1 (a impact q rate delta : ℝ) : ℝ :=
  impact * (a + impact * (q / 2 * (rate - delta) + q / 2 * (rate + delta)))

def splitPriceTap2 (a impact q rate delta : ℝ) : ℝ :=
  (a + impact * (q / 2 * (rate - delta) + q / 2 * (rate + delta))) *
    splitPriceTap1 a impact q rate delta +
    impact ^ 2 * (q / 2 * (rate - delta) * (1 - (rate - delta)) +
      q / 2 * (rate + delta) * (1 - (rate + delta)))

theorem symmetric_first_tap_identical (a impact q rate delta : ℝ) :
    splitPriceTap1 a impact q rate delta = singlePriceTap1 a impact q rate := by
  unfold splitPriceTap1 singlePriceTap1
  ring

theorem symmetric_third_tap_difference (a impact q rate delta : ℝ) :
    splitPriceTap2 a impact q rate delta - singlePriceTap2 a impact q rate =
      -impact ^ 2 * q * delta ^ 2 := by
  unfold splitPriceTap2 singlePriceTap2 splitPriceTap1 singlePriceTap1
  ring

theorem symmetric_third_tap_separates (a impact q rate delta : ℝ)
    (hk : 0 < impact) (hq : 0 < q) (hd : delta ≠ 0) :
    splitPriceTap2 a impact q rate delta ≠ singlePriceTap2 a impact q rate := by
  have h := symmetric_third_tap_difference a impact q rate delta
  have hp : 0 < impact ^ 2 * q * delta ^ 2 := by positivity
  intro heq
  rw [heq] at h
  linarith

def singleTransfer (q rate z : ℝ) : ℝ := q * rate * z / (z - 1 + rate)
def splitTransfer (q rate delta z : ℝ) : ℝ :=
  q / 2 * ((rate - delta) * z / (z - 1 + rate - delta) +
    (rate + delta) * z / (z - 1 + rate + delta))

theorem split_transfer_difference (q rate delta z : ℝ)
    (h0 : z - 1 + rate ≠ 0)
    (hm : z - 1 + rate - delta ≠ 0)
    (hp : z - 1 + rate + delta ≠ 0) :
    splitTransfer q rate delta z - singleTransfer q rate z =
      -q * z * (z - 1) * delta ^ 2 /
        ((z - 1 + rate) * ((z - 1 + rate) ^ 2 - delta ^ 2)) := by
  have hd : (z - 1 + rate) ^ 2 - delta ^ 2 ≠ 0 := by
    have heq : (z - 1 + rate) ^ 2 - delta ^ 2 =
        (z - 1 + rate - delta) * (z - 1 + rate + delta) := by ring
    rw [heq]
    exact mul_ne_zero hm hp
  unfold splitTransfer singleTransfer
  field_simp <;> ring

def closedPriceTransfer (a impact G z : ℝ) : ℝ := impact / (z - a - impact * G)

theorem closed_price_transfer_difference (a impact G0 G1 z : ℝ)
    (h0 : z - a - impact * G0 ≠ 0) (h1 : z - a - impact * G1 ≠ 0) :
    closedPriceTransfer a impact G1 z - closedPriceTransfer a impact G0 z =
      closedPriceTransfer a impact G1 z * closedPriceTransfer a impact G0 z *
        (G1 - G0) := by
  unfold closedPriceTransfer
  field_simp <;> ring

theorem ogd_rate_normalization (theta x gamma alpha curvature : ℝ) :
    theta - alpha * curvature * (theta - x) - gamma * theta =
      (1 - (gamma + alpha * curvature)) * theta + alpha * curvature * x := by ring

theorem ogd_normalized_recursion (theta x gamma alpha curvature : ℝ)
    (h : gamma + alpha * curvature ≠ 0) :
    theta - alpha * curvature * (theta - x) - gamma * theta =
      (1 - (gamma + alpha * curvature)) * theta +
        (gamma + alpha * curvature) *
          (alpha * curvature / (gamma + alpha * curvature)) * x := by
  field_simp <;> ring

end
end CurrentMM
