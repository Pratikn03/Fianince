# Author proof check: the five results new in the 20 November 2026 version

Written by an AI system for the authors. This is not independent review. Page numbers refer to
`Paper1_ssrn_supplement.pdf` of 20 November 2026.

Lean covers the deterministic steps (files `PublicationRevision.lean` and `PublicationRevision2.lean`, 22 declarations,
standard axioms only; supplement Table S5). Your check is needed for the steps marked "by hand". When every row has a
checker and an outcome, delete the "being checked" sentence in Declarations.

| Result | Proof (page) | Step | Lean | By hand: what to confirm | Checker | Outcome |
|---|---|---|---|---|---|---|
| Thm 5.5 smooth-family lower bound | S-90 | Gauss and Radau rules have positive weights and match moments of order 0 to 2K−2 | — | Szegő §3.4; check K = 2 by hand: Gauss nodes ±1/√3 with weights ½ each; Radau nodes −1 and 1/3 with weights ¼ and ¾ | | |
| | | Taylor remainder: flow gap ≤ 2W·B(h)·Δ^(2K−1)/(2K−1)! | `matched_polynomial`, `flow_gap` | That the derivative envelope B(h) is the one in the hypothesis | | |
| | | KL of the records = Σ_t κ²E(F−F′)²/(2σ²) | — | Chain rule; same probe policy and same initial law under both populations | | |
| | | Errors < 1/4 ⇒ KL > 1/2 ⇒ the T bound | `errors_need_unit_loss`, `sample_size_lower_bound` | Pinsker's inequality is used in the form KL ≥ 2·TV² | | |
| Prop 5.6 conditional recovery | S-90 | Minimum distance gives W₁ ≤ (2‖ξ̄‖/c₀)^(1/(2K−1)) | `minimum_distance_error` | Gaussian concentration: ‖ξ̄‖ ≤ σ(√L + √(2 log(1/δ)))/√N | | |
| Thm 5.7 shrinking cluster | S-94 | 2K moments determine K atoms | `vandermonde_signed_zero` | Reduction from two K-atom populations to a signed measure with at most 2K atoms | | |
| | | Confluent-Vandermonde Jacobian ≠ 0 ⇒ Lipschitz inverse on the compact class | — | The compactness argument (sequence and limit) | | |
| | | Remainder O(Δ^(2K)) absorbed for Δ ≤ Δ₀ | `inverse_remainder_absorption` | Bound on the remainder's derivatives | | |
| | | Rank condition for exponential and power-law memory | — | Polynomial-in-log(m+1) argument for the power law | | |
| Thm 6.1 detection = forecast loss | S-94 | KL = Λ/2 | `forecast_mismatch_identity` (algebra) | Gaussian KL with common variance is (m−m′)²/(2σ²) | | |
| | | Λ ≤ 1 ⇒ no test with both errors < 1/4 | `errors_need_unit_loss` | — | | |
| | | Bayesian mixture loses at most log(1/π) | `bayes_mixture_regret` | — | | |
| Thm 6.2 forecast benchmark | S-90 | Positions are kernel convolutions of past prices | `pos_closed`, `positions_kernel` | — | | |
| | | Ing and Wei expansion | — | Read Ing and Wei (2005), Proposition 2; check the conditions on the order L and the news | | |
| | | Approximation term ≤ S²r̄^(2L)σ²/(1−S)² | `tail_budget` | The variance bound E x² ≤ σ²/(1−S)² | | |
| Thm 6.3 uniform log-loss | S-95 | Gaussian integral, completed square | — | The algebra of q(X) | | |
| | | log det ≤ L log(1 + T/(1−S)²) | `sum_log_le` (Jensen step) | Diagonalization and E tr(Z′Z) ≤ Tσ²L/(1−S)² | | |
| | | Omitted-coefficient term and the choice of L | `geometric_tail`, `tail_budget`, `order_choice` | — | | |
| Prop 6.5 channels | S-91 | (b) value = κ² × reduction in projection error | — | Information sets of the two observers | | |
