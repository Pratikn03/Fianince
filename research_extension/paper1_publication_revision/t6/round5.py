"""21 November 2026, fifth round: Theorem n:paradox (the surveillance paradox: in equilibrium, more data leave the
supervisor less informed about composition). Applied by build_revision.py after round4."""

MAIN = r'''\paragraph{Surveillance when algorithms can hide.} The results so far take memories as given. An algorithm that expects to be targeted once identified can trade more like its neighbour, at a cost to its own strategy. The next result gives the equilibrium identification rate.

\begin{theorem}[The surveillance paradox]\label{n:paradox}
An untagged group chooses the distance $D\in[0,D_0]$ between its memory and its neighbour's. It pays $k(D_0-D)^2$ for moving from its preferred strategy and $L$ if the supervisor's level-$\alpha$ test detects it, with $D_0,k,L>0$. With $N$ observations, the divergence between the records with the group at distance $D$ and with the group trading like its neighbour is $J=cND^n$, where $n=6$ for two groups and $n=4K-2$ for a cluster of $K$ (Theorem~\ref{n:cost}). The test is unbiased, detecting with probability $\pi(J)\ge\alpha$. Let $D^*$ be an optimal distance and $J^*=cND^{*n}$.
\begin{enumerate}[label=(\roman*),itemsep=1pt]
\item \emph{Hiding is never complete.} Against every test, $D^*>0$, and $D^{*\,n-2}\ge2k^2D_0^2/(2^nL^2cN)$ whenever $D^*\le D_0/3$.
\item \emph{A good test forces crowding.} Suppose the test's power satisfies $\pi(J)-\alpha\ge\beta\min\{\sqrt J,\sqrt{\bar J}\}$ and the stakes are high, $L\beta\sqrt{\bar J}>kD_0^2$. Then, for every $N$,
\[
D^{*\,n-2}\le\frac{4k^2D_0^2}{L^2\beta^2cN}.
\]
\item \emph{More data, less information.} Against such a test, for all large $N$, $D^*$ is of exact order $N^{-1/(n-2)}$ and the supervisor's information $J^*$ is of exact order $N^{-2/(n-2)}$. It falls to zero as $N$ grows: like $N^{-1/2}$ for two groups and like $N^{-1/(2K-2)}$ for a cluster of $K$. The detection probability tends to $\alpha$, and the group's distortion cost $k(D_0-D^*)^2$ tends to $kD_0^2$.
\item \emph{Tags reverse it.} With a class tag the group gains nothing from moving, $D^*=D_0$, and the information $cND_0^n$ grows in proportion to $N$.
\end{enumerate}
\end{theorem}

The Neyman--Pearson test in a Gaussian experiment satisfies (ii) with $\beta=\sqrt2\,\phi(z_\alpha)$ and $\bar J=z_\alpha^2/2$. Without tags, each new observation is more than offset by the crowding it provokes: doubling the data shrinks the optimal spacing by the factor $2^{-1/(n-2)}$, and the information falls. Supervision therefore does not converge to knowledge of composition however long the record. The group pays for its invisibility with a distorted strategy, at a cost approaching $kD_0^2$, and that cost is a value of tags that does not depend on whether the supervisor ever acts on what it learns. Supplement Proposition~\ref{prop:hidegame} bounded detection; Theorem~\ref{n:paradox} gives the exact equilibrium rate. The proof is in Supplement Section~\ref{app:paradox}; its deterministic steps are checked in Lean~4 and its rates numerically.

'''

