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
