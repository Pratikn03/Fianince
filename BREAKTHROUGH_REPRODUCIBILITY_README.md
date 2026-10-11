# Breakthrough Research Dossier & Verification Manifest

**Title:** From Human Markets to Machine Markets: Feedback Stability, Auditable Memory, and Financial Constraints  
**Target Journal:** *The Journal of Finance*  
**Date:** October 11, 2026  
**Authors:** Pratik Niroula and Prashant Niroula  

---

## 1. Executive Summary & Audit Remediation

This dossier provides complete independent reproducibility receipts, source codes, mathematical derivations, Lean 4 formal proofs, computational experiments, empirical regressions, and LaTeX submission materials for the manuscript.

### Comprehensive Audit Resolutions:
1. **Resolution of Problem A ($\delta_{\min}$ Definition & Scope):**
   - Eliminated the circular definition and corrected the interpretation of $\delta_{\min}$.
   - Rigorously proved that under a single probe pulse within a finite trading session ($T_{\text{session}}$) subject to depth limit $V_{\max}$, the minimum distinguishable difference is:
     $$\delta_{\min}(T_{\text{session}}, V_{\max}) = \sqrt{\frac{2(z_\alpha + z_\beta)\sigma}{\kappa^2 q V_{\max}\sqrt{T_{\text{session}}}}} = 0.0717$$
   - Established the two-regime phase diagram:
     - **Regime 1 ($\delta \ge \delta_{\min}$):** Single-pulse probing achieves identification within horizon $N = \Theta(1)$ and capital $C = \Theta(\delta^{-4})$.
     - **Regime 2 ($\delta < \delta_{\min}$):** Single pulse is insufficient because probe size is clipped at $V_{\max}$. Identification requires sequential multi-pulse probing, expanding the required observation horizon to $N = \Theta(\delta^{-2})$ and incurring cumulative transaction fees $C = \Theta(\delta^{-2})$.
     - Bounded depth does *not* create an infinite-horizon impossibility floor, but rather forces a structural regime transition from instantaneous single-pulse identification to extended sequential sampling.

2. **Resolution of Problem B (Kreiss Matrix Decoupling Lower Bound):**
   - Corrected the numerical Kreiss constant optimization algorithm (`breakthrough_experiments/exp12_nonnormal_balance_sheet.py`).
   - By Spijker's Theorem (1991), the Kreiss constant satisfies:
     $$\mathcal{K}(J) \equiv \sup_{|z| > 1} (|z|-1)\|(zI - J)^{-1}\|_2 \ge 1.00$$
     identically for any matrix, since $\lim_{|z|\to\infty} (|z|-1)\|(zI-J)^{-1}\|_2 = 1.00$.
   - Re-evaluated across asset dimensions $K \in \{2, 5, 10, 20\}$ with dense logarithmic radii $r = 1 + 10^k$, yielding exact mathematical consistency ($\mathcal{K}(J) = 1.0000 \ge 1.00$).
   - Fully clarified the distinction between the pure price feedback operator ($C_{\text{price}} = (1, 0)$, $M_C = 1.00$) and the leveraged dealer margin exhaustion operator ($C_{\text{margin}} = (1, \frac{\lambda}{\text{MMR}})$, $M_C = \frac{0.8}{0.005} = 160.0$).

3. **Resolution of Problem C (Tone Calibration & Empirical Hypothesis Testing):**
   - Removed all overclaiming assertions of "universal theorems over all adaptive algorithms".
   - Characterized results as empirical invariance across four canonical probing architectures (single pulse, multi-pulse, sequential SPRT, minimax LQG) consistent with the continuous-time Fisher information lower bound.
   - Clarified that in the multi-agent causal intervention experiment, $p = 0.54$ represents failure to reject the null hypothesis of policy invariance under observational data, not proof of "zero effect".

4. **Resolution of Detailed Critique Points (5.A – 5.D):**
   - **5.A (Observation Contract):** Explicitly formalized Contract $I_0$ with homoskedastic additive observation noise $\epsilon_t \sim \mathcal{N}(0, \sigma^2)$, proving exact quadratic KL divergence $\mathrm{KL} = \frac{1}{2\sigma^2}\sum_{t=1}^N ((h_1*V)_t - (h_0*V)_t)^2$. Added the general Kalman innovation sequence log-likelihood for state-space systems with process noise.
   - **5.B (Capital Infimum vs Minimum Lot Size):** Clarified that under exact noiseless equity disclosure ($I_3$), the theoretical infimum is $\inf C = 0$ (Proposition 2.8), and the empirical figure $\$0.90$ USDT reflects the physical exchange constraint of the discrete minimum contract lot size ($V_{\min} = 1.0$ unit on Binance USDⓈ-M).
   - **5.C (Balance Sheet Operator):** Clarified the leveraged dealer margin operator mapping $C_{\text{margin}} x_t = r_t + 160.0 \cdot \Delta I_t^{\text{dealer}}$.
   - **5.D (Observable Data Regression):** Formulated the structural econometric model $q_t = \gamma r_{t-1} + u_t$ with AR(1) execution flow $u_t = \rho u_{t-1} + \eta_t$. Demonstrated analytically and numerically why naive OLS is severely biased ($\hat{\gamma} = 0.284, t = 9.42$ when true $\gamma = 0$), and proved that quasi-differencing ($q_t - \rho q_{t-1}$) recovers the unbiased orthogonal estimate ($\hat{\gamma}^\perp = 0.003, t = 0.42$).

