"""21 November 2026, fifth round: Theorem n:paradox (the surveillance paradox: when a group best-responds to a fixed test,
more data leave the supervisor less informed about composition). Applied by build_revision.py after round4.

Revised the same day after two simulated referee reports: the exponent is n = 4 (one group against the closest economy
in which it trades like its neighbour; paradox/exponent_check.py), not the n = 6 of the moment-matched pairs of
Theorem n:cost; the null is composite; the result is a best response, not an equilibrium; the distance is delta and
the detection probability P_d, to free D (dealer root) and pi (labellings)."""

MAIN = r'''\paragraph{Surveillance when algorithms can hide.} The results so far take memories as given. An algorithm that expects to be targeted once identified can trade more like its neighbour, at a cost to its own strategy. The next result gives what the supervisor learns when the algorithm best-responds to a fixed test.

\begin{theorem}[The surveillance paradox]\label{n:paradox}
An untagged group chooses the distance $\delta\in[0,\delta_0]$ between its memory and its neighbour's; the neighbour and all other groups stay where they are. The supervisor tests the null that the group trades like its neighbour (one group in place of the two, with unknown memory and weight) at level $\alpha$ under every economy in the null. Detection triggers an inquiry that costs the group $L$, and moving costs it $k(\delta_0-\delta)^2$, with $\delta_0,k,L>0$. With $N$ observations, let $J$ be the divergence from the record with the group at distance $\delta$ to the closest record in the null. We take its leading order, $J=cN\delta^n$ with $n>2$; for a group and its neighbour, $n=4$. The test is unbiased, and its detection probability depends on $\delta$ only through $J$: it is $P_{\rm d}(J)\ge\alpha$. Let $\delta^*$ be an optimal distance and $J^*=cN\delta^{*n}$.
\begin{enumerate}[label=(\roman*),itemsep=1pt]
\item \emph{Hiding is never complete.} Against every such test, $\delta^*>0$, and $\delta^{*\,n-2}\ge2k^2\delta_0^2/(2^nL^2cN)$ whenever $\delta^*\le\delta_0/3$.
\item \emph{A good test forces crowding.} Suppose the test's power satisfies $P_{\rm d}(J)-\alpha\ge\beta\min\{\sqrt J,\sqrt{\bar J}\}$ and the stakes are high, $L\beta\sqrt{\bar J}>k\delta_0^2$. Then, for every $N$,
\[
\delta^{*\,n-2}\le\frac{4k^2\delta_0^2}{L^2\beta^2cN}.
\]
\item \emph{More data, less information.} Against such a test, for all large $N$, $\delta^*$ is of exact order $N^{-1/(n-2)}$ and the supervisor's information $J^*$ is of exact order $N^{-2/(n-2)}$: like $N^{-1}$ for a group and its neighbour. The detection probability tends to $\alpha$, and the group's distortion cost $k(\delta_0-\delta^*)^2$ tends to $k\delta_0^2$.
\item \emph{Tags reverse it.} With a class tag, detection does not depend on $\delta$, so $\delta^*=\delta_0$, and the supervisor learns the group's rule from its tagged flow (Theorem~\ref{n:disc}).
\end{enumerate}
\end{theorem}

The exponent depends on what the supervisor knows. The record does not say which nearby memory is the neighbour's, so the null is composite. A single group with the pair's total weight and mean memory matches the kernel up to the spread of the two memories, which is of order $\delta^2$ in the kernel and $\delta^4$ in the divergence (Supplement Theorem~\ref{prop:passive}(i); computed from the spectra, the slope is $4.1$, Supplement Section~\ref{app:paradox}). A supervisor that knew the neighbour's memory and both weights would face a simple null with $n=2$; then, against the Gaussian test with high stakes, hiding is complete once $N$ is large, and the record carries no information about the group. In the limiting Gaussian experiment, the one-sided test in the direction orthogonal to the null satisfies (ii) with $\beta=\sqrt2\,\phi(z_\alpha)$ and $\bar J=z_\alpha^2/2$.

Without tags, each new observation is more than offset by the crowding it provokes: doubling the data shrinks the optimal distance by the factor $2^{-1/(n-2)}$, and the information falls. Against a group that best-responds, supervision does not converge to knowledge of composition however long the record. The group pays for its invisibility with a distorted strategy, at a cost approaching $k\delta_0^2$. Whether this is a failure depends on what the supervisor wants. If the conduct at $\delta_0$ is what it fears, the crowding is deterrence; what fails is learning, not necessarily welfare. This is the tension between acting on market information and preserving it \citep{bond2010,bond2015}, here for information about who trades rather than about fundamentals; \citet{frankel2019} study how manipulation muddles a signal. The loss $L$ stands for the inquiry that detection triggers, for example a request to brokers for account records; without such an inquiry, detection would have no consequence (Theorem~\ref{n:minimax}). Supplement Proposition~\ref{prop:hidegame} bounds detection for any power function and lets several groups move at once; Theorem~\ref{n:paradox} gives the rate for one group. The proof is in Supplement Section~\ref{app:paradox}; its deterministic steps are checked in Lean~4 and its rates numerically.

'''

