"""Inventory related research workspaces and archives; search claims without modifying sources."""
from pathlib import Path
import os,re,json,hashlib,tarfile,zipfile
REV=Path(__file__).resolve().parent
HOME=Path('/Users/pratik_n')
roots=sorted(p for p in (HOME/'Downloads').glob('Machine_Markets_*') if p.is_dir())
roots += [Path('/Volumes/T9/machine_markets_data'),Path('/Volumes/T9/machine_markets_datasets'),HOME/'.gemini/antigravity/brain/fca7b050-1d79-4849-8dc1-2c344e17fc9f', HOME/'.gemini/antigravity/brain/d31d9234-c763-40d6-a292-79ab009a89fa', HOME/'.gemini/antigravity-backup/brain', HOME/'.gemini/antigravity-ide/brain']
patterns={'joint_venue':r'FEVD|0\.9612|21\.6\s*[%\\]|78\.4|S_.?cross|joint.?VAR|cross.?venue.*VAR',
 'eventstudy':r'0\.835|F.?=.?0\.42|pre.?trend|event.?study',
 'stress':r'62\.7|1450\.2|10.\{?-300|markov.?switch',
 'raw_binance':r'binance_1s|vision.*1s|read_parquet|klines/1s',
 'equity':r'FI.?2010|54.?588|18308|39555',
 'learner':r'support_pass|structural_pass|turnover.match|reward.sweep'}
compiled={k:re.compile(v,re.I) for k,v in patterns.items()}
inv=[];hits=[];errors=[];seen=set(); suffixes={'.py','.json','.csv','.md','.tex','.txt','.log','.yml','.yaml'}
def inspect(name,b,kind):
 h=hashlib.sha256(b).hexdigest(); inv.append({'path':name,'bytes':len(b),'sha256':h,'kind':kind})
 s=b.decode('utf8',errors='replace')
 for k,pat in compiled.items():
  m=list(pat.finditer(s))
  if m:
   snippets=[s[max(0,x.start()-100):min(len(s),x.end()+180)].replace('\n',' ') for x in m[:5]]
   hits.append({'path':name,'sha256':h,'claim':k,'match_count':len(m),'snippets':snippets})
for root in roots:
 if not root.exists():continue
 for base,dirs,files in os.walk(root):
  dirs[:]=[d for d in dirs if d not in {'.git','.venv','node_modules','__pycache__','qa'}]
  for f in files:
   p=Path(base)/f
   if p.suffix.lower() not in suffixes or p.stat().st_size>2_000_000 or REV in p.parents:continue
   try:inspect(str(p),p.read_bytes(),'file')
   except OSError as e:errors.append({'path':str(p),'error':str(e)})
archives=sorted((HOME/'Downloads').glob('Machine_Markets_*.tar.gz'))+sorted(Path('/Volumes/T9/machine_markets_releases').glob('*.tar.gz'))+[HOME/'Documents/Zoom/Machine_Markets_Master_Release.zip']
for archive in archives:
 if not archive.exists():continue
 try:
  if archive.suffix=='.zip':
   with zipfile.ZipFile(archive) as z:
    for m in z.infolist():
     if Path(m.filename).suffix.lower() in suffixes and m.file_size<=2_000_000:inspect(str(archive)+'::'+m.filename,z.read(m),'archive_member')
  else:
   with tarfile.open(archive,'r|gz') as t:
    for m in t:
     if m.isfile() and Path(m.name).suffix.lower() in suffixes and m.size<=2_000_000:
      inspect(str(archive)+'::'+m.name,t.extractfile(m).read(),'archive_member')
 except Exception as e:errors.append({'path':str(archive),'error':str(e)})
report={'scope':[str(p) for p in roots],'archives':[str(p) for p in archives],'excluded':'virtual environments, git objects, extensions, credentials, files above 2 MB for text search; raw data located separately','inventory':inv,'hits':hits,'errors':errors}
(REV/'existing_evidence_search.json').write_text(json.dumps(report,indent=2))
print('Files/member texts:',len(inv),'unique content hashes:',len({r['sha256'] for r in inv}),'hits:',len(hits),'errors:',errors,flush=True)
for k in patterns:
 group=[r for r in hits if r['claim']==k]; uniq={r['sha256'] for r in group}
 print(k,'matching files',len(group),'unique content',len(uniq),flush=True)
