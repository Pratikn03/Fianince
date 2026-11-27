"""Revision of 27 November 2026: sharper claims, one headline theorem, three side results moved to the supplement.

Applied last, to the main text written by make_short.build and to the supplement written by build_short.supplement_tex.
Every replacement asserts that its target occurs exactly once, so a change upstream fails loudly.

Main text:
  * abstract restated around the supervisory separation; "prices alone" and "durable targeting requires" removed;
  * new Theorem (The supervisory separation), label n:separation, at the head of Section 7, with a proof in Appendix A;
  * introduction: the central result stated first; item 1 cites the near-instability proposition, not the figure;
    item 4 says what is assumed about owner-linked records; item 5 states the class of tests; Taiwan paragraph
    states the grant and the leading-order caveat;
  * the uniform-cut paragraph states the measurement model it uses (direct kernel taps), as the supplement does;
  * Taiwan: the registered holdout (D = 0.0426) is reported as the registered result; the limit-masked rerun and the
    regime split are labelled post hoc; "reflect TWAP/VWAP slicing" becomes "consistent with"; the supplement's
    non-claim is stated;
  * Theorem thm:mpv, Corollary cor:posthaltflip and Proposition prop:endogenous_supervisor, with their proofs, move to
    the supplement; one sentence each stays in the main text.

Supplement: receives the three results; Table S2 rows say what Lean checks; the declaration count is 1,310.
"""
import re

MOVED_LABELS = ('thm:mpv', 'cor:posthaltflip', 'prop:endogenous_supervisor')


def rep(t, old, new, count=1):
    n = t.count(old)
    assert n == count, (old[:140], n, count)
    return t.replace(old, new)


def cut(t, start, end):
    """Remove t[start .. end] inclusive of both markers; return (new text, removed block)."""
    a = t.index(start)
    b = t.index(end, a) + len(end)
    assert t.count(start) == 1, start[:80]
    return t[:a] + t[b:], t[a:b]


ABSTRACT_OLD_START = r"We study financial markets in which heterogeneous trading algorithms"
ABSTRACT_OLD_END = r"illustrate the magnitude of this informational gap."
ABSTRACT_NEW = (
    r"We study financial markets in which heterogeneous trading algorithms feed a common public pricing signal back "
    r"into order flow. In a linear market and in a stationary inventory-dealer equilibrium, every public "
    r"outcome---prices, volume, dealer inventories and optimal forecasts---depends on the trader population only "
    r"through its aggregate feedback kernel. This yields a supervisory separation. Once persistence and impact are "
    r"known, whether a uniform feedback cut meets a stability ceiling can be learned from the aggregate response at a "
    r"cost that does not depend on how close the traders' memories are, and without class tags the uniform cut is "
    r"minimax over labelings. Whether a targeted restriction meets the same ceiling can require of order "
    r"$\Delta^{-(4K-2)}$ observations when $K$ classes have memory rates within $\Delta$, even near instability or "
    r"under active probes; verified class tags remove that penalty. Cheap relabeling across accounts erodes tags, "
    r"and untagged surveillance invites traders to crowd their memories. Class-tagged flows from the Taiwan Stock "
    r"Exchange calibrate the gap."
)

CENTRAL = (
    r"\textbf{The central result.} The paper's central result is a supervisory separation "
    r"(Theorem~\ref{n:separation}). Given persistence, impact and a memory bound, whether a uniform feedback cut "
    r"meets a stability ceiling depends on the population only through the aggregate budget, which "
    r"$O(\sigma^2\epsilon^{-2}\log(1/\epsilon))$ kernel-tap records estimate to accuracy $\epsilon$ however close "
    r"the traders' memories are; without tags, the uniform cut is minimax over labelings. Whether a targeted "
    r"restriction meets the same ceiling can require $c\sigma^2(\Delta\eta)^{-(4K-2)}$ records, and verified class "
    r"tags remove that dependence on spacing for class weights. The five results below supply the pieces, and the "
    r"last two ask how far tags survive strategic traders." + "\n\n"
)

