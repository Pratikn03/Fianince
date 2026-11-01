# Semantic audit of the older Lean mappings for Paper 1 (1 November 2026)

**Question:** do the Lean theorems mapped to the nine older "full" rows of `COVERAGE.md` prove the statements as the paper now words them?

**Method:** each Lean statement was read against the paper's statement. Auditor: Claude (**not independent**).

| Result | Lean theorems | Verdict |
|---|---|---|
| `lem:micro` | `tracking_prior_variance_unique_positive`, `p1_prop_kalman_memory`, `actual_quadratic_ogd_update` | full (steady-state algebra; convergence of the Kalman recursion not claimed) |
| `lem:cm` | `actual_nonnegative_anchor_impulse_mixture`, `actual_physical_impulse_completely_monotone` | full |
| `lem:toeplitz` | `actual_trader_fundamental_equity`, `quadratic_execution_cost_triangular`, `actual_all_anchor_execution_coercive` | full |
| `thm:cap` | `actual_physical_counterparty_robust_cap` | full (the error clause inherits `thm:quantity` (ii)) |
| `prop:disclosure` | `arbitrarily_small_solvent_exact_disclosure` | full |
| `thm:quantity` | `actual_pair_quantity_kl_bound`, `actual_pair_first_pulse_attains_kl`, `p1_thm_quantity_sharp_orders` | **conditional**: exact error formula and classifier optimality not formal |
| `thm:capital` | `actual_all_anchor_trader_energy_bound`, `p1_thm_capital_funded_probes` | **conditional**: energy-to-divergence step and converse not formal |
| `thm:abstain` | `finite_window_abstention_lower_bound`, `scalar_ar1_path_kl_bound` | **conditional**: Gaussian AR(1) path divergence and Pinsker not formal |
| `prop:passive0` | `passive_covariance_gap_and_chebyshev_sample_bound`, `p1_prop_passive0_three_step_blocks` | **conditional**: variance formula `R` not formal |

**Counts:** Paper 1 coverage moves from 14 full / 10 conditional / 2 arithmetic to **10 full / 14 conditional / 2 arithmetic**. The paper never claimed the four downgraded results as machine-checked. Its verification paragraph now names the five confirmed results and states exactly what is checked for the four conditional ones.

## Addendum (1 Nov 2026, later): `Paper1QuantityCapital.lean`

Five new declarations, standard axioms only (`propext`, `Classical.choice`, `Quot.sound`):

- `p1_pair_record_kl_energy`: for the paper's split pair in the actual cohort model, `KL ≤ K*²δ⁴‖v‖²/(2σ²)` with the paper's `K* = 2κ²q/(ε³(1−S)²)`.
- `p1_thm_quantity_kl`, `p1_thm_quantity_test`: Theorem `thm:quantity` (i) with an ℓ₁ budget `V`, and the resulting `σ² ≤ 2K*²V²δ⁴` for any test with both errors at most 1/4.
- `p1_thm_capital_kl`, `p1_thm_capital_test`: Lemma `thm:capital` lower bound. There is `m = κ(1−r)/(1+r) > 0` (radius from the energy lemma, not the paper's explicit `r`) such that every probe that leaves a trader with starting cash `B` solvent at the fundamental mark gives `KL ≤ K*²Bδ⁴/(σ²m)`, and a 1/4-error test needs `σ²m ≤ 4K*²Bδ⁴`.

Semantic check. The two laws are `gaussianRecordLaw` of the actual `controlledCohortRun` prices for `![q/2,q/2], ![η−δ,η+δ]` and `![q], ![η]`, which is the paper's experiment. The divergence direction is `KL(P_δ‖P_0)`; the paper writes the other direction (equal here, symmetry not formalized). The solvency hypothesis is the existing `equity (traderCashAfter …) ≥ 0`, marking at the fundamental price, as in the paper's proof.

Status change: both rows stay `conditional` (part (ii)'s exact error formula and the capital converse are not formal), but the gap noted in the 1 Nov audit, "the step from the energy bound to the divergence", is closed.

Still not formal and left on paper: the Gaussian AR(1) path divergence and Pinsker for `thm:abstain` (Mathlib has no Pinsker); the exact Neyman–Pearson error for `thm:quantity` (ii).
