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
sys.path.insert(0, str(HERE))
import sharpen_1127  # noqa: E402  (revision of 27 November 2026)

MOVED = {}  # blocks moved to the supplement by sharpen_1127
SRC = HERE / 'received' / 'Paper1_JEDC_final.tex'
OUT = HERE / 'Paper1_JEDC_main.tex'

# Set to True only after the first author says he has read and checked Proposition 7.1(iii) and (iv), Theorem 7.3(ii), Lemma 7.7, Theorem 7.9 and
# Supplement Propositions S4.5 and S11.1 in their present form.
CORRECTIONS_CHECKED_BY_FIRST_AUTHOR = True


def rep(t, old, new, count=1):
    n = t.count(old)
    assert n == count, (old[:120], n, count)
    return t.replace(old, new)



MPV_THEOREM = r"""Discrete exchange tick grids do not rescue compositional identification---and can extinguish it completely when shocks remain sub-tick:

\begin{theorem}[Minimum price variation and tick-grid resolution]\label{thm:mpv}
Let transaction prices $p_t = F_t + x_t$ be rounded onto a uniform tick grid $\Delta_{\mathrm{tick}} > 0$ via $\mathcal{Q}(p) = \Delta_{\mathrm{tick}} \lfloor p / \Delta_{\mathrm{tick}} + 1/2 \rfloor$ (under either open-loop observer rounding or closed-loop exchange tick clearing) for two $K$-group economies satisfying $\|h^A - h^B\|_1 \le C (\Delta\eta)^{2K-1}$ (or $\|k^A - k^B\|_1 \le C_k(\Delta\eta)^{2K-1}$ in closed loop).
\begin{enumerate}
  \item[(i)] \emph{Sub-cell coincidence.} Under bounded shocks $\|v\|_\infty \le \bar{v}$, if the baseline trajectory $p_t^A$ stays strictly farther than $C_{\mathrm{cl}}(\bar{v} + \|\tilde{x}^A\|_\infty)(\Delta\eta)^{2K-1}$ from every half-tick boundary $(m + \tfrac{1}{2})\Delta_{\mathrm{tick}}$, then $\mathcal{Q}(p_t^A) = \mathcal{Q}(p_t^B)$ pathwise, $\KL(P_{\mathcal{Q}}^A \| P_{\mathcal{Q}}^B) = 0$, and $N = \infty$; bounded continuous shocks crossing a half-tick boundary yield positive $\KL$.
  \item[(ii)] \emph{Gaussian dithering.} Under $N(0,\sigma^2)$ innovations, quantized Fisher information satisfies $\mathcal{I}_{\mathcal{Q}}(\mu) > 0$ for every $\Delta_{\mathrm{tick}} > 0$, and data processing preserves $\KL(P_{\mathcal{Q}}^A \| P_{\mathcal{Q}}^B) \le C T (\Delta\eta)^{4K-2}$. As $\Delta_{\mathrm{tick}}/\sigma \to 0$, independent reset impulses preserve the $(\Delta\eta)^{4K-2}$ lower bound with Sheppard efficiency $1 - \Delta_{\mathrm{tick}}^2/(12\sigma^2) + O(\Delta_{\mathrm{tick}}^4/\sigma^4)$, while passive $\mathrm{AR}(1)$ records incur double-quantization Whittle factor $1 - (1 - a^2)\Delta_{\mathrm{tick}}^2/(6\sigma^2) + O(\Delta_{\mathrm{tick}}^4/\sigma^4)$ alongside Markov-chain conditioning loss.
\end{enumerate}
\end{theorem}"""

MPV_PROOF = r"""\begin{proof}[Proof of Theorem~\ref{thm:mpv}]
For~(i), $|p_t^A - p_t^B| \le C_{\mathrm{cl}}(\bar{v} + \|\tilde{x}^A\|_\infty)(\Delta\eta)^{2K-1}$ whenever both trajectories remain inside the same tick cell through $t - 1$ (inductively, quantized state deviations vanish while $\tilde{x}_s^B = \tilde{x}_s^A$); hence $\max_t |p_t^A - m_t \Delta_{\mathrm{tick}}| + C_{\mathrm{cl}}(\bar{v} + \|\tilde{x}^A\|_\infty)(\Delta\eta)^{2K-1} < \Delta_{\mathrm{tick}}/2$ confines both $p_t^A$ and $p_t^B$ to $[(m_t-\tfrac{1}{2})\Delta_{\mathrm{tick}}, (m_t+\tfrac{1}{2})\Delta_{\mathrm{tick}})$ for all $t$, giving pathwise coincidence and $\KL = 0$. For~(ii), data processing gives $\KL(P_{\mathcal{Q}}^A \| P_{\mathcal{Q}}^B) \le \KL(P^A \| P^B)$; for every $\Delta_{\mathrm{tick}} > 0$, strictly positive Gaussian density renders each cell probability $C^2$-sensitive to mean shifts ($\mathcal{I}_{\mathcal{Q}} > 0$), preserving the $(\Delta\eta)^{4K-2}$ order on independent reset impulses with small-tick Sheppard limit $1 - \Delta_{\mathrm{tick}}^2/(12\sigma^2)$ and passive $\mathrm{AR}(1)$ double-quantization Whittle factor $1 - (1 - a^2)\Delta_{\mathrm{tick}}^2/(6\sigma^2)$ (Supplement Section~\ref{S-sec:mpv_supp}).
\end{proof}

"""

ABSTRACT = (
    r"We study financial markets in which heterogeneous trading algorithms feed a common public pricing signal back into order flow. "
    r"Both in a linear market and in a stationary inventory-dealer equilibrium, all public outcomes---transaction prices, aggregate volume, dealer inventories, and optimal price forecasts---depend on the trader population solely through its aggregate feedback kernel. "
    r"Separating $K$ trader classes whose memory rates lie within $\Delta$ requires of order $\Delta^{-(4K-2)}$ observations under Gaussian noise, even near market instability or under active impulse probes. "
    r"Consequently, market-wide feedback cuts can be calibrated from prices alone and are minimax-optimal over unknown class labelings, whereas targeted restrictions require trader-level attribution. "
    r"Because strategic traders can evade account-level class tags by rerouting orders and evade untagged surveillance by crowding their speeds together, durable targeting requires owner-linked audit trails. "
    r"Daily class-tagged institutional flows from the Taiwan Stock Exchange illustrate the magnitude of this informational gap."
)

ENDOGENOUS_SUPERVISOR_PROP = r"""Endogenizing the supervisor's monitoring intensity sharpens this tension: because strategic crowding erodes detection power as $N$ grows, deterministic commitment collapses under high stakes and equilibrium auditing must be randomized.

\begin{proposition}[Endogenous monitoring commitment and mixed-strategy auditing]\label{prop:endogenous_supervisor}
In the Gaussian experiment of Theorem~\ref{thm:paradox} ($J = c N \delta^n$, $n > 2$), suppose the supervisor chooses monitoring size $\alpha \in \{0\} \cup [\alpha_{\min}, \bar{\alpha}]$ ($\alpha_{\min} > 0$) at cost $C(\alpha) \ge c_{\min} > 0$ on $[\alpha_{\min}, \bar{\alpha}]$ ($C(0) = 0$) to maximize $V_{\mathrm{det}}(P_{\mathrm{d}}(\alpha, J) - \alpha) - C(\alpha)$, while the untagged group chooses $\delta \in [0, \delta_0]$ to minimize $L P_{\mathrm{d}}(\alpha, J) + k(\delta_0 - \delta)^2$.
\begin{enumerate}
  \item[(i)] \emph{High-stakes crowding and low-stakes separation.} Fix $\alpha \ge \alpha_{\min}$. Under high stakes $L(1 - \alpha) > k \delta_0^2$, the global minimizer for large $N$ obeys
  \[
    \delta_N^* = \left(\frac{4 k \delta_0}{n \beta L}\right)^{\frac{2}{n-2}} (c N)^{-\frac{1}{n-2}} (1 + o(1)), \qquad J_N^* = c N (\delta_N^*)^n \asymp N^{-\frac{2}{n-2}} \to 0,
  \]
  where $\beta = \sqrt{2}\phi(z_\alpha)$ for a one-sided test along a known normal direction, so $P_{\mathrm{d}}(\alpha, J_N^*) \to \alpha$ and distortion cost $k(\delta_0 - \delta_N^*)^2 \to k\delta_0^2$. Conversely, if $L(1 - \alpha) < k \delta_0^2$, full separation prevails ($\delta_N^* \to \delta_0$, $P_{\mathrm{d}} \to 1$). Without a known normal direction, a two-sided composite-null GLRT ($P_{\mathrm{d}}(J) - \alpha = c_2 J + O(J^2)$, $c_2 > 0$) slows crowding to $\delta_N^* \asymp N^{-1/(n-1)}$ and $J_N^* \asymp N^{-1/(n-1)}$ ($N^{-1/3}$ at $n=4$).
  \item[(ii)] \emph{Stackelberg collapse and simultaneous mixed-strategy auditing.} Under high stakes, if the supervisor commits to a pure $\alpha$ before $\delta$ is chosen, $P_{\mathrm{d}}(\alpha, J_N^*) - \alpha \to 0$ uniformly on $[\alpha_{\min}, \bar{\alpha}]$ drives committed net supervisory payoff strictly below zero for large $N$, forcing $\alpha_N^* = 0$. In a simultaneous-move game with $V_{\mathrm{det}}(1 - \alpha_{\min}) > C(\alpha_{\min})$ ($V_{\mathrm{det}} > c_{\min}$), no pure-strategy Nash equilibrium exists for large $N$; equilibrium requires randomized monitoring ($p^* > 0$) leaving traders indifferent. Verified class tags decouple $P_{\mathrm{d}}$ from $\delta$ and restore $\delta^* = \delta_0$.
\end{enumerate}
\end{proposition}"""

ENDOGENOUS_SUPERVISOR_PROOF = r"""\begin{proof}[Proof of Proposition~\ref{prop:endogenous_supervisor}]
\emph{(i)} In the known-direction shift experiment, the Neyman--Pearson test rejects above $z_\alpha = \Phi^{-1}(1 - \alpha)$, giving $V_A(\delta) = k(\delta_0 - \delta)^2 + L \Phi(\sqrt{2 c N \delta^n} - z_\alpha)$. Differentiating yields
\[
  V_A'(\delta) = L \phi\bigl(\sqrt{2 c N \delta^n} - z_\alpha\bigr) \frac{n \sqrt{c N}}{\sqrt{2}} \delta^{\frac{n}{2} - 1} - 2 k (\delta_0 - \delta).
\]
For large $N$, on $J(\delta) \le z_\alpha^2/2$, $P_{\mathrm{d}}$ is convex in $\sqrt{2J}$, yielding a unique interior local minimizer with $\sqrt{2 c N (\delta_N^*)^n} \to 0$ solving $L \phi(z_\alpha) \frac{n \sqrt{c N}}{\sqrt{2}} (\delta_N^*)^{\frac{n-2}{2}} \sim 2 k \delta_0$, i.e., $\delta_N^* = [4 k \delta_0 / (n \beta L)]^{2/(n-2)} (c N)^{-1/(n-2)} (1 + o(1))$ with $V_A(\delta_N^*) \to k\delta_0^2 + L \alpha$; on $J(\delta) > z_\alpha^2/2$, $V_A \to L$ near $\delta_0$. Hence $\delta_N^*$ is the unique global minimizer if and only if $L(1 - \alpha) > k \delta_0^2$, whereas $L(1 - \alpha) < k \delta_0^2$ selects $\delta_N^* \to \delta_0$. Under a two-sided $\chi^2$ GLRT, odd first-order terms cancel so $P_{\mathrm{d}}(J) - \alpha = c_2 J + O(J^2)$ ($c_2 = 2 z_{\alpha/2}\phi(z_{\alpha/2})$), and the first-order condition $n L c_2 c N \delta^{n-1} \sim 2 k \delta_0$ gives $\delta_N^* \asymp N^{-1/(n-1)}$ and $J_N^* \asymp N^{-1/(n-1)}$. \emph{(ii)} Under Stackelberg commitment, for every $\alpha \ge \alpha_{\min}$, $V_{\mathrm{det}}(P_{\mathrm{d}}(\alpha, J_N^*) - \alpha) - C(\alpha) \le V_{\mathrm{det}} \sqrt{J_N^*/2} - c_{\min} < 0$ for large $N$, forcing $\alpha_N^* = 0$. In the simultaneous game, $(\alpha=0, \delta=\delta_0)$ invites a profitable supervisory deviation to $\alpha \in [\alpha_{\min}, \bar\alpha]$ when $V_{\mathrm{det}}(1-\alpha_{\min}) > C(\alpha_{\min})$, whereas any pure $\alpha \ge \alpha_{\min}$ induces crowding $\delta_N^*$ and negative supervisory surplus; hence no pure Nash equilibrium exists and randomized monitoring $p^* \in (0, 1)$ obtains.
\end{proof}"""

POSTHALT_COROLLARY = r"""\begin{corollary}[Ceiling stabilization versus dealer-capacity withdrawal]\label{cor:posthaltflip}
Consider a stationary high-feedback economy with pre-intervention budget $S < 1$:
\begin{enumerate}
  \item[(i)] \emph{Ceiling stabilization vs.\ dealer-capacity withdrawal.} Halting group $i^*$ removes $\kappa q_{i^*}$ at fixed dealer capacity $A$: for a target ceiling $\bar{s} \in (a, 1)$ with $S \in (\bar{s}, 1)$, if $\kappa q_{i^*} > S - \bar{s}$ then $S_{\mathrm{halt}} < \bar{s}$ without losing Schur stability. Conversely, in the inventory equilibrium of Theorem~\ref{thm:fragility} near $\lambda_{\mathrm{crit}}$, if halting a multi-strategy firm simultaneously removes dealer risk-bearing capacity ($\Delta A > 0$), endogenous impact can jump past $\lambda_{\mathrm{crit}}$, destroying linear equilibrium existence post-halt.
  \item[(ii)] \emph{Targeted miss around a prudential ceiling $\bar{s} < 1$.} In the moment-matched $K$-group pair of Proposition~\ref{prop:interventions}(ii) with ordered largest weights $q_{\max}^{(2)} < q_{\max}^{(1)}$ separated by order $W/K^2$, suppose $\kappa q_{\max}^{(2)} < 1 - \bar{s}$ and let pre-halt $S < 1$ satisfy $\bar{s} + \kappa q_{\max}^{(2)} < S < \min(1,\, \bar{s} + \kappa q_{\max}^{(1)})$. Halting the largest group stabilizes below $\bar{s}$ in one economy while leaving $S_{\mathrm{halt}} > \bar{s}$ in the other; separating them requires $N \ge c \sigma^2 (\Delta\eta)^{-(4K-2)}$ reset records.
\end{enumerate}
\end{corollary}"""

