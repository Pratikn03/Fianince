"""Paper 1, JEDC main text (short version), 22 November 2026.

Input: received/Paper1_JEDC_final.tex, a 27-page main text the authors received on 22 November 2026 (SHA-256
190728c0...). Output: Paper1_JEDC_main.tex, the same paper with the corrections that answer the two simulated referee
reports (ceiling_suite/papers/paper1/review/REFEREE_REPORTS_SIMULATED_20261121.md):

* Theorem (surveillance paradox): exponent n = 4 against the closest economy in the null (composite null), a best
  response to a fixed test rather than an equilibrium, the inquiry cost L, part (iv), the deterrence caveat.
* Near instability: an admissible pair (common persistence, rescaled weights); Figure 1 and Table 1 recomputed
  (research_extension/fragility_reveals/nearcrit_admissible.py).
* What setting a uniform cut from prices requires (known persistence, a memory bound).
* Taiwan: the targeted range fills the cap by construction; what is granted; definitions; literature.
* Overclaims and precision: minimax over labelings, audit trail assumed ungameable, reset contract of the equilibrium
  rate, small-feedback condition, computability of the minimum-distance estimator, Monte Carlo sentences removed.
* References to the Online Supplement become cross-document references (xr-hyper) to Paper1_JEDC_online_supplement,
  which build_short.py extracts from the journal version; labels shared with the supplement follow its names.
* The AI declaration states what the authors have and have not yet checked (flag below).

Every replacement must match exactly once, so a change in the received text stops the build.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'research_extension/paper1_publication_revision/t6'))
import round10  # noqa: E402  (P1M-A1 passages, applied only once the result files exist)
SRC = HERE / 'received' / 'Paper1_JEDC_final.tex'
OUT = HERE / 'Paper1_JEDC_main.tex'

# Set to True only after the first author says he has read and checked Theorem 7.3(ii), Lemma 7.7, Theorem 7.9 and
# Supplement Propositions S4.5 and S11.1 in their present form.
CORRECTIONS_CHECKED_BY_FIRST_AUTHOR = False


def rep(t, old, new, count=1):
    n = t.count(old)
    assert n == count, (old[:120], n, count)
    return t.replace(old, new)


ABSTRACT = (r"Algorithmic traders read prices and move them. We show that a population of such traders affects prices, "
            r"order flows and dealer inventories only through its aggregate feedback response, even in equilibrium, and "
            r"that in the worst case separating $K$ trader types whose rules lie within $\Delta$ takes on the order of "
            r"$\Delta^{-(4K-2)}$ observations. Given the market's persistence and a memory bound, a uniform cut in "
            r"feedback can be set from prices and, without class tags, is minimax over labelings; targeted "
            r"restrictions need tags, which help only if relabeling is costly. A calibration to Taiwan's tagged "
            r"exchange flows illustrates the barrier.")

PARADOX_START = r"Even without account relabeling, an untagged algorithm that anticipates targeting"
PARADOX_END = r"verified class tags eliminate both crowding and costly defensive repositioning simultaneously."
PARADOX_NEW = r"""Even without account relabeling, an untagged algorithm that anticipates targeting can disguise itself by shifting its trading rule toward its neighbor's, at a cost to its own strategy. The next result gives what the supervisor learns when the algorithm best-responds to a fixed test.

\begin{theorem}[The surveillance paradox]\label{thm:paradox}
An untagged group chooses the distance $\delta \in [0, \delta_0]$ between its memory rate and its neighbor's; the neighbor and all other groups stay where they are. The supervisor tests the null that the group trades like its neighbor (one group in place of the two, with unknown memory and weight) at level $\alpha$ under every economy in the null. Detection triggers an inquiry that costs the group $L$, and moving costs it $k(\delta_0 - \delta)^2$, with $\delta_0, k, L > 0$. With $N$ observations, let $J$ be the divergence from the record with the group at distance $\delta$ to the closest record in the null. We take its leading order, $J = c N \delta^n$ with $n > 2$; for a group and its neighbor, $n = 4$. The test is unbiased, and its detection probability depends on $\delta$ only through $J$: it is $P_{\mathrm{d}}(J) \ge \alpha$. Let $\delta^*$ be an optimal distance and $J^* = c N (\delta^*)^n$.
\begin{enumerate}
  \item[(i)] \emph{Hiding is never complete.} Against every such test, $\delta^* > 0$, and $(\delta^*)^{n-2} \ge 2 k^2 \delta_0^2 / (2^n L^2 c N)$ whenever $\delta^* \le \delta_0 / 3$.
  \item[(ii)] \emph{A good test forces crowding.} If the test's power satisfies $P_{\mathrm{d}}(J) - \alpha \ge \beta \min\{\sqrt{J}, \sqrt{\bar{J}}\}$ and the stakes are high ($L \beta \sqrt{\bar{J}} > k \delta_0^2$), then for every $N$,
  \[
    (\delta^*)^{n-2} \le \frac{4 k^2 \delta_0^2}{L^2 \beta^2 c N}.
  \]
  \item[(iii)] \emph{More data, less information.} Against such a test, for all large $N$, $\delta^* \asymp N^{-1/(n-2)}$ and the supervisor's information obeys $J^* \asymp N^{-2/(n-2)} \to 0$: like $N^{-1}$ for a group and its neighbor. The detection probability tends to $\alpha$, and the group's distortion cost $k(\delta_0 - \delta^*)^2$ tends to $k \delta_0^2$.
  \item[(iv)] \emph{Tags reverse it.} With a verified class tag, detection does not depend on $\delta$, so $\delta^* = \delta_0$, and the supervisor learns the group's rule from its tagged flow (Theorem~\ref{thm:tags}).
\end{enumerate}
\end{theorem}

The exponent depends on what the supervisor knows. The record does not say which nearby memory is the neighbor's, so the null is composite. A single group with the pair's total weight and mean memory matches the kernel up to the spread of the two memories, which is of order $\delta^2$ in the kernel and $\delta^4$ in the divergence (Supplement Theorem~\ref{S-thm:merged}(ii) for probes and Proposition~\ref{S-prop:passive}(i) for passive prices; computed from the spectra, the fitted slope is $4.1$, Supplement Section~\ref{S-app:paradox}). A supervisor that knew the neighbor's memory and both weights would face a simple null with $n = 2$; then, against the Gaussian test with high stakes, hiding is complete once $N$ is large, and the record carries no information about the group. If several groups crowd together, $n$ is larger (numerically $8$ for a cluster of three), and the information falls more slowly. In the limiting Gaussian experiment, the one-sided test in the direction orthogonal to the null satisfies (ii) with $\beta = \sqrt{2}\phi(z_\alpha)$ and $\bar{J} = z_\alpha^2 / 2$ (Appendix~\ref{app:proofs}).

Without tags, each new observation is more than offset by the crowding it provokes, and against a group that best-responds, supervision does not converge to knowledge of composition. The group pays for its invisibility with a distorted strategy: by Lemma~\ref{lem:micro}(ii), the cost $k(\delta_0 - \delta)^2$ is the leading-order profit loss of a Kalman-filtering desk that deviates from its optimal memory rate. Whether this is a failure depends on what the supervisor wants. If the conduct at $\delta_0$ is what it fears, the crowding is deterrence; what fails is learning, not necessarily welfare. This is the tension between acting on market information and preserving it (Bond et al., 2010; Bond and Goldstein, 2015), here for information about who trades rather than about fundamentals; Frankel and Kartik (2019) study how manipulation muddles a signal. The loss $L$ stands for the inquiry that detection triggers, for example a request to brokers for account records; without such an inquiry, detection would have no consequence (Theorem~\ref{thm:minimax}). The theorem describes a best response to a fixed test, not an equilibrium: the neighbor does not move and the supervisor does not adapt its test. When several untagged groups position strategically, Supplement Proposition~\ref{S-prop:hidegame}(iv) shows that in any Nash equilibrium with bounded nearest-neighbor distances, every group's asymptotic detection probability is at most $\alpha + k_g \limsup_N \Delta_g^2 / L_g$; verified class tags remove both the crowding and the defensive repositioning."""

