"""Authenticate existing FI-2010 representation against its original release.

The original benchmark is acquired only to reconstruct the user's existing
representation and diagnose its stock-splitting/decimal transformation.
No additional empirical study is introduced.
"""
from pathlib import Path
import urllib.request,json,hashlib,zipfile,sys,shutil
HERE=Path(__file__).resolve().parent
TARGET=Path('/Volumes/T9/machine_markets_data/primary_equity_authentication_20261008')
DATASET='73eb48d7-4dbc-4a10-a52a-da745b47a649'
def run():
    meta=json.loads((HERE/'fi_primary_files.json').read_text())['results'][0]
    TARGET.mkdir(parents=True,exist_ok=True);path=TARGET/meta['filename']
    if not path.exists():
        if len(sys.argv)>1:download_url=sys.argv[1]
        else:
            payload=json.dumps(dict(cr_id=DATASET,file=meta['pathname'])).encode()
            req=urllib.request.Request('https://etsin.fairdata.fi/api/download/authorize',data=payload,headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=30) as r:authorization=json.loads(r.read())
            download_url=authorization['url']
        # Ephemeral open-download credentials are kept in memory and never logged.
        partial=path.with_suffix('.part');n=0;last=0
        with urllib.request.urlopen(download_url,timeout=60) as r,partial.open('wb') as f:
            contenttype=r.headers.get('Content-Type','')
            if 'zip' not in contenttype and 'octet-stream' not in contenttype:raise ValueError('Unexpected file content type')
            while block:=r.read1(64*1024):
                f.write(block);n+=len(block)
                if n-last>250_000_000:print('Original equity archive',n,'bytes received',flush=True);last=n
        if n==meta['size']:partial.rename(path)
        else:
            with zipfile.ZipFile(partial) as z:
                members=[i for i in z.infolist() if Path(i.filename).name==meta['filename']]
                if len(members)!=1 or members[0].file_size!=meta['size']:raise ValueError('Primary archive missing from provider package')
                with z.open(members[0]) as src,path.open('wb') as dest:shutil.copyfileobj(src,dest,4*1024*1024)
    h=hashlib.sha256()
    with path.open('rb') as f:
        while b:=f.read(4*1024*1024):h.update(b)
    assert 'sha256:'+h.hexdigest()==meta['checksum']
    with zipfile.ZipFile(path) as z:names=z.namelist()
    report=dict(status='PRIMARY_ARCHIVE_SHA256_MATCH_REPRESENTATION_RECONSTRUCTION_PENDING',
                path=str(path),dataset_id=DATASET,sha256=h.hexdigest(),bytes=path.stat().st_size,
                licence='CC BY 4.0 per primary Fairdata record',member_names=names,
                scope='Original normalized benchmark bytes; does not yet authenticate local CSV transformations or stock identity mapping')
    (HERE/'equity_archive_authentication.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original equity release checksum authenticated;',len(names),'archive members',flush=True)
if __name__=='__main__':run()
