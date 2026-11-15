"""Frozen offline diagnostic grid for the UNREGISTERED empirical candidate.

200 independent replications per cell; 30 symbols, 60 days of half-hour bars.
Population incremental R2 is g for R[t+1]=rho*R[t]+beta*u[t]+epsilon[t+1],
where the report's first difference reveals u[t] and beta^2=g/(1-rho^2-g).
The baseline includes R[t]; both shocks have marginal variance one.
Scenarios test common shocks, persistence, heavy tails, and missing reports.

Predeclared diagnostic criteria (not a certification of empirical validity):
  g=0 or .01: Wilson 95% lower limit on the correct verdict probability >= .8;
  g=.005: Wilson 95% upper limit on either incorrect decisive verdict <= .15.
The .0025 cell is descriptive. Failed cells are reported without retuning.
The known g is the population-oracle increment. A finite fitted learner has a
different conditional risk; discrepancies diagnose both training effects and
inference. This grid is not a size theorem for that conditional estimand.
"""
from pathlib import Path
import importlib.util
import json
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('candidate',HERE.parent/'candidate_p1f_executor.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
REPS=200
SCENARIOS=[('iid',0.,0.,False,False),('persistent_common',.6,.65,False,False),
           ('heavy_common',.6,.65,True,False),('missing_reports',.6,.65,False,True)]
GAINS=[0.,.0025,.005,.01]

def wilson(k,n):
    z=1.959963984540054;p=k/n;den=1+z*z/n
    centre=(p+z*z/(2*n))/den
    half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [float(centre-half),float(centre+half)]

def world(rho,common,heavy,missing,g,seed):
    rng=np.random.default_rng(seed); T,S,burn=2880,30,500; nt=T+burn
    def shock():
        draw=lambda shape:rng.standard_t(5,size=shape)*np.sqrt(3/5) if heavy else rng.normal(size=shape)
        return np.sqrt(common)*draw((nt,1))+np.sqrt(1-common)*draw((nt,S))
    u,eps=shock(),shock(); beta=np.sqrt(g/(1-rho*rho-g))
    R=np.zeros((nt,S))
    for t in range(1,nt):R[t]=rho*R[t-1]+beta*u[t-1]+eps[t]
    N=np.stack([np.cumsum(u,axis=0),np.cumsum(shock(),axis=0),np.cumsum(shock(),axis=0)],-1)
    R=R[burn:];N=N[burn:]
    if missing:
        # One whole common day in each half, plus one symbol-specific report day.
        for day in (10,43):N[day*48:(day+1)*48]=np.nan
        for s in range(S):
            day=int(rng.integers(0,60));N[day*48:(day+1)*48,s]=np.nan
    return R,rng.normal(size=(T,S)),rng.normal(size=(T,S)),N

def main():
    results=[]
    for sid,(name,rho,common,heavy,missing) in enumerate(SCENARIOS):
        for gid,g in enumerate(GAINS):
            counts={k:0 for k in ['irrelevant','relevant','inconclusive']}; estimates=[];coverage=0
            for rep in range(REPS):
                seed=700000+10000*sid+1000*gid+rep
                r=ex.evaluate(*world(rho,common,heavy,missing,g,seed),.005,1440,2879,
                              rng=np.random.default_rng(seed+99),boot=2000)
                counts[r['verdict']]+=1;estimates.append(r['dR2'])
                coverage+=r['lower90']<=g<=r['upper90']
            intervals={k:wilson(v,REPS) for k,v in counts.items()}
            passed=None
            if g==0:passed=intervals['irrelevant'][0]>=.8
            if g==.01:passed=intervals['relevant'][0]>=.8
            if g==.005:passed=max(intervals['irrelevant'][1],intervals['relevant'][1])<=.15
            row=dict(scenario=name,population_incremental_R2=g,replications=REPS,verdict_counts=counts,
                     verdict_probability_CI95=intervals,mean_estimate=float(np.mean(estimates)),
                     central80_coverage=coverage/REPS,coverage_CI95=wilson(coverage,REPS),diagnostic_pass=passed)
            results.append(row)
            print(json.dumps(row,allow_nan=False),flush=True)
            (HERE/'calibration_grid_results.json').write_text(json.dumps({'complete':False,'rows':results},indent=2)+'\n')
    out={'complete':True,'replications':len(SCENARIOS)*len(GAINS)*REPS,
         'all_diagnostic_criteria_pass':all(r['diagnostic_pass'] is not False for r in results),'rows':results}
    (HERE/'calibration_grid_results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('COMPLETE; all diagnostic criteria pass:',out['all_diagnostic_criteria_pass'],flush=True)

if __name__=='__main__':main()
