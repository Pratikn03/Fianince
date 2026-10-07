"""Semantic row/cell lineage for the selected revision, without altering freezes.
Checks source rendering against explicitly named output fields, not token matches.
This is an artifact-consistency audit; it does not certify econometric validity.
"""
from pathlib import Path
import csv, hashlib, json, re
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
REV=ROOT/'research_extension/paper_revision_20261006'
SOURCE=ROOT/'paper/Machine_Markets_JF_Submission.tex'
APPENDIX=REV/'full_scope_appendix.tex'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def load(n): return json.loads((REV/'results'/f'{n}.json').read_text())
def norm(s): return re.sub(r'\s+',' ',s).strip()
def cell(value,field,format=None):
    return {'rendered':str(value) if format is None else f'{value:{format}}','field':field}
def interval(v,path,n=5,key='ci95'):
    return cell(f"{v['mean']:.{n}f} [{v[key][0]:.{n}f}, {v[key][1]:.{n}f}]",[path+'.mean',path+'.'+key+'[0]',path+'.'+key+'[1]'])

def inventory(path):
    txt=path.read_text(); out=[]
    for m in re.finditer(r'\\begin\{(table|longtable|figure|theorem|proposition)\}(?:\[[^\]]*\])?',txt):
        env=m.group(1); end=txt.index('\\end{'+env+'}',m.end())+len('\\end{'+env+'}')
        content=txt[m.start():end]
        labels=re.findall(r'\\label\{([^}]+)\}',content)
        caption=re.search(r'\\caption\{(.*?)\}\\',content,re.S) if env=='longtable' else re.search(r'\\caption\{(.*?)\}\s*\\label',content,re.S)
        out.append({'id':labels[0] if labels else f'{path.stem}:{env}:{len(out)+1}', 'environment':env,'labels':labels,
                    'source':str(path.relative_to(ROOT)),'start_line':txt.count('\n',0,m.start())+1,
                    'end_line':txt.count('\n',0,end)+1,'statement_sha256':hashlib.sha256(content.encode()).hexdigest(),
                    'caption':caption.group(1) if caption else None,'content':content})
    return out

def actual_rows(block):
    s=block['content']
    if block['environment']=='longtable': s=s.split('\\endfoot',1)[1]
    else: s=s.split('\\midrule',1)[1].split('\\bottomrule',1)[0]
    return [[norm(c) for c in line.split('&')] for line in s.splitlines() if '&' in line and line.rstrip().endswith('\\\\') for line in [line.rstrip()[:-2]]]

specs={}
def add(key,result,function,rows,scope):
    specs[key]={'result':result,'function':function,'rows':rows,'scope':scope}

cb=load('coinbase_reanalysis'); rows=[]
for a in ['BTC','ETH','ADA']:
    for k,label in [('x_observed','EMA / observed'),('x_forward','EMA / forward'),('return_observed','Return / observed')]:
        v=cb[a]['variants'][k]; p=f'{a}.variants.{k}'
        rows.append([cell(a,'asset'),cell(label,'state/alignment definition'),cell(v['n_days'],p+'.n_days'),interval(v['Q'],p+'.Q'),cell(v['S']['mean'],p+'.S.mean','.4f'),cell(v['max_rho'],p+'.max_rho','.4f')])
add('tab:timing_revised','coinbase_reanalysis','revise_evidence.py:empirical/series/fit_segments/summary',rows,'Recorded April 7–19 data; observational filtered-state diagnostics; provider authentication open')
null=load('mechanical_nulls');rows=[]
for key,label in [('martingale_independent_flow','Independent martingale'),('persistent_exogenous_flow','Persistent exogenous flow'),('order_splitting_with_impact','Order splitting with impact'),('common_news','Common news')]:
    rows.append([cell(label,'cases.'+key)]+[cell(null['cases'][key][timing][metric],f'cases.{key}.{timing}.{metric}','.5f') for timing in ['observed','forward'] for metric in ['mean_Q','sd_Q']])
add('tab:nulls_revised','mechanical_nulls','revise_evidence.py:mechanical_nulls',rows,'Declared simulation nulls; not calibrated market null distributions')
grid=load('sampling_grid');rows=[]
for i,v in enumerate(grid['cells']):
    p=f'cells[{i}]'; rows.append([cell(v['asset'],p+'.asset'),cell(v['delta_seconds'],p+'.delta_seconds'),cell(v['window_seconds'],p+'.window_seconds'),cell(v['mechanical_anchor'],p+'.mechanical_anchor','.4f'),interval(v['Q'],p+'.Q'),cell(v['S']['mean'],p+'.S.mean','.4f'),cell(v['max_rho'],p+'.max_rho','.4f')])
