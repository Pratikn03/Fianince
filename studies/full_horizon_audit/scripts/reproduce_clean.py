#!/usr/bin/env python3
"""Rerun primary comparison from copied inputs in a clean local directory.
Compares all non-timing fields; same-environment repeatability, not external review.
"""
from pathlib import Path
import argparse,shutil,subprocess,sys,json,time
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--datasets',type=int,default=21600);p.add_argument('--workers',type=int,default=4);args=p.parse_args()
 target=args.output.resolve()
 if target.exists():raise SystemExit('Choose a new output directory; refusing to overwrite existing files.')
 target.mkdir(parents=True)
 for folder in ['src','configs','data']:
  shutil.copytree(ROOT/folder,target/folder,ignore=shutil.ignore_patterns('__pycache__'))
 (target/'scripts').mkdir();(target/'results').mkdir()
 shutil.copy2(ROOT/'scripts/run_comparison.py',target/'scripts/run_comparison.py')
 start=time.perf_counter()
 with (target/'results/progress.log').open('w') as out:
  subprocess.run([sys.executable,str(target/'scripts/run_comparison.py'),'--datasets',str(args.datasets),'--workers',str(args.workers)],stdout=out,stderr=subprocess.STDOUT,check=True,cwd=target)
 expected=pd.read_csv(ROOT/'results/paired_comparison.csv');expected=expected[expected.dataset_id<args.datasets].reset_index(drop=True)
 actual=pd.read_csv(target/'results/paired_comparison.csv')
 columns=[c for c in expected.columns if not c.endswith('_seconds')]
 assert len(expected)==len(actual)
 maxdiff=0.;exact=True
 for c in columns:
  if pd.api.types.is_numeric_dtype(expected[c]):
   e=expected[c].to_numpy();a=actual[c].to_numpy();assert np.allclose(e,a,rtol=1e-10,atol=1e-10,equal_nan=True),c
   finite=np.isfinite(e)&np.isfinite(a)
   if finite.any():maxdiff=max(maxdiff,float(np.max(np.abs(e[finite]-a[finite]))))
   exact=exact and bool(np.array_equal(e,a,equal_nan=True))
  else:assert expected[c].fillna('').equals(actual[c].fillna('')),c
 result={'datasets':args.datasets,'paired_rows':len(actual),'non_timing_columns':len(columns),'all_comparisons_passed':True,'numeric_fields_exactly_equal':exact,'max_absolute_numeric_difference':maxdiff,'same_environment_not_external_replication':True,'seconds':time.perf_counter()-start,'clean_directory':str(target)}
 (ROOT/'results/clean_reproduction.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
