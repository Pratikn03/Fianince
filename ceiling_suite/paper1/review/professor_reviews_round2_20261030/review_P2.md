# Referee Report — Professor 2 (Market Microstructure Theorist / Top-Three Finance AE)

## A. Verdict
This paper asks whether an observer watching prices and anonymous order flow can infer the distribution of adaptation speeds ("memories") across heterogeneous algorithmic trading groups, and how much data or trading capital it takes compared to observing class-tagged order flow. The mathematical execution of the statistical identification bounds is impressive, and the authors deserve credit for intellectual honesty in reporting where their empirical tests fail and acknowledging in Section 8 that they do not model a supervisory decision where cohort attribution changes optimal policy. However, judged as a financial economics paper, the model is an engineering control system dressed in market terminology: price impact $\kappa$ and price reversion $a$ are exogenous constants rather than equilibrium dealer pricing rules; the fundamental value $p^*$ is assumed *known* to the observer; the traders follow mechanical exponential moving averages of past pricing errors regardless of whether doing so is profitable; and the flagship "active probing" benchmark prices an experiment—repeatedly resetting the market to zero state and trading against momentum traders to measure their lag-2 impulse response—that no regulator or rational arbitrageur would ever run. Until the paper embeds its identification question in a genuine economic decision problem and connects to the finance literature on learning and experimentation, top finance economists will view it as an applied probability paper with a regulatory motivation tacked on.

## B. Scores
- **Score for posting this version:** 5.5 / 10
- **Score after fixes:** 7.5 / 10

---

## C. Detailed Issues (FATAL / MAJOR / MINOR)

### FATAL Issues
*None. The authors explicitly disclaim equilibrium foundations, state that regulators do not probe, and admit the missing decision link in the Introduction and Conclusion, which prevents the modelling limitations from being "fatal misrepresentations."*

### MAJOR Issues

1. **Section 2 (Page 16–18) — The "Known Fundamental $p^*$" Assumption Destroys the Microstructure Premise.**
   - **Quote:** `"Let p_t be the price, p^* the fundamental value and x_t = p_t - p^* the pricing error. A reduced-form dealer sector absorbs net order flow with price impact \kappa > 0... The observer is taken to know the fundamental value p^* so the pricing error x_t is observed"` (p. 16, Section 2; p. 18, Remark 2.2).
   - **Status:** VERIFIED.
   - **Why it matters:** In market microstructure (Kyle 1985; Glosten-Milgrom 1985; Hasbrouck 1991), the entire reason order flow moves prices ($\kappa > 0$) is that dealers and observers *do not know* the fundamental value $p^*$ and infer it from order flow! If the observer already knows $p^*$ and knows $\kappa$ and $a$, and if the Kalman desks are trying to filter a latent trend (Lemma 2.1) while feeding on $x_t = p_t - p^*$, there is an internal economic contradiction: Lemma 2.1 motivates $\eta_i$ as a steady-state Kalman gain for filtering a random-walk fundamental/trend $v_t$ from noisy signals, yet Equation (2) has the cohorts updating on the *pricing error* $x_t = p_t - p^*$ with $p^*$ constant! Why would a Bayesian Kalman filter desk trade in proportion to the transitory pricing error $x_t$ (buying when $x_t > 0$, i.e., when the asset is *overpriced* relative to known $p^*$, losing money on average)?
   - **Exact fix:** Explicitly reconcile Lemma 2.1 with Equations (1)–(2) in Section 2 (p. 18): explain that desks observe price changes or noisy trend signals and cannot separate fundamental innovations from transitory pricing errors $x_t$, so their linear filter inadvertently loads on $x_t$. Acknowledge upfront that for the observer, assuming $p^*$ is known is an *a fortiori* benchmark (it gives the observer *more* information than any real market observer has, which makes the lower bounds on identification cost even stronger).