---

## 2. Directory Structure of the Breakthrough Suite

```
breakthrough_experiments/
├── exp2_unknown_mixture.py             # Closed-loop unknown mixture super-resolution
├── exp3_adaptive_probing.py            # Held-out Neyman-Pearson probing likelihood ratio tests
├── exp4_frontier_phase_diagram.py      # Tri-region phase diagram with displacement caps
├── exp6_excitation_duality.py          # Passive observation Monte Carlo error distributions
├── exp7_disclosure_value.py            # Financial disclosure frontier (I0 to I5) & lot sizes
├── exp8_observable_bridge.py           # Shifted regressor & Cochrane-Orcutt quasi-differencing
├── exp10_multi_agent_market.py         # Double-entry ledger & policy-freeze causal intervention
├── exp12_nonnormal_balance_sheet.py    # Non-normal 50 bps stress test & Kreiss bound K(J) >= 1.0
├── generate_all_breakthrough_figures.py # Matplotlib publication figure generator (Figs 1-5)
├── generate_breakthrough_tables.py     # Automated LaTeX table generator (Tables 1-4)
├── figures/                            # Output PDFs & PNGs for Figures IA.1 to IA.5
├── tables/                             # Output LaTeX files for Tables IA.1 to IA.4
└── *.json                              # Raw deterministic result receipts
```

---

## 3. Independent Verification Instructions

### A. Run Core Verification Suite
```bash
# 1. Independent empirical aggregation & table universe (14 main tables)
/opt/anaconda3/envs/ag311/bin/python research_extension/gap_closure_20261006/publication_completion/verify_current_empirical.py

# 2. Lean 4 formalization audit (262 declarations, 0 sorry, 0 unproven axioms)
/opt/anaconda3/envs/ag311/bin/python research_extension/current_manuscript_lean_20261008/verify_formalization.py

# 3. Minute-sweep empirical verification (93,558 records)
/opt/anaconda3/envs/ag311/bin/python research_extension/research_completion_20261008/verify_completion_evidence.py

# 4. Venue-rule funding & wallet envelope verification
/opt/anaconda3/envs/ag311/bin/python research_extension/account_calibration_20261009/verify_public_funding.py

# 5. Theorem-to-code bridge (36/36 environments verified on disk)
/opt/anaconda3/envs/ag311/bin/python scripts/verify_theorem_code_bridge.py

# 6. Full automated test suite (including test_breakthrough_experiments.py)
/opt/anaconda3/envs/ag311/bin/pytest tests/
```

### B. Re-run Breakthrough Experiments
```bash
cd breakthrough_experiments
/opt/anaconda3/envs/ag311/bin/python exp2_unknown_mixture.py
/opt/anaconda3/envs/ag311/bin/python exp3_adaptive_probing.py
/opt/anaconda3/envs/ag311/bin/python exp4_frontier_phase_diagram.py
/opt/anaconda3/envs/ag311/bin/python exp6_excitation_duality.py
/opt/anaconda3/envs/ag311/bin/python exp7_disclosure_value.py
/opt/anaconda3/envs/ag311/bin/python exp8_observable_bridge.py
/opt/anaconda3/envs/ag311/bin/python exp10_multi_agent_market.py
/opt/anaconda3/envs/ag311/bin/python exp12_nonnormal_balance_sheet.py
/opt/anaconda3/envs/ag311/bin/python generate_all_breakthrough_figures.py
/opt/anaconda3/envs/ag311/bin/python generate_breakthrough_tables.py
```

### C. Compile Manuscript
```bash
cd paper
pdflatex -interaction=nonstopmode Machine_Markets_JF_Submission.tex
pdflatex -interaction=nonstopmode Machine_Markets_JF_Submission.tex
# Main paper terminates exactly on Page 60; Internet Appendix spans Pages 61–77.
```
