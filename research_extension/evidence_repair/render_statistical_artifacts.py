"""Generate self-contained TeX evidence blocks from corrective results."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from .statistical_repair import summarize_panels, json_safe, write_locked_json

NAMES = {'recurrence_lp': 'Recurrence LP', 'conic_certificate': 'Conic (numerical)',
         'output_error': 'Output-error', 'deconvolution_interval': 'Interval deconvolution',
         'naive_point_fit': 'Constrained point fit'}


def decoded(value):
    if isinstance(value, dict):
        return {k: decoded(v) for k,v in value.items()}
    if isinstance(value, list):
        return [decoded(v) for v in value]
    if isinstance(value, str) and value in ('Infinity', '-Infinity'):
        return float(value)
    return value


def fmt(x, digits=2):
    return '--' if x is None or not np.isfinite(x) else f'{x:.{digits}f}'


def table(label, caption, columns, header, rows, note=''):
    return (r'\begin{table}[htbp]\centering\small'+'\n'+r'\caption{'+caption+'}\n'+
        r'\label{'+label+'}\n'+r'\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}'+columns+r'@{}}'+'\n'+
        r'\toprule'+'\n'+header+r' \\'+'\n'+r'\midrule'+'\n'+
        '\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n'+r'\bottomrule\end{tabular*}'+'\n'+
        (r'\par\smallskip\begin{minipage}{\textwidth}\footnotesize '+note+r'\end{minipage}'+'\n' if note else '')+
        r'\end{table}'+'\n')


def render(data):
    grid, diag, cal = (decoded(data[k]) for k in ('grid','diagnostic','calibration'))
    assert grid['status'] == 'complete', 'grid must be complete'
    assert grid['source_hashes'] == grid['source_hashes_after'], 'source drift'
    recomputed = summarize_panels(grid['panel_records'])
    assert json_safe(recomputed) == json_safe(grid['summary']), 'grid summary drift'
    n = len(grid['panel_records'])
    assert n == grid['metadata']['total_panels']
    assert len(diag['panel_records']) == diag['total_attempted']
    parts = [r'''\subsection{Corrected observable-data experiments}
\label{sec:observable_results}
The following analyses are post-hoc corrective reruns. The earlier comparator
grid used a pre-probe price as its first response coefficient; its method
rankings are withdrawn. The corrected inputs begin with the post-probe price,
$x_1$, and end at $x_{H+1}$. Failed fits and invalid endpoints count in the
attempted-panel denominator rather than being treated as covered intervals.
The earlier files remain in the archive; they are not pooled with these results.
''']
    parts.append(table('tab:method_crosswalk', 'Assumption--implementation--evidence links for the corrected analyses.',
        r'p{.25\textwidth}p{.34\textwidth}p{.32\textwidth}', 'Method & Contract & Corrective artifact', [
        ['Recurrence LP', r'Theorem~\ref{thm:observable_stability}; Gaussian episode regression', r'\texttt{grid/results.json}'],
        ['Conic relaxation', 'Known covariance: chi-square; estimated covariance: F. Numerical certification withheld.', r'\texttt{grid/}, \texttt{sweep\_known/}, \texttt{sweep\_estimated/}'],
        ['Output-error', 'Single-rate local nonlinear fit; profile and sandwich intervals separately recorded', r'\texttt{grid/}, \texttt{diagnostic/}'],
        ['Point/deconvolution', 'Constrained point heuristic or interval propagation', r'\texttt{grid/results.json}'],
        ['Response-region pivot', 'Gaussian errors and independent Wishart covariance where estimated', r'\texttt{calibration/results.json}']],
        r'Paths are relative to \path{statistical_repair_20260926/verified/}. Source hashes, full per-panel observations, failure statuses and the repair protocol accompany these outputs. The separate audited-disclosure results in Section~\ref{sec:audited_inference} are not a matched estimator comparison on this grid.'))
    parts.append(f"\nThe corrected grid contains {n} independent panels within {grid['metadata']['total_cells']} fixed cells. "+r'''The production design crosses $S\in\{.70,.82,1,1.03,1.18\}$,
slow rates $.002,.02,.10$, episode budgets $R=128,1024$, probe sizes $1,4$,
and horizons $H=24,64$, with five panels per cell. The aggregate rates are
descriptive averages over this fixed, heterogeneous design, not universal
performance guarantees or evidence that every cell is adequately powered.
''')
    baseline_covered=sum(p['true_S']>=0 for p in grid['panel_records'])
    rows = [['Always abstain',f'{baseline_covered}/{n}',f'0/{n}',0,'0.00','--',0]]
    widths = [['Always abstain',0,n,0,'--','--']]
    coordinates = [[], []]
    for index,(key,name) in enumerate(NAMES.items(),1):
        item = recomputed[key]
        m = item.get('numerical_candidate_metrics', item['metrics'])
        rows.append([name, f"{m['covered_panels']}/{n}", f"{m['issued_decisions']}/{n}",
            m['wrong_decisions'], fmt(m['unconditional_error_pct']), fmt(m['conditional_error_pct']), item['invalid_intervals']])
        widths.append([name, item['finite_intervals'], item['unbounded_intervals'], item['invalid_intervals'],
            fmt(item['finite_mean_interval_width'],3),fmt(item['finite_p90_interval_width'],3)])
        coordinates[0].append(f"({index},{m['parameter_coverage_pct']:.6f})")
        coordinates[1].append(f"({index},{m['decisiveness_pct']:.6f})")
    parts.append(table('tab:comparator_comparison','Corrective grid: containment and issued labels. All attempted panels are retained.',
        'lrrrrrr',r'Method & Covered/$N$ & Issued/$N$ & Wrong & \shortstack{Wrong/$N$\\(\%)} & \shortstack{Wrong/issued\\(\%)} & Invalid', rows,
        r'Always abstain returns $[0,\infty)$ under the nonnegative model. Conic issued labels here are numerical candidates only: every certified label is withheld. Invalid or missing intervals are not covered. A zero wrong-label count with no issued labels is abstention, not successful discrimination. The point-fit interval has no nominal confidence guarantee.'))
    parts.append(r'''\begin{figure}[htbp]\centering
\begin{tikzpicture}\begin{axis}[
width=.94\textwidth,height=6.4cm,ybar,bar width=11pt,ymin=0,ymax=105,
ylabel={Observed fraction (\%)},xtick={1,2,3,4,5},
xticklabels={Recurrence,Conic candidate,Output-error,Deconvolution,Point fit},
x tick label style={font=\scriptsize},grid=major,
legend style={at={(.5,1.04)},anchor=south,legend columns=2,font=\small}]
\addplot[fill=blue!65,draw=black] coordinates {'''+ ' '.join(coordinates[0])+r'''};
\addlegendentry{Interval contains truth}
\addplot[fill=orange!70,draw=black] coordinates {'''+ ' '.join(coordinates[1])+r'''};
\addlegendentry{Issued label (conic: candidate)}
\end{axis}\end{tikzpicture}
\caption{Empirical containment and labeling on the corrected grid. These are
descriptive panel frequencies, not confidence bounds on performance. Conic
certification remains withheld; a candidate label is not a certified decision.
Audited-disclosure experiments use a different information contract and are
therefore not placed on this plot as a matched comparison.}
\label{fig:comparator_frontier}\end{figure}
''')
    parts.append(table('tab:corrective_widths','Interval availability and finite-width distributions on the corrected grid.',
        'lrrrrr','Method & Finite & Unbounded & Invalid & Finite mean & Finite $p_{90}$',widths,
        'Finite-width summaries condition on the finite count in that row. They are not unconditional mean widths when intervals are unbounded or invalid.'))
    oe = recomputed['output_error']
    cut_limited = sum(any(p['conic_certificate']['diagnostics'].get('termination_'+side)=='max_cuts_reached'
        for side in ('min','max')) for p in grid['panel_records'])
    parts.append(f'\nIn the grid, {cut_limited}/{n} panels have a cut-limit stop at one or both conic endpoints. '+
        'A finite-cut outer candidate is not a converged second-order-cone optimum.\n')
    parts.append(f"\nOutput-error inference is unavailable on {oe['unavailable_inference_panels']}/{n} panels. "+r'''The conic routine records optimizer status, cut counts, residuals and both
objective corrections. Full outward rounding of all assembled constraints is
not established, so \texttt{certified=False} is returned even when a numerical
candidate separates $S$ from one. The exact-arithmetic outer-set theorem is
not a proof that floating-point endpoints have been certified.

\paragraph{Output-error benchmark and interval interpretation.}
The single-rate model fits $\theta=(a,\eta,Q,\kappa)$ by
\begin{equation}
 \min_\theta (\hat\beta-\beta(\theta))^\top W(\hat\beta-\beta(\theta))
       +\lambda(a^2+Q^2),\qquad \lambda=0.
 \label{eq:output_error_obj}
\end{equation}
The constraints are $0\le a\le.995$, $\underline\eta\le\eta\le1$,
$0\le Q\le4$, with $\kappa$ initialized at $\max(.001,\hat\beta_0)$
and bounded between $.1$ and $5$ times that initialization. Thus impact is
estimated, not supplied by the simulator oracle. The covariance inverse uses
the disclosed trace-scaled ridge $10^{-6}\operatorname{tr}(\widehat\Sigma)/(H+1)$.
With response Jacobian $J$, the reported covariance is the local
Gauss--Newton propagation
\[
 B J^\top W\widehat\Sigma WJ B,\qquad B=(J^\top WJ)^{-1}.
\]
This is not a general misspecification-robust variance formula for arbitrary
nonlinear models. Profile intervals use a local objective-increase threshold
and numerical nuisance minimization. The primary interval is the profile
interval when available; sandwich intervals are recorded separately. Neither
is a global profile-set certificate or a finite-sample guarantee. Failed
optimization, rank deficiency or an unavailable profile is retained as such,
without inventing a standard error or counting a fallback as valid inference.
''')
    rows=[]
    for mode in ('known','estimated'):
        r=cal[mode]
        rows.append([mode.title(), r'$\chi^2$' if mode=='known' else '$F$',
            f"{r['covered']}/{cal['trials_per_mode']}",fmt(100*r['empirical_coverage'],3),
            '['+', '.join(fmt(100*x,3) for x in r['exact_99pct_interval'])+']'])
    parts.append(table('tab:response_pivot_calibration','Response-region calibration, separate from structural interval optimization.',
        'llrrr',r'Covariance & Pivot & Covered/draws & Coverage (\%) & \shortstack{Exact 99\%\\interval (\%)}',rows,
        f"Dimension {cal['p']}, episode-budget parameter {cal['R']}; nominal coverage 95\\%. "+
        r'Estimated mode draws an independent Wishart covariance. The fixed acceptance tolerance is one percentage point around nominal. Passing this check does not validate outward numerical constraint assembly.'))
    sweep_rows=[]
    sweep_stops=[]
    plots=[]
    maxima=[]
    for mode in ('known','estimated'):
        s = decoded(data['sweep_'+mode])
        assert s['covariance_mode']==mode
        stopped=sum(any(p['diagnostics'].get('termination_'+side)=='max_cuts_reached'
            for side in ('min','max')) for p in s['panel_records'])
        sweep_stops.append(f"{mode}: {stopped}/{len(s['panel_records'])}")
        for name,series in s['results'].items():
            first,last=series[0],series[-1]
            ps=[p for p in s['panel_records'] if p['model']==name and p['budget_R']==last['budget_R']]
            sweep_rows.append([mode, fmt(last['true_S']),fmt(first['mean_width'],3),fmt(last['mean_width'],3),
                f"{sum(p['is_covered'] for p in ps)}/{len(ps)}",
                f"{sum(p['is_issued'] for p in ps)}/{len(ps)}",sum(p['is_wrong'] for p in ps)])
            maxima.extend(r['mean_width'] for r in series if r['mean_width'] is not None)
        plots.append(s)
    ymax=max(maxima)*1.1 if maxima else 1
    parts.append(r'''\paragraph{Known versus estimated covariance in the budget sweep.}
These experiments draw Gaussian response coefficients directly, not noisy
episode histories. Their covariance is either known exactly or estimated by
an independent Wishart draw. They are useful checks of covariance calibration
and numerical contraction, not evidence about fills, latency or exchange data.
The two modes share coefficient-noise draws; only their covariance treatment
differs. Each production cell has 20 draws and horizon $H=24$.
''')
    parts.append(table('tab:corrective_sweep','Conic numerical endpoints at the first and last budget in each sweep.',
        'llrrrrr',r'Covariance & $S$ & \shortstack{First\\width} & \shortstack{Last\\width} & \shortstack{Last\\covered/$N$} & \shortstack{Last\\candidates/$N$} & Wrong',sweep_rows,
        'Widths are unconditional means only when every interval is finite. Production budgets run from 128 to 32,768. All certified labels are withheld.'))
    parts.append('\nPanels with a cut-limit stop at one or both endpoints are '+
        '; '.join(sweep_stops)+'. These are finite-cut outer approximations; the width curves do not demonstrate convergence to the exact conic optimum.\n')
    figure=[r'\begin{figure}[htbp]\centering']
    for s in plots:
        figure.append(r'\begin{tikzpicture}\begin{axis}[width=.47\textwidth,height=5.8cm,xmode=log,log basis x=2,'+
            'ymin=0,ymax='+fmt(ymax,3)+',title={'+s['covariance_mode'].title()+r' covariance},xlabel={Budget $R$},ylabel={Mean numerical width},'+
            'xtick={'+','.join(map(str,s['budgets']))+r'},x tick label style={font=\tiny},grid=major,legend style={font=\scriptsize}]')
        for (name,series),color,mark in zip(s['results'].items(),('blue','orange!80!black','black'),('square*','diamond*','triangle*')):
            coords=' '.join(f"({r['budget_R']},{r['mean_width']:.7f})" for r in series if r['mean_width'] is not None)
            figure.append(r'\addplot[thick,mark='+mark+','+color+'] coordinates {'+coords+'};'+
                r'\addlegendentry{$S='+fmt(series[0]['true_S'])+'$}')
        figure.append(r'\end{axis}\end{tikzpicture}')
    figure.append(r'''\caption{Descriptive numerical interval widths under the two
covariance contracts, on common vertical scales. Each point averages a fixed
cell, not a confidence interval. Missing means indicate an invalid or unbounded
interval and are not imputed. Contraction is not certification or a universal
asymptotic claim.}\label{fig:conic_contraction}\end{figure}''')
    parts.append('\n'.join(figure))
    diag_rows=[]
    for condition,row in diag['summary'].items():
        diag_rows.append([condition[:2],row['attempted_count'],fmt(row['mean_S_model'],4),fmt(row['mean_bias'],6),
            f"{row['profile_covered_count']}/{row['profile_coverage_denominator']}",
            f"{row['sandwich_covered_count']}/{row['sandwich_coverage_denominator']}",row['unavailable_count']])
    parts.append(r'''\paragraph{Matched and misspecified output-error fits.}
C1/C3 are single deterministic cases, not repeated independent observations.
C2/C4 use independent Gaussian coefficient noise with known covariance, at
the same fixed horizon and noise scale. C1/C2 have one true rate; C3/C4 have
two rates but are fit by the same single-rate estimator. This design isolates
one form of structural mismatch; it does not establish an asymptotic bias
theorem or identify every reason for grid undercoverage. In particular, a
profile-interval result must not be relabeled as sandwich-interval coverage.
''')
    parts.append(table('tab:output_error_diagnostic','Separate profile and sandwich diagnostics; true $S=.82$.',
        'lrrrrrr',r'Case & Attempts & Mean $\hat S$ & Bias & \shortstack{Profile\\covered/valid} & \shortstack{Sandwich\\covered/valid} & Unavailable',diag_rows,
        'Coverage denominators condition on an available interval of the named type; unavailable reports are counted separately. C1/C3 entries are deterministic containment only. The raw records also report optimizer failures, bound hits and interval fallbacks.'))
    parts.append(r'''\paragraph{What the corrected studies establish.}
The response-region probability calculation is a statement under its explicit
Gaussian sampling law. The comparator grid evaluates implemented methods,
including their numerical failures and modeling restrictions. Neither
experiment proves estimator superiority across information contracts, a
universal impossibility theorem, or real-market safety. The original
price-only primary experiment below remains a distinct dataset and is not
combined with this corrective grid.
''')
    return dict(section_tex='\n'.join(parts), funded_tex=render_funded(data['funded']) if 'funded' in data else '',
        denominators=dict(grid_panels=n,
        diagnostic_attempts=diag['total_attempted'],calibration_draws_per_mode=cal['trials_per_mode']),
        grid_summary=json_safe(recomputed))


def render_funded(data):
    names=dict(adaptive='Active memory',frozen='Frozen memory',zero_feedback='Zero feedback',
               unlimited_funding='Inventory limit removed')
    rows=[]
    coords=[]
    for index,(regime,name) in enumerate(names.items(),1):
        s=data['summary'][regime]
        rows.append([name,fmt(s['halt_rate_pct'],1),fmt(s['composite_failure_pct'],1),
            fmt(s['mean_dislocation'],5),fmt(s['mean_min_equity'],2)])
        coords.append(f"({s['mean_dislocation']:.7f},{index})")
    text=table('tab:funded_controls',f"Paired capacity-scenario summaries on {data['n_replicates']} disturbance tapes.",
        'lrrrr',r'Regime & \shortstack{Constraint\\hit (\%)} & \shortstack{Composite\\event (\%)} & \shortstack{Mean\\dislocation} & \shortstack{Min. equity\\(\$)}',rows,
        r'Dislocation is the time-average absolute displacement over 64 steps, in dollars. The hit flag is not a permanent trading ban: subsequent reversing fills remain possible. Removing the inventory limit does not add funding. Means are descriptive; these summaries do not include uncertainty for each arm mean.')
    rows=[]
    for key,label in [('adaptive_minus_frozen','Active minus frozen'),('adaptive_minus_zero_feedback','Active minus zero feedback')]:
        c=data['paired_contrasts'][key]
        rows.append([label,fmt(c['dislocation_diff_mean'],5),
            '['+', '.join(fmt(x,5) for x in c['dislocation_diff_ci_95'])+']'])
    text+=table('tab:funded_paired_contrasts','Paired dislocation contrasts (dollars).',
        'lrr',r'Contrast & Mean difference & Paired bootstrap 95\% interval',rows,
        'Percentile intervals use 1,000 resamples of paired tapes. They describe this fixed simulation, not real-market intervention effects or a universal variance-reduction guarantee.')
    radius=data['dynamics_diagnostics']['adaptive']['spectral_radius']
    text+=r'''\begin{figure}[htbp]\centering
\begin{tikzpicture}\begin{axis}[width=.78\textwidth,height=5.5cm,xbar,
xmin=0,xmax=6.5,ymin=.5,ymax=4.5,ytick={1,2,3,4},
yticklabels={Active memory,Frozen memory,Zero feedback,Inventory limit removed},
xlabel={Time-average absolute dislocation (dollars)},grid=major]
\addplot[fill=blue!55,draw=black,bar width=.4cm] coordinates {'''+ ' '.join(coords)+r'''};
\end{axis}\end{tikzpicture}
\caption{Descriptive regime means, generated from the preserved scenario rules.
Paired-difference uncertainty is reported separately in
Table~\ref{tab:funded_paired_contrasts}. The unconstrained adaptive transition
has spectral radius $'''+fmt(radius,5)+r'''$, so this is not a stable-system
safety counterexample.}\label{fig:paired_mechanism_dislocation}\end{figure}
'''
    return text


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results-dir',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    if args.output_dir.exists():
        parser.error('Refusing existing artifacts directory')
    inputs={name:args.results_dir/name/'results.json' for name in
        ('grid','sweep_known','sweep_estimated','calibration','diagnostic','funded')}
    data={name:json.loads(path.read_text()) for name,path in inputs.items()}
    for name in inputs:
        if name != 'grid':
            receipt=json.loads((args.results_dir/name/'manifest.json').read_text())
            assert receipt['status']=='complete'
            assert receipt['source_hashes']==receipt['source_hashes_after']
            assert receipt['result_sha256']==hashlib.sha256(inputs[name].read_bytes()).hexdigest()
    result=render(data)
    result['input_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs.values()}
    args.output_dir.mkdir(parents=True)
    (args.output_dir/'section.tex').write_text(result['section_tex'])
    (args.output_dir/'funded.tex').write_text(result['funded_tex'])
    write_locked_json(args.output_dir/'paper_artifacts.json',result)
    print(json.dumps({'status':'rendered','output':str(args.output_dir),'denominators':result['denominators']}))


if __name__=='__main__':
    main()
