#!/usr/bin/env python3
"""Declared post-primary budget exploration, assumption failures and price-law limits."""
from pathlib import Path
import csv,json,time
import numpy as np
from scipy.stats import norm
from src.market import MarketConfig,simulate,impulse,joint_matrix
from src.observable import response_intervals,recurrence_interval
from run_study import write_csv

root=Path(__file__).resolve().parent

def evaluate(cfg,R,delta,seed,floor,confounded=False,audit=True):
    sim=simulate(cfg,R,delta,66,seed,audit=audit,confounded=confounded)
    obs=response_intervals(**sim['public'])
    ans=recurrence_interval(obs['lower'][:65],obs['upper'][:65],floor)
    target=cfg.a+sum(cfg.q);truth='stable' if target<1 else 'unstable'
    b=impulse(cfg.a,np.array(cfg.q),np.array(cfg.rates),cfg.impact,66)
    return dict(lower=ans['lower'],upper=ans['upper'],label=ans['label'],
        reference_linear_S=target,reference_linear_label=truth,
        disagreement=bool(ans['label'] in ['stable','unstable'] and ans['label']!=truth),
        linear_response_covered=bool(np.all((obs['lower']<=b)&(b<=obs['upper']))),
        measured_initial_impact=float(obs['estimate'][0]),**sim['audit'])

start=time.time();controls=[]
for setting in ['valid_reference','false_rate_floor','confounded_assignment','nonlinear_impact']:
    for rep in range(20):
        cfg=MarketConfig(.4,.02,(.5,.1),(.252,.168))
        floor=.1;confounded=False
        if setting=='false_rate_floor': cfg=MarketConfig(.4,.02,(.5,1e-5),(.42,.24))
        if setting=='confounded_assignment':
            cfg=MarketConfig(.4,.02,(.5,.1),(.252,.168),noise_flow_sd=2.)
            confounded=True
        if setting=='nonlinear_impact': cfg=MarketConfig(.4,.02,(.5,.1),(.252,.168),nonlinear_capacity=1.)
        res=evaluate(cfg,4096,4.,451000+rep,floor,confounded)
        controls.append(dict(setting=setting,replicate=rep,probe_shares=4.,**res))
write_csv(root/'results'/'negative_controls.csv',controls)

# Exact homogeneity failure: no random noise, no zero-state access by estimator.
nonlinear=[]
for amp in [.25,1.,4.]:
    cfg=MarketConfig(.4,.02,(.5,.1),(.252,.168),noise_flow_sd=0.,quote_noise_sd=0.,initial_memory_sd=0.,nonlinear_capacity=1.)
    sim=simulate(cfg,8,amp,66,914,audit=True);obs=response_intervals(**sim['public'])
    nonlinear.append({'amplitude':amp,'initial_impact':float(obs['estimate'][0]),
                      'theoretical_initial_impact':float(.02*np.tanh(amp)/amp)})
(root/'results'/'nonlinear_scaling.json').write_text(json.dumps(nonlinear,indent=2))

# New common-covariance PRICE observation subexperiment, not the legacy kernel law.
R=1024;delta=4.;sigma=.002;kappa=.02;a=.4;H=64
limit=[]
for eta in [1e-7,1e-6,1e-5,1e-4,.001,.01]:
    rates=np.array([.5,eta]);q0=.6*np.array([.7,.2]);q1=.6*np.array([.7,.4])
    b0=impulse(a,q0,rates,kappa,H+1);b1=impulse(a,q1,rates,kappa,H+1)
    d2=float(R*delta**2*np.sum((b1-b0)**2)/sigma**2);d=np.sqrt(d2)
    tv=2*norm.cdf(d/2)-1
    limit.append({'slow_rate':eta,'R':R,'pulse_shares':delta,'noise_sd':sigma,'last_lag':H,
                  'stable_G':.9,'unstable_G':1.1,'distance_squared':d2,
                  'oracle_error':float(norm.cdf(-d/2)),
                  'max_coverage_at_5pct_unconditional_error':float(min(1,.1+tv))})
(root/'results'/'price_observation_limits.json').write_text(json.dumps(limit,indent=2))
# Likelihood-ratio Monte Carlo, using sufficient 1D Gaussian score. Checks formula.
z=np.random.default_rng(16180339).normal(size=100000)
d=np.sqrt(limit[2]['distance_squared']);emp=float(np.mean(z>d/2))
(root/'results'/'price_limit_mc.json').write_text(json.dumps({'eta':1e-5,'draws':len(z),'empirical_error':emp,'exact_error':limit[2]['oracle_error']},indent=2))

budgets=[]
for cid,(slow,G) in enumerate((s,g) for s in [.002,.02,.1] for g in [.7,.95,1.05,1.3]):
    cfg=MarketConfig(.4,.02,(.5,slow),tuple(.6*G*np.array([.6,.4])))
    for R in [8192,32768]:
        for rep in range(5):
            res=evaluate(cfg,R,4.,271828+cid*100000+R+rep,slow)
            budgets.append(dict(configuration=cid,rate_floor=slow,G=G,probe_shares=4.,replicate=rep,**res))
    print('budget model',cid+1,'seconds',round(time.time()-start,1),flush=True)
write_csv(root/'results'/'budget_extension.csv',budgets)
summary={'control_panels':len(controls),'control_episodes':sum(x['episodes'] for x in controls),
         'budget_panels':len(budgets),'budget_episodes':sum(x['episodes'] for x in budgets),
         'budget_wrong':sum(x['disagreement'] for x in budgets),'seconds':time.time()-start,
         'note':'Post-primary budget exploration; not pooled with frozen primary results.'}
(root/'results'/'extension_summary.json').write_text(json.dumps(summary,indent=2));print(summary)
