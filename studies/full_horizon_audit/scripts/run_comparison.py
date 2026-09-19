#!/usr/bin/env python3
"""Execute equal-information comparisons on all original saved datasets.

Defaults run 86,400 paired rows. --datasets selects a deterministic prefix for
smoke/reproduction tests, never the headline analysis. No network access.
"""
from __future__ import annotations
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
from concurrent.futures import ProcessPoolExecutor
import argparse,csv,json,platform,sys,time
from pathlib import Path
import numpy as np
import scipy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mmfh.estimators import summary_interval,fit_nnls,moment_interval
STATE={}


def initialize():
    arc=np.load(ROOT/'data/full_measurements.npz')
    STATE.update({key:arc[key] for key in arc.files});arc.close()
    STATE['cases']=json.loads((ROOT/'data/configurations.json').read_text())
    STATE['cfg']=json.loads((ROOT/'configs/study.json').read_text())


def process_chunk(task):
    start,end=task;records=[];cfg=STATE['cfg']
    for i in range(start,end):
        c=STATE['cases'][int(STATE['case_ids'][i])]
        # Information firewall: only y, se and floor are passed into estimators.
        y=STATE['taps'][i]/(1-c['a'])
        se=float(STATE['tap_standard_errors'][i])/(1-c['a'])
        for H in cfg['horizons']:
            obs=y[:H]
            t=time.perf_counter();legacy=summary_interval(obs,se,c['eta_floor'])
            budget=summary_interval(obs,se,c['eta_floor'],alpha=.025)
            t_summary=time.perf_counter()-t
            t=time.perf_counter();fit=fit_nnls(obs,se,c['eta_floor'],nodes=cfg['mixture_grid_nodes'],maxiter=cfg['max_nnls_iterations'])
            t_nnls=time.perf_counter()-t
            t=time.perf_counter();lp=moment_interval(obs,se,c['eta_floor'],bins=cfg['outer_bins'])
            t_lp=time.perf_counter()-t
            r={'dataset_id':i,'case_id':c['case_id'],'noise_id':int(STATE['noise_ids'][i]),
               'repetition_id':int(STATE['repetition_ids'][i]),'H':H,'a':c['a'],
               'eta_floor':c['eta_floor'],'slow_share':c['slow_share'],'true_gain_ratio':c['loop_ratio'],
               'truth':c['true_label'],'normalized_se':se,
               'legacy_lower':legacy['lower'],'legacy_upper':legacy['upper'],'legacy_label':legacy['label'],
               'budget_lower':budget['lower'],'budget_upper':budget['upper'],'budget_label':budget['label'],
               'nnls_gain':fit['gain'],'nnls_label':fit['label'],'nnls_status':fit['status'],
               'nnls_residual':fit['residual'],'nnls_kkt_violation':fit['kkt_violation'],
               'lp_lower':lp['raw_lower'],'lp_upper':lp['raw_upper'],'lp_label':lp['raw_label'],
               'combined_lower':lp['lower'],'combined_upper':lp['upper'],'combined_label':lp['label'],
               'lp_status':lp['status'],'lp_dual_violation':lp['dual_violation'],
               'lp_primal_violation':lp['primal_violation'],'lp_max_gap':lp['max_gap'],
               'lp_max_repair':lp['max_repair'],'summary_seconds':t_summary,
               'nnls_seconds':t_nnls,'lp_seconds':t_lp}
            records.append(r)
    return records


def main():
    pa=argparse.ArgumentParser();pa.add_argument('--workers',type=int,default=4)
    pa.add_argument('--datasets',type=int,default=21600);pa.add_argument('--output',type=Path,default=ROOT/'results')
    args=pa.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    jobs=[(s,min(args.datasets,s+100)) for s in range(0,args.datasets,100)]
    begin=time.perf_counter();n=0
    with (args.output/'paired_comparison.csv').open('w',newline='') as handle:
        writer=None
        with ProcessPoolExecutor(max_workers=args.workers,initializer=initialize) as pool:
            for j,records in enumerate(pool.map(process_chunk,jobs,chunksize=1)):
                if writer is None:
                    writer=csv.DictWriter(handle,fieldnames=list(records[0]));writer.writeheader()
                writer.writerows(records);handle.flush();n+=len(records)
                if j%5==0 or j==len(jobs)-1:
                    print(json.dumps({'chunks_done':j+1,'chunks_total':len(jobs),'rows_written':n,
                          'elapsed_seconds':round(time.perf_counter()-begin,2)}),flush=True)
    meta={'paired_rows':n,'datasets':args.datasets,'horizons':[4,16,64,256],
          'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
          'platform':platform.platform(),'workers':args.workers,
          'elapsed_seconds':time.perf_counter()-begin,
          'all_methods_receive_same_data_and_side_information':True,
          'external_data':False,'trained_AI_agents':False}
    (args.output/'run_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('COMPLETE',json.dumps(meta),flush=True)
if __name__=='__main__':main()
