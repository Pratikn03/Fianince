# Authorship, AI-Use, Ethics, and Data Governance Disclosures

**Manuscript:** *From Human Markets to Machine Markets: Feedback Stability, Auditable Memory, and Financial Constraints*  
**Date:** October 2026  

---

## 1. Authorship Declaration and CRediT Statement
Both authors contributed substantially to the conception, theoretical analysis, mathematical formalization, econometric estimation, software implementation, and drafting of the manuscript:
- **Pratik Niroula:** Conceptualization, methodology, closed-loop identification proofs, systems theory, Lean 4 mechanization, C++20 SIMD/FPGA RTL design, econometric estimation, software validation, manuscript drafting and revision.
- **Prashant Niroula:** Theoretical validation, control-theoretic review, mathematical supplement proofs, provenance auditing, econometric pipeline verification, manuscript drafting and review.

Both authors have read and approved the final manuscript and bear full accountability for the integrity of the work.

---

## 2. Artificial Intelligence and Assistive Technology Disclosure
In compliance with journal policies regarding Generative Artificial Intelligence (GAI) and Large Language Models (LLMs):
- **Role of Generative AI:** AI tools were utilized during the research and preparation process strictly for code syntax formatting, boilerplate test scaffolding, literature search queries, and LaTeX typesetting assistance.
- **Author Responsibility:** All conceptual models, theorems, mathematical proofs, Lean 4 formal logic statements, econometric interpretations, and scientific claims were formulated, mathematically proved, verified, and audited by the human authors. The human authors take complete intellectual responsibility for the veracity, rigor, and conclusions of the work.

---

## 3. Data Governance, Provenance, and Licensing
All empirical analyses in this paper utilize publicly accessible, ethically sourced, and legally compliant market data:
1. **NASDAQ Nordic Equities (FI-2010 Benchmark):**
   - Source: Benchmark dataset for mid-price forecasting (Ntakaris et al., IEEE TNNLS 2018).
   - Local Path: `empirical_pipeline/fi2010/data/data.csv` (56.13 MB).
   - SHA-256 Digest: `0fac513a408b4dd803373860831874d3423a89f41fbaf13323f8a25a3019f3eb`.
   - License: CC0 1.0 Universal Public Domain.
   - Status: Primary canonical equity benchmark; supersedes and replaces earlier withdrawn synthetic latency-instrument exploratory scripts (`archive/withdrawn_20261003/`).
2. **Coinbase Pro Cryptocurrency Level-3 Feed:**
   - Source: Public WebSocket and REST market data APIs for BTC-USD and ETH-USD.
   - License: Educational and non-commercial research use.
3. **Binance USDⓈ-M Futures Feed:**
   - Source: Public Binance Data Collection archive (1-second tick-aggregated order books and trade bars).
   - License: Public research distribution under Binance terms of service.

---

## 4. Conflict of Interest and Funding Statement
The authors declare no competing financial interests, institutional consulting retainers, or commercial affiliations that could have influenced or appeared to influence the research presented in this manuscript. The research was conducted independently without external grant funding or proprietary exchange sponsorship.

---

## 5. Ethical Considerations and Algorithmic Safety
The Agentic Market Interoperability Protocol (AMIP RFC-001) specification introduced in this manuscript is designed solely as a defensive, stability-preserving supervisory mechanism. It enforces pre-trade risk limits, mitigates nonnormal liquidity evaporation, and ensures clearinghouse solvency preservation under SEC Rule 15c3-5 and MiFID II RTS 6. No predatory or manipulative trading strategies are facilitated by this work.
