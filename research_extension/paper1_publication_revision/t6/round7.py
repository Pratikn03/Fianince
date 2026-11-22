"""Seventh round (21 November 2026): full audit of every result against the Lean project.

1. Corollary cor:robustuniform (robust supervision is uniform), main text, checked in PublicationRevision8.lean.
2. New machine checks: n:interv, n:target (i), n:decisionloss, n:sep, prop:hiding (PublicationRevision8.lean) and
   n:learnergap (PublicationRevision9.lean).
3. Credit for modules of the inherited Lean project that check results stated in the paper but were not cited in the
   coverage table (each row checked against the Lean statement; scope differences are stated in the row).
4. The Taiwan evidence paragraph: the registered verdict label of the reverse-causality check and its pre-specified
   descriptive diagnostics, from results/p1t_holdout_A4_printed_output.txt.
Applied by build_revision.py after round5 (and after round6 once the P1M results exist)."""

COR = r'''

\begin{theorem}[Without tags, uniform policies are minimax]\label{n:minimax}
Let class $d$ contribute $H_d$ to the feedback budget, $U=\sum_dH_d$, and let a policy scale the feedback of the class carrying label $c$ by $\theta_c$, at cost $C(\theta)$. The resulting budget is $S'_\sigma=a+\sum_c\theta_cH_{\sigma(c)}$, where $\sigma$ is the unknown assignment of labels to classes, and its loss is $\ell(S'_\sigma)$. If $\ell$ is convex and $C$ is convex and unchanged when labels are permuted, the uniform policy that scales every class by $\bar\theta=K^{-1}\sum_c\theta_c$ has a budget $a+\bar\theta U$ that does not depend on $\sigma$, and
\[
\ell(a+\bar\theta U)+C(\bar\theta\mathbf 1)\ \le\ \frac1{K!}\sum_\sigma\ell(S'_\sigma)+C(\theta)\ \le\ \max_\sigma\ell(S'_\sigma)+C(\theta).
\]
No price record distinguishes labellings (Theorem~\ref{n:suff}), so against the worst labelling consistent with the record, every policy a supervisor can base on prices is weakly dominated by a uniform one.
\end{theorem}

The proof averages over labellings. Every label is carried by every class equally often, so the average budget is $a+\bar\theta U$ and the average relabeled policy is $\bar\theta\mathbf 1$; Jensen's inequality for $\ell$ and for $C$ gives the first inequality, and an average is at most a maximum. The theorem is machine-checked in full (\nolinkurl{PublicationRevision10.lean}). On 14,400 random economies with three convex losses and three costs, the uniform policy is never worse and is strictly better in 86\% of them (\nolinkurl{minimax/minimax_check.py}). Tags break the symmetry the proof uses: with verified labels the supervisor can tailor the policy to each class, and the gain from doing so is the value of tags studied in Theorem~\ref{n:disc} and Proposition~\ref{n:relabel}. A single halt shows the size of the gap.

\begin{corollary}[What a halt guarantees]\label{cor:robustuniform}
In the setting of Theorem~\ref{n:minimax}:
\begin{enumerate}[label=(\roman*),itemsep=1pt]
\item For every label $F$, halting the class labelled $F$ is guaranteed to lower the budget only by $\min_cH_c$, and some labelling consistent with the record attains this.
\item A uniform cut to the fraction $\theta=(\bar s-a)/(S-a)$ brings the budget exactly to the ceiling $\bar s$ in every population with budget $S$, and no policy that meets the ceiling removes less feedback than $S-\bar s$.
\end{enumerate}
So a halt of one class meets the ceiling with certainty only if $\min_cH_c\ge S-\bar s$, while the uniform cut always meets it with the least removal. Without tags, the guarantee of a targeted halt is set by the weakest class, not the one targeted.
\end{corollary}

Tags change the answer group by group.

\begin{theorem}[What tags buy, in minimax terms]\label{n:minimaxtags}
Let verified tags split the classes into groups $g=1,\ldots,G$, so that the record identifies each class's group but cannot rule out relabelings within a group. Let $\ell$ be convex and $C$ convex and unchanged by relabelings within groups. The policy that scales every class of group $g$ by the group's average intensity $\bar\theta_g$ has the budget $a+\sum_g\bar\theta_gU_g$, with $U_g=\sum_{d\in g}H_d$, under every labelling consistent with the record, and it does at least as well as $\theta$ against the worst such labelling. The minimax supervisor therefore chooses one intensity per tagged group, and the value of tags is
\[
V=\min_{\bar\theta}\,\max_\sigma\{\ell(S'_\sigma)+C\}-\min_{(\bar\theta_g)_g}\max_\sigma\{\ell(S'_\sigma)+C\}\ \ge\ 0,
\]
the gain from tailoring intensities across verified groups. With a single group, $V=0$ and Theorem~\ref{n:minimax} is recovered; with every class its own group, $V$ is the full value of targeting.
\end{theorem}

The proof restricts the averaging of Theorem~\ref{n:minimax} to relabelings within groups: within a group, every label is carried by every class of the group equally often, so averaging replaces each intensity by its group mean and the budget by $a+\sum_g\bar\theta_gU_g$. It is machine-checked in full (\nolinkurl{PublicationRevision11.lean}). On 1,200 random economies with random tag partitions, the group-average policy is never worse, and tags have positive value in 27\% of them; in the rest the best group policy is uniform, which includes every economy with a single group (\nolinkurl{minimax/minimax_tags_check.py}). This is the decision-theoretic counterpart of Theorem~\ref{n:disc}: tags are worth what they let a supervisor tailor, and Proposition~\ref{n:relabel} prices how far relabeling erodes that.'''

