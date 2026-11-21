"""Journal version of Paper 1 (authors' decision, 21 November 2026: "make it publication close, cut whatever is
needed to keep the best novelty").

Input: the full working paper (paper1_full.tex, everything) and its compiled .aux (for the numbers of results that
move out). Output: the focused version. Nothing is lost: every removed result stays in the full working paper, which
is delivered beside the journal version and cited as niroula2026full, with the result's number there.

What changes
  Main text
    - The forecasting benchmarks (Theorems n:irr, n:uniformlog) move to the supplement; the section keeps Theorem
      n:dual and is renamed "What a record reveals".
    - Paragraphs that listed extensions now live in the full working paper are rewritten to cite it.
  Supplement: removed (to the full working paper)
    pooling markets; saturating traders, stress and any-population sufficiency; execution cost and capital; the
    global two-point bound for two groups; the cost-and-error decision model; tracking and the observer effect; one
    running market, news of any law and money; the pooling Jacobian, the insider-game Nash certificate and
    convolved news; general memory, the uniform rate, Cramer-Rao and finite-window bounds; economic primitives, the
    worked example and spectral blindness; fragility, the strategic insider and their proofs; the moved-from-main
    propositions on noisy flow recovery, record channels and fitted-forecast gains.
  Every remaining reference to a removed result becomes a citation of the full working paper with its number there.
"""
import re

FULL_KEY = 'niroula2026full'
BIB_ANCHOR = r'\bibitem[Batenkov et~al.(2021)]{batenkov2021}'
BIB = (r'\bibitem[Niroula et~al.(2026d)]{niroula2026full} Niroula, P., P. Niroula, and S. Khatiwada (2026d). '
       r'Observationally equivalent algorithms: Full working paper with all supplementary results. Working paper, '
       r'21 November 2026, \url{https://github.com/Pratikn03/Fianince}.' + '\n\n')

# (start marker, end marker[, anchor after which to search]); text from start up to (not including) end is removed
SUPP_CUTS = [
    (r'\subsection{Pooling markets}', r'\subsection{Traders who respond to being watched}'),
    (r'\section{Beyond the kernel: saturating traders and stress}', r'\section{Scope and limits}'),
    (r'\section{Execution cost and capital}', r'\section{The supervisory decision in detail}'),
    (r'\paragraph{A complete conditional cost-and-error model.}', r'\subsection{The targeted halt for every $K$}'),
    (r'\subsection{Stress identification with noisy observations}', r'\section{Which questions prices answer cheaply}'),
    (r'\subsection{Tracking a moving population}', r'\subsection{A surveillance and hiding game}'),
    (r'\section{One running market, news of any law, and the value of tags in money}', r'\section{The hard pair: moment gap'),
    (r'\subsection{The pooling moment map: Jacobian and global immersion}', r'\section{Do the rates survive real market noise?}'),
    (r'\section{What prices hide, in economic terms}', r'\section{Pricing, evasion and the choice of an audit trail}'),
    (r'\paragraph{Moved from the main text.}', r'\paragraph{Numerical evidence and formal scope.}',
     r'\section{Smooth-family lower bounds and forecast comparisons}'),
    # equilibrium: keep sufficiency, the inventory equilibrium, disclosure in equilibrium, rents and the halt
    (r'\begin{theorem}[Fragility: where liquidity disappears]', r'\paragraph{A misjudged dealer and a targeted halt.}',
     r'\section{Equilibrium: further results and proofs}'),
    (r'\paragraph{Numerical illustration.}', r'\paragraph{Proof of Theorem~\ref{thm:rents}',
     r'\section{Equilibrium: further results and proofs}'),
    (r'\paragraph{Proof of Theorem~\ref{thm:fragility}', r'\paragraph{Proof of Corollary~\ref{cor:eqdisclosure}',
     r'\section{Equilibrium: further results and proofs}'),
    (r'\paragraph{Proof of Theorem~\ref{thm:insider}', r'\paragraph{Numerical solution of Theorem~\ref{thm:inventory}',
     r'\section{Equilibrium: further results and proofs}'),
]

