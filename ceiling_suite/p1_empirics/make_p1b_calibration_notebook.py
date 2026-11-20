"""Builds P1B_PreBan_Calibration_Colab.ipynb: downloads Korean pre-ban data only (1 June 2021 to 3 November 2023) and
computes the simulator parameters for P1B's simulation check. Every request passes a date guard that refuses any
date after 3 November 2023, the last trading day before the ban was announced. It reads no return, price or
short-selling observation from the ban period or later. The KRX login comes from Colab Secrets (KRX_ID, KRX_PW)."""
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
CORE = (HERE / "p1b_core.py").read_text()
CORE_SHA = hashlib.sha256(CORE.encode()).hexdigest()

MD = f"""# P1B pre-ban calibration (reads data up to 3 November 2023 only)

P1B asks whether Korea's short-selling ban of 6 November 2023 changed each stock's price dynamics in proportion to
the short sellers' own feedback kernel, as Paper 1's sufficiency theorem predicts. Before the test can be registered,
its simulation check must be calibrated to real data, and only **pre-ban** data may be read for that.

This notebook:
1. downloads, for 1 June 2021 to 3 November 2023 only, daily prices, volumes and short-selling volumes of the
   KOSPI 200 and KOSDAQ 150 stocks that were constituents throughout, and of size-matched non-constituents;
2. fixes the treated and control lists (saved, with a hash);
3. computes the simulator's parameters (`p1b_core.calibrate`).

A guard refuses any request dated after 3 November 2023, so no ban-period data can be read by accident.

**Before running:** Colab Secrets `KRX_ID` and `KRX_PW` (key icon on the left, notebook access on), as for P1K.
Runtime: about 15 to 30 minutes. The download is cached in your Google Drive (`MyDrive/P1B_preban`), so a
disconnect resumes where it stopped. When it finishes, reply "P1B calibration done"; the result file
`MyDrive/P1B_preban/P1B_calibration.json` is read from Drive. The last cell also prints it.

Embedded estimator: `p1b_core.py`, sha256 `{CORE_SHA}`.
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
assert hashlib.sha256(CORE.encode()).hexdigest() == ''' + repr(CORE_SHA) + r''', 'p1b_core differs from the repository'
print('p1b_core.py sha256', hashlib.sha256(CORE.encode()).hexdigest())
'''

MAIN = r'''
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
sys.path.insert(0, '/content')
import p1b_core as B
from pykrx import stock

FIRST, SPLIT, LAST = '20210601', '20220901', '20231103'   # W0a = [FIRST, SPLIT), W0b = [SPLIT, LAST]
CACHE = '/content/drive/MyDrive/P1B_preban'
for sub in ('ohlcv', 'short'):
    os.makedirs(f'{CACHE}/{sub}', exist_ok=True)

def guard(*dates):
    for d in dates:
        d = str(d).replace('-', '')[:8]
        if d > LAST:
            raise SystemExit(f'refused: {d} is after {LAST}. P1B calibration reads pre-ban data only.')

def need(df, cols, what):
    miss = [c for c in cols if c not in df.columns]
    if miss:
        raise SystemExit(f'{what}: expected columns {cols}, got {list(df.columns)}. Stopped; send this message back.')

def pause():
    time.sleep(0.3)

# 1. Trading calendar and market returns
guard(FIRST, LAST)
idx = {}
for mk, code in (('KOSPI', '1001'), ('KOSDAQ', '2001')):
    df = stock.get_index_ohlcv_by_date(FIRST, LAST, code, name_display=False); pause()
    need(df, ['종가'], f'index {code}')
    idx[mk] = df['종가'].astype(float)
days = [d.strftime('%Y%m%d') for d in idx['KOSPI'].index]
assert days[0] >= FIRST and days[-1] <= LAST, (days[0], days[-1])
cal = pd.DatetimeIndex(idx['KOSPI'].index)
mret = {mk: np.log(s.reindex(cal)).diff().values for mk, s in idx.items()}
print('trading days', len(days), days[0], '-', days[-1])

# 2. Constituents throughout (KOSPI 200 = 1028, KOSDAQ 150 = 2203)
CHECK = ['20210601', '20211201', '20220602', '20221201', '20230601', '20231103']
def tday(d):
    return next(x for x in days if x >= d)
mem = {}
for mk, code in (('KOSPI', '1028'), ('KOSDAQ', '2203')):
    sets = []
    for d in CHECK:
        guard(d)
        sets.append(set(stock.get_index_portfolio_deposit_file(code, tday(d)))); pause()
    if min(len(s) for s in sets) < 100:
        raise SystemExit(f'constituent lists for {code} look wrong: sizes {[len(s) for s in sets]}')
    mem[mk] = (set.intersection(*sets), set.union(*sets))

# 3. Universe, size, sectors (as of 3 November 2023)
rows = []
for mk in ('KOSPI', 'KOSDAQ'):
    c0 = stock.get_market_cap_by_ticker(days[0], market=mk); pause()
    c1 = stock.get_market_cap_by_ticker(days[-1], market=mk); pause()
    need(c1, ['시가총액'], 'market cap')
    sec = stock.get_market_sector_classifications(days[-1], mk); pause()
    need(sec, ['종목명', '업종명'], 'sectors')
    for t in c0.index.intersection(c1.index).intersection(sec.index):
        name = str(sec.loc[t, '종목명'])
        common = t.endswith('0') and '스팩' not in name and '리츠' not in name
        rows.append(dict(ticker=t, market=mk, name=name, sector=mk + ':' + str(sec.loc[t, '업종명']),
                         cap=float(c1.loc[t, '시가총액']), common=common,
                         treated=t in mem[mk][0], ever=t in mem[mk][1]))
U = pd.DataFrame(rows)
U = U[U.common & (U.cap > 0)]
T_ = U[U.treated].sort_values('cap', ascending=False)
pool = {mk: U[(U.market == mk) & ~U.ever].copy() for mk in ('KOSPI', 'KOSDAQ')}
ctrl = []
for _, row in T_.iterrows():
    p = pool[row.market]
    if p.empty:
        continue
    j = (np.log(p.cap) - np.log(row.cap)).abs().idxmin()
    ctrl.append(p.loc[j]); pool[row.market] = p.drop(j)
C_ = pd.DataFrame(ctrl)
print('treated', len(T_), 'controls', len(C_))
lists = {'treated': T_[['ticker', 'market', 'sector']].values.tolist(),
         'control': C_[['ticker', 'market', 'sector']].values.tolist()}
lists_txt = json.dumps(lists, ensure_ascii=False, sort_keys=True)
lists_sha = hashlib.sha256(lists_txt.encode()).hexdigest()
open(f'{CACHE}/P1B_lists.json', 'w').write(lists_txt)

# 4. Per-stock downloads (cached)
def cached(kind, t, fn):
    f = f'{CACHE}/{kind}/{t}.parquet'
    if os.path.exists(f):
        return pd.read_parquet(f)
    guard(FIRST, LAST)
    df = fn(); pause()
    df.to_parquet(f)
    return df
both = pd.concat([T_, C_])
first = True
R = np.full((len(both), len(days)), np.nan); S = np.full_like(R, np.nan); M = np.full_like(R, np.nan)
turn = np.full(len(both), np.nan)
for i, (_, row) in enumerate(both.iterrows()):
    o = cached('ohlcv', row.ticker, lambda: stock.get_market_ohlcv_by_date(FIRST, LAST, row.ticker, adjusted=True))
    need(o, ['종가', '거래량', '거래대금'], 'ohlcv')
    o = o.reindex(cal)
    vol = o['거래량'].astype(float).values
    live = vol > 0
    lr = np.log(o['종가'].astype(float).where(live)).diff().values
    lr[1:][~live[:-1]] = np.nan
    R[i] = lr; M[i] = mret[row.market]
    turn[i] = np.nanmean(o['거래대금'].astype(float).values[:days.index(tday(SPLIT))]) / row.cap
    if row.treated:
        sh = cached('short', row.ticker, lambda: stock.get_shorting_volume_by_date(FIRST, LAST, row.ticker))
        if first:
            print('short-selling columns:', list(sh.columns)); first = False
        need(sh, ['공매도'], 'short selling')
        sh = sh.reindex(cal)
        S[i] = np.where(live, sh['공매도'].astype(float).values / np.where(live, vol, 1), np.nan)
    if i % 50 == 0:
        print(i, 'of', len(both), flush=True)

secs = {s: k for k, s in enumerate(sorted(both.sector.unique()))}
panel = dict(r=R, m=M, s=S, treated=both.treated.values.astype(bool), kosdaq=(both.market == 'KOSDAQ').values,
             logcap=np.log(both.cap.values), logturn=np.log(turn), sector=both.sector.map(secs).values)
k = days.index(tday(SPLIT))
sim, rep = B.calibrate(panel, slice(0, k), slice(k, len(days)))
out = dict(simulator=sim, report=rep, lists_sha256=lists_sha, n_treated_listed=len(T_), n_control_listed=len(C_),
           first_date_read=days[0], last_date_read=days[-1], core_sha256=hashlib.sha256(open('/content/p1b_core.py','rb').read()).hexdigest(),
           pykrx='1.2.9')
open(f'{CACHE}/P1B_calibration.json', 'w').write(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
print('\nSaved to MyDrive/P1B_preban/P1B_calibration.json. Last date read:', days[-1])
'''

nb = {"nbformat": 4, "nbformat_minor": 5,
      "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}},
      "cells": [{"cell_type": "markdown", "metadata": {}, "source": MD.splitlines(keepends=True)}]
      + [{"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
          "source": c.lstrip("\n").splitlines(keepends=True)} for c in (SETUP, WRITE_CORE, MAIN)]}

if __name__ == "__main__":
    for c in (SETUP, WRITE_CORE, MAIN):
        compile(c, "cell", "exec")
    out = HERE / "P1B_PreBan_Calibration_Colab.ipynb"
    out.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
    print("wrote", out.name, "core sha256", CORE_SHA)
