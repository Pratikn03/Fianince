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
# The full working paper keeps every result; the journal version (paper1_ssrn) is cut from it by
# t6/round8_journal.py, which cites the full working paper, with numbers from its .aux, for every result it removes.
full=(SOURCE/'paper1_revised.tex').read_text()
full=full.replace(r'\date{Working paper,',r'\date{Full working paper with all supplementary results,',1)
(HERE/'paper1_full.tex').write_text(full)
shutil.copy2(SOURCE/'fig_intervention_revision.pdf',HERE/'fig_intervention_revision.pdf')
sys.path.insert(0,str(REV/'t6'))
import json
import round8_journal


def pdflatex(stem,passes,validate=True):
    for iteration in range(1,passes+1):
        log=REV/'validation'/f'canonical_{stem}_{iteration}.log'
        with log.open('w') as handle:
            subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex'],
                           cwd=HERE,stdout=handle,stderr=subprocess.STDOUT,check=True)
    if not validate:
        return
    log=(HERE/(stem+'.log')).read_text()
    for marker in ['undefined','multiply defined','Overfull']:
        if marker in log:raise RuntimeError(f'LaTeX validation failed ({stem}): '+marker)


def journal_cut():
    tex,report=round8_journal.apply((HERE/'paper1_full.tex').read_text(),(HERE/'paper1_full.aux').read_text())
    tex=tex.replace(r'\date{Full working paper with all supplementary results,',r'\date{Working paper,',1)
    (HERE/'paper1_ssrn.tex').write_text(tex)
    (REV/'validation'/'journal_cut_report.json').write_text(json.dumps(report,indent=1))
    print(f"Journal version: {len(report['removed_labels'])} labelled items moved to the full working paper, "
          f"{len(report['citations_added'])} references now cite it, {report['rows_dropped']} coverage rows dropped.")


if not args.pdf:
    if (HERE/'paper1_full.aux').exists():
        journal_cut()
    else:
        shutil.copy2(HERE/'paper1_full.tex',HERE/'paper1_ssrn.tex')
    print('Updated canonical paper1_ssrn.tex from the reconciled revision sources.')
if args.pdf:
    pdflatex('paper1b_companion',2,validate=False)  # as before: the companion is not gated here
    pdflatex('paper1_full',3)
    journal_cut()
    pdflatex('paper1_ssrn',3)
    import jedc_front
    (HERE/'paper1_jedc.tex').write_text(jedc_front.apply((HERE/'paper1_ssrn.tex').read_text()))
    pdflatex('paper1_jedc',3)
    from pypdf import PdfReader,PdfWriter
    pages={}
    for stem in ['paper1_full','paper1_ssrn']:
        reader=PdfReader(HERE/(stem+'.pdf'))
        texts=[p.extract_text() or '' for p in reader.pages]
        assert '??' not in ''.join(texts), stem
        pages[stem]=(reader,texts,next(i for i,t in enumerate(texts) if 'Online Supplement' in t))
    reader,texts,split=pages['paper1_ssrn']
    for name,a,b in [('Paper1_ssrn_main.pdf',0,split),('Paper1_ssrn_supplement.pdf',split,len(texts))]:
        writer=PdfWriter();writer.append(reader,pages=(a,b),import_outline=False);writer.write(HERE/name)
    outputs=[ROOT/'pdf_delivered',HERE.parent/'pdf_delivered',REV/'pdfs']
    for out in outputs:
        out.mkdir(parents=True,exist_ok=True)
        for name in ['Paper1_ssrn_main.pdf','Paper1_ssrn_supplement.pdf','paper1b_companion.pdf']:
            shutil.copy2(HERE/name,out/name)
        shutil.copy2(HERE/'paper1_ssrn.pdf',out/'Paper1_ssrn_complete.pdf')
        shutil.copy2(HERE/'paper1_full.pdf',out/'Paper1_full_working_paper.pdf')
        shutil.copy2(HERE/'paper1_jedc.pdf',out/'Paper1_JEDC_submission.pdf')
    ftexts=pages['paper1_full'][1]
    print(f'Delivered journal version {len(texts)} pages: {split} main and {len(texts)-split} supplement; '
          f'full working paper {len(ftexts)} pages.')