COR_ANCHOR = r'The proof and a stable two-class example are in Supplement Section~\ref{app:revisiondecision}.'

NEWLEAN_ROWS = (
    r'Prop.~\ref{n:interv} & (ii) and (iii): \texttt{interv\_same}, \texttt{interv\_tv} & the definition of total variation\\' '\n'
    r'Prop.~\ref{n:target}(i) & \texttt{target\_uniform\_iff}, \texttt{target\_uniform\_same} & none\\' '\n'
    r'Cor.~\ref{n:decisionloss} & two-point loss bound, its divergence form, the record length and the tagged loss (\texttt{decision\_loss\_tv}, \texttt{decision\_loss\_kl}, \texttt{decision\_record\_length}, \texttt{decision\_tag\_loss}) & Pinsker' "'" r's inequality and the Gaussian tail (hypotheses)\\' '\n'
    r'Cor.~\ref{n:sep} & the ratio bound and its divergence (\texttt{sep\_ratio}, \texttt{sep\_unbounded}) & the two input bounds (Theorems~\ref{n:cost}(i) and~\ref{n:questions}(ii))\\' '\n'
    r'Theorem~\ref{n:minimax} & the whole theorem: equal label frequencies, the average budget and policy, Jensen for the loss and the cost, worst case (\texttt{perm\_sum\_const}, \texttt{perm\_average\_budget}, \texttt{perm\_average\_policy}, \texttt{minimax\_uniform}, \texttt{uniform\_budget\_label\_free}) & none\\' '\n'
    r'Theorem~\ref{n:minimaxtags} & the whole theorem: consistent relabelings form a group, group sums are invariant, the counting identity, the group-average budget is label-free, Jensen for loss and cost, worst case, $V\ge0$ (\texttt{tag\_count}, \texttt{group\_policy\_budget}, \texttt{tag\_minimax}, \texttt{value\_of\_tags\_nonneg}) & none\\' '\n'
    r'Cor.~\ref{cor:robustuniform} & \texttt{halt\_guarantee}, \texttt{halt\_guarantee\_attained}, \texttt{uniform\_exact}, \texttt{uniform\_minimal\_removal}; relabeling leaves the kernel unchanged (\texttt{relabel\_kernel}) & none\\' '\n'
)
NEWLEAN_ANCHOR = r'Theorem~\ref{n:uniformlog} & omitted coefficients'