add('tab:grid_revised','sampling_grid','sampling_grid.py:run',rows,'Exploratory sampling/filter grid; all declared nondegenerate cells')
md=load('md_reanalysis');rows=[]
for a in ['BTC','ETH','ADA']:
    v=md[a];rows.append([cell(a,'asset'),cell(v['n_moment_rows'],a+'.n_moment_rows'),cell(v['Q'],a+'.Q','.5f'),cell(v['J_stat'],a+'.J_stat','.2f'),cell(v['p_chi2'],a+'.p_chi2','.3g')])
add('tab:md_revised','md_reanalysis','diagnostics.py:md/covariance_checks',rows,'HAC covariance restrictions; all three reject at 5%; causal validation open')
panel=load('saved_panel_audit');rows=[]
for k,v in panel['pooled'].items():
    rows.append([cell(k,'index'),cell(v['mean'],f'pooled.{k}.mean','.5f'),cell(f"[{v['ci95_date_block'][0]:.5f}, {v['ci95_date_block'][1]:.5f}]",[f'pooled.{k}.ci95_date_block[0]',f'pooled.{k}.ci95_date_block[1]'])])
add('tab:panel_revised','saved_panel_audit','revise_evidence.py:panel_audit',rows,'Saved derived panel; original raw lineage open')
fee=load('fee_reanalysis');rows=[]
for dep in ['Q','S']:
    for k,label in [('classical','Classical OLS'),('asset_cluster','Asset clusters, $t_7$'),('date_cluster','Date clusters, $t_{23}$')]:
        v=fee[dep][k];p=dep+'.'+k
        rows.append([cell(dep,'outcome'),cell(label,p),cell(v['beta'],p+'.beta','.6f'),cell(v['se'],p+'.se','.6f'),cell(v['p_t'],p+'.p_t','.3f'),cell(f"[{v['ci95'][0]:.5f}, {v['ci95'][1]:.5f}]",[p+'.ci95[0]',p+'.ci95[1]'])])
add('tab:fee_revised','fee_reanalysis','revise_evidence.py:intervention/ols',rows,'One treated asset; saved-panel association; causal identification open')
stress=load('threshold_reanalysis');rows=[]
for label,k,n in [('Calm flow slope','flow_slope_calm',4),('Wide-spread flow slope','flow_slope_wide',4),('Slope difference','flow_slope_difference',4),('HAC SE of difference','HAC_se_difference',4),('Normal-reference p','p_normal_reference',3),('Residual SD ratio','residual_sd_ratio',2),('Calm inside-depth mean','calm_depth_mean',2),('Wide-spread inside-depth mean','wide_depth_mean',2)]:
    rows.append([cell(label,'definition'),cell(stress[k],k,f'.{n}f')])
add('tab:stress_revised','threshold_reanalysis','diagnostics.py:threshold_check',rows,'Exploratory first-50000-row subsample; dimensional slopes; no causal bifurcation')
eq=load('equity_reanalysis');rows=[]
for a,v in eq['per_stock'].items():
    p='per_stock.'+a;rows.append([cell(a,'stock ID'),cell(eq['stock_counts'][a],'stock_counts.'+a),cell(v['n_sessions'],p+'.n_sessions'),cell(v['Q_mean'],p+'.Q_mean','.6f'),cell(v['S_mean'],p+'.S_mean','.5f'),cell(v['max_rho'],p+'.max_rho','.5f')])
