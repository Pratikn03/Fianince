import Mathlib

/-!
# Paper 1, 21 November 2026: Proposition `n:learnergap` (fitted-forecast gains and the value of information)

The Hilbert-space core of the proposition. Work in a real inner product space (for the proposition, square-integrable
random variables with the inner product `E[XY | D]`). The oracle forecasts `mA`, `mB` are orthogonal projections:
the error `Y - mA` is orthogonal to everything measurable with respect to the augmented information set, which
contains `mA - fA` and `mA - mB`, and `Y - mB` is orthogonal to `mB - fB`.

* `risk_decomposition`: `‖Y - f‖² = ‖Y - m‖² + ‖m - f‖²` when `Y - m ⟂ m - f`.
* `learner_gap_identity`: `R_B - R_A = Δ* + e_B - e_A` with `Δ* = ‖Y - mB‖² - ‖Y - mA‖²`.
* `oracle_gain_nonneg`: `Δ* = ‖mA - mB‖² ≥ 0`.
* `oracle_gain_bound`: `Δ* ≤ R_B - R_A + e_A`.
-/
namespace Paper1Revision9

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-- Pythagoras for a projection error. -/
theorem risk_decomposition (Y m f : E) (h : inner ℝ (Y - m) (m - f) = 0) :
    ‖Y - f‖ ^ 2 = ‖Y - m‖ ^ 2 + ‖m - f‖ ^ 2 := by
  have hsplit : Y - f = (Y - m) + (m - f) := by abel
  rw [hsplit, norm_add_sq_real, h]
  ring

/-- The learner-gap identity: the gain of fitted forecasts is the oracle gain plus the difference of the fitted
predictors' excess risks. -/
theorem learner_gap_identity (Y mA mB fA fB : E)
    (hA : inner ℝ (Y - mA) (mA - fA) = 0) (hB : inner ℝ (Y - mB) (mB - fB) = 0) :
    ‖Y - fB‖ ^ 2 - ‖Y - fA‖ ^ 2 =
      (‖Y - mB‖ ^ 2 - ‖Y - mA‖ ^ 2) + ‖mB - fB‖ ^ 2 - ‖mA - fA‖ ^ 2 := by
  rw [risk_decomposition Y mA fA hA, risk_decomposition Y mB fB hB]
  ring

/-- The oracle gain is nonnegative: it equals `‖mA - mB‖²` when `Y - mA ⟂ mA - mB`. -/
theorem oracle_gain_nonneg (Y mA mB : E) (h : inner ℝ (Y - mA) (mA - mB) = 0) :
    ‖Y - mB‖ ^ 2 - ‖Y - mA‖ ^ 2 = ‖mA - mB‖ ^ 2 ∧ 0 ≤ ‖Y - mB‖ ^ 2 - ‖Y - mA‖ ^ 2 := by
  have := risk_decomposition Y mA mB h
  constructor
  · linarith
  · nlinarith [sq_nonneg ‖mA - mB‖]

/-- An upper bound on the gain of fitted forecasts bounds the oracle gain only together with the augmented
predictor's excess risk: `Δ* ≤ R_B - R_A + e_A`. -/
theorem oracle_gain_bound (Y mA mB fA fB : E)
    (hA : inner ℝ (Y - mA) (mA - fA) = 0) (hB : inner ℝ (Y - mB) (mB - fB) = 0) :
    ‖Y - mB‖ ^ 2 - ‖Y - mA‖ ^ 2 ≤ (‖Y - fB‖ ^ 2 - ‖Y - fA‖ ^ 2) + ‖mA - fA‖ ^ 2 := by
  have h := learner_gap_identity Y mA mB fA fB hA hB
  nlinarith [sq_nonneg ‖mB - fB‖]

end Paper1Revision9
