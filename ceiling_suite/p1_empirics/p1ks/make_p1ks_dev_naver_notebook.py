"""Builds P1KS_Dev_Window_Naver_Colab.ipynb: development-window calibration (2015-2019 only) from Naver Finance.

Flows: Naver mobile trend endpoint (foreignerPureBuyQuant, accumulatedTradingVolume), paged back from 2019-12-30.
Prices: Naver siseJson with endTime 2019-12-30; fallback fchart, with rows from 2020 on discarded on arrival.
Universe: a fixed random sample of 700 common stocks listed on KOSPI or KOSDAQ through 2015-2019 (FinanceDataReader
listings plus stocks delisted from 2020 on). Groups for calibration: 'large' = top quarter of the sample by mean
2015-2019 traded value (a proxy for index membership, which Naver does not keep). Prints cross-stock summaries only."""
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = (HERE / 'p1ks_dev.py').read_text()
SHA = hashlib.sha256(SRC.encode()).hexdigest()

MD = f"""# P1KS development window from Naver Finance (2015–2019 only, no login)

Calibration for the power check of the planned Korea short-sale test. **Nothing dated 2020 or later is used**: flow
requests start at 2019-12-30 and page backwards, prices are requested up to 2019-12-30, and the calibration code
stops if any later date reaches it. It prints summary statistics across stocks only.

Runtime → Run all. Downloading takes roughly 30–90 minutes; it caches each stock, so if Colab disconnects, rerun
and it resumes. Send back the final printed JSON.

Calibration code: `p1ks_dev.py`, SHA-256 `{SHA}`.
"""

SETUP = r'''
import os, subprocess, sys, hashlib
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'finance-datareader', 'lxml'], check=True)
SRC = %s
assert hashlib.sha256(SRC.encode()).hexdigest() == %r, 'calibration code changed'
open('p1ks_dev.py', 'w').write(SRC)
print('setup ok')
''' % (repr(SRC), SHA)