add('tab:equity_revised','equity_reanalysis','revise_evidence.py:equity',rows,'Supplied identifiers; event clock; provider mapping open')
depth=load('depth_reanalysis');ds=depth['summary']
rows=[[cell('Raw depth records','definition'),cell(depth['n_raw'],'n_raw')],[cell('Dates retained','definition'),cell(ds['n_days'],'summary.n_days')],[cell('Fitted transitions','definition'),cell(ds['n_transitions'],'summary.n_transitions')]]
for label,k in [('Mean $Q$ [date interval]','Q'),('Mean $Q_{30}$ [date interval]','Q30'),('Mean $S$ [date interval]','S')]: rows.append([cell(label,'definition'),interval(ds[k],'summary.'+k)])
rows.append([cell(r'Maximum segment $\rho$','definition'),cell(ds['max_rho'],'summary.max_rho','.5f')])
add('tab:depth_revised','depth_reanalysis','holdout_reanalysis.py:run',rows,'Jan 9–20 previously examined quote-depth sample; provider open')
tr=load('transient_checks');rows=[]
for i,v in enumerate(tr['rows']):
    rows.append([cell(v[k],f'rows[{i}].{k}',fmt) for k,fmt in [('theta','.1f'),('rho','.2f'),('peak_time',None),('M_C','.4f'),('safe_radius','.5f')]])
add('tab:transient_revised','transient_checks','diagnostics.py:transient_checks',rows,'Fixed-coordinate illustrative matrix family; no market calibration')
dealer=load('dealer_reproduction');rows=[]
lookup={(v['S'],v['L'],v['mode']):(i,v) for i,v in enumerate(dealer['cells'])}
for L in [10.,20.]:
    for S in [.5,.6,.7,.8,.9,.95]:
        rho=max(abs(np.linalg.eigvals([[.5,1],[.2*(S-.5),.8]])))
        row=[cell(L,'L','.0f'),cell(S,'S','.2f'),cell(rho,'eig([[a,1],[eta*(S-a),1-eta]])','.4f')]
        for mode in ['feedback','B1','B2','B3']:
            i,v=lookup[S,L,mode];row.append(cell(f"{100*v['rate']:.1f}\\%",f'cells[{i}].rate * 100'))
        rows.append(row)
add('tab:dealer_revised','dealer_reproduction','diagnostics.py:dealer_checks -> simulations/feedback_dealer.py:simulate',rows,'Conditional replay, not independent calibration or historical failure evidence')



# New joint-study rows are anchored to their independent saved fit.
joint= json.loads((HERE/'cross_venue/joint_results.json').read_text())
rows=[]
for a,r in joint['assets'].items():
    for key,label in [('primary','EMA, offset 0'),('raw_return','Return, offset 0'),('cb_offset_minus1','EMA, offset -1s'),('cb_offset_plus1','EMA, offset +1s')]:
        fit=r['variants'][key]['fit'];p=f'assets.{a}.variants.{key}.fit'
        rows.append([cell(a,'asset'),cell(label,'state and clock definition'),cell(fit['n_transitions'],p+'.n_transitions'),cell(fit['n_segments'],p+'.n_segments'),cell(fit['rho'],p+'.rho','.6f')])
add('tab:joint_fit_recovered','joint_results','cross_venue/joint_var.py:aligned_segments/fit_joint',rows,'Independent reconstructed original overlap; recorder identity and causal shock identification remain open')
rows=[]
for a,r in joint['assets'].items():
    v=r['variants']['primary']['decomposition']['horizons']['6'];p=f'assets.{a}.variants.primary.decomposition.horizons.6'
    sh=v['generalized_row_normalized'];lo=v['orthogonal_order_min'];hi=v['orthogonal_order_max']
    rows.append([cell(a,'asset'),cell(100*sh[0][2],p+'.generalized_row_normalized[0][2] * 100','.2f'),cell(f'[{100*lo[0][2]:.2f}, {100*hi[0][2]:.2f}]',[p+'.orthogonal_order_min[0][2] * 100',p+'.orthogonal_order_max[0][2] * 100']),cell(100*sh[2][0],p+'.generalized_row_normalized[2][0] * 100','.2f'),cell(f'[{100*lo[2][0]:.2f}, {100*hi[2][0]:.2f}]',[p+'.orthogonal_order_min[2][0] * 100',p+'.orthogonal_order_max[2][0] * 100'])])
add('tab:joint_fevd_recovered','joint_results','cross_venue/joint_var.py:generalized_fevd/orthogonal_fevd',rows,'Predictive decomposition; ordering ranges are not confidence intervals')
rows=[]
for a,r in joint['assets'].items():
    fit=r['variants']['primary']['fit'];p=f'assets.{a}.variants.primary.fit'
    for key,label in [('J_normalized','$J$'),('covariance_normalized','$\\Sigma$')]:
        for i,row in enumerate(fit[key]):rows.append([cell(a,'asset'),cell(label,'matrix definition'),cell(i+1,'matrix row')]+[cell(v,p+f'.{key}[{i}][{j}]','.6f') for j,v in enumerate(row)])
