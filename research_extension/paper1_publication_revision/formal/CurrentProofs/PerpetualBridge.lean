import CurrentProofs.PhysicalAccounts
import CurrentProofs.ZeroAnchorKernel

namespace CurrentMM
noncomputable section
open scoped BigOperators

def executedNotional {T : ℕ} (P impact : ℝ) (h : ℕ → ℝ) (v : Fin T → ℝ) : ℝ :=
  ∑ i, v i * (P + baselineDisplacement h v i + impact * v i / 2)

def shortPerpetualWallet {T : ℕ} (B P impact flatFee commission funding : ℝ)
    (h : ℕ → ℝ) (v : Fin T → ℝ) : ℝ :=
  B - flatFee * cumulativeQuantity v - commission * executedNotional P impact h v - funding

def shortPerpetualEntry {T : ℕ} (P impact : ℝ) (h : ℕ → ℝ) (v : Fin T → ℝ) : ℝ :=
  executedNotional P impact h v / cumulativeQuantity v

def shortPerpetualEquity {T : ℕ} (B P impact flatFee commission funding : ℝ)
    (h : ℕ → ℝ) (v : Fin T → ℝ) : ℝ :=
  shortPerpetualWallet B P impact flatFee commission funding h v - cumulativeQuantity v *
    (P + sequenceFinalDisplacement h v - shortPerpetualEntry P impact h v)

theorem nonnegative_probe_zero_quantity {T : ℕ} (v : Fin T → ℝ) (hv : ∀ i, 0 ≤ v i)
    (hzero : cumulativeQuantity v = 0) : ∀ i, v i = 0 := by
  exact fun i => (Finset.sum_eq_zero_iff_of_nonneg (fun j _ => hv j)).1 hzero i (Finset.mem_univ _)

theorem actual_short_perpetual_entry_basis {T : ℕ} (P impact : ℝ) (h : ℕ → ℝ)
    (v : Fin T → ℝ) (hv : ∀ i, 0 ≤ v i) :
    cumulativeQuantity v * shortPerpetualEntry P impact h v = executedNotional P impact h v := by
  by_cases hzero : cumulativeQuantity v = 0
  · have hnil := nonnegative_probe_zero_quantity v hv hzero
    simp [shortPerpetualEntry, executedNotional, hnil, cumulativeQuantity]
  · unfold shortPerpetualEntry
    exact mul_div_cancel₀ _ hzero

theorem actual_perpetual_principal_equity_bridge {T : ℕ} (B P impact flatFee commission funding : ℝ)
    (h : ℕ → ℝ) (v : Fin T → ℝ) (hv : ∀ i, 0 ≤ v i) :
    shortPerpetualEquity B P impact flatFee commission funding h v =
      sequenceDealerEquity B P impact flatFee h v - commission * executedNotional P impact h v - funding := by
  have he := actual_short_perpetual_entry_basis P impact h v hv
  unfold shortPerpetualEquity shortPerpetualWallet sequenceDealerEquity equity sequenceDealerCash
  change B - flatFee * cumulativeQuantity v - commission * executedNotional P impact h v - funding -
    cumulativeQuantity v * (P + sequenceFinalDisplacement h v - shortPerpetualEntry P impact h v) =
    B + executedNotional P impact h v - flatFee * cumulativeQuantity v +
      -cumulativeQuantity v * (P + sequenceFinalDisplacement h v) - commission * executedNotional P impact h v - funding
  nlinarith [he]

theorem actual_executed_notional_cost_identity {T : ℕ} (P impact : ℝ) (h : ℕ → ℝ)
    (v : Fin T → ℝ) (h0 : h 0 = impact) :
    executedNotional P impact h v = P * cumulativeQuantity v + quadraticExecutionCost h v := by
  have he := actual_sequence_dealer_equity 0 P impact 0 h v h0
  unfold sequenceDealerEquity equity sequenceDealerCash at he
  simp only [zero_add, zero_mul, sub_zero] at he
  change executedNotional P impact h v + -cumulativeQuantity v * (P + sequenceFinalDisplacement h v) =
    quadraticExecutionCost h v - cumulativeQuantity v * sequenceFinalDisplacement h v at he
  nlinarith

theorem nonnegative_execution_cost_upper_bound {T : ℕ} (impact : ℝ) (h : ℕ → ℝ)
    (v : Fin T → ℝ) (hv : ∀ i, 0 ≤ v i) (hpeak : ∀ j, h j ≤ impact) :
    quadraticExecutionCost h v ≤ impact / 2 * (cumulativeQuantity v) ^ 2 := by
  have hs : (∑ i, ∑ j, v i * v j * h (Nat.dist i.val j.val)) ≤
      ∑ i, ∑ j, v i * v j * impact := by
    apply Finset.sum_le_sum
    intro i hi
    apply Finset.sum_le_sum
    intro j hj
    exact mul_le_mul_of_nonneg_left (hpeak _) (mul_nonneg (hv i) (hv j))
  have hright : (∑ i, ∑ j, v i * v j * impact) = impact * (cumulativeQuantity v) ^ 2 := by
    simp only [cumulativeQuantity, pow_two, Finset.mul_sum, Finset.sum_mul]
    apply Finset.sum_congr rfl
    intro i hi
    apply Finset.sum_congr rfl
    intro j hj
    ring
  rw [hright] at hs
  unfold quadraticExecutionCost
  nlinarith

