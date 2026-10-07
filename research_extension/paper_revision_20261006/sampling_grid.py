"""Declared sampling/filter grid on the same locally available recorder data."""
import json
from pathlib import Path
import pandas as pd
from revise_evidence import series,summary
from empirical_pipeline.feedback_var import var1

REV=Path(__file__).resolve().parent
ROOT=REV.parents[1]


def run():
    results=[]
    for asset in ['BTC','ETH','ADA']:
        frame=pd.read_pickle(ROOT/'empirical_pipeline/cache'/f'{asset}_1sec_core_v2dedup.pkl')
        for delta in [1,10,60]:
            for window in [60,300,900]:
                if window<=delta:continue
                s=series(frame,delta,window);rows=[]
                for (day,segment),g in s.groupby(['day','segment']):
                    if len(g)<500:continue
                    e=var1(g.x.to_numpy(),g.flow.to_numpy())
                    rows.append(dict(date=str(day.date()),**e))
                results.append({'asset':asset,'delta_seconds':delta,'window_seconds':window,
                                'mechanical_anchor':1-2/(window/delta+1),**summary(rows,('Q','S','rho'))})
        print(asset,'grid complete',flush=True)
    (REV/'results/sampling_grid.json').write_text(json.dumps({'scope':'exploratory declared grid, same recorded sample and observed-flow alignment; no structural identification',
                                                           'cells':results},indent=2)+'\n')


if __name__=='__main__':run()
