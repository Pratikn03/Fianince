"""Builds P7S_Availability_Colab.ipynb: a listing-only check of which Binance USD-M daily files exist.

It sends HEAD requests and bucket-listing requests only. No kline or metrics file is downloaded, so no price,
return or open-interest value is read. Its purpose is to let the evaluation window of P7S amendment A1 be fixed
on files that exist. It is not a test and computes no statistic.
"""
import json
import pathlib

MD = """# P7S availability check (listing only)

**No market data are downloaded.** The notebook asks the public Binance archive which daily files exist:
- a bucket listing of the symbol folders;
- HEAD requests for the 5-minute kline file and the metrics file of each USDT perpetual on ten probe dates;
- HEAD requests for BTCUSDT and ETHUSDT metrics on the first day of each month from 2020-01 on.

It reads no price, return or open-interest value, computes no statistic and burns no date.
Run the cell, then send back the printed summary and `p7s_availability.json`.
"""

CODE = r'''
import json, time, datetime, urllib.request, urllib.error, urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

S3 = 'https://s3-ap-northeast-1.amazonaws.com/data.binance.vision'
ROOT = 'https://data.binance.vision/data/futures/um/daily'
HEADERS = {'User-Agent': 'Mozilla/5.0 (research availability check)'}
PROBE_DATES = ['2022-01-01', '2022-07-01', '2023-01-01', '2023-07-01', '2023-12-02', '2024-01-03',
               '2024-07-01', '2025-07-01', '2026-07-01', '2026-10-28']


def parse_listing(xml_text):
    """Returns (folder names, next marker or None) from one S3 listing page."""
    root = ET.fromstring(xml_text)
    ns = root.tag.split('}')[0] + '}' if root.tag.startswith('{') else ''
    names = [e.find(ns + 'Prefix').text for e in root.findall(ns + 'CommonPrefixes')]
    trunc = root.find(ns + 'IsTruncated')
    nxt = root.find(ns + 'NextMarker')
    more = trunc is not None and trunc.text == 'true'
    return names, ((nxt.text if nxt is not None else (names[-1] if names else None)) if more else None)


def list_folders(prefix):
    out, marker = [], None
    for _ in range(50):
        url = f'{S3}?delimiter=/&prefix={urllib.parse.quote(prefix)}'
        if marker:
            url += '&marker=' + urllib.parse.quote(marker)
        with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as r:
            names, marker = parse_listing(r.read().decode())
        out += names
        if marker is None:
            break
    return [n[len(prefix):].strip('/') for n in out]


def exists(url):
    """True / False from a HEAD request; None if the request failed for another reason."""
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS, method='HEAD')
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status == 200
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                return False
        except Exception:
            pass
        time.sleep(1 + attempt)
    return None


def kline_url(sym, d):
    return f'{ROOT}/klines/{sym}/5m/{sym}-5m-{d}.zip'


def metrics_url(sym, d):
    return f'{ROOT}/metrics/{sym}/{sym}-metrics-{d}.zip'


t0 = time.time()
folders = list_folders('data/futures/um/daily/klines/')
symbols = sorted(s for s in folders if s.endswith('USDT') and '_' not in s)
print(f'{len(folders)} kline folders listed, {len(symbols)} USDT perpetual symbols')

jobs = [(s, d, kind) for s in symbols for d in PROBE_DATES for kind in ('kline', 'metrics')]
with ThreadPoolExecutor(16) as pool:
    res = list(pool.map(lambda j: exists(kline_url(j[0], j[1]) if j[2] == 'kline' else metrics_url(j[0], j[1])), jobs))
table = {s: {d: {} for d in PROBE_DATES} for s in symbols}
for (s, d, kind), ok in zip(jobs, res):
    table[s][d][kind] = ok

print('\nSymbols with a file on each probe date')
print('date         kline  metrics  both  failed requests')
for d in PROBE_DATES:
    k = sum(table[s][d]['kline'] is True for s in symbols)
    m = sum(table[s][d]['metrics'] is True for s in symbols)
    b = sum(table[s][d]['kline'] is True and table[s][d]['metrics'] is True for s in symbols)
    f = sum(table[s][d][x] is None for s in symbols for x in ('kline', 'metrics'))
    print(f'{d}   {k:5d}  {m:7d}  {b:4d}  {f}')

both_all = [s for s in symbols if all(table[s][d]['kline'] and table[s][d]['metrics'] for d in PROBE_DATES[4:])]
print(f'\nSymbols with both files on every probe date from {PROBE_DATES[4]} on: {len(both_all)}')

months = [f'{y}-{m:02d}-01' for y in range(2020, 2027) for m in range(1, 13) if (y, m) <= (2026, 11)]
first = {}
for sym in ('BTCUSDT', 'ETHUSDT'):
    with ThreadPoolExecutor(8) as pool:
        ok = list(pool.map(lambda d: exists(metrics_url(sym, d)), months))
    have = [d for d, o in zip(months, ok) if o]
    first[sym] = {'first_month_start_with_metrics': have[0] if have else None,
                  'months_missing_after_first': [d for d, o in zip(months, ok) if have and d > have[0] and o is False]}
    print(sym, 'metrics: first month start with a file =', first[sym]['first_month_start_with_metrics'],
          '| later month starts without a file =', first[sym]['months_missing_after_first'])

out = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'probe_dates': PROBE_DATES,
       'n_symbols': len(symbols), 'symbols_complete_from_2023_12_02': both_all, 'first_metrics': first,
       'table': table, 'note': 'HEAD and listing requests only; no file content was downloaded'}
json.dump(out, open('p7s_availability.json', 'w'), indent=1)
print(f'\nWrote p7s_availability.json in {time.time() - t0:.0f}s. No file content was downloaded.')
try:
    from google.colab import files
    files.download('p7s_availability.json')
except Exception:
    pass
'''

nb = {"nbformat": 4, "nbformat_minor": 5,
      "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}},
      "cells": [{"cell_type": "markdown", "metadata": {}, "source": MD.splitlines(keepends=True)},
                {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                 "source": CODE.lstrip("\n").splitlines(keepends=True)}]}

if __name__ == "__main__":
    here = pathlib.Path(__file__).resolve().parent
    (here / "P7S_Availability_Colab.ipynb").write_text(json.dumps(nb, indent=1))
    print("wrote P7S_Availability_Colab.ipynb")
