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

# Set to True only after the first author says he has read and checked Proposition 7.1(iii) and (iv), Theorem 7.3(ii), Lemma 7.7, Theorem 7.9 and
# Supplement Propositions S4.5 and S11.1 in their present form.
CORRECTIONS_CHECKED_BY_FIRST_AUTHOR = False


def rep(t, old, new, count=1):
    n = t.count(old)
    assert n == count, (old[:120], n, count)
    return t.replace(old, new)


ABSTRACT = (
    r"We study traders whose fixed rules feed a common pricing signal back into order flow. "
    r"In a linear market and a stationary inventory-dealer equilibrium, the aggregate kernel governs "
    r"public outcomes. In the Gaussian model, separating nearby trader types can require "
    r"$\Delta^{-(4K-2)}$ observations for $K$ types within spread $\Delta$. Under fixed price impact "
    r"and persistence, market-wide feedback cuts depend on an aggregate budget, while class-specific "
    r"halts generally need attribution. Uniform rules are minimax over unknown labelings. "
    r"A calibration to Taiwan's tagged institutional flows illustrates the distinction."
)

PARADOX_START = r"Even without account relabeling, an untagged algorithm that anticipates targeting"
PARADOX_END = r"verified class tags eliminate both crowding and costly defensive repositioning simultaneously."
PARADOX_NEW = r"""Even without account relabeling, an untagged algorithm that anticipates targeting can disguise itself by shifting its trading rule toward its neighbor's, at a cost to its own strategy. The next result gives what the supervisor learns when the algorithm best-responds to a fixed test.

\begin{theorem}[The surveillance paradox]\label{thm:paradox}
An untagged group chooses the distance $\delta \in [0, \delta_0]$ between its memory rate and its neighbor's; the neighbor and all other groups stay where they are. The supervisor tests the null that the group trades like its neighbor (one group in place of the two, with unknown memory and weight) at level $\alpha$ under every economy in the null. Detection triggers an inquiry that costs the group $L$, and moving costs it $k(\delta_0 - \delta)^2$, with $\delta_0, k, L > 0$. With $N$ observations, let $J$ be the divergence from the record with the group at distance $\delta$ to the closest record in the null. In this benchmark record experiment assume $J=cN\delta^n$ on the action set, with $c>0$ and $n>2$. The test has continuous power $P_{\mathrm{d}}(J)\ge\alpha$ with $P_{\mathrm{d}}(0)=\alpha$ and $0<\alpha<1/2$. Let $\delta^*$ be an optimal distance and $J^* = c N (\delta^*)^n$.
\begin{enumerate}
  \item[(i)] \emph{Hiding is never complete.} Against every such test, $\delta^* > 0$, and $(\delta^*)^{n-2} \ge 2 k^2 \delta_0^2 / (2^n L^2 c N)$ whenever $\delta^* \le \delta_0 / 3$.
  \item[(ii)] \emph{A good test forces crowding.} If the test's power satisfies $P_{\mathrm{d}}(J) - \alpha \ge \beta \min\{\sqrt{J}, \sqrt{\bar{J}}\}$ and the stakes are high ($L \beta \sqrt{\bar{J}} > k \delta_0^2$), then for every $N$,
  \[
    (\delta^*)^{n-2} \le \frac{4 k^2 \delta_0^2}{L^2 \beta^2 c N}.
  \]
  \item[(iii)] \emph{More data, less information.} Against such a test, for all large $N$, $\delta^* \asymp N^{-1/(n-2)}$ and the supervisor's information obeys $J^* \asymp N^{-2/(n-2)} \to 0$; this is $N^{-1}$ in the benchmark with $n=4$. The detection probability tends to $\alpha$, and the group's distortion cost $k(\delta_0 - \delta^*)^2$ tends to $k \delta_0^2$.
  \item[(iv)] \emph{Tag-based inquiry.} If a verified class tag supports an inquiry with probability independent of $\delta$, then $\delta^*=\delta_0$. The supervisor can estimate the group's rule from its tagged flow (Theorem~\ref{thm:tags}).
\end{enumerate}
\end{theorem}

The exponent depends on the comparator and observation contract. The record does not say which nearby memory is the neighbor's, so the null is composite. A single group with the pair's total weight and mean memory matches the kernel up to the spread of the two memories, which is of order $\delta^2$ in the kernel and $\delta^4$ in the divergence (Supplement Theorem~\ref{S-thm:merged}(ii) for probes and Proposition~\ref{S-prop:passive}(i) for passive prices; computed from the spectra, the fitted slope is $4.1$, Supplement Section~\ref{S-app:paradox}). A supervisor that knew the neighbor's memory and both weights would face a simple null with $n = 2$; then, against the Gaussian test with high stakes, hiding is complete once $N$ is large, and the record carries no information about the group. If several groups crowd together, $n$ is larger (numerically $8$ for a cluster of three), and the information falls more slowly. The spectral slope does not establish a finite-record power envelope. In a Gaussian shift experiment with a specified normal direction, a one-sided test satisfies (ii) with $\beta = \sqrt{2}\phi(z_\alpha)$ and $\bar{J} = z_\alpha^2 / 2$ (Appendix~\ref{app:proofs}).

Without tags, each new observation is more than offset by the crowding it provokes, and against a group that best-responds, supervision does not converge to knowledge of composition. The group pays for its invisibility with a distorted strategy: by Lemma~\ref{lem:micro}(ii), the cost $k(\delta_0 - \delta)^2$ is the leading-order profit loss of a Kalman-filtering desk that deviates from its optimal memory rate at fixed impact. Whether this is a failure depends on what the supervisor wants. If the conduct at $\delta_0$ is what it fears, the crowding is deterrence; what fails is learning, not necessarily welfare. This is the tension between acting on market information and preserving it (Bond et al., 2010; Bond and Goldstein, 2015), here for information about who trades rather than about fundamentals; Frankel and Kartik (2019) study how manipulation muddles a signal. The loss $L$ stands for the inquiry that detection triggers, for example a request to brokers for account records; without such an inquiry, detection would have no consequence (Theorem~\ref{thm:minimax}). The theorem describes a best response to a fixed test, not an equilibrium: the neighbor does not move and the supervisor does not adapt its test. When several untagged groups position strategically, Supplement Proposition~\ref{S-prop:hidegame}(iv) shows that in any Nash equilibrium with bounded nearest-neighbor distances, every group's asymptotic detection probability is at most $\alpha + k_g \limsup_N \Delta_g^2 / L_g$. Tag-based inquiries remove this incentive when their probability is independent of the memory choice."""

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

\emph{The Gaussian test.} In the limiting Gaussian experiment, let the null be a linear subspace and the alternative lie at distance $t$ from it. Assume a unit normal direction is known and every alternative has positive projection $t$ along it. Rejecting when that projection exceeds $z_\alpha=\Phi^{-1}(1-\alpha)$ has level $\alpha$ and power $\Phi(t-z_\alpha)$, and $J = t^2/2$. As a function of $t = \sqrt{2J}$ the power is convex on $[0, z_\alpha]$, so it lies above its tangent at zero: $P_{\mathrm{d}}(J) - \alpha \ge \phi(z_\alpha)\sqrt{2J}$ for $J \le z_\alpha^2/2$, and it is increasing beyond. The two bounds on $(\delta^*)^{n-2}$ in (i) and (ii), and the comparisons of costs behind them, are checked in Lean~4 for every exponent $n \ge 2$ (Supplement Table~\ref{S-tab:newlean}); Pinsker's inequality, unbiasedness and the power envelope enter there as hypotheses, and the rates in (iii) follow from the two bounds.
\end{proof}"""

UNIFORM_REMARK = r"""

\textbf{Information needed for a uniform cut.} A zero-memory group is observationally equivalent to persistence (Supplement Theorem~\ref{S-thm:merged}(i)). For known $(a,\kappa)$ and a memory bound $\bar r<1$, the omitted tail is at most $W\bar r^L/(1-\bar r)$. Summing noisy taps at logarithmic depth gives the budget to accuracy $\epsilon$ with order $\sigma^2\epsilon^{-2}\log(1/\epsilon)$ experiments. Certification of a post-policy ceiling also requires a model of the market's response."""

HORIZON_ITEM = r"""  \item[(iii)] \emph{Restriction by horizon.} Halting the feedback of every group whose memory lies below a cutoff $\hat r \in (0, 1)$ does not either. Under the conditions of Theorem~\ref{thm:cost}, for every $K \ge 2$ and all small $\Delta\eta > 0$, there exist two $K$-group economies with memories in $[\hat r - \Delta\eta, \hat r + 2\Delta\eta]$ whose merged measures match moments $0, \dots, 2K-2$, such that the restriction removes at least $\kappa W/K^2$ of the budget in one economy and nothing in the other, where $W$ is the total merged weight. Over a nonempty interval of ceilings $\bar{s}$, the restriction satisfies the ceiling in one economy and breaches it in the other; deciding between them from $N$ reset records with both errors at most $1/4$ requires $N \ge c \sigma^2 (\Delta\eta)^{-(4K-2)}$.

"""