# ---- the forecasting benchmarks move from the main text to the supplement ----
MOVE_START = r'The error curve $\Phi(-\sqrt{\Lambda}/2)$'
MOVE_END = r'\section{Who needs composition, and what disclosure buys}'
MOVE_DROP_TAIL = r'Class records can still matter for forecasts through'
MAIN_REPLACEMENT = r'''\paragraph{Forecasting without composition.} Composition is not needed to forecast the pricing error either. With known parameters, the price record and the class records give the same optimal forecast; for a fixed unknown population, a fitted autoregression of order $\log T$ attains the known-population forecast up to excess risk of order $\sigma^2\log T/T$, and a Bayesian autoregression has a cumulative log-loss bound that is uniform over stable populations (Supplement Theorems~\ref{n:irr} and~\ref{n:uniformlog}). What a supervisor cannot get from prices is therefore not a better forecast but the attribution that a targeted policy needs.

'''
SUPP_MOVE_ANCHOR = r'\section{Detection, local-cluster recovery, and uniform log-loss}\label{app:incoming}'
SUPP_INTRO_OLD = (r'This section incorporates the incoming SSRN additions with explicit observation and initialization '
                  r'conditions. The statements are proved on paper. The revision formal file checks selected supporting '
                  r'algebra, rather than the full statistical or inverse-map results.')
SUPP_INTRO_NEW = (r'This section states the forecasting benchmarks summarized in Section~\ref{n:irr_sec} and proves them, '
                  r'together with Theorems~\ref{n:dual} and~\ref{n:shape}. The probabilistic steps are proved on paper; '
                  r'Table~\ref{tab:newlean} lists the machine-checked steps.' + '\n\n'
                  r'\subsection{Forecasting the pricing error without composition}\label{app:forecastbench}' + '\n\n')

MAIN_EDITS = [
    (r'\section{Forecasting the public signal without recovering composition}\label{n:irr_sec}',
     r'\section{What a record reveals}\label{n:irr_sec}'),
    (r'''\paragraph{Forecasting without composition.} Composition is not needed to forecast the public signal: for an unknown fixed population in a stationary Gaussian market, a specified autoregressive predictor has excess forecast risk of order $\log T/T$ (Theorem~\ref{n:irr}), with a uniform cumulative log-loss bound under zero initialization (Theorem~\ref{n:uniformlog}). What a record reveals about which of two populations is trading equals the forecast loss from confusing them (Theorem~\ref{n:dual}), and a matching recovery bound holds within separated shrinking clusters (Theorem~\ref{n:shape}).''',
     r'''\paragraph{What a record reveals.} What a record reveals about which of two populations is trading equals the forecast loss from confusing them (Theorem~\ref{n:dual}), and a matching recovery bound holds within separated shrinking clusters (Theorem~\ref{n:shape}). Composition is not needed to forecast the public signal itself (Supplement Theorems~\ref{n:irr} and~\ref{n:uniformlog}).'''),
    (r'Section~\ref{n:irr_sec} separates forecasting from composition',
     r'Section~\ref{n:irr_sec} equates what a record reveals with forecast loss'),
    (r'''\paragraph{Four extensions.} \emph{Without resets.} A supervisor that trades random signs into a market running from an unknown state, and correlates prices with its own trades, estimates the response with error of order $T^{-1/2}$ whatever the law of the news; Prony's method then recovers the weights from order $(\Delta\eta)^{-(4K-2)}$ periods, and no method needs fewer (Supplement Theorem~\ref{thm:running}). \emph{Without separation.} If groups may nearly coincide or be tiny, individual weights cannot be recovered uniformly, but the merged memory distribution can, at the same order $N^{-1/(4K-2)}$ in Wasserstein distance (Supplement Theorem~\ref{thm:uniformw1}). \emph{General memory.} If memory is any mixture of exponentials, finite or infinite, composition is harder still: the best attainable accuracy for the memory distribution improves only like $1/\log(N/\sigma^2)$, and this order is attained, so halving the error squares the data needed (Supplement Theorem~\ref{thm:general}; both bounds are machine-checked, with larger constants). \emph{Money.} Probing a market is trading in it: to tell one group from two with memories $\pm\delta$ apart, the quantity traded must grow like $\delta^{-2}$ and the capital at risk like $\delta^{-4}$ (Supplement Theorem~\ref{thm:quantity} and Section~\ref{app:capital}). Priced this way, the cost of learning composition from prices is a lower bound on the money value of class tags to a supervisor who needs composition (Supplement Corollary~\ref{cor:money}).''',
     r'''\paragraph{Extensions.} The full working paper \citep{niroula2026full} carries the cost further. A supervisor that trades random signs into a market running from an unknown state needs the same order of data, whatever the law of the news. If groups may nearly coincide or be tiny, the merged memory distribution is still recovered at the order $N^{-1/(4K-2)}$ in Wasserstein distance. If memory is any mixture of exponentials, accuracy improves only like $1/\log(N/\sigma^2)$, so halving the error squares the data needed. And probing is trading: telling one group from two with memories $\pm\delta$ apart takes a traded quantity of order $\delta^{-2}$ and capital of order $\delta^{-4}$, a lower bound on the money value of class tags.'''),
    (r'''\paragraph{Drift and position limits.} Two extensions are in the supplement. If the population drifts by at most $v$ per period, its weights can be tracked with error of order $\min\{1,(\sigma^2v(\Delta\eta)^{-(4K-2)}/n)^{1/3}\}$ and no better, while market-wide quantities are tracked at the cube-root rate whatever the spacing (Supplement Theorem~\ref{thm:track}); a group that expects to be targeted can crowd its memory toward its neighbour's, which tags tied to accounts prevent (Supplement Proposition~\ref{prop:hidegame}). With hard position limits, populations with the same kernel give identical paths until a limit is reached, while probes that push traders to their limits identify the signed capacity measure (Supplement Theorems~\ref{thm:satsuff}, \ref{thm:stress} and~\ref{thm:satident}).''',
     r'''\paragraph{Drift and position limits.} A group that expects to be targeted can crowd its memory toward its neighbour's, which tags tied to accounts prevent (Supplement Proposition~\ref{prop:hidegame} and Theorem~\ref{n:paradox}). The full working paper \citep{niroula2026full} adds two extensions. If the population drifts by at most $v$ per period, its weights can be tracked with error of order $\min\{1,(\sigma^2v(\Delta\eta)^{-(4K-2)}/n)^{1/3}\}$ and no better, while market-wide quantities are tracked at the cube-root rate whatever the spacing. With hard position limits, populations with the same kernel give identical paths until a limit is reached, while probes that push traders to their limits identify the signed capacity measure.'''),
    (r'''The uniqueness of the pure equilibrium in Supplement Section~\ref{app:nashtight} is certified by interval arithmetic (\texttt{nash\_certify.py}). ''', ''),
    (r'''This section supplies the corrected proofs of Theorem~\ref{n:univ}, Proposition~\ref{n:univup}, Theorem~\ref{n:irr} and Proposition~\ref{n:exc}.''',
     r'''This section supplies the corrected proof of Theorem~\ref{n:univ} and lists the machine-checked steps of the results new in this revision.'''),
]

