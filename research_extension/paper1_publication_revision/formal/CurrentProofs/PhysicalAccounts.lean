import CurrentProofs.SpectralCohorts

namespace CurrentMM
noncomputable section
open scoped BigOperators

def actualBaselineBeforeFill {n T : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ)
    (v : Fin T → ℝ) (i : Fin T) : ℝ :=
  (cohortStep a impact q rate 0
    (controlledCohortRun a impact q rate (extendFiniteProbe v) i.val)).price

theorem actual_baseline_direct_fill {n T : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ)
    (v : Fin T → ℝ) (i : Fin T) :
    actualBaselineBeforeFill a impact q rate v i + impact * v i =
      (controlledCohortRun a impact q rate (extendFiniteProbe v) (i.val + 1)).price := by
  simp [actualBaselineBeforeFill, controlledCohortRun, cohortStep, extendFiniteProbe]

theorem actual_finite_price_scalar_convolution {n T : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (v : Fin T → ℝ) (i : Fin T) :
    (controlledCohortRun a impact q rate (extendFiniteProbe v) (i.val + 1)).price =
      ∑ j, v j * (if j ≤ i then actualCohortImpulse a impact q rate (i.val - j.val) else 0) := by
  have h := congrArg (fun z : EuclideanSpace ℝ (Fin T) => z i)
    (actual_cohort_record_is_causal_convolution a impact q rate v)
  simpa only [actualCohortPriceRecord, PiLp.toLp_apply, causalImpulseConvolution,
    causalImpulseColumn, WithLp.ofLp_sum, Finset.sum_apply, PiLp.smul_apply,
    smul_eq_mul] using h

theorem actual_refreshed_baseline_is_kernel {n T : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (v : Fin T → ℝ) (i : Fin T) :
    actualBaselineBeforeFill a impact q rate v i =
      baselineDisplacement (actualCohortImpulse a impact q rate) v i := by
  have hzero : actualCohortImpulse a impact q rate 0 = impact := by
    simp [actualCohortImpulse, cohortInputVector]
  have hterm (j : Fin T) :
      v j * (if j ≤ i then actualCohortImpulse a impact q rate (i.val - j.val) else 0) =
      (if j < i then actualCohortImpulse a impact q rate (i.val - j.val) * v j else 0) +
        (if j = i then impact * v i else 0) := by
    rcases lt_trichotomy j i with hji | heq | hij
    · simp [hji, le_of_lt hji, ne_of_lt hji]; ring
    · subst j
      simp [hzero]
      ring
    · simp [not_le_of_gt hij, not_lt_of_ge (le_of_lt hij), ne_of_gt hij]
  have hsum : (∑ j, v j * (if j ≤ i then actualCohortImpulse a impact q rate
      (i.val - j.val) else 0)) =
      baselineDisplacement (actualCohortImpulse a impact q rate) v i + impact * v i := by
    simp_rw [hterm, Finset.sum_add_distrib]
    simp [baselineDisplacement]
  have hprice := actual_finite_price_scalar_convolution a impact q rate v i
  rw [hsum] at hprice
  have hfill := actual_baseline_direct_fill a impact q rate v i
  linarith

theorem actual_final_price_is_sequence_displacement {n T : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (v : Fin T → ℝ) :
    (controlledCohortRun a impact q rate (extendFiniteProbe v) T).price =
      sequenceFinalDisplacement (actualCohortImpulse a impact q rate) v := by
  cases T with
  | zero => simp [controlledCohortRun, zeroState, sequenceFinalDisplacement]
  | succ T =>
    rw [actual_reset_price_convolution, Finset.sum_range]
    simp [sequenceFinalDisplacement, extendFiniteProbe]
    apply Finset.sum_congr rfl
    intro i hi
    have hle : i.val ≤ T := by omega
    simp [hle]

def physicalDealerCash {n T : ℕ} (a B P impact fee : ℝ) (q rate : Fin n → ℝ)
    (v : Fin T → ℝ) : ℝ :=
  B + ∑ i, v i * (P + actualBaselineBeforeFill a impact q rate v i + impact * v i / 2)
    - fee * cumulativeQuantity v

def physicalDealerEquity {n T : ℕ} (a B P impact fee : ℝ) (q rate : Fin n → ℝ)
    (v : Fin T → ℝ) : ℝ :=
  equity (physicalDealerCash a B P impact fee q rate v) (-cumulativeQuantity v)
    (P + (controlledCohortRun a impact q rate (extendFiniteProbe v) T).price)

theorem physical_dealer_cash_matches_sequence {n T : ℕ} (a B P impact fee : ℝ)
    (q rate : Fin n → ℝ) (v : Fin T → ℝ) :
    physicalDealerCash a B P impact fee q rate v =
      sequenceDealerCash B P impact fee (actualCohortImpulse a impact q rate) v := by
  simp only [physicalDealerCash, sequenceDealerCash, actual_refreshed_baseline_is_kernel]

theorem physical_dealer_equity_matches_sequence {n T : ℕ} (a B P impact fee : ℝ)
    (q rate : Fin n → ℝ) (v : Fin T → ℝ) :
    physicalDealerEquity a B P impact fee q rate v =
      sequenceDealerEquity B P impact fee (actualCohortImpulse a impact q rate) v := by
  simp only [physicalDealerEquity, sequenceDealerEquity,
    physical_dealer_cash_matches_sequence, actual_final_price_is_sequence_displacement]

def physicalRobustQuantityMargin {n : ℕ} (a B P impact fee margin V : ℝ)
    (q rate : Fin n → ℝ) : Prop :=
  ∀ T (v : Fin T → ℝ), (∀ i, 0 ≤ v i) → cumulativeQuantity v ≤ V →
    margin * |-(cumulativeQuantity v)| *
        (P + (controlledCohortRun a impact q rate (extendFiniteProbe v) T).price) ≤
      physicalDealerEquity a B P impact fee q rate v

theorem actual_physical_counterparty_robust_cap {n : ℕ} (a B P impact fee margin V : ℝ)
    (q rate : Fin n → ℝ) (ha : 0 ≤ a) (hk : 0 < impact) (hP : 0 < P)
    (hc : 0 ≤ fee) (hm : 0 < margin) (hB : 0 < B) (hV : 0 ≤ V)
    (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : a + impact * ∑ i, q i < 1) :
    physicalRobustQuantityMargin a B P impact fee margin V q rate ↔
      V ≤ robustQuantityCap ((margin + 1 / 2) * impact) (fee + margin * P) B := by
  have heq : physicalRobustQuantityMargin a B P impact fee margin V q rate ↔
      robustNonnegativeSequenceMargin B P impact fee margin V (actualCohortImpulse a impact q rate) := by
    simp only [physicalRobustQuantityMargin, robustNonnegativeSequenceMargin,
      physical_dealer_equity_matches_sequence, actual_final_price_is_sequence_displacement]
  rw [heq]
  exact physical_cohort_robust_quantity_allowance a B P impact fee margin V q rate
    ha hk hP hc hm hB hV hq hr hf

theorem actual_physical_partial_fill_margin {n T : ℕ} (a B P impact fee margin V : ℝ)
    (q rate : Fin n → ℝ) (v : Fin (T + 1) → ℝ) (fraction : ℝ)
    (ha : 0 ≤ a) (hk : 0 < impact) (hP : 0 < P) (hc : 0 ≤ fee) (hm : 0 < margin)
    (hB : 0 < B) (hV : 0 ≤ V) (hq : ∀ i, 0 ≤ q i)
    (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1) (hf : a + impact * ∑ i, q i < 1)
    (hv : ∀ i, 0 ≤ v i) (hfrac : 0 ≤ fraction ∧ fraction ≤ 1)
    (hbudget : cumulativeQuantity v ≤ V)
    (hcap : V ≤ robustQuantityCap ((margin + 1 / 2) * impact) (fee + margin * P) B) :
    margin * |-(cumulativeQuantity (partialLastFill v fraction))| *
        (P + (controlledCohortRun a impact q rate
          (extendFiniteProbe (partialLastFill v fraction)) (T + 1)).price) ≤
      physicalDealerEquity a B P impact fee q rate (partialLastFill v fraction) := by
  have hall := (actual_physical_counterparty_robust_cap a B P impact fee margin V q rate
    ha hk hP hc hm hB hV hq hr hf).2 hcap
  have hp := partial_last_fill_quantity_bound v fraction hv hfrac
  exact hall (T + 1) _ hp.1 (le_trans hp.2 hbudget)

theorem actual_physical_nonnegative_probe_mark_positive {n T : ℕ} (a P impact : ℝ)
    (q rate : Fin n → ℝ) (v : Fin T → ℝ) (ha : 0 ≤ a) (hk : 0 ≤ impact) (hP : 0 < P)
    (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : a + impact * ∑ i, q i < 1) (hv : ∀ i, 0 ≤ v i) :
    0 < P + (controlledCohortRun a impact q rate (extendFiniteProbe v) T).price := by
  rw [actual_final_price_is_sequence_displacement]
  have hp : 0 ≤ sequenceFinalDisplacement (actualCohortImpulse a impact q rate) v := by
    apply Finset.sum_nonneg
    intro i hi
    exact mul_nonneg (hv i) (actual_positive_impulse_peak a impact q rate ha hk hq
      (fun j => ⟨le_of_lt (hr j).1, (hr j).2⟩) (le_of_lt hf) _).1
  linarith

theorem actual_physical_counterparty_equity_positive {n T : ℕ} (a B P impact fee margin V : ℝ)
    (q rate : Fin n → ℝ) (v : Fin T → ℝ)
    (ha : 0 ≤ a) (hk : 0 < impact) (hP : 0 < P) (hc : 0 ≤ fee) (hm : 0 < margin)
    (hB : 0 < B) (hV : 0 ≤ V) (hq : ∀ i, 0 ≤ q i)
    (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1) (hf : a + impact * ∑ i, q i < 1)
    (hv : ∀ i, 0 ≤ v i) (hbudget : cumulativeQuantity v ≤ V)
    (hcap : V ≤ robustQuantityCap ((margin + 1 / 2) * impact) (fee + margin * P) B) :
    0 < physicalDealerEquity a B P impact fee q rate v := by
  have hU : 0 ≤ cumulativeQuantity v := Finset.sum_nonneg fun i _ => hv i
  rcases lt_or_eq_of_le hU with hpositive | hzero
  · have hall := (actual_physical_counterparty_robust_cap a B P impact fee margin V q rate
      ha hk hP hc hm hB hV hq hr hf).2 hcap
    have hs := hall T v hv hbudget
    rw [abs_neg, abs_of_nonneg hU] at hs
    have hp := actual_physical_nonnegative_probe_mark_positive a P impact q rate v
      ha (le_of_lt hk) hP hq hr hf hv
    exact lt_of_lt_of_le (mul_pos (mul_pos hm hpositive) hp) hs
  · have hnil : ∀ i, v i = 0 := by
      have hsum : (∑ i, v i) = 0 := hzero.symm
      exact fun i => (Finset.sum_eq_zero_iff_of_nonneg (fun j _ => hv j)).1 hsum i (Finset.mem_univ _)
    simpa [physicalDealerEquity, physicalDealerCash, equity, cumulativeQuantity, hnil] using hB

end
end CurrentMM
