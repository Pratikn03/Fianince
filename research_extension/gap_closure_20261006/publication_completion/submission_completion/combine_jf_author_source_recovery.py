"""Combine the current formatted manuscript, IA cover and evidence PDF.

Requires pypdf6.10. Main link destinations and every page's text are checked;
duplicate appendix destination warnings are logged rather than ignored silently.
"""
from pathlib import Path
import json,hashlib,subprocess,logging
from pypdf import PdfReader,PdfWriter
HERE=Path(__file__).resolve().parent;H=HERE.parent;ROOT=HERE.parents[3];BASE=H.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 cover_source=HERE/'JF_Internet_Appendix_Cover_20261008.tex'
 r=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={BASE / "build"}',str(cover_source)],cwd=HERE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(BASE/'logs/jf_ia_cover_compile_20261008.txt').write_bytes(r.stdout);assert r.returncode==0
 main=BASE/'build/Machine_Markets_JF_Format_Candidate_20261008.pdf';cover=BASE/'build/JF_Internet_Appendix_Cover_20261008.pdf';evidence=ROOT/'Machine_Markets_Current_Evidence_AuthorSourceRecovery_20261008.pdf'
 logging.basicConfig(filename=str(BASE/'logs/jf_merge_diagnostics_20261008.txt'),level=logging.WARNING,force=True)
 w=PdfWriter();w.append(str(main),outline_item='Main manuscript and author disclosure drafts');w.append(str(cover),outline_item='Internet Appendix');w.append(str(evidence),outline_item='Current numerical evidence')
 output=ROOT/'Machine_Markets_JF_PreSubmission_AuthorSourceRecovery_20261008.pdf'
 with output.open('wb') as f:w.write(f)
 a,b,c=map(PdfReader,[main,cover,evidence]);combined=PdfReader(output);pages=[*a.pages,*b.pages,*c.pages]
 assert len(combined.pages)==len(pages)
 for old,new in zip(pages,combined.pages):assert old.extract_text()==new.extract_text()
 links=0
 for page in a.pages:
  for ref in page.get('/Annots',[]):
   act=ref.get_object().get('/A',{})
   if act.get('/S')=='/GoTo':
    name=act['/D'];assert a.get_destination_page_number(a.named_destinations[name])==combined.get_destination_page_number(combined.named_destinations[name]);links+=1
 d=json.loads((HERE/'jf_format_receipt.json').read_text());assert d['baseline_source_sha256']==sha(ROOT/'paper/Machine_Markets_JF_Submission.tex')
 d.update(combined_pdf=str(output),combined_sha256=sha(output),internet_appendix_pages=len(b.pages)+len(c.pages),combined_physical_pages=len(combined.pages),main_pdf_sha256=sha(main),appendix_evidence_sha256=sha(evidence),all_page_text_preserved=True,main_internal_link_destinations_preserved=links,pypdf_version='6.10.0')
 (HERE/'jf_combined_format_receipt.json').write_text(json.dumps(d,indent=2)+'\n');print('Combined current JF draft:',d['combined_physical_pages'],'physical pages;',d['counted_manuscript_pages'],'counted manuscript pages;',links,'internal links verified')
if __name__=='__main__':run()