HORIZON_PROOF = r"""\begin{proof}[Proof of Proposition~\ref{prop:interventions}(iii)]
Let $x_K < 1$ be the largest node of the $K$-point Gauss--Legendre rule on $[-1, 1]$, and place the hard pair of Theorem~\ref{thm:cost}, with a common persistence and total merged weight $W$, on $r_c + \Delta\eta[-1, 1]$ with $r_c = \hat r + (1 + x_K)\Delta\eta/2$. Its memories lie in $[\hat r - \Delta\eta, \hat r + 2\Delta\eta]$. The Gauss--Radau economy has an atom of weight $W/K^2$ at $r_c - \Delta\eta < \hat r$, because the endpoint weight of the $K$-point Gauss--Radau rule on $[-1, 1]$ is $2/K^2$. Every memory of the Gauss economy is at least $r_c - x_K\Delta\eta > \hat r$. Group $i$ contributes $\kappa q_i = \kappa w_i/(1 - r_i)$ to the budget, so the restriction removes at least $\kappa W/K^2$ in the Gauss--Radau economy and nothing in the Gauss economy. The budgets themselves, $a + \kappa\int (1 - r)^{-1}\,dM(r)$, differ by $O((\Delta\eta)^{2K-1})$, because the merged measures match moments $0, \dots, 2K-2$ and $(1 - r)^{-1}$ is smooth near $r_c$. For small $\Delta\eta$ the budgets after the restriction therefore differ by at least $\kappa W/(2K^2)$, and every ceiling between them is met in one economy and breached in the other. The record length is that of Theorem~\ref{thm:cost}(ii), which concerns the same pair.
\end{proof}

"""

TAIWAN_QUAL = r"""

Four qualifications apply. First, the range $[-0.028, 0.028]$ in item~2 fills the cap by construction: two classes can share one memory with large weights of opposite sign, which leaves the aggregate kernel unchanged, so the width is set by the cap on each class's contribution, not by the data (the extreme compositions the search finds have weights $-9.0$, $4.6$ and $4.7$). Weights restricted to one sign would exclude these compositions; we have not computed the range under that restriction. The fitted relabelings that satisfy the restrictions have identical kernels. Second, the tagged intervals in Table~\ref{tab:taiwan} assume that each class's feedback decays at the persistence of its own flow, while the price-only comparisons let feedback memory vary with non-feedback flow held fixed. Third, item~3 rests on the grant: the price-only supervisor is given the persistences $a_j$, the impact $\kappa$ and the non-feedback law, all estimated with the tagged flows; with feedback contributing $0.0017$ to a budget of $0.97$, separating the two from prices alone is the problem that Proposition~\ref{prop:interventions} assumes away. Fourth, the record lengths treat the 300 stocks as independent, for the calendar conversion. The common-date bootstrap allows cross-stock dependence. The panel's effective sample size is unresolved. An archived Gaussian diagnostic compares exact and Whittle divergence for selected alternatives. It supplies no uniform error bound over the search set. The dealers' estimated response is negative, so the calibrated economy lies outside the positive class used for the lower bounds; the computations here (Whittle rates, Pinsker's inequality, relabeling) do not need positivity."""


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



COMPOSITION_PROOFS = r"""\begin{proof}[Proof of Theorem~\ref{thm:cost}]
Let $n=2K-1$ and normalize the $K$-node Gauss--Legendre and left Gauss--Radau rules to mass one. Both integrate degree $n-1$ exactly. Their degree-$n$ moments differ because the monic polynomial $(s+1)\prod_{j>1}(s-s_j)^2$ vanishes at all Radau nodes and has positive integral, which the Gauss rule integrates exactly. Scale the nodes by $r_c+\Delta\eta s$ and masses by $W$. Taylor expansion gives $|\Delta k_m|\le 2W\binom{m}{n}(\Delta\eta)^n(r_c+\Delta\eta)^{m-n}$ for $m\ge n$, with zero difference before that and $|\Delta k_n|\asymp(\Delta\eta)^n$. In particular $\|\Delta k\|_1=O((\Delta\eta)^n)$ uniformly.

Write the innovation filter as $B_X(z)=[1-az-\kappa z\sum_{m\ge0}k_{X,m}z^m]^{-1}$ in the lag variable and the reset response as $h_X=\kappa B_X$. The uniform stability bound gives bounded $\ell^1$ norms of the filters by the geometric series for the inverse. Subtracting the inverse filters shows $\|h_1-h_0\|_2\le C\|\Delta k\|_1$; the first nonzero difference is $\kappa^2\Delta k_n$ at lag $n+1$. The reset KL is $N\|h_1-h_0\|_2^2/(2\sigma^2)$ for the observed taps. Both errors at most $1/4$ imply TV at least $1/2$ and KL at least $1/2$ by Pinsker.

For stationary prices the spectral ratio is $f_1/f_0=|B_1/B_0|^2=1+O((\Delta\eta)^n)$ uniformly, with spectra bounded above and away from zero. The leading ratio term is twice the real part of a nonzero analytic function on the disk which vanishes at zero: use the resolvent identity and the leading Taylor term of $\sum_m \Delta k_m z^m$, whose coefficient at $z^n$ is nonzero. Its real part cannot vanish identically on the unit circle: it is harmonic on the disk, so it would then vanish on the whole disk by the maximum principle, making the function an imaginary constant, which is zero because the function vanishes at zero. The integral of its square over the circle is therefore positive. Thus the Gaussian spectral integral of $(f_1/f_0)-1-\log(f_1/f_0)$ has exact order $(\Delta\eta)^{2n}$. For finite records the uniform ratio bound sandwiches the two Toeplitz covariance matrices, putting the eigenvalues of their relative covariance within $O((\Delta\eta)^n)$ of one. Summing the quadratic bound on $\lambda-1-\log\lambda$ gives KL $\le CT(\Delta\eta)^{2n}$, so the same testing argument applies.

For recovery, the impulse recursion inverts the first $2K$ kernel taps triangularly, with nonzero divisor $\kappa h_0=\kappa^2$. Averaging independent Gaussian responses gives tap errors $O_P(\sigma/\sqrt N)$ at fixed depth. Centering the kernel moments at $r_c$ and dividing moment $j$ by $(\Delta\eta)^j$ gives errors $O_P(\sigma/(\sqrt N(\Delta\eta)^n))$. On the separated class the ordered rescaled moment map is injective by the Vandermonde equations for the difference of two atomic measures. Its Jacobian is a nonsingular confluent Vandermonde with weights bounded away from zero. The inverse function theorem and compactness give a uniformly Lipschitz local inverse. On its domain the Prony reconstruction returns that inverse, giving the stated fixed-accuracy rate.
\end{proof}

\begin{proof}[Proof of Theorem~\ref{thm:cheap}]
The largest difference of $F_g$ between two positive measures of mass at most $\bar W$ with tap distance at most $\delta$ is the displayed modulus. To see this, enforce the norm constraint by infimizing $\delta\|c\|_2-c\cdot(k_1-k_0)$ over $c$. Exchange infimum and supremum by convex minimax on the weak-star compact pair of measure sets. The residual supremum is $\bar W\mathcal R(g-p_c)$, with $p_c(r)=\sum_{t<L}c_t r^t$. Two Gaussian means at tap distance below $2z_{1-\alpha}\sigma/\sqrt N$ have TV below $1-2\alpha$, so uniform coverage forces answer separation at most $2\epsilon$. Continuity of the modulus gives the boundary. For sufficiency center the residual range and use the affine tap estimate. Its worst-case bias is at most $\bar W\mathcal R(g-p_c)/2$ and its standard deviation is $\sigma\|c\|_2/\sqrt N$.

If the coefficients of $g$ belong to $\ell^2$, truncation gives uniform residual $O(\bar r^L)$ by Cauchy--Schwarz. Choose logarithmic depth to make it $O(\epsilon)$ with bounded coefficient norm. Conversely the necessary condition with $N=O(\sigma^2\epsilon^{-2})$ gives polynomial approximants with bounded coefficient norms and residual tending to zero. Pad their coefficients with zeros and extract a weakly convergent subsequence in $\ell^2$. Point evaluation on $[0,\bar r]$ is continuous on coefficient space, so the limit represents $g$. For (iii) compare zero mass with $c\delta_r$ where $c=d\sigma\sqrt{(1-r^2)/N}$, with $0<d<1-2\alpha$ and $d$ small enough that $c\le\bar W$. Even with all taps observed, the divergence of the averaged record is $N\sum_m c^2r^{2m}/(2\sigma^2)=d^2/2$, so by Pinsker's inequality the total variation is at most $d/2<1-2\alpha$, yet the answer separation $c\,|g(r)|$ is unbounded as $r\uparrow1$. This contradicts uniform coverage. The deterministic steps are checked in Lean~4 (\nolinkurl{PublicationRevision13.lean}; Supplement Table~\ref{S-tab:newlean}).
\end{proof}

\begin{proof}[Proof of Theorem~\ref{thm:recovery}]
Taylor expansion gives $k(z)=A\,\mathrm{diag}(\Delta^j)_{j=0}^{2K-1}\mu(z)+R_\Delta(z)$, where $\mu_j(z)=\sum_i w_i s_i^j$ and $A$ has the independent derivative columns divided by $j!$. The same injectivity and Jacobian argument as above gives a global lower Lipschitz constant for $\mu$ on the compact separated class: use local inversion near the diagonal, and compactness and injectivity away from it. Differentiating the Taylor remainder bounds its Lipschitz constant on the convex set $\mathcal{Z}$ by $O(\Delta^{2K})$; take $\Delta\le1$. For small $\Delta$, absorption gives $\|k(z)-k(z')\|\ge c\Delta^{2K-1}\|z-z'\|$. The triangular response inverse is Lipschitz on a bounded set containing the response class. Minimum distance therefore bounds the parameter error by $C\Delta^{-(2K-1)}$ times twice the Gaussian sample-mean noise norm. The Gaussian norm bound gives the stated tail probability. The deterministic steps are checked in Lean~4 (\nolinkurl{PublicationRevision13.lean}; Supplement Table~\ref{S-tab:newlean}).
\end{proof}

"""

