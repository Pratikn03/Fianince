"""21 November 2026, ninth round: the response to two simulated referee reports
(ceiling_suite/papers/paper1/review/REFEREE_REPORTS_SIMULATED_20261121.md; response in REFEREE_RESPONSE_20261121.md).
Applied by build_revision.py after round7, so both the full working paper and the journal version carry it.

Corrections of substance:
  * Supplement Proposition prop:nearcrit used a pair that the paper's observer can tell apart (different persistences).
    It is restated for an admissible pair: a common persistence, with the Gauss--Radau weights rescaled by 1 + c,
    c = O((spacing)^(2K-1)), to match budgets. Figure 1, Table 1 and the numerical checks are recomputed for that pair
    (research_extension/fragility_reveals/nearcrit_admissible.py).
  * Supplement Proposition prop:hidegame took the exponent 6 from the moment-matched pairs; it now takes c N delta^n,
    with n = 4 against the closest economy in the null (Theorem n:paradox, round5).
  * The Taiwan calibration states that the targeted range fills the box by construction, what is granted to the
    price-only supervisor, and the definitions of x, the flows and the universe.
Statements made precise: what a uniform cut needs (known persistence, a memory bound), the reset contract of
Theorem n:thm_eqreduced(iv), the small-feedback condition of Theorem n:thm_inventory(iv), the minimax wording of
Theorem n:minimax (labels pi), the computability caveat of Theorem n:shape, the scope of the Lean check of
Theorem n:dual, the attribution of Theorem n:questions, and the ranking built into Proposition n:relabel.
Presentation: abstract, revision-history wording, cross-references, related manuscripts, references (cited only,
alphabetical).
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NEARCRIT = ROOT / 'research_extension/fragility_reveals/nearcrit_admissible_results.json'

# The corrected Theorem n:paradox, the remarks on restrictions by horizon and on uniqueness, and Supplement
# Propositions prop:nearcrit and prop:hidegame have not been read by the authors yet. Set to True only after the first author says
# he has read and checked them.
CORRECTIONS_CHECKED_BY_FIRST_AUTHOR = False


def _rep(t, old, new, count=1):
    n = t.count(old)
    assert n == count, (old[:100], n, count)
    return t.replace(old, new)


ABSTRACT = (r"Algorithmic traders read prices and, by trading, move them. We ask what the public record reveals about "
            r"the population of such traders, and what supervisors need beyond it. When traders respond to a common "
            r"public signal, the population affects prices, order flows and dealer inventories only through its "
            r"aggregate feedback response, also in an inventory equilibrium. Learning anything finer is expensive: in "
            r"the worst case, telling apart $K$ trader types whose rules lie within $\Delta$ of one another takes on "
            r"the order of $\Delta^{-(4K-2)}$ observations, an order attained for linear memory rules. Given the "
            r"market's own persistence and a bound on memory, a uniform cut in feedback can be set from prices, and "
            r"without class tags it is minimax over the assignments of labels that the record allows; a targeted "
            r"restriction cannot be set from prices. Class tags restore targeting only if relabeling is costly; an "
            r"audit trail that links accounts to owners, and cannot be gamed, does not need that. Without tags, more "
            r"data can leave the supervisor less informed, because an algorithm that fears targeting crowds toward "
            r"its neighbour. A calibration to Taiwan's tagged exchange flows illustrates the barrier; a registered "
            r"test there did not establish that the tagged responses are feedback. Core steps are checked in Lean~4.")

WHATSNEW_OLD = (r"The new results are economic. Sufficiency survives when price impact is an equilibrium outcome. In a "
                r"feedback market, what a record reveals about two candidate populations equals the forecast loss from "
                r"confusing them, which is why a uniform cut can be set from prices while a targeted restriction cannot. "
                r"And the disclosure game has a sharp answer:")
WHATSNEW_NEW = (r"That market-wide policies need only a reduced-form aggregate while targeted ones need structure is "
                r"Marschak's maxim and the logic of sufficient statistics for policy \citep{marschak1953,chetty2009}; "
                r"what we add is the price of the structure in a feedback market. Sufficiency survives when price "
                r"impact is an equilibrium outcome, and dealers' anticipation over-weights slow memories in equilibrium "
                r"prices (Theorem~\ref{n:thm_eqreduced}). Which linear questions about the population prices answer "
                r"cheaply is characterized exactly (Theorem~\ref{n:questions}). And the disclosure game has a sharp "
                r"answer:")

LIT_ADD = (r"Feedback traders are central to models of destabilizing speculation and of return autocorrelation "
           r"\citep{delong1990,cutler1990,sentana1992}; inventory-based price impact goes back to \citet{ho1981} and "
           r"\citet{grossman1988}, and \citet{hendershott2014} measure it. Simulation-based estimation of agent-based "
           r"models \citep{grazzini2015,platt2020} faces the same identification question in nonlinear models. Our "
           r"identification result is global; where memories collide, the information matrix of "
           r"\citet{rothenberg1971} is singular, and our rates say how fast identification weakens near a collision. "
           r"Our minimax results are decisions under ambiguity in the sense of \citet{manski2000}. "
           r"Crowding among algorithmic and quantitative strategies is documented by \citet{chaboud2014} and "
           r"\citet{khandani2011} and analysed by \citet{stein2009}, and anonymity in limit-order markets, which "
           r"concerns who quotes rather than who trades on feedback, by \citet{foucault2007}. ")

UNIFORM_REMARK = r'''

\paragraph{What setting a uniform cut from prices requires.} Part~(i) takes the persistence $a$ as known, and that is a restriction on the population: a group with memory zero acts exactly like persistence (Supplement Theorem~\ref{thm:merged}(i)), so knowing $a$ amounts to assuming that every memory exceeds some $\underline r>0$, or to knowing which part of the response at the first lag is feedback. The budget also needs a bound on memory. It is the linear question $g(r)=1/(1-r)$, and by Theorem~\ref{n:questions}(iii) a group with memory close to one and negligible weight can move it at bounded divergence unless memories are bounded by some $\bar r<1$. Under both restrictions the budget is learned at nearly the parametric rate: the taps beyond the first $L$ sum to at most $W\bar r^{L}/(1-\bar r)$, so summing the first $L\approx\log(1/\epsilon)/\log(1/\bar r)$ estimated taps gives the feedback weight $\sum_mk_m$, and with it the budget, to accuracy $\epsilon$ from order $\sigma^2\epsilon^{-2}\log(1/\epsilon)$ experiments. Without the restrictions, the uniform cut inherits part of the composition problem. The instrument must also scale feedback traders while sparing arbitrageurs and dealers. Real instruments, such as transaction taxes, minimum resting times and order-to-trade limits, act with an incidence $\theta(r)$ that varies with the trader's horizon, so their effect on the budget is the linear question with $g(r)=\theta(r)/(1-r)$, whose cost Theorem~\ref{n:questions} gives. An incidence that does not vary with memory gives the budget itself. One that singles out the memories below a cutoff $\hat r$ meets the barrier of Theorem~\ref{n:cost}. Place the moment-matched pair of that theorem, with a common persistence and total merged weight $W$, on $r_c+\Delta\eta[-1,1]$ with $r_c=\hat r+(1+x_K)\Delta\eta/2$, where $x_K<1$ is the largest Gauss node on $[-1,1]$. The Gauss--Radau economy then has an atom of weight $W/K^2$ below $\hat r$, and every memory of the Gauss economy lies above it. A restriction that halts feedback below $\hat r$ removes at least $\kappa W/K^2$ of the budget in one economy and nothing in the other, while the budgets differ by $O((\Delta\eta)^{2K-1})$ and the records are as hard to tell apart as in Theorem~\ref{n:cost}. A restriction by horizon, which needs no tags, is thus a policy for which composition decides whether a ceiling is met.'''

MINIMAX_SENT_OLD = (r"No price record distinguishes labellings (Theorem~\ref{n:suff}), so against the worst labelling "
                    r"consistent with the record, every policy a supervisor can base on prices is weakly dominated by a "
                    r"uniform one.")
MINIMAX_SENT_NEW = (r"Labels do not enter prices, so no record distinguishes labellings; the uniform policy does at least "
                    r"as well as $\theta$ against the worst labelling (it is minimax) and on average over labellings (it "
                    r"is Bayes under an exchangeable prior).")
MINIMAX_MC_OLD = (r"The theorem is machine-checked in full (\nolinkurl{PublicationRevision10.lean}). On 14,400 random "
                  r"economies with three convex losses and three costs, the uniform policy is never worse and is strictly "
                  r"better in 86\% of them (\nolinkurl{minimax/minimax_check.py}).")
MINIMAX_MC_NEW = (r"The theorem is machine-checked in full, for a cost convex on all of $\mathbb R^K$ "
                  r"(\nolinkurl{PublicationRevision10.lean}) or only on $[0,1]^K$ "
                  r"(\nolinkurl{PublicationRevision12.lean}). When $C$ is strictly convex on $[0,1]^K$, the uniform "
                  r"policy strictly dominates every non-uniform one, so the minimax policy is unique and uniform; this "
                  r"is machine-checked in the same file. The argument is the "
                  r"finite-group case of the Hunt--Stein theorem \citep[Chapter~8]{lehmann2005}. Because the law of the "
                  r"record does not depend on the labelling, it applies record by record, so it also covers policies "
                  r"that depend on the record. The comparison with the worst labelling, "
                  r"$\ell(a+\bar\theta U)+C(\bar\theta\mathbf 1)\le\max_\pi\ell(S'_\pi)+C(\theta)$, also holds when "
                  r"$\ell$ and $C$ are only quasi-convex, as is the loss of missing a ceiling: replace Jensen's "
                  r"inequality by $\ell(\sum_\pi\lambda_\pi x_\pi)\le\max_\pi\ell(x_\pi)$. The comparison with the "
                  r"average does not extend, and the quasi-convex case is not machine-checked.")
TAGS_MC_OLD = (r"It is machine-checked in full (\nolinkurl{PublicationRevision11.lean}). On 1,200 random economies with "
               r"random tag partitions, the group-average policy is never worse, and tags have positive value in 27\% of "
               r"them; in the rest the best group policy is uniform, which includes every economy with a single group "
               r"(\nolinkurl{minimax/minimax_tags_check.py}).")
TAGS_MC_NEW = (r"It is machine-checked in full, also for a cost convex only on $[0,1]^K$ "
               r"(\nolinkurl{PublicationRevision11.lean}).")

# The Lean record: PublicationRevision12.lean (22 November 2026) joins the list, and the rows of the two minimax
# theorems name the declarations for a cost convex only on [0,1]^K and for uniqueness.
LEAN_COUNT_OLD = r'eleven Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision11.lean}'
LEAN_COUNT_NEW = r'twelve Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision12.lean}'
LEAN_MINIMAX_ROW_OLD = (r"\texttt{perm\_average\_policy}, \texttt{minimax\_uniform}, \nolinkurl{uniform_budget_label_free}) "
                        r"& none\\")
LEAN_MINIMAX_ROW_NEW = (r"\texttt{perm\_average\_policy}, \texttt{minimax\_uniform}, \nolinkurl{uniform_budget_label_free}), "
                        r"also for a cost convex only on $[0,1]^K$ (\nolinkurl{minimax_uniform_on}); for a strictly "
                        r"convex cost, strict dominance and uniqueness (\nolinkurl{minimax_uniform_strict}, "
                        r"\nolinkurl{minimax_unique}) & none\\")
LEAN_TAGS_ROW_OLD = r"\texttt{tag\_minimax}, \texttt{value\_of\_tags\_nonneg}) & none\\"
LEAN_TAGS_ROW_NEW = (r"\texttt{tag\_minimax}, \texttt{value\_of\_tags\_nonneg}), also for a cost convex only on "
                     r"$[0,1]^K$ (\nolinkurl{tag_minimax_on}) & none\\")

RELABEL_OLD = (r"Third, an audit trail that links accounts to owners keeps its full gain at every $\gamma$, so its "
               r"advantage over class tags is largest where relabeling is cheapest.")
RELABEL_NEW = (RELABEL_OLD + r" This ranking is built in, because the audit trail is assumed not to be gameable. What "
               r"it needs is a stable link from accounts to an owner, which can be pseudonymous: the Consolidated Audit "
               r"Trail, for example, keeps consistent anonymized customer identifiers after the 2025 exemption from "
               r"reporting names, addresses and years of birth \citep{sec2025cat}. Labels that firms assign to their own "
               r"algorithms are the gameable kind. That a principal should rely less on a signal that agents can "
               r"manipulate is close to \citet{frankel2022} and \citet{perezrichet2022}.")

TAIWAN_TAIL = (r"The barrier is this large partly because lagged institutional flow moves prices little "
               r"($\kappa=0.0038$): the three classes together contribute $0.0017$ to a feedback budget of $0.97$.")
TAIWAN_QUAL = r'''

\paragraph{What the calibration shows and what it does not.} Four qualifications apply. First, the targeted range fills the box by construction. Two classes can share one memory with large weights of opposite sign, which leaves the aggregate kernel unchanged, so the range is set by the cap on each class's contribution, not by the data. Weights restricted to one sign would exclude these compositions; we have not computed the range under that restriction. The exact barrier, the relabeling set, does not depend on the cap. Second, the tagged intervals assume that each class's feedback decays at the persistence of its own flow, while the price-only comparisons let feedback memory vary with non-feedback flow held fixed; under the second model, tagged flows carry little information about feedback memory (the $5{,}738$ years above). Third, the uniform cut is fixed by prices only because the supervisor is granted the price persistences $a_j$, the impact $\kappa$ and the non-feedback law, all estimated with the tagged flows. With feedback contributing $0.0017$ to a budget of $0.97$ and memories near $0.35$, separating the two from prices alone is the problem that Proposition~\ref{n:target} assumes away (see the paragraph after it). Fourth, the record lengths treat the 300 stocks as independent, which is generous to prices; the bootstrap resamples dates because they are not independent. Positive feedback in foreign investors' daily flows, and the difficulty of separating it from prices responding to flows, are documented for Taiwan and other markets \citep{froot2001,griffin2004,richards2005}. The dealers' estimated weight is negative, so the calibrated economy lies outside the positive class of Sections~\ref{n:cost_sec}--\ref{n:sup}; the computations here (Whittle rates, Pinsker's inequality, relabeling) do not need positivity.'''

BARRIER_DEF_OLD = (r"The measurement follows \nolinkurl{P1M_measurement_protocol.md}, fixed before the run, on the P1T "
                   r"development period (2013-01-02 to 2016-12-30, designated for exploration; no later date is loaded).")
BARRIER_DEF_NEW = (BARRIER_DEF_OLD + r" The universe is the 300 four-digit stocks with the highest turnover over that "
                   r"period, after the P1T exclusions. For each stock, $x_t$ is the event-adjusted log price minus "
                   r"$\hat\beta$ times the log TAIEX, minus its trailing 60-day mean; it stands in for the model's "
                   r"pricing error, and its persistence partly reflects the detrending. Each class's flow $u_{c,t}$ is "
                   r"its daily net buying of the stock scaled by the stock's average daily volume over the period, so "
                   r"$\kappa$ is the response of $x$ to one day's average volume.")
BARRIER_EQ_OLD = r"intervals use a stationary date-block bootstrap (mean block 20, $B=999$)."
BARRIER_EQ_NEW = (BARRIER_EQ_OLD + r" The price equation has $R^2=0.95$, with first-lag coefficient $0.957$ and "
                  r"$\sum_j\hat a_j=0.972$; with class-specific impacts, a diagnostic, those impacts are $0.0035$ for "
                  r"foreign investors, $0.012$ for investment trusts and $-0.0004$ for dealers.")
BARRIER_RANGE_OLD = (r"For a single stock's record the targeted range is [$-0.028$, $0.028$] and the uniform range "
                     r"[$-0.0020$, $0.0054$].")
BARRIER_RANGE_NEW = (BARRIER_RANGE_OLD + r" The targeted ranges fill the box by construction (main text): the extreme "
                     r"compositions that the search finds pair large weights of opposite sign, and some have negative "
                     r"memories (for the whole panel at the lower end, weights $-9.0$, $4.6$ and $4.7$ at memories "
                     r"$-0.21$, $-0.12$ and $-0.25$).")

HIDEGAME_START = r'A group that expects to be targeted once identified may choose to trade like its neighbours.'
HIDEGAME_END = r'whether an equilibrium exists, and what it looks like, is not studied here.'
HIDEGAME_NEW = r'''A group that expects to be targeted once identified may choose to trade like its neighbours. Consider two untagged groups and let one of them choose the distance $\delta\in(0,\delta_0]$ between its memory and its neighbour's, where $\delta_0$ is the distance of its preferred strategy and moving away from it costs $k(\delta_0-\delta)^2$. A supervisor with $N$ observations tests, with false-alarm probability $\alpha$, the null that the group trades like its neighbour. At leading order its detection probability depends on the data and the distance through $cN\delta^n$, with $n=4$ against the closest economy in the null (Theorem~\ref{n:paradox}); write it $P_{\rm d}(cN\delta^n)$, with $P_{\rm d}$ continuous and nondecreasing and $P_{\rm d}(0)\le\alpha$. Detection costs the group $L>0$. Tags, if the supervisor imposes them, make the group's weight identifiable at a cost that does not depend on $\delta$ (Theorem~\ref{thm:partial}).

\begin{proposition}[Surveillance and hiding]\label{prop:hidegame}
Let $\delta^*(N)$ minimize $k(\delta_0-\delta)^2+LP_{\rm d}(cN\delta^n)$ over $(0,\delta_0]$, with $n>0$.
\begin{enumerate}[label=(\roman*),itemsep=1pt]
\item \emph{Crowding.} If $P_{\rm d}$ is differentiable at $cN\delta_0^n$ with positive derivative, then $\delta^*(N)<\delta_0$.
\item \emph{Surveillance without tags is self-limiting.} $\limsup_{N\to\infty}P_{\rm d}(cN\delta^*(N)^n)\le\alpha+k\delta_0^2/L$. When the stakes are high, $L\gg k\delta_0^2$, the group is detected about as often as a false alarm, however much data the supervisor has.
\item \emph{Tags remove crowding.} If the detection probability does not depend on $\delta$, then $\delta^*=\delta_0$.
\item \emph{Many groups.} Let $M\ge2$ untagged groups choose memory positions $p_g$, group $g$ paying $k_g(p_g-p^\circ_g)^2+L_gP_{\rm d}(cN\delta_g^n)$, where $p^\circ_g$ is its preferred position and $\delta_g$ its distance to the nearest other group. In every Nash equilibrium (existence is not established here) in which the distance $\Delta_g$ from $p^\circ_g$ to the nearest other group's position stays bounded as $N$ grows, $\limsup_{N\to\infty}P_{\rm d}(cN\delta_g^n)\le\alpha+k_g\limsup_N\Delta_g^2/L_g$ for every group.
\end{enumerate}
\end{proposition}

\begin{proof}
(i) The derivative of the objective at $\delta_0$ is $ncLN\delta_0^{n-1}P_{\rm d}'(cN\delta_0^n)>0$, so a small move below $\delta_0$ lowers it. (ii) For any $b>0$ and $N$ large enough that $b(cN)^{-1/n}\le\delta_0$, optimality against $\delta=b(cN)^{-1/n}$ gives $LP_{\rm d}(cN\delta^{*n})\le k(\delta_0-b(cN)^{-1/n})^2+LP_{\rm d}(b^n)\le k\delta_0^2+LP_{\rm d}(b^n)$. Letting $b\to0$ and using continuity of $P_{\rm d}$ at zero gives the bound. (iii) The cost $k(\delta_0-\delta)^2$ is minimized at $\delta_0$. (iv) Holding the others' positions fixed, group $g$ can move to within $b(cN)^{-1/n}$ of its nearest neighbour, at cost at most $k_g(\Delta_g+b(cN)^{-1/n})^2$ and detection probability at most $P_{\rm d}(b^n)$, because $P_{\rm d}$ is nondecreasing. Equilibrium gives $L_gP_{\rm d}(cN\delta_g^n)\le k_g(\Delta_g+b(cN)^{-1/n})^2+L_gP_{\rm d}(b^n)$; letting $N\to\infty$ and then $b\to0$ gives the bound.
\end{proof}

The proposition gives the paper's results on cost a strategic reading. More data without tags make high-stakes algorithms trade alike, and so make composition harder to learn, while the detection probability stays near the false-alarm level. Tags undo the crowding. Two predictions follow that algorithm-level data could test: where algorithm identification is introduced, the dispersion of memory rates across algorithm classes should rise; and in untagged markets, the memories of strategies with the most to lose from targeting should converge as surveillance improves. With the Gaussian test and $n=4$, the optimal distance in the high-stakes case falls like $N^{-1/2}$ and detection stays at the $5\%$ false-alarm level up to $N=10^{14}$; when detection costs less than moving, $L(1-\alpha)<k\delta_0^2$, the group hides for moderate $N$ and stops hiding once data are plentiful (\nolinkurl{paradox/paradox_check.py}). With several groups, part (iv) bounds detection group by group in every equilibrium; whether an equilibrium exists, and what it looks like, is not studied here.'''

NEARCRIT_STMT_OLD = (r"Fix $K\ge2$ and the $K$-group Gauss and Gauss--Radau economies $A$ and $B$ of Theorem~\ref{thm:kcohort}, "
                     r"with positive weights, rates in $(0,1)$ and $\kappa>0$. For a margin $\epsilon>0$, choose "
                     r"persistences $a_A(\epsilon)$ and $a_B(\epsilon)$ so that both economies have feedback budget "
                     r"$S=1-\epsilon$, and suppose $a_A(\epsilon),a_B(\epsilon)>0$ for $\epsilon\le\epsilon_0$.")
NEARCRIT_STMT_NEW = (r"Fix $K\ge2$ and the $K$-group Gauss and Gauss--Radau economies $A$ and $B$ of "
                     r"Theorem~\ref{thm:kcohort}, with positive weights, rates in $(0,1)$, $\kappa>0$ and a common "
                     r"persistence. Rescale the weights of $B$ by the factor $1+c$ that gives both economies the same "
                     r"feedback budget; $c$ is of order $(\Delta\eta)^{2K-1}$, so the largest weights of the two economies "
                     r"still differ by a fixed fraction of the total. For a margin $\epsilon>0$, let $a(\epsilon)$ be the "
                     r"common persistence at which both economies have feedback budget $S=1-\epsilon$, and suppose "
                     r"$a(\epsilon)>0$ for $\epsilon\le\epsilon_0$.")
NEARCRIT_WORDS_OLD = (r"They reveal more and more about how close the market is to instability: if the two economies share "
                      r"the persistence $a$ instead of the budget, their budgets differ by order $(\Delta\eta)^{2K-1}$, and "
                      r"numerically the divergence rate then grows like $\epsilon^{-1}$.")
NEARCRIT_WORDS_NEW = (r"They reveal more and more about how close the market is to instability: without the rescaling, "
                      r"the two economies' budgets differ by order $(\Delta\eta)^{2K-1}$, and numerically the divergence "
                      r"rate then grows roughly like $\epsilon^{-1}$ until the margin reaches that gap, and levels off.")
NEARCRIT_MAIN_OLD = (r"The barrier does not lift near instability. At a common feedback budget $S=1-\epsilon$ the passive "
                     r"information per observation between the pair of Theorem~\ref{n:cost}(i) is at most "
                     r"$C(\Delta\eta)^{4K-2}$, with $C$ independent of $\epsilon$")
NEARCRIT_MAIN_NEW = (r"The barrier does not lift near instability. Give the pair of Theorem~\ref{n:cost}(i) a common "
                     r"persistence and, by rescaling one economy's weights by a factor $1+O((\Delta\eta)^{2K-1})$, a common "
                     r"feedback budget $S=1-\epsilon$. Their passive information per observation is then at most "
                     r"$C(\Delta\eta)^{4K-2}$, with $C$ independent of $\epsilon$")
CAPTION_A_OLD = r"(a)~At a common feedback budget one millionth below instability"
CAPTION_A_NEW = r"(a)~At a common persistence and a common feedback budget one millionth below instability"
CAPTION_B_OLD = (r"(b)~Held at a common budget (solid), the information stays bounded as the margin $1-S$ shrinks; held "
                 r"at a common persistence (dashed), it grows without bound, because the budgets then differ.")
CAPTION_B_NEW = (r"(b)~With a common persistence and a common budget (solid; the Gauss--Radau weights rescaled by a factor "
                 r"$1+O((\Delta\eta)^{2K-1})$), the information stays bounded as the margin $1-S$ shrinks. With a common "
                 r"persistence and no rescaling (dashed), the budgets differ by order $(\Delta\eta)^{2K-1}$; the "
                 r"information then grows roughly like $(1-S)^{-1}$ until the margin reaches that gap, and levels off.")
PROOF_SETUP_OLD = (r"Write $D_X(z)=z-a_X-\kappa G_X(z)$ for economy $X$, so that $H_X=\kappa z/D_X$ and the stationary "
                   r"price spectrum is $f_X(\omega)=\sigma^2\kappa^2/|D_X(e^{i\omega})|^2$. Because both economies have "
                   r"budget $1-\epsilon$, $D_A(1)=D_B(1)=\epsilon$.")
PROOF_SETUP_NEW = (r"Write $D_X(z)=z-a-\kappa G_X(z)$ for economy $X$, so that $H_X=\kappa z/D_X$ and the stationary "
                   r"price spectrum is $f_X(\omega)=\sigma^2\kappa^2/|D_X(e^{i\omega})|^2$. Because both economies have "
                   r"budget $1-\epsilon$ and the same persistence, $D_A(1)=D_B(1)=\epsilon$ and $G_A(1)=G_B(1)$.")
PROOF_STEP1_START = r"\emph{Step 1: the difference vanishes at zero frequency.}"
PROOF_STEP1_END = r"Hence $|\Delta(e^{i\omega})|\le\kappa C_1(\Delta\eta)^{2K-1}|\omega|$."
PROOF_STEP1_NEW = (r"\emph{Step 1: the difference vanishes at zero frequency.} With $E=G_B-G_A$, "
                   r"$\Delta(z)\equiv D_B(z)-D_A(z)=-\kappa E(z)=-\kappa\,(E(z)-E(1))$, because the common budget gives "
                   r"$E(1)=0$; $\Delta$ does not depend on $\epsilon$. Write $E(z)=\sum_me_mz^{-m}$ with "
                   r"$e_m=k^B_m-k^A_m$. Then $|E(e^{i\omega})-E(1)|\le|\omega|\sum_mm|e_m|$. The rates are "
                   r"$r_c+\Delta\eta\,s$. Expanding $(r_c+\Delta\eta\,s)^m$ and $(1-r_c-\Delta\eta\,s)^{-1}$ in powers of "
                   r"$\Delta\eta$, the moments of order up to $2K-2$ of the two normalized rules cancel, so the rescaling "
                   r"factor satisfies $|c|\le C_0(\Delta\eta)^{2K-1}$ and "
                   r"$|e_m|\le2W\sum_{j\ge2K-1}\binom mj r_c^{m-j}(\Delta\eta)^j+|c|W(r_c+\Delta\eta)^m$. Summing, "
                   r"$\sum_mm|e_m|\le C_1(\Delta\eta)^{2K-1}$, with $C_1$ depending on $K,W,r_c$ and a bound on "
                   r"$\Delta\eta$. Hence $|\Delta(e^{i\omega})|\le\kappa C_1(\Delta\eta)^{2K-1}|\omega|$.")
PROOF_ASTAR_OLD = r"Let $a^*=\lim_{\epsilon\to0}a_A(\epsilon)$"
PROOF_ASTAR_NEW = r"Let $a^*=\lim_{\epsilon\to0}a(\epsilon)$"
PROOF_STEP3_OLD = r"while $|\Delta|\le|a_B-a_A|+\kappa|E(e^{i\omega})|=O((\Delta\eta)^{2K-1})$;"
PROOF_STEP3_NEW = r"while $|\Delta|=\kappa|E(e^{i\omega})|=O((\Delta\eta)^{2K-1})$;"
NUMCHECK_START = r"\paragraph{Numerical check.} For $K=2,3$, $\Delta\eta\in\{0.1,0.05,0.025\}$"
NUMCHECK_END = r"which is the budget difference becoming visible."
FINITE_START = r"Numerically, the exact divergence of $n$ consecutive stationary observations lies between $97.8\%$"
FINITE_END = r"and the divergence is below the bound (Supplement Section~\ref{app:verification}, \nolinkurl{reproduce.py})."

TABLE_FOOT_OLD = (r"computed as in Figure~\ref{n:fig_barrier}, at a common feedback budget $S$, impact $\kappa=0.5$ and "
                  r"feedback share $\kappa\sum_iq_i=0.3$ (total weight $0.6(1-r_c)$ at centre rate $r_c$).")
TABLE_FOOT_NEW = (r"computed as in Figure~\ref{n:fig_barrier}, at a common persistence and a common feedback budget $S$ "
                  r"(the Gauss--Radau weights rescaled to match the budget), impact $\kappa=0.5$ and feedback share "
                  r"$\kappa\sum_iq_i=0.3$ (total weight $0.6(1-r_c)$ of the Gauss economy at centre rate $r_c$).")
TABLE_FOOT_END_OLD = r"divide by $417$. Two significant digits.}"
TABLE_FOOT_END_NEW = (r"divide by $417$. With non-Gaussian news the bounds can be smaller, by at most the factor "
                      r"$\sigma^2I^*_f$ of Theorem~\ref{n:cost} ($2$ for Laplace news), which can be large for "
                      r"heavy-tailed news. Two significant digits.}")

RELATED = (r"\paragraph{Related manuscripts.} This article grows out of \citet{niroula2026a}, an earlier working paper "
           r"of the same authors on the same model. It cites that paper only for results not reproduced here: "
           r"simulations, test reports, the account-level cost of probing, an upper bound for the memory distribution "
           r"and the rate for completely monotone memory. \citet{niroula2026c} collects companion results on breaches "
           r"and nonlinear rules.")

PLAIN = [
    # Theorem n:dual: what Lean checks
    (r"the theorem is machine-checked end to end (\nolinkurl{dual_end_to_end},",
     r"the algebra of the theorem is machine-checked (\nolinkurl{dual_end_to_end},"),
    # Remark: unobserved fundamentals
    (r"handles unknown primitives under active reset probes).",
     r"handles unknown primitives under active reset probes). The positive results, identification and the upper "
     r"bounds, assume that the pricing error is observed."),
    # Theorem n:thm_inventory(iv)
    (r"\item \emph{Small feedback.} For small feedback intensity $G(1)=\sum_i q_i$, there exists a unique equilibrium "
     r"near $(\kappa_-,1)$ with",
     r"\item \emph{Small feedback.} Let $\Delta>0$, fix $\delta>0$ with $\max_ir_i<1-\delta$, and suppose "
     r"$\epsilon=\sup_{|D-1|\le\delta}(|G(D)|+|G'(D)|)$ is small. Then there exists a unique equilibrium near "
     r"$(\kappa_-,1)$, and with the feedback intensity $G(1)=\sum_i q_i$,"),
    # Theorem n:thm_eqreduced(iv): the observation contract
    (r"require $N\ge c\,\sigma^2(\Delta\eta)^{-(4K-2)}$ observations to be distinguished.",
     r"require $N\ge c\,\sigma^2(\Delta\eta)^{-(4K-2)}$ reset experiments to be distinguished, each recording the "
     r"equilibrium price response to a probe with Gaussian noise of variance $\sigma^2$."),
    # Theorem n:questions: attribution
    (r"This is Supplement Theorem~\ref{thm:questions} and Proposition~\ref{prop:parametric}, adapted from the first "
     r"author's thesis;",
     r"This is Supplement Theorem~\ref{thm:questions} and Proposition~\ref{prop:parametric}, proved in full in the "
     r"supplement;"),
    (r"The results and proofs are adapted from the first author's thesis (in preparation).",
     r"The results also appear in the first author's thesis (in preparation); the proofs below are complete."),
    # Theorem n:shape: computability
    (r"Its constants can deteriorate as $\gamma$ or $\omega_{\min}$ tends to zero.",
     r"Its constants can deteriorate as $\gamma$ or $\omega_{\min}$ tends to zero. The estimator is an exact global "
     r"minimizer over $\mathcal Z$, which is not convex, and the theorem gives no algorithm that finds it."),
    # completely monotone memory
    (r"prove that the minimax accuracy for the memory distribution is of exact order $1/\log(N/\sigma^2)$.",
     r"prove that the minimax accuracy for the memory distribution is of exact order $1/\log(N/\sigma^2)$. This is the "
     r"severe ill-posedness of inverting a Laplace transform \citep{epstein2008}."),
    # How large is the barrier: Table 1 recomputed for the admissible pair
    (r"some pairs require more than $4{,}000$ calendar years", r"some pairs require more than $11{,}000$ calendar years"),
    # revision-history wording
    (r"are new in this revision:", r"were written in November 2026:"),
    (r"It has not begun on this revision's date.", r"It had not begun on 21 November 2026."),
    (r"Candidate repairs and tests accompany this revision;", r"Candidate repairs and tests are in the repository;"),
    (r"\caption{What is machine-checked in the results new in this revision.}",
     r"\caption{Machine-checked steps of the results listed.}"),
    (r"\paragraph{Recomputed numerical checks for this revision.}", r"\paragraph{Numerical checks.}"),
    (r"recorded in this revision package.", r"recorded in the repository."),
    (r"in the revision package.}\label{tab:revisionnumerics}", r"in the repository.}\label{tab:revisionnumerics}"),
    (r"Additional regression tests in the revision package check", r"Additional regression tests in the repository check"),
    (r"This section supplies the corrected proofs of", r"This section supplies the proofs of"),
    (r"Earlier versions of this table did not cite 24 modules of the project that check results stated here. Each was "
     r"compared with the statement it checks, and the rows below now list them with every difference of scope.",
     r"The table also cites 24 further modules that check results stated here; each was compared with the statement it "
     r"checks, and the rows list every difference of scope."),
    (r"The incoming optimizer simulation starts at the true parameter",
     r"The optimizer simulation in the repository starts at the true parameter"),
    (r"The incoming simulation evaluates 64 pair-and-probe combinations",
     r"The repository simulation evaluates 64 pair-and-probe combinations"),
    (r"Three questions were open in earlier versions, and the supplement answers each in part.",
     r"Three further questions are answered in part in the companion paper \citep{niroula2026c}."),
    (r"\paragraph{Open problems.} Supplement Section~\ref{app:openres} settles several earlier open questions:",
     r"\paragraph{Open problems.} The companion paper \citep{niroula2026c} answers several further questions:"),
    (r"Supplement Section~\ref{app:openres} also gives forward-looking dealers", r"It also gives forward-looking dealers"),
    (r"\paragraph{Moved from the main text.} The proposition below and its discussion were in the main text of earlier "
     r"versions." + "\n\n", ""),
    (r"\paragraph{Moved from the main text.} The statements below were in the main text of earlier versions." + "\n\n", ""),
    # the description of the surveillance section
    (r"and an equilibrium in which surveillance without tags pushes algorithms together and never detects them.",
     r"and a bound on detection in any equilibrium in which surveillance without tags pushes algorithms together."),
]

LEMMA_ANCHOR = (r"\item There are $c_1\ne c_2$ in $[-c_0,c_0]$ for which $R_{c_1}$ and $R_{c_2}$ have different largest "
                r"weights. Their moments of degree $2K-1$ differ." + "\n" + r"\end{enumerate}" + "\n" + r"\end{lemma}" + "\n")
LEMMA_CITE = (r"Parts (i) and (ii) are classical: the weights are the Christoffel numbers of $\mu$, and $p_K-c\,p_{K-1}$ "
              r"is a quasi-orthogonal polynomial \citep{szego1975,gautschi2004}. We include the short proofs." + "\n")

NEW_BIB = r'''
\bibitem[Bond and Goldstein(2015)]{bond2015} Bond, P., and I. Goldstein (2015). Government intervention and information aggregation by prices. \emph{Journal of Finance} 70(6), 2777--2812.

\bibitem[Bond et~al.(2010)]{bond2010} Bond, P., I. Goldstein, and E.~S. Prescott (2010). Market-based corrective actions. \emph{Review of Financial Studies} 23(2), 781--820.

\bibitem[Chaboud et~al.(2014)]{chaboud2014} Chaboud, A.~P., B. Chiquoine, E. Hjalmarsson, and C. Vega (2014). Rise of the machines: Algorithmic trading in the foreign exchange market. \emph{Journal of Finance} 69(5), 2045--2084.

\bibitem[Chetty(2009)]{chetty2009} Chetty, R. (2009). Sufficient statistics for welfare analysis: A bridge between structural and reduced-form methods. \emph{Annual Review of Economics} 1, 451--488.

\bibitem[Cutler et~al.(1990)]{cutler1990} Cutler, D.~M., J.~M. Poterba, and L.~H. Summers (1990). Speculative dynamics and the role of feedback traders. \emph{American Economic Review} 80(2), 63--68.

\bibitem[De~Long et~al.(1990)]{delong1990} De~Long, J.~B., A. Shleifer, L.~H. Summers, and R.~J. Waldmann (1990). Positive feedback investment strategies and destabilizing rational speculation. \emph{Journal of Finance} 45(2), 379--395.

\bibitem[Epstein and Schotland(2008)]{epstein2008} Epstein, C.~L., and J. Schotland (2008). The bad truth about Laplace's transform. \emph{SIAM Review} 50(3), 504--520.

\bibitem[Foucault et~al.(2007)]{foucault2007} Foucault, T., S. Moinas, and E. Theissen (2007). Does anonymity matter in electronic limit order markets? \emph{Review of Financial Studies} 20(5), 1707--1747.

\bibitem[Frankel and Kartik(2019)]{frankel2019} Frankel, A., and N. Kartik (2019). Muddled information. \emph{Journal of Political Economy} 127(4), 1739--1776.

\bibitem[Frankel and Kartik(2022)]{frankel2022} Frankel, A., and N. Kartik (2022). Improving information from manipulable data. \emph{Journal of the European Economic Association} 20(1), 79--115.

\bibitem[Froot et~al.(2001)]{froot2001} Froot, K.~A., P.~G.~J. O'Connell, and M.~S. Seasholes (2001). The portfolio flows of international investors. \emph{Journal of Financial Economics} 59(2), 151--193.

\bibitem[Gautschi(2004)]{gautschi2004} Gautschi, W. (2004). \emph{Orthogonal Polynomials: Computation and Approximation}. Oxford University Press, Oxford.

\bibitem[Grazzini and Richiardi(2015)]{grazzini2015} Grazzini, J., and M. Richiardi (2015). Estimation of ergodic agent-based models by simulated minimum distance. \emph{Journal of Economic Dynamics and Control} 51, 148--165.

\bibitem[Griffin et~al.(2004)]{griffin2004} Griffin, J.~M., F. Nardari, and R.~M. Stulz (2004). Are daily cross-border equity flows pushed or pulled? \emph{Review of Economics and Statistics} 86(3), 641--657.

\bibitem[Grossman and Miller(1988)]{grossman1988} Grossman, S.~J., and M.~H. Miller (1988). Liquidity and market structure. \emph{Journal of Finance} 43(3), 617--633.

\bibitem[Hendershott and Menkveld(2014)]{hendershott2014} Hendershott, T., and A.~J. Menkveld (2014). Price pressures. \emph{Journal of Financial Economics} 114(3), 405--423.

\bibitem[Ho and Stoll(1981)]{ho1981} Ho, T., and H.~R. Stoll (1981). Optimal dealer pricing under transactions and return uncertainty. \emph{Journal of Financial Economics} 9(1), 47--73.

\bibitem[Khandani and Lo(2011)]{khandani2011} Khandani, A.~E., and A.~W. Lo (2011). What happened to the quants in August 2007? Evidence from factors and transactions data. \emph{Journal of Financial Markets} 14(1), 1--46.

\bibitem[Lehmann and Romano(2005)]{lehmann2005} Lehmann, E.~L., and J.~P. Romano (2005). \emph{Testing Statistical Hypotheses}, 3rd ed. Springer, New York.

\bibitem[Marschak(1953)]{marschak1953} Marschak, J. (1953). Economic measurements for policy and prediction. In W.~C. Hood and T.~C. Koopmans (Eds.), \emph{Studies in Econometric Method}, Cowles Commission Monograph 14, 1--26. Wiley, New York.

\bibitem[Manski(2000)]{manski2000} Manski, C.~F. (2000). Identification problems and decisions under ambiguity: Empirical analysis of treatment response and normative analysis of treatment choice. \emph{Journal of Econometrics} 95(2), 415--442.

\bibitem[Rothenberg(1971)]{rothenberg1971} Rothenberg, T.~J. (1971). Identification in parametric models. \emph{Econometrica} 39(3), 577--591.

\bibitem[Perez-Richet and Skreta(2022)]{perezrichet2022} Perez-Richet, E., and V. Skreta (2022). Test design under falsification. \emph{Econometrica} 90(3), 1109--1142.

\bibitem[Platt(2020)]{platt2020} Platt, D. (2020). A comparison of economic agent-based model calibration methods. \emph{Journal of Economic Dynamics and Control} 113, 103859.

\bibitem[Richards(2005)]{richards2005} Richards, A. (2005). Big fish in small ponds: The trading behavior and price impact of foreign investors in Asian emerging equity markets. \emph{Journal of Financial and Quantitative Analysis} 40(1), 1--27.

\bibitem[Securities and Exchange Commission(2025)]{sec2025cat} Securities and Exchange Commission (2025). Press release 2025-38, 10 February 2025: exemption from reporting the names, addresses and years of birth of natural persons to the Consolidated Audit Trail. \url{https://www.sec.gov/newsroom/press-releases/2025-38}.

\bibitem[Sentana and Wadhwani(1992)]{sentana1992} Sentana, E., and S. Wadhwani (1992). Feedback traders and stock return autocorrelations: Evidence from a century of daily data. \emph{Economic Journal} 102(411), 415--425.

\bibitem[Stein(2009)]{stein2009} Stein, J.~C. (2009). Presidential address: Sophisticated investors and market efficiency. \emph{Journal of Finance} 64(4), 1517--1548.
'''


def _sig2(x):
    """Two significant digits in the table's style: 20{,}000 below a million, a\\times10^{k} above."""
    from math import floor, log10
    e = floor(log10(abs(x)))
    m = round(x / 10 ** e, 1)
    if m >= 10:
        m, e = m / 10, e + 1
    if e >= 6:
        return r'$%.1f\times10^{%d}$' % (m, e)
    v = int(round(m * 10 ** e)) if e >= 1 else m * 10 ** e
    s = f'{v:,}'.replace(',', '{,}')
    return s


