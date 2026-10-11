"""Independent scalar sweep and difference-of-group-means inference verification."""
from pathlib import Path
import hashlib,json,itertools,math
import numpy as np
from scipy import stats
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
def close(a,b):np.testing.assert_allclose(a,b,rtol=1e-9,atol=1e-10)
def run():
 inference=json.loads((HERE/'inference_completion.json').read_text())
 path=ROOT/'research_extension/gap_closure_20261006/cross_venue/original_panel_reproduction.json'
 assert sha(path)==inference['input_sha256']; rows=json.loads(path.read_text())['rows']
 for reference in inference['dependence']:
  values=[]
  for year in sorted({r['year'] for r in rows}):
   selected=[r[reference['variant']]['Q'] for r in rows if r['year']==year]
   assert len(selected)==192
   value=math.fsum(selected)/len(selected);values.append(value)
   close(value,reference['yearly_means'][str(year)])
  mean=math.fsum(values)/4;variance=math.fsum((x-mean)**2 for x in values)/3
  half=stats.t.ppf(.975,3)*math.sqrt(variance/4)
  close([mean-half,mean+half],reference['year_t3_95'])
  patterns=[math.fsum(s*x for s,x in zip(signs,values))/4 for signs in itertools.product([-1,1],repeat=4)]
  close(sum(abs(x)>=abs(mean)-1e-15 for x in patterns)/16,reference['annual_sign_symmetry_reference_p'])
 panel=[r for r in rows if r['year']==2022]
 groups={}
 for r in panel:groups.setdefault((r['symbol']=='BTCUSDT',r['date']>='2022-07-08'),[]).append(r['observed']['Q'])
 means={g:math.fsum(x)/len(x) for g,x in groups.items()}
 effect=means[True,True]-means[True,False]-means[False,True]+means[False,False]
 # Contrast influence computed directly from four cell means, no matrix fit.
 date_scores={}
 for r in panel:
  g=(r['symbol']=='BTCUSDT',r['date']>='2022-07-08')
  sign=1 if g[0]==g[1] else -1
  date_scores.setdefault(r['date'],0.)
  date_scores[r['date']]+=sign*(r['observed']['Q']-means[g])/len(groups[g])
 se=math.sqrt(math.fsum(x*x for x in date_scores.values())*24/23*191/188)
 close(effect,inference['fee']['effect']);close(se,inference['fee']['date_cluster_se'])
 for ref in inference['fee']['equivalence_sensitivity']:
  lo=stats.t.sf((effect+ref['margin'])/se,23);hi=stats.t.cdf((effect-ref['margin'])/se,23)
  close([lo,hi],[ref['lower_test_p'],ref['upper_test_p']])
  assert (max(lo,hi)<.05)==ref['passes_5_percent_TOST']
 book=json.loads((HERE/'displayed_book_calibration.json').read_text())
 cache=Path(book['cache_path']);assert sha(cache)==book['cache_sha256']
 with np.load(cache) as archive:z={key:archive[key] for key in archive.files if key!='date'}
 import datetime
 z['date']=np.array([datetime.datetime.fromtimestamp(int(ms)/1000,datetime.timezone.utc).strftime('%Y-%m-%d') for ms in z['ms']])
 mask=z['valid'];n=len(mask);assert n==book['selected_minutes']==15593
 computed={key:[] for key in book['pooled_metrics']}
 for i in range(n):
  if not mask[i]:continue
  bp,ap=z['bid_price'][i],z['ask_price'][i];bs,az=z['bid_size'][i],z['ask_size'][i]
  mid=(float(bp[0])+float(ap[0]))/2;spread=float(ap[0])-float(bp[0])
  d={'spread_quote_units':spread,'spread_basis_points':spread/mid*1e4,'midpoint_quote_units':mid,
     'bid_L10_reported_size':math.fsum(bs),'ask_L10_reported_size':math.fsum(az)}
  for side,p,v in [('buy',ap,az),('sell',bp,bs)]:
   for fraction in book['fractions_of_side_L10_depth']:
    quantity=fraction*math.fsum(v);remaining=quantity;cash=0.
    for price,size in zip(p,v):
     take=min(remaining,float(size));cash+=take*float(price);remaining-=take
     if remaining<=0:break
    assert abs(remaining)<1e-9
    avg=cash/quantity
    cost=avg-mid if side=='buy' else mid-avg
    incremental=avg-float(p[0]) if side=='buy' else float(p[0])-avg
    d[f'{side}_{fraction:g}_sweep_cost_per_reported_unit']=cost
    d[f'{side}_{fraction:g}_static_depth_slope']=2*incremental/quantity
  for key,value in d.items():computed[key].append(value)
 for key,values in computed.items():
  ref=book['pooled_metrics'][key];close(np.quantile(values,[.1,.5,.9]),[ref['p10'],ref['median'],ref['p90']])
  for row in book['daily']:
   selected=np.array(values)[z['date'][mask]==row['date']]
   ref=row['metrics'][key];close(np.quantile(selected,[.1,.5,.9]),[ref['p10'],ref['median'],ref['p90']])
 result=dict(status='INDEPENDENT_INFERENCE_AND_ALL_MINUTE_SWEEP_CHECKS_PASS',
             inference_sha256=sha(HERE/'inference_completion.json'),book_sha256=sha(HERE/'displayed_book_calibration.json'),
             scalar_sweep_records=int(mask.sum())*6,pooled_metrics=len(computed),daily_summaries=len(book['daily']),
             limits='Independent arithmetic and declared scope checks; not causal identification, real fills, rights or full market calibration.')
 (HERE/'completion_evidence_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':run()
