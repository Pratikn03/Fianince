# P1F amendment A1: prospective window (registered 15 November 2026 UTC)

**Approved by the author on 14 November 2026, US Central ("approve A").** Pushed in a commit of its own on
15 November 2026 (UTC), before the window opens on 16 November 2026 (UTC).

## Why

The first run (14 November 2026) was **VOID**: 0 of 30 symbols met the coverage rule. A diagnostic on two days
outside the window showed that Binance's 2022 metrics files leave both top-trader ratios empty in every row. No
outcome statistic was computed. The original specification and its result stand as recorded.

## What changes

| Item | Original | A1 |
|---|---|---|
| Window | 2022-03-01 to 2022-04-29 (retrospective) | **2026-11-16 to 2027-01-14 (prospective; these data do not exist at registration)** |
| Training / test | first / last 30 days | first / last 30 days: 2026-11-16 to 2026-12-15 / 2026-12-16 to 2027-01-14 |
| Universe volume month | February 2022 | October 2026 |
| Universe: listing | file presence on first and last day | also monthly 1-day kline files for August and September 2026 (listed about 90 days before the window) |
| Universe: fields | not checked | **top-trader position, top-trader account and all-account ratios filled in at least 90% of rows on 2026-11-14**, a day outside the window and unused by any test |
| Earliest run | none | **2027-01-16 (UTC)**: the executor stops before downloading anything if run earlier |
| Executor | `p1f_executor.py` | `p1f_executor_A1.py`, identical except for the rows above |
| Notebook / counter | `P1F_Forecast_Irrelevance_Colab.ipynb` / `P1F_unlocks.json` (opens = 1, void) | `P1F_A1_Colab.ipynb` / `P1F_A1_unlocks.json` (opens = 0) |

Everything else is unchanged: features, pooled estimation, margin δ = 0.005 (0.002 secondary), bootstrap, verdict
wording, A1, the A3 power gate, coverage rule and secondary results.

## Overlap, disclosed

- **P7S replication.** The window lies inside the P7S replication window (2026-11-16 to 2027-02-14). The two
  tests ask different questions and use different features, and they may share symbols, so they are not
  independent.
- **Hyperliquid.** H1 uses a different venue.

## Checks before registration

`research_extension/irrelevance/executor_test/` holds three offline tests on synthetic files:
- **Date guard:** stops the run before any download.
- **Universe rule:** excludes a symbol with empty top-trader fields and a recently listed symbol, and picks the 30
  largest eligible symbols.
- **Verdicts:** "irrelevant" on null data (ΔR² = −0.013%) and "relevant" on informed data (ΔR² = +0.75%).
