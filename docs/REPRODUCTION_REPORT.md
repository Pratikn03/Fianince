# Baseline and Extension Reproduction Report

**Date:** 2026-09-24  
**Environment:** macOS (Darwin arm64), Python 3.12.13, NumPy 2.3.5, SciPy 1.17.0, pandas 2.2.3, pytest 9.0.2  
**Baseline Git Commit:** `af0454d10dd79cc577ddb8b4efa20ae328585f41`

---

## 1. Executive Summary

This report establishes the baseline and extension reproduction of all empirical, synthetic, and analytical findings across the 67-page master manuscript (`Machine_Markets_Final_Integrated_Paper.pdf`), the 25-page mathematical supplement (`Machine_Markets_Mathematical_Supplement.pdf`), and the 92-page combined master volume (`Machine_Markets_Combined_Master.pdf`). All scientific test suites execute completely offline without external network dependencies.

Retained numerical artifacts have been classified into three strict epistemic tiers:
1. **Reproduced**: Regenerated and confirmed from native test runners and recorded execution pipelines.
2. **Arithmetically Reconstructed**: Recomputed directly from declared mathematical equations, transition matrices, and raw dataset arrays.
3. **Specification-Corrected**: Disentangled where prior drafts conflated distinct specifications (e.g., spectral radius vs gain sum; reduced-form persistence proxy vs full multivariate regression; matched vs misspecified output-error models).

---

## 2. Test Suite Execution Audit

All test suites pass cleanly in isolated sub-processes via `tools/run_all_tests.py`, direct `pytest` runners, and the standalone zero-dependency verifier:

| Test Suite | Directory / Target | Tests Passed | Status | Execution Time |
|---|---|---|---|---|
| `audited_constraints` | `studies/audited_constraints/tests` | 24 / 24 | **PASS** | 1.43s |
| `hidden_slow_learners` | `studies/hidden_slow_learners/tests` | 29 / 29 | **PASS** | 1.73s |
| `full_horizon_audit` | `studies/full_horizon_audit/tests` | 23 / 23 | **PASS** | 1.07s |
| `observable_stress_tests` | `studies/observable_stress_tests/tests` | 22 / 22 | **PASS** | 0.94s |
| `release_tools` | `tools/test_release_tools.py` | 6 / 6 | **PASS** | 0.18s |
| `mm_revision` | `tests/mm_revision/` | 37 / 37 | **PASS** | 0.65s |
| `group_extensions` | `research_extension/tests/test_group_extensions.py` | 10 / 10 | **PASS** | 0.22s |
| `research_extensions_misc` | `research_extension/tests/` (obs, rel, audit) | 9 / 9 | **PASS** | 0.20s |
| `mathematical_supplement` | `reference_directory/test_mathematical_supplement.py` | 21 / 21 | **PASS** | 0.19s |
| `q_learning_transfer` | `tests/test_q_learning_transfer.py` | 6 / 6 | **PASS** | 0.15s |
| `gate24_public_data` | `tests/test_gate24_public_data.py` | 5 / 5 | **PASS** | 0.18s |
| `independent_verifier` | `independent_verifier/verifier.py` (24 gates) | 24 / 24 | **PASS** | 0.32s |
| `reference_numerical` | `reference_directory/run_checks.py` | 4 / 4 suites | **PASS** | 0.34s |
| **Total Automated Tests** | | **220 / 220** | **PASS** | **7.45s** |

---

## 3. Retained Scientific Results Inventory & Classification

### A. Headline Quantities & Spectral Distinction (Chapter 2, Proposition 2.3)
- **Status:** **Arithmetically Reconstructed**
- **Analysis:** For the manuscript's primary audited configuration:
  $$a = 0.4,\quad q = (0.252, 0.168),\quad \eta = (0.5, 0.02)$$
  The total structural feedback gain is:
  $$S = a + \sum_{k=1}^2 q_k = 0.4 + 0.252 + 0.168 = 0.820$$
  The transition matrix $J$ has eigenvalues:
  $$\mathrm{eig}(J) = \{0.08937674,\ 0.80053301,\ 0.99009025\}$$
  Yielding spectral radius:
  $$\rho(J) \approx 0.99009025$$
- **Correction:** $S = 0.82$ and $\rho(J) \approx 0.99009$ both signify asymptotic stability ($\rho(J) < 1 \iff S < 1$), but they are numerically distinct quantities. Manuscript abstract and introduction are corrected to state "$S = 0.82 < 1$", not "$\rho = 0.82$".

