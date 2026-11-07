"""Builds P1T_Diagnostics_A2_Colab.ipynb: runs the amendment A2 diagnostics on the validation period from the raw
files already on Drive (no new downloads beyond cached ones; the holdout is never requested), after checking that the
primary validation statistic is reproduced exactly."""
import hashlib
import json

src = open("p1t_executor.py").read()
sha = hashlib.sha256(src.encode()).hexdigest()
nb = json.load(open("P1T_Validation_A1_Colab.ipynb"))
cell = "".join(nb["cells"][1]["source"])
i = cell.index("EXECUTOR_SHA256 = "); j = cell.index("\n", i)
cell = cell[:i] + f'EXECUTOR_SHA256 = "{sha}"' + cell[j:]
i = cell.index("EXECUTOR_SRC = "); j = cell.index("\n", i)
cell = cell[:i] + "EXECUTOR_SRC = " + json.dumps(src, ensure_ascii=False) + cell[j:]
k = cell.index("# 4. run the registered executor once on the validation period")
cell = cell[:k] + r'''# 4. amendment A2: pre-specified diagnostics on the validation period (exploratory; the primary is not re-tested)
def load(sub, d): return json.loads(gzip.open(os.path.join(ROOT, sub, d + ".json.gz")).read())
day_files = [(d, load("T86", d), load("MI", d)) for d in days]
P = ex.build_panel(day_files, ev)
dates = np.array(P.dates); dev = dates <= DEV_END; val = ~dev
prep = ex.prepare(P, dev)
D_check, _ = ex.panel_D(ex.panel_L(prep, dev, val, "Foreign"))
assert abs(D_check - 0.04045892959202791) < 1e-12, f"primary not reproduced: {D_check}"
diag = ex.diagnostics(prep, P.dates, dev, val)
res = {"spec": "P1T", "period": "validation", "amendment": "A2", "label": "exploratory diagnostics on the validation period",
       "executor_sha256": EXECUTOR_SHA256, "run_utc": now(), "primary_D_reproduced": D_check, "diagnostics": diag}
json.dump(res, open("p1t_A2_diagnostics_validation.json", "w"), indent=1, ensure_ascii=False, default=float)
with zipfile.ZipFile("p1t_A2_diagnostics_validation.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write("p1t_A2_diagnostics_validation.json")
import shutil; shutil.copy("p1t_A2_diagnostics_validation.zip", os.path.join(ROOT, "p1t_A2_diagnostics_validation.zip"))
print("reverse causality:", json.dumps(diag["reverse_causality"], indent=1))
print("S3:", json.dumps(diag["S3"], indent=1))
try:
    from google.colab import files; files.download("p1t_A2_diagnostics_validation.zip")
except Exception: print("saved p1t_A2_diagnostics_validation.zip (also on Drive)")
'''
nb["cells"][1]["source"] = cell
nb["cells"][0]["source"] = ("# P1T amendment A2: pre-specified diagnostics on the validation period\n\n"
    "Exploratory run of the spec §7 diagnostics and §8 secondary outcomes on the validation period, with the A2 executor. "
    "It reuses the raw files on Drive (nothing new is downloaded; the holdout is never requested), first checks that the "
    "primary validation statistic D = 0.04045892959202791 is reproduced exactly, and returns `p1t_A2_diagnostics_validation.zip` "
    "(also saved to Drive). **Run the single code cell once.** It takes about 10–20 minutes.")
for c in nb["cells"]:
    if c["cell_type"] == "code":
        c["outputs"] = []; c["execution_count"] = None
json.dump(nb, open("P1T_Diagnostics_A2_Colab.ipynb", "w"), ensure_ascii=False, indent=1)
compile(cell, "cell", "exec")
print(sha)
