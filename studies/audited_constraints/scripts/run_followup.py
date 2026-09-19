#!/usr/bin/env python3
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
from scipy.stats import binomtest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.linear import simulate_linear
from src.inference import variable_terminal,terminal_interval,binomial_interval
from src.finance import market_panel

def main(out):
    data=out.parent/'data';rows=[];XX=[];yy=[];offset=[];pos=0
    for mid,(slow,G) in enumerate((s,g) for s in [.002,.02,.1] for g in [.7,.95,1.05,1.3]):
        for N in [32,128,512]:
            for rep in range(20):
                seed=130000000+mid*100000+N*30+rep
                sim=simulate_linear(.4,.6*G*np.array([.6,.4]),[.5,slow],.02,N,64,seed,'impulse')
                rng=np.random.default_rng(seed+9000000);T=np.tile([8,16,32,64],N//4);rng.shuffle(T)
                for design,tt in [('fixed64',np.full(N,64)),('diversified',T)]:
                    X,y=variable_terminal(sim['prices'],tt,[.5,slow]);z=terminal_interval(X,y);truth=.4+.6*G
                    rows.append({'row':len(rows),'model_id':mid,'slow':slow,'G':G,'truth':truth,'episodes':N,'replicate':rep,'seed':seed,'design':design,'mean_observations':float(tt.mean()),**{k:v for k,v in z.items() if k!='coefficient_estimates'},'definite':z['label'] in ['stable','unstable'],'wrong':(z['label']=='stable' and truth>1)or(z['label']=='unstable'and truth<1),'covered':z['lower']<=truth<=z['upper']})
                    XX.append(X);yy.append(y);offset.append([pos,pos+N]);pos+=N
                if rep==0 and N==128:
                    np.savez_compressed(data/f'endpoint_public_{mid}.npz',prices=sim['prices'],probes=sim['probes'],endpoints=T,rates=np.array([.5,slow]))
    df=pd.DataFrame(rows);df.to_csv(out/'endpoint_confirmation.csv',index=False)
    np.savez_compressed(data/'endpoint_terminal_rows.npz',X=np.concatenate(XX),y=np.concatenate(yy),offsets=np.array(offset))
    agg=df.groupby(['design','episodes']).agg(panels=('row','size'),definite=('definite','sum'),wrong=('wrong','sum'),covered=('covered','sum')).reset_index();agg['definite_rate']=agg.definite/agg.panels
    agg.to_csv(out/'endpoint_summary.csv',index=False)
    df.groupby(['slow','design','episodes']).agg(panels=('row','size'),definite=('definite','sum'),wrong=('wrong','sum'),covered=('covered','sum')).reset_index().to_csv(out/'endpoint_by_rate.csv',index=False)
    paired=[]
    for n in [32,128,512]:
        sub=df[df.episodes==n];A=sub[sub.design=='fixed64'].reset_index(drop=True);B=sub[sub.design=='diversified'].reset_index(drop=True)
        new=(~A.definite)&B.definite;lost=A.definite&(~B.definite);b=int(new.sum());c=int(lost.sum());p=float(binomtest(b,b+c,.5).pvalue) if b+c else 1.
        paired.append({'episodes':n,'new_definite':b,'lost_definite':c,'net_additional':b-c,'n_pairs':len(A),'mcnemar_p':p})
    order=np.argsort([p['mcnemar_p'] for p in paired]);prev=0
    for rank,idx in enumerate(order):
        val=min(1.,(3-rank)*paired[idx]['mcnemar_p']);prev=max(prev,val);paired[idx]['holm_p']=prev
    pd.DataFrame(paired).to_csv(out/'endpoint_paired_comparison.csv',index=False)
    print(agg.to_string(index=False));print(paired)
    stress=[]
    for sid,(g,s,j) in enumerate((g,s,j) for g in [.7,1.3] for s in [.02,.1] for j in [-2.,-10.]):
        result=market_panel(g,s,'tight',j,8192,17000000+sid*100,preloaded_dealer=True,shock_jitter=1.)
        n=int(result['event'].sum());lo,hi=binomial_interval(n,8192)
        row={'setting':sid,'gain':g,'slow':s,'mean_shock':j,'shock_sd':1.,'episodes':8192,'events':n,'event_rate':n/8192,'lower':lo,'upper':hi,'halt_rate':float(result['halt'].mean()),'default_rate':float(result['default'].mean()),'margin_rate':float(result['margin'].mean()),'mean_drawdown':float(result['drawdown'].mean()),**{k:v for k,v in result['audit'].items() if k not in ['episodes','steps','regime','preloaded_dealer','shock_jitter']}}
        stress.append(row);np.savez_compressed(data/f'dealer_stress_{sid}.npz',**{k:v for k,v in result.items() if isinstance(v,np.ndarray)})
    pd.DataFrame(stress).to_csv(out/'dealer_stress.csv',index=False)
    (out/'followup_summary.json').write_text(json.dumps({'confirmation_rows':len(df),'independent_confirmation_panels':len(df)//2,'independent_confirmation_episodes':pos//2,'confirmation_covered':int(df.covered.sum()),'confirmation_wrong':int(df.wrong.sum()),'dealer_stress_settings':len(stress),'dealer_stress_episodes':8192*len(stress),'primary_status':'post-primary held-out confirmation; no external preregistration'},indent=2))

if __name__=='__main__':main(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'results')
