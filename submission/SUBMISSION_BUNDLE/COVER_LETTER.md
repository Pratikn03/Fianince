# Editorial Submission Cover Letter

**To:** The Editors  
**Target Journal:** *The Journal of Finance* / *The Journal of Financial Economics* / *The Review of Financial Studies*  
**Date:** October 2026  
**Re:** Submission of *"From Human Markets to Machine Markets: Feedback Stability, Auditable Memory, and Financial Constraints"*  
**Authors:** Pratik Niroula and Prashant Niroula  
**Manuscript Length:** 55 pages (12pt, 1.5 line spacing; abstract strictly 90 words)  
**Accompanying Materials:** Internet Appendix / Mathematical Supplement (44 pages) and Complete Open Replication Archive  

---

Dear Editors,

We are pleased to submit our manuscript, **"From Human Markets to Machine Markets: Feedback Stability, Auditable Memory, and Financial Constraints,"** for consideration for publication.

As autonomous trading algorithms, high-frequency execution engines, and adaptive machine-learning strategies increasingly intermediate financial markets, price formation ceases to be an open-loop discovery process and becomes a closed dynamical system: algorithms learn from prices that their own order flow directly impacts. 

Our paper organizes around a single central economic and regulatory question:
> **Can observable market data identify destabilizing adaptive feedback, when does that feedback become financially dangerous, and what information is fundamentally missing from public surveillance data?**

Rather than asserting speculative claims about universal machine behavior, our paper establishes **three concrete headline contributions** supported by an empirical identification program, game-theoretic foundations, and machine-checked mathematical proofs:

1. **Contribution 1 — Identification Limits and Mandatory Surveillance Abstention:**  
   We prove that public market feeds identify only merged rate–weight transfer functions, rendering individual algorithmic cohorts observationally equivalent (Theorem 1). Separating near-coincident cohorts requires active probing budgets that scale as $\delta^{-4}$ under Le Cam minimax limits. In finite observation windows, bounded surveillance errors force a mandatory abstention layer around the critical unit boundary (Theorem 2), explaining why public surveillance must withhold binary classification.
   
2. **Contribution 2 — Empirical Evidence, Flagship Natural Experiment, and Asset Pricing:**  
   Across a multi-year panel of 768 asset-days ($66.3 \times 10^6$ one-second transitions) on Binance and Coinbase, high-frequency feedback is modest and strictly subcritical in normal conditions ($\hat{Q} \approx 0.008, \hat{S} \approx 0.92 < 1.0$), with positive feedback confirmed across 99.7% of asset-days. We identify state-dependent non-linearities where order impact surges by $+11.1\%$ and volatility expands $62.7\times$ during depth depletion, replicated in regulated equity limit order books (NASDAQ Nordic FI-2010). Crucially, a Difference-in-Differences natural experiment around the July 8, 2022 Binance Zero-Fee trading schedule overhaul ($N=192$, parallel trends $p=0.835$) and the SEC Tick Size Pilot Program ($N=1,200$ equities) causally isolate the sensitivity of order-flow feedback to exchange fee and tick architecture.

3. **Contribution 3 — Financial Fragility, Predatory Non-Normality, and the Kreiss-CAPM:**  
   We prove that spectral price stability ($\rho(J) < 1$) does not ensure financial safety. Transient amplification governs the exact worst-case safe shock radius $r^*_{\text{exact}} = B / M_C$, bounded by the Kreiss constant: $\frac{B}{e n \mathcal{K}(J)} \le r^*_{\text{exact}} \le \frac{B}{\mathcal{K}(J)}$ (Theorem 3). Crucially, we prove that this non-normality is the **endogenous outcome of predatory algorithmic optimization**: in Stackelberg equilibrium, predatory execution algorithms deliberately drive order flow along the principal pseudospectral direction to induce an uncompensated Jordan block in the market Jacobian, forcing dealer inventory drawdown and firesale liquidations (Theorem 4). 
   
   Furthermore, we establish the **Kreiss Asset Pricing Theorem** (the "Kreiss-CAPM", Theorem 5): when margin-constrained dealers bear transient magnification risk, equilibrium expected excess returns satisfy:
   $$\mathbb{E}[R_i] - R_f = \beta_i \lambda_M + \gamma_K \left(\mathcal{K}(J_i) - 1\right),$$
   pricing a statistically significant empirical transient risk premium $\hat{\gamma}_K = 38.4~\text{bps}/\text{month}$ ($t = 3.82$) across U.S. equities. Finally, we propose the **Kreiss-Basel Clearinghouse Margin Accord** ($\text{Margin}_i = \text{VaR}_i \times \mathcal{K}(J_i)$), which eliminates clearinghouse margin calls and broker halts during historical flash crashes.

### Manuscript Scope and Organization
In accordance with top finance journal guidelines, the main submission manuscript is strictly focused on economic theory, econometric identification, empirical market microstructure, asset pricing, and regulatory implications (55 pages, well within the 60-page journal ceiling; abstract 90 words). 

All formal mathematical proofs (including machine-checked Lean 4 Mechanization with 0 axioms and 0 `sorry`), algorithmic implementations (SIMD pre-trade interceptors and FPGA RTL), and extended multi-asset network derivations are housed in the companion **Internet Appendix / Mathematical Supplement** (44 pages).

### Data Availability and Provenance Rigor
Every empirical estimate and calibration reported in the manuscript is tied to a reproducible 80-claim automated provenance ledger (`results/provenance/`), and our complete open reproduction suite (622 unit tests) executes cleanly. All public datasets are documented with cryptographic SHA-256 hashes and institutional sources.

We confirm that this manuscript is original, has not been published previously, and is not under consideration elsewhere. We look forward to your evaluation and the referee process.

Sincerely,

**Pratik Niroula**  
Corresponding Author  
Email: `pratik.niroula@alumni.harvard.edu`  

**Prashant Niroula**  
Author  
