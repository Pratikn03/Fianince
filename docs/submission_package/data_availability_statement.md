# Data and Code Availability Statement

**Research Program:** Machine Markets  
**Manuscripts:**
- Paper 1: *Auditable Memory and Financial Identification Limits in Electronic Limit Order Books*
- Paper 2: *From Human Markets to Machine Markets: Transient Amplification, an Exact Depth Condition, and a Maximal Pre-Trade Guard*

---

## 1. Code Availability

All code required to reproduce the theoretical, numerical, simulation, and econometric results in both manuscripts is permanently archived in the official repository:
- **Repository:** `https://github.com/Pratikn03/Fianince`
- **License:** Open Academic / Research Reproduction License
- **Programming Languages:** Python (3.11+), Lean 4 (v4.34.1 with Mathlib), POSIX Shell, GNU Make, LaTeX.

### Reproduction Command
A complete, non-interactive clean-environment reproduction of all data-free theorems, unit tests, numerical receipts, LaTeX manuscript compilations, and real-data result ledgers can be executed in a single command:
```bash
SKIP_LEAN=1 sh reproduce_paper_suite.sh
```
To additionally build the complete Lean 4 formalization and execute the automated axiom audit:
```bash
cd research_extension/current_manuscript_lean_20261008
lake exe cache get
lake build
lake env lean AxiomAudit.lean
```

---

## 2. Data Availability and Provenance

### A. Publicly Available Market Data
1. **Binance Public Historical 1-Second Spot and Futures Archives:**
   - **Source:** Official public archive at `https://data.binance.vision`.
   - **Coverage:** 1-second price and aggressor-signed trade volume bars for `BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `BNBUSDT`, `ADAUSDT`, `XRPUSDT`, `DOGEUSDT`, `MATICUSDT`.
   - **Historical Stress Dates Analyzed:**
     - May 19, 2021 (Crypto Flash Crash)
     - May 9, 2022 (Terra/LUNA Algorithmic Stablecoin Collapse)
     - November 8, 2022 (FTX Solvency Crisis)
     - March 11, 2023 (SVB/USDC Depeg Crisis)
   - **Verification:** All downloaded raw files are verified against official SHA-256 checksums published by Binance.

2. **Binance Venue Rules and Margin Schedules:**
   - USDⓈ-M maintenance-margin tiers, leverage brackets, and fee schedules archived via the Internet Archive Wayback Machine (snapshots from December 9, 2022; January 9, 17, 20, and 23, 2023). Complete URLs, snapshot timestamps, and exact bracket boundaries are codified in `ceiling_suite/papers/recomputed/` and `venue_rule_calibration_20261010`.

3. **Bybit Public Microstructure Data:**
   - 10 thin cryptocurrency pairs across the 2023 observation sample, downloaded from official Bybit public market data APIs.

4. **US Equity TAQ / CRSP Data:**
   - 23 small-capitalization US equities analyzed in the cross-asset validation panel. Data accessible via Wharton Research Data Services (WRDS) under standard institutional subscription.

### B. Pre-computed Result Artifacts
To ensure complete transparency and facilitate replication without requiring multi-day downloads of multi-gigabyte tick data:
- All econometric point estimates, standard errors, $t$-statistics, and bootstrap confidence intervals are permanently committed in JSON format in `results/provenance/` and `ceiling_suite/papers/recomputed/`.
- Every empirical claim in Paper 2 is audited by `verify_paper_numbers.py`, checking 74 pre-registered numbers with 0 discrepancies against the committed result files.

### C. Simulation Checkpoints
- All neural network weights, RLS covariance matrices, profit-gradient parameters, and tabular Bellman Q-tables are serialized in JSON format in:
  `ceiling_suite/papers/recomputed/learner_checkpoints/`
  These checkpoints allow exact evaluation of learned policies without stochastic retraining divergence.

---

## 3. Human Subjects and Regulatory Compliance
This research involves exclusively computational modeling, mathematical proof formalization, and econometric analysis of public, anonymized market data. No human subjects, survey instruments, or proprietary personal data were involved.
