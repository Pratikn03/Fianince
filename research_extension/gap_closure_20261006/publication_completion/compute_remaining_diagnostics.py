"""Declared retrospective diagnostics on existing recorded data, no new data/training.

Inference is exploratory: date t references and Gaussian cone simulation are
not certified finite-sample market tests. Output does not attribute algorithms.
"""
from pathlib import Path
import sys, json, hashlib
import numpy as np
import pandas as pd
from scipy import stats, optimize, linalg

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REV=ROOT/'research_extension/paper_revision_20261006'
sys.path[:0]=[str(ROOT),str(REV)]
from revise_evidence import series
from empirical_pipeline.feedback_var import var1, q_long_memory_robust

PROTOCOL=dict(assets=['BTC','ETH','ADA'],delta_seconds=10,ema_seconds=300,
              lags_bars=[1,5,15,30,60,90],kernel_taps=6,permutations=199,
              cone_draws=1999,seed=20261008,
              scope='Existing recorder data, retrospective diagnostic. No random treatment, algorithm attribution, or structural cone interpretation.',
              permutation='Fixed-point-free whole-date flow relabelling; longest continuous segment per date; position aligned and truncated to shorter length; comparison mean observed Q; finite simulated rank, not a randomized-treatment p value.',
              cone='Negative orthant for observable six-tap regression coefficients, a superset of the negative Hausdorff cone. Gaussian least-favourable vertex simulation with sample date-mean covariance. This is not a finite-sample certificate or a full continuous-cone estimator.',
              aggregation='Transition-weighted segment estimates within date, equal-weight dates, Student t interval. Sampled-date independence unproved.')

def interval(v):
    v=np.asarray(v);se=float(stats.sem(v));c=stats.t.ppf(.975,len(v)-1)
    return dict(n_dates=len(v),mean=float(v.mean()),se=se,ci95=[float(v.mean()-c*se),float(v.mean()+c*se)])

def kernel(x,f,K):
    n=len(x);idx=np.arange(K,n)
    X=np.column_stack([np.ones(len(idx))]+[x[idx-1-j] for j in range(K)])
    return np.linalg.lstsq(X,f[idx],rcond=None)[0][1:]

def run():
    HERE.mkdir(exist_ok=True)
    (HERE/'diagnostic_protocol.json').write_text(json.dumps(PROTOCOL,indent=2)+'\n')
    report={'protocol':PROTOCOL,'assets':{}}
    segment_records=[]
    for asset in PROTOCOL['assets']:
        p=ROOT/'empirical_pipeline/cache'/f'{asset}_1sec_core_v2dedup.pkl'
        frame=series(pd.read_pickle(p));days={};lags={L:{} for L in PROTOCOL['lags_bars']};taps={}
        lead={}
        for (day,seg),g in frame.groupby(['day','segment']):
            if len(g)<500:continue
            name=str(day.date());x=g.x.to_numpy();f=g.flow.to_numpy();n=len(x)-1
            days.setdefault(name,[]).append((x,f))
            taps.setdefault(name,[]).append((n,kernel(x,f,PROTOCOL['kernel_taps'])))
            for L in PROTOCOL['lags_bars']:
                fit=q_long_memory_robust(x,f,L)
                lags[L].setdefault(name,[]).append((n,fit['Q_L']))
                segment_records.append(dict(asset=asset,date=name,segment=int(seg),n=n,L_bars=L,**fit))
            lead.setdefault(name,[]).append((n-1,var1(x[:-1],f[1:])['Q']))
        agg=lambda entries: np.average([z[1] for z in entries],axis=0,weights=[z[0] for z in entries])
        lag_summary={str(L):dict(horizon_seconds=L*10,**interval([agg(v) for v in lags[L].values()])) for L in lags}
        # Whole-date exchangeability is an exploratory null assumption only.
        longest=[max(days[k],key=lambda z:len(z[0])) for k in sorted(days)]
        actual=float(np.mean([var1(x,f)['Q'] for x,f in longest]))
        rng=np.random.default_rng(PROTOCOL['seed']);ranks=[];permutation_indices=[]
        for _ in range(PROTOCOL['permutations']):
            perm=rng.permutation(len(longest))
            while np.any(perm==np.arange(len(perm))):perm=rng.permutation(len(longest))
            estimates=[]
            for i,j in enumerate(perm):
                x=longest[i][0];f=longest[j][1];n=min(len(x),len(f));estimates.append(var1(x[:n],f[:n])['Q'])
            ranks.append(float(np.mean(estimates)));permutation_indices.append(perm.tolist())
        b=np.array([agg(taps[k]) for k in sorted(taps)]);mean=b.mean(0);cov=np.cov(b,rowvar=False,ddof=1)/len(b)
        ev=np.linalg.eigvalsh(cov)
        if ev.min()<=0:raise ValueError('Date kernel covariance is not positive definite')
        chol=linalg.cholesky(cov,lower=True);W=linalg.solve_triangular(chol,np.eye(len(mean)),lower=True)
        # Negative orthant projection; nnls KKT checked on each projection.
        basis=-W
        def distance(y):
            w,res=optimize.nnls(basis,W@y,maxiter=500)
            gradient=basis.T@(basis@w-W@y)
            if gradient.min() < -1e-6*max(1,np.linalg.norm(W@y)):raise ValueError('NNLS KKT violation')
            return float(res*res)
        T=distance(mean);rng=np.random.default_rng(PROTOCOL['seed']+1)
        draws=[distance(chol@rng.standard_normal(len(mean))) for _ in range(PROTOCOL['cone_draws'])]
        cone_p=float((1+sum(t>=T for t in draws))/(len(draws)+1))
        report['assets'][asset]=dict(cache_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),n_dates=len(days),
            lag_summary=lag_summary,lead_flow=interval([agg(v) for v in lead.values()]),
            date_shuffle=dict(observed_longest_segment_Q=actual,simulated_means=ranks,
                              permutation_indices=permutation_indices,
                              two_sided_rank_fraction=float((1+sum(abs(r)>=abs(actual) for r in ranks))/(1+len(ranks)))),
            kernel=dict(date_coefficients=b.tolist(),date_names=sorted(taps),mean=mean.tolist(),mean_covariance=cov.tolist(),
                        negative_orthant_statistic=T,gaussian_vertex_rank=cone_p,covariance_eigenvalues=ev.tolist()))
        print(asset,'remaining diagnostics complete',flush=True)
        (HERE/'remaining_diagnostics.json').write_text(json.dumps(report,indent=2)+'\n')
    pd.DataFrame(segment_records).to_csv(HERE/'lag_segment_estimates.csv',index=False)

if __name__=='__main__':run()
