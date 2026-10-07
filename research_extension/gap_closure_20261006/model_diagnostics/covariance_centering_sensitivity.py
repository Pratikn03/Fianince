"""Retain an explicit within-segment mean sensitivity to explain pooled rejection."""
from pathlib import Path
import json,sys
import pandas as pd
from covariance_audit import audit,BANDWIDTHS
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REV=ROOT/'research_extension/paper_revision_20261006'
sys.path.insert(0,str(REV));from revise_evidence import series
results={}
for asset in ['BTC','ETH','ADA']:
    path=ROOT/'empirical_pipeline/cache'/f'{asset}_1sec_core_v2dedup.pkl';s=series(pd.read_pickle(path));segments=[g[['x','flow']].to_numpy() for _,g in s.groupby(['day','segment']) if len(g)>=500]
    cases={}
    for bandwidth in BANDWIDTHS:
        r=audit(segments,bandwidth,centering='within_segment');cases[str(bandwidth)]=r
        print(asset,bandwidth,'centered J',r['J_stat'],'p',r['p_chi2'],flush=True)
    results[asset]=cases
    (HERE/'centering_sensitivity.json').write_text(json.dumps({'scope':'Retrospective fixed within-segment mean sensitivity, all bandwidths/starts retained; not a selected replacement for original global-centering results','limits':'Demeaning changes the maintained covariance model and introduces finite-segment mean estimation. Neither a rejection nor nonrejection proves structural/causal validity.','assets':results},indent=2)+'\n')
