import CurrentProofs.Accounts

namespace CurrentMM
noncomputable section

def capacityProfit (edge holding depth : ℝ) : ℝ :=
  edge * depth - holding * depth ^ 2 / 2

def clampedCapacity (lower upper edge holding : ℝ) : ℝ :=
  min upper (max lower (edge / holding))

theorem capacity_interval_infeasible (lower upper budget capitalPerQuantity depth : ℝ)
    (hm : 0 < capitalPerQuantity) (hcut : min upper (budget / capitalPerQuantity) < lower)
    (hlower : lower ≤ depth) (hupper : depth ≤ upper)
    (hbudget : capitalPerQuantity * depth ≤ budget) : False := by
  have hb : depth ≤ budget / capitalPerQuantity := by
    apply (le_div_iff₀ hm).2
    nlinarith
  have hbar : depth ≤ min upper (budget / capitalPerQuantity) := le_min hupper hb
  linarith

theorem clamped_capacity_feasible (lower upper edge holding : ℝ) (hlu : lower ≤ upper) :
    lower ≤ clampedCapacity lower upper edge holding ∧
      clampedCapacity lower upper edge holding ≤ upper := by
  unfold clampedCapacity
  exact ⟨le_min hlu (le_max_left _ _), min_le_left _ _⟩

theorem capacity_quadratic_difference (edge holding optimum depth : ℝ) :
    capacityProfit edge holding optimum - capacityProfit edge holding depth =
      (optimum - depth) * (edge - holding * (optimum + depth) / 2) := by
  unfold capacityProfit
  ring

theorem clamped_capacity_maximizes (lower upper edge holding depth : ℝ)
    (hh : 0 < holding) (hlu : lower ≤ upper)
    (hdepth : lower ≤ depth ∧ depth ≤ upper) :
    capacityProfit edge holding depth ≤
      capacityProfit edge holding (clampedCapacity lower upper edge holding) := by
  have hdiv : holding * (edge / holding) = edge := by
    field_simp
  have hnonneg : 0 ≤ holding := le_of_lt hh
  by_cases hl : edge / holding ≤ lower
  · have hc : clampedCapacity lower upper edge holding = lower := by
      simp [clampedCapacity, max_eq_left hl, min_eq_right hlu]
    rw [hc]
    rw [← sub_nonneg, capacity_quadratic_difference]
    have hleft : lower - depth ≤ 0 := by linarith [hdepth.1]
    have hedge : edge ≤ holding * lower := by
      nlinarith [mul_nonneg hnonneg (sub_nonneg.mpr hl)]
    have hright : edge - holding * (lower + depth) / 2 ≤ 0 := by
      nlinarith [mul_nonneg hnonneg (sub_nonneg.mpr hdepth.1)]
    exact mul_nonneg_of_nonpos_of_nonpos hleft hright
  · have hl' : lower ≤ edge / holding := le_of_lt (lt_of_not_ge hl)
    by_cases hu : upper ≤ edge / holding
    · have hc : clampedCapacity lower upper edge holding = upper := by
        simp [clampedCapacity, max_eq_right hl', min_eq_left hu]
      rw [hc]
      rw [← sub_nonneg, capacity_quadratic_difference]
      have hleft : 0 ≤ upper - depth := by linarith [hdepth.2]
      have hedge : holding * upper ≤ edge := by
        nlinarith [mul_nonneg hnonneg (sub_nonneg.mpr hu)]
      have hright : 0 ≤ edge - holding * (upper + depth) / 2 := by
        nlinarith [mul_nonneg hnonneg (sub_nonneg.mpr hdepth.2)]
      exact mul_nonneg hleft hright
    · have hu' : edge / holding ≤ upper := le_of_lt (lt_of_not_ge hu)
      have hc : clampedCapacity lower upper edge holding = edge / holding := by
        simp [clampedCapacity, max_eq_right hl', min_eq_right hu']
      rw [hc]
      unfold capacityProfit
      nlinarith [sq_nonneg (depth - edge / holding)]

theorem capacity_weakly_increases_with_budget (lower upper edge holding b0 b1 m : ℝ)
    (hm : 0 < m) (hb : b0 ≤ b1) :
    clampedCapacity lower (min upper (b0 / m)) edge holding ≤
      clampedCapacity lower (min upper (b1 / m)) edge holding := by
  unfold clampedCapacity
  exact min_le_min (min_le_min_left upper (div_le_div_of_nonneg_right hb (le_of_lt hm)))
    (le_refl _)

end
end CurrentMM
