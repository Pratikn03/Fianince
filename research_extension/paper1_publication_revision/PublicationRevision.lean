import Mathlib

/-!
Deterministic proof components for the revised Paper 1.
The Gaussian likelihood, Pinsker theorem, Gaussian concentration, and
same-realization AR risk expansion are NOT formalized by this file.
-/
namespace Paper1Revision

open Finset

/-- Matched moments cancel every polynomial of the specified degree. -/
theorem matched_polynomial {K n : ℕ} (w v x y : Fin K → ℝ)
    (c : Fin n → ℝ)
    (hm : ∀ j : Fin n, ∑ i, w i * x i ^ (j : ℕ) = ∑ i, v i * y i ^ (j : ℕ)) :
    ∑ i, w i * (∑ j, c j * x i ^ (j : ℕ)) =
    ∑ i, v i * (∑ j, c j * y i ^ (j : ℕ)) := by
  have expand (u z : Fin K → ℝ) :
      ∑ i, u i * (∑ j, c j * z i ^ (j : ℕ)) =
      ∑ j, c j * (∑ i, u i * z i ^ (j : ℕ)) := by
    simp_rw [Finset.mul_sum]
    rw [Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro j _
    apply Finset.sum_congr rfl
    intro i _
    ring
  rw [expand w x, expand v y]
  simp_rw [hm]

/-- A positive weighted remainder with mass W has absolute size at most W E. -/
theorem remainder_bound {K : ℕ} (w e : Fin K → ℝ) (W E : ℝ)
    (hw : ∀ i, 0 ≤ w i) (hm : ∑ i, w i = W) (he : ∀ i, |e i| ≤ E) :
    |∑ i, w i * e i| ≤ W * E := by
  calc
    |∑ i, w i * e i| ≤ ∑ i, |w i * e i| := Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ i, w i * E := Finset.sum_le_sum fun i _ => by
      rw [abs_mul, abs_of_nonneg (hw i)]
      exact mul_le_mul_of_nonneg_left (he i) (hw i)
    _ = W * E := by rw [← Finset.sum_mul, hm]

/-- Polynomial cancellation leaves at most two positive-mass remainder bounds. -/
theorem flow_gap {K : ℕ} (w v p q e f : Fin K → ℝ) (W E : ℝ)
    (hw : ∀ i, 0 ≤ w i) (hv : ∀ i, 0 ≤ v i)
    (hmw : ∑ i, w i = W) (hmv : ∑ i, v i = W)
    (hp : ∑ i, w i * p i = ∑ i, v i * q i)
    (he : ∀ i, |e i| ≤ E) (hf : ∀ i, |f i| ≤ E) :
    |(∑ i, w i * (p i + e i)) - (∑ i, v i * (q i + f i))| ≤ 2 * W * E := by
  have h1 := remainder_bound w e W E hw hmw he
  have h2 := remainder_bound v f W E hv hmv hf
  have hcancel : (∑ i, w i * (p i + e i)) - (∑ i, v i * (q i + f i)) =
      (∑ i, w i * e i) - (∑ i, v i * f i) := by
    simp_rw [mul_add, Finset.sum_add_distrib]
    linarith [hp]
  rw [hcancel]
  have htri := abs_sub (∑ i, w i * e i) (∑ i, v i * f i)
  linarith

/-- Approximate least-distance fitting controls the distance between fitted and true means. -/
theorem minimum_distance_error {E : Type*} [PseudoMetricSpace E]
    (truth fitted observed : E) (tol : ℝ)
    (hfit : dist fitted observed ≤ dist truth observed + tol) :
    dist fitted truth ≤ 2 * dist observed truth + tol := by
  have h := dist_triangle fitted observed truth
  rw [dist_comm truth observed] at hfit
  linarith

/-- Different initial group states leave an exponentially decaying residual. -/
theorem initial_state_residual (u v x : ℕ → ℝ) (r eta : ℝ)
    (hu : ∀ t, u (t+1) = r*u t + eta*x t)
    (hv : ∀ t, v (t+1) = r*v t + eta*x t) (t : ℕ) :
    u t-v t = r^t*(u 0-v 0) := by
  induction t with
  | zero => simp
  | succ t ih =>
    rw [hu, hv, pow_succ]
    calc
      r*u t+eta*x t-(r*v t+eta*x t) = r*(u t-v t) := by ring
      _ = r*(r^t*(u 0-v 0)) := by rw [ih]
      _ = r^t*r*(u 0-v 0) := by ring

/-- Binary decision loss given the total-variation testing inequality. -/
theorem decision_loss (b c e0 e1 tv : ℝ)
    (hb : 0 ≤ b) (hc : 0 ≤ c) (h0 : 0 ≤ e0) (h1 : 0 ≤ e1)
    (htest : 1-tv ≤ e0+e1) :
    min b c * (1-tv)/2 ≤ (b*e0+c*e1)/2 := by
  have hm : 0 ≤ min b c := le_min hb hc
  have hsum := mul_le_mul_of_nonneg_left htest hm
  have hleft := mul_le_mul_of_nonneg_right (min_le_left b c) h0
  have hright := mul_le_mul_of_nonneg_right (min_le_right b c) h1
  nlinarith

/-- A final independent equal-variance report can halve the variance. -/
theorem final_tag_precision (variance : ℝ) (h : 0 < variance) :
    (variance + variance)/4 < variance := by linarith

/-- The two limiting post-halt budgets have a strictly positive decision margin. -/
theorem limiting_decision_separation (a k W r : ℝ)
    (hk : 0 < k) (hW : 0 < W) (hr : r < 1) :
    a+k*W/(4*(1-r)) < a+3*k*W/(8*(1-r)) ∧
    a+3*k*W/(8*(1-r)) < a+k*W/(2*(1-r)) := by
  have hd : 0 < 1-r := by linarith
  have hp : 0 < k*W/(8*(1-r)) := div_pos (mul_pos hk hW) (by positivity)
  constructor <;> field_simp <;> nlinarith [mul_pos hk hW]

/-- Exact squared-error mismatch underlying the conditional Gaussian KL identity. -/
theorem forecast_mismatch_identity (y m0 m1 : ℝ) :
    (y-m1)^2-(y-m0)^2 = 2*(y-m0)*(m0-m1)+(m0-m1)^2 := by ring

/-- A one-order-smaller remainder preserves half the inverse-map lower bound. -/
theorem inverse_remainder_absorption (a b d z response : ℝ) (n : ℕ)
    (hd : 0 ≤ d) (hz : 0 ≤ z) (hsmall : b*d ≤ a/2)
    (hresponse : (a-b*d)*d^n*z ≤ response) :
    (a/2)*d^n*z ≤ response := by
  have hco : a/2 ≤ a-b*d := by linarith
  have hnonneg : 0 ≤ d^n*z := mul_nonneg (pow_nonneg hd n) hz
  calc
    (a/2)*d^n*z = (a/2)*(d^n*z) := by ring
    _ ≤ (a-b*d)*(d^n*z) := mul_le_mul_of_nonneg_right hco hnonneg
    _ = (a-b*d)*d^n*z := by ring
    _ ≤ response := hresponse

end Paper1Revision

#print axioms Paper1Revision.matched_polynomial
#print axioms Paper1Revision.remainder_bound
#print axioms Paper1Revision.flow_gap
#print axioms Paper1Revision.minimum_distance_error
#print axioms Paper1Revision.initial_state_residual
#print axioms Paper1Revision.decision_loss
#print axioms Paper1Revision.final_tag_precision
#print axioms Paper1Revision.limiting_decision_separation
#print axioms Paper1Revision.forecast_mismatch_identity
#print axioms Paper1Revision.inverse_remainder_absorption
