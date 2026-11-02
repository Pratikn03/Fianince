# Referee Report — Professor 3 (Empirical Finance Econometrician)

## A. Verdict
The empirical sections of this paper (Sections 6.3–6.4 and Appendix H) are a fascinating paradox. On one hand, the authors display exemplary scientific candor: they report failed pre-specified hypotheses prominently in Table 1 (Page 5) and the Abstract, disclose that a split-panel jackknife bias correction pushes the Binance 5-minute class position persistence to a near-unit-root median of $1.0008$, show that their out-of-sample return forecast test failed ($\Delta R^2 = -1.09$ percentage points), and explicitly admit that their GitHub "pre-registration" was pushed in the same commit batch as the results. On the other hand, the core headline empirical comparison—comparing the confidence-interval width of $\hat{r}_c$ from an ARX(1) on observed class *positions* against the confidence-interval width of two exponential decay rates fitted by nonlinear least squares to a 12-lag (or 96-lag) distributed lag of *prices/flow on returns*—is an econometrically mismatched comparison of two completely different statistical objects. Estimating an AR(1) coefficient on a smooth, near-unit-root stock variable (open-interest-normalized net positions) will *mechanically* yield a tight confidence interval of width $O(T^{-1/2})$ (or $O(T^{-1})$ under near-unit-root asymptotics), whereas fitting a two-exponential mixture $\sum_{k=1}^2 w_k r_k^m$ to noisy return/flow regressions without knowing whether two exponentials even exist in the data is a textbook weakly identified nonlinear problem (Andrews & Cheng 2012). While the authors admit this is "descriptive, not a race between estimators of the same object", the paper still headlines the width ratios (9x to 71x in CFTC; 7.3x in Binance) as empirical validation of the theory.

## B. Scores
- **Score for posting this version:** 6.5 / 10
- **Score after fixes:** 8.5 / 10

---

## C. Detailed Issues (FATAL / MAJOR / MINOR)

### FATAL Issues
*None. Every empirical limitation that would normally be fatal—the unit-root jackknife result, the OOS forecast failure, the basis/spot return mismatch in CFTC, and the same-push GitHub timestamp—is already explicitly disclosed by the authors in the text.*

### MAJOR Issues

1. **Section 6.3 (Page 57–58, Table 15) — Spot/Yield Proxies Instead of Actual CME Futures Returns in the CFTC Regressions.**
   - **Quote:** `"Weekly returns from Binance spot (Bitcoin, Ether) and Yahoo Finance (others; the Treasury return is minus the change in the 10-year yield), not from the CME futures contracts themselves; the basis between them is ignored."` (p. 58, Table 15 note).
   - **Status:** VERIFIED.
   - **Why it matters:** A financial econometrician who works with CFTC Commitments of Traders (CoT) data will stop cold at this footnote. First, you are testing whether leveraged funds in CME futures respond positively or negatively to weekly returns ($w_c$ in $n_{c,t} = \alpha_c + r_c n_{c,t-1} + w_c ret_t$), and you make a big deal on p. 58 about H2 failing because leveraged funds have $\hat{w}_{fast} < 0$ in CME Bitcoin, CME Ether, and E-mini S&P 500, attributing this to cash-futures basis trades! If leveraged funds are trading the *cash-futures basis*, using **Binance spot returns** instead of CME futures returns introduces classical errors-in-variables / basis-shock bias directly into $ret_t$! Second, continuous CME front-month futures prices are available for free on Yahoo Finance (`BTC=F`, `ETH=F`, `ES=F`, `ZN=F`, `6E=F`, `6J=F`, `CL=F`, `NG=F`) or FRED. There is no excuse for using spot crypto and 10-year constant-maturity yield changes instead of actual futures contract returns (or at least verifying that the sign of $\hat{w}_{fast}$ is unchanged when using rolled futures returns).
   - **Exact fix:** Either re-run the 8-market CFTC script (`Part 11: C3_cot_data, C4_cot_disclosure`) using actual Yahoo Finance continuous futures tickers (`ES=F`, `ZN=F`, `6E=F`, `6J=F`, `CL=F`, `NG=F`, `BTC=F`, `ETH=F`)—which takes 5 minutes and is not a "new experiment" but fixing a data proxy—or state prominently in the main text of Section 6.3 (not buried in the Table 15 caption) that spot/yield proxies are used and explain how cash-futures basis fluctuations affect $\hat{w}_c$.