HIDING_OLD = r'Proposition~\ref{prop:hiding} & none; it rests on Theorem~\ref{thm:eqinv} & All of it\\'
HIDING_NEW = (r'Proposition~\ref{prop:hiding} & (i) from sufficiency (\texttt{hiding\_sufficiency}); (ii) the cap (\texttt{hiding\_cap}); '
              r'(iii) adoption and its eventual form (\texttt{hiding\_adopt}, \texttt{hiding\_eventually}) '
              r'(\nolinkurl{PublicationRevision8.lean}) & That targeting depends on the record only through its law, which is Theorem~\ref{thm:eqinv}\\')

BUNDLE_OLD = (r'Theorem~\ref{thm:blind}, Propositions~\ref{prop:primitives}, \ref{prop:tied}, \ref{prop:choice}, '
              r'\ref{prop:passive0} and Theorem~\ref{thm:abstain} & none in this table & All of them (proofs in the supplement)\\')
BUNDLE_NEW = r'''Theorem~\ref{thm:blind} & The whole theorem: shared eigenvalues, one-step and unique stationary price variance, unbounded coupling (\texttt{p1\_thm\_blind}, \texttt{p1\_blind\_lyapunov\_unique}, \nolinkurl{Paper1Blind.lean}) & ---\\
Proposition~\ref{prop:primitives} & (i): the Kalman gain is positive, below one, strictly increasing and solves the Riccati equation (\texttt{p1\_kalmanGain\_riccati\_eq}, \texttt{p1\_kalmanGain\_strict\_mono}, \nolinkurl{Paper1Primitives.lean}); (ii) the lower bound in signal-to-noise units for the binomial matched pair (\texttt{p1\_prop\_primitives\_lower\_bound}, \texttt{p1\_kalmanGain\_lipschitz}, \nolinkurl{Paper1KalmanTied.lean}) & The upper bound in (ii) by Prony's method composed with $\eta^{-1}$\\
Proposition~\ref{prop:tied} & (i) mass inversion (\texttt{p1\_intensity\_tied\_mass\_inversion}, \nolinkurl{Paper1Primitives.lean}); (ii) known numbers of desks keep the $\delta^{-4}$ order (\texttt{p1\_prop\_tied\_lower\_bound}, \nolinkurl{Paper1KalmanTied.lean}) & ---\\
Proposition~\ref{prop:passive0} & The midpoint test's error bound for $n\ge4R/(\alpha\Delta^2)$ blocks, for innovations with fourth moment at most $3s_w^4$, which uniform innovations satisfy (\texttt{p1\_thm\_passive0}, \nolinkurl{Paper1PassiveVariance.lean}) & ---\\
Theorem~\ref{thm:abstain} & The abstention bound on $B_T$ and the binary minimax error $1/2$, for path laws of the Gaussian autoregression and measurable outcome sets (\texttt{p1\_thm\_abstain}, \texttt{p1\_thm\_abstain\_binary}, \texttt{p1\_ar\_path\_kl\_le}, \nolinkurl{Paper1Abstain.lean}) & Randomized rules (the checked statement covers deterministic measurable rules)\\
Proposition~\ref{prop:choice} & none & All of it\\'''

