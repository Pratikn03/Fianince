#!/usr/bin/env python3
"""Reproduce the synthetic study; no network, credentials, or market data needed."""
from __future__ import annotations
import argparse
import csv
from fractions import Fraction as F
import itertools
import json
import math
from pathlib import Path
import platform
import sys
import time
import numpy as np
import scipy
from scipy.stats import norm

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from machine_markets.model import Market,recover_kernel
from machine_markets.construction import construct_pair,to_markets
from machine_markets.inference import (feedback_bounds,classify,gaussian_certificate,
                                       single_rate,matrix_pencil,point_label)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def exact_experiments(cfg: dict,out: Path) -> dict:
    pairs=[];rows=[];comparisons=[];shock_rows=[]
    for K,astr,rstr in itertools.product(cfg['exact_K'],cfg['exact_a'],cfg['slow_persistence']):
        nodes=[F(0)] if K==1 else [F(3,4)*F(i,K-1) for i in range(K)]
        p=construct_pair(F(astr),nodes+[F(rstr)])
        p['id']=len(pairs)
        minus,plus=to_markets(p)
        hm,hp=minus.impulse(K+2),plus.impulse(K+2)
        km,kp=minus.kernel(K+1),plus.kernel(K+1)
        row={'pair_id':p['id'],'K':K,'a':minus.a,'slow_persistence':float(F(rstr)),
             'agents_each':len(minus.q),'Q_minus':minus.feedback,'Q_plus':plus.feedback,
             'rho_minus':minus.spectral_radius(),'rho_plus':plus.spectral_radius(),
             'matched_price_max_abs_error':float(abs(hm[:K+2]-hp[:K+2]).max()),
             'matched_kernel_max_abs_error':float(abs(km[:K]-kp[:K]).max()),
             'next_price_difference':float(hp[K+2]-hm[K+2]),
             'exact_next_difference':float(F(p['scale']))}
        assert minus.margin>0>plus.margin
        assert row['rho_minus']<1<row['rho_plus']
        assert row['matched_price_max_abs_error']<5e-11
        assert abs(row['next_price_difference']-row['exact_next_difference'])<5e-11
        common_floor=1-float(F(rstr))
        L,U=feedback_bounds(km[:K].sum(),km[:K].sum(),km[K-1],K,common_floor)
        for name,m in [('stable',minus),('unstable',plus)]:
            k=m.kernel(K)
            one=single_rate(k)
            pencil=matrix_pencil(k,0.0,common_floor)
            comparisons.append({'pair_id':p['id'],'true_label':name,'K':K,
                'one_rate_Q':one,'one_rate_label':point_label(m.a,one),
                'matrix_pencil_Q':pencil,'matrix_pencil_label':point_label(m.a,pencil),
                'rate_bound_lower':L,'rate_bound_upper':U,
                'rate_bound_label':classify(m.a,L,U)})
        for repetition in range(3):
            rng=np.random.default_rng(np.random.SeedSequence([cfg['seed'],p['id'],repetition,17]))
            shocks=rng.normal(size=K+2)
            xm,xp=minus.simulate(shocks),plus.simulate(shocks)
            # A K+2-input experiment has h[0] through h[K+1] as its relevant responses.
            difference=float(np.max(abs(xm-xp)))
            assert difference<5e-10
            shock_rows.append({'pair_id':p['id'],'repetition':repetition,
                               'input_steps':K+2,'path_max_abs_difference':difference,
                               'variance_minus':float(np.var(xm)),
                               'variance_plus':float(np.var(xp))})
        pairs.append(p);rows.append(row)
    write_json(out/'exact_witnesses.json',pairs)
    write_csv(out/'exact_pairs.csv',rows)
    write_csv(out/'matched_pair_baselines.csv',comparisons)
    write_csv(out/'matched_shock_paths.csv',shock_rows)
    summary={'pairs':len(pairs),'markets':2*len(pairs),
             'all_opposite_stability':all(x['rho_minus']<1<x['rho_plus'] for x in rows),
             'max_matched_price_error':max(x['matched_price_max_abs_error'] for x in rows),
             'max_matched_kernel_error':max(x['matched_kernel_max_abs_error'] for x in rows),
             'short_shock_comparisons':len(shock_rows),
             'max_short_shock_path_error':max(x['path_max_abs_difference'] for x in shock_rows),
             'min_spectral_separation_above_one':min(x['rho_plus']-1 for x in rows)}
    return summary


