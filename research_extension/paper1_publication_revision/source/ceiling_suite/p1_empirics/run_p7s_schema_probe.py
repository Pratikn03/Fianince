# P7S Binance Schema Probe Local Runner
import io, json, time, zipfile, datetime, hashlib, urllib.request, re, os
import pandas as pd

BURNED_DATE = '2024-01-02'
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
ROOT = 'https://data.binance.vision/data/futures/um/daily'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Research Schema Probe)'}

OUT = {}
LOG = []

def fetch_file(name, url):
    t = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=60) as resp:
            content = resp.read()
            sha = hashlib.sha256(content).hexdigest()
            LOG.append({'name': name, 'url': url, 'status': resp.status, 'bytes': len(content), 'sha256': sha, 'utc': t})
            return content
    except Exception as e:
        LOG.append({'name': name, 'url': url, 'error': repr(e), 'utc': t})
        return None

def analyze_zip_csv(name, raw_zip, default_cols=None):
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as z:
        csv_names = [n for n in z.namelist() if n.endswith('.csv')]
        if not csv_names:
            return None
        txt = z.read(csv_names[0]).decode('utf-8', errors='ignore')
        first_line = txt.split('\n', 1)[0]
        has_header = bool(re.search(r'[A-Za-z_]', first_line.split(',')[0]))
        df = pd.read_csv(io.StringIO(txt), header=0 if has_header else None)
        if not has_header and default_cols is not None:
            df.columns = default_cols[:df.shape[1]]
        df.columns = [str(c).strip().lower() for c in df.columns]
        schema_meta = {
            'name': name,
            'rows': int(len(df)),
            'columns': df.columns.tolist(),
            'dtypes': {c: str(t) for c, t in df.dtypes.items()},
            'null_counts': df.isnull().sum().to_dict(),
            'first_3_rows': df.head(3).astype(str).to_dict(orient='records'),
            'last_row': df.tail(1).astype(str).to_dict(orient='records')
        }
        OUT[f'{name}.schema.json'] = json.dumps(schema_meta, indent=2).encode()
        return schema_meta

def main():
    print(f'Starting Schema Probe for Declared Burned Date: {BURNED_DATE}')
    KL_COLS = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
               'quote_volume', 'count', 'taker_buy_volume', 'taker_buy_quote_volume', 'ignore']

    for sym in SYMBOLS:
        # 1. 5m Klines
        kl_url = f'{ROOT}/klines/{sym}/5m/{sym}-5m-{BURNED_DATE}.zip'
        kl_raw = fetch_file(f'{sym}_klines_5m', kl_url)
        if kl_raw:
            meta_kl = analyze_zip_csv(f'{sym}_klines_5m', kl_raw, default_cols=KL_COLS)
            print(f'[{sym} Klines 5m] rows={meta_kl["rows"]}, cols={len(meta_kl["columns"])}')
        
        # 2. 5m Metrics
        mt_url = f'{ROOT}/metrics/{sym}/{sym}-metrics-{BURNED_DATE}.zip'
        mt_raw = fetch_file(f'{sym}_metrics', mt_url)
        if mt_raw:
            meta_mt = analyze_zip_csv(f'{sym}_metrics', mt_raw)
            print(f'[{sym} Metrics 5m] rows={meta_mt["rows"]}, cols={len(meta_mt["columns"])}')
        time.sleep(1)

    OUT['probe_log.json'] = json.dumps(LOG, indent=2).encode()
    out_zip = 'ceiling_suite/p1_empirics/results/p7s_schema_probe_results.zip'
    os.makedirs(os.path.dirname(out_zip), exist_ok=True)
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as z:
        for k, v in OUT.items():
            z.writestr(k, v)
    with zipfile.ZipFile('pdf_delivered/p7s_schema_probe_results.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for k, v in OUT.items():
            z.writestr(k, v)

    print(f'\nSchema probe completed successfully. Saved {out_zip} and pdf_delivered/p7s_schema_probe_results.zip')
    for e in LOG:
        print(f" - {e.get('name')}: status {e.get('status')} ({e.get('bytes')} bytes, sha256 {e.get('sha256')[:12]}...)")

if __name__ == '__main__':
    main()
