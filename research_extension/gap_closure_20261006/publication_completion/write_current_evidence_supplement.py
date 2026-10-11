"""Single-file supplement of current, explicitly scoped numerical evidence."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;ROOT=HERE.parents[2]
REV=ROOT/'research_extension/paper_revision_20261006/results'
def load(p):return json.loads(p.read_text())
def esc(s):return str(s).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')
def interval(v,n=7):return '['+', '.join(f'{x:.{n}f}' for x in v)+']'
def tab(label,caption,heads,rows):
 spec='l'+'r'*(len(heads)-1)
 return '\n\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{longtable}{'+spec+'}\n\\caption{'+caption+'}\\label{'+label+'}\\\\\n\\toprule\n'+' & '.join(heads)+r' \\\midrule\endfirsthead'+'\n\\toprule\n'+' & '.join(heads)+r' \\\midrule\endhead'+'\n'+'\n'.join(' & '.join(map(str,r))+r' \\' for r in rows)+'\n\\bottomrule\\end{longtable}\\normalsize\n'
def run():
 parts=[r'''\documentclass[10pt]{article}
\usepackage[T1]{fontenc}\usepackage{lmodern}\usepackage[margin=.8in]{geometry}
\usepackage{amsmath,amssymb,booktabs,longtable}\usepackage[colorlinks=true,urlcolor=blue]{hyperref}
\title{Machine Markets: Current Numerical Evidence Supplement}
\author{Pratik Niroula and Prashant Niroula}\date{October 8, 2026}
\begin{document}\maketitle
\noindent This supplement documents the current reconstructed questions and numerical references. Its intervals are exploratory references under the stated assumptions, not certificates of serial confidence coverage, causal learning attribution, source rights for every transformation, market calibration or independent specialist review. Historical literals are preserved in earlier artifacts and superseded by the named reconstructions.

\section{Sources, Representation and Protocols}
The original 768 Binance study units are reproduced from current official archives with official SHA256 and ZIP CRC checks. Historical download-time hashes were not preserved. All three recorded one-second files match version 1 of Nielsen's primary release byte for byte (uploader-declared CC0). The January CSV exactly reproduces from version 1 of the primary Parquet distribution (uploader-declared Apache 2.0); exchange/contract metadata are absent. The FI-2010 primary record declares CC BY 4.0, while original archive acquisition and local stock/day transformation authentication remain open. Current Binance Vision terms specify CC BY-NC-SA 4.0; final derivative publication must reflect the provider terms.

The recorder baseline admits occupied ten-second bins, including partial bins. Its EMA resets at missing whole bins and continues across contiguous dates; regressions split dates and bin gaps. The strict sensitivity requires ten observed seconds per bin and resets across the resulting gaps. Recorded flow is a constructed feature; source-byte authentication does not authenticate an executed-volume accumulation window. The original Binance reconstruction separately requires complete bins and resets by date/gap. Equity uses event-indexed supplied labels, not authenticated company identities. January uses top-quote OFI, not executed trades.

\section{Strict Recorder Completeness Sensitivity}
Strict constructions use EMA 300, burn 150 ten-second states and sufficiently long date/gap segments. Counts and date-Student references are calculated from separately saved segment estimates. Baseline partial-bin counts are 75(BTC), 72(ETH), 69(ADA); removing those bins also changes subsequent EMA burn and segment eligibility.
''']
 strict=load(HERE/'recorder_bin_completeness.json');rows=[]
 for asset,d in strict['assets'].items():
  for key,v in d['strict_variants'].items():
   rows.append([asset,esc(key),v['n_dates'],v['n_segments'],v['n_transitions'],f"{v['mean_Q']:.7f}",interval(v['date_reference_interval'])])
 parts.append(tab('tab:strict_recorder','Every strict recorder construction; all questions retained.',['Asset','Construction','Dates','Segments','Transitions','$Q$','Date reference'],rows))
 parts.append(r'\section{Original-Panel Lag Controls and Date References}'+'\n'+r'All 768 study units are reconstructed without filling. $L$ counts ten-second bars, so $L=90$ is 900 seconds. Segment estimates combine within each date using transition weights. The following intervals use equal-weight sampled dates, with serial-dependence and selection limitations.'+'\n')
 rows=[]
 for v in load(HERE/'panel_lag_summary.json'):
  rows.append([v['asset'][:-4],v['L'],v['L']*10,v['n_dates'],f"{v['mean']:.7f}",interval(v['ci95'])])
 parts.append(tab('tab:full_lag_intervals','Full six-horizon original-panel lag ledger.',['Pair','$L$','Seconds','Dates','Mean $Q_L$','Date reference'],rows))
 parts.append(r'\section{Calendar Dependence Sensitivity}'+'\n'+r'Calendar Bartlett weights depend on actual elapsed days, rather than treating irregular sampled dates as equally spaced. The Gaussian references require additional mixing/stationarity conditions. The 32-reference grid is retrospective and does not establish finite-sample or causal confidence coverage.'+'\n')
 rows=[]
 for r in load(HERE/'calendar_inference_sensitivity.json')['rows']:
  rows.append([esc(r['variant']),r['metric'],r['calendar_bandwidth_days'],r['n_dates'],f"{r['mean']:.7f}",interval(r['normal_reference_interval'])])
 parts.append(tab('tab:calendar_references','All calendar covariance references.',['Construction','Index','Days','Dates','Mean','Gaussian reference'],rows))
 parts.append(r'\section{Fee Comparison: Reference Sensitivity}'+'\n'+r'The four-regressor BTC-by-post specification has 192 rows, one treated asset, eight asset groups and 24 date groups. Non-rejection does not establish causal invariance. The legacy placebo rank is not a randomized-treatment probability. The old 0.007 equivalence margin is inappropriate relative to the corrected baseline magnitude.'+'\n')
 p=load(BASE/'cross_venue/restored_panel_summary.json');fee=p['fee_observed'];rows=[]
 for metric in ['Q','S']:
  for ref in ['classical','asset_cluster','date_cluster']:
   r=fee[metric][ref];rows.append([metric,esc(ref),r['df'],f"{r['beta']:.7f}",f"{r['se']:.7f}",f"{r['p_t']:.6f}",interval(r['ci95'])])
 parts.append(tab('tab:fee_reference_intervals','Corrected observed-flow coefficient under all declared references.',['Index','Reference','df','Effect','SE','$p$','Reference interval'],rows))
 parts.append(r'\section{Covariance Model Restrictions}'+'\n'+r'All fixed centering/bandwidth cases are retained, with six starts each. The model uses unrestricted stable transition and positive-definite innovation parameterization. The 11 moments and seven parameters give a four-degree asymptotic reference. Rejection is evidence against maintained restrictions for that construction, not validation of latent learning or a causal model.'+'\n')
 rows=[]
 cov=load(BASE/'model_diagnostics/covariance_complete.json')
 for asset,d in cov['assets'].items():
  for key,r in d['cases'].items():
   rows.append([asset,esc(key),r['n_rows'],r['df'],f"{r['J_stat']:.5f}",f"{r['p_chi2']:.4g}",f"{r['Q']:.7f}"])
 parts.append(tab('tab:covariance_all_cases','Complete maintained-model diagnostic grid.',['Asset','Case','Rows','df','$J$','$p$','$Q$'],rows))
 parts.append(r'\section{Joint Cross-Venue Association}'+'\n'+r'The joint four-variable VAR uses 11 matched April 2021 dates, complete ten-second bins, segment effects and actual timestamps. Generalized shares are normalized by row. All 24 orthogonal orderings are retained. Quote-currency and timing differences and missing structural shock identification prevent a causal transmission claim.'+'\n')
 import pandas as pd
 f=pd.read_csv(BASE/'cross_venue/joint_fevd_summary.csv');rows=[]
 for _,r in f.iterrows():
  rows.append([r.asset,int(r.horizon_seconds),f'{r.rho:.7f}',f'{r.bn_price_to_cb_price_generalized:.5f}',f'[{r.bn_price_to_cb_price_order_min:.5f}, {r.bn_price_to_cb_price_order_max:.5f}]',f'{r.cb_price_to_bn_price_generalized:.5f}'])
 parts.append(tab('tab:joint_fevd_all_horizons','All six horizons for both predictive directions.',['Asset','Seconds',r'$\rho$','BN-to-recorder','Ordering range','Recorder-to-BN'],rows))
 parts.append(r'\section{Switching Models and Forecast Boundaries}'+'\n'+r'The scalar switching regression uses exact joint transition posteriors, four starts, two variance floors, two specifications and six datasets. Forecasts use seven chronological expanding test dates, April 13--19, 2021. All MSE references span zero; every full-coefficient versus variance-only reference also spans zero. Selected iteration-limit fits and variance-floor sensitivity remain part of the result.'+'\n')
 market=load(BASE/'regime_model/market_results.json');rows=[]
 for name,d in market['datasets'].items():
  for key in ['variance_only','coefficients_and_variance','full_minus_variance_only']:
   a=d['summary'][key]['mse'];b=d['summary'][key]['negative_log_score']
   label={'variance_only':'Var--OLS','coefficients_and_variance':'Full--OLS','full_minus_variance_only':'Full--Var'}[key]
   rows.append([esc(name),label,f"{a['mean']:.5f}",interval(a['ci95'],5),f"{b['mean']:.5f}",interval(b['ci95'],5)])
 parts.append(tab('tab:all_switching_forecasts','Every reported switching forecast comparison.',['Dataset','Comparison','MSE change','Date reference','Density change','Date reference'],rows))
 parts.append(r'\section{Replayed Financial Scenarios}'+'\n'+r'The 22,000 existing funded paths are rerun with their saved seed and independently reconstructed cash/mark identity. Capacity scales the 25-share inventory limit at fixed initial equity 10,000. Effective anchor is 0.80 rather than nominal 0.40. All effective systems in that grid are supercritical; inventory-limit hits are sticky occurrences, not a permanent ban or default. Independent inventory projection sensitivity leaves the reported hit counts unchanged.'+'\n')
 funded=load(HERE/'high_power_table16_results.json');rows=[]
 for r in funded['cells']:
  rows.append([f"{r['S']:.2f}",f"{r['S']+.4:.2f}",f"{r['capital_multiplier']:.1f}",f"{r['mean_shock']:.1f}",r['halt_count'],r['default_count'],f"{r['mean_min_equity']:.4f}"])
 parts.append(tab('tab:all_funded_replays','All 22 funded cells, 1,000 paths each.',['Nominal $S$','Effective $S$','Capacity','Shock','Hits','Defaults','Mean minimum equity'],rows))
 parts.append(r'The separate lagged-memory dealer experiment uses 400 paths per cell. Its archived halt flag combines nonpositive equity and a position-limit event. These causes are not separated in the saved count, and its flow calibration remains model moments rather than real queue fills. All 48 cells and exact binomial references are retained below.'+'\n')
 rows=[]
 for r in load(REV/'dealer_reproduction.json')['cells']:
  rows.append([f"{r['S']:.2f}",f"{r['L']:.0f}",r['mode'],r['halts'],r['n'],f"{r['rate']:.4f}",interval(r['ci95_exact'],5)])
 parts.append(tab('tab:all_lagged_dealer_cells','Complete conditional dealer replay; a limit event is not an observed market default.',['$S$','Leverage','Mode','Halts','Paths','Rate','Exact binomial reference'],rows))
 parts.append(r'\section{January Retrospective Forecast Reconstruction}'+'\n'+r'The existing authenticated January sample now has its own forecast computation. Quote OFI and the gap-reset EMA 120 retain the same 152 eligible date/gap segments and 844,621 baseline transitions. Regression lags split dates/gaps. Six initial training dates precede each of six expanding evaluation dates, January 15--20, 2023. All four lag horizons are retained; normalization and coefficients use training observations only. The one-second lag grid and protocol are retrospective, rather than an untouched holdout or preregistered selection. Positive mean reductions are predictive associations, with six serial dates and no multiple-comparison or causal guarantee.'+'\n')
 rows=[]
 january=load(HERE/'january_forecast_results.json')
 for lag,r in january['summary']['paired'].items():
  for target,v in r['variables'].items():
   ar=january['summary']['models']['AR'+lag]['equal_date_mean_MSE'][target]
   rows.append([lag,target,r['n_dates'],f'{ar:.7f}',f"{v['AR_minus_VAR_mean_loss']:.7f}",interval(v['date_t95']),f"{v['relative_mean_improvement_percent']:.5f}"])
 parts.append(tab('tab:january_forecast_all_lags','All existing-sample January AR-minus-VAR losses; scale is training SD.',['Lag sec','Target','Dates','AR MSE','Mean reduction','Date reference','Reduction percent'],rows))
 equity_source=load(HERE/'submission_completion/equity_source_sensitivity.json')
 parts.append(r'\section{Equity Source Replay and Full Coverage}'+'\n'+r'The supplied CSV now reproduces byte for byte from ten independently retrieved normalized DecPre files using its preserved transformation. The six-largest-jump/five-interval rule omits the endpoint: it retains272,941 of394,337 events and drops121,396(30.7848percent). Legacy labels2--5 map to different inferred price blocks across days and are not authenticated company identities. A full-coverage sensitivity uses four largest finite price gaps plus an explicit endpoint, retaining all394,337 events in50 eligible day/block sessions. The event EMA100, burn500 and preserved decimal conversion remain explicit. All50 fits are independently reconstructed using decimal GCD, manual OFI/EMA and QR. The smallest selected gap is at least12.3055 times the largest omitted gap; this supports a declared partition, not a company map. Primary Fairdata archive byte identity and original physical normalization denominators remain unverified.'+'\n')
 rows=[]
 for block,v in equity_source['by_block'].items():
  for metric in ['Q','S']:rows.append([block,metric,v['n_raw'],v['n_sessions'],f"{v[metric]['mean']:.7f}",interval(v[metric]['date_t95'])])
 parts.append(tab('tab:equity_full_source','All full-coverage blocks and ten-day references; block1 Q spans zero.',['Block','Index','Events','Sessions','Mean','Date reference'],rows))
 parts.append(r'''\section{Financial Information and Publication Boundaries}
The main manuscript and central-result review packet now specify the physical input, positive price-response geometry, refreshed average-book execution, actual cash/inventory and distinct counterparty/probe-trader funding. A restricted noisy-price observer faces the stated resource orders. Exact marked equity and naturally excited price blocks change that experiment. These constructed financial models do not authenticate actual impact, queue fills, funding, collateral, positions or a financial data-noise contract for the recorded samples.

Existing learned-policy aggregate outputs are audited without new training: their asserted high R-squared conclusion is contradicted by the saved values and constant-action substitution, and the source lacks a sufficient checkpoint chain and genuine queue-fill calibration. The current manuscript uses none of those outputs as an operational safety certificate.

The historical flash-crash script assigns or simulates its coefficients, contains no historical TAQ/account ingest and changes several counterfactual inputs at once. Its underlying research question remains open, and its original outputs are retained as illustrations. Original equity archive acquisition, representation/stock mapping, real financial calibration, defensible causal inference where needed and independent specialist assessment remain publication gates.

Named source/evidence receipts accompany this supplement; a computation, source hash or clean PDF is not scientific or publication closure.
\end{document}
''')
 body='\n'.join(parts)
 body=body.replace('original archive acquisition and local stock/day transformation authentication remain open','independent normalized-file transformation replay matches the supplied CSV, while original archive hash and company/unit authentication remain open')
 body=body.replace('Original equity archive acquisition, representation/stock mapping, real financial calibration','Original equity archive byte authentication, company/unit mapping, real financial calibration')
 for old,new in {'retains272,941 of394,337':'retains 272,941 of 394,337','drops121,396(30.7848percent)':'drops 121,396 (30.7848 percent)','labels2--5':'labels 2--5','all394,337':'all 394,337','in50':'in 50','EMA100':'EMA 100','burn500':'burn 500','All50':'All 50','least12.3055':'least 12.3055','block1':'block 1'}.items():body=body.replace(old,new)
 target=HERE/'Machine_Markets_Current_Evidence_Supplement_20261008.tex';target.write_text(body);print(target)
if __name__=='__main__':run()