def readable_witness(out: Path) -> dict:
    p=construct_pair(F(2,5),[F(0),F(1,2),F(19,20)])
    minus,plus=to_markets(p)
    T=200
    xm,xp=minus.impulse(T),plus.impulse(T)
    frozen=plus.simulate(np.zeros(T),1.0,True)
    write_csv(out/'witness_impulses.csv',[{'t':t,'stable':xm[t],'unstable':xp[t],
                                        'frozen_learning':frozen[t]} for t in range(T+1)])
    short=[]
    for H in [2,4,8,16,64,128,256]:
        km,kp=minus.kernel(H),plus.kernel(H)
        for name,m,k in [('stable',minus,km),('unstable',plus,kp)]:
            L,U=feedback_bounds(k.sum(),k.sum(),k[-1],H,.05)
            short.append({'market':name,'H':H,'lower':L,'upper':U,
                          'certificate':classify(m.a,L,U),
                          'one_rate_Q':single_rate(k),
                          'matrix_pencil_Q':matrix_pencil(k,0,.05)})
    write_csv(out/'witness_horizon_recovery.csv',short)
    p.update({'rho_minus':minus.spectral_radius(),'rho_plus':plus.spectral_radius(),
              'h_minus':xm[:7].tolist(),'h_plus':xp[:7].tolist(),
              'true_Q_minus':minus.feedback,'true_Q_plus':plus.feedback,
              'one_rate_Q_from_two_taps':single_rate(plus.kernel(2)),
              'agents_each':len(plus.q),
              'unstable_impulse_at_200':float(xp[200]),
              'stable_impulse_at_200':float(xm[200]),
              'unstable_asymptotic_efold_steps':1/math.log(plus.spectral_radius())})
    write_json(out/'readable_witness.json',p)
    return p


def panel_configurations(cfg: dict) -> list[dict]:
    configs=[]
    for a,floor,share,ratio in itertools.product(cfg['panel_a'],cfg['eta_floors'],
                                               cfg['slow_shares'],cfg['loop_ratios']):
        case_id=len(configs)
        rng=np.random.default_rng(np.random.SeedSequence([cfg['seed'],case_id,991]))
        eta_s=np.minimum(floor*np.array([1,1.3,1.8,2.5]),.9)
        eta_f=rng.uniform(.2,.9,4)
        qtotal=ratio*(1-a)
        q_s=rng.dirichlet(np.ones(4))*share*qtotal
        q_f=rng.dirichlet(np.ones(4))*(1-share)*qtotal
        m=Market(a,np.r_[q_s,q_f],np.r_[eta_s,eta_f])
        configs.append({'case_id':case_id,'a':a,'eta_floor':floor,'slow_share':share,
                        'loop_ratio':ratio,'q':m.q.tolist(),'eta':m.eta.tolist(),
                        'true_Q':m.feedback,'rho':m.spectral_radius(),
                        'true_label':'stable' if m.margin>0 else 'unstable'})
    return configs


