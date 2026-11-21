"""21 November 2026, second round: many-class relabeling, behaviour-based labels and memory spacing, certified
pure-Nash verification, literature, a shorter abstract, and a shorter main text (secondary results moved to the
supplement). Applied by build_revision.py through apply(t)."""
import re

KCLASS = r'''

\paragraph{Many classes.} Let classes $j=1,\ldots,K$ have shares $\theta_j$, net values $n_j$ and private gains $b_j>0$, and let the supervisor set label retentions $x\in[0,1]^K$. Class $j$ may route a share $z\in[0,1]$ of its activity through one label $k$ in a channel set $E_j$, at resource cost $c_{jk}z^2/2$ per unit of its activity. Write $W_C(c)$ for the best welfare under class tags, $W_N=\max\{0,\sum_j\theta_jn_j\}$ for the uniform cut and $W_A=\sum_j\theta_j\max\{n_j,0\}$ for an audit trail before its cost.

\begin{proposition}[Disclosure with many classes]\label{prop:relabelK}
\begin{enumerate}[label=(\roman*),itemsep=1pt]
\item Class $j$ routes through a label $k\in E_j$ that maximizes $\psi_j(x_k-x_j,c_{jk})$, where $\psi_j(d,c)=\max_{0\le z\le1}(b_jdz-cz^2/2)$, with share $\min\{1,b_j(x_k-x_j)^+/c_{jk}\}$.
\item $W_N\le W_C(c)\le W_A$ for every cost profile.
\item \emph{Cheap channels.} If $c_{jk}=\epsilon\bar c_{jk}$ for $k\in E_j$, then
\[
\Big|W_C(c)-\max_{x\in[0,1]^K}\sum_j\theta_jn_j\max_{k\in E_j\cup\{j\}}x_k\Big|\ \le\ \epsilon\sum_j\theta_j\Big(\frac{|n_j|}{2b_j}+\frac12\Big)\max_{k\in E_j}\bar c_{jk}.
\]
As $\epsilon\to0$, class tags are worth only the value of the coarser problem in which each class receives the best retention among the labels it can reach.
\item \emph{Expensive channels.} With the same scaling, $|W_C(c)-W_A|\le\epsilon^{-1}\sum_j\theta_j(|n_j|b_j+b_j^2)/\min_{k\in E_j}\bar c_{jk}$, so $W_C(c)\to W_A$ as $\epsilon\to\infty$.
\end{enumerate}
\end{proposition}

\begin{corollary}[Behaviour-based labels and memory spacing]\label{cor:relabelspacing}
Suppose labels are assigned from measured memory rates, class $j$ has rate $r_c+\Delta\eta\,s_j$, and shifting the measured rate of a unit of activity into a neighbouring class's band costs $c_0(\Delta\eta)^2(s_k-s_j)^2$ without changing its economic effect. Then Proposition~\ref{prop:relabelK}(iii) applies with $\epsilon=(\Delta\eta)^2$ and $E_j$ the neighbouring classes: the value of behaviour-based class tags is within $O((\Delta\eta)^2)$ of the coarse value. With two classes the coarse value is the uniform cut's, so behaviour-based tags lose their value as the memories approach each other, the same limit in which Theorem~\ref{n:cost} makes composition costly to learn from prices. Owner-linked audit trails are unaffected.
\end{corollary}

\paragraph{Proof of Proposition~\ref{prop:relabelK} and Corollary~\ref{cor:relabelspacing}.} (i) For a given channel the payoff $b_jdz-cz^2/2$ is strictly concave in $z$; its maximizer on $[0,1]$ is $\min\{1,b_jd^+/c\}$, and the class picks the channel with the largest maximum. (ii) The uniform policy $x_j\equiv x$ gives no class a reason to route and attains $x\sum_j\theta_jn_j$, so $W_C\ge W_N$. For any policy, welfare is $\sum_j\theta_j(n_je_j-\text{cost}_j)$ with effective retention $e_j\in[0,1]$ and nonnegative cost, so it is at most $W_A$. (iii) Fix $x$ and a class $j$, let $D=\max_{k\in E_j}(x_k-x_j)^+$, attained at $k^*$, and write $c^*=c_{jk^*}$. The chosen channel, with gap $d\le D$ and share $z$, pays at least what routing everything through $k^*$ would: $b_jdz-c_{jk}z^2/2\ge b_jD-c^*/2$. Since $dz\le D$, this gives $D-c^*/(2b_j)\le dz\le D$ and $c_{jk}z^2/2\le c^*/2$ (\nolinkurl{routing_near_best}). The effective retention $x_j+dz$ is therefore within $c^*/(2b_j)$ of $x_j+D=\max_{k\in E_j\cup\{j\}}x_k$ and the cost is at most $c^*/2$, so welfare at $x$ is within the stated bound of the coarse objective at $x$, uniformly in $x$; the maxima are within the same bound. (iv) The chosen share is at most $b_j/c_{jk}$, so the effective retention is within $b_j/c_{jk}$ of $x_j$; the cost is at most the gross gain $b_jdz\le b_j^2/c_{jk}$ (\nolinkurl{routing_expensive}). Welfare at $x$ is therefore within the stated bound of $\sum_j\theta_jn_jx_j$, whose maximum is $W_A$. For the corollary, substitute $c_{jk}=c_0(\Delta\eta)^2(s_k-s_j)^2$ into (iii); with two classes routing both ways the coarse objective is $(\theta_1n_1+\theta_2n_2)\max\{x_1,x_2\}$, whose maximum is $W_N$. $\square$

\paragraph{Checks.} \nolinkurl{t6/t6_check.py} also verifies (iii) and (iv) on random three-class economies with nearest-neighbour channels: over a grid of policies, the best welfare stays within the stated bounds of the coarse and audit values.'''