POLICY_PROOFS = r"""\begin{proof}[Proof of Proposition~\ref{prop:interventions}(i)--(ii) and Corollary~\ref{cor:loss}]
Uniform scaling multiplies the feedback part of $S$ by $\theta$. For the halt, take the quadrature rules at the zeros of $p_K-cp_{K-1}$, where $p_j$ are orthonormal for the uniform probability on $[-1,1]$. For small $c$ the zeros stay simple and interior. The interpolatory rule integrates degree $2K-2$ exactly: divide by $p_K-cp_{K-1}$ and use orthogonality of the quotient of degree at most $K-2$. Products of the Lagrange polynomials show that their squared norms are the weights. Normalizing them to an orthonormal basis gives weight $1/\sum_{j<K}p_j(s)^2$ at a node $s$. As $c$ varies, a node cannot recur, since consecutive orthogonal polynomials have no common zero by the three-term recurrence. Each weight level set is finite, so two such rules have distinct largest weights. After shifting and scaling, Taylor expansion of $(1-r)^{-1}$ gives an $O((\Delta\eta)^{2K-1})$ difference in total feedback. The largest activities converge to the different largest masses divided by $1-r_c$, giving separated post-halt budgets for small spacing. The reset KL proof above applies to this moment-matched pair.

For the binary decision let $A$ be the event of choosing the halt. Its excess loss is $(bP_0(A)+cP_1(A^c))/2\ge \min(b,c)(1-\TV)/2$. Apply Pinsker and solve for the required length. For equal-covariance Gaussian records the equal-prior likelihood rule has each error $\Phi(-\sqrt{N}\|d\|/(2\tau))$; the normal tail bound gives the displayed risk bound. The deterministic steps are checked in Lean~4 (\nolinkurl{PublicationRevision13.lean}; Supplement Table~\ref{S-tab:newlean}).
\end{proof}

\begin{proof}[Proof of Theorem~\ref{thm:tags}]
The first two noiseless class-flow coordinates are $w_i h_0$ and $w_i(h_1+r_i h_0)$. Since $h_0=\kappa>0$ and $w_i$ is bounded below, sample averages of these and of the price taps estimate both parameters with error $O_P(N^{-1/2})$ uniformly, using ratios on an event where denominators stay bounded away from zero. This suffices for fixed weight accuracy and for the specified shrinking rate accuracy. In an interior ball choose two rate vectors separated by more than twice the target, with identical weights. Their physical rates differ by $O(\Delta\eta)$, and the finite observed means differ by $O(\Delta\eta)$ by smoothness. Thus the Gaussian two-point bound requires order $(\Delta\eta)^{-2}$ tagged experiments. The untagged weight comparison follows from Theorem~\ref{thm:cost}. The deterministic steps are checked in Lean~4 (\nolinkurl{PublicationRevision13.lean}; Supplement Table~\ref{S-tab:newlean}).
\end{proof}

"""


INSTRUMENT_THEOREM = r"""

At fixed memories, let a desk choose a nonnegative scale $q$ for the normalized filter $y_t=(1-r)\sum_{j\ge0}r^j x_{t-1-j}$ of a centered stationary Gaussian reference price signal. At revision dates spaced $h$ periods apart it holds its exposure until the next revision. Its perceived expected return for period $j$ of that exposure is $\beta \rho^j y_t$ for $j=0,\ldots,h-1$, with common $\beta,b>0$ and $0\le\rho\le1$. The desk uses the reference covariance to evaluate risk and volume. The parameters $\beta,b,\rho$ describe preferences and beliefs and are given to the observer. Write $V=\operatorname{Var}(y_t)$, $D_h=\Var(y_t-y_{t-h})$, $T_h=h^{-1}\sqrt{2D_h/\pi}$, and $A_h=h^{-1}\sum_{j<h}\rho^j$. Per-date perceived gain less risk and trading costs is
\[
 (\beta A_h V-\tau T_h)q-\tfrac12(bV+\nu D_h/h)q^2,
 \qquad q\ge0,\quad qT_h\le c .
\]
Here $\tau$ charges expected traded volume and $\nu$ charges squared changes at revision dates. Allow $c=\infty$. A group consists of desks with the same memory. If $q^0(r)>0$ is baseline scale per desk and $q^1(r)$ is its policy scale, the reduction at fixed $(a,\kappa)$ is $\kappa F_g(M)$ for $g(r)=(1-q^1(r)/q^0(r))/(1-r)$. With scheduled revisions the relevant quantity is the response to a constant signal, averaged over the revision cycle.

\begin{instrumentthm}[Derived incidence of price and quantity instruments]\label{thm:instruments}
Assume $0<\bar r<1$, memories in $[0,\bar r]$, a bounded total merged weight, and known $\kappa$ in the tap experiment. The reference covariances satisfy a uniform geometric decay bound and the spectrum is uniformly positive. The benchmark experiment uses Gaussian taps and an independent reference sample as in Theorem~\ref{thm:cheap}. A passive alternative uses a single observed stationary pricing-error record from \eqref{eq:baseline}, with known $a$, $S\le\bar S<1$ and unknown innovation variance bounded above and away from zero. Under this alternative the desk uses the pre-policy price law as its reference.
\begin{enumerate}
\item[(a)] \emph{Trading costs.} With $h=1,\ \tau=0,\ c=\infty$, imposing a sufficiently small quadratic charge from zero gives a square-summable Taylor series for $g$. At logarithmic tap depth the reduction is estimable to error $O_P(n^{-1/2}+\sigma N^{-1/2})$. The passive alternative gives error $O_P(n^{-1/2})$ without a separate reference sample, taps, or knowledge of $\kappa$. A proportional transaction tax can fail the parametric criterion even with every desk active: for white-noise reference prices its active incidence is $1-q^1/q^0=d\sqrt{1+r}$ for a positive tax multiplier $d$.
\item[(b)] \emph{Scheduled revisions.} Changing the schedule from daily to every $h$ periods at a common small $\nu$, with $\tau=0$ and no cap, gives a square-summable term in $g$ plus $(1-A_h)/(1-r)$. The analytic term is estimable at the rates in (a). When $\rho=1$ this is the whole effect. Otherwise the second term needs the initial aggregate feedback budget. The signed reduction can be negative. The response concerns scheduled holdings. A cancellation constraint for orders resting in a book requires an execution model.
\item[(c)] \emph{Exit.} Under a proportional tax, a transversal zero of $\beta V-\tau T_1$ at an interior memory gives a kink in $g$. For the reset model of Theorem~\ref{thm:cost}, with a common reference law, there are moment-matched $K$-group alternatives near the threshold with budget reductions separated by order $\Delta\eta$. In one economy a desk type exits and in the other all types remain active. To distinguish these decisions, or estimate the reduction at a sufficiently small constant times $\Delta\eta$, requires $N\ge c_*\sigma^2(\Delta\eta)^{-(4K-2)}$ at fixed error probabilities below one quarter.
\item[(d)] \emph{Turnover caps.} With daily revisions, when a positive per-desk cap crosses smooth unconstrained turnover transversally, $g$ has a kink. The lower bounds in (c) apply to the reduction and to deciding whether the cap binds. The gap is of order $\Delta\eta$ for both types of continuous threshold.
\end{enumerate}
\end{instrumentthm}
"""

