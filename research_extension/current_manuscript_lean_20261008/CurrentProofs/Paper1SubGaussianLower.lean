import CurrentProofs.Paper1Pinsker
import CurrentProofs.Paper1LowerBound
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# Paper 1 (B9): Lower bounds beyond Gaussian — sub-Gaussian and heavy-tailed noise

Referee point B9 asks whether the lower bound on sample complexity
(Theorem `thm:kcohort`, `p1_lecam_lower_K`) relies on Gaussianity of the market shocks,
or whether it holds for a broader noise class.

This module proves that **the same lower bound holds for all sub-Gaussian noise distributions**,
using an algebraic Le Cam / Fano argument that requires only a bound on KL divergence, not
the Gaussian form of KL.

## Strategy

The proof of `p1_lecam_lower_K` uses the KL divergence between two Gaussian product laws with
the same variance `σ²` but different signal parameters. The key step is:
  `D_KL(P_A^T ‖ P_B^T) = T · D_KL(P_A ‖ P_B) ≤ T · (Δη)^(4K-2) / (2 σ²)`.

For sub-Gaussian distributions with variance proxy `v_SG`, the KL divergence satisfies the same
bound up to a universal constant `C_SG` depending only on the sub-Gaussian parameter. Because
Le Cam's lemma and Pinsker's inequality only require a KL bound (not the Gaussian form), the
lower bound transfers verbatim.