theorem actual_short_perpetual_margin_with_charges {T : ℕ}
    (B P impact flatFee commission funding margin V reserve : ℝ)
    (h : ℕ → ℝ) (v : Fin T → ℝ) (hv : ∀ i, 0 ≤ v i)
    (hk : 0 ≤ impact) (hP : 0 ≤ P) (hc : 0 ≤ flatFee) (hr : 0 ≤ commission) (hm : 0 ≤ margin)
    (hmono : Antitone h) (h0 : h 0 = impact) (hbudget : cumulativeQuantity v ≤ V)
    (hfund : funding ≤ reserve)
    (hcapital : (margin + 1 / 2 + commission / 2) * impact * V ^ 2 +
      (flatFee + (margin + commission) * P) * V + reserve ≤ B) :
    margin * |-(cumulativeQuantity v)| * (P + sequenceFinalDisplacement h v) ≤
      shortPerpetualEquity B P impact flatFee commission funding h v := by
  have hU : 0 ≤ cumulativeQuantity v := Finset.sum_nonneg fun i _ => hv i
  have hV : 0 ≤ V := le_trans hU hbudget
  have hsq : (cumulativeQuantity v) ^ 2 ≤ V ^ 2 := by nlinarith
  have ha := nonnegative_sequence_adverse_mark_bound h impact v hv hmono h0
  have hx := nonnegative_sequence_displacement_bound h impact v hv hmono h0
  have hN := nonnegative_execution_cost_upper_bound impact h v hv
    (fun j => by simpa [h0] using hmono (Nat.zero_le j))
  have hcost := mul_le_mul_of_nonneg_left hN hr
  have hmargin := mul_le_mul_of_nonneg_left hx (mul_nonneg hm hU)
  have hquad := mul_le_mul_of_nonneg_left hsq
    (show 0 ≤ (margin + 1 / 2 + commission / 2) * impact by positivity)
  have hlinear := mul_le_mul_of_nonneg_left hbudget
    (show 0 ≤ flatFee + (margin + commission) * P by positivity)
  rw [abs_neg, abs_of_nonneg hU, actual_perpetual_principal_equity_bridge _ _ _ _ _ _ _ _ hv,
    actual_sequence_dealer_equity _ _ _ _ _ _ h0, actual_executed_notional_cost_identity _ _ _ _ h0]
  nlinarith

theorem actual_physical_perpetual_fee_reserve_cap {n T : ℕ}
    (a B P impact flatFee commission funding margin V reserve : ℝ)
    (q rate : Fin n → ℝ) (v : Fin T → ℝ)
    (ha : 0 ≤ a) (hk : 0 < impact) (hP : 0 < P) (hc : 0 ≤ flatFee) (hr : 0 ≤ commission)
    (hm : 0 < margin) (hB : 0 < B - reserve) (hV : 0 ≤ V)
    (hq : ∀ i, 0 ≤ q i) (heta : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : a + impact * ∑ i, q i < 1) (hv : ∀ i, 0 ≤ v i)
    (hbudget : cumulativeQuantity v ≤ V) (hfund : funding ≤ reserve)
    (hcap : V ≤ robustQuantityCap ((margin + 1 / 2 + commission / 2) * impact)
      (flatFee + (margin + commission) * P) (B - reserve)) :
    margin * |-(cumulativeQuantity v)| * (P + sequenceFinalDisplacement (actualCohortImpulse a impact q rate) v) ≤
      shortPerpetualEquity B P impact flatFee commission funding (actualCohortImpulse a impact q rate) v := by
  have hb := (robust_quantity_cap_iff ((margin + 1 / 2 + commission / 2) * impact)
    (flatFee + (margin + commission) * P) (B - reserve) V (by positivity) (by positivity) hB hV).2 hcap
  apply actual_short_perpetual_margin_with_charges B P impact flatFee commission funding margin V reserve _ v hv
    (le_of_lt hk) (le_of_lt hP) hc hr (le_of_lt hm)
    (actual_nonnegative_anchor_impulse_antitone a impact q rate ha (le_of_lt hk) hq heta hf)
    (by simp [actualCohortImpulse, cohortInputVector]) hbudget hfund
  linarith

end
end CurrentMM