add('tab:joint_matrices_recovered','joint_results','cross_venue/joint_var.py:fit_joint',rows,'Normalized matrix/covariance; full precision and raw units saved; no structural certification')
for key in ['tab:joint_fit_recovered','tab:joint_fevd_recovered','tab:joint_matrices_recovered']:
    specs[key]['result_path']=HERE/'cross_venue/joint_results.json'


# Fully restored original-panel comparison, including unfavorable return/fee results.
panel_new=json.loads((HERE/'cross_venue/restored_panel_summary.json').read_text());rows=[]
for key,label in [('legacy','Legacy EMA / forward'),('observed','EMA / observed'),('raw_return','Return / observed')]:
    v=panel_new['summaries'][key];p='summaries.'+key
    rows.append([cell(label,'construction definition'),interval(v['Q'],p+'.Q',6,'date_t95'),interval(v['Q30'],p+'.Q30',6,'date_t95') if key!='raw_return' else cell('--','not estimated'),cell(v['S']['mean'],p+'.S.mean','.6f'),cell(100*v['share_Q_positive'],p+'.share_Q_positive * 100','.2f'),cell(v['max_rho'],p+'.max_rho','.6f')])
add('tab:restored_panel_comparison','restored_panel_summary','cross_venue/reproduce_original_panel.py + summarize_restored_panel.py',rows,'Original768 study units; measured diagnostics and descriptive date variation; no identified learning')
rows=[]
for a,v in panel_new['summaries']['observed']['by_asset'].items():
    p='summaries.observed.by_asset.'+a;rv=panel_new['summaries']['raw_return']['by_asset'][a]
    rows.append([cell(a,'asset'),cell(v['Q'],p+'.Q','.7f'),cell(v['Q30'],p+'.Q30','.7f'),cell(rv['Q'],'summaries.raw_return.by_asset.'+a+'.Q','.7f'),cell(v['S'],p+'.S','.6f')])
add('tab:restored_panel_assets','restored_panel_summary','cross_venue/summarize_restored_panel.py:run',rows,'All assets retained under corrected timing; source raw archives checksum verified')
rows=[]
for dep in ['Q','S']:
    for key,label in [('classical','Classical'),('asset_cluster','Asset clusters, $t_7$'),('date_cluster','Date clusters, $t_{23}$')]:
        v=panel_new['fee_observed'][dep][key];p='fee_observed.'+dep+'.'+key
        rows.append([cell(dep,'outcome'),cell(label,'covariance definition'),cell(v['beta'],p+'.beta','.7f'),cell(v['se'],p+'.se','.7f'),cell(v['p_t'],p+'.p_t','.4f'),cell(f"[{v['ci95'][0]:.7f}, {v['ci95'][1]:.7f}]",[p+'.ci95[0]',p+'.ci95[1]'])])
add('tab:restored_panel_fee','restored_panel_summary','cross_venue/summarize_restored_panel.py:fee',rows,'Corrected-timing policy-period association; one treated asset; causal identification open')
for key in ['tab:restored_panel_comparison','tab:restored_panel_assets','tab:restored_panel_fee']:
    specs[key]['result_path']=HERE/'cross_venue/restored_panel_summary.json'

# Each appendix cell has a field-specific derivation too.
def esc(s):
    for a,b in [('&',r'\&'),('%',r'\%'),('_',r'\_'),('#',r'\#')]: s=s.replace(a,b)
    return s
appendix_specs=[]
appendix_specs.append([[cell(esc(a),'symbol')]+[cell(v[k],f'by_asset.{a}.{k}','.7f') for k in ['Q','S','Q30']] for a,v in panel['by_asset'].items()])
rows=[]
for dep in ['Q','S']:
    for k in ['classical','asset_cluster','date_cluster']:
        v=fee[dep][k];p=dep+'.'+k
        rows.append([cell(dep,'outcome'),cell(esc(k),'covariance definition')]+[cell(v[f],p+'.'+f,fmt) for f,fmt in [('beta','.7f'),('se','.7f'),('df',None),('p_t','.5f')]])
