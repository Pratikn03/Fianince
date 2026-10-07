"""Full-panel summaries require all original units; never summarize partial recovery."""
from pathlib import Path
import json,sys
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REV=ROOT/'research_extension/paper_revision_20261006'
sys.path.insert(0,str(REV));from revise_evidence import ols

def date_summary(frame,metrics):
    dates=frame.groupby('date')[metrics].mean();out={'n_dates':len(dates)}
    rng=np.random.default_rng(20261006)
    for key in metrics:
        v=dates[key].to_numpy();mean=float(v.mean());se=float(stats.sem(v));crit=float(stats.t.ppf(.975,len(v)-1));intervals={}
        for block in [2,4,8]:
            draws=[]
            for _ in range(500):
                starts=rng.integers(0,len(v),size=int(np.ceil(len(v)/block)))
                index=np.concatenate([(s+np.arange(block))%len(v) for s in starts])[:len(v)];draws.append(v[index].mean())
            intervals[str(block)]=np.quantile(draws,[.025,.975]).tolist()
        out[key]={'mean':mean,'date_t95':[mean-crit*se,mean+crit*se],'circular_date_block_bootstrap95':intervals}
    return out

def fee(frame):
    d=frame[frame.year==2022].copy();post=(d.date>='2022-07-08').to_numpy(float);treat=(d.symbol=='BTCUSDT').to_numpy(float);X=np.column_stack([np.ones(len(d)),treat,post,treat*post]);result={'n':len(d),'scope':'Restored original dates; corrected observed-flow diagnostic; descriptive association, one treated asset, no randomized assignment or defended parallel counterfactual trends'}
    for dep in ['Q','S']:
        fits={}
        for kind,groups in [('classical',None),('asset_cluster',d.symbol.to_numpy()),('date_cluster',d.date.to_numpy())]:
            b,se,df,cov=ols(d[dep].to_numpy(),X,groups);crit=stats.t.ppf(.975,df)
            fits[kind]={'beta':float(b[3]),'se':float(se[3]),'df':df,'p_t':float(2*stats.t.sf(abs(b[3]/se[3]),df)),'ci95':[float(b[3]-crit*se[3]),float(b[3]+crit*se[3])]}
        result[dep]=fits
    v=result['Q']['date_cluster'];margin=.007;result['Q']['equivalence_date_cluster']={'margin':margin,'p_tost':float(max(stats.t.sf((v['beta']+margin)/v['se'],v['df']),stats.t.sf((margin-v['beta'])/v['se'],v['df'])))}
    btc=d[d.symbol=='BTCUSDT'];pre=btc[btc.date<'2022-07-08'].volume.mean();post=btc[btc.date>='2022-07-08'].volume.mean()
    result['measured_btc_quote_volume']={'pre_sampled_day_mean':float(pre),'post_sampled_day_mean':float(post),'percentage_change':float(100*(post/pre-1)),'scope':'Recorded quote-volume totals after first-row timestamp deduplication; descriptive sampled-day comparison, not fee-induced causal growth'}
    piv=d.pivot(index='date',columns='symbol',values='Q');gap=piv.BTCUSDT-piv.drop(columns='BTCUSDT').mean(axis=1);base='2022-06-24'
    result['dated_Q_contrasts']=[{'date':date,'gap':float(g),'relative_to_june24':float(g-gap.loc[base])} for date,g in gap.items()]
    return result

def run():
    data=json.loads((HERE/'original_panel_reproduction.json').read_text());rows=data['rows']
    if len(rows)!=768 or any(r['status']!='RAW_REPRODUCED' for r in rows):raise RuntimeError('Full original-panel raw reproduction has not passed; do not use partial summary')
    if len({(r['symbol'],r['date']) for r in rows})!=768:raise ValueError('Duplicate study units')
    old=json.loads((ROOT/'results/provenance/binance_panel_results.json').read_text())['results'];old_lookup={(r['symbol'],r['date']):r for r in old}
    loop_errors=[]
    for r in rows:
        loop=r['legacy']['Q']/(1-r['legacy']['J11']);expected=old_lookup[r['symbol'],r['date']]['L']
        if not np.isclose(loop,expected,atol=1e-10,rtol=1e-10):raise ValueError('Legacy loop identity discrepancy')
        loop_errors.append(abs(loop-expected))

    summaries={};frames={}
    for variant in ['legacy','observed','raw_return']:
        frame=pd.DataFrame([dict(symbol=r['symbol'],date=r['date'],year=r['year'],volume=r['total_quote_volume_deduplicated'],**{k:v for k,v in r[variant].items() if k!='segments'}) for r in rows]);frames[variant]=frame
        metrics=['Q','S']+(['Q30'] if variant!='raw_return' else [])
        summaries[variant]=date_summary(frame,metrics);summaries[variant]['share_Q_positive']=float((frame.Q>0).mean());summaries[variant]['max_rho']=float(frame.rho.max() if variant=='legacy' else frame.max_rho.max())
        summaries[variant]['by_asset']=frame.groupby('symbol')[metrics].mean().to_dict('index')
    missing=[{'symbol':r['symbol'],'date':r['date'],'missing_seconds':r['missing_seconds'],'duplicate_seconds':r['duplicate_seconds'],'conflicting_duplicate_seconds':r['conflicting_duplicate_seconds'],'primary_segments':r['observed']['n_segments']} for r in rows if r['missing_seconds'] or r['duplicate_seconds']]
    report={'scope':'Independent current-official-archive reproduction of all original768 study units; exact historical download bytes were not preserved; causal learning and structural MD/heteroskedastic claims are not certified','max_legacy_loop_ratio_error':max(loop_errors),'n_asset_days':768,'n_dates':len({r['date'] for r in rows}),'n_raw_rows':sum(r['raw_rows'] for r in rows),'n_unique_seconds':sum(r['unique_seconds'] for r in rows),'n_legacy_states':sum(r['legacy']['n_obs'] for r in rows),'n_primary_transitions':sum(r['observed']['n_transitions'] for r in rows),'n_primary_segments':sum(r['observed']['n_segments'] for r in rows),'missingness':missing,'summaries':summaries,'fee_observed':fee(frames['observed']),'uncertainty_scope':'Date means/intervals and exploratory circular block sensitivity. Blocks of2/4/8 sampled dates are not a proof of serial independence or an external preregistration.'}
    (HERE/'restored_panel_summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['n_asset_days','n_raw_rows','n_unique_seconds','n_primary_transitions','n_primary_segments']},indent=2));print('Observed Q',summaries['observed']['Q']['mean'],'return Q',summaries['raw_return']['Q']['mean']);print('Observed fee',report['fee_observed']['Q']['date_cluster'])
if __name__=='__main__':run()
