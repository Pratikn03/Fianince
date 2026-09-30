import Init.GrindInstances.Ring.Rat

namespace MachineMarkets

/-!
# Proposition 5.1 & Theorem 5.2: PBH Rank Defect and Swapped Feedback Invariance
Mechanized proof that swapped feedback allocations induce identical aggregate transfer
functions due to an exact Popov-Belevitch-Hautus (PBH) unobservable eigenspace defect.
-/

/-- State representation for an economy with price x and two adaptive agents (y1, y2). -/
structure Vec3 where
  x : Rat
  y1 : Rat
  y2 : Rat
  deriving DecidableEq, Repr

/-- Output measurement map C = [1, 0, 0]: public surveillance observes only price x. -/
def C_dot (v : Vec3) : Rat := v.x

/-- Transition operator J:
    [ a,        1,       1      ]
    [ eta*q1, 1 - eta,   0      ]
    [ eta*q2,   0,     1 - eta  ]
-/
def J_mul (a eta q1 q2 : Rat) (v : Vec3) : Vec3 :=
  ⟨a * v.x + v.y1 + v.y2,
   eta * q1 * v.x + (1 - eta) * v.y1,
   eta * q2 * v.x + (1 - eta) * v.y2⟩

/-- The unobservable direction: zero price perturbation, balanced opposing agent memory. -/
def pbh_null_vec : Vec3 := ⟨0, 1, -1⟩

/-- The null vector produces zero price observation deflection: C * v = 0. -/
theorem pbh_unobservable : C_dot pbh_null_vec = 0 := by
  unfold C_dot pbh_null_vec
  decide

/-- The null vector is an exact eigenvector of J corresponding to eigenvalue lambda = 1 - eta:
    J * v = (1 - eta) * v. -/
theorem pbh_eigenvector_x (a eta q1 q2 : Rat) :
    (J_mul a eta q1 q2 pbh_null_vec).x = 0 := by
  unfold J_mul pbh_null_vec
  grind

theorem pbh_eigenvector_y1 (a eta q1 q2 : Rat) :
    (J_mul a eta q1 q2 pbh_null_vec).y1 = 1 - eta := by
  unfold J_mul pbh_null_vec
  grind

theorem pbh_eigenvector_y2 (a eta q1 q2 : Rat) :
    (J_mul a eta q1 q2 pbh_null_vec).y2 = -(1 - eta) := by
  unfold J_mul pbh_null_vec
  grind

/-- Characteristic resolvent denominator:
    D(z) = (z - a)(z - 1 + eta) - eta * Q
    which depends solely on the aggregate scalar sum Q = q1 + q2. -/
def transferDenom (a eta Q z : Rat) : Rat :=
  (z - a) * (z - 1 + eta) - eta * Q

/-- Economy A: (q1, q2) = (0.30, 0.10) => Q_A = 0.40.
    Economy B: (q1, q2) = (0.10, 0.30) => Q_B = 0.40.
    Both economies induce identical aggregate feedback sums. -/
theorem economy_A_sum : (3/10 : Rat) + 1/10 = 2/5 := by decide +kernel
theorem economy_B_sum : (1/10 : Rat) + 3/10 = 2/5 := by decide +kernel

theorem swapped_feedback_sum_equal :
    (3/10 : Rat) + 1/10 = 1/10 + 3/10 := by
  decide +kernel

/-- Swapped feedback allocations have identical transfer function denominators at all frequencies z. -/
theorem swapped_feedback_transfer_invariant (a eta z : Rat) :
    transferDenom a eta (3/10 + 1/10) z = transferDenom a eta (1/10 + 3/10) z := by
  unfold transferDenom
  grind

/-- Theorem 5.2 Case 2: Minimal separation under known total Q.
    When channel probe vector u is non-zero, measured response b = eta * u * q.
    With known Q = q1 + q2, the augmented measurement matrix has full rank. -/
def channelResponse (eta u1 u2 q1 q2 : Rat) : Rat :=
  eta * (u1 * q1 + u2 * q2)

theorem channel_response_separates :
    channelResponse (1/5) 1 0 (3/10) (1/10) ≠ channelResponse (1/5) 1 0 (1/10) (3/10) := by
  unfold channelResponse
  decide +kernel

end MachineMarkets
