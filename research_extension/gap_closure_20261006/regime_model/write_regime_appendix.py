from pathlib import Path
import json
HERE=Path(__file__).resolve().parent

def longtable(caption,columns,header,rows,label,size='small'):
    return '\n{\\'+size+'\n\\begin{longtable}{'+columns+'}\n\\caption{'+caption+'}\\label{'+label+r'}\\'+'\n'+r'\toprule '+header+r'\\\midrule\endfirsthead'+'\n'+r'\toprule '+header+r'\\\midrule\endhead'+'\n'+r'\bottomrule\endfoot'+'\n'+'\n'.join(' & '.join(map(str,row))+r'\\' for row in rows)+'\n'+r'\end{longtable}'+'\n}\n'

def build():
    d=json.loads((HERE/'market_results.json').read_text());s=r'''
\section{Repaired Switching Likelihood: Variance Floors and Chronological Forecasts}
\label{sec:regime_repaired}
The historical generator fits a scalar differenced-EMA regression, rather than a two-equation structural VAR. Its transition updates multiply marginal smoothed probabilities instead of using joint state-transition posteriors. It also imposes persistence bounds, floors emission densities, labels iteration counts as convergence, and forms a unit-dependent index by adding persistence to ten times a flow slope. These defects invalidate its asserted structural interpretation. They do not establish the source of every historical numerical discrepancy.

The replacement uses log-domain forward/backward calculations and exact posterior transition counts. Regression segments restart at gaps and UTC dates; the EMA itself continues across contiguous UTC dates under the preserved measurement construction. Transition parameters are shared across segments, while latent-state probabilities restart. A fitted initial-state distribution and a declared variance floor are included. Independent exhaustive hidden-path enumeration checks the likelihood and both marginal and pair posteriors. The compiled two-state calculation matches the Python reference, including extreme tail emissions.

The data are the existing April 7--19, 2021 recorder caches. BTC, ETH and ADA contribute 102,470, 102,771 and 102,898 transitions respectively under each measurement construction, split into 16, 14 and 13 regression segments. These are ten-second bins, including the raw-return sensitivity; they are not one-second return observations. The response is the next change in the 300-second EMA deviation, or the next ten-second raw return. Regressors are an intercept, the lagged price state and observed signed flow. This remains a conditional scalar regression and does not identify a participant's learning rule.

A shared-coefficient variance-switching model is compared with a model whose coefficients and variances both switch. Full-sample fits use four initializations at each of two fixed variance floors, $10^{-6}$ and $10^{-4}$ in standardized target units. All 96 full-sample starts converge. The maximum training likelihood selects a start within each fixed specification; agreement across these starts is not a global optimality certificate.

BTC's lower variance binds at both floors. Its full-switching residual-standard-deviation ratio is about 1,103 at $10^{-6}$ and 112 at $10^{-4}$ for EMA differences; the corresponding return ratios are about 1,113 and 113. The variance-only model shows similar sensitivity. Such ratios describe the constrained likelihood fit and cannot be presented as an identified crisis multiplier. ETH and ADA do not hit these floors in the reported full-sample fits.
'''
    rows=[]
    for name,ds in d['datasets'].items():
        asset,state=name.split('_',1)
        for key,v in ds['specifications'].items():
            f=v['selected'];floor=float(key.split('_')[0]);mode='Variance' if f['shared_beta'] else 'Full';ll=[r['log_likelihood'] for r in v['starts']]
            rows.append([asset,'EMA' if state=='x' else 'Return',f'{floor:.0e}',mode,f"{v['residual_sd_ratio']:.3f}",f"{f['variance'][0]:.6g}",sum(r['status']=='CONVERGED' for r in v['starts']),f'{max(ll)-min(ll):.3g}'])
    s+=longtable('All fixed full-sample specifications. Variance floors are in standardized target units. SD ratios are conditional fit summaries; BTC lower variances bind at the declared floors.','llllrrrr',r'Asset & State & Floor & Model & SD ratio & Low variance & Conv./4 & LL spread',rows,'tab:regime_floor_sensitivity',size='footnotesize')
    s+=r'''
Chronological expanding-window forecasts train on six initial dates and evaluate April 13--19, 2021. Each test segment starts from the fitted initial-state distribution; predictions use only preceding outcomes, and scaling uses training data alone. Two starts are retained per model/fold at the primary floor. Of 168 forecast fit starts, 156 converge and 12 reach the iteration limit. Four of the 84 selected model/fold fits reach that limit; these cases remain in the ledger and comparisons rather than being relabeled as converged.

The table reports mean absolute loss differences across seven evaluation dates. Positive differences favor the indicated switching model over single-regime OLS. The ``Full--variance'' rows compare full switching directly with variance-only switching. MSE differences have squared-basis-point units; negative-log-score differences are in nats per observation. These are not percentage improvements. Date-level Student intervals are exploratory references with seven consecutive dates, without justified serial independence or multiplicity coverage.
'''
    rows=[]
    comparisons=[('variance_only','Variance--OLS'),('coefficients_and_variance','Full--OLS'),('full_minus_variance_only','Full--variance')]
    for name,ds in d['datasets'].items():
        asset,state=name.split('_',1)
        for key,label in comparisons:
            a=ds['summary'][key]['mse'];b=ds['summary'][key]['negative_log_score']
            rows.append([asset,'EMA' if state=='x' else 'Return',label,f"{a['mean']:.4f}",f"[{a['ci95'][0]:.4f}, {a['ci95'][1]:.4f}]",f"{b['mean']:.4f}",f"[{b['ci95'][0]:.4f}, {b['ci95'][1]:.4f}]"])
    s+=longtable('Chronological forecast differences on seven dates. All MSE intervals and all full-versus-variance-only score intervals span zero. Some switching density-score intervals versus OLS exclude zero.','lllrlrl',r'Asset & State & Comparison & $\Delta$MSE & Date interval & $\Delta$NLS & Date interval',rows,'tab:regime_market_rebuilt',size='footnotesize')
    s+=r'''
All MSE-difference intervals include zero. BTC and ETH switching density scores improve relative to the single-Gaussian benchmark under the exploratory date reference, while ADA intervals include zero. Every full-versus-variance-only interval includes zero for both losses. Thus additional coefficient switching has no clear forecast advantage over volatility switching in this small retrospective evaluation. This does not prove equal forecasts, absent regimes, or absent adaptive trading. A conditional-volatility explanation remains compatible with the density gains.

The historical 62.7-fold structural claim remains unsupported by its generating procedure. The repaired ratios are materially sensitive to an explicit constraint, and this study does not authenticate that old literal or establish that all historical differences have one cause. Provider authentication, serially valid parameter uncertainty, model adequacy, and causal mechanism identification remain separate gates. Full parameters, likelihood histories, all starts and all forecast folds are retained in the digital results.
'''
    return s
if __name__=='__main__':(HERE/'regime_appendix.tex').write_text(build())
