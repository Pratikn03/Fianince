import CurrentProofs.Paper1Tagged
import CurrentProofs.Paper1SupervisorySeparation

/-!
# A declared supervisory measurement contract and after-cost decisions

The probability theorem below concerns actual product Gaussian measures, not
a number named `prob_bound`. The scalar observation is a direct measurement of
a fixed post-halt feedback budget. It is not identified with tagged order flow
or with reported position stocks. The action-response allowance is a hypothesis,
not a derived strategic equilibrium. The Chebyshev gate is deliberately distinct
from the sharper normal-quantile gate used in the earlier numerical illustration.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory Finset
open scoped ENNReal NNReal

/-- A valid response allowance preserves a nonempty threshold window. -/
theorem p1_response_robust_threshold
    (rA rB movedA movedB threshold radius : ℝ)
    (hA : rA + radius ≤ threshold) (hB : threshold < rB - radius)
    (hMoveA : |movedA - rA| ≤ radius)
    (hMoveB : |movedB - rB| ≤ radius) :
    movedA ≤ threshold ∧ threshold < movedB := by
  have hUpper := (abs_le.mp hMoveA).2
  have hLower := (abs_le.mp hMoveB).1
  constructor <;> linarith

/-- Under the declared scalar Gaussian reset contract, an unsafe halt is
contained in an actual sample-mean deviation event. This theorem includes
the product law, the sample statistic, the action event and the response bound. -/
theorem p1_supervisory_gaussian_unsafe_halt
    (N : ℕ) (hN : 0 < N) (r threshold allowance drift radius : ℝ)
    (v : ℝ≥0) (hRadius : 0 < radius) (hDrift : drift ≤ allowance) :
    (Measure.pi fun _ : Fin N => gaussianReal r v)
        {x | (∑ i, x i) / N + radius + allowance ≤ threshold ∧
          threshold < r + drift} ≤
      ENNReal.ofReal (v / (N * radius ^ 2)) := by
  refine le_trans (measure_mono ?_) (p1_tagged_mean_chebyshev N hN r v radius hRadius)
  intro x hx
  change radius ≤ |(∑ i, x i) / N - r|
  have hdev : radius ≤ -((∑ i, x i) / N - r) := by
    have hGate := hx.1
    have hUnsafe := hx.2
    linarith
  exact le_trans hdev (neg_le_abs _)

/-- A sample-size/precision budget bounds the unsafe-halt event by beta. -/
theorem p1_supervisory_gaussian_unsafe_halt_budget
    (N : ℕ) (hN : 0 < N) (r threshold allowance drift radius beta : ℝ)
    (v : ℝ≥0) (hRadius : 0 < radius) (hDrift : drift ≤ allowance)
    (hBudget : (v : ℝ) ≤ beta * (N * radius ^ 2)) :
    (Measure.pi fun _ : Fin N => gaussianReal r v)
        {x | (∑ i, x i) / N + radius + allowance ≤ threshold ∧
          threshold < r + drift} ≤ ENNReal.ofReal beta := by
  refine le_trans (p1_supervisory_gaussian_unsafe_halt N hN r threshold allowance drift
    radius v hRadius hDrift) (ENNReal.ofReal_le_ofReal ?_)
  have hNReal : (0 : ℝ) < N := by exact_mod_cast hN
  exact (div_le_iff₀ (by positivity : (0 : ℝ) < N * radius ^ 2)).2 hBudget

/-- If halting is weakly more expensive in expectation, the optimal no-data
lottery over halt/throttle never halts. This is a fixed two-action menu. -/
theorem p1_no_data_throttle_optimal (fallback halt p : ℝ)
    (hp : 0 ≤ p) (hCost : fallback ≤ halt) :
    fallback ≤ p * halt + (1 - p) * fallback := by
  nlinarith [mul_nonneg hp (sub_nonneg.mpr hCost)]

/-- If halting is cheaper, the best feasible no-data lottery uses the largest
allowed halt probability. The caller must establish its error-budget cap. -/
theorem p1_no_data_capped_halt_optimal (fallback halt p pMax : ℝ)
    (hp : p ≤ pMax) (hCost : halt ≤ fallback) :
    pMax * halt + (1 - pMax) * fallback ≤
      p * halt + (1 - p) * fallback := by
  nlinarith [mul_nonneg (sub_nonneg.mpr hp) (sub_nonneg.mpr hCost)]

/-- Complete cost decomposition: information is beneficial exactly when its
gross improvement exceeds its declared bill. This does not estimate the bill. -/
theorem p1_information_purchase_break_even
    (fallback expectedActionLoss fixedFee perSample n : ℝ) :
    fixedFee + n * perSample + expectedActionLoss < fallback ↔
      fixedFee + n * perSample < fallback - expectedActionLoss := by
  constructor <;> intro h <;> linarith

/-- Optional acquisition cannot worsen the modeled objective because abstaining
from the purchase and retaining the fallback remains feasible. -/
theorem p1_optional_information_value_nonnegative (fallback paid : ℝ) :
    0 ≤ fallback - min fallback paid := by
  exact sub_nonneg.mpr (min_le_left _ _)

/-- Robust feasibility of the fallback action under a known aggregate envelope. -/
theorem p1_robust_uniform_action (a theta sEnvelope s threshold allowance drift : ℝ)
    (hTheta : 0 ≤ theta) (hEnvelope : s ≤ sEnvelope)
    (hBound : a + theta * (sEnvelope - a) + allowance ≤ threshold)
    (hDrift : drift ≤ allowance) :
    a + theta * (s - a) + drift ≤ threshold := by
  have hScale := mul_le_mul_of_nonneg_left hEnvelope hTheta
  nlinarith

end CurrentMM

#print axioms CurrentMM.p1_response_robust_threshold
#print axioms CurrentMM.p1_supervisory_gaussian_unsafe_halt
#print axioms CurrentMM.p1_supervisory_gaussian_unsafe_halt_budget
#print axioms CurrentMM.p1_no_data_throttle_optimal
#print axioms CurrentMM.p1_no_data_capped_halt_optimal
#print axioms CurrentMM.p1_information_purchase_break_even
#print axioms CurrentMM.p1_optional_information_value_nonnegative
#print axioms CurrentMM.p1_robust_uniform_action
