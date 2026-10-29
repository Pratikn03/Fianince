"""Generate the Colab notebook; outputs are deliberately cleared."""
from pathlib import Path
import nbformat as nbf

HERE=Path(__file__).resolve().parent
nb=nbf.v4.new_notebook()
nb.metadata={"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
             "language_info":{"name":"python","version":"3"},
             "colab":{"name":"Machine Markets - Economic Review Experiments"}}
md=nbf.v4.new_markdown_cell;code=nbf.v4.new_code_cell
nb.cells=[
md("""# Machine Markets: economic review experiments

Run all cells in order. Start with **smoke**, then select **full** below.
CPU runtime is sufficient for this new package. No paid API or GPU is used.

These are **new exploratory diagnostics**, separate from the original registered
tests. A successful run is not a paper pass or a production safety certificate.
The source commit, code hashes, dependencies, seed and input hash are saved.
Existing results are never overwritten. Read the repository research plan before
interpreting results. Do not change a seed to select a favorable outcome.
"""),
code('''import os, sys, subprocess
from pathlib import Path
REPOSITORY = "https://github.com/Pratikn03/Fianince.git"
REF = "19805d7ec6265691166456407902d63215747e51"  # reviewed immutable source commit
local = os.environ.get("MM_LOCAL_REPO")  # optional local validation path
REPO = Path(local) if local else Path("/content/machine-markets-economic-review")
if not local:
    if not REPO.exists():
        subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout", "--depth", "1", REPOSITORY, str(REPO)], check=True)
        subprocess.run(["git", "fetch", "--depth", "1", "origin", REF], cwd=REPO, check=True)
        subprocess.run(["git", "sparse-checkout", "init", "--cone"], cwd=REPO, check=True)
        subprocess.run(["git", "sparse-checkout", "set", "studies/economic_review_20261029", "tests/economic_review_20261029"], cwd=REPO, check=True)
        subprocess.run(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=REPO, check=True)
    subprocess.run([sys.executable, "-m", "pip", "-q", "install", "-r", str(REPO/"studies/economic_review_20261029/requirements.txt")], check=True)
os.chdir(REPO)
SOURCE_COMMIT = subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()
print("Using source commit:", SOURCE_COMMIT)
print("Existing checkout is reused unchanged. Start a fresh runtime to resolve a newer REF.")
'''),
md("""## 1. Verify the corrected model and analysis safeguards

Tests independently compare the drift identity with a resolvent, enumerate short
shock-path corners, check the invariant box and tail bound, and check feature
timing. They do not certify all manuscript theorems.
"""),
code('''subprocess.run([sys.executable,"-m","pytest","tests/economic_review_20261029","-q"], check=True)
'''),
md("""## 2. Configure the run

Smoke: small pipeline check. Full: larger exploratory study, possibly several
minutes depending on the runtime. E1/E2/E3/E4/E6 run automatically.
E5 requires your own regularly spaced CSV. E7 remains separate below.
"""),
code('''MODE = "smoke"  # change to "full" after the first run succeeds
SEED = 20261029
CSV_PATH = None  # optional absolute path after uploading a real market CSV
WINDOW = 120
FORECAST_HORIZON = 12  # bars, not automatically minutes or hours
'''),
md("""### Optional: upload real market data

Required columns: `timestamp,market,price,signed_flow`. Use positive prices and
signed executed flow; regular bars; chronological rows; no duplicates/missing
required values. Document units, availability times, source and prior sample use.
This pipeline is exploratory and does not replace a registered primary.
Upload only if permitted by your data license. Input bytes stay out of the ZIP;
prediction outputs still include timestamps and market identifiers.
"""),
code('''UPLOAD_REAL_DATA = False
if UPLOAD_REAL_DATA:
    from google.colab import files
    uploaded = files.upload()
    if len(uploaded) != 1:
        raise ValueError("Upload exactly one CSV.")
    CSV_PATH = str(Path(next(iter(uploaded))).resolve())
    print("Using", CSV_PATH)
'''),
code('''from datetime import datetime, timezone
import uuid
OUTPUT_PARENT = Path(os.environ.get("MM_OUTPUT_PARENT", "/content" if not local else "/tmp"))
RUN = OUTPUT_PARENT/("mm-economic-review-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")+"-"+uuid.uuid4().hex[:8])
command=[sys.executable,"-m","studies.economic_review_20261029.run","--mode",MODE,"--seed",str(SEED),"--out",str(RUN)]
if CSV_PATH:
    command += ["--csv",str(CSV_PATH),"--window",str(WINDOW),"--forecast-horizon",str(FORECAST_HORIZON)]
print("Running", " ".join(command))
subprocess.run(command, check=True)
print("Results:", RUN)
'''),
md("""## 3. Inspect all results

E1: cumulative drift is different from peak loss. E2: EMA persistence is partly
mechanical; the VAR loop proxy is not generally structural Phi. E3: the known
alternatives have equal risk by construction, so this is a witness, not a uniform
rate theorem. E4: baselines match training capacity, which can drift on test.
E6: only the iid Gaussian case meets every stated interval assumption.
"""),
code('''import json
import pandas as pd
from IPython.display import display
manifest=json.loads((RUN/"manifest.json").read_text())
assert manifest["status"] == "completed"
display(pd.Series({k:manifest[k] for k in ["source_commit","status","smoke_only","elapsed_seconds","completed_experiments"]}))
for name in manifest["completed_experiments"]:
    frame=pd.read_csv(RUN/(name+".csv"))
    print("\\n",name,"-",len(frame),"rows; full rows are saved in the ZIP")
    display(frame if len(frame)<=30 else frame.head(12))
'''),
code('''import matplotlib.pyplot as plt
fig,axs=plt.subplots(1,3,figsize=(16,4))
f=pd.read_csv(RUN/"E2_filter_controls.csv")
f=f[f.dgp=="martingale_independent_flow"]
group=f.groupby("span")[["estimated_price_persistence","mechanical_persistence"]].mean()
group.plot(ax=axs[0],marker="o",title="EMA null: persistence is mechanical")
axs[0].set_ylabel("VAR price persistence")
i=pd.read_csv(RUN/"E3_information_targets.csv").drop_duplicates("delta")
axs[1].loglog(i.delta,i.known_pair_N_for_5pct_error,"o-")
axs[1].set(xlabel="Memory separation delta",ylabel="Reset experiments",title="Known-pair identification cost")
c=pd.read_csv(RUN/"E6_coverage.csv")
axs[2].errorbar(range(len(c)),c.coverage,yerr=[(c.coverage-c.mc_ci_low).clip(lower=0),(c.mc_ci_high-c.coverage).clip(lower=0)],fmt="o")
axs[2].axhline(.95,color="grey",linestyle="--")
axs[2].set(xticks=range(len(c)),xticklabels=c.setting,ylim=(-.03,1.05),ylabel="Coverage",title="Coverage and violated assumptions")
axs[2].tick_params(axis="x",labelrotation=75)
fig.tight_layout()
fig.savefig(RUN/"diagnostic_plots.png",dpi=160,bbox_inches="tight")
plt.show()
'''),
md("""## 4. Download and preserve the run

Keep all outcomes and the manifest, including failures. Never replace an original
registered result with a favorable rerun. Bring the full tables, not only plots,
to the professor. These experiments do not settle novelty, economic equilibrium
or the correctness of the specialist proofs.
"""),
code('''import shutil, hashlib
# Add the plot hash after plotting; the runner already hashes its CSV outputs.
manifest=json.loads((RUN/"manifest.json").read_text())
manifest["output_sha256"]["diagnostic_plots.png"]=hashlib.sha256((RUN/"diagnostic_plots.png").read_bytes()).hexdigest()
(RUN/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\\n")
ARCHIVE=shutil.make_archive(str(RUN),"zip",root_dir=RUN)
print("ZIP:", ARCHIVE)
if not local:
    from google.colab import files
    files.download(ARCHIVE)
'''),
md("""## 5. Data/GPU/prospective work to run separately

Read the original specifications before running these notebooks. Existing
registered tests are not silently reopened by this notebook. Future-data studies
must respect their accumulation and opening conditions.

* [K1 ETF feedback](https://github.com/Pratikn03/Fianince/blob/main/thesis/evidence/K1_LETF_Test.ipynb): economic measurement bridge, with its original data requirements.
* [B3 model diversity](https://github.com/Pratikn03/Fianince/blob/main/thesis/evidence/B3_Diversity_Test.ipynb): model/GPU access; preserve revision and prompt hashes.
* [B2 LLM test](https://github.com/Pratikn03/Fianince/blob/main/thesis/evidence/B2_LLM_Test.ipynb): inspect archived outcomes; label new runs as replications.
* [H1 participant study](https://github.com/Pratikn03/Fianince/blob/main/thesis/evidence/H1_Hyperliquid.ipynb), [H2 cascade study](https://github.com/Pratikn03/Fianince/blob/main/thesis/evidence/H2_Cascades.ipynb), [E2 prospective analysis](https://github.com/Pratikn03/Fianince/blob/main/thesis/evidence/E2_Prospective_Analysis.ipynb): verify original future-data conditions first.

These links point to the existing main-branch protocols and can change. Record
the exact commit used for each separate run. New causal and equilibrium claims
still need design work with the professor.
""")]
nbf.validate(nb)
nbf.write(nb,HERE/'Economic_Review_Experiments.ipynb')
print(HERE/'Economic_Review_Experiments.ipynb')
