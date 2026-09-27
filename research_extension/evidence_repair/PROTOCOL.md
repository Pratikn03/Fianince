# Evidence repair, 2026-09-26

Status: post-review corrective analysis; not a new confirmatory experiment.
The purpose is implementation and claim consistency, not favorable findings.

## Preservation

Work branch: `codex/paper-evidence-repair-20260926`. Main's commit is unchanged.
The starting manuscript, supplements, learned-agent code/checkpoints/results,
inference code and Gate24 implementation (including pre-existing uncommitted
edits) were copied to:
`/Users/pratik_n/Downloads/Machine_Markets_repair_baseline_IMV6As/starting-paper-and-code.tgz`.
SHA-256: `d75686c528ac3819e10cd6f464dab2770bc813148bf529f880a4d73f33dd026f`.
Historical results remain in their original directories. Corrected numerical
artifacts go under `research_extension/outputs/evidence_repair_20260926/`.

## Locked corrective training specification

- Ten independent tabular policies, 100,000 transitions each; validation at
  20,000-step intervals. No neural or multi-dealer claims.
- Training seeds 926101--926110; validation seeds 926201--926205;
  evaluation seeds 926301--926310, ten fixed shared exogenous tapes.
- MarketConfig defaults and QLearningAgent defaults, serialized in the run.
- Inventory-only dealer, simultaneous netting and proportional fills, four
  counterpart ledgers. Negative cash permitted; no margin/liquidation claim.
- Halt means no further execution; price marks continue to 128 steps.
- Shock -2 at step 16. Report mean absolute displacement, turnover, equity,
  and halt frequency. No favorable-effect stopping criterion.
- Each active/frozen run starts from a fresh clone of the same checkpoint;
  tie-breaking seeds match within pair; validation cannot mutate training RNG.
- Random-trading control probability comes from validation trading frequency,
  not test outcomes. This matches a frequency target, not realized volume.
- Report active-minus-frozen and frozen-minus-no-trade displacement contrasts.
  Student-t intervals use the ten policy means, conditional on the fixed ten
  test tapes. They are not unconditional market-population guarantees.
- Finite-grid response screen requires recorded visits for every action;
  absence of support or constant response causes abstention. No grid regression
  certifies a full-state positive-memory architecture or spectral radius.
- No model choice/hyperparameter changes after looking at corrected evaluation.
  Failed runs retained; runner refuses to reuse its output directory.

## Other repairs

Episode-level endpoint inference must enforce its sampling/design contract.
Chronological dynamics cannot use shuffled observations as a trajectory.
Empirical regression rows must regenerate statistics, with in-sample and
out-of-sample claims separated. Gate24 impact units, halt behavior, cash
transfers and source provenance require explicit correction. All previous
unsupported numbers are either withdrawn or labeled legacy, never silently
pooled with corrected results. Proof boundary qualifications and exact-witness
plots must agree with executable algebra.

## Completion boundaries

Local verification is not external review, novelty confirmation, real-market
execution validation, or publication acceptance. Those gates remain open.
