"""Recalculate recorded date summaries and check each new main-table field."""
from pathlib import Path
import json,hashlib,re
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REV=ROOT/'research_extension/paper_revision_20261006'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    result_path=REV/'results/coinbase_reanalysis.json';d=json.loads(result_path.read_text());daily_path=REV/'results/coinbase_daily_estimates.csv';frame=pd.read_csv(daily_path);expected=[];records=[]
    for asset in ['BTC','ETH','ADA']:
        cache=ROOT/'empirical_pipeline/cache'/f'{asset}_1sec_core_v2dedup.pkl';assert sha(cache)==d[asset]['input_sha256']
        for state,alignment,label,key in [('x','observed','EMA / observed','x_observed'),('x','forward','EMA / forward','x_forward'),('return','observed','Return / observed','return_observed')]:
            f=frame[(frame.asset==asset)&(frame.state==state)&(frame.alignment==alignment)]
            q=np.array([np.average(g.Q,weights=g.n) for _,g in f.groupby('date')]);mean=float(q.mean());se=float(stats.sem(q));half=float(stats.t.ppf(.975,len(q)-1)*se);interval=[mean-half,mean+half];saved=d[asset]['variants'][key]
            assert len(q)==saved['n_days'] and int(f.n.sum())==saved['n_transitions']
            np.testing.assert_allclose(mean,saved['Q']['mean'],rtol=1e-11,atol=1e-14);np.testing.assert_allclose(interval,saved['Q']['ci95'],rtol=1e-11,atol=1e-14)
            expected.append([asset,label,str(len(q)),str(int(f.n.sum())),f'{mean:.7f}',f'[{interval[0]:.5f}, {interval[1]:.5f}]'])
            records.append({'asset':asset,'construction':key,'n_dates':len(q),'transitions':int(f.n.sum()),'date_Q':q.tolist(),'mean':mean,'ci95_date_t':interval,'result_field':f'{asset}.variants.{key}.Q','cache_sha256':sha(cache)})
    source=ROOT/'paper/Machine_Markets_JF_Submission.tex';s=source.read_text();pos=s.index('\\label{tab:measurement_sensitivity}');a=s.rfind('\\begin{table}',0,pos);b=s.index('\\end{table}',pos);table=s[a:b].split('\\midrule',1)[1].split('\\bottomrule',1)[0]
    actual=[[re.sub(r'\s+',' ',v).strip() for v in line.rstrip()[:-2].split('&')] for line in table.splitlines() if '&' in line and line.rstrip().endswith('\\\\')];assert actual==expected
    out={'status':'54_ROW_FIELD_CELLS_MATCH_INDEPENDENT_DATE_AGGREGATION','source_sha256':sha(source),'result_sha256':sha(result_path),'daily_estimate_sha256':sha(daily_path),'rows':records,'cells_checked':54,'scope':'Input cache integrity and date aggregation/rendering, not provider/licence authentication or serially justified confidence coverage'}
    (HERE/'recorded_table_lineage.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':run()