def measurement_experiments(cfg: dict,out: Path) -> dict:
    cases=panel_configurations(cfg)
    write_json(out/'configurations.json',cases)
    horizons=cfg['horizons'];nh=len(horizons);Hmax=max(horizons)
    nkeep=min(cfg['first_taps_saved'],Hmax)
    ndata=len(cases)*len(cfg['relative_noise_sigma'])*cfg['noise_repetitions']
    first=np.empty((ndata,nkeep));sums=np.empty((ndata,nh));last=np.empty((ndata,nh))
    ids=np.empty(ndata,dtype=np.int32);repids=ids.copy();noiseids=ids.copy();ses=np.empty(ndata)
    truth=np.empty((len(cases),Hmax));records=[];dataset_checks=[];noiseless=[]
    z=float(norm.ppf(1-cfg['alpha']/(4*nh)))
    index=0
    for c in cases:
        market=Market(c['a'],np.array(c['q']),np.array(c['eta']))
        exact=market.loop_open_kernel(Hmax)
        assert np.allclose(exact,market.kernel(Hmax),rtol=1e-11,atol=1e-14)
        truth[c['case_id']]=exact
        for H in horizons:
            k=exact[:H]
            L,U=feedback_bounds(k.sum(),k.sum(),k[-1],H,c['eta_floor'])
            assert L-1e-12 <= market.feedback <= U+1e-12
            noiseless.append({'case_id':c['case_id'],'H':H,'true_label':c['true_label'],
                              'true_Q':market.feedback,'lower':L,'upper':U,
                              'label':classify(c['a'],L,U)})
        for noise_id,rel in enumerate(cfg['relative_noise_sigma']):
            se=rel*(1-c['a'])/math.sqrt(cfg['sample_mean_replicates'])
            for repetition in range(cfg['noise_repetitions']):
                rng=np.random.default_rng(np.random.SeedSequence([cfg['seed'],c['case_id'],noise_id,repetition]))
                observed=exact+rng.normal(0,se,Hmax)
                first[index]=observed[:nkeep]
                ids[index]=c['case_id'];repids[index]=repetition;noiseids[index]=noise_id;ses[index]=se
                any_error=False;all_covered=True;interval_event=True
                for hi,H in enumerate(horizons):
                    observed_sum=float(observed[:H].sum());observed_last=float(observed[H-1])
                    sums[index,hi]=observed_sum;last[index,hi]=observed_last
                    cert=gaussian_certificate(c['a'],observed_sum,observed_last,H,se,c['eta_floor'],nh,cfg['alpha'])
                    nofloor=gaussian_certificate(c['a'],observed_sum,observed_last,H,se,0.0,nh,cfg['alpha'])
                    one=single_rate(observed[:H])
                    # Conventional comparator uses at most the first 32 taps; all saved.
                    pencil=matrix_pencil(observed[:min(H,nkeep)],se,c['eta_floor'])
                    trunc=max(0.0,observed_sum)
                    error=cert['label'] in ['stable','unstable'] and cert['label']!=c['true_label']
                    covered=cert['lower']-1e-12 <= market.feedback <= cert['upper']+1e-12
                    event=(abs(observed_sum-exact[:H].sum())<=z*se*math.sqrt(H)+1e-13 and
                           abs(observed_last-exact[H-1])<=z*se+1e-13)
                    if event:
                        assert covered,('coverage contract',c['case_id'],H)
                        assert not error,('incorrect on coverage event',c['case_id'],H)
                    any_error |= error;all_covered &= covered;interval_event &= event
                    records.append({'dataset_id':index,'case_id':c['case_id'],'noise_id':noise_id,
                        'relative_sigma':rel,'repetition':repetition,'H':H,
                        'true_label':c['true_label'],'true_Q':market.feedback,
                        'a':c['a'],'eta_floor':c['eta_floor'],'slow_share':c['slow_share'],
                        'loop_ratio':c['loop_ratio'],'tap_se':se,
                        'lower':cert['lower'],'upper':cert['upper'],'rate_aware':cert['label'],
                        'no_floor':nofloor['label'],'truncation':point_label(c['a'],trunc),
                        'truncation_Q':trunc,'one_rate':point_label(c['a'],one),'one_rate_Q':one,
                        'matrix_pencil':point_label(c['a'],pencil),'matrix_pencil_Q':pencil,
                        'oracle':c['true_label'],'interval_event':event,
                        'feedback_covered':covered})
                dataset_checks.append({'dataset_id':index,'case_id':c['case_id'],'noise_id':noise_id,
                    'any_wrong_rate_aware_label':any_error,'all_Q_bounds_cover':all_covered,
                    'joint_measurement_interval_event':interval_event})
                index+=1
    np.savez_compressed(out/'measurement_inputs.npz',first_tap_means=first,
                        partial_sums=sums,terminal_taps=last,case_ids=ids,
                        noise_ids=noiseids,repetition_ids=repids,tap_standard_errors=ses,
                        horizons=np.array(horizons))
    np.savez_compressed(out/'true_kernels.npz',kernels=truth)
    write_csv(out/'decisions.csv',records)
    write_csv(out/'measurement_dataset_checks.csv',dataset_checks)
    write_csv(out/'noiseless_bounds.csv',noiseless)
    methods=['rate_aware','no_floor','truncation','one_rate','matrix_pencil','oracle']
    metrics=[]
    for noise_id,H,method in itertools.product(range(len(cfg['relative_noise_sigma'])),horizons,methods):
        rows=[r for r in records if r['noise_id']==noise_id and r['H']==H]
        n=len(rows);unstable=sum(r['true_label']=='unstable' for r in rows);stable=n-unstable
        decided=sum(r[method] in ['stable','unstable'] for r in rows)
        false_safe=sum(r[method]=='stable' and r['true_label']=='unstable' for r in rows)
        false_alarm=sum(r[method]=='unstable' and r['true_label']=='stable' for r in rows)
        errors=false_safe+false_alarm
        metrics.append({'noise_id':noise_id,'relative_sigma':cfg['relative_noise_sigma'][noise_id],
                        'H':H,'method':method,'n_datasets':n,'decided':decided,
                        'decision_fraction':decided/n,'incorrect':errors,
                        'unconditional_error_fraction':errors/n,
                        'wrong_stable_count':false_safe,'true_unstable_count':unstable,
                        'wrong_stable_fraction':false_safe/unstable if unstable else None,
                        'wrong_unstable_count':false_alarm,'true_stable_count':stable,
                        'wrong_unstable_fraction':false_alarm/stable if stable else None,
                        'error_among_decisions':errors/decided if decided else None})
    write_csv(out/'comparison_summary.csv',metrics)
    wrong=sum(d['any_wrong_rate_aware_label'] for d in dataset_checks)
    radius=math.sqrt(math.log(2/.05)/(2*ndata))
    pernoise=[]
    for ni in range(len(cfg['relative_noise_sigma'])):
        subset=[d for d in dataset_checks if d['noise_id']==ni]
        pernoise.append({'noise_id':ni,'datasets':len(subset),
            'any_wrong_label_count':sum(d['any_wrong_rate_aware_label'] for d in subset),
            'joint_measurement_interval_coverage':np.mean([d['joint_measurement_interval_event'] for d in subset]).item(),
            'joint_Q_bound_coverage':np.mean([d['all_Q_bounds_cover'] for d in subset]).item()})
    return {'configurations':len(cases),'datasets':ndata,'horizons':horizons,
            'decision_rows':len(records),'reported_methods':methods,
            'sample_mean_replicates':cfg['sample_mean_replicates'],
            'interpretation':'distribution-equivalent noisy kernel sample means; not trained-agent runs',
            'any_wrong_rate_aware_label_count':wrong,
            'any_wrong_rate_aware_label_fraction':wrong/ndata,
            'hoeffding_95_interval_for_design_average_error_probability':
                [max(0.0,wrong/ndata-radius),min(1.0,wrong/ndata+radius)],
            'per_noise':pernoise,'comparison_metrics':metrics}


