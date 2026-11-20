# P1F amendment A2 (DRAFT, not registered): purge labels at the training/evaluation boundary

Status: **draft for author approval.** This draft is not part of the registration until the author approves it and it
is pushed with its hash record. Until then, amendment A1 and `p1f_executor_A1.py` remain the registered test, with
unlock counter `P1F_A1_unlocks.json` at 0.

## Why

An internal review of the A1 executor (15 November 2026) found that three training-side quantities use labels that
fall in the evaluation half:

| Arm | Where | What leaks |
|---|---|---|
| A2 (irrelevance) | `evaluate`: training rows run to `train_end - 1`, and the label of row t is the return at t+1 | The last training row's label is the first evaluation return |
| A3 (power gate) | `power_gate`: label standardization, and the gate's own test half, run to `train_end - 1` | The same evaluation return enters the gate |
| A1 (invisibility) | `a1`: training rows run to `train_end - 1`, with target N[t+8] − N[t] | The last eight training targets use positions from the evaluation half |

The leak is at most eight bars of a 1,440-bar training half per symbol, so its effect on any verdict is negligible.
A referee would still be right to call it leakage, and it costs nothing to remove before any window data are read.

## What changes (seven lines of `p1f_executor_A1.py`; nothing else)

1. `evaluate`: training mask `tmask[start:train_end]` becomes `tmask[start:train_end - 1]`.
2. `power_gate`: the standardization mask becomes `tmask[2 * bpd:train_end - 1]`.
3. `power_gate`: the gate's evaluation ends at `train_end - 1`. The synthetic feature is zeroed from `train_end - 1`, and the call becomes `evaluate(..., mid, train_end - 1, ...)`.
4. `a1`: `tr[train_end:] = False` becomes `tr[train_end - 8:] = False`.
5. Portability: the bar grid and the kline and metric time indexes are cast to nanoseconds (`unit="ns"`, `as_unit("ns")`).
   - Under pandas 2, which the A1 checks used, they already are nanoseconds, so nothing changes.
   - Under pandas 3, the A1 executor stops with a unit-cast error while building bars. That would void the run if Colab ships pandas 3 by January 2027.

The window (16 November 2026 to 14 January 2027), universe rule, structure check, date guard (no run before 16 January
2027), features, pooled regression, margins (δ = 0.005 primary, 0.002 secondary), bootstrap, verdict rules and readout
sentences are unchanged.

## Timing and data access

- The A1 executor refuses to download anything before 16 January 2027, so no one has read any window data.
- This draft was written on 20 November 2026. Window data have been published daily since 16 November, but none have been fetched or read.
- If approved, A2 must be pushed in a commit of its own, with SHA-256 hashes of this file, the A2 executor and its notebook, and a new counter `P1F_A2_unlocks.json` at 0.
- The A1 counter is then closed as "superseded by A2 before any run".

## Simulation check (offline, synthetic data only)

`research_extension/irrelevance/executor_test/test_p1f_executor_A2.py` runs the A2 executor on the synthetic 30-symbol,
60-day worlds used to check A1. The registered rule requires the same verdicts as A1: NULL gives irrelevant, INFORMED gives relevant, and the power gate passes. The results are recorded in `A2_offline_test.txt` next to this file.

## What A2 does not change

- The independent review also proposed a different inference: a moving-block bootstrap and a two-sided equivalence verdict.
- That candidate failed 7 of the 12 cells of its own calibration grid, so it is **not** adopted here.
- A2 is the minimal repair.
