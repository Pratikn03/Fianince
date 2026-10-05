# Publication Packet & Master Submission Checklist

**Manuscript Title:** *From Human Markets to Machine Markets: Feedback Stability, Auditable Memory, and Financial Constraints*  
**Authors:** Pratik Niroula and Prashant Niroula  
**Primary Target Venues:** *The Journal of Finance* (JF) / *Journal of Financial Economics* (JFE) / *The Review of Financial Studies* (RFS)  
**Primary Submission Manuscript:** `Machine_Markets_JF_Submission.pdf` (48 pages, 12pt, 1.5 line spacing, 97-word abstract)  
**Internet Appendix / Supplement:** `paper/Machine_Markets_Mathematical_Supplement.pdf` (44 pages)  
**Comprehensive Technical Monograph:** `paper/Machine_Markets_Final_Integrated_Paper.pdf` (80 pages)  
**Canonical Master Archive:** `Machine_Markets_Combined_Master.pdf` (124 pages total)  
**Formal Verification:** 216 Lean 4 Theorems verified with 0 `sorry` (`lean_proofs/AxiomAudit.lean`)  
**Provenance Ledger:** 80 / 80 Claims Verified (`scripts/provenance_ledger.py`)  
**Test Suite:** 622 / 622 Tests Passing (`pytest tests/`)  
**Canonical Benchmark Data:** FI-2010 NASDAQ Nordic L2 (`empirical_pipeline/fi2010/data/data.csv`, SHA-256: `0fac513a408b4dd803373860831874d3423a89f41fbaf13323f8a25a3019f3eb`, CC0 1.0)  

---

## 1. Submission Artifact Inventory

| Artifact | File Path | Format / Size | Status | Role in Submission |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Submission Paper** | `Machine_Markets_JF_Submission.pdf` | PDF (48 pp., 12pt, 1.5 spacing) | Verified (0 undefined refs, 97-wd abstract) | Main Manuscript for JF / JFE / RFS |
| **Internet Appendix** | `Machine_Markets_Mathematical_Supplement.pdf` | PDF (44 pp.) | Verified (0 undefined refs) | Online Companion / Mathematical Supplement |
| **Comprehensive Monograph** | `Machine_Markets_Final_Integrated_Paper.pdf` | PDF (80 pp.) | Verified (0 undefined refs) | Technical Reference / Full Treatise |
| **Combined Master Volume** | `Machine_Markets_Combined_Master.pdf` | PDF (124 pp.) | Verified (0 warnings) | Complete Unified Archive |
| **Formal Lean 4 Suite** | `lean_proofs/Proofs/` | 11 submodules | 216 Theorems, 0 sorry | Mathematical Soundness Verification |
| **Lean 4 Axiom Audit** | `lean_proofs/AxiomAudit.lean` | Lean 4 script | 100% sound (0 axioms) | Machine-Checked Axiom Audit |
| **Theorem-Code Bridge** | `scripts/verify_theorem_code_bridge.py` | Python 3.11 | 36 / 36 Environments Mapped | Cross-Validation Bridge |
| **Provenance Claims Ledger** | `scripts/provenance_ledger.py` | Python 3.11 | 80 / 80 Claims Verified | Empirical & Mathematical Audit |
| **Cover Letter** | `submission/SUBMISSION_BUNDLE/COVER_LETTER.md` | Markdown / Text | Submission Ready | Editorial Submission Letter |
| **Authorship & Disclosures** | `submission/SUBMISSION_BUNDLE/DISCLOSURES.md` | Markdown / Text | Submission Ready | Ethics, Conflicts & Data Disclosures |
| **Replication Guide** | `README.md` & `reproduce.py` | Python CLI | One-Click Reproducible | Public Replication Suite |

---

## 2. Editorial Focus & 3 Headline Contributions

The submission manuscript is structured around a single central economic question:
> *"Can observable market data identify destabilizing adaptive feedback, when does that feedback become financially dangerous, and what information is fundamentally missing from public surveillance data?"*