SEPARATION = r"""\subsection{The supervisory separation}\label{sec:separation}

The results of this section combine into one statement. Fix $K \ge 2$, known $(a, \kappa)$, a memory bound $\bar r < 1$ on total merged weight at most $\bar W$, and a ceiling $\bar s \in (a, 1)$ in a positive, stable market. Records are $N$ independent experiments with Gaussian noise of variance $\sigma^2$: direct kernel-tap measurements as in Theorem~\ref{n:questions} for part~(i), and the reset contract of Theorem~\ref{n:cost} for parts~(ii) and~(iii).

\begin{theorem}[The supervisory separation]\label{n:separation}
\begin{enumerate}
  \item[(i)] \emph{Uniform cuts need only the aggregate.} Whether scaling all feedback by $\theta \in [0, 1]$ meets $\bar s$ depends on the population only through the budget $S$. For every $\epsilon \in (0, 1)$ and $\beta \in (0, 1)$, $S$ is estimated to accuracy $\epsilon$ with probability at least $1 - \beta$ from $N = O(\sigma^2 \kappa^2 \epsilon^{-2} \log(1/\epsilon) \log(1/\beta))$ records at tap depth $O(\log(1/\epsilon))$, with constants depending only on $(\kappa, \bar r, \bar W)$ and not on the number of groups or the spacing of their memory rates. Without tags, for convex prudential loss and continuous, convex, label-symmetric cost, uniform scaling is minimax over labelings.
  \item[(ii)] \emph{Targeted restrictions need composition.} For halting the largest group, and for halting every group whose memory lies below a cutoff, there are pairs of $K$-group economies with memory rates in an interval of length $3\Delta\eta$ on which, over a nonempty interval of ceilings, the restriction meets $\bar s$ in one economy and breaches it in the other; deciding which, with both error probabilities at most $1/4$, requires $N \ge c\, \sigma^2 (\Delta\eta)^{-(4K-2)}$ records.
  \item[(iii)] \emph{Verified tags remove the spacing penalty for weights.} If each class's flow is also recorded at the first two response dates, then over the families of Theorem~\ref{n:disc} recovering class weights to a fixed accuracy below half the weight gap of the hard pair requires a number of experiments that does not grow as $\Delta\eta \to 0$; recovering memory rates to accuracy $c_0 \Delta\eta$ still requires order $(\Delta\eta)^{-2}$.
\end{enumerate}
\end{theorem}

Part~(i) is a statement about the aggregate alone; parts~(ii) and~(iii) say that composition is what a targeted rule needs and what tags supply. The rest of the section proves the parts and asks how far tags survive traders who respond to them: relabeling erodes tags (Proposition~\ref{n:relabel}) and untagged tests invite crowding (Theorem~\ref{n:paradox}).

"""

SEPARATION_PROOF = r"""\begin{proof}[Proof of Theorem~\ref{n:separation}]
\emph{(i)} The first claim is Proposition~\ref{n:target}(i). For the rate, write $S = a + \kappa \sum_{m \ge 0} k_m$ and estimate $\sum_{m < L} k_m$ by the sum of the $L$ tap averages. Because $|k_m| \le \bar W \bar r^m$, the omitted tail is at most $\bar W \bar r^L / (1 - \bar r)$, which is below $\epsilon / (2\kappa)$ once $L \ge \log(2\kappa \bar W / (\epsilon(1 - \bar r))) / \log(1/\bar r)$. The sum of $L$ independent tap averages has Gaussian error with variance $L \sigma^2 / N$, so it is within $\epsilon / (2\kappa)$ with probability at least $1 - \beta$ once $N \ge 8 \kappa^2 \sigma^2 L \log(2/\beta) / \epsilon^2$. Neither bound involves $K$ or the memory spacing. Minimax optimality is Theorem~\ref{n:minimax}(i). \emph{(ii)} Proposition~\ref{n:target}(ii) for the largest group (memories in $r_c + \Delta\eta[-1, 1]$) and Proposition~\ref{n:target}(iii) for the cutoff (memories in $[\hat r - \Delta\eta, \hat r + 2\Delta\eta]$). \emph{(iii)} Theorem~\ref{n:disc}.
\end{proof}

"""

MPV_STUB = (r"Rounding prices to the exchange's tick grid does not rescue identification either: the barrier survives Gaussian "
            r"dithering, and it becomes absolute when shocks stay inside one tick cell (Supplement "
            r"Theorem~\ref{S-thm:mpv}).")

POSTHALT_STUB = (r"A halt can also fail in equilibrium for a different reason: if it removes dealer risk-bearing capacity, "
                 r"endogenous impact can pass the fold of Theorem~\ref{thm:fragility} (Supplement "
                 r"Corollary~\ref{S-cor:posthaltflip}).")

SUPERVISOR_STUB = (r"If the supervisor also chooses how hard to monitor, crowding makes committed monitoring unprofitable for "
                   r"large records under high stakes, and equilibrium auditing must be randomized (Supplement "
                   r"Proposition~\ref{S-prop:endogenous_supervisor}).")