appendix_specs.append(rows)
with (REV/'results/event_gaps_descriptive.csv').open() as f: events=list(csv.DictReader(f))
appendix_specs.append([[cell(r['date'],f'row[{i}].date'),cell(float(r['relative_gap_Q']),f'row[{i}].relative_gap_Q','.6f')] for i,r in enumerate(events)])
rows=[]
for i,v in enumerate(dealer['cells']):
    p=f'cells[{i}]';rows.append([cell(v['S'],p+'.S','.2f'),cell(v['L'],p+'.L','.0f'),cell(v['mode'],p+'.mode'),cell(v['halts'],p+'.halts'),cell(v['rate'],p+'.rate','.4f'),cell(f"[{v['ci95_exact'][0]:.4f}, {v['ci95_exact'][1]:.4f}]",[p+'.ci95_exact[0]',p+'.ci95_exact[1]'])])
appendix_specs.append(rows)
with (REV/'results/equity_session_estimates.csv').open() as f:sessions=list(csv.DictReader(f))
appendix_specs.append([[cell(r[k],f'row[{i}].{k}') for k in ['stock','day','raw_rows','n']]+[cell(float(r[k]),f'row[{i}].{k}',fmt) for k,fmt in [('Q','.7f'),('S','.6f'),('rho','.6f')]] for i,r in enumerate(sessions)])
with (REV/'original_page_disposition.csv').open() as f:pages=list(csv.DictReader(f))
appendix_specs.append([[cell(r['original_page'],f'row[{i}].original_page'),cell(esc(r['topic']).replace('/',r'/\allowbreak '),f'row[{i}].topic'),cell(esc(r['action']),f'row[{i}].action')] for i,r in enumerate(pages)])

# Appendix sources are mapped separately; verification of row formatting is explicit.
appendix_results=['saved_panel_audit','fee_reanalysis','event_gaps_descriptive','dealer_reproduction','equity_session_estimates','original_page_disposition']
appendix_functions=['revise_evidence.py:panel_audit','revise_evidence.py:intervention/ols','revise_evidence.py:intervention','diagnostics.py:dealer_checks','revise_evidence.py:equity','original_page_disposition.csv (documented audit, not numeric economic evidence)']

inputs=[]
rawcheck=load('raw_input_verification')
for a,v in rawcheck.items():
    for kind,path,key in [('raw',ROOT/'empirical_pipeline/data'/f'{a}_1sec.csv','raw_sha256'),('cache',ROOT/'empirical_pipeline/cache'/f'{a}_1sec_core_v2dedup.pkl','cache_sha256')]:
        current=sha(path);inputs.append({'asset':a,'kind':kind,'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':current,'matches_reconstruction_receipt':current==v[key],'provider_authenticated':False})
for path in [ROOT/'results/provenance/binance_panel_results.json',ROOT/'empirical_pipeline/fi2010/data/data.csv',ROOT/'empirical_pipeline/data/1-09-1-20.csv']:
    inputs.append({'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':sha(path),'provider_authenticated':False})