POSTHALT_PROOF = r"""\begin{proof}[Proof of Corollary~\ref{cor:posthaltflip}]
\emph{(i)} Subtracting $\kappa q_{i^*}$ at fixed $(a,\kappa)$ lowers $S$ below $\bar{s}$ whenever $\kappa q_{i^*} > S - \bar{s}$ while remaining Schur stable ($S_{\mathrm{halt}} < S < 1$). However, in Theorem~\ref{thm:fragility}, if halting a multi-strategy firm raises remaining dealer effective risk aversion ($A_{\mathrm{post}} > A$) faster than feedback mass drops, $\lambda S_M(D)\kappa_-(D; A_{\mathrm{post}})$ shifts above $1 - D$, eliminating the real fixed point beyond $\lambda_{\mathrm{crit}}$. \emph{(ii)} By Proposition~\ref{prop:interventions}(ii), the moment-matched pair maintains identical pre-halt budgets modulo $O((\Delta\eta)^{2K-1})$ and uniform stability $S < 1$ (satisfying Supplement Proposition~\ref{S-prop:nearcrit} and Theorem~\ref{thm:cost}), while $q_{\max}^{(1)} - q_{\max}^{(2)} \asymp W/K^2$; choosing $\bar{s}$ in the stated window ensures opposite ceiling compliance and invokes Theorem~\ref{thm:cost}'s $(\Delta\eta)^{-(4K-2)}$ bound.
\end{proof}
"""

IDENT_PROOF = r"""\begin{proof}[Proof of Theorem~\ref{thm:what-id}]
With $x_{-1} = 0$ and zero initial group states, each group's state obeys $y_{i,t} = \sum_{s \le t} \eta_i r_i^{t-s} x_s$. Aggregating over groups gives total feedback flow $\sum_i q_i y_{i,t} = \sum_{s \le t} k_{t-s} x_s$. By induction on $t$, pricing errors $x_t$ under probe sequence $v_t$ are determined uniquely by $(a, \kappa)$ and the feedback kernel $k_m = \int r^m \, dM(r)$, hence by the merged measure $M$. Conversely, matching price responses to all probe sequences requires matching impulse responses $h_j$ for all $j \ge 0$, uniquely identifying the closed-loop transfer function $H(z)$ and the feedback transfer $G(z) = \sum_{m \ge 0} k_m z^{-m} = \sum_i w_i z / (z - r_i)$. Partial fraction decomposition of $G(z)/z = S_M(z)$ uniquely identifies its poles $r_i \in (0,1)$ and nonzero merged weights $w_i$, uniquely recovering $M = \sum_i w_i \delta_{r_i}$ (Supplement Section~\ref{S-sec:suff} and Theorem~\ref{S-thm:merged}).
\end{proof}
"""

FRAGILITY_THEOREM = r"""Before turning to identification, we characterize how endogenous dealer risk-bearing alters stability as feedback scales up---replacing the linear $S \uparrow 1$ variance blow-up with a saddle-node liquidity fold at strictly finite variance:

\begin{theorem}[Equilibrium fragility and liquidity collapse]\label{thm:fragility}
Let $A, \sigma_F^2, \sigma_\xi^2 > 0$, $\bar{a} \in [0, 1)$, and $w_i > 0$ with $\Lambda_0 = (1 - \bar{a})^2 - 4 A^2 \sigma_F^2 \sigma_\xi^2 > 0$, holding intraday dealer risk tolerance $A^{-1}$ fixed. Write $S_M(D) = \sum_{i=1}^K w_i/(D - r_i)$ and scale feedback intensity by $\lambda S_M(D)$ for $\lambda \ge 0$. On the principal monotone branch $D \in (\max(D_{\min}, \max_i r_i), 1]$, where $D_{\min} \equiv \bar{a} + 2 A \sigma_F \sigma_\xi$:
\begin{enumerate}
  \item[(i)] \emph{Principal critical threshold and saddle-node exit.} There exists a finite threshold $\lambda_{\mathrm{crit}} \in \bigl(0, [\kappa_- S_M(1)]^{-1}\bigr)$ such that a stable linear equilibrium $(\kappa(\lambda), D(\lambda), V(\lambda))$ exists on the principal branch for $\lambda < \lambda_{\mathrm{crit}}$, whereas for $\lambda > \lambda_{\mathrm{crit}}$ no real equilibrium exists on $(\max(D_{\min}, \max_i r_i), 1]$ at fixed $A$.
  \item[(ii)] \emph{Liquidity collapse and square-root fragility.} Under the standard non-degenerate quadratic fold condition $F_{DD}(D_{\mathrm{crit}}; \lambda_{\mathrm{crit}}) > 0$ on $F_-(D; \lambda) \equiv D - 1 + \lambda \kappa_-(D) S_M(D)$ (automatic for $K=1$, generic for $K \ge 2$), as $\lambda \uparrow \lambda_{\mathrm{crit}}$, $D(\lambda) - D_{\mathrm{crit}} \asymp \sqrt{\lambda_{\mathrm{crit}} - \lambda}$ and effective depth $D/\kappa$ shrinks with square-root fold asymptotics.
  \item[(iii)] \emph{Finite threshold variance and diverging sensitivities.} At $\lambda = \lambda_{\mathrm{crit}}$ with $D_{\mathrm{crit}} > \max(D_{\min}, \max_i r_i)$ and $F_{DD} > 0$, conditional variance $V(\lambda_{\mathrm{crit}}) < 2\sigma_F^2 < \infty$, the effective closed-loop budget $S^*(\lambda_{\mathrm{crit}}) < 1$, and $\Var(H_t) < \infty$ remain strictly finite, while sensitivities $d\kappa/d\lambda$, $dV/d\lambda$, and $d\Var(H_t)/d\lambda$ diverge as $(\lambda_{\mathrm{crit}} - \lambda)^{-1/2} \to +\infty$ as $\lambda \uparrow \lambda_{\mathrm{crit}}$.
\end{enumerate}
\end{theorem}

For $K \ge 2$ with $\max_i r_i > D_{\min}$, secondary inter-pole branches may exist on $(D_{\min}, \max_i r_i)$, while long-run dealer entry unfolds the fixed-$A$ cliff into a smooth schedule (Supplement Section~\ref{S-sec:mixed_sign} and Figure~\ref{S-fig:supp_fragility})."""

FRAGILITY_PROOF = r"""\begin{proof}[Proof of Theorem~\ref{thm:fragility}]
Substituting $V = \sigma_F^2 + \kappa^2 \sigma_\xi^2 / D^2$ into $\kappa(D - \bar{a}) = A V D$ yields $A \sigma_\xi^2 \kappa^2 - D(D - \bar{a})\kappa + A \sigma_F^2 D^2 = 0$, whose discriminant $\Lambda(D) = D^2[(D - \bar{a})^2 - 4 A^2 \sigma_F^2 \sigma_\xi^2]$ is positive iff $D > D_{\min}$. On $(D_{\min}, 1]$, both quadratic roots $\kappa_\pm(D) = [D(D - \bar{a}) \pm \sqrt{\Lambda(D)}]/(2 A \sigma_\xi^2)$ are strictly positive with $\kappa_+(D) > \kappa_-(D)$ and $\kappa_-(1) = \kappa_-$. For $D \in (\max(D_{\min}, \max_i r_i), 1]$ with $w_i > 0$, $S_M(D) > 0$ and is strictly decreasing in $D$, while $\kappa_-(D)$ decreases on $(D_{\min}, 1]$ and $d\kappa_-/dD \to -\infty$ as $D \downarrow D_{\min}$ (and $S_M(D) \to +\infty$ as $D \downarrow \max_i r_i$). Setting $F_\pm(D; \lambda) \equiv D - 1 + \lambda \kappa_\pm(D) S_M(D)$, we have $F_-(1; \lambda) = \lambda \kappa_- S_M(1) > 0$, $F_-(D; 0) = D - 1 < 0$ for $D < 1$, and $F_-(D; \lambda) \to +\infty$ as $D \downarrow D_* \equiv \max(D_{\min}, \max_i r_i)$. Thus $\lambda_{\mathrm{crit}} = \sup_{D \in (D_*, 1)} (1 - D)/[\kappa_-(D) S_M(D)] > 0$ is attained at an interior point $D_{\mathrm{crit}} \in (D_*, 1)$; because both $\kappa_-(D)$ and $S_M(D)$ strictly decrease on $(D_*, 1]$ and $1 - D_{\mathrm{crit}} < 1$, $\kappa_-(D_{\mathrm{crit}}) S_M(D_{\mathrm{crit}}) > \kappa_- S_M(1)$, proving strictly $\lambda_{\mathrm{crit}} < [\kappa_- S_M(1)]^{-1}$, with $F_+(D;\lambda) > F_-(D;\lambda) > 0$ for all $\lambda > \lambda_{\mathrm{crit}}$ so neither root exists on $(D_*, 1]$. At the interior fold $D_{\mathrm{crit}} > D_*$, $\Lambda(D_{\mathrm{crit}}) > 0$. By Vieta's identity on the quadratic $A \sigma_\xi^2 \kappa^2 - D(D-\bar{a})\kappa + A \sigma_F^2 D^2 = 0$, the two roots satisfy $\kappa_-(D) < \kappa_+(D)$ and $\kappa_+(D)\kappa_-(D) = (\sigma_F^2/\sigma_\xi^2) D^2$, so $[\kappa_-(D)/D]^2 \sigma_\xi^2 < \kappa_+(D)\kappa_-(D)\sigma_\xi^2/D^2 = \sigma_F^2$ and hence $V(\lambda_{\mathrm{crit}}) = \sigma_F^2 + (\kappa_{\mathrm{crit}}/D_{\mathrm{crit}})^2 \sigma_\xi^2 < 2\sigma_F^2 < \infty$. Also by Theorem~\ref{thm:eq-id}(i), $S^*(\lambda_{\mathrm{crit}}) = 1 - \frac{D_{\mathrm{crit}}-\bar{a}}{D_{\mathrm{crit}}}\frac{S_M(1)}{S_M(D_{\mathrm{crit}})} < 1$ because $D_{\mathrm{crit}} > \bar{a}$ and $S_M(D_{\mathrm{crit}}) > S_M(1) > 0$, keeping $\Var(H_t) < \infty$. At the non-degenerate fold ($F_D = 0, F_{DD} > 0, F_\lambda > 0$), expanding $F_-(D; \lambda) \approx \frac{1}{2} F_{DD}(D - D_{\mathrm{crit}})^2 + F_\lambda(\lambda - \lambda_{\mathrm{crit}})$ yields $D - D_{\mathrm{crit}} \asymp \sqrt{\lambda_{\mathrm{crit}} - \lambda}$ and $d\kappa/d\lambda, dV/d\lambda, d\Var(H_t)/d\lambda \asymp (\lambda_{\mathrm{crit}} - \lambda)^{-1/2} \to +\infty$.
\end{proof}
"""

PARADOX_START = r"Even without account relabeling, an untagged algorithm that anticipates targeting"
PARADOX_END = r"verified class tags eliminate both crowding and costly defensive repositioning simultaneously."
PARADOX_NEW = r"""Even without account relabeling, an untagged algorithm that anticipates targeting can disguise itself by shifting its trading rule toward its neighbor's, at a cost to its own strategy. The next result characterizes what the supervisor learns when the algorithm best-responds to a fixed test.

\begin{theorem}[The surveillance paradox]\label{thm:paradox}
Consider an untagged group that chooses the distance $\delta \in [0, \delta_0]$ between its memory rate and its neighbor's at strategy-distortion cost $k(\delta_0 - \delta)^2$, holding all other groups fixed ($\delta_0, k > 0$). From $N$ observations, the supervisor tests at level $\alpha \in (0, 1/2)$ the composite null that the two groups merge into a single group of unknown memory and weight; rejection triggers an inquiry costing the group $L > 0$. Suppose the Kullback--Leibler divergence from the economy at distance $\delta$ to the closest null economy satisfies $J = c N \delta^n$ on $[0, \delta_0]$ with $c > 0$ and $n > 2$, and the test has continuous power $P_{\mathrm{d}}(J) \ge \alpha$ with $P_{\mathrm{d}}(0) = \alpha$. Let $\delta^*$ minimize $k(\delta_0 - \delta)^2 + L P_{\mathrm{d}}(c N \delta^n)$ and set $J^* = c N (\delta^*)^n$.
\begin{enumerate}
  \item[(i)] \emph{Hiding is never complete.} Against every such test, $\delta^* > 0$, and $(\delta^*)^{n-2} \ge 2 k^2 \delta_0^2 / (2^n L^2 c N)$ whenever $\delta^* \le \delta_0 / 3$.
  \item[(ii)] \emph{A good test forces crowding.} If the test's power satisfies $P_{\mathrm{d}}(J) - \alpha \ge \beta \min\{\sqrt{J}, \sqrt{\bar{J}}\}$ and the stakes are high ($L \beta \sqrt{\bar{J}} > k \delta_0^2$), then for every $N$,
  \[
    (\delta^*)^{n-2} \le \frac{4 k^2 \delta_0^2}{L^2 \beta^2 c N}.
  \]
  \item[(iii)] \emph{More data, less information.} Against such a test, for all large $N$, $\delta^* \asymp N^{-1/(n-2)}$ and the supervisor's information obeys $J^* \asymp N^{-2/(n-2)} \to 0$ ($N^{-1}$ in the benchmark $n=4$): detection probability tends to $\alpha$, and distortion cost $k(\delta_0 - \delta^*)^2$ tends to $k \delta_0^2$.
  \item[(iv)] \emph{Tag-based inquiry.} Under a verified class tag whose inquiry probability is independent of $\delta$, the unique optimum is $\delta^* = \delta_0$, and the group's rule is estimable from tagged flow (Theorem~\ref{thm:tags}).
\end{enumerate}
\end{theorem}

The exponent $n$ reflects the composite null: because prices do not reveal the neighbor's memory, a single merged group matching total weight $W = w_1 + w_2 \neq 0$ and mean memory cancels linear differences and leaves an $O(\delta^2)$ kernel gap and $O(\delta^4)$ divergence ($n = 4$; fitted spectral slope $4.1$ in Supplement Section~\ref{S-app:paradox}, vs.\ $n = 8$ for three-group clusters). By contrast, opposite-sign pairs ($w_1 = -w_2$) or a known simple null yield $n = 2$, permitting complete hiding once $N$ is large. In a Gaussian shift experiment along a known normal direction, a one-sided test satisfies~(ii) with $\beta = \sqrt{2}\phi(z_\alpha)$ and $\bar{J} = z_\alpha^2 / 2$ (Appendix~\ref{app:proofs}), whereas an unknown sign requires a composite-null GLRT ($P_{\mathrm{d}}(J) - \alpha = c_2 J + O(J^2)$) that slows crowding to $\delta_N^* \asymp N^{-1/(n-1)}$.

Economically, untagged surveillance provokes crowding that more than offsets additional observations, imposing a permanent strategy-distortion loss $k(\delta_0 - \delta)^2$ (microfounded by Kalman filtering in Lemma~\ref{lem:micro}(ii)). If the conduct at $\delta_0$ is itself harmful, this crowding acts as deterrence; what fails is supervisory learning rather than necessarily welfare---mirroring how policy intervention degrades market signals (Bond et al., 2010; Bond and Goldstein, 2015; Frankel and Kartik, 2019). Without an inquiry cost $L > 0$, detection has no behavioral bite (Theorem~\ref{thm:minimax}). When multiple untagged groups position simultaneously, Supplement Proposition~\ref{S-prop:hidegame}(iv) bounds asymptotic detection across any pure-strategy Nash equilibrium with bounded neighbor distances, while memory-independent tag inquiries eliminate crowding altogether.""" + "\n\n" + ENDOGENOUS_SUPERVISOR_PROP

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
\end{proof}""" + "\n\n" + ENDOGENOUS_SUPERVISOR_PROOF

UNIFORM_REMARK = r"""

