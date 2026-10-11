"""Export frozen editable sources, leaving original root freezes untouched."""
from pathlib import Path
import subprocess,json,hashlib,shutil
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 originals=[ROOT/'Machine_Markets_JF_Submission.pdf',ROOT/'Machine_Markets_External_Review_Freeze.pdf']
 before={str(p.name):sha(p) for p in originals};build=BASE/'build';build.mkdir(exist_ok=True);logs=BASE/'logs';logs.mkdir(exist_ok=True);records=[]
 jobs=[('Machine_Markets_PublicationRevision_20261008',ROOT/'paper/Machine_Markets_JF_Submission.tex',ROOT/'paper','Machine_Markets_JF_Submission_PublicationRevision_20261008.pdf'),('Machine_Markets_Central_Result_Review_20261008',HERE/'Machine_Markets_Central_Result_Review_20261008.tex',HERE,'Machine_Markets_Central_Result_Review_20261008.pdf'),('Machine_Markets_Current_Evidence_Supplement_20261008',HERE/'Machine_Markets_Current_Evidence_Supplement_20261008.tex',HERE,'Machine_Markets_Current_Evidence_Supplement_20261008.pdf')]
 for job,source,cwd,delivery in jobs:
  source_before=sha(source)
  for iteration in range(1,4):
   result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-recorder',f'-jobname={job}',f'-output-directory={build}',str(source)],cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   (logs/f'{job}_final_pass{iteration}.txt').write_bytes(result.stdout)
   if result.returncode:raise RuntimeError(result.stdout.decode()[-4000:])
  text=result.stdout.decode();assert 'undefined' not in text.lower() and 'Overfull' not in text
  assert source_before==sha(source)
  pdf=build/f'{job}.pdf';target=ROOT/delivery;shutil.copy2(pdf,target)
  info=subprocess.run(['pdfinfo',str(target)],capture_output=True,text=True,check=True).stdout
  pages=int(next(l.split(':',1)[1] for l in info.splitlines() if l.startswith('Pages:')))
  records.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),pdf=str(target.relative_to(ROOT)),pdf_sha256=sha(target),pages=pages,compiler_record=str((build/f'{job}.fls').relative_to(ROOT)),final_log=str((logs/f'{job}_final_pass3.txt').relative_to(ROOT))))
  print(delivery,pages,'pages',flush=True)
 assert before=={p.name:sha(p) for p in originals}
 (HERE/'pdf_export_receipt.json').write_text(json.dumps(dict(status='CURRENT_SOURCE_EXPORT_COMPILED_ORIGINAL_FREEZES_PRESERVED',outputs=records,original_freeze_hashes=before,limitations=['Export and compilation do not establish scientific closure or journal readiness.']),indent=2)+'\n')
if __name__=='__main__':run()
