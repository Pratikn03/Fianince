# DISCLOSURE INFORMATION VALUE AUDIT (PHASE 5)

**Repository:** `Pratikn03/Fianince`  
**Audit Baseline Commit:** `94dc1511d5de13f6d6bd1b81f1100554e08a85cd`  
**Baseline Test Audited:** `P1_disclosure_state_oos` in `recompute_prereg_oct21_followup.py` (`R_P1_disclosure_state_oos.json`, preserved intact)  
**Execution Script:** `ceiling_suite/papers/hardened_empirical_audits.py`  
**Results File:** `ceiling_suite/papers/recomputed/R_hardened_empirical_audits.json` (`phase_5_disclosure_hierarchy`)

---

## 1. Audit of the Baseline Table 18 Specification (Task 5.1)

In Paper 1 Section 8.3 (`recompute_prereg_oct21_followup.py`, lines 150–251), the pre-registered `P1_disclosure_state_oos` test compared a public price-and-flow filter (`pf_cols`) against an aggregate trader-class tagged model (`tag_cols`) to forecast 30-minute-ahead post-shock positioning:
- `fut_div_30m`: 30-minute-ahead top-trader vs. all-trader positioning divergence $(n_{\mathrm{top},t+6} - n_{\mathrm{all},t+6})$.
- `fut_nt_30m`: 30-minute-ahead top-trader net positioning $n_{\mathrm{top},t+6}$.

The baseline test reported massive out-of-sample forecast improvements:
- Divergence: $\Delta R^2 = +50.728\text{ pt}$ ($R^2_{\mathrm{tag}} = 45.962\text{ pt}$ vs. $R^2_{\mathrm{pf}} = -4.766\text{ pt}$, Clark–West $t = 27.99, p < 10^{-6}$).
- Top-Trader State: $\Delta R^2 = +50.404\text{ pt}$ ($R^2_{\mathrm{tag}} = 54.845\text{ pt}$ vs. $R^2_{\mathrm{pf}} = 4.441\text{ pt}$, Clark–West $t = 29.35, p < 10^{-6}$).

### The Critical Information-Set Mismatch

Our inspection of `pf_cols` vs. `tag_cols` (lines 159–160) revealed an asymmetric information structure:
```python
pf_cols = ["ret5", "u5", "xf", "xs", "uf", "us"]
tag_cols = ["ret5", "u5", "xf", "xs", "uf", "us", "nt", "na", "d_nt", "d_na", "div_t"]
```
- `pf_cols` contains **only price and order flow**; it has **no access to current positioning levels** $(n_{\mathrm{top},t}, n_{\mathrm{all},t}, \mathrm{div}_t)$.
- `tag_cols` contains current positioning levels $(n_{\mathrm{top},t}, n_{\mathrm{all},t})$ and their current difference $\mathrm{div}_t$.

Because trader positioning ratios are slow-moving stock variables with high autoregressive persistence (near unit roots), predicting $y_{t+6}$ when observing $y_t$ is trivial statistical persistence ($y_{t+6} \approx \rho^6 y_t$). The baseline comparison did not distinguish whether the $+50.7\text{ pt}$ gain reflects:
1. **Level persistence**: Simply observing the current positioning state $y_t$; or
2. **Dynamic memory filtering**: The multi-cohort exponential filtering theory developed in Paper 1.

---

## 2. Hardened Nested Model Hierarchy (Tasks 5.2–5.4)

To decompose the information value rigorously, `hardened_empirical_audits.py` evaluated a nested hierarchy of 7 models on the exact same sample of $N_{\mathrm{train}} = 1{,}629$ and $N_{\mathrm{test}} = 2{,}882$ post-shock 5-minute bars:
- **`M1` (Price-and-Flow 2-Exponential Only)**: Baseline `pf_cols` ($\Delta p_t, u_t$, fast/slow filters).
- **`M2` (Naive Random Walk Benchmark)**: $\hat y_{t+6} = y_t$ (zero fitted parameters).
- **`M3` (Univariate Class AR(1))**: Predicts $y_{t+6}$ using only current class levels $(n_{\mathrm{top},t}, n_{\mathrm{all},t}, \mathrm{div}_t)$ plus symbol intercepts.
- **`M4` (Univariate Class AR(3))**: Adds lags at $t-1$ and $t-2$ plus 1-step differences.
- **`M5` (Class ARX with Price & Flow)**: Adds immediate return $\Delta p_t$ and immediate flow $u_t$ to `M3`.
- **`M6` (Baseline Full Tag Cols)**: Baseline `tag_cols` specification from Table 18.
- **`M7` (Augmented Cohort Memory Filters)**: Adds explicit fast and slow exponential memory filters of the class position streams $(n_{\mathrm{top},\mathrm{fast}}, n_{\mathrm{top},\mathrm{slow}}, n_{\mathrm{all},\mathrm{fast}}, n_{\mathrm{all},\mathrm{slow}})$.

We also evaluated these models on the **30-minute position changes** $\Delta y_{t+6} = y_{t+6} - y_t$ (`delta_div_30m` and `delta_nt_30m`) to remove the level persistence entirely.

