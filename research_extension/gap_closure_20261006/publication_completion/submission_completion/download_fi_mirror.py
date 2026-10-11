"""Recover only ten existing-sample DecPre files from an independent mirror.

Mirror bytes do not authenticate the unavailable primary archive's checksum or
override its CC BY4.0 terms. This is a representation diagnostic, not a new study.
"""
from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,zipfile,shutil
HERE=Path(__file__).resolve().parent
TARGET=Path('/Volumes/T9/machine_markets_data/fi_equity_mirror_20261008')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def run():
 TARGET.mkdir(exist_ok=True);files=json.loads((HERE/'fi_mirror_file_inventory.json').read_text())['files']
 selected=[r for r in files if '3.NoAuction_DecPre/' in r['name'] and ('_Testing/' in r['name'] or r['name'].endswith('Training/Train_Dst_NoAuction_DecPre_CF_1.txt'))]
 assert len(selected)==10;records=[]
 for r in selected:
  name=r['name'];target=TARGET/Path(name).name;archive=TARGET/(target.name+'.zip')
  url='https://www.kaggle.com/api/v1/datasets/download/ulfricirons/fi-2010/'+urllib.parse.quote(name,safe='')+'?datasetVersionNumber=1'
  if not archive.exists():
   partial=archive.with_suffix('.part')
   with urllib.request.urlopen(url,timeout=60) as response,partial.open('wb') as out:
    while block:=response.read(1024*1024):out.write(block)
   partial.replace(archive)
  if not target.exists():
   with zipfile.ZipFile(archive) as z:
    z.testzip();entries=[i for i in z.infolist() if Path(i.filename).name==target.name];assert len(entries)==1
    with z.open(entries[0]) as src,target.open('wb') as dst:shutil.copyfileobj(src,dst,4*1024*1024)
  assert target.stat().st_size==r['totalBytes']
  records.append(dict(mirror='ulfricirons/fi-2010',version=1,remote_filename=name,path=str(target),bytes=target.stat().st_size,sha256=sha(target),archive_sha256=sha(archive),public_download_url=url))
  (HERE/'fi_mirror_acquisition.json').write_text(json.dumps(dict(status='INDEPENDENT_MIRROR_BYTES_FOR_REPRESENTATION_DIAGNOSIS_PRIMARY_CHECKSUM_NOT_AUTHENTICATED',files=records,primary_licence='CC BY4.0; mirror metadata license Unknown, not a replacement'),indent=2)+'\n')
  print(target.name,'received',target.stat().st_size,'bytes',flush=True)
if __name__=='__main__':run()
