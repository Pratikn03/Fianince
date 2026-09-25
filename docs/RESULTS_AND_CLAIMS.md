# Result-to-evidence map

Paths below are relative to the master root. This index summarizes the preserved files; it adds
no new experimental results. The original per-study dictionaries and protocols remain authoritative
for column definitions, generated settings, noise laws, timing, and information supplied to inference.

## 1. Original framework and deterministic algebra
**Paper:** `original_framework/Machine_Markets_Research_Paper.pdf` (original 24 pages).
**Code:** `studies/observable_stress_tests/provenance/verify_original_algebra.py`.
**Fresh output:** `verification/fresh_verifiers/original_algebra.json`.
The 625 scalar and 250 small-network checks verify the stated restricted-model algebra.
They are not trained AI-agent experiments or evidence from actual financial markets. The complete
joint Jacobian supersedes the incomplete channel-only expression in the historical concept note.

## 2. Hidden Slow Learners
**Root:** `studies/hidden_slow_learners/`.
**Code:** `src/machine_markets/`; main runner `scripts/run_experiments.py`.
**Data/results:** `results/exact_witnesses.json`, `readable_witness.json`, `measurement_inputs.npz`,
`decisions.csv`, `comparison_summary.csv`, `negative_controls.json`.
**Paper:** `paper/Hidden_Slow_Learners.pdf`.
The 112 matched pairs and readable witness exhibit exact finite-window ambiguity within a specified
positive linear model. The noisy experiment has 21,600 datasets and 86,400 decisions at nested
horizons. Its initial comparator is not a basis for claiming superiority over full-horizon methods.
Figures and their building script are included. Global priority is not established.

## 3. Full-horizon conventional comparison
**Root:** `studies/full_horizon_audit/`.
**Code:** `src/mmfh/estimators.py`, `scripts/run_comparison.py`.
**Data:** `data/full_measurements.npz`; full comparison `results/paired_comparison.csv`.
**Summaries:** `results/aggregate_comparison.csv`, `confidence_event_audit.json`,
`testing_limits_summary.json`, `resolution_sensitivity.csv`.
At 256 observations, out of 10,800 vectors per noise condition:

| Method | Lower noise: definite | Wrong | Higher noise: definite | Wrong |
|---|---:|---:|---:|---:|
| Original summary bound | 8,930 | 0 | 7,150 | 0 |
| Positive point fit | 10,800 | 24 | 10,800 | 306 |
| Full-moment outer bound | 9,508 | 0 | 8,278 | 4 |

Point fitting is not a confidence certificate. The full-moment procedure resolves more cases on
average, but not every previous case. All four high-noise confident errors are retained.
The Gaussian two-point limit concerns its own declared observation law, not every financial
stress test. The contribution supported here is a restricted measurement limit, not universal
superiority of the original diagnostic.

## 4. Observable orders and prices
**Root:** `studies/observable_stress_tests/`.
**Code:** `src/market.py`, `src/observable.py`, `run_study.py`, `run_extensions.py`.
**Data:** `data/public_panel_statistics.npz`, public example price/probe archives.
**Results:** `results/comparison.csv`, `panels.csv`, `design_summary.csv`, `negative_controls.csv`.
The 1,920 primary panels contain 1,105,920 synthetic episodes and 5,760 nested-horizon comparisons.
At the longest horizon, the strongest primary design labels 80 of 480 panels (16.67%) and leaves
400 inconclusive, with no wrong confident label in that run. The false-floor control has 20/20
false-stable labels despite coverage of every true measured response. Gaussian episode assumptions,
exogenous probes, a correct floor and the observation law are essential.

## 5. Audited memory and episode budgets
**Root:** `studies/audited_constraints/`.
**Code:** `src/audit.py`, `src/inference.py`, `src/linear.py`, `scripts/run_linear.py`,
`scripts/run_followup.py`, `scripts/measure_tail.py`.
**Data:** `data/linear_terminal_rows.npz`, `endpoint_terminal_rows.npz`, public price examples.
**Results:** `results/linear_panels.csv`, `endpoint_confirmation.csv`, `endpoint_summary.csv`,
`measured_tail.csv`, `assumption_control_summary.csv`.
A complete, truthful geometric-memory contract justifies the specified tail bound. It does not
authenticate a proprietary runtime. Omitting a slow state produces 80/80 false-stable calls.
The confirmation has 240 panels per method and episode budget:

