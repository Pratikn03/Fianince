"""P1M-A1 part A (protocol P1M_A1_protocol.md): the targeted-halt and uniform-cut ranges on the classes of compositions
the theory covers, computed once from the P1M estimate stored in results/p1m_results.json. No new data.

Run: python run_p1m_a1_part_a.py      (writes results/p1m_a1_partA_results.json; a rerun refuses to recompute)
"""
import datetime
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

import p1m_a1_core as a1
import p1m_core as pm

HERE = Path(__file__).resolve().parent
P1M = HERE / "results/p1m_results.json"
OUT = HERE / "results/p1m_a1_partA_results.json"
P1M_SHA = "b7ad67bb"          # first 8 hex of the P1M result recorded in P1M_measurement_protocol.md, section 8


def main():
    if OUT.exists():
        sys.exit(f"{OUT.name} exists: part A was already computed; not recomputed.")
    raw = P1M.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    assert sha.startswith(P1M_SHA), ("P1M result file changed", sha)
    R = json.loads(raw)["runs"]["primary"]
    t = R["theta"]
    th = {"a": np.array(t["a"]), "kappa": float(t["kappa"]), "r": np.array(t["r"]), "w": np.array(t["w"]),
          "delay": int(R["delay"])}
    cfgs = a1.part_a_configs(th, R["records"], R["hbar"], R["hbar_tight"])
    out = {"spec": "P1M-A1 part A", "protocol": "P1M_A1_protocol.md", "p1m_results_sha256": sha,
           "a1_core_sha256": hashlib.sha256((HERE / "p1m_a1_core.py").read_bytes()).hexdigest(),
           "core_sha256": hashlib.sha256((HERE / "p1m_core.py").read_bytes()).hexdigest(),
           "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "configs": {}}
    t0 = time.time()
    for k, c in enumerate(cfgs):
        res = a1.constrained_ranges(th, c["n_rec"], c["hbar"], c["variant"], c["gamma"])
        res.update({"box": c["box"], "record": c["record"]})
        out["configs"][c["key"]] = res
        hf = "empty" if res["empty"] else f"[{res['H_Foreign']['min']:.4g}, {res['H_Foreign']['max']:.4g}]"
        uu = "" if res["empty"] else f"[{res['U']['min']:.4g}, {res['U']['max']:.4g}]"
        print(f"{k + 1:2d}/{len(cfgs)} {c['key']:28s} H_F {hf:28s} U {uu:24s} feasible starts "
              f"{res['n_feasible_starts']}/{res['n_starts']}  {time.time() - t0:7.0f}s", flush=True)
    out["computed_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    out["seconds"] = time.time() - t0
    OUT.write_text(json.dumps(out, indent=1, default=float))
    print("wrote", OUT, hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
