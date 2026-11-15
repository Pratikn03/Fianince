from pathlib import Path
import shutil
import subprocess
import json
import argparse
from pypdf import PdfReader,PdfWriter

HERE=Path(__file__).resolve().parent
NOTE=HERE/'source/ceiling_suite/papers/paper1_note'
parser=argparse.ArgumentParser(description='Split and inspect the revised manuscript PDF.')
parser.add_argument('--output-dir',type=Path,default=HERE/'pdfs')
OUT=parser.parse_args().output_dir.resolve()
OUT.mkdir(parents=True,exist_ok=True)
source=NOTE/'paper1_revised.pdf'
reader=PdfReader(source)
texts=[p.extract_text() or '' for p in reader.pages]
split=next(i for i,t in enumerate(texts) if 'Online Supplement' in t)
for name,a,b in [('Paper1_ssrn_main.pdf',0,split),('Paper1_ssrn_supplement.pdf',split,len(texts))]:
    writer=PdfWriter()
    writer.append(reader,pages=(a,b),import_outline=False)
    writer.write(OUT/name)
shutil.copy2(source,OUT/'Paper1_ssrn_complete.pdf')
shutil.copy2(NOTE/'paper1b_companion.pdf',OUT/'paper1b_companion.pdf')
checks=['Revised research draft','A lower bound for smooth','Fitted-forecast gains',
        'Expected loss from','Intervention choice and','Smooth-family lower bounds','Intervention loss: proof',
        'Machine-checked declarations']
pages={}
for term in checks:
    found=[i+1 for i,t in enumerate(texts) if term in t]
    if found:pages[term]=found[0]
assert '??' not in ''.join(texts)
log=(NOTE/'paper1_revised.log').read_text()
assert 'undefined' not in log and 'multiply defined' not in log and 'Overfull' not in log
qa=HERE/'validation/rendered';qa.mkdir(exist_ok=True)
for page in sorted(set([1,split+1,*pages.values()])):
    subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','1200','-png','-singlefile',str(source),str(qa/f'paper_page_{page:03d}')],check=True,capture_output=True)
meta={'combined_pages':len(texts),'main_pages':split,'supplement_pages':len(texts)-split,'selected_pages':pages,
      'latex_undefined_references':False,'latex_overfull_boxes':False}
(HERE/'validation/pdf_checks.json').write_text(json.dumps(meta,indent=2)+'\n')
(HERE/'validation/revised_paper_text.txt').write_text('\n\f\n'.join(texts))
print(json.dumps(meta,indent=2))