CREDIT_ANCHOR = r'Proposition~\ref{prop:delever} & \texttt{p1\_delever\_stress\_invariance}'
CREDIT_ROWS = r'''Theorem~\ref{thm:merged} and Theorem~\ref{n:ident} & (i) for the model: the price response obeys the closed loop with the cohort kernel, deconvolution, identification of the merged measure, its converse and identification from finitely many noise-free observations (\texttt{p1\_impulse\_closed\_loop\_recursion}, \texttt{p1\_thm\_merged\_model\_identification}, \texttt{p1\_thm\_merged\_model\_converse}, \nolinkurl{Paper1MergedModel.lean}; \texttt{p1\_thm\_merged\_deconvolution}, \texttt{p1\_thm\_merged\_measure\_identified}, \nolinkurl{Paper1Identification.lean}; \texttt{p1\_thm\_merged\_model\_finite\_identification}, \nolinkurl{Paper1FiniteIdentification.lean}); the pole count $1+K$ (\nolinkurl{Paper1PoleCount.lean}); (ii) the lower bound $\sigma^2\le2K_*^2P\delta^4T$ for tests with both errors at most $1/4$ (\texttt{p1\_thm\_merged\_separation\_power}, \nolinkurl{Paper1MergedSeparation.lean}) & Minimality of the realization from lowest terms (a standard result of linear systems)\\
Theorem~\ref{thm:minphase}, part (ii) for every $K$ & The spectrum determines the memory rates and the merged measure, with possibly different innovation variances (\nolinkurl{Paper1SpectralID.lean}) & ---\\
Theorem~\ref{thm:kcohort}, further steps & The kernel moment gap $|k_m-k'_m|\le2W\binom mn d^n(c+d)^{m-n}$ (\texttt{p1\_thm\_kcohort\_kernel\_moment\_gap}, \nolinkurl{Paper1MomentGap.lean}); the lower bound from a kernel gap and its $K$-group form (\texttt{p1\_thm\_lower\_bound\_from\_kernel\_gap}, \texttt{p1\_thm\_kcohort\_lower\_bound\_formal}, \nolinkurl{Paper1LowerBound.lean}); every error level (\nolinkurl{Paper1GeneralLevel.lean}) & ---\\
Theorem~\ref{thm:twocohort} & The two-group lower bound on Gaussian records, for an explicit moment-matched pair of the same order (\texttt{p1\_thm\_twocohort\_lower\_bound\_formal}, \nolinkurl{Paper1LowerBound.lean}) & The checked pair differs from the pair \eqref{eq:pair}; the matching upper bound\\
Theorem~\ref{thm:discvalue} (upper bounds) & In reset experiments, all $K$ merged weights from tagged first-period flows with error probability $Kv/(N\kappa^2\varepsilon^2)$, free of the spacing, and each memory rate with error $Le$ (\texttt{p1\_thm\_tagged\_recovery\_all\_classes}, \nolinkurl{Paper1Tagged.lean}; \texttt{p1\_thm\_tagged\_rate\_recovery}, \nolinkurl{Paper1TaggedRates.lean}) & The stationary-record version (Proposition~\ref{prop:tagged})\\
Corollary~\ref{cor:unknown_primitives} & (i) persistence acts as a memory-rate-zero group; (ii) identification of $(\kappa,a,M)$ (\texttt{p1\_cor\_unknown\_primitives\_recursion}, \texttt{p1\_cor\_unknown\_primitives\_identification}, \nolinkurl{Paper1UnknownPrimitives.lean}) & Part (iii), the estimator's rate\\
Theorem~\ref{thm:quantity} & (i): divergence at most $K_*^2V^2\delta^4/(2\sigma^2)$, the worst error and the quantity needed at every error level (\texttt{p1\_thm\_quantity\_kl}, \texttt{p1\_thm\_quantity\_test}, \nolinkurl{Paper1QuantityCapital.lean}; \texttt{p1\_thm\_quantity\_worst\_error}, \texttt{p1\_thm\_quantity\_test\_general}, \nolinkurl{Paper1GeneralLevel.lean}) & Parts (ii)--(iii), the exact error and its attainment\\
Lemma~\ref{lem:toeplitz} & Positivity: for a nonnegative mixture of decaying exponentials the execution cost is at least $\kappa\frac{1-\bar\lambda}{1+\bar\lambda}\frac12\|v\|^2$ and positive for every nonzero probe (\texttt{mixture\_execution\_cost\_identity}, \texttt{mixture\_execution\_cost\_coercive}, \texttt{mixture\_execution\_cost\_positive}, \nolinkurl{ARKernels.lean}) & The ledger identity \eqref{eq:cost} (checked numerically)\\
Theorem~\ref{thm:cap} and Proposition~\ref{prop:disclosure} & The cap as the root of the margin quadratic and the first-pulse margin condition (\texttt{robust\_quantity\_cap\_iff}, \texttt{counterparty\_first\_pulse\_margin\_iff}); the exact equity difference $A^2\kappa^2q\delta^2$ (\texttt{exact\_equity\_disclosure\_separation}) (\nolinkurl{Accounts.lean}) & The reduction of the robust contract to the first pulse; the error statement\\
Lemma~\ref{thm:capital} & Both directions: the divergence bound for solvent probes and the capital needed at every error level (\texttt{p1\_thm\_capital\_kl}, \texttt{p1\_thm\_capital\_test}, \nolinkurl{Paper1QuantityCapital.lean}; \texttt{p1\_thm\_capital\_test\_general}, \nolinkurl{Paper1GeneralLevel.lean}); the pulse's errors and its margin solvency (\texttt{p1\_thm\_capital\_converse\_errors}, \texttt{p1\_thm\_capital\_converse\_margin}, \nolinkurl{Paper1CapitalConverse.lean}) & ---\\
Proposition~\ref{prop:crb}, part (i) & Cram\'er--Rao for every square-integrable locally unbiased statistic of the raw records of the actual closed-loop market, with the true Jacobian (\texttt{p1\_thm\_cramer\_rao\_raw\_actual}, \nolinkurl{Paper1CRRaw.lean}, \nolinkurl{Paper1CRActual.lean}; \texttt{p1\_thm\_gaussian\_cramer\_rao}, \nolinkurl{Paper1GaussianCR.lean}) & ---\\
Proposition~\ref{n:learnergap} & The Hilbert-space core: the risk decomposition, the identity and the bound (\texttt{risk\_decomposition}, \texttt{learner\_gap\_identity}, \texttt{oracle\_gain\_nonneg}, \texttt{oracle\_gain\_bound}, \nolinkurl{PublicationRevision9.lean}) & That conditional expectations are orthogonal projections in $L^2(\cdot\mid D)$\\
'''

