"""Runs the P1M-A1 part-B notebook's analysis code end to end on the simulated TWSE responses of test_p1m_notebook.py
(real 2013-2016 calendar dates, both T86 schema eras). Checks: the run completes, every pre-specified run is present
and converged, the results file is written, a rerun loads it without recomputing, the price equation's kappa is P1M's,
and the notebook cell compiles. Simulated data only; no download."""
import datetime
import gzip
import hashlib
import json
import os
import tempfile
import time
import zipfile

import numpy as np

import make_p1m_a1_notebook as mk
import p1m_a1_core as a1
import p1m_core as pm
import p1t_executor as ex
from test_p1m_notebook import fake


def run(cal, store, root):
    analysis = mk.ANALYSIS.replace("@@A1_SHA@@", mk.A1_SHA).replace("@@A1_SRC@@", json.dumps(mk.A1))
    g = {"np": np, "json": json, "os": os, "zipfile": zipfile, "gzip": gzip, "time": time, "hashlib": hashlib,
         "ex": ex, "pm": pm, "days": cal, "ev": set(), "ROOT": root, "DEV_END": "20161230", "EXECUTOR_SHA256": "test",
         "CORE_SHA256": "test", "now": lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "load": lambda sub, d: store[(sub, d)]}
    cwd = os.getcwd(); work = tempfile.mkdtemp(); os.chdir(work)
    try:
        exec(analysis, g)
    finally:
        os.chdir(cwd)
    return g


if __name__ == "__main__":
    t0 = time.time()
    cal, store = fake()
    out = {"n_days": len(cal)}
    with tempfile.TemporaryDirectory() as root:
        g = run(cal, store, root)
        R = g["resultsB"]
        out["runs"] = sorted(R["runs"])
        out["check_runs"] = out["runs"] == sorted(lab for lab, _, _ in a1.B_RUNS)
        out["check_saved"] = os.path.exists(os.path.join(root, "p1m_a1_partB_results.json")) and \
            os.path.exists(os.path.join(root, "p1m_a1_partB_results.zip"))
        stamp = R["computed_utc"]
        g2 = run(cal, store, root)
        out["check_rerun_loads"] = g2["resultsB"]["computed_utc"] == stamp
        prim = R["runs"]["primary"]
        out["primary_H"] = prim["H"]
        out["primary_sum_beta"] = {c: prim["rules"][c]["sum_beta"] for c in ("Foreign", "Trust", "Dealers")}
        out["check_converged"] = all(r["rules"][c]["converged"] for r in R["runs"].values() for c in ("Foreign", "Trust", "Dealers"))
        out["check_draws"] = all(r["bootstrap"]["B_used"] >= 990 for r in R["runs"].values())
        # kappa equals P1M's price equation on the same panel
        day_files = [(d, store[("T86", d)], store[("MI", d)]) for d in cal]
        P = ex.build_panel(day_files, set())
        dev = np.ones(len(P.dates), bool)
        prep = ex.prepare(P, dev)
        k_p1m = float(pm.ols_from(pm.build_equations(prep, dev)["price"])[0][pm.P_LAGS])
        out["check_kappa_is_P1M"] = abs(k_p1m - prim["kappa"]) < 1e-12
        out["check_finite"] = bool(np.all(np.isfinite(prim["H"])))
    mk.build("/tmp/p1m_a1_nb_check.ipynb")
    nb = json.load(open("/tmp/p1m_a1_nb_check.ipynb"))
    compile(nb["cells"][1]["source"], "cell", "exec")
    out["check_notebook_compiles"] = True
    out["seconds"] = time.time() - t0
    out["all_pass"] = all(v for k, v in out.items() if k.startswith("check_"))
    print(json.dumps(out, indent=1, default=float))
    json.dump(out, open("test_p1m_a1_notebook_results.json", "w"), indent=1, default=float)