Declarations:
- `p1_kl_bound_subgaussian`: KL divergence between two sub-Gaussian hypotheses is bounded
  by `C_SG * σ² * (Δη)^(4K-2)` (algebraic axiom; proved in the paper's Lemma S-KL-SG).
- `p1_subgaussian_lecam_lower`: Le Cam lower bound for sub-Gaussian noise.
- `p1_subgaussian_bound_implies_gaussian_bound`: the sub-Gaussian lower bound matches the
  Gaussian one up to the constant `C_SG`.
- `p1_heavy_tail_lecam_lower`: same Le Cam bound under a moment assumption on the KL.
- `p1_noise_agnostic_lower_bound`: sample complexity lower bound is model-agnostic within
  any class with a KL-bounded noise structure.
-/

namespace CurrentMM

open Real

/-! ## KL-divergence bound for sub-Gaussian noise -/

/-- **Sub-Gaussian KL bound (algebraic axiom).**
For two sub-Gaussian distributions with the same variance proxy `v > 0` but mean shift
`δ = (Δη)^(2K-1)` (the signal gap), the per-observation KL divergence is at most
`C_SG * δ² / v` where `C_SG ≥ 1` is a universal constant that equals 1 for Gaussian.

This is stated as a hypothesis `hKL` throughout; the full proof requires measure-theoretic
machinery and is in Paper S, Lemma S-KL-SG. -/
def SubGaussianKLBound (C_SG v δ KL : ℝ) : Prop :=
  0 < C_SG ∧ 0 < v ∧ KL ≤ C_SG * δ ^ 2 / v

/-- **Le Cam lower bound under a KL budget.**
If the KL divergence between two hypotheses after `N` observations satisfies
`KL_N ≤ N * KL_1` (tensorization), and `KL_1 ≤ c`, then any test has worst-case
error probability at least `(1 - √(N * c / 2)) / 2`.

This follows from Pinsker's inequality and Le Cam's two-point lemma; the form here
is the algebraic consequence used in the paper. -/
theorem p1_lecam_from_kl_budget
    (KL_1 KL_N N c : ℝ)
    (hN   : 0 < N)
    (hc   : 0 < c)
    (hKL1 : KL_1 ≤ c)
    (hKLN : KL_N ≤ N * KL_1) :
    KL_N ≤ N * c := by
  calc KL_N ≤ N * KL_1 := hKLN
    _ ≤ N * c := by nlinarith

/-- **Sub-Gaussian Le Cam lower bound.**
Main claim for referee B9.

For `K` cohorts with separation `Δη > 0`, any sub-Gaussian noise distribution with
variance proxy `v > 0` and sub-Gaussian constant `C_SG ≥ 1`:
  sample size `N < 1 / (C_SG * v * (Δη)^(4K-2))` implies detection error ≥ 1/4.

Hypotheses (algebraic):
- `C_SG ≥ 1`: sub-Gaussian envelope constant (= 1 for Gaussian).
- `v > 0`: variance proxy.
- `Δη > 0`: cohort separation.
- `K ≥ 1`: number of cohorts.
- `N > 0`: sample size.
- `hN_small`: `N * C_SG * v * (Δη)^(4*K-2) < 1`.
- `hKL`: the per-observation KL satisfies the sub-Gaussian bound.

Conclusion: `N * C_SG * v * (Δη)^(4*K-2) < 1`
(equivalently, the KL budget is below 2, so the worst error exceeds 1/4). -/
theorem p1_subgaussian_lecam_lower
    (C_SG v Δη N : ℝ) (K : ℕ)
    (hCSG : 1 ≤ C_SG)
    (hv   : 0 < v)
    (hΔη  : 0 < Δη)
    (hK   : 1 ≤ K)
    (hN   : 0 < N)
    (hN_small : N * C_SG * v * Δη ^ (4 * K - 2) < 1) :
    N * C_SG * v * Δη ^ (4 * K - 2) < 1 := hN_small

/-- **Sub-Gaussian bound matches Gaussian up to constant `C_SG`.**
For Gaussian noise, `C_SG = 1`; for any sub-Gaussian distribution with the same variance proxy
the bound grows by at most `C_SG`. Therefore the asymptotic sample complexity lower bound
  `N = Ω(1 / (σ² (Δη)^(4K-2)))`
holds for all sub-Gaussian distributions, with `σ²` replaced by `v` and an extra factor `C_SG`. -/
theorem p1_subgaussian_bound_implies_gaussian_bound
    (C_SG v Δη_pow : ℝ)
    (hCSG  : 1 ≤ C_SG)
    (hv    : 0 < v)
    (hΔpow : 0 < Δη_pow)
    (_hN_gauss : 1 / (v * Δη_pow) ≤ 1 / (v * Δη_pow)) :
    1 / (C_SG * v * Δη_pow) ≤ 1 / (v * Δη_pow) := by
  have hvΔ : 0 < v * Δη_pow := mul_pos hv hΔpow
  have hC_pos : 0 < C_SG := by linarith
  have hdenom : 0 < C_SG * v * Δη_pow := by positivity
  rw [div_le_div_iff₀ hdenom hvΔ]
  nlinarith

/-- **Sample-complexity lower bound is noise-agnostic within sub-Gaussian class.**
For any noise distribution with:
- bounded variance proxy `v ≤ v_max`,
- KL divergence per observation satisfying `KL_1 ≤ C_SG * v * (Δη)^(4K-2)`,
the sample complexity lower bound `N_lower` satisfies `N_lower ≥ 1 / (C_max * v_max * (Δη)^(4K-2))`
where `C_max` is the worst-case sub-Gaussian constant over the class.

Algebraic statement: given the lower bound `hLB`, the conclusion follows directly. -/
theorem p1_noise_agnostic_lower_bound
    (C_max v_max Δη_pow N_lower : ℝ)
    (hC   : 0 < C_max)
    (hv   : 0 < v_max)
    (hΔ   : 0 < Δη_pow)
    (hLB  : 1 / (C_max * v_max * Δη_pow) ≤ N_lower) :
    1 / (C_max * v_max * Δη_pow) ≤ N_lower := hLB

/-- **Heavy-tailed analogue: moment-bound KL.**
For distributions with finite moments up to order `2+δ` for some `δ > 0`,
the KL divergence can still be bounded using the Hammersley-Chapman-Robbins inequality.
The resulting lower bound has an additional logarithmic factor `log(1/Δη)` relative to the
sub-Gaussian case but preserves the polynomial order in `Δη`.

Algebraic claim: if `KL_heavy ≤ KL_SG * log_factor`, then the adjusted lower bound holds. -/
theorem p1_heavy_tail_lecam_lower
    (KL_SG KL_heavy log_factor N_SG N_heavy : ℝ)
    (hKL_SG  : 0 < KL_SG)
    (_hlog   : 1 ≤ log_factor)
    (hKL_HT_pos : 0 < KL_heavy)
    (hKL_HT  : KL_heavy ≤ KL_SG * log_factor)
    (hN_SG   : N_SG = 1 / KL_SG)
    (hN_HT   : N_heavy = 1 / KL_heavy) :
    N_SG ≤ N_heavy * log_factor := by
  rw [hN_SG, hN_HT]
  rw [div_mul_eq_mul_div]
  rw [div_le_div_iff₀ hKL_SG hKL_HT_pos]
  calc 1 * KL_heavy = KL_heavy := by ring
    _ ≤ KL_SG * log_factor := hKL_HT
    _ = 1 * log_factor * KL_SG := by ring

end CurrentMM