INTRO_OLD = r'The inherited project has 1,238 named declarations in 144 modules and builds against a pinned Mathlib.'
INTRO_NEW = (INTRO_OLD + r' Earlier versions of this table did not cite 24 modules of the project that check results '
             r'stated here. Each was compared with the statement it checks, and the rows below now list them with every '
             r'difference of scope. The modules still uncited are supporting lemmas of cited results (Pinsker' + "'" +
             r's inequality for events, the Hammersley--Chapman--Robbins bound, Jackson' + "'" + r's theorem, Prony '
             r'steps) or arithmetic-only steps that are not used to credit any result.')

TAIWAN_OLD = r'The pre-specified reverse-causality check gives $D=-0.0065$ $[-0.0316, 0.0165]$, which does not meet it.'
TAIWAN_NEW = (TAIWAN_OLD + r' Under the registered rule that check is inconclusive rather than contrary: its interval contains '
              r'both zero and the smallest effect of interest, and 68\% of stocks keep a positive gain after the '
              r'adjustment (median $0.012$). By calendar year the primary gain meets the criterion in 2019--2021 and '
              r'not in 2022--2023.')

DECL_OLD = r'Theorem~\ref{n:paradox} was added on the same day with AI assistance;'
DECL_NEW = (r'Theorems~\ref{n:minimax} and~\ref{n:minimaxtags} and Corollary~\ref{cor:robustuniform} were added on the '
            r'same day with AI assistance and are checked in Lean~4 in full. ' + DECL_OLD)


