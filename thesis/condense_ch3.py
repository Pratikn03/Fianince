"""Assemble the condensed Chapter 3 from the full chapter (ch3_paper2_full.tex) plus new connecting text.

Theorem, proof and table blocks are copied verbatim by line range; every other paragraph is new, shorter text.
Called by make_chapters.py after it writes ch3_paper2_full.tex; also runnable: python3 condense_ch3.py
Every copied block is checked against the first characters of its expected first line, so a change in Paper 2 that
moves its lines stops the build instead of copying the wrong text.
"""
import re
import sys
from pathlib import Path

ANCHOR = {105: 'Time is discrete', 116: '\\begin{proposition}[Stability with one cohort]', 128: 'Chapter~\\ref{ch:p1} shows that prices identify', 140: '\\begin{proposition}[Summed response with carried', 175: '\\begin{theorem}[Safe radius', 242: 'Let $x_t$ be the price displacement', 258: 'Add momentum traders', 309: '\\begin{theorem}[Summed response in closed form]', 327: 'We work in the positive cohort economy', 341: '\\begin{example}[An exact ambiguity witness]', 361: 'Lags $1$ to $n$', 384: '\\begin{theorem}[Certification cost', 441: 'A dealer with inventory', 479: '\\begin{theorem}[Robust gain]', 493: 'The guard of Lemma', 602: '\\begin{proposition}[Hidden-state drift', 648: '\\begin{theorem}[Decision value of disclosure]', 689: '\\subsection{Setup}', 1308: '\\begin{table}[!htbp]', 1380: '\\begin{table}[!tbp]', 1769: '\\begin{thebibliography}', 1838: '\\paragraph{Proposition~\\ref{p2:prop:jury}.}', 1840: '\\paragraph{Proposition~\\ref{p2:prop:invariance}.}', 1842: '\\paragraph{Proposition~\\ref{p2:prop:inventory_S}.}', 1849: '\\paragraph{Theorem~\\ref{p2:thm:radius}.}', 1855: '\\paragraph{Proposition~\\ref{p2:prop:driftguard}.}', 1863: '\\paragraph{Theorem~\\ref{p2:thm:window}.}', 1865: '\\paragraph{Theorem~\\ref{p2:thm:certcost}.}', 1867: '\\paragraph{Lemma~\\ref{p2:lem:sound}.}', 1869: '\\paragraph{Theorem~\\ref{p2:thm:robustguard}.}', 1871: '\\paragraph{Theorem~\\ref{p2:thm:disclosure}.}'}
END = {112: '\\end{equation}', 122: '\\end{proposition}', 188: '\\end{theorem}', 254: '\\end{definition}', 1345: '\\end{table}', 1834: '\\end{thebibliography}'}
FULL = []


def L(a, b):
    """Lines a..b of the full chapter, 1-based inclusive, checked against their anchors."""
    assert FULL[a - 1].startswith(ANCHOR[a]), f"Paper 2 moved: line {a} no longer starts with {ANCHOR[a]!r}"
    if a == b and FULL[a - 1].startswith("\\paragraph{"):
        stop = a
        while stop < len(FULL) and not FULL[stop].startswith(("\\paragraph{", "\\section{")):
            stop += 1
        return "\n".join(FULL[a - 1:stop]).rstrip()
    if b in END:
        assert FULL[b - 1].startswith(END[b]), f"Paper 2 moved: line {b} no longer is {END[b]!r}"
    return "\n".join(FULL[a - 1:b])


def main(here="."):
    global FULL
    T = Path(here)
    FULL = open(T / "ch3_paper2_full.tex", newline="").read().split("\n")
    _build(T)


