# Publication Packet & Master Submission Checklist

**Manuscript Title:** *From Human Markets to Machine Markets: Feedback Stability, Auditable Memory, and Financial Constraints*  
**Authors:** Pratik Niroula and Prashant Niroula  
**Target Journals:** *The Journal of Finance* (JF) / *Journal of Financial Economics* (JFE) / *The Review of Financial Studies* (RFS)  
**Primary Submission Manuscript:** `Machine_Markets_JF_Submission.pdf` (Strictly 48 pages exact, 12pt, 1.5 line spacing, 1-inch margins, 90-word abstract)  
**Unabridged Technical Archive / Internet Appendix:** `Machine_Markets_JF_Submission_Full_20261006.pdf` (72 pages, containing all 29 tables, 10 technical appendices, and workspace provenance)  
**Verification Standard:** Cryptographic lineage ledger across 29 table blocks and 3,219 table cells (`check_lineage_receipt.py`) with zero manual literals  
**Regression Test Suite:** 35 / 35 tests passing (`pytest research_extension/gap_closure_20261006/`)  

---

## 1. Submission Artifact Inventory & SHA-256 Digests

| Artifact | File Path | Format / Length | SHA-256 Digest | Role in Submission |
| :--- | :--- | :---: | :--- | :--- |
| **Primary Submission Paper** | `Machine_Markets_JF_Submission.pdf` | PDF (48 pp. exact) | `3739d00ea516e2bb108d1a17367f102b3157a06a0f4a13b810cf55d6ecdb37f7` | Core submission manuscript for JF / JFE / RFS |
| **External Review Freeze** | `Machine_Markets_External_Review_Freeze.pdf` | PDF (48 pp. exact) | `3739d00ea516e2bb108d1a17367f102b3157a06a0f4a13b810cf55d6ecdb37f7` | Identical frozen reference copy |
| **Unabridged Master Archive** | `Machine_Markets_JF_Submission_Full_20261006.pdf` | PDF (72 pp.) | `2104487739b8bebb0d656938dd872346b95a7758f2056822c661e972d0bebf67` | Complete technical monograph & Internet Appendix |
| **Cover Letter** | `submission/SUBMISSION_BUNDLE/COVER_LETTER.md` | Markdown | Verified | Editorial submission letter |
| **Authorship & Disclosures** | `submission/SUBMISSION_BUNDLE/DISCLOSURES.md` | Markdown | Verified | Ethics, conflict of interest, and data disclosures |
| **Lineage Ledger Audit** | `research_extension/gap_closure_20261006/check_lineage_receipt.py` | Python 3.11 | Verified | 29 tables, 3,219 cells verified against disk data |
| **Delivery Receipt** | `research_extension/gap_closure_20261006/final_delivery_receipt.json` | JSON | Verified | Authoritative delivery and integrity hashes |

---

## 2. Editorial Summary & Headline Contributions

The submission manuscript is organized around a single central economic and regulatory question:
> *"Can observable market data identify destabilizing adaptive feedback, when does that feedback become financially dangerous, and what information is fundamentally missing from public surveillance data?"*

1. **Contribution 1 — Identification Limits and Mandatory Surveillance Abstention:**  
   - Public market price–flow feeds identify only merged rate–weight transfer functions; individual algorithmic cohorts sharing adaptation rates cannot be distinguished from public price feeds (Theorem 2.1).  
   - Detecting heterogeneity between two symmetric cohorts whose adaptation rates differ by $\delta$ requires active probing budgets scaling as $\Omega(\delta^{-4})$ under Le Cam minimax limits (Theorem 2.3).  
   - Finite observation windows force an explicit mandatory abstention layer $\mathcal{B}_T = (1 - \epsilon_T, 1 + \epsilon_T)$ around the critical unit stability boundary where no bounded-error binary classification is possible (Theorem 2.5).

2. **Contribution 2 — High-Frequency Empirical Evidence and Natural Experiment:**  
   - 768 asset-days ($66.3 \times 10^6$ 1-second transitions) on Binance Spot: baseline feedback is consistently small, positive, and strictly subcritical ($\hat{Q} \approx 0.008, \hat{S} \approx 0.92 < 1.0$).
   - Dynamic robustness: reduced-form estimates are numerically similar under minimum-distance covariance matching ($Q_{\text{MD}} = 0.0086$), while the pooled overidentifying restrictions reject the parsimonious linear specification ($J = 73.0, df = 4, p < 0.001$), and Rigobon heteroskedasticity identification reveals negative contemporaneous buffering ($Q_{\text{Rig}} = -0.0191$).  
   - Flagship Natural Experiment: July 8, 2022 Binance zero-fee schedule overhaul ($N=192$ panel). Eliminating taker fees sparked a $+75.01\%$ volume surge with no detectable change in closed-loop feedback persistence ($\hat{\beta}_3 = -0.00186, p = 0.547$, permutation $p = 0.750$), remaining strictly subcritical.
   - Out-of-Sample Regime Evaluation (Table 29): 2-state Markov switching models evaluated across 7 chronological out-of-sample expanding window test dates yield MSE difference 95% confidence intervals that uniformly span zero, refuting the legacy 62.7-fold regime bifurcation claim.

3. **Contribution 3 — Financial Fragility, Non-Normal Amplification, and Dealer Solvency:**  
   - Local price stability ($\rho(J) < 1$) does not prevent dealer balance-sheet exhaustion under non-normal transient magnification. Generically, $J J^\top - J^\top J \neq 0$ under asymmetric price-impact and flow memory.  
   - The exact safe shock radius for a leveraged dealer is governed by peak transient magnification: $r^*_{\text{exact}} = B / \sup_{t \ge 0} \|C J^t\|_2$, bounded by the Kreiss constant: $\frac{B}{e n \mathcal{K}(J)} \le r^*_{\text{exact}} \le \frac{B}{\mathcal{K}(J)}$ (Theorem 2.6).  
   - Funded dealer simulations (19,200 paths) separate transient magnification from persistent-flow accumulation, demonstrating that stable eigenvalues alone do not guarantee capital solvency under non-normal execution dynamics.

---

## 3. Verification & Reproducibility Certification

```text
Compilation Status:     SUCCESS (48 pages exact core / 72 pages unabridged archive)
Abstract Constraint:    90 words (Strictly <= 100 words)
Format Constraint:      12pt Times, 1.5 line spacing, 1-inch margins (Strict 48-page limit)
Overfull H-boxes:       0
Undefined References:   0
Unit/Regression Tests:  35 / 35 tests passing (0.82s)
Lineage Audit Ledger:   29 table blocks, 3,219 cells verified (0 mismatches)
Input Checksums:        192 T9 archives + 9 raw input files SHA-256 verified
Local Gap Status:       26 / 26 local gaps closed (100.0%)
Overall Status:         96.3% (26 of 27 items closed; G27 external peer review pending)
```
