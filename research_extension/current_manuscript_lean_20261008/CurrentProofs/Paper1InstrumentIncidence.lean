import Lean

/-!
Exact rational identities for the deterministic algebra of the instrument theorem.
These declarations do not formalize real analysis, the Gaussian observation model,
the optimizer's boundary conditions, or the statistical rate.
-/
namespace CurrentMM

def payoff (gain curvature q : Rat) : Rat :=
  gain * q - curvature * q * q / 2

theorem payoff_gap (gain curvature optimum q : Rat)
    (firstOrder : gain = curvature * optimum) :
    payoff gain curvature optimum - payoff gain curvature q =
      curvature * (q - optimum) * (q - optimum) / 2 := by
  unfold payoff
  rw [firstOrder]
  grind

theorem cross_multiplied_incidence (b friction ratio attenuation : Rat)
    (baseline : b = (b + friction) * ratio)
    (definitionOfAttenuation : attenuation = 1 - ratio) :
    (b + friction) * attenuation = friction := by
  rw [definitionOfAttenuation]
  grind

def geometricSum (x : Rat) : Nat → Rat
  | 0 => 0
  | n + 1 => 1 + x * geometricSum x n

theorem geometricTruncation (x : Rat) (n : Nat) :
    (1 - x) * geometricSum x n = 1 - x ^ n := by
  induction n with
  | zero => simp [geometricSum] <;> grind
  | succ n hypothesis =>
    rw [geometricSum, Rat.pow_succ]
    calc
      (1 - x) * (1 + x * geometricSum x n) =
          (1 - x) + x * ((1 - x) * geometricSum x n) := by grind
      _ = 1 - x ^ n * x := by rw [hypothesis]; grind

theorem quadratic_series_tail (intercept slope coefficient ratio r : Rat) (depth : Nat)
    (slopeRelation : slope = intercept * ratio) :
    (intercept - slope * r) * (coefficient * geometricSum (ratio * r) depth) =
      intercept * coefficient * (1 - (ratio * r) ^ depth) := by
  rw [slopeRelation]
  calc
    _ = (intercept * coefficient) * ((1 - ratio * r) * geometricSum (ratio * r) depth) := by
      grind
    _ = _ := by rw [geometricTruncation]

theorem kink_endpoint_gap
    (baseA baseB jump mass offset remainderA remainderB : Rat)
    (sameAffineContribution : baseA = baseB) :
    (baseB + jump * mass * offset + remainderB) - (baseA + remainderA) =
      jump * mass * offset + (remainderB - remainderA) := by
  rw [sameAffineContribution]
  grind

end CurrentMM