def _build(T):

    parts = []
    add = parts.append

    add(r"""\chapter{Safety without identification: transient amplification and a maximal pre-trade guard}\label{ch:p2}

    This chapter, the second paper of the thesis, condenses the paper \emph{From Human Markets to Machine Markets: Transient Amplification, an Exact Depth Condition, and a Maximal Pre-Trade Guard}, joint with Suboh Alkhushayni, Yuhao Chen, Mansi Bhavsar and Prashant Niroula. It keeps the theorems the rest of the thesis uses, with their proofs, and the empirical program in summary, with every registered test and its outcome in Table~\ref{p2:tab:alltests}. The full version, with every table, robustness check and the source of every number, is in the replication package (\texttt{thesis/ch3\_paper2\_full.tex}).

    \begin{quote}\small\textbf{Summary.} Eigenvalues and volatility do not bound the losses a market produces before it settles. In a limit order book with adaptive traders, cumulative transient risk is $S=\tilde\kappa/(m-q\tilde\kappa)$, long-run impact over reversion net of momentum; a book overshoots its direct impact if and only if $\varphi\varepsilon>(1-a)\kappa$; and a pre-trade guard on the summed impulse response is the largest safe admission rule and does not depend on how the traders split into cohorts. The summed response is certified with $\Theta(\sigma^2\epsilon^{-2}\log(1/\epsilon))$ experiments whatever the cohort spacing, while identifying the cohorts costs polynomially more, and the certified guard is minimax-optimal in lost capacity up to a logarithm. Of 25 registered empirical tests, 15 pass: six-hour estimates of the statistic forecast the size of the next hour's adverse excursion in thin Binance perpetuals beyond a full volatility baseline and VPIN, more weakly in thin US stocks, and not on Coinbase or in the deepest book; tests of a liquidation mechanism fail.\end{quote}

    \section{Introduction}

    On October 10, 2025, crypto derivatives markets liquidated an estimated \$19 billion of leveraged positions in a single day \citep{p2:shares2025}; on May 6, 2010, US equity prices fell and recovered by several percent within minutes \citep{p2:kirilenko2017}. In both episodes the losses that mattered were transient: positions were closed out on the path, before prices settled. Algorithmic markets are closed-loop systems, and a common shortcut equates their stability with eigenvalues inside the unit circle. For a leveraged intermediary that is the wrong object: a market can be spectrally stable and still push a dealer through its maintenance margin within seconds.

    The chapter asks three questions. When does a limit order book amplify a flow shock? How can a dealer or a venue control transient loss without identifying who is trading, which Chapter~\ref{ch:p1} shows is expensive from public data? And what information certifies a safe trading decision, at what cost? The answers, in a linear book model, are these.

    \paragraph{Spectral stability does not bound transient loss.} The safe shock radius of a stable market is the loss budget over its peak transient gain, and that gain can be arbitrarily large at any fixed spectral radius (Theorem~\ref{p2:thm:radius}).

    \paragraph{When a book amplifies.} A book with depletion and refill overshoots its direct impact if and only if $\varphi\varepsilon>(1-a)\kappa$; momentum alone cannot make a stable book overshoot; and cumulative risk has the closed form $S=\tilde\kappa/(m-q\tilde\kappa)$, which needs no depletion (Theorems~\ref{p2:thm:peak} and~\ref{p2:thm:sum}).

    \paragraph{The maximal guard.} Under a declared risk contract, worst-case loss is inventory times the shock bound times the summed absolute impulse response, so a guard on that sum admits exactly the safe actions (Lemma~\ref{p2:thm:guard}); a guard on the peak response admits unsafe ones. The guard survives estimation error (Theorem~\ref{p2:thm:robust}) and needs no identification of the traders (Proposition~\ref{p2:prop:invariance}).

    \paragraph{Certifying is cheaper than identifying.} Two markets can agree on their early responses and differ threefold in risk (Example~\ref{p2:ex:witness}). A finite window certifies the summed response under a memory bound and certifies nothing without one (Theorem~\ref{p2:thm:window}); with noisy experiments the cost of certification is $\Theta(\sigma^2\epsilon^{-2}\log(1/\epsilon))$ whatever the cohort structure, against $(\Delta\eta)^{-(4K-2)}$ for identification (Theorem~\ref{p2:thm:certcost}). The guard built on the certificate has a closed form and is minimax-optimal (Theorem~\ref{p2:thm:robustguard}); disclosure is worth most when memory is long, and a noisy proxy can be worth less than nothing (Theorem~\ref{p2:thm:disclosure}).

    \paragraph{Who controls the risk.} Reversion is a public good: dealers under-provide it, momentum traders over-provide feedback, and the corrective rebate is a function of the guard's own statistic (Proposition~\ref{p2:prop:equil}).

    \paragraph{Evidence.} Twenty-five primaries were registered; twenty-four were tested and one was not opened under its fixed sequence; fifteen pass (Table~\ref{p2:tab:alltests}). The deepest book, BTCUSDT, sits on the stable side of the amplification condition and fails a registered forecasting test. In thin books the statistic forecasts the size of the next hour's adverse excursion in every registered forecasting test on Binance, on new symbols and on untouched days, by up to $2.8$ points of $R^2$ beyond a full volatility baseline; about a fifth as much in thin US stocks; negligibly on Bybit; not at all on Coinbase. We have not identified a deeper mechanism: the effect does not run through open-interest liquidations, and it is carried by slow reversion relative to impact, which is what the statistic measures. As a risk control the certified guard lowers tail loss against a static limit but not against a volatility cap at matched exposure.

    \paragraph{What we do not claim.} The information-safety theorems concern declared observation contracts (controlled reset experiments, exact windows, audited data), not finite-sample guarantees for observational order-book records. Cohorts are any traders whose demand is a linear filter of past prices; nothing attributes an effect to algorithms rather than people. The forecasting result is reduced-form, and its size depends on the venue.

    \paragraph{Related work.} Models of transient impact and resilience \citep{p2:obizhaeva2013,p2:bouchaud2004,p2:bouchaud2018} take the decay of impact as given; we derive when depletion, refill and momentum make a book overshoot and give cumulative impact in closed form. Liquidity spirals \citep{p2:brunnermeier2009,p2:shleifer1992} need funding constraints; our amplification does not, and our guard is the control that bounds it. \citet{p2:sornette2023} show that non-normal interactions create transient bubbles. The guard's worst-case identity is the $\ell_1$ gain of $\ell_1$-optimal control \citep{p2:vidyasagar1986,p2:dahleh1987,p2:dahleh1995}; what is new is its use as an admission rule, its invariance to the cohort coordinates and its identification from prices. The early-warning benchmark is VPIN \citep{p2:easley2012,p2:andersen2014}; forecast evaluation uses \citet{p2:clark2007} with the volatility baselines of \citet{p2:corsi2009} and \citet{p2:riskmetrics1996}, and we pre-register following \citet{p2:nosek2018} and \citet{p2:harvey2017}. Rule 15c3-5 requires pre-trade controls on credit and capital \citep{p2:sec2010}; the guard is a candidate with a provable maximality property.

    \section{The closed-loop market}\label{p2:sec:model}

    \subsection{Price formation}""")
    add(L(105, 112))
    add(r"""
    \subsection{Stability and what an observer can use}""")
    add(L(116, 122))
    add(L(128, 138))
    add(L(140, 155))
    add(r"""
    The model is linear: it describes the transient response to flow shocks of ordinary size, which is what a pre-trade control must bound, not regime changes such as exchange outages. Every input to the guard (impulse coefficients, an operator estimate and its confidence radius, inventory and margin) is observable to a dealer or a venue.

    \section{Spectral stability is not solvency}\label{p2:sec:radius}
    """)
    add(L(175, 188))
    add(r"""
    For $J_\theta=\begin{psmallmatrix}0.8&\theta\\0&0.4\end{psmallmatrix}$ the spectral radius is $0.8$ throughout, while the price-row gain rises from 1 to 120 as $\theta$ goes from 0 to 100 and the safe radius falls by the same factor. Chapter~\ref{ch:p1} shows more: markets that share their eigenvalues, one-step price variance and stationary price variance can differ arbitrarily in worst-case transient gain, so neither eigenvalue nor volatility monitors bound transient loss. In the cohort economy with nonnegative weights the price response is a nonnegative mixture of decaying exponentials and peaks at the direct impact (Chapter~\ref{ch:p1}, positive-geometry lemma): non-normality is not sufficient for scalar price overshoot, and necessity for Euclidean state-norm growth does not extend to arbitrary input-output responses. In this positive cohort model, momentum alone does not supply overshoot. Depth depletion does.

    \section{When does a book amplify? An exact condition}\label{p2:sec:t6}

    Transient path risk takes two forms. \emph{Peak overshoot} is a response that rises above its direct impact; \emph{cumulative amplification} is a summed response much larger than direct impact. The data support the second form, not the first.

    \subsection{A book with depletion and refill}""")
    add(L(242, 254))
    add(r"""
    \subsection{Peak overshoot}""")
    add(L(258, 290))
    add(r"""
    The converse of part~\ref{p2:prop:t6m} fails with two slow modes: near the stability boundary, or with slow refill and slow momentum, a book can have $C_3<0$ and still peak far above its impact, because the depth channel creates a negative residue on an intermediate mode. No condition on the one-period margin alone is exact.

    \subsection{Cumulative transient risk}""")
    add(L(309, 321))
    add(r"""
    \section{Identification and financial safety}\label{p2:sec:infosafety}

    Chapter~\ref{ch:p1} shows that identifying the cohorts from prices is expensive. A pre-trade control does not need them; it needs a bound on the risk they create. This section asks what information certifies a safe decision, what it costs, and how much safe trading is lost without it.

    \subsection{Observation and risk contracts}\label{p2:sec:contracts}""")
    add(L(327, 337))
    add(r"""
    \subsection{Two markets that look the same}""")
    add(L(341, 357))
    add(r"""
    \subsection{What a finite window certifies}""")
    add(L(361, 371))
    add(r"""
    Part (i) applies the Markov--Krein theorem \citep{p2:krein1977,p2:karlin1966}, part (ii) Chebyshev's best approximation of $1/(x_0-x)$ \citep{p2:achieser1956}; the proofs are in Appendix~\ref{p2:app:proofs}. In an eight-cohort economy with memory bound $0.95$ and true summed response $5.56$, lags $0$--$3$ certify nothing, lags $0$--$6$ give $[5.01,7.20]$ and lags $0$--$8$ give $[5.30,6.00]$; for fixed data the upper end grows without limit as the memory bound approaches one, as part (iii) says. The endpoints are proved, not only computed: polynomial bounds whose sign conditions are verified in interval arithmetic with outward rounding turn them into certified intervals \citep{p2:rump2010}.

    \subsection{What certification costs, and what identification costs}""")
    add(L(384, 413))
    add(r"""
    Two refinements are in the full version. If the noise in the taps of one experiment is correlated, the certificate of part (i) can under-cover (75\% at nominal 95\% in simulation), while a Student-$t$ certificate on the summed taps and a Hotelling region over the window keep their level \citep{p2:hotelling1931}; and experiments can be run one at a time with an anytime-valid version of the certificate that stops once the data decide.

    \section{An identification-free pre-trade guard}\label{p2:sec:guard}

    \subsection{Maximality}""")
    add(L(441, 453))
    add(r"""
    The identity is the classical $\ell_1$ gain of a convolution operator \citep{p2:vidyasagar1986,p2:dahleh1987,p2:dahleh1995}; we use it rather than claim it. The finance content is that the dealer's admission level changes the operator, so the guard is a rule over an action set; that its single input is invariant to how the traders split into cohorts and is identified from prices; and that the same statistic prices the corrective rebate in equilibrium (Proposition~\ref{p2:prop:equil}). The guard coincides with a brute-force adversary's maximal safe level in 200 of 200 random states, and the peak-gain guard admitted an unsafe level in 2{,}000 of 2{,}000. An infinite-horizon gain is computed on a finite horizon with a contraction-block tail bound.

    \subsection{Robustness to estimation error}""")
    add(L(479, 489))
    add(r"""
    \subsection{An uncertainty-aware guard}\label{p2:sec:robustguard}""")
    add(L(493, 510))
    add(r"""
    When admission also changes the book, deepening it and speeding reversion as well as adding feedback, risk can first rise and then fall with the admission level, and the safe levels need not form an interval: certifying the largest safe level then no longer certifies those below it. The full version certifies the whole safe set by interval branch and bound \citep{p2:hansen2004}, with soundness and completeness; in a book where admission raises feedback linearly and liquidity quadratically the certified safe set is $[0,0.053]\cup[0.178,1]$.

    \paragraph{Why the peak guard is unsafe in a real book.} At the median BTCUSDT estimates of Section~\ref{p2:sec:evidence}, price impact is persistent ($\hat a\approx0.97$ per minute), so the summed gain over 15 minutes is about 13 times the peak. A guard calibrated to the peak would admit inventory about 13 times larger than is safe against a sustained adversarial flow of the declared size, although that book does not amplify. Persistence alone makes peak-based limits unsafe.

    \paragraph{The guard on a dealer's balance sheet.} The full version carries the guard through maintenance margin, hedging and worst-case fills, and proves forward solvency at every step at which an admissible level exists; when none exists the guard halts new fills and flags the state, because existing inventory can still breach margin. In a matched-shock Monte Carlo inside the model, with every rule calibrated to the same trading capacity, the guard has no forced liquidations against 31.6\% with no control, 31.4\% under a trailing volatility limit and 20.3\% under an inventory cap. With a hidden cohort state the drift of future prices is not identification-invariant under a Euclidean bound, whereas the natural interval bound supports the following sufficient invariant box. Cumulative unforced drift still depends on the updating rates:
    """)
    add(L(602, 624))
    add(r"""
    Re-optimization by the traders does not undo the guard: when a venue throttles admission, filtering cohorts lower their adaptation rates, and in the positive cohort economy every finite-horizon summed response falls with them.

    \section{The value of disclosure for safe trading}\label{p2:sec:disclosure}

    Chapter~\ref{ch:p1} measures disclosure in samples needed to identify the cohorts. For a pre-trade control the relevant value is the safe trading capacity it unlocks.
    """)
    add(L(648, 684))
    add(r"""
    \section{Who provides reversion? An equilibrium}\label{p2:sec:equil}

    Theorem~\ref{p2:thm:sum} says that transient risk is governed by $S=\tilde\kappa/(m-q\tilde\kappa)$, and its ingredients are chosen by participants: dealers decide how hard to lean against displacements, which sets reversion $m$, and momentum traders how strongly to chase them, which sets $q$.
    """)
    add(L(689, 715))
    add(r"""
    Across the liquidity terciles of 30 Binance perpetuals the summed response per dollar of flow rises steeply as depth falls (Spearman correlation with log depth $-0.94$), as part (ii) predicts, but the unit-free multiple $S/|h_0|$ is the same in all three terciles (medians $46.4$, $47.3$ and $46.9$): thinner books carry more cumulative risk because their impact is larger, not because they revert more slowly. That is the pattern of part (v), which we added after seeing the comparison, so the match is a consistency check, not a test.

    \section{Evidence}\label{p2:sec:evidence}

    The empirical program tests the theory's content in order-book data. Every test fixed its specification, hashed it and committed it before its test data were opened, and every test set was opened once except where Table~\ref{p2:tab:alltests} says otherwise. Data are public: Binance USD-M futures and spot archives (one-minute klines with taker volume, depth within $\pm1$--$5\%$ of the mid at about 30-second intervals, open interest), verified against published checksums and screened by validation rules fixed in advance; Bybit trade and order-book archives; Coinbase trades; and consolidated US trades. The out-of-sample criterion is a one-sided Clark--West test \emph{and} a date-block bootstrap interval for the gain in $R^2$ that excludes zero.

    \subsection{The deepest book does not amplify}

    In BTCUSDT futures on 718 training days, the estimated one-period margin $\hat C_3$ is negative on 93.5\% of days and the median implied response peaks at impact. Local projections show no overshoot once future flow is held fixed. A registered test of whether six-hour estimates of $\hat C_3$ forecast the next hour's maximum adverse excursion beyond volatility, flow and depth controls fails ($+0.018$ points of $R^2$, interval including zero), and a volatility flag classifies tail hours far better. In spot data, a unit-free measure of transient amplification on five crash days is indistinguishable from one and from a no-feedback null, and a registered forecasting test fails. Binance's depth bands appear to show replenishment of the side being hit; on a fixed price grid built from Bybit's full order books the sign reverses, so the replenishment is an artefact of band re-centring and depletion is present, but it is not large enough to produce an overshoot. Where the theory predicts nothing, we find nothing.

    \subsection{Thin books: the summed response forecasts the size of excursions}\label{p2:sec:thin}

    Thirty Binance perpetuals were fixed from one 2024 training day before any statistic was computed, spanning BTCUSDT to symbols with under \$5M of daily volume. The amplifying regime is more frequent in thinner books (16.1\% of symbol-days with $\hat C_3>0$ in the thin tercile against 9.4\% in the thick one), although the average margin is negative everywhere. Measured feedback is larger in \emph{deeper} books: feedback and amplification are different objects.

    \begin{table}[t]\centering\small
    \begin{threeparttable}
    \caption{Registered forecasting tests in thin Binance books, 2025--2026}\label{p2:tab:thin}
    \setlength{\tabcolsep}{3pt}
    \begin{tabular}{p{0.42\textwidth}cc}
    \toprule
    Test (what changes) & $\Delta R^2$ (pts) [CI] & Clark--West $t$\\
    \midrule
    Ten thin symbols, volatility and flow controls & $+1.216$ [$+0.273$, $+7.987$] & 8.53\\
    Ten new thin symbols drawn by a seeded rule & $+0.845$ [$+0.303$, $+6.371$] & 11.66\\
    Fresh days, 20 thin symbols, price-impact controls in the baseline & $+1.583$ [$+0.588$, $+3.237$] & 9.46\\
    Fresh days, full volatility-forecasting baseline (HAR, EWMA, hour effects) & $+2.787$ [$+1.425$, $+4.944$] & 12.59\\
    \quad the guard's statistic $S_{60}$ instead of $\hat C_3$ (secondary) & $+2.098$ [$+1.165$, $+3.597$] & ---\\
    Untouched days, model frozen at its training estimates & $+4.196$ [$+1.551$, $+8.233$] & ---\\
    Untouched thin symbols & $+0.727$ [$+0.377$, $+1.428$] & ---\\
    Untouched thin symbols, beyond the baseline plus VPIN & $+0.562$ [$+0.274$, $+1.159$] & ---\\
    \bottomrule
    \end{tabular}
    \begin{tablenotes}\footnotesize\item Outcome: the next hour's maximum adverse excursion; candidate estimated from the previous six hours. Date-block bootstrap intervals (97.5\% for the fresh-day and untouched-day primaries, 95\% otherwise). Every row is a registered primary except the $S_{60}$ row. Full tables and secondaries in the full version.\end{tablenotes}
    \end{threeparttable}
    \end{table}

    The result holds in every registered forecasting test on thin Binance books (Table~\ref{p2:tab:thin}). It strengthens as the baseline gets harder: beyond a full volatility-forecasting baseline that already explains 18.6\% of the variance, $\hat C_3$ adds $2.8$ points of $R^2$, the volatility benchmarks themselves add nothing beyond the simpler controls, and the summed response $S$, the guard's own statistic, adds $2.1$ points. The decomposition matches the theory: a larger momentum term predicts larger excursions, a larger reversion term smaller ones, and the depth term nothing; most of the variation is in impact-weighted reversion, as $S=\tilde\kappa/(m-q\tilde\kappa)$ implies. It is not price impact (with four impact controls it keeps about 80\% of its gain, and impact alone forecasts nothing), not tick size (it survives tick controls, the removal of days at a non-training tick and of any single symbol; unit-free versions work on fresh days), not order-flow toxicity (it keeps about 73\% of its gain beyond VPIN, a comparison made post hoc and then confirmed in a registered test), and not order-flow persistence (a placebo with the same flow persistence but broken alignment with prices adds nothing). In economic terms, within a volatility quintile the top quintile of $\hat C_3$ has next-hour excursions about 26 basis points larger than the bottom quintile, enough to roughly double the hourly liquidation probability of a $20\times$ position.

    \subsection{Other venues}

    The result belongs to thin markets, not to one venue, but its size depends on the venue. In 23 thin US stocks a registered test passes at about a fifth of the Binance size ($+0.50$ points beyond the full baseline), carried again by the reversion term; mid-size stocks show a gain too. On Bybit the statistic is absent with trades alone (a registered failure) and, with order-book depth, meets its registered criterion with an effect about one eightieth of Binance's; on Coinbase spot the registered test fails. On both crypto venues where it fails, thin pairs trade sparsely (11\% of Bybit minutes have no trade, against 0.1\% on Binance), which leaves the series the statistic is estimated from much noisier.

    \subsection{The guard as a risk control}

    The guard's theorems concern worst-case loss under a certified operator; whether its statistic helps size positions in practice is a separate question, and the answer is: modestly, and not instead of volatility. A six-hour estimate scaled into a volatility limit does not improve it (a registered failure), and limits built on the estimate alone are worse than a static limit. With an operator certified from three days of data, the scaled limit lowers tail loss per unit of position by 2.4\% (a narrow registered pass). Used as the theorem uses it, as a one-sided throttle, the certified guard lowers tail loss against a static limit by 8\% on untouched days and 23\% on untouched symbols (registered passes), but not against a volatility cap at matched activity. Over 18-hour holding periods, an uncapped version failed its registered capacity test; a capped throttle of the kind Rule~15c3-5 requires, registered after that failure, lowers the forced-liquidation rate of a $20\times$ position by 7.4 percentage points against a volatility cap, mostly because it admits 11\% less exposure; scaled to the same mean exposure the two rules are indistinguishable.\label{p2:sec:p24}

    \subsection{What the effect is not: the mechanism tests}\label{p2:sec:p22}

    Two registered tests asked whether the forecasting content runs through forced liquidations, measured by five-minute open-interest contractions with adverse price moves. Both fail: $\hat C_3$ does not forecast them, and they mediate none of its forecasting gain ($-6.8\%$). A leverage interaction, specified in advance but not hash-registered, also fails. A follow-up registered after these failures finds that $\hat C_3$ forecasts price persistence over the next 15 to 60 minutes and that this persistence accounts for nearly all of its forecasting gain, but its registered placebo clause fails, so the mediation is not established.\label{p2:sec:p25} A zero-fee natural experiment leaves reversion unchanged and lowers impact. On October 10, 2025, reported descriptively, the summed response was elevated all day but did not warn of anything volatility missed in the final hours. We therefore read the evidence as showing that thin books are risky because their prices revert slowly relative to impact, which is what the statistic measures, not as a test of a deeper mechanism.

    \subsection{Every registered test}\label{p2:sec:alltests}
    Of twenty-five registered primaries, fifteen pass, nine fail and one was not tested because the test it depended on failed (Table~\ref{p2:tab:alltests}).
    """)
    add(L(1308, 1345))
    add(r"""
    \paragraph{How to read the passes.} The program was sequential: each registration protected one test from specification search on its own test data, but which test to run next was chosen after the earlier results were known. The passing Binance tests share training days and are not independent replications; they vary one thing at a time (symbols, days, baseline), and the US test shares none of their data. Every feature uses only minutes before the forecast hour, and a scrambling audit leaves every feature unchanged when later data are permuted. The gains are modest on top of a strong baseline, a 15\% increase in the explained variance of the next hour's excursion at most; they are not a new predictor that replaces volatility.

    \section{Tests of the information-safety results}\label{p2:sec:istests}

    The theorems of Sections~\ref{p2:sec:infosafety}--\ref{p2:sec:disclosure} concern declared contracts, which market data cannot deliver. They are therefore tested in simulations with a known truth (Table~\ref{p2:tab:simtests}).
    """)
    add(L(1380, 1408))
    add(r"""
    \section{Policy implications}\label{p2:sec:policy}

    Rule 15c3-5 requires pre-trade controls that prevent orders exceeding credit or capital thresholds \citep{p2:sec2010}; static caps and daily value-at-risk limits do not see transient dynamics. Lemma~\ref{p2:thm:guard} names the quantity a solvency-motivated control should bound, inventory times the shock envelope times the summed absolute impulse response, and peak- or eigenvalue-based limits are unsafe or blind exactly where they matter. The evidence says where such a control matters (thin books, under about \$0.4M of depth within 1\% of the mid) and what it can do with public data: correct a volatility limit modestly, not replace it. Because the summed response is certified without identifying the traders, a supervisor or venue can set limits, or price a reversion rebate in proportion to $S^2/\tilde\kappa$, from an observable. Guards should use certified upper bounds; rebates should use point estimates.

    \section{Conclusion}\label{p2:sec:conclusion}

    The theory answers four questions. A book amplifies when depletion outweighs impact-weighted reversion; cumulative transient risk is long-run impact over reversion net of momentum; the guard on the summed response is the largest safe admission rule and needs no identification of the traders; and the information that certifies a safe decision is cheap in exactly the directions in which identification is expensive. The evidence is mixed in an informative way: the deepest book does not amplify and the statistic is useless there, while in thin books it forecasts the size of adverse excursions beyond every baseline we tried, at a size that depends on the venue, and as a practical control it adds to volatility only modestly. Message-level data from a regulated market, data on liquidity-provider identities, and a market observed near the stability boundary would settle what remains open.

    \paragraph{Data, code and AI use.} All data are public and every number is produced by archived code from them; specifications, hashes and unlock counters are in the replication package. The authors used Claude (Anthropic) to write and debug analysis code, check derivations and draft and edit text; every number comes from code the authors executed, and the authors take full responsibility for the content.
    """)

    # bibliography: keep the full chapter's environment, filtered below to the keys still cited
    add(L(1769, 1834))

    add(r"""
    \section{Appendix: Proofs}\label{p2:app:proofs}
    """)
    for a in (1838, 1840, 1842, 1849, 1855, 1863, 1865, 1867, 1869, 1871):
        add(L(a, a))
        add("")

    out = "\n".join(parts) + "\n"

    # drop bibliography entries no longer cited
    cited = set()
    for m in re.finditer(r"\\cite[pt]?\*?(?:\[[^\]]*\])?\{([^}]*)\}", out.split("\\begin{thebibliography}")[0] + out.split("\\end{thebibliography}")[1]):
        cited.update(k.strip() for k in m.group(1).split(","))
    head, rest = out.split("\\begin{thebibliography}", 1)
    bib, tail = rest.split("\\end{thebibliography}", 1)
    lines = bib.split("\n")
    keep = [lines[0]] + [l for l in lines[1:] if not l.startswith("\\bibitem") or re.search(r"\]\{([^}]*)\}", l).group(1) in cited]
    out = head + "\\begin{thebibliography}" + "\n".join(keep) + "\\end{thebibliography}" + tail
    # references to sections, results and tables of the full chapter that the condensed chapter does not keep
    TEXT_FIX = {
        "are analysed in Theorem~\\ref{p2:thm:forward}": "are treated in the full version",
        "(Mode B below)": "(a venue that admits a fraction of incoming algorithmic flow)",
        "Certified by Lemma~\\ref{p2:lem:certnum} for every window": "Certified by verified polynomial sign conditions for every window",
    }
    for a, b in TEXT_FIX.items():
        out = out.replace(a.replace("\\\\", "\\"), b)
    REF_MAP = {"p2:sec:depth": "p2:sec:evidence", "p2:sec:spot": "p2:sec:evidence", "p2:sec:p15": "p2:sec:evidence",
               "p2:sec:p16": "p2:sec:evidence", "p2:sec:x6": "p2:sec:thin", "p2:sec:fixedgrid": "p2:sec:evidence",
               "p2:sec:y6": "p2:sec:thin", "p2:sec:z6": "p2:sec:thin", "p2:sec:z9": "p2:sec:thin", "p2:sec:us": "p2:sec:evidence",
               "p2:sec:simtests": "p2:sec:istests", "p2:sec:backtest": "p2:sec:p24", "p2:sec:certguard": "p2:sec:p24"}
    for a, b in REF_MAP.items():
        out = out.replace("{" + a + "}", "{" + b + "}")
    defined = set(re.findall(r"\\label\{([^}]*)\}", out))
    for f in T.glob("*.tex"):
        if f.name not in ("ch3_paper2.tex", "ch3_paper2_full.tex"):
            defined |= set(re.findall(r"\\label\{([^}]*)\}", f.read_text()))
    missing = sorted({m for m in re.findall(r"\\(?:ref|eqref|Cref|cref)\{([^}]*)\}", out) if m not in defined})
    print("undefined references after mapping:", missing)
    (T / "ch3_paper2.tex").write_text(out)
    words = len(re.sub(r"\\[a-zA-Z]+", "", out).split())
    print("ch3_paper2.tex written:", len(out.split("\n")), "lines,", words, "words; bib entries kept:",
          sum(l.startswith("\\bibitem") for l in keep))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
