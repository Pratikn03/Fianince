#!/usr/bin/env python3
"""Recompute measurement inputs and certificates without importing project code.

NumPy is used only for archived arrays and regenerating the declared RNG.
The normal quantile and feedback bounds are recalculated independently.
"""
import argparse
import csv
import json
import math
from pathlib import Path
from statistics import NormalDist
import numpy as np


def main():
    root=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser()
    parser.add_argument('--results',type=Path,default=root/'results')
    args=parser.parse_args();folder=args.results
    cfg=json.loads((folder/'executed_config.json').read_text())
    cases=json.loads((folder/'configurations.json').read_text())
    with np.load(folder/'measurement_inputs.npz') as archive:
        data={key:archive[key] for key in archive.files}
    kernels=np.load(folder/'true_kernels.npz')['kernels']
    Hs=data['horizons'];nh=len(Hs);Hmax=int(max(Hs))
    z=NormalDist().inv_cdf(1-cfg['alpha']/(4*nh))
    regenerated=0
    for i,ci in enumerate(data['case_ids']):
        ni=int(data['noise_ids'][i]);rep=int(data['repetition_ids'][i])
        rng=np.random.default_rng(np.random.SeedSequence([cfg['seed'],int(ci),ni,rep]))
        obs=kernels[ci]+rng.normal(0,data['tap_standard_errors'][i],Hmax)
        assert np.array_equal(obs[:data['first_tap_means'].shape[1]],data['first_tap_means'][i])
        for j,H in enumerate(Hs):
            assert float(obs[:H].sum())==float(data['partial_sums'][i,j])
            assert float(obs[H-1])==float(data['terminal_taps'][i,j])
        regenerated+=1
    checked=0;wrong=0
    with (folder/'decisions.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            i=int(row['dataset_id']);H=int(row['H']);hi=list(Hs).index(H)
            ci=int(row['case_id']);case=cases[ci]
            se=float(data['tap_standard_errors'][i]);a=case['a'];floor=case['eta_floor']
            sl=float(data['partial_sums'][i,hi])-z*se*math.sqrt(H)
            su=float(data['partial_sums'][i,hi])+z*se*math.sqrt(H)
            ku=float(data['terminal_taps'][i,hi])+z*se
            if su<0 or ku<0:
                label='model_conflict'
            else:
                lower=max(0,sl)
                fraction=1-(1-floor)**H
                upper=min(su/fraction,su+(1-floor)/floor*ku)
                assert math.isclose(lower,float(row['lower']),abs_tol=1e-11,rel_tol=1e-11)
                assert math.isclose(upper,float(row['upper']),abs_tol=1e-10,rel_tol=1e-10)
                label=('model_conflict' if lower>upper+1e-12 else
                       'stable' if a+upper<1-1e-12 else
                       'unstable' if a+lower>1+1e-12 else 'inconclusive')
            assert label==row['rate_aware']
            wrong+=label in ['stable','unstable'] and label!=row['true_label']
            checked+=1
    print(json.dumps({'status':'PASS','measurement_datasets_regenerated':regenerated,
                      'decision_rows_independently_recomputed':checked,
                      'wrong_confident_decisions':wrong,
                      'external_replication':False},indent=2))

if __name__=='__main__':main()