TAIWAN_HOLDOUT_OLD_START = r"Second, in the 2019--2023 out-of-sample holdout (Figure~\ref{fig:twse_sensitivity};"
TAIWAN_HOLDOUT_OLD_END = r"rather than pure causal feedback."
TAIWAN_HOLDOUT_NEW = (
    r"Second, in the registered 2019--2023 out-of-sample holdout (Figure~\ref{fig:twse_sensitivity}; Supplement "
    r"Sections~\ref{S-sec:scope} and~\ref{S-app:barrier}), let $\hat D_{\mathrm{OOS}}$ denote the proportional "
    r"out-of-sample MSE reduction in forecasting class flow from $x_{t-1}$ beyond own-flow persistence. The registered "
    r"primary statistic is $\hat D_{\mathrm{OOS}} = 0.0426$ for foreign flow ($95\%$ block-20 interval "
    r"$[0.0206, 0.0643]$, block-60 $p = 0.0024$), which meets the registered supportive criterion; it is positive in "
    r"2019--2021 and not distinguishable from zero in 2022 ($0.0141$) or 2023 ($-0.0158$), trust and proprietary "
    r"dealer flows are null ($p_{\mathrm{Holm}} = 1.0$), finite-sample plug-in standard errors are severely "
    r"downward-biased relative to the block bootstrap, and the registered reverse-causality placebo "
    r"($-0.0065$, $[-0.0316, 0.0165]$) cannot rule out that daily price deviations partly reflect prior institutional "
    r"order flow rather than pure causal feedback. Two later analyses, not registered, point the same way: masking "
    r"price-limit and post-halt days gives $0.0410$ ($[0.0197, 0.0623]$), and splitting at the 23~March~2020 switch to "
    r"continuous matching gives $0.0319$ before and $0.0421$ after. We do not claim that tagged flow in Taiwan "
    r"responds causally to price deviations."
)

FIG3_OLD_START = r"\caption{TWSE empirical sensitivity and 2019--2023 out-of-sample holdout."
FIG3_OLD_END = r"$\hat{\kappa}_{\Delta x}=0.00209$).}"
FIG3_NEW = (
    r"\caption{TWSE 2019--2023 out-of-sample holdout and specification sensitivity. Panel~A: foreign proportional MSE "
    r"gain $\hat{D}_{\mathrm{OOS}}$ with $95\%$ block-20 intervals. Rows marked ``registered'' are the registered "
    r"holdout (pooled $0.0426$, annual subsamples, reverse-causality placebo $-0.0065$); rows marked ``post hoc'' were "
    r"run after the holdout was opened (limit and post-halt days masked, $0.0410$; split at the 23~March~2020 switch to "
    r"continuous matching, $0.0319 \to 0.0421$). Panel~B: estimated persistence $\hat{r}_c$ ($95\%$ CI) across "
    r"Baseline, Limit-Excluded ($\hat{\kappa}=0.00409$), and First-Differenced $\Delta x_t$ ($\sum \hat{a}_j=-0.109$, "
    r"$\hat{\kappa}_{\Delta x}=0.00209$).}"
)


