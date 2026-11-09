# P7S: Does Stress Reveal What Calm Prices Hide?
## Pre-Registered Stress-Layer Empirical Specification (Option A: Binance USDT Perpetuals)

**Status:** REGISTERED & FROZEN  
**Date of Registration:** 8 November 2026  
**Venue & Dataset:** Binance USD-M Perpetuals (public daily 5-minute klines and 5-minute metrics)  
**Schema Probe Status:** COMPLETED & VERIFIED (`2024-01-02` UTC burned probe, archive hash verified)  
**Pre-Registration Principle:** Zero p-hacking. Specifications, thresholds, hypotheses, and decision criteria frozen before prospective holdout collection.

---

### 1. Theoretical Foundation and Research Question

The core paper's Section 7 establishes a fundamental two-layer dichotomy for feedback trading under position limits:
1. **Calm Layer (Theorem 7.2, Proposition 7.6):** When trader positions remain inside their limits ($|\ell_i m_{i,t}| \le 1$), market dynamics follow the linear model governed solely by the feedback kernel $k_m$. Proximity to limits is strictly unobservable; the only potential price leak is through forward-looking dealers who anticipate future breaches, which is exponentially small:
   $$\Delta f_{\text{leak}} \le \sum_{g} c_g \sqrt{2/\pi} \, \sigma_g e^{-\delta_g^2 / (2\sigma_g^2)}$$
2. **Stress Layer (Theorem 7.4):** When price moves are large enough to push traders toward or against their position caps, the aggregate flow departs nonlinearly from the linear kernel, separating populations according to their capacity and leverage distribution $\tilde{\mu}$.

**Hypothesis:** Price continuation/reversal dynamics following large moves ("stress") depend significantly on proximity to position limits, whereas dynamics following normal moves ("calm") do not.

---

### 2. Universe and Fixed Time Windows

- **Asset Universe ($N = 30$):**
  Top 30 liquid Binance USDT-margined perpetual futures:
  `BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `BNBUSDT`, `DOGEUSDT`, `XRPUSDT`, `ADAUSDT`, `AVAXUSDT`, `LINKUSDT`, `SUIUSDT`,
  `NEARUSDT`, `PEPEUSDT`, `SHIBUSDT`, `APTUSDT`, `DOTUSDT`, `LTCUSDT`, `WIFUSDT`, `ARBUSDT`, `OPUSDT`, `TIAUSDT`,
  `FTMUSDT`, `INJUSDT`, `RENDERUSDT`, `FETUSDT`, `GALAUSDT`, `FILUSDT`, `AAVEUSDT`, `UNIUSDT`, `ATOMUSDT`, `CRVUSDT`.
- **Calibration & Development Period:** `2026-08-01` to `2026-10-31` (92 days). Used strictly to calculate per-symbol return volatility $\sigma_i$, return percentiles, and open-interest terciles.
- **Holdout Period (Prospective):** `2026-11-16` to `2027-02-14` (90 days). Data are prospective and uncollected at registration. Opened strictly once.

---

### 3. State Variables and Event Construction

1. **Limit Proximity Proxy ($\Pi_{i,t}$):**
   At each 5-minute bar $t$ for asset $i$:
   $$\Pi_{i,t} = \frac{\text{sum\_open\_interest\_value}_{i,t}}{\max_{s \in [t - 30\text{d}, t]} \text{sum\_open\_interest\_value}_{i,s}} \in (0, 1]$$
   - $\text{State}_{i,t} = \text{High}$ if $\Pi_{i,t} \ge \tau_{i, \text{high}}$ (top tercile of development period).
   - $\text{State}_{i,t} = \text{Low}$ if $\Pi_{i,t} \le \tau_{i, \text{low}}$ (bottom tercile of development period).
2. **Standardized Moves ($r_{i,t}$):**
   $$r_{i,t} = \frac{\ln(P_{i,t} / P_{i,t-1})}{\sigma_{i, \text{dev}}}$$
   - **Stress Moves:** $|r_{i,t}| \ge q_{i}(0.99)$ (99th percentile of $|r|$ in development).
   - **Calm Moves:** $q_{i}(0.50) \le |r_{i,t}| \le q_{i}(0.80)$ (median to 80th percentile).
3. **Response Variable ($R_{i,t}^{(60)}$):**
   The subsequent 60-minute cumulative log return aligned with the sign of the initiating shock:
   $$R_{i,t}^{(60)} = \operatorname{sgn}(r_{i,t}) \cdot \ln\left(\frac{P_{i,t+12}}{P_{i,t}}\right)$$
   Positive values denote continuation; negative values denote reversal.

---

### 4. Primary Estimand and Hypotheses

For each asset $i$:
$$\beta_{i, \text{calm}} = \mathbb{E}\left[R_{i,t}^{(60)} \mid \text{Calm}, \Pi = \text{High}\right] - \mathbb{E}\left[R_{i,t}^{(60)} \mid \text{Calm}, \Pi = \text{Low}\right]$$
$$\beta_{i, \text{stress}} = \mathbb{E}\left[R_{i,t}^{(60)} \mid \text{Stress}, \Pi = \text{High}\right] - \mathbb{E}\left[R_{i,t}^{(60)} \mid \text{Stress}, \Pi = \text{Low}\right]$$

The primary population statistics average across all 30 assets:
$$\bar{\beta}_{\text{calm}} = \frac{1}{N} \sum_{i=1}^N \beta_{i, \text{calm}}, \qquad \bar{\beta}_{\text{stress}} = \frac{1}{N} \sum_{i=1}^N \beta_{i, \text{stress}}$$
$$\text{DiD} = \bar{\beta}_{\text{stress}} - \bar{\beta}_{\text{calm}}$$

#### Registered Hypotheses:
- **H1 (Calm Silence):** $|\bar{\beta}_{\text{calm}}| < E$, evaluated by two one-sided tests (TOST) at 5% significance, where $E = 0.0015$ (calibrated from development standard error).
- **H2 (Stress Reveals):** $\text{DiD} \neq 0$ with two-sided bootstrap $p < 0.05$.
- **Inference:** Stationary block bootstrap by date with mean block length 5 days ($B = 9,999$ replications), joint resampling across assets, fixed seed `20261108`.

#### Decision Rule:
- **SUPPORTIVE:** H1 holds ($|\bar{\beta}_{\text{calm}}| < E$) AND H2 rejects ($\text{DiD} \neq 0, p < 0.05$).
- **INCONSISTENT:** H1 rejects ($|\bar{\beta}_{\text{calm}}| \ge E$), indicating that calm moves leak limit proximity into prices beyond the theoretical bound.
- **INCONCLUSIVE:** All other outcomes.

---

### 5. Pre-Specified Sensitivity and Confounds

1. **Volatility Normalization:** Replace fixed $\sigma_{i, \text{dev}}$ with trailing 1-day realized volatility $\sigma_{i, t}^{\text{RV}}$.
2. **Time-Shift Placebo:** Lead $\Pi_{i,t}$ by 30 calendar days. Under null of no look-ahead, DiD must collapse to zero.
3. **Volume Conditioning:** Add taker volume terciles as a covariate state.
4. **Top-Trader Sentiment:** Replace $\Pi_{i,t}$ with the absolute log top-trader long/short ratio $|\ln(\text{top\_ls\_ratio})|$.
