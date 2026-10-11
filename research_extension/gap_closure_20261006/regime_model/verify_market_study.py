"""Verify completed switching fits, dates, provenance and scope of interpretations."""
from pathlib import Path
import json,hashlib
from collections import Counter
import numpy as np
from run_market_study import prepare,coinbase
from switching_regression import expectation
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def audit():
    data=json.loads((HERE/'market_results.json').read_text());assert data['status']=='COMPLETED_FIXED_PROTOCOL'
    checks=[];statuses=Counter();foldstatuses=Counter();selectedstatuses=Counter();datasets={};nfits=0
    for name,ds in data['datasets'].items():
        asset,state=name.split('_',1);chunks,provenance=coinbase(asset,state)
        assert provenance['sha256']==ds['provenance']['sha256']
        for c in chunks:c['state']=state
        full,sc=prepare(chunks);assert sum(len(y) for X,y in full)==ds['n']
        floors={}
        for key,spec in ds['specifications'].items():
            chosen=spec['selected'];assert chosen['log_likelihood']==max(s['log_likelihood'] for s in spec['starts'])
            for f in spec['starts']:
                statuses[f['status']]+=1;nfits+=1;verify_fit(full,f,checks)
            floor=float(key.split('_')[0]);floors[key]={'low_variance':chosen['variance'][0],'variance_floor':floor,'at_floor':bool(np.isclose(chosen['variance'][0],floor,rtol=1e-7,atol=0)),'sd_ratio':spec['residual_sd_ratio']}
        for fold in ds['folds']:
            assert all(day<fold['date'] for day in fold['train_dates'])
            train=[c for c in chunks if c['date']<fold['date']];tr,_=prepare(train)
            for model in fold['models'].values():
                selectedstatuses[model['selected']['status']]+=1
                assert model['selected']['log_likelihood']==max(s['log_likelihood'] for s in model['starts'])
                for f in model['starts']:
                    foldstatuses[f['status']]+=1;nfits+=1;verify_fit(tr,f,checks)
        datasets[name]={'n':ds['n'],'segments':ds['segments'],'evaluation_dates':[f['date'] for f in ds['folds']],'floors':floors,'all_baseline_mse_intervals_include_zero':all(v['mse']['ci95'][0]<=0<=v['mse']['ci95'][1] for k,v in ds['summary'].items() if k!='full_minus_variance_only'),'full_minus_variance_only_intervals_include_zero':all(v['ci95'][0]<=0<=v['ci95'][1] for v in ds['summary']['full_minus_variance_only'].values())}
    receipt=json.loads((HERE.parent/'final_delivery_receipt.json').read_text())
    actual_dates=datasets['BTC_x']['evaluation_dates'];declared=receipt['regime_study_summary']['evaluation_dates']
    out={'status':'VERIFIED_COMPUTATION_WITH_INFERENCE_LIMITS','fit_records_checked':nfits,'full_sample_start_statuses':dict(statuses),'forecast_start_statuses':dict(foldstatuses),'selected_forecast_statuses':dict(selectedstatuses),'max_final_log_likelihood_error':max(checks),'datasets':datasets,'historical_final_receipt_contradictions':{'declared_evaluation_dates':declared,'actual_evaluation_dates':actual_dates,'dates_match':declared==actual_dates,'claimed_raw_return_clock':'1s','actual_raw_return_clock':'10s bins from existing series construction','closure_claim':'G01-G26 100% locally complete is inconsistent with open provider/causal/calibration/semantic gates in GAPS.md'},'input_sha256':hashlib.sha256((HERE/'market_results.json').read_bytes()).hexdigest(),'limits':['Variance-floor-dependent BTC state separation does not authenticate old62.7 ratio','Failure to find mean forecast gain does not prove regime absence','Forecast variance-only density gains may reflect conditional volatility without coefficient changes','Only7 consecutive evaluation dates; serial dependence and model misspecification remain','Iteration limits retained; best training likelihood is not a global optimum certificate']}
    (HERE/'market_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='datasets'},indent=2));return out

def verify_fit(segments,f,errors):
    h=np.array(f['history']);assert np.min(np.diff(h))>=-1e-5
    beta=np.array(f['beta']);var=np.array(f['variance']);P=np.array(f['transition']);pi=np.array(f['initial'])
    assert np.all(var>=f['variance_floor']);np.testing.assert_allclose(P.sum(1),1);assert np.isclose(pi.sum(),1)
    ll,_=expectation(segments,beta,var,P,pi);error=abs(ll-f['log_likelihood']);assert error<1e-5;errors.append(error)
if __name__=='__main__':audit()
