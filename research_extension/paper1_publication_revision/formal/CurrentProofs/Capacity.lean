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

/-- Lemma 2.13: One-cohort characteristic polynomial Jury quantities and Schur stability equivalence. -/
theorem one_cohort_jury_stability_iff (kappa phi q eta : ℝ)
    (hkappa : 0 < kappa) (hphi : 0 < phi) (heta0 : 0 < eta) (heta1 : eta < 1) :
    let a := 1 - kappa * phi
    let tr := a + (1 - eta) + eta * kappa * q
    let det := a * (1 - eta)
    (1 - tr + det = kappa * eta * (phi - q) ∧
      1 + tr + det = 4 - 2 * eta - kappa * ((2 - eta) * phi - eta * q) ∧
      1 - det = eta + (1 - eta) * kappa * phi) ∧
    ((0 < 1 - tr + det ∧ 0 < 1 + tr + det ∧ 0 < 1 - det) ↔
      (q < phi ∧ kappa * ((2 - eta) * phi - eta * q) < 4 - 2 * eta)) := by
  dsimp only
  have h1 : 1 - (1 - kappa * phi + (1 - eta) + eta * kappa * q) + (1 - kappa * phi) * (1 - eta) =
      kappa * eta * (phi - q) := by ring
  have h2 : 1 + (1 - kappa * phi + (1 - eta) + eta * kappa * q) + (1 - kappa * phi) * (1 - eta) =
      4 - 2 * eta - kappa * ((2 - eta) * phi - eta * q) := by ring
  have h3 : 1 - (1 - kappa * phi) * (1 - eta) = eta + (1 - eta) * kappa * phi := by ring
  refine ⟨⟨h1, h2, h3⟩, ?_⟩
  rw [h1, h2, h3]
  have hke : 0 < kappa * eta := mul_pos hkappa heta0
  have hdet_pos : 0 < eta + (1 - eta) * kappa * phi := by
    have : 0 < (1 - eta) * kappa * phi := mul_pos (mul_pos (by linarith) hkappa) hphi
    linarith
  constructor
  · rintro ⟨hj1, hj2, _⟩
    have hqp : 0 < phi - q := (mul_pos_iff_of_pos_left hke).mp hj1
    exact ⟨by linarith, by linarith⟩
  · rintro ⟨hq, hk⟩
    exact ⟨mul_pos hke (by linarith), by linarith, hdet_pos⟩

/-- Lemma 2.13: Exact two-matrix counterexample showing higher impact `κ` can reduce peak Euclidean magnification. -/
theorem capacity_impact_transient_counterexample :
    ((9 : ℝ) / 10) ^ 2 + ((81 : ℝ) / 100) ^ 2 = 14661 / 10000 ∧
    (1 : ℝ) < ((9 : ℝ) / 10) ^ 2 + ((81 : ℝ) / 100) ^ 2 ∧
    ((1 : ℝ) / 10) ^ 2 + ((19 : ℝ) / 100) ^ 2 = 461 / 10000 ∧
    ((1 : ℝ) / 10) ^ 2 + ((19 : ℝ) / 100) ^ 2 < 1 := by
  refine ⟨by norm_num, by norm_num, by norm_num, by norm_num⟩

end
end CurrentMM

