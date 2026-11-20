"""Build the consolidated SSRN author-review revision.

Current sources are in research_extension/paper1_publication_revision.
Use the repository Python environment; add --pdf to compile and deliver PDFs.
No empirical study or unlock counter is executed or changed.
"""
from pathlib import Path
import argparse
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REV=ROOT/'research_extension/paper1_publication_revision'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--pdf',action='store_true',help='Compile, check references, split, and copy the PDFs.')
args=parser.parse_args()
subprocess.run([sys.executable,str(HERE/'build_note.py')],cwd=HERE,check=True,stdout=subprocess.DEVNULL)
subprocess.run([sys.executable,str(REV/'make_base.py')],check=True)
subprocess.run([sys.executable,str(REV/'build_revision.py')],check=True)
SOURCE=REV/'source/ceiling_suite/papers/paper1_note'
shutil.copy2(SOURCE/'paper1_revised.tex',HERE/'paper1_ssrn.tex')
shutil.copy2(SOURCE/'fig_intervention_revision.pdf',HERE/'fig_intervention_revision.pdf')
print('Updated canonical paper1_ssrn.tex from the reconciled revision sources.')
if args.pdf:
    for stem,passes in [('paper1b_companion',2),('paper1_ssrn',3)]:
        for iteration in range(1,passes+1):
            log=REV/'validation'/f'canonical_{stem}_{iteration}.log'
            with log.open('w') as handle:
                subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex'],
                               cwd=HERE,stdout=handle,stderr=subprocess.STDOUT,check=True)
    log=(HERE/'paper1_ssrn.log').read_text()
    for marker in ['undefined','multiply defined','Overfull']:
        if marker in log:raise RuntimeError('LaTeX validation failed: '+marker)
    from pypdf import PdfReader,PdfWriter
    reader=PdfReader(HERE/'paper1_ssrn.pdf')
    texts=[p.extract_text() or '' for p in reader.pages]
    assert '??' not in ''.join(texts)
    split=next(i for i,t in enumerate(texts) if 'Online Supplement' in t)
    for name,a,b in [('Paper1_ssrn_main.pdf',0,split),('Paper1_ssrn_supplement.pdf',split,len(texts))]:
        writer=PdfWriter();writer.append(reader,pages=(a,b),import_outline=False);writer.write(HERE/name)
    outputs=[ROOT/'pdf_delivered',HERE.parent/'pdf_delivered',REV/'pdfs']
    for out in outputs:
        out.mkdir(parents=True,exist_ok=True)
        for name in ['Paper1_ssrn_main.pdf','Paper1_ssrn_supplement.pdf','paper1b_companion.pdf']:
            shutil.copy2(HERE/name,out/name)
        shutil.copy2(HERE/'paper1_ssrn.pdf',out/'Paper1_ssrn_complete.pdf')
    print(f'Delivered {len(texts)} pages: {split} main and {len(texts)-split} supplement.')
