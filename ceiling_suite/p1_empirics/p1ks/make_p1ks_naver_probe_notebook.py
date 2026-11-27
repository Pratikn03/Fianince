"""Builds P1KS_Naver_Probe_Colab.ipynb: a schema probe for Naver Finance as the P1KS data source (KRX requires Korean
identity verification). It prints column names, row counts, page counts and the earliest reachable date only. It
prints no flow, price or holding value and computes no statistic. No login."""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

MD = """# P1KS data probe: Naver Finance (no login)

KRX sign-up needs Korean identity verification, so this checks whether Naver Finance can supply the same inputs:
daily foreign net buying, prices and shares outstanding by stock, back to 2015, plus stock lists that include
delisted stocks.

It prints **only** column names, row counts, page counts and the earliest date reachable. It prints no flow, price or
holding value. Runtime → Run all, then send back the printed JSON.
"""

CODE = r'''
import subprocess, sys, io, re, json, time
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'finance-datareader', 'lxml'], check=True)
import requests, pandas as pd

H = {'User-Agent': 'Mozilla/5.0 (research probe)'}
TICKERS = ['005930', '000660', '035720']   # two KOSPI stocks, one KOSPI 200 internet stock
report = {}

def frgn_page(code, page):
    r = requests.get('https://finance.naver.com/item/frgn.naver', params={'code': code, 'page': page}, headers=H, timeout=20)
    r.encoding = 'euc-kr'
    tables = pd.read_html(io.StringIO(r.text))
    tab = None
    for t in tables:
        cols = ' '.join(map(str, t.columns))
        if '날짜' in cols and '외국인' in cols:
            tab = t
            break
    last = max([int(p) for p in re.findall(r'page=(\d+)', r.text)] or [1])
    return tab, last

def dates_of(tab):
    col = [c for c in tab.columns if '날짜' in str(c)][0]
    d = pd.to_datetime(tab[col], format='%Y.%m.%d', errors='coerce').dropna()
    return d

for code in TICKERS:
    out = {}
    try:
        tab, last = frgn_page(code, 1)
        out['frgn_columns'] = [str(c) for c in tab.columns]
        out['frgn_rows_page1'] = int(len(dates_of(tab)))
        out['frgn_last_page_link'] = last
        tab_last, _ = frgn_page(code, last)
        d = dates_of(tab_last)
        out['frgn_earliest_date'] = str(d.min().date()) if len(d) else None
        lo, hi = 1, last
        while lo < hi:                      # first page whose newest date is before 2015-01-01 (dates only)
            mid = (lo + hi) // 2
            t, _ = frgn_page(code, mid)
            dm = dates_of(t)
            if len(dm) and dm.max() < pd.Timestamp('2015-01-01'):
                hi = mid
            else:
                lo = mid + 1
            time.sleep(0.3)
        out['frgn_page_reaching_2015'] = lo
    except Exception as e:
        out['frgn_error'] = type(e).__name__ + ': ' + str(e)[:200]
    try:
        r = requests.get('https://fchart.stock.naver.com/sise.nhn',
                         params={'symbol': code, 'timeframe': 'day', 'count': 4000, 'requestType': 0}, headers=H, timeout=20)
        items = re.findall(r'data="([^"]+)"', r.text)
        out['fchart_rows'] = len(items)
        out['fchart_fields_per_row'] = len(items[0].split('|')) if items else 0
        out['fchart_earliest_date'] = items[0].split('|')[0] if items else None
    except Exception as e:
        out['fchart_error'] = type(e).__name__ + ': ' + str(e)[:200]
    report[code] = out
    time.sleep(0.5)

try:
    import FinanceDataReader as fdr
    for name in ('KOSPI', 'KOSDAQ', 'KRX-DELISTING'):
        try:
            df = fdr.StockListing(name)
            report['fdr_' + name] = {'rows': int(len(df)), 'columns': [str(c) for c in df.columns][:15]}
        except Exception as e:
            report['fdr_' + name] = {'error': type(e).__name__ + ': ' + str(e)[:200]}
except Exception as e:
    report['fdr_import_error'] = type(e).__name__ + ': ' + str(e)[:200]

print(json.dumps(report, indent=1, ensure_ascii=False))
print('\nOnly column names, row and page counts and dates were printed. No flow, price or holding values.')
'''


def cell(kind, src):
    c = {'cell_type': kind, 'metadata': {}, 'source': src.strip('\n').splitlines(keepends=True)}
    if kind == 'code':
        c.update({'execution_count': None, 'outputs': []})
    return c


nb = {'nbformat': 4, 'nbformat_minor': 5,
      'metadata': {'kernelspec': {'name': 'python3', 'display_name': 'Python 3'}, 'language_info': {'name': 'python'}},
      'cells': [cell('markdown', MD), cell('code', CODE)]}
out = HERE / 'P1KS_Naver_Probe_Colab.ipynb'
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print('wrote', out.name)
