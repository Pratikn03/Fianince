# MUST-FIX ITEMS: PRE-CIRCULATION COMPLIANCE AUDIT

**Audit Date**: October 5, 2026  
**Auditor**: Antigravity Quantitative Verification Engine (Submission Hardening Cycle 8)  
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
| **MF-14** | **Replication** | Multi-path bundle synchronization | Mismatched PDF versions across folders | Byte-for-byte identical PDF (`0637103...`) across all 3 directories | **VERIFIED** |
| **MF-15** | **Theory** | Single-cohort stability under signed feedback | Omitted lower Jury stability bound | Explicitly stated: $-\frac{(2-\eta)(1+a)}{\eta} < Q < 1 - a$ prevents oscillatory period-doubling explosion | **VERIFIED** |
| **MF-16** | **Theory** | Theorem 2.3 $z$-transform timing & realization | Missing factor $z$; $\eta=1$ included in states | Preserved contemporaneous update algebra with factor $z$; restricted minimal realization to dynamic $\eta \in (0, 1)$ | **VERIFIED** |
| **MF-17** | **Theory** | Closed-loop reduction lemma for $\delta^{-4}$ | $\Delta h_t$ evaluated on open-loop memory kernel | Proved closed-loop perturbation $H_\delta - H_0 = H_0 H_\delta z \Delta U_{\text{end}} = \mathcal{O}(\delta^2)$ in $\ell_1$ norm | **VERIFIED** |
| **MF-18** | **Theory** | Two-state to scalar local-to-unity reduction | Evaluated scalar AR(1) likelihood ratio | Proved Jordan spectral decomposition into scalar local diffusion + stationary nuisance mode $\mathcal{O}_p(T^{-1/2})$ | **VERIFIED** |
| **MF-19** | **Empirical** | Historical E-mini Flash Crash arithmetic | Conflicted $25\times$ impact with $0.0125$ feedback | Harmonized: $25\times$ depth collapse combined with momentum acceleration $q=0.0326$ yields implied $65.1\times$ surge to $0.8142$ | **VERIFIED** |
| **MF-20** | **Econometrics**| Latent vs return VAR stability boundary bridge | Latent $x_t = p_t - p_t^*$ vs return $x_t = 10,000 \Delta p_t$ | Added Remark showing $\det(I - J) = (1 - J_{22})(1 - S)$, establishing observational equivalence | **VERIFIED** |
| **MF-21** | **Claim Discipline**| Caption, cross-venue, and policy claims | Over-claiming phrases flagged in red team | Repaired Table 12 caption ("most closely matched by B3"), cross-venue VAR, FI-2010 replication, pre-trends, session resets | **VERIFIED** |

---

## 3. Detailed Verification of Completed Actions

### MF-15: Signed-Feedback Jury Stability Interval
- Updated Section 2.1: clarified that Schur stability is strictly equivalent to $S = a + Q < 1$ for positive-feedback economies ($Q \ge 0$), and stated the complete two-sided Jury stability interval $-\frac{(2-\eta)(1+a)}{\eta} < Q < 1 - a$ for signed feedback ($Q \in \mathbb{R}$).

### MF-16 & MF-17: Theorem 1 Timing, Realization Domain, and Closed-Loop Reduction
- Equation (243) specifies dynamic memory $\eta_i \in (0, 1)$.
- Proof of Theorem 1 Part 1 carries factor $z$ in $Y_i(z) = \frac{\eta_i z}{z - (1 - \eta_i)} X(z)$ and $H(z) = \frac{\kappa}{z - a - \kappa z \sum \frac{c_r}{z-r}}$, with dynamic minimal realization degree $1 + |\operatorname{supp}(\mathcal{M})|$.
- Proof of Theorem 1 Part 2 provides a formal reduction lemma establishing that bilateral symmetry $\bar{\eta} \pm \delta$ ensures the closed-loop resolvent perturbation satisfies $\|H_\delta - H_0\|_{\ell_1} \le C_H \delta^2$, yielding $T = \Omega(\delta^{-4})$ on the full closed-loop price output via Young's inequality and Le Cam's two-point bound.

### MF-18: Theorem 2 Jordan Spectral Reduction Lemma
- Proof of Theorem 2 decomposes the $2 \times 2$ structural system via Jordan spectral projection into a local-to-unity scalar diffusion mode $\xi_{1, t}$ plus a geometrically ergodic stationary nuisance mode $\xi_{2, t}$ satisfying $\sum \xi_{2, t}^2 = \mathcal{O}_p(T)$, establishing that the local asymptotic experiment is contiguous and statistically equivalent to the scalar Phillips (1987) experiment.

### MF-19: Historical E-mini Flash Crash Calibration Harmonization
- Section 5.1 harmonized all numbers: baseline price impact $\kappa_0 = 1.0$ (calm feedback $\hat{Q}_{\text{calm}} = 0.0125$), stressed impact $\kappa_{\text{crisis}} = 25.0$ due to $25\times$ depth collapse, and momentum feedback acceleration $q_{\text{crisis}} = 0.0326$, yielding implied crisis feedback $\hat{Q}_{\text{crisis}} = 25.0 \times 0.03257 = 0.8142$ (a $65.1\times$ total amplification over calm conditions), perfectly matching `equity_flash_crash_taq_results.json` and Figure 3.

### MF-20: Return VAR Observational Equivalence Bridge Remark
- Added formal Remark in Section 3.1 proving $\det(I - J) = (1 - J_{22})(1 - S)$, establishing that $S = 1.0$ is the exact unit-root stability boundary directly from the observable $2 \times 2$ return-flow VAR without requiring unobserved latent fundamentals.

### MF-21: Claim Discipline and Caption Sweep
- Table 12 caption: replaced "captured exclusively by benchmark B3" with **"most closely matched by benchmark B3"**.
- Cross-venue VAR: replaced "dominant share of price discovery" with **"consistent with stronger Binance-to-Coinbase information transmission"**, and replaced "cross-venue arbitrage binds fragmented books" with **"confirming that the estimated joint VAR is dynamically stable"**.
- FI-2010: replaced "shared cross-market microstructural invariant" with **"The same qualitative subcritical pattern appears in this regulated-equity benchmark"**, and replaced "proving that subcritical feedback is not a crypto artifact" with **"replicating the qualitative subcritical pattern in regulated equities"**.
- Historical calibration framing: replaced "demonstrates that severe feedback surges occur" with **"The calibrations illustrate how documented liquidity depletion maps into large model-implied feedback sensitivity"**.
- Pre-trend and reverse causality: replaced "moved in lockstep" with **"we detect no statistically significant differential pre-trend"**; replaced "confirm[s] that causality does not operate backward in time" with **"providing no evidence of a reverse-timing artifact"**; replaced "proves that positive feedback is not an econometric illusion" with **"showing that the positive estimate persists after extensive lag controls"**.
- Policy discussion: streamlined Section 6.2 item 2 to **"Standardized Session Memory Clearing"**, eliminating mentions of "mandatory neural weight resets".
- Holdout validation: framed Direct VAR ($\hat{S} = 0.983$) as the primary benchmark and noted strong first-stage predictive power ($F > 100$) for the 2SLS check.
- Table 15: renamed $a_0$ to **$a_{\text{EMA}}$ (Filter Anchor)** in table header and text, clarifying that it is the mechanical EMA filter parameter distinct from empirical return autoregression $\hat{J}_{11}$.

---

## 4. Certification
All MUST-FIX items are completely repaired, verified against the source code, and certified for submission.
