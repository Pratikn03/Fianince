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
