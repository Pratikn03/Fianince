import Mathlib.MeasureTheory.Integral.Bochner.Basic
import Mathlib.Tactic

namespace CurrentMM
open MeasureTheory

/-- A uniform tail controls bias for an arbitrary finite positive measure. -/
theorem thesis_general_measure_bias (μ : Measure ℝ) [IsFiniteMeasure μ]
    (g p : ℝ → ℝ) (B u : ℝ) (hg : Integrable g μ) (hp : Integrable p μ)
    (hmass : μ.real Set.univ ≤ B) (hu : 0 ≤ u)
    (htail : ∀ᵐ r ∂μ, |g r-p r| ≤ u) :
    |(∫ r, g r ∂μ)-(∫ r, p r ∂μ)| ≤ B*u := by
  have hnorm : ∀ᵐ r ∂μ, ‖g r-p r‖ ≤ u := by
    simpa only [Real.norm_eq_abs] using htail
  have hi := norm_integral_le_of_norm_le_const hnorm
  rw [Real.norm_eq_abs] at hi
  calc
    |(∫ r, g r ∂μ)-(∫ r, p r ∂μ)| = |∫ r, g r-p r ∂μ| := by
      rw [integral_sub hg hp]
    _ ≤ u*μ.real Set.univ := hi
    _ ≤ u*B := mul_le_mul_of_nonneg_left hmass hu
    _ = B*u := mul_comm _ _

end CurrentMM