blocks=inventory(SOURCE)+inventory(APPENDIX);failures=[];checked=0;appindex=0
for b in blocks:
    if b['environment']=='table':
        spec=specs.get(b['id'])
        if not spec: b['status']='UNMAPPED';failures.append(b['id']);continue
        actual=actual_rows(b);expected=[[norm(c['rendered']) for c in row] for row in spec['rows']]
        b['status']='RENDERING_MATCH' if actual==expected else 'RENDERING_MISMATCH'
        if actual!=expected: failures.append({'id':b['id'],'actual':actual,'expected':expected})
        checked+=sum(len(row) for row in expected)
        b['semantic_cells']=spec['rows'];b['output']=str(spec.get('result_path',REV/'results'/f"{spec['result']}.json").relative_to(ROOT));b['output_sha256']=sha(ROOT/b['output'])
        b['generator_function']=spec['function'];b['scope']=spec['scope'];b['scientific_gate']='OPEN: see GAPS.md; rendering match is not scientific validity'
    elif b['environment']=='longtable':
        result=appendix_results[appindex];b['generator_function']=appendix_functions[appindex]
        rows=appendix_specs[appindex];actual=actual_rows(b);expected=[[norm(c['rendered']) for c in row] for row in rows]
        b['semantic_cells']=rows; b['status']='RENDERING_MATCH' if actual==expected else 'RENDERING_MISMATCH'
        checked+=sum(len(row) for row in rows)
        if actual!=expected:failures.append({'id':b['id'],'actual':actual,'expected':expected})
        appindex+=1
        path=REV/'results'/f'{result}.json'
        if result in ['event_gaps_descriptive','equity_session_estimates']:path=REV/'results'/f'{result}.csv'
        if result=='original_page_disposition':path=REV/'original_page_disposition.csv'
        b['output']=str(path.relative_to(ROOT));b['output_sha256']=sha(path);b['scientific_gate']='OPEN: declared interpretation/provider/identification limits remain'
    elif b['environment']=='figure':
        name='coinbase_reanalysis' if 'timing' in b['id'] else 'transient_checks'
        b['output']=str((REV/'results'/f'{name}.json').relative_to(ROOT));b['output_sha256']=sha(ROOT/b['output']);b['generator_function']='diagnostics.py:figures'
        receipt_path=HERE/'figure_data_receipt.json'
        if receipt_path.is_file():
            evidence=json.loads(receipt_path.read_text());stem='timing_comparison' if 'timing' in b['id'] else 'transient_loss'
            figure=REV/'figures'/f'{stem}.pdf'
            assert sha(figure)==evidence['files'][figure.name]
            b['figure_pdf_sha256']=sha(figure);b['artist_receipt']=str(receipt_path.relative_to(ROOT));b['status']='PLOT_ARTISTS_VERIFIED'
        else:b['status']='SOURCE_MAPPED: visual/data-series check pending'
        b['scientific_gate']='OPEN: provider/identification/market-calibration scope remains'
    else:
        b['status']='PROOF_REVIEW_OPEN';b['scientific_gate']='Local proof statement inventoried; independent specialist review and novelty not certified'
    del b['content']

# Numeric prose is a review queue, not automatically certified by matching tokens.
prose=[]
for path in [SOURCE,APPENDIX]:
    txt=path.read_text(); excluded=set()
    for b in blocks:
        if b['source']==str(path.relative_to(ROOT)):excluded.update(range(b['start_line'],b['end_line']+1))
    for i,line in enumerate(txt.splitlines(),1):
        if i in excluded or not re.search(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?',line):continue
        if line.startswith(('\\bibitem','\\usepackage','\\documentclass','\\newcommand','\\setlength','\\geometry')):continue
        prose.append({'source':str(path.relative_to(ROOT)),'line':i,'text':line,'status':'SEMANTIC_REVIEW_PENDING'})
legacy=list(csv.DictReader((ROOT/'manifests/claims.csv').open()))
report={'status':'Partial semantic lineage closure; scientific gates open','source_sha256':sha(SOURCE),'appendix_sha256':sha(APPENDIX),'inputs':inputs,'blocks':blocks,'numeric_prose_review_queue':prose,'rendering_failures':failures,'table_cells_checked':checked,'legacy_ledger':{'path':'manifests/claims.csv','claims':len(legacy),'authority':'Different chapter/location scheme; do not treat verified labels as certification of this revised manuscript'},'limits':['Does not authenticate provider','Does not prove economics or novelty','Prose, independent proof review, and figure-series verification remain pending','Raw reconstruction receipt applies only to named recorder inputs']}
(HERE/'claim_lineage.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# Current-source claim lineage audit','',f"Main and appendix table checks: {checked} cells; {len(failures)} failures.",f"Inventoried environments: {len(blocks)}; numerical source lines awaiting semantic review: {len(prose)}.",'','These are source-to-output checks, not a declaration of scientific closure.','','| Location | Environment | Status | Remaining gate |','|---|---|---|---|']
for b in blocks:lines.append(f"| {b['source']}:{b['start_line']} ({b['id']}) | {b['environment']} | {b['status']} | {b['scientific_gate']} |")
lines+=['','## Legacy ledger boundary','',f'The older manifests/claims.csv contains {len(legacy)} claims under a different chapter/location scheme. Its verified labels are not evidence that the revised paper has passed those gates. The current ledger above is anchored to exact source hashes.','','## Input integrity','']
for i in inputs:lines.append(f"- {i['path']}: `{i['sha256']}`; provider authentication remains open.")
(HERE/'CLAIM_LINEAGE_AUDIT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'environments':len(blocks),'table_cells':checked,'rendering_failures':len(failures),'numeric_source_lines_pending':len(prose),'input_hashes':len(inputs)},indent=2))
if failures:raise SystemExit('Rendering mismatches require repair; see claim_lineage.json')