SCOPE_OLD = r'If instead classes are defined by measured behaviour, hiding requires changing behaviour, which changes harm as well, and the model would need a joint cost of disguise and harm.'
SCOPE_NEW = r'If classes are defined by measured behaviour and disguise also changes harm, the model needs a joint cost of disguise and harm; Corollary~\ref{cor:relabelspacing} treats the case in which the measured statistic can be shifted without changing harm.'

MAIN_KCLASS_OLD = r'The proof is in Supplement Section~\ref{app:relabel}; its algebra is checked in Lean~4 and its closed forms by brute force.'
MAIN_KCLASS_NEW = r'The proof is in Supplement Section~\ref{app:relabel}; its algebra is checked in Lean~4 and its closed forms by brute force. With many classes the same logic holds channel by channel: as relabeling becomes cheap, class tags are worth only what a coarser partition is worth, in which each class receives the best retention among the labels it can reach (Supplement Proposition~\ref{prop:relabelK}). If labels are assigned from measured memory and shifting it costs the square of the shift, behaviour-based tags lose their value as memories approach each other, the same limit in which Theorem~\ref{n:cost} makes prices uninformative about composition (Supplement Corollary~\ref{cor:relabelspacing}).'

ABSTRACT = r'''\noindent Algorithmic traders read prices and, by trading, move them. We ask what the public record reveals about the population of such traders, and what supervisors need beyond it. When traders respond to a common public signal, the population affects prices, order flows and dealer inventories only through its aggregate feedback response, also in an inventory equilibrium. Learning anything finer is expensive: telling apart $K$ trader types whose rules lie within $\Delta$ of one another needs of order $\Delta^{-(4K-2)}$ observations, an order attained for linear memory rules. With Gaussian news, what a record reveals about two candidate populations equals the cumulative forecast loss from confusing them. A uniform cut in feedback can therefore be set from prices; a targeted restriction cannot. Class tags restore targeting only if relabeling is costly; an audit trail linking accounts to owners does not need that. Core steps are checked in Lean~4.
'''

