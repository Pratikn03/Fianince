"""Verify only already inventoried archive payloads; never acquire new data."""
from pathlib import Path
import hashlib,json,re,time,zipfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
INVENTORY=ROOT/'research_extension/paper_revision_20261006/t9_recovered_inventory.json'

def run():
    inv=json.loads(INVENTORY.read_text()); results=[]; started=time.time()
    paths=sorted({f['path'] for f in inv['files'] if f['path'].endswith('.zip')})
    for i,name in enumerate(paths,1):
        p=Path(name); checksum=Path(name+'.CHECKSUM')
        row={'path':name,'checksum_file':str(checksum),'status':'PENDING','sample_replacement_allowed':False}
        try:
            row['bytes']=p.stat().st_size
            if not checksum.is_file():row['status']='MISSING_CHECKSUM';results.append(row);continue
            checksum_text=checksum.read_text().strip();token=checksum_text.split()[0]
            if not re.fullmatch('[0-9a-fA-F]{64}',token):raise ValueError('Invalid SHA256 checksum syntax')
            row['checksum_file_sha256']=hashlib.sha256(checksum.read_bytes()).hexdigest();row['declared_sha256']=token.lower()
            h=hashlib.sha256()
            with p.open('rb') as f:
                for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
            row['actual_sha256']=h.hexdigest()
            if row['actual_sha256']!=row['declared_sha256']:row['status']='CHECKSUM_MISMATCH'
            else:
                with zipfile.ZipFile(p) as z:
                    row['members']=[{'name':m.filename,'uncompressed_bytes':m.file_size,'crc32':m.CRC} for m in z.infolist()]
                    csvs=[m for m in z.infolist() if m.filename.endswith('.csv')]
                    row['first_csv_lines']=[]
                    if csvs:
                        with z.open(csvs[0]) as stream:
                            row['first_csv_lines']=[stream.readline().decode('utf-8',errors='replace').strip() for _ in range(3)]
                row['status']='PAYLOAD_SHA256_MATCH'
        except Exception as e:row['status']='READ_ERROR';row['error']=f'{type(e).__name__}: {e}'
        results.append(row)
        summary={'inventory_sha256':hashlib.sha256(INVENTORY.read_bytes()).hexdigest(),'archives_expected':len(paths),'archives_checked':len(results),'elapsed_seconds':time.time()-started,'results':results,'limits':['Supplied checksum files are local records; this does not independently authenticate the exchange provider','SHA256 verifies complete compressed bytes; full decompression/row-level CSV audit not performed','January 2025 observations do not replace the original 2021–2024 sample','No new acquisition, extraction, or experiments launched']}
        (HERE/'existing_archive_integrity.json').write_text(json.dumps(summary,indent=2)+'\n')
        if i%12==0 or i==len(paths):print(f"Archives {i}/{len(paths)}: {row['status']}; elapsed {time.time()-started:.1f}s",flush=True)
    statuses={}
    for r in results:statuses[r['status']]=statuses.get(r['status'],0)+1
    summary['status_counts']=statuses
    (HERE/'existing_archive_integrity.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(statuses),flush=True)
if __name__=='__main__':run()
