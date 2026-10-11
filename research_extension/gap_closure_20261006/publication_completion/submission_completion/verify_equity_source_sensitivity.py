"""Independent decimal-GCD, OFI, EMA and QR reconstruction of all50 fits."""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy import linalg,stats
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 d=json.loads((HERE/'equity_source_sensitivity.json').read_text());records={(r['day'],r['block']):r for r in d['rows']};inputs=json.loads((HERE/'fi_mirror_acquisition.json').read_text())['files'];max_error=0;events=0
 for day in range(1,11):
  basename='Train_Dst_NoAuction_DecPre_CF_1.txt' if day==1 else f'Test_Dst_NoAuction_DecPre_CF_{day-1}.txt'
  source=next(r for r in inputs if Path(r['path']).name==basename);p=Path(source['path']);assert sha(p)==source['sha256']
  raw=[]
  with p.open() as f:
   for i,line in enumerate(f):
    if i>=40:break
    raw.append(np.fromstring(line,sep=' '))
  matrix=np.array(raw).T;events+=len(matrix);gaps=abs(np.diff(matrix[:,0]));indices=np.argpartition(gaps,-4)[-4:]+1;bounds=sorted([0,*indices.tolist(),len(matrix)])
  assert bounds==d['coverage'][day-1]['boundaries']
  for block,(a,b) in enumerate(zip(bounds[:-1],bounds[1:]),1):
   v=np.rint(matrix[a:b]*1e8).astype(np.int64)
   for col in range(40):
    divisor=int(np.gcd.reduce(v[:,col]));factor=1
    while divisor%10==0:factor*=10;divisor//=10
    v[:,col]//=factor
   ap,az,bp,bs=[v[:,j].astype(float) for j in [0,1,2,3]];flow=np.zeros(len(v));bid_delta=np.diff(bp);ask_delta=np.diff(ap)
   flow[1:]=np.where(bid_delta>0,bs[1:],np.where(bid_delta==0,bs[1:]-bs[:-1],-bs[:-1]))-np.where(ask_delta<0,az[1:],np.where(ask_delta==0,az[1:]-az[:-1],-az[:-1]))
   price=np.log((bp+ap)/2)*1e4;ema=np.empty(len(price));ema[0]=price[0];alpha=2/101
   for i in range(1,len(price)):ema[i]=(1-alpha)*ema[i-1]+alpha*price[i]
   z=np.column_stack([(price-ema)[500:],flow[500:]]);X=np.column_stack([np.ones(len(z)-1),z[:-1]]);Y=z[1:]
   q,r=linalg.qr(X,mode='economic');B=linalg.solve_triangular(r,q.T@Y);J=B[1:].T;Q=J[0,1]*J[1,0]/(1-J[1,1]);S=J[0,0]+Q;rho=max(abs(np.linalg.eigvals(J)));ref=records[day,block]
   calculated=[*J.ravel(),Q,S,rho];stored=[ref[k] for k in ['J11','J12','J21','J22','Q','S','rho']]
   np.testing.assert_allclose(calculated,stored,rtol=2e-7,atol=2e-9)
   assert ref['n']==len(Y) and ref['n_raw']==b-a;max_error=max(max_error,float(np.max(np.abs(np.array(calculated)-stored))))
 for block,summary in d['by_block'].items():
  rows=[records[day,int(block)] for day in range(1,11)]
  for key in ['Q','S']:
   values=np.array([r[key] for r in rows]);half=stats.t.ppf(.975,9)*values.std(ddof=1)/np.sqrt(10)
   np.testing.assert_allclose(summary[key]['date_t95'],[values.mean()-half,values.mean()+half],rtol=1e-10)
  assert sum(r['n_raw'] for r in rows)==summary['n_raw'] and sum(r['n'] for r in rows)==summary['n_transitions']
 assert events==d['source_events']==394337 and len(records)==50 and sum(r['n'] for r in records.values())==369287
 out=dict(status='ALL50_SOURCE_FITS_INDEPENDENTLY_RECONSTRUCTED_AND_QR_VERIFIED',result_sha256=sha(HERE/'equity_source_sensitivity.json'),fits=50,source_events=events,max_coefficient_or_index_error=max_error,scope='Independent numerical reconstruction; no authentication of actual companies/currency or primary Fairdata archive bytes; exploratory uncertainty only')
 (HERE/'equity_source_sensitivity_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':run()
