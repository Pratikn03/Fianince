# Changes from the earlier versions (for a cover letter or response to editors; NOT for the paper)

## Paper 1
\subsection*{Changes from the earlier version}
\begin{itemize}[itemsep=1pt]
\item The observation-noise calibration of 4 USDT is replaced by a measured Roll estimate (median 0.40 USDT); the headline Bitcoin capital falls from 9.83 million to about 99,000 USDT at $\delta=0.05$.
\item A real-data 2SLS feedback estimate with funding-settlement instruments is removed: the exclusion restriction was not established.
\item The claimed ``1.98$\times$'' two-sided minimax sandwich is removed; the order is now established for every $K$ by Theorems~\ref{thm:kcohort} and~\ref{prop:esprit}.
\item A Nasdaq Nordic benchmark and the FI-2010 dataset are removed; their licensing and construction could not be documented to the standard of the rest of the paper.
\item The statement that all results are formally verified in Lean is removed; formal verification is not part of this paper's claims.
\item Every real-data table of the earlier version except the recorder series is re-run from raw public files (Part 8 of the replication package) and reproduces to the third significant digit; the single fee event is replaced by two events with a strong first stage.
\item New results: Theorems~\ref{prop:esprit}, \ref{thm:general} and~\ref{thm:discvalue}; the real-data disclosure test of Section~\ref{sec:disc_data}; Theorems~\ref{thm:kcohort} and~\ref{thm:minphase}, Propositions~\ref{prop:passive}, \ref{prop:tagged} and~\ref{prop:esprit}, Theorem~\ref{thm:blind}, the placebo test of Table~\ref{tab:feedback}, and the estimator comparison of Table~\ref{tab:iv}.
\end{itemize}

## Paper 2
\subsection*{Changes from the earlier version}
\begin{itemize}[itemsep=1pt]
\item The earlier version reported transient amplification of 14--40$\times$ in real crash bursts. Those figures used state norms that depend on units (Proposition~\ref{prop:invariance}); the unit-free statistic is $\approx1.0000$ (Table~\ref{tab:spotnull}). The 40.79 value is retained only as the gain of a constructed operator (Appendix~\ref{sec:sims}).
\item Predictive gains for crash drawdowns (+1.21\% $R^2$) in the earlier version were not pre-registered and used the unit-dependent statistic; they are removed. The pre-registered tests fail in BTCUSDT spot and futures, pass three times in thin Binance books, and fail on Bybit.
\item The reported 87.3\% compression of ambiguity surcharges and 89.9\% welfare gain came from simulated accounts; they are removed. Proposition~\ref{prop:ambig} is kept as a mechanism.
\item Liquidation-prevention results on raw historical replays used guard inputs computed from the unit-dependent norm; they are removed pending a re-run with the unit-free statistic.
\item Results on Nasdaq Nordic equities and the FI-2010 dataset are removed; their licensing and construction could not be documented to the standard of the rest of the paper.
\item The statement that all results are formally verified in Lean is removed.
\item New results: Theorem~\ref{thm:t6} and Propositions~\ref{prop:shape}--\ref{prop:t6m}; Theorems~\ref{thm:guard} and~\ref{thm:robust}; Proposition~\ref{prop:bridge}; the depth evidence of Section~\ref{sec:depth}; the unit-free spot evidence of Section~\ref{sec:spot}; Theorems~\ref{thm:nomom} and~\ref{thm:noover}, Proposition~\ref{prop:sum} and the equilibrium of Section~\ref{sec:equil}; and the thin-book program of Section~\ref{sec:thin}.
\item The earlier statement that the three-state book amplifies if and only if $C_3>0$ (supported by 1{,}136 random draws) is false; Remark~\ref{rem:counter} gives counterexamples.
\end{itemize}
## October 19, 2026 revision (both papers)

### Paper 1
- The general-memory result is now unconditional and two-sided: Lemma (moment-matched cohort pairs) proves the Wasserstein separation that was previously assumed, and Theorem (minimax rate for general memory) gives matching lower and upper bounds of order 1/log N (moment estimator solved as a linear program). Constants differ by a factor that grows as rho -> 1; stated in the paper.
- New pre-registered test (Part 11, SHA-256 6f1d6f35...): CFTC Commitments of Traders, 8 regulated futures markets. H1 (class reports pin down memory; primary) 8/8 pass; H3 (fast class has shorter memory) 6/8 pass; H2 (fast class trend-follows) 4/8 fail. New subsection and Table (tab:cot).
- References added: Bernstein (1914), Varga and Carpenter (1985), Rivlin (1981), Fan (1991), Pagano and Roell (1996), Boehmer, Saar and Yu (2005), Bessembinder, Maxwell and Venkataraman (2006), Moskowitz, Ooi and Pedersen (2012), Makarov and Schoar (2020).

