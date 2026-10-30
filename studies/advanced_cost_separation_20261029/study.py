"""Continuous simulator cases, matched-cost decisions and resumable statistics."""
import hashlib,json,os,time
from pathlib import Path
from dataclasses import asdict,replace
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
import pandas as pd
from scipy.stats import norm,t,chi2,binomtest
from model import Contract,response,position,gross_value,net_value,risk_reserve,no_data_randomized

SCENARIOS=['gaussian_iid','very_slow_memory','correlated_gaussian','finite_variance_t3','biased_readings','future_regime_change']
METHODS=['gaussian_iid','gaussian_variance_bound','student_t_projection','median_of_means','full_ellipsoid_iid','point_uncertified','gaussian_rational_margin']
PROFILES={'quick':dict(seeds=3,cases_per_seed=6,trials=256,bootstrap=400),
          'research':dict(seeds=12,cases_per_seed=12,trials=1024,bootstrap=2000),
          'deep':dict(seeds=24,cases_per_seed=12,trials=4096,bootstrap=5000)}

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic_json(path,value):
    tmp=Path(str(path)+'.tmp');tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');os.replace(tmp,path)
def usable_cpus():
    n=os.cpu_count() or 1
    try:n=min(n,len(os.sched_getaffinity(0)))
    except AttributeError:pass
    try:
        q,p=Path('/sys/fs/cgroup/cpu.max').read_text().split()
        if q!='max':n=min(n,max(1,int(q)//int(p)))
    except (OSError,ValueError):pass
    return max(1,n)

def make_case(seed_index,case_index,base_seed):
    rng=np.random.default_rng(np.random.SeedSequence([base_seed,seed_index,case_index,7]))
    scenario=SCENARIOS[case_index%len(SCENARIOS)]
    H=[10,60,240][(seed_index+case_index//6)%3]
    a=float(rng.choice([.2,.4,.6]));kappa=float(rng.choice([.5,1.,1.5]))
    qmax=float(rng.choice([.9,.97]))*(1-a)/kappa
    total=qmax*rng.uniform(.05,.99);K=int(rng.choice([1,2,4,8]))
    weights=rng.dirichlet(np.full(K,.6))*total
    eta=10**rng.uniform(-6 if scenario=='very_slow_memory' else -2,0,K)
    if case_index%5==0:eta[:max(1,K//2)]=eta[0]  # merged/shared-memory challenge
    future=weights.copy()
    if scenario=='future_regime_change':future*=qmax*.995/max(total,1e-12)
    rho=float(rng.uniform(.2,.45)) if scenario=='correlated_gaussian' else 0.
    c=Contract(H=H,a=a,kappa=kappa,qmax=qmax,sigma=float(rng.choice([.005,.02,.08])),
        budget=float(rng.choice([.5,1.,2.])),service_fee=float(rng.choice([.003,.02,.08])))
    g_obs=float(response(weights,eta,H,a,kappa).sum());g_future=float(response(future,eta,H,a,kappa).sum())
    assert c.gain_min-1e-10<=g_future<=c.gain_max+1e-10
    assert c.price>c.flow_bound*c.gain_max
    return dict(case_id=f's{seed_index:03d}_c{case_index:03d}',seed_index=seed_index,case_index=case_index,
        scenario=scenario,contract=asdict(c),q=weights.tolist(),future_q=future.tolist(),eta=eta.tolist(),
        K=K,observation_gain=g_obs,future_gain=g_future,rho=rho,rho_upper=.5 if rho else 0.,
        observation_seed=[base_seed,seed_index,case_index,19],noise_family='t3_scalar_reset_sum' if scenario=='finite_variance_t3' else 'gaussian_scalar_reset_sum')

def mom_parameters(N,gamma):
    k=int(np.ceil(8*np.log(1/gamma)));k+=1-k%2
    return k,N//k

def sufficient_statistics(case,N,trials):
    c=Contract(**case['contract']);rng=np.random.default_rng(np.random.SeedSequence(case['observation_seed']+[N]))
    v=c.H*c.sigma**2*(1+(c.H-1)*case['rho'])
    if case['scenario']=='finite_variance_t3':errors=rng.standard_t(3,size=(trials,N))/np.sqrt(3)
    else:errors=rng.standard_normal((trials,N))
    X=case['observation_gain']+np.sqrt(v)*errors
    if case['scenario']=='biased_readings':X-=.02*c.H
    mean=X.mean(1);sd=X.std(1,ddof=1);k,m=mom_parameters(N,c.gamma)
    median=np.median(X[:,:k*m].reshape(trials,k,m).mean(2),axis=1) if m else np.zeros(trials)
    return dict(mean=mean,sd=sd,mom=median),v

def certificates(stats,c,method,variance_upper):
    mean=stats['mean'];used=True;reason=''
    if method=='gaussian_iid':raw=mean+c.z*c.se
    elif method=='gaussian_rational_margin':raw=mean+2.1*c.se
    elif method=='gaussian_variance_bound':raw=mean+c.z*np.sqrt(variance_upper/c.N)
    elif method=='student_t_projection':raw=mean+t.ppf(1-c.gamma,c.N-1)*stats['sd']/np.sqrt(c.N)
    elif method=='full_ellipsoid_iid':raw=mean+c.se*np.sqrt(chi2.ppf(1-c.gamma,c.H))
    elif method=='point_uncertified':raw=mean
    elif method=='median_of_means':
        k,m=mom_parameters(c.N,c.gamma)
        if not m:
            raw=np.full_like(mean,c.gain_max);used=False;reason='N below the proved block-count requirement; paid prior-bound fallback'
        else:raw=stats['mom']+2*np.sqrt(variance_upper/m)
    else:raise ValueError(method)
    return np.clip(raw,c.gain_min,c.gain_max),used,reason

def method_valid(case,method,used):
    if not used:return True  # prior-only bound ignores faulty observations
    scenario=case['scenario']
    if scenario in ['biased_readings','future_regime_change']:return False
    if method=='point_uncertified':return False
    if scenario=='finite_variance_t3':return method=='median_of_means'
    if scenario=='correlated_gaussian':return method in ['student_t_projection','median_of_means','gaussian_variance_bound']
    return True

def one_case(job):
    case,trials,runhash,folder=job;start=time.perf_counter();folder=Path(folder)
    jp=folder/(case['case_id']+'.json');ap=folder/(case['case_id']+'.npz')
    if jp.exists():
        old=json.loads(jp.read_text())
        if old.get('run_hash')==runhash and ap.exists() and old.get('statistics_sha256')==sha(ap):return dict(case_id=case['case_id'],cached=True)
        raise ValueError('Checkpoint differs from configuration/code or is corrupt: '+str(jp))
    rows=[];arrays={};base=Contract(**case['contract']);G=case['future_gain']
    for N in [8,32,128]:
        stats,actual_v=sufficient_statistics(case,N,trials)
        for key,x in stats.items():arrays[f'N{N}_{key}']=x
        for multiplier in [0.,1.,5.]:
            c=replace(base,N=N,reset_fee=multiplier*(.0005+.000025*base.H))
            nd=no_data_randomized(c);F=c.info_fee
            var_upper=c.H*c.sigma**2*(1+(c.H-1)*case['rho_upper'])
            common=dict(case_id=case['case_id'],seed_index=case['seed_index'],scenario=case['scenario'],H=c.H,N=N,
                K=case['K'],information_multiplier=multiplier,reset_fee=c.reset_fee,budget=c.budget,
                service_fee=c.service_fee,true_gain=G,no_data_same_error_value=nd['value'],trials=trials,
                simultaneous_deployment=False)
            for method in METHODS:
                affordable=F<=min(c.budget,c.wealth)
                if not affordable:
                    I=nd['mean_units'];value=nd['value'];viol=c.gamma if risk_reserve(nd['free_units'],G,c)>c.budget+1e-10 else 0.
                    row=dict(common,policy=method,affordable=False,information_fee_paid=0.,contract_valid=True,
                        used_measurements=False,fallback='No purchase; optimal same-error no-data lottery',
                        mean_units=I,mean_net_value=value,net_advantage=0.,MC_standard_error=0.,
                        unsafe_action_rate=float(viol),unsafe_count=None,gain_coverage=None,binomial_p=None)
                else:
                    cert,used,why=certificates(stats,c,method,var_upper)
                    I=position(cert,c,F);V=net_value(I,c,F);loss=risk_reserve(I,G,c,F)
                    count=int(np.count_nonzero(loss>c.budget+1e-10));valid=method_valid(case,method,used)
                    row=dict(common,policy=method,affordable=True,information_fee_paid=F,contract_valid=valid,
                        used_measurements=used,fallback=why,mean_units=float(I.mean()),mean_net_value=float(V.mean()),
                        net_advantage=float(V.mean()-nd['value']),MC_standard_error=float(V.std(ddof=1)/np.sqrt(trials)),
                        unsafe_action_rate=count/trials,unsafe_count=count,gain_coverage=float((cert>=G).mean()),
                        binomial_p=float(binomtest(count,trials,c.gamma,alternative='greater').pvalue) if valid else None)
                rows.append(row)
            safe=float(position(G,c));free=nd['free_units']
            rows.append(dict(common,policy='oracle_same_error',affordable=True,information_fee_paid=0.,contract_valid=True,
                used_measurements=False,fallback='Oracle knows future response; no future shocks',
                mean_units=(1-c.gamma)*safe+c.gamma*free,
                mean_net_value=float((1-c.gamma)*gross_value(safe,c)+c.gamma*gross_value(free,c)),
                net_advantage=float((1-c.gamma)*gross_value(safe,c)+c.gamma*gross_value(free,c)-nd['value']),
                MC_standard_error=0.,unsafe_action_rate=c.gamma if risk_reserve(free,G,c)>c.budget+1e-10 else 0.,
                unsafe_count=None,gain_coverage=None,binomial_p=None))
    tmp=Path(str(ap)+'.tmp')
    with tmp.open('wb') as f:np.savez_compressed(f,**arrays)
    os.replace(tmp,ap)
    atomic_json(jp,dict(run_hash=runhash,case=case,rows=rows,statistics_sha256=sha(ap),elapsed_seconds=time.perf_counter()-start))
    return dict(case_id=case['case_id'],cached=False)

def holm(values):
    p=np.asarray(values,float);order=np.argsort(p);out=np.empty(len(p));prev=0.
    for j,i in enumerate(order):prev=max(prev,min(1.,(len(p)-j)*p[i]));out[i]=prev
    return out

def run_suite(out,config,source_hash):
    out=Path(out);folder=out/'checkpoints';folder.mkdir(parents=True,exist_ok=True)
    scientific={k:v for k,v in config.items() if k!='workers'}
    runhash=hashlib.sha256((canonical(scientific)+source_hash).encode()).hexdigest()
    jobs=[]
    for seed in range(config['seeds']):
        for caseid in range(config['cases_per_seed']):jobs.append((make_case(seed,caseid,config['base_seed']),config['trials'],runhash,str(folder)))
    if config['workers']<=1:
        for j,job in enumerate(jobs):
            one_case(job)
            if j%10==0:print(f'Completed case {j+1}/{len(jobs)}',flush=True)
    else:
        with ProcessPoolExecutor(max_workers=config['workers']) as ex:
            fs=[ex.submit(one_case,j) for j in jobs]
            for j,f in enumerate(as_completed(fs)):
                f.result()
                if (j+1)%12==0 or j+1==len(jobs):print(f'Completed case {j+1}/{len(jobs)}',flush=True)
    rows=[]
    for case,_,_,_ in jobs:rows.extend(json.loads((folder/(case['case_id']+'.json')).read_text())['rows'])
    df=pd.DataFrame(rows);mask=df.binomial_p.notna();df['holm_p']=np.nan
    df.loc[mask,'holm_p']=holm(df.loc[mask,'binomial_p'])
    df.to_csv(out/'all_policy_results.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    grouped=df.groupby(['scenario','policy'],dropna=False).agg(cases=('case_id','nunique'),
        rows=('case_id','size'),mean_advantage=('net_advantage','mean'),median_advantage=('net_advantage','median'),
        mean_unsafe_rate=('unsafe_action_rate','mean'),fraction_contract_valid=('contract_valid','mean'),
        fraction_affordable=('affordable','mean'))
    grouped.to_csv(out/'scenario_policy_summary.csv')
    seedmeans=df.groupby(['scenario','policy','seed_index']).net_advantage.mean().reset_index()
    rng=np.random.default_rng(config['base_seed']+900);ci=[]
    for (scenario,policy),g in seedmeans.groupby(['scenario','policy']):
        x=g.net_advantage.to_numpy();sample=rng.choice(x,size=(config['bootstrap'],len(x)),replace=True).mean(1)
        ci.append(dict(scenario=scenario,policy=policy,seeds=len(x),mean=float(x.mean()),lower=float(np.quantile(sample,.025)),upper=float(np.quantile(sample,.975)),
            interpretation='Exploratory seed-cluster percentile bootstrap over the specified simulator design, not external market uncertainty'))
    pd.DataFrame(ci).to_csv(out/'seed_cluster_intervals.csv',index=False)
    metrics=dict(case_count=len(jobs),policy_rows=len(df),reading_repetitions_per_case_N=config['trials'],
        seeds=config['seeds'],holm_tests=int(mask.sum()),holm_rejections=int((df.loc[mask,'holm_p']<.05).sum()),
        unavailable_purchases=int((~df.affordable).sum()),negative_advantage_rows=int((df.net_advantage<0).sum()),
        note='Cost/N/policy rows reuse readings. Raw sufficient statistics plus every checkpoint and source hash are retained. Seed clusters are the uncertainty units, not policy rows.')
    atomic_json(out/'synthetic_status.json',metrics)
    return df,metrics