MAIN_EDITS += [
    (r'Propositions~\ref{n:univup}, \ref{n:exc} and~\ref{n:learnergap} are stated in the supplement only.', ''),
    (r'\citep{lutkepohl1987,hendry2011}; Supplement Proposition~\ref{n:exc}(b) is that result in this market.',
     r'\citep{lutkepohl1987,hendry2011}; the full working paper \citep{niroula2026full} states that result in this market.'),
    (r'\paragraph{Numerical checks of Theorems~\ref{thm:eqreduced} and~\ref{thm:fragility}.}',
     r'\paragraph{Numerical checks of Theorem~\ref{thm:eqreduced}.}'),
    (r'Four results in Supplement~\ref{app:eqinv} extend this section.',
     r'Four results extend this section; the first two are in the full working paper \citep{niroula2026full}, the last two in Supplement Section~\ref{app:eqinv}.'),
    (r"""Theorem~\ref{thm:track}, Propositions~\ref{prop:observer}, \ref{prop:hidegame} & Divergence of a moving window, Le Cam's two-point step, the bias--noise trade-off (\texttt{p1\_track\_kl\_window}, \texttt{p1\_track\_two\_point}, \texttt{p1\_track\_tradeoff}); the observer-effect inequality (\texttt{p1\_observer\_floor}); parts (ii) and (iii) of the game (\texttt{p1\_hiding\_detection\_bound}, \texttt{p1\_hiding\_tag\_no\_crowding}) (\nolinkurl{Paper1TrackingGame.lean}) & Analyticity and Lipschitz properties of the family $R_c$; the closed-loop and Prony steps, as in Theorems~\ref{thm:kcohort} and~\ref{prop:esprit}; part (i) of the game\\""",
     r"""Proposition~\ref{prop:hidegame} & Parts (ii) and (iii) of the game (\texttt{p1\_hiding\_detection\_bound}, \texttt{p1\_hiding\_tag\_no\_crowding}, \nolinkurl{Paper1TrackingGame.lean}); part (iv), group by group (\texttt{p1\_hiding\_nash\_bound}, \nolinkurl{Paper1NewsLawHiding.lean}) & Part (i) of the game\\"""),
    (r"""Proposition~\ref{prop:nongauss}, Corollary~\ref{cor:money}, Proposition~\ref{prop:hidegame}(iv) & Laplace bound, comparison of divergences, money bound composed with the lower bound of Theorem~\ref{thm:kcohort}, group-by-group equilibrium bound (\texttt{p1\_laplace\_vs\_gaussian}, \texttt{p1\_newslaw\_kl\_compare}, \texttt{p1\_tags\_value\_money}, \texttt{p1\_hiding\_nash\_bound}, \nolinkurl{Paper1NewsLawHiding.lean}) & Chain-rule identity, Laplace divergence formula, Proposition~\ref{prop:nongauss}(i) and (iii)\\""",
     ''),
    (r"""\paragraph{Machine check.} The divergence of a moving window, Le Cam's two-point step, the bias--noise trade-off, the observer-effect inequality and parts (ii)--(iv) of Proposition~\ref{prop:hidegame} are machine-checked (\texttt{p1\_track\_kl\_window}, \texttt{p1\_track\_two\_point}, \texttt{p1\_track\_tradeoff}, \texttt{p1\_observer\_floor}, \texttt{p1\_hiding\_detection\_bound}, \texttt{p1\_hiding\_tag\_no\_crowding}, \nolinkurl{Paper1TrackingGame.lean}; \texttt{p1\_hiding\_nash\_bound}, \nolinkurl{Paper1NewsLawHiding.lean}).""",
     r"""\paragraph{Machine check.} Parts (ii)--(iv) of Proposition~\ref{prop:hidegame} are machine-checked (\texttt{p1\_hiding\_detection\_bound}, \texttt{p1\_hiding\_tag\_no\_crowding}, \nolinkurl{Paper1TrackingGame.lean}; \texttt{p1\_hiding\_nash\_bound}, \nolinkurl{Paper1NewsLawHiding.lean})."""),
    (r"""This section gives three results: a speed limit on tracking a moving population, a floor on what probing can learn about traders who learn from prices, and an equilibrium in which surveillance without tags pushes algorithms together and never detects them.""",
     r"""This section gives an equilibrium in which surveillance without tags pushes algorithms together and never detects them, and the equilibrium identification rate. A speed limit on tracking a moving population and a floor on what probing can learn about traders who learn from prices are in the full working paper \citep{niroula2026full}."""),
    (r'\section{The hard pair: moment gap, largest weights, Jacobian and extensions}\label{app:openres}',
     r'\section{The hard pair: moment gap and largest weights}\label{app:openres}'),
    (r"""This section gives the exact size of the moment gap behind the constants of Theorem~\ref{thm:kcohort}, compares the largest weights of the hard pair, proves global immersion of the pooling moment map, existence and uniqueness of pure Nash equilibrium, and the extension of passive lower bounds to Gaussian-convolved news.""",
     r"""This section gives the exact size of the moment gap behind the constants of Theorem~\ref{thm:kcohort} and compares the largest weights of the hard pair."""),
]