PARADOX_PROOF_START = r"\begin{proof}[Proof of Theorem~\ref{thm:paradox}]"
PARADOX_PROOF_END = r"\end{proof}"
PARADOX_PROOF_NEW = r"""\begin{proof}[Proof of Theorem~\ref{thm:paradox}]
\emph{(i)} The test rejects with probability at most $\alpha$ under the closest economy in the null, and with the group at distance $\delta$ it rejects with a probability that exceeds this by at most the total variation between the two records, which is at most $\sqrt{J/2}$ by Pinsker's inequality. So moving from $\delta = 0$ to a small $\delta > 0$ changes expected cost by at most $-2k\delta_0\delta + k\delta^2 + L\sqrt{cN\delta^n/2}$, which is negative near zero because $n > 2$; hence $\delta^* > 0$. If $\delta^* \le \delta_0/3$, then $2\delta^* \le \delta_0$ is feasible; optimality of $\delta^*$ against $2\delta^*$, together with $P_{\mathrm{d}}(J^*) \ge \alpha$ and Pinsker's inequality, gives
\[
  k\delta_0\delta^* \le k\bigl[(\delta_0 - \delta^*)^2 - (\delta_0 - 2\delta^*)^2\bigr] \le L\sqrt{cN(2\delta^*)^n/2}.
\]
Squaring and dividing by $(\delta^*)^2$ yields $(\delta^*)^{n-2} \ge 2k^2\delta_0^2/(2^n L^2 cN)$.

\emph{(ii)} At $\delta = 0$ the record is in the null, so the detection probability is at most $\alpha$. Optimality of $\delta^*$ against $\delta = 0$ gives
\[
  L\bigl(P_{\mathrm{d}}(J^*) - \alpha\bigr) \le k\bigl[\delta_0^2 - (\delta_0 - \delta^*)^2\bigr] \le \min\{k\delta_0^2,\; 2k\delta_0\delta^*\}.
\]
If $J^* \ge \bar{J}$, the power envelope implies $L\beta\sqrt{\bar{J}} \le k\delta_0^2$, contradicting the high-stakes condition. Thus $J^* < \bar{J}$ and $L\beta\sqrt{cN(\delta^*)^n} \le 2k\delta_0\delta^*$; squaring and dividing by $(\delta^*)^2$ gives the bound.

\emph{(iii)} For all sufficiently large $N$, part~(ii) forces $\delta^* \le \delta_0/3$, so (i) and (ii) hold together: $(\delta^*)^{n-2} \asymp N^{-1}$, i.e., $\delta^* \asymp N^{-1/(n-2)}$, and $J^* = cN(\delta^*)^n \asymp N \cdot N^{-n/(n-2)} = N^{-2/(n-2)} \to 0$. Hence $P_{\mathrm{d}}(J^*) \le \alpha + \sqrt{J^*/2} \to \alpha$ and $k(\delta_0 - \delta^*)^2 \to k\delta_0^2$.

\emph{(iv)} Under a tag, detection does not depend on $\delta$, so $k(\delta_0 - \delta)^2$ is minimized at $\delta^* = \delta_0$.

\emph{The Gaussian test.} In the limiting Gaussian experiment, let the null be a linear subspace and the alternative lie at distance $t$ from it. The test that rejects when the component of the observation orthogonal to the null exceeds $z_\alpha$ has level $\alpha$ under every null economy and power $\Phi(t - z_\alpha)$, and $J = t^2/2$. As a function of $t = \sqrt{2J}$ the power is convex on $[0, z_\alpha]$, so it lies above its tangent at zero: $P_{\mathrm{d}}(J) - \alpha \ge \phi(z_\alpha)\sqrt{2J}$ for $J \le z_\alpha^2/2$, and it is increasing beyond. The two bounds on $(\delta^*)^{n-2}$ in (i) and (ii), and the comparisons of costs behind them, are checked in Lean~4 for every exponent $n \ge 2$ (Supplement Table~\ref{S-tab:newlean}); Pinsker's inequality, unbiasedness and the power envelope enter there as hypotheses, and the rates in (iii) follow from the two bounds.
\end{proof}"""

UNIFORM_REMARK = r"""

\textbf{What setting a uniform cut from prices requires.} Part~(i) of Proposition~\ref{prop:interventions} takes the persistence $a$ as known, and that is a restriction on the population: a group with memory zero acts exactly like persistence (Supplement Theorem~\ref{S-thm:merged}(i)), so knowing $a$ amounts to assuming that every memory exceeds some $\underline{r} > 0$, or to knowing which part of the response at the first lag is feedback. The budget also needs a bound on memory. It is the linear functional with $g(r) = 1/(1-r)$, and by Theorem~\ref{thm:cheap}(iii) a group with memory close to one and negligible weight can move it at bounded divergence unless memories are bounded by some $\bar{r} < 1$. Under both restrictions the budget is learned at nearly the parametric rate: the taps beyond the first $L$ sum to at most $W\bar r^{L}/(1-\bar r)$, so summing the first $L \approx \log(1/\epsilon)/\log(1/\bar r)$ estimated taps gives the feedback weight $\sum_m k_m$, and with it the budget, to accuracy $\epsilon$ from order $\sigma^2\epsilon^{-2}\log(1/\epsilon)$ experiments. Without the restrictions, the uniform cut inherits part of the composition problem. The instrument must also scale feedback traders while sparing arbitrageurs and dealers. Real instruments, such as transaction taxes, minimum resting times and order-to-trade limits, act with an incidence $\theta(r)$ that varies with the trader's horizon, so their effect on the budget is the linear functional with $g(r) = \theta(r)/(1-r)$, whose cost Theorem~\ref{thm:cheap} gives. An incidence that does not vary with memory gives the budget itself. One that singles out the memories below a cutoff meets the barrier of Theorem~\ref{thm:cost}: by part~(iii) of Proposition~\ref{prop:interventions}, a restriction by horizon, which needs no tags, is a policy for which composition decides whether a ceiling is met."""

HORIZON_ITEM = r"""  \item[(iii)] \emph{Restriction by horizon.} Halting the feedback of every group whose memory lies below a cutoff $\hat r \in (0, 1)$ does not either. Under the conditions of Theorem~\ref{thm:cost}, for every $K \ge 2$ and all small $\Delta\eta > 0$, there exist two $K$-group economies with memories in $[\hat r - \Delta\eta, \hat r + 2\Delta\eta]$ whose merged measures match moments $0, \dots, 2K-2$, such that the restriction removes at least $\kappa W/K^2$ of the budget in one economy and nothing in the other, where $W$ is the total merged weight. Over a nonempty interval of ceilings $\bar{s}$, the restriction satisfies the ceiling in one economy and breaches it in the other; deciding between them from $N$ reset records with both errors at most $1/4$ requires $N \ge c \sigma^2 (\Delta\eta)^{-(4K-2)}$.
"""

HORIZON_PROOF = r"""\begin{proof}[Proof of Proposition~\ref{prop:interventions}(iii)]
Let $x_K < 1$ be the largest node of the $K$-point Gauss--Legendre rule on $[-1, 1]$, and place the hard pair of Theorem~\ref{thm:cost}, with a common persistence and total merged weight $W$, on $r_c + \Delta\eta[-1, 1]$ with $r_c = \hat r + (1 + x_K)\Delta\eta/2$. Its memories lie in $[\hat r - \Delta\eta, \hat r + 2\Delta\eta]$. The Gauss--Radau economy has an atom of weight $W/K^2$ at $r_c - \Delta\eta < \hat r$, because the endpoint weight of the $K$-point Gauss--Radau rule on $[-1, 1]$ is $2/K^2$. Every memory of the Gauss economy is at least $r_c - x_K\Delta\eta > \hat r$. Group $i$ contributes $\kappa q_i = \kappa w_i/(1 - r_i)$ to the budget, so the restriction removes at least $\kappa W/K^2$ in the Gauss--Radau economy and nothing in the Gauss economy. The budgets themselves, $a + \kappa\int (1 - r)^{-1}\,dM(r)$, differ by $O((\Delta\eta)^{2K-1})$, because the merged measures match moments $0, \dots, 2K-2$ and $(1 - r)^{-1}$ is smooth near $r_c$. For small $\Delta\eta$ the budgets after the restriction therefore differ by at least $\kappa W/(2K^2)$, and every ceiling between them is met in one economy and breached in the other. The record length is that of Theorem~\ref{thm:cost}(ii), which concerns the same pair.
\end{proof}

"""