def _table_rows():
    rows = json.loads(NEARCRIT.read_text())['table']
    half = {(0.5, 0.1): '0.8--1.4', (0.5, 0.05): '0.9--1.2', (0.8, 0.1): '1.9--6.6', (0.8, 0.05): '2.4--4.3',
            (0.9, 0.05): '4.3--13.5', (0.9, 0.025): '5.2--8.9'}
    out = []
    for i, r in enumerate(rows):
        lead = ('$K=%d$' % r['K']) if (i == 0 or rows[i - 1]['K'] != r['K']) else ''
        if i > 0 and rows[i - 1]['K'] != r['K']:
            out.append(r'\midrule')
        spacing = ('%g' % r['spacing'])
        out.append(r'%s & $%g\pm%s$ & %s & %s & %s\\' % (lead, r['rc'], spacing, half[(r['rc'], r['spacing'])],
                                                       _sig2(r['years_0.1']), _sig2(r['years_1e-06'])))
    return '\n'.join(out)


def _nearcrit_numcheck():
    d = json.loads(NEARCRIT.read_text())
    uni = d['uniform_check']
    lim = {K: [r['scaled'] for r in uni[K] if r['margin'] == 1e-6] for K in ('2', '3')}
    c2 = [r['c'] for r in uni['2'] if r['spacing'] == 0.1][0]
    c3 = [r['c'] for r in uni['3'] if r['spacing'] == 0.1][0]
    g2 = d['figure']['panel_b']['2']['budget_gap_unrescaled']
    g3 = d['figure']['panel_b']['3']['budget_gap_unrescaled']

    def sci(x):
        e = int(__import__('math').floor(__import__('math').log10(abs(x))))
        return r'%.1f\times10^{%d}' % (abs(x) / 10 ** e, e)
    return (r"\paragraph{Numerical check.} For $K=2,3$, $\Delta\eta\in\{0.1,0.05,0.025\}$ and margins from $10^{-1}$ to "
            r"$10^{-6}$, the ratio $D_\epsilon(B\|A)/(\Delta\eta)^{4K-2}$ increases to a finite limit as $\epsilon\to0$ "
            r"($%.2f$ to $%.2f$ for $K=2$, $%.2f$ to $%.2f$ for $K=3$; \nolinkurl{nearcrit_admissible.py}). At "
            r"$\Delta\eta=0.1$ the rescaling factor is $1+c$ with $c=%s$ for $K=2$ and $c=%s$ for $K=3$. Without the "
            r"rescaling the budgets differ by $%s$ and $%s$; the divergence rate then grows roughly like "
            r"$\epsilon^{-1}$ until $\epsilon$ reaches that gap, and levels off, which is the budget difference "
            r"becoming visible."
            % (min(lim['2']), max(lim['2']), min(lim['3']), max(lim['3']), sci(c2), sci(c3), sci(g2), sci(g3)))


