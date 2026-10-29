"""Run all declared exploratory tests and export a verifiable return archive."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,platform,shutil,subprocess,sys,traceback,zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from experiments import run,information_frontier,paired_intervals
from verify_lean import verify

ROOT=Path(__file__).resolve().parent


def write_json(p,d):p.write_text(json.dumps(d,indent=2,default=str,allow_nan=False))


def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',choices=['smoke','full'],default='full')
    p.add_argument('--seed',type=int,default=20261029);p.add_argument('--out',required=True)
    p.add_argument('--market-csv');p.add_argument('--lean',choices=['skip','check','install'],default='check')
    p.add_argument('--lean-cache');a=p.parse_args()
    out=Path(a.out).resolve()
    if out.exists():raise ValueError('output directory already exists; preserve every prior run')
    out.mkdir(parents=True);status={'status':'RUNNING','independent_validation':False,'profile':a.profile}
    write_json(out/'configuration.json',vars(a)|dict(holding_minutes=60,bar_minutes=1,observed_taps=12,
      observation_contract='independent reset episodes; known a=.4, kappa=1 and sigma=.02; finite candidate class',
      common_training_episodes=768 if a.profile=='full' else 96,
      common_validation_episodes=384 if a.profile=='full' else 64,
      reset_observation_count='N additional episodes, each with 12 independent Gaussian noisy taps',
      disclosure='verified minimum-memory band, width .05; hypothetical fixed cost $0.01 per account episode',
      note='Finite-horizon expected-log utility; NOT an implementation of the published infinite-horizon Kelly theorems.'))
    sources=out/'source_snapshot';sources.mkdir()
    for f in ROOT.rglob('*'):
        if f.is_file() and f.suffix in ['.py','.md','.tex','.lean','.json','.txt','.csv','.pdf','.c'] and not any(x in f.parts for x in ['__pycache__','results','validation']):
            dest=sources/f.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
    write_json(out/'environment.json',dict(python=sys.version,platform=platform.platform(),numpy=np.__version__,pandas=pd.__version__,utc=datetime.now(timezone.utc).isoformat()))
    try:
        t=subprocess.run([sys.executable,'-m','pytest','-q',str(ROOT/'test_package.py')],cwd=ROOT,capture_output=True,text=True)
        (out/'tests.log').write_text(t.stdout+'\n'+t.stderr)
        status['tests_returncode']=t.returncode
        if t.returncode:raise RuntimeError('targeted tests failed; results not eligible for interpretation')
        print('Tests passed. Running all declared regimes...',flush=True)
        rows,decisions,contrasts=run(a.profile,a.seed)
        rows.to_csv(out/'account_results.csv',index=False);decisions.to_csv(out/'information_decisions.csv',index=False)
        contrasts.to_csv(out/'paired_contrasts.csv',index=False)
        paired_intervals(contrasts,a.seed+1).to_csv(out/'paired_intervals.csv',index=False)
        information_frontier().to_csv(out/'identification_witness.csv',index=False)
        summary=rows.groupby(['regime','N','budget','policy'],as_index=False).mean(numeric_only=True)
        summary.to_csv(out/'policy_summary.csv',index=False)
        fig,ax=plt.subplots(figsize=(10,5),layout='constrained')
        sel=summary[(summary.regime=='moderate_feedback')&(summary.N==summary.N.max())]
        for pol,d in sel.groupby('policy'):
            ax.plot(d.inventory,d.mean_log_wealth,marker='o',label=pol)
        ax.set(xlabel='Average inventory (units)',ylabel='Mean log terminal wealth / initial wealth',title='Exploratory synthetic decision comparison; all policies shown')
        ax.legend(fontsize=7,ncol=2);fig.savefig(out/'growth_capacity.png',dpi=160);plt.close(fig)
        if a.market_csv:
            from market import evaluate
            status['market']=evaluate(a.market_csv,out)
        else:status['market']={'status':'NOT_RUN','reason':'No market CSV supplied; all primary outputs are synthetic.'}
        if a.lean=='skip':status['lean']={'status':'NOT_RUN','reason':'Explicitly skipped'}
        else:
            try:status['lean']=verify(out/'formal',a.lean=='install',a.lean_cache)
            except Exception as exc:
                status['lean']={'status':'FAILED','reason':str(exc)}
                (out/'lean_failure.log').write_text(traceback.format_exc())
        status['status']='COMPLETED_EXPLORATORY' if status['lean'].get('status') in ['PASS_PARTIAL_LOGICAL_CORE','NOT_RUN'] else 'COMPLETED_WITH_FORMAL_CHECK_FAILURE'
        status['row_counts']={'account_results':len(rows),'information_decisions':len(decisions),'paired_contrasts':len(contrasts)}
    except Exception as exc:
        status.update(status='FAILED',error=str(exc));(out/'failure.log').write_text(traceback.format_exc())
    finally:
        write_json(out/'run_status.json',status)
        write_json(out/'scientific_status.json',dict(
          experiment='exploratory; neither independently preregistered nor independently replicated',
          novelty='PENDING_SPECIALIST_COMPARISON',general_identification_vs_decision_rate='NOT_PROVED_BY_THIS_RUN',
          statistical_coverage='written Gaussian union-bound argument; not Lean formalized',
          market_transfer='NOT_ESTABLISHED',dynamic_inventory='NOT_TESTED',endogenous_market_policy='NOT_TESTED',
          publication_rating='NOT_INFERRED',paper_population='DISABLED: blank templates are preserved',
          future_work='compare genuine OFI/depth baselines on appropriate data; independent proofs and external replication'))
        manifest={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file()}
        write_json(out/'manifest.json',manifest)
        archive=out.with_suffix('.zip')
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for f in sorted(out.rglob('*')):
                if f.is_file():z.write(f,f.relative_to(out))
        print(json.dumps(status,indent=2));print('RETURN_ZIP='+str(archive),flush=True)
    return 1 if status['status']=='FAILED' else 0


if __name__=='__main__':sys.exit(main())
