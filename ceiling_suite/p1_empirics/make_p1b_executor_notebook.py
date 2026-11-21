"""Builds P1B_Executor_Colab.ipynb: the one-time data run of P1B (draft; usable only after the simulation check passes
and the author approves registration). It reads the treated and control lists fixed by the calibration notebook,
downloads 1 June 2021 to 30 October 2026 for those stocks, computes p1b_core.run_statistics once, and prints the
verdict. A marker file in Drive refuses a second run."""
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
CORE = (HERE / "p1b_core.py").read_text()
CORE_SHA = hashlib.sha256(CORE.encode()).hexdigest()

MD = f"""# P1B data run (one time only)

Run this only after P1B is registered (spec, code and lists hashed in a commit of their own, with the author's
approval). It downloads ban-period and post-reinstatement data, computes the registered statistics once, and prints
the verdict. A marker in `MyDrive/P1B_preban/P1B_OPENED` makes a second run stop. Embedded estimator sha256
`{CORE_SHA}`.
"""

SETUP = r'''
import os, subprocess, sys
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'pykrx==1.2.9', 'pyarrow'], check=True)
from google.colab import userdata, drive
os.environ['KRX_ID'] = userdata.get('KRX_ID')
os.environ['KRX_PW'] = userdata.get('KRX_PW')
drive.mount('/content/drive')
'''

WRITE_CORE = "import hashlib, pathlib\nCORE = " + repr(CORE) + "\n" + r'''
pathlib.Path('/content/p1b_core.py').write_text(CORE)
assert hashlib.sha256(CORE.encode()).hexdigest() == ''' + repr(CORE_SHA) + r''', 'p1b_core differs from the registered file'
'''

MAIN = r'''
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
sys.path.insert(0, '/content')
import p1b_core as B
from pykrx import stock

CACHE = '/content/drive/MyDrive/P1B_preban'
MARK = f'{CACHE}/P1B_OPENED'
if os.path.exists(MARK):
    raise SystemExit('P1B has already been run once (marker present). Registered rule: no second run.')
REG = json.load(open(f'{CACHE}/P1B_registration.json'))      # written at registration: hashes and windows
lists_txt = open(f'{CACHE}/P1B_lists.json').read()
assert hashlib.sha256(lists_txt.encode()).hexdigest() == REG['lists_sha256'], 'lists differ from the registered ones'
lists = json.loads(lists_txt)
FIRST, LAST, CAPDAY = '20210601', '20261030', '20231103'
W = {'W0a': ('20210601', '20220831'), 'W0b': ('20220901', '20231103'),
     'W1': ('20231204', '20250328'), 'W2': ('20250502', '20261030')}
open(MARK, 'w').write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))   # the run counts from here

def pause():
    time.sleep(0.3)

idx = {}
for mk, code in (('KOSPI', '1001'), ('KOSDAQ', '2001')):
    idx[mk] = stock.get_index_ohlcv_by_date(FIRST, LAST, code, name_display=False)['종가'].astype(float); pause()
cal = pd.DatetimeIndex(idx['KOSPI'].index)
days = [d.strftime('%Y%m%d') for d in cal]
mret = {mk: np.log(s.reindex(cal)).diff().values for mk, s in idx.items()}
caps = {}
for mk in ('KOSPI', 'KOSDAQ'):
    c = stock.get_market_cap_by_ticker(CAPDAY, market=mk); pause()
    caps.update({(mk, t): float(c.loc[t, '시가총액']) for t in c.index})
rows = [(t, mk, sec, True) for t, mk, sec in lists['treated']] + [(t, mk, sec, False) for t, mk, sec in lists['control']]
R = np.full((len(rows), len(days)), np.nan); S = np.full_like(R, np.nan); M = np.full_like(R, np.nan)
turn = np.full(len(rows), np.nan); cap = np.full(len(rows), np.nan)
w0a_end = next(i for i, d in enumerate(days) if d > W['W0a'][1])
for i, (t, mk, sec, tr) in enumerate(rows):
    o = stock.get_market_ohlcv_by_date(FIRST, LAST, t, adjusted=True).reindex(cal); pause()
    vol = o['거래량'].astype(float).values
    live = vol > 0
    lr = np.log(o['종가'].astype(float).where(live)).diff().values
    lr[1:][~live[:-1]] = np.nan
    R[i] = lr; M[i] = mret[mk]
    cap[i] = caps.get((mk, t), np.nan)
    turn[i] = np.nanmean(o['거래대금'].astype(float).values[:w0a_end]) / cap[i]
    if tr:
        sh = stock.get_shorting_volume_by_date(FIRST, LAST, t).reindex(cal); pause()
        S[i] = np.where(live, sh['공매도'].astype(float).values / np.where(live, vol, 1), np.nan)
    if i % 50 == 0:
        print(i, 'of', len(rows), flush=True)
secs = {s: k for k, s in enumerate(sorted({r[2] for r in rows}))}
panel = dict(r=R, m=M, s=S, treated=np.array([r[3] for r in rows]), kosdaq=np.array([r[1] == 'KOSDAQ' for r in rows]),
             logcap=np.log(cap), logturn=np.log(turn), sector=np.array([secs[r[2]] for r in rows]))
def sl(a, b):
    i0 = next(i for i, d in enumerate(days) if d >= a); i1 = max(i for i, d in enumerate(days) if d <= b) + 1
    return slice(i0, i1)
Ws = {k: sl(*v) for k, v in W.items()}
out = B.run_statistics(panel, Ws)
out['first_date'], out['last_date'] = days[0], days[-1]
open(f'{CACHE}/P1B_result.json', 'w').write(json.dumps(out, indent=1, default=float))
print(json.dumps(out, indent=1, default=float))
print('\nVERDICT:', out['verdict'])
'''

nb = {"nbformat": 4, "nbformat_minor": 5,
      "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}},
      "cells": [{"cell_type": "markdown", "metadata": {}, "source": MD.splitlines(keepends=True)}]
      + [{"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
          "source": c.lstrip("\n").splitlines(keepends=True)} for c in (SETUP, WRITE_CORE, MAIN)]}

if __name__ == "__main__":
    for c in (SETUP, WRITE_CORE, MAIN):
        compile(c, "cell", "exec")
    (HERE / "P1B_Executor_Colab_DRAFT.ipynb").write_text(json.dumps(nb, indent=1, ensure_ascii=False))
    print("wrote P1B_Executor_Colab_DRAFT.ipynb; core sha256", CORE_SHA)
