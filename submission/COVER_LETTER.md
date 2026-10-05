# Editorial Submission Cover Letter

**To:** The Editorial Board  
**Target Journal:** *The Review of Financial Studies* / *Journal of Financial Economics*  
**Date:** October 2026  
**Re:** Submission of *"From Human Markets to Machine Markets: Feedback Stability, Auditable Memory, and Financial Constraints"*  
**Authors:** Pratik Niroula and Prashant Niroula  

---

Dear Editors and Program Committee,

We are pleased to submit our manuscript, **"From Human Markets to Machine Markets: Feedback Stability, Auditable Memory, and Financial Constraints,"** for consideration for publication.

Modern electronic exchanges are increasingly dominated by autonomous algorithms, high-frequency quoting engines, and adaptive reinforcement learning agents. While classical market microstructure models treat liquidity providers and consumers as static linear optimizers or exogenous noise traders, real-world algorithmic market participants adapt dynamically, creating closed-loop feedback between order book flow and price dynamics.

In this paper, we address the fundamental question: **When can an exchange supervisor or macroprudential regulator determine whether an observed market is operating in a stable versus supercritical feedback regime, and how can pre-trade market mechanisms provably bound nonnormal inventory amplification?**

Our manuscript establishes five core contributions:

1. **Closed-Loop Systems-Theoretic Identification Boundary:**  
   We prove the *Swapped-Feedback Non-Identifiability Theorem* (Theorem M1): when algorithmic cohorts adapt with symmetric memory, the aggregate price response exhibits an exact Popov--Belevitch--Hautus (PBH) unobservable eigenspace defect of dimension $n-1$. Consequently, passive surveillance cannot identify cohort-level allocations, and we establish the minimal active probing rank conditions required to break this unobservable defect.

2. **Minimax Information Bounds & Mandatory Abstention:**  
   We prove a fundamental $\delta^{-4}$ sample-complexity lower bound for resolving cohort heterogeneity (Theorem M2) and establish the *Two-World Abstention Theorem* (Theorem M3): any error-controlled stability classifier must abstain near the critical spectral boundary $S = 1$, formally proving why selective classification unavoidably withholds judgment under finite observation windows.

3. **Nonnormal Solvency & Kreiss Matrix Safe Radii:**  
   We show that classical spectral radius stability ($\rho(J) < 1$) is strictly insufficient to prevent dealer default. Leveraging the Kreiss Matrix Theorem (Theorem M5) and its non-linear concave impact extension (Theorem NL1), we derive the exact worst-case safe inventory radius $r^* = B / (\mathcal{K}(J) \cdot P)$, proving that multi-asset cross-impact (Theorem M6) inflates the empirical Kreiss constant from $1.48$ to $1.73$, contracting clearinghouse solvency buffers by $14.43\%$.

4. **Machine-Checked Formal Verification in Lean 4:**  
   To guarantee complete mathematical certitude across all linearizations, polynomials, and invariant bounds, all 36 mathematical environments and 216 theorems in the manuscript and supplement are formally mechanized in **Lean 4** with **0 `sorry` and 0 unproved axioms**, verified via `AxiomAudit.lean`.

5. **Empirical Calibration & Provenance Rigor:**  
   Using 6.3+ GB of Level-2 and Level-3 market data across crypto perpetuals (Coinbase L3, Binance 1-sec bars) and regulated equity markets (canonical NASDAQ Nordic FI-2010 Level-2 benchmark, SHA-256 `0fac513a408b4dd803373860831874d3423a89f41fbaf13323f8a25a3019f3eb`, CC0 1.0 license), an unsupervised Markov-Switching VAR identifies endogenous phase transitions into supercritical territory ($\hat{Q}_{\text{calm}} = 0.0076$ vs. $\hat{Q}_{\text{crisis}} = 1.1109$), while our AMIP RFC-001 pre-trade interceptor (implemented in C++20 SIMD at 7.7 ns and FPGA Verilog at 20.0 ns) suppresses flash-crash drawdown by $86.28\%$ with zero dealer insolvencies.

### Data Availability and Reproducibility
The manuscript is accompanied by an open, fully verified reproduction suite. Every numerical claim in the paper is validated against the 80-claim automated provenance ledger (`scripts/provenance_ledger.py`), and the full test suite of 622 tests passes in under 60 seconds (`scripts/regenerate_all.py`). All benchmark datasets are publicly accessible with SHA-256 checksums.

We certify that this manuscript is original, has not been published previously, and is not under consideration elsewhere. We look forward to the editorial evaluation and referee review.

Sincerely,

**Pratik Niroula**  
Author  

**Prashant Niroula**  
Author  
