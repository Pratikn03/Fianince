# P1X: does a trader class have the same memory in every market? (DRAFT: not approved, not registered)

Drafted 12 November 2026 by an AI system for the authors' approval. Nothing here is in force. No data have been read.

## Why

The pooling theorem (core `thm:pool`) rests on one premise: an algorithm's memory is the same in every market it
trades, while its participation varies. That premise is testable with public tagged data. The CFTC Commitments of
Traders (disaggregated) report weekly positions of "managed money" (mostly trend-following funds) in many futures
markets.

## Design (to be fixed before any data are read)

- Data: CFTC disaggregated futures-only reports, weekly, all markets with continuous reporting; a development period
  and a holdout period fixed in advance; settlement prices for the same markets.
- For each market, estimate the managed-money memory rate r_j and weight w_j from the tagged regression of the
  paper (`prop:tagged`) with lagged-price instruments.
- H1 (premise): the r_j are equal across markets (test of homogeneity, with a pre-set equivalence margin).
- H2 (heterogeneous participation): the w_j differ across markets (rank of the participation pattern > 1).
- H3 (consequence): a pooled estimator with common r predicts holdout flows at least as well as market-by-market
  estimators.

## Before registration

1. The authors approve or change this draft (markets, periods, margin, instruments).
2. A simulation check like those of P7S and P1K: size and power on simulated markets where the premise holds and
   where it fails. P1K's two designs failed this step; this one must pass it before anything is registered.
3. Specification, executor and notebooks hashed and committed before any data are read. Each test runs once.

Earlier CFTC tests of the full working paper used the same reports for other questions; the overlap must be stated.

## 9. Simulation check (12 November 2026): both designs fail; not registered

Script `research_extension/cross_market/p1x_design_sim.py` (no real data read). Simulated managed-money positions in
30 markets, 480 development and 480 holdout weeks, positions unrelated to trends persistent (AR(1), 0.9), trend share
R2 of weekly flow variance 0.1 or 0.25. Premise test H1: common memory rates (R_K) against market-specific rates
(U_K) on the holdout, residual block bootstrap from the fitted R_K, 199 draws, reject at 5%. H2: rank of the weights
above one. Criteria fixed before running: H1 rejects at most 7.5% under the premise and at least 80% under a large
violation (each market's half-lives multiplied by exp(N(0,1))); H2 at least 80% when weights vary, at most 7.5% under
rank one. 100 replications per scenario. The first runs of both designs were stopped at the 30-minute limit after the
R2 0.10 scenarios (printed output kept in `research_extension/cross_market/results_p1x/`); the R2 0.25 scenarios were
run separately to completion.

| Scenario | Design 1: K by BIC, H1 / H2 reject | Design 2: K = 3 fixed, H1 / H2 reject |
|---|---|---|
| R2 0.10, premise, two classes | 10% / 4% | 1% / 4% |
| R2 0.10, premise, three classes | 25% / 8% | 2% / 8% |
| R2 0.10, half-lives spread x exp(0.5 N) | 33% / 12% | 1% / 12% |
| R2 0.10, half-lives spread x exp(N) | 62% / 42% | 0% / 42% |
| R2 0.10, rank-one weights | 8% / 7% | not reached (run stopped at its time limit) |
| R2 0.25, premise, two classes | 27% / 6% | 1% / 6% |
| R2 0.25, premise, three classes | 66% / 22% | 2% / 22% |
| R2 0.25, half-lives spread x exp(0.5 N) | 66% / 46% | 1% / 46% |
| R2 0.25, half-lives spread x exp(N) | 100% / 91% | 1% / 91% |
| R2 0.25, rank-one weights | 8% / 6% | 0% / 6% |

Design 1 picks one memory class in every replication, so under the premise each market's single fitted memory
reflects its own mix of classes and the test rejects a true premise 10-66% of the time. Design 2 allows three
classes; it no longer rejects a true premise, but it also almost never detects a false one, because three free
memory rates per market absorb the violation. H2 has power only when the premise is badly violated. Both designs
fail their criteria. The reason is the paper's own: within an untagged class, memories that differ by a factor of
two cannot be resolved from a few hundred weekly observations. Weekly class positions aggregated over many funds
cannot test the pooling premise. A test needs positions by fund or by strategy across markets, which are not public.
Decision recorded by the AI system for the authors: P1X is not registered.