def _cut(t, start, end, after=None):
    base = t.index(after) if after else t.index('Online Supplement')
    a = t.index(start, base)
    b = t.index(end, a + len(start))
    return t[:a] + t[b:], t[a:b]


def _rep(t, old, new):
    assert t.count(old) == 1, (old[:90], t.count(old))
    return t.replace(old, new)


def aux_numbers(aux_text):
    return {lab: num for lab, num in re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', aux_text)}


_KIND = r'(Theorems?|Propositions?|Corollar(?:y|ies)|Lemmas?|Sections?|Figures?|Tables?|Remarks?|Appendix|equation)'


def _singular(k):
    return {'Theorems': 'Theorem', 'Propositions': 'Proposition', 'Corollaries': 'Corollary', 'Lemmas': 'Lemma',
            'Sections': 'Section', 'Figures': 'Figure', 'Tables': 'Table', 'Remarks': 'Remark'}.get(k, k)


def _inside_parens(t, pos):
    start = max(t.rfind('\n\n', 0, pos), 0)
    seg = t[start:pos]
    return seg.count('(') > seg.count(')')


def cite_removed(t, removed, nums):
    """Every '[Supplement ]Kind~\\ref{lab}' with lab removed becomes a citation of the full working paper."""
    report = []
    pat = re.compile(r'(Supplement |Companion )?' + _KIND + r'~\\(ref|eqref)\{([^}]+)\}')

    def sub(m):
        pre, kind, cmd, lab = m.group(1), m.group(2), m.group(3), m.group(4)
        if lab not in removed or pre == 'Companion ':
            return m.group(0)
        num = nums.get(lab, '?')
        k = _singular(kind)
        loc = f'({num})' if cmd == 'eqref' or k == 'equation' else f'{k}~{num}'
        if k == 'equation':
            loc = f'eq.~({num})'
        macro = r'\citealp' if _inside_parens(t, m.start()) else r'\citet'
        report.append((lab, m.group(0)))
        return f'{macro}[{loc}]{{{FULL_KEY}}}'
    t = pat.sub(sub, t)
    # bare \ref / \eqref left over (lists such as "Theorems~\ref{a} and~\ref{b}")
    def bare(m):
        lab = m.group(2)
        if lab not in removed:
            return m.group(0)
        report.append((lab, m.group(0)))
        num = nums.get(lab, '?')
        return (f'({num})' if m.group(1) == 'eqref' else num) + f' of \\citet{{{FULL_KEY}}}'
    t = re.sub(r'\\(ref|eqref)\{([^}]+)\}', bare, t)
    t = re.sub(r'\\(citet|citealp)\[([^\]]*)\]\{' + FULL_KEY + r'\}(\([ivx]+\))', r'\\\1[\2\3]{' + FULL_KEY + '}', t)
    return t, report


def drop_table_rows(t, table_start, table_end, removed):
    """Delete table rows whose first cell refers only to removed results."""
    a = t.index(table_start)
    b = t.index(table_end, a)
    body = t[a:b]
    rows = body.split('\\\\\n')
    kept, dropped = [], 0
    for r in rows:
        first = r.split('&')[0]
        labs = re.findall(r'\\ref\{([^}]+)\}', first)
        if labs and all(l in removed for l in labs) and '&' in r:
            dropped += 1
            continue
        kept.append(r)
    return t[:a] + '\\\\\n'.join(kept) + t[b:], dropped


def apply(full_tex, full_aux):
    t = full_tex
    nums = aux_numbers(full_aux)
    removed_text = []
    for c in SUPP_CUTS:
        t, cut = _cut(t, *c)
        removed_text.append(cut)
    # move the forecasting benchmarks
    a = t.index(MOVE_START)
    b = t.index(MOVE_END, a)
    moved = t[a:b]
    tail = moved.find(MOVE_DROP_TAIL)
    if tail >= 0:
        removed_text.append(moved[tail:])
        moved = moved[:tail]
    t = t[:a] + MAIN_REPLACEMENT + t[b:]
    t = _rep(t, SUPP_INTRO_OLD, SUPP_INTRO_NEW + moved.rstrip() + '\n\n' + r'\subsection{Proofs}' + '\n')
    for old, new in MAIN_EDITS:
        t = _rep(t, old, new)
    removed = set()
    for r in removed_text:
        removed |= set(re.findall(r'\\label\{([^}]+)\}', r))
    removed -= set(re.findall(r'\\label\{([^}]+)\}', t))
    # coverage tables: rows for removed results go with them
    t, d1 = drop_table_rows(t, r'\section{Machine-checked declarations}', r'\end{longtable}', removed)
    t, d2 = drop_table_rows(t, r'\begin{table}[ht]\centering\small' + '\n' + r'\begin{tabular}{>{\raggedright\arraybackslash}p{0.15\textwidth}',
                            r'\end{tabular}', removed)
    t, report = cite_removed(t, removed, nums)
    t = _rep(t, BIB_ANCHOR, BIB + BIB_ANCHOR)
    left = [m.group(1) for m in re.finditer(r'\\(?:ref|eqref)\{([^}]+)\}', t) if m.group(1) in removed]
    assert not left, left
    return t, {'removed_labels': sorted(removed), 'citations_added': report, 'rows_dropped': d1 + d2,
               'chars_removed': sum(len(r) for r in removed_text)}
