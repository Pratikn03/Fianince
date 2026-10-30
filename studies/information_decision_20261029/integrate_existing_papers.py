"""Revise existing manuscripts and integrate only the checked returned run.

No notebook regeneration: the running, pinned experiment remains unchanged.
Historical theorem statements, proofs, tables and archived results are preserved.
"""
from pathlib import Path
import argparse,collections,hashlib,io,json,re,shutil,zipfile
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BEGIN='% BEGIN INFORMATION DECISION REVISION 20261029'
END='% END INFORMATION DECISION REVISION 20261029'


def replace_block(s,block):
    s=re.sub(re.escape(BEGIN)+'.*?'+re.escape(END)+'\n*','',s,flags=re.S)
    return s.replace('\\end{document}',BEGIN+'\n'+block+'\n'+END+'\n\n\\end{document}')


def insert_in_existing_blank(s,marker,paragraph):
    # Preserve the physical line count used by the existing guarded thesis
    # extractor. This replaces a blank line; all previous text stays intact.
    anchor='\n\n'+marker
    if paragraph in s:return s
    if anchor not in s:raise ValueError('missing insertion anchor '+marker)
    return s.replace(anchor,'\n'+paragraph+'\n'+marker,1)


def checks(archive):
    with zipfile.ZipFile(archive) as z:
        if sum(x.file_size for x in z.infolist())>50_000_000:raise ValueError('unexpected archive size')
        names=z.namelist()
        if len(names)!=len(set(names)):raise ValueError('duplicate archive paths')
        if any(Path(n).is_absolute() or '..' in Path(n).parts for n in names):raise ValueError('unsafe archive path')
        manifest=json.loads(z.read('manifest.json'))
        for name,digest in manifest.items():
            if hashlib.sha256(z.read(name)).hexdigest()!=digest:raise ValueError('hash mismatch '+name)
        sources={}
        for name in ['model.py','experiments.py','market.py','run.py','verify_lean.py','test_package.py','formal/DecisionCore.lean','formal/host_path_compat.c']:
            digest=hashlib.sha256(z.read('source_snapshot/'+name)).hexdigest()
            if digest!=hashlib.sha256((HERE/name).read_bytes()).hexdigest():raise ValueError('source mismatch '+name)
            sources[name]=digest
        status=json.loads(z.read('run_status.json'));config=json.loads(z.read('configuration.json'))
        if status['status']!='COMPLETED_EXPLORATORY' or status['tests_returncode']!=0:raise ValueError('incomplete experiment')
        if config['profile']!='full' or config['seed']!=20261029:raise ValueError('unexpected profile')
        receipt=json.loads(z.read('formal/lean_receipt.json'))
        if receipt['status']!='PASS_PARTIAL_LOGICAL_CORE':raise ValueError('Lean check not passed')
        dest=HERE/'results/returned_20261029T225100';dest.mkdir(parents=True,exist_ok=True)
        selected=['configuration.json','run_status.json','scientific_status.json','environment.json','tests.log',
                  'formal/lean_receipt.json','formal/lean_stdout.log','account_results.csv',
                  'information_decisions.csv','paired_contrasts.csv','paired_intervals.csv',
                  'identification_witness.csv','policy_summary.csv','growth_capacity.png']
        for name in selected:
            target=dest/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(name))
        verification=dict(archive_sha256=hashlib.sha256(Path(archive).read_bytes()).hexdigest(),
          manifest_verified=len(manifest),matched_core_sources=sources,
          interpretation='author-returned seeded reproduction; not independent scientific validation',
          market_data_run=False,general_separation_theorem_proved=False)
        (dest/'verification.json').write_text(json.dumps(verification,indent=2))
    return dest


