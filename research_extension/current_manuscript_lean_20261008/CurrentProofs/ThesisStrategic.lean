import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum

namespace CurrentMM

/-- Exact certification followed by a discontinuous admission threshold. -/
noncomputable def thesisStrategicAdmission (q : ℝ) : ℝ := if q ≤ 1/2 then 1 else 0

/-- Continuous profit in weight and admission; the cost is identically zero. -/
def thesisStrategicProfit (q admission : ℝ) : ℝ := (1-admission)*(1-q)

noncomputable def thesisStrategicUtility (q : ℝ) : ℝ :=
  thesisStrategicProfit q (thesisStrategicAdmission q)

/-- Every admissible weight has a strictly profitable admissible deviation. -/
theorem thesis_strategic_profitable_deviation (q : ℝ) (h0 : 0 ≤ q) (h1 : q ≤ 1) :
    ∃ q' : ℝ, 0 ≤ q' ∧ q' ≤ 1 ∧ thesisStrategicUtility q < thesisStrategicUtility q' := by
  by_cases h : q ≤ 1/2
  · refine ⟨3/4, by norm_num, by norm_num, ?_⟩
    norm_num [thesisStrategicUtility, thesisStrategicProfit, thesisStrategicAdmission, h]
  · have hgt : 1/2 < q := lt_of_not_ge h
    have hmid : ¬ (q+1/2)/2 ≤ 1/2 := by linarith
    refine ⟨(q+1/2)/2, by linarith, by linarith, ?_⟩
    simp only [thesisStrategicUtility, thesisStrategicProfit, thesisStrategicAdmission,
      if_neg h, if_neg hmid]
    linarith

/-- The one-player game has no maximizer, hence no pure Nash equilibrium. -/
theorem thesis_strategic_no_equilibrium :
    ¬ ∃ q : ℝ, 0 ≤ q ∧ q ≤ 1 ∧
      ∀ z : ℝ, 0 ≤ z → z ≤ 1 → thesisStrategicUtility z ≤ thesisStrategicUtility q := by
  rintro ⟨q, h0, h1, hmax⟩
  obtain ⟨z, hz0, hz1, hgain⟩ := thesis_strategic_profitable_deviation q h0 h1
  have hbound := hmax z hz0 hz1
  linarith

end CurrentMM