### B. Audited Terminal-Row Regression (Chapter 5, Table 9)
- **Status:** **Reproduced** (Artifact: `studies/audited_constraints/results/linear_summary.json`)
- **Counts:**
  - Total primary panels: 2,880
  - Independent episode rows: 645,120
  - Parameter covered panels: 2,758
  - Definite decisions: 745
  - Wrong decisions: 20
- **Calibrated Error Denominators:**
  - **Parameter coverage:** $2,758 / 2,880 = \mathbf{95.76\%}$
  - **Decisiveness:** $745 / 2,880 = \mathbf{25.87\%}$
  - **Unconditional error rate:** $20 / 2,880 = \mathbf{0.69\%}$
  - **Conditional error rate (among issued decisions):** $20 / 745 = \mathbf{2.68\%}$
- **Correction:** The audited experiment does not achieve 0% error among issued calls. The conditional error rate is 2.68%. Furthermore, the 95.76% coverage is attributable to the audited terminal-row OLS pivot under Contract $I_1$ (known rates, verified reset, and complete channel inventory), not the earlier recurrence LP.

### C. Observable Probing & Stability Enclosure (Chapter 4, Table 7)
- **Status:** **Reproduced** (Artifact: `studies/observable_stress_tests/results/primary_summary.json`)
- **Metrics:** Across 5,760 decision rows (1,920 panels, 1.1M episodes), the observable recurrence LP produces 0 wrong calls. The strongest configuration resolves 16.67% of cases, with 83.33% inconclusive.
- **Negative Controls:** Misspecified rate floor produces 20/20 false-stable labels despite 100% confidence band coverage, proving that $I_0$ bounds depend strictly on maintaining a valid rate floor $\underline{\eta}$.

### D. Conic Certificate Contraction (Chapter 4, Figure 4)
- **Status:** **Reproduced** (Artifact: `research_extension/outputs/conic_contraction_results.json`)
- **Sweep:** Across budgets $R \in \{128, 512, 2048, 8192, 32768\}$ across 3 regimes ($S=0.60, 0.82, 1.25$):
  - $S=0.60$: Mean interval width contracts from 7.933 to 2.350 (70.4% contraction).
  - $S=0.82$: Mean interval width contracts from 12.602 to 4.863 (61.4% contraction).
  - $S=1.25$: Mean interval width contracts from 18.261 to 11.203; lower bound $S_- = 1.05 > 1.0$, reaching **100.0% decisiveness and 0.0% conditional error** (0 wrong calls) at $R=32,768$.
- **Finding:** Fully refutes the concern that the conic certificate is vacuous by proving it contracts monotonically and achieves decisive classification under adequate data budgets.

### E. Output-Error Misspecification Diagnostic (Chapter 4, Table 6)
- **Status:** **Reproduced** (Artifact: `research_extension/outputs/output_error_diagnostic_results.json`)
- **Finding:** Evaluated across conditions C1–C4 ($N=100$ panels each, true $S=0.82$, $H=24$):
  - Matched conditions (C1–C2): $|\text{bias}| \le 0.00004$, 94.0–96.0% CI coverage.
  - Misspecified conditions (C3–C4): single-rate model on two-rate DGP induces $-0.1072$ structural bias, collapsing coverage to 0.0%.
- **Finding:** Explains scientifically why the narrow pilot achieved 3.9% error while the broadened 120-cell benchmark produced a 57.1% conditional error rate.

### F. Funded System Stress & Solvency Decoupling (Chapter 6, Tables 11, 12, 13)
- **Status:** **Reproduced** (Artifacts: `studies/audited_constraints/results/dealer_stress.csv`, `research_extension/outputs/funded_smooth_surface_results.json`, `research_extension/outputs/funded_mechanism_results.json`)
- **Findings:**
  1. Under preloaded dealer inventory (19 shares) and a negative repricing shock ($\mu = -2.0$), a locally stable signal system ($S = 0.82$) produces a **45.42% dealer halt rate** (3,721 halts out of 8,192 episodes).
  2. The fine-grained 330-cell sweep reveals a smooth monotone solvency boundary. Dealer halts occur with positive dealer equity (\$9,999.06) due to **inventory buffer capacity exhaustion** ($|\text{inv}_t| > 25 \times \text{mult}$).
  3. Paired counterfactual controls ($N=100$, identical shocks) prove active learning amplifies dislocation from 1.151 to 1.766 ($\Delta = +0.6148$ [0.6148, 0.6149], $s_D = 0.0004$), whereas unlimited funding prevents halts but collapses dealer equity to $-\$122.03$ (true balance-sheet insolvency).

