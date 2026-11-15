"""Fixed-design Gaussian forecasting check; no tuning on evaluation outcomes.
The order, sample sizes, populations, seeds and tolerances are fixed in this file.
Evaluates excess risk through the error in predicting the known conditional mean.
This experiment is supporting simulation, not a proof of the AR theorem.
"""
from pathlib import Path
import json
import numpy as np

def simulate(length, rates, seed):
    rng=np.random.default_rng(seed)
    rates=np.asarray(rates); eta=1-rates
    x=np.zeros(length); means=np.zeros(length); states=np.zeros(2)
    eps=rng.normal(size=length)
    for t in range(1,length):
        means[t]=.3*x[t-1]+.1*states.sum()
        x[t]=means[t]+eps[t]
        states=rates*states+eta*x[t]
    return x,means

def main():
    burn, L, ntest, reps = 1500, 16, 1000, 48
    rows=[]
    for name,rates in [('separated',[.3,.6]),('close',[.44,.46])]:
        for T in (3000,9000):
            risks=[]
            for seed in range(reps):
                x,means=simulate(burn+T+ntest+L,rates,10000+seed)
                Z=np.lib.stride_tricks.sliding_window_view(x,L)[:-1]
                y=x[L:]; mu=means[L:]
                beta=np.linalg.lstsq(Z[burn:burn+T],y[burn:burn+T],rcond=None)[0]
                sl=slice(burn+T,burn+T+ntest)
                risks.append(float(np.mean((Z[sl]@beta-mu[sl])**2)))
            avg=float(np.mean(risks)); se=float(np.std(risks,ddof=1)/np.sqrt(reps))
            row=dict(population=name,T=T,L=L,replications=reps,excess_risk=avg,
                     monte_carlo_se=se,reference=L/T,ratio=avg/(L/T))
            assert .5 < row['ratio'] < 1.8
            rows.append(row); print(row,flush=True)
    for name in ('separated','close'):
        rr=[r for r in rows if r['population']==name]
        assert rr[1]['excess_risk'] < rr[0]['excess_risk']
    out=dict(status='PASS',design='fixed L; independent fixed seeds; no test-set hyperparameter choice',rows=rows)
    Path(__file__).with_name('forecast_check_results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')

if __name__=='__main__':main()
