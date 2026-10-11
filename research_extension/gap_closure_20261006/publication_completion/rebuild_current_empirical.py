"""Localized current-source revision, with generated field-level evidence records.

Preserves historical result files and the prior candidate. Never calls the old
whole-manuscript generator. Verification is performed by a separate script.
"""
from pathlib import Path
import json,re,hashlib,shutil
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PAPER=ROOT/'paper'
REV=ROOT/'research_extension/paper_revision_20261006/results'
BASE=HERE.parent
fields=[]

def load(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def field(table,row,key,value,source,pointer,fmt='.7f'):
    rendered=format(value,fmt) if fmt else str(value)
    fields.append(dict(table=table,row=row,key=key,value=value,rendered=rendered,
                       source=str(source.relative_to(ROOT)),pointer=pointer,source_sha256=sha(source)))
    return rendered
def table(label,caption,heads,rows,width=None):
    spec=width or ('l'+'r'*(len(heads)-1))
    return '\\begin{table}[htbp]\n\\centering\\footnotesize\\setlength{\\tabcolsep}{3pt}\n\\caption{'+caption+'}\n\\label{'+label+'}\n'+('\\begin{tabularx}{\\textwidth}{'+spec+'}' if 'X' in spec else '\\resizebox{\\textwidth}{!}{\\begin{tabular}{'+spec+'}')+'\\toprule\n'+' & '.join(heads)+r' \\\midrule'+'\n'+'\n'.join(' & '.join(r)+r' \\' for r in rows)+'\n\\bottomrule\\end{'+('tabularx' if 'X' in spec else 'tabular')+'}'+('' if 'X' in spec else '}')+'\n\\end{table}\n'
def replace_between(s,start,end,replacement):
    a=s.index(start);b=s.index(end,a);return s[:a]+replacement+'\n\n'+s[b:]
def paragraph_replace(s,start,replacement):
    a=s.index(start);b=s.index('\n\n',a);return s[:a]+replacement+s[b:]
def intstr(v):return f'{v:,}'

def main():
    source=PAPER/'Machine_Markets_JF_Submission.tex';text=source.read_text()
    backup=HERE/'baseline_current_source.tex'
    if not backup.exists():shutil.copy2(source,backup)
    text=backup.read_text()
    panelpath=BASE/'cross_venue/restored_panel_summary.json';panel=load(panelpath)
    rawpath=BASE/'cross_venue/original_panel_reproduction.json';raw=load(rawpath)['rows']
    lagpath=HERE/'panel_lag_reproduction.json';lagraw=load(lagpath)['rows'];assert len(lagraw)==768
    rempath=HERE/'remaining_diagnostics.json';rem=load(rempath)
    thresholdpath=REV/'threshold_reanalysis.json';threshold=load(thresholdpath)
    eqpath=REV/'equity_reanalysis.json';eq=load(eqpath)
    gridpath=REV/'sampling_grid.json';grid=load(gridpath)
    dealerpath=REV/'dealer_reproduction.json';dealer=load(dealerpath)
    fundedpath=HERE/'high_power_table16_results.json';funded=load(fundedpath)
    rows=[]
    for variant,title in [('legacy','Legacy forward-flow'),('observed','Observed-flow EMA'),('raw_return','Observed raw return')]:
        d=panel['summaries'][variant];row=[title]
        for metric in ['Q','S']:
            row.append(field('tab:binance_panel',variant,metric,d[metric]['mean'],panelpath,['summaries',variant,metric,'mean']))
            ci=[field('tab:binance_panel',variant,metric+str(i),v,panelpath,['summaries',variant,metric,'date_t95',i]) for i,v in enumerate(d[metric]['date_t95'])]
            row.append('['+', '.join(ci)+']')
        row.append(field('tab:binance_panel',variant,'positive_share',100*d['share_Q_positive'],panelpath,['summaries',variant,'share_Q_positive'],'.2f')+r'\%')
        rows.append(row)
    baseline=table('tab:binance_panel','Original-panel measurement reconstruction: equal-weight means across assets within each of 96 sampled dates, followed by date means and exploratory Student intervals. The 768 study units contain 66,316,704 raw one-second rows; primary fits use 6,513,239 ten-second transitions. These are reduced-form diagnostics.',
        ['Construction','$Q$','Date interval','$S$','Date interval','$Q>0$ share'],rows)
    assetrows=[]
    for asset in ['BTCUSDT','ETHUSDT','SOLUSDT','ADAUSDT','DOGEUSDT','BNBUSDT','XRPUSDT','LTCUSDT']:
        row=[asset.replace('USDT','/USDT'),'96']
        for var,metric in [('legacy','Q'),('observed','Q'),('observed','Q30'),('raw_return','Q'),('observed','S')]:
            val=panel['summaries'][var]['by_asset'][asset][metric]
            row.append(field('tab:cross_asset_panel',asset,var+'_'+metric,val,panelpath,['summaries',var,'by_asset',asset,metric]))
        assetrows.append(row)
    assets=table('tab:cross_asset_panel','Original-panel asset means under explicit timing/state choices. $Q_{30}$ controls 30 ten-second bars (300 seconds); it is a long-run regression diagnostic. No participant or regulatory causal effect is identified.',
                 ['Pair','Days','Legacy $Q$','Observed $Q$','$Q_{30}$','Return $Q$','Observed $S$'],assetrows)
    feerows=[]
    for var,p,label in [('legacy',REV/'fee_reanalysis.json','Legacy'),('observed',panelpath,'Observed')]:
        d=load(p) if var=='legacy' else panel['fee_observed']
        for dep in ['Q','S']:
            for kind in ['classical','asset_cluster','date_cluster']:
                v=d[dep][kind];ptr=[dep,kind] if var=='legacy' else ['fee_observed',dep,kind]
                row=[label,dep,kind.replace('_',r'\ ')]
                for key,fmt in [('beta','.7f'),('se','.7f'),('df','.0f'),('p_t','.6f')]:
                    row.append(field('tab:natural_experiment_did',var+'_'+dep+'_'+kind,key,v[key],p,ptr+[key],fmt))
                feerows.append(row)
    fee=table('tab:natural_experiment_did','Recomputed BTC-by-post association in the original 192-unit 2022 panel. The same four-regressor specification is evaluated under three covariance references; cluster counts are eight assets and 24 sampled dates. The assignment is not randomized.',
        ['State','Index','Reference','$\\hat\\beta_3$','SE','df','$p$'],feerows)
    t=threshold
    thrrows=[]
    for name,label in [('calm','Spread at/below threshold'),('wide','Spread above threshold')]:
        row=[label]
        for key,fmt in [(name+'_n',',.0f'),('flow_slope_'+name,'.7f'),(name+'_depth_mean',',.2f'),('residual_sd_'+name,'.5f')]:
            row.append(field('tab:threshold_var',name,key,t[key],thresholdpath,[key],fmt))
        thrrows.append(row)
    thresholdtable=table('tab:threshold_var','Exploratory BTC spread-interaction regression on the first 50,000 supplied records, with 49,497 valid transitions after burn and gap filtering. Flow is signed base quantity; the slope has dollars per base unit and is not the dimensionless $Q$.',
       ['Regime','Transitions','Flow slope','Mean inside notional','Residual SD'],thrrows)
    eqrows=[]
    for stock,d in eq['per_stock'].items():
        row=['Stock '+stock,field('tab:equity_benchmark',stock,'n_rows',eq['stock_counts'][stock],eqpath,['stock_counts',stock],',.0f')]
        for key,fmt in [('n_sessions','.0f'),('Q_mean','.7f'),('S_mean','.7f'),('max_rho','.7f')]:
            row.append(field('tab:equity_benchmark',stock,key,d[key],eqpath,['per_stock',stock,key],fmt))
        eqrows.append(row)
    equitytable=table('tab:equity_benchmark','Supplied event-indexed equity representation: actual counts and means of separately reset sessions. The original stock/day mapping, decimal reconstruction and upstream licence require authentication; identities are not inferred from anonymous stock labels.',
        ['Identifier','Rows','Sessions','Mean $Q$','Mean $S$','Maximum $\\rho$'],eqrows)
    # Date-weighted full original-panel lag controls.
    lagrows=[];lagderived=[]
    for asset in ['BTCUSDT','ETHUSDT','SOLUSDT','ADAUSDT','DOGEUSDT','BNBUSDT','XRPUSDT','LTCUSDT']:
        units=[r for r in lagraw if r['symbol']==asset];row=[asset.replace('USDT','/USDT')]
        for L in [1,5,15,30,60,90]:
            v=[np.average([s['fits'][str(L)]['Q_L'] for s in r['segments']],weights=[s['n'] for s in r['segments']]) for r in units]
            mean=float(np.mean(v));ci=stats.t.interval(.95,len(v)-1,loc=mean,scale=stats.sem(v))
            lagderived.append(dict(asset=asset,L=L,n_dates=len(v),mean=mean,ci95=list(ci),daily=v))
            row.append(f'{mean:.7f}')
        lagrows.append(row)
    (HERE/'panel_lag_summary.json').write_text(json.dumps(lagderived,indent=2)+'\n')
    derivedpath=HERE/'panel_lag_summary.json'
    for i,v in enumerate(lagderived):field('tab:lag_memory_controls',v['asset'],str(v['L']),v['mean'],derivedpath,[i,'mean'])
    lagtable=table('tab:lag_memory_controls','Fresh controls on all 768 original study units, using observed flow. $L$ counts ten-second bars: the displayed horizons are 10, 50, 150, 300, 600 and 900 seconds. $L=1$ equals baseline VAR. Date intervals and every segment denominator are retained in the digital ledger.',
       ['Pair','$L=1$','$L=5$','$L=15$','$L=30$','$L=60$','$L=90$'],lagrows)
    gridrows=[]
    for i,d in enumerate(grid['cells']):
        row=[d['asset'],str(d['delta_seconds']),str(d['window_seconds'])]
        for metric in ['Q','S']:
            row.append(field('tab:empirical_grid',str(i),metric,d[metric]['mean'],gridpath,['cells',i,metric,'mean']))
            ci=[field('tab:empirical_grid',str(i),metric+str(k),v,gridpath,['cells',i,metric,'ci95',k]) for k,v in enumerate(d[metric]['ci95'])]
            row.append('['+', '.join(ci)+']')
        gridrows.append(row)
    gridtable=table('tab:empirical_grid','Complete computed recorder grid: existing BTC/ETH/ADA sample, observed flow, gap-aware filters. Each cell uses 13 dates. Intervals use a retrospective date Student reference; 60-second windows at 60-second sampling are excluded because the filter is degenerate.',
        ['Asset','$\\Delta$ (s)','$W$ (s)','$Q$','Date interval','$S$','Date interval'],gridrows)
    diagrows=[]
    for a,d in rem['assets'].items():
        row=[a]
        row.append(field('tab:falsification',a,'shuffle_rank',d['date_shuffle']['two_sided_rank_fraction'],rempath,['assets',a,'date_shuffle','two_sided_rank_fraction'],'.4f'))
        row.append(field('tab:falsification',a,'lead_Q',d['lead_flow']['mean'],rempath,['assets',a,'lead_flow','mean']))
        row.append(field('tab:falsification',a,'negative_orthant',d['kernel']['gaussian_vertex_rank'],rempath,['assets',a,'kernel','gaussian_vertex_rank'],'.4f'))
        diagrows.append(row)
    diagtable=table('tab:falsification','Reconstructed recorder diagnostics: 199 fixed-point-free whole-date flow relabellings and 1,999 Gaussian vertex draws for the six-tap negative orthant. The printed ranks are simulation diagnostics at finite resolution, not randomized-treatment or finite-sample market $p$ values.',
       ['Asset','Date-shuffle rank','Forward-paired $Q$','Negative-orthant rank'],diagrows)
    fundedrows=[]
    for i,r in enumerate(funded['cells']):
        S=r['S'];Q=S-.4;J=np.array([[.8,.6*Q,.4*Q],[.4,.5+.3*Q,.2*Q],[.016,.012*Q,.98+.008*Q]])
        radius=float(max(abs(np.linalg.eigvals(J))))
        row=[f'{S:.2f}',f'{S+.4:.2f}',f'{radius:.3f}',f'{r["capital_multiplier"]:.1f}',f'{r["mean_shock"]:.1f}']
        for key,fmt in [('halt_count','.0f'),('default_count','.0f'),('mean_min_equity',',.2f')]:
            row.append(field('tab:funded_risk_surface',str(i),key,r[key],fundedpath,['cells',i,key],fmt))
        fundedrows.append(row)
    fundedtable=table('tab:funded_risk_surface','Replayed existing funded scenarios: 1,000 paths per cell, fixed initial equity 10,000, capacity multiplier scales a 25-share limit. Halts are sticky inventory-limit hits, not a permanent trading ban or insolvency. The unconstrained system uses effective anchor 0.80 instead of nominal 0.40; all shown effective systems are supercritical.',
        ['$S_{nom}$','$S_{eff}$','$\\rho$','Capacity','Shock','Hits','Defaults','Mean min equity'],fundedrows)
    dealerrows=[]
    for S in [.5,.6,.7,.8,.9,.95]:
        row=[f'{S:.2f}'];mom=dealer['moments'][str(S)]
        row += [f'{mom["var"]:.4f}',f'{mom["lrv"]:.4f}']
        for mode in ['feedback','B1','B2','B3']:
            r=next(r for r in dealer['cells'] if r['S']==S and r['L']==10 and r['mode']==mode)
            idx=dealer['cells'].index(r)
            row.append(field('tab:dealer_drawdown_stats',str(S),mode,r['halts'],dealerpath,['cells',idx,'halts'],'.0f')+'/400')
        dealerrows.append(row)
    dealertable=table('tab:dealer_drawdown_stats','Reproduced existing lagged-memory dealer simulations at leverage parameter 10. A halt occurs at nonpositive equity or the model position limit; these causes are not separated in the archived counts. B1/B2/B3 reuse saved model flow moments, not estimated real dealer fills. All 48 cells and exact binomial intervals remain available.',
        ['$S$','Saved variance','Analytic LRV','Feedback','B1','B2','B3'],dealerrows)

    # Rebuild the panel figure from verified reconstructed units.
    frames={v:pd.DataFrame([dict(date=r['date'],symbol=r['symbol'],**{k:r[v][k] for k in ['Q','S']}) for r in raw]) for v in ['legacy','observed','raw_return']}
    fig,axes=plt.subplots(1,3,figsize=(12,3.7),layout='constrained')
    dates=frames['observed'].groupby('date').S.agg(['mean','min','max']);xx=np.arange(len(dates))
    axes[0].plot(xx,dates['mean'],label='Date mean');axes[0].fill_between(xx,dates['min'],dates['max'],alpha=.2,label='Asset range');axes[0].axhline(1,color='red',ls='--');axes[0].set(xlabel='Sampled date index',ylabel='Observed EMA index S',title='(a) Original panel');axes[0].legend(fontsize=8)
    order=['BTCUSDT','ETHUSDT','SOLUSDT','ADAUSDT','DOGEUSDT','BNBUSDT','XRPUSDT','LTCUSDT'];xx=np.arange(8)
    for v,offset,title in [('legacy',-.18,'Legacy forward flow'),('observed',.18,'Observed flow')]:
        vals=frames[v].groupby('symbol').Q.mean().reindex(order);axes[1].bar(xx+offset,vals,width=.36,label=title)
    axes[1].set_xticks(xx,[s[:-4] for s in order],rotation=45);axes[1].set(ylabel='Mean Q',title='(b) Timing sensitivity');axes[1].legend(fontsize=8)
    for i,(v,title) in enumerate([('legacy','Legacy EMA'),('observed','Observed EMA'),('raw_return','Observed return')]):
        d=panel['summaries'][v]['Q'];m=d['mean'];lo,hi=d['date_t95'];axes[2].errorbar(i,m,yerr=[[m-lo],[hi-m]],fmt='o',capsize=4)
    axes[2].axhline(0,color='black',lw=.8);axes[2].set_xticks(range(3),['Legacy','Observed','Return']);axes[2].set(title='(c) Date references',ylabel='Mean Q / date interval')
    figure=PAPER/'figures/fig_verified_panel_20261008.pdf';fig.savefig(figure);plt.close(fig)
    # True SVD pseudospectrum, explicitly a constructed fixed-coordinate example.
    J=np.array([[.5,3.],[0,.2]]);rr=np.linspace(-1.3,1.5,240);ii=np.linspace(-1.2,1.2,220)
    z=rr[None,:]+1j*ii[:,None];M=z[...,None,None]*np.eye(2)-J;singular=np.linalg.svd(M,compute_uv=False)[...,-1]
    fig,ax=plt.subplots(figsize=(5.2,4));ct=ax.contour(rr,ii,singular,levels=[.05,.15],colors=['orange','red']);ax.clabel(ct,fmt='%.2f');theta=np.linspace(0,2*np.pi,200);ax.plot(np.cos(theta),np.sin(theta),'--',color='gray');ax.scatter([.5,.2],[0,0],color='blue');ax.set(xlabel='Real z',ylabel='Imaginary z',title='Constructed J = [[0.5, 3], [0, 0.2]]',aspect='equal')
    ps=PAPER/'figures/fig_verified_pseudospectrum_20261008.pdf';fig.savefig(ps,bbox_inches='tight');plt.close(fig)
    (HERE/'figure_lineage.json').write_text(json.dumps(dict(panel_sources=[str(rawpath.relative_to(ROOT)),str(panelpath.relative_to(ROOT))],panel_figure_sha256=sha(figure),pseudospectrum_matrix=J.tolist(),pseudospectrum_levels=[.05,.15],pseudospectrum_unit_point_sigma_min=float(np.linalg.svd(np.eye(2)-J,compute_uv=False)[-1]),pseudospectrum_figure_sha256=sha(ps),scope='Generated from named numerical arrays; not evidence of actual market calibration'),indent=2)+'\n')

    # Retain the already-verified monthly table exactly.
    event_start=text.index(r'\subsection{Dynamic Monthly Event Study and Pretrend Sensitivity}')
    event_end=text.index(r'\subsection{Cross-Venue Feedback Propagation',event_start)
    event=text[event_start:event_end]
    # Full replacement of the inconsistent current empirical block; questions retained.
    body=r'''\paragraph{Controlling for Order-Splitting Memory.}
The diagnostic $Q_L=\hat J_{12}\hat c_L/(1-\sum_{\ell=1}^L\hat\phi_\ell)$ uses the regression $F_{b+1}$ on $x_b,F_b,\ldots,F_{b-L+1}$. Here $L$ counts bars, not seconds, and $L=1$ recovers VAR(1). This is an observable long-run response functional; omitted fundamentals, endogenous flow, near-zero denominators and filtering can prevent a structural interpretation.

\subsection{Covariance Restrictions and the Limits of Heteroskedastic Identification}
For a stationary VAR, $\Gamma_0=J\Gamma_0J^\top+\Sigma$ and $\Gamma_k=J^k\Gamma_0$. Matching three contemporaneous and eight lagged covariance entries gives 11 moments and seven transition/noise parameters. Our diagnostic uses a full stable transition and positive-definite innovation parameterization, segment-aware moment HAC and six starts per declared case. All 24 cases (three assets, two centering rules and four bandwidths) reject their maintained restrictions under their stated asymptotic reference. For global centering and bandwidth ten bars, $J$ statistics are 41.4063, 28.3094 and 12.1175 for BTC, ETH and ADA. These rejections do not validate the fitted economic model. The earlier restricted-fit statistic 73 concerns a different parameter class and is retained only in the historical ledger.

Contemporaneous heteroskedastic identification additionally requires invariant structural coefficients, valid innovations, orthogonal structural shocks and a defended regime partition. Nonproportional variance shifts alone do not supply all of these. In the two-equation system, exchanging shock labels maps $(\lambda,c)$ to $(1/c,1/\lambda)$ while preserving each covariance after variance rescaling. Sign or economic exclusions can distinguish some branches, but the current source's single bounded numerical root is not an identification proof. Its forward-flow pairing and endogenous volatility grouping do not establish the required assumptions. Thus the old negative coefficient is not evidence that market makers provide identified instantaneous buffering. The exact branch-equivalence witness and all covariance sensitivities are retained.

\subsection{Data Coverage, Representation and Authentication}
The supplied data are different measurement objects. Official Binance trade bars have raw executed-volume fields; the recorder files contain supplied quote/flow features; the equity representation is event-indexed; the January file contains depth snapshots. Counts of these objects cannot be combined into a count of independent, continuous one-second transitions.
'''
    body+=table('tab:datasets','Exact working-sample coverage. Original-provider attribution and reuse permission are separate from local file hashes.',
        ['Sample','Coverage','Raw rows / representation','Source status'],[
        ['Binance spot','96 dates, 2021--2024','66,316,704 one-second bar rows','Current official checksums'],
        ['Recorded BTC/ETH/ADA','April 7--19, 2021','Existing second-indexed feature files','Recorder/provider unresolved'],
        ['Supplied equity','49 stock/day sessions','272,941 event snapshots','Upstream mapping unresolved'],
        ['January BTC depth','January 9--20, 2023','3,730,870 raw snapshots','Provider/licence unresolved']],width='lXXX')
    body+=r'''
The Binance reconstruction retains the first duplicate timestamp and requires all ten observed seconds per primary bar. It resets the EMA at each gap and date, burns 150 ten-second states and estimates sufficiently long segments separately. There are 38,859 missing seconds and 363 duplicate seconds across the reconstructed study units, without conflicting duplicate rows. Legacy filling is reproduced solely to explain the original outputs. The recorder EMA is reset at gaps, continues across contiguous dates, and regressions split dates and gaps. Consecutively repeated feature renders have their recorded flow set to zero under the archived deduplication rule; this reconstructs the cache but does not authenticate the underlying execution window. No universal winsorization or quote-filter percentage is asserted.

For quote OFI, a price increase contributes new bid size and a bid-price decrease removes old bid size; an unchanged bid contributes its size change. Ask signs reverse. Quote OFI is distinct from executed signed flow. The previous simplified price-indicator formula and claim that a depth proxy automatically purges endogeneity are not used.

\section{Original Panel, Timing Sensitivity and the Fee-Schedule Comparison}
\label{sec:baseline_natural_exp}
\subsection{Baseline Reconstruction and Cross-Asset Measurement}
'''+baseline+assets+r'''
The original panel is fully reconstructed at its 768 named study units using current official archives. The large legacy positive estimate changes materially under observed-flow alignment; raw-return date intervals include zero for the pooled diagnostic. This is a measurement result, not a proof that learning is absent. A stable fitted VAR or $S<1$ is not an authenticated structural stability statement about the market.
\begin{figure*}[htbp]\centering
\includegraphics[width=\textwidth]{figures/fig_verified_panel_20261008.pdf}
\caption{Reconstructed original panel: observed EMA index by date, legacy versus observed asset means, and pooled date-level uncertainty for three measurement constructions. Every panel uses the raw-reproduced study units. No identified market-maker buffering coefficient is plotted.}
\label{fig:binance_panel_and_identification}\end{figure*}

\subsection{July 2022 Fee-Schedule Comparison and Inference}
For the 24 sampled 2022 dates, fit $Y_{it}=\beta_0+\beta_1\mathrm{BTC}_i+\beta_2\mathrm{Post}_t+\beta_3\mathrm{BTC}_i\mathrm{Post}_t+e_{it}$, where post means dates on/after July 8. There are 192 rows and one treated asset. The reconstructed sampled-date mean BTC quote volume increases by 75.010858 percent; that descriptive difference is not a fee-induced causal estimate. Table~\ref{tab:natural_experiment_did} separates the actual covariance references instead of calling classical uncertainty clustered.
'''+fee+r'''
For observed $Q$, the date-cluster interval is $[-0.001025969,0.000814559]$. Neither a non-rejection nor the cross-asset placebo ranking proves invariance or a parallel counterfactual. The old equivalence margin 0.007 is about 18 times the corrected pooled baseline; passing such a margin cannot establish economically meaningful equivalence. Asset comparisons are not random treatment reassignments. Serial dependence across sampled dates, spillovers and the single treated unit remain material inference limitations.
'''+event+r'''
\subsection{Joint Cross-Venue Predictive Association}
\label{sec:cross_venue_verified}
An unrestricted joint four-variable VAR uses price and flow from the recorder and Binance on 11 overlapping April 2021 dates, with ten-second bins, complete-bin restrictions and segment intercepts. Its baseline EMA spectral radii are 0.950614 (BTC), 0.949934 (ETH) and 0.948204 (ADA). At the BTC 60-second horizon, the normalized generalized Binance-to-recorder price share is 0.442926; the corresponding share across all 24 orthogonal orderings ranges approximately 0.17--0.8483. That interval concerns this asset, direction and horizon; it is not the range over all horizons. Raw-return and timestamp-shift sensitivities and all six horizons are retained. Quote-currency differences, subsecond alignment and shock identification prevent a causal transmission claim.

\section{Liquidity States, Equity Representation and Financial Simulations}
\label{sec:stress_fragility}
\subsection{Spread-Interaction and Switching-Regression Diagnostics}
The exploratory spread regression uses the first 50,000 supplied BTC records, a 100-event EMA deviation in dollars, observed signed base-unit flow, valid consecutive-second pairs, burn 500 and the lagged-spread 90th percentile. Its selected threshold is 5.874 dollars. The flow-slope contrast is 0.1242465 dollars per base unit, with 60-second HAC SE 0.2181307 and normal-reference $p=0.568951$. These dimensional slopes are not the theoretical feedback $Q$; an assumed 10-basis-point conversion cannot create an empirical instability index.
'''+thresholdtable+r'''
The wider-spread subset has lower recorded inside depth and residual SD ratio 1.450627. Selection on observed spread is descriptive. The repaired switching regression uses exact joint transition posteriors, two specifications, four starts, two variance floors and all three assets under EMA/return measurements. On the seven expanding test dates April 13--19, all MSE-contrast intervals include zero, and every full-coefficient versus variance-only contrast interval includes zero. Some density scores improve relative to OLS. BTC full-switching SD ratios change from about 1,103 to 112 across the two variance floors, and four selected forecast fits reach their iteration limit. Neither this sensitivity nor non-rejection proves absent regimes.

\subsection{Historical Flash-Crash Question and Constructed Scenarios}
\label{sec:historical_flash_crashes}
The 2010 equity flash crash and 2014 Treasury event motivate the question of liquidity depletion and feedback. The retained historical script does not ingest either event's transaction/account data: it assigns feedback coefficients and simulates one price/depth path; the Treasury function returns fixed inputs. Its protected path changes depth and external liquidation flow as well as clipping adaptive flow. The calculated scenario differences therefore cannot be attributed to gating alone, calibrated historical dealer losses, or measured policy protection. The original numerical outputs remain archived as constructed illustrations. Authenticating event-level data and an isolated counterfactual remains an open question.
\begin{figure*}[htbp]\centering
\begin{tabularx}{\textwidth}{XX}\toprule
Constructed 2010 scenario & Constructed 2014 scenario \\\midrule
Assigned depth and adaptive coefficients; simulated price paths & Assigned yield excursion and protected excursion \\
Protected path changes multiple inputs & Suppression follows from assigned endpoints \\
No historical TAQ ingest & No historical order/account ingest \\\bottomrule\end{tabularx}
\caption{Source audit of the retained historical illustrations. Neither scenario supplies a measured historical intervention effect. The original numerical studies and their questions are preserved in the evidence archive.}
\label{fig:equity_flash_crash_taq}\end{figure*}

\subsection{Supplied Equity Representation}
The equity calculations use top-quote OFI, a 100-event EMA, burn 500 and session resets. Negative-feedback sessions are retained. The anonymous STOCK/DAY labels and event clock do not authenticate original company identities, exchange rules or a causal comparison with crypto.
'''+equitytable+r'''
\subsection{Replayed Financial Scenarios and Accounting Limits}
The existing funded-scenario grid has been rerun with its saved seed and inputs. Capacity means an inventory limit at fixed initial capital. Effective persistence differs from nominal metadata; the unconstrained transitions in this grid are supercritical. The recorded limit-hit event does not halt later trading. These rows cannot establish insolvency inside a stable system.
'''+fundedtable+r'''
The separate lagged-memory dealer experiment has 48 cells with 400 paths each. Its own implemented matrix is $J_{lag}=\left(\begin{smallmatrix}a&1\\\eta Q&1-\eta\end{smallmatrix}\right)$, so its eigenvalues must be calculated under that timing rather than the price-first theoretical matrix. Cash receives signed fills at the current mark plus half-spread, inventory takes the opposite fill, then equity is marked at the next price. Saved halt counts combine equity and position-limit events. They illustrate a model risk limit, not observed dealer defaults.
'''+dealertable+r'''
Here low-frequency power means long-run variance, not marginal variance. With two independent unit-variance shock streams, the lagged model's analytic flow LRV is $[(1-a)^2+(Q\sigma/\lambda)^2]/(1-S)^2$; its saved marginal variance is a separate quantity. B3 can match the severe halt pattern with exogenous persistent flow, so these simulations do not isolate adaptive learning as its cause. Pricing, spread, leverage, fees, funding, fills and queue priority are hypothetical inputs. A tested cash identity is necessary but insufficient for market calibration.

\section{Observation Contracts and Reconstructed Robustness}
\label{sec:surveillance}
\subsection{Participant Information and Reset Requirements}
Anonymous aggregate market features do not reveal participant identities. The exact merged-rate equivalence theorem concerns a reset modeled price state with known anchor and impact; it does not imply that an arbitrary public VAR identifies its latent cohort measure. A hypothetical audited contract would provide participant-specific flow, state definitions and a verifiable reset. Such information can change identification, but regression consistency additionally needs excitation and valid innovations. These are proposed information requirements, not a statement that existing legal identifiers reveal every algorithm or internal learning state.

\begin{figure*}[htbp]\centering
\begin{tikzpicture}[node distance=1.4cm]
\node[draw,align=center,text width=5.5cm] (public) {Aggregate observed features\\Timing/filter-dependent diagnostics};
\node[draw,align=center,text width=5.5cm,right=0.6cm of public] (audit) {Hypothetical audited experiment\\Defined state, input and reset};
\node[draw,align=center,text width=5.5cm,below=of public] (limit) {No participant attribution\\No automatic structural identification};
\node[draw,align=center,text width=5.5cm,below=of audit] (req) {Needs excitation and innovation assumptions\\Monetary loss requires exposures};
\draw[->] (public)--(limit);\draw[->] (audit)--(req);
\end{tikzpicture}
\caption{Information requirements for distinct experiments. Legal audit tags alone do not disclose a learning recursion or authenticate a cash-loss functional.}
\label{fig:surveillance_contracts}\end{figure*}

\subsection{Reconstructed Date-Shuffle, Lead-Flow and Sign Diagnostics}
The previously untraced placebo questions have now been computed under a written retrospective protocol on the existing recorder sample. Date relabelling uses each date's longest continuous segment, position alignment and truncation; all relabellings exclude fixed points. The six-tap price-to-flow regression has a date-mean covariance and is projected onto the negative orthant. That orthant contains the negative Hausdorff-memory cone, so its rejection is a sufficient observable sign restriction diagnostic under the assumed Gaussian covariance law. The diagnostic does not establish that regression taps equal latent algorithm kernels. It does not certify the full continuous-cone test or repair endogenous regressors.
'''+diagtable+r'''
All three shuffle ranks reach the 1/200 simulation floor, and all three Gaussian orthant ranks reach the 1/2000 floor. These are lower-resolution ranks rather than exact zero probabilities. Cross-date exchangeability and the Gaussian covariance reference remain unproved in 13 dates. Lead-flow pairing reproduces the much larger forward diagnostic; it is evidence that timing matters, not a valid exclusion of reverse causation. The independent ledger retains all coefficients, covariances and relabelling indices.

\subsection{Original-Panel Lag Controls and Horizon Units}
The original 768-unit lag grid is newly recomputed from the authenticated current archives. It uses observed flow and complete ten-second bars, without filling or cross-gap regressors. The digital ledger retains every coefficient and denominator as well as date means and intervals. A positive adjusted mean cannot distinguish meta-order execution from adaptive feedback, and finite lag controls do not prove a positive asymptotic floor.
'''+lagtable+r'''
\subsection{Sampling and Filter Sensitivity}
The complete recorder grid reports each computed construction. The mechanical EMA anchor is $1-2/(W/\Delta+1)$ and is distinct from a fitted VAR coefficient. Finite grid comparisons do not establish a universal $O(1/W)$ economic law or robustness to every discretization. Some coarse-clock $Q$ intervals include zero.
'''+gridtable+r'''
\subsection{January Depth and Retrospective Forecasts}
The January sample has 3,730,870 raw snapshots spanning January 9--20, 2023. Top-quote OFI and the 120-second EMA yield 844,621 valid transitions in 152 segments over 12 dates. Mean $Q=0.000910232$, while $Q_{30}=-0.001296032$ with date interval $[-0.001567464,-0.001024600]$. The provider is unresolved and the sample was previously examined; it is not an untouched prospective holdout. Existing expanding-date AR/VAR forecasts use training-only scaling and retain all contrasts; price-loss intervals include zero. Non-rejection neither proves equal prediction nor validates a learning mechanism.
'''
    text=replace_between(text,r'\paragraph{Controlling for Order-Splitting Long Memory.}',r'\section{Regulatory Policy Implications and Conclusion}',body)
    # Import the proven resource result before the conditional economic theorem.
    marker=r'\begin{proposition}[Conditional Quote and Allocation Cost of Ambiguity]'
    importline=r'\input{../research_extension/gap_closure_20261006/publication_completion/resource_frontier.tex}'
    if importline not in text:text=text.replace(marker,importline+'\n\n'+marker)
    # Eliminate stale generated macro imports now unused by the rendered manuscript.
    for name in ['binance_panel_macros','empirical_macros','solvency_macros']:
        text=text.replace(r'\input{generated/'+name+'.tex}','% Historical macro import retired after current-source reconstruction.')
    text=replace_between(text,r'\begin{abstract}',r'\end{abstract}',r'''\begin{abstract}
\noindent We study what a controlled aggregate price experiment can reveal about adaptive memory, and which financially specified resources make that inference possible. For a known symmetric single-versus-split cohort pair, total executed probing quantity has necessary and sufficient order $\delta^{-2}$ under Gaussian observation noise. A fixed lifetime quantity budget cannot be overcome by waiting, whereas an average-power budget yields horizon order $\delta^{-4}$. Positive price-response gains connect this distinction to an explicit monetary output and cost allowance. These are conditional experiment results, distinct from public participant attribution or operational solvency guarantees. Empirically, reconstruction of the original 768-unit market panel shows pronounced flow-timing and filter sensitivity; raw-return date intervals include zero and maintained covariance restrictions reject. Replayed financial simulations separate model inventory-limit events from defaults and expose nominal/effective persistence differences. The resulting evidence supports precise information and calibration requirements, while leaving causal learning attribution and real-market safety validation unresolved.
''')
    text=paragraph_replace(text,'Crucially, we show that this identification boundary extends to empirical measurement:',r'''The empirical reconstruction tests observable measurement and model restrictions rather than claiming latent learning identification. In the original 768-unit panel, mean legacy forward-flow $Q=0.0081536$ becomes $0.0003807$ with observed flow; pooled raw-return $Q=-0.0001625$ has a date interval including zero. The recorder timing comparison is a different sample and is reported separately. Maintained covariance restrictions reject, and the fee-schedule exercise is a one-treated-asset descriptive association with covariance-sensitive uncertainty. These findings establish why a public reduced-form coefficient cannot be substituted for the controlled information contract.''')
    text=paragraph_replace(text,r'We establish what public price and order-flow data can and cannot reveal',r'''We identify the merged rate--weight representation under the modeled reset price-response contract, with known anchor and impact (Theorem~\ref{thm:m1_equivalence}). The new resource comparison establishes necessary and sufficient quantity order $\delta^{-2}$ for a known symmetric pair and horizon order $\delta^{-4}$ under average power (Theorem~\ref{thm:resource_frontier}). Waiting cannot compensate for a fixed lifetime executed-quantity budget. Conditional monetary exposure and accumulated cost convert that quantity allowance into a resolution constraint. This is the proposed central advance; general unknown-mixture recovery and adaptive probing remain outside the theorem.''')
    # Related-work claims are limited to the actual compared primary settings.
    text=paragraph_replace(text,r'A extensive literature examines',r'''An extensive literature studies price impact, signed-flow memory and quote imbalance \citep{bouchaud2004fluctuations,cont2014}. Our long-run regression diagnostics retain these as competing explanations. Lag controls and observable kernel signs do not identify parent orders, learner policies or contemporaneous structural shocks.''')
    text=paragraph_replace(text,r'In applied mathematics and fluid mechanics, non-normal',r'''Non-normal transients and Kreiss bounds are established mathematical tools \citep{kreiss1962,spijker1991,trefethen2005spectra}. Their application to financial bubbles also precedes this paper: \citet{sornette2023nonnormal} links subcritical financial dynamics to non-normal networks and the Kreiss constant. We therefore do not claim first application to finance. Our proposed contribution connects a particular memory-resolution experiment to executed-quantity and monetary-output resources; the underlying norm and testing tools remain established.''')
    text=replace_between(text,r'\subsection{Empirical Research Design and Setting}',r'\section{Theoretical Model and Identification Boundaries}',r'''\subsection{Empirical Research Design and Setting}
We retain the original multi-year panel, recorder timing/filter comparison, joint cross-venue VAR, liquidity-state regressions, supplied equity representation, financial simulations and forecast diagnostics. Each has its own clock, sample and inference assumptions. Existing raw files and outputs are reconstructed before interpreting mechanisms. The paper distinguishes an observed coefficient, a maintained-model test, a constructed financial scenario and a controlled identification theorem. Data/provider and calibration boundaries accompany the results; they are not inferred from a successful numerical reproduction.

Theoretical identification and resource bounds appear first, followed by measurement construction and reconstructed empirical studies. The final section gives the finite-window input/output gate and its operational limitations.
''')
    # Numerical-looking hand-drawn contours replaced by actual singular values.
    a=text.index(r'\begin{figure}[tbp]',text.index(r'\subsection{Pseudospectral Contours'))
    b=text.index(r'\end{figure}',a)+len(r'\end{figure}')
    text=text[:a]+r'''\begin{figure}[tbp]\centering
\includegraphics[width=0.65\textwidth]{figures/fig_verified_pseudospectrum_20261008.pdf}
\caption{Computed singular-value contours for the declared constructed matrix $J=\left(\begin{smallmatrix}0.5&3\\0&0.2\end{smallmatrix}\right)$ at 0.05 and 0.15. Its spectral radius is 0.5; the 0.15 contour crosses the unit circle. This fixed-coordinate illustration is not a calibrated cohort-market or monetary-loss experiment.}
\label{fig:pseudospectrum}\end{figure}'''+text[b:]
    text=text.replace('for the non-normal market Jacobian, the pseudospectral contours stretch dramatically','for a constructed non-normal matrix, computed pseudospectral contours can stretch')
    text=text.replace('In empirical cross-impact calibrations examined here, asymmetric feedforward coupling injects transient terms of order $t K_{21} \\rho^{t-1}$, compressing the safe radius by $14.5\\%$ relative to decoupled trading.','A fixed-coordinate constructed coupling can increase peak gain. Its magnitude requires a declared output and shock set; no empirical percentage follows from this proposition.')
    text=paragraph_replace(text,r'Proposition~\ref{prop:cross_kreiss} demonstrates',r'''Proposition~\ref{prop:cross_kreiss} concerns nonnegative downstream coupling under fixed shock/output geometry. Hedged or signed monetary outputs need separate treatment; they do not inherit a universal monotonic radius comparison. The earlier empirical 14.5-percent calibration claim is not established by this proof.''')
    text=paragraph_replace(text,r'We examine whether observable market data can identify destabilizing',r'''We establish a resource distinction within a precisely defined memory-resolution experiment: lifetime executed quantity of order $\delta^{-2}$ is necessary and sufficient for a known symmetric pair, while average power gives horizon order $\delta^{-4}$. A fixed monetary-output and accumulated-cost allowance bounds quantity; more waiting alone cannot overcome that lifetime resource limit. The empirical reconstruction shows strong timing/filter sensitivity and maintained-model rejection, rather than participant-level learning attribution. Existing simulations distinguish capacity events, defaults and effective dynamics. Real-market financial calibration and independent specialist assessment remain necessary before publication and operational claims.''')
    # Add actual nearest-work citations rather than invented priority assertions.
    refs=r'''
\bibitem[Liu and Ammari(2023)]{liuammari2023}
Liu, P., and H. Ammari, 2023, Super-resolution of positive near-colliding point sources, \emph{Information and Inference} 12, 3087--3111; primary preprint arXiv:2212.00536.
\bibitem[Manole and Ho(2022)]{manoleho2022}
Manole, T., and N. Ho, 2022, Refined convergence rates for maximum likelihood estimation under finite mixture models, \emph{Proceedings of Machine Learning Research} 162, 14979--15006.
\bibitem[Sornette et al.(2023)]{sornette2023nonnormal}
Sornette, D., S. Lera, J. Lin, and K. Wu, 2023, Non-normal interactions create socio-economic bubbles, primary manuscript arXiv:2205.08661v5.
'''
    if r'\bibitem[Liu and Ammari' not in text:text=text.replace(r'\end{thebibliography}',refs+'\n'+r'\end{thebibliography}')
    source.write_text(text)
    (HERE/'generated_field_ledger.json').write_text(json.dumps(dict(status='GENERATED_REQUIRES_INDEPENDENT_VERIFICATION',current_source_sha256=sha(source),baseline_source_sha256=sha(backup),fields=fields),indent=2)+'\n')
    (HERE/'empirical_body.tex').write_text(body)
    print('Rebuilt current empirical source and',len(fields),'field records; independent verifier required')

if __name__=='__main__':main()
