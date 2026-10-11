"""Full logical and serialization comparison of the existing January CSV to source Parquet."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Volumes/T9/machine_markets_data/publication_audit_dependencies_20261008/site')
import pyarrow,pyarrow.parquet as pq
import pandas as pd
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(4*1024*1024):h.update(b)
 return h.hexdigest()
def run():
 source=Path('/Volumes/T9/machine_markets_data/primary_january_authentication_20261008/1-09-1-20.pq')
 local=ROOT/'empirical_pipeline/data/1-09-1-20.csv'
 metadata=json.loads((HERE/'szh765_view.json').read_text());files=json.loads((HERE/'szh765_list.json').read_text())['datasetFiles']
 assert source.stat().st_size==files[0]['totalBytes']==246077535
 parquet=pq.ParquetFile(source);csv=pd.read_csv(local,index_col=0,chunksize=100000,float_precision='round_trip')
 serialized=hashlib.sha256();count=0;first=True;comparisons=0
 for batch in parquet.iter_batches(batch_size=100000):
  frame=batch.to_pandas();expected=csv.get_chunk(len(frame))
  assert len(frame)==len(expected) and list(map(str,frame.columns))==list(expected.columns)
  assert np.array_equal(frame.index.to_numpy(),expected.index.to_numpy())
  for col in frame:
   a=frame[col].to_numpy();b=expected[str(col)].to_numpy()
   if np.issubdtype(a.dtype,np.number):assert np.array_equal(a,b,equal_nan=True),(count,col)
   else:assert np.array_equal(a.astype(str),b.astype(str)),(count,col)
   comparisons+=len(a)
  serialized.update(frame.to_csv(index=True,header=first).encode());first=False;count+=len(frame)
  if count%500000==0:print('January source-to-CSV rows matched:',count,flush=True)
 try:csv.get_chunk(1);raise ValueError('CSV has surplus rows')
 except StopIteration:pass
 assert count==parquet.metadata.num_rows==3730870
 local_sha=sha(local);reconstructed_sha=serialized.hexdigest()
 receipt=dict(status='ALL_PRIMARY_PARQUET_ROWS_COLUMNS_AND_INDEX_MATCH_LOCAL_CSV',
              primary_url='https://www.kaggle.com/datasets/szh765/bitcoin-orderbook',version=metadata['currentVersionNumber'],
              dataset_id=metadata['id'],declared_license=metadata['licenseName'],source_path=str(source),source_sha256=sha(source),
              local_csv_sha256=local_sha,reconstructed_csv_sha256=reconstructed_sha,serialization_bytes_match=reconstructed_sha==local_sha,
              rows=count,columns=42,cells_compared=comparisons,index_compared=True,pyarrow_version=pyarrow.__version__,
              scope='Exact primary distribution and declared uploader licence authenticated. Primary description does not establish exchange, contract, collector or monetary units. Logical equality is distinguished from serialization-byte equality.')
 (HERE/'january_authentication.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print('All January rows/columns/index match; serialization bytes identical:',receipt['serialization_bytes_match'])
if __name__=='__main__':run()
