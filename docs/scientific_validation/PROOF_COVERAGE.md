# Machine Markets (113p) — Formal Proof Coverage & Obligation Ledger (`23 / 23 FULL`)

## 1. Summary of Lean 4 Verification Scope
- **Lean Project Directory:** `research_extension/current_manuscript_lean_20261008`
- **Verification Script:** `research_extension/current_manuscript_lean_20261008/verify_formalization.py` and `scripts/verify_theorem_code_bridge.py`
- **Build & Axiom Audit Status:** `NAMED_PROOFS_BUILD_AND_STRICT_AXIOM_AUDIT_PASS` (`317` named mathematical declarations across `30` Lean files; `0` `sorry`; `0` unapproved axioms).
- **Manuscript Theorem Coverage Counts (`23` environments in `paper/Machine_Markets_JF_Submission.tex`, indexed as `S01`–`S23`):**
  - `FULL`: `23 / 23` (100% of manuscript mathematical statements completely formalized in Lean 4; external classical theorems such as Spijker's 1991 complex-analytic $e \cdot n$ resolvent arc-length lemma enter strictly as explicit named theorem hypotheses `hSpijker`, never unproved axioms).
  - `PARTIAL`: `0`
  - `SUBRESULTS (obligations remain)`: `0`
  - `NOT FORMALIZED`: `0`
  - `NOT IN COVERAGE DOC`: `0` (all 23 manuscript statements explicitly documented in `MANUSCRIPT_COVERAGE.md` and `paper/generated/claim_to_code_map.tex`).

## 2. Explicit Scope of `CurrentProofs/SpectralCapital.lean` Declarations (`25` Kernel-Checked Theorems)
All 25 declarations in `CurrentProofs/SpectralCapital.lean` are kernel-checked with zero remaining analytical obligations:

| Lean 4 Declaration | Exact Kernel-Checked Statement | Status |
|---|---|---|
| `capital_lower_bound_of_information_ratio` | Scalar algebraic transfer: if `0 < r`, `info_req <= d_sq`, and `d_sq <= r * loss`, then `info_req / r <= loss`. | `FULL` |
| `parseval_weighted_quadratic_ratio_bound` | Finite-horizon weighted Parseval inequality $\sum d_k |V_k|^2 \le r \sum g_k |V_k|^2$ and induced ratio bound. | `FULL` |
| `parseval_toep_quadratic_ratio_bound` | Exact Toeplitz Parseval quadratic energy identity and supremum ratio bound for Theorem IA.D.2 (`S17`). | `FULL` |
| `expected_loss_lower_bound_of_information_ratio` | Scalar expected-loss transfer: if `0 < r`, `kl_req <= E_d_sq`, and `E_d_sq <= r * E_loss`, then `kl_req / r <= E_loss`. | `FULL` |
| `stopped_process_expected_loss_lower_bound` | Stopped-process expected-loss bound under Wald KL accumulation. | `FULL` |
| `wald_sequential_kl_chain_rule_capital_bound` | Complete Wald sequential KL chain-rule and adaptive expected-loss lower bound for Theorem IA.D.3 (`S18`). | `FULL` |
| `sq_sum_le_cap_mul_abs_sum` | Finite-horizon capped $L_2$-to-$L_1$ inequality: if $\forall i, |v_i| \le V_{\mathrm{eff}}$, then $\sum_i v_i^2 \le V_{\mathrm{eff}} \sum_i |v_i|$. | `FULL` |
| `rayleigh_holder_total_loss_lower_bound` | Additive quadratic-plus-fee lower bound for Rayleigh–Hölder duality. | `FULL` |
| `finite_horizon_generalized_rayleigh_decomposition` | Exact 2D spectral-residual decomposition $u = r d(\theta) + u_\perp$ and excess quadratic loss $\Delta_2$ bound. | `FULL` |
| `zero_padding_monotone_capital` | Zero-padding embedding $\mathcal{V}_L \hookrightarrow \mathcal{V}_{L+1}$ proving horizon monotonicity $C^*(L+1) \le C^*(L)$ (`TC-C4`). | `FULL` |
| `analytical_quadratic_linear_envelope_bound` | Closed-form $\Delta_2$-free quadratic-square-root minimum $\alpha\Delta_2 - W_{\perp,\max}\sqrt{\Delta_2} \ge -W_{\perp,\max}^2/(4\alpha)$. | `FULL` |
| `rayleigh_holder_closed_form_analytic_lower_bound` | Purely analytical 0-grid Rayleigh–Hölder lower bound $\underline{C}_{\mathrm{RH,0grid}}(L)$. | `FULL` |
| `flat_round_trip_double_entry_terminal_loss_identity` | Exact telescopic double-entry cash-loss identity for flat round-trip probes ($\sum v_t = 0$, `TC-C5`, Finding F07). | `FULL` |
| `numerical_certificate_64_74_rational_enclosure` | Exact rational interval enclosure certifying the worst-box $(m^*=955, k^*=89)$ lower bound $> 64.742288$~USDT (`TC-C1`, Finding F06). | `FULL` |
| `subgaussian_martingale_drawdown_and_cvar_bound` | Sub-Gaussian martingale exponential concentration, drawdown probability, and CVaR tail bound for Proposition IA.D.5 (`S21`). | `FULL` |
| `lecam_two_point_moment_matched_cubic_gap` | Exact closed-form ring identity: $\Delta M_0 = \Delta M_1 = \Delta M_2 = 0$ and $\Delta M_3 = 4 \tau p_- p_+ (\Delta\eta)^3$. | `FULL` |
| `lecam_two_point_minimax_risk_lower_bound` | Estimator-independent Le Cam two-point minimax risk lower bound. | `FULL` |
| `moment_estimator_cubic_inversion_stability` | Exact Lipschitz cubic moment-inversion stability bound $\|\hat{w}_{\mathrm{mom}} - w(\theta)\|_\infty \le |\hat{M}_3 - M_3|/(2p_-p_+(\Delta\eta)^3)$. | `FULL` |
| `minimax_sample_complexity_theta_d_eta_minus_six` | Matching global non-asymptotic Le Cam lower and moment-projection upper bounds $N^*(\Delta\eta) = \Theta((\Delta\eta)^{-6})$ for Theorem IA.D.6 (`S22`). | `FULL` |
| `kreiss_resolvent_guard_solvency_invariance` | Single-step and recursive residual-buffer solvency invariance under $\mathcal{G}_{\mathrm{Kreiss}}$. | `FULL` |
| `signed_shock_counterexample_short_dealer` | Formal verification of the signed-shock counterexample (`CE-15`, $\Delta p = -10$ safe vs. $\Delta p = +10$ insolvent). | `FULL` |
| `adversarial_signed_shock_iff_norm_bound` | Exact equivalence between worst-case norm-ball safety and adversarially signed shock safety. | `FULL` |
| `resolvent_guard_cumulative_positive_at_zero_alpha` | Strictly positive cumulative shock risk at $\alpha = 0$ (`TC-G1`, Finding F03). | `FULL` |
| `resolvent_guard_maintenance_margin_tier2_consistency` | Tier-2 maintenance-margin factor $(1+\mu)=1.005$ consistency across Eq. IA.39 and IA.40, rejecting $d=4.05$ (`TC-G2`, Finding F04). | `FULL` |
| `non_anticipative_guard_action_invariance` | Non-anticipative guard action invariance: $\alpha_t$ depends only on pre-shock state and declared envelope (`TC-G3`, Finding F05). | `FULL` |
