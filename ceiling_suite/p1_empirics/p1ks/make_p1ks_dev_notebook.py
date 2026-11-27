"""Builds P1KS_Dev_Window_Colab.ipynb: development-window calibration for the P1KS power check.

Reads KRX data dated 2014-09-01 to 2019-12-30 only (asserted), for KOSPI 200 and KOSDAQ 150 constituents on
2019-01-02 and a fixed random sample of 400 other common stocks listed that day. Prints cross-stock summaries only.
The KRX login comes from Colab Secrets (KRX_ID, KRX_PW); nothing is typed into the notebook."""
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = (HERE / 'p1ks_dev.py').read_text()
SHA = hashlib.sha256(SRC.encode()).hexdigest()

MD = f"""# P1KS development window (2015–2019 only)

Calibration for the power check of the planned Korea short-sale test. **It reads nothing dated 2020 or later**, and
the code stops if any date reaches 2020. It prints summary statistics across stocks only.

**Before running:** in Colab, open the key icon (Secrets) and make sure `KRX_ID` and `KRX_PW` exist with notebook
access on. Never paste them into a cell or into chat. Then Runtime → Run all. The download takes about 20–40 minutes.
Send back the final printed JSON.

Calibration code: `p1ks_dev.py`, SHA-256 `{SHA}`.
"""

SETUP = r'''
import os, subprocess, sys, time, json, hashlib, random
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'pykrx==1.2.9'], check=True)
from google.colab import userdata
os.environ['KRX_ID'] = userdata.get('KRX_ID')
os.environ['KRX_PW'] = userdata.get('KRX_PW')
SRC = %s
assert hashlib.sha256(SRC.encode()).hexdigest() == %r, 'calibration code changed'
open('p1ks_dev.py', 'w').write(SRC)
print('setup ok')
''' % (repr(SRC), SHA)

RUN = r'''
import time, json, hashlib, random
import numpy as np, pandas as pd
from pykrx import stock
import p1ks_dev as P

DAY = '20190102'
P_START, F_START, END = '20140901', '20150102', '20191230'
assert END < '20200101'
idx = set(stock.get_index_portfolio_deposit_file('1028', DAY)) | set(stock.get_index_portfolio_deposit_file('2203', DAY))
allt = sorted(t for m in ('KOSPI', 'KOSDAQ') for t in stock.get_market_ticker_list(DAY, market=m) if t.endswith('0'))
others = sorted(t for t in allt if t not in idx)
rng = random.Random(20261127)
sample_other = sorted(rng.sample(others, min(400, len(others))))
universe = sorted(idx) + sample_other
groups = {t: ('index' if t in idx else 'other') for t in universe}
print('index constituents:', len(idx), ' other sampled:', len(sample_other), ' of', len(others))

def fetch(t):
    for attempt in range(4):
        try:
            px = stock.get_market_ohlcv_by_date(P_START, END, t, adjusted=True)
            time.sleep(0.25)
            cap = stock.get_market_cap_by_date(P_START, END, t)
            time.sleep(0.25)
            fl = stock.get_market_trading_value_by_date(F_START, END, t, detail=True)
            time.sleep(0.25)
            fcols = [c for c in fl.columns if c in ('외국인', '기타외국인')]
            if len(fcols) != 2:
                return None, 'foreign columns: ' + ','.join(map(str, fl.columns))
            df = pd.DataFrame({'close': px['종가'], 'mcap': cap['시가총액']}).join(fl[fcols].sum(axis=1).rename('fnet'))
            df.index = pd.to_datetime(df.index)
            df = df[(df.index < pd.Timestamp('2020-01-01'))]
            df['fnet'] = df['fnet'].where(df.index >= pd.Timestamp('2015-01-02'))
            return df, None
        except Exception as e:
            err = type(e).__name__ + ': ' + str(e)[:120]
            time.sleep(2 + 3 * attempt)
    return None, err

results, failures = {}, {}
for i, t in enumerate(universe):
    df, err = fetch(t)
    if df is None:
        failures[t] = err
        continue
    try:
        results[t] = P.stock_stats(df)
    except Exception as e:
        failures[t] = 'estimate: ' + type(e).__name__
    if i % 50 == 0:
        print(i, 'of', len(universe), 'done;', len(failures), 'failures', flush=True)

summary = P.summarize(results, groups)
summary['n_failures'] = len(failures)
summary['failure_kinds'] = sorted(set(v.split(':')[0] for v in failures.values()))[:10]
summary['code_sha256'] = hashlib.sha256(open('p1ks_dev.py').read().encode()).hexdigest()
print(json.dumps(summary, indent=1, ensure_ascii=False))
print('Only cross-stock summaries were printed. No data dated 2020 or later were read.')
'''


def cell(kind, src):
    c = {'cell_type': kind, 'metadata': {}, 'source': src.strip('\n').splitlines(keepends=True)}
    if kind == 'code':
        c.update({'execution_count': None, 'outputs': []})
    return c


nb = {'nbformat': 4, 'nbformat_minor': 5,
      'metadata': {'kernelspec': {'name': 'python3', 'display_name': 'Python 3'}, 'language_info': {'name': 'python'}},
      'cells': [cell('markdown', MD), cell('code', SETUP), cell('code', RUN)]}
out = HERE / 'P1KS_Dev_Window_Colab.ipynb'
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print('wrote', out.name, 'p1ks_dev sha', SHA[:12])
