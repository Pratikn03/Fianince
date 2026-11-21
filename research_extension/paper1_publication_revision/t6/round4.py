"""21 November 2026, fourth round: the general disclosure game (nonlinear values, any convex concealment cost, any
Lipschitz welfare including an aggregate-feedback externality), and a 'What is new' paragraph that separates the
borrowed rate from the paper's own results. Applied by build_revision.py after round3."""

GENERAL = r'''

\paragraph{General primitives.} The limits in Proposition~\ref{prop:relabelK} do not need linear values or quadratic costs. Let class $j$ have share $\chi_j$ and an increasing private payoff $\pi_j$ of its effective retention with slopes in $[\beta_j,B_j]$, $0<\beta_j\le B_j$; let routing a share $z$ through label $k\in E_j$ cost $c_{jk}C(z)$ per unit, with $C$ continuous, $C(0)=0$, $C$ strictly increasing and $C(z)\ge\kappa_Cz^2$ for some $\kappa_C>0$. Let social welfare be $U(e)-\sum_j\chi_j\,\mathrm{cost}_j$ for any function $U$ of the effective retentions $e\in[0,1]^K$ with $|U(e)-U(e')|\le\sum_jL_j|e_j-e'_j|$. This covers a stability externality that depends on aggregate feedback, $U(e)=\sum_j\chi_jb_je_j-\tfrac\lambda2(\sum_j\chi_jw_je_j)^2$, with $L_j=\chi_j(|b_j|+\lambda w_j\sum_i\chi_iw_i)$. Write $m_j(x)=\max_{k\in E_j\cup\{j\}}x_k$, $W_N=\max_{x\in[0,1]}U(x\mathbf 1)$ and $W_A=\max_{e\in[0,1]^K}U(e)$.

\begin{theorem}[The disclosure game with general primitives]\label{thm:relabelgeneral}
\begin{enumerate}[label=(\roman*),itemsep=1pt]
\item $W_N\le W_C(c)\le W_A$ for every cost profile.
\item If $c_{jk}=\epsilon\bar c_{jk}$, then $\big|W_C(c)-\max_xU(m(x))\big|\le\epsilon\,C(1)\sum_j\max_{k\in E_j}\bar c_{jk}\,(L_j/\beta_j+\chi_j)$.
\item With the same scaling, $|W_C(c)-W_A|\le\epsilon^{-1}\kappa_C^{-1}\sum_j(L_jB_j+\chi_jB_j^2)/\min_{k\in E_j}\bar c_{jk}$.
\item If every class can route through every label ($E_j\supseteq\{1,\ldots,K\}\setminus\{j\}$), the coarse value in (ii) is $W_N$: as relabeling becomes cheap, class tags are worth nothing.
\end{enumerate}
\end{theorem}

\paragraph{Proof of Theorem~\ref{thm:relabelgeneral}.} (i) Under a uniform policy no class gains from routing and $C(z)>0$ for $z>0$, so no class routes and welfare is $U(x\mathbf 1)$; hence $W_C\ge W_N$. Costs are nonnegative and $e\in[0,1]^K$, so $W_C\le W_A$. (ii) Fix $x$ and a class $j$; let $D=m_j(x)-x_j$, attained through $k^*$ at cost $c^*=c_{jk^*}$. The chosen channel, with gain $g=zd\le D$ and cost $c\,C(z)$, pays at least what routing everything through $k^*$ would, $\pi_j(x_j+g)-c\,C(z)\ge\pi_j(x_j+D)-c^*C(1)$. With slope at least $\beta_j$ this gives $D-g\le c^*C(1)/\beta_j$ and $c\,C(z)\le c^*C(1)$ (\nolinkurl{general_cheap}). Each effective retention is therefore within $\epsilon\bar c\,C(1)/\beta_j$ of $m_j(x)$ and each cost at most $\epsilon\bar c\,C(1)$; the Lipschitz property of $U$ (\nolinkurl{lipschitz_transfer}) bounds the welfare difference at every $x$, and so the difference of maxima. (iii) The chosen share pays at least the no-routing option, so $c\,C(z)\le\pi_j(x_j+zd)-\pi_j(x_j)\le B_jzd$; with $C(z)\ge\kappa_Cz^2$ this gives $z\le B_j/(c\kappa_C)$ and cost at most $B_j^2/(c\kappa_C)$ (\nolinkurl{general_expensive}). Effective retentions are within $B_j/(c\kappa_C)$ of $x$, and $\max_xU(x)=W_A$. (iv) With every label reachable, $m_j(x)=\max_kx_k$ for every $j$, so $U(m(x))=U(\max_kx_k\mathbf 1)$, whose maximum is $W_N$. $\square$

\paragraph{Checks.} \nolinkurl{PublicationRevision5.lean} checks the three per-class steps. \nolinkurl{t6/general_check.py} checks (ii) and (iii) on random three-class economies with concave payoffs, the concealment cost $z^2/2+z^4$ and the aggregate-feedback externality above, solving each class's best response numerically.'''