### Paper 2
- New subsection "Threats to validity": multiple testing (all four passing primaries survive Bonferroni across the eight primaries), dependence among the passes, look-ahead and estimated regressors, selection and survivorship, economic size, venue.
- New related-literature paragraph on early-warning metrics (VPIN and its critique) and liquidity-crash models; 18 standard references added (now 42), including the HAR, RiskMetrics, Kyle, Amihud, Newey-West and block-bootstrap sources for methods already used, and the pre-registration / multiple-testing literature.
- Pending: Part 10 (Bybit with order-book depth, pre-registered), Part 12 (certified guard backtest, economic size in bps, Oct 10 2025 event study).
- Part 12 (SHA-256 b9a56af4...): certified-guard backtest PASSES narrowly (amplification-adjusted volatility limit with a three-day certified gain multiple: log TLR -0.024 [-0.051, -0.0004] vs volatility limit); all secondaries fail (certified guard alone +0.339; combined +0.009; certified vs six-hour guard -0.020 [-0.165, 0.118]). New subsection and Table tab:certguard.
- Economic size (descriptive, Part 9 test set): within volatility quintiles, top vs bottom C3 quintile next-hour MAE +25.6 bp [18.6, 32.8] (mean 112.5 bp); tail share 2.3% -> 5.1%. Added to Threats to validity, abstract and introduction.
- October 10, 2025 descriptive event study with figure (fig_oct10): S60 elevated all day and above its previous-week 90th percentile for 16 of 18 thin symbols at the crash hour, but volatility was also at the top of its range; no cross-sectional ranking (Spearman -0.11). Labelled descriptive.
- Part 10 (SHA-256 ec2145fa...): Bybit with order-book depth, 6 coins included by the pre-registered rule. Primary criterion met (dR2 +0.033 pts [0.019, 0.053], Clark-West t 5.73) but the effect is about 1/80 of Binance's, with no AUC gain; only the momentum term helps. New paragraph and Table tab:bybitob; abstract, introduction, map, threats, conclusion and data statement updated. Ledger now 10 pre-registered tests, 6 pass, 4 fail.

## October 20, 2026 (review response round)
- References: Liu and Ammari now cited as arXiv:2212.00536 (journal details could not be verified); October 10, 2025 liquidation figure now cited to the 21Shares research note (Oct 13, 2025). All Part 7 numbers verified against W6_bybit_test.json (p7_results.zip received).
- Unreproduced numbers: every "not re-run" item was re-run or removed. Re-run: cohort-split invariance, symmetric multi-asset network (rho 0.822 -> 0.973, Kreiss 1), Prop. lucas monotonicity check (3,000 draws), ML-at-CRB columns and the four-estimator check (re-implemented, recompute_p1_estimators.py). Removed (data or code not available): DQN-checkpoint figures, ERA 7% figure, L2 book-walking and GARCH multipliers, recorder-series appendix, dealer grid, Paper 2 constructed-regime/book-walking/venue appendices.
- Paper 1: precision comparison reframed (partly mechanical; identified-subset ratios 27.6-62.5); positions-vs-flow bridge stated as an assumption; Table 5 L=320/480 filled (<=64.48 by zero padding); Theorem capital framed as coercivity lemma; rho->1 gap explained; AI statement drafted.
- Paper 2: Section 4 reframed around peak overshoot vs cumulative amplification; simultaneity paragraph; inverse sizing vs one-sided throttle explained; AI statement drafted.
- Replication README written; "Part N" explained in both appendices.
- Journal versions: Paper1_QE (150-word abstract, 1.25in margins, 6-page supplement) and Paper2_JF (100-word abstract, 1.5 spacing, 58-page main text + internet appendix).
- Part 13 (post-hoc robustness) notebook delivered; results pending.
- Part 13 (post hoc) results integrated: R5 fixed-grid depletion REVERSES the replenishment finding (fixed band eps30 +0.0021 [0.0013, 0.0032], 19/20 coin-days > 0; re-centred band -0.0004) -> all "flow replenishes" claims rewritten; new subsection and Table tab:fixedgrid. R1 throttle: cap on static limit -13% tail loss [-27%, -3%], on vol limit +0.8% [-1.3, 2.7]. R2: physical S rises with thinness (Spearman with log depth -0.94) but gain multiple flat (~47) -> equilibrium channel is impact, not reversion. R3: Bybit bounce hypothesis rejected (less negative ac1), sparse trading (11% no-trade minutes) supported. R4: lagged-flow instrument weak (first-stage corr 0.005) -> uninformative; stated. R6: basis-trade signature consistent but not decisive. R7: Cochrane-Orcutt changes Q negligibly (rho ~ 0). R8 (VPIN) not in the received zip.
- Paper 1: Passive cost promoted from numerical proposition to theorem with proof; explicit known-vs-new paragraph vs super-resolution literature.

