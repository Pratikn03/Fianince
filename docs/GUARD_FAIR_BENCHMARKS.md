# GUARD FAIR BENCHMARKS AUDIT (PHASE 4)

**Repository:** `Pratikn03/Fianince`  
**Audit Baseline Commit:** `94dc1511d5de13f6d6bd1b81f1100554e08a85cd`  
**Dataset:** 19 thin perpetual futures symbols $\times$ 66 dates ($24$ train dates in 2024, $42$ untouched test dates in 2025–2026; $1{,}252$ valid symbol-days)  
**Execution Script:** `ceiling_suite/papers/hardened_empirical_audits.py`  
**Results File:** `ceiling_suite/papers/recomputed/R_hardened_empirical_audits.json` (`phase_4_guard_fair_benchmarks`)

---

## 1. Audit of the Baseline Part 24 Specification (Task 4.1)

In Paper 2 Part 24 (`recompute_prereg_oct21_followup.py`, lines 351–408), the pre-registered test evaluated the SEC Rule 15c3-5 pre-trade throttle $q_t \in (0, 1]$ on a $\$1\text{M}$ facility across 42 untouched test dates, comparing Policy (b) (`vol_cap`, $q_t = \min(1, k_{\mathrm{vol}}/\mathrm{rv})$) against Policy (c) (`vol_plus_guard`, $q_t = \min(1, k_{\mathrm{vol}}/\mathrm{rv}) \times \min(1, k_{\mathrm{grd}}/\mathrm{cert\_risk})$).

Our audit uncovered three critical methodological issues in that comparison:

1. **Exposure Reduction Confound**:
   - Policy (b) (`vol_cap`) admits a mean notional of **$\$829{,}463$**, whereas Policy (c) (`vol_plus_guard`) multiplies two independent numbers in $(0, 1]$, reducing mean admitted notional to **$\$734{,}945$** (an **$11.39\%$ exposure reduction** relative to `vol_cap`, and a $26.5\%$ haircut relative to $\$1\text{M}$).
   - Because losses and margin crossings scale with admitted exposure, much of the reported breach-rate reduction ($38.69\% \to 31.28\%$, $\Delta = -7.41\text{ pp}$) and tail-excursion loss reduction ($\$163{,}099 \to \$136{,}670$, $\Delta = -\$26{,}429$) was driven by simply trading smaller size.

2. **Test-Sample Calibration in Secondary Capacity**:
   - In lines 381–389 of `recompute_prereg_oct21_followup.py`, the secondary matched-notional metric used `mae_te = B24["MAE_day"].to_numpy()` (the **realized test-sample adverse excursions**) to compute the scalar multiplier $c_{\mathrm{vg}} = \mathrm{quantile}(450 / (q_c \cdot \mathrm{mae}), 1 - \mathrm{target\_rate})$.
   - This used test-sample outcomes to calibrate policy sizing, violating Global Research-Integrity Rule 8.
   - Furthermore, multiplying $q_c$ by $c_{\mathrm{vg}} = 1.6589$ allowed individual trades to exceed $\$1\text{M}$ (up to $\$1.66\text{M}$), violating the per-trade Rule 15c3-5 capital ceiling.

3. **Stylized Absolute Excursion vs. Realized Liquidation**:
   - The metric $q_t \cdot \mathrm{MAE}_{\mathrm{day}} \ge 450\text{ bp}$ measures two-sided absolute log-price displacement $\max_{t} |p_t - p_0|$, not an actual exchange liquidation. A directional long position only suffers if price drops, and a short position only suffers if price rises.

---

## 2. Fair Multi-Policy Evaluation (Tasks 4.2–4.5)

To establish fair economic comparisons, `hardened_empirical_audits.py` evaluated six distinct risk-control policies:
1. `static_cap`: Flat $q_t = 1.0$ ($\$1\text{M}$ fixed notional).
2. `vol_cap`: Inverse realized volatility throttle $q_t = \min(1, k_{\mathrm{vol}}/\mathrm{rv}_{\mathrm{morn}})$.
3. `margin_rule`: Inverse 99th percentile price jump throttle $q_t = \min(1, k_{\mathrm{var}}/\mathrm{VaR}_{99,\mathrm{morn}})$.
4. `inventory_cap`: Inverse morning flow pressure throttle $q_t = \min(1, k_{\mathrm{inv}}/\mathrm{inv}_{\mathrm{morn}})$.
5. `guard_only`: Inverse certified multi-step response throttle $q_t = \min(1, k_{\mathrm{grd}}/\mathrm{cert\_risk})$.
6. `vol_plus_guard`: Combined volatility and certified response throttle $q_t = q_{\mathrm{vol}} \times q_{\mathrm{grd}}$.

