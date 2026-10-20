"""Independent witnesses and source-bound comparisons. Does not rewrite upstream outputs.
Ablation changes only a parsed in-memory AST: removes the ORIUS-only post-dynamics state clamp.
It retains the simulator's controller-specific actuator convention, which is a separate limitation.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,datetime
import numpy as np
import pandas as pd
OUT=Path(__file__).resolve().parent
G=Path('/Volumes/T9/gridpulse');sys.path.insert(0,str(G/'src'))
from orius.kbound.crash_free_governor import AnytimeEProcessGate
from orius.kbound.mind import evaluate_kbound_mind
p=G/'experiments/orius_foundations/six_domain_crash_free_validation.py'
source=p.read_text(); tree=ast.parse(source)
# Match only the simulator if containing the x_next boundary assignment.
removed=[]
class RemoveClamp(ast.NodeTransformer):
 def visit_If(self,node):
  if node.lineno==478:
   assert ast.unparse(node.test)=="controller == 'orius_kbound_crash_free'"
   assert 'x_next = cfg.x_max - 0.0001' in ast.unparse(node)
   removed.append({'start':node.lineno,'end':node.end_lineno});return ast.Pass()
  return self.generic_visit(node)
patched=RemoveClamp().visit(tree);ast.fix_missing_locations(patched)
assert len(removed)==1
spec=importlib.util.spec_from_file_location('audited_original',p);mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
ns=dict(mod.__dict__);exec(compile(patched,str(p)+'::without_state_clamp','exec'),ns)
report=json.loads((G/'reports/orius_foundations/six_domain_crash_free_report.json').read_text())
records=[]
for domain,cfg in mod.DOMAIN_CONFIGS.items():
 d=pd.read_csv(G/report['datasets'][domain]['processed_csv']); sig=d.iloc[:,1].to_numpy(dtype=float)
 for regime in ['hallucination','unbounded_blackout','byzantine_spoof','compound_shift']:
  for seed in [42,43,44,45,46]:
   original=mod.simulate_controller_episode(cfg,sig,'orius_kbound_crash_free',regime,seed,400)
   altered=ns['simulate_controller_episode'](cfg,sig,'orius_kbound_crash_free',regime,seed,400)
   records.append({'domain':domain,'regime':regime,'seed':seed,'steps':400,'original_violations':original['violations'],'unclamped_violations':altered['violations'],'original_crashed':original['crashed'],'unclamped_crashed':altered['crashed']})
 pd.DataFrame(records).to_csv(OUT/'orius_state_clamp_ablation.csv',index=False)
 print(domain,'done',flush=True)
g0=AnytimeEProcessGate(alpha=.05,bet_fraction=.5)
g1=AnytimeEProcessGate(alpha=.05,bet_fraction=.5)
w0=g0.update(0).e_value;w1=g1.update(100).e_value
expected=.95*w0+.05*w1
missing=evaluate_kbound_mind(reliability_w=1,delta_hat=.3,calib_residuals=None)
# AST provenance of fixed-MSE rows, without running a generator that rewrites research outputs.
hp=G/'experiments/orius_foundations/hardware_and_ablation_closure.py';ht=ast.parse(hp.read_text())
fn=next(n for n in ht.body if isinstance(n,ast.FunctionDef) and n.name=='run_gap_g12_two_regime_tta')
assign=next(n for n in fn.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='rows' for t in n.targets))
fixed=ast.literal_eval(assign.value)
out={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest(),str(hp):hashlib.sha256(hp.read_bytes()).hexdigest()},'clamp_removed_ast_nodes':removed,'episodes':len(records),'steps':sum(r['steps'] for r in records),'original_violations':sum(r['original_violations'] for r in records),'unclamped_violations':sum(r['unclamped_violations'] for r in records),'unclamped_failed_episodes':sum(r['unclamped_crashed'] for r in records),'one_step_eprocess_null_counterexample':{'exceedance_probability':.05,'nonexceed_wealth':w0,'exceed_wealth':w1,'expected_wealth':expected,'supermartingale_initial_wealth':1,'violation':expected>1},'missing_calibration_witness':{'decision':missing.kga_decision,'n_calibration':missing.n_calibration,'delta_hat':.3,'actual_records_supplied':0},'tta_fixed_literal_rows':fixed,'reported_h5':report['hypotheses']['H5_realtime_microsecond_execution'],'limits':['Ablation is a counterfactual code diagnostic, not an independent plant experiment.','Original reference signals and simulator dynamics retained; no seven-domain hardware or trading-account validity inferred.','The default calibration witness supplies a hypothetical benefit estimate; it does not establish the estimate was valid.']}
(OUT/'cross_project_evidence_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['tta_fixed_literal_rows','reported_h5','source_sha256']},indent=2))