TAIWAN_QUAL = r"""

Four qualifications apply. First, the range $[-0.028, 0.028]$ in item~2 fills the cap by construction: two classes can share one memory with large weights of opposite sign, which leaves the aggregate kernel unchanged, so the width is set by the cap on each class's contribution, not by the data (the extreme compositions the search finds have weights $-9.0$, $4.6$ and $4.7$). Weights restricted to one sign would exclude these compositions; we have not computed the range under that restriction. The exact barrier, the relabeling set, does not depend on the cap. Second, the tagged intervals in Table~\ref{tab:taiwan} assume that each class's feedback decays at the persistence of its own flow, while the price-only comparisons let feedback memory vary with non-feedback flow held fixed. Third, item~3 rests on the grant: the price-only supervisor is given the persistences $a_j$, the impact $\kappa$ and the non-feedback law, all estimated with the tagged flows; with feedback contributing $0.0017$ to a budget of $0.97$, separating the two from prices alone is the problem that Proposition~\ref{prop:interventions} assumes away. Fourth, the record lengths treat the 300 stocks as independent, which is generous to prices; the bootstrap resamples dates because they are not independent. The dealers' estimated response is negative, so the calibrated economy lies outside the positive class used for the lower bounds; the computations here (Whittle rates, Pinsker's inequality, relabeling) do not need positivity."""


RELETTER = {'a': 'b', 'b': 'c', 'c': 'd'}


def reletter(t):
    """Use the Online Supplement's letters for the authors' own working papers, so that a citation means the same
    paper in both documents: 2026a the earlier working paper of 5 November 2026, 2026b the paper on machine markets,
    2026c the companion note, 2026d the full working paper. The received main text used a, b, c for the last three."""
    n = len(re.findall(r'Niroula et al\., 2026[abc]', t))
    t = re.sub(r'Niroula et al\., 2026[abc](?:, 2026[abc])*',
               lambda m: re.sub(r'2026([abc])', lambda k: '2026' + RELETTER[k.group(1)], m.group(0)), t)
    assert len(re.findall(r'Niroula et al\., 2026[bcd]', t)) == n
    t = rep(t, r"Niroula, P., Alkhushayni, S., Chen, Y., Bhavsar, M., Niroula, P., 2026a.",
            r"Niroula, P., Alkhushayni, S., Chen, Y., Bhavsar, M., Niroula, P., 2026b.")
    t = rep(t, r"Niroula, P., Niroula, P., Khatiwada, S., 2026b. After a breach",
            r"Niroula, P., Niroula, P., Khatiwada, S., 2026c. After a breach")
    t = rep(t, r"Niroula, P., Niroula, P., Khatiwada, S., 2026c. Observationally equivalent",
            r"Niroula, P., Niroula, P., Khatiwada, S., 2026d. Observationally equivalent")
    t = rep(t, r"(Niroula et al., 2026c, Proposition~C2.1)", r"(Niroula et al., 2026c, Proposition~C2.1(iv))")
    return t


