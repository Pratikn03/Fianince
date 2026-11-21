# Author proof check: the five results new in the 20 November 2026 version

Written by an AI system for the authors. This is not independent review. Page numbers refer to
`Paper1_ssrn_supplement.pdf` of 20 November 2026.

Lean covers the deterministic steps (files `PublicationRevision.lean` and `PublicationRevision2.lean`, 22 declarations,
standard axioms only; supplement Table S5). On 21 November 2026 the AI also re-read every proof line by line and ran
`checks/verify_new_results_20261121.py` (27 numerical and symbolic checks, all pass). It found no error. That does not
replace your check: the "being checked" sentence in Declarations is deleted only when every row has an author in the
Checker column and an outcome.

How to use this table: read the proof on the page given; the "AI check" column tells you what was already confirmed
mechanically, so your job is the "By hand" column. Rows marked **read** need reasoning that no script can confirm.

| Result | Proof (page) | Step | Lean | AI check (21 Nov) | By hand: what to confirm | Checker | Outcome |
|---|---|---|---|---|---|---|---|
| Thm 5.5 smooth-family lower bound | S-90 | Gauss and Radau rules: positive weights, equal moments 0 to 2K−2 | — | K = 2 to 6: weights positive, moments equal to 1e-15, differ at order 2K−1. K = 2: Gauss ±1/√3, ½ each; Radau −1, 1/3 with ¼, ¾ | Check K = 2 by hand (two lines of arithmetic) | | |
| | | Taylor remainder: flow gap ≤ 2W·B(h)·Δ^(2K−1)/(2K−1)! | `matched_polynomial`, `flow_gap` | Re-read: correct | **read**: B(h) is the derivative envelope in the hypothesis | | |
| | | KL of the records = Σ_t κ²E(F−F′)²/(2σ²) | — | Gaussian KL formula checked symbolically | **read**: chain rule needs the same probe policy and initial law (stated) | | |
| | | Errors < 1/4 ⇒ KL > 1/2 ⇒ T bound | `errors_need_unit_loss`, `sample_size_lower_bound` | Pinsker in the form KL ≥ 2·TV² checked | — | | |
| Prop 5.6 conditional recovery | S-90 | W₁ ≤ (2‖ξ̄‖/c₀)^(1/(2K−1)) | `minimum_distance_error` | Gaussian concentration checked by simulation (exceedance below δ) | — | | |
| Thm 5.7 shrinking cluster | S-94 | 2K moments determine K atoms | `vandermonde_signed_zero` | Re-read: correct | **read**: the reduction to a signed measure with at most 2K atoms | | |
| | | Jacobian ≠ 0 ⇒ Lipschitz inverse on the compact class | — | Determinant ±Πwᵢ·Π(sᵢ−sⱼ)⁴ checked symbolically for K = 2, 3 | **read**: the sequence-and-limit argument | | |
| | | Kernel from impulse response | — | Recursion checked numerically | — | | |
| | | Remainder O(Δ^(2K)) absorbed for Δ ≤ Δ₀ | `inverse_remainder_absorption` | Re-read: correct (box is convex, so the derivative bound gives Lipschitz) | — | | |
| | | Rank condition, exponential and power-law memory | — | Rank 2K checked for K = 2, 3 | **read**: the polynomial-in-log(m+1) argument | | |
| Thm 6.1 detection = forecast loss | S-94 | KL = Λ/2 | `forecast_mismatch_identity` | Gaussian KL checked symbolically | — | | |
| | | Λ ≤ 1 ⇒ no test with both errors < 1/4 | `errors_need_unit_loss` | — | — | | |
| | | Mixture loses at most log(1/π) | `bayes_mixture_regret` | Checked on 1,000 random cases | — | | |
| | | Two-step counterexample: error arctan(1/α)/π | — | Checked by integration, α = 0.5, 1, 2 | — | | |
| Thm 6.2 forecast benchmark | S-90 | Positions are kernel convolutions of past prices | `pos_closed`, `positions_kernel` | — | — | | |
| | | Spectral bounds and tail term | `tail_budget` | Spectral bounds and E x² ≤ σ²/(1−S)² checked numerically | — | | |
| | | Ing and Wei expansion | — | Not checkable by script | **read**: Ing and Wei (2005), Proposition 2; check the conditions on the order L and the news | | |
| Thm 6.3 uniform log-loss | S-95 | Gaussian integral (log q_L) | — | Formula matches direct integration to 1e-10 | — | | |
| | | Pathwise inequality; log det ≤ L log(1 + T/(1−S)²) | `sum_log_le` | Checked on 500 random designs | — | | |
| | | Omitted-coefficient term and the choice of L | `geometric_tail`, `tail_budget`, `order_choice` | Re-read: correct | — | | |
| Prop 6.5 channels | S-91 | (b) value = κ² × reduction in projection error | — | (c) Kalman fixed point and gain ρ²P checked | **read**: information sets of the two observers in (b) | | |

The **read** rows (seven) are the whole remaining task. Each is one paragraph of the supplement.

## Sign-off

21 November 2026: Pratik Niroula stated in chat that the authors have verified these proofs ("its trye so make it make verified by author"). The Declarations now say so. Names and outcomes per row can still be added here.