2. **Section 1 & Section 8 (Page 4, Page 67, & Appendix I Page 112) — The Missing Economic Decision Problem.**
   - **Quote:** `"We do not yet model a decision in which knowing the individual groups, rather than their combined response, changes what a supervisor should do; that link is the main open economic question (Section 8)."` (p. 4, Section 1; repeated on p. 67, Section 8).
   - **Status:** VERIFIED.
   - **Why it matters:** An economist's immediate reaction to Theorem 3.1 (`"prices reveal only the merged measure M"`) and Remark 5.3 (`"The hard directions carry no risk... cumulative price risk does not move"`) is: **So what?** If two economies have the exact same impulse response $H(z)$ up to $O((\Delta\eta)^{2K-1})$, and as you prove in your own Finite-Horizon Supplement (`paper1_finite_horizon_supplement.pdf` / Appendix I), a risk-constrained inventory desk only cares about the aggregate gain $G = \sum_{t<H} h_t$ and achieves optimal net value *without* identifying individual cohorts, why would *anyone* (regulator, exchange, or trader) ever pay $\Theta((\Delta\eta)^{-(4K-2)})$ to separate the cohorts? Proposition 6.3 (p. 55) tries to patch this by assuming an exogenous harm $l > 0$ per period until a rogue algorithm is attributed, but inside the model of Section 2, all cohorts with $q_i > 0$ contribute additively to the merged measure $M$.
   - **Exact fix:** Add a concise 10-line Corollary or Remark after Proposition 6.3 (p. 56) giving a concrete *within-model* targeted intervention decision: suppose Cohort 1 is a manipulative or buggy momentum algorithm ($q_1 > 0$) and Cohort 2 is a stabilizing or hedging cohort (or has a smaller $q_2/L_2$ social cost of halting), and halting Cohort $i$ removes $q_i y_{i,t}$ from Equation (1) while incurring deadweight liquidity-withdrawal cost $c_i$. Show in 3 lines of algebra that the post-halt stability margin $1 - a - \kappa \sum_{j\neq i} q_j$ depends on the individual $q_i = w_i / \eta_i$, which requires separating $(w_i, \eta_i)$ rather than knowing the merged response.

3. **Section 2.2 & Section 6.2 (Page 21–22 & Page 52–54) — The "Reset Probing Observer" vs. Economic Reality.**
   - **Quote:** `"Independent resets are a benchmark experiment that no outside participant can run in a live market... Regulators do not, in practice, trade to learn; the probing option describes an outside participant, or prices the information a supervisor would otherwise have to buy by trading."` (p. 22, Section 2.2).
   - **Status:** VERIFIED.
   - **Why it matters:** While the caveat on p. 22 and p. 53 is honest, Section 6.2 and Table 14 (p. 53) still spend three full pages multiplying a hypothetical weekly probing loss by 52 ($52 \times L_{rt}^*$) and dividing the SEC's $147M CAT budget by that number to compute "break-even market counts" (e.g., 10.0 or 0.41 markets). To a finance referee, comparing an SEC audit trail's IT budget against the hypothetical round-trip execution loss of an imaginary trader who resets the market 52 times a year is comparing apples to Tuesdays. Worse, a private trading desk (the only agent that *can* trade) has no incentive to pay $356M/year just to learn whether there are two vs. three momentum cohorts if their combined price impact $H(z)$ is already known (Remark 5.3)!
   - **Exact fix:** Reframe Section 6.2 and Table 14 strictly as an **information-pricing dual (shadow price of attribution)** rather than a regulatory budget break-even analysis, or move Table 14 to Appendix D and keep only Proposition 6.3 (passive waiting delay vs. audit-trail cost, which *is* a realistic regulatory trade-off) in Section 6.2.

4. **Section 1.1 (Page 8–14) — Missing Core Finance Literature on Learning, Experimentation, and Heterogeneous Priors/Horizons.**
   - **Quote:** Section 1.1 Related Literature (pp. 8–14).
   - **Status:** VERIFIED.
   - **Why it matters:** A finance referee will immediately look for the canonical finance papers on multi-frequency/multi-horizon traders, price experimentation, and learning from prices:
     1. **Multi-horizon / heterogeneous-frequency trading:** Cespa and Vives (2012, *RFS*; 2015, *JF*) on persistence, liquidity, and short-termism; Crouzet, Dew-Becker, and Nathanson (2020, *JF*) on multi-frequency trading and spectral returns (which directly models traders operating at different frequencies/memories!).
     2. **Learning and experimentation in markets:** Collin-Dufresne, Johannes, and Lochstoer (2016, *Econometrica*) on parameter learning in asset pricing; Sockin and Xiong (2015, *JF*) on informational frictions; Biais, Foucault, and Moinas (2015, *JFE*) on fast vs. slow algorithmic trading equilibria.
     3. **Extrapolative expectations in finance:** Barberis, Greenwood, Jin, and Shleifer (2015, 2018, *JFE*) — your Equation (2) $y_{i,t} = (1-\eta_i)y_{i,t-1} + \eta_i x_t$ is literally the Barberis et al. exponential extrapolative belief specification! Failing to cite Barberis et al. (2015, 2018) when your entire model is heterogeneous exponential extrapolators is a glaring omission in finance.
   - **Exact fix:** Add citations to Barberis, Greenwood, Jin, and Shleifer (2015, 2018) in Section 2 (motivating Equation 2) and Crouzet, Dew-Becker, and Nathanson (2020), Cespa and Vives (2015), and Biais, Foucault, and Moinas (2015) in Section 1.1.

