"""Advanced research runner: checkpoints, proof audit, stress and optional quotes."""
import argparse,hashlib,json,os,platform,subprocess,sys,time,traceback,zipfile
from pathlib import Path
from dataclasses import replace
import numpy as np
import pandas as pd
import scipy
from scipy.stats import norm
from model import Contract,pair_testing,position,net_value,no_data_randomized
from study import PROFILES,run_suite,usable_cpus,atomic_json,sha
import proof_audit

HERE=Path(__file__).resolve().parent
def source_files():
    return sorted(p for p in HERE.rglob('*') if p.is_file() and p.suffix in {'.py','.md','.tex','.lean','.json','.txt'} and '__pycache__' not in p.parts and 'validation' not in p.parts and p.name!='EMBEDDED_SOURCE.json')
def source_digest():
    return hashlib.sha256(''.join(str(p.relative_to(HERE))+':'+sha(p)+'\n' for p in source_files()).encode()).hexdigest()

def identification_audit(out,config):
    rng=np.random.default_rng(config['base_seed']+301);rows=[]
    for H in [4,10,60,240]:
      for delta in [.08,.04,.02,.01,.005,.0025]:
        base=pair_testing(delta,H=H)
        for sigma in [.005,.02,.08]:
            distance=base['distance'];required=(2*sigma*norm.ppf(.95)/distance)**2
            for N in [32,128,500]:
                strength=np.sqrt(N)*distance/(2*sigma)
                # Exact projected likelihood statistic for the FULL H-tap Gaussian experiment.
                ea=float((rng.standard_normal(config['trials'])>strength).mean())
                eb=float((rng.standard_normal(config['trials'])<-strength).mean())
                rows.append(dict(H=H,delta=delta,sigma=sigma,N=N,full_vector_distance=distance,
                    exact_minimax_error=float(norm.cdf(-strength)),simulated_error_A=ea,simulated_error_B=eb,
                    resets_for_95_percent=required,independent_tap_readings=required*H,
                    illustrative_fee_requirement=required*(.0005+.000025*H),contract='Gaussian fixed impulse query only'))
    a=pd.DataFrame(rows);a.to_csv(Path(out)/'identification_power.csv',index=False);return a

def figures(out,frame,hard):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out=Path(out)
    means=frame[frame.policy!='oracle_same_error'].groupby(['scenario','policy']).net_advantage.mean().unstack()
    fig,ax=plt.subplots(figsize=(11,5));v=means.to_numpy();lim=max(.01,np.nanmax(abs(v)))
    im=ax.imshow(v,cmap='RdBu',vmin=-lim,vmax=lim,aspect='auto');ax.set_xticks(range(len(means.columns)),means.columns,rotation=30,ha='right',fontsize=8);ax.set_yticks(range(len(means.index)),means.index,fontsize=8)
    valid=frame[frame.policy!='oracle_same_error'].groupby(['scenario','policy']).contract_valid.all().unstack().reindex(index=means.index,columns=means.columns)
    for i in range(len(means.index)):
        for j in range(len(means.columns)):
            if not valid.iloc[i,j]:ax.text(j,i,'×',ha='center',va='center',fontsize=14,color='black')
    ax.set_title('× includes measurement rules outside their guarantee; extra profit is not a safe improvement',fontsize=9)
    fig.colorbar(im,ax=ax,label='Mean net advantage over same-error no-data (model dollars)');fig.tight_layout();fig.savefig(out/'net_value_by_scenario.png',dpi=140);plt.close(fig)
    x=frame[frame.affordable & frame.unsafe_count.notna()];fig,ax=plt.subplots(figsize=(9,4))
    for valid,g in x.groupby('contract_valid'):ax.scatter(np.arange(len(g)),g.unsafe_action_rate,s=5,alpha=.4,label='Declared contract valid' if valid else 'Outside guarantee')
    ax.axhline(.025,color='black',ls='--',label='Allowed unsafe-action probability');ax.set(xlabel='Diagnostic rows (dependent across costs/policies)',ylabel='Empirical unsafe-action rate');ax.legend();fig.tight_layout();fig.savefig(out/'coverage_failures.png',dpi=140);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4))
    for H,g in hard[(hard.sigma==.02)&(hard.N==32)].groupby('H'):ax.loglog(g.delta,g.resets_for_95_percent,'o-',label=f'H={H}')
    ax.set(xlabel='Cohort separation scale delta',ylabel='Reset experiments for 95% identification');ax.legend();fig.tight_layout();fig.savefig(out/'identification_scaling.png',dpi=140);plt.close(fig)
    c=Contract();rng=np.random.default_rng(20261031);Y=4.998938687136357+c.se*rng.standard_normal(100000);vals=[]
    for fee in np.linspace(0,.025,51):
        cc=replace(c,reset_fee=float(fee));F=cc.info_fee
        if F>cc.budget:vals.append(np.nan);continue
        C=np.clip(Y+2.1*cc.se,cc.gain_min,cc.gain_max)
        vals.append(float(net_value(position(C,cc,F),cc,F).mean()-no_data_randomized(cc)['value']))
    fig,ax=plt.subplots(figsize=(7,4));ax.plot(np.linspace(0,.025,51),vals);ax.axhline(0,color='black',lw=.8)
    ax.set(xlabel='Illustrative all-in reset price',ylabel='Net information value, conservative Gaussian rule');fig.tight_layout();fig.savefig(out/'information_cost_frontier.png',dpi=140);plt.close(fig)

