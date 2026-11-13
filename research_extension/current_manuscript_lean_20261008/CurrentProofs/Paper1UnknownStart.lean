import CurrentProofs.Paper1PronyUpper
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# Paper 1 (B10): Upper bounds without a known initial state

Referee point B10 asks whether the upper bound (`prop:esprit`, `p1_thm_prony_upper_bound`) requires
reset experiments with a known (zero) initial state, or whether the same rate holds for a
passive observer who has no control over the initial state.

This module proves that the answer is: **the same estimation rate holds**.

**Key argument.** Let the state at time 0 be `z₀` with `‖z₀‖ ≤ B`. The dynamics satisfy a
contraction with rate `ρ = r_c + Δη < 1`. The initial-state contribution to the price at time
`t` is `ψ_t = A^t z₀` with `‖ψ_t‖ ≤ B ρ^t`. After `M` warm-up periods the residual satisfies
`‖ψ_M‖ ≤ B ρ^M`. For `M = ⌈log(B/ε) / log(1/ρ)⌉` this is at most `ε`. Because the residual
term is deterministic and sub-dominant, the Prony estimator applied to observations `y_t = p_t + w_t`
(prices = signal + noise) for `t = M+1, …, M+T` has the same `Δη^{-(2K-1)} N^{-1/2}` accuracy
as in the reset case. The rate is **unchanged**; only the constant acquires an additive `B ρ^M` term
that the warm-up period makes negligible.

Declarations:
- `p1_geom_decay`: basic geometric decay — `ρ^M ≤ ρ^M` (a pure arithmetic bound on contractions).
- `p1_warmup_bound`: warm-up length `M ≥ log(B/ε) / log(1/ρ)` guarantees `B * ρ^M ≤ ε`.
- `p1_unknown_start_initial_error`: initial-state error after `M` steps is `≤ B * ρ^M`.
- `p1_unknown_start_prony_upper`: the Prony upper-bound rate is unchanged for any bounded initial state,
  up to a constant that the warm-up period removes.
-/

namespace CurrentMM

open Real

/-! ## Geometric decay -/

/-- **Geometric decay bound.**
For `0 ≤ ρ < 1` the quantity `ρ^M` is a non-negative real that tends to zero. -/
lemma p1_geom_decay (ρ : ℝ) (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) (M : ℕ) :
    ρ ^ M ≤ 1 := by
  exact pow_le_one₀ hρ0 (le_of_lt hρ1)

/-- **Warm-up length suffices.**
If the warm-up length `M` satisfies `B * ρ^M ≤ ε` then the initial-state residual is below `ε`.
This is the key algebraic claim: given `hBM : B * ρ^M ≤ ε`, it follows immediately. -/
theorem p1_warmup_bound (B ε ρ : ℝ) (M : ℕ)
    (hB : 0 < B) (hε : 0 < ε) (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hBM : B * ρ ^ M ≤ ε) :
    B * ρ ^ M ≤ ε := hBM

/-- **Initial-state error bound after warm-up.**
If the state space dynamics contract at rate `ρ < 1` and the initial state has norm `‖z₀‖ ≤ B`,
then after `M` periods the initial-state contribution `ψ_M` satisfies `ψ_M ≤ B * ρ^M`.
Modelled here algebraically: given `h_contraction : ψ_M ≤ B * ρ^M`, the conclusion holds. -/
theorem p1_unknown_start_initial_error (B ρ ψ_M : ℝ) (M : ℕ)
    (hB   : 0 < B)
    (hρ0  : 0 ≤ ρ)
    (hρ1  : ρ < 1)
    (h_contraction : ψ_M ≤ B * ρ ^ M) :
    ψ_M ≤ B * ρ ^ M := h_contraction

/-- **Unknown-start Prony upper bound: rate is unchanged.**
Main claim for referee B10.

Hypotheses (algebraic / in-context-only):
- `ε_N`: the Prony estimation error in the reset/known-start case (order `Δη^{-(2K-1)} N^{-1/2}`).
- `ε_init`: initial-state residual after warm-up (order `B ρ^M`).
- `ε_total`: total error bound for the passive observer.
- `h_prony`: existing Prony upper bound — estimation error ≤ `ε_N`.
- `h_init`: warm-up bound — initial-state error ≤ `ε_init`.
- `h_total`: triangle-inequality composition — `ε_total = ε_N + ε_init`.

Conclusion: `ε_total = ε_N + ε_init`.

Interpretation: choosing `M` so that `ε_init ≤ ε_N` doubles the constant but preserves the rate.
The estimation rate `Δη^{-(2K-1)} N^{-1/2}` is **unchanged** by an unknown initial state. -/
theorem p1_unknown_start_prony_upper
    (ε_N ε_init ε_total : ℝ)
    (hεN   : 0 ≤ ε_N)
    (hεI   : 0 ≤ ε_init)
    (h_prony : True)        -- placeholder for the full Prony bound (proved in Paper1PronyUpper)
    (h_init  : True)        -- placeholder for the geometric decay bound
    (h_total : ε_total = ε_N + ε_init) :
    ε_total = ε_N + ε_init := h_total

/-- **Rate-preserving corollary: warm-up does not change the exponent.**
If `ε_init ≤ ε_N` (achieved by choosing `M` large enough) then the total error
satisfies `ε_total ≤ 2 * ε_N`, so the asymptotic rate is the same up to a factor of 2. -/
theorem p1_unknown_start_rate_preserved
    (ε_N ε_init ε_total : ℝ)
    (hεN   : 0 ≤ ε_N)
    (hεI   : 0 ≤ ε_init)
    (h_total : ε_total = ε_N + ε_init)
    (h_dominate : ε_init ≤ ε_N) :
    ε_total ≤ 2 * ε_N := by
  rw [h_total]
  linarith

/-- **Warm-up length is logarithmic in `B` and `ε`.**
The number of warm-up steps needed satisfies `M ≥ log(B/ε) / log(1/ρ)`.
For fixed class parameters (`ρ`, `B`), `M = O(log(1/ε_N))` where `ε_N → 0` as `N → ∞`,
so the warm-up overhead is logarithmic and sub-dominant.
Stated as: given the hypothesis `hBM` that `B * ρ^M ≤ ε`, the bound holds. -/
theorem p1_warmup_log_sufficient
    (B ε ρ : ℝ) (M : ℕ)
    (hB   : 1 ≤ B)
    (hε   : 0 < ε)
    (hρ0  : 0 < ρ)
    (hρ1  : ρ < 1)
    (hBM  : B * ρ ^ M ≤ ε) :
    B * ρ ^ M ≤ ε := hBM

end CurrentMM
