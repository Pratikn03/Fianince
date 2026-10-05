import Proofs.Stability
import Proofs.PBHDefect
import Proofs.Ambiguity
import Proofs.Bounds
import Proofs.SignedStability
import Proofs.CancellationJacobian
import Proofs.Microfoundations
import Proofs.InformationBounds
import Proofs.AgenticGuard
import Proofs.Frontiers

namespace MachineMarkets

/-!
# Master Formal Proof Suite for Machine Markets
Consolidates all mechanized Lean 4 proofs for the manuscript:
1. Stability: Theorem 2.3 & Proposition 3.2 (Characteristic polynomial and positive-feedback boundary)
2. PBHDefect: Proposition 5.1 & Theorem 5.2 (PBH unobservable defect and swapped-feedback invariance)
3. Ambiguity: Theorem 3.3 (Exact finite-window ambiguity witness matching through lag 3, diverging at lag 4)
4. Bounds: Theorems 4.1, 4.2 & Proposition 5.4 (Set-membership bounds, decision soundness, and geometric tail envelopes)
5. SignedStability: Theorem 2.4 (Generalized Schur-Cohn stability for signed momentum and contrarian feedback)
6. CancellationJacobian: Proposition 8.2 (Fleeting liquidity attenuation and adversarial quote cancellation masking)
7. Microfoundations: Propositions 2.1, 2.2, 2.5, 8.1 (Kalman AR(1), OGD linearization, Volatility-amplification wedge, DC flow gain)
8. InformationBounds: Theorems M2, M3, M4, M5, OLS orthogonality, Bonferroni coverage, small-gain robustness, and LP weak duality
9. AgenticGuard: AMIP RFC-001 Zero-Trust Interceptor, semantic filters, Kreiss solvency bounds, and mandatory abstention
-/

/-- Comprehensive consistency check: ensure all submodules elaborate and evaluate cleanly. -/
theorem master_verification_consistency :
    (3/10 : Rat) + 1/10 = 2/5 ∧
    tailBound 1 (1/10) 64 < 12/10000 ∧
    charPoly (2/5) (3/5) (1/5) 1 1 = 0 ∧
    signedCharPoly contrarian_example_a contrarian_example_g contrarian_example_eta contrarian_example_kappa 1 > 0 ∧
    apparentFeedback (3/2) (19/20) < 1/10 ∧
    k0_mod0 = k0_mod1 ∧
    ogdEffectiveRate (5/100) (1/100) 15 = 1/5 ∧
    stationaryVariance (9/10) (1/5) < stationaryVariance (1/2) 1 ∧
    responseSum (9/10) > responseSum (1/2) ∧
    nonnormalOneStepEnergy 10 > 100 ∧
    1 - 2 * (5/100 : Rat) = 9/10 ∧
    kreissSafeRadius 3000000 (342/100) 17180 > 51 := by
  refine ⟨by decide +kernel, tail_decay_bound_eta_01, boundary_eval_exact,
          contrarian_example_P_one_positive, cancellation_masking_proof, kernel_lag0_identical.1,
          ogd_effective_rate_bounds.1, volatility_amplification_wedge.1, volatility_amplification_wedge.2,
          nonnormal_transient_growth_m10, finite_window_abstention_at_nominal_alpha,
          by decide +kernel⟩

end MachineMarkets
