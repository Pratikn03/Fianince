import CurrentProofs.Accounts

namespace CurrentMM

noncomputable section

def trackingPriorVariance (Q R : ℝ) : ℝ :=
  (Q + Real.sqrt (Q ^ 2 + 4 * Q * R)) / 2

theorem tracking_prior_variance_pos (Q R : ℝ) (hQ : 0 < Q) (hR : 0 < R) :
    0 < trackingPriorVariance Q R := by
  unfold trackingPriorVariance
  positivity

theorem tracking_prior_variance_quadratic (Q R : ℝ) (hQ : 0 < Q) (hR : 0 < R) :
    trackingPriorVariance Q R ^ 2 - Q * trackingPriorVariance Q R - Q * R = 0 := by
  have hD : 0 ≤ Q ^ 2 + 4 * Q * R := by positivity
  have hs := Real.sq_sqrt hD
  unfold trackingPriorVariance
  nlinarith

theorem tracking_prior_variance_unique_positive (Q R P : ℝ)
    (hQ : 0 < Q) (hR : 0 < R) (hP : 0 < P)
    (hpoly : P ^ 2 - Q * P - Q * R = 0) :
    P = trackingPriorVariance Q R := by
  have hc := tracking_prior_variance_quadratic Q R hQ hR
  have hcp := tracking_prior_variance_pos Q R hQ hR
  have hQr : Q < trackingPriorVariance Q R := by nlinarith
  have hfactor : (P - trackingPriorVariance Q R) *
      (P + trackingPriorVariance Q R - Q) = 0 := by nlinarith
  rcases mul_eq_zero.mp hfactor with h | h
  · linarith
  · linarith

def trackingGain (Q R : ℝ) : ℝ :=
  trackingPriorVariance Q R / (trackingPriorVariance Q R + R)

theorem tracking_gain_unit_interval (Q R : ℝ) (hQ : 0 < Q) (hR : 0 < R) :
    0 < trackingGain Q R ∧ trackingGain Q R < 1 := by
  have hP := tracking_prior_variance_pos Q R hQ hR
  unfold trackingGain
  constructor
  · positivity
  · exact (div_lt_one (by positivity)).2 (by linarith)

theorem tracking_prior_riccati_equation (Q R : ℝ) (hQ : 0 < Q) (hR : 0 < R) :
    trackingPriorVariance Q R = trackingPriorVariance Q R -
      trackingPriorVariance Q R ^ 2 / (trackingPriorVariance Q R + R) + Q := by
  have hP := tracking_prior_variance_pos Q R hQ hR
  have hc := tracking_prior_variance_quadratic Q R hQ hR
  have hd : trackingPriorVariance Q R + R ≠ 0 := by positivity
  field_simp
  nlinarith

def emaUpdate (alpha oldAnchor price : ℝ) : ℝ :=
  (1 - alpha) * oldAnchor + alpha * price

theorem tracking_gain_explicit_root (Q R : ℝ) (hQ : 0 < Q) (hR : 0 < R) :
    trackingGain Q R = (-Q + Real.sqrt (Q ^ 2 + 4 * Q * R)) / (2 * R) := by
  have hP := tracking_prior_variance_pos Q R hQ hR
  have hc := tracking_prior_variance_quadratic Q R hQ hR
  have hquot : trackingGain Q R = (trackingPriorVariance Q R - Q) / R := by
    unfold trackingGain
    apply (div_eq_div_iff (by positivity) (ne_of_gt hR)).2
    nlinarith
  rw [hquot]
  unfold trackingPriorVariance
  ring

theorem ema_deviation_identity (alpha oldAnchor price : ℝ) :
    price - emaUpdate alpha oldAnchor price = (1 - alpha) * (price - oldAnchor) := by
  unfold emaUpdate
  ring

theorem ema_next_deviation_identity (alpha price oldAnchor increment : ℝ) :
    (price + increment) - emaUpdate alpha oldAnchor (price + increment) =
      (1 - alpha) * ((price - oldAnchor) + increment) := by
  unfold emaUpdate
  ring

def allocationSurplusPrimitive (V0 b cost V : ℝ) : ℝ :=
  (V0 / b - cost) * V - V ^ 2 / (2 * b)

theorem allocation_loss_formula (V0 b cost s0 delta : ℝ) (hb : b ≠ 0) :
    allocationSurplusPrimitive V0 b cost (V0 - b * s0) -
      allocationSurplusPrimitive V0 b cost (V0 - b * (s0 + delta)) =
      b * (s0 - cost) * delta + b * delta ^ 2 / 2 := by
  unfold allocationSurplusPrimitive
  field_simp <;> ring

theorem allocation_triangle_requires_efficient_baseline (V0 b cost delta : ℝ) (hb : b ≠ 0) :
    allocationSurplusPrimitive V0 b cost (V0 - b * cost) -
      allocationSurplusPrimitive V0 b cost (V0 - b * (cost + delta)) =
      b * delta ^ 2 / 2 := by
  rw [allocation_loss_formula V0 b cost cost delta hb]
  ring

end
end CurrentMM