\textbf{Information needed for a uniform cut.} Because a zero-memory group is observationally equivalent to baseline persistence (Supplement Theorem~\ref{S-thm:merged}(i)), calibrating a uniform cut requires known $(a,\kappa)$ and a memory bound $\bar r<1$, under which the omitted tail beyond lag $L$ is at most $W\bar r^L/(1-\bar r)$; summing noisy impulse-response lags at logarithmic depth estimates $S$ to accuracy $\epsilon$ in $O(\sigma^2\epsilon^{-2}\log(1/\epsilon))$ experiments."""

HORIZON_ITEM = r"""  \item[(iii)] \emph{Restriction by horizon.} Halting every group whose memory rate lies below a cutoff $\hat r \in (0, 1)$ likewise fails to be kernel-determined. Under the conditions of Theorem~\ref{thm:cost}, for every $K \ge 2$ and all small $\Delta\eta > 0$, there exist two $K$-group economies with memories in $[\hat r - \Delta\eta, \hat r + 2\Delta\eta]$ whose merged measures match moments $0, \dots, 2K-2$, such that the restriction removes at least $\kappa W/K^2$ of the budget in one economy and nothing in the other, where $W$ is the total merged weight. Over a nonempty interval of ceilings $\bar{s}$, the restriction satisfies the ceiling in one economy and breaches it in the other; deciding between them from $N$ reset records with both errors at most $1/4$ requires $N \ge c \sigma^2 (\Delta\eta)^{-(4K-2)}$.
"""

HORIZON_PROOF = r"""\begin{proof}[Proof of Proposition~\ref{prop:interventions}(iii)]
Let $x_K < 1$ be the largest node of the $K$-point Gauss--Legendre rule on $[-1, 1]$, and place the hard pair of Theorem~\ref{thm:cost}, with a common persistence and total merged weight $W$, on $r_c + \Delta\eta[-1, 1]$ with $r_c = \hat r + (1 + x_K)\Delta\eta/2$. Its memories lie in $[\hat r - \Delta\eta, \hat r + 2\Delta\eta]$. The Gauss--Radau economy has an atom of weight $W/K^2$ at $r_c - \Delta\eta < \hat r$, because the endpoint weight of the $K$-point Gauss--Radau rule on $[-1, 1]$ is $2/K^2$. Every memory of the Gauss economy is at least $r_c - x_K\Delta\eta > \hat r$. Group $i$ contributes $\kappa q_i = \kappa w_i/(1 - r_i)$ to the budget, so the restriction removes at least $\kappa W/K^2$ in the Gauss--Radau economy and nothing in the Gauss economy. The budgets themselves, $a + \kappa\int (1 - r)^{-1}\,dM(r)$, differ by $O((\Delta\eta)^{2K-1})$, because the merged measures match moments $0, \dots, 2K-2$ and $(1 - r)^{-1}$ is smooth near $r_c$. For small $\Delta\eta$ the budgets after the restriction therefore differ by at least $\kappa W/(2K^2)$, and every ceiling between them is met in one economy and breached in the other. The record length is that of Theorem~\ref{thm:cost}(ii), which concerns the same pair.
\end{proof}

"""

TAIWAN_QUAL = r"""

Four qualifications apply. First, the range $[-0.028, 0.028]$ in item~2 fills the cap by construction: two classes can share one memory with large weights of opposite sign, which leaves the aggregate kernel unchanged, so the width is set by the cap on each class's contribution, not by the data (the extreme compositions the search finds have weights $-9.0$, $4.6$ and $4.7$). Weights restricted to one sign would exclude these compositions; we have not computed the range under that restriction. The fitted relabelings that satisfy the restrictions have identical kernels. Second, the tagged intervals in Table~\ref{tab:taiwan} assume that each class's feedback decays at the persistence of its own flow, while the price-only comparisons let feedback memory vary with non-feedback flow held fixed. Third, item~3 rests on the grant: the price-only supervisor is given the persistences $a_j$, the impact $\kappa$ and the non-feedback law, all estimated with the tagged flows; with feedback contributing $0.0017$ to a budget of $0.97$, separating the two from prices alone is the problem that Proposition~\ref{prop:interventions} assumes away. Fourth, the calendar-year conversion treats the 300 stocks as independent, whereas the common-date bootstrap accommodates cross-stock dependence and leaves the panel's effective sample size open; similarly, an archived Gaussian diagnostic compares exact and Whittle divergences at selected points without supplying a uniform bound over the search set. Finally, because the dealers' estimated response is negative, the calibrated economy lies outside the positive class of the lower bounds, although the Whittle rates, Pinsker's inequality, and relabeling invariance used here require no positivity."""


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



COMPOSITION_PROOFS_PART1 = r"""\begin{proof}[Proof of Theorem~\ref{thm:cost}]
Let $n=2K-1$ and normalize the $K$-node Gauss--Legendre and left Gauss--Radau rules to mass one. Both integrate degree $n-1$ exactly. Their degree-$n$ moments differ because the monic polynomial $(s+1)\prod_{j>1}(s-s_j)^2$ vanishes at all Radau nodes and has positive integral, which the Gauss rule integrates exactly. Scale the nodes by $r_c+\Delta\eta s$ and masses by $W$. Taylor expansion gives $|\Delta k_m|\le 2W\binom{m}{n}(\Delta\eta)^n(r_c+\Delta\eta)^{m-n}$ for $m\ge n$, with zero difference before that and $|\Delta k_n|\asymp(\Delta\eta)^n$. In particular $\|\Delta k\|_1=O((\Delta\eta)^n)$ uniformly.

Write the innovation filter as $B_X(z)=[1-az-\kappa z\sum_{m\ge0}k_{X,m}z^m]^{-1}$ in the lag variable and the reset response as $h_X=\kappa B_X$. The uniform stability bound gives bounded $\ell^1$ norms of the filters by the geometric series for the inverse. Subtracting the inverse filters shows $\|h_1-h_0\|_2\le C\|\Delta k\|_1$; the first nonzero difference is $\kappa^2\Delta k_n$ at lag $n+1$. The reset KL is $N\|h_1-h_0\|_2^2/(2\sigma^2)$ for the observed taps. Both errors at most $1/4$ imply TV at least $1/2$ and KL at least $1/2$ by Pinsker.

For stationary prices the spectral ratio is $f_1/f_0=|B_1/B_0|^2=1+O((\Delta\eta)^n)$ uniformly, with spectra bounded above and away from zero. The leading ratio term is twice the real part of a nonzero analytic function on the disk which vanishes at zero: use the resolvent identity and the leading Taylor term of $\sum_m \Delta k_m z^m$, whose coefficient at $z^n$ is nonzero. Its real part cannot vanish identically on the unit circle: it is harmonic on the disk, so it would then vanish on the whole disk by the maximum and minimum principles for harmonic functions, making the function an imaginary constant, which is zero because the function vanishes at zero. The integral of its square over the circle is therefore positive. Thus the Gaussian spectral integral of $(f_1/f_0)-1-\log(f_1/f_0)$ has exact order $(\Delta\eta)^{2n}$. For finite records the uniform ratio bound sandwiches the two Toeplitz covariance matrices, putting the eigenvalues of their relative covariance within $O((\Delta\eta)^n)$ of one. Summing the quadratic bound on $\lambda-1-\log\lambda$ gives KL $\le CT(\Delta\eta)^{2n}$, so the same testing argument applies.

For recovery, the impulse recursion inverts the first $2K$ kernel taps triangularly, with nonzero divisor $\kappa h_0=\kappa^2$. Averaging independent Gaussian responses gives tap errors $O_P(\sigma/\sqrt N)$ at fixed depth. Centering the kernel moments at $r_c$ and dividing moment $j$ by $(\Delta\eta)^j$ gives errors $O_P(\sigma/(\sqrt N(\Delta\eta)^n))$. On the separated class the ordered rescaled moment map is injective by the Vandermonde equations for the difference of two atomic measures. Its Jacobian is a nonsingular confluent Vandermonde with weights bounded away from zero. The inverse function theorem and compactness give a uniformly Lipschitz local inverse. On its domain the Prony reconstruction returns that inverse, giving the stated fixed-accuracy rate.
\end{proof}

""" + MPV_PROOF + r"""\begin{proof}[Proof of Theorem~\ref{thm:cheap}]
The largest difference of $F_g$ between two positive measures of mass at most $\bar W$ with tap distance at most $\delta$ is the displayed modulus. To see this, enforce the norm constraint by infimizing $\delta\|c\|_2-c\cdot(k_1-k_0)$ over $c$. Exchange infimum and supremum by convex minimax on the weak-star compact pair of measure sets. The residual supremum is $\bar W\mathcal R(g-p_c)$, with $p_c(r)=\sum_{t<L}c_t r^t$. Two Gaussian means at tap distance below $2z_{1-\alpha}\sigma/\sqrt N$ have TV below $1-2\alpha$, so uniform coverage forces answer separation at most $2\epsilon$. Continuity of the modulus gives the boundary. For sufficiency center the residual range and use the affine tap estimate. Its worst-case bias is at most $\bar W\mathcal R(g-p_c)/2$ and its standard deviation is $\sigma\|c\|_2/\sqrt N$.

If the coefficients of $g$ belong to $\ell^2$, truncation gives uniform residual $O(\bar r^L)$ by Cauchy--Schwarz. Choose logarithmic depth to make it $O(\epsilon)$ with bounded coefficient norm. Conversely the necessary condition with $N=O(\sigma^2\epsilon^{-2})$ gives polynomial approximants with bounded coefficient norms and residual tending to zero. Pad their coefficients with zeros and extract a weakly convergent subsequence in $\ell^2$. Point evaluation on $[0,\bar r]$ is continuous on coefficient space, so the limit represents $g$. For (iii) compare zero mass with $c\delta_r$ where $c=d\sigma\sqrt{(1-r^2)/N}$, with $0<d<1-2\alpha$ and $d$ small enough that $c\le\bar W$. Even with all taps observed, the divergence of the averaged record is $N\sum_m c^2r^{2m}/(2\sigma^2)=d^2/2$, so by Pinsker's inequality the total variation is at most $d/2<1-2\alpha$, yet the answer separation $c\,|g(r)|$ is unbounded as $r\uparrow1$. This contradicts uniform coverage. The deterministic steps are checked in Lean~4 (\mbox{\nolinkurl{PublicationRevision13.lean}}; Supplement Table~\ref{S-tab:newlean}).
\end{proof}

"""

RECOVERY_PROOF = r"""\begin{proof}[Proof of Theorem~\ref{thm:recovery}]
Taylor expansion gives $k(z)=A\,\mathrm{diag}(\Delta^j)_{j=0}^{2K-1}\mu(z)+R_\Delta(z)$, where $\mu_j(z)=\sum_i w_i s_i^j$ and $A$ has the independent derivative columns divided by $j!$. The same injectivity and Jacobian argument as above gives a global lower Lipschitz constant for $\mu$ on the compact separated class: use local inversion near the diagonal, and compactness and injectivity away from it. Differentiating the Taylor remainder bounds its Lipschitz constant on the convex set $\mathcal{Z}$ by $O(\Delta^{2K})$; take $\Delta\le1$. For small $\Delta$, absorption gives $\|k(z)-k(z')\|\ge c\Delta^{2K-1}\|z-z'\|$. The triangular response inverse is Lipschitz on a bounded set containing the response class. Minimum distance therefore bounds the parameter error by $C\Delta^{-(2K-1)}$ times twice the Gaussian sample-mean noise norm. The Gaussian norm bound gives the stated tail probability. The deterministic steps are checked in Lean~4 (\mbox{\nolinkurl{PublicationRevision13.lean}}; Supplement Table~\ref{S-tab:newlean}).
\end{proof}

"""