def build(text):
    t = reletter(text)
    # ---------------------------------------------------------------- preamble and front matter
    t = rep(t, "\\usepackage{fancyhdr}\n\\usepackage{hyperref}\n",
            "\\usepackage{fancyhdr}\n\\usepackage{xr-hyper}\n\\usepackage{hyperref}\n"
            "\\externaldocument[S-]{Paper1_JEDC_online_supplement}\n"
            "\\graphicspath{{../paper1_core/}{../paper1_note/}}\n")
    t = rep(t, "\\linespread{1.12}\n", "\\linespread{1.12}\n\\emergencystretch=3em\n")
    t = re.sub(r"(\\begin\{abstract\}\n\\noindent\n).*?(\n\\end\{abstract\})",
               lambda m: m.group(1) + ABSTRACT + m.group(2), t, count=1, flags=re.S)
    t = rep(t, r"\noindent\textbf{Online Supplement and Replication:} Technical lemmas,",
            r"\noindent\textbf{Online Supplement and Replication:} References of the form ``Supplement Theorem~S4.1'' are to the Online Supplement, which states every result in full; the full working paper (Niroula et al., 2026d) collects every supplementary result. Technical lemmas,")
    t = rep(t, r"\textbf{Funding and competing interests.}",
            r"\textbf{Related manuscripts.} An earlier working paper of the same authors (Niroula et al., 2026a, dated 5 November 2026) studied the same model; this article supersedes it. The earlier paper, the companion note (Niroula et al., 2026c) and the full working paper (Niroula et al., 2026d) are in the repository cited below.\par\medskip" + "\n\n" + r"\textbf{Funding and competing interests.}")
    # ---------------------------------------------------------------- introduction
    t = rep(t, r"In a Gaussian feedback market, the Kullback--Leibler divergence between two candidate populations equals half the cumulative excess mean-squared forecast error from confusing them (Theorem~\ref{thm:forecast-kl}); hence composition",
            r"In a Gaussian feedback market, the Kullback--Leibler divergence between two candidate populations equals half the cumulative excess mean-squared forecast error from confusing them (Theorem~\ref{thm:forecast-kl}, the Gaussian chain rule stated in market terms); composition")
    t = rep(t, r"Because prices cannot distinguish label permutations, a uniform cut across all feedback activity weakly dominates every price-based policy against the worst labeling consistent with the record for any convex loss and label-symmetric cost—and is the unique minimax supervisory policy whenever the cost is strictly convex (Theorem~\ref{thm:minimax}).",
            r"Because prices cannot distinguish label permutations, a uniform cut across all feedback activity does at least as well as every price-based policy against the worst labeling consistent with the record, for any convex loss and label-symmetric cost: it is minimax over labelings, Bayes under an exchangeable prior, and, when the cost is strictly convex, the unique minimax policy (Theorem~\ref{thm:minimax}). Given the market's own persistence and a bound on memory, such a cut can be set from prices (Section~\ref{sec:supervision}).")
    t = rep(t, r"Only an owner-linked audit trail that ties accounts to beneficial owners retains its value.",
            r"An owner-linked audit trail that ties accounts to beneficial owners keeps its value, because we assume that it cannot be gamed.")
    t = rep(t, r"\item \emph{The surveillance paradox.} Without class tags, an untagged algorithm facing a level-$\alpha$ detection test crowds its memory rate toward its neighbor as the supervisor's data record $N$ grows. Whenever the identification divergence scales as $c N D^p$ with $p > 2$ (including $p=4$ for symmetric splitting and $p=6$ for moment-matched two-group hiding), crowding more than offsets the added data: the supervisor's equilibrium information falls to zero at rate $N^{-2/(p-2)}$ (e.g., $N^{-1/2}$ for $p=6$), detection probability collapses to the false-alarm rate $\alpha$, and the trader incurs a permanent strategy distortion cost (Theorem~\ref{thm:paradox}). Class tags eliminate this crowding.",
            r"\item \emph{The surveillance paradox.} Without class tags, an untagged algorithm facing a fixed level-$\alpha$ test crowds its memory rate toward its neighbor as the supervisor's record $N$ grows. Against the closest economy in which it trades like its neighbor, the divergence is of order $N\delta^4$ in the distance $\delta$, so crowding more than offsets the added data: when the algorithm best-responds, the supervisor's information about it falls like $N^{-1}$, detection collapses to the false-alarm rate $\alpha$, and the trader bears a permanent strategy distortion (Theorem~\ref{thm:paradox}). Class tags eliminate this crowding.")
    t = rep(t, r"Our contribution is economic: we show that kernel sufficiency survives endogenous inventory-equilibrium pricing; establish the exact equivalence between supervisory identification and forecast loss in a feedback market; prove the minimax optimality of uniform (and group-uniform) supervisory policies; solve the strategic relabeling disclosure game comparing class tags to owner-linked audit trails; and derive the negative equilibrium identification rate of the surveillance paradox.",
            r"That market-wide policies need only a reduced-form aggregate while targeted ones need structure is Marschak's maxim and the logic of sufficient statistics for policy (Marschak, 1953; Chetty, 2009); what we add is the price of the structure in a feedback market. Our contribution is economic: we show that kernel sufficiency survives endogenous inventory-equilibrium pricing, where dealers' anticipation over-weights slow memories; characterize which linear questions about the population prices answer cheaply; prove the minimax optimality of uniform (and group-uniform) supervisory policies over labelings; solve the strategic relabeling disclosure game comparing class tags to owner-linked audit trails; and derive the rate at which an algorithm that best-responds to surveillance degrades what the supervisor learns. The equivalence between detection and forecast loss (Theorem~\ref{thm:forecast-kl}) is the Gaussian chain rule applied to a feedback market; we use it to explain the separation, not as a new statistical result.")
    t = rep(t, r"Tagged flows carry $4.7 \times 10^5$ times more information per stock-day about class composition than prices alone. Over all compositions statistically indistinguishable from the full panel price record, the effect of a uniform feedback cut is tightly pinned to $[0.0014, 0.0019]$, whereas the effect of halting foreign feedback spans $[-0.028, 0.028]$.",
            r"With each class's non-feedback flow held at its estimated law, tagged flows carry $4.7 \times 10^5$ times more information per stock-day about class composition than prices alone. Granting a price-only supervisor the market's persistence, impact and non-feedback order flow, the effect of a uniform feedback cut over all compositions statistically indistinguishable from the full panel price record lies in $[0.0014, 0.0019]$. The effect of halting foreign feedback is not identified: relabeling alone leaves each class's estimated contribution possible, and classes with offsetting weights fill any cap placed on each class's contribution. Even with every class's weight nonnegative, the compositions the panel cannot tell apart allow anything from none to nearly all of the total feedback, and the tagged estimate survives decoupling feedback from each class's flow persistence (Section~\ref{sec:taiwan}). A registered test did not establish that the tagged responses are causal feedback, so the calibration illustrates the barrier rather than testing the model.")
    t = rep(t, r"our results establish precisely which features of a trader population are recoverable from prices and at what statistical cost.",
            r"our results establish precisely which features of a trader population are recoverable from prices and at what statistical cost. Feedback traders are central to models of destabilizing speculation and of return autocorrelation (De Long et al., 1990; Cutler et al., 1990; Sentana and Wadhwani, 1992), and simulation-based estimation of agent-based models (Grazzini and Richiardi, 2015; Platt, 2020) faces the same identification question in nonlinear models. Our identification result is global (Theorem~\ref{thm:what-id}); where memories collide, the information matrix of Rothenberg (1971) is singular, and Theorems~\ref{thm:cost} and~\ref{thm:recovery} give the rate at which identification weakens near a collision. Our minimax results are decisions under ambiguity in the sense of Manski (2000).")
    t = rep(t, r"Our setting isolates a distinct mechanism: under a common public signal, identity is irrelevant for price discovery and forecasting, yet essential for assigning targeted supervisory interventions.",
            r"Our setting isolates a distinct mechanism: under a common public signal, identity is irrelevant for price discovery and forecasting, yet essential for assigning targeted supervisory interventions. Inventory-based price impact goes back to Ho and Stoll (1981) and Grossman and Miller (1988), and Hendershott and Menkveld (2014) measure it. Crowding among algorithmic and quantitative strategies is documented by Chaboud et al.\ (2014) and Khandani and Lo (2011) and analyzed by Stein (2009); pre-trade anonymity in limit-order markets, which concerns who quotes rather than who trades on feedback, is studied by Foucault et al.\ (2007).")
    t = rep(t, r"provides a formal rationale for that architecture: market-wide remedies require only prices, targeted restrictions require class records, and relabeling incentives necessitate owner-linked audit trails.",
            r"provides a formal rationale for that architecture: market-wide remedies require only prices, targeted restrictions require class records, and cheap relabeling favors owner-linked audit trails. Acting on market information can degrade it (Bond et al., 2010; Bond and Goldstein, 2015), and manipulation muddles the signals a principal relies on (Frankel and Kartik, 2019, 2022; Perez-Richet and Skreta, 2022).")
    t = rep(t, r"whereas compositional weights require $\Delta^{-(4K-2)}$ observations (Theorem~\ref{thm:cheap} and Corollary~\ref{cor:sep}).",
            r"whereas compositional weights require $\Delta^{-(4K-2)}$ observations (Theorem~\ref{thm:cheap} and Corollary~\ref{cor:sep}). The same barrier decides whether a restriction by horizon, which halts feedback from traders with memories below a cutoff and needs no tags, meets a prudential ceiling (Proposition~\ref{prop:interventions}(iii)).")
    # ---------------------------------------------------------------- model, sufficiency, equilibrium
    t = rep(t, r"$D, D_0, p, J$ & Distance to neighbor's memory, preferred distance, divergence exponent ($p > 2$), divergence $J = cND^p$ \\",
            r"$\delta, \delta_0, n, J$ & Distance to the neighbor's memory, preferred distance, divergence exponent ($n = 4$), divergence $J = cN\delta^n$ \\")
    t = rep(t, r"we derive price impact and pricing-error persistence endogenously from competitive, risk-averse overlapping-generations dealers who bear inventory risk.",
            r"we derive price impact, and pricing-error persistence given the share of inventory that dealers carry over, from competitive, risk-averse overlapping-generations dealers who bear inventory risk.")
    t = rep(t, r"We now derive both endogenously from competitive, risk-averse dealers who carry inventory risk,",
            r"We now derive both from competitive, risk-averse dealers who carry inventory risk, taking as given the share $\bar{a}$ of inventory they carry from one period to the next,")
    t = rep(t, r"As shown in the Online Supplement (Lemma~S1.1), both",
            r"As shown in Supplement Lemma~\ref{S-lem:micro}, both")
    t = rep(t, r"sufficiency extends to arbitrary nonlinear or profit-switching populations via the aggregate flow map (Online Supplement, Section~S2).",
            r"sufficiency extends to arbitrary nonlinear or profit-switching populations via the aggregate flow map (Supplement Section~\ref{S-sec:suff}).")
    t = rep(t, r"\item[(iv)] \emph{Small feedback.} For small aggregate feedback intensity $G(1) = \sum_i q_i$ with $\Lambda_0 > 0$, there exists a unique equilibrium near $(\kappa_-, 1)$ satisfying",
            r"\item[(iv)] \emph{Small feedback.} Let $\Lambda_0 > 0$, fix $\delta > 0$ with $\max_i r_i < 1 - \delta$, and suppose $\epsilon = \sup_{|D - 1| \le \delta}(|G(D)| + |G'(D)|)$ is small. Then there exists a unique equilibrium near $(\kappa_-, 1)$, and with the aggregate feedback intensity $G(1) = \sum_i q_i$,")
    t = rep(t, r"D = 1 - \kappa_- G(1) + o(G(1)), \qquad", r"D = 1 - \kappa_- G(1) + o(\epsilon), \qquad")
    t = rep(t, r"\, G(1) + o(G(1)).", r"\, G(1) + o(\epsilon).")
    t = rep(t, r"Every sample-complexity lower bound derived below therefore holds \emph{a fortiori} under unobserved fundamentals (while Corollary~S7.2 in the Online Supplement shows that unknown primitives do not alter the upper-bound rate under active probes).",
            r"Every sample-complexity lower bound derived below therefore holds \emph{a fortiori} under unobserved fundamentals (while Supplement Corollary~\ref{S-cor:unknown_primitives} shows that unknown primitives do not alter the upper-bound rate under active probes). The positive results, identification and the upper bounds, assume that the pricing error is observed.")
    t = rep(t, r"This introduces a second exogenous innovation channel (analyzed in Online Supplement Section~S8) without altering pathwise kernel sufficiency (Theorem~\ref{thm:sufficiency}) or relaxing the $\Delta^{-(4K-2)}$ identification barrier for closely spaced memory rates.",
            r"This introduces a second exogenous innovation channel. It does not alter pathwise kernel sufficiency (Theorem~\ref{thm:sufficiency}), which allows any public signal, and the lower bound of Theorem~\ref{thm:smooth}, which allows any smooth causal rule of the observed history, still applies when the observed innovations are Gaussian.")
    t = rep(t, r"require $N \ge c \sigma^2 (\Delta\eta)^{-(4K-2)}$ observations to be distinguished.",
            r"require $N \ge c \sigma^2 (\Delta\eta)^{-(4K-2)}$ reset experiments to be distinguished, each recording the equilibrium price response to a probe with Gaussian noise of variance $\sigma^2$.")
    t = rep(t, r"The proofs of Theorems~\ref{thm:inv-eq} and~\ref{thm:eq-id} are given in Appendix~\ref{app:proofs}.",
            r"Part~(iv) uses the reset contract of Section~\ref{sec:cost}, a benchmark for what data can reveal rather than a description of a running market. The proofs of Theorems~\ref{thm:inv-eq} and~\ref{thm:eq-id} are given in Appendix~\ref{app:proofs}.")
    # ---------------------------------------------------------------- the price of composition
    t = rep(t, r"The proofs of parts (i)--(iii) appear in the Online Supplement (Theorems~S4.1, S4.2, and~S4.4).",
            r"Part~(i) is Supplement Proposition~\ref{S-prop:passive}, part~(ii) Supplement Theorem~\ref{S-thm:kcohort}, and part~(iii) Supplement Proposition~\ref{S-prop:esprit}.")
    t = rep(t, r"(such as Laplace innovations), the exponent $4K-2$ is unchanged (Online Supplement, Section~S4).",
            r"(such as Laplace innovations), the exponent $4K-2$ is unchanged, and the lower bounds shrink by at most the factor $\sigma^2 I_f$, where $I_f$ is the Fisher information for location of the news law; the factor is $2$ for Laplace news but can be large for heavy-tailed news (Supplement Section~\ref{S-sec:cost}).")
    t = rep(t, r"The opposite holds: at a common feedback budget $S = 1 - \epsilon$, the passive KL divergence per observation between the hard pair of Theorem~\ref{thm:cost} remains bounded by $C(\Delta\eta)^{4K-2}$ uniformly in $\epsilon > 0$ (Online Supplement, Proposition~S4.5).",
            r"The opposite holds. Give the hard pair of Theorem~\ref{thm:cost} a common persistence and, by rescaling one economy's weights by a factor $1 + O((\Delta\eta)^{2K-1})$, a common feedback budget $S = 1 - \epsilon$. The passive KL divergence per observation then remains bounded by $C(\Delta\eta)^{4K-2}$ uniformly in $\epsilon > 0$ (Supplement Proposition~\ref{S-prop:nearcrit}).")
    t = rep(t, r"\includegraphics[width=\linewidth]{fig1.png}", r"\includegraphics[width=\linewidth]{fig_barrier_admissible.pdf}")
    t = rep(t, r"\caption{The passive identification barrier near instability. Both panels plot the Gaussian Kullback--Leibler divergence per observation between the stationary price processes of the $K$-node Gauss and Gauss--Radau populations spread over $\Delta\eta$ around $r_c = 0.5$ (total weight $0.3$, impact $\kappa = 0.5$). Panel~(a): at a common feedback budget $1 - S = 10^{-6}$, information decays as $(\Delta\eta)^{4K-2}$ (slopes $6$ and $10$). Panel~(b): holding the feedback budget common across economies (solid curves), information stays uniformly bounded as $1 - S \to 0$; holding persistence $a$ common instead (dashed curves), information diverges only because the two economies' feedback budgets then differ.}",
            r"\caption{The passive identification barrier near instability. Both panels plot the Gaussian Kullback--Leibler divergence per observation between the stationary price processes of the $K$-node Gauss and Gauss--Radau populations spread over $\Delta\eta$ around $r_c = 0.5$ (total weight $0.3$, impact $\kappa = 0.5$). Panel~(a): at a common persistence and a common feedback budget $1 - S = 10^{-6}$, information decays as $(\Delta\eta)^{4K-2}$ (fitted slopes $5.8$ and $9.9$). Panel~(b): with a common persistence and a common budget (solid; the Gauss--Radau weights rescaled by a factor $1 + O((\Delta\eta)^{2K-1})$), information stays bounded as $1 - S \to 0$. With a common persistence and no rescaling (dashed), the budgets differ by order $(\Delta\eta)^{2K-1}$; the information then grows roughly like $(1 - S)^{-1}$ until the margin reaches that gap, and levels off. Computed from the closed-form spectra; the code is in the replication archive.}")
    old_rows = r"""$K = 2$ & $0.5 \pm 0.1$   & $0.8\text{--}1.4$  & $20{,}000$        & $16{,}000$ \\
        & $0.5 \pm 0.05$  & $0.9\text{--}1.2$  & $1.2 \times 10^6$ & $9.0 \times 10^5$ \\
        & $0.8 \pm 0.1$   & $1.9\text{--}6.6$  & $100$             & $69$ \\
        & $0.8 \pm 0.05$  & $2.4\text{--}4.3$  & $6{,}000$         & $3{,}900$ \\
        & $0.9 \pm 0.05$  & $4.3\text{--}13.5$ & $120$             & $77$ \\
        & $0.9 \pm 0.025$ & $5.2\text{--}8.9$  & $7{,}000$         & $4{,}300$ \\
\midrule
$K = 3$ & $0.5 \pm 0.1$   & $0.8\text{--}1.4$  & $1.5 \times 10^8$ & $9.9 \times 10^7$ \\
        & $0.5 \pm 0.05$  & $0.9\text{--}1.2$  & $1.5 \times 10^{11}$ & $9.6 \times 10^{10}$ \\"""
    new_rows = r"""$K = 2$ & $0.5 \pm 0.1$   & $0.8\text{--}1.4$  & $31{,}000$        & $23{,}000$ \\
        & $0.5 \pm 0.05$  & $0.9\text{--}1.2$  & $1.8 \times 10^6$ & $1.3 \times 10^6$ \\
        & $0.8 \pm 0.1$   & $1.9\text{--}6.6$  & $280$             & $160$ \\
        & $0.8 \pm 0.05$  & $2.4\text{--}4.3$  & $15{,}000$        & $8{,}100$ \\
        & $0.9 \pm 0.05$  & $4.3\text{--}13.5$ & $480$             & $230$ \\
        & $0.9 \pm 0.025$ & $5.2\text{--}8.9$  & $25{,}000$        & $11{,}000$ \\
\midrule
$K = 3$ & $0.5 \pm 0.1$   & $0.8\text{--}1.4$  & $2.0 \times 10^8$ & $1.3 \times 10^8$ \\
        & $0.5 \pm 0.05$  & $0.9\text{--}1.2$  & $1.9 \times 10^{11}$ & $1.2 \times 10^{11}$ \\"""
    t = rep(t, old_rows, new_rows)
    t = rep(t, r"computed from the closed-form Gaussian spectra at common feedback budget $S$, $\kappa = 0.5$, and feedback share $\kappa \sum_i q_i = 0.3$, assuming $252$ trading days per year.",
            r"computed from the closed-form Gaussian spectra at a common persistence and a common feedback budget $S$ (the Gauss--Radau weights rescaled to match the budget), $\kappa = 0.5$, and feedback share $\kappa \sum_i q_i = 0.3$ (total weight $0.6(1 - r_c)$ of the Gauss economy), assuming $252$ trading days per year.")
    t = rep(t, r"Entries are worst-case lower bounds for moment-matched pairs, not fitted venue horizons.}",
            r"With non-Gaussian news the bounds can be smaller, by at most the factor $\sigma^2 I_f$ ($2$ for Laplace news). Entries are worst-case lower bounds for moment-matched pairs, not fitted venue horizons.}")
    t = rep(t, r"Theorem~\ref{thm:cheap} (Online Supplement, Theorem~S10.1 and Proposition~S10.2) specializes",
            r"Theorem~\ref{thm:cheap} (Supplement Theorem~\ref{S-thm:questions} and Proposition~\ref{S-prop:parametric}) specializes")
    t = rep(t, r"matching the $\Delta^{-(4K-2)}$ sample order of Theorem~\ref{thm:smooth} (Online Supplement, Section~S18).",
            r"matching the $\Delta^{-(4K-2)}$ sample order of Theorem~\ref{thm:smooth} (Supplement Section~\ref{S-app:incoming}). The estimator is an exact global minimizer over $\mathcal{Z}$, which is not convex; the theorem gives no algorithm that finds it.")
    # ---------------------------------------------------------------- forecasting
    t = rep(t, r"The next theorem provides the exact information-theoretic link: in a Gaussian feedback market, the information a price record carries about two competing populations is literally proportional to the cumulative forecast loss from mistaking one for the other.",
            r"The next theorem states the Gaussian chain rule in market terms: in a Gaussian feedback market, the information a price record carries about two competing populations equals half the cumulative excess forecast loss from mistaking one for the other. Populations that forecast alike are therefore hard to tell apart, and a uniform cut depends only on what forecasts reveal.")
    t = rep(t, r"(Online Supplement, Theorems~S18.1 and~S18.2)", r"(Supplement Theorems~\ref{S-n:irr} and~\ref{S-n:uniformlog})")
    # ---------------------------------------------------------------- supervision
    t = rep(t, r"""\end{enumerate}
\end{proposition}

\begin{corollary}[Expected loss from weakly identified targeting]""",
            HORIZON_ITEM + r"""\end{enumerate}
\end{proposition}""" + UNIFORM_REMARK + r"""

\begin{corollary}[Expected loss from weakly identified targeting]""")
    t = rep(t, r"Figure~\ref{fig:intervention} illustrates this contrast in a two-class economy: halting the largest class produces qualitatively opposite prudential outcomes across nearly indistinguishable economies, whereas a single verified class report collapses decision error by six orders of magnitude in sample size.",
            r"Figure~\ref{fig:intervention} illustrates this contrast in a two-class economy and an illustrative measurement experiment: halting the largest class produces qualitatively opposite prudential outcomes across nearly indistinguishable economies, whereas verified class reports cut the sample needed for a $5\%$ error by six orders of magnitude.")
    t = rep(t, r"\includegraphics[width=\linewidth]{fig2.png}", r"\includegraphics[width=\linewidth]{fig_intervention_revision.pdf}")
    t = rep(t, r"Panel~A uses the two-class construction of Online Supplement Section~S17",
            r"Panel~A uses the two-class construction of Supplement Section~\ref{S-app:revisiondecision}")
    t = rep(t, r"achieving $5\%$ error requires roughly $2.03 \times 10^6$ public-response repetitions versus $2$ class reports.}",
            r"achieving $5\%$ error requires roughly $2.03 \times 10^6$ public-response repetitions versus $2$ class reports. These are assumptions of an illustrative measurement experiment, not a passive-innovation model, a feasible live reset policy or a market calibration.}")
    # minimax: labelings are pi (sigma is a noise level throughout)
    a = t.index(r"Let class $d \in \{1, \dots, K\}$ contribute $u_d = \kappa q_d$")
    b = t.index(r"Verified partial tags break permutation symmetry", a)
    span = t[a:b]
    span = span.replace(r"\sigma(c)", r"\pi(c)").replace(r"\sigma", r"\pi")
    t = t[:a] + span + t[b:]
    a = t.index(r"\begin{theorem}[Minimax value of partial tags]")
    b = t.index(r"\end{theorem}", a)
    t = t[:a] + t[a:b].replace(r"\sigma", r"\pi") + t[b:]
    t = rep(t, r"If $\pi$ is the unknown permutation assigning labels to underlying classes,",
            r"If $\pi$ is the unknown permutation assigning labels to underlying classes (a labeling),")
    t = rep(t, r"Because no price record distinguishes labelings (Theorem~\ref{thm:sufficiency}), every price-based policy is weakly dominated by a uniform policy against the worst consistent labeling.",
            r"Labels do not enter prices (Theorem~\ref{thm:sufficiency}), so no record distinguishes labelings; the uniform policy does at least as well as $\theta$ against the worst labeling (it is minimax) and on average over labelings (it is Bayes under an exchangeable prior).")
    t = rep(t, r"the minimax problem admits a unique solution $\bar{\theta}^*\mathbf{1}$: the uniform cut is the unique minimax supervisory policy.",
            r"the minimax problem admits a unique solution $\bar{\theta}^*\mathbf{1}$: the uniform cut is the unique minimax policy over labelings.")
    t = rep(t, r"The proofs of Theorems~\ref{thm:minimax} and~\ref{thm:partial-minimax} and Corollary~\ref{cor:halt} are short and self-contained (Appendix~\ref{app:proofs}), and their finite combinatorial statements are verified in Lean~4 (the Online Supplement documents exact formalization scope across all results, separating machine-checked deterministic steps from paper-level probabilistic arguments). In numerical checks across $14{,}400$ random economies with three convex losses and three cost functions, the uniform policy is strictly better than non-uniform policies in $86\%$ of cases; across $1{,}200$ random tag partitions, partial tags deliver strictly positive value in $27\%$ of economies.",
            r"The proofs of Theorems~\ref{thm:minimax} and~\ref{thm:partial-minimax} and Corollary~\ref{cor:halt} are short and self-contained (Appendix~\ref{app:proofs}). Theorem~\ref{thm:minimax}(i), Corollary~\ref{cor:halt} and the dominance part of Theorem~\ref{thm:partial-minimax} are checked in Lean~4 in full, with the cost convex on $[0,1]^K$, and so is Theorem~\ref{thm:minimax}(ii) for a strictly convex cost, uniqueness included (Supplement Table~\ref{S-tab:newlean}); the case of a strictly convex loss and the uniqueness claim of Theorem~\ref{thm:partial-minimax} are proved on paper. The argument is the finite-group case of the Hunt--Stein theorem (Lehmann and Romano, 2005, Chapter~8). Because the law of the record does not depend on the labeling, it applies record by record, so it also covers policies that depend on the record. The comparison with the worst labeling also holds when $\ell$ and $C$ are only quasi-convex, as is the loss of missing a ceiling; the comparison with the average does not.")
    t = rep(t, r"As shown in the Online Supplement (Theorem~S5.4), tagging",
            r"As shown in Supplement Theorem~\ref{S-thm:partial}, tagging")
    t = rep(t, r"In the small-feedback equilibrium of Theorem~\ref{thm:inv-eq}(iv), each unit of aggregate feedback intensity $G(1) = \sum_j q_j$ raises equilibrium impact $\kappa$ by $\kappa_-^2(\bar{a} + 2A\kappa_-\sigma_\xi^2)/\sqrt{\Lambda_0} > 0$, creating a marginal dealer-inventory and price-dislocation externality $\lambda_{\mathrm{ext}} > 0$. If class $j \in \{\mathcal{H}, \mathcal{B}\}$ earns private value $b_j > 0$ per retained unit and imposes marginal feedback externality $\lambda_{\mathrm{ext}} \phi_j$, then",
            r"In the small-feedback equilibrium of Theorem~\ref{thm:inv-eq}(iv), each unit of aggregate feedback intensity $G(1) = \sum_j q_j$ raises equilibrium impact $\kappa$ by $\kappa_-^2(\bar{a} + 2A\kappa_-\sigma_\xi^2)/\sqrt{\Lambda_0} > 0$. Suppose the supervisor values a unit of feedback intensity, through the rise in impact and inventory risk it causes, at $\lambda_{\mathrm{ext}} > 0$, a parameter of its welfare criterion rather than an equilibrium object. If class $j \in \{\mathcal{H}, \mathcal{B}\}$ earns private value $b_j > 0$ per retained unit and adds $\phi_j$ to the feedback intensity, then")
    t = rep(t, r"\item[(i)] \emph{First-order welfare from inventory-equilibrium price impact.}",
            r"\item[(i)] \emph{Welfare weights from equilibrium impact.}")
    t = rep(t, r"so the quadratic distortion cost $k(D_0 - D)^2$ is exact at leading order.",
            r"so the quadratic distortion cost $k(\delta_0 - \delta)^2$ of Theorem~\ref{thm:paradox} is exact at leading order.")
    t = rep(t, r"Third, an audit trail linking accounts to beneficial owners preserves its full value $V_A$ regardless of $\gamma$.",
            r"Third, an audit trail linking accounts to beneficial owners preserves its full value $V_A$ regardless of $\gamma$. This ranking is built in, because the audit trail is assumed not to be gameable. What it needs is a stable link from accounts to an owner, which can be pseudonymous: the Consolidated Audit Trail, for example, keeps consistent anonymized customer identifiers after the 2025 exemption from reporting names, addresses and years of birth (Securities and Exchange Commission, 2025). Labels that firms assign to their own algorithms are the gameable kind. That a principal should rely less on a signal that agents can manipulate is close to Frankel and Kartik (2022) and Perez-Richet and Skreta (2022).")
    t = rep(t, r"Online Supplement Theorem~S15.4 proves", r"Supplement Theorem~\ref{S-thm:relabelgeneral} proves")
    a = t.index(PARADOX_START)
    b = t.index(PARADOX_END, a) + len(PARADOX_END)
    t = t[:a] + PARADOX_NEW + t[b:]
    # ---------------------------------------------------------------- Taiwan
    t = rep(t, r"\subsection{Illustrative empirical calibration: Taiwan Stock Exchange tagged flows}",
            r"\subsection{Illustrative empirical calibration: Taiwan Stock Exchange tagged flows}\label{sec:taiwan}")
    t = rep(t, r"using stock fixed effects and stationary date-block bootstrap confidence intervals (Table~\ref{tab:taiwan}).",
            r"using stock fixed effects and stationary date-block bootstrap confidence intervals (Table~\ref{tab:taiwan}). For each stock, the price deviation $x_t$ is the event-adjusted log price minus $\hat\beta$ times the log TAIEX, minus its trailing 60-day mean; it stands in for the model's pricing error. Each class's flow is its daily net buying scaled by the stock's average daily volume, so $\kappa$ is the response of $x$ to one day's average volume. The universe is the 300 four-digit stocks with the highest turnover over 2013--2016.")
    t = rep(t, r"(so only class composition is unknown) yields three sharp quantitative contrasts (Online Supplement, Section~S19):",
            r"(so only class composition is unknown) yields three quantitative contrasts (Supplement Section~\ref{S-app:barrier}). Both record lengths below compare feedback rules with each class's non-feedback flow held at its estimated law.")
    t = rep(t, r"Reaching $80\%$ power at a $5\%$ test size from prices alone requires at least $2.7 \times 10^9$ stock-years ($9.1 \times 10^6$ years across 300 independent stocks).",
            r"Reaching $80\%$ power at a $5\%$ test size from prices alone requires at least $2.7 \times 10^9$ years of one stock, or $9.1 \times 10^6$ years of all 300 stocks treated as independent.")
    t = rep(t, r"\item \emph{Uniform cut is pinned down by prices.} Over the exact same indistinguishable set, the effect of cutting all feedback uniformly lies within the tight band $[0.0014, 0.0019]$.",
            r"\item \emph{Uniform cut is pinned down by prices, given the grant.} Over the exact same indistinguishable set, the effect of cutting all feedback uniformly lies within the band $[0.0014, 0.0019]$.")
    t = rep(t, r"""\item \emph{Uniform cut is pinned down by prices, given the grant.} Over the exact same indistinguishable set, the effect of cutting all feedback uniformly lies within the band $[0.0014, 0.0019]$.
\end{enumerate}""",
            r"""\item \emph{Uniform cut is pinned down by prices, given the grant.} Over the exact same indistinguishable set, the effect of cutting all feedback uniformly lies within the band $[0.0014, 0.0019]$.
\end{enumerate}""" + TAIWAN_QUAL)
    t = rep(t, r"Two caveats discipline this calibration.", r"Two further caveats concern the data.")
    if round10.RES_A.exists():
        RA = json.loads(round10.RES_A.read_text())
        t = rep(t, round10.NOT_COMPUTED, round10.part_a_passage(RA) + round10.post_run_main(RA))
    if round10.RES_B.exists():
        second = (r"while the price-only comparisons let feedback memory vary with non-feedback flow held fixed.")
        t = rep(t, second, second + " " + round10.part_b_sentence(json.loads(round10.RES_B.read_text()),
                                                                   r"Table~\ref{tab:taiwan}"))
    t = rep(t, r"Second, as documented in Online Supplement Section~S6, a pre-registered out-of-sample reverse-causality diagnostic on 2019--2023 holdout data cannot rule out",
            r"Second, as documented in Supplement Section~\ref{S-sec:scope}, a pre-registered out-of-sample reverse-causality diagnostic on 2019--2023 holdout data cannot rule out")
    t = rep(t, r"Accordingly, these figures serve as an illustrative calibration",
            r"Positive feedback in foreign investors' daily flows, and the difficulty of separating it from prices responding to flows, are documented for Taiwan and other markets (Froot et al., 2001; Griffin et al., 2004; Richards, 2005). Accordingly, these figures serve as an illustrative calibration")
    t = rep(t, r"the same $(\Delta\eta)^{-(4K-2)}$ barrier operates with direct prudential significance.",
            r"the same $(\Delta\eta)^{-(4K-2)}$ barrier would apply with more prudential weight.")
    t = rep(t, r"aggregate price persistence $\sum_{j=1}^5 a_j = 0.97$.} \\",
            r"aggregate price persistence $\sum_{j=1}^5 a_j = 0.97$.} \\" + "\n" +
            r"\multicolumn{4}{@{}l}{\footnotesize Within-stock $R^2$: price equation $0.95$; rules $0.14$ (Foreign), $0.18$ (Trust) and $0.10$ (Dealers).} \\")
    # ---------------------------------------------------------------- conclusion
    t = rep(t, r"First, market-wide interventions (such as uniform feedback cuts or market-design changes calibrated to aggregate response) are statistically well-posed from public prices and are minimax-optimal when class identities are unverified.",
            r"First, market-wide interventions (such as uniform feedback cuts or market-design changes calibrated to aggregate response) are statistically well-posed from public prices, given the market's persistence and a bound on memory, and are minimax-optimal over labelings when class identities are unverified.")
    t = rep(t, r"durable targeted supervision requires owner-linked audit trails—such as",
            r"durable targeted supervision rests on owner-linked audit trails, which we assume cannot be gamed—such as")
    t = rep(t, r"Our passive sample-complexity bounds assume Gaussian (or quadratically regular) innovations and exclude bounded-support noise laws.",
            r"Our passive sample-complexity bounds assume Gaussian (or quadratically regular) innovations and exclude bounded-support noise laws. The surveillance result describes a best response to a fixed test, not an equilibrium between the supervisor and the traders. The Taiwan calibration grants the price-only supervisor the market's persistence and impact, and a registered test there did not establish that the tagged responses are feedback. Trader rules are fixed and respond to deviations from a public fundamental, and the classes in the calibration are investor types rather than algorithms.")
    # ---------------------------------------------------------------- declarations
    old_ai = r"All mathematical proofs, economic arguments, empirical calculations, and formal statements were independently verified and edited by the authors, who take full responsibility for the content of the publication."
    if CORRECTIONS_CHECKED_BY_FIRST_AUTHOR:
        new_ai = (r"The authors take full responsibility for the content of the publication. The first author read and "
                  r"checked the proofs, including those of Proposition~\ref{prop:interventions}(iii), Theorem~\ref{thm:minimax}(ii), Lemma~\ref{lem:micro}, "
                  r"Theorem~\ref{thm:paradox} and Supplement Propositions~\ref{S-prop:nearcrit} and~\ref{S-prop:hidegame} "
                  r"in their present form. Lean~4 checks certify only the formal statements listed in the Supplement's "
                  r"machine-check tables and in the repository; they do not certify the probabilistic steps, empirical "
                  r"validity or novelty.")
    else:
        new_ai = (r"The authors take full responsibility for the content of the publication. The first author read and "
                  r"checked the proofs of the results developed with AI assistance up to 21 November 2026. "
                  r"Proposition~\ref{prop:interventions}(iii), Theorem~\ref{thm:minimax}(ii), Lemma~\ref{lem:micro} and Theorem~\ref{thm:paradox} of this paper and "
                  r"Propositions~\ref{S-prop:nearcrit} and~\ref{S-prop:hidegame} of the Supplement, in their present form, "
                  r"were added or corrected with AI assistance on 21--22 November 2026 and have not yet been checked by "
                  r"the authors. Lean~4 checks certify only the formal statements listed in the Supplement's "
                  r"machine-check tables and in the repository; they do not certify the probabilistic steps, empirical "
                  r"validity or novelty.")
    t = rep(t, old_ai, new_ai)
    t = rep(t, r"to assist with literature cross-checking, numerical verification scripts, Lean~4 formalization coding, and language editing.",
            r"to assist with literature cross-checking, numerical verification scripts, Lean~4 formalization coding, drafting, and language editing.")
    # ---------------------------------------------------------------- appendix
    t = rep(t, r"Part~(ii) follows from Online Supplement Theorem~S4.3(i) applied to the closed loop in~(i).",
            r"Part~(ii) follows from Supplement Theorem~\ref{S-thm:minphase}(i) applied to the closed loop in~(i).")
    t = rep(t, r"\begin{proof}[Proof of Theorems~\ref{thm:minimax} and~\ref{thm:partial-minimax} and Corollary~\ref{cor:halt}]",
            HORIZON_PROOF + r"\begin{proof}[Proof of Theorems~\ref{thm:minimax} and~\ref{thm:partial-minimax} and Corollary~\ref{cor:halt}]")
    a = t.index(r"\begin{proof}[Proof of Theorems~\ref{thm:minimax} and~\ref{thm:partial-minimax} and Corollary~\ref{cor:halt}]")
    b = t.index(r"\end{proof}", a)
    t = t[:a] + t[a:b].replace(r"\sigma", r"\pi") + t[b:]
    t = rep(t, r"Valuing the marginal market-wide impact and inventory-risk externality at $\lambda_{\mathrm{ext}} > 0$ gives",
            r"Valuing a unit of feedback intensity at $\lambda_{\mathrm{ext}} > 0$, the supervisor's valuation of the rise in impact and inventory risk, gives")
    a = t.index(PARADOX_PROOF_START)
    b = t.index(PARADOX_PROOF_END, a) + len(PARADOX_PROOF_END)
    t = t[:a] + PARADOX_PROOF_NEW + t[b:]
    # ---------------------------------------------------------------- references
    t = add_references(t)
    # ---------------------------------------------------------------- labels shared with the supplement
    for old, new in LABELS.items():
        t = t.replace(r"\label{" + old + "}", r"\label{" + new + "}").replace(r"\ref{" + old + "}", r"\ref{" + new + "}")
    left = re.findall(r"Online Supplement[^.]{0,40}S\d", t)
    assert not left, left
    assert 'p = 6' not in t and 'p=6' not in t and 'equilibrium information' not in t
    return t