def main_text(t):
    """Apply the 27 November revision to the main text; return (text, moved blocks)."""
    moved = {}
    # ---------------------------------------------------------------- abstract
    a = t.index(ABSTRACT_OLD_START)
    b = t.index(ABSTRACT_OLD_END, a) + len(ABSTRACT_OLD_END)
    t = t[:a] + ABSTRACT_NEW + t[b:]
    # ---------------------------------------------------------------- introduction
    t = rep(t, "Five economic results organize the analysis:", CENTRAL + "Five economic results organize the analysis:")
    t = rep(t, r"and does not vanish as the market approaches instability (Figure~\ref{fig:near-instability}).",
            r"and does not vanish as the market approaches instability (Supplement Proposition~\ref{S-prop:nearcrit}; "
            r"Figure~\ref{fig:near-instability}).")
    t = rep(t, r"An owner-linked audit trail that ties accounts to beneficial owners retains its value whenever "
               r"beneficial-ownership links prevent cross-account routing.",
            r"Records that link accounts to beneficial owners keep their value only to the extent that they make such "
            r"routing visible; the model takes this as a property of the audit trail, not as a result.")
    t = rep(t, r"Against any standard local-power test, a high-stakes untagged algorithm",
            r"Against a fixed-level test whose power grows at least like the square root of the divergence, a "
            r"high-stakes untagged algorithm")
    t = rep(t, r"Holding each class's non-feedback flow law fixed, tagged flows carry $4.7 \times 10^5$ times more "
               r"information per stock-day about composition than prices alone. Given market persistence, impact, and "
               r"non-feedback flow, a spectral-rate search",
            r"Granting a price-only supervisor the market's persistence, impact and non-feedback flow law, tagged "
            r"flows carry, at leading order, $4.7 \times 10^5$ times more information per stock-day about composition "
            r"than prices. On the same grant, a spectral-rate search")
    t = rep(t, r"solve the strategic relabeling game between class tags and owner-linked audit trails,",
            r"combine these into a supervisory separation between uniform and targeted rules (Theorem~\ref{n:separation}), "
            r"solve the strategic relabeling game between class tags and owner-linked audit trails,")
    # ---------------------------------------------------------------- Section 7 headline theorem
    marker = r"\subsection{Market-wide versus targeted interventions}"
    t = rep(t, marker, SEPARATION + marker)
    t = rep(t, r"summing noisy impulse-response lags at logarithmic depth estimates $S$ to accuracy $\epsilon$ in "
               r"$O(\sigma^2\epsilon^{-2}\log(1/\epsilon))$ experiments.",
            r"summing noisy kernel-tap measurements at logarithmic depth estimates $S$ to accuracy $\epsilon$ in "
            r"$O(\sigma^2\epsilon^{-2}\log(1/\epsilon))$ experiments (Theorem~\ref{n:separation}(i)); price-only "
            r"impulse records need separate growing-depth bounds on the reconstructed taps (Supplement "
            r"Section~\ref{S-app:questions}).")
    # ---------------------------------------------------------------- move three side results
    t, moved['thm:mpv'] = cut(t, r"Discrete exchange tick grids do not rescue compositional identification",
                              "\\end{theorem}\n")
    t = rep(t, r"\subsection{Which questions prices answer cheaply}",
            MPV_STUB + "\n\n" + r"\subsection{Which questions prices answer cheaply}")
    t, moved['thm:mpv_proof'] = cut(t, r"\begin{proof}[Proof of Theorem~\ref{thm:mpv}]", "\\end{proof}\n")
    t, moved['cor:posthaltflip'] = cut(t, r"\begin{corollary}[Ceiling stabilization versus dealer-capacity withdrawal]",
                                       "\\end{corollary}\n")
    t = rep(t, r"Figure~\ref{fig:intervention} illustrates this contrast",
            POSTHALT_STUB + "\n\n" + r"Figure~\ref{fig:intervention} illustrates this contrast")
    t, moved['cor:posthaltflip_proof'] = cut(t, r"\begin{proof}[Proof of Corollary~\ref{cor:posthaltflip}]",
                                             "\\end{proof}\n")
    t, moved['prop:endogenous_supervisor'] = cut(
        t, r"Endogenizing the supervisor's monitoring intensity sharpens this tension", "\\end{proposition}\n")
    t, moved['prop:endogenous_supervisor_proof'] = cut(
        t, r"\begin{proof}[Proof of Proposition~\ref{prop:endogenous_supervisor}]", "\\end{proof}\n")
    t = rep(t, r"while memory-independent tag inquiries eliminate crowding altogether.",
            r"while memory-independent tag inquiries eliminate crowding altogether. " + SUPERVISOR_STUB)
    t = rep(t, r"GLRT slowing; Proposition~\ref{prop:endogenous_supervisor})",
            r"GLRT slowing; Supplement Proposition~\ref{S-prop:endogenous_supervisor})")
    for lab in MOVED_LABELS:
        assert '{' + lab + '}' not in t, lab
    # ---------------------------------------------------------------- Taiwan
    t = rep(t, r"while unconstrained distributed lags reflect day-1 TWAP/VWAP parent-order slicing reversal followed by "
               r"multi-day persistence",
            r"while unconstrained distributed lags show a day-1 reversal followed by multi-day persistence, consistent "
            r"with (but not shown to be) the slicing of parent orders by TWAP/VWAP algorithms")
    a = t.index(TAIWAN_HOLDOUT_OLD_START)
    b = t.index(TAIWAN_HOLDOUT_OLD_END, a) + len(TAIWAN_HOLDOUT_OLD_END)
    t = t[:a] + TAIWAN_HOLDOUT_NEW + t[b:]
    a = t.index(FIG3_OLD_START)
    b = t.index(FIG3_OLD_END, a) + len(FIG3_OLD_END)
    t = t[:a] + FIG3_NEW + t[b:]
    # ---------------------------------------------------------------- conclusion
    t = rep(t, r"First, market-wide feedback cuts are minimax-optimal over unknown labelings and can be calibrated from "
               r"impulse-response lags given market persistence, impact, and a memory bound",
            r"First, market-wide feedback cuts are minimax-optimal over unknown labelings and can be calibrated from "
            r"the aggregate response given market persistence, impact, and a memory bound, at a cost free of the "
            r"traders' spacing (Theorem~\ref{n:separation})")
    # ---------------------------------------------------------------- appendix proof of the new theorem
    t = rep(t, r"\begin{proof}[Proof of Proposition~\ref{n:target}(i)--(ii) and Corollary~\ref{n:decisionloss}]",
            SEPARATION_PROOF + r"\begin{proof}[Proof of Proposition~\ref{n:target}(i)--(ii) and Corollary~\ref{n:decisionloss}]")
    t = passive_upper(t)
    return t, moved