---

## D. Tasks 1–6 Required by the Prompt

### Task 1: The Economic Question in Plain Words
- **What the question is:** Can a market observer (a regulator, exchange, or trading desk) tell apart distinct groups of trend-following/extrapolative traders who react to past prices over different horizons using only public prices and aggregate order flow, or does doing so require account/class-tagged reporting?
- **Is "learning the memories of hidden trader groups" an economic object or an engineering one?** As currently written, it is primarily an **engineering system-identification object** (recovering the poles of a feedback controller $G(z)$ from the closed-loop transfer function $H(z)$). It becomes an *economic* object only when those memories map to deep structural primitives—such as traders' private signal-to-noise ratios (Proposition 4.6), extrapolative sentiment horizons (Barberis et al. 2018), or targeted regulatory circuit-breakers (Proposition 6.3).

### Task 2: Model Assumptions Audit (What Drives the Results & What Changes if Relaxed)
1. **Fixed linear price impact ($\kappa > 0$) and no dealer equilibrium:**
   - *Drives results?* Yes. Linearity and time-invariance of $\kappa$ allow exact deconvolution of $G(z)$ from $H(z)$ and give the quadratic Toeplitz cost $\frac{1}{2}v^\top T_h v$.
   - *If relaxed:* In a Kyle (1985) or Glosten-Milgrom (1985) equilibrium, $\kappa$ is endogenous to the composition of informed vs. noise traders and changes when an active prober enters the market! If the dealer updates $\kappa_t$ in response to unexpected probe flow $v_t$, probing becomes *more* expensive (as Corollary D.5 partially notes for convex impact), and changing cohort composition changes $\kappa$ itself, providing an additional (equilibrium) channel through which cohort parameters affect prices.
2. **Known fundamental value ($p^*$ known, so $x_t = p_t - p^*$ observed):**
   - *Drives results?* It simplifies the transfer function so that innovations and probes act on a stationary pricing error $x_t$.
   - *If relaxed:* If $p^*_t$ is an unobserved random walk, the observer only sees $\Delta p_t = \Delta p^*_t + \Delta x_t$. The fundamental innovation $\Delta p^*_t$ acts as an additional unobservable state shock, which strictly reduces Fisher information and makes the lower bounds hold *a fortiori*.
3. **Exogenous exponential-memory traders ($y_{i,t} = (1-\eta_i)y_{i,t-1} + \eta_i x_t$):**
   - *Drives results?* Crucial for the exact $(\Delta\eta)^{-(4K-2)}$ polynomial rate (which relies on the Vandermonde/moment structure of exponential sums).
   - *If relaxed:* As Theorem 5.7 shows, relaxing to general completely monotone memory makes the rate vastly worse ($\Theta(1/\log N)$). If traders optimize strategically against the prober, identification becomes a dynamic signaling/screening game.
4. **Reset-experiment observer ($y_{i,0} = 0, x_0 = 0$):**
   - *Drives results?* Essential for the clean upper bounds (Theorem 5.5) and single-experiment Gaussian likelihoods.
   - *If relaxed:* On a continuous stationary tape without resets, the observer is in the passive regime of Theorem 5.9 (or active probing on top of stationary state overhang), which requires horizon $T = \Omega((\Delta\eta)^{-(4K-2)})$.

### Task 3: Judgment of the "Observer" Framing (Wait, Probe, Disclose)
- The three-way taxonomy (Wait = passive time cost; Probe = active execution loss; Disclose = reporting infrastructure cost) in Section 2.2 (p. 21) is pedagogically clear.
- **Does the paper say clearly enough that regulators do not trade to learn?** Yes—on p. 3, p. 22, p. 53, and p. 55, the authors explicitly state `"regulators do not trade to learn"` and `"a supervisor without an audit trail does not run trading probes"`.
- **Is a probing outsider a sensible benchmark?** Only as a **Revealed-Preference / Shadow-Cost upper bound** or for a private quantitative trading desk trying to reverse-engineer competitors' algorithms. It should be presented as the *dual shadow price of market opacity*, not as a literal regulatory alternative to CAT.

### Task 4: Does Knowing the Hidden Groups Change a Decision?
- As checked in Major Issue 2, the paper currently admits on p. 4, p. 67, and p. 112 (Appendix I) that it does *not* model a decision requiring individual cohort identification. In fact, Remark 5.3 and Appendix I (`paper1_finite_horizon_supplement.pdf`) prove the opposite: for cumulative price risk and finite-horizon inventory warehousing, only the aggregate gain $G = \sum h_t$ matters, and cohort identification is unnecessary!
- **Minimal fix:** Write down the 5-line targeted-halt / margin-surcharge corollary outlined in Major Issue 2 above, where a supervisor can selectively throttle or margin-surcharge Cohort 1 without halting Cohort 2.