All threshold parameters $(k_{\mathrm{vol}}, k_{\mathrm{var}}, k_{\mathrm{inv}}, k_{\mathrm{grd}})$ were fitted strictly on the $2024$ training panel.

### 2.1 Benchmark Comparison Table Across 42 Untouched Test Dates ($N_{\mathrm{test}} = 796$ Symbol-Days)

| Policy | Mean Notional (\$) | Median Notional (\$) | Stylized Breach Rate (450 bp) | Directional Long Breach Rate | Directional Short Breach Rate | $\text{ES}_{95}$ Loss (\$) | Net $\text{ES}_{95}$ Long (+Fees/Fund) | Net $\text{ES}_{95}$ Short (+Fees/Fund) | Max Drawdown (\$) | $\text{ES}_{95}$ per \$1M Notional |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Benchmark 4A: Baseline Capped Rule 15c3-5 ($q_t \in (0, 1]$)** | | | | | | | | | | |
| `static_cap` | $1{,}000{,}000$ | $1{,}000{,}000$ | $51.88\%$ | $23.12\%$ | $31.78\%$ | $\$248{,}756$ | $\$157{,}510$ | $\$214{,}760$ | $\$840{,}783$ | $\$248{,}756$ |
| `vol_cap` | $829{,}463$ | $923{,}093$ | $38.69\%$ | $16.08\%$ | $22.74\%$ | $\$163{,}099$ | $\$116{,}394$ | $\$151{,}070$ | $\$532{,}740$ | $\$196{,}632$ |
| `margin_rule` | $826{,}028$ | $935{,}008$ | $38.19\%$ | $15.58\%$ | $22.74\%$ | $\$162{,}260$ | $\$116{,}577$ | $\$148{,}842$ | $\$570{,}734$ | $\$196{,}434$ |
| `inventory_cap` | $870{,}581$ | $931{,}353$ | $42.34\%$ | $18.34\%$ | $26.13\%$ | $\$191{,}362$ | $\$119{,}187$ | $\$172{,}468$ | $\$794{,}410$ | $\$219{,}809$ |
| `guard_only` | $820{,}912$ | $927{,}798$ | $39.57\%$ | $17.59\%$ | $24.12\%$ | $\$161{,}901$ | $\$111{,}386$ | $\$145{,}654$ | $\$832{,}113$ | $\$197{,}221$ |
| `vol_plus_guard` | $734{,}945$ | $865{,}798$ | $31.28\%$ | $14.32\%$ | $18.34\%$ | $\$136{,}670$ | $\$101{,}439$ | $\$124{,}447$ | $\$305{,}617$ | $\$185{,}959$ |
| **Benchmark 4B-ii: Unit Training-Normalized Notional ($\mathbb E_{\mathrm{train}}[q_t] = \$1\text{M}$)** | | | | | | | | | | |
| `static_cap` | $1{,}000{,}000$ | $1{,}000{,}000$ | $51.88\%$ | $23.12\%$ | $31.78\%$ | $\$248{,}756$ | $\$157{,}510$ | $\$214{,}760$ | $\$840{,}783$ | $\$248{,}756$ |
| `vol_cap` | $963{,}874$ | $1{,}099{,}197$ | $48.37\%$ | $22.11\%$ | $28.39\%$ | $\$188{,}508$ | $\$134{,}232$ | $\$174{,}470$ | $\$623{,}252$ | $\$195{,}573$ |
| `margin_rule` | $967{,}835$ | $1{,}114{,}626$ | $48.12\%$ | $21.61\%$ | $28.39\%$ | $\$189{,}635$ | $\$136{,}421$ | $\$173{,}962$ | $\$665{,}693$ | $\$195{,}937$ |
| `inventory_cap` | $1{,}187{,}298$ | $1{,}274{,}052$ | $58.17\%$ | $26.38\%$ | $36.43\%$ | $\$257{,}002$ | $\$163{,}282$ | $\$230{,}580$ | $\$1{,}083{,}957$ | $\$216{,}460$ |
| `guard_only` | $1{,}132{,}274$ | $1{,}288{,}515$ | $55.53\%$ | $26.38\%$ | $33.67\%$ | $\$223{,}521$ | $\$154{,}001$ | $\$201{,}125$ | $\$1{,}143{,}772$ | $\$197{,}409$ |
| `vol_plus_guard` | $1{,}070{,}675$ | $1{,}274{,}944$ | $48.62\%$ | $23.74\%$ | $28.64\%$ | $\$197{,}395$ | $\$147{,}066$ | $\$180{,}447$ | $\$445{,}487$ | $\$184{,}365$ |
| **Benchmark 4C-i: Strictly Training-Calibrated Matched $\text{ES}_{95}$ Risk Budget** | | | | | | | | | | |
| `static_cap` | $813{,}079$ | $813{,}079$ | $40.58\%$ | $16.83\%$ | $23.99\%$ | $\$202{,}258$ | $\$128{,}069$ | $\$174{,}618$ | $\$683{,}623$ | $\$248{,}756$ |
| `vol_cap` | $963{,}874$ | $1{,}099{,}197$ | $48.37\%$ | $22.11\%$ | $28.39\%$ | $\$188{,}508$ | $\$134{,}232$ | $\$174{,}470$ | $\$623{,}252$ | $\$195{,}573$ |
| `margin_rule` | $959{,}928$ | $1{,}105{,}518$ | $47.74\%$ | $21.48\%$ | $28.27\%$ | $\$188{,}085$ | $\$135{,}307$ | $\$172{,}541$ | $\$660{,}253$ | $\$195{,}937$ |
| `inventory_cap` | $979{,}867$ | $1{,}051{,}465$ | $49.37\%$ | $20.98\%$ | $30.78\%$ | $\$212{,}099$ | $\$134{,}756$ | $\$190{,}293$ | $\$894{,}567$ | $\$216{,}460$ |
| `guard_only` | $1{,}029{,}232$ | $1{,}171{,}254$ | $51.01\%$ | $23.24\%$ | $30.40\%$ | $\$203{,}179$ | $\$140{,}011$ | $\$182{,}821$ | $\$1{,}039{,}682$ | $\$197{,}409$ |
| `vol_plus_guard` | $1{,}040{,}119$ | $1{,}238{,}586$ | $47.36\%$ | $22.86\%$ | $27.51\%$ | $\$191{,}764$ | $\$142{,}869$ | $\$175{,}298$ | $\$432{,}777$ | $\$184{,}365$ |

