"""21 November 2026, third round: comparative statics of the disclosure game, Lean coverage of Theorem 6.1 end to end
and of the case analysis, a two-page introduction with a separate related-literature subsection, and the
independent number checks. Applied by build_revision.py after round2."""

STATICS = r'''

\begin{corollary}[Comparative statics]\label{cor:relabelstatics}
At the interior optima of Proposition~\ref{n:relabel}:
\begin{enumerate}[label=(\roman*),itemsep=1pt]
\item when $m\ge0$, the optimal label gap $a\gamma/\{b_H(2a+b_H)\}$ rises with the relabeling cost and falls with the restricted traders' private gain $b_H$;
\item the equilibrium hiding share does not depend on $\gamma$: it is $a/(2a+b_H)$ when $m\ge0$ and $s/\{\theta(2a+b_H)\}$ when $m<0$, and it falls with $b_H$; when $m\ge0$ it rises with the harm $a$;
\item the gain from class tags, $\theta a^2\gamma/\{2b_H(2a+b_H)\}$ when $m\ge0$ and $s^2\gamma/\{2\theta b_H(2a+b_H)\}$ when $m<0$, rises with $\gamma$ and falls with $b_H$; when $m\ge0$ it rises with the harm $a$.
\end{enumerate}
\end{corollary}

\paragraph{Proof of Corollary~\ref{cor:relabelstatics}.} Substitute $g=\gamma/\{b_H(2a+b_H)\}$ in the closed forms of Proposition~\ref{n:relabel}(ii) and in the hiding share $b_Hd/\gamma$ at the optimal gap ($d=ag$ when $m\ge0$, $d=sg/\theta$ when $m<0$); the factor $\gamma$ cancels from the share. The monotonicity statements compare ratios of positive quantities (\nolinkurl{gap_antitone_gain}, \nolinkurl{hiding_share_antitone_gain}, \nolinkurl{hiding_share_monotone_harm}, \nolinkurl{tag_value_antitone_gain}, \nolinkurl{tag_value_monotone_harm}, \nolinkurl{tag_value_mono}). $\square$

The share of the restricted activity that hides is therefore set by the harm and the private gain, not by the cost of hiding: a cheaper channel leads the supervisor to narrow the gap until the same share hides. The more profitable the restricted activity, the milder the optimal restriction and the less class tags are worth.'''

MAIN_STATICS_OLD = r'(Supplement Corollary~\ref{cor:relabelspacing}).'
MAIN_STATICS_NEW = (r'(Supplement Corollary~\ref{cor:relabelspacing}). At the optimum the share of restricted activity '
                    r'that hides does not depend on the cost of hiding, and the more profitable the restricted activity, '
                    r'the milder the optimal restriction and the less class tags are worth (Supplement '
                    r'Corollary~\ref{cor:relabelstatics}).')

MAIN_LEAN_OLD = r'The proof is in Supplement Section~\ref{app:relabel}; its algebra is checked in Lean~4 and its closed forms by brute force.'
MAIN_LEAN_NEW = (r'The proof is in Supplement Section~\ref{app:relabel}. Its steps, including the case analysis and the '
                 r'dominance of complete pooling, are checked in Lean~4, and its closed forms also by brute force.')

CHECKS_OLD = r'The case analysis that assembles them is checked by \nolinkurl{t6/t6_check.py}:'
CHECKS_NEW = (r'\nolinkurl{PublicationRevision4.lean} checks the case analysis: the bound in each of the four cases '
              r'(\nolinkurl{case_mnonneg_inner}, \nolinkurl{case_mnonneg_outer}, \nolinkurl{case_mneg_inner}, '
              r'\nolinkurl{case_mneg_outer}) and the dominance of complete pooling (\nolinkurl{pooling_dominated}). '
              r'The closed forms are also checked by \nolinkurl{t6/t6_check.py}:')

DUAL_OLD = r'This is the Gaussian chain rule and the standard mixture likelihood bound, applied to the market experiment \citep{dawid1984,vovk2001}.'
DUAL_NEW = (DUAL_OLD + r' Given three probability facts that enter as explicit hypotheses (the one-step Gaussian divergence, '
            r'the chain rule over the record and Pinsker' + "'" + r's inequality), the theorem is machine-checked end to end '
            r'(\nolinkurl{dual_end_to_end}, \nolinkurl{excess_forecast_error}, \nolinkurl{mixture_bound}).')

