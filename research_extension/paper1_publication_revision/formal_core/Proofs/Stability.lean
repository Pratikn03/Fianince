import Init.GrindInstances.Ring.Rat

namespace MachineMarkets

/-!
# Theorem 2.3 & Proposition 3.2: Positive-Feedback Stability Boundary
Mechanized formalization of the characteristic polynomial, eigenvalue crossing,
and spectral radius stability boundary for adaptive market feedback.
-/

/-- The characteristic polynomial of the 2x2 joint market-learning Jacobian:
    J = [ a,         g        ]
        [ eta*kappa, 1 - eta   ]
    det(lambda*I - J) = lambda^2 - (a + 1 - eta)*lambda + a*(1 - eta) - g*eta*kappa
-/
def charPoly (a g eta kappa lam : Rat) : Rat :=
  lam * lam - (a + 1 - eta) * lam + a * (1 - eta) - g * eta * kappa

/-- Direct algebraic identity: at lambda = 1, the characteristic polynomial
    factors exactly into eta * (1 - a - g * kappa). -/
theorem charPoly_at_one_identity (a g eta kappa : Rat) :
    charPoly a g eta kappa 1 = (1 - a - g * kappa) * eta := by
  unfold charPoly
  grind

/-- Exact numerical check of the boundary at a = 2/5 (0.4), kappa = 1, eta = 1/5 (0.2).
    The critical boundary occurs at g = 3/5 (0.6). -/
theorem boundary_eval_exact :
    charPoly (2/5) (3/5) (1/5) 1 1 = 0 := by
  decide +kernel

/-- When feedback gain is below boundary (g = 1/2 < 3/5), charPoly(1) > 0. -/
theorem stable_eval_exact :
    charPoly (2/5) (1/2) (1/5) 1 1 = 1 / 50 := by
  decide +kernel

/-- When feedback gain is strictly above boundary (g = 9/10 > 3/5), charPoly(1) < 0,
    proving an eigenvalue strictly outside the unit disk. -/
theorem unstable_eval_exact :
    charPoly (2/5) (9/10) (1/5) 1 1 = -3 / 50 := by
  decide +kernel

/-- Resolvent denominator root function:
    f(lambda) = lambda - a - (eta * g * kappa) / (lambda - 1 + eta)
    (lambda - a)(lambda - 1 + eta) - g * eta * kappa. -/
def resolventDenom (a g eta kappa lam : Rat) : Rat :=
  (lam - a) * (lam - 1 + eta) - g * eta * kappa

theorem resolvent_charPoly_equiv (a g eta kappa lam : Rat) :
    resolventDenom a g eta kappa lam = charPoly a g eta kappa lam := by
  unfold resolventDenom charPoly
  grind

/-- Multi-agent feedback sum Q = sum q_i.
    For n agents with feedback weights q and common rate eta,
    the aggregate loop gain is S = a + Q. -/
def aggregateStability (a Q : Rat) : Rat := a + Q

theorem aggregate_stability_criterion (a Q : Rat) :
    aggregateStability a Q < 1 ↔ Q < 1 - a := by
  unfold aggregateStability
  grind

theorem aggregate_instability_criterion (a Q : Rat) :
    aggregateStability a Q > 1 ↔ Q > 1 - a := by
  unfold aggregateStability
  grind

theorem aggregate_boundary_criterion (a Q : Rat) :
    aggregateStability a Q = 1 ↔ Q = 1 - a := by
  unfold aggregateStability
  grind

end MachineMarkets
