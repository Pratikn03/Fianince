"""Authenticate the user's existing three files against their named primary release.

This acquires no new study/sample: version1 exact files are streamed as provider
compressed copies on T9 solely to compare full uncompressed SHA256/CRC.
"""
from pathlib import Path
import urllib.request,hashlib,json,zipfile,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
TARGET=Path('/Volumes/T9/machine_markets_data/primary_recorder_authentication_20261008')

def digest(stream):
    h=hashlib.sha256();n=0
    for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block);n+=len(block)
    return h.hexdigest(),n

def run():
    metadata=json.loads((HERE/'recorder_primary_metadata.json').read_text())
    files=json.loads((HERE/'recorder_file_metadata.json').read_text())['datasetFiles']
    assert metadata['currentVersionNumber']==1
    TARGET.mkdir(parents=True,exist_ok=True)
    records=[]
    for asset in ['BTC','ETH','ADA']:
        name=asset+'_1sec.csv';url='https://www.kaggle.com/api/v1/datasets/download/martinsn/high-frequency-crypto-limit-order-book-data/'+name+'?datasetVersionNumber=1'
        archive=TARGET/(name+'.zip');start=time.time()
        if not archive.exists():
            partial=archive.with_suffix('.part')
            with urllib.request.urlopen(url,timeout=60) as r,partial.open('wb') as dest:
                if 'zip' not in (r.headers.get('Content-Type') or ''):raise ValueError('Unexpected non-ZIP provider response')
                while block:=r.read(4*1024*1024):dest.write(block)
            partial.rename(archive)
        with zipfile.ZipFile(archive) as z:
            assert len(z.namelist())==1 and Path(z.namelist()[0]).name==name
            member=z.infolist()[0]
            with z.open(member) as f:provider_sha,n=digest(f)
        local=ROOT/'empirical_pipeline/data'/name
        with local.open('rb') as f:local_sha,local_n=digest(f)
        expected=next(f['totalBytes'] for f in files if f['name']==name)
        assert n==local_n==expected and provider_sha==local_sha
        with archive.open('rb') as f:archive_sha,_=digest(f)
        records.append(dict(asset=asset,primary_url=url,dataset_id=metadata['id'],version=1,
                       provider=metadata['ownerRef'],license=metadata['licenseName'],local_path=str(local),
                       local_sha256=local_sha,provider_uncompressed_sha256=provider_sha,bytes=n,
                       provider_archive=str(archive),archive_sha256=archive_sha,zip_crc=member.CRC,
                       status='EXACT_PRIMARY_RELEASE_BYTES_MATCH'))
        (HERE/'recorder_authentication.json').write_text(json.dumps(dict(scope='Exact current provider version1 bytes and declared uploader licence; not an independent audit of collection correctness or exchange rights',rows=records),indent=2)+'\n')
        print(asset,'exact primary release bytes match;',round(time.time()-start,1),'seconds',flush=True)
    print('All three recorder files authenticated against named release',flush=True)

if __name__=='__main__':run()
