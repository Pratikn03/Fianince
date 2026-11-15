import Mathlib.Basic.Real.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Positivity

namespace CurrentMM

noncomputable section

/-! Real-valued cash/inventory identities for the current execution contracts.
These declarations do not assume the accounting conclusions they establish.
The statistical and positive-kernel obligations are tracked separately. -/

def dealerCash (cash quantity price spread fees funding : ℝ) : ℝ :=
  cash + quantity * price + spread * |quantity| - fees - funding

def dealerInventory (inventory quantity : ℝ) : ℝ := inventory - quantity

def equity (cash inventory price : ℝ) : ℝ := cash + inventory * price

theorem dealer_marked_equity_identity
    (cash inventory quantity price nextPrice spread fees funding : ℝ) :
    equity (dealerCash cash quantity price spread fees funding)
      (dealerInventory inventory quantity) nextPrice - equity cash inventory price =
      spread * |quantity| + (inventory - quantity) * (nextPrice - price) - fees - funding := by
  unfold equity dealerCash dealerInventory
  ring

def averageFill (baseline impact quantity : ℝ) : ℝ := baseline + impact * quantity / 2
def postMark (baseline impact quantity : ℝ) : ℝ := baseline + impact * quantity

theorem counterparty_first_pulse_equity (B P impact quantity cost : ℝ) :
    equity (B + quantity * averageFill P impact quantity - cost * quantity)
      (-quantity) (postMark P impact quantity) =
      B - impact * quantity ^ 2 / 2 - cost * quantity := by
  unfold equity averageFill postMark
  ring

theorem counterparty_first_pulse_margin_iff (B P impact quantity cost margin : ℝ)
    (hq : 0 ≤ quantity) :
    margin * |quantity| * (postMark P impact quantity) ≤
      equity (B + quantity * averageFill P impact quantity - cost * quantity)
        (-quantity) (postMark P impact quantity) ↔
      (margin + 1 / 2) * impact * quantity ^ 2 + (cost + margin * P) * quantity ≤ B := by
  rw [counterparty_first_pulse_equity, abs_of_nonneg hq]
  unfold postMark
  constructor <;> intro h <;> nlinarith

theorem trader_first_pulse_equity (B P impact quantity cost : ℝ) :
    equity (B - quantity * averageFill P impact quantity - cost * quantity)
      quantity (postMark P impact quantity) =
      B + impact * quantity ^ 2 / 2 - cost * quantity := by
  unfold equity averageFill postMark
  ring

theorem trader_fundamental_mark_equity (B P impact quantity cost : ℝ) :
    equity (B - quantity * averageFill P impact quantity - cost * quantity)
      quantity P = B - impact * quantity ^ 2 / 2 - cost * quantity := by
  unfold equity averageFill
  ring

theorem two_account_equity_conservation
    (Btrader Bdealer inventory quantity fill mark traderCost dealerCost : ℝ) :
    equity (Btrader - quantity * fill - traderCost) (inventory + quantity) mark +
      equity (Bdealer + quantity * fill - dealerCost) (-inventory - quantity) mark =
      Btrader + Bdealer - traderCost - dealerCost := by
  unfold equity
  ring

def pulseTraderCapital (impact cost margin P quantity : ℝ) : ℝ :=
  impact * quantity ^ 2 / 2 + (cost + margin * P) * quantity

theorem funded_trader_pulse_equity (impact cost margin P quantity h : ℝ) :
    equity (pulseTraderCapital impact cost margin P quantity -
      quantity * averageFill P impact quantity - cost * quantity)
      quantity (P + quantity * h) = margin * quantity * P + quantity ^ 2 * h := by
  unfold equity pulseTraderCapital averageFill
  ring

theorem funded_trader_pulse_margin (impact cost margin P quantity h : ℝ)
    (hq : 0 ≤ quantity) (hh : 0 ≤ h) (hmargin : margin ≤ 1) :
    margin * |quantity| * (P + quantity * h) ≤
      equity (pulseTraderCapital impact cost margin P quantity -
        quantity * averageFill P impact quantity - cost * quantity)
        quantity (P + quantity * h) := by
  rw [funded_trader_pulse_equity, abs_of_nonneg hq]
  have hnonneg : 0 ≤ (1 - margin) * quantity ^ 2 * h := by positivity
  nlinarith

def robustQuantityCap (alpha beta B : ℝ) : ℝ :=
  2 * B / (beta + Real.sqrt (beta ^ 2 + 4 * alpha * B))

theorem robust_quantity_cap_pos (alpha beta B : ℝ)
    (ha : 0 < alpha) (hb : 0 < beta) (hB : 0 < B) :
    0 < robustQuantityCap alpha beta B := by
  unfold robustQuantityCap
  positivity

theorem robust_quantity_cap_quadratic (alpha beta B : ℝ)
    (ha : 0 < alpha) (hb : 0 < beta) (hB : 0 < B) :
    alpha * (robustQuantityCap alpha beta B) ^ 2 +
      beta * robustQuantityCap alpha beta B = B := by
  have hd : 0 ≤ beta ^ 2 + 4 * alpha * B := by positivity
  have hs := Real.sq_sqrt hd
  have hden : beta + Real.sqrt (beta ^ 2 + 4 * alpha * B) ≠ 0 := by positivity
  unfold robustQuantityCap
  generalize hr : Real.sqrt (beta ^ 2 + 4 * alpha * B) = r at *
  field_simp
  nlinarith

theorem robust_quantity_cap_iff (alpha beta B V : ℝ)
    (ha : 0 < alpha) (hb : 0 < beta) (hB : 0 < B) (hV : 0 ≤ V) :
    alpha * V ^ 2 + beta * V ≤ B ↔ V ≤ robustQuantityCap alpha beta B := by
  have hc := robust_quantity_cap_quadratic alpha beta B ha hb hB
  have hcp := robust_quantity_cap_pos alpha beta B ha hb hB
  constructor
  · intro h
    by_contra hnot
    have hlt : robustQuantityCap alpha beta B < V := lt_of_not_ge hnot
    have hprod : 0 < (V - robustQuantityCap alpha beta B) *
        (alpha * (V + robustQuantityCap alpha beta B) + beta) := by positivity
    nlinarith
  · intro h
    have hprod : 0 ≤ (robustQuantityCap alpha beta B - V) *
        (alpha * (V + robustQuantityCap alpha beta B) + beta) := by positivity
    nlinarith

theorem exact_equity_disclosure_separation (B impact quantity cost h0 h1 q delta : ℝ)
    (htap : h1 - h0 = -impact ^ 2 * q * delta ^ 2) :
    (B + impact * quantity ^ 2 / 2 - cost * quantity - quantity ^ 2 * h1) -
      (B + impact * quantity ^ 2 / 2 - cost * quantity - quantity ^ 2 * h0) =
      quantity ^ 2 * impact ^ 2 * q * delta ^ 2 := by
  nlinarith [htap]

end
end CurrentMM