INTRO_OLD = r'Third, reports that separately measure class flows change the observation experiment. In the exponential-memory model, tagging all but one memory class removes the spacing penalty for recovering class weights. An additional tag can still improve precision.'
INTRO_NEW = INTRO_OLD + r' Fourth, disclosure must survive the traders' + "'" + r' response. When restricted traders can route activity through accounts that carry another label, class tags lose their value as relabeling becomes cheap and the best targeted restriction is partial, while an audit trail that links accounts to owners keeps its value (Proposition~\ref{n:relabel}).'

RESULTS_OLD = r'Section~\ref{n:sup} studies common interventions, targeting, partial disclosure and pooling across markets with shared memory rates. Section~\ref{n:dyn} considers bounded drift, and Section~\ref{n:sat} separates calm observations from observations that reach hard position limits.'
RESULTS_NEW = r'Section~\ref{n:sup} studies common and targeted interventions, the value of disclosure, and the disclosure game when labels can be gamed. The supplement treats partial disclosure, pooling across markets, drift (Supplement Theorems~\ref{thm:partial}, \ref{thm:pool} and~\ref{thm:track}) and hard position limits (Supplement Section~\ref{sec:saturating}).'

LIT = r'''\paragraph{Regulating algorithmic trading.} The policy debate turns on what supervisors can see. \citet{budish2015} trace the high-frequency arms race to the design of continuous limit order books and propose frequent batch auctions, a market-wide remedy. \citet{kirilenko2017} reconstruct the Flash Crash from account-level audit-trail data, classifying traders by their observed behaviour, and \citet{menkveld2016} surveys the economics of high-frequency trading. In the United States, SEC Rule~613 created the Consolidated Audit Trail, which links orders to customers across venues \citep{sec2012cat}. Our results give one reason for that architecture: a market-wide remedy can be calibrated from prices, a class restriction needs class records, and when traders can relabel, those records must be tied to owners (Proposition~\ref{n:relabel}).

'''

BIB = {
    r'\bibitem[Cagan(1956)]': r'''\bibitem[Budish et~al.(2015)]{budish2015} Budish, E., P. Cramton, and J. Shim (2015). The high-frequency trading arms race: Frequent batch auctions as a market design response. \emph{Quarterly Journal of Economics} 130(4), 1547--1621.''',
    r'\bibitem[Kong and Valiant(2017)]': r'''\bibitem[Kirilenko et~al.(2017)]{kirilenko2017} Kirilenko, A., A. S. Kyle, M. Samadi, and T. Tuzun (2017). The Flash Crash: High-frequency trading in an electronic market. \emph{Journal of Finance} 72(3), 967--998.''',
    r'\bibitem[Muth(1960)]': r'''\bibitem[Menkveld(2016)]{menkveld2016} Menkveld, A. J. (2016). The economics of high-frequency trading: Taking stock. \emph{Annual Review of Financial Economics} 8, 1--24.''',
    r'\bibitem[Sussmann(1992)]': r'''\bibitem[Securities and Exchange Commission(2012)]{sec2012cat} Securities and Exchange Commission (2012). Consolidated Audit Trail. Final rule, Release No.~34-67457, 18 July 2012.''',
}

