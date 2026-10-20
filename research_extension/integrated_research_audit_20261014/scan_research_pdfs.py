"""Read every page of the explicitly inventoried research PDFs; deduplicate by SHA256.
This is a text/metadata audit, not an assertion of mathematical or visual verification.
"""
from pathlib import Path
import hashlib,json,re,subprocess,datetime
from pypdf import PdfReader
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
G=Path('/Volumes/T9/gridpulse')
paths=[]
for r in [ROOT,ROOT/'paper']:
 paths.extend(r.glob('*.pdf'))
paths.extend(G/p for p in ['orius_book.pdf','paper.pdf','paper/paper.pdf','paper/orius_book.pdf','paper/orius_foundations/main.pdf','paper/orius_monograph_complete.pdf','paper/ieee/orius_ieee_main.pdf','paper/ieee/orius_ieee_detailed_main.pdf','paper/review/orius_review_dossier.pdf','appendices/app_c_all_theorems.pdf','orius_battery_409page_figures_upgraded_main.pdf'])
for name in ['KBound_Publication_20260923','KBound_Theory_Assumption_Completion_20260923']:
 paths.extend((Path('/Users/pratik_n/Documents')/name).glob('*.pdf'))
paths.extend(Path('/Users/pratik_n/Downloads').glob('*[Kk]*[Bb]ound*.pdf'))
for name in ['ORIUS_Current_Manuscript_362p.pdf','orius_battery_413page_unified_manuscript.pdf','orius_book.pdf']:
 paths.append(Path('/Users/pratik_n/Downloads')/name)
paths=sorted(set(p for p in paths if p.is_file() and not p.name.startswith('.')))
(OUT/'pdf_text').mkdir(exist_ok=True)
results=[]; cache={}; matches={}
terms=re.compile(r'10[.]0?\s*/\s*10|best.paper|immunity|martingale|hardware|physical bench|50 micro|73[.]65|Theorem H|complete formal|320|FULL|safe.stop|epistemic|64[.]74|Prony|Wald|Parseval',re.I)
for p in paths:
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 row={'path':str(p),'sha256':sha,'bytes':p.stat().st_size}
 if sha in cache:
  row.update(duplicate_of=cache[sha]['path'],pages=cache[sha]['pages']); results.append(row);continue
 try:
  reader=PdfReader(p);pages=[];texts=[]; excerpts=[]
  for n,page in enumerate(reader.pages,1):
   txt=page.extract_text() or '';texts.append(f'\n=== PHYSICAL PAGE {n} ===\n{txt}')
   flags=[]
   if re.search(r'\?\?|\[\?\]',txt):flags.append('unresolved_reference_token')
   if re.search(r'\b(TODO|FIXME|TBD|PLACEHOLDER)\b',txt,re.I):flags.append('unfinished_marker_requires_context')
   if 'J. Doe' in txt or 'R. Smith' in txt: flags.append('placeholder_author')
   pages.append({'page':n,'characters':len(txt),'flags':flags})
   if terms.search(txt): excerpts.append({'page':n,'lines':[line for line in txt.splitlines() if terms.search(line)][:18]})
  target=OUT/'pdf_text'/f'{sha[:12]}_{p.stem}.txt';target.write_text('\n'.join(texts))
  row.update(pages=len(pages),page_checks=pages,text_file=str(target),claim_excerpts=excerpts)
 except Exception as e:row['error']=repr(e)
 cache[sha]=row;results.append(row)
(OUT/'pdf_inventory.json').write_text(json.dumps({'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Explicit canonical and historical PDF list; all pages text-extracted; duplicates SHA-deduplicated; visual QA separately recorded','pdfs':results},indent=2))
print('PDF paths:',len(results),'unique hashes:',len(cache),'unique physical pages:',sum(r.get('pages',0) for r in cache.values()))
for r in results:
 bad=[q['page'] for q in r.get('page_checks',[]) if q['flags']]
 print(r.get('pages'),str(Path(r['path']).relative_to(ROOT)) if Path(r['path']).is_relative_to(ROOT) else r['path'],'duplicate' if 'duplicate_of' in r else '', 'flag_pages='+str(bad))
