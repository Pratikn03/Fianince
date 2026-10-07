"""Verify preserved recorder caches against existing raw CSVs without writing caches."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from revise_evidence import digest

REV=Path(__file__).resolve().parent
ROOT=REV.parents[1]
KEYS=['midpoint','spread','buys','sells','bids_notional_0','asks_notional_0','bids_distance_0','asks_distance_0']


def run():
    results={}
    for asset in ['BTC','ETH','ADA']:
        raw=ROOT/'empirical_pipeline/data'/f'{asset}_1sec.csv'
        blocks=[];previous=None;n_raw=0
        for df in pd.read_csv(raw,usecols=['system_time']+KEYS,chunksize=150000):
            dup=df[KEYS].eq(df[KEYS].shift()).all(axis=1).to_numpy().copy()
            if previous is not None:dup[0]=bool(df[KEYS].iloc[0].eq(previous).all())
            previous=df[KEYS].iloc[-1].copy()
            sec=((pd.to_datetime(df.system_time,utc=True)-pd.Timestamp('1970-01-01',tz='UTC'))//pd.Timedelta('1s')).astype('int64')
            blocks.append(pd.DataFrame({'sec':sec.to_numpy(),'mid':df.midpoint.to_numpy(),
                                        'flow':np.where(dup,0.,(df.buys-df.sells).to_numpy()),'dup':dup}))
            n_raw+=len(df)
        reconstructed=pd.concat(blocks).drop_duplicates('sec').sort_values('sec').reset_index(drop=True)
        cache=ROOT/'empirical_pipeline/cache'/f'{asset}_1sec_core_v2dedup.pkl'
        saved=pd.read_pickle(cache)
        assert len(reconstructed)==len(saved)
        errors={}
        for col in ['sec','mid','flow','dup']:
            a=reconstructed[col].to_numpy();b=saved[col].to_numpy()
            if col=='dup':assert np.array_equal(a,b);errors[col]=0
            else:
                errors[col]=float(np.max(abs(a-b)))
                assert errors[col]==0,(asset,col,errors[col])
        results[asset]={'raw_sha256':digest(raw),'cache_sha256':digest(cache),'raw_rows':n_raw,
                        'retained_seconds':len(saved),'column_max_errors':errors,
                        'duplicate_renders':int(saved.dup.sum()),'status':'exact raw-to-cache reconstruction verified'}
        print(asset,results[asset],flush=True)
    (REV/'results/raw_input_verification.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':run()
