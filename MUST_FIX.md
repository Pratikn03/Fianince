# MUST-FIX ITEMS: PRE-CIRCULATION COMPLIANCE AUDIT

**Audit Date**: October 5, 2026  
**Auditor**: Antigravity Quantitative Verification Engine (Submission Hardening Cycle 6)  
**Status**: **ALL ITEMS AUDITED, REPAIRED, AND VERIFIED (100% COMPLETE)**

---

## 1. Overview

This document tracks all non-fatal but critical technical, terminological, typographical, and presentation items required to harden `Machine_Markets_JF_Submission.pdf` prior to external circulation to top-tier finance scholars and journal submission.

---

## 2. Item-by-Item Remediation Ledger

| ID | Domain | Issue Description | Initial State | Remediated State | Verification Status |
|---|---|---|---|---|---|
| **MF-01** | **Econometrics** | Lyapunov estimator terminology | Referred to as "SMM" | Renamed to **Analytical Minimum-Distance (MD) Lyapunov Covariance Matching** ($Q_{\text{MD}}$) | **VERIFIED** |
| **MF-02** | **Econometrics** | Order Flow Imbalance (OFI) characterization | Described as an "instrument" | Renamed to **Depth-aware robustness proxy** | **VERIFIED** |
| **MF-03** | **Causal Inference** | Binance July 2022 DiD conclusion | Labeled as "Structural Invariance" | Disciplined to **No Detectable Feedback Response (Null)** | **VERIFIED** |
| **MF-04** | **Microstructure** | Maker liquidity mechanism | Risk of claiming unmeasured depth surge | Disciplined to **Consistent with offsetting endogenous liquidity provision** | **VERIFIED** |
| **MF-05** | **Theory** | Proposition 2.8 exact radius logic | Inferred exact safe radius contraction solely from Kreiss | Restated to distinguish Kreiss bound from exact radius; proved entrywise monotonicity for $C \ge 0$ | **VERIFIED** |
| **MF-06** | **Theory** | Theorem 2.5 local-to-unity scaling | Prior draft mentioned $T^{-1/2}$ near unit root | Corrected to Phillips (1987) $S = 1 \pm c/T$ yielding boundary layer $\epsilon_T = \mathcal{O}(T^{-1})$ | **VERIFIED** |
| **MF-07** | **Empirical** | TVAR regime differential interpretation | Risk of claiming feedback slope explosion | Accurately stated: slope difference is modest ($\Delta \hat{q} = +0.0694, t=0.94, p=0.35$), while volatility explodes $62.70\times$ ($p<10^{-300}$) | **VERIFIED** |
| **MF-08** | **Policy** | Kreiss pre-trade rate gating dimensional formula | Missing price impact coefficient $\kappa$ in earlier formula | Formula strictly dimensioned: $R_{\max}(t) \le \frac{\gamma L E_{\text{MM}, t}}{\kappa \tau M_C} D_t$ | **VERIFIED** |
| **MF-09** | **Tables** | Table 14 reconciliation with Tables 3 & 4 | Discrepancies in $L=0$ and $L=30$ estimates | Exact match to 4 decimal places across all cells | **VERIFIED** |
| **MF-10** | **Formatting** | Page budget enforcement | Spilled to 49 pages | Compacted Section 7 inline enumerations: **exactly 48 pages** | **VERIFIED** |
| **MF-11** | **Formatting** | Overfull horizontal boxes | 99.1 pt overfull in DiD table | Added `\resizebox{0.88\textwidth}{!}`: **0.0 pt overfull hboxes** | **VERIFIED** |
| **MF-12** | **Formatting** | Undefined citations and cross-references | Risk of broken keys | Compiler log confirms **0 undefined references/citations** | **VERIFIED** |
| **MF-13** | **Abstract** | Word count limit compliance | Required $\le 100$ words | Exactly **98 words** in source (85 words in PDF) | **VERIFIED** |
| **MF-14** | **Replication** | Multi-path bundle synchronization | Mismatched PDF versions across folders | Byte-for-byte identical PDF (`03b812a...`) across all 3 directories | **VERIFIED** |

---

## 3. Detailed Verification of Completed Actions

### MF-01 & MF-02: Structural Estimator & Regressor Terminology
- Inspected `paper/Machine_Markets_JF_Submission.tex` lines 106, 169, 652--666, 688, 731, 749, 754.
- In all instances, "Simulated Method of Moments (SMM)" has been replaced by "analytical minimum-distance Lyapunov covariance matching" ($Q_{\text{MD}}$).
- In line 688, "instrument for transaction order flow" has been replaced by "depth-aware robustness proxy for transaction order flow".

### MF-03 & MF-04: Causal & Mechanism Discipline
- Table 5 (`paper/generated/natural_experiment_table.tex`) conclusion row updated to:
  `Statistical Conclusion & \textbf{No Detectable Response (Null)} & \textbf{No Detectable Response (Null)} \\`
- Abstract and Conclusion updated to state: "with no detectable change in closed-loop feedback persistence, which remained strictly subcritical."
- Text explicitly states that order book depth was not observed directly on proprietary tapes, and frames the stability as "consistent with offsetting endogenous liquidity provision."

### MF-05: Proposition 2.8 Repair
- Proposition 2.8 restated in `paper/Machine_Markets_JF_Submission.tex` lines 594--601.
- Supported by `proposition_2_8_redteam.md`, `crossimpact_counterexample_search.csv` (103,340 trials, 0 counterexamples), and `crossimpact_grid.csv`.

### MF-10, MF-11, MF-12, MF-13: Strict Editorial Constraints
- `scripts/generate_jf_paper.py` executed: compiled cleanly to **exactly 48 pages**.
- `grep -c "Overfull" paper/Machine_Markets_JF_Submission.log` returns **0**.
- `grep -c -i "undefined" paper/Machine_Markets_JF_Submission.log` returns **0**.
- Abstract word count verified at **98 words** (source) and **85 words** (extracted PDF text).

---

## 4. Certification
All MUST-FIX items are completely repaired, verified against the source code, and certified for submission.