SUPP = r'''\subsection{The surveillance paradox}\label{app:paradox}

\paragraph{Proof of Theorem~\ref{n:paradox}.} (i) First, $D^*>0$: moving from $0$ to a small $D$ changes the cost by at most $-2kD_0D+kD^2+L\sqrt{cND^n/2}$, because the power of any test exceeds its size by at most the total variation, which is at most $\sqrt{J/2}$ (Pinsker); since $n>2$ this is negative for small $D$. Next, if $D^*\le D_0/3$ then $2D^*$ is feasible, and optimality against it gives $k(D_0-D^*)^2+L\pi(J^*)\le k(D_0-2D^*)^2+L\pi(cN(2D^*)^n)$. With $\pi(J^*)\ge\alpha$ and Pinsker, $k[(D_0-D^*)^2-(D_0-2D^*)^2]\le L\sqrt{cN(2D^*)^n/2}$. The left side is at least $kD_0D^*$ (\nolinkurl{compare_double}); squaring and dividing by $D^{*2}$ gives the bound (\nolinkurl{paradox_lower}).
(ii) Optimality against $D=0$, where $J=0$ and the power is $\alpha$, gives $L(\pi(J^*)-\alpha)\le k[D_0^2-(D_0-D^*)^2]$, which is at most $kD_0^2$ and at most $2kD_0D^*$ (\nolinkurl{compare_zero}). If $J^*\ge\bar J$, the power envelope would give $L\beta\sqrt{\bar J}\le kD_0^2$, contrary to the stakes condition; so $J^*<\bar J$ and $L\beta\sqrt{cND^{*n}}\le2kD_0D^*$. Squaring and dividing by $D^{*2}$ gives the bound (\nolinkurl{paradox_upper}).
(iii) By (ii), $D^*\le D_0/3$ once $N\ge4k^2D_0^2\,3^{n-2}/(L^2\beta^2cD_0^{n-2})$; then (i) applies too, so $D^{*\,n-2}$ lies between two constant multiples of $1/N$. Hence $J^*=cN(D^{*\,n-2})^{n/(n-2)}$ lies between constant multiples of $N\cdot N^{-n/(n-2)}=N^{-2/(n-2)}$. The detection probability is at most $\alpha+\sqrt{J^*/2}\to\alpha$, and $k(D_0-D^*)^2\to kD_0^2$ because $D^*\to0$.
(iv) With a tag, detection does not depend on $D$, and $k(D_0-D)^2$ is minimized at $D_0$.
For the Gaussian test, $\pi(J)=\Phi(\sqrt{2J}-z_\alpha)$; as a function of $u=\sqrt{2J}$ it is convex on $[0,z_\alpha]$, so it lies above its tangent at $0$, $\pi(J)-\alpha\ge\phi(z_\alpha)\sqrt{2J}$ for $J\le z_\alpha^2/2$, and it is increasing beyond. $\square$

\paragraph{Checks.} \nolinkurl{PublicationRevision6.lean} checks the deterministic steps (\nolinkurl{compare_zero}, \nolinkurl{compare_double}, \nolinkurl{paradox_upper}, \nolinkurl{paradox_lower}) with only Lean's standard axioms; Pinsker's inequality, unbiasedness and the power envelope enter as hypotheses. \nolinkurl{paradox/paradox_check.py} solves the group's problem against the Gaussian test for $N$ from $10^2$ to $10^{14}$, with $k=D_0=c=1$, $L=50$, $\alpha=0.05$. The two-sided bounds hold at every $N$; the fitted slopes of $\log J^*$ on $\log N$ are $-0.498$ for $n=6$ and $-0.239$ for $n=10$, against $-1/2$ and $-1/4$; and the detection probability at $N=10^{14}$ is $0.0500$ and $0.0501$.

\paragraph{Scope.} The group takes the supervisor's test and record length as given, and only the group's distance is strategic; the neighbour does not respond. The divergence $cND^n$ is the leading order of Theorem~\ref{n:cost}; the constant $c$ depends on the market. Part~(ii) needs a test whose power rises like the square root of the divergence near zero, as the Neyman--Pearson test does in a Gaussian experiment; a weaker test only strengthens the crowding.

'''

ABSTRACT_OLD = r'Class tags restore targeting only if relabeling is costly; an audit trail linking accounts to owners does not need that.'
ABSTRACT_NEW = (ABSTRACT_OLD + r' Without tags, more surveillance data can leave the supervisor less informed, because '
                r'algorithms that fear targeting crowd together.')

INTRO_OLD = r'and only audit trails that link accounts to owners escape the problem.'
INTRO_NEW = (INTRO_OLD + r' Finally, without tags the equilibrium identification rate is negative: algorithms that fear '
             r'targeting crowd together fast enough that the supervisor' + "'" + r's information about composition falls '
             r'like $N^{-1/2}$ as its record grows (Theorem~\ref{n:paradox}).')

LEAN_ROW_ANCHOR = r'Theorem~\ref{n:uniformlog} & omitted coefficients'
LEAN_ROW = (r'Theorem~\ref{n:paradox} & distortion comparisons (\texttt{compare\_zero}, \texttt{compare\_double}); '
            r'two-sided bound on the optimal spacing (\texttt{paradox\_upper}, \texttt{paradox\_lower}) & Pinsker' + "'" +
            r's inequality, unbiasedness and the power envelope (hypotheses)\\' + '\n')


def _rep(t, old, new):
    assert t.count(old) == 1, (old[:80], t.count(old))
    return t.replace(old, new)


def apply(t):
    t = _rep(t, r'\section{Scope and conclusion}\label{n:concl}', MAIN + r'\section{Scope and conclusion}\label{n:concl}')
    t = _rep(t, r'\paragraph{Machine check.} The divergence of a moving window', SUPP + r'\paragraph{Machine check.} The divergence of a moving window')
    t = _rep(t, ABSTRACT_OLD, ABSTRACT_NEW)
    t = _rep(t, INTRO_OLD, INTRO_NEW)
    t = _rep(t, LEAN_ROW_ANCHOR, LEAN_ROW + LEAN_ROW_ANCHOR)
    t = _rep(t, r'five Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision5.lean}',
             r'six Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision6.lean}')
    t = _rep(t, r'Proposition~\ref{n:relabel} to Section~\ref{app:relabel}.', r'Proposition~\ref{n:relabel} to Section~\ref{app:relabel}; Theorem~\ref{n:paradox} to Section~\ref{app:paradox}.')
    t = _rep(t, r'The uniqueness of the pure equilibrium in Supplement Section~\ref{app:nashtight} is certified',
             r'Theorem~\ref{n:paradox} was added on the same day with AI assistance; its deterministic steps are checked in Lean~4 and its rates numerically (\texttt{paradox\_check.py}). The uniqueness of the pure equilibrium in Supplement Section~\ref{app:nashtight} is certified')
    return t