def _to_supplement(block, main_labels):
    """Rewrite a main-text block for the supplement: main labels get M-, supplement labels lose S-."""
    for lab in sorted(main_labels):
        for cmd in ('ref', 'eqref'):
            block = block.replace('\\' + cmd + '{' + lab + '}', '\\' + cmd + '{M-' + lab + '}')
    block = re.sub(r"Supplement (Section|Sections|Proposition|Theorem|Table|Lemma|Corollary)~\\ref\{S-",
                   r"\1~\\ref{", block)
    block = block.replace(r'\ref{S-', r'\ref{')
    block = re.sub(r"(?<!Main )Appendix~\\ref\{M-app:proofs\}", r"Main Appendix~\\ref{M-app:proofs}", block)
    return block


def supplement(doc, moved, main_labels):
    main_labels = set(main_labels) - set(MOVED_LABELS)
    # Every reference to the moved results now points inside the supplement.
    for lab in MOVED_LABELS:
        doc = doc.replace('{M-' + lab + '}', '{' + lab + '}')
    doc = rep(doc, r"(and Proposition~\ref{prop:endogenous_supervisor} is proved in Main Appendix~\ref{M-app:proofs}, "
                   r"extending Section~\ref{app:paradox})",
              r"(and Proposition~\ref{prop:endogenous_supervisor}, moved from the main text, is proved in "
              r"Section~\ref{app:paradox})")
    doc = rep(doc, r"Theorem~\ref{M-thm:fragility} and Corollary~\ref{cor:posthaltflip} are proved in Main "
                   r"Appendix~\ref{M-app:proofs}",
              r"Theorem~\ref{M-thm:fragility} is proved in Main Appendix~\ref{M-app:proofs} and "
              r"Corollary~\ref{cor:posthaltflip} in Section~\ref{sec:mixed_sign}")
    doc = rep(doc, r"Theorem~\ref{thm:mpv} is proved in Main Appendix~\ref{M-app:proofs} (details in "
                   r"Section~\ref{sec:mpv_supp})",
              r"Theorem~\ref{thm:mpv} is proved in Section~\ref{sec:mpv_supp}")
    # Insert the moved results where their details already are.
    mpv = (_to_supplement(moved['thm:mpv'], main_labels) + "\n" + _to_supplement(moved['thm:mpv_proof'], main_labels)
           .replace(r" (Section~\ref{sec:mpv_supp})", ""))
    head = r"\subsection{Minimum price variation and stochastic dithering details}\label{sec:mpv_supp}" + "\n"
    doc = rep(doc, head, head + "\n" + r"\noindent This result was moved from the main text (Section~\ref{M-sec:cost})."
              + " " + mpv + "\n")
    post = (_to_supplement(moved['cor:posthaltflip'], main_labels) + "\n"
            + _to_supplement(moved['cor:posthaltflip_proof'], main_labels))
    head = (r"\subsection{Mixed-sign stability, no-arbitrage spread bounds, and two-timescale dealer entry}"
            r"\label{sec:mixed_sign}" + "\n")
    doc = rep(doc, head, head + "\n" + r"\noindent The next result was moved from the main text "
              r"(Section~\ref{M-sec:supervision})." + "\n\n" + post + "\n")
    sup = (_to_supplement(moved['prop:endogenous_supervisor'], main_labels) + "\n"
           + _to_supplement(moved['prop:endogenous_supervisor_proof'], main_labels))
    head = r"\subsection{The surveillance paradox}\label{app:paradox}" + "\n"
    doc = rep(doc, head, head + "\n" + r"\noindent The next result was moved from the main text "
              r"(Section~\ref{M-sec:supervision})." + " " + sup + "\n")
    # Table S2: say what Lean checks.
    doc = rep(doc, r"small-feedback impact derivative, $n_{\mathcal{H}}<0<n_{\mathcal{B}}$ separation, Kalman variance "
                   r"identity, strict convexity $P''(r)>0$, and monotone $P'(r)$ (\texttt{micro\_welfare\_weight\_separation}, "
                   r"\texttt{kalman\_stationary\_var\_identity}, ",
              r"small-feedback impact derivative (the separation $n_{\mathcal{H}}<0<n_{\mathcal{B}}$ is a hypothesis of the "
              r"Lean statement, not derived there), Kalman variance identity, the formulas for $P'$ and $P''$ as the "
              r"derivatives of $P$, strict convexity $P''(r)>0$, and monotone $P'(r)$ "
              r"(\texttt{micro\_welfare\_weight\_separation}, \texttt{kalman\_stationary\_var\_identity}, "
              r"\texttt{kalmanP\_hasDerivAt}, \texttt{kalmanPderiv\_hasDerivAt}, ")
    doc = rep(doc, r"Stackelberg general-$n$ collapse, simultaneous non-existence of pure NE,",
              r"the final inequality of the Stackelberg collapse, the two payoff inequalities behind non-existence of a "
              r"pure NE (the best-response argument is on paper),")
    doc = rep(doc, r"zero-divergence inequality, and deterministic",
              r"the arithmetic of the zero-divergence case (the risk bound and unbounded sample complexity are proved on "
              r"paper), and deterministic")
    doc = rep(doc, r"transfer factor and function errors (\texttt{p1\_transfer\_factor\_error}",
              r"transfer factor and function errors, the factor bound with its exponential Lipschitz step proved "
              r"(\texttt{p1\_transfer\_factor\_error}, \texttt{p1\_exp\_lipschitz\_below}, "
              r"\texttt{p1\_transfer\_factor\_error\_unconditional}")
    doc = rep(doc, "1,306 named declarations", "1,310 named declarations")
    doc = passive_upper_supplement(doc)
    return doc


