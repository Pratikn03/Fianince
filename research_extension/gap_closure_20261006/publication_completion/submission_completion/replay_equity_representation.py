"""Replay the preserved mirror notebook and quantify its representation damage.

Independent normalized-file acquisition is a diagnostic, not primary archive
checksum authentication or a verified company/currency/volume-unit map.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
TARGET=Path('/Volumes/T9/machine_markets_data/fi_equity_mirror_20261008')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load_needed(path):
 arrays={};n_lines=0
 with path.open() as f:
  for i,line in enumerate(f):
   if i<40 or i>=144:arrays[i]=np.fromstring(line,sep=' ')
   n_lines+=1
 assert n_lines==149 and len({len(v) for v in arrays.values()})==1
 return arrays
def run():
 saved=pd.read_csv(ROOT/'empirical_pipeline/fi2010/data/data.csv',index_col=0)
 acquisition=json.loads((HERE/'fi_mirror_acquisition.json').read_text());assert len(acquisition['files'])==10
 rows=[];fragments={};input_total=0
 for day in range(1,11):
  name='Train_Dst_NoAuction_DecPre_CF_1.txt' if day==1 else f'Test_Dst_NoAuction_DecPre_CF_{day-1}.txt'
  p=TARGET/name;a=load_needed(p);n=len(a[0]);input_total+=n
  # Exactly the saved notebook: six large jumps, five intervals, no endpoint.
  differences=np.abs(np.diff(a[0],prepend=np.inf));boundaries=np.sort(np.argsort(differences)[-6:])
  order=[4*i for i in range(10)]+[4*i+2 for i in range(10)]+[4*i+1 for i in range(10)]+[4*i+3 for i in range(10)]
  columns=[f'PRICE_ASK_{i}' for i in range(10)]+[f'PRICE_BID_{i}' for i in range(10)]+[f'VOLUME_ASK_{i}' for i in range(10)]+[f'VOLUME_BID_{i}' for i in range(10)]
  for stock in range(1,6):
   start,end=map(int,boundaries[stock-1:stock+1]);raw=np.column_stack([a[k][start:end] for k in order]);assert np.all(raw!=0)
   values=np.rint(raw*1e8).astype(np.int64);powers=[]
   for j in range(40):
    power=0
    while np.all(values[:,j]%10==0):
     if np.all(values[:,j]==0):raise ValueError('Legacy notebook would loop forever on an all-zero converted column')
     values[:,j]//=10;power+=1
    powers.append(power)
   frame=pd.DataFrame(values,columns=columns)
   for k,label in zip(range(144,149),[1,2,3,5,10]):frame[f'LABEL_{label}TICK']=(2-a[k][start:end]).astype(np.int64)
   frame.insert(0,'DAY',day);frame.insert(0,'STOCK',stock);fragments[stock,day]=frame
   local=saved[(saved.STOCK==stock)&(saved.DAY==day)].reset_index(drop=True)
   equal_shape=frame.shape==local.shape;errors=0 if equal_shape else None
   if equal_shape:errors=int(np.count_nonzero(frame.to_numpy()!=local[frame.columns].to_numpy()))
   bp=frame.PRICE_BID_0.to_numpy();ap=frame.PRICE_ASK_0.to_numpy()
   qa=dict(crossed_top_quotes=int((bp>ap).sum()),equal_top_quotes=int((bp==ap).sum()),ask_ladder_violations=int((np.diff(values[:,:10],axis=1)<0).any(axis=1).sum()),bid_ladder_violations=int((np.diff(values[:,10:20],axis=1)>0).any(axis=1).sum()),price_column_decimal_powers=powers[:20],volume_column_decimal_powers=powers[20:])
   rows.append(dict(day=day,label=stock,source_start=start,source_end=end,source_day_states=n,retained_states=end-start,supplied_states=len(local),matching_shape=equal_shape,cell_mismatches=errors,quality=qa))
  print('Day',day,'source states',n,'kept',int(boundaries[-1]-boundaries[0]),'tail dropped',n-int(boundaries[-1]),flush=True)
 reconstructed=pd.concat([fragments[stock,day] for stock in range(1,6) for day in range(1,11)],ignore_index=True).astype(np.int64)
 output=TARGET/'reconstructed_supplied_data.csv';reconstructed.to_csv(output)
 original=ROOT/'empirical_pipeline/fi2010/data/data.csv';match=sha(output)==sha(original)
 report=dict(status='PRESERVED_TRANSFORMATION_MATCHED_INDEPENDENT_MIRROR' if match else 'TRANSFORMATION_COMPARISON_MISMATCH_REQUIRES_DIAGNOSIS',original_csv_sha256=sha(original),reconstructed_csv_sha256=sha(output),exact_csv_bytes_match=match,input_states=input_total,retained_states=len(reconstructed),dropped_states=input_total-len(reconstructed),rows=rows,all_50_shapes_and_cells_match=all(r['matching_shape'] and r['cell_mismatches']==0 for r in rows),reconstructed_csv_path=str(output),source_receipt_sha256=sha(HERE/'fi_mirror_acquisition.json'),not_authenticated=['Primary Fairdata archive full checksum','Actual company map','Original currency and each feature normalization denominator','Mirror redistribution licence; primary CC BY4.0 still applies'],interpretation='This replays a heuristic/truncating/per-column rescaling representation. A byte match is source-lineage evidence, not an authentic physical order book or correctly segmented-company study.')
 (HERE/'equity_representation_replay.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2),flush=True)
if __name__=='__main__':run()