| Episodes | Fixed endpoint: definite / wrong | Diverse endpoints: definite / wrong |
|---|---:|---:|
| 32 | 26 / 0 | 75 / 2 |
| 128 | 86 / 0 | 112 / 1 |
| 512 | 159 / 1 | 144 / 0 |

The exact rates, initial reset and prices are additional information. This is not an equal-information
victory over the earlier black-box experiment. Repeated small round trips also fail to improve on
an impulse under the tested gross-volume comparison. The negative results remain part of the paper.

## 6. Financial constraints and operational risk
**Root:** `studies/audited_constraints/`.
**Code:** `src/finance.py`, `scripts/run_finance.py`, `scripts/run_followup.py`.
**Data:** `data/finance_episodes_*.npz`, `finance_ledger_example_*.npz`, `dealer_stress_*.npz`.
**Results:** `results/financial_settings.csv`, `financial_budget_panels.csv`,
`financial_accounting_audits.csv`, `financial_summary.json`, `dealer_stress.csv`.
The primary design has 491,520 setting-trajectories but 163,840 distinct exogenous tapes because
funding comparisons are paired. Constraints alter 12,388,550 order requests and cause 2,240,614
account-step margin calls; these are not counts of independent financial crises.
In one dealer-stress scenario, the stable isolated signal model (a + sum(q) = 0.82) coexists with
45.42% halts over 8,192 simulated episodes. The risk target is a specified finite-horizon event,
not asymptotic stability. The simulation is uncalibrated; the primary near-zero/near-one event
probabilities do not establish general practical performance near a threshold.

## 7. Broadened 120-cell Comparator Benchmark and Conic Contraction
**Paper:** `paper/Machine_Markets_Final_Integrated_Paper.pdf` (Chapter 4, Table 5, Figure 4).
**Code:** `research_extension/mm_revision/studies/run_broadened_comparator_grid.py`, `conic_informativeness_curve.py`.
**Artifacts:** `research_extension/outputs/broadened_comparator_results.json`, `conic_contraction_results.json`.
The 120-cell grid tests 600 synthetic panels across 5 feedback regimes ($S \in \{0.70, 0.82, 1.00, 1.03, 1.18\}$), 3 decay rates, 2 budgets, and 2 horizons. At low budget ($R=128$), the Covariance Conic Certificate achieves 100% parameter coverage and 0% decisiveness. Under the monotonic budget sweep ($R=128 \to 32,768$, 300 solves total), the conic certificate contracts by up to 70.4% in width, reaching 100.0% decisiveness and 0.0% conditional error at $R=32,768$.

## 8. Output-Error Misspecification Diagnostic
**Paper:** `paper/Machine_Markets_Final_Integrated_Paper.pdf` (Chapter 4, Table 6).
**Code:** `research_extension/mm_revision/studies/output_error_misspecification_diagnostic.py`.
**Artifact:** `research_extension/outputs/output_error_diagnostic_results.json`.
Evaluating 400 panels across conditions C1–C4 reveals that output-error estimators are unbiased ($|\text{bias}| \le 0.00004$) under matched models, but fitting a single-rate model to a two-rate ground truth induces an irreducible structural bias of $-0.1072$, explaining the 57.1% conditional error rate in Table 5.

## 9. Group Identification and Continuous-Time Dynamics
**Paper:** `paper/Machine_Markets_Final_Integrated_Paper.pdf` (Chapter 5), `paper/Machine_Markets_Mathematical_Supplement.pdf` (Sections S1–S14).
**Code:** `research_extension/group_identification.py`, `reference_directory/group.py`, `reference_directory/continuous.py`.
Swapped-feedback non-identifiability (Proposition 5.1) proves that symmetric memory decay prevents isolating individual group feedbacks from aggregate prices. Channel excitation ($b = \eta U q$, Theorem 5.2) yields unique recovery only under known learning rates. The continuous-time extension establishes exact Hurwitz conditions and Euler discretization error bounds ($\mathcal{O}(h^2)$).