1. **Contribution 1 — Identification Limits and Mandatory Surveillance Abstention:**  
   - Public market data identify only merged rate–weight transfer functions; individual cohorts are non-identifiable without audited internal state.  
   - $\delta^{-4}$ active probing lower bound (Le Cam minimax).  
   - Mandatory surveillance abstention layer $\mathcal{B}_T = (1 - \epsilon_T, 1 + \epsilon_T)$ under finite sample horizons.

2. **Contribution 2 — High-Frequency Empirical Evidence and Natural Experiment:**  
   - 768 asset-days ($66.3 \times 10^6$ 1-second transitions): $\hat{Q} \approx 0.008, \hat{S} \approx 0.92 < 1.0$.  
   - Liquidity depletion surge: $+11.1\%$ price impact, $62.7\times$ volatility explosion in TVAR/MS-VAR.  
   - Independent cross-market replication in regulated equities (NASDAQ Nordic FI-2010).  
   - Flagship Difference-in-Differences around the July 8, 2022 Binance Zero-Fee schedule overhaul ($N=192$, parallel trends $p=0.835$).

3. **Contribution 3 — Financial Fragility vs. Price Stability:**  
   - Price stability ($\rho(J) < 1$) does not prevent dealer balance-sheet exhaustion under non-normal transient amplification.  
   - Exact safe shock radius $r^*_{\text{exact}} = B / M_C$ with Spijker–Kreiss bounds $\frac{B}{e n \mathcal{K}(J)} \le r^*_{\text{exact}} \le \frac{B}{\mathcal{K}(J)}$.  
   - Low-frequency variance inflation $(1 - S)^{-2}$ expands order flow variance by $4.0\times$, accumulating dealer inventory to regulatory margin breach in 69.1% of trials inside the spectrally stable regime.

---

## 3. The 10-Study Empirical Program

1. **Baseline High-Frequency Feedback Panel:** 768 asset-days on Binance Spot (2021--2024), $\hat{Q} = 0.0082$, $\hat{S} = 0.921$.
2. **Cross-Asset Heterogeneity:** Panel across 8 major assets (BTC, ETH, SOL, BNB, ADA, DOGE, XRP, LTC).
3. **Flagship Natural Experiment:** DiD around July 8, 2022 Binance Zero-Fee shock ($N=192$).
4. **Dynamic Event Study:** Multi-period lead-lag event study confirming parallel pre-trends ($F=0.42, p=0.835$).
5. **Cross-Venue Identification:** Binance vs. Coinbase lead-lag transmission and Granger causality.
6. **Forecast Error Variance Decomposition (FEVD):** Global crypto price variance decomposition.
7. **Liquidity-State Dependence (TVAR & MS-VAR):** High-spread/low-depth non-linear feedback and volatility expansion.
8. **Microstructure of Historical Flash Crashes:** E-mini S&P 500 (May 6, 2010) and U.S. Treasuries (Oct 15, 2014) TAQ depth depletion.
9. **Cross-Market Replication in Regulated Equities:** Benchmark evaluation on NASDAQ Nordic FI-2010 Level-2 LOB data.
10. **Funded Dealer Solvency Simulation:** 22,000 Monte Carlo paths tracking inventory exhaustion under $(1-S)^{-2}$ variance inflation.

---

## 4. Verification and Reproducibility Status

```text
Compilation Status:     SUCCESS (48 pages, 0 undefined references, 0 '??')
Abstract Constraint:    97 words (Strictly <= 100 words)
Format Constraint:      12pt Times, 1.5 line spacing, 1-inch margins (<= 60 page limit)
Lean 4 Mechanization:   216 Theorems, 0 sorry, 0 unproved axioms
Provenance Ledger:      80 / 80 claims verified
Pytest Test Suite:      622 / 622 tests passing
Submission Status:      100% COMPLETE & SUBMISSION READY
```