def negative_controls(out: Path) -> dict:
    market=Market(.4,np.array([.8]),np.array([.001]))
    rows=[]
    for H,floor in itertools.product([4,256,2048,4096],[.001,.2]):
        k=market.kernel(H)
        L,U=feedback_bounds(k.sum(),k.sum(),k[-1],H,floor)
        rows.append({'H':H,'assumed_eta_floor':floor,'actual_eta':.001,
                     'floor_valid':floor<=.001,'lower':L,'upper':U,
                     'label':classify(.4,L,U),'actual_label':'unstable'})
    J=np.array([[.4,1.0],[-1.5,0.0]])
    negative={'wrong_floor_cases':rows,
              'signed_feedback':{'a':.4,'q':-1.5,'eta':1.0,
                                  'a_plus_Q':-1.1,
                                  'spectral_radius':float(np.max(abs(np.linalg.eigvals(J)))),
                                  'interpretation':'positivity violated; the positive-model criterion is inapplicable and the public Market constructor rejects this input'}}
    write_json(out/'negative_controls.json',negative)
    return negative


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',type=Path,default=ROOT/'configs'/'main.json')
    parser.add_argument('--output',type=Path,default=ROOT/'results')
    parser.add_argument('--smoke',action='store_true')
    args=parser.parse_args()
    cfg=json.loads(args.config.read_text())
    if args.smoke:
        cfg.update(exact_K=[1,2],exact_a=['2/5'],slow_persistence=['99/100'],
                   panel_a=[.4],eta_floors=[.02],slow_shares=[.3],
                   loop_ratios=[.6,1.4],noise_repetitions=2)
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter()
    write_json(out/'executed_config.json',cfg)
    exact=exact_experiments(cfg,out)
    witness=readable_witness(out)
    measurement=measurement_experiments(cfg,out)
    negatives=negative_controls(out)
    summary={'study':cfg['study'],'exact':exact,'measurement':measurement,
             'readable_witness':{key:witness[key] for key in
                 ['true_Q_minus','true_Q_plus','rho_minus','rho_plus','h_minus','h_plus',
                  'one_rate_Q_from_two_taps','unstable_asymptotic_efold_steps']},
             'negative_controls_executed':True}
    write_json(out/'summary.json',summary)
    environment={'python':sys.version,'platform':platform.platform(),
                 'numpy':np.__version__,'scipy':scipy.__version__,
                 'elapsed_seconds':time.perf_counter()-start,
                 'command':' '.join(sys.argv),'config_file':str(args.config),
                 'external_market_data_used':False,'trained_AI_agents_used':False}
    write_json(out/'environment.json',environment)
    print(json.dumps({'exact_pairs':exact['pairs'],'datasets':measurement['datasets'],
                      'wrong_rate_aware_labels':measurement['any_wrong_rate_aware_label_count'],
                      'seconds':environment['elapsed_seconds'],'output':str(out)},indent=2))

if __name__=='__main__':
    main()
