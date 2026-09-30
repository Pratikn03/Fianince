import Proofs.Stability
import Proofs.PBHDefect
import Proofs.Ambiguity
import Proofs.Bounds

namespace MachineMarkets

/-!
# Master Formal Proof Suite for Machine Markets
Consolidates all mechanized Lean 4 proofs for the manuscript:
1. Stability: Theorem 2.3 & Proposition 3.2 (Characteristic polynomial and positive-feedback boundary)
2. PBHDefect: Proposition 5.1 & Theorem 5.2 (PBH unobservable defect and swapped-feedback invariance)
3. Ambiguity: Theorem 3.3 (Exact finite-window ambiguity witness matching through lag 3, diverging at lag 4)
4. Bounds: Theorems 4.1, 4.2 & Proposition 5.4 (Set-membership bounds, decision soundness, and geometric tail envelopes)
-/

/-- Comprehensive consistency check: ensure all submodules elaborate and evaluate cleanly. -/
theorem master_verification_consistency :
    (3/10 : Rat) + 1/10 = 2/5 ∧
    tailBound 1 (1/10) 64 < 12/10000 ∧
    charPoly (2/5) (3/5) (1/5) 1 1 = 0 ∧
    k0_mod0 = k0_mod1 := by
  refine ⟨by decide +kernel, tail_decay_bound_eta_01, boundary_eval_exact, kernel_lag0_identical.1⟩

end MachineMarkets