INSTRUMENT_PROOF = r"""\begin{proof}[Proof of Theorem~\ref{thm:instruments}]
Concavity gives $q=\min\{c/T_h,(\beta A_hV-\tau T_h)_+/(bV+\nu D_h/h)\}$. At revision dates the conditional perceived payoff and the quadratic risk cost scale with $V$, while Gaussian changes give expected absolute volume $qT_h$ per date. A constant signal produces constant $y$, so the ratio of scales gives the stated budget formula after aggregation.

Write $\gamma_j=\E[x_t x_{t-j}]$, $B(z)=\sum_{j\in\mathbb Z}\gamma_j z^{|j|}$,
$B_h(z)=\sum_{j\in\mathbb Z}\gamma_{j+h} z^{|j|}$, and $C_h(z)=2(B(z)-B_h(z))/(1-z)$. Summing by the difference of the filter indices gives $V=(1-r)B(r)/(1+r)$ and $D_h/V=(1-r)C_h(r)/B(r)$. The geometric bound extends the series past the unit circle. Since $B(1)=B_h(1)$, $C_h$ extends there too. The real part of $B$ is uniformly positive on the circle by the spectral bound, and hence in the disk. For the quadratic charge from zero,
\[
 g=\frac{\nu C_1}{bB+\nu(1-r)C_1}.
\]
For scheduled revisions, division by the old scale gives
\[
 g=\frac{1-A_h}{1-r}+
 \frac{A_h\nu(C_h/h-C_1)}{bB+\nu(1-r)C_h/h}.
\]
Small $\nu$ keeps both denominators bounded away from zero throughout the disk. The analytic terms have uniformly bounded square-summable Taylor coefficients. For a white-noise reference with variance $\gamma_0$, $T_1/V=2\sqrt{(1+r)/(\pi\gamma_0)}$. Thus $d=2\tau/(\beta\sqrt{\pi\gamma_0})$ in (a). The analytic continuation from an active interval grows like $(1-r)^{-1}$, whereas a square-summable Taylor series is bounded by its coefficient norm times $(1-r^2)^{-1/2}$. The same argument applies to the first term in (b) when $A_h<1$.

For the plug-in estimate, Wick's formula bounds the variance of each sample covariance up to lag $\lfloor n/2\rfloor$ by $C/n$. Summing errors with geometrically decaying weights on $[0,\bar r]$ gives uniform error $O_P(n^{-1/2})$ for the analytic term, after flooring denominators. Fit a degree-$<L$ polynomial to it in uniform norm with a known coefficient-norm bound. The truncated true series is feasible with error $O(\bar r^L)$. The resulting integrated bias is bounded by total mass times $O_P(n^{-1/2}+\bar r^L)$. Given the independent reference record, the tap statistic's variance is $O(\sigma^2/N)$ by the norm bound. Take logarithmic depth to make the tail no larger than the sampling errors.


In the passive alternative write $J(z)=\kappa\sum_{m\ge0}k_mz^m$ and $Q(z)=1-z(a+J(z))$. The memory and stability margins bound $Q$ away from zero on a disk larger than the unit disk and yield uniform geometric covariance decay. The stationary spectrum is $f=\sigma^2/|Q|^2$ in the covariance-series normalization. With $\ell_j$ the positive Fourier coefficients of $\log f$ under $z=e^{-i\omega}$ and $Q(0)=1$,
\[
 Q(z)=\exp\{-\textstyle\sum_{j\ge1}\ell_j z^j\},\qquad J(z)=(1-Q(z))/z-a .
\]
The constant coefficient absorbs the variance scale. A covariance series estimated to logarithmic lag depth has uniform error $O_P(\log n/\sqrt n)$, so linearizing its log leaves an $o_P(n^{-1/2})$ remainder. Each linear Fourier coefficient is a Gaussian quadratic form whose squared matrix Frobenius norm is bounded by $C/n$ times the squared sum of its Fourier weights. Parseval bounds the weights of $e^{ij\omega}/f$ uniformly in $j$. Geometric summation on any interior circle gives $\|\hat J-J\|_s=O_P(n^{-1/2})$.

Estimate $g$ from the same sample covariances. The analytic terms extend uniformly to a disk larger than the unit disk, so their coefficients have a uniform weighted sum bound $\sum_m R^m|c_m|\le B$ for some $R>1$. Fit the pilot at logarithmic depth under that bound. Its fitted polynomial approximates $g$ on the memory interval with $O_P(n^{-1/2})$ error by the preceding approximation argument. Choose $R^{-1}<s<1$. Cauchy's estimate gives $|\sum_m\hat c_m(\hat J_m-J_m)|\le B\|\hat J-J\|_s$. Integrating the weight error costs at most $\kappa M([0,\bar r])\|\hat g-g\|_\infty$. These pathwise bounds allow both fits to use the same observations. Supplement Section~\ref{S-app:passiveincidence} gives details.

At an interior transversal exit or binding point $r_*$, the positive part gives a nonzero jump $J$ of the one-sided derivative of $g$. Locally $g(r)=g(r_*)+g'_-(r-r_*)+J(r-r_*)_++O((r-r_*)^2)$. Reflect the Gauss--Legendre and left Gauss--Radau pair of Theorem~\ref{thm:cost} and place it so that only the Radau endpoint lies on the clipped side, at distance $u\Delta\eta$ for a fixed $u>0$. A reflection of the construction for Proposition~\ref{prop:interventions}(iii) gives the opposite orientation if needed. The affine terms cancel, and the lone endpoint generates a nonzero term of magnitude $|J|Wu\Delta\eta/K^2$. The quadratic remainder is $O((\Delta\eta)^2)$. The common reference record carries no additional information about the pair. The reset KL is $O(N(\Delta\eta)^{4K-2}/\sigma^2)$ from moment cancellation. Applying the same two-point test to the binary decision or to estimates with disjoint accuracy intervals proves the bounds. For caps, the policy scale is $\min(q^0,c/T_1)$ and the same derivative jump follows at a transversal binding point.
\end{proof}

"""
def build(text):
    t = reletter(text)
    # ---------------------------------------------------------------- preamble and front matter
    t = rep(t, "\\usepackage{fancyhdr}\n\\usepackage{hyperref}\n",
            "\\usepackage{fancyhdr}\n\\usepackage{xr-hyper}\n\\usepackage{hyperref}\n"
            "\\externaldocument[S-]{Paper1_JEDC_online_supplement}\n"
            "\\graphicspath{{../paper1_core/}{../paper1_note/}}\n")
    t = rep(t, "\\linespread{1.12}\n", "\\linespread{1.08}\n\\emergencystretch=3em\n")
    t = re.sub(r"(\\begin\{abstract\}\n\\noindent\n).*?(\n\\end\{abstract\})",
               lambda m: m.group(1) + ABSTRACT + m.group(2), t, count=1, flags=re.S)
    t = rep(t, r"\noindent\textbf{Online Supplement and Replication:} Technical lemmas,",
            r"\noindent\textbf{Online Supplement and Replication:} References of the form ``Supplement Theorem~S4.1'' are to the Online Supplement, which states every result in full; the full working paper (Niroula et al., 2026d) collects further results on the feedback model. Technical lemmas,")
    t = rep(t, r"\textbf{Funding and competing interests.}",
            r"\textbf{Related manuscripts.} An earlier working paper of the same authors (Niroula et al., 2026a, dated 5 November 2026) studied the same model; this article supersedes it. The earlier paper, the companion note (Niroula et al., 2026c) and the full working paper (Niroula et al., 2026d) are in the repository cited below.\par\medskip" + "\n\n" + r"\textbf{Funding and competing interests.}")
    t = rep(t, "\\newtheorem{theorem}{Theorem}[section]\n",
            "\\newtheorem{theorem}{Theorem}[section]\n"
            "\\newtheorem{instrumentthm}{Theorem}\n"
            "\\renewcommand{\\theinstrumentthm}{\\thetheorem(iv)}\n")
    # ---------------------------------------------------------------- introduction
    t = rep(t, r"In a Gaussian feedback market, the Kullback--Leibler divergence between two candidate populations equals half the cumulative excess mean-squared forecast error from confusing them (Theorem~\ref{thm:forecast-kl}); hence composition",
            r"In a Gaussian feedback market, the Kullback--Leibler divergence between two candidate populations equals half the cumulative excess forecast MSE divided by innovation variance (Theorem~\ref{thm:forecast-kl}, the Gaussian chain rule stated in market terms); composition")
    t = rep(t, r"Because prices cannot distinguish label permutations, a uniform cut across all feedback activity weakly dominates every price-based policy against the worst labeling consistent with the record for any convex loss and label-symmetric cost—and is the unique minimax supervisory policy whenever the cost is strictly convex (Theorem~\ref{thm:minimax}).",
            r"Because prices cannot distinguish label permutations, a uniform cut across all feedback activity does at least as well as every price-based policy against the worst labeling consistent with the record, for any convex loss and label-symmetric cost: it is minimax over labelings, Bayes under an exchangeable prior, and, when the cost is continuous and strictly convex, the unique minimax policy (Theorem~\ref{thm:minimax}). With known persistence, impact, a memory bound and tap measurements, the pre-policy budget can be estimated (Section~\ref{sec:supervision}).")
    t = rep(t, r"Only an owner-linked audit trail that ties accounts to beneficial owners retains its value.",
            r"An owner-linked audit trail that ties accounts to beneficial owners keeps its value, because we assume that it cannot be gamed.")
    t = rep(t, r"\item \emph{The surveillance paradox.} Without class tags, an untagged algorithm facing a level-$\alpha$ detection test crowds its memory rate toward its neighbor as the supervisor's data record $N$ grows. Whenever the identification divergence scales as $c N D^p$ with $p > 2$ (including $p=4$ for symmetric splitting and $p=6$ for moment-matched two-group hiding), crowding more than offsets the added data: the supervisor's equilibrium information falls to zero at rate $N^{-2/(p-2)}$ (e.g., $N^{-1/2}$ for $p=6$), detection probability collapses to the false-alarm rate $\alpha$, and the trader incurs a permanent strategy distortion cost (Theorem~\ref{thm:paradox}). Class tags eliminate this crowding.",
            r"\item \emph{The surveillance paradox.} In the fixed-test game, a high-stakes untagged algorithm facing a test with the required power envelope crowds its memory rate toward its neighbor as the supervisor's record $N$ grows. Against the closest economy in which it trades like its neighbor, the divergence is of order $N\delta^4$ in the distance $\delta$, so crowding more than offsets the added data: when the algorithm best-responds, the supervisor's information about it falls like $N^{-1}$, detection collapses to the false-alarm rate $\alpha$, and the trader bears a permanent strategy distortion (Theorem~\ref{thm:paradox}). Memory-independent tag-based inquiries remove this incentive.")
    t = rep(t, r"Our contribution is economic: we show that kernel sufficiency survives endogenous inventory-equilibrium pricing; establish the exact equivalence between supervisory identification and forecast loss in a feedback market; prove the minimax optimality of uniform (and group-uniform) supervisory policies; solve the strategic relabeling disclosure game comparing class tags to owner-linked audit trails; and derive the negative equilibrium identification rate of the surveillance paradox.",
            r"That market-wide policies need only a reduced-form aggregate while targeted ones need structure is Marschak's maxim and the logic of sufficient statistics for policy (Marschak, 1953; Chetty, 2009); what we add is the price of the structure in a feedback market. Our contribution is economic: we show that kernel sufficiency survives endogenous inventory-equilibrium pricing, where dealers' anticipation over-weights slow memories; characterize which linear questions about the population prices answer cheaply; prove the minimax optimality of uniform (and group-uniform) supervisory policies over labelings; solve the strategic relabeling disclosure game comparing class tags to owner-linked audit trails; and derive the rate at which an algorithm that best-responds to surveillance degrades what the supervisor learns. The equivalence between detection and forecast loss (Theorem~\ref{thm:forecast-kl}) is the Gaussian chain rule applied to a feedback market; we use it to explain the separation, not as a new statistical result.")
    t = rep(t, r"Tagged flows carry $4.7 \times 10^5$ times more information per stock-day about class composition than prices alone. Over all compositions statistically indistinguishable from the full panel price record, the effect of a uniform feedback cut is tightly pinned to $[0.0014, 0.0019]$, whereas the effect of halting foreign feedback spans $[-0.028, 0.028]$.",
            r"With each class's non-feedback flow held at its estimated law, tagged flows carry $4.7 \times 10^5$ times more information per stock-day about class composition than prices alone. Granting the price-only observer the market's persistence, impact and non-feedback order flow, a multistart search under a spectral-rate constraint found uniform-cut effects from $0.0014$ to $0.0019$. The effect of halting foreign feedback is not identified: relabeling alone leaves each class's estimated contribution possible, and classes with offsetting weights fill any cap placed on each class's contribution. With every class's weight nonnegative, the search found examples from zero to nearly all of the total feedback, and the tagged estimate survives decoupling feedback from each class's flow persistence (Section~\ref{sec:taiwan}). The registered foreign-flow holdout supported incremental prediction; its reverse-causality diagnostic left the causal feedback interpretation unresolved.")
    t = rep(t, r"our results establish precisely which features of a trader population are recoverable from prices and at what statistical cost.",
            r"our results establish precisely which features of a trader population are recoverable from prices and at what statistical cost. Feedback traders are central to models of destabilizing speculation and of return autocorrelation (De Long et al., 1990; Cutler et al., 1990; Sentana and Wadhwani, 1992), and simulation-based estimation of agent-based models (Grazzini and Richiardi, 2015; Platt, 2020) faces the same identification question in nonlinear models. Our identification result is global (Theorem~\ref{thm:what-id}); where memories collide, the information matrix of Rothenberg (1971) is singular, and Theorems~\ref{thm:cost} and~\ref{thm:recovery} give the rate at which identification weakens near a collision. Our minimax results are decisions under ambiguity in the sense of Manski (2000).")
    t = rep(t, r"Our setting isolates a distinct mechanism: under a common public signal, identity is irrelevant for price discovery and forecasting, yet essential for assigning targeted supervisory interventions.",
            r"Our setting isolates a distinct mechanism: under a common public signal, identity is irrelevant for price discovery and forecasting, yet essential for assigning targeted supervisory interventions. Inventory-based price impact goes back to Ho and Stoll (1981) and Grossman and Miller (1988), and Hendershott and Menkveld (2014) measure it. Crowding among algorithmic and quantitative strategies is documented by Chaboud et al.\ (2014) and Khandani and Lo (2011) and analyzed by Stein (2009); pre-trade anonymity in limit-order markets, which concerns who quotes rather than who trades on feedback, is studied by Foucault et al.\ (2007).")
    t = rep(t, r"provides a formal rationale for that architecture: market-wide remedies require only prices, targeted restrictions require class records, and relabeling incentives necessitate owner-linked audit trails.",
            r"provides a formal rationale for that architecture: market-wide remedies require only prices, targeted restrictions require class records, and cheap relabeling favors owner-linked audit trails. Acting on market information can degrade it (Bond et al., 2010; Bond and Goldstein, 2015), and manipulation muddles the signals a principal relies on (Frankel and Kartik, 2019, 2022; Perez-Richet and Skreta, 2022).")
    t = rep(t, r"whereas compositional weights require $\Delta^{-(4K-2)}$ observations (Theorem~\ref{thm:cheap} and Corollary~\ref{cor:sep}).",
            r"whereas compositional weights require $\Delta^{-(4K-2)}$ observations (Theorem~\ref{thm:cheap} and Corollary~\ref{cor:sep}). The same lower bound can apply when an enforceable horizon cutoff replaces a class label (Proposition~\ref{prop:interventions}(iii)). Derived quadratic costs admit parametric estimation from a passive Gaussian pricing-error record with a known anchor. Proportional taxes can fail even before exit, and exit and binding caps give lower bounds at shrinking accuracy (Theorem~\ref{thm:instruments}).")
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
            r"form a pair requiring $N \ge c \sigma^2 (\Delta\eta)^{-(4K-2)}$ reset experiments to distinguish, each recording the equilibrium price response to a probe with Gaussian noise of variance $\sigma^2$.")
    t = rep(t, r"The proofs of Theorems~\ref{thm:inv-eq} and~\ref{thm:eq-id} are given in Appendix~\ref{app:proofs}.",
            r"Part~(iv) uses the reset contract of Section~\ref{sec:cost}, a benchmark for what data can reveal rather than a description of a running market. The proofs of Theorems~\ref{thm:inv-eq} and~\ref{thm:eq-id} are given in Appendix~\ref{app:proofs}.")
    # ---------------------------------------------------------------- the price of composition
    t = rep(t, r"The proofs of parts (i)--(iii) appear in the Online Supplement (Theorems~S4.1, S4.2, and~S4.4).",
            r"Appendix~\ref{app:proofs} gives the argument. Supplement Theorems~\ref{S-prop:passive}, \ref{S-thm:kcohort} and~\ref{S-prop:esprit} give further details.")
    t = rep(t, r"Gaussian news is the least-favorable innovation law: for any regular non-Gaussian news law whose location divergence is quadratically bounded (such as Laplace innovations), the exponent $4K-2$ is unchanged (Online Supplement, Section~S4).",
            r"A global quadratic bound on the location KL of a news law can give the same lower-bound order in a sequential Gaussian-style comparison with common observed initialization and a uniform moment bound. The constant then uses that global bound.")
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
            r"Entries substitute the asymptotic KL rate for finite-record KL per observation. They are model-based horizon benchmarks.}")
    t = rep(t, r"Theorem~\ref{thm:cheap} (Online Supplement, Theorem~S10.1 and Proposition~S10.2) specializes",
            r"Theorem~\ref{thm:cheap} (Supplement Theorem~\ref{S-thm:questions} and Proposition~\ref{S-prop:parametric}) specializes")
    t = rep(t, r"matching the $\Delta^{-(4K-2)}$ sample order of Theorem~\ref{thm:smooth} (Online Supplement, Section~S18).",
            r"matching the $\Delta^{-(4K-2)}$ sample order of Theorem~\ref{thm:smooth} (Supplement Section~\ref{S-app:incoming}). The estimator is an exact global minimizer over $\mathcal{Z}$, which is not convex; the theorem gives no algorithm that finds it.")
    # ---------------------------------------------------------------- forecasting
    t = rep(t, r"The next theorem provides the exact information-theoretic link: in a Gaussian feedback market, the information a price record carries about two competing populations is literally proportional to the cumulative forecast loss from mistaking one for the other.",
            r"The next theorem states the Gaussian chain rule in market terms: in a Gaussian feedback market, the information a price record carries about two competing populations equals half the cumulative excess forecast MSE divided by innovation variance. Populations that forecast alike are therefore hard to tell apart, and a uniform cut depends only on what forecasts reveal.")
    t = rep(t, r"(Online Supplement, Theorems~S18.1 and~S18.2)", r"(Supplement Theorems~\ref{S-n:irr} and~\ref{S-n:uniformlog})")
    # ---------------------------------------------------------------- supervision
    t = rep(t, r"""\end{enumerate}
\end{proposition}

\begin{corollary}[Expected loss from weakly identified targeting]""",
            HORIZON_ITEM + r"""\end{enumerate}
\end{proposition}""" + UNIFORM_REMARK + INSTRUMENT_THEOREM + r"""

\begin{corollary}[Expected loss from weakly identified targeting]""")
    t = rep(t, r"Figure~\ref{fig:intervention} illustrates this contrast in a two-class economy: halting the largest class produces qualitatively opposite prudential outcomes across nearly indistinguishable economies, whereas a single verified class report collapses decision error by six orders of magnitude in sample size.",
            r"Figure~\ref{fig:intervention} illustrates this contrast in a two-class economy and an illustrative measurement experiment: halting the largest class produces qualitatively opposite prudential outcomes across nearly indistinguishable economies, whereas verified class reports cut the sample needed for a $5\%$ error by six orders of magnitude.")
    t = rep(t, r"\includegraphics[width=\linewidth]{fig2.png}", r"\includegraphics[width=.87\linewidth]{fig_intervention_revision.pdf}")
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
            r"The proofs of Theorems~\ref{thm:minimax} and~\ref{thm:partial-minimax} and Corollary~\ref{cor:halt} are short and self-contained (Appendix~\ref{app:proofs}). Supplement Table~\ref{S-tab:newlean} lists formal declarations for the averaging inequalities and uniqueness given two minimizers under strict cost convexity. Existence on the compact policy set and the additional strict-loss and partial-tag cases are proved on paper. The argument is the finite-group case of the Hunt--Stein theorem (Lehmann and Romano, 2005, Chapter~8). For price-dependent policies, integrating the permutation-average inequality under the common record law gives dominance in worst-case expected loss.")
    t = rep(t, r"As shown in the Online Supplement (Theorem~S5.4), tagging",
            r"As shown in Supplement Theorem~\ref{S-thm:partial}, tagging")
    t = rep(t, r"In the small-feedback equilibrium of Theorem~\ref{thm:inv-eq}(iv), each unit of aggregate feedback intensity $G(1) = \sum_j q_j$ raises equilibrium impact $\kappa$ by $\kappa_-^2(\bar{a} + 2A\kappa_-\sigma_\xi^2)/\sqrt{\Lambda_0} > 0$, creating a marginal dealer-inventory and price-dislocation externality $\lambda_{\mathrm{ext}} > 0$. If class $j \in \{\mathcal{H}, \mathcal{B}\}$ earns private value $b_j > 0$ per retained unit and imposes marginal feedback externality $\lambda_{\mathrm{ext}} \phi_j$, then",
            r"In the small-feedback equilibrium of Theorem~\ref{thm:inv-eq}(iv), each unit of aggregate feedback intensity $G(1) = \sum_j q_j$ raises equilibrium impact $\kappa$ by $\kappa_-^2(\bar{a} + 2A\kappa_-\sigma_\xi^2)/\sqrt{\Lambda_0} > 0$. Suppose the supervisor values a unit of feedback intensity, through the rise in impact and inventory risk it causes, at $\lambda_{\mathrm{ext}} > 0$, a parameter of its welfare criterion rather than an equilibrium object. If class $j \in \{\mathcal{H}, \mathcal{B}\}$ earns private value $b_j > 0$ per retained unit and adds $\phi_j$ to the feedback intensity, then")
    t = rep(t, r"\item[(i)] \emph{First-order welfare from inventory-equilibrium price impact.}",
            r"\item[(i)] \emph{Welfare weights from equilibrium impact.}")
    t = rep(t, r"Third, an audit trail linking accounts to beneficial owners preserves its full value $V_A$ regardless of $\gamma$.",
            r"Third, an audit trail linking accounts to beneficial owners preserves its full value $V_A$ regardless of $\gamma$. This ranking is built in, because the audit trail is assumed not to be gameable. The Consolidated Audit Trail illustrates stable anonymized customer IDs (Securities and Exchange Commission, 2025). Identifying the relevant beneficial owner or algorithm and preventing routing through another owner require further assumptions. Labels that firms assign to their own algorithms are the gameable kind. That a principal should rely less on a signal that agents can manipulate is close to Frankel and Kartik (2022) and Perez-Richet and Skreta (2022).")
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
            r"(so only class composition is unknown) yields three quantitative contrasts (Supplement Section~\ref{S-app:barrier}). The price and tagged records are compared to separately optimized single-memory candidates with each class's non-feedback flow held at its estimated law.")
    t = rep(t, r"Reaching $80\%$ power at a $5\%$ test size from prices alone requires at least $2.7 \times 10^9$ stock-years ($9.1 \times 10^6$ years across 300 independent stocks).",
            r"Using the rate as KL per stock-day gives a horizon proxy of $2.7 \times 10^9$ years for one stock at $80\%$ power and $5\%$ size, or $9.1 \times 10^6$ years under independent stocks. No finite-record KL bound is supplied for this calibration.")
    t = rep(t, r"\item \emph{Uniform cut is pinned down by prices.} Over the exact same indistinguishable set, the effect of cutting all feedback uniformly lies within the tight band $[0.0014, 0.0019]$.",
            r"\item \emph{Uniform feedback reduction.} In the same search, the endpoints found for setting all feedback to zero are $[0.0014, 0.0019]$. The search supplies examples and leaves the outer range open.")
    t = rep(t, r"""\item \emph{Uniform feedback reduction.} In the same search, the endpoints found for setting all feedback to zero are $[0.0014, 0.0019]$. The search supplies examples and leaves the outer range open.
\end{enumerate}""",
            r"""\item \emph{Uniform feedback reduction.} In the same search, the endpoints found for setting all feedback to zero are $[0.0014, 0.0019]$. The search supplies examples and leaves the outer range open.
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
            r"Second, as documented in Supplement Section~\ref{S-sec:scope}, the separately registered P1T primary holdout supported incremental prediction of foreign net flow. Its pre-specified reverse-causality diagnostic leaves open")
    t = rep(t, r"Accordingly, these figures serve as an illustrative calibration",
            r"Positive feedback in foreign investors' daily flows, and the difficulty of separating it from prices responding to flows, are documented for Taiwan and other markets (Froot et al., 2001; Griffin et al., 2004; Richards, 2005). Wu and Wang (2020) report higher day-trading activity after Taiwan's tax reduction. Their turnover outcome leaves the signed feedback response by trader type unmeasured. Accordingly, these figures serve as an illustrative calibration")
    t = rep(t, r"the same $(\Delta\eta)^{-(4K-2)}$ barrier operates with direct prudential significance.",
            r"the same $(\Delta\eta)^{-(4K-2)}$ barrier would apply with more prudential weight.")
    t = rep(t, r"aggregate price persistence $\sum_{j=1}^5 a_j = 0.97$.} \\",
            r"aggregate price persistence $\sum_{j=1}^5 a_j = 0.97$.} \\" + "\n" +
            r"\multicolumn{4}{@{}l}{\footnotesize Within-stock $R^2$: price equation $0.95$; rules $0.14$ (Foreign), $0.18$ (Trust) and $0.10$ (Dealers).} \\")
    # ---------------------------------------------------------------- conclusion
    t = rep(t, r"First, market-wide interventions (such as uniform feedback cuts or market-design changes calibrated to aggregate response) are statistically well-posed from public prices and are minimax-optimal when class identities are unverified.",
            r"First, the budget for a uniform feedback cut can be estimated from kernel taps, given the market's persistence, impact and a bound on memory. Uniform policies are minimax over labelings in the fixed-population decision problem. In the Gaussian model a passive pricing-error record suffices for the smooth quadratic effect. Proportional taxes and threshold policies can require more information (Theorem~\ref{thm:instruments}).")
    t = rep(t, r"durable targeted supervision requires owner-linked audit trails—such as",
            r"owner-linked reporting can support targeted supervision when the link is reliable, as illustrated by")
    t = rep(t, r"Our passive sample-complexity bounds assume Gaussian (or quadratically regular) innovations and exclude bounded-support noise laws.",
            r"Our passive sample-complexity bounds assume Gaussian (or quadratically regular) innovations and exclude bounded-support noise laws. The surveillance result describes a best response to a fixed test, not an equilibrium between the supervisor and the traders. The Taiwan calibration uses development data under P1M and P1M-A1 protocols set before their runs. It grants the observer the market's persistence and impact and uses asymptotic rate proxies and local numerical search. Causal feedback and the effective number of independent stocks remain unresolved. Trader rules are fixed and respond to deviations from a public fundamental, and the classes in the calibration are investor types rather than algorithms.")
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
    review_ai = (
        r" On 22 November 2026 the proofs or statements of Proposition~\ref{prop:decision-suff}, "
        r"Theorems~\ref{thm:eq-id}, \ref{thm:cost}, \ref{thm:cheap}, \ref{thm:recovery}, "
        r"\ref{thm:minimax}, \ref{thm:partial-minimax}, \ref{thm:tags} and \ref{thm:paradox}, "
        r"Proposition~\ref{prop:interventions}, Corollaries~\ref{cor:loss} and \ref{cor:halt}, "
        r"Lemma~\ref{lem:micro} and Proposition~\ref{prop:relabeling} were added or corrected with AI "
        r"assistance and have not yet been checked by the authors. Supplement Theorem~\ref{S-prop:passive}(ii), "
        r"Corollary~\ref{S-cor:unknown_primitives}, Theorem~\ref{S-thm:questions}(ii)--(iii), "
        r"Propositions~\ref{S-prop:hidegame} and~\ref{S-prop:relabelK}, and Theorem~\ref{S-thm:relabelgeneral} "
        r"were also corrected with AI assistance and have not yet been checked by the authors. "
        r"The Taiwan calibration wording was corrected against the archived outputs."
    )
    instrument_ai = (
        r" Theorem~\ref{thm:instruments} and Supplement Section~\ref{S-app:instruments} "
        r"were added with AI assistance and have not yet been checked by the authors. This includes the passive-price "
        r"extension and its proof in Supplement Section~\ref{S-app:passiveincidence}."
    )
    t = rep(t, old_ai, new_ai + review_ai + instrument_ai)
    t = rep(t, r"to assist with literature cross-checking, numerical verification scripts, Lean~4 formalization coding, and language editing.",
            r"to assist with literature cross-checking, numerical verification scripts, Lean~4 formalization coding, drafting, and language editing.")
    # ---------------------------------------------------------------- appendix
    t = rep(t, r"Part~(ii) follows from Online Supplement Theorem~S4.3(i) applied to the closed loop in~(i).",
            r"Part~(ii) follows from Supplement Theorem~\ref{S-thm:minphase}(i) applied to the closed loop in~(i).")
    t = rep(t, r"\begin{proof}[Proof of Theorems~\ref{thm:minimax} and~\ref{thm:partial-minimax} and Corollary~\ref{cor:halt}]",
            POLICY_PROOFS + HORIZON_PROOF + INSTRUMENT_PROOF + r"\begin{proof}[Proof of Theorems~\ref{thm:minimax} and~\ref{thm:partial-minimax} and Corollary~\ref{cor:halt}]")
    a = t.index(r"\begin{proof}[Proof of Theorems~\ref{thm:minimax} and~\ref{thm:partial-minimax} and Corollary~\ref{cor:halt}]")
    b = t.index(r"\end{proof}", a)
    t = t[:a] + t[a:b].replace(r"\sigma", r"\pi") + t[b:]
    t = rep(t, r"Valuing the marginal market-wide impact and inventory-risk externality at $\lambda_{\mathrm{ext}} > 0$ gives",
            r"Valuing a unit of feedback intensity at $\lambda_{\mathrm{ext}} > 0$, the supervisor's valuation of the rise in impact and inventory risk, gives")
    a = t.index(PARADOX_PROOF_START)
    b = t.index(PARADOX_PROOF_END, a) + len(PARADOX_PROOF_END)
    t = t[:a] + PARADOX_PROOF_NEW + t[b:]
    # ---------------------------------------------------------------- referee corrections
    t = rep(t, 'If the loss of an action depends on the population only through the flow map, the set of safe actions is identified by prices.', 'If the observation law identifies the flow map and the loss depends on the population only through that map, the set of safe actions is identified in that experiment.')
    t = rep(t, 'and spacing $\\Delta\\eta > 0$ such that every candidate economy is Schur stable.', 'and small $\\Delta\\eta>0$ with $r_c+\\Delta\\eta[-1,1]\\subset(0,1)$. Fix known $(a,\\kappa)$ with $a+\\kappa W/(1-r_c-\\Delta\\eta)$ bounded below one by a common positive margin over the spacings considered.')
    t = rep(t, 'the same pair has impulse-response gap of order $(\\Delta\\eta)^{2K-1}$, requiring', 'the same pair has response gap $O((\\Delta\\eta)^{2K-1})$, of that exact order when the tap $h_{2K}$ is recorded, requiring')
    t = rep(t, "Prony's method applied to the first $2K$ estimated kernel values recovers the weights from $N = C \\sigma^2 (\\Delta\\eta)^{-(4K-2)}$ reset experiments.", "Prony's method applied to the first $2K$ kernel values reconstructed from taps through $h_{2K}$ attains fixed positive accuracy at fixed confidence with $O(\\sigma^2(\\Delta\\eta)^{-(4K-2)})$ reset experiments. The matching lower bound applies on classes containing the hard pair with accuracy below half its weight gap.")
    t = rep(t, '\\caption{Illustrative years of daily price data below which no test separates the two populations of Theorem~\\ref{thm:cost}(i) with both error probabilities at $5\\%$.}', '\\caption{Illustrative daily-data horizons at $5\\%$ per error, using the stationary KL rate for the budget-matched populations.}')
    t = rep(t, 'Composition is only one functional of the merged measure $M$.', 'This section concerns direct, independent measurements of kernel taps. Composition is only one functional of the merged measure $M$.')
    t = rep(t, '$N_{\\mathrm{cert}}(\\epsilon; F_g) = O(\\sigma^2 \\epsilon^{-2})$—independent of the number of groups $K$ and their memory spacing—if and only if', 'Allowing the tap depth $L$ to grow, $N_{\\mathrm{cert}}(\\epsilon;F_g)=O(\\sigma^2\\epsilon^{-2})$ as $\\epsilon\\downarrow0$, uniformly over the measure class, if and only if')
    t = rep(t, 'with $N(0, \\sigma^2)$ noise across $N$ experiments.', 'with independent $N(0,\\sigma^2)$ noise across taps and across $N$ experiments.')
    t = rep(t, 'is pinned, up to the quantile ratio $\\lambda_\\alpha = z_{1-\\alpha/2}/z_{1-\\alpha}$ (approximately $1.19$ at the $95\\%$ level), by the polynomial approximation problem', 'is bounded by the necessary condition $\\omega_L(2z_{1-\\alpha}\\sigma/\\sqrt N)\\le2\\epsilon$ and the sufficient condition $\\omega_L(2z_{1-\\alpha/2}\\sigma/\\sqrt N)\\le2\\epsilon$, where the modulus is')
    t = rep(t, 'Instantiating Proposition~\\ref{prop:decision-suff}, suppose a supervisor must keep', 'For the post-policy calculation, hold dealers, price impact, persistence and the remaining rules fixed. Suppose a supervisor must keep')
    t = rep(t, '\\item[(ii)] A uniform cut to $\\theta = (\\bar{s} - a)/(S - a)$', '\\item[(ii)] If $S>a$ and $a\\le\\bar{s}\\le S$, a uniform cut to $\\theta = (\\bar{s} - a)/(S - a)$')
    t = rep(t, 'If $\\ell$ is convex and $C$ is convex and invariant to within-group permutations,', 'With the same continuous cost and convex loss in both regimes, suppose $C$ is convex and invariant to within-group permutations. Then')
    t = rep(t, 'we calibrate Theorems~\\ref{thm:cost} and~\\ref{thm:forecast-kl} using', 'we illustrate the decision problem in Theorems~\\ref{thm:cost} and~\\ref{thm:forecast-kl} using')
    t = rep(t, 'submitting the one-period optimal trade $u_t = \\hat{v}_t / (\\kappa + \\lambda)$ that maximizes $\\E[v_t u - \\frac{1}{2}(\\kappa + \\lambda)u^2 \\mid \\hat{v}_t]$.', 'using the plug-in trade $u_t=\\hat v_t/(\\kappa+\\lambda)$ for a fixed $\\kappa+\\lambda>0$. Assume independent centered innovations and square-integrable initial levels, and evaluate the loss at stationary filtering error.')
    t = rep(t, 'Substituting the one-period optimal trade', 'Substituting the plug-in trade at the same date and fixed impact')
    t = rep(t, 'Given fixed costs $F_C \\le F_A$, an owner-linked audit trail strictly dominates class tags if and only if $F_A - F_C < V_A - V_C(\\gamma)$, i.e., whenever relabeling cost $\\gamma$ lies below a unique threshold $\\gamma^*$.', 'Given fixed costs $F_C\\le F_A$, an owner-linked trail strictly dominates if $F_A-F_C<V_A-V_C(\\gamma)$. A unique finite positive cutoff applies for $0<F_A-F_C<V_A$. At zero incremental cost the trail strictly dominates for all finite $\\gamma>0$; for $F_A-F_C\\ge V_A$ it never strictly dominates.')
    t = rep(t, 'Across all compositions statistically indistinguishable from the full panel price record (no test exceeding its size by more than $0.10$), the implied effect of halting one class spans', 'Among candidates found using the panel-length spectral-rate proxy and the $0.10$ power-gap calibration, the effect of halting one class spans')
    t = rep(t, 'Against the closest single-memory population, one stock-day of prices carries', 'Against their respective fitted single-memory alternatives, one stock-day of prices has an estimated divergence of')
    t = rep(t, "public prices reveal the population's aggregate feedback kernel—and nothing finer—at standard statistical rates,", 'the pricing-error response identifies the aggregate kernel under the observation conditions of Sections~\\ref{sec:equilibrium} and~\\ref{sec:cost},')
    t = rep(t, 'uniform cumulative log-loss $O(\\log^2(T+1)/T)$ across all stable populations', 'expected cumulative log-loss per observation $O(\\log^2(T+1)/T)$ under fixed uniform stability and memory bounds')
    t = rep(t, 'Deviating from $r_0$ to $r$ incurs per-period expected profit loss', 'At fixed impact, deviating from $r_0$ to $r$ incurs the stationary-error profit loss')
    t = rep(t, 'Let $\\ell$ be convex and $C$ be convex and permutation-invariant on $[0, 1]^K$.',
            'Let $\\ell:\\mathbb{R}\\to\\mathbb{R}$ be convex and $C$ continuous, convex and permutation-invariant on $[0,1]^K$.')
    t = rep(t, "Suppose that in addition to prices, the supervisor receives each class's order flow with independent Gaussian measurement noise. On the rich class of Theorem~\\ref{thm:cost}(iii), the number of experiments required to recover group weights drops from order $(\\Delta\\eta)^{-(4K-2)}$ to a constant independent of $\\Delta\\eta$, and for memory rates it drops to order $(\\Delta\\eta)^{-2}$.",
            "In the reset experiment of Theorem~\\ref{thm:cost}, each class's flow is measured at the first two response dates with independent Gaussian noise. On a compact uniformly stable separated class containing the hard pair and an open set of rescaled nodes and positive weights, a fixed weight accuracy below half the pair's weight gap requires a number of tagged experiments bounded independently of $\\Delta\\eta$. Rate accuracy $c_0\\Delta\\eta$ requires order $(\\Delta\\eta)^{-2}$ tagged experiments for sufficiently small fixed $c_0>0$ and fixed confidence.")
    t = rep(t, 'Lower bound $T \\ge \\ln(5)/\\KL$ (Bretagnolle--Huber),',
            'Rate-based proxy $\\ln(5)/D$, where $D$ is the stationary Gaussian KL rate')
    t = rep(t, 'the optimal targeted restriction is partial—when uniform retention is worthwhile ($m \\ge 0$), the supervisor leaves the harmful label partly open; when $m < 0$, it also restricts the benign label because that label serves as the hiding channel.',
            'a harmful label is left partly open in the interior case with positive net value of uniform retention. At a boundary it may be closed. When $m<0$ the supervisor can restrict the benign label because it serves as the hiding channel.')
    t = rep(t, 'the equilibrium share of restricted activity that hides is independent of $\\gamma$',
            'the hiding share is independent of $\\gamma$ on the interior branch')
    t = rep(t, 'For a small trader group ($w_i \\ll 1$), shifting $r_i$ alters the market-wide Stieltjes transform $G(D)$—and hence equilibrium impact $\\kappa$ in Theorem~\\ref{thm:inv-eq}(iv)—only at order $O(w_i)$, so the quadratic distortion cost $k(D_0 - D)^2$ is exact at leading order.',
            'The expansion holds at fixed impact. It leaves open the optimal memory and local distortion cost when the desk internalizes its effect on dealer impact.')
    t = rep(t, "Finally, by Theorem~\\ref{thm:inv-eq}(iv), $\\partial \\kappa / \\partial r_i = O(w_i)$, so for a small group ($w_i \\ll 1$) the induced equilibrium shift in $\\kappa$ is of order $O(w_i)$, leaving $k = P''(r_0)/(4(\\kappa + \\lambda))$ invariant at leading order.",
            'The term $\\E[v_t^2]$ may grow with calendar time but cancels when the two rules are compared at the same date.')
    t = rep(t, 'then replacing $\\theta$ by the group-average policy',
            'replacing $\\theta$ by the group-average policy')
    t = rep(t, 'halting the largest group satisfies the ceiling in one economy and breaches it in the other; deciding between them from $N$ reset records with both errors at most $1/4$ requires $N \\ge c \\sigma^2 (\\Delta\\eta)^{-(4K-2)}$.',
            'halting the largest group satisfies the ceiling in one economy and breaches it in the other; deciding between them from $N$ reset records with both errors at most $1/4$ requires $N \\ge c \\sigma^2 (\\Delta\\eta)^{-(4K-2)}$ under the reset contract of Theorem~\\ref{thm:cost}.')
    t = rep(t, 'Second, targeted restrictions aimed at specific trader classes require class-tagged flow reports, which eliminate the spacing penalty for weight recovery.',
            'Second, class-specific restrictions require attribution. Verified flow tags remove the spacing penalty for weights in the reset experiment.')
    t = rep(t, 'because daily aggregation blends intraday momentum with liquidity provision',
            'at this daily frequency')
    t = rep(t, 'intraday limit-order-book markets where aggregate feedback shares',
            'a high-feedback venue would require separate evidence on whether shares')
    t = rep(t, 'are economically larger',
            "are economically larger")
    t = rep(t, 'A large literature studies heterogeneous fundamentalist and chartist asset-pricing models (Brock and Hommes, 1998; Hommes, 2006) and estimates trader shares from prices (Boswijk et al., 2007; Franke and Westerhoff, 2012; Lux and Zwinkels, 2018);',
            "A large literature studies heterogeneous fundamentalist and chartist asset-pricing models (Brock and Hommes, 1998; Hommes, 2006) and estimates trader shares from prices (Boswijk et al., 2007; Franke and Westerhoff, 2012; Lux and Zwinkels, 2018); Brock and Hommes model fitness-driven switching among predictors. We fix the rules and masses, so variation in their composition enters through moments of one measure. Heinrich and Kahn's local mixture rate concerns the mixing law in a sampling model. Here the kernel is observed through a feedback recursion or a separate tap experiment.")
    t = rep(t, 'Budish et al.\\ (2015) advocate market-wide structural remedies (frequent batch auctions),',
            'Budish et al.\\ (2015) analyze continuous-book cancellation and batch auctions. Colliard and Hoffmann (2017) document volume, liquidity and composition responses to a transaction tax. Theorem~\\ref{thm:instruments} derives incidence for a perceived-return benchmark with fixed memories. Its scheduled holding rule abstracts from order cancellation and execution. Kirilenko et al.\\ (2017)')
    t = rep(t, '\\begin{proof}[Proof of Theorem~\\ref{thm:smooth}]', COMPOSITION_PROOFS + '\\begin{proof}[Proof of Theorem~\\ref{thm:smooth}]')
    t = rep(t, 'evaluated at $\\delta = 2 z_{1-\\alpha} \\sigma / \\sqrt{N}$.', 'The necessary and sufficient conditions use the same modulus.')
    t = rep(t, 'proves that the same limits—collapse of class-tag value as $\\gamma \\to 0$ and convergence to $V_A$ as $\\gamma \\to \\infty$—hold for arbitrary concave private payoffs, general convex concealment costs, and any Lipschitz social welfare functional $U(e)$,', 'extends the limits to Lipschitz social welfare and private payoffs with slopes bounded above and bounded away from zero, under the stated routing-cost conditions. The cheap-routing collapse requires all labels to be reachable. This covers')
    t = rep(t, 'If $m \\ge 0$: $\\theta_{\\mathcal{B}} = 1$,',
            'If $m \\ge 0$: one optimum sets $\\theta_{\\mathcal{B}} = 1$,')
    t = rep(t, 'If $m \\ge 0$, $\\varphi$ is nondecreasing, so',
            'If $m \\ge 0$, $\\varphi$ is nondecreasing (with a flat region above $\\hat d$ when $m=0$), so')
    t = rep(t, 'a fitted autoregression of order $L_T = \\lceil c \\log T \\rceil$ attains the oracle risk up to',
            'at each fixed parameter under the conditions of the forecasting result a fitted autoregression of order $L_T = \\lceil c \\log T \\rceil$ attains the oracle risk up to')
    t = rep(t, 'Replication scripts, numerical checks, and Lean~4 formalization files',
            'The protocols and archived Taiwan outputs are under \\nolinkurl{ceiling_suite/p1_empirics}. Replication scripts, numerical checks, and Lean~4 formalization files')
    t = rep(t, '\\small\\setlength{\\leftmargin}{1.8em}',
            '\\small\\linespread{1}\\selectfont\\setlength{\\leftmargin}{1.8em}')
    t = rep(t, '\\setlength{\\itemsep}{3pt}\\setlength{\\parsep}{0pt}', '\\setlength{\\itemsep}{0.5pt}\\setlength{\\parsep}{0pt}')
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
    r"Wu, C.-H., Wang, T.-Y., 2020. The effects of reducing the securities transaction tax on day trading: Evidence from the Taiwan stock market. \emph{Journal of Accounting Review} 70, 135--169.",
    r"Colliard, J.-E., Hoffmann, P., 2017. Financial transaction taxes, market composition, and liquidity. \emph{Journal of Finance} 72(6), 2685--2716.",
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