LABELS = {
    'thm:sufficiency': 'n:suff', 'thm:what-id': 'n:ident', 'thm:inv-eq': 'n:thm_inventory',
    'thm:eq-id': 'n:thm_eqreduced', 'prop:decision-suff': 'n:interv', 'thm:cost': 'n:cost',
    'thm:cheap': 'n:questions', 'cor:sep': 'n:sep', 'thm:smooth': 'n:univ', 'thm:recovery': 'n:shape',
    'thm:forecast-kl': 'n:dual', 'sec:forecast': 'n:irr_sec', 'prop:interventions': 'n:target',
    'cor:loss': 'n:decisionloss', 'thm:minimax': 'n:minimax', 'cor:halt': 'cor:robustuniform',
    'thm:partial-minimax': 'n:minimaxtags', 'thm:tags': 'n:disc', 'prop:relabeling': 'n:relabel',
    'thm:paradox': 'n:paradox',
}

NEW_REFS = [
    r"Bond, P., Goldstein, I., 2015. Government intervention and information aggregation by prices. \emph{Journal of Finance} 70(6), 2777--2812.",
    r"Bond, P., Goldstein, I., Prescott, E.S., 2010. Market-based corrective actions. \emph{Review of Financial Studies} 23(2), 781--820.",
    r"Chaboud, A.P., Chiquoine, B., Hjalmarsson, E., Vega, C., 2014. Rise of the machines: Algorithmic trading in the foreign exchange market. \emph{Journal of Finance} 69(5), 2045--2084.",
    r"Chetty, R., 2009. Sufficient statistics for welfare analysis: A bridge between structural and reduced-form methods. \emph{Annual Review of Economics} 1, 451--488.",
    r"Cutler, D.M., Poterba, J.M., Summers, L.H., 1990. Speculative dynamics and the role of feedback traders. \emph{American Economic Review} 80(2), 63--68.",
    r"De Long, J.B., Shleifer, A., Summers, L.H., Waldmann, R.J., 1990. Positive feedback investment strategies and destabilizing rational speculation. \emph{Journal of Finance} 45(2), 379--395.",
    r"Foucault, T., Moinas, S., Theissen, E., 2007. Does anonymity matter in electronic limit order markets? \emph{Review of Financial Studies} 20(5), 1707--1747.",
    r"Frankel, A., Kartik, N., 2019. Muddled information. \emph{Journal of Political Economy} 127(4), 1739--1776.",
    r"Frankel, A., Kartik, N., 2022. Improving information from manipulable data. \emph{Journal of the European Economic Association} 20(1), 79--115.",
    r"Froot, K.A., O'Connell, P.G.J., Seasholes, M.S., 2001. The portfolio flows of international investors. \emph{Journal of Financial Economics} 59(2), 151--193.",
    r"Grazzini, J., Richiardi, M., 2015. Estimation of ergodic agent-based models by simulated minimum distance. \emph{Journal of Economic Dynamics and Control} 51, 148--165.",
    r"Griffin, J.M., Nardari, F., Stulz, R.M., 2004. Are daily cross-border equity flows pushed or pulled? \emph{Review of Economics and Statistics} 86(3), 641--657.",
    r"Grossman, S.J., Miller, M.H., 1988. Liquidity and market structure. \emph{Journal of Finance} 43(3), 617--633.",
    r"Hendershott, T., Menkveld, A.J., 2014. Price pressures. \emph{Journal of Financial Economics} 114(3), 405--423.",
    r"Ho, T., Stoll, H.R., 1981. Optimal dealer pricing under transactions and return uncertainty. \emph{Journal of Financial Economics} 9(1), 47--73.",
    r"Khandani, A.E., Lo, A.W., 2011. What happened to the quants in August 2007? Evidence from factors and transactions data. \emph{Journal of Financial Markets} 14(1), 1--46.",
    r"Lehmann, E.L., Romano, J.P., 2005. \emph{Testing Statistical Hypotheses}, 3rd ed. Springer, New York.",
    r"Marschak, J., 1953. Economic measurements for policy and prediction. In: Hood, W.C., Koopmans, T.C.\ (Eds.), \emph{Studies in Econometric Method}. Cowles Commission Monograph 14. Wiley, New York, pp.\ 1--26.",
    r"Perez-Richet, E., Skreta, V., 2022. Test design under falsification. \emph{Econometrica} 90(3), 1109--1142.",
    r"Platt, D., 2020. A comparison of economic agent-based model calibration methods. \emph{Journal of Economic Dynamics and Control} 113, 103859.",
    r"Niroula, P., Niroula, P., Khatiwada, S., 2026a. What prices cannot tell a market supervisor: The cost of identifying trader groups and the value of class disclosure. Working paper, 5 November 2026, \url{https://github.com/Pratikn03/Fianince}.",
    r"Manski, C.F., 2000. Identification problems and decisions under ambiguity: Empirical analysis of treatment response and normative analysis of treatment choice. \emph{Journal of Econometrics} 95(2), 415--442.",
    r"Rothenberg, T.J., 1971. Identification in parametric models. \emph{Econometrica} 39(3), 577--591.",
    r"Richards, A., 2005. Big fish in small ponds: The trading behavior and price impact of foreign investors in Asian emerging equity markets. \emph{Journal of Financial and Quantitative Analysis} 40(1), 1--27.",
    r"Securities and Exchange Commission, 2025. Press release 2025-38, 10 February 2025: exemption from reporting the names, addresses and years of birth of natural persons to the Consolidated Audit Trail. \url{https://www.sec.gov/newsroom/press-releases/2025-38}.",
    r"Sentana, E., Wadhwani, S., 1992. Feedback traders and stock return autocorrelations: Evidence from a century of daily data. \emph{Economic Journal} 102(411), 415--425.",
    r"Stein, J.C., 2009. Presidential address: Sophisticated investors and market efficiency. \emph{Journal of Finance} 64(4), 1517--1548.",
]


def _key(item):
    s = re.sub(r'\\[a-zA-Z]+\s*', '', item)
    s = s.replace('\\"', '').replace("\\'", '').replace('{', '').replace('}', '').replace('\\', '')
    return s.lower()


def add_references(t):
    a = t.index(r"\begin{list}{}")
    a = t.index('\n', a) + 1
    b = t.index(r"\end{list}", a)
    body = t[a:b]
    items = [s.strip() for s in re.split(r'\n\s*\\item ', '\n' + body) if s.strip()]
    items += NEW_REFS
    items.sort(key=_key)
    new_body = '\n' + '\n\n'.join(r'\item ' + s for s in items) + '\n\n'
    return t[:a] + new_body + t[b:]


if __name__ == '__main__':
    out = build(SRC.read_text())
    OUT.write_text(out)
    print('wrote', OUT.name, len(out.splitlines()), 'lines')
