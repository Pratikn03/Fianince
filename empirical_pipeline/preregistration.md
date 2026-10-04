# Pre-Registration Protocol: Multi-Venue, Multi-Regime Empirical Feedback Panel

**Date**: 2026-10-04  
**Project**: Machine Markets Empirical Microstructure Analysis  
**Repository Branch**: `codex/paper-evidence-repair-20260926`  
**Status**: Pre-registered prior to large-scale data ingestion.

---

## 1. Objective and Scientific Question

This study evaluates whether aggregate taker market-order flow exhibits stabilizing (contrarian) or destabilizing (trend-following/momentum) feedback on quote midpoints across liquid cryptocurrency markets, and whether the estimated closed-loop feedback parameters reside within the theoretical stability boundary established in the paper.

The baseline exploratory evidence on a 12-day April 2021 Coinbase sample identified:
1. Moderate positive reduced-form feedback: $\hat Q \in [0.007, 0.013]$.
2. Closed-loop persistence $\hat S \approx 0.935\text{--}0.942 < 1.0$, remaining strictly below the real-root instability boundary.
3. Statistical rejection of the pure contrarian cone ($\hat b \le 0$) via Kodde-Palm / Wolak / CM tests ($p < 0.01$ for BTC and ETH).

This protocol pre-registers the empirical architecture for a systematic 768 asset-day panel across 2021–2024 and out-of-sample data (`1-09-1-20.csv`), preventing post-hoc specification searching.

---

## 2. Target Panel Design

### 2.1 Universe
8 top liquid crypto assets quoted against USDT:
1. `BTC` (Bitcoin)
2. `ETH` (Ethereum)
3. `SOL` (Solana)
4. `BNB` (Binance Coin)
5. `XRP` (Ripple)
6. `ADA` (Cardano)
7. `DOGE` (Dogecoin)
8. `LTC` (Litecoin)

### 2.2 Time Horizon and Sampling Schedule
* **Horizon**: 48 calendar months (January 2021 through December 2024).
* **Schedule**: 2 pre-scheduled days per month:
  * Day A: The 10th of each month (00:00:00 to 23:59:59 UTC).
  * Day B: The 24th of each month (00:00:00 to 23:59:59 UTC).
* **Total Sample Size**: $8 \text{ assets} \times 48 \text{ months} \times 2 \text{ days} = 768 \text{ asset-days}$.
* **Data Venue**: Binance Public Archive (Binance Vision) spot `aggTrades` and USDⓈ-M futures `bookTicker`.
* **Out-of-sample Holdout Dataset**: High-frequency order book depth file `1-09-1-20.csv` (1.2 GB, January 9–20, 2023, BTCUSDT).

---

## 3. Variable Definitions and Filtering Rules

### 3.1 Raw Trades to 1-Second Aggregates
From Binance `aggTrades` (each record: trade ID, price $p$, quantity $q$, timestamp $t_{ms}$, buyer-is-maker flag $m$):
1. **Timestamp**: Assigned to integer UTC second $T = \lfloor t_{ms} / 1000 \rfloor$.
2. **Taker Side**:
   * If `buyer_is_maker == True`: seller was taker $\implies$ aggressive sell.
   * If `buyer_is_maker == False`: buyer was taker $\implies$ aggressive buy.
3. **Signed Flow**:
   $$f_T = \sum_{i \in T, \text{buy}} p_i q_i - \sum_{i \in T, \text{sell}} p_i q_i \quad \text{(quote currency notional)}$$
4. **Midpoint Proxy**:
   * Last trade price in second $T$, or best-bid/ask midpoint from `bookTicker` where available.

### 3.2 Time Series Construction $(x_t, f_t)$
For a binning interval $\Delta$ seconds and reference window $W$ seconds:
1. Bin index $b = \lfloor T / \Delta \rfloor$.
2. Mid-price $P_b$ is the last observed quote in bin $b$ (forward-filled across inactive bins).
3. Bin flow $F_b = \sum_{T \in \text{bin } b} f_T$ (zero-filled across inactive bins).
4. Log mid-price in basis points: $p_b = 10^4 \cdot \ln(P_b)$.
5. Reference EMA with smoothing factor $\alpha = 2 / (W/\Delta + 1)$:
   $$m_b = \alpha p_b + (1 - \alpha) m_{b-1}$$
6. Deviation: $x_b = p_b - m_b$.
7. Regressor flow: $f_b = F_{b+1}$ (taker flow executed over $(t_b, t_{b+1}]$).
8. Burn-in: Discard the first $5 \cdot (W/\Delta)$ observations of each asset-day.

---

## 4. Frozen Estimators and Hypothesis Tests