SUPP = r'''\subsection{The surveillance paradox}\label{app:paradox}

\paragraph{Proof of Theorem~\ref{n:paradox}.} (i) First, $\delta^*>0$. The test rejects with probability at most $\alpha$ under the closest economy in the null, and with the group at distance $\delta$ it rejects with a probability that exceeds this by at most the total variation between the two records, which is at most $\sqrt{J/2}$ (Pinsker). So moving from $0$ to a small $\delta$ changes the cost by at most $-2k\delta_0\delta+k\delta^2+L\sqrt{cN\delta^n/2}$, which is negative for small $\delta$ because $n>2$. Next, if $\delta^*\le\delta_0/3$ then $2\delta^*$ is feasible, and optimality against it gives $k(\delta_0-\delta^*)^2+LP_{\rm d}(J^*)\le k(\delta_0-2\delta^*)^2+LP_{\rm d}(cN(2\delta^*)^n)$. With $P_{\rm d}(J^*)\ge\alpha$ and Pinsker, $k[(\delta_0-\delta^*)^2-(\delta_0-2\delta^*)^2]\le L\sqrt{cN(2\delta^*)^n/2}$. The left side is at least $k\delta_0\delta^*$ (\nolinkurl{compare_double}); squaring and dividing by $\delta^{*2}$ gives the bound (\nolinkurl{paradox_lower}).
(ii) At $\delta=0$ the record is in the null, so the detection probability is at most $\alpha$; optimality against $\delta=0$ gives $L(P_{\rm d}(J^*)-\alpha)\le k[\delta_0^2-(\delta_0-\delta^*)^2]$, which is at most $k\delta_0^2$ and at most $2k\delta_0\delta^*$ (\nolinkurl{compare_zero}). If $J^*\ge\bar J$, the power envelope would give $L\beta\sqrt{\bar J}\le k\delta_0^2$, contrary to the stakes condition; so $J^*<\bar J$ and $L\beta\sqrt{cN\delta^{*n}}\le2k\delta_0\delta^*$. Squaring and dividing by $\delta^{*2}$ gives the bound (\nolinkurl{paradox_upper}).
(iii) By (ii), $\delta^*\le\delta_0/3$ once $N\ge4k^2\delta_0^2\,3^{n-2}/(L^2\beta^2c\delta_0^{n-2})$; then (i) applies too, so $\delta^{*\,n-2}$ lies between two constant multiples of $1/N$. Hence $J^*=cN(\delta^{*\,n-2})^{n/(n-2)}$ lies between constant multiples of $N\cdot N^{-n/(n-2)}=N^{-2/(n-2)}$. The detection probability is at most $\alpha+\sqrt{J^*/2}\to\alpha$, and $k(\delta_0-\delta^*)^2\to k\delta_0^2$ because $\delta^*\to0$.
(iv) With a tag, detection does not depend on $\delta$, and $k(\delta_0-\delta)^2$ is minimized at $\delta_0$.
For the limiting Gaussian experiment, let the null be a linear subspace and the alternative lie at distance $t$ from it. The test that rejects when the component of the observation orthogonal to the null exceeds $z_\alpha$ has level $\alpha$ under every null economy and power $\Phi(t-z_\alpha)$, and $J=t^2/2$. As a function of $t=\sqrt{2J}$ the power is convex on $[0,z_\alpha]$, so it lies above its tangent at $0$: $P_{\rm d}(J)-\alpha\ge\phi(z_\alpha)\sqrt{2J}$ for $J\le z_\alpha^2/2$, and it is increasing beyond. $\square$

\paragraph{Checks.} \nolinkurl{PublicationRevision6.lean} checks the deterministic steps (\nolinkurl{compare_zero}, \nolinkurl{compare_double}, \nolinkurl{paradox_upper}, \nolinkurl{paradox_lower}) for every exponent $n\ge2$, with only Lean's standard axioms; Pinsker's inequality, unbiasedness and the power envelope enter as hypotheses. \nolinkurl{paradox/exponent_check.py} computes the divergence rate from the closed-form spectra ($a=0.3$, $\kappa=0.5$, the neighbour at memory $0.5$, both weights $0.05$, $\delta$ from $0.1$ to $0.00625$). The fitted slope of the log rate on $\log\delta$ is $4.1$ against the closest single-group economy, $4.3$ when a third, separated group is present, $2.1$ against the economy in which the group trades exactly like its neighbour, and $8.0$ for a cluster of three that shrinks together. \nolinkurl{paradox/paradox_check.py} solves the group's problem against the Gaussian test for $N$ from $10^2$ to $10^{14}$, with $k=\delta_0=c=1$, $L=50$ and $\alpha=0.05$. The two-sided bounds hold at every $N$; the fitted slopes of $\log J^*$ on $\log N$ are $-1.000$ for $n=4$ and $-0.327$ for $n=8$, against $-1$ and $-1/3$; and the detection probability at $N=10^{14}$ is $0.0500$ for both. With $n=2$ the optimal distance is $0$ at every $N$ from $10^2$ to $10^{12}$.

\paragraph{Scope.} The group takes the supervisor's test and record length as given, and only the group's distance is strategic: the neighbour does not respond, and the supervisor does not choose its test in response to the group. The theorem therefore describes a best response, not an equilibrium of a game between the supervisor and the groups. The divergence $cN\delta^n$ is the leading order, with $c$ depending on the market. Part~(ii) needs a test whose power rises like the square root of the divergence near zero; a weaker test only strengthens the crowding. If several groups crowd together, $n$ is larger (numerically $8$ for a cluster of three), and the information falls more slowly, like $N^{-2/(n-2)}$.

'''

ABSTRACT_OLD = r'Class tags restore targeting only if relabeling is costly; an audit trail linking accounts to owners does not need that.'
ABSTRACT_NEW = (ABSTRACT_OLD + r' Without tags, more surveillance data can leave the supervisor less informed, because '
                r'algorithms that fear targeting crowd together.')

INTRO_OLD = r'and only audit trails that link accounts to owners escape the problem.'
INTRO_NEW = (INTRO_OLD + r' Finally, without tags more data can mean less information: an algorithm that fears '
             r'targeting, facing a fixed test, crowds toward its neighbour fast enough that the supervisor' + "'" + r's '
             r'information about it falls like $N^{-1}$ as its record grows (Theorem~\ref{n:paradox}).')

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