## October 20, 2026 (harsh-review fixes)
- Paper 2: guard positioned against l1-optimal control. The worst-case identity in Theorem guard is stated to be the classical l1 (peak-to-peak) gain (Vidyasagar 1986; Dahleh and Pearson 1987; Dahleh and Diaz-Bobillo 1995); the paper now says what is new: admission rule over an action set that changes the operator, balance-sheet embedding, cohort-split invariance and identification from prices, comparison with supervisory peak/eigenvalue rules, and the equilibrium rebate in S. Remark after the theorem; related-literature paragraph and contribution paragraph updated.
- Paper 2: resiliency literature added (Biais, Hillion and Spatt 1995; Degryse et al. 2005; Large 2007; Foucault, Kadan and Kandel 2005), with the link from resiliency to the reversion term m and to S.
- Paper 2: new "Sequential design" paragraph in Threats to validity stating that the choice of each next test adapted to earlier results, and what pre-registration does and does not protect.
- Paper 2: new "In margin terms" paragraph. Lognormal fit to E1 quintile means and medians (validated: reproduces observed tail shares by quintile within 0.6 pp). The 25.6 bp within-volatility effect roughly doubles the hourly liquidation probability of a 20x position (1.3% -> 2.7%; 2.3%-3.2% across the CI) and almost triples it at 10x (0.04% -> 0.11%); about $710 extra expected margin loss per hour per $1M notional at 20x ($490-$960). Script recompute_dollar.py -> R_P2_dollar_translation.json. Labelled illustrative, post hoc. One clause added to the introduction.
- Paper 2: table note of tab:calib fixed (stray text). JF version: calibrated illustration moved to the Internet Appendix with a pointer paragraph; main text remains 60 pages.
- Paper 1: new paragraph "When audit trails already exist" (SEC Rule 613 / CAT, Release 34-67457; 2025 PII exemption, Release 34-102386): prices the value of account linkage, explains that audit trails record accounts not decision rules, and that CAT does not reach crypto or CFTC markets. Intro cites Rule 613.
- Paper 1: new assumptions paragraph "Algorithms that react to being probed" (shared vs cohort-specific reactions; passive route at the same order; detection is itself a testing problem; adversarial design left as future work).

## October 20, 2026 (proof audit and Part 14)
### Proof audit (both papers; recompute_audit.py -> R_audit_oct2026.json)
Every theorem, proposition and lemma was re-read against its proof; closed forms were re-derived symbolically and inequalities checked numerically. Corrections:
- Paper 2, Prop. shape: the claim that the peak occurs at the integer nearest to k* is FALSE (fails in 15% of 150,039 amplifying draws). Corrected to: the peak lag is floor(k*) or ceil(k*), and 1 when k*<1 (holds in all draws; proof added: unique critical point, unimodality). The earlier "verified in 565 draws" sentence is removed.
- Paper 2, Thm. forward solvency: "necessary for adversarially signed disturbances" was an overclaim. Now: necessary when z_t = 0; with z_t != 0 the drift bound may not be attained, so the condition is sufficient (possibly conservative). The M_C(0)=1 assumption at alpha=0 is stated.
- Paper 2, Prop. dominance: the trailing ">= M_C(0)=1" was a feasibility assumption written as part of an iff; restated as an explicit assumption.
- Paper 2, Prop. invariance: index of the past-input sum corrected (g_{k-1+j}).
- Paper 2, Remark: second counterexample peaks at 9.2 kappa with the printed (rounded) parameters (was 9.28).
- Paper 2, Thm. nomom proof: m11 <= rho (was strict).
- Paper 1: resolvent identity had a spurious kappa^{-1} (H1 - H0 = H1 H0 (G1 - G0)); fixed in three places. The constants K* were already computed with the correct identity (numerically, ||d||_1 <= 0.12 K* delta^2 in 1,610 draws).
- Paper 1, Thm. twocohort (iii): Hankel determinant now includes the factor r1 r2.
- Paper 1, Thm. rh: Q_i = T_{h_i}/2 and A_diff defined; table note normalization made consistent.
- Paper 1, Thm. minphase: merged measure identified with kappa and a known (rates identified regardless).
- Paper 1: truncated sentence in Section 4 completed.
Verified without change: all other results, including the summed-response closed form and determinant (symbolic), the amplification theorem, the guard, tail lemma, robust gain, equilibrium (numbers reproduced), Kalman/OGD reductions, merged equivalence, the d_2 identity, capital theorems, spectral dissipation and adaptive bounds, the Lemma (moment-matched pairs) and the general-memory minimax argument, the passive-cost theorem, and the spectral-blindness example (numbers reproduced).
### Part 14 (US equities, SHA-256 f5800a69..., opened once): PASS
- 23 thin US stocks (of 40 drawn; validity rule), SIP trades via Alpaca, depth-free C3_flow beyond the full volatility + impact baseline: dR2 +0.499 pts [0.272, 0.779], Clark-West t 5.05. S60 +0.153 [0.046, 0.272]; reversion term +0.613; momentum term nil. Mid-size controls ALSO show a gain (+0.316 [0.074, 0.634]) against the prediction. Limitations stated: universe rule did not exclude funds (CRF, BNDX); 17 thinnest names dropped by validity rule; survivorship; tick-rule signing.
- New subsection and Table tab:us; abstract (both versions), introduction, map, what-we-do-not-claim, ledger (11 tests, 7 pass, 4 fail), threats (multiple testing over 11, sequential design, dependence, venue), summary, conclusion, data statement and forest figure (now includes Parts 7, 10 and 14) updated.
- JF version: price-impact check and Bybit order-book detail moved to the Internet Appendix with pointer paragraphs; main text 60 pages.