NASH_OLD_START = r'\paragraph{Verification.} For the numerical example of Companion Proposition~\ref{prop:insidergame}'
NASH_OLD_END = r'\subsection{Gaussian-convolved news of arbitrary law}'
NASH_NEW = r'''\paragraph{Certified verification.} For the numerical example of Companion Proposition~\ref{prop:insidergame} ($a=0.3$, $\kappa=0.5$, $r=0.6$, $\theta=1$, $T=10$, $\Sigma=\sigma^2=1$, $W=[-0.515,0.515]$), interval (Arb ball) arithmetic proves three facts. Each is checked by covering $W$, or $W\times W$, with cells and bounding every quantity over a whole cell, so the bounds hold for every point and are not grid evaluations (\nolinkurl{nash/nash_certify.py}, 80-bit precision, 95 seconds):
\begin{enumerate}[label=(\Alph*),itemsep=1pt]
\item $\partial^2U_G/\partial w'^2\,(w',\zeta^*(w))\le-3.17$ for all $w,w'\in W$ ($600\times600$ cells): the group's payoff is strictly concave in its own weight against every schedule the insider plays in equilibrium;
\item $g'(w)\le-7.92$ for all $w\in W$ (4,000 cells);
\item $g(-0.515)=8.5529\pm10^{-5}>0$ and $g(0.515)=-69.145\pm10^{-4}<0$.
\end{enumerate}
These give a unique pure equilibrium without the condition of part (i) on the whole ball $B$. By (B) and (C), $g$ has exactly one zero $w^*$, and it is interior. By (A), $U_G(\cdot,\zeta^*(w^*))$ is strictly concave on $W$, so $g(w^*)=0$ makes $w^*$ the group's best response to $\zeta^*(w^*)$, and $(w^*,\zeta^*(w^*))$ is a pure equilibrium. In any pure equilibrium the insider plays $\zeta^*(w)$; an interior $w$ has $g(w)=0$, so $w=w^*$, and the endpoints are excluded because by (A) and (C) the group's payoff strictly increases into $W$ from $-0.515$ and strictly decreases toward $0.515$. The equilibrium at $w^*\approx0.032$ is therefore the unique pure equilibrium; a floating-point replication gives $w^*=0.0319$ and payoff $0.0165$ (\nolinkurl{nash/nash_float.py}).

'''

# ---- moves from the main text to the supplement ----
NEARCRIT_START = r'\begin{proposition}[The barrier does not lift near instability]\label{n:nearcrit}'
NEARCRIT_END = r'\begin{figure}[t]'
NEARCRIT_NEW = r'''The barrier does not lift near instability. At a common feedback budget $S=1-\epsilon$ the passive information per observation between the pair of Theorem~\ref{n:cost}(i) is at most $C(\Delta\eta)^{4K-2}$, with $C$ independent of $\epsilon$ (Supplement Proposition~\ref{prop:nearcrit} and Figure~\ref{n:fig_barrier}): a market near instability reveals how close it is to instability, not who trades in it.'''

UNIVUP_START = r'The next result gives a conditional upper bound in a different, fixed-history flow experiment.'
UNIVUP_END = '\\Needspace{6\\baselineskip}\n\\begin{theorem}[Recovery within a shrinking cluster'
UNIVUP_MAIN = r'''Supplement Proposition~\ref{n:univup} gives a conditional matching upper bound in a fixed-history flow experiment under a strong-identifiability condition, which smoothness alone does not deliver. The next theorem proves such a bound for linear memory rules.'''

EXC_START = r'\begin{remark}[Drift remains a separate problem]'
EXC_END = r'\section{Who needs composition, and what disclosure buys}'
EXC_MAIN = r'''Class records can still matter for forecasts through private signals, exogenous component flows, unobserved components of the price and stress; Supplement Proposition~\ref{n:exc} states these channels, and Supplement Proposition~\ref{n:learnergap} delimits what fitted-forecast comparisons can establish.

'''