INTRO_ANCHOR = r'as its record grows (Theorem~\ref{n:paradox}).'
INTRO_ADD = (r' Without tags, a uniform policy is also minimax: for any convex loss and any cost that ignores labels, it '
             r'weakly dominates every policy a supervisor can base on prices, against the worst labelling consistent '
             r'with the record (Theorem~\ref{n:minimax}); with partial tags it is uniform within each tagged group, so the '
             r'value of tags is exactly the gain from tailoring across groups (Theorem~\ref{n:minimaxtags}).')


NEW_OLD = r'and only audit trails that link accounts to owners escape the problem. Finally, without tags'
NEW_NEW = (r'and an audit trail that links accounts to owners keeps its value, because we assume that it cannot be '
           r'gamed. Without tags, a uniform policy is minimax over the labellings the record allows, for every convex '
           r'loss, and with partial tags the minimax policy is uniform within each tagged group '
           r'(Theorems~\ref{n:minimax} and~\ref{n:minimaxtags}). Finally, without tags')
ABS_OLD = r'A uniform cut in feedback can therefore be set from prices; a targeted restriction cannot.'
ABS_NEW = (r'A uniform cut in feedback can therefore be set from prices, and without class tags it is the minimax '
           r'policy; a targeted restriction cannot be set from prices.')


# Pratik Niroula, 21 Nov 2026, 15:42 CST, in chat: "okay do it i have read all of it" (after being asked to read the
# results added on 21 November). Recorded as the first author's check; the co-authors' check is not claimed.
NEW_RESULTS_CHECKED_BY_FIRST_AUTHOR = True
CHK_START = (r'Proposition~\ref{n:relabel}, Supplement Proposition~\ref{prop:relabelK} and Supplement Corollaries~'
             r'\ref{cor:relabelspacing} and~\ref{cor:relabelstatics} and Supplement Theorem~\ref{thm:relabelgeneral} were '
             r'added on 21 November 2026 with AI assistance;')
CHK_END = r'its deterministic steps are checked in Lean~4 and its rates numerically (\texttt{paradox\_check.py}).'
CHK_NEW = (r'Proposition~\ref{n:relabel}, Supplement Proposition~\ref{prop:relabelK}, Supplement Corollaries~'
           r'\ref{cor:relabelspacing} and~\ref{cor:relabelstatics}, Supplement Theorem~\ref{thm:relabelgeneral}, '
           r'Theorems~\ref{n:minimax}, \ref{n:minimaxtags} and~\ref{n:paradox} and Corollary~\ref{cor:robustuniform} were '
           r'developed on 21 November 2026 with AI assistance. Their deterministic steps are checked in Lean~4 '
           r'(Theorems~\ref{n:minimax} and~\ref{n:minimaxtags} and Corollary~\ref{cor:robustuniform} in full); their '
           r'closed forms, bounds and rates are also checked by computation (\texttt{t6\_check.py}, '
           r'\texttt{paradox\_check.py}, \texttt{exponent\_check.py}, \texttt{minimax\_check.py}, '
           r'\texttt{minimax\_tags\_check.py}); and their proofs were read and checked by the first author.')


def _rep(t, old, new):
    assert t.count(old) == 1, (old[:90], t.count(old))
    return t.replace(old, new)


import re as _re


def _breakable(s, limit=24):
    """Long identifiers as \\nolinkurl (breaks at underscores) so the narrow table columns do not overflow."""
    return _re.sub(r"\\texttt\{([A-Za-z0-9\\_]+)\}",
                   lambda m: m.group(0) if len(m.group(1).replace("\\_", "_")) <= limit
                   else "\\nolinkurl{" + m.group(1).replace("\\_", "_") + "}", s)


