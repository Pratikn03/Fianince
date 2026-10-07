"""Restore exactly the already claimed 768-row panel, not an expanded dataset."""
from pathlib import Path
import concurrent.futures,hashlib,json,shutil,time,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE))
from restore_original_overlap import restore,STORE

def run():
    if not Path('/Volumes/T9').is_mount() or shutil.disk_usage('/Volumes/T9').free<20*1024**3:raise RuntimeError('Original-panel recovery needs mounted T9 and 20GB free')
    saved=json.loads((ROOT/'results/provenance/binance_panel_results.json').read_text())
    keys=sorted({(r['symbol'],r['date']) for r in saved['results']})
    if len(keys)!=768:raise ValueError('Saved panel does not have 768 distinct original study units')
    manifest=HERE/'original_panel_restoration_manifest.json';prior={}
    if manifest.is_file():
        old=json.loads(manifest.read_text());prior={(r['symbol'],r['date']):r for r in old['rows'] if r['status']=='VERIFIED_ORIGINAL_SAMPLE_RESTORED'}
    results=[];pending=[];started=time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for key in keys:
            old=prior.get(key)
            if old and Path(old['path']).is_file():
                h=hashlib.sha256(Path(old['path']).read_bytes()).hexdigest()
                if h==old['sha256']:results.append(old);continue
            pending.append(pool.submit(restore,key))
        for task in concurrent.futures.as_completed(pending):
            r=task.result();results.append(r)
            report={'scope':'Exact original saved-panel symbols/dates only; current exchange archives restore missing inputs, original download-time hashes were not preserved','saved_panel_sha256':hashlib.sha256((ROOT/'results/provenance/binance_panel_results.json').read_bytes()).hexdigest(),'n_target':768,'n_processed':len(results),'store':str(STORE),'rows':sorted(results,key=lambda r:(r['symbol'],r['date']))}
            manifest.write_text(json.dumps(report,indent=2)+'\n')
            if len(results)%12==0 or r['status']=='FAILED':print(f"Original panel {len(results)}/768: {r['symbol']} {r['date']} {r['status']}; elapsed {time.time()-started:.0f}s",flush=True)
    failed=[r for r in results if r['status']=='FAILED'];print('Finished',len(results),'failures',len(failed),'bytes',sum(r.get('bytes',0) for r in results),flush=True)
    if failed:raise SystemExit('Some original objects require retry; manifest retained')
if __name__=='__main__':run()
