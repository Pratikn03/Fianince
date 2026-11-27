"""Builds P1KS_Naver_Probe2_Colab.ipynb: second schema probe. Diagnoses the Naver foreign/institution page (status,
length, structural markers) and tries Naver's mobile investor-trend endpoints. Prints keys, counts and dates only;
no flow, price or holding values."""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

MD = """# P1KS data probe 2: Naver investor flows (no login)

Diagnoses why the desktop foreign/institution page returned no table, and tries Naver's mobile data endpoints for the
same numbers. Prints only status codes, field names, counts and dates. Runtime → Run all, then send the printed JSON.
"""

CODE = r'''
import subprocess, sys, io, re, json, time
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'lxml'], check=True)
import requests, pandas as pd

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
CODE = '005930'
rep = {}

# 1. Desktop page diagnosis (structure only)
for name, hdr in (('plain', UA), ('with_referer', dict(UA, Referer='https://finance.naver.com/item/main.naver?code=' + CODE))):
    try:
        r = requests.get('https://finance.naver.com/item/frgn.naver', params={'code': CODE, 'page': 1}, headers=hdr, timeout=20)
        raw = r.content
        txt = raw.decode('euc-kr', errors='replace')
        info = {'status': r.status_code, 'bytes': len(raw), 'final_url_host': r.url.split('/')[2],
                'has_table_tag': '<table' in txt, 'n_table_tags': txt.count('<table'),
                'has_type2': 'type2' in txt, 'has_word_foreign': '외국인' in txt,
                'title': (re.search(r'<title>(.*?)</title>', txt, re.S).group(1).strip()[:60] if '<title>' in txt else None)}
        try:
            tabs = pd.read_html(io.StringIO(txt))
            info['read_html_tables'] = len(tabs)
            info['table_columns'] = [[str(c) for c in t.columns][:12] for t in tabs if '날짜' in ' '.join(map(str, t.columns))][:2]
        except Exception as e:
            info['read_html_error'] = type(e).__name__
        rep['desktop_' + name] = info
    except Exception as e:
        rep['desktop_' + name] = {'error': type(e).__name__ + ': ' + str(e)[:150]}
    time.sleep(0.5)

# 2. Mobile endpoints (field names and dates only)
def keys_of(obj):
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        return {'type': 'list', 'n': len(obj), 'keys': sorted(obj[0].keys())[:40]}
    if isinstance(obj, dict):
        return {'type': 'dict', 'keys': sorted(obj.keys())[:40]}
    return {'type': type(obj).__name__}

def date_range(obj):
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        for k in ('bizdate', 'localTradedAt', 'date', 'tradeDate'):
            if k in obj[0]:
                v = [str(o.get(k))[:10] for o in obj]
                return {'date_key': k, 'first': v[0], 'last': v[-1]}
    return None

urls = {
    'trend_page': 'https://m.stock.naver.com/api/stock/%s/trend?pageSize=20' % CODE,
    'trend_bizdate_2015': 'https://m.stock.naver.com/api/stock/%s/trend?pageSize=20&bizdate=20150130' % CODE,
    'investor_trend': 'https://m.stock.naver.com/api/stock/%s/investorTrend?pageSize=20' % CODE,
}
for name, u in urls.items():
    try:
        r = requests.get(u, headers=UA, timeout=20)
        info = {'status': r.status_code, 'bytes': len(r.content)}
        try:
            j = r.json()
            info['shape'] = keys_of(j)
            info['dates'] = date_range(j)
        except Exception as e:
            info['json_error'] = type(e).__name__
        rep['mobile_' + name] = info
    except Exception as e:
        rep['mobile_' + name] = {'error': type(e).__name__ + ': ' + str(e)[:150]}
    time.sleep(0.5)

print(json.dumps(rep, indent=1, ensure_ascii=False))
print('\nOnly status codes, field names, counts and dates were printed.')
'''


def cell(kind, src):
    c = {'cell_type': kind, 'metadata': {}, 'source': src.strip('\n').splitlines(keepends=True)}
    if kind == 'code':
        c.update({'execution_count': None, 'outputs': []})
    return c


nb = {'nbformat': 4, 'nbformat_minor': 5,
      'metadata': {'kernelspec': {'name': 'python3', 'display_name': 'Python 3'}, 'language_info': {'name': 'python'}},
      'cells': [cell('markdown', MD), cell('code', CODE)]}
out = HERE / 'P1KS_Naver_Probe2_Colab.ipynb'
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print('wrote', out.name)