---

## 3. Key Scientific Findings & Synthesis

1. **At Matched Training Notional (Benchmark 4B-ii)**:
   - When scaled on the training set so that both policies target $\$1\text{M}$ mean exposure, `vol_plus_guard` achieves an identical breach rate ($48.62\%$ vs. $48.37\%$, $\Delta = +0.25\text{ pp}$, $95\%\text{ CI}: [-5.64, +5.16]\text{ pp}$) and comparable tail loss ($\$197{,}395$ vs. $\$188{,}508$, $\Delta = +\$8{,}887$, $95\%\text{ CI}: [-\$25{,}253, +\$33{,}587]$).
   - In statistical significance testing, the confidence interval covers zero symmetrically, showing that **under matched average notional exposure, the combined guard does not provide a statistically significant reduction in breach rates over a conventional volatility throttle**.

2. **Where the Guard Provides Measurable Decision Value**:
   - **Tail Downside Truncation (Max Drawdown)**: Under identical training-normalized exposure, `vol_plus_guard` reduces the worst-case sample loss from **$\$623{,}252$** (`vol_cap`) and **$\$840{,}783$** (`static_cap`) down to **$\$445{,}487$** (a **$28.5\%$ reduction in peak catastrophic loss**). The certified response filter throttles aggressively on extreme non-normal liquidity-spiral days when volatility alone has not yet spiked.
   - **Capacity Gain at Matched Training Risk Budget (Benchmark 4C-i)**: When policies are calibrated on training data to deliver the exact same risk budget ($\mathrm{ES}_{95}$), `vol_plus_guard` admits **$\$1{,}040{,}119$** mean notional versus **$\$963{,}874$** for `vol_cap` (+**$7.91\%$ incremental capacity** at matched training risk), and achieves a normalized tail loss of **$\$184{,}365$ per $\$1\text{M}$ deployed** (vs. $\$195{,}573$ for `vol_cap`).

3. **Directional vs. Stylized Breach Rates**:
   - Incorporating realistic 18-hour directional mark-to-market accounting with $10\text{ bp}$ taker fee and funding costs reveals that realized breach rates are **$14.3\%$ (long) and $18.3\%$ (short)** under `vol_plus_guard`, compared to the stylized two-sided figure of $31.3\%$. The two-sided metric counts a day as a breach even if price moves favorably first, inflating modeled risk.