def _nearcrit_finite():
    d = json.loads(NEARCRIT.read_text())
    fs = d['finite_sample']
    lo, hi = min(r['ratio'] for r in fs), max(r['ratio'] for r in fs)
    s = (r"Numerically, the exact divergence of $n$ consecutive stationary observations lies between $%.1f\%%$ and "
         r"$%.1f\%%$ of $n$ times the per-observation rate for $K=2$, $\Delta\eta\in\{0.1,0.2\}$, "
         r"$\epsilon\in\{10^{-1},10^{-2},10^{-3}\}$ and $n\in\{250,1000,4000\}$ (\nolinkurl{nearcrit_admissible.py})."
         % (100 * lo, 100 * hi))
    band = d.get('finite_sample_band')
    if band and all(b['in_band'] and b['below_bound'] for b in band):
        s += (r" In every such case all eigenvalues lie in the band of the proof, and the divergence is below the "
              r"bound.")
    return s


def tidy_bib(t):
    """Keep only cited references and sort them by their author-year label."""
    a = t.index(r'\begin{thebibliography}')
    head_end = t.index('\n', a) + 1
    b = t.index(r'\end{thebibliography}')
    body = t[head_end:b]
    starts = [m.start() for m in re.finditer(r'\\bibitem\[', body)]
    assert starts, 'no bibitems'
    pre = body[:starts[0]].strip()
    assert not pre, ('text before the first bibitem', pre[:80])
    items = [body[s:e].strip() for s, e in zip(starts, starts[1:] + [len(body)])]
    text = t[:a] + t[b:]
    cited = set()
    for m in re.finditer(r'\\(?:cite[a-zA-Z]*|nocite)\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}', text):
        cited.update(k.strip() for k in m.group(1).split(','))
    keep, dropped = [], []
    for it in items:
        m = re.match(r'\\bibitem\[([^\]]*)\]\{([^}]*)\}', it.strip())
        assert m, it[:80]
        (keep if m.group(2) in cited else dropped).append((m.group(1), m.group(2), it.strip()))

    def key(entry):
        label = entry[0]
        label = re.sub(r'\\[a-zA-Z]+\s*', '', label).replace('{', '').replace('}', '').replace('~', ' ')
        label = label.replace('\\"', '').replace('\\H', '').replace("\\'", '')
        return label.lower()
    keep.sort(key=key)
    missing = cited - {k for _, k, _ in keep}
    assert not missing, ('cited but not in the bibliography', sorted(missing))
    new_body = '\n\n'.join(it for _, _, it in keep) + '\n'
    return t[:head_end] + new_body + t[b:], [k for _, k, _ in dropped]


