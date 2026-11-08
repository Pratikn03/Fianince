# P7S: does stress reveal what calm prices hide? (DRAFT plan, not registered)

*Drafted 8 November 2026 for the author's approval. **No data have been requested, downloaded or looked at for this
plan.** Nothing below is registered until the author approves it and the final version is committed with a SHA-256
before any outcome data are collected.*

## 1. Question and theory

The core paper's Section 7 makes a two-layer prediction for markets whose feedback traders face position limits:

- **Calm layer (Theorem 7.2, Proposition 7.6).** While traders are inside their limits, prices move as in the linear
  model. How close traders are to their limits does not change the price response to ordinary moves. The one leak is
  through informed dealers, and it is exponentially small.
- **Stress layer (Theorem 7.4).** Moves large enough to push traders to their limits do respond differently according
  to how close the traders are to their limits.

**What the test can and cannot show.** The theory's capacities and leverages are not observed. The test therefore
checks the qualitative two-layer pattern with a proxy for "proximity to limits". It is not a test of the
identification theorem.

## 2. Data (choose one, author decision)

| Option | Source | Proximity proxy | Pros | Cons |
|---|---|---|---|---|
| **A (recommended)** | Binance USDT-margined perpetuals: public daily files of 5-minute klines and 5-minute "metrics" (open interest, top-trader and global long/short ratios, taker volume ratio) | Open-interest value relative to its trailing 30-day maximum | Free, high frequency, and the period can be **prospective** (data that do not yet exist at registration) | Proxy measures positions, not limits. The same venue as E8–E23, so the period must be new |
| B | CFTC Commitments of Traders (managed money) plus exchange margin changes | Managed-money net position relative to its 3-year maximum, and margin increases | Positions of trend-following funds (CTAs); regulated data | Weekly; margin history must be compiled by hand; few stress events |
| C | Hyperliquid on-chain positions, with leverage and liquidation prices | Distance of open positions to their liquidation prices | The closest match to the theory: limits are directly visible | **Must not be analysed before 2026-12-10** (standing H1 rule), and it may overlap the H1 study. At most a later replication |

**Before registration:** a schema probe that downloads **one day of metrics files** and checks only their columns,
not outcomes. That needs separate approval, as earlier schema probes did.

## 3. Design (written for Option A)

- **Universe.** The 30 USDT perpetuals with the largest average daily volume over 2026-08-01 to 2026-10-31. The list
  is fixed and hashed at registration.
- **Periods.**
  - *Development* (2026-08-01 to 2026-10-31): only to fix per-symbol thresholds (the return percentiles and the
    proximity terciles) and to run a power check. The October 2026 Binance data were used by E20 for a different
    statistic; this is disclosed.
  - *Holdout* (2026-11-16 to 2027-02-14): **prospective**. None of these data exist at registration. It is opened
    once, after the executor is frozen.
- **Proximity state.** Π_t = open-interest value divided by its maximum over the trailing 30 days, at 5-minute
  resolution. "High" and "low" are the top and bottom terciles of Π, with thresholds per symbol from development.
- **Moves.** 5-minute log returns r_t, normalized by their development-period standard deviation.
  - **Stress moves:** |r_t| at or above the symbol's 99th development percentile.
  - **Calm moves:** |r_t| between the 50th and 80th percentiles.
- **Response.** The cumulative return over the next 60 minutes, multiplied by sign(r_t): positive is continuation,
  negative is reversal.
- **Statistics.** For each symbol, the average response in the high-Π state minus the low-Π state:
  - β_calm for calm moves;
  - β_stress for stress moves.

  The primary statistic averages over symbols: **DiD = mean over symbols of (β_stress − β_calm)**.
- **Inference.** A stationary block bootstrap by day, with mean block 5 days and B = 9,999, a fixed seed, and symbols
  resampled jointly.

## 4. Hypotheses and decision rule (fixed in advance)

- **H1, calm silence.** |mean β_calm| < E, tested by two one-sided tests at 5%. E is set from development data
  before registration, as the smallest calm difference that would contradict Proposition 7.6's bound at the
  observed noise level. The rule for setting E must be written down; E is not chosen by looking at outcomes.
- **H2, stress reveals.** DiD ≠ 0, two-sided, p < 0.05.
- **Verdict.**
  - *Supportive* if H1 holds and H2 rejects.
  - *Inconsistent* if calm moves already differ by more than E, which contradicts Theorem 7.2.
  - *Inconclusive* otherwise.
- **Sign** (secondary, reported but not tested as primary):
  - **Saturation** predicts weaker continuation when traders are near their limits (β_stress < 0).
  - **Forced deleveraging** predicts stronger continuation (β_stress > 0).

  The theory allows either, depending on what traders do at the limit.

## 5. Confounds and checks (pre-specified, reported whatever they show)

- **Volatility regimes.** High open interest may coincide with high volatility. Repeat with returns normalized by
  trailing 1-day realized volatility.
- **Placebo.** Shift Π by 30 days within each symbol. DiD should be about zero.
- **Volume.** Add terciles of taker volume as a second state; report the result.
- **Long/short crowding.** Replace Π by the absolute log top-trader long/short ratio; report the result.

## 6. Rules carried over from the project

- The executor is written and validated on simulated markets first: one with the two-layer property and one without.
- The holdout is run once. Failures are reported as they come out, and nothing is redefined after the fact.
- No Hyperliquid data before 2026-12-10. Burned days do not apply (TWSE, TPEx and NSE are not used).
- The result is reported in the paper whatever it says, with the readout fixed before the holdout is opened.

## 7. Decisions needed from the author before registration

1. **Data:** option A, B or C.
2. **Proxy:** Π (open interest relative to its 30-day maximum), or another one.
3. **Equivalence margin:** approve the method for setting E.
4. **Holdout window:** approve the prospective window (2026-11-16 to 2027-02-14). The result would then not exist
   before mid-February 2027.
5. **Schema probe:** approve a one-day schema probe of the metrics files, columns only.