MAIN_OLD = (r'The model is stylised: linear values, one cycle, enforced retentions, and a quadratic concealment cost as in '
            r'the costly-state-falsification literature \citep{lackerweinberg1989,crockermorgan1998}.')
MAIN_NEW = (r'The closed forms use linear values and a quadratic concealment cost, as in the costly-state-falsification '
            r'literature \citep{lackerweinberg1989,crockermorgan1998}. The limits do not: with concave private payoffs, '
            r'any convex concealment cost and any Lipschitz welfare of effective retentions, including an externality '
            r'that depends on aggregate feedback, class tags are worth only the value of the coarse partition when '
            r'relabeling is cheap, approach the audit trail' + "'" + r's value when it is expensive, and are worth nothing '
            r'if every class can reach every label (Supplement Theorem~\ref{thm:relabelgeneral}). The model has one '
            r'cycle and enforced retentions.')

NEW_PARA = r'''

\paragraph{What is new, and what is not.} The identification rate $\Delta^{-(4K-2)}$ is the known minimax rate for mixtures with near-colliding components \citep{heinrich2018,wu2020}; we use it and do not claim it. The new results are economic. Sufficiency survives when price impact is an equilibrium outcome. In a feedback market, what a record reveals about two candidate populations equals the forecast loss from confusing them, which is why a uniform cut can be set from prices while a targeted restriction cannot. And the disclosure game has a sharp answer: class tags are worth only what relabeling costs, the share that hides does not depend on that cost, and only audit trails that link accounts to owners escape the problem.'''

INTRO_ANCHOR = r'keeps its value (Proposition~\ref{n:relabel}).'


def _rep(t, old, new):
    assert t.count(old) == 1, (old[:80], t.count(old))
    return t.replace(old, new)


def apply(t):
    t = _rep(t, r'stays within the stated bounds of the coarse and audit values.',
             r'stays within the stated bounds of the coarse and audit values.' + GENERAL)
    t = _rep(t, MAIN_OLD, MAIN_NEW)
    t = _rep(t, INTRO_ANCHOR, INTRO_ANCHOR + NEW_PARA)
    t = _rep(t, r'four Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision4.lean}',
             r'five Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision5.lean}')
    t = _rep(t, r'Supplement Corollaries~\ref{cor:relabelspacing} and~\ref{cor:relabelstatics} were added',
             r'Supplement Corollaries~\ref{cor:relabelspacing} and~\ref{cor:relabelstatics} and Supplement Theorem~\ref{thm:relabelgeneral} were added')
    t = _rep(t, r'(\texttt{gap\_antitone\_gain} and four others) & none beyond the stated model\\',
             r'(\texttt{gap\_antitone\_gain} and four others); general primitives (\texttt{general\_cheap}, \texttt{general\_expensive}, \texttt{lipschitz\_transfer}) & none beyond the stated model\\')
    return t
