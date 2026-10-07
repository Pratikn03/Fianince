"""Restore only named original April overlap; bounded downloads and checksums."""
from pathlib import Path
import concurrent.futures,hashlib,json,shutil,urllib.request,zipfile,time
HERE=Path(__file__).resolve().parent
STORE=Path('/Volumes/T9/machine_markets_data/recovered_original_overlap_20261006')
ASSETS=['BTCUSDT','ETHUSDT','ADAUSDT']
DATES=[f'2021-04-{d:02}' for d in range(8,19)]
MAX_ARCHIVE_BYTES=8*1024*1024

def get(url,maximum):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MachineMarkets-evidence-recovery'}),timeout=45) as r:
        data=r.read(maximum+1)
        if len(data)>maximum:raise ValueError('Object exceeds declared bounded recovery limit')
        return data,dict(r.headers)

def restore(pair):
    asset,date=pair;name=f'{asset}-1s-{date}.zip';url=f'https://data.binance.vision/data/spot/daily/klines/{asset}/1s/{name}'
    row={'symbol':asset,'date':date,'url':url,'checksum_url':url+'.CHECKSUM','path':str(STORE/name),'status':'PENDING'}
    try:
        cs,ch=get(url+'.CHECKSUM',8192);expected=cs.decode().split()[0].lower()
        if len(expected)!=64:raise ValueError('Invalid SHA256 record')
        target=STORE/name
        if target.exists():payload=target.read_bytes();headers={}
        else:payload,headers=get(url,MAX_ARCHIVE_BYTES)
        actual=hashlib.sha256(payload).hexdigest()
        if actual!=expected:raise ValueError('Archive checksum mismatch')
        temporary=target.with_suffix('.zip.partial');temporary.write_bytes(payload);temporary.replace(target)
        Path(str(target)+'.CHECKSUM').write_bytes(cs)
        with zipfile.ZipFile(target) as z:
            members=z.infolist()
            if len(members)!=1 or not members[0].filename.endswith('.csv'):raise ValueError('Unexpected archive members')
            if members[0].file_size>40*1024*1024:raise ValueError('Unexpected uncompressed size')
            bad=z.testzip()
            if bad:raise ValueError('CRC failure '+bad)
            with z.open(members[0]) as f: first=f.readline().decode().strip()
        row.update(status='VERIFIED_ORIGINAL_SAMPLE_RESTORED',sha256=actual,checksum_sha256=hashlib.sha256(cs).hexdigest(),bytes=len(payload),uncompressed_bytes=members[0].file_size,first_record=first,http_headers=headers)
    except Exception as e:row.update(status='FAILED',error=f'{type(e).__name__}: {e}')
    return row

def run():
    if not Path('/Volumes/T9').is_mount():raise RuntimeError('T9 is not mounted')
    if shutil.disk_usage('/Volumes/T9').free<2*1024**3:raise RuntimeError('Insufficient free storage')
    STORE.mkdir(parents=True,exist_ok=True);rows=[];start=time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        pending=[pool.submit(restore,(a,d)) for a in ASSETS for d in DATES]
        for task in concurrent.futures.as_completed(pending):
            row=task.result();rows.append(row)
            report={'scope':'restoration of exact original cross-venue study inputs; no new sample dates or assets','timestamp_note':'2021 spot kline timestamps are milliseconds; 2025 spot uses microseconds and is not substituted','n_target':33,'max_archive_bytes':MAX_ARCHIVE_BYTES,'rows':sorted(rows,key=lambda r:(r['symbol'],r['date']))}
            (HERE/'restoration_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
            print(f"{len(rows)}/33 {row['symbol']} {row['date']}: {row['status']}",flush=True)
    print('Elapsed',round(time.time()-start,1),'seconds; bytes',sum(r.get('bytes',0) for r in rows),flush=True)
    if any(r['status']=='FAILED' for r in rows):raise SystemExit('Recovery incomplete; inspect manifest')
if __name__=='__main__':run()