def apply(t):
    global NEWLEAN_ROWS, HIDING_NEW, BUNDLE_NEW, CREDIT_ROWS
    NEWLEAN_ROWS, HIDING_NEW, BUNDLE_NEW, CREDIT_ROWS = (_breakable(x) for x in (NEWLEAN_ROWS, HIDING_NEW, BUNDLE_NEW, CREDIT_ROWS))
    t = _rep(t, COR_ANCHOR, COR_ANCHOR + COR)
    t = _rep(t, NEWLEAN_ANCHOR, NEWLEAN_ROWS + NEWLEAN_ANCHOR)
    t = _rep(t, HIDING_OLD, HIDING_NEW)
    t = _rep(t, BUNDLE_OLD, BUNDLE_NEW)
    t = _rep(t, CREDIT_ANCHOR, CREDIT_ROWS + CREDIT_ANCHOR)
    t = _rep(t, INTRO_OLD, INTRO_NEW)
    t = _rep(t, TAIWAN_OLD, TAIWAN_NEW)
    t = _rep(t, DECL_OLD, DECL_NEW)
    # INTRO_ADD repeated the minimax sentence of the 'What is new' paragraph (both referees); it is no longer added.
    assert t.count(INTRO_ANCHOR) == 1, 'intro anchor'
    if t.count(NEW_OLD) == 1:
        t = t.replace(NEW_OLD, NEW_NEW)
    t = _rep(t, ABS_OLD, ABS_NEW)
    # once the P1M results exist: one clarifying sentence after the fixed template paragraph (no template sentence
    # or number is changed; recorded in P1M_measurement_protocol.md, post-result notes) and one abstract sentence
    tail = (r'the pre-specified sensitivity runs are in Supplement Section~\ref{app:barrier}.')
    if tail in t:
        import json as _json
        import round6 as _r6
        _R = _json.load(open(_r6.RESULTS))['runs']['primary']
        _k, _U, _S = _R['theta']['kappa'], _R['effects']['U'], _R['effects']['S']
        t = _rep(t, tail, tail + (r' Both record lengths compare feedback rules with each class' + "'" + r's non-feedback flow held '
                 r'at its estimated law; with tags, each class' + "'" + r's contribution is estimated directly, with the '
                 r'intervals of Table~\ref{tab:barrier}. The barrier is this large partly because lagged institutional flow '
                 r'moves prices little ($\kappa=' + _r6.sig(_k).strip('$') + r'$): the three classes together contribute '
                 + _r6.sig(_U) + r' to a feedback budget of ' + _r6.sig(_S) + r'.'))
        t = _rep(t, r'Class tags restore targeting only if relabeling is costly;',
                 r'Calibrated to Taiwan' + "'" + r's tagged exchange flows, prices alone pin down the effect of a uniform '
                 r'cut but cannot attribute feedback to the trading classes. Class tags restore targeting only if '
                 r'relabeling is costly;')
    # the estimates table of round6 is a few points too wide at \small (layout only)
    _tb = '\\begin{table}[t]\\centering\\small\n\\caption{Tagged rules in Taiwan'
    if _tb in t:
        t = _rep(t, _tb, '\\begin{table}[t]\\centering\\footnotesize\\setlength{\\tabcolsep}{4pt}\n\\caption{Tagged rules in Taiwan')
    # once the P1M results exist, round6 inserts its supplement subsection inside the surveillance section; it is a
    # section of its own, placed before the machine-check sections (placement only; the text is round6's)
    bar = r'\subsection{The barrier in a real market: protocol and sensitivity}'
    if bar in t:
        a = t.index(bar)
        b = t.index(r'\paragraph{Machine check.} The divergence of a moving window', a)
        block = t[a:b]
        t = t[:a] + t[b:]
        anchor = r'\section{Machine checks in detail}'
        t = _rep(t, anchor, block.replace(r'\subsection{', r'\section{', 1) + anchor)
    if NEW_RESULTS_CHECKED_BY_FIRST_AUTHOR:
        a = t.index(CHK_START)
        b = t.index(CHK_END, a) + len(CHK_END)
        assert b - a < 1500, "declarations span not found as expected"
        t = t[:a] + CHK_NEW + t[b:]
    for old in (r'seven Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision7.lean}',
                r'six Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision6.lean}'):
        if t.count(old) == 1:
            t = t.replace(old, r'eleven Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision11.lean}')
            break
    else:
        raise AssertionError("Lean file count sentence not found")
    return t
