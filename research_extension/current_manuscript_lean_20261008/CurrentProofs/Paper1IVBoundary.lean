import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Algebra.Module.Basic
import Mathlib.Tactic.Module
import Mathlib.Data.Real.Basic

/-!
# Paper 1, Proposition `prop:tagged`, step I3: the exact boundary decomposition of the IV score

With reported-flow error `e_t = ε_t - r ε_{t-1}`, the IV score `∑_{t=1}^T Z_t e_t` is a sum of terms with fixed
coefficients on the reporting errors plus two boundary terms:

`∑_{t=1}^T Z_t e_t = ∑_{t=1}^T (Z_t - r Z_{t+1}) ε_t + r Z_{T+1} ε_T - r Z_1 ε_0`.

This is pure algebra, valid for vector-valued instruments in any real module. The limit theorems of the proposition
(the boundary over `√T` tends to zero in probability; the conditional central limit theorem) are not covered here.
-/

namespace CurrentMM

open Finset

theorem p1_iv_boundary_decomposition {E : Type*} [AddCommGroup E] [Module ℝ E] (Z : ℕ → E) (ε : ℕ → ℝ)
    (r : ℝ) (T : ℕ) :
    ∑ t ∈ Ico 1 (T + 1), (ε t - r * ε (t - 1)) • Z t =
      ∑ t ∈ Ico 1 (T + 1), ε t • (Z t - r • Z (t + 1)) + (r * ε T) • Z (T + 1) - (r * ε 0) • Z 1 := by
  induction T with
  | zero => simp
  | succ T ih =>
      rw [sum_Ico_succ_top (by omega : 1 ≤ T + 1), sum_Ico_succ_top (by omega : 1 ≤ T + 1), ih]
      simp only [Nat.add_sub_cancel]
      module

end CurrentMM