# ==================================================================== passive upper bound (27 November 2026, part 2)

PASSIVE_THEOREM = r"""\textbf{One passive price record attains the rates.} The upper bound in Theorem~\ref{n:cost}(iii) uses reset experiments. A single stationary record suffices too, because feedback flow is a causal filter of past pricing errors: with $v_t \equiv 0$, \eqref{eq:baseline} reads $x_t - a x_{t-1} = \kappa \sum_{j \ge 0} k_j x_{t-1-j} + \varepsilon_t$, an autoregression of infinite order whose coefficients are the kernel taps.

\begin{theorem}[One passive price record attains the rates]\label{n:passiveupper}
Fix known $(a, \kappa)$ with $a \ge 0$, $\kappa > 0$, and a margin $m \in (0, 1)$. Consider positive economies ($w_i \ge 0$) with budget $S \le 1 - m$, memory rates at most $\bar r < 1$ and total merged weight at most $\bar W$, observed through one stationary record $x_{1-L}, \dots, x_T$ of~\eqref{eq:baseline} with $v_t \equiv 0$ and i.i.d.\ $N(0, \sigma^2)$ news. Let $\hat\theta \in \R^L$ be the least-squares coefficients of $x_t - a x_{t-1}$ on $(x_{t-1}, \dots, x_{t-L})$, $\hat k = \hat\theta / \kappa$ and $\hat S = a + \sum_{j < L} \hat\theta_j$. For $\beta \in (0, 1/3)$ and $T \ge 128 L^2 / (m^4 \beta)$, with probability at least $1 - 3\beta$,
\[
  \|\hat k - (k_0, \dots, k_{L-1})\|_2 \le \frac{8\sqrt{L}}{\kappa}\Bigl(\frac{1}{m\sqrt{T\beta}} + \frac{\rho_L}{m^2 \beta}\Bigr),
  \qquad \rho_L = \frac{\kappa \bar W \bar r^L}{1 - \bar r},
\]
and $|\hat S - S| \le \kappa\sqrt{L}\, \|\hat k - (k_0, \dots, k_{L-1})\|_2 + \rho_L$. The news variance $\sigma^2$ does not enter.
\begin{enumerate}
  \item[(i)] \emph{The budget.} With $L$ of order $\log(1/(\epsilon\beta))$, $|\hat S - S| \le \epsilon$ with probability at least $1 - 3\beta$ once $T \ge C \epsilon^{-2} \beta^{-1} \log^2(1/(\epsilon\beta))$, whatever the number of groups and the spacing of their memories.
  \item[(ii)] \emph{Composition.} On the compact class of Theorem~\ref{n:cost}(iii) (rates $r_c + \Delta\eta\, s$ with $s$ $\gamma$-separated, weights in $[w_{\min}, w_{\max}]$, $w_{\min} > 0$, spacing $\Delta\eta \le \Delta\eta_0$), Prony's method applied to $\hat k_0, \dots, \hat k_{2K-1}$ recovers every weight to accuracy $\epsilon \in (0, \epsilon_0]$ with probability at least $1 - 3\beta$ once $L$ is of order $\log(1/(\epsilon\beta\Delta\eta))$ and
  \[
    T \ge C \epsilon^{-2} \beta^{-1} (\Delta\eta)^{-(4K-2)} \log\frac{1}{\epsilon\beta\Delta\eta}.
  \]
\end{enumerate}
The constants $C$ and $\epsilon_0$ depend only on $(\kappa, m, \bar r, \bar W)$ and, in~(ii), on $K$, $r_c$, $\Delta\eta_0$ and the class.
\end{theorem}

With Theorem~\ref{n:cost}(i), part~(ii) gives the passive sample requirement for composition, $(\Delta\eta)^{-(4K-2)}$ up to a logarithmic factor, from the record a supervisor actually has. Part~(i) does the same for the uniform cut: given $(a, \kappa)$, its budget is learned from passive prices at a near-parametric rate. The first step is the classical long autoregression \citep[Berk, 1974]{}; what the feedback market adds is that the autoregressive coefficients are the kernel taps, that positivity bounds the spectral density away from zero and infinity uniformly in the population, and that the tap error therefore does not depend on the spacing. In a simulation of a two-group economy from one stationary record ($a = 0.1$, $\kappa = 1$, $r_c = 0.45$, total weight $0.2$, memory offsets $\pm 0.5\,\Delta\eta$, $30$ lags, $40$ replications; replication archive), tap errors are flat in the spacing (fitted slope $-0.04$) and fall like $T^{-0.42}$, and weight errors have fitted slopes $-2.5$ in $\log\Delta\eta$ over $\Delta\eta \in [0.36, 0.70]$ (the asymptotic exponent $-3$ is approached as the spacing shrinks) and $-0.45$ in $\log T$.

"""