HALT_PROOF = r"""\begin{proof}[Proof of Proposition~\ref{prop:interventions}(i)--(ii) and Corollary~\ref{cor:loss}]
Uniform scaling multiplies the feedback part of $S$ by $\theta$. For the halt, take the quadrature rules at the zeros of $p_K-cp_{K-1}$, where $p_j$ are orthonormal for the uniform probability on $[-1,1]$. For small $c$ the zeros stay simple and interior. The interpolatory rule integrates degree $2K-2$ exactly: divide by $p_K-cp_{K-1}$ and use orthogonality of the quotient of degree at most $K-2$. Products of the Lagrange polynomials show that their squared norms are the weights. Normalizing them to an orthonormal basis gives weight $1/\sum_{j<K}p_j(s)^2$ at a node $s$. As $c$ varies, a node cannot recur, since consecutive orthogonal polynomials have no common zero by the three-term recurrence. Each weight level set is finite, so two such rules have distinct largest weights. After shifting and scaling, Taylor expansion of $(1-r)^{-1}$ gives an $O((\Delta\eta)^{2K-1})$ difference in total feedback. The largest activities converge to the different largest masses divided by $1-r_c$, giving separated post-halt budgets for small spacing. The reset KL proof above applies to this moment-matched pair.

For the binary decision let $A$ be the event of choosing the halt. Its excess loss is $(bP_0(A)+cP_1(A^c))/2\ge \min(b,c)(1-\TV)/2$. Apply Pinsker and solve for the required length. For equal-covariance Gaussian records the equal-prior likelihood rule has each error $\Phi(-\sqrt{N}\|d\|/(2\tau))$; the normal tail bound gives the displayed risk bound. The deterministic steps are checked in Lean~4 (\mbox{\nolinkurl{PublicationRevision13.lean}}; Supplement Table~\ref{S-tab:newlean}).
\end{proof}

"""

TAGS_PROOF = r"""\begin{proof}[Proof of Theorem~\ref{thm:tags}]
The first two noiseless class-flow coordinates are $w_i h_0$ and $w_i(h_1+r_i h_0)$. Since $h_0=\kappa>0$ and $w_i$ is bounded below, sample averages of these and of the price taps estimate both parameters with error $O_P(N^{-1/2})$ uniformly, using ratios on an event where denominators stay bounded away from zero. This suffices for fixed weight accuracy and for the specified shrinking rate accuracy. In an interior ball choose two rate vectors separated by more than twice the target, with identical weights. Their physical rates differ by $O(\Delta\eta)$, and the finite observed means differ by $O(\Delta\eta)$ by smoothness. Thus the Gaussian two-point bound requires order $(\Delta\eta)^{-2}$ tagged experiments. The untagged weight comparison follows from Theorem~\ref{thm:cost}. The deterministic steps are checked in Lean~4 (\mbox{\nolinkurl{PublicationRevision13.lean}}; Supplement Table~\ref{S-tab:newlean}).
\end{proof}

"""


INSTRUMENT_THEOREM = r"""

\textbf{Endogenous desk adjustments to taxes, holding schedules, and caps.} When policy acts indirectly through trading costs or quantity limits rather than direct scaling, certifying the post-policy budget requires mapping the instrument into each desk's chosen trading intensity. Suppose a desk with fixed memory rate $r$ chooses scale $q \ge 0$ on the normalized filter $y_t=(1-r)\sum_{j\ge0}r^j x_{t-1-j}$ of a centered stationary Gaussian reference price signal (observed over a reference sample of length $n$), revising its exposure every $h$ periods at known preference and belief parameters $\beta, b > 0$ and $\rho \in [0, 1]$ (perceiving period-$j$ expected return $\beta \rho^j y_t$). Writing $V=\operatorname{Var}(y_t)$, $D_h=\Var(y_t-y_{t-h})$, $T_h=h^{-1}\sqrt{2D_h/\pi}$, and $A_h=h^{-1}\sum_{j<h}\rho^j$, per-date perceived surplus under a proportional volume tax $\tau$, quadratic adjustment charge $\nu$, and turnover cap $c \in (0, \infty]$ is
\[
 (\beta A_h V-\tau T_h)q-\tfrac12(bV+\nu D_h/h)q^2,
 \qquad q\ge0,\quad qT_h\le c .
\]
Aggregating desks of common memory rate $r$ from baseline scale $q^0(r)>0$ to policy scale $q^1(r)$ (evaluated at cycle-averaged constant-signal exposure) reduces the fixed-$(a,\kappa)$ feedback budget by $\kappa F_g(M)$, where $g(r)=(1-q^1(r)/q^0(r))/(1-r)$.

\begin{proposition}[Partial-equilibrium incidence of price and quantity instruments]\label{thm:instruments}
Fix $0 < \bar{r} < 1$, bounded total merged weight, common $(\beta, b, \rho)$, and pre-policy covariances and impact $(V, D_h, a, \kappa)$ away from kinks, with memories in $[r_{\min}, \bar{r}]$ ($r_{\min} > 0$) when $(a, \kappa)$ are estimated jointly or $[0, \bar{r}]$ when $a$ is known. Consider either the benchmark experiment of $N$ Gaussian impulse-response records (with known $\kappa$) plus an independent length-$n$ reference sample, or a single passive stationary pricing-error record of length $n$ from~\eqref{eq:baseline} with known $a$, $S \le \bar{S} < 1$, and innovation variance bounded above and away from zero.
\begin{enumerate}
\item[(i)] \emph{Trading costs.} With $h=1$, $\tau=0$, and $c=\infty$, a sufficiently small quadratic charge $\nu > 0$ yields a square-summable Taylor series for $g$: the budget reduction is estimable at logarithmic lag depth with error $O_P(n^{-1/2}+\sigma N^{-1/2})$, and from the passive record alone with error $O_P(n^{-1/2})$ without impulse probes, a separate reference sample, or known $\kappa$. By contrast, a proportional tax $\tau > 0$ can violate square-summability even when all desks remain active ($1-q^1/q^0=d\sqrt{1+r}$, $d > 0$, under white-noise reference prices).
\item[(ii)] \emph{Scheduled revisions.} Lengthening the revision cycle from $1$ to $h$ dates at small $\nu > 0$ ($\tau=0, c=\infty$) decomposes $g$ into a square-summable component estimable at the rates in~(i) plus $(1-A_h)/(1-r)$, which vanishes when $\rho=1$ and otherwise requires the initial aggregate budget (allowing a negative net reduction in cycle-averaged exposure).
\item[(iii)] \emph{Exit.} Under a proportional tax, a transversal zero of $\beta V-\tau T_1$ at an interior memory rate creates a kink in $g$. In the reset model of Theorem~\ref{thm:cost} under a common reference law, there exist moment-matched $K$-group pairs near the exit threshold---one with exit, one with all groups active---whose budget reductions differ by order $\Delta\eta$, requiring $N\ge c_*\sigma^2(\Delta\eta)^{-(4K-2)}$ records to separate with both error probabilities below $1/4$.
\item[(iv)] \emph{Turnover caps.} With $h = 1$, a positive per-desk cap $c$ crossing smooth unconstrained turnover transversally likewise induces an order-$\Delta\eta$ kink in $g$, so the $(\Delta\eta)^{-(4K-2)}$ lower bound of~(iii) applies both to estimating the reduction and to deciding whether the cap binds.
\end{enumerate}
\end{proposition}

Proposition~\ref{thm:instruments} evaluates partial-equilibrium incidence for scheduled holdings at fixed $(V, D_h, a, \kappa)$; modeling resting-order cancellation requires a limit-order execution model, finite closed-loop policies shift $(V, D_h)$ and $(\kappa, D, a^*)$ via Theorem~\ref{thm:inv-eq} (Supplement Sections~\ref{S-app:instruments}--\ref{S-app:passiveincidence}), and unexempted proportional taxes in mixed-sign markets can drive out low-margin contrarian liquidity suppliers ($w_i < 0$) first, raising net $S$ (Supplement Section~\ref{S-sec:margin_scaling}).
"""

