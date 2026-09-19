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

## Never combine these quantities into one headline sample count
Observation laws differ between hidden kernels and public prices. Nested horizons share data.
Funding scenarios share random inputs. Alternative inference methods are paired on the same data.
Tail reanalysis reuses the primary linear rows. Simulation events, panels, scalar checks and solver
comparisons are different counting units. Per-study protocols explain each denominator.

## Reviewer-ready sources
Each study includes its original theory/claim ledger, data dictionary and research protocol.
The latest outside-replication instructions are
`studies/audited_constraints/replication/EXTERNAL_REPLICATION.md`.
All outside-review and deployment-authentication gates remain pending.
