"""Inspect the newly generated extended search, not the inherited truncated archive.

Numerical approximate roots cannot certify a globally unique inverse. This
records residuals and distance to permutations, including near-collision cases.
"""
from pathlib import Path
import hashlib
import importlib.util
import itertools
import json
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent/'source/research_extension/cross_market'
spec=importlib.util.spec_from_file_location('gf',ROOT/'global_fibres.py')
gf=importlib.util.module_from_spec(spec);spec.loader.exec_module(gf)
summary_path=ROOT/'global_fibres_extended_results.json'
solutions_path=ROOT/'global_fibres_extended_solutions.json'
summary=json.loads(summary_path.read_text())
solutions=json.loads(solutions_path.read_text())
assert set(summary)=={'2,2','3,2','3,3','4,2','4,4'}
assert all(v['configurations']==12 for v in summary.values())
rows=[]
for case, configurations in solutions.items():
    K,D=map(int,case.split(','))
    L=summary[case]['lstar']
    for index,cfg in enumerate(configurations):
        x0=np.asarray(cfg['x0'])
        perms=[np.r_[x0[:K][list(p)],x0[K:].reshape(D,K)[:,list(p)].ravel()]
               for p in itertools.permutations(range(K))]
        for label,degree in [('at_lstar',L),('at_lstar_plus_1',L+1)]:
            for raw in cfg[label]:
                x=np.asarray(raw)
                residual=float(np.max(np.abs(gf.moments(x,K,D,degree)-gf.moments(x0,K,D,degree))))
                distance=float(min(np.max(np.abs(x-p)) for p in perms))
                gap=float(np.min(np.diff(np.sort(x0[:K]))))
                rows.append(dict(case=case,configuration=index,degree=degree,
                                 residual=residual,distance_to_permutation=distance,
                                 true_minimum_node_gap=gap,
                                 within_legacy_near_collision_tolerance=bool(gap<.04 and distance<.06)))
out={'source':'fresh complete extended search, 12 configurations per case, 400 starts per solve',
     'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [summary_path,solutions_path]},
     'case_summary':summary,'apparent_other_solutions':len(rows),'solution_diagnostics':rows,
     'all_recorded_residuals_below_1e_minus_10':all(r['residual']<1e-10 for r in rows),
     'all_apparent_solutions_within_legacy_near_collision_tolerance':all(r['within_legacy_near_collision_tolerance'] for r in rows),
     'global_uniqueness_proved':False}
(HERE/'fresh_global_search_validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='solution_diagnostics'},indent=2))
