# Machine Markets next-stage task board

Status vocabulary: `NOT_STARTED`, `IN_PROGRESS`, `DONE_INTERNAL`, `FAILED`,
`BLOCKED_EXTERNAL`, `NOT_APPLICABLE`.

This board records the state of the work packages in the attached master plan.
`DONE_INTERNAL` means the repository-level work is complete; it does not mean
external replication, publication acceptance, or empirical validity.

| Work package | Status | Current evidence | Next action / dependency |
|---|---|---|---|
| WP00 baseline | DONE_INTERNAL | `docs/BASELINE_AUDIT.md`; 98 + 6 tests; algebra verifier | Resolve or preserve six checksum discrepancies in a future release process |
| WP01 claim ledger | DONE_INTERNAL | `docs/CLAIM_EVIDENCE_LEDGER.csv`; `docs/CORRECTIONS.md` | Use IDs in every new protocol and manuscript table |
| WP02 primary question | DONE_INTERNAL | `docs/NEXT_STUDY_PROTOCOL.md`; `docs/ANALYSIS_PLAN.md`; `studies/next_stage_validation/configs/frozen_config.json` | Keep later changes versioned |
| WP03 priority audit | IN_PROGRESS | Targeted internal reviews exist; no exhaustive external priority review | Complete primary-source matrix and independent review |
| WP04 proof audit | DONE_INTERNAL | Existing companion proof/code audits and negative controls | Revisit only when WP05 changes the estimand |
| WP05 measurement result | NOT_STARTED | Existing restricted limits are recorded | Define next estimator/limit protocol |
| WP06 model boundary | DONE_INTERNAL | Runtime audit extension and fail-closed tests | Institutional authentication remains external |
| WP07 tail uncertainty | DONE_INTERNAL | Existing tail contract and controls | Add uncertain-rate/unknown-initial-state extensions under WP05 |
| WP08 observation errors | DONE_INTERNAL | `observation_benchmark.json`; episode-block bootstrap estimator | Extend only with a new declared observation law |
| WP09 dependence/resets | IN_PROGRESS | Dependent episode benchmark uses episode-level units | Add reset and time-uniform monitoring study |
| WP10 economic budgets | DONE_INTERNAL | Existing volume/cost counters and endpoint comparison | Add simulated unwind to the observation law |
| WP11 conventional baselines | DONE_INTERNAL | Full-horizon comparison with retained errors | Keep equal-information contract for new estimators |
| WP12 second market implementation | DONE_INTERNAL | `studies/next_stage_validation/src/mm_next/market.py`; property tests | Structural differences and calibration limits remain documented |
| WP13 empirical calibration | BLOCKED_EXTERNAL | Public crypto pilot only; no historical L2 calibration | Obtain authorized historical order-book data or mark blocked |
| WP14 accounting | DONE_INTERNAL | Existing ledger, fill, liquidation, and dealer audits | Extend after WP12 environment exists |
| WP15 operational risk | DONE_INTERNAL | `intervention_results.json`; difficult synthetic held-out regime | External transfer and loss shifting remain untested |
| WP16 AI-specific effect | DONE_INTERNAL | `matched_agent_analysis.json`; three seeds, paired tapes | Result is null; do not claim AI-specific effect |
| WP17 transfer | NOT_STARTED | No second calibrated environment | Depends on WP12-WP16 |
| WP18 interventions | DONE_INTERNAL | `intervention_results.json`; fixed target and 256 held-out tapes | Add multi-account transfer only with a new environment |
| WP19 failure taxonomy | DONE_INTERNAL | Existing false-floor, omitted-state, reset, noise, and audit controls | Add violations from WP08-WP16 |
| WP20 portability | IN_PROGRESS | Frozen config, scripts, generated paper assets, test commands | Fresh-copy package and new manifest remain |
| WP21 external review | BLOCKED_EXTERNAL | Challenge package prepared; no reviewer assigned | Human reviewer/team required |
| WP22 manuscript rewrite | DONE_INTERNAL | `paper/Machine_Markets_Next_Research_Paper.tex/.pdf`; changelog | Human authorship, novelty, rights, and review sections remain open |
| WP23 versioned release | NOT_STARTED | Release 1.0 is preserved on `main` | Package only after manuscript and evidence freeze |

## Current checkpoint

- Branch: `codex/machine-markets-wp00-wp01` in an isolated worktree.
- Reference branch: `main`, unchanged by this checkpoint.
- No new scientific result is claimed by WP00/WP01.
- The four existing study packages remain isolated and unmodified.
