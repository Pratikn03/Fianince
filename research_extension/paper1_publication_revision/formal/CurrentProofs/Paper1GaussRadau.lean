import CurrentProofs.Paper1SupervisorySeparation
import Mathlib.Analysis.SpecialFunctions.Sqrt

/-! The exact two-point Gauss/Gauss--Radau witness used by the numerical table.
The nodes, weights, matched moments and a spacing-independent dominant-intensity
gap are proved here. This is not an all-K quadrature construction. -/

namespace CurrentMM
open Finset MeasureTheory
open scoped ENNReal NNReal

noncomputable def grGNode : Fin 2 → ℝ := ![-Real.sqrt (1 / 3), Real.sqrt (1 / 3)]
noncomputable def grRNode : Fin 2 → ℝ := ![-1, 1 / 3]
noncomputable def grGWeight : Fin 2 → ℝ := ![1 / 2, 1 / 2]
noncomputable def grRWeight : Fin 2 → ℝ := ![1 / 4, 3 / 4]

theorem p1_gr_node_bounds : (∀ i, |grGNode i| ≤ 1) ∧ (∀ i, |grRNode i| ≤ 1) := by
  have h0 : 0 ≤ Real.sqrt (1 / 3 : ℝ) := Real.sqrt_nonneg _
  have hsq := Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 1 / 3)
  have h1 : Real.sqrt (1 / 3 : ℝ) ≤ 1 := by nlinarith
  constructor
  · intro i
    fin_cases i
    · change |-Real.sqrt (1 / 3 : ℝ)| ≤ 1
      rw [abs_neg, abs_of_nonneg h0]
      exact h1
    · change |Real.sqrt (1 / 3 : ℝ)| ≤ 1
      rw [abs_of_nonneg h0]
      exact h1
  · intro i; fin_cases i <;> norm_num [grRNode]

theorem p1_gr_positive_weights :
    (∀ i, 0 < grGWeight i) ∧ (∀ i, 0 < grRWeight i) := by
  constructor <;> intro i <;> fin_cases i <;> norm_num [grGWeight, grRWeight]

theorem p1_gr_normalized_weights : (∑ i, grGWeight i) = 1 ∧ (∑ i, grRWeight i) = 1 := by
  norm_num [Fin.sum_univ_two, grGWeight, grRWeight]

theorem p1_gr_three_matched_moments (W : ℝ) (j : ℕ) (hj : j < 3) :
    (∑ i, W * grGWeight i * grGNode i ^ j) =
      ∑ i, W * grRWeight i * grRNode i ^ j := by
  have hsq := Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 1 / 3)
  have hScaled : W * Real.sqrt (1 / 3 : ℝ) ^ 2 = W / 3 := by rw [hsq]; ring
  interval_cases j <;> simp [Fin.sum_univ_two, grGWeight, grRWeight, grGNode, grRNode] <;>
    nlinarith

theorem p1_gr_third_moment_gap (W : ℝ) :
    (∑ i, W * grGWeight i * grGNode i ^ 3) -
      (∑ i, W * grRWeight i * grRNode i ^ 3) = 2 * W / 9 := by
  simp [Fin.sum_univ_two, grGWeight, grRWeight, grGNode, grRNode]
  ring

noncomputable def grIntensity (weight node : Fin 2 → ℝ) (W u d : ℝ) (i : Fin 2) : ℝ :=
  W * weight i / (u - d * node i)

/-- The weight-gap premise for the exact K=2 numerical pair is constructed,
not supplied as a hypothesis. The gap remains positive as d tends to zero. -/
theorem p1_gr_dominant_intensity_gap (W u d : ℝ)
    (hW : 0 < W) (hu : 0 < u) (hd : 0 ≤ d) (hSmall : d ≤ u / 3) :
    ∀ i : Fin 2, grIntensity grGWeight grGNode W u d i ≤
      grIntensity grRWeight grRNode W u d 1 - W / (8 * u) := by
  have hud : 0 < u - d := by linarith
  have hDenR : 0 < u - d / 3 := by linarith
  have hR : 3 * W / (4 * u) ≤ grIntensity grRWeight grRNode W u d 1 := by
    norm_num [grIntensity, grRWeight, grRNode]
    rw [div_le_div_iff₀ (by positivity : (0 : ℝ) < 4 * u) (by linarith)]
    nlinarith [mul_nonneg hW.le hd]
  intro i
  have hs := (p1_gr_node_bounds.1 i)
  have hgs : grGNode i ≤ 3 / 5 := by
    have h0 : 0 ≤ Real.sqrt (1 / 3 : ℝ) := Real.sqrt_nonneg _
    have hsq := Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 1 / 3)
    have hRoot : Real.sqrt (1 / 3 : ℝ) ≤ 3 / 5 := by nlinarith
    fin_cases i
    · change -Real.sqrt (1 / 3 : ℝ) ≤ 3 / 5
      linarith
    · change Real.sqrt (1 / 3 : ℝ) ≤ 3 / 5
      exact hRoot
  have hScaled := mul_le_mul_of_nonneg_left hgs hd
  have hds : 5 * d * grGNode i ≤ u := by linarith
  have hDenG : 0 < u - d * grGNode i := by linarith
  have hWeight : grGWeight i = 1 / 2 := by fin_cases i <;> norm_num [grGWeight]
  have hG : grIntensity grGWeight grGNode W u d i ≤ 5 * W / (8 * u) := by
    simp only [grIntensity, hWeight]
    rw [div_le_div_iff₀ hDenG (by positivity : (0 : ℝ) < 8 * u)]
    have hMargin : 0 ≤ W * (u - 5 * d * grGNode i) := mul_nonneg hW.le (by linarith)
    nlinarith
  have hId : 3 * W / (4 * u) - 5 * W / (8 * u) = W / (8 * u) := by ring
  linarith

