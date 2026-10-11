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
   - Eliminated the circular definition and harmonized the resolution floors.
   - Proved that under a single probe pulse within a finite trading session ($T_{\text{session}}$) subject to resting depth limit $V_{\max} = 50.0$, the unconstrained depth floor is:
     $$\delta_{\min}^{\mathrm{depth}}(T_{\text{session}}, V_{\max}) = \sqrt{\frac{2(z_\alpha + z_\beta)\sigma}{\kappa^2 q V_{\max}\sqrt{T_{\text{session}}}}} = 0.0717$$
   - Under an active market price-displacement cap $D_{\max} = 5.0$ ($\kappa = 0.8$), the effective per-fill quantity limit is $V_{\mathrm{eff}} = \min(V_{\max}, D_{\max}/\kappa) = \min(50, 6.25) = 6.25$, defining an operational single-pulse resolution floor:
     $$\delta_{\min} = \sqrt{\frac{2 z_\alpha \sigma}{\kappa^2 q V_{\mathrm{eff}}}} \approx 0.2028$$
   - Established the tri-region phase diagram (1,949 Feasible, 5,151 Costly Sequential, 2,900 Infeasible):
     - **Regime 1 ($\delta \ge \delta_{\min}$):** Single-pulse probing achieves identification within horizon $N = \Theta(1)$ and capital $C = \Theta(\delta^{-4})$.
     - **Regime 2 ($\delta < \delta_{\min}$):** Single pulse is insufficient because probe size is clipped at $V_{\mathrm{eff}}$. Each bounded pulse supplies Fisher information $\mathcal{I} = \Theta(V_{\mathrm{eff}}^2 \delta^4 / \sigma^2)$. Therefore, accumulating fixed Fisher information requires $N_{\mathrm{pulses}} = \Theta(\delta^{-4})$ pulses and cumulative transaction capital $C_{\mathrm{seq}} = \Theta(\delta^{-4})$.
     - Bounded depth does *not* create an infinite-horizon impossibility floor, but imposes a steep $\Theta(\delta^{-4})$ sequential capital barrier.

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
   - In the multi-agent causal intervention experiment, upgraded the frozen benchmark to an authentic pre-trained policy snapshot with learning disabled ($\eta = 0$), producing non-zero execution flow and isolating the causal effect of online adaptation from flow persistence.

4. **Resolution of Detailed Critique Points (5.A – 5.D):**
   - **5.A (Observation Contract):** Explicitly formalized Contract $I_0$ with homoskedastic additive observation noise $\epsilon_t \sim \mathcal{N}(0, \sigma^2)$, proving exact Gaussian testing separation $\frac{1}{2}(z_\alpha + z_\beta)^2 = 2 z_\alpha^2 \approx 5.41$, matching $A_{\mathrm{req}} = \frac{2\sigma z_\alpha}{\kappa^2 q \delta^2}$.
   - **5.B (Exact Equity Scaling & Minimum Lot Size):** Formalized Proposition 2.8 exact equity difference $\Delta E = \kappa^2 q A^2 \delta^2$. Under Gaussian measurement noise $\sigma_E = 0.50$, required volume scales as $\Theta(\delta^{-1})$ ($A_{\mathrm{req}} \approx 71.70$ at $\delta = 0.05$, saving 51.1% over price-only probing). Under continuous quantities and exact audit marks, the theoretical infimum is $\inf C = 0$, while Binance minimum lot $V_{\min} = 1.0$ sets an operational floor of $\$0.94$ USDT (99.98% savings).
   - **5.C (Balance Sheet Operator):** Clarified the leveraged dealer margin operator mapping $C_{\text{margin}} x_t = r_t + 160.0 \cdot \Delta I_t^{\text{dealer}}$.
   - **5.D (Observable Data Regression & Structural Recovery):** Uncovered that naive lag regression estimates $\beta_{\mathrm{RF}} \approx \gamma \cdot \eta \approx 0.0208$ due to exponential memory filtering. Implemented Cochrane-Orcutt quasi-differencing on reconstructed filtered memory state $\hat{y}_t$, successfully recovering true structural feedback $\hat{\gamma} = 0.1965$ (bias $-0.0035$ against true $\gamma = 0.20$).

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
# Main paper terminates on Page 59/60 (strictly <= 60 pages); Internet Appendix spans Pages 61–82.
```