RUN = r'''
import ast, io, json, os, pickle, random, re, time, hashlib
import numpy as np, pandas as pd, requests
import FinanceDataReader as fdr
import p1ks_dev as P

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
END, PSTART = '20191230', '20140901'
CUT = pd.Timestamp('2020-01-01')
CACHE = '/content/p1ks_cache'
os.makedirs(CACHE, exist_ok=True)

# ---------------------------------------------------------------- universe (listings only, no market data)
cur = pd.concat([fdr.StockListing('KOSPI'), fdr.StockListing('KOSDAQ')])
cur_codes = set(cur['Code'].astype(str))
dl = fdr.StockListing('KRX-DELISTING')
dl = dl[dl['Market'].astype(str).isin(['KOSPI', 'KOSDAQ'])]
dl = dl[(pd.to_datetime(dl['ListingDate'], errors='coerce') < pd.Timestamp('2015-01-01'))
        & (pd.to_datetime(dl['DelistingDate'], errors='coerce') >= CUT)]
codes = sorted(c for c in cur_codes | set(dl['Symbol'].astype(str)) if re.fullmatch(r'\d{5}0', c))
rng = random.Random(20261127)
universe = sorted(rng.sample(codes, min(700, len(codes))))
print('candidates', len(codes), 'sampled', len(universe))

def num(v):
    if v is None:
        return np.nan
    s = str(v).replace(',', '').replace('+', '').strip()
    try:
        return float(s)
    except ValueError:
        return np.nan

def trend_page(code, bizdate, size):
    r = requests.get('https://m.stock.naver.com/api/stock/%s/trend' % code,
                     params={'pageSize': size, 'bizdate': bizdate}, headers=UA, timeout=20)
    r.raise_for_status()
    return r.json()

# page size: the largest of 100 / 60 / 20 that the endpoint honours
PAGE = 20
for size in (100, 60):
    try:
        j = trend_page('005930', END, size)
        if isinstance(j, list) and len(j) >= size:
            PAGE = size
            break
    except Exception:
        pass
print('trend page size', PAGE)

def flows(code):
    rows, biz, seen = [], END, set()
    for _ in range(200):
        j = trend_page(code, biz, PAGE)
        if not isinstance(j, list) or not j:
            break
        for o in j:
            d = str(o.get('bizdate', ''))[:8]
            if d and d not in seen and d < '20200101':
                seen.add(d)
                rows.append((d, num(o.get('foreignerPureBuyQuant')), num(o.get('accumulatedTradingVolume')),
                             num(o.get('closePrice'))))
        earliest = min(str(o.get('bizdate', ''))[:8] for o in j)
        if earliest <= PSTART:
            break
        nb = (pd.Timestamp(earliest) - pd.Timedelta(days=1)).strftime('%Y%m%d')
        if nb >= biz:
            break
        biz = nb
        time.sleep(0.12)
    if not rows:
        return None
    df = pd.DataFrame(rows, columns=['date', 'fnet', 'vol', 'rawclose'])
    df['date'] = pd.to_datetime(df['date'])
    return df.set_index('date').sort_index()

PRICE_SOURCE = {}
def prices(code):
    try:
        r = requests.get('https://api.finance.naver.com/siseJson.naver',
                         params={'symbol': code, 'requestType': 1, 'startTime': PSTART, 'endTime': END, 'timeframe': 'day'},
                         headers=UA, timeout=20)
        data = ast.literal_eval(r.text.strip().replace('\n', '').replace('\t', ''))
        hdr, body = data[0], data[1:]
        ci = [i for i, h in enumerate(hdr) if '종가' in str(h)][0]
        s = pd.Series({pd.Timestamp(str(b[0])): float(b[ci]) for b in body if str(b[0]) < '20200101'})
        if len(s) > 100:
            PRICE_SOURCE['siseJson'] = PRICE_SOURCE.get('siseJson', 0) + 1
            return s.sort_index()
    except Exception:
        pass
    r = requests.get('https://fchart.stock.naver.com/sise.nhn',
                     params={'symbol': code, 'timeframe': 'day', 'count': 3000, 'requestType': 0}, headers=UA, timeout=20)
    items = [it.split('|') for it in re.findall(r'data="([^"]+)"', r.text)]
    items = [it for it in items if it[0] < '20200101']          # later rows discarded on arrival
    PRICE_SOURCE['fchart'] = PRICE_SOURCE.get('fchart', 0) + 1
    return pd.Series({pd.Timestamp(it[0]): float(it[4]) for it in items}).sort_index()

def load(code):
    f = os.path.join(CACHE, code + '.pkl')
    if os.path.exists(f):
        return pickle.load(open(f, 'rb'))
    fl = flows(code)
    if fl is None or len(fl) < 300:
        out = None
    else:
        px = prices(code)
        df = fl.join(px.rename('close'), how='left')
        df['scale'] = df['vol'].rolling(60).mean()
        df = df[df.index < CUT]
        out = df
    pickle.dump(out, open(f, 'wb'))
    return out

results, failures, split_jumps, tv = {}, {}, 0, {}
for i, code in enumerate(universe):
    try:
        df = load(code)
        if df is None or df['close'].notna().sum() < 300:
            failures[code] = 'short history'
            continue
        lr = np.log(df['close']).diff().abs()
        if (lr > np.log(1.35)).any():          # beyond the +-30% daily limit: unadjusted split; drop the stock
            split_jumps += 1
            continue
        tv[code] = float((df['rawclose'] * df['vol'])[df.index >= pd.Timestamp('2015-01-01')].mean())
        results[code] = P.stock_stats(df[['close', 'scale', 'fnet']].dropna(subset=['close']))
    except Exception as e:
        failures[code] = type(e).__name__
    if i % 50 == 0:
        print(i, 'of', len(universe), '| ok', len(results), '| failures', len(failures), flush=True)

cut = np.quantile(list(tv.values()), 0.75) if tv else np.inf
groups = {c: ('large' if tv.get(c, 0) >= cut else 'other') for c in results}
summary = P.summarize(results, groups)
summary.update({'n_sampled': len(universe), 'n_ok': len(results), 'n_failures': len(failures),
                'failure_kinds': sorted(set(failures.values()))[:10], 'n_dropped_split_jumps': split_jumps,
                'trend_page_size': PAGE, 'price_source_counts': PRICE_SOURCE,
                'code_sha256': hashlib.sha256(open('p1ks_dev.py').read().encode()).hexdigest()})
print(json.dumps(summary, indent=1, ensure_ascii=False))
print('Only cross-stock summaries were printed. Nothing dated 2020 or later was used.')
'''


def cell(kind, src):
    c = {'cell_type': kind, 'metadata': {}, 'source': src.strip('\n').splitlines(keepends=True)}
    if kind == 'code':
        c.update({'execution_count': None, 'outputs': []})
    return c


nb = {'nbformat': 4, 'nbformat_minor': 5,
      'metadata': {'kernelspec': {'name': 'python3', 'display_name': 'Python 3'}, 'language_info': {'name': 'python'}},
      'cells': [cell('markdown', MD), cell('code', SETUP), cell('code', RUN)]}
out = HERE / 'P1KS_Dev_Window_Naver_Colab.ipynb'
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print('wrote', out.name, 'p1ks_dev sha', SHA[:12])