def main():
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);args=p.parse_args();dest=checks(args.archive)
    a=pd.read_csv(dest/'account_results.csv');d=pd.read_csv(dest/'information_decisions.csv')
    c=pd.read_csv(dest/'paired_intervals.csv')
    sel=(a.N==32)&(a.budget==1)&a.guarantee_applicable
    metrics=a[sel].groupby(['regime','policy']).mean(numeric_only=True)
    info=d[(d.N==32)&(d.budget==1)].groupby('regime').mean(numeric_only=True)
    labels={'no_feedback':'No feedback','moderate_feedback':'Moderate feedback','near_boundary':'Near boundary'}
    common=r'''
\subsection*{What this revision adds}
The information question is distinct from choosing a preferred amount of risk.
For a specified financial decision, the relevant issue is which observations
support an exposure constraint, what remains unidentified, and whether obtaining
additional information changes the attainable decision after costs. This does
not introduce portfolio choice or control without full identification as new
ideas. The general identification-versus-decision-value result still requires
independent proof and a comparison with the closest existing results.

\subsection*{Time conventions and the institution}
The new application is a price-taking, unlevered own-account investor, not a
venue-wide supervisor. It begins with cash, buys once, holds a fixed position
for 60 one-minute model periods, and closes fully. Round-trip linear and
quadratic charges enter cash and wealth. The account cannot change the market's
feedback, and the experiment does not measure customer liquidity or welfare.
This is separate from the paper's dealer/venue admission contracts.

\begin{center}\small
\begin{tabular}{p{0.26\textwidth}p{0.65\textwidth}}
\toprule
Quantity & Interpretation\\
\midrule
Sampling interval & One minute in the new synthetic account; other historical studies retain their stated sampling clocks.\\
Historical lookback & Often six hours in the existing forecasting studies; not a holding period.\\
Forecast horizon & Often the next hour's adverse excursion; not an executed round-trip trade.\\
New holding period & Exactly 60 model minutes, with explicit entry and exit charges.\\
Other theory horizons & The existing finite-horizon theorems retain their declared $H$; no universal holding period is imposed.\\
\bottomrule
\end{tabular}
\end{center}

\subsection*{Information and decision design}
The new comparison uses controlled independent reset observations of 12 impulse
taps, a known plant and reading variance, and a declared finite candidate class.
It does not treat public market trading as a reset experiment. Common training
and validation paths supply 768 and 384 additional reset episodes per repetition;
512 further paths evaluate the selected actions. These are in addition to the
reported tap-reading budget, not evidence of learning from 32 observations in
total. Verified disclosure restricts
the minimum-memory rate to an audited band. The oracle knows the true response,
not future shocks. All certificate arms use the same training objective.

The account selects a position by empirical expected logarithmic terminal
wealth, subject to its information-supported exposure restriction. This is a
finite-horizon application of logarithmic utility, not a newly proved Kelly
growth-optimality theorem. Equal response bounds alone do not imply equal
expected returns or identical utility-optimal portfolios.

The new account has initial wealth of 1,000 dollars and an initial price of
100 dollars; its position grid runs from zero to 9.9 units. Its round-trip
dollar charge is $c(I)=0.002I+0.0002I^2$. For bounded external flow, the
constraint adds this charge to position times the largest admissible absolute
price response over the holding horizon. The resulting bound concerns loss
from initial wealth at each date. It is not peak-to-trough drawdown, protection
against arbitrary unbounded shocks, or a rolling deployment guarantee.

\subsection*{Returned execution and proof scope}
The returned full-mode archive uses seed 20261029. All 35 manifest entries and
eight core source files were checked. The run contains 20 independent
repetitions per regime, not 16,800 independent experiments: the 16,800 policy
rows reuse tapes across policies, budgets and observation counts. Twelve
targeted checks passed. Eight conditional decision-logic lemmas compiled with
Lean 4.19.0 and their axiom printouts report no axioms. This is a seeded
execution reproduction. It neither completes the older manuscript's Lean
coverage nor formalizes the Gaussian confidence argument, market dynamics,
general minimax separation, portfolio optimality or welfare.

The displayed slice uses 32 reset episodes and a one-dollar loss budget from
initial wealth of 1,000 dollars. It is an illustrative presentation of an
exploratory grid, not a primary selected before the results were seen. All
regimes, budgets, policies and negative outcomes remain in the result archive.
The inputs and complete outputs are retained with the verification record in
the new information-decision study directory.
'''
    info_table=r'''
\subsection*{Aggregate information and unresolved cohorts: returned simulation}
\begin{center}\small
\begin{tabular}{lrrr}
\toprule
Regime & Unique candidate (\%) & Certified units & Oracle units\\
\midrule
'''
    for regime,label in labels.items():
        row=info.loc[regime]
        info_table+=f"{label} & {100*row.cohort_identified:.1f} & {row.certified_capacity:.3f} & {row.oracle_capacity:.3f}\\\\\n"
    info_table+=r'''\bottomrule
\end{tabular}
\end{center}
Here ``unique'' means one remaining candidate in the declared finite class,
not identification of arbitrary real-world algorithms. In the moderate and
near-boundary configurations, the aggregate certificate reaches the oracle's
grid capacity in this slice even though the candidate decomposition is usually
unresolved. This is an illustrative decision comparison; it does not prove a
uniform rate separation for continuous classes.
'''
    pols=[('aggregate_certificate','Aggregate certificate'),('disclosure_certificate','Unpaid disclosure'),
          ('paid_disclosure_certificate','Paid disclosure'),('oracle_response','Oracle response'),
          ('volatility_persistence','Volatility and persistence'),('point_response','Point response'),
          ('log_utility','Expected-log objective'),('fractional_log_validation','Fractional log, validation'),
          ('empirical_loss_constrained_log','Empirical loss constraint'),('robust_empirical_log','Robust empirical log')]
    result_table=r'''
\subsection*{Financial decisions: returned simulation}
{\footnotesize\setlength{\tabcolsep}{4pt}\renewcommand{\arraystretch}{0.9}
\begin{longtable}{p{0.36\textwidth}rrrr}
\toprule
Policy & Units & Log growth (bp) & ES95 (\$) & Breach (\%)\\
\midrule
\endfirsthead
\toprule
Policy & Units & Log growth (bp) & ES95 (\$) & Breach (\%)\\
\midrule
\endhead
'''
    for regime,label in labels.items():
        result_table+=r'\multicolumn{5}{l}{\textit{'+label+r'}}\\'+'\n'
        for pol,title in pols:
            row=metrics.loc[(regime,pol)]
            result_table+=f"{title} & {row.inventory:.3f} & {1e4*row.mean_log_wealth:.3f} & {row.loss_es95:.3f} & {100*row.budget_breach_rate:.3f}\\\\\n"
        result_table+=r'\midrule'+'\n'
    result_table+=r'''\bottomrule
\end{longtable}}
Values average 20 repetitions. Log growth is $10^4$ times the mean logarithm
of terminal wealth divided by initial wealth; ES95 is the mean of each
repetition's worst five percent of initial-wealth losses. It is not a return
forecast or a peak-to-trough drawdown guarantee. Position sizes differ across
policies; the table reports a risk--growth tradeoff rather than equal-exposure
dominance. A zero observed breach is not proof of zero breach probability.
'''
    cost_table=r'''
\subsection*{Disclosure cost and the negative result}
\begin{center}\small
\begin{tabular}{lrrr}
\toprule
Paid minus aggregate & Mean (bp) & Lower (bp) & Upper (bp)\\
\midrule
'''
    for regime,label in labels.items():
        row=c[(c.regime==regime)&(c.N==32)&(c.budget==1)&(c.contrast=='paid_disclosure_certificate minus aggregate')&(c.metric=='paired_mean_log_difference')].iloc[0]
        cost_table+=f"{label} & {1e4*row['mean']:.3f} & {1e4*row.ci_low:.3f} & {1e4*row.ci_high:.3f}\\\\\n"
    cost_table+=r'''\bottomrule
\end{tabular}
\end{center}
The intervals are exploratory percentile bootstraps over repetition-level
paired means, not simultaneous intervals across the grid. In this slice the
unpaid disclosure does not expand capacity, while the assumed one-cent charge
reduces net log wealth. This run therefore does not establish a positive net
economic value of disclosure. The price is hypothetical, not a calibrated
reporting cost. Stronger disclosure need not be worth purchasing when aggregate
information already supports the relevant decision.
'''
    failure_table=r'''
\subsection*{Assumption failures and calibration diagnostics}
The table reports finite-sample frequencies for all seven regimes, combining
the three reading budgets. Each band outcome is counted once per repetition
and reading budget (60 outcomes per regime); repeating the same outcome across
four financial loss budgets would not create further observations. The three
reading budgets within a repetition are not an independent replication.
\begin{center}\small
\begin{tabular}{lcrr}
\toprule
Regime & Contract valid & Tap-band hit (\%) & Empty set (\%)\\
\midrule
'''
    failure_labels={**labels,'hidden_slow_memory':'Hidden slow memory',
      'correlated_readings':'Correlated readings','biased_readings':'Biased readings',
      'behavior_change':'Behaviour change'}
    bands=d.drop_duplicates(['regime','rep','N']).groupby('regime').mean(numeric_only=True)
    for regime,label in failure_labels.items():
        row=bands.loc[regime]
        valid='Yes' if row.guarantee_applicable else 'No'
        failure_table+=f"{label} & {valid} & {100*row.true_response_in_band:.1f} & {100*row.empty_set:.1f}\\\\\n"
    failure_table+=r'''\bottomrule
\end{tabular}
\end{center}
The nominal one-decision band coverage is 95 percent under the valid contract;
these small, dependent-budget frequencies are diagnostics, not a new coverage
theorem. A tap-band hit concerns the observed response, not membership in the
finite candidate class or stability of future behaviour. In particular, hidden
slow memory falls outside the declared class even when its first 12 taps fit
the bands. Under behaviour change the readings describe the old response.
Biased readings empty the set throughout this run and force the certificate
policy to abstain. Correlated readings use an unverified standard-error model.
None of these four regimes retains the stated guarantee; a high observed band
hit or zero observed financial breaches does not make an invalid contract valid.
'''
    pending=r'''
\subsection*{Pending evidence: deliberately empty result cells}
The following numerical cells remain empty. The returned archive contained no
market CSV, dynamic-inventory experiment, institution-level intervention or
external replication. The general theorem and independent novelty review also
remain open; a table placeholder is not a theorem statement or a proof.

\begin{center}\small
\begin{tabular}{p{0.62\textwidth}cc}
\toprule
Pending study & Estimate & Uncertainty\\
\midrule
Untouched market-data test beyond order-flow imbalance and depth & & \\[1.8ex]
Full changing-inventory, execution and funding comparison & & \\[1.8ex]
Dealer/venue intervention with endogenous market response & & \\[1.8ex]
Net value under empirically calibrated disclosure costs & & \\[1.8ex]
Independent implementation and replication & & \\[1.8ex]
\bottomrule
\end{tabular}
\end{center}
\noindent Further data cannot by themselves prove a general identification or
decision-value theorem. Its exact statement, proof and literature priority
require separate review. No publication rating follows from the returned run.
'''
    p1block=r'\section*{Economic interpretation and information-to-decision extension}'+'\n'+common+info_table+cost_table+failure_table+pending
    p2block=r'\section*{Information-supported portfolio choice: economic revision and returned evidence}'+'\n'+common+info_table+result_table+cost_table+failure_table+pending
    (HERE/'paper/p1_existing_revision.tex').write_text(p1block)
    (HERE/'paper/p2_existing_revision.tex').write_text(p2block)
    for num,block in [(1,p1block),(2,p2block)]:
        path=ROOT/f'ceiling_suite/papers/paper{num}/p{num}_appendix.tex'
        path.write_text(replace_block(path.read_text(),block))

    p1para=r'''\paragraph{The financial decision and related learning problems.} The proposed distinction is between recovering hidden trading structure and learning enough to support a specified exposure constraint. It does not claim that optimal risk-taking or control without complete identification is new. Moallemi, Park and Van Roy's \emph{The Execution Game} studies strategic learning about a hidden position from prices; van Waarde and colleagues' \emph{Data Informativity} studies when control is possible without unique system identification.\footnote{C.~C. Moallemi, B. Park and B. Van Roy, \emph{The Execution Game}, working paper, 2008; H.~J. van Waarde, J. Eising, H.~L. Trentelman and M.~K. Camlibel, \emph{Data Informativity: A New Perspective on Data-Driven Analysis and Control}, IEEE Transactions on Automatic Control 65 (2020), 4753--4768.} Our candidate contribution must lie in the stated market observation contract, its financial resource costs, and the comparison with a particular decision target. Equal risk targets do not imply identical return opportunities or utility-optimal portfolios. The existing identification results and historical evidence are retained; the economic extension and the scope of its returned synthetic run are recorded at the end of this draft.'''
    p2para=r'''\paragraph{Exposure feasibility and preferred risk-taking.} The guard answers whether an action satisfies a declared loss restriction; it does not, by itself, determine the investor's preferred position. Growth-optimal portfolio theory already addresses allocation, and risk-constrained and distributionally robust Kelly methods already address drawdown and distribution uncertainty.\footnote{E. Busseti, E.~K. Ryu and S. Boyd, \emph{Risk-Constrained Kelly Gambling}, Journal of Investing 25(3) (2016), 118--134; Q. Sun and S. Boyd, \emph{Distributional Robust Kelly Gambling: Optimal Strategy under Uncertainty in the Long-Run}, arXiv:1812.10371.} Related work on execution, order-book events and fund runs also makes trading costs, depth and institutional incentives central.\footnote{C. Maglaras, C.~C. Moallemi and H. Zheng, \emph{Optimal Execution in a Limit Order Book and an Associated Microstructure Market Impact Model}, working paper, 2015; R. Cont, A. Kukanov and S. Stoikov, \emph{The Price Impact of Order Book Events}, Journal of Financial Econometrics 12 (2014), 47--88; A. Capponi, P. Glasserman and M. Weber, \emph{Swing Pricing for Mutual Funds: Breaking the Feedback Loop Between Fire Sales and Fund Runs}, OFR Working Paper 18-04, 2018.} The proposed extension asks which observations justify a constraint when feedback is hidden, then chooses among feasible actions with an explicit objective. A price-taking position choice is distinct from a venue-wide intervention that changes feedback or depth. The returned exploratory account comparison and the still-empty evidence fields appear at the end of this draft.'''
    path=ROOT/'ceiling_suite/papers/paper1/p1_front.tex';s=path.read_text();path.write_text(insert_in_existing_blank(s,r'\paragraph{Closest work.}',p1para))
    path=ROOT/'ceiling_suite/papers/paper2/p2_front.tex';s=path.read_text();path.write_text(insert_in_existing_blank(s,r'\paragraph{Regulation.}',p2para))

    # One common thesis appendix, rather than repeating additions inside chapters.
    path=ROOT/'thesis/make_chapters.py';s=path.read_text()
    needle='    body = s[s.index("\\\\begin{document}")'
    if 'INFORMATION DECISION REVISION' not in s:
        at=s.index(needle)
        s=s[:at]+'    s = re.sub(r"% BEGIN INFORMATION DECISION REVISION 20261029.*?% END INFORMATION DECISION REVISION 20261029", "", s, flags=re.S)\n'+s[at:]
        path.write_text(s)
    thesis_block=p2block.replace(r'\section*{Information-supported portfolio choice: economic revision and returned evidence}',r'\chapter{Economic decision and returned information-decision experiment}')
    path=ROOT/'thesis/thesis.tex';s=path.read_text();s=re.sub(re.escape(BEGIN)+'.*?'+re.escape(END)+'\n*','',s,flags=re.S)
    anchor=r'\chapter*{Bibliography for Chapters~1, 4 and 5}'
    s=s.replace(anchor,BEGIN+'\n'+thesis_block+'\n'+END+'\n\n'+anchor)
    path.write_text(s)

    # The synthesis keeps its original theorems and adds the same evidence boundary.
    path=ROOT/'ceiling_suite/papers/flagship/identify_certify.tex'
    synth=r'\section*{Economic interpretation and returned decision experiment}'+'\n'+common+info_table+cost_table+failure_table+pending
    path.write_text(replace_block(path.read_text(),synth))
    (dest/'editorial_summary.json').write_text(json.dumps(dict(integrated='verified synthetic account and information results',pending='real data, general theorem, changing inventory, endogenous policy, calibrated disclosure and independent replication',original_findings_retained=True),indent=2))
    print('Updated existing modular sources, synthesis and common thesis appendix. Refresh/build next.')


if __name__=='__main__':main()