2. **Section 6.3 & Section 6.4 (Page 57 & Page 60–61) — Econometric Validity of Percentile Moving-Block Bootstrap Near a Unit Root.**
   - **Quote:** `"Intervals come from a 13-week moving-block bootstrap; near a unit root such percentile intervals are pointwise and can understate uncertainty, and price-only intervals that fill the admissible range are better read as a sign of weak identification than as calibrated 95% intervals."` (p. 57, Section 6.3). And on p. 61: `"Day-demeaned regressions bias persistence down; corrected by a split-panel jackknife, the median tagged rate is 1.0008 per five minutes, and the corrected interval lies below one in only 7 of 87 class fits."`
   - **Status:** VERIFIED.
   - **Why it matters:** In Table 15 (CFTC), the estimated slow persistence is $0.999$ (WTI), $0.996$ (Euro), $0.993$ (10-year T-note), and $0.986$ (Bitcoin), and fast persistence is $0.992$ in 10-year T-notes (`[0.985, 0.998]`, width `0.013`, giving your largest width ratio of `71.4`!). It is a foundational theorem in time-series econometrics (e.g., Phillips 1987; Andrews 1993; Mikusheva 2007) that: (a) the asymptotic variance of $\hat{r}$ near $r=1$ shrinks at rate $O(T^{-1})$ rather than $O(T^{-1/2})$ (super-consistency), which *mechanically* makes the confidence interval around $\hat{r} = 0.992$ tiny (`0.013` wide) compared to an interior parameter! Thus, the `71.4` width ratio in 10-year T-notes is heavily driven by $T^{-1}$ near-unit-root scaling of stock positions! (b) In Binance (Section 6.4), Table 16 reports *uncorrected* day-demeaned intervals (`0.9889 [0.9842, 0.9935]`) where the Nickell (1981) within-day fixed-effect bias ($- (1+r)/(T_{day}-1)$ with $T_{day} = 288$ five-minute bars, which is $\approx -2/287 \approx -0.007$!) creates the illusion of a stationary memory rate around $0.989$ when the true process is a random walk ($r \approx 1.0008$)!
   - **Exact fix:**
     1. In Section 6.3 (p. 58), explicitly note that because $1 - \hat{r}_{fast}$ is close to zero (especially in 10-year T-notes where $\hat{r}_{fast} = 0.992$), the narrow interval (`0.013`) partly reflects $O(T^{-1})$ near-unit-root scaling of persistent position stocks rather than superior signal-to-noise ratio alone.
     2. In Table 16 (p. 60), add a footnote or column reporting the split-panel jackknife bias-corrected point estimate alongside the day-demeaned estimate so a reader skimming Table 16 does not misread `0.9889` as an unbiased 5-minute decay rate before reaching p. 61.

3. **Section 6.3 & 6.4 (Page 57 & Page 60) — The "Price-Only Competitor" Specification is Not Specified as a Clean Equation.**
   - **Quote:** `"The price-only alternative fits a two-exponential kernel to twelve weekly return lags."` (p. 57). `"The price-only alternative regresses signed five-minute taker flow on twelve lagged five-minute returns and fits two exponentials to the kernel; it estimates the memory rates without class information."` (p. 60).
   - **Status:** VERIFIED.
   - **Why it matters:** In Binance (Section 6.4), you have signed 5-minute taker flow, so you regress aggregate flow on 12 lagged returns and fit a 2-exponential kernel to the impulse response coefficients. What did you regress on 12 weekly return lags in the CFTC test (Section 6.3), where there is *no* weekly aggregate signed taker flow in Yahoo Finance? The text on p. 57 (`"fits a two-exponential kernel to twelve weekly return lags"`) does not state what the dependent variable $Y_t$ of that regression is! Furthermore, if you fit a two-exponential kernel to return autocorrelations in CFTC markets where weekly returns are nearly serially uncorrelated (a martingale!), the true impulse response coefficients at lags $1,\dots,12$ are nearly zero ($w_1 \approx w_2 \approx 0$). Under $w_k = 0$, the decay rates $(r_1, r_2)$ are completely unidentified nuisance parameters (Davies 1977; Andrews & Cheng 2012), so their bootstrap interval *must* span $[0, 0.99]$!
   - **Exact fix:** On p. 57, write down the exact regression equation estimated for the CFTC price-only route (stating the dependent variable, how the 12 lag coefficients are obtained, and the constrained nonlinear least-squares objective on $[0, 0.99]^2$), and state explicitly that because weekly futures returns have near-zero autocorrelation, the price-only weights are near zero and the decay rates are weakly identified nuisance parameters in the sense of Andrews and Cheng (2012).

