"""Builds P1M_A1_Decoupled_Colab.ipynb (protocol P1M_A1_protocol.md, part B).

One code cell. It mounts Drive, reuses the stored TWSE files in P1T_raw for 2013-01-02 to 2016-12-30 exactly as the P1M
notebook does (the data-loading code is P1M's, unchanged), builds the P1T panel with the unchanged executor, estimates
the decoupled rules once (primary and three pre-specified sensitivity runs), and saves p1m_a1_partB_results.json / .zip
to Drive.
"""
import hashlib
import json

import make_p1m_notebook as p1m

A1 = open("p1m_a1_core.py").read()
A1_SHA = hashlib.sha256(A1.encode()).hexdigest()

ANALYSIS = r'''
# ---- P1M-A1 part B: decoupled rules (protocol P1M_A1_protocol.md) ----
A1_SHA256 = "@@A1_SHA@@"
A1_SRC = @@A1_SRC@@
assert hashlib.sha256(A1_SRC.encode()).hexdigest() == A1_SHA256, "P1M-A1 core changed"
open("p1m_a1_core.py", "w").write(A1_SRC)
import importlib; import p1m_a1_core as a1; importlib.reload(a1)
RES = os.path.join(ROOT, "p1m_a1_partB_results.json")
if os.path.exists(RES):
    resultsB = json.load(open(RES))
    print("P1M-A1 part B was already computed on", resultsB["computed_utc"], "- loaded from Drive, NOT recomputed.")
else:
    assert days and max(days) <= DEV_END, "a date after the development period would be loaded"
    day_files = [(d, load("T86", d), load("MI", d)) for d in days]
    P = ex.build_panel(day_files, ev)
    dates = np.array(P.dates); dev = np.ones(len(dates), bool)
    prep = ex.prepare(P, dev)
    print("panel:", len(P.codes), "codes,", len(dates), "days; universe", len(prep["U"]), flush=True)
    t0 = time.time()
    runs = {}
    for label, J, p in a1.B_RUNS:
        runs[label] = a1.decoupled(prep, dev, J, p, label=label)
        print(label, "done", round(time.time() - t0), "s", flush=True)
    p1m_path = os.path.join(ROOT, "p1m_results.json")
    restricted = None
    if os.path.exists(p1m_path):
        q = json.load(open(p1m_path))["runs"]["primary"]
        restricted = {"kappa": q["theta"]["kappa"], "H": q["effects"]["H"], "U": q["effects"]["U"],
                      "ci": {k: q["bootstrap"]["ci"][k] for k in ("H_Foreign", "H_Trust", "H_Dealers", "U")}}
    resultsB = {"spec": "P1M-A1 part B", "protocol": "P1M_A1_protocol.md", "period": [days[0], days[-1]],
                "n_days": len(days), "executor_sha256": EXECUTOR_SHA256, "core_sha256": CORE_SHA256,
                "a1_core_sha256": A1_SHA256, "computed_utc": now(), "runs": runs, "restricted_P1M": restricted,
                "kappa_matches_P1M": None if restricted is None else abs(runs["primary"]["kappa"] - restricted["kappa"]) < 1e-12}
    json.dump(resultsB, open("p1m_a1_partB_results.json", "w"), indent=1, ensure_ascii=False, default=float)
    with zipfile.ZipFile("p1m_a1_partB_results.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write("p1m_a1_partB_results.json")
    import shutil
    shutil.copy("p1m_a1_partB_results.json", RES)
    shutil.copy("p1m_a1_partB_results.zip", os.path.join(ROOT, "p1m_a1_partB_results.zip"))

def _f(v):
    return f"{v:.3g}" if isinstance(v, (int, float)) and v == v else str(v)
print("kappa matches P1M:", resultsB["kappa_matches_P1M"])
if resultsB["restricted_P1M"]:
    rc = resultsB["restricted_P1M"]["ci"]
    print("restricted (P1M): H_Foreign", _f(rc["H_Foreign"]["est"]), [_f(v) for v in rc["H_Foreign"]["ci95"]])
for name, R in resultsB["runs"].items():
    ci = R["bootstrap"]["ci"]
    print(f"\n=== {name} === J={R['J']} AR({R['ar_order']}) kappa={_f(R['kappa'])} draws={R['bootstrap']['B_used']}")
    for c in ("Foreign", "Trust", "Dealers"):
        ru = R["rules"][c]
        print(f"  {c}: sum beta {_f(ru['sum_beta'])}  phi {[_f(v) for v in ru['phi']]}  converged {ru['converged']}  rows {ru['rows']}")
        print(f"     H_{c} = {_f(ci['H_'+c]['est'])}  95% [{_f(ci['H_'+c]['ci95'][0])}, {_f(ci['H_'+c]['ci95'][1])}]")
    print(f"  U = {_f(ci['U']['est'])}  95% [{_f(ci['U']['ci95'][0])}, {_f(ci['U']['ci95'][1])}]")
try:
    from google.colab import files; files.download("p1m_a1_partB_results.zip")
except Exception:
    print("saved p1m_a1_partB_results.zip (also on Drive in P1T_raw)")
'''


def cell():
    head = p1m.HEAD % {"EX_SHA": p1m.EX_SHA, "CORE_SHA": p1m.CORE_SHA, "EX_SRC": json.dumps(p1m.EX),
                       "CORE_SRC": json.dumps(p1m.CORE)}
    return head + ANALYSIS.replace("@@A1_SHA@@", A1_SHA).replace("@@A1_SRC@@", json.dumps(A1))


def build(path="P1M_A1_Decoupled_Colab.ipynb"):
    src = cell()
    compile(src, "cell", "exec")
    md = ("# P1M-A1 part B: Taiwan's tagged rules with feedback decoupled from flow persistence (2013–2016)\n\n"
          "Analysis fixed before the run in `P1M_A1_protocol.md`. It reuses the TWSE files already on your Drive in "
          "`P1T_raw` (development period only, 2013-01-02 to 2016-12-30; nothing later is loaded) with P1M's data code, "
          "unchanged. It estimates each class's response to the price deviation as a free distributed lag, with the "
          "class's other flow following its own autoregression, and computes each class's contribution to the feedback "
          "budget with a date-block bootstrap.\n\n"
          "**Run the single code cell once** (Runtime → Run all). Allow Drive access when asked. Loading the files "
          "takes most of the time (about 15–30 minutes). It saves `p1m_a1_partB_results.json` and "
          "`p1m_a1_partB_results.zip` to Drive (`P1T_raw`) and downloads the zip. Send the zip, or paste the printed "
          "summary. A rerun loads the saved result and does not recompute.")
    nb = {"nbformat": 4, "nbformat_minor": 5, "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"},
                                                             "colab": {"provenance": []}},
          "cells": [{"cell_type": "markdown", "metadata": {}, "source": md, "id": "md0"},
                    {"cell_type": "code", "metadata": {}, "source": src, "outputs": [], "execution_count": None, "id": "c1"}]}
    json.dump(nb, open(path, "w"), ensure_ascii=False, indent=1)
    return A1_SHA


if __name__ == "__main__":
    print("a1 core sha256", build())