PASSIVE_PROOF = r"""\begin{proof}[Proof of Theorem~\ref{n:passiveupper}]
Because $y_{i,t-1} = \eta_i \sum_{j \ge 0} r_i^j x_{t-1-j}$, equation~\eqref{eq:baseline} with $v_t \equiv 0$ reads $x_t - a x_{t-1} = \sum_{j \ge 0} \theta_j x_{t-1-j} + \varepsilon_t$ with $\theta_j = \kappa k_j \ge 0$. Let $A(z) = 1 - a z - \sum_{j \ge 0} \theta_j z^{j+1}$. On $|z| \le 1$, $|A(z) - 1| \le a + \sum_j \theta_j = S \le 1 - m$, so $A$ has no zero in the closed disc, the record is causal in the news, and $m \le |A(e^{i\omega})| \le 2$. The spectral density $f = \sigma^2 / (2\pi |A(e^{-i\omega})|^2)$ lies in $[\sigma^2/(8\pi), \sigma^2/(2\pi m^2)]$, so the covariance matrix $\Gamma$ of $X_t = (x_{t-1}, \dots, x_{t-L})$ has eigenvalues in $[\sigma^2/4, \sigma^2/m^2]$, $\gamma(0) \le \sigma^2/m^2$, and by Parseval $\sum_u \gamma(u)^2 = 2\pi \int f^2 \le \sigma^4/m^4$.

Write $x_t - a x_{t-1} = X_t^\top \theta_{0:L-1} + \varrho_t + \varepsilon_t$ with $\varrho_t = \sum_{j \ge L} \theta_j x_{t-1-j}$, so that $\hat\theta - \theta_{0:L-1} = \hat\Gamma^{-1} T^{-1} \sum_t X_t (\varrho_t + \varepsilon_t)$ with $\hat\Gamma = T^{-1} \sum_t X_t X_t^\top$. (a) For a stationary Gaussian record each entry of $\hat\Gamma - \Gamma$ has variance at most $2 T^{-1} \sum_u \gamma(u)^2$, so $E\|\hat\Gamma - \Gamma\|_F^2 \le 2 L^2 \sigma^4 / (m^4 T)$; by Chebyshev's inequality $\|\hat\Gamma - \Gamma\|_{\mathrm{op}} \le \sigma^2/8$, hence $\|\hat\Gamma^{-1}\|_{\mathrm{op}} \le 8/\sigma^2$, with probability at least $1 - 128 L^2/(m^4 T) \ge 1 - \beta$. (b) $\varepsilon_t$ is independent of $(X_s, \varepsilon_s, X_t)$ for $s < t$, so $E\|T^{-1} \sum_t X_t \varepsilon_t\|^2 = L \gamma(0) \sigma^2 / T$, and this norm is at most $\sigma^2 \sqrt{L/(m^2 T \beta)}$ with probability at least $1 - \beta$. (c) $\operatorname{Var} \varrho_t \le \rho_L^2 \gamma(0)$ with $\rho_L \ge \sum_{j \ge L} \theta_j$, so $E\|T^{-1} \sum_t X_t \varrho_t\| \le \sqrt{L}\, \gamma(0) \rho_L$, and this norm is at most $\sqrt{L}\, \sigma^2 \rho_L / (m^2 \beta)$ with probability at least $1 - \beta$. On the intersection, $\|\hat\theta - \theta_{0:L-1}\|_2 \le 8\sqrt{L}\{(m\sqrt{T\beta})^{-1} + \rho_L/(m^2\beta)\}$, the displayed bound; and $|\hat S - S| = |\sum_{j < L} (\hat\theta_j - \theta_j) - \sum_{j \ge L} \theta_j| \le \sqrt{L}\, \|\hat\theta - \theta_{0:L-1}\|_2 + \rho_L$.

\emph{(i)} Take the least $L$ with $8 L \rho_L / (m^2 \beta) + \rho_L \le \epsilon/2$, of order $\log(1/(\epsilon\beta))$, and
\[ T \ge \max\{256 L^2 / (m^2 \beta \epsilon^2),\ 128 L^2/(m^4\beta)\}. \]
\emph{(ii)} By the proof of Theorem~\ref{n:cost}(iii) there are $c_0, C_P$, depending only on the class, such that if the first $2K$ taps are known to within $\tau \le c_0 (\Delta\eta)^{2K-1}$ in Euclidean norm, Prony's method returns every weight to within $C_P \tau (\Delta\eta)^{-(2K-1)}$. Set $\epsilon_0 = c_0 C_P$ and $\tau = \epsilon (\Delta\eta)^{2K-1} / C_P$. On the class, rates are at most $\bar r = r_c + \Delta\eta_0 \max_{s,i} |s_i| < 1$ and total weight at most $K w_{\max}$. Take the least $L \ge 2K$ with $8\sqrt{L}\, \rho_L / (\kappa m^2 \beta) \le \tau/2$, of order $\log(1/(\epsilon\beta\Delta\eta))$, and
\[ T \ge \max\{256 L / (\kappa^2 m^2 \beta \tau^2),\ 128 L^2/(m^4\beta)\}, \]
which is the stated order.
\end{proof}

"""


