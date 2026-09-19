#!/usr/bin/env python3
"""Internal cross-checks with alternate regression and LP calculations.
This is not independent external replication or peer review.
"""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from scipy.stats import t
from src.market import MarketConfig,simulate
from src.observable import recurrence_interval
from run_study import array_hash
root=Path(__file__).resolve().parent
panels=pd.read_csv(root/'results/panels.csv');rows=pd.read_csv(root/'results/comparison.csv')
stats=np.load(root/'data/public_panel_statistics.npz')['statistics']
models=json.loads((root/'configs/models.json').read_text())
regmax=0.;hash_count=0;lpmax=0.;lpcount=0
for _,p in panels.query('replicate==0').iterrows():
    cfg=MarketConfig(**models[int(p.configuration)]['cfg'])
    raw=simulate(cfg,int(p.episodes),float(p.probe_shares),66,int(p.seed),audit=True)
    assert array_hash(**raw['public'])==p.public_sha256;hash_count+=1
    y=raw['prices'];u=raw['probes'];d=float(p.probe_shares);R=len(u)
    pos=y[u>0];neg=y[u<0]
    slope=(pos.mean(axis=0)-neg.mean(axis=0))/(2*d)
    residual=np.concatenate((pos-pos.mean(axis=0),neg-neg.mean(axis=0)))
    sd=np.sqrt(np.sum(residual**2,axis=0)/(R-2));se=sd/(d*np.sqrt(R))
    crit=t.ppf(1-.05/(2*66),R-2)
    lower=slope-crit*se-1e-14;upper=slope+crit*se+1e-14
    alt=np.stack([slope,lower,upper,se]);err=float(np.max(np.abs(alt-stats[int(p.panel_id)])))
    assert err<1e-10;regmax=max(regmax,err)
    for _,row in rows[rows.panel_id==p.panel_id].iterrows():
        h=int(row.horizon);a=recurrence_interval(lower[:h+1],upper[:h+1],float(p.rate_floor),method='highs-ipm')
        diff=max(abs(a['lower']-row.recurrence_lower),abs(a['upper']-row.recurrence_upper))
        assert diff<2e-5;assert a['label']==row.recurrence_label
        lpmax=max(lpmax,diff);lpcount+=1
assert int(rows.loc[rows.response_event,'recurrence_wrong'].sum())==0
assert bool(rows.loc[rows.response_event,'recurrence_contains'].all())
report={'public_seed_regenerations':hash_count,'independent_group_means_regressions':hash_count,
        'regression_max_absolute_error':regmax,'alternate_solver_comparisons':lpcount,
        'alternate_solver_max_bound_difference':lpmax,
        'gain_contained_on_every_primary_response_event':True,'external_replication':False}
(root/'results/verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