theorem p1_gr_aggregate_gap (W u d : ℝ)
    (hW : 0 < W) (hd : 0 ≤ d) (hdu : d < u) :
    |(∑ i, grIntensity grGWeight grGNode W u d i) -
      ∑ i, grIntensity grRWeight grRNode W u d i| ≤
        2 * W * d ^ 3 / (u ^ 3 * (u - d)) := by
  apply p1_persistence_gap (fun i => W * grGWeight i) grGNode
    (fun i => W * grRWeight i) grRNode u d W 3 hd hdu
  · intro i; exact mul_nonneg hW.le (p1_gr_positive_weights.1 i).le
  · intro i; exact mul_nonneg hW.le (p1_gr_positive_weights.2 i).le
  · simp [Fin.sum_univ_two, grGWeight]; linarith
  · simp [Fin.sum_univ_two, grRWeight]; linarith
  · exact p1_gr_node_bounds.1
  · exact p1_gr_node_bounds.2
  · exact p1_gr_three_matched_moments W

/-- Actual finite Gaussian price-record testing bound for the exact two-point
Gauss/Radau witness. The rate and weight equalities specify the model; neither
matched moments nor a statistical divergence conclusion is assumed. -/
theorem p1_gr_reset_lower_bound (a κ c d W H : ℝ) (N T : ℕ)
    (q rate q' rate' : Fin 2 → ℝ) (variance : ℝ≥0) (hv : variance ≠ 0)
    (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd : c + d ≤ 1) (hW : 0 < W) (hH : 0 ≤ H)
    (hr : ∀ i, 1 - rate i = c + d * grGNode i)
    (hr' : ∀ i, 1 - rate' i = c + d * grRNode i)
    (hq : ∀ i, q i * rate i = W * grGWeight i)
    (hq' : ∀ i, q' i * rate' i = W * grRWeight i)
    (hh' : ∀ t, t < T → |actualCohortImpulse a κ q' rate' t| ≤ H)
    (A : Set (ObservationRecord (N * T))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate))
      variance).real A ≤ 1 / 4)
    (herr1 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate'))
      variance).real Aᶜ ≤ 1 / 4) :
    (variance : ℝ) ≤ 2 * N * T * ((2 * W * 2 ^ T * d ^ 3) * p1GapConst a |κ| W H T) ^ 2 := by
  apply p1_thm_kcohort_lower_bound_formal a κ c d W H 3 N T q rate grGNode q' rate' grRNode
    variance hv hc hd hcd hH hr hr' p1_gr_node_bounds.1 p1_gr_node_bounds.2
  · intro i; rw [hq]; exact mul_nonneg hW.le (p1_gr_positive_weights.1 i).le
  · intro i; rw [hq']; exact mul_nonneg hW.le (p1_gr_positive_weights.2 i).le
  · simp_rw [hq]; simp [Fin.sum_univ_two, grGWeight]; linarith
  · simp_rw [hq']; simp [Fin.sum_univ_two, grRWeight]; linarith
  · intro j hj
    simp only [mgMoment]
    simp_rw [hq, hq']
    exact p1_gr_three_matched_moments W j hj
  · exact hh'
  · exact hA
  · exact herr0
  · exact herr1

end CurrentMM

#print axioms CurrentMM.p1_gr_node_bounds
#print axioms CurrentMM.p1_gr_positive_weights
#print axioms CurrentMM.p1_gr_normalized_weights
#print axioms CurrentMM.p1_gr_three_matched_moments
#print axioms CurrentMM.p1_gr_third_moment_gap
#print axioms CurrentMM.p1_gr_dominant_intensity_gap
#print axioms CurrentMM.p1_gr_aggregate_gap
#print axioms CurrentMM.p1_gr_reset_lower_bound
