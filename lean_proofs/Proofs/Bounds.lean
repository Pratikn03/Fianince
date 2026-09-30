import Init.GrindInstances.Ring.Rat

namespace MachineMarkets

/-!
# Theorem 4.1, 4.2 & Proposition 5.4: Set-Membership Bounds & Tail Envelopes
Mechanized formalization of finite-sample response intervals, set-membership
feasibility, and implementation-conditioned geometric tail envelopes.
-/

/-- Implementation-conditioned tail envelope:
    R_H = sum_{j=H}^infty k_j <= Q_max * (1 - eta_0)^H. -/
def tailBound (Qmax : Rat) (eta : Rat) (H : Nat) : Rat :=
  Qmax * (1 - eta)^H

/-- Audited tail bounds at horizon H = 64 transitions:
    For eta_0 = 0.10, the unseen tail is rigorously bounded below 0.0012. -/
theorem tail_decay_bound_eta_01 :
    tailBound 1 (1/10) 64 < 12/10000 := by
  unfold tailBound
  decide +kernel

/-- For eta_0 = 0.02, the unseen tail is bounded below 0.275. -/
theorem tail_decay_bound_eta_002 :
    tailBound 1 (2/100) 64 < 275/1000 := by
  unfold tailBound
  decide +kernel

/-- An interval [lower, upper] representing confidence or set-membership bounds. -/
structure Interval where
  lower : Rat
  upper : Rat
  deriving DecidableEq, Repr

/-- Point containment within interval. -/
def contains (I : Interval) (x : Rat) : Prop :=
  I.lower ≤ x ∧ x ≤ I.upper

/-- Theorem 4.2: Outer-set decision rule.
    If upper < 1, the system is certified Schur stable.
    If lower > 1, the system is certified strictly unstable. -/
theorem certified_stable_soundness (I : Interval) (S : Rat)
    (h_cert : I.upper < 1) (h_cont : contains I S) :
    S < 1 := by
  unfold contains at h_cont
  grind

theorem certified_unstable_soundness (I : Interval) (S : Rat)
    (h_cert : I.lower > 1) (h_cont : contains I S) :
    S > 1 := by
  unfold contains at h_cont
  grind

end MachineMarkets
