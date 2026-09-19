#!/usr/bin/env python3
"""Primary fixed-budget, audited-rate inference study; no latent-state access."""
from pathlib import Path
import sys,json,hashlib,time
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.linear import simulate_linear
from src.inference import reconstruct_terminal,terminal_interval
from src.audit import make_contract,validate_contract,tail_envelope

def run(out:Path):
    out.mkdir(parents=True,exist_ok=True);data=out.parent/'data';data.mkdir(exist_ok=True)
    digest=hashlib.sha256((ROOT/'src/linear.py').read_bytes()).hexdigest();rows=[];XX=[];yy=[];offsets=[];pos=0;contracts=[];tic=time.time()
    for mid,(slow,G) in enumerate((s,g) for s in [.002,.02,.1] for g in [.7,.95,1.05,1.3]):
        q=.6*G*np.array([.6,.4]);rates=[.5,slow];truth=.4+sum(q)
        c=make_contract(rates,digest);assert validate_contract(c,digest)['eligible'];contracts.append(dict(c,model_id=mid))
        for steps in [16,64]:
            for design_i,design in enumerate(['impulse','roundtrips']):
                for N in [32,128,512]:
                    for rep in range(20):
                        seed=50000000+mid*100000+steps*1000+design_i*10000+N*20+rep
                        sim=simulate_linear(.4,q,rates,.02,N,steps,seed,design)
                        X,y=reconstruct_terminal(sim['prices'],rates)
                        r=terminal_interval(X,y);decision=r['label']
                        row={'panel_id':len(rows),'model_id':mid,'slow':slow,'normalized_G':G,'truth_a_plus_Q':truth,'true_stable':truth<1,
                             'steps':steps,'design':design,'episodes':N,'replicate':rep,'seed':seed,
                             **{k:v for k,v in r.items() if k!='coefficient_estimates'},
                             'covered':r['lower']<=truth<=r['upper'], 'definite':decision in ('stable','unstable'),
                             'wrong':(decision=='stable' and truth>1) or (decision=='unstable' and truth<1),
                             'gross_probe_volume_per_episode':float(sim['gross_volume'].mean()),
                             'probe_squared_energy_per_episode':float(sim['squared_energy'].mean()),
                             'mean_peak_probe_inventory':float(sim['peak_probe_inventory'].mean())}
                        rows.append(row);XX.append(X);yy.append(y);offsets.append([pos,pos+N]);pos+=N
                        if steps==64 and N==128 and rep==0:
                            np.savez_compressed(data/f'linear_public_{mid}_{design}.npz',prices=sim['prices'],probes=sim['probes'],rates=np.array(rates),seed=seed)
        print('linear model',mid,'panels',len(rows),flush=True)
    df=pd.DataFrame(rows);df.to_csv(out/'linear_panels.csv',index=False)
    np.savez_compressed(data/'linear_terminal_rows.npz',X=np.concatenate(XX),y=np.concatenate(yy),offsets=np.array(offsets))
    agg=df.groupby(['steps','design','episodes']).agg(panels=('panel_id','size'),covered=('covered','sum'),definite=('definite','sum'),wrong=('wrong','sum'),median_se=('se','median'),median_condition=('condition_number_scaled','median')).reset_index()
    agg['coverage']=agg.covered/agg.panels;agg['definite_rate']=agg.definite/agg.panels
    agg.to_csv(out/'linear_budget_summary.csv',index=False)
    df.groupby(['slow','steps','design','episodes']).agg(panels=('panel_id','size'),definite=('definite','sum'),wrong=('wrong','sum'),covered=('covered','sum')).reset_index().to_csv(out/'linear_by_rate.csv',index=False)
    (out.parent/'configs/audit_contracts.json').write_text(json.dumps(contracts,indent=2))
    (out/'linear_summary.json').write_text(json.dumps({'panels':len(df),'independent_episode_rows':pos,'covered':int(df.covered.sum()),'wrong':int(df.wrong.sum()),'definite':int(df.definite.sum()),'runtime_seconds':time.time()-tic,'source_digest':digest},indent=2))
    tails=[]
    for rate in [.002,.02,.1]:
        for h in [16,64,256]:tails.append({'Qmax':1,'rate_floor':rate,'horizon':h,'tail_bound':tail_envelope(1,rate,h)})
    pd.DataFrame(tails).to_csv(out/'tail_envelopes.csv',index=False)
    print(agg.to_string(index=False))

if __name__=='__main__':run(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'results')