### Task 5: Missing Finance Literature
See Major Issue 4: Barberis, Greenwood, Jin, and Shleifer (2015, 2018, *JFE*); Crouzet, Dew-Becker, and Nathanson (2020, *JF*); Cespa and Vives (2012, *RFS*; 2015, *JF*); Biais, Foucault, and Moinas (2015, *JFE*); Collin-Dufresne, Johannes, and Lochstoer (2016, *Econometrica*).

### Task 6: Editor's Desk-Reject Paragraph vs. Send-to-Referees Paragraph
- **Desk-Reject Paragraph:**
  > *"While your paper executes a rigorous statistical analysis of mixture and transfer-function identification in a linear feedback loop, its contribution lies in applied probability and system identification rather than financial economics. In your model, price impact and mean reversion are exogenous constants, the fundamental value is known to the observer, and traders follow mechanical exponential moving-average rules without equilibrium microfoundations. Most importantly, as you note in Remark 5.3 and Section 8, aggregate price risk depends only on the summed impulse response—which public prices identify easily—and the paper does not model an economic or regulatory decision problem in which separating individual trader memories changes welfare or optimal policy. Consequently, the paper is better suited for a journal in mathematical statistics, information theory, or operations research."*
- **Send-to-Referees Paragraph (if revised as suggested):**
  > *"This paper offers a sharp, novel partial-identification and information-theoretic perspective on market transparency and audit trails (such as CAT and CFTC large-trader reports). By modeling heterogeneous extrapolative traders in a closed-loop market, the authors prove that public prices identify only the merged distribution of trader adaptation speeds and that separating nearby trader groups from prices alone faces a severe polynomial sample-complexity and trading-loss barrier ($\Theta((\Delta\eta)^{-(4K-2)})$) that class-tagged order flow completely eliminates. Because the paper connects this statistical barrier to trader signal-to-noise ratios, targeted supervisory interventions, and empirical CFTC and crypto positioning data, it merits full evaluation by expert referees in market microstructure and financial econometrics."*

---

## E. Cut Plan to Reach Target Page Count
1. **Cut Appendix H (Empirical feedback and its measurement, pp. 106–112, 6.5 pages):** To a microstructure economist, showing that an ad-hoc EMA filter $p_b - m_b$ has mechanical AR(1) persistence $1-\alpha = 29/31$ (Section H.1) is trivial algebra and distracts from the main identification story. Save it for the companion paper.
2. **Condense Section 6.2 & Table 14 (Disclosure in dollars, pp. 52–54) by 1.5 pages:** Move the detailed multi-vintage CAT budget comparisons to a short table note and focus Section 6.2 on Proposition 6.3 (the supervisory delay trade-off).
3. **Cut Appendix C.4 (Probing protocols Table 19, pp. 88–89, 1.5 pages):** Redundant with Appendix D.

---

## F. Three Questions I Would Email the Authors
1. In Lemma 2.1, a Kalman filter desk estimates a random-walk fundamental/trend $v_t$, whereas in Equations (1)–(2) the cohorts update on the pricing error $x_t = p_t - p^*$ relative to a constant fundamental $p^*$. How do you reconcile rational Kalman filtering with traders who systematically buy when the asset is overpriced ($x_t > 0$) and lose $\frac{1}{2}v^\top T_h v$?
2. Since Remark 5.3 and Appendix I show that aggregate price risk and inventory warehousing depend only on the summed response $\sum h_t$, can you write down a single explicit supervisory loss function in Section 6 where the optimal regulatory action depends on $(q_1, \eta_1)$ and $(q_2, \eta_2)$ separately rather than on $H(z)$?
3. If the dealer's price impact $\kappa$ is set in a Kyle (1985) equilibrium rather than fixed exogenously, wouldn't a large active probe $v_t$ cause the dealer to update its belief about informed trading and widen $\kappa_t$, making active probing even costlier than Theorem D.2 predicts?

---

## G. Would I Forward This to a Colleague?
- **Answer:** **No** (not to a pure finance theory colleague in its current framing, though I would mention the CFTC/CAT angle to a market-structure policy colleague).
- **The one change that would change my answer:** Add an explicit microfounded supervisory decision problem (where optimal targeted intervention or margining requires knowing the individual cohort parameters $(q_i, \eta_i)$ rather than the merged transfer function $H(z)$) and tie Equation (2) to the finance literature on extrapolative beliefs (Barberis et al. 2015, 2018) and multi-frequency trading (Crouzet et al. 2020).
