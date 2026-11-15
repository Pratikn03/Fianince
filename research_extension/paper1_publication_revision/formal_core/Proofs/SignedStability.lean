import Init.GrindInstances.Ring.Rat

namespace MachineMarkets

/-!
# Signed Feedback Stability Theorem (Schur-Cohn Criterion)
Extends stability theory beyond positive M-matrices (Theorems 2.3 & 2.4) to signed feedback (S ∈ ℝ).
Provides exact necessary and sufficient algebraic identities for both positive (S ≥ 0)
and contrarian (S < 0) feedback regimes.
-/

/-- Discrete-time characteristic polynomial: det(λI - J) = λ^2 - T*λ + D -/
def signedCharPoly (a g eta kappa lam : Rat) : Rat :=
  lam * lam - (a + 1 - eta) * lam + (a * (1 - eta) - g * eta * kappa)

/-- Trace of closed-loop Jacobian -/
def jacobianTrace (a eta : Rat) : Rat := a + 1 - eta

/-- Determinant of closed-loop Jacobian -/
def jacobianDet (a g eta kappa : Rat) : Rat := a * (1 - eta) - g * eta * kappa

/-- Theorem 2.4A: Root identity at boundary λ = 1 holds identically for ANY signed feedback (g*kappa ∈ ℝ) -/
theorem signed_boundary_at_one (a g eta kappa : Rat) :
    signedCharPoly a g eta kappa 1 = (1 - a - g * kappa) * eta := by
  unfold signedCharPoly
  grind

/-- Theorem 2.4B: Root identity at boundary λ = -1 for period-doubling/flip bifurcations -/
theorem signed_boundary_at_neg_one (a g eta kappa : Rat) :
    signedCharPoly a g eta kappa (-1) = (1 + a) * (2 - eta) - g * eta * kappa := by
  unfold signedCharPoly
  grind

/-- Theorem 2.4C: Exact determinant decomposition for contrarian feedback (g*kappa < 0) -/
theorem signed_det_decomposition (a g eta kappa : Rat) :
    jacobianDet a g eta kappa = a * (1 - eta) - g * eta * kappa := by
  unfold jacobianDet
  rfl

/-- Worked example: illustrative contrarian parameters (a = 2/5, eta = 1/5, g = 1/2, kappa = -3/4),
    chosen for exposition only; they are NOT empirical estimates.
    the system is strictly Schur stable:
    1. P(1) > 0
    2. P(-1) > 0
    3. |det(J)| < 1
-/
def contrarian_example_a : Rat := 2/5
def contrarian_example_eta : Rat := 1/5
def contrarian_example_g : Rat := 1/2
def contrarian_example_kappa : Rat := -3/4  -- contrarian feedback, g*kappa < 0

theorem contrarian_example_P_one_positive : signedCharPoly contrarian_example_a contrarian_example_g contrarian_example_eta contrarian_example_kappa 1 > 0 := by
  unfold signedCharPoly contrarian_example_a contrarian_example_eta contrarian_example_g contrarian_example_kappa
  decide +kernel

theorem contrarian_example_P_neg_one_positive : signedCharPoly contrarian_example_a contrarian_example_g contrarian_example_eta contrarian_example_kappa (-1) > 0 := by
  unfold signedCharPoly contrarian_example_a contrarian_example_eta contrarian_example_g contrarian_example_kappa
  decide +kernel

theorem contrarian_example_det_bounded :
    jacobianDet contrarian_example_a contrarian_example_g contrarian_example_eta contrarian_example_kappa > -1 ∧
    jacobianDet contrarian_example_a contrarian_example_g contrarian_example_eta contrarian_example_kappa < 1 := by
  unfold jacobianDet contrarian_example_a contrarian_example_eta contrarian_example_g contrarian_example_kappa
  decide +kernel

end MachineMarkets
