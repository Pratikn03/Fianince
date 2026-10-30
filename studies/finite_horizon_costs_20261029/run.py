"""Run the frozen synthetic study; export every result and a return ZIP."""
import argparse,hashlib,json,platform,subprocess,sys,zipfile,gzip
from pathlib import Path
from dataclasses import replace,asdict
import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.stats import norm
import scipy
from model import *

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def safe_json(v):
    if isinstance(v,np.generic):return v.item()
    if isinstance(v,Path):return str(v)
    raise TypeError(type(v).__name__)
def expected_value(g,c,kind='functional',fee=None):
    F=c.info_fee if fee is None else fee
    if F>min(c.budget,c.wealth):return (None,None)
    def fn(z):
        cert=gain_certificate(g+c.se*z,c,kind)
        return float(net_value(position(cert,c,F),c,F))*norm.pdf(z)
    v,e=quad(fn,-12,12,epsabs=1e-10,epsrel=1e-10,limit=150)
    return float(v),float(e)

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    p.add_argument('--profile',choices=['smoke','full'],default='full');p.add_argument('--seed',type=int,default=20261030)
    args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    tests=subprocess.run([sys.executable,'-m','unittest','-v','test_theory'],cwd=HERE,text=True,capture_output=True)
    (out/'tests.log').write_text(tests.stdout+tests.stderr)
    if tests.returncode:raise SystemExit('Theorem checks failed; inspect tests.log')
    c=Contract();rng=np.random.default_rng(args.seed);R=20000 if args.profile=='full' else 2000
    hard=pd.DataFrame([pair_testing(d) for d in [.08,.04,.02,.01,.005,.0025]])
    hard['information_cost_lower']=hard.N_required*c.reset_fee
    hard['within_loss_budget']=hard.information_cost_lower<=c.budget
    hard.to_csv(out/'hard_pair_requirements.csv',index=False)
    h=response([.2,.2],[.49,.51],c.H);g=float(h.sum());bound=guarantees(g,c)
    observed=g+c.se*rng.standard_normal(R);rows=[];summary=[]
    for kind in ['functional','linear_functional_projection','ellipsoid','point']:
        cert=gain_certificate(observed,c,kind);I=position(cert,c,c.info_fee)
        V=net_value(I,c,c.info_fee);reserve=risk_reserve(I,g,c,c.info_fee)
        pd.DataFrame(dict(rep=np.arange(R),policy=kind,certified_gain=cert,units=I,net_expected_service_profit=V,stress_reserve=reserve,reserve_violation=reserve>c.budget+1e-10)).to_csv(out/(kind+'_draws.csv.gz'),index=False,compression={'method':'gzip','mtime':0})
        v,e=expected_value(g,c,kind)
        summary.append(dict(policy=kind,units=float(I.mean()),net_value_MC=float(V.mean()),MC_se=float(V.std(ddof=1)/np.sqrt(R)),net_value_integral=v,integration_error=e,fee=c.info_fee,reserve_violation_rate=float((reserve>c.budget+1e-10).mean()),gain_coverage=float((cert>=g).mean())))
    for name,gain,F in [('no_data_robust',c.gain_max,0.),('oracle_response',g,0.),('targeted_gain_disclosure',g,.05)]:
        I=float(position(gain,c,F));v=float(net_value(I,c,F));summary.append(dict(policy=name,units=I,net_value_MC=v,MC_se=0.,net_value_integral=v,integration_error=0.,fee=F,reserve_violation_rate=float(risk_reserve(I,g,c,F)>c.budget+1e-10),gain_coverage=1.))
    nd_random=no_data_randomized(c);free=nd_random['free_units']
    for name,safe in [('no_data_same_gamma',nd_random['safe_units']),('oracle_same_gamma',float(position(g,c)))]:
        units=(1-c.gamma)*safe+c.gamma*free
        value=(1-c.gamma)*gross_value(safe,c)+c.gamma*gross_value(free,c)
        breach=c.gamma if risk_reserve(free,g,c)>c.budget+1e-10 else 0.
        summary.append(dict(policy=name,units=units,net_value_MC=float(value),MC_se=0.,net_value_integral=float(value),integration_error=0.,fee=0.,reserve_violation_rate=breach,gain_coverage=None))
    primary=pd.DataFrame(summary);primary.to_csv(out/'primary_decisions.csv',index=False)
    nd=bound['no_data_same_gamma_value']
    break_even=brentq(lambda f:expected_value(g,replace(c,reset_fee=f))[0]-nd,0.,.02)
    paid_exact_break=brentq(lambda f:float(net_value(position(g,c,f),c,f))-nd,0.,.9)
    (out/'primary_summary.json').write_text(json.dumps(dict(contract=asdict(c),gain=g,derived_linear_cost=c.b,guarantees=bound,
        expected_information_gain=float(primary.loc[primary.policy=='functional','net_value_integral'].iloc[0]-nd),
        limiting_merged_net_value_lower=guarantees(float(response([.4],[.5],c.H).sum()),c)['net_information_value_lower'],
        per_reset_break_even=break_even,exact_gain_disclosure_break_even=paid_exact_break,
        id_requirement_at_delta_01=hard[hard.delta==.01].iloc[0].to_dict(),noise_repetitions=R,
        novelty_status='UNCONFIRMED',proof_status='WRITTEN_ANALYTIC_PROOF_WITH_CHECKS_NOT_LEAN_OR_INDEPENDENT_REVIEW'),indent=2,default=safe_json)+'\n')
    # All sensitivity rows survive, including cases where purchasing data loses money.
    sensitivity=[]
    Hs=[10,60,240] if args.profile=='full' else [60]
    Ns=[8,32,128] if args.profile=='full' else [32]
    for H in Hs:
      for Q in [.1,.4,.55]:
       for eta in [.02,.2,.5,1.]:
        gain=float(response([Q],[eta],H).sum())
        for N in Ns:
         for fee in [0.,.001,.002,.005,.01,.02,.05]:
          cc=replace(c,H=H,N=N,reset_fee=fee)
          v,e=expected_value(gain,cc)
          ndv=no_data_randomized(cc)['value']
          sensitivity.append(dict(H=H,Q=Q,eta=eta,N=N,reset_fee=fee,service_fee=cc.service_fee,affordable=v is not None,net_value=v,no_data_value=ndv,net_information_value=None if v is None else v-ndv,integration_error=e))
    for service in [.002,.003,.02]:
      for N in Ns:
       for fee in [0.,.001,.002,.005,.01,.02,.05]:
        cc=replace(c,N=N,reset_fee=fee,service_fee=service)
        v,e=expected_value(g,cc);ndv=no_data_randomized(cc)['value']
        sensitivity.append(dict(H=60,Q=.4,eta=.5,N=N,reset_fee=fee,service_fee=service,affordable=v is not None,net_value=v,no_data_value=ndv,net_information_value=None if v is None else v-ndv,integration_error=e))
    pd.DataFrame(sensitivity).to_csv(out/'all_cost_horizon_sensitivities.csv',index=False)
    # Failed assumptions are shown using the correct actual reserve, not a zero realized-breach slogan.
    failures=[];z=rng.standard_normal(R);rho=.2
    for name,mean_g,actual_g,scale,kind in [
      ('iid_valid',g,g,1.,'functional'),
      ('correlated_iid_formula_invalid',g,g,np.sqrt(1+(c.H-1)*rho),'functional'),
      ('correlated_corrected_variance',g,g,np.sqrt(1+(c.H-1)*rho),'corrected_covariance'),
      ('negative_reading_bias_invalid',g-.02*c.H,g,1.,'functional'),
      ('future_feedback_change_invalid',g,float(response([.55],[.5],c.H).sum()),1.,'functional')]:
        cert=gain_certificate(mean_g+c.se*scale*z,c,kind,rho=rho);I=position(cert,c,c.info_fee)
        failures.append(dict(case=name,contract_valid=name in ['iid_valid','correlated_corrected_variance'],gain_coverage=float((cert>=actual_g).mean()),reserve_violation_rate=float((risk_reserve(I,actual_g,c,c.info_fee)>c.budget+1e-10).mean()),mean_units=float(I.mean()),mean_net_service_value=float(net_value(I,c,c.info_fee).mean())))
    failures.append(dict(case='signed_kernel_[1,-.9]_invalid',contract_valid=False,sum_response=.1,true_absolute_gain=1.9))
    pd.DataFrame(failures).to_csv(out/'assumption_failures.csv',index=False)
    # A separate cash-flow audit, using common bounded future tapes for all policies.
    u=rng.uniform(-c.flow_bound,c.flow_bound,(4096,c.H));audit=[]
    for row in summary:
        I=row['units'];F=row['fee'];a=account_path(h,u,I,c,F)
        extreme=account_path(h,np.full((1,c.H),-c.flow_bound),I,c,F)
        identity=c.wealth-F+I*a['price_change'][:,-1]+gross_value(I,c)
        audit.append(dict(policy=row['policy'],note='mean decision used only for accounting audit; primary inference above uses every reading draw',units=I,MC_realized_profit=float((a['terminal']-c.wealth).mean()),exact_conditional_expected_profit=float(net_value(I,c,F)),worst_corner_loss=float(extreme['maximum_loss'][0]),theoretical_stress_reserve=float(risk_reserve(I,g,c,F)),cash_identity_max_error=float(abs(a['terminal']-identity).max())))
    pd.DataFrame(audit).to_csv(out/'cashflow_audit.csv',index=False)
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(1,2,figsize=(10,4))
    ax[0].loglog(hard.delta,hard.N_required,'o-',label='Known-pair cohort test, 95%')
    ax[0].axhline(c.N,color='green',label='Primary decision reading budget')
    ax[0].set(xlabel='Cohort separation scale delta',ylabel='Reset experiments');ax[0].legend(fontsize=8)
    s=pd.DataFrame(sensitivity);ss=s[(s.H==60)&(s.Q==.4)&(s.eta==.5)&(s.service_fee==.08)]
    for N,group in ss.groupby('N'):ax[1].plot(group.reset_fee,group.net_information_value,'o-',label=f'N={N}')
    ax[1].axhline(0,color='black',lw=.8);ax[1].set(xlabel='All-in cost per reset (illustrative dollars)',ylabel='Net information value over no-data');ax[1].legend(fontsize=8)
    fig.tight_layout();fig.savefig(out/'separation_and_net_value.png',dpi=160);plt.close(fig)
    status=dict(status='COMPLETED_SYNTHETIC',profile=args.profile,seed=args.seed,tests_returncode=tests.returncode,
        market_data=False,novelty_confirmed=False,independent_replication=False,lean_full_proof=False,
        methods='Gaussian projection is standard and exactly equals the functional estimator; no new estimation algorithm is claimed',
        frozen_protocol_sha256=sha(HERE/'PROTOCOL.md'),repeated_deployment_warning='single decision only; 100 independent unadjusted decisions have failure chance 1-(1-gamma)^100',
        amendment_sha256=sha(HERE/'DESIGN_AMENDMENT.md'),
        environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,pandas=pd.__version__))
    (out/'run_status.json').write_text(json.dumps(status,indent=2)+'\n')
    snap=out/'source_snapshot';snap.mkdir(exist_ok=True)
    for name in ['model.py','test_theory.py','run.py','PROTOCOL.md','PROOF.tex','LITERATURE.md','README.md','DESIGN_AMENDMENT.md']:
        if (HERE/name).exists():(snap/name).write_bytes((HERE/name).read_bytes())
    manifest={str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='manifest.json'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=out.with_suffix('.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as zz:
        for f in sorted(out.rglob('*')):
            if f.is_file():zz.write(f,str(f.relative_to(out)))
    print(json.dumps(dict(out=str(out),archive=str(archive),primary_summary=json.loads((out/'primary_summary.json').read_text())),default=safe_json))

if __name__=='__main__':main()
