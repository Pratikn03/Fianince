#!/usr/bin/env python3
from pathlib import Path
import sys,json,time,hashlib,argparse
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.finance import market_panel
from src.inference import binomial_interval,label_probability

def run(out,max_new=8):
    out.mkdir(exist_ok=True,parents=True);data=out.parent/'data';data.mkdir(exist_ok=True)
    rows=[];setting_summary=[];audits=[];counts=[];tic=time.time();new_count=0
    checkpoint=out/'finance_checkpoints';checkpoint.mkdir(exist_ok=True)
    source_hash=hashlib.sha256((ROOT/'src/finance.py').read_bytes()).hexdigest()
    settings=[(g,s,r,j) for g in [.7,1.3] for s in [.02,.1] for r in ['unlimited','ample','tight'] for j in [0.,-2.]]
    for sid,(g,s,r,shock) in enumerate(settings):
        cache=checkpoint/f'{sid:02d}.json'
        if cache.exists():
            cached=json.loads(cache.read_text())
            if cached['source_sha256']!=source_hash:raise RuntimeError('stale checkpoint: remove finance_checkpoints to rerun')
            setting_summary.append(cached['setting']);audits.append(cached['audit']);rows.extend(cached['rows']);continue
        if new_count>=max_new:
            print('CHECKPOINT: rerun this command to continue; completed',len(setting_summary),'of',len(settings),flush=True);return
        row_start=len(rows)
        # Identical exogenous tapes for each funding counterfactual, independent across batches.
        seed=80000000+int(g*100)*10000+int(s*1000)*10+int(abs(shock))*100
        result=market_panel(g,s,r,shock,20480,seed)
        dat={k:v for k,v in result.items() if isinstance(v,np.ndarray)}
        np.savez_compressed(data/f'finance_episodes_{sid}.npz',**dat)
        n=int(result['event'].sum());lo,hi=binomial_interval(n,20480)
        setting_summary.append({'setting_id':sid,'gain':g,'slow':s,'regime':r,'shock':shock,'episodes':20480,'events':n,'event_rate':n/20480,'probability_lower':lo,'probability_upper':hi,'margin_rate':float(result['margin'].mean()),'clip_rate':float(result['clipped'].mean()),'default_rate':float(result['default'].mean()),'halt_rate':float(result['halt'].mean()),'mean_drawdown':float(result['drawdown'].mean()),'mean_displacement':float(result['displacement'].mean()),'mean_probe_filled':float(result['probe_filled'].mean()),'mean_gross_volume':float(result['gross_volume'].mean()),'mean_rejected_volume':float(result['rejected_volume'].mean()),'mean_peak_leverage':float(result['peak_leverage'].mean()),'seed':seed})
        audits.append(dict(setting_id=sid,**result['audit']))
        events=result['event'].reshape(40,512)
        for rep in range(40):
            for N in [32,128,512]:
                count=int(events[rep,:N].sum());lower,upper=binomial_interval(count,N,.05/3)
                rows.append({'setting_id':sid,'regime':r,'gain':g,'slow':s,'shock':shock,'panel':rep,'episodes':N,'events':count,'lower':lower,'upper':upper,'label':label_probability(lower,upper), 'alpha_per_look':.05/3})
        if sid in [0,5,17,23]:
            example=market_panel(g,s,r,shock,16,seed+1,save_paths=True)
            np.savez_compressed(data/f'finance_ledger_example_{sid}.npz',prices=example['prices'],ledger=example['ledger'])
        cache.write_text(json.dumps({'source_sha256':source_hash,'setting':setting_summary[-1],'audit':audits[-1],'rows':rows[row_start:]},indent=2))
        new_count+=1
        print('finance setting',sid,r,shock,'risk',n/20480,'clipped',result['clipped'].mean(),flush=True)
    df=pd.DataFrame(rows);df.to_csv(out/'financial_budget_panels.csv',index=False)
    ss=pd.DataFrame(setting_summary);ss.to_csv(out/'financial_settings.csv',index=False)
    pd.DataFrame(audits).to_csv(out/'financial_accounting_audits.csv',index=False)
    df.groupby(['episodes','label']).size().unstack(fill_value=0).to_csv(out/'financial_budget_summary.csv')
    pairs=[]
    for g in [.7,1.3]:
        for s in [.02,.1]:
            for shock in [0.,-2.]:
                sub=ss[(ss.gain==g)&(ss.slow==s)&(ss.shock==shock)]
                base=sub[sub.regime=='unlimited'].iloc[0]
                z0=np.load(data/f'finance_episodes_{int(base.setting_id)}.npz')
                for regime in ['ample','tight']:
                    compare=sub[sub.regime==regime].iloc[0];z1=np.load(data/f'finance_episodes_{int(compare.setting_id)}.npz')
                    delta=z1['event'].astype(float)-z0['event'].astype(float)
                    # Hoeffding interval for mean of independent bounded [-1,1] paired differences.
                    radius=2*np.sqrt(np.log(2/.05)/(2*len(delta)))
                    pairs.append({'gain':g,'slow':s,'shock':shock,'regime':regime,'risk_difference':float(delta.mean()),'lower':max(-1,float(delta.mean()-radius)),'upper':min(1,float(delta.mean()+radius)),'episodes':len(delta)})
    pd.DataFrame(pairs).to_csv(out/'paired_funding_comparison.csv',index=False)
    summary={'settings':len(ss),'simulated_setting_episodes':20480*len(ss),'unique_exogenous_episode_tapes':20480*len(ss)//3,'budget_rows':len(df),'setting_panels':40*len(ss),'unique_exogenous_panels':40*len(ss)//3,'simultaneous_planned_looks':3,'risk_threshold':.05,'runtime_seconds':time.time()-tic,'max_cash_error':max(x['max_cash_error'] for x in audits),'max_share_error':max(x['max_share_error'] for x in audits),'max_fresh_trade_violation':max(x['max_fresh_trade_violation'] for x in audits),'clipped_orders':sum(x['clipped_orders'] for x in audits),'margin_calls':sum(x['margin_calls'] for x in audits),'market_halts':sum(x['new_dealer_halts'] for x in audits)}
    (out/'financial_summary.json').write_text(json.dumps(summary,indent=2));print(summary)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=ROOT/'results');parser.add_argument('--max-new',type=int,default=8);args=parser.parse_args()
    if args.max_new<1:parser.error('--max-new must be positive')
    run(args.out,args.max_new)
