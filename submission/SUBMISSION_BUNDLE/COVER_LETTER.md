# Editorial Submission Cover Letter

**To:** The Editors  
**Target Journal:** *The Journal of Finance* / *Journal of Financial Economics* / *The Review of Financial Studies*  
**Date:** October 2026  
**Re:** Submission of *"From Human Markets to Machine Markets: Feedback Stability, Auditable Memory, and Financial Constraints"*  
**Authors:** Pratik Niroula and Prashant Niroula  
**Manuscript Length:** Strictly 48 pages exact (12pt, 1.5 line spacing, 1-inch margins; abstract strictly 90 words)  
**Accompanying Materials:** Authoritative Internet Appendix / Technical Monograph (72 pages) and Complete Open Replication Suite  

---

Dear Editors,

We are pleased to submit our manuscript, **"From Human Markets to Machine Markets: Feedback Stability, Auditable Memory, and Financial Constraints,"** for consideration for publication.

As autonomous trading algorithms, high-frequency execution engines, and adaptive machine-learning strategies increasingly intermediate modern financial markets, price formation ceases to be an open-loop discovery process and becomes a closed dynamical system: algorithms learn from prices that their own order flow directly impacts. 

Our paper organizes around a single central economic and regulatory question:
> **Can observable market data identify destabilizing adaptive feedback, when does that feedback become financially dangerous, and what information is fundamentally missing from public surveillance data?**

Rather than asserting speculative claims about black-box artificial intelligence, our paper establishes **three concrete headline contributions** supported by realization theory, high-frequency limit order book econometrics, and dealer balance-sheet constraints:

1. **Contribution 1 — Identification Limits and Mandatory Surveillance Abstention:**  
   We prove that public market feeds identify only merged rate–weight transfer functions, rendering individual algorithmic cohorts sharing adaptation rates observationally equivalent (Theorem 2.1). Separating near-coincident cohorts requires active probing budgets that scale as $\Omega(\delta^{-4})$ under Le Cam minimax limits (Theorem 2.3). In finite observation windows, bounded surveillance errors force an explicit mandatory abstention layer $\mathcal{B}_T = (1 - \epsilon_T, 1 + \epsilon_T)$ around the critical unit stability boundary (Theorem 2.5), explaining why public surveillance must withhold binary classification.
   
2. **Contribution 2 — Empirical Evidence and Flagship Natural Experiment:**  
   Across a multi-year panel of 768 asset-days ($66.3 \times 10^6$ one-second transitions) on Binance Spot, high-frequency feedback is modest and strictly subcritical in normal conditions ($\hat{Q} \approx 0.008, \hat{S} \approx 0.92 < 1.0$). We examine dynamic robustness via minimum-distance covariance matching ($Q_{\text{MD}} = 0.0086$), while openly reporting that the pooled overidentifying restrictions reject the parsimonious linear specification ($J = 73.0, df = 4, p < 0.001$), and Rigobon heteroskedasticity identification reveals negative contemporaneous buffering ($Q_{\text{Rig}} = -0.0191$). Crucially, a Difference-in-Differences natural experiment around the July 8, 2022 Binance Zero-Fee trading schedule overhaul ($N=192$) reveals no detectable feedback amplification despite a $+75.01\%$ volume surge ($\hat{\beta}_3 = -0.00186, p = 0.547$, permutation $p = 0.750$). Out-of-sample expanding-window folds across seven chronological test dates confirm that 2-state Markov switching models offer zero statistically significant MSE predictive advantage over a single-regime linear specification.

3. **Contribution 3 — Financial Fragility, Non-Normal Amplification, and Dealer Solvency:**  
   We prove that spectral price stability ($\rho(J) < 1$) does not ensure dealer capital solvency. Because the closed-loop market Jacobian $J$ is generically non-normal under asymmetric price-impact and flow memory ($J J^\top - J^\top J \neq 0$), stable eigenvalues can coexist with massive transient balance-sheet excursion. The exact worst-case safe shock radius for a leveraged dealer is governed by peak transient magnification: $r^*_{\text{exact}} = B / \sup_{t \ge 0} \|C J^t\|_2$, bounded by the Kreiss constant: $\frac{B}{e n \mathcal{K}(J)} \le r^*_{\text{exact}} \le \frac{B}{\mathcal{K}(J)}$ (Theorem 2.6). Funded dealer simulations (19,200 paths) separate transient magnification from persistent-flow accumulation, demonstrating why capital-aware pre-trade gating is a necessary complement to post-trade circuit breakers.

### Manuscript Scope and Organization
In strict accordance with top finance journal guidelines, the primary submission manuscript is formatted to 48 pages exact (12pt, 1.5 line spacing, 1-inch margins, 0 overfull hboxes, 0 undefined references, abstract 90 words).

All 10 extended technical appendices (Appendices A through N), full-program audits, joint-venue VAR reconstructions, 768 asset-day raw reproduction tables, and richer observation contracts are housed in the companion **Authoritative Internet Appendix / Technical Archive** (72 pages, `Machine_Markets_JF_Submission_Full_20261006.pdf`).

### Data Availability and Cryptographic Lineage Rigor
Every table cell in the manuscript is certified by an automated cryptographic lineage ledger covering 29 table blocks and 3,219 individual table cells (`check_lineage_receipt.py`), with zero manual literals. The 35-test unit/regression suite executes cleanly in under one second. All raw exchange archives are documented with SHA-256 digests.

We confirm that this manuscript is original, has not been published previously, and is not under consideration elsewhere. We look forward to your evaluation and the referee process.

Sincerely,

**Pratik Niroula**  
Corresponding Author  
Email: `pratik.niroula@alumni.harvard.edu`  

**Prashant Niroula**  
Author  
