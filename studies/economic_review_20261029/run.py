"""Run with python -m studies.economic_review_20261029.run --help."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np

from . import experiments as ex


def sha256(path):
    h = hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode",choices=["smoke","full"],default="smoke")
    parser.add_argument("--seed",type=int,default=20261029)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--csv",type=Path)
    parser.add_argument("--window",type=int,default=120)
    parser.add_argument("--forecast-horizon",type=int,default=12)
    args=parser.parse_args(argv)
    if args.window<10 or args.forecast_horizon<1:parser.error("invalid window or horizon")
    args.out.mkdir(parents=True,exist_ok=True)
    if any(args.out.iterdir()):parser.error("output directory must be empty; preserve previous runs")
    root=Path(__file__).resolve().parents[2]
    def git(*cmd):
        p=subprocess.run(["git",*cmd],cwd=root,text=True,capture_output=True)
        return p.stdout.strip() if p.returncode==0 else "unavailable"
    config={k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()}
    # Written BEFORE experiments, but no independent preregistration is claimed.
    (args.out/"configuration.json").write_text(json.dumps(config,indent=2)+"\n")
    manifest=dict(started_utc=datetime.now(timezone.utc).isoformat(),status="running",
                  exploratory=True,smoke_only=args.mode=="smoke",configuration=config,
                  source_commit=git("rev-parse","HEAD"),source_changes=git("status","--porcelain","--untracked-files=no"),
                  source_hashes={p.name:sha256(p) for p in Path(__file__).parent.glob("*.py")},
                  python=sys.version,platform=platform.platform(),
                  packages={n:importlib.metadata.version(n) for n in ["numpy","scipy","pandas","matplotlib"]},
                  input_sha256=sha256(args.csv) if args.csv else None,
                  scope="research diagnostics; synthetic reset contracts are not public-data certification")
    fp=args.out/"manifest.json"
    def save():fp.write_text(json.dumps(manifest,indent=2)+"\n")
    save();started=time.monotonic()
    reps,H,n=(40,256,1500) if args.mode=="smoke" else (1000,512,6000)
    tasks=[("E1_drift",lambda r:ex.drift_experiment(r,reps,H)),
           ("E2_filter_controls",lambda r:ex.filtering_experiment(r,max(10,reps//5),n)),
           ("E3_information_targets",lambda r:ex.information_experiment(r,reps,H)),
           ("E4_matched_capacity",lambda r:ex.benchmarks_experiment(r,reps,min(H,128))),
           ("E6_coverage",lambda r:ex.coverage_experiment(r,reps,H))]
    if args.csv:tasks.append(("E5_real_data",lambda r:ex.real_data_experiment(args.csv,r,args.window,args.forecast_horizon)))
    streams=np.random.SeedSequence(args.seed).spawn(len(tasks))
    manifest["completed_experiments"]=[]
    try:
        for (name,task),stream in zip(tasks,streams):
            frame=task(np.random.default_rng(stream))
            if isinstance(frame,tuple):
                frame, predictions=frame;predictions.to_csv(args.out/(name+"_predictions.csv"),index=False)
            frame.to_csv(args.out/(name+".csv"),index=False)
            manifest["completed_experiments"].append(name);save()
            print(name,len(frame),"rows",flush=True)
        manifest.update(status="completed",elapsed_seconds=time.monotonic()-started,
                        finished_utc=datetime.now(timezone.utc).isoformat())
        if not args.csv:manifest["not_run"]=["E5 real market data: no CSV supplied","E7 existing GPU/data-dependent protocols: manual execution"]
        manifest["output_sha256"]={p.name:sha256(p) for p in args.out.glob("*.csv")}
        save()
        (args.out/"INTERPRETATION.md").write_text(
            "# Run interpretation\n\n"+('SMOKE RUN: pipeline check; not a paper result.\n\n' if args.mode=="smoke" else 'EXPLORATORY FULL RUN: not independently preregistered.\n\n')+
            "Read every row, including negative results. E1 is mathematical verification. E2 tests filtering artifacts. "
            "E3 is a same-risk identification witness, not proof of a general rate separation. E4 matches baseline "
            "capacity on training episodes and reports test capacity drift. E6 deliberately violates assumptions in "
            "four settings. E5, when supplied, is a purged predictive comparison with an EMA proxy; it does not "
            "identify endogenous feedback. Existing registered studies remain separate.\n")
    except Exception as error:
        manifest.update(status="failed",error=str(error),elapsed_seconds=time.monotonic()-started);save();raise
    print("Saved",args.out)


if __name__=="__main__":main()
