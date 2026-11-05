import Mathlib

/-! Scalar robustness of a declared supervisory threshold.
These lemmas do not formalize an equilibrium, probability law, acquisition
optimum, or the manuscript's complete identification theorem.
-/
namespace SupervisoryRelease

theorem robust_threshold_separation
    (rA rB threshold movedA movedB radius : ℝ)
    (hA : rA + radius ≤ threshold)
    (hB : threshold < rB - radius)
    (hMoveA : |movedA - rA| ≤ radius)
    (hMoveB : |movedB - rB| ≤ radius) :
    movedA ≤ threshold ∧ threshold < movedB := by
  have hUpper := (abs_le.mp hMoveA).2
  have hLower := (abs_le.mp hMoveB).1
  constructor <;> linarith

theorem robust_window_nonempty (rA rB radius : ℝ)
    (hGap : 2 * radius < rB - rA) :
    rA + radius < rB - radius := by
  linarith

theorem bounded_adjustment_keeps_gap
    (rA rB movedA movedB radius : ℝ)
    (hMoveA : |movedA - rA| ≤ radius)
    (hMoveB : |movedB - rB| ≤ radius) :
    rB - rA - 2 * radius ≤ movedB - movedA := by
  have hUpper := (abs_le.mp hMoveA).2
  have hLower := (abs_le.mp hMoveB).1
  linarith

end SupervisoryRelease
