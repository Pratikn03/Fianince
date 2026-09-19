#!/usr/bin/env python3
"""Predeclared resolution sensitivity; no changes to primary configuration."""
from __future__ import annotations
import os
for n in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[n]='1'
import csv,json,sys,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mmfh.estimators import fit_nnls,moment_interval
STATE={}
def init():
 a=np.load(ROOT/'data/full_measurements.npz');STATE.update({k:a[k] for k in a.files});a.close()
 STATE['cases']=json.loads((ROOT/'data/configurations.json').read_text())
def one(i):
 c=STATE['cases'][int(STATE['case_ids'][i])];y=STATE['taps'][i]/(1-c['a']);se=float(STATE['tap_standard_errors'][i])/(1-c['a'])
 base={'dataset_id':i,'case_id':c['case_id'],'noise_id':int(STATE['noise_ids'][i]),'repetition_id':int(STATE['repetition_ids'][i]),'H':256,'truth':c['true_label'],'true_gain_ratio':c['loop_ratio']};out=[]
 for n in (32,128,256):
  z=moment_interval(y,se,c['eta_floor'],bins=n)
  out.append(base|{'method':'outer_lp','resolution':n,'lower':z['raw_lower'],'upper':z['raw_upper'],'gain':float('nan'),'label':z['raw_label'],'status':z['status'],'residual':z['primal_violation']})
 for n in (65,257):
  z=fit_nnls(y,se,c['eta_floor'],nodes=n)
  out.append(base|{'method':'nnls','resolution':n,'lower':float('nan'),'upper':float('nan'),'gain':z['gain'],'label':z['label'],'status':z['status'],'residual':z['kkt_violation']})
 return out
if __name__=='__main__':
 a=np.load(ROOT/'data/full_measurements.npz');ids=np.where(np.isin(a['repetition_ids'],[0,20,40,60,80]))[0].tolist();a.close();start=time.perf_counter()
 with (ROOT/'results/resolution_sensitivity.csv').open('w',newline='') as f:
  writer=None
  with ProcessPoolExecutor(max_workers=4,initializer=init) as pool:
   for k,rows in enumerate(pool.map(one,ids,chunksize=10)):
    if writer is None:writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader()
    writer.writerows(rows)
    if k%100==0:print(json.dumps({'datasets':k+1,'of':len(ids),'seconds':round(time.perf_counter()-start,2)}),flush=True)
 meta={'datasets':len(ids),'rows':len(ids)*5,'H':256,'outer_bins':[32,128,256],'nnls_nodes':[65,257],'seconds':time.perf_counter()-start,'selection':'repetitions 0,20,40,60,80; fixed before primary results'}
 (ROOT/'results/sensitivity_metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print('COMPLETE',meta,flush=True)