def make_report(out,status):
    out=Path(out);text=['<html><head><meta charset="utf-8"><title>Machine Markets research audit</title><style>body{font:15px system-ui;max-width:1200px;margin:30px auto;padding:20px}table{border-collapse:collapse;font-size:12px}td,th{border:1px solid #ccc;padding:5px}img{max-width:100%}pre{white-space:pre-wrap}</style></head><body>',
        '<h1>Machine Markets: advanced research audit</h1>',
        '<p>Exploratory synthetic audit; novelty, independent proof review and real-market safety remain unestablished. Large computation does not prove the entire paper.</p>',
        '<pre>'+__import__('html').escape(json.dumps(status,indent=2))+'</pre>']
    for name in ['scenario_policy_summary.csv','seed_cluster_intervals.csv']:
        if (out/name).exists():text+=['<h2>'+name+'</h2>',pd.read_csv(out/name).to_html(index=False,escape=True)]
    for name in ['net_value_by_scenario.png','coverage_failures.png','identification_scaling.png','information_cost_frontier.png']:
        if (out/name).exists():text+=['<h2>'+name+'</h2>','<img src="'+name+'">']
    text+=['<p>See exact_witness/ for exact scalar arithmetic and Lean scope; market/ is observational only. All negative rows and checkpoints are retained.</p></body></html>']
    (out/'REPORT.html').write_text('\n'.join(text))

def finalize(out):
    out=Path(out);manifest={str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='manifest.json' and not p.name.endswith('.tmp')}
    atomic_json(out/'manifest.json',manifest);target=out.with_suffix('.zip')
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for name in manifest:z.write(out/name,name)
        z.write(out/'manifest.json','manifest.json')
    with zipfile.ZipFile(target) as z:
        for name,h in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==h,name
    return target

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--profile',choices=PROFILES,default='deep')
    p.add_argument('--workers',type=int,default=0);p.add_argument('--base-seed',type=int,default=20261030)
    p.add_argument('--skip-lean',action='store_true');p.add_argument('--lean-cache',type=Path)
    p.add_argument('--market-csv',type=Path);p.add_argument('--market-metadata',type=Path);a=p.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    config=dict(PROFILES[a.profile],profile=a.profile,base_seed=a.base_seed,workers=min(usable_cpus(),a.workers or usable_cpus()),
        environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,pandas=pd.__version__))
    if config['workers']<1:raise ValueError('At least one worker needed')
    digest=source_digest();configfile=out/'configuration.json'
    if configfile.exists():
        old=json.loads(configfile.read_text());science=lambda x:{k:v for k,v in x.items() if k!='workers'}
        if science(old)!=science(config):raise ValueError('Use a different run directory for a different scientific configuration')
    atomic_json(configfile,config);snap=out/'source_snapshot';snap.mkdir(exist_ok=True)
    for f in source_files():
        q=snap/f.relative_to(HERE);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(f.read_bytes())
    status=dict(status='RUNNING',profile=a.profile,source_sha256=digest,configuration=config,
        novelty_confirmed=False,full_paper_proved=False,independent_implementation=False,
        python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,pandas=pd.__version__)
    atomic_json(out/'run_status.json',status);failed=False
    try:
        checks=subprocess.run([sys.executable,'-m','unittest','-v','test_theory','test_advanced'],cwd=HERE,text=True,capture_output=True)
        (out/'tests.log').write_text(checks.stdout+checks.stderr);status['tests_returncode']=checks.returncode
        if checks.returncode:raise RuntimeError('A test failed; tests.log retained')
        print('Tests passed. Running exact witness and scoped Lean certificates.',flush=True)
        receipt=proof_audit.run(out/'exact_witness',not a.skip_lean,a.lean_cache);status['lean_status']=receipt['status']
        print('Proof audit:',receipt['status'],'(scalar certificates only)',flush=True)
        frame,metrics=run_suite(out,config,digest);status['synthetic']=metrics
        hard=identification_audit(out,config);figures(out,frame,hard)
        if a.market_csv:
            if not a.market_metadata:raise ValueError('Metadata JSON is required for real quote data')
            from market import evaluate
            status['market']=evaluate(a.market_csv,a.market_metadata,out/'market',bootstrap=config['bootstrap'])
        else:status['market']=dict(status='NOT_RUN',reason='No event-level best-quote CSV and metadata supplied',formal_certificate=False)
        status['status']='COMPLETED_EXPLORATORY' if receipt['status']!='FAILED' else 'COMPLETED_WITH_FORMAL_FAILURE'
    except Exception:
        failed=True;status['status']='FAILED';(out/'failure.log').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True)
    finally:
        status['elapsed_seconds']=time.perf_counter()-start;atomic_json(out/'run_status.json',status)
        make_report(out,status);archive=finalize(out);print(json.dumps(dict(status=status['status'],archive=str(archive),elapsed_seconds=status['elapsed_seconds'])),flush=True)
    if failed:raise SystemExit(1)

if __name__=='__main__':main()