TAIL_START = r'Real regimes tag some traders and leave the rest anonymous. The next result prices that.'
TAIL_END = r'\begin{proposition}[Disclosure when labels can be gamed]'
TAIL_NEW = r'''Three further results are in the supplement. Tagging $m$ of the $K$ groups lowers the exponent of the composition cost by four per tag, and tagging all but one memory class removes the spacing penalty for weight recovery (Supplement Theorem~\ref{thm:partial}). Pooling price records from $D$ markets in which the same algorithms trade in different proportions lowers the exponent to $2(K-1+\lceil K/D\rceil)$ near generic configurations, so cross-market surveillance is a partial substitute for tagging (Supplement Theorem~\ref{thm:pool}). Monitors built on eigenvalues and second moments of prices are not uniformly safe (Supplement Theorem~\ref{thm:blind}).

The results so far take the groups' rules as given. A group that expects to be targeted can change its rule toward a population that is targeted less often: whatever the probes and record length, it is then targeted with probability at most $\alpha+C_0/P$, where $\alpha$ is that population's targeting probability, $C_0$ the cost of the change and $P$ the cost of being targeted (Supplement Proposition~\ref{prop:hiding}). A class tag is attached to the account, so changing the trading rule does not remove it. Activity can, however, be routed through accounts that carry another label. The next result solves the disclosure game when it can.

'''

SECS_START = r'\section{Surveillance over time}\label{n:dyn}'
SECS_END = r'\section{Scope and conclusion}\label{n:concl}'
SECS_NEW = r'''\section{Scope and conclusion}\label{n:concl}

\paragraph{Drift and position limits.} Two extensions are in the supplement. If the population drifts by at most $v$ per period, its weights can be tracked with error of order $\min\{1,(\sigma^2v(\Delta\eta)^{-(4K-2)}/n)^{1/3}\}$ and no better, while market-wide quantities are tracked at the cube-root rate whatever the spacing (Supplement Theorem~\ref{thm:track}); a group that expects to be targeted can crowd its memory toward its neighbour's, which tags tied to accounts prevent (Supplement Proposition~\ref{prop:hidegame}). With hard position limits, populations with the same kernel give identical paths until a limit is reached, while probes that push traders to their limits identify the signed capacity measure (Supplement Theorems~\ref{thm:satsuff}, \ref{thm:stress} and~\ref{thm:satident}). How close traders are to their limits, which decides whether a breach cascades, leaves no trace in calm prices.

'''


def _span(t, start, end, new):
    a = t.index(start)
    b = t.index(end, a)
    assert t.count(start) == 1, start[:60]
    return t[:a] + new + t[b:]


def _cut(t, start, end):
    a = t.index(start)
    b = t.index(end, a)
    return t[:a] + t[b:], t[a:b]


def _rep(t, old, new):
    assert t.count(old) == 1, (old[:80], t.count(old))
    return t.replace(old, new)