def apply(t):
    t = re.sub(r"(\\begin\{abstract\}\n\\noindent ).*?(\n\\end\{abstract\})",
               lambda m: m.group(1) + ABSTRACT + m.group(2), t, count=1, flags=re.S)
    t = _rep(t, WHATSNEW_OLD, WHATSNEW_NEW)
    t = _rep(t, r'We do not claim these.', LIT_ADD + r'We do not claim these.')
    anchor = (r"Part~(ii) is Supplement Proposition~\ref{prop:targetK}; its pair comes from a family of quadrature rules "
              r"whose weights are the values of one function at their nodes (Supplement Lemma~\ref{lem:everyK}).")
    t = _rep(t, anchor, anchor + UNIFORM_REMARK)
    t = _rep(t, MINIMAX_SENT_OLD, MINIMAX_SENT_NEW)
    t = _rep(t, MINIMAX_MC_OLD, MINIMAX_MC_NEW)
    t = _rep(t, TAGS_MC_OLD, TAGS_MC_NEW)
    # the registered tests, described as what they show and where they are recorded
    t = _rep(t, r"The registered test is supportive, but its pre-specified diagnostic attributes the gain to reverse "
                r"causality.",
             r"The registered test is supportive, but its pre-specified diagnostic cannot separate the gain from "
             r"prices revealing past flow.")
    t = _rep(t, r"A prospective replication protocol on Binance perpetual futures is pre-specified with fixed "
                r"development thresholds (August to October 2026) serving as an externally locked template for "
                r"subsequent window observation.",
             r"A prospective replication on Binance perpetual futures fixes its thresholds on a development window "
             r"(August to October 2026); its protocol and development outputs were recorded with hashes in the "
             r"authors' public repository before the evaluation window opened on 16 November 2026.")
    assert t.count(LEAN_COUNT_OLD) >= 1, 'Lean file count not found'
    t = t.replace(LEAN_COUNT_OLD, LEAN_COUNT_NEW)
    t = _rep(t, LEAN_MINIMAX_ROW_OLD, LEAN_MINIMAX_ROW_NEW)
    t = _rep(t, LEAN_TAGS_ROW_OLD, LEAN_TAGS_ROW_NEW)
    # labellings are pi, not sigma (sigma is a noise level throughout)
    a = t.index(r'\begin{theorem}[Without tags, uniform policies are minimax]')
    b = t.index(r'This is the decision-theoretic counterpart of Theorem~\ref{n:disc}', a)
    span = t[a:b]
    assert span.count(r'\sigma') >= 8 and r'\sigma^2' not in span and r'\sigma_' not in span, span.count(r'\sigma')
    t = t[:a] + span.replace(r'\sigma', r'\pi') + t[b:]
    t = _rep(t, RELABEL_OLD, RELABEL_NEW)
    t = _rep(t, TAIWAN_TAIL, TAIWAN_TAIL + TAIWAN_QUAL)
    t = _rep(t, BARRIER_DEF_OLD, BARRIER_DEF_NEW)
    t = _rep(t, BARRIER_EQ_OLD, BARRIER_EQ_NEW)
    t = _rep(t, BARRIER_RANGE_OLD, BARRIER_RANGE_NEW)
    a = t.index(HIDEGAME_START)
    b = t.index(HIDEGAME_END, a) + len(HIDEGAME_END)
    assert b - a < 6000
    t = t[:a] + HIDEGAME_NEW + t[b:]
    # near instability: an admissible pair
    t = _rep(t, NEARCRIT_STMT_OLD, NEARCRIT_STMT_NEW)
    t = _rep(t, NEARCRIT_WORDS_OLD, NEARCRIT_WORDS_NEW)
    t = _rep(t, NEARCRIT_MAIN_OLD, NEARCRIT_MAIN_NEW)
    t = _rep(t, CAPTION_A_OLD, CAPTION_A_NEW, count=2)
    t = _rep(t, CAPTION_B_OLD, CAPTION_B_NEW, count=2)
    t = _rep(t, r'\includegraphics[width=\textwidth]{fig_barrier.pdf}',
             r'\includegraphics[width=\textwidth]{fig_barrier_admissible.pdf}', count=2)
    d = json.loads(NEARCRIT.read_text())
    t = _rep(t, r'numerically the exact information in $n$ observations stays within $3\%$ below $n$ times the rate',
             r'numerically the exact information in $n$ observations stays within $%.0f\%%$ below $n$ times the rate'
             % (100 * (1 - min(r['ratio'] for r in d['finite_sample']))))
    act = d.get('active_probing')
    old_act = r'the squared response difference grows like $\epsilon^{-1}$ (numerical)'
    if act:
        e2, e3 = act['2']['exponent_last4'], act['3']['exponent_last4']
        t = _rep(t, old_act, r'the squared response difference grows like $\epsilon^{-1}$ (fitted exponents $%.2f$ for '
                             r'$K=2$ and $%.2f$ for $K=3$; \nolinkurl{nearcrit_admissible.py})' % (e2, e3))
    t = _rep(t, PROOF_SETUP_OLD, PROOF_SETUP_NEW)
    a = t.index(PROOF_STEP1_START)
    b = t.index(PROOF_STEP1_END, a) + len(PROOF_STEP1_END)
    t = t[:a] + PROOF_STEP1_NEW + t[b:]
    t = _rep(t, PROOF_ASTAR_OLD, PROOF_ASTAR_NEW)
    t = _rep(t, PROOF_STEP3_OLD, PROOF_STEP3_NEW)
    a = t.index(NUMCHECK_START)
    b = t.index(NUMCHECK_END, a) + len(NUMCHECK_END)
    t = t[:a] + _nearcrit_numcheck() + t[b:]
    a = t.index(FINITE_START)
    b = t.index(FINITE_END, a) + len(FINITE_END)
    t = t[:a] + _nearcrit_finite() + t[b:]
    # Table 1, recomputed for the admissible pair
    a = t.index(r'$K=2$ & $0.5\pm0.1$ & 0.8--1.4 &')
    b = t.index(r'\bottomrule', a)
    t = t[:a] + _table_rows() + '\n' + t[b:]
    t = _rep(t, TABLE_FOOT_OLD, TABLE_FOOT_NEW)
    t = _rep(t, TABLE_FOOT_END_OLD, TABLE_FOOT_END_NEW)
    for old, new in PLAIN:
        t = _rep(t, old, new)
    t = _rep(t, r'+o(G(1))', r'+o(\epsilon)', count=2)
    t = _rep(t, LEMMA_ANCHOR, LEMMA_ANCHOR + '\n' + LEMMA_CITE)
    # numerical-check references: the repository script, not the Lean table
    t = t.replace(r'Supplement Section~\ref{app:verification}, \nolinkurl{reproduce.py}',
                  r'repository script \nolinkurl{reproduce.py}')
    t = _rep(t, r'((repository script \nolinkurl{reproduce.py}), which also holds the calibration scripts)',
             r'(repository script \nolinkurl{reproduce.py}, which also holds the calibration scripts)')
    # the Theorem n:thm_eqreduced(iv) contract, said once after the theorem
    t = _rep(t, r'equilibrium price response to a probe with Gaussian noise of variance $\sigma^2$.' + '\n'
             + r'\end{enumerate}' + '\n' + r'\end{theorem}' + '\n',
             r'equilibrium price response to a probe with Gaussian noise of variance $\sigma^2$.' + '\n'
             + r'\end{enumerate}' + '\n' + r'\end{theorem}' + '\n\n'
             + r'Part~(iv) uses the reset contract of Section~\ref{n:cost_sec}, a benchmark for what data can reveal '
               r'rather than a description of a running market.' + '\n')
    t = _rep(t, r'\paragraph{Declaration of generative AI and AI-assisted technologies.}',
             RELATED + '\n\n' + r'\paragraph{Declaration of generative AI and AI-assisted technologies.}')
    t = _rep(t, r'\end{thebibliography}', NEW_BIB.strip() + '\n\n' + r'\end{thebibliography}')
    # the declaration: what the authors have and have not checked
    old = r'and their proofs were read and checked by the first author.'
    if old in t:
        if CORRECTIONS_CHECKED_BY_FIRST_AUTHOR:
            new = (r'and their proofs, including those of Theorem~\ref{n:paradox}, the remark on restrictions by '
                   r'horizon after Proposition~\ref{n:target}, the uniqueness remark after Theorem~\ref{n:minimax} and '
                   r'Supplement Propositions~\ref{prop:nearcrit} and~\ref{prop:hidegame} in their present form, were '
                   r'read and checked by the first author.')
        else:
            new = (r'and the first author read and checked their proofs. Theorem~\ref{n:paradox}, the remark on '
                   r'restrictions by horizon after Proposition~\ref{n:target}, the uniqueness remark after '
                   r'Theorem~\ref{n:minimax} and Supplement Propositions~\ref{prop:nearcrit} and~\ref{prop:hidegame} '
                   r'in their present form, also developed with AI assistance, have not yet been checked by the '
                   r'authors.')
        t = _rep(t, old, new)
    t, dropped = tidy_bib(t)
    assert 'this revision' not in t and 'earlier versions' not in t.lower(), 'revision-history wording left'
    return t