4. **Section 6.4 (Page 59–60) — Stocks (Positions) vs. Flows Mapping.**
   - **Quote:** `"We treat a class's reported net position as the observable counterpart of its cohort state: it obeys the same one-lag recursion class by class, so the block-diagonal information structure of Proposition 6.1 carries over. The mapping is an assumption, because the reports are positions rather than flows..."` (p. 59–60).
   - **Status:** VERIFIED.
   - **Why it matters:** In Section 2, Equation (1) has *order flow* (change in inventory) equal to $q_i y_{i,t}$, whereas Remark 2.2 (p. 18) shows that with inventory holding costs, optimal order flow is $u_{i,t}^* = q_i y_{i,t} - \psi_{inv,i} I_{i,t-1}$, which means *inventory* $I_{i,t} = (1 - \delta_{inv} - \psi_{inv,i})I_{i,t-1} + q_i y_{i,t}$ is a two-state AR(2) filter of prices (one root from inventory mean-reversion $1-\delta_{inv}-\psi_{inv,i}$, and one root from belief memory $1-\eta_i$)! When you estimate an ARX(1) on CFTC or Binance *net positions* $I_{i,t}$ (`n_{c,t} = r_c n_{c,t-1} + w_c ret_t`), $\hat{r}_c$ is estimating the slow inventory-turnover root $1 - \delta_{inv} - \psi_{inv,i} \approx 1$, *not* the belief-updating memory $1-\eta_i$!
   - **Exact fix:** Add 2 sentences in Section 6.3/6.4 pointing back to Remark 2.2 (p. 18): explain that under inventory holding costs, net positions $I_{i,t}$ accumulate order flow $u_{i,t}$ and therefore inherit an inventory-adjustment root near unity on top of the belief root $r_i$, which explains why position levels $n_{c,t}$ exhibit near-unit-root persistence in Binance while their changes $\Delta n_{c,t}$ measure net class flow.

---

## D. Tasks 1–6 Required by the Prompt

### Task 1: Audit of the CFTC Test (8 Futures Markets)
- **Specification & Inference:** Regresses $n_{c,t} = (\text{long} - \text{short})/\text{OI}$ on $n_{c,t-1}$ and weekly return $ret_t$ with a 13-week moving-block bootstrap. As noted in Major Issues 1–3, using spot/yield proxies instead of CME futures returns is a flaw that is easily fixed, and the 13-week bootstrap percentile intervals near $r=1$ are subject to local-to-unity distortion (which the authors candidly note on p. 57).
- **Is `"class reports restrict persistence that prices leave unrestricted"` a fair summary?** Yes, as a literal description of the confidence intervals, *provided* it is always paired with the caveat that the price-only route is attempting to identify latent exponential decay rates from near-martingale weekly returns (where the signal weights are near zero and thus unidentified).
- **Is the price-only comparison a fair competitor or a straw man?** On weekly return data alone (CFTC), fitting a two-exponential kernel to 12 lags of returns is close to a **straw man** because weekly returns have virtually no serial correlation; however, on 5-minute Binance signed taker flow vs. 96 lags of 5-minute returns (where order-flow autocorrelation is strong and well-documented), the horizon-matched 96-lag comparison (median width ratio 7.3 across 29 of 29 markets, p. 61) is much fairer.

### Task 2: Audit of the Binance Tests & the Near-Unit-Root Persistence
- **Does the near unit root ($1.0008$ after split-panel jackknife bias correction) undermine the claim?** It undermines any claim that $\hat{r}_c$ is a stationary *learning memory rate* $1-\eta_c \in (0,1)$, **and the authors explicitly say so** in the Abstract (p. 1), Table 1 (p. 5), and Section 6.4 (p. 61): `"Within a day the class ratios are close to a random walk, so the half-lives of a few hours reported here are largely produced by removing each day's mean. The evidence therefore supports a narrower claim than identification of class memory: positioning data restrict a persistence parameter that prices cannot bound"`. This level of self-critical honesty is rare and completely protects the authors from an econometric referee accusing them of hiding a unit root.

### Task 3: Audit of the Failed Out-of-Sample Forecast Test
- **Is it reported honestly and prominently enough?** **Yes, exemplary.** It is reported in the last sentence of the Abstract (`"a pre-specified test of what prices do reveal failed, and class data did not improve return forecasts"`), in Table 1 on Page 5 (`"Fail (\Delta R^2 = -1.09 points, inconclusive)"`), in Section 6.4 (p. 62), and in the Conclusion (p. 67).