## 10. Smooth Solvency Surface and Inventory Buffer Exhaustion
**Paper:** `paper/Machine_Markets_Final_Integrated_Paper.pdf` (Chapter 6, Tables 11, 12, 13).
**Code:** `research_extension/mm_revision/studies/funded_smooth_surface.py`, `funded_stress.py`.
**Artifacts:** `research_extension/outputs/funded_smooth_surface_results.json`, `funded_mechanism_results.json`.
Across 330 factorial cells ($\mu \in [-0.2, -2.0]$), resolving inventory drift shows a smooth monotone solvency frontier. Dealer halts occur with positive dealer equity (\$9,999.06) due to inventory buffer exhaustion ($|\text{inv}_t| > 25 \times \text{mult}$), whereas unlimited funding causes true balance-sheet insolvency ($-\$122.03$). Paired counterfactual controls ($N=100$) confirm that active learning amplifies price dislocation by $+0.6148$ [0.6148, 0.6149] ($s_D = 0.0004$).

## 11. Exploratory Public Market Studies (Digital Assets)
**Paper:** `paper/Machine_Markets_Final_Integrated_Paper.pdf` (Chapter 7, Tables 14, 15, 16).
**Code:** `research_extension/real_data_study.py`, `research_extension/mm_revision/studies/binance_robustness.py`.
**Artifacts:** `research_extension/outputs/empirical_results.json`, `binance_robustness_results.json`.
Coinbase predictive regressions ($N=10$) yield bivariate $t=+2.47$ ($p=0.039$) which attenuates to $t=+1.23$ ($p=0.264$) under spread and volatility controls. Binance US state-space estimation across 175 runs hits parameter bounds in 93.1% of fits. These are strictly framed as exploratory cross-sectional associations and empirical model sensitivity, not structural causal identification.

## 12. Empirical Microstructure Calibration (Gates 2–4)
**Paper:** `paper/Machine_Markets_Final_Integrated_Paper.pdf` (Chapter 7, Section 7.3, Table 17).
**Code:** `research_extension/gate24_public_data/gate24_analysis.py`, `research_extension/gate24_public_data/calibrated_simulator.py`.
**Artifacts:** `research_extension/gate24_public_data/gate24_analysis_results.json`, `data_acquisition_manifest.json`.
Analysis of 3.41 GB public data from Binance Vision across 129,600 1-minute bars and 1,000-level LOB depth for BTC, ETH, and SOL authenticates external market channels. Probing costs range from \$0.59 (ETH) to \$89.00 (BTC) for $N=1,000$ active probe episodes. An independent clean-room calibrated simulator confirms balance-sheet conservation ($\text{residual} < 10^{-10}$) and monotone solvency frontiers under empirically grounded parameters.

## 13. Learned-Agent Transfer Layer (Q-Learning and Model Audit)
**Paper:** `paper/Machine_Markets_Final_Integrated_Paper.pdf` (Chapter 6, Section 6.4, Table 14).
**Code:** `research_extension/learned_agents/train_q_learning.py`, `research_extension/learned_agents/evaluate_q_learning.py`.
**Artifacts:** `research_extension/outputs/learned_agents/q_learning_transfer_results.json`, `trained_q_agents.json`.
Evaluating 5 independently trained tabular Q-learning agents (6,125 states, 5 actions) across 10 held-out test seeds (15,000 steps each) reveals that learned agents reduce dealer halt rates from 100% to 0.0% and price dislocations by 75% compared to naive trend-followers. Active adaptation introduces contrarian damping ($dq/dx < 0$). Crucially, the local model-class validity audit correctly classifies 5/5 learned policies as `OUTSIDE_CERTIFIED_MODEL_CLASS` ($R^2 = 0.01\text{--}0.24$) rather than force-fitting positive linear feedback theorems, demonstrating safe observer abstention under architectural violation.

## Never combine these quantities into one headline sample count
Observation laws differ between hidden kernels and public prices. Nested horizons share data.
Funding scenarios share random inputs. Alternative inference methods are paired on the same data.
Tail reanalysis reuses the primary linear rows. Simulation events, panels, scalar checks and solver
comparisons are different counting units. Table 18 in Chapter 8 and Appendix B explains each denominator.

## Reviewer-ready sources
Each study includes its original theory/claim ledger, data dictionary and research protocol.
The latest outside-replication instructions are
`studies/audited_constraints/replication/EXTERNAL_REPLICATION.md` and `docs/REPRODUCTION_GUIDE.md`.
All outside-review and deployment-authentication gates remain pending.

