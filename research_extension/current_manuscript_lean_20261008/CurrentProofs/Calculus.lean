import CurrentProofs.Microfoundations
import CurrentProofs.CohortAlgebra
import Mathlib.Analysis.Calculus.Deriv.Pow
import Mathlib.Analysis.SpecialFunctions.Integrals.Basic

namespace CurrentMM
noncomputable section
open MeasureTheory

def quadraticPredictionLoss (curvature observation theta : ℝ) : ℝ :=
  curvature / 2 * (observation - theta) ^ 2

theorem prediction_loss_derivative (curvature observation theta : ℝ) :
    HasDerivAt (quadraticPredictionLoss curvature observation)
      (curvature * (theta - observation)) theta := by
  have hd := (((hasDerivAt_id theta).const_sub observation).pow 2).const_mul (curvature / 2)
  convert hd using 1
  · rfl
  · dsimp only [id_eq]
    ring

theorem actual_quadratic_ogd_update (theta observation gamma alpha curvature : ℝ)
    (hrate : gamma + alpha * curvature ≠ 0) :
    (1 - gamma) * theta - alpha * deriv (quadraticPredictionLoss curvature observation) theta =
      (1 - (gamma + alpha * curvature)) * theta +
        (gamma + alpha * curvature) *
          (alpha * curvature / (gamma + alpha * curvature)) * observation := by
  rw [(prediction_loss_derivative curvature observation theta).deriv]
  convert ogd_normalized_recursion theta observation gamma alpha curvature hrate using 1
  ring

theorem normalized_ogd_gain_unit_interval (gamma alpha curvature : ℝ)
    (hg : 0 < gamma) (ha : 0 < alpha) (hh : 0 < curvature) :
    0 < alpha * curvature / (gamma + alpha * curvature) ∧
      alpha * curvature / (gamma + alpha * curvature) < 1 := by
  constructor
  · positivity
  · exact (div_lt_one (by positivity)).2 (by linarith)

theorem willingness_to_pay_integral (V0 b cost L U : ℝ) :
    (∫ V in L..U, ((V0 - V) / b - cost)) =
      allocationSurplusPrimitive V0 b cost U - allocationSurplusPrimitive V0 b cost L := by
  have hi : IntervalIntegrable (fun V : ℝ => (V0 - V) / b) volume L U :=
    (continuous_const.sub continuous_id).div_const b |>.intervalIntegrable L U
  have hlin : (fun V : ℝ => (V0 - V) / b) =
      (fun V : ℝ => V0 / b - V / b) := by
    funext V
    ring
  have hidiv : IntervalIntegrable (fun V : ℝ => V / b) volume L U := by
    simpa only [id_eq] using (continuous_id.div_const b).intervalIntegrable L U
  rw [intervalIntegral.integral_sub hi intervalIntegrable_const, hlin,
    intervalIntegral.integral_sub (f := fun _ : ℝ => V0 / b)
      (g := fun V : ℝ => V / b) intervalIntegrable_const hidiv]
  simp_rw [intervalIntegral.integral_div]
  rw [integral_id, intervalIntegral.integral_const, intervalIntegral.integral_const]
  simp only [smul_eq_mul]
  unfold allocationSurplusPrimitive
  ring

theorem allocation_loss_from_actual_integral (V0 b cost s0 delta : ℝ) (hb : b ≠ 0) :
    (∫ V in (V0 - b * (s0 + delta))..(V0 - b * s0), ((V0 - V) / b - cost)) =
      b * (s0 - cost) * delta + b * delta ^ 2 / 2 := by
  rw [willingness_to_pay_integral]
  exact allocation_loss_formula V0 b cost s0 delta hb

end
end CurrentMM
