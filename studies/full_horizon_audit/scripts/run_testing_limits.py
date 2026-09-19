#!/usr/bin/env python3
from pathlib import Path
import sys,json,csv,math
import numpy as np
from scipy.stats import norm
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mmfh.testing_limits import squared_distance,oracle_error,total_variation,coverage_upper_bound
rows=[];draws_per_class=100000
for noise_id,rel in enumerate([.002,.02]):
    se=rel/math.sqrt(128)
    for ei,eta in enumerate([1e-5,1e-4,.001,.01,.1]):
        for hi,H in enumerate([4,16,64,256,1024,4096]):
            delta=.2;v=delta*eta*(1-eta)**np.arange(H)
            d2=squared_distance(delta,eta,H,se);direct=float(v@v)/se**2
            assert np.isclose(d2,direct,rtol=1e-10)
            d=math.sqrt(d2);rng=np.random.default_rng(np.random.SeedSequence([20260918,noise_id,ei,hi,733]))
            # Standardized likelihood-ratio sufficient statistic: all H coordinates
            # are projected onto their known mean-difference direction.
            x0=rng.normal(-d/2,1,draws_per_class);x1=rng.normal(d/2,1,draws_per_class)
            wrong=int(np.count_nonzero(x0>0)+np.count_nonzero(x1<=0));n=2*draws_per_class
            theory=oracle_error(d2);measured=wrong/n
            tolerance=6*math.sqrt(max(theory*(1-theory),1/n)/n)+2/n
            rows.append({'relative_noise':rel,'eta':eta,'H':H,'delta_gain':delta,
                         'squared_distance':d2,'oracle_error':theory,'empirical_error':measured,
                         'wrong':wrong,'draws':n,'within_6sigma_tolerance':abs(measured-theory)<=tolerance,
                         'total_variation':total_variation(d2),
                         'coverage_upper_bound_at_5pct_error':coverage_upper_bound(d2,.05),
                         'infinite_horizon_oracle_error':oracle_error(squared_distance(delta,eta,None,se))})
with (ROOT/'results/testing_limits.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
summary={'configurations':len(rows),'projected_LRT_simulations':sum(r['draws'] for r in rows),
         'all_formula_checks_passed':True,'all_simulations_within_6sigma_tolerance':all(r['within_6sigma_tolerance'] for r in rows),
         'maximum_absolute_error_discrepancy':max(abs(r['oracle_error']-r['empirical_error']) for r in rows),
         'example':[r for r in rows if r['relative_noise']==.02 and r['eta']==1e-5 and r['H']==256][0],
         'not_independent_real_market_observations':True,
         'simulation_uses_exact_one_dimensional_sufficient_statistic':True}
(ROOT/'results/testing_limits_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
# Reproduce the illustrative necessary observation budget from the paper.
eta=1e-5;H=256;delta=.2;sigma=.02;target=.05
factor=-math.expm1(2*H*math.log1p(-eta))
required=math.ceil(4*sigma**2*(2-eta)*norm.ppf(1-target)**2/(delta**2*eta*factor))
required_infinite=math.ceil(4*sigma**2*(2-eta)*norm.ppf(1-target)**2/(delta**2*eta))
assert oracle_error(squared_distance(delta,eta,H,sigma/math.sqrt(required)))<=target
assert oracle_error(squared_distance(delta,eta,H,sigma/math.sqrt(required-1)))>target
budget={'normalized_single_probe_sd':sigma,'eta':eta,'gain_difference':delta,'H':H,
        'target_oracle_balanced_error':target,'necessary_independent_replicates_at_H':required,
        'necessary_independent_replicates_infinite_H':required_infinite,
        'caveat':'Necessary for forced testing this known pair in the stated pulse-response experiment, not a sufficient practical design or a real-market cost estimate.'}
(ROOT/'results/measurement_budget_example.json').write_text(json.dumps(budget,indent=2)+'\n')