### 4.1 Primary Estimand: Baseline VAR(1)
* Baseline parameter: $\Delta = 10\,\text{s}$, $W = 300\,\text{s}$.
* OLS regression per asset-day:
  $$x_{b+1} = J_{11} x_b + J_{12} f_b + e_{b+1}$$
  $$f_{b+1} = J_{21} x_b + J_{22} f_b + u_{b+1}$$
* Invariant quantities:
  $$\hat Q = \frac{\hat J_{12} \hat J_{21}}{1 - \hat J_{22}}, \qquad \hat S = \hat J_{11} + \hat Q, \qquad \hat{\mathcal L} = \frac{\hat Q}{1 - \hat J_{11}}$$
* Benchmark under martingale price: $a_0 = 1 - \alpha = 1 - 2/(W/\Delta + 1)$.

### 4.2 Robustness Grid
* $\Delta \in \{1, 5, 10, 30, 60\}$ seconds.
* $W \in \{60, 300, 900\}$ seconds.
* Persistence controls: $L \in \{1, 10, 30, 90\}$ lags of autoregressive flow $f_{b-1}, \dots, f_{b-L}$ in the $f$ equation to prevent sign-memory contamination.

### 4.3 Distributed Lag Kernel and Cone Testing
* Distributed lag regression up to lag $K = 10$:
  $$x_{b+1} = a x_b + \sum_{k=0}^{K} b_k f_{b-k} + \epsilon_{b+1}$$
* Standard errors: Newey-West HAC covariance with automatic lag truncation.
* Hypothesis tests:
  * $H_0^+: b \in \mathbb{R}_+^{K+1}$ (pure positive/momentum feedback cone).
  * $H_0^-: b \in \mathbb{R}_-^{K+1}$ (pure negative/contrarian feedback cone).
  * Test statistic: Kodde-Palm / Wolak / CM cone distance statistic $T = \min_{\theta \in \mathcal{C}} (\hat b - \theta)' \hat\Sigma^{-1} (\hat b - \theta)$.

### 4.4 Placebo Verification
* Day-scrambled placebo: pair $x^{(d)}$ with flow $f^{(d+1)}$ from the following day. Pre-registered expectation: $\hat Q_{\text{placebo}} \approx 0$ with 95% CI covering zero.

---

## 5. Identification Methodology

In addition to the reduced-form VAR(1), two structural identification strategies are pre-registered:

### 5.1 C1: Minimum-Distance Covariance Matching (SMM)
Match the sample cross-autocovariance sequence $\Gamma_k = \mathbb{E}[(x_t, f_t)' (x_{t-k}, f_{t-k})]$ for $k = 0, 1, \dots, K$ to the closed-loop structural model:
$$x_{t+1} = a x_t + \lambda f_t + \epsilon_{t+1}^x$$
$$f_{t+1} = (1 - \eta) f_t + \eta c x_t + \epsilon_{t+1}^f$$
with free parameters $\theta = (a, \lambda, \eta, c, \sigma_x^2, \sigma_f^2, \rho_{xf})$.
* Evaluate Hansen's $J$-test for over-identifying restrictions ($df = 2(K+1) - 7$).

### 5.2 C2: Rigobon Identification through Heteroskedasticity
Exploit diurnal or volatility-regime shifts in the covariance matrix of structural shocks:
$$\Omega_m = \text{Cov}\begin{pmatrix}\epsilon_t^x \\ \epsilon_t^f\end{pmatrix}_{\text{regime } m}, \quad m \in \{1, 2, \dots, M\}$$
* Estimate structural impact $\lambda$ and feedback $c$ from regime shifts in variance without requiring exogenous instrument variables.
* Perform Sargan-style over-identification test for $M \ge 3$ regimes.

---

## 6. Pre-Committed Decision Rules

1. **Replication of Positive Feedback**:
   * If pooled $\hat Q > 0$ with $p < 0.01$ across the 768 asset-days, confirm that public order flows exhibit aggregate positive feedback across crypto markets.
   * If pooled $\hat Q \le 0$ or fluctuates symmetrically around zero across regimes, report that the 12-day April 2021 finding was sample-specific and that multi-year crypto markets exhibit net liquidity buffering.
2. **Stability Boundary**:
   * If $\hat S < 1.0$ across $\ge 99\%$ of asset-days, report empirical support for subcritical feedback operation.
   * If $\hat S \ge 1.0$ or $\hat{\mathcal L} \ge 1.0$ is systematically observed during high-volatility regimes, report empirical evidence of supercritical feedback transitions.
3. **Contrarian Cone**:
   * If the negative cone is rejected across the majority of assets ($p < 0.05$), confirm the rejection of passive market buffering.
