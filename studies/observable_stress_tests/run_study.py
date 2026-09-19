#!/usr/bin/env python3
"""Frozen observable-data study. No network, live orders, or hidden-state inference."""
from __future__ import annotations
import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']: os.environ.setdefault(key,'1')
from pathlib import Path
from dataclasses import asdict
import argparse,csv,hashlib,json,time
import numpy as np
from src.market import MarketConfig,simulate,impulse,joint_matrix
from src.observable import response_intervals,recurrence_interval,deconvolution_interval,recurrence_point


def write_csv(path,rows):
    if rows:
        with Path(path).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def array_hash(probes,prices):
    h=hashlib.sha256()
    for v in (probes,prices): h.update(np.asarray(v,dtype='<f8').tobytes())
    return h.hexdigest()


def iswrong(label,true): return label in ('stable','unstable') and label!=true


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='.');ap.add_argument('--repetitions',type=int,default=40)
    args=ap.parse_args();root=Path(args.out);root.mkdir(exist_ok=True,parents=True)
    for p in ['data','results','configs']: (root/p).mkdir(exist_ok=True)
    horizons=[8,24,64];steps=66;rows=[];panels=[];statistics=[];configs=[]
    start=time.time();pid=0
    for cid,(slow,G) in enumerate((s,g) for s in [.002,.02,.1] for g in [.7,.95,1.05,1.3]):
        q=tuple(.6*G*np.array([.6,.4]));cfg=MarketConfig(.4,.02,(.5,slow),q)
        true='stable' if G<1 else 'unstable';S=.4+sum(q)
        beta=impulse(.4,np.array(q),np.array([.5,slow]),.02,steps)
        rho=float(np.max(np.abs(np.linalg.eigvals(joint_matrix(.4,np.array(q),np.array([.5,slow]))))))
        configs.append({'id':cid,'G':G,'gain_a_plus_Q':S,'rate_floor':slow,'cfg':asdict(cfg),'spectral_radius':rho})
        for R in [128,1024]:
            for delta in [1.,4.]:
                for rep in range(args.repetitions):
                    seed=314159260+cid*100000+R*10+int(delta)*1000+rep
                    sim=simulate(cfg,R,delta,steps,seed,audit=True)
                    obs=response_intervals(**sim['public'],alpha=.05)
                    covered=bool(np.all((obs['lower']<=beta)&(beta<=obs['upper'])))
                    corr=obs['covariance']/np.maximum(np.outer(obs['se'],obs['se']),1e-30)
                    panel={'panel_id':pid,'configuration':cid,'G':G,'S':S,'rate_floor':slow,'episodes':R,
                           'probe_shares':delta,'replicate':rep,'seed':seed,'response_event':covered,
                           'mean_abs_adjacent_correlation':float(np.mean(np.abs(np.diag(corr,1)))),
                           'response_rmse':float(np.sqrt(np.mean((obs['estimate']-beta)**2))),
                           'public_sha256':array_hash(**sim['public']),**sim['audit']}
                    panels.append(panel);statistics.append(np.stack((obs['estimate'],obs['lower'],obs['upper'],obs['se'])))
                    if rep==0 and R==1024 and delta==4 and cid in [0,7,8,11]:
                        np.savez_compressed(root/'data'/f'public_example_{cid}.npz',**sim['public'])
                        np.savez_compressed(root/'data'/f'covariance_example_{cid}.npz',covariance=obs['covariance'],true_response=beta)
                    for H in horizons:
                        sub=slice(0,H+1)
                        bounds=recurrence_interval(obs['lower'][sub],obs['upper'][sub],slow)
                        old=deconvolution_interval(obs['lower'][sub],obs['upper'][sub],slow)
                        point=recurrence_point(obs['estimate'][sub],slow)
                        row={k:panel[k] for k in ['panel_id','configuration','G','S','rate_floor','episodes','probe_shares','replicate','seed','response_event']}
                        row.update(horizon=H,true_label=true,recurrence_lower=bounds['lower'],recurrence_upper=bounds['upper'],
                            recurrence_label=bounds['label'],recurrence_wrong=iswrong(bounds['label'],true),recurrence_status=bounds['status'],
                            recurrence_contains=bool(bounds['lower']-1e-7<=S<=bounds['upper']+1e-7),
                            dual_violation=bounds['dual_violation'],primal_violation=bounds['primal_violation'],dual_repair=bounds['repair'],
                            deconvolution_lower=old['lower'],deconvolution_upper=old['upper'],deconvolution_label=old['label'],
                            deconvolution_wrong=iswrong(old['label'],true),point_gain=point['gain'],point_label=point['label'],
                            point_wrong=iswrong(point['label'],true),point_status=point['status'])
                        rows.append(row)
                    pid+=1
        print(f'configuration {cid+1}/12; {pid} panels; {len(rows)} rows; {time.time()-start:.1f}s',flush=True)
    write_csv(root/'results'/'panels.csv',panels);write_csv(root/'results'/'comparison.csv',rows)
    np.savez_compressed(root/'data'/'public_panel_statistics.npz',statistics=np.asarray(statistics),
                        fields=np.array(['estimate','lower','upper','standard_error']))
    (root/'configs'/'models.json').write_text(json.dumps(configs,indent=2))
    summary={'panels':len(panels),'comparison_rows':len(rows),'configurations':12,'repetitions':args.repetitions,
             'episodes':sum(x['episodes'] for x in panels),'price_observations':sum(x['episodes']*steps for x in panels),
             'steps':steps,'horizons':horizons,'response_coverage_count':sum(x['response_event'] for x in panels),
             'recurrence_wrong':sum(x['recurrence_wrong'] for x in rows),'deconvolution_wrong':sum(x['deconvolution_wrong'] for x in rows),
             'point_wrong':sum(x['point_wrong'] for x in rows),
             'wrong_recurrence_on_event':sum(x['recurrence_wrong'] and x['response_event'] for x in rows),
             'missed_gain_on_event':sum(not x['recurrence_contains'] and x['response_event'] for x in rows),
             'max_cash_error':max(x['max_cash_error'] for x in panels),'max_share_error':max(x['max_share_error'] for x in panels),
             'max_marked_wealth_error':max(x['max_marked_wealth_error'] for x in panels),
             'mean_abs_adjacent_correlation':float(np.mean([x['mean_abs_adjacent_correlation'] for x in panels])),
             'max_primal_violation':max(x['primal_violation'] for x in rows),'max_dual_violation':max(x['dual_violation'] for x in rows),
             'seconds':time.time()-start}
    (root/'results'/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