### 2.1 Out-of-Sample Performance Table ($N_{\mathrm{test}} = 2{,}882$ Shocks)

| Model Specification | Features Included | Divergence Level $R^2$ (`fut_div_30m`) | Top-Trader Level $R^2$ (`fut_nt_30m`) | $\Delta$ Divergence $R^2$ (`delta_div_30m`) | $\Delta$ Top-Trader $R^2$ (`delta_nt_30m`) |
|---|---|---:|---:|---:|---:|
| `M1`: Price/Flow Only | $\Delta p_t, u_t, x_f, x_s, u_f, u_s$ | $-4.766\text{ pt}$ | $+4.441\text{ pt}$ | $+0.467\text{ pt}$ | $+1.374\text{ pt}$ |
| `M2`: Naive Random Walk | $y_t$ (no parameters) | $+46.090\text{ pt}$ | $+53.752\text{ pt}$ | $0.000\text{ pt}$ | $0.000\text{ pt}$ |
| `M3`: Univariate Class AR(1) | $y_t, n_t, n_a$ | $+46.205\text{ pt}$ | $+54.413\text{ pt}$ | $-0.177\text{ pt}$ | $+0.397\text{ pt}$ |
| `M4`: Univariate Class AR(3) | $y_t, y_{t-1}, y_{t-2}, \Delta y_t$ | $+46.789\text{ pt}$ | $+54.581\text{ pt}$ | $+1.047\text{ pt}$ | $+0.740\text{ pt}$ |
| `M5`: Class ARX + Price/Flow | $y_t, \Delta p_t, u_t$ | $+46.288\text{ pt}$ | $+54.651\text{ pt}$ | $+0.067\text{ pt}$ | $+0.968\text{ pt}$ |
| `M6`: Baseline Full Tag Cols | All `tag_cols` | $+45.962\text{ pt}$ | $+54.845\text{ pt}$ | $-0.256\text{ pt}$ | $+1.407\text{ pt}$ |
| `M7`: Augmented Cohort Filters | `tag_cols` + fast/slow class filters | $+44.941\text{ pt}$ | $+54.681\text{ pt}$ | $-2.273\text{ pt}$ | $+1.088\text{ pt}$ |

---

## 3. Variance Decomposition & Scientific Findings

1. **Decomposition of the $+50.7\text{ pt}$ Gain**:
   - For **cohort divergence** (`fut_div_30m`), comparing `M1` ($-4.766\text{ pt}$) to `M3` ($+46.205\text{ pt}$) shows that simply knowing current positioning accounts for **$+50.971\text{ pt}$** of out-of-sample $R^2$ (**$100.48\%$ of the total gain**).
   - Adding the full suite of price/flow exponential memory filters (`M6`) yields $R^2 = 45.962\text{ pt}$—which is slightly *lower* than the simple AR(1) benchmark ($-0.243\text{ pt}$, dynamic share **$-0.48\%$**).
   - For **top-trader positioning** (`fut_nt_30m`), `M3` accounts for **$+49.972\text{ pt}$** of the $+50.404\text{ pt}$ total gain (**$99.14\%$ of the total gain**). Dynamic memory filters add only $+0.432\text{ pt}$ (**$0.86\%$**).

2. **Predicting Incremental Changes ($\Delta y_{t+6} = y_{t+6} - y_t$)**:
   - When the trivial level persistence is subtracted and models are asked to forecast where positioning will *move* over the next 30 minutes, out-of-sample $R^2$ collapses across all models:
     - Divergence change: $R^2 = -0.256\text{ pt}$ (`M6`) and $-2.273\text{ pt}$ (`M7`).
     - Top-trader change: $R^2 = +1.407\text{ pt}$ (`M6`) and $+1.088\text{ pt}$ (`M7`).
   - This proves that the market data do not support fine-grained multi-cohort dynamic trajectory forecasting beyond simple mean-reversion around the current level.

3. **Public Tagged Aggregates vs. Strategic Algorithm Identification**:
   - Exchange-disclosed positioning aggregates (Binance top-trader accounts) are **coarse, self-reported account classes**, not individual algorithm identifiers.
   - Proposition `prop:tagged` in Paper 1 proves that *tagged order flow* from individual trading algorithms enables linear instrumental-variable identification of cohort memory rates without the $(\Delta\eta)^{-(4K-2)}$ ill-conditioning barrier.
   - However, our empirical findings demonstrate that existing commercial venue disclosure provides only broad class-level inventory persistence, which does not constitute identification of individual proprietary algorithmic strategies.

### Required Manuscript Qualification

In Paper 1 Section 8.3 (`ceiling_suite/papers/paper1/p1_mixture.tex`), qualify the interpretation of Table 18:
> *The $+50.7\text{ pt}$ out-of-sample $R^2$ gain demonstrates that public price and flow alone cannot reconstruct current trader-class positioning (which is private to the exchange), but this gain is overwhelmingly driven by the high autoregressive persistence of observed positioning levels ($99.1\%$–$100.5\%$ of the gain is captured by a univariate AR(1) benchmark). Aggregated exchange disclosures inform market participants about current class inventory imbalances, but they do not circumvent the mathematical barrier to identifying individual hidden trading strategies.*