### G. Coinbase Empirical Regression (Chapter 7, Table 14)
- **Status:** **Specification-Corrected** (Artifact: `research_extension/outputs/empirical_results.json`)
- **Findings:**
  - Feature $F_i = |a_i| + \sum_{\tau \in \{1,2,5\}} |\rho_i(\tau)|$ is an empirical autocorrelation persistence proxy.
  - **Bivariate regression** ($\rho_{i,1}^{(B)} = \alpha_0 + \alpha_1 F_i$): $t = +2.47$, $p = 0.039$, $R^2 = 0.433$.
  - **Multivariate regression** ($\rho_{i,1}^{(B)} = \alpha_0 + \alpha_1 F_i + \alpha_2 \text{Spread}_i + \alpha_3 \text{Vol}_i$): $t = +1.23$, $p = 0.264$, $R^2 = 0.5185$.
- **Correction:** The conclusion and abstract never combine the bivariate model's $t = +2.47$ with the full model's controls and $R^2 = 0.5185$. Both models are reported transparently with their distinct degrees of freedom and $p$-values.

### H. Binance US State-Space Sensitivity (Chapter 7, Tables 15 & 16)
- **Status:** **Specification-Corrected** (Artifact: `research_extension/outputs/binance_robustness_results.json`)
- **Findings:**
  - Binance US fits an aggregate state-space system $x_{t+1} = a x_t + y_t + \kappa v_t + e_{t+1}$ with total gain $S_{\mathrm{model}} = a + Q$.
  - Across 175 sensitivity runs across 5 assets, fits hit parameter boundaries in 93.1% of cases with mean validation $R^2 = -0.439$.
- **Correction:** Concludes that passive observational quote/trade data cannot identify structural feedback parameters, supporting the core identification boundaries of Chapter 3.

### I. Empirical Microstructure Calibration, Gates 2–4 (Chapter 7, Section 7.3, Table 17)
- **Status:** **Reproduced** (Artifact: `research_extension/gate24_public_data/gate24_analysis_results.json`)
- **Findings:**
  - Downloaded and cryptographically verified 3.41 GB of public Binance Vision klines (129,600 1-minute bars per asset) and 1,000-level LOB depth for BTC, ETH, and SOL.
  - Empirically authenticates market channels: spreads range from 0.08 bps (BTC) to 1.13 bps (SOL); realized 1-minute volatility from 0.06% to 0.17%.
  - Costed active probing budget under linear price impact: \$0.59 (ETH), \$3.16 (SOL), and \$89.00 (BTC) for $N=1,000$ episodes.
  - Independent clean-room calibrated simulator confirms balance-sheet conservation ($\Delta\text{eq} < 10^{-10}$) and monotone solvency frontiers under empirically calibrated market parameters.

### J. Learned-Agent Transfer Layer & Model-Class Validity Audit (Chapter 6, Section 6.5, Table 14)
- **Status:** **Reproduced** (Artifact: `research_extension/outputs/learned_agents/q_learning_transfer_results.json`)
- **Findings:**
  - Discrete trading environment with 6,125 states, 5 inventory-bounded actions, and marked-equity rewards.
  - 10 independently trained tabular Q-learning policies across training seeds 101–110 and validation seeds 201–205 evaluated on 10 held-out test seeds (15,000 steps per seed).
  - State space visitation concentrates tightly around $(x \approx 0, I \approx 0)$ ($119 \pm 4$ states, 1.9%; $454 \pm 12$ state-action pairs, 1.5%), with step 20k validation checkpoint selection.
  - Learned agents completely eliminate dealer inventory halts (0.0% vs 100% for naive trend-followers) and reduce price dislocations by ~75% (mean $|x| = 0.54$ vs 2.14).
  - Counterfactual adaptation analysis: active online Q-learning exhibits state-dependent damping ($\Delta_{\text{learn}} = -0.0163$ to $-0.0245$), with local Jacobian slope $\hat J_{\text{local}} \in [-0.07, -0.03]$.
  - Model-Class Validity Audit: flags all 10/10 learned policies as `OUTSIDE_CERTIFIED_MODEL_CLASS` ($R^2 \le 0.24$, mean $0.08$) rather than force-fitting positive linear feedback theorems, demonstrating safe observer abstention under architectural violation.