def apply(t):
    # many classes and spacing (supplement), and a pointer in the main text
    t = _rep(t, SCOPE_OLD, SCOPE_NEW)
    t = _rep(t, r'are outside the model.', r'are outside the model.' + KCLASS)
    t = _rep(t, MAIN_KCLASS_OLD, MAIN_KCLASS_NEW)
    # certified Nash
    t = _span(t, NASH_OLD_START, NASH_OLD_END, NASH_NEW)
    # abstract, introduction, literature
    t = _span(t, '\\begin{abstract}\n', '\\end{abstract}', '\\begin{abstract}\n' + ABSTRACT)
    t = _rep(t, 'Three results organize the analysis.', 'Four results organize the analysis.')
    t = _rep(t, INTRO_OLD, INTRO_NEW)
    t = _rep(t, RESULTS_OLD, RESULTS_NEW)
    t = _rep(t, r'\paragraph{Contribution relative to existing methods.}', LIT + r'\paragraph{Contribution relative to existing methods.}')
    for anchor, item in BIB.items():
        t = _rep(t, anchor, item + '\n\n' + anchor)
    # moves: n:nearcrit (supplement already states it), n:univup, n:exc, n:learnergap, drift remark, empirical scope
    t = _span(t, NEARCRIT_START, NEARCRIT_END, NEARCRIT_NEW + '\n\n')
    t, univup = _cut(t, UNIVUP_START, UNIVUP_END)
    t = t.replace(UNIVUP_END, UNIVUP_MAIN + '\n\n' + UNIVUP_END, 1)
    t, exc = _cut(t, EXC_START, EXC_END)
    t = t.replace(EXC_END, EXC_MAIN + EXC_END, 1)
    exc = exc.replace(r'Theorem~\ref{n:sat_thm}', r'Theorem~\ref{thm:stress}')
    t = _rep(t, r'\begin{proof}[Proof of Proposition~\ref{n:univup}]',
             r'\paragraph{Moved from the main text.} The proposition below and its discussion were in the main text of earlier versions.' + '\n\n' + univup + '\n' + r'\begin{proof}[Proof of Proposition~\ref{n:univup}]')
    t = _rep(t, r'\begin{proof}[Proof of Proposition~\ref{n:exc}]',
             r'\paragraph{Moved from the main text.} The statements below were in the main text of earlier versions.' + '\n\n' + exc + '\n' + r'\begin{proof}[Proof of Proposition~\ref{n:exc}]')
    # section 7 tail and sections 8-9
    t = _span(t, TAIL_START, TAIL_END, TAIL_NEW)
    t = _span(t, SECS_START, SECS_END, '')
    t = _rep(t, SECS_END + '\n', SECS_NEW)
    t = t.replace(r'and $\nu$ when it saturates as in Section~\ref{n:sat}', r'and $\nu$ when it saturates as in Supplement Section~\ref{sec:saturating}')
    t = _rep(t, r'Class identifiers must correspond to executable accounts, reports have noise and costs, and strategic responses can alter the counterfactual.',
             r'Class identifiers must correspond to executable accounts, reports have noise and costs, and strategic responses can alter the counterfactual. Proposition~\ref{n:relabel} quantifies one such response: class tags are worth only as much as relabeling costs, while owner-linked audit trails are not exposed to it.')
    t = _rep(t, r'Proposition~\ref{n:exc}(b) is that result in this market.', r'Supplement Proposition~\ref{n:exc}(b) is that result in this market.')
    t = _rep(t, r'needs a strong-identifiability condition (Proposition~\ref{n:univup})', r'needs a strong-identifiability condition (Supplement Proposition~\ref{n:univup})')
    t = _rep(t, r'Part~(iii) does not weaken as the market approaches instability (Proposition~\ref{n:nearcrit}).', r'Part~(iii) does not weaken as the market approaches instability (Supplement Proposition~\ref{prop:nearcrit}).')
    t = _rep(t, r'below the speed limit of Section~\ref{n:dyn}', r'below the speed limit of Supplement Theorem~\ref{thm:track}')
    t = _rep(t, r'Proposition~\ref{n:univup} & approximate minimum-distance fitting', r'Prop.~\ref{n:univup} & approximate minimum-distance fitting')
    t = _rep(t, r'\date{Working paper, 20 November 2026}', r'\date{Working paper, 21 November 2026}')
    t = _rep(t, 'Niroula, Niroula and Khatiwada, 20 November 2026', 'Niroula, Niroula and Khatiwada, 21 November 2026')
    # main-to-supplement map
    for clause in [r'Proposition~\ref{n:nearcrit} to Proposition~\ref{prop:nearcrit}; ',
                   r'Proposition~\ref{n:hiding} to Proposition~\ref{prop:hiding}; ',
                   r'Theorem~\ref{n:partial} to Theorem~\ref{thm:partial}; ',
                   r'Theorem~\ref{n:pool} to Theorem~\ref{thm:pool}; ',
                   r'Theorem~\ref{n:track} to Theorem~\ref{thm:track}; ']:
        t = _rep(t, clause, '')
    t = re.sub(r'; Theorem~\\ref\{n:sat_thm\} to Theorems~\\ref\{thm:satsuff\}, \\ref\{thm:stress\} and~\\ref\{thm:satident\}\.',
               r'; Proposition~\\ref{n:relabel} to Section~\\ref{app:relabel}. Propositions~\\ref{n:univup}, \\ref{n:exc} and~\\ref{n:learnergap} are stated in the supplement only.', t, count=1)
    return t
