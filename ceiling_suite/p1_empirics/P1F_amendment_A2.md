# P1F amendment A2: purge labels at the training/evaluation boundary (registered 20 November 2026 UTC)

**Approved by the author on 20 November 2026, US Central** (chat: "lets do leakage free"). Pushed in a commit of its
own on 20 November 2026 (UTC). From this commit, the registered P1F test is the specification as amended by A1 and A2,
run once with `P1F_A2_Colab.ipynb` and `p1f_executor_A2.py`; its counter is `P1F_A2_unlocks.json`. The A1 executor and
notebook are superseded before any run: `P1F_A1_unlocks.json` stays at 0, and the A2 notebook stops if it is not.

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

- The window opened on 16 November 2026. Binance has published window files daily since then, but none has been
  fetched or read: the A1 executor refuses to download before 16 January 2027, and no other code in the repository
  reads these files.
- The changes were decided from code review and synthetic data only. They do not depend on any window outcome.
- Hashes of the specification, both amendments, the A2 executor and the A2 notebook are in `P1F_A2_spec.json`.

## Simulation check (offline, synthetic data only)

`research_extension/irrelevance/executor_test/test_p1f_executor_A2.py` runs the A2 executor on the synthetic 30-symbol,
60-day worlds used to check A1 (`P1F_A2_offline_test.txt`):

| Executor | pandas | NULL world | INFORMED world | Power gate |
|---|---|---|---|---|
| A1 (registered before A2) | 2.2.3 | irrelevant, ΔR² −0.00013 | relevant, ΔR² 0.00745 | 1.00 |
| A2 | 2.2.3 | irrelevant, ΔR² −0.00012 | relevant, ΔR² 0.00746 | 1.00 |
| A2 | 3.1.1 | irrelevant, ΔR² −0.00012 | relevant, ΔR² 0.00746 | 1.00 |
| A1 | 3.1.1 | stops with a unit-cast error | — | — |

## What A2 does not change

- The independent review also proposed a different inference: a moving-block bootstrap and a two-sided equivalence verdict.
- That candidate failed 7 of the 12 cells of its own calibration grid, so it is **not** adopted here.
- A2 is the minimal repair.
