import Init.GrindInstances.Ring.Rat

namespace MachineMarkets

/-!
# Fleeting Liquidity and Adversarial Cancellation Theorem
Formalizes the impact of high-frequency quote cancellation (rate χ ∈ [0, 1)) on observable feedback.
Proves that adversarial quote cancellations strictly attenuate apparent feedback S_obs = (1 - χ) * S_true,
inducing an apparent S_obs ≈ 0 even when underlying intent S_true is critically unstable.
-/

/-- Apparent feedback under cancellation fraction chi -/
def apparentFeedback (s_true chi : Rat) : Rat :=
  (1 - chi) * s_true

/-- Theorem: Cancellation attenuation identity -/
theorem cancellation_attenuation_identity (s_true chi : Rat) :
    apparentFeedback s_true chi = s_true - chi * s_true := by
  unfold apparentFeedback
  grind

/-- Theorem: When cancellation rate exceeds 95% (chi = 19/20),
    an explosive feedback system (S_true = 3/2 > 1) registers as structurally stable (S_apparent = 3/40 < 1/10). -/
theorem cancellation_masking_proof :
    let chi : Rat := 19/20
    let s_true : Rat := 3/2
    apparentFeedback s_true chi < 1/10 := by
  decide +kernel

/-- Cancellation-adjusted Jacobian characteristic polynomial -/
def cancellationCharPoly (a g eta kappa chi lam : Rat) : Rat :=
  lam * lam - (a + 1 - eta) * lam + (a * (1 - eta) - g * (1 - chi) * eta * kappa)

/-- Theorem: Exact root factorization of cancellation Jacobian at λ = 1 -/
theorem cancellation_boundary_at_one (a g eta kappa chi : Rat) :
    cancellationCharPoly a g eta kappa chi 1 = (1 - a - g * (1 - chi) * kappa) * eta := by
  unfold cancellationCharPoly
  grind

/-- Effective feedback persistence under cancellation fraction chi -/
def effectiveS (a g kappa chi : Rat) : Rat :=
  a + (1 - chi) * g * kappa

/-- Critical cancellation rate that brings an unstable system (a + g*kappa > 1) to the boundary S = 1 -/
def criticalChi (a g kappa : Rat) : Rat :=
  1 - (1 - a) / (g * kappa)

theorem critical_cancellation_brings_to_boundary (a g kappa : Rat) (h : g * kappa ≠ 0) :
    effectiveS a g kappa (criticalChi a g kappa) = 1 := by
  unfold effectiveS criticalChi
  grind

end MachineMarkets
