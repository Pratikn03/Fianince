import CurrentProofs.GaussianQuotes
import Mathlib.Analysis.InnerProductSpace.PiL2

namespace CurrentMM
noncomputable section
open scoped BigOperators

/-- Input-column inequality for a fixed finite-horizon experiment, in any real normed space.
Euclidean instantiations use `EuclideanSpace`, never the sup norm on a bare function type. -/
theorem finite_column_quantity_bound {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    {n : ℕ} (columns : Fin n → E) (quantity : Fin n → ℝ) (M V : ℝ)
    (hM : 0 ≤ M) (hcolumns : ∀ i, ‖columns i‖ ≤ M)
    (hbudget : ∑ i, |quantity i| ≤ V) :
    ‖∑ i, quantity i • columns i‖ ≤ V * M := by
  calc
    ‖∑ i, quantity i • columns i‖ ≤ ∑ i, ‖quantity i • columns i‖ := norm_sum_le _ _
    _ = ∑ i, |quantity i| * ‖columns i‖ := by simp [norm_smul, Real.norm_eq_abs]
    _ ≤ ∑ i, |quantity i| * M := by
      apply Finset.sum_le_sum
      intro i hi
      exact mul_le_mul_of_nonneg_left (hcolumns i) (abs_nonneg _)
    _ = (∑ i, |quantity i|) * M := (Finset.sum_mul _ _ _).symm
    _ ≤ V * M := mul_le_mul_of_nonneg_right hbudget hM

theorem quantity_pulse_attains_column_bound {E : Type*}
    [NormedAddCommGroup E] [NormedSpace ℝ E] {n : ℕ}
    (columns : Fin n → E) (pulseIndex : Fin n) (V : ℝ) (hV : 0 ≤ V) :
    (∑ i, |if i = pulseIndex then V else 0|) = V ∧
      ‖∑ i, (if i = pulseIndex then V else 0) • columns i‖ = V * ‖columns pulseIndex‖ := by
  constructor
  · have habs : ∀ i : Fin n, |if i = pulseIndex then V else 0| =
        (if i = pulseIndex then V else 0) := by
      intro i
      by_cases hi : i = pulseIndex
      · simp [hi, abs_of_nonneg hV]
      · simp [hi]
    simp_rw [habs]
    simp
  · simp [ite_smul, norm_smul, Real.norm_eq_abs, abs_of_nonneg hV]

def thirdTapVector (impact q delta : ℝ) : EuclideanSpace ℝ (Fin 3) :=
  EuclideanSpace.single 2 (-impact ^ 2 * q * delta ^ 2)

theorem euclidean_third_tap_norm (impact q delta : ℝ)
    (_hk : 0 ≤ impact) (hq : 0 ≤ q) :
    ‖thirdTapVector impact q delta‖ = impact ^ 2 * q * delta ^ 2 := by
  unfold thirdTapVector
  change ‖PiLp.single (β := fun _ : Fin 3 => ℝ) 2 (2 : Fin 3)
    (-impact ^ 2 * q * delta ^ 2)‖ = _
  rw [PiLp.norm_single, Real.norm_eq_abs]
  have hneg : -impact ^ 2 * q * delta ^ 2 = -(impact ^ 2 * q * delta ^ 2) := by ring
  rw [hneg, abs_neg, abs_of_nonneg (by positivity)]

theorem positive_pulse_third_tap_signal (A impact q delta : ℝ)
    (hA : 0 ≤ A) (hk : 0 ≤ impact) (hq : 0 ≤ q) :
    ‖A • thirdTapVector impact q delta‖ = A * impact ^ 2 * q * delta ^ 2 := by
  rw [norm_smul, Real.norm_eq_abs, abs_of_nonneg hA,
    euclidean_third_tap_norm impact q delta hk hq]
  ring

end
end CurrentMM