### Task 4: Judgment of the Meaning of "Registered"
- **How it is described:** Page 2 ("Reproducibility") states: `"'Registered' or 'pre-specified' in this paper means that the authors wrote the specification and committed it to the public repository before opening the test data; because specification and results reached the repository in the same push, this is the authors' declaration, not independent preregistration."`
- **What a sceptic would say:** A sceptical econometrician will point out that local git commit timestamps are controlled by the user's system clock and can be amended (`git commit --amend` or `git rebase`) prior to a `git push`. Therefore, when the specification JSON and the results JSON reach GitHub in the *same push*, the commit history provides **zero cryptographic proof** of temporal ordering—it is purely an honor-system declaration by the authors, reinforced only by the fact that so many of their pre-specified tests *failed*.
- **Exact fix:** Globally replace the word `"Pre-registered"` / `"registered"` in Table 15, Table 16, Table 17, and the text with `"Pre-specified"`, keeping the explanation on p. 2. In empirical finance, "pre-registered" implies an external time-stamped registry (OSF, AEA, AsPredicted, or an earlier independent GitHub push before data existed).

### Task 5: Audit of the Mapping from Class Positions to Cohort States Across the Paper
- Checked across Abstract (p. 1), Introduction (p. 5, 7), Table 5 (p. 15), Section 6.3–6.4 (p. 56–64), and Conclusion (p. 66–67). Every single one of those locations explicitly distinguishes `"fitted position persistence"` from `"learning memory"`.
- **One spot to tighten:** In **Section 7 ("What disclosure buys", p. 64)**, the text says: `"Calibrated to Binance's published class ratios, separating the memories of the top-trader group and of all accounts in BTCUSDT would take prices alone about 333 times as long (Theorem 6.2)."` Change `"separating the memories"` on p. 64 to `"separating the fitted day-demeaned persistences (used as an illustrative calibration)"`.

### Task 6: Data Availability and Reproducibility Check
- **Could I reproduce one table from the description given?** **Yes.** Together with `paper1_reproducibility_map.pdf` (Appendix J), every table is mapped to an exact Python script or Colab notebook (`Part 11: C3_cot_data, C4_cot_disclosure -> P11_cot.json` for Table 15; `recompute_prereg_oct21_followup.py -> R_P1_disclosure_state_oos.json` for Table 17) and a public GitHub URL (`https://github.com/Pratikn03/Fianince`). Adding the exact start date for each CFTC market and the exact price-only objective function (Major Issue 3) will make Table 15 100% self-contained even without opening the code.

---

## E. Cut Plan to Reach Target Page Count
1. **Cut Appendix H (pp. 106–112, 6.5 pages):** Appendix H is an entirely separate empirical note on high-frequency VAR(1) timing alignment and Binance spot fee holidays. Removing it makes the paper much tighter and saves **6.5 pages**.
2. **Condense the narrative of the 3 follow-up Binance tests in Section 6.4 (pp. 61–62) by 1 page:** Since Table 1 (p. 5) already summarizes all passes and failures, the chronological story of the exploratory check, the 105-day follow-up, and the 58-day follow-up on pp. 61–62 reads like a lab notebook log. Summarize the net statistical finding in one tight paragraph.
3. **Cut Table 24 (p. 98, 0.5 pages) and Appendix C.4 / Table 19 (pp. 88–89, 1.5 pages).**

---

## F. Three Questions I Would Email the Authors
1. Why did you use Binance spot returns and 10-year Treasury yield changes in the CFTC regressions (Table 15) instead of actual rolled CME futures returns (`BTC=F`, `ES=F`, `ZN=F`), especially when interpreting the negative coefficient $\hat{w}_{fast} < 0$ as a cash-futures basis trade signature?
2. Since Binance class ratios are net *positions* $n_{c,t}$ that behave like a random walk within the day ($r_c \approx 1.0008$ after jackknife correction), what happens if you take first differences $\Delta n_{c,t}$ as a proxy for 5-minute class *net order flow* and estimate Proposition 6.1's IV regression on $\Delta n_{c,t}$?
3. In the CFTC price-only comparison (Section 6.3), what is the exact dependent variable and nonlinear least-squares objective used to fit the two-exponential kernel to 12 weekly return lags?

---

## G. Would I Forward This to a Colleague?
- **Answer:** **Yes** (specifically pointing out the refreshing honesty of Table 1's pass/fail reporting and the CFTC vs. price-only weak-identification diagnostic).
- **The one change that would make it much stronger:** Replace the spot/yield return proxies in the CFTC test (Table 15) with actual CME futures contract returns, and replace `"Pre-registered"` with `"Pre-specified"` in the table headers so no referee feels misled before reading the p. 2 disclaimer.