TABLE_DUAL_OLD = r'Bayesian-mixture regret (\texttt{bayes\_mixture\_regret}) & Gaussian KL formula and chain rule; Pinsker' + "'" + r's inequality\\'
TABLE_DUAL_NEW = (r'Bayesian-mixture regret (\texttt{bayes\_mixture\_regret}); the whole theorem assembled from its three '
                  r'probability inputs (\texttt{dual\_end\_to\_end}) & the three inputs: one-step Gaussian KL, chain rule, '
                  r'Pinsker' + "'" + r's inequality\\')
TABLE_RELABEL_OLD = r'& assembly of the cases (checked by brute force)\\'
TABLE_RELABEL_NEW = (r'; the four cases and dominance of pooling (\texttt{case\_*}, \texttt{pooling\_dominated}); comparative '
                     r'statics (\texttt{gap\_antitone\_gain} and four others) & none beyond the stated model\\')

FILES_OLD = r'three Lean~4 files, \nolinkurl{PublicationRevision.lean}, \nolinkurl{PublicationRevision2.lean} and \nolinkurl{PublicationRevision3.lean}'
FILES_NEW = r'four Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision4.lean}'

FORECAST_START = r'\paragraph{A forecasting benchmark.}'
FORECAST_END = r'\paragraph{Results and interpretation.}'
FORECAST_NEW = r'''\paragraph{Forecasting without composition.} Composition is not needed to forecast the public signal: for an unknown fixed population in a stationary Gaussian market, a specified autoregressive predictor has excess forecast risk of order $\log T/T$ (Theorem~\ref{n:irr}), with a uniform cumulative log-loss bound under zero initialization (Theorem~\ref{n:uniformlog}). What a record reveals about which of two populations is trading equals the forecast loss from confusing them (Theorem~\ref{n:dual}), and a matching recovery bound holds within separated shrinking clusters (Theorem~\ref{n:shape}). These results concern the observed pricing-error signal, not traded returns with hidden fundamentals.

'''
RESULTS_START = r'\paragraph{Results and interpretation.}'
RESULTS_END = r'The motivation is consistent with evidence'
RESULTS_NEW = r'''\paragraph{Plan.} Section~\ref{n:model} sets out the model. Section~\ref{n:suff_sec} proves sufficiency and identification, and Section~\ref{n:sec_equilibrium} carries them to an inventory equilibrium. Section~\ref{n:cost_sec} prices composition, Section~\ref{n:irr_sec} separates forecasting from composition, and Section~\ref{n:sup} turns to supervision and disclosure. Section~\ref{n:concl} records the evidence and the limits. Calendar-year conversions are illustrative, not estimates of any venue's identification horizon.

\subsection{Related literature}\label{n:lit}

'''


def _rep(t, old, new):
    assert t.count(old) == 1, (old[:80], t.count(old))
    return t.replace(old, new)


def apply(t):
    t = _rep(t, r'are outside the model.' + '\n\n' + r'\paragraph{Many classes.}',
             r'are outside the model.' + STATICS + '\n\n' + r'\paragraph{Many classes.}')
    t = _rep(t, MAIN_STATICS_OLD, MAIN_STATICS_NEW)
    t = _rep(t, MAIN_LEAN_OLD, MAIN_LEAN_NEW)
    t = _rep(t, CHECKS_OLD, CHECKS_NEW)
    t = _rep(t, DUAL_OLD, DUAL_NEW)
    t = _rep(t, TABLE_DUAL_OLD, TABLE_DUAL_NEW)
    t = _rep(t, TABLE_RELABEL_OLD, TABLE_RELABEL_NEW)
    t = _rep(t, FILES_OLD, FILES_NEW)
    t = _rep(t, r'Supplement Proposition~\ref{prop:relabelK} and Supplement Corollary~\ref{cor:relabelspacing} were added on 21 November 2026 with AI assistance; their algebra is checked in Lean~4 and their closed forms and bounds by computation (\texttt{t6\_check.py}).',
             r'Supplement Proposition~\ref{prop:relabelK} and Supplement Corollaries~\ref{cor:relabelspacing} and~\ref{cor:relabelstatics} were added on 21 November 2026 with AI assistance; their steps, including the case analysis, are checked in Lean~4, and their closed forms and bounds also by computation (\texttt{t6\_check.py}).')
    a, b = t.index(FORECAST_START), t.index(FORECAST_END)
    t = t[:a] + FORECAST_NEW + t[b:]
    a, b = t.index(RESULTS_START), t.index(RESULTS_END)
    t = t[:a] + RESULTS_NEW + t[b:]
    return t
