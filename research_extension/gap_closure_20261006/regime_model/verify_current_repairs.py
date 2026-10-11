"""Scoped source-to-field checks; cannot certify the full newer manuscript."""
from pathlib import Path
import json,re,hashlib
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;ROOT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def block(txt,label):
 pos=txt.index('\\label{'+label+'}');start=max(txt.rfind('\\begin{table}',0,pos),txt.rfind('\\begin{longtable}',0,pos));end=txt.find('\\end{longtable}',pos) if txt[start:].startswith('\\begin{longtable}') else txt.find('\\end{table}',pos);return txt[start:end]
def rows(txt):
 if '\\endfoot' in txt:txt=txt.split('\\endfoot',1)[1]
 else:txt=txt.split('\\midrule',1)[1].split('\\bottomrule',1)[0]
 return [[re.sub(r'\s+',' ',c).strip() for c in line.rstrip()[:-2].split('&')] for line in txt.splitlines() if '&' in line and line.rstrip().endswith('\\\\')]
def run():
 d=json.loads((HERE/'market_results.json').read_text());e=json.loads((BASE/'event_study/event_results.json').read_text());paper=ROOT/'paper/Machine_Markets_JF_Submission.tex';supp=HERE/'Machine_Markets_Regime_Review_20261007.tex';checks=[]
 def check(path,label,expected,result,fields):
  actual=rows(block(path.read_text(),label));assert actual==expected,(label,actual,expected)
  checks.append({'source':str(path.relative_to(ROOT)),'source_sha256':sha(path),'label':label,'cells':sum(map(len,actual)),'rows':len(actual),'status':'ROW_FIELD_RENDERING_MATCH','result':str(result.relative_to(ROOT)),'result_sha256':sha(result),'field_derivation':fields})
 expected=[]
 for name,ds in d['datasets'].items():
  asset,state=name.split('_',1)
  for key,v in ds['specifications'].items():
   f=v['selected'];ll=[r['log_likelihood'] for r in v['starts']]
   expected.append([asset,'EMA' if state=='x' else 'Return',f'{float(key.split("_")[0]):.0e}','Variance' if f['shared_beta'] else 'Full',f"{v['residual_sd_ratio']:.3f}",f"{f['variance'][0]:.6g}",str(sum(r['status']=='CONVERGED' for r in v['starts'])),f'{max(ll)-min(ll):.3g}'])
 check(supp,'tab:regime_floor_sensitivity',expected,HERE/'market_results.json','datasets.{asset}_{state}.specifications.{floor}_{mode}: residual_sd_ratio, selected.variance[0], starts.status convergence count, max/min starts.log_likelihood')
 expected=[]
 for name,ds in d['datasets'].items():
  asset,state=name.split('_',1)
  for key,label in [('variance_only','Variance--OLS'),('coefficients_and_variance','Full--OLS'),('full_minus_variance_only','Full--variance')]:
   a=ds['summary'][key]['mse'];b=ds['summary'][key]['negative_log_score'];expected.append([asset,'EMA' if state=='x' else 'Return',label,f"{a['mean']:.4f}",f"[{a['ci95'][0]:.4f}, {a['ci95'][1]:.4f}]",f"{b['mean']:.4f}",f"[{b['ci95'][0]:.4f}, {b['ci95'][1]:.4f}]"])
 check(supp,'tab:regime_market_rebuilt',expected,HERE/'market_results.json','datasets.{asset}_{state}.summary.{comparison}.{mse,negative_log_score}.{mean,ci95}')
 expected=[]
 for v in e['variants']['observed']['monthly']['Q']['contrasts']:
  f=v['references']['date_cluster'];expected.append([v['period'],str(v['event_month']),f"{f['beta']:.7f}",f"{f['se']:.7f}",f"{f['p_t']:.4g}"])
 check(paper,'tab:dynamic_event_study',expected,BASE/'event_study/event_results.json','variants.observed.monthly.Q.contrasts[*]: period,event_month,references.date_cluster.{beta,se,p_t}')
 old=json.loads((BASE/'claim_lineage.json').read_text());out={'status':'SCOPED_RENDERING_VERIFIED_FULL_CURRENT_SOURCE_REVIEW_OPEN','checks':checks,'cells':sum(c['cells'] for c in checks),'current_main_source_sha256':sha(paper),'prior_main_lineage_source_sha256':old['source_sha256'],'prior_lineage_applies_to_current_main_source':old['source_sha256']==sha(paper),'limits':['373 scoped cells, not all current manuscript tables','Does not certify causal identification, model validity, theorem novelty or financial policy guarantees','Prior29-table ledger applies only to its original source hashes']}
 assert out['cells']==373
 (HERE/'current_repairs_lineage.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['cells'])
if __name__=='__main__':run()
