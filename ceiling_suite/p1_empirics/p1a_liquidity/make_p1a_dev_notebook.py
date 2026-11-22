"""Builds P1A_Dev_Window_Colab.ipynb: the development-window extraction and calibration of the draft liquidity test.

The notebook embeds p1a_dev.py and checks its SHA-256 before using it. Run: python make_p1a_dev_notebook.py
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).parent
SRC = (HERE / "p1a_dev.py").read_text()
SHA = hashlib.sha256(SRC.encode()).hexdigest()

INTRO = """# P1A development window: the liquidity test's calibration (draft test, not registered)

This notebook reads **only the development window, 1 January to 30 June 2024**. The code refuses any later date. It
measures what the power simulation needs (step 2 of section 7 in `P1A_liquidity_spec_DRAFT.md`):
- how many pools and token pairs pass the activity floors;
- how reliable the weekly response estimate is;
- how strongly the instrument moves composition;
- how noisy depth is.

On purpose, it computes **no estimate of composition's effect on depth**, so the test's outcome is not previewed.
Please don't compute it from the saved files either.

**Before you start.** Create a Google Cloud project at console.cloud.google.com and copy its project ID. The free
BigQuery sandbox is enough; no billing account is needed.

**Cost.** Step 3 only estimates how much data each query would scan, which costs nothing. Step 4 refuses to run unless
the total is below 950 GB (the sandbox gives 1,000 GB free each month) and you have set `I_ACCEPT_THE_SCAN = True`.
Each query is also capped, so BigQuery stops it rather than bill more.

**Time.** About one to two hours. Everything is saved to `MyDrive/P1A_dev`. If the session disconnects, run the cells
again from the top; finished steps are skipped.

**At the end**, copy the JSON printed by step 7 into the chat with Claude.
"""

SETTINGS = """# Step 1. Settings
PROJECT_ID = ""                          # your Google Cloud project ID
OUT_DIR = "/content/drive/MyDrive/P1A_dev"
I_ACCEPT_THE_SCAN = False                # set to True after reading the estimate in step 3, then rerun"""

SETUP = f"""# Step 2. Setup: Drive, Google sign-in, and the pipeline code (checked by its SHA-256)
!pip -q install pycryptodome
import hashlib, importlib, json, os, sys
from google.colab import auth, drive
drive.mount("/content/drive")
auth.authenticate_user()
P1A_DEV_SHA256 = "{SHA}"
P1A_DEV_SRC = {json.dumps(SRC)}
assert hashlib.sha256(P1A_DEV_SRC.encode()).hexdigest() == P1A_DEV_SHA256, "the pipeline code changed"
open("/content/p1a_dev.py", "w").write(P1A_DEV_SRC)
sys.path.insert(0, "/content")
import p1a_dev as M
importlib.reload(M)
from google.cloud import bigquery
assert PROJECT_ID, "set PROJECT_ID in step 1"
client = bigquery.Client(project=PROJECT_ID)
os.makedirs(OUT_DIR, exist_ok=True)
print("ready; pipeline", P1A_DEV_SHA256[:12])"""

ESTIMATE = """# Step 3. Candidate pools, and dry runs (free): how much each query would scan
pools = M.candidate_pools()
print(len(pools), "candidate pools in", pools.pair.nunique(), "token pairs; the pool-address self-test passed")
est_file = os.path.join(OUT_DIR, "estimates.json")
if os.path.exists(est_file):
    est = json.load(open(est_file))
else:
    est = M.estimate(client, pools.pool.tolist())
    json.dump(est, open(est_file, "w"))
for name, b in est:
    print(f"  {name:12s} {b / 1e9:9.1f} GB")
total = sum(b for _, b in est)
print(f"total {total / 1e9:.1f} GB; this notebook's budget {M.BUDGET_BYTES / 1e9:.0f} GB")
print("OK to run step 4 once I_ACCEPT_THE_SCAN = True" if total <= M.BUDGET_BYTES else
      "ABOVE THE BUDGET: stop here and send these numbers to Claude")"""

EXTRACT = """# Step 4. The queries (development window only), month by month, each capped at its estimate
assert total <= M.BUDGET_BYTES, "the scan is above the budget: stop here and send the numbers from step 3 to Claude"
assert I_ACCEPT_THE_SCAN, "read the estimate in step 3, then set I_ACCEPT_THE_SCAN = True in step 1 and rerun"
M.extract(client, OUT_DIR, pools.pool.tolist(), est)
bad = M.check_tokens(OUT_DIR)
print("token check:", bad if bad else "every symbol and decimals value matches BigQuery's token table")"""

BINANCE = """# Step 5. Binance one-second prices for the pools that trade in every week (public archive, no account)
import urllib.request
try:
    urllib.request.urlopen("https://data.binance.vision/data/spot/monthly/klines/ETHUSDT/1s/ETHUSDT-1s-2024-01.zip.CHECKSUM",
                           timeout=60).read()
except Exception as e:
    raise SystemExit(f"data.binance.vision is not reachable from this session ({e}); send this message to Claude")
spw = M.swap_counts(OUT_DIR)
syms = M.needed_symbols(pools, spw)
print(len(spw), "pools have swaps;", int((spw >= M.MIN_SWAPS_WEEK).all(axis=1).sum()),
      f"have at least {M.MIN_SWAPS_WEEK} in every week; Binance symbols needed:", len(syms))
M.binance(syms, OUT_DIR)"""

PANEL = """# Step 6. Pool-week measures: response halves, composition, depth, controls
panel, arbv = M.build_panel(OUT_DIR, pools)
print(panel.pool.nunique(), "pools,", len(panel), "pool-weeks")"""

CALIB = """# Step 7. Calibration. Copy everything printed below into the chat with Claude.
res = M.calibrate(OUT_DIR, panel, arbv)
print(M.summary_for_chat(res))"""


def code(src, i):
    return {"cell_type": "code", "id": f"step{i}", "metadata": {}, "execution_count": None, "outputs": [],
            "source": src.splitlines(True)}


def main():
    cells = [{"cell_type": "markdown", "id": "intro", "metadata": {}, "source": INTRO.splitlines(True)}]
    cells += [code(s, i) for i, s in enumerate((SETTINGS, SETUP, ESTIMATE, EXTRACT, BINANCE, PANEL, CALIB), start=1)]
    nb = {"nbformat": 4, "nbformat_minor": 5, "cells": cells,
          "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"},
                       "colab": {"provenance": []}}}
    path = HERE / "P1A_Dev_Window_Colab.ipynb"
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1))
    print("wrote", path.name, "with p1a_dev.py", SHA[:12])


if __name__ == "__main__":
    main()
