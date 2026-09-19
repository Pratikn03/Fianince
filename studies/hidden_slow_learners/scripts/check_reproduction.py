#!/usr/bin/env python3
"""Compare all reported experiment data with a fresh output directory."""
from pathlib import Path
import argparse
import json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--reference',type=Path,default=ROOT/'results')
    p.add_argument('--candidate',type=Path,required=True)
    a=p.parse_args()
    names=json.loads((a.reference/'clean_reproduction_check.json').read_text())['files']
    differences=[]
    for name in names:
        r,c=a.reference/name,a.candidate/name
        if not c.exists():
            differences.append(f'{name}: missing');continue
        if r.suffix=='.npz':
            with np.load(r) as rr,np.load(c) as cc:
                if sorted(rr.files)!=sorted(cc.files):
                    differences.append(f'{name}: array keys differ');continue
                for key in rr.files:
                    if not np.array_equal(rr[key],cc[key],equal_nan=True):
                        differences.append(f'{name}: array {key} differs')
        elif r.read_bytes()!=c.read_bytes():
            differences.append(f'{name}: bytes differ')
    print(json.dumps({'status':'FAIL' if differences else 'PASS',
                      'files_compared':len(names),'differences':differences},indent=2))
    raise SystemExit(bool(differences))

if __name__=='__main__':main()