INSTRUMENT_PROOF = r"""\begin{proof}[Proof of Proposition~\ref{thm:instruments}]
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

Estimate $g$ from the same sample covariances. The analytic terms extend uniformly to a disk larger than the unit disk, so their coefficients have a uniform weighted sum bound $\sum_m R^m|c_m|\le B$ for some $R>1$. Fit the pilot at logarithmic depth under that bound. Its fitted polynomial approximates $g$ on the memory interval with $O_P(n^{-1/2})$ error by the preceding approximation argument. Choose $R^{-1}<s<1$. Cauchy's integral estimate gives $|\sum_m\hat c_m(\hat J_m-J_m)|\le B\|\hat J-J\|_s$. Integrating the weight error costs at most $\kappa M([0,\bar r])\|\hat g-g\|_\infty$. These pathwise bounds allow both fits to use the same observations. The deterministic steps are checked in Lean~4 (\mbox{\nolinkurl{PublicationRevision14.lean}}; Supplement Table~\ref{S-tab:newlean}). Supplement Section~\ref{S-app:passiveincidence} gives details.

At an interior transversal exit or binding point $r_*$, the positive part gives a nonzero jump $\Delta g'$ of the one-sided derivative of $g$. Locally $g(r)=g(r_*)+g'_-(r-r_*)+\Delta g'(r-r_*)_++O((r-r_*)^2)$. Reflect the Gauss--Legendre and left Gauss--Radau pair of Theorem~\ref{thm:cost} and place it so that only the Radau endpoint lies on the clipped side, at distance $u\Delta\eta$ for a fixed $u>0$. A reflection of the construction for Proposition~\ref{prop:interventions}(iii) gives the opposite orientation if needed. The affine terms cancel, and the lone endpoint generates a nonzero term of magnitude $|\Delta g'|Wu\Delta\eta/K^2$. The quadratic remainder is $O((\Delta\eta)^2)$. The common reference record carries no additional information about the pair. The reset KL is $O(N(\Delta\eta)^{4K-2}/\sigma^2)$ from moment cancellation. Applying the same two-point test to the binary decision or to estimates with disjoint accuracy intervals proves the bounds. For caps, the policy scale is $\min(q^0,c/T_1)$ and the same derivative jump follows at a transversal binding point.
\end{proof}

"""
def build(text):
    t = reletter(text)
    # ---------------------------------------------------------------- preamble and front matter
    t = rep(t, "\\usepackage{fancyhdr}\n\\usepackage{hyperref}\n",
            "\\usepackage{fancyhdr}\n\\usepackage{xr-hyper}\n\\usepackage{hyperref}\n"
            "\\externaldocument[S-]{Paper1_JEDC_online_supplement}\n"
            "\\graphicspath{{../paper1_core/}{../paper1_note/}}\n")
    t = rep(t, "\\setlength{\\parskip}{4pt plus 1pt minus 1pt}\n\\setlength{\\parindent}{1.2em}\n\\linespread{1.12}\n",
            "\\setlength{\\parskip}{2.5pt plus 1pt minus 1pt}\n\\setlength{\\parindent}{1.2em}\n\\linespread{1.03}\n\\emergencystretch=3em\n")
    t = rep(t, "\\begin{document}\n\n\\thispagestyle{empty}", "\\begin{document}\n\\hypersetup{pageanchor=false}\n\\thispagestyle{empty}")
    t = rep(t, "\\newpage\n\\setcounter{page}{1}\n", "\\newpage\n\\hypersetup{pageanchor=true}\n\\setcounter{page}{1}\n")
    t = re.sub(r"(\\begin\{abstract\}\n\\noindent\n).*?(\n\\end\{abstract\})",
               lambda m: m.group(1) + ABSTRACT + m.group(2), t, count=1, flags=re.S)
    t = rep(t, r"\noindent\textbf{Online Supplement and Replication:} Technical lemmas,",
            r"\noindent\textbf{Online Supplement and Replication:} References of the form ``Supplement Theorem~S4.1'' are to the Online Supplement, which states every result in full; the full working paper (Niroula et al., 2026d) collects further results on the feedback model. Technical lemmas,")
    t = rep(t, r"\textbf{Funding and competing interests.}",
            r"\textbf{Related manuscripts.} An earlier working paper of the same authors (Niroula et al., 2026a, dated 5 November 2026) studied the same model; this article supersedes it. The earlier paper, the companion note (Niroula et al., 2026c) and the full working paper (Niroula et al., 2026d) are in the repository cited below.\par\medskip" + "\n\n" + r"\textbf{Funding and competing interests.}")
    # ---------------------------------------------------------------- introduction
    t = rep(t, r"what requires class-tagged or owner-linked supervisory reporting.",
            r"what requires class-tagged or owner-linked supervisory reporting." + "\n\n" +
            r"To see the mechanism, consider algorithms that trade on exponentially weighted past pricing errors at different decay rates. Because transaction prices clear only \emph{aggregate} order flow, individual speeds blend together: two equal-sized groups with memory rates $0.49$ and $0.51$ ($\Delta = 0.01$) generate nearly the same aggregate flow as a single group at $0.50$. First- and second-order differences cancel, leaving an $O(\Delta^3)$ lag-curvature gap that requires $O(\Delta^{-6})$ noisy observations to detect---and $O(\Delta^{-(4K-2)})$ for $K$ nearby groups. Public prices therefore suffice to calibrate a uniform market-wide cut, whereas selective class halts require trader-level reporting---and even class tags fail if restricted traders can reroute orders across labels or crowd their speeds together to hide.")
    t = rep(t, r"In a Gaussian feedback market, the Kullback--Leibler divergence between two candidate populations equals half the cumulative excess mean-squared forecast error from confusing them (Theorem~\ref{thm:forecast-kl}); hence composition",
            r"In a Gaussian feedback market, the Kullback--Leibler divergence between two candidate populations equals half the cumulative excess forecast MSE divided by innovation variance (Theorem~\ref{thm:forecast-kl}); composition")
    t = rep(t, r"Because prices cannot distinguish label permutations, a uniform cut across all feedback activity weakly dominates every price-based policy against the worst labeling consistent with the record for any convex loss and label-symmetric cost—and is the unique minimax supervisory policy whenever the cost is strictly convex (Theorem~\ref{thm:minimax}).",
            r"Because prices cannot distinguish label permutations, a uniform cut across all feedback activity does at least as well as every price-based policy against the worst labeling consistent with the record, for any convex loss and label-symmetric cost: it is minimax over labelings, Bayes under an exchangeable prior, and, under continuous strictly convex cost, the unique minimax policy (Theorem~\ref{thm:minimax}). Given persistence, impact, and a memory bound, impulse-response lags estimate the pre-policy budget (Section~\ref{sec:supervision}), pinning down the uniform cut under exogenous $(a, \kappa)$ while shifting equilibrium impact and persistence jointly when dealers re-price risk (Theorem~\ref{thm:inv-eq}; Supplement Section~\ref{S-app:instruments}).")
    t = rep(t, r"Only an owner-linked audit trail that ties accounts to beneficial owners retains its value.",
            r"An owner-linked audit trail that ties accounts to beneficial owners retains its value whenever beneficial-ownership links prevent cross-account routing.")
    t = rep(t, r"\item \emph{The surveillance paradox.} Without class tags, an untagged algorithm facing a level-$\alpha$ detection test crowds its memory rate toward its neighbor as the supervisor's data record $N$ grows. Whenever the identification divergence scales as $c N D^p$ with $p > 2$ (including $p=4$ for symmetric splitting and $p=6$ for moment-matched two-group hiding), crowding more than offsets the added data: the supervisor's equilibrium information falls to zero at rate $N^{-2/(p-2)}$ (e.g., $N^{-1/2}$ for $p=6$), detection probability collapses to the false-alarm rate $\alpha$, and the trader incurs a permanent strategy distortion cost (Theorem~\ref{thm:paradox}). Class tags eliminate this crowding.",
            r"\item \emph{The surveillance paradox.} Against any standard local-power test, a high-stakes untagged algorithm crowds its memory rate toward its neighbor as the supervisor's record $N$ grows. Against the closest merged economy in the composite null, divergence scales as $N\delta^4$ in the memory distance $\delta$, so crowding more than offsets additional data: the supervisor's information falls at rate $N^{-1}$, detection collapses toward the false-alarm rate $\alpha$, and the trader bears a permanent strategy distortion (Theorem~\ref{thm:paradox}). Memory-independent tag inquiries eliminate this incentive.")
    t = rep(t, r"Our contribution is economic: we show that kernel sufficiency survives endogenous inventory-equilibrium pricing; establish the exact equivalence between supervisory identification and forecast loss in a feedback market; prove the minimax optimality of uniform (and group-uniform) supervisory policies; solve the strategic relabeling disclosure game comparing class tags to owner-linked audit trails; and derive the negative equilibrium identification rate of the surveillance paradox.",
            r"That market-wide policies need only a reduced-form aggregate while targeted ones need structure is Marschak's maxim and the logic of sufficient statistics for policy (Marschak, 1953; Chetty, 2009); what we add is the informational price of that structure in a feedback market. Specifically, we show that kernel sufficiency survives endogenous inventory-equilibrium pricing (where dealer anticipation over-weights slow memories), characterize which linear functionals prices answer at parametric rates, establish minimax optimality of uniform and group-uniform policies over unknown labelings, solve the strategic relabeling game between class tags and owner-linked audit trails, and derive how strategic crowding degrades untagged surveillance (using the Gaussian chain rule in Theorem~\ref{thm:forecast-kl} to link detection and forecast loss).")
    t = rep(t, r"Tagged flows carry $4.7 \times 10^5$ times more information per stock-day about class composition than prices alone. Over all compositions statistically indistinguishable from the full panel price record, the effect of a uniform feedback cut is tightly pinned to $[0.0014, 0.0019]$, whereas the effect of halting foreign feedback spans $[-0.028, 0.028]$.",
            r"Holding each class's non-feedback flow law fixed, tagged flows carry $4.7 \times 10^5$ times more information per stock-day about composition than prices alone. Given market persistence, impact, and non-feedback flow, a spectral-rate search pins market-wide cut effects to $[0.0014, 0.0019]$, whereas the price-consistent effect of halting foreign feedback spans $[0, 0.0018]$ under nonnegative weights---ranging from zero to nearly the entire aggregate effect (Section~\ref{sec:taiwan}).")
    t = rep(t, r"our results establish precisely which features of a trader population are recoverable from prices and at what statistical cost.",
            r"Our results establish precisely which features of a trader population are recoverable from prices and at what statistical cost. Feedback traders are central to models of destabilizing speculation and of return autocorrelation (De Long et al., 1990; Cutler et al., 1990; Sentana and Wadhwani, 1992), and simulation-based estimation of agent-based models (Grazzini and Richiardi, 2015; Platt, 2020) faces the same identification question in nonlinear models. Our identification result is global (Theorem~\ref{thm:what-id}); where memories collide, the information matrix of Rothenberg (1971) is singular, and Theorems~\ref{thm:cost} and~\ref{thm:recovery} give the rate at which identification weakens near a collision. Our minimax results are decisions under ambiguity in the sense of Manski (2000).")
    t = rep(t, r"Our setting isolates a distinct mechanism: under a common public signal, identity is irrelevant for price discovery and forecasting, yet essential for assigning targeted supervisory interventions.",
            r"Our setting isolates a distinct mechanism: under a common public signal, identity is irrelevant for price discovery and forecasting, yet essential for assigning targeted supervisory interventions. Inventory-based price impact goes back to Ho and Stoll (1981) and Grossman and Miller (1988), and Hendershott and Menkveld (2014) measure it. Crowding among algorithmic and quantitative strategies is documented by Chaboud et al.\ (2014) and Khandani and Lo (2011) and analyzed by Stein (2009); pre-trade anonymity in limit-order markets, which concerns who quotes rather than who trades on feedback, is studied by Foucault et al.\ (2007).")
    t = rep(t, r"provides a formal rationale for that architecture: market-wide remedies require only prices, targeted restrictions require class records, and relabeling incentives necessitate owner-linked audit trails.",
            r"provides a formal rationale for that architecture: market-wide remedies require only prices, targeted restrictions require class records, and cheap relabeling favors owner-linked audit trails. Acting on market information can degrade it (Bond et al., 2010; Bond and Goldstein, 2015), and manipulation muddles the signals a principal relies on (Frankel and Kartik, 2019, 2022; Perez-Richet and Skreta, 2022).")
    t = rep(t, r"whereas compositional weights require $\Delta^{-(4K-2)}$ observations (Theorem~\ref{thm:cheap} and Corollary~\ref{cor:sep}).",
            r"whereas compositional weights require $\Delta^{-(4K-2)}$ observations (Theorem~\ref{thm:cheap} and Corollary~\ref{cor:sep}), including when an enforceable horizon cutoff replaces a class label (Proposition~\ref{prop:interventions}(iii)). Smooth quadratic trading charges admit parametric estimation from passive Gaussian pricing-error records given persistence $a$, whereas proportional taxes, exit thresholds, and binding turnover caps incur non-analyticity barriers (Proposition~\ref{thm:instruments}).")
    # ---------------------------------------------------------------- model, sufficiency, equilibrium
    t = rep(t,
        r"Let $x_t$ denote the pricing error—the gap between the transaction price $p_t$ and the asset's fundamental value $F_t$.",
        r"In theoretical Sections~\ref{sec:model}--\ref{sec:supervision}, let $p_t$ and $F_t$ denote dollar prices and fundamental value per share, and $x_t = p_t - F_t$ the dollar pricing error per share (making CARA-normal linear demand exact across long and short positions; empirical log-price proxies $\log P_t$ are reserved for Section~\ref{sec:taiwan}).")
    t = rep(t,
        r"$x_t, F_t, p_t$ & Pricing error ($x_t = p_t - F_t$), public fundamental, and transaction price \\",
        r"$x_t, F_t, p_t$ & Dollar pricing error ($x_t = p_t - F_t$), fundamental, and price (log proxy in Sec.~\ref{sec:taiwan}) \\")
    t = rep(t,
        r"$M, k_m, G(z)$ & Merged measure $\sum_i w_i \delta_{r_i}$, feedback kernel $k_m = \int r^m dM$, Stieltjes transform $\sum_i w_i/(z - r_i)$ \\",
        r"$M, S_M(D), G(z)$ & Merged measure $\sum_i w_i \delta_{r_i}$, Stieltjes transform $\sum_i w_i/(D - r_i)$, transfer $G(z) = \sum_i w_i z/(z - r_i)$ \\")
    t = rep(t,
        r"Reset probing is strictly an information-theoretic benchmark—not a proposed regulatory policy—demonstrating that even an unrealistically powerful probing supervisor cannot escape the $\Delta^{-(4K-2)}$ barrier.",
        r"Reset probing is strictly an information-theoretic benchmark—not a proposed regulatory policy, as unscheduled exploratory order injection on live venues is constrained by anti-manipulation and anti-spoofing statutes (15 U.S.C.\ \S\,78i; MAR Art.\ 12)—demonstrating that even an idealized probing observer cannot escape the $\Delta^{-(4K-2)}$ barrier.")
    t = rep(t,
        r"In the positive-feedback economy ($q_i \ge 0$), the closed-loop system~\eqref{eq:baseline} is Schur stable if and only if $S < 1$. ",
        r"In the positive-feedback economy ($q_i \ge 0$), the closed-loop system~\eqref{eq:baseline} is Schur stable if and only if $S < 1$; when $S \ge 1$, no stationary equilibrium exists and inventory variance diverges. "
        r"With contrarian groups ($q_i < 0$), $S < 1$ rules out a unit root at $\omega = 0$, $\sup_\omega |L(e^{i\omega})| < 1$ for $L(e^{i\omega}) = e^{-i\omega}(a + \kappa \sum_{m \ge 0} k_m e^{-i\omega m})$ gives a sufficient small-gain test, and necessary and sufficient Schur stability holds by the Nyquist criterion for $L(e^{i\omega})$ around $+1$ (all roots of $1 - z(a + \kappa \sum_{m\ge 0} k_m z^m) = 0$ outside $|z| \le 1$, Supplement Section~\ref{S-sec:mixed_sign}). ")
    t = rep(t,
        r"In model~\eqref{eq:baseline}, fix known $(a, \kappa)$ and zero initial group states, and compare noiseless probe responses.",
        r"In model~\eqref{eq:baseline}, fix known $(a, \kappa)$, $x_{-1} = 0$, and zero initial group states, and compare noiseless probe responses (Supplement Section~\ref{S-sec:suff}).")
    t = rep(t,
        r"where $\xi_t \sim N(0, \sigma_\xi^2)$ is i.i.d.\ noise trading (or supervisory probing priced by dealers as noise).",
        r"where fundamental innovations $\Delta F_t \sim N(0, \sigma_F^2)$ and exogenous flow shocks $\xi_t \sim N(0, \sigma_\xi^2)$ are mutually independent.")
    t = rep(t,
        r"The implicit function theorem yields a unique continuous branch near $(\kappa_-, 1)$ for small $G$.",
        r"The implicit function theorem applied on the Banach space $C^1([1-\delta, 1+\delta])$ for $S_M$ yields a unique continuous branch near $(\kappa_-, 1)$ for small $\epsilon = \|S_M\|_{C^1}$.")
    t = rep(t,
        r"\item[(ii)] \emph{Transmission zeros.} The memory rates $r_i$ remain the exact transmission zeros of the equilibrium price response.",
        r"\item[(ii)] \emph{Transmission zeros.} If $\bar{a} > 0$, the memory rates $r_i \in (0,1)$ are distinct, and weights $w_i > 0$, the $r_i$ remain the exact transmission zeros of the equilibrium price response.")
    t = rep(t,
        r"realized insider profit $\sum_{t < T}(v - p_t) X_t$, and dealer inventory $-\sum_{t < T} Y_t$ coincide pathwise.",
        r"realized insider profit $\sum_{t \le T}(v - p_t) X_t$, and dealer inventory $-\sum_{t \le T} Y_t$ coincide pathwise.")
    # ---------------------------------------------------------------- model, sufficiency, equilibrium
    t = rep(t, r"$D, D_0, p, J$ & Distance to neighbor's memory, preferred distance, divergence exponent ($p > 2$), divergence $J = cND^p$ \\",
            r"$\delta, \delta_0, n, J$ & Distance to the neighbor's memory, preferred distance, divergence exponent ($n = 4$), divergence $J = cN\delta^n$ \\")
    t = rep(t, r"we derive price impact and pricing-error persistence endogenously from competitive, risk-averse overlapping-generations dealers who bear inventory risk.",
            r"we derive price impact, and pricing-error persistence given the share of inventory that dealers carry over, from competitive, risk-averse overlapping-generations dealers who bear inventory risk.")
    t = rep(t, r"We now derive both endogenously from competitive, risk-averse dealers who carry inventory risk,",
            r"We now derive both in equilibrium from competitive, risk-averse dealers who take the overnight carry share $\bar{a} \in [0, 1)$ as given (passive capital absorbs $(1-\bar{a})H_{t-1}$ at the start of date $t$ while generation-$t$ dealers hold $H_t$ into $t+1$, with spreads or convex trading fees ruling out round-trip manipulation, Huberman and Stanzl, 2004; Supplement Section~\ref{S-sec:mixed_sign}),")
    t = rep(t, r"lay off a fraction $1 - \bar{a} \in (0, 1]$ of inventory each period",
            r"exogenously carry fraction $\bar{a} \in [0, 1)$ of inventory overnight while passive off-market capital absorbs $(1 - \bar{a})H_{t-1}$ at the start of date $t$")
    t = rep(t, r"As shown in the Online Supplement (Lemma~S1.1), both",
            r"As shown in Supplement Lemma~\ref{S-lem:micro}, both")
    t = rep(t, r"sufficiency extends to arbitrary nonlinear or profit-switching populations via the aggregate flow map (Online Supplement, Section~S2).",
            r"sufficiency extends to arbitrary nonlinear or profit-switching populations via the aggregate flow map (Supplement Section~\ref{S-sec:suff}).")
    t = rep(t, r"Let $G(D) = \sum_{i=1}^K w_i / (D - r_i) = \int (D - r)^{-1} \, dM(r)$ denote the Stieltjes transform of the merged measure $M$.",
            r"Let $S_M(D) = \sum_{i=1}^K w_i / (D - r_i) = \int (D - r)^{-1} \, dM(r)$ denote the Stieltjes transform of the merged measure $M$ (distinct from $G(z)$ in frequency space).")
    t = rep(t, r"D = 1 - \kappa G(D),", r"D = 1 - \kappa S_M(D),")
    t = rep(t, r"solely through $G$, and hence solely through the merged measure $M$.", r"solely through $S_M$, and hence solely through the merged measure $M$.")
    t = rep(t, r"\item[(iv)] \emph{Small feedback.} For small aggregate feedback intensity $G(1) = \sum_i q_i$ with $\Lambda_0 > 0$, there exists a unique equilibrium near $(\kappa_-, 1)$ satisfying",
            r"\item[(iv)] \emph{Small feedback.} Let $\Lambda_0 > 0$, fix $\delta > 0$ with $\max_i r_i < 1 - \delta$, and suppose $\epsilon = \sup_{|D - 1| \le \delta}(|S_M(D)| + |S_M'(D)|)$ is small. Then there exists a unique equilibrium near $(\kappa_-, 1)$, and with the aggregate feedback intensity $S_M(1) = \sum_i q_i$,")
    t = rep(t, r"D = 1 - \kappa_- G(1) + o(G(1)), \qquad", r"D = 1 - \kappa_- S_M(1) + o(\epsilon), \qquad")
    t = rep(t, r"\, G(1) + o(G(1)).", r"\, S_M(1) + o(\epsilon).")
    t = rep(t, r"Every sample-complexity lower bound derived below therefore holds \emph{a fortiori} under unobserved fundamentals (while Corollary~S7.2 in the Online Supplement shows that unknown primitives do not alter the upper-bound rate under active probes).",
            r"Every sample-complexity lower bound derived below therefore holds \emph{a fortiori} under unobserved fundamentals (while Supplement Corollary~\ref{S-cor:unknown_primitives} shows that unknown primitives do not alter the upper-bound rate under active probes). The positive results, identification and the upper bounds, assume that the pricing error is observed.")
    t = rep(t, r"This introduces a second exogenous innovation channel (analyzed in Online Supplement Section~S8) without altering pathwise kernel sufficiency (Theorem~\ref{thm:sufficiency}) or relaxing the $\Delta^{-(4K-2)}$ identification barrier for closely spaced memory rates.",
            r"This introduces a second exogenous innovation channel. It does not alter pathwise kernel sufficiency (Theorem~\ref{thm:sufficiency}), which allows any public signal, and the lower bound of Theorem~\ref{thm:smooth}, which allows any smooth causal rule of the observed history, still applies when the observed innovations are Gaussian.")
    t = rep(t, r"\end{remark}" + "\n\n" + r"\begin{theorem}[Identification results carry over to equilibrium]",
            r"\end{remark}" + "\n\n" + FRAGILITY_THEOREM + "\n\n" + r"\begin{theorem}[Identification results carry over to equilibrium]")
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
    t = rep(t, r"\end{table}" + "\n\n" + r"\subsection{Which questions prices answer cheaply}",
            r"\end{table}" + "\n\n" + MPV_THEOREM + "\n\n" + r"\subsection{Which questions prices answer cheaply}")
    t = rep(t, r"Theorem~\ref{thm:cheap} (Online Supplement, Theorem~S10.1 and Proposition~S10.2) specializes",
            r"Theorem~\ref{thm:cheap} (Supplement Theorem~\ref{S-thm:questions} and Proposition~\ref{S-prop:parametric}) specializes")
    t = rep(t, r"Groups & Memory rates & Half-lives (days) & $1 - S = 0.1$ & $1 - S = 10^{-6}$ \\",
            r"Groups & Memory rates & Half-lives (days) & Years ($1 - S = 0.1$) & Years ($1 - S = 10^{-6}$) \\")
    t = rep(t, r"matching the $\Delta^{-(4K-2)}$ sample order of Theorem~\ref{thm:smooth} (Online Supplement, Section~S18).",
            r"matching the $\Delta^{-(4K-2)}$ sample order of Theorem~\ref{thm:smooth} (Supplement Section~\ref{S-app:incoming}), though computing the global minimum over the non-convex set $\mathcal{Z}$ may be computationally costly.")
    # ---------------------------------------------------------------- forecasting
    t = rep(t, r"The next theorem provides the exact information-theoretic link: in a Gaussian feedback market, the information a price record carries about two competing populations is literally proportional to the cumulative forecast loss from mistaking one for the other.",
            r"The next theorem states the Gaussian chain rule in market terms: in a Gaussian feedback market, the information a price record carries about two competing populations equals half the cumulative excess forecast MSE divided by innovation variance. Populations that forecast alike are therefore hard to tell apart, and a uniform cut depends only on what forecasts reveal.")
    t = rep(t, r"(Online Supplement, Theorems~S18.1 and~S18.2)", r"(Supplement Theorems~\ref{S-n:irr} and~\ref{S-n:uniformlog})")
    # ---------------------------------------------------------------- supervision
    t = rep(t, "We now derive the regulatory implications of observational equivalence, moving from static prudential ceilings to minimax policy design, class-tagged disclosure, strategic relabeling, endogenous crowding, and an empirical calibration.",
            r"We now derive regulatory implications, moving from static ceilings and countercyclical pre-funded margin buffers to minimax policy design, class-tagged disclosure, and empirical calibration. Because fair-access statutes (U.S.\ Exchange Act \S\,6(b)(5); MiFID~II Art.\ 53(1)/18(3)) and prime-broker omnibus accounts bar arbitrary participant-specific halts, selective class halts serve here as an analytical benchmark; in continuous venues, predictable ceilings also invite circuit-breaker magnet runs (Subrahmanyam, 1994), favoring stress-thresholded randomized volatility interruptions with jittered clocks (Supplement Sections~\ref{S-sec:jittered_auctions}--\ref{S-sec:margin_scaling}).")
    t = rep(t, r"""\end{enumerate}
\end{proposition}

\begin{corollary}[Expected loss from weakly identified targeting]""",
            HORIZON_ITEM + r"""\end{enumerate}
\end{proposition}""" + UNIFORM_REMARK + INSTRUMENT_THEOREM + r"""

\begin{corollary}[Expected loss from weakly identified targeting]""")
    t = rep(t, r"\end{corollary}" + "\n\n" + r"Figure~\ref{fig:intervention}",
            r"\end{corollary}" + "\n\n" + POSTHALT_COROLLARY + "\n\n" + r"Figure~\ref{fig:intervention}")
    t = rep(t, r"Figure~\ref{fig:intervention} illustrates this contrast in a two-class economy: halting the largest class produces qualitatively opposite prudential outcomes across nearly indistinguishable economies, whereas a single verified class report collapses decision error by six orders of magnitude in sample size.",
            r"Figure~\ref{fig:intervention} illustrates this contrast in a two-class economy and an illustrative measurement experiment: halting the largest class produces qualitatively opposite prudential outcomes across nearly indistinguishable economies, whereas verified class reports cut the sample needed for a $5\%$ error by six orders of magnitude.")
    t = rep(t, r"\includegraphics[width=\linewidth]{fig2.png}", r"\includegraphics[width=.87\linewidth]{fig_intervention_revision.pdf}")
    t = rep(t, r"Panel~A uses the two-class construction of Online Supplement Section~S17",
            r"Panel~A uses the two-class construction of Supplement Section~\ref{S-app:revisiondecision}")
    t = rep(t, r"achieving $5\%$ error requires roughly $2.03 \times 10^6$ public-response repetitions versus $2$ class reports.}",
            r"achieving $5\%$ error requires roughly $2.03 \times 10^6$ public-response repetitions versus $2$ class reports (in Panel~A, the two uniform-scaling curves coincide to $O(\Delta^3)$; Panel~B is an illustrative reset benchmark rather than a live market policy).}")
    # minimax: labelings are pi (sigma is a noise level throughout)
    a = t.index(r"Let class $d \in \{1, \dots, K\}$ contribute $u_d = \kappa q_d$")
    b = t.index(r"Verified partial tags break permutation symmetry", a)
    span = t[a:b]
    span = span.replace(r"\sigma(c)", r"\pi(c)").replace(r"\sigma", r"\pi")
    t = t[:a] + span + t[b:]
    t = rep(t,
        r"Let class $d \in \{1, \dots, K\}$ contribute $u_d = \kappa q_d$ to the feedback budget, with total feedback $U = \sum_{d=1}^K u_d$.",
        r"Let class $d \in \{1, \dots, K\}$ contribute $u_d = \kappa q_d \ge 0$ to the feedback budget, with total feedback $U = \sum_{d=1}^K u_d \ge 0$ (if contrarian dealers have $u_D < 0$ as in Table~\ref{tab:taiwan}, halting an unverified label can target them and raise $S$ by $|u_D|$; Supplement Section~\ref{S-sec:mixed_sign}).")
    a = t.index(r"\begin{theorem}[Minimax value of partial tags]")
    b = t.index(r"\end{theorem}", a)
    t = t[:a] + t[a:b].replace(r"\sigma", r"\pi") + t[b:]
    t = rep(t, r"If $\pi$ is the unknown permutation assigning labels to underlying classes,",
            r"If $\pi$ is the unknown permutation assigning labels to underlying classes (a labeling),")
    t = rep(t, r"Because no price record distinguishes labelings (Theorem~\ref{thm:sufficiency}), every price-based policy is weakly dominated by a uniform policy against the worst consistent labeling.",
            r"Labels do not enter prices (Theorem~\ref{thm:sufficiency}), so no record distinguishes labelings; the uniform policy does at least as well as $\theta$ against the worst labeling (it is minimax) and on average over labelings (it is Bayes under an exchangeable prior).")
    t = rep(t,
        r"(or $\ell$ is strictly convex on $[a, a + U]$ with $U > 0$ and not all $u_d$ equal), then $\bar{\theta}\mathbf{1}$ strictly dominates every non-uniform policy $\theta \neq \bar{\theta}\mathbf{1}$, and the minimax problem admits a unique solution $\bar{\theta}^*\mathbf{1}$: the uniform cut is the unique minimax supervisory policy.",
        r"---or if $U \neq 0$, the class contributions $u_d$ are distinct, and $\ell$ is strictly convex on $[a + \sum_d \min(0, u_d),\, a + \sum_d \max(0, u_d)]$---then $\bar{\theta}\mathbf{1}$ strictly dominates every non-uniform policy $\theta \neq \bar{\theta}\mathbf{1}$, and the minimax problem admits a unique solution $\bar{\theta}^*\mathbf{1}$ (heterogeneous elastic exit is analyzed in Supplement Section~\ref{S-sec:elastic_exit}).")
    t = rep(t, r"Halting any single label $F$ is guaranteed to reduce the feedback budget only by $\min_d u_d$, and some labeling consistent with the price record attains this worst case.",
            r"Halting any single label $c \in \{1,\dots,K\}$ leaves worst-case post-halt budget $\max_\pi (S - u_{\pi(c)}) = S - \min_d u_d$, attained whenever $\pi(c) \in \arg\min_d u_d$ (reducing $S$ by at most $\min_d u_d$ when $u_d \ge 0$, and raising $S$ when $\min_d u_d < 0$).")
    t = rep(t, r"The proofs of Theorems~\ref{thm:minimax} and~\ref{thm:partial-minimax} and Corollary~\ref{cor:halt} are short and self-contained (Appendix~\ref{app:proofs}), and their finite combinatorial statements are verified in Lean~4 (the Online Supplement documents exact formalization scope across all results, separating machine-checked deterministic steps from paper-level probabilistic arguments). In numerical checks across $14{,}400$ random economies with three convex losses and three cost functions, the uniform policy is strictly better than non-uniform policies in $86\%$ of cases; across $1{,}200$ random tag partitions, partial tags deliver strictly positive value in $27\%$ of economies.",
            r"The proofs of Theorems~\ref{thm:minimax} and~\ref{thm:partial-minimax} and Corollary~\ref{cor:halt} (Appendix~\ref{app:proofs}; formalized in Supplement Table~\ref{S-tab:newlean}) specialize the finite-group Hunt--Stein theorem (Lehmann and Romano, 2005, Chapter~8), while heterogeneous elastic exit is analyzed in Supplement Section~\ref{S-sec:elastic_exit}. Integrating the permutation-average inequality over the common price law extends minimax dominance to price-contingent policy rules.")
    t = rep(t, r"As shown in the Online Supplement (Theorem~S5.4), tagging",
            r"As shown in Supplement Theorem~\ref{S-thm:partial}, tagging")
    t = rep(t, r"In the small-feedback equilibrium of Theorem~\ref{thm:inv-eq}(iv), each unit of aggregate feedback intensity $G(1) = \sum_j q_j$ raises equilibrium impact $\kappa$ by $\kappa_-^2(\bar{a} + 2A\kappa_-\sigma_\xi^2)/\sqrt{\Lambda_0} > 0$, creating a marginal dealer-inventory and price-dislocation externality $\lambda_{\mathrm{ext}} > 0$. If class $j \in \{\mathcal{H}, \mathcal{B}\}$ earns private value $b_j > 0$ per retained unit and imposes marginal feedback externality $\lambda_{\mathrm{ext}} \phi_j$, then",
            r"In the small-feedback equilibrium of Theorem~\ref{thm:inv-eq}(iv), each unit of aggregate feedback intensity $S_M(1) = \sum_j q_j$ raises equilibrium impact $\kappa$ by $\kappa_-^2(\bar{a} + 2A\kappa_-\sigma_\xi^2)/\sqrt{\Lambda_0} > 0$. Suppose the supervisor values a unit of feedback intensity, through the rise in impact and inventory risk it causes, at $\lambda_{\mathrm{ext}} > 0$, a parameter of its welfare criterion rather than an equilibrium object. If class $j \in \{\mathcal{H}, \mathcal{B}\}$ earns private value $b_j > 0$ per retained unit and adds $\phi_j$ to the feedback intensity, then")
    t = rep(t, r"\item[(i)] \emph{First-order welfare from inventory-equilibrium price impact.}",
            r"\item[(i)] \emph{Welfare weights from equilibrium impact.}")
    t = rep(t, r"Third, an audit trail linking accounts to beneficial owners preserves its full value $V_A$ regardless of $\gamma$.",
            r"Third, an owner-linked audit trail preserves its full value $V_A$ only when beneficial ownership is not severed by synthetic offshore total-return swaps ($\gamma_{\mathrm{TRS}}$) or multi-desk netting inside a single legal entity. In practice, natural-person reporting exemptions and litigation over Consolidated Audit Trail funding highlight both the governance costs $F_A$ and the institutional boundaries of owner-level linkage (Securities and Exchange Commission, 2025; Eleventh Circuit July 2025 decision in \emph{ASA v.\ SEC}; Supplement Section~\ref{S-app:relabel}), while firm-assigned labels remain gameable (Frankel and Kartik, 2022; Perez-Richet and Skreta, 2022).")
    t = rep(t, r"Online Supplement Theorem~S15.4 proves", r"Supplement Theorem~\ref{S-thm:relabelgeneral} proves")
    a = t.index(PARADOX_START)
    b = t.index(PARADOX_END, a) + len(PARADOX_END)
    t = t[:a] + PARADOX_NEW + t[b:]
    # ---------------------------------------------------------------- Taiwan
    t = rep(t, r"\subsection{Illustrative empirical calibration: Taiwan Stock Exchange tagged flows}",
            r"\subsection{Illustrative empirical calibration: Taiwan Stock Exchange tagged flows}\label{sec:taiwan}")
    t = rep(t, r"using stock fixed effects and stationary date-block bootstrap confidence intervals (Table~\ref{tab:taiwan}).",
            r"using stock fixed effects and stationary date-block bootstrap confidence intervals (Table~\ref{tab:taiwan}). For each stock, $x_t$ is the event-adjusted basis $\log P_t - \hat\beta \log\mathrm{TAIEX}_t$ minus its trailing 60-day mean, with $u_{c,t}$ reacting to $x_{t-1}$ and $x_t$ loading on $U_{t-1}$ (a two-day feedback loop; Supplement Section~\ref{S-app:barrier}).\footnote{Trailing-mean detrending induces AR(1) persistence near $0.975$; Figure~\ref{fig:twse_sensitivity}B and Supplement Table~\ref{S-tab:p1m_sensitivity} confirm that first-differencing $\Delta x_t$ and excluding price-limit days leave the class persistence estimates intact.} Market structure shapes these daily series: TWSE shortened its 5-second periodic call auction ($20\text{s}\to 5\text{s}$, 2013--2016), expanded day trading in 2014, widened daily price limits ($\pm 7\%\to\pm 10\%$, June~2015), publishes daily post-close institutional summaries permitting next-day copycatting outside Theorem~\ref{thm:sufficiency}, and shifted to continuous matching on 23~March~2020. In addition, aggregate dealers ($w_D = -0.022$) combine warrant hedging with proprietary dealer accounts (\texttt{DealerOwn}, $\hat w = +0.00295$), while unconstrained distributed lags reflect day-1 TWAP/VWAP parent-order slicing reversal followed by multi-day persistence ($\hat\beta_{F,1} = -1.235$ vs.\ lags $+0.741, +0.496$; Supplement Section~\ref{S-app:barrier}).")
    t = rep(t, r"(so only class composition is unknown) yields three sharp quantitative contrasts (Online Supplement, Section~S19):",
            r"(so only class composition is unknown) yields three quantitative contrasts (Supplement Section~\ref{S-app:barrier}). Price and tagged records are compared against separately optimized single-memory candidates with non-feedback flow held at its estimated law.")
    t = rep(t, r"Reaching $80\%$ power at a $5\%$ test size from prices alone requires at least $2.7 \times 10^9$ stock-years ($9.1 \times 10^6$ years across 300 independent stocks).",
            r"Substituting the asymptotic KL rate per stock-day yields a horizon benchmark of $2.7 \times 10^9$ years for one stock at $80\%$ power and $5\%$ size, or $9.1 \times 10^6$ years across 300 independent stocks.")
    t = rep(t, r"\item \emph{Uniform cut is pinned down by prices.} Over the exact same indistinguishable set, the effect of cutting all feedback uniformly lies within the tight band $[0.0014, 0.0019]$.",
            r"\item \emph{Uniform feedback reduction.} Across all price-consistent candidates found by the spectral search, setting total feedback to zero lowers the budget within $[0.0014, 0.0019]$.")
    t = rep(t, r"""\item \emph{Uniform feedback reduction.} Across all price-consistent candidates found by the spectral search, setting total feedback to zero lowers the budget within $[0.0014, 0.0019]$.
\end{enumerate}""",
            r"""\item \emph{Uniform feedback reduction.} Across all price-consistent candidates found by the spectral search, setting total feedback to zero lowers the budget within $[0.0014, 0.0019]$.
\end{enumerate}""" + TAIWAN_QUAL)
    t = rep(t, r"Two caveats discipline this calibration.", r"Two further caveats concern the data.")
    if round10.RES_A.exists():
        RA = json.loads(round10.RES_A.read_text())
        t = rep(t, round10.NOT_COMPUTED, round10.part_a_passage(RA) + round10.post_run_main(RA))
    if round10.RES_B.exists():
        second = (r"while the price-only comparisons let feedback memory vary with non-feedback flow held fixed.")
        t = rep(t, second, second + " " + round10.part_b_sentence(json.loads(round10.RES_B.read_text()),
                                                                   r"Table~\ref{tab:taiwan}"))
    t = rep(t,
            r"Fourth, the calendar-year conversion treats the 300 stocks as independent, whereas the common-date bootstrap accommodates cross-stock dependence and leaves the panel's effective sample size open; similarly, an archived Gaussian diagnostic compares exact and Whittle divergences at selected points without supplying a uniform bound over the search set. Finally, because the dealers' estimated response is negative, the calibrated economy lies outside the positive class of the lower bounds, although the Whittle rates, Pinsker's inequality, and relabeling invariance used here require no positivity.",
            r"Fourth, the calendar-year conversion assumes cross-stock independence (whereas the common-date bootstrap accommodates cross-stock dependence), and dealers' negative $w_D$ lies outside the positive class (though Whittle rates, Pinsker's inequality, and relabeling invariance still apply).")
    t = rep(t, r"Second, as documented in Online Supplement Section~S6, a pre-registered out-of-sample reverse-causality diagnostic on 2019--2023 holdout data cannot rule out",
            r"Second, in the 2019--2023 out-of-sample holdout (Figure~\ref{fig:twse_sensitivity}; Supplement Sections~\ref{S-sec:scope} and~\ref{S-app:barrier}), let $\hat D_{\mathrm{OOS}}$ denote the proportional out-of-sample MSE reduction in forecasting class flow from $x_{t-1}$ beyond own-flow persistence: Foreign predictability is positive ($\hat D_{\mathrm{OOS}} = 0.0410$, $95\%$ CI $[0.0197, 0.0623]$, block-60 $p=0.0019$, rising from $0.0319$ in the 5s call auction to $0.0421$ after 23~March~2020), but attenuates in 2022--2023 ($+0.0166, -0.0175$), Trust and proprietary dealers are null ($p_{\mathrm{Holm}}=1.0$), finite-sample plug-in standard errors are severely downward-biased relative to the block bootstrap, and the reverse-causality placebo ($\hat D_{\mathrm{OOS}} = -0.0083$, $[-0.0332, +0.0150]$) cannot rule out")
    t = rep(t, r"Accordingly, these figures serve as an illustrative calibration",
            r"Positive feedback in foreign flows is documented across markets (Froot et al., 2001; Griffin et al., 2004; Richards, 2005), while Wu and Wang (2020) measure turnover rather than signed trader-type feedback. Accordingly, these figures serve as an illustrative calibration")
    t = rep(t,
        r"; in intraday limit-order-book markets where aggregate feedback shares $\kappa \sum_i q_i$ are economically larger (as in the Section~\ref{sec:equilibrium} equilibrium calibrations underlying Figures~\ref{fig:near-instability} and~\ref{fig:intervention}), the same $(\Delta\eta)^{-(4K-2)}$ barrier operates with direct prudential significance.",
        r"; evaluating a high-feedback venue would require separate evidence on whether shares $\kappa\sum_i q_i$ are economically larger (as in the Section~\ref{sec:cost} and Supplement Section~\ref{S-app:revisiondecision} parameterizations underlying Figures~\ref{fig:near-instability} and~\ref{fig:intervention}), where the same $(\Delta\eta)^{-(4K-2)}$ barrier carries direct prudential weight.")
    t = rep(t, r"aggregate price persistence $\sum_{j=1}^5 a_j = 0.97$.} \\",
            r"aggregate price persistence $\sum_{j=1}^5 a_j = 0.97$.} \\" + "\n" +
            r"\multicolumn{4}{@{}l}{\footnotesize Within-stock $R^2$: price equation $0.95$; rules $0.14$ (Foreign), $0.18$ (Trust) and $0.10$ (Dealers).} \\")
    fig3 = (
        "\n\n"
        r"\begin{figure}[!htbp]" + "\n"
        r"  \centering" + "\n"
        r"  \includegraphics[width=.80\linewidth]{fig_twse_sensitivity.pdf}" + "\n"
        r"  \caption{TWSE empirical sensitivity and 2019--2023 out-of-sample holdout. "
        r"Panel~A: limit-masked Foreign proportional MSE gain $\hat{D}_{\mathrm{OOS}}$ ($95\%$ block-20 CI) across the pooled holdout ($0.0410$), pre/post-23-March-2020 matching regimes ($0.0319 \to 0.0421$), annual subsamples, and reverse-causality placebo ($-0.0083$). "
        r"Panel~B: estimated persistence $\hat{r}_c$ ($95\%$ CI) across Baseline, Limit-Excluded ($\hat{\kappa}=0.00409$), and First-Differenced $\Delta x_t$ ($\sum \hat{a}_j=-0.109$, $\hat{\kappa}_{\Delta x}=0.00209$).}" + "\n"
        r"  \label{fig:twse_sensitivity}" + "\n"
        r"\end{figure}"
    )
    t = rep(t, r"\end{table}" + "\n\n" + r"Granting a price-only supervisor",
            r"\end{table}" + fig3 + "\n\n" + r"Granting a price-only supervisor")
    # ---------------------------------------------------------------- conclusion
    t = rep(t, r"First, market-wide interventions (such as uniform feedback cuts or market-design changes calibrated to aggregate response) are statistically well-posed from public prices and are minimax-optimal when class identities are unverified.",
            r"First, market-wide feedback cuts are minimax-optimal over unknown labelings and can be calibrated from impulse-response lags given market persistence, impact, and a memory bound---while smooth quadratic charges admit passive estimation from pricing errors alone, unlike proportional taxes and binding caps (Proposition~\ref{thm:instruments}).")
    t = rep(t, r"durable targeted supervision requires owner-linked audit trails—such as",
            r"owner-linked reporting can support targeted supervision when beneficial-ownership links hold, as illustrated by")
    t = rep(t, r"Our passive sample-complexity bounds assume Gaussian (or quadratically regular) innovations and exclude bounded-support noise laws.",
            r"Our passive bounds require Gaussian (or quadratically regular) innovations and exclude bounded-support laws. Theorem~\ref{thm:paradox} fixes the test, whereas endogenizing costly monitoring yields either Stackelberg collapse ($\alpha_N^* = 0$) or simultaneous mixed-strategy auditing ($p^* > 0$, with no pure Nash equilibrium) under high stakes ($L(1-\alpha) > k\delta_0^2$, vs.\ separation $\delta_N^* \to \delta_0$ under low stakes or $N^{-1/(n-1)}$ GLRT slowing; Proposition~\ref{prop:endogenous_supervisor}), abstracting from repeated reputation. The Taiwan calibration holds persistence and impact fixed and relies on asymptotic rate proxies, leaving pure causal feedback and cross-stock independence open, while discrete time abstracts from continuous-book cancellations and sub-millisecond races (Supplement Sections~\ref{S-sec:scope} and~\ref{S-sec:natural_experiments}, Proposition~\ref{S-prop:natural_exp}).")
    # ---------------------------------------------------------------- declarations
    old_ai = r"All mathematical proofs, economic arguments, empirical calculations, and formal statements were independently verified and edited by the authors, who take full responsibility for the content of the publication."
    if CORRECTIONS_CHECKED_BY_FIRST_AUTHOR:
        new_ai = (r"After using these tools, the authors independently reviewed, verified, and edited all mathematical proofs, "
                  r"calculations, and prose (including all extensions finalized during 21--26 November 2026), and take full responsibility for the content of the publication. "
                  r"Lean~4 checks certify only the formal deterministic statements cataloged in the Online Supplement tables, not probabilistic steps, empirical validity, or novelty.")
        review_ai = ""
        instrument_ai = ""
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
            r" Proposition~\ref{thm:instruments} and Supplement Section~\ref{S-app:instruments} "
            r"were added with AI assistance and have not yet been checked by the authors. This includes the passive-price "
            r"extension and its proof in Supplement Section~\ref{S-app:passiveincidence}."
        )
    t = rep(t, old_ai, new_ai + review_ai + instrument_ai)
    t = rep(t, r"to assist with literature cross-checking, numerical verification scripts, Lean~4 formalization coding, and language editing.",
            r"to assist with literature cross-checking, numerical verification scripts, Lean~4 formalization coding, drafting, and language editing.")
    # ---------------------------------------------------------------- appendix
    t = rep(t, r"\begin{proof}[Proof of Theorem~\ref{thm:inv-eq}]",
            IDENT_PROOF + r"\begin{proof}[Proof of Theorem~\ref{thm:inv-eq}]")
    t = rep(t, r"\begin{proof}[Proof of Theorem~\ref{thm:eq-id}]",
            FRAGILITY_PROOF + r"\begin{proof}[Proof of Theorem~\ref{thm:eq-id}]")
    t = rep(t, r"Part~(ii) follows from Online Supplement Theorem~S4.3(i) applied to the closed loop in~(i).",
            r"Part~(ii) follows from Supplement Theorem~\ref{S-thm:minphase}(i) applied to the closed loop in~(i).")
    # Unify Stieltjes transform notation S_M(D) across received Section 4 / Appendix A proofs
    t = rep(t, r"Substituting into $D = 1 - \sum_i \beta_i w_i$ gives $D = 1 - \kappa G(D)$",
            r"Substituting into $D = 1 - \sum_i \beta_i w_i$ gives $D = 1 - \kappa S_M(D)$")
    t = rep(t, r"Setting $w_i = 0$ yields $G \equiv 0$", r"Setting $w_i = 0$ yields $S_M \equiv 0$")
    t = rep(t, r"solely through $G(D) = \int (D - r)^{-1} dM(r)$", r"solely through $S_M(D) = \int (D - r)^{-1} dM(r)$")
    t = rep(t, r"\Phi(\kappa, D; M) = \bigl(D + \kappa G(D) - 1,", r"\Phi(\kappa, D; M) = \bigl(D + \kappa S_M(D) - 1,")
    t = rep(t, r"Linearizing gives $dD = -\kappa_- G(1)$", r"Linearizing gives $dD = -\kappa_- S_M(1)$")
    t = rep(t, r"with $G(1) = \sum_i w_i/(1 - r_i) = \sum_i q_i$.", r"with $S_M(1) = \sum_i w_i/(1 - r_i) = \sum_i q_i$.")
    t = rep(t, r"For~(iii), $G(D) = \sum_i \tilde{w}_i/(D - \bar{a})$ turns $D = 1 - \kappa G(D)$",
            r"For~(iii), $S_M(D) = \sum_i \tilde{w}_i/(D - \bar{a})$ turns $D = 1 - \kappa S_M(D)$")
    t = rep(t, r"\begin{proof}[Proof of Theorem~\ref{thm:forecast-kl}]",
            RECOVERY_PROOF + r"\begin{proof}[Proof of Theorem~\ref{thm:forecast-kl}]")
    t = rep(t, r"\begin{proof}[Proof of Theorems~\ref{thm:minimax} and~\ref{thm:partial-minimax} and Corollary~\ref{cor:halt}]",
            HALT_PROOF + HORIZON_PROOF + INSTRUMENT_PROOF + POSTHALT_PROOF + r"\begin{proof}[Proof of Theorems~\ref{thm:minimax} and~\ref{thm:partial-minimax} and Corollary~\ref{cor:halt}]")
    t = rep(t, r"\begin{proof}[Proof of Lemma~\ref{lem:micro}]",
            TAGS_PROOF + r"\begin{proof}[Proof of Lemma~\ref{lem:micro}]")
    a = t.index(r"\begin{proof}[Proof of Theorems~\ref{thm:minimax} and~\ref{thm:partial-minimax} and Corollary~\ref{cor:halt}]")
    b = t.index(r"\end{proof}", a)
    t = t[:a] + t[a:b].replace(r"\sigma", r"\pi") + t[b:]
    t = rep(t, r"halting label $F$ yields post-halt budget $S - u_{\pi(F)}$, whose worst case over $\pi$ is $S - \min_d u_d$ (attained whenever $\pi(F) \in \arg\min_d u_d$)",
            r"halting label $c$ leaves budget $S - u_{\pi(c)}$, whose worst case over $\pi$ is $S - \min_d u_d$, attained whenever $\pi(c) \in \arg\min_d u_d$")
    t = rep(t, r"Valuing the marginal market-wide impact and inventory-risk externality at $\lambda_{\mathrm{ext}} > 0$ gives",
            r"Valuing a unit of feedback intensity at $\lambda_{\mathrm{ext}} > 0$, the supervisor's valuation of the rise in impact and inventory risk, gives")
    a = t.index(PARADOX_PROOF_START)
    b = t.index(PARADOX_PROOF_END, a) + len(PARADOX_PROOF_END)
    t = t[:a] + PARADOX_PROOF_NEW + t[b:]
    # ---------------------------------------------------------------- referee corrections
    t = rep(t, 'If the loss of an action depends on the population only through the flow map, the set of safe actions is identified by prices.', 'If the observation law identifies the flow map and the loss depends on the population only through that map, the set of safe actions is identified in that experiment.')
    t = rep(t, 'and spacing $\\Delta\\eta > 0$ such that every candidate economy is Schur stable.', 'and small $\\Delta\\eta>0$ with $r_c+\\Delta\\eta[-1,1]\\subset(0,1)$. Fix known $(a,\\kappa)$ with $a+\\kappa W/(1-r_c-\\Delta\\eta)$ bounded below one by a common positive margin over the spacings considered.')
    t = rep(t, 'the same pair has impulse-response gap of order $(\\Delta\\eta)^{2K-1}$, requiring', 'the same pair has impulse-response gap $O((\\Delta\\eta)^{2K-1})$, of that exact order when the lag-$2K$ impulse-response coefficient ("tap") $h_{2K}$ is recorded, requiring')
    t = rep(t, "Prony's method applied to the first $2K$ estimated kernel values recovers the weights from $N = C \\sigma^2 (\\Delta\\eta)^{-(4K-2)}$ reset experiments.", "Prony's method applied to the first $2K$ kernel values reconstructed from impulse responses through $h_{2K}$ attains fixed positive accuracy at fixed confidence with $O(\\sigma^2(\\Delta\\eta)^{-(4K-2)})$ reset experiments, matching the lower bound on parameter families containing the hard pair.")
    t = rep(t, '\\caption{Illustrative years of daily price data below which no test separates the two populations of Theorem~\\ref{thm:cost}(i) with both error probabilities at $5\\%$.}', '\\caption{Illustrative calendar years of daily price data required at $5\\%$ per error, computed from the stationary KL rate of the budget-matched populations.}')
    t = rep(t, 'Composition is only one functional of the merged measure $M$.', 'When independent measurements of kernel lags are available, composition is only one functional of the merged measure $M$.')
    t = rep(t, '$N_{\\mathrm{cert}}(\\epsilon; F_g) = O(\\sigma^2 \\epsilon^{-2})$—independent of the number of groups $K$ and their memory spacing—if and only if', 'Allowing the tap depth $L$ to grow, $N_{\\mathrm{cert}}(\\epsilon;F_g)=O(\\sigma^2\\epsilon^{-2})$ as $\\epsilon\\downarrow0$, uniformly over the measure class, if and only if')
    t = rep(t, 'with $N(0, \\sigma^2)$ noise across $N$ experiments.', 'with independent $N(0,\\sigma^2)$ noise across taps and across $N$ experiments.')
    t = rep(t, 'is pinned, up to the quantile ratio $\\lambda_\\alpha = z_{1-\\alpha/2}/z_{1-\\alpha}$ (approximately $1.19$ at the $95\\%$ level), by the polynomial approximation problem', 'is bounded by the necessary condition $\\omega_L(2z_{1-\\alpha}\\sigma/\\sqrt N)\\le2\\epsilon$ and the sufficient condition $\\omega_L(2z_{1-\\alpha/2}\\sigma/\\sqrt N)\\le2\\epsilon$, where the modulus is')
    t = rep(t, 'Instantiating Proposition~\\ref{prop:decision-suff}, suppose a supervisor must keep', 'For the post-policy calculation, hold dealers, price impact, persistence and the remaining rules fixed. Suppose a supervisor must keep')
    t = rep(t, '\\item[(ii)] A uniform cut to $\\theta = (\\bar{s} - a)/(S - a)$', '\\item[(ii)] Holding dealer capacity and impact parameters $(a, \\kappa)$ fixed, if $S>a$ and $a\\le\\bar{s}\\le S$, a uniform cut to $\\theta = (\\bar{s} - a)/(S - a)$')
    t = rep(t, 'If $\\ell$ is convex and $C$ is convex and invariant to within-group permutations,', 'With the same continuous cost and convex loss in both regimes, suppose $C$ is convex and invariant to within-group permutations. Then')
    t = rep(t, 'we calibrate Theorems~\\ref{thm:cost} and~\\ref{thm:forecast-kl} using', 'we examine the decision problem in Theorems~\\ref{thm:cost} and~\\ref{thm:forecast-kl} using')
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
            "Suppose that in each reset experiment of Theorem~\\ref{thm:cost}, each trader class's order flow is also observed at the first two response dates with independent Gaussian noise. Over any compact, uniformly stable separated family containing the hard pair and an open neighborhood of rescaled nodes and positive weights, recovering weights to a fixed accuracy below half the pair's weight gap requires $O(1)$ tagged experiments independent of $\\Delta\\eta$, whereas recovering memory rates to accuracy $c_0\\Delta\\eta$ (for sufficiently small fixed $c_0>0$) requires order $(\\Delta\\eta)^{-2}$ tagged experiments at fixed confidence.")
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
    t = rep(t, 'A large literature studies heterogeneous fundamentalist and chartist asset-pricing models (Brock and Hommes, 1998; Hommes, 2006) and estimates trader shares from prices (Boswijk et al., 2007; Franke and Westerhoff, 2012; Lux and Zwinkels, 2018);',
            "A large literature studies heterogeneous fundamentalist and chartist asset-pricing models (Brock and Hommes, 1998; Hommes, 2006) and estimates trader shares from prices (Boswijk et al., 2007; Franke and Westerhoff, 2012; Lux and Zwinkels, 2018): whereas Brock and Hommes model fitness-driven predictor switching and Heinrich and Kahn study i.i.d.\\ mixture sampling, we hold rules and masses fixed so composition enters through the moments of a single measure observed via a closed-loop feedback recursion.")
    t = rep(t, 'Budish et al.\\ (2015) advocate market-wide structural remedies (frequent batch auctions),',
            'Budish et al.\\ (2015) analyze continuous-book cancellation and batch auctions, while Colliard and Hoffmann (2017) document volume, liquidity, and composition responses to a transaction tax (complementing our fixed-memory scheduled-holding benchmark in Proposition~\\ref{thm:instruments}),')
    t = rep(t, r"\begin{proof}[Proof of Theorem~\ref{thm:smooth}]",
            COMPOSITION_PROOFS_PART1 + r"\begin{proof}[Proof of Theorem~\ref{thm:smooth}]")
    t = rep(t, 'evaluated at $\\delta = 2 z_{1-\\alpha} \\sigma / \\sqrt{N}$.', 'governed by this common modulus.')
    t = rep(t, 'proves that the same limits—collapse of class-tag value as $\\gamma \\to 0$ and convergence to $V_A$ as $\\gamma \\to \\infty$—hold for arbitrary concave private payoffs, general convex concealment costs, and any Lipschitz social welfare functional $U(e)$, including quadratic',
            'extends the limits to Lipschitz social welfare and private payoffs with slopes bounded above and bounded away from zero, under the stated routing-cost conditions. The cheap-routing collapse requires all labels to be reachable. This covers quadratic')
    t = rep(t, 'If $m \\ge 0$: $\\theta_{\\mathcal{B}} = 1$,',
            'If $m \\ge 0$: one optimum sets $\\theta_{\\mathcal{B}} = 1$,')
    t = rep(t, 'If $m \\ge 0$, $\\varphi$ is nondecreasing, so',
            'If $m \\ge 0$, $\\varphi$ is nondecreasing (with a flat region above $\\hat d$ when $m=0$), so')
    t = rep(t, 'a fitted autoregression of order $L_T = \\lceil c \\log T \\rceil$ attains the oracle risk up to',
            'at each fixed parameter under the conditions of the forecasting result a fitted autoregression of order $L_T = \\lceil c \\log T \\rceil$ attains the oracle risk up to')
    t = rep(t, 'Replication scripts, numerical checks, and Lean~4 formalization files',
            'Empirical protocols, replication scripts, numerical checks, and Lean~4 formalization files')
    t = rep(t, '\\small\\setlength{\\leftmargin}{1.8em}',
            '\\footnotesize\\linespread{0.89}\\selectfont\\setlength{\\leftmargin}{1.3em}')
    t = rep(t, '\\setlength{\\itemsep}{3pt}\\setlength{\\parsep}{0pt}', '\\setlength{\\itemsep}{0pt}\\setlength{\\parsep}{0pt}')
    # ---------------------------------------------------------------- references
    t = add_references(t)
    # ---------------------------------------------------------------- labels shared with the supplement
    for old, new in LABELS.items():
        t = t.replace(r"\label{" + old + "}", r"\label{" + new + "}").replace(r"\ref{" + old + "}", r"\ref{" + new + "}")
    left = re.findall(r"Online Supplement[^.]{0,40}S\d", t)
    assert not left, left
    assert 'p = 6' not in t and 'p=6' not in t and 'equilibrium information' not in t

    # Appendix layout tightening and audit label synchronization
    app_setup = (r'\appendix' + '\n' +
                 r'\small\linespread{0.94}\selectfont' + '\n' +
                 r'\setlength{\parskip}{1.5pt plus 0.5pt minus 0.5pt}' + '\n' +
                 r'\setlength{\abovedisplayskip}{2pt plus 1pt minus 1pt}' + '\n' +
                 r'\setlength{\belowdisplayskip}{2pt plus 1pt minus 1pt}' + '\n' +
                 r'\setlength{\abovedisplayshortskip}{1pt plus 1pt}' + '\n' +
                 r'\setlength{\belowdisplayshortskip}{1pt plus 1pt}' + '\n')
    t = t.replace(r'\appendix' + '\n', app_setup)
    t = t.replace(r'\label{n:ident}', r'\label{n:ident}\label{thm:what-id}')
    t = t.replace(r'\label{n:decisionloss}', r'\label{n:decisionloss}\label{thm:decisionloss}')
    t = t.replace(r'\label{thm:instruments}', r'\label{thm:instruments}\label{prop:instrument_bound}')
    t = t.replace(r'Proof of Theorem~\ref{n:ident}', r'Proof of Theorem~\ref{thm:what-id}')
    t = t.replace(r'\begin{proof}[Proof of Proposition~\ref{thm:instruments}]',
                  r'\begin{proof}[Proof of Proposition~\ref{prop:instrument_bound}]')
    t = t.replace(r' (\mbox{\nolinkurl{PublicationRevision13.lean}}; Supplement Table~\ref{S-tab:newlean})', '')
    t = t.replace(r' (\mbox{\nolinkurl{PublicationRevision14.lean}}; Supplement Table~\ref{S-tab:newlean})', '')
    t = t.replace(' The deterministic steps are checked in Lean~4.', '')
    t = t.replace(r'\section{Proofs of Main Economic Results}\label{app:proofs}',
                  r'\section{Proofs of Main Economic Results}\label{app:proofs}' + '\n\n' +
                  r'\noindent Extended derivations and the exact mapping between deterministic proof steps and Lean~4 formalizations appear in the Online Supplement (Sections~\ref{S-app:proofs} and~\ref{S-app:verification} and Table~\ref{S-tab:newlean}).')
    t = t.replace(' — ', '---').replace('—', '---').replace(' ---or', '---or')

    t, moved = sharpen_1127.main_text(t)
    MOVED.clear()
    MOVED.update(moved)
    return t