def passive_upper(t):
    t = rep(t, r"\textbf{The barrier does not lift near instability.}",
            PASSIVE_THEOREM + r"\textbf{The barrier does not lift near instability.}")
    t = rep(t, r"\begin{proof}[Proof of Theorem~\ref{n:questions}]", PASSIVE_PROOF + r"\begin{proof}[Proof of Theorem~\ref{n:questions}]")
    t = t.replace(r"\citep[Berk, 1974]{}", r"(Berk, 1974)")
    t = rep(t, r"with constants depending only on $(\kappa, \bar r, \bar W)$ and not on the number of groups or the spacing of "
               r"their memory rates.",
            r"with constants depending only on $(\kappa, \bar r, \bar W)$ and not on the number of groups or the spacing of "
            r"their memory rates; if $S \le 1 - m$ for a fixed margin $m$, one passive price record of length "
            r"$O(\epsilon^{-2}\log^2(1/\epsilon))$ suffices as well.")
    t = rep(t, r"Neither bound involves $K$ or the memory spacing. Minimax optimality is Theorem~\ref{n:minimax}(i).",
            r"Neither bound involves $K$ or the memory spacing. The passive version is "
            r"Theorem~\ref{n:passiveupper}(i). Minimax optimality is Theorem~\ref{n:minimax}(i).")
    t = rep(t, r"; price-only impulse records need separate growing-depth bounds on the reconstructed taps (Supplement "
               r"Section~\ref{S-app:questions}).",
            r"; one passive price record suffices at rate $O(\epsilon^{-2}\log^2(1/\epsilon))$ "
            r"(Theorem~\ref{n:passiveupper}(i)).")
    t = rep(t, r"which $O(\sigma^2\epsilon^{-2}\log(1/\epsilon))$ kernel-tap records estimate to accuracy $\epsilon$ however "
               r"close the traders' memories are;",
            r"which kernel-tap records, or a single passive price record, estimate at a near-parametric rate however "
            r"close the traders' memories are (Theorem~\ref{n:passiveupper});")
    t = rep(t, r"matches a Prony and minimum-distance upper bound on separated shrinking clusters (Theorem~\ref{n:shape}),",
            r"matches a Prony and minimum-distance upper bound on separated shrinking clusters (Theorem~\ref{n:shape}), is "
            r"attained up to a logarithmic factor from one passive price record (Theorem~\ref{n:passiveupper}),")
    t = rep(t, r"characterize which linear functionals prices answer at parametric rates,",
            r"show that one passive price record attains the composition rate up to a logarithm and learns the budget at a "
            r"near-parametric rate, characterize which linear functionals prices answer at parametric rates,")
    return t


def passive_upper_supplement(doc):
    return rep(doc, r"Growing-depth guarantees for price-only records require separate bounds on the reconstructed "
                    r"statistic and its error.",
               r"For a single passive record, least-squares autoregression on logarithmically many lags gives such "
               r"growing-depth guarantees (Main Theorem~\ref{M-n:passiveupper}).")
