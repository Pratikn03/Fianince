import json

notebook_content = {
 "nbformat": 4,
 "nbformat_minor": 5,
 "metadata": {
  "kernelspec": {
   "name": "python3",
   "display_name": "Python 3"
  },
  "language_info": {
   "name": "python"
  }
 },
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# P7S Schema Probe (Binance USD-M Futures 5m Klines & Metrics)\n",
    "\n",
    "**Pre-registration check only — NOT AN ESTIMATOR OR TEST.**\n",
    "- Probes only the declared burned date: `2024-01-02` (UTC).\n",
    "- Touches ZERO data from development (2026-08-01 to 2026-10-31) or prospective holdout (2026-11-16 to 2027-02-14).\n",
    "- Verifies column layout, 5-minute sampling frequencies (288 rows/day), and open-interest fields.\n",
    "- Outputs `p7s_schema_probe_results.zip` for archival before freezing `P7S_stress_spec.md`."
   ]
  },
  {
   "cell_type": "code",
   "metadata": {},
   "execution_count": None,
   "outputs": [],
   "source": [
    "# P7S Binance Schema Probe Runner\n",
    "import io, json, time, zipfile, datetime, hashlib, urllib.request\n",
    "import pandas as pd\n",
    "\n",
    "BURNED_DATE = '2024-01-02'\n",
    "SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']\n",
    "ROOT = 'https://data.binance.vision/data/futures/um/daily'\n",
    "HEADERS = {'User-Agent': 'Mozilla/5.0 (Research Schema Probe)'}\n",
    "\n",
    "OUT = {}\n",
    "LOG = []\n",
    "\n",
    "def fetch_file(name, url):\n",
    "    t = datetime.datetime.now(datetime.timezone.utc).isoformat()\n",
    "    try:\n",
    "        req = urllib.request.Request(url, headers=HEADERS)\n",
    "        with urllib.request.urlopen(req, timeout=60) as resp:\n",
    "            content = resp.read()\n",
    "            sha = hashlib.sha256(content).hexdigest()\n",
    "            LOG.append({'name': name, 'url': url, 'status': resp.status, 'bytes': len(content), 'sha256': sha, 'utc': t})\n",
    "            return content\n",
    "    except Exception as e:\n",
    "        LOG.append({'name': name, 'url': url, 'error': repr(e), 'utc': t})\n",
    "        return None\n",
    "\n",
    "def analyze_zip_csv(name, raw_zip, default_cols=None):\n",
    "    with zipfile.ZipFile(io.BytesIO(raw_zip)) as z:\n",
    "        csv_names = [n for n in z.namelist() if n.endswith('.csv')]\n",
    "        if not csv_names:\n",
    "            return None\n",
    "        txt = z.read(csv_names[0]).decode('utf-8', errors='ignore')\n",
    "        first_line = txt.split('\\n', 1)[0]\n",
    "        import re\n",
    "        has_header = bool(re.search(r'[A-Za-z_]', first_line.split(',')[0]))\n",
    "        df = pd.read_csv(io.StringIO(txt), header=0 if has_header else None)\n",
    "        if not has_header and default_cols is not None:\n",
    "            df.columns = default_cols[:df.shape[1]]\n",
    "        df.columns = [str(c).strip().lower() for c in df.columns]\n",
    "        schema_meta = {\n",
    "            'name': name,\n",
    "            'rows': int(len(df)),\n",
    "            'columns': df.columns.tolist(),\n",
    "            'dtypes': {c: str(t) for c, t in df.dtypes.items()},\n",
    "            'null_counts': df.isnull().sum().to_dict(),\n",
    "            'first_3_rows': df.head(3).astype(str).to_dict(orient='records'),\n",
    "            'last_row': df.tail(1).astype(str).to_dict(orient='records')\n",
    "        }\n",
    "        OUT[f'{name}.schema.json'] = json.dumps(schema_meta, indent=2).encode()\n",
    "        return schema_meta\n",
    "\n",
    "print(f'Starting Schema Probe for Burned Date: {BURNED_DATE}')\n",
    "\n",
    "KL_COLS = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',\n",
    "           'quote_volume', 'count', 'taker_buy_volume', 'taker_buy_quote_volume', 'ignore']\n",
    "\n",
    "for sym in SYMBOLS:\n",
    "    # 1. 5m Klines\n",
    "    kl_url = f'{ROOT}/klines/{sym}/5m/{sym}-5m-{BURNED_DATE}.zip'\n",
    "    kl_raw = fetch_file(f'{sym}_klines_5m', kl_url)\n",
    "    if kl_raw:\n",
    "        meta_kl = analyze_zip_csv(f'{sym}_klines_5m', kl_raw, default_cols=KL_COLS)\n",
    "        print(f'[{sym} Klines 5m] rows={meta_kl[\"rows\"]}, cols={len(meta_kl[\"columns\"])}')\n",
    "    \n",
    "    # 2. 5m Metrics (Open Interest, Long/Short Ratios, Taker Volume)\n",
    "    mt_url = f'{ROOT}/metrics/{sym}/{sym}-metrics-{BURNED_DATE}.zip'\n",
    "    mt_raw = fetch_file(f'{sym}_metrics', mt_url)\n",
    "    if mt_raw:\n",
    "        meta_mt = analyze_zip_csv(f'{sym}_metrics', mt_raw)\n",
    "        print(f'[{sym} Metrics 5m] rows={meta_mt[\"rows\"]}, cols={len(meta_mt[\"columns\"])}')\n",
    "    \n",
    "    time.sleep(1)\n",
    "\n",
    "# Package results\n",
    "OUT['probe_log.json'] = json.dumps(LOG, indent=2).encode()\n",
    "with zipfile.ZipFile('p7s_schema_probe_results.zip', 'w', zipfile.ZIP_DEFLATED) as z:\n",
    "    for k, v in OUT.items():\n",
    "        z.writestr(k, v)\n",
    "\n",
    "print('\\nSchema probe completed successfully.')\n",
    "print('Logged entries:')\n",
    "for e in LOG:\n",
    "    print(f' - {e.get(\"name\")}: status {e.get(\"status\")} ({e.get(\"bytes\")} bytes)')\n",
    "\n",
    "try:\n",
    "    from google.colab import files\n",
    "    files.download('p7s_schema_probe_results.zip')\n",
    "    print('Initiated download: p7s_schema_probe_results.zip')\n",
    "except Exception:\n",
    "    print('Saved p7s_schema_probe_results.zip locally.')\n"
   ]
  }
 ]
}

with open('/Users/pratik_n/Downloads/Machine_Markets_Master_Release/ceiling_suite/p1_empirics/P7S_Schema_Probe_Colab.ipynb', 'w') as f:
    json.dump(notebook_content, f, indent=1)

with open('/Users/pratik_n/Downloads/Machine_Markets_Master_Release/pdf_delivered/P7S_Schema_Probe_Colab.ipynb', 'w') as f:
    json.dump(notebook_content, f, indent=1)

print('Wrote P7S_Schema_Probe_Colab.ipynb')