LABELS = {
    'thm:sufficiency': 'n:suff', 'thm:what-id': 'n:ident', 'thm:inv-eq': 'n:thm_inventory',
    'thm:eq-id': 'n:thm_eqreduced', 'prop:decision-suff': 'n:interv', 'thm:cost': 'n:cost',
    'thm:cheap': 'n:questions', 'cor:sep': 'n:sep', 'thm:smooth': 'n:univ', 'thm:recovery': 'n:shape',
    'thm:forecast-kl': 'n:dual', 'sec:forecast': 'n:irr_sec', 'prop:interventions': 'n:target',
    'cor:loss': 'n:decisionloss', 'thm:minimax': 'n:minimax', 'cor:halt': 'cor:robustuniform',
    'thm:partial-minimax': 'n:minimaxtags', 'thm:tags': 'n:disc', 'prop:relabeling': 'n:relabel',
    'thm:paradox': 'n:paradox',
    'thm:fragility': 'thm:fragility', 'cor:posthaltflip': 'cor:posthaltflip',
    'prop:endogenous_supervisor': 'prop:endogenous_supervisor', 'thm:mpv': 'thm:mpv',
}

NEW_REFS = [
    r"Huberman, G., Stanzl, W., 2004. Price manipulation and quasi-arbitrage. \emph{Econometrica} 72(4), 1247--1275.",
    r"Subrahmanyam, A., 1994. Circuit breakers and market volatility: A theoretical perspective. \emph{Journal of Finance} 49(1), 237--254.",
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
    r"Berk, K.N., 1974. Consistent autoregressive spectral estimates. \emph{Annals of Statistics} 2(3), 489--502.",
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
