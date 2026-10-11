"""Observed spread/depth and hypothetical sweep-cost calibration on existing data.

Last snapshot of each observed UTC minute; no gap filling or price/size filtering
before snapshot selection. Reported size units are not authenticated trade units.
Static displayed quotes do not establish fills, dynamic impact or account rules.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = Path('/Volumes/T9/machine_markets_data/primary_january_authentication_20261008/1-09-1-20.pq')
OUT = Path('/Volumes/T9/machine_markets_data/research_completion_20261008')
FRACTIONS = [.01, .1, .5]


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while b := f.read(1024*1024):
            h.update(b)
    return h.hexdigest()


def run():
    reference = json.loads((ROOT/'research_extension/gap_closure_20261006/publication_completion/january_authentication.json').read_text())
    assert sha(SOURCE) == reference['source_sha256']
    columns = ['0'] + [str(i) for i in range(2,42)]
    chunks=[]
    raw=0
    for batch in pq.ParquetFile(SOURCE).iter_batches(batch_size=100000,columns=columns):
        f=batch.to_pandas()
        raw+=len(f)
        f['minute']=f['0']//60000
        chunks.append(f.groupby('minute',sort=False).tail(1))
    sample=pd.concat(chunks).drop_duplicates('minute',keep='last').sort_values('minute')
    assert raw == 3730870
    bp=sample[[str(i) for i in range(2,22,2)]].to_numpy(float)
    bs=sample[[str(i) for i in range(3,22,2)]].to_numpy(float)
    ap=sample[[str(i) for i in range(22,42,2)]].to_numpy(float)
    az=sample[[str(i) for i in range(23,42,2)]].to_numpy(float)
    valid=(np.isfinite(bp).all(1)&np.isfinite(bs).all(1)&np.isfinite(ap).all(1)&np.isfinite(az).all(1)
           &(bp>0).all(1)&(ap>0).all(1)&(bs>=0).all(1)&(az>=0).all(1)
           &(bp[:,0]<=ap[:,0])&(np.diff(bp,axis=1)<=0).all(1)&(np.diff(ap,axis=1)>=0).all(1)
           &(bs.sum(1)>0)&(az.sum(1)>0))
    dates=pd.to_datetime(sample['0'],unit='ms',utc=True).dt.strftime('%Y-%m-%d').to_numpy()
    data=dict(ms=sample['0'].to_numpy(np.int64),date=dates.astype('U10'),bid_price=bp,bid_size=bs,ask_price=ap,ask_size=az,valid=valid)
    OUT.mkdir(parents=True,exist_ok=True)
    cache=OUT/'minute_displayed_book.npz'
    np.savez_compressed(cache,**data)
    mid=(bp[:,0]+ap[:,0])/2
    metrics={'spread_quote_units':ap[:,0]-bp[:,0],
             'spread_basis_points':(ap[:,0]-bp[:,0])/mid*1e4,
             'midpoint_quote_units':mid,
             'bid_L10_reported_size':bs.sum(1),'ask_L10_reported_size':az.sum(1)}
    for side,prices,sizes in [('buy',ap,az),('sell',bp,bs)]:
        before=np.cumsum(sizes,axis=1)-sizes
        for fraction in FRACTIONS:
            quantity=fraction*sizes.sum(1)
            consumed=np.minimum(sizes,np.maximum(quantity[:,None]-before,0))
            np.testing.assert_allclose(consumed.sum(1)[valid],quantity[valid],atol=1e-10,rtol=1e-12)
            avg=np.divide((consumed*prices).sum(1),quantity,out=np.full(len(quantity),np.nan),where=quantity>0)
            cost=(avg-mid) if side=='buy' else (mid-avg)
            incremental=(avg-prices[:,0]) if side=='buy' else (prices[:,0]-avg)
            metrics[f'{side}_{fraction:g}_sweep_cost_per_reported_unit']=cost
            metrics[f'{side}_{fraction:g}_static_depth_slope']=np.divide(2*incremental,quantity,out=np.full(len(quantity),np.nan),where=quantity>0)
    def summary(mask):
        return {key:dict(p10=float(np.quantile(value[mask],.1)),median=float(np.median(value[mask])),
                         p90=float(np.quantile(value[mask],.9))) for key,value in metrics.items()}
    rows=[dict(date=date,selected_minutes=int((dates==date).sum()),valid_minutes=int((valid&(dates==date)).sum()),
               metrics=summary(valid&(dates==date))) for date in sorted(set(dates))]
    result=dict(status='OBSERVED_DISPLAYED_BOOK_CALIBRATION_NOT_EXECUTION_OR_STRUCTURAL_IMPACT',
                source_sha256=reference['source_sha256'],raw_snapshots=raw,selected_minutes=len(sample),
                valid_minutes=int(valid.sum()),invalid_minutes=int((~valid).sum()),
                minute_rule='Last original-row snapshot in every observed UTC minute; no missing-minute interpolation; validation after selection',
                cache_path=str(cache),cache_sha256=sha(cache),fractions_of_side_L10_depth=FRACTIONS,
                pooled_metrics=summary(valid),daily=rows,
                limits=['Quote prices are provider-declared BTCUSDT.P quote units; size units and exchange records are not independently authenticated.',
                        'Sweep costs assume immediate access to all displayed levels; they are hypothetical quote costs, not actual fills or executable guarantees.',
                        'The reported static depth slope is not the dynamic structural impact kappa in the theorem.',
                        'Spreads and hypothetical depth costs can be calibrated from snapshots. Fees, funding, margin, positions and realized executions cannot be recovered from these snapshots.',
                        'No uncertainty interval treats snapshots or selected minutes as independent observations.'],
                script_sha256=sha(Path(__file__)))
    (HERE/'displayed_book_calibration.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ['raw_snapshots','selected_minutes','valid_minutes','invalid_minutes','pooled_metrics']},indent=2))


if __name__=='__main__':
    run()
