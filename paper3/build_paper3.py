"""Generate the stand-alone draft from the authoritative thesis Paper 3 text.

Build canonical companion papers in a disposable folder to resolve their actual
reference numbers; never edit or rebuild the working co-authored sources in place.
"""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    source_path = ROOT/'thesis/ch4_paper3.tex'
    source = source_path.read_text()
    source_hash = sha(source_path)
    refs = {}
    with tempfile.TemporaryDirectory(prefix='paper3-companion-refs-') as tmp:
        tmp = Path(tmp)
        for number in [1,2]:
            name = f'paper{number}'
            shutil.copytree(ROOT/'ceiling_suite/papers'/name,tmp/name)
            build = f'build_p{number}.sh'
            shutil.copy2(ROOT/'ceiling_suite/papers'/build,tmp/build)
            subprocess.run(['sh',str(tmp/build)],cwd=tmp,check=True,capture_output=True,text=True)
            aux = (tmp/name/(name+'.aux')).read_text()
            refs.update({f'p{number}:'+label:{'number':value,'paper':number}
                         for label,value in re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}',aux)})
    body = source[source.index('\\section{Markets with adaptive agents}'):]
    body = body.replace('Chapters~\\ref{ch:p1}--\\ref{ch:p2}', 'Papers~1--2')
    for number in [1,2]:
        body = body.replace(f'Chapter~\\ref{{ch:p{number}}}',f'Paper~{number}')
        body = body.replace(f'\\ref{{ch:p{number}}}',str(number))
    body = body.replace('\\ProvedIn{CH.~2}', '\\ProvedIn{PAPER 1}').replace('\\ProvedIn{CH.~3}', '\\ProvedIn{PAPER 2}')
    used = {}
    def external(m):
        command,key = m.groups()
        if not key.startswith(('p1:','p2:')): return m[0]
        if key not in refs: raise ValueError('Unresolved companion reference: '+key)
        used[key]=refs[key]
        number,paper = refs[key]['number'],refs[key]['paper']
        value = f'{number} in Paper~{paper}'
        return '\\textup{'+('('+value+')' if command=='eqref' else value)+'}'
    body = re.sub(r'\\(ref|eqref)\{([^}]+)\}',external,body)
    # Proof text remains generated from the same source; the main text gets a pointer.
    proofs=[]
    def move_proof(m):
        labels = re.findall(r'\\label\{([^}]+)\}',body[:m.start()])
        label = labels[-1] if labels else 'thm:dich'
        index = len(proofs)+1
        proofs.append('\\subsection{Proof for result~\\ref{'+label+'}}\\label{app:paper3proof'+str(index)+'}\n'+m[0])
        return '\\paragraph{Proof.} See Appendix~\\ref{app:paper3proof'+str(index)+'}.\n'
    body = re.sub(r'\\begin\{proof\}(?:\[[^\]]*\])?.*?\\end\{proof\}',move_proof,body,flags=re.S)
    body = body.replace('\\input{checks/multiasset_numbers}','\\input{../thesis/checks/multiasset_numbers}')
    if re.search(r'\\(?:ref|eqref)\{(?:p1:|p2:|ch:)',body):
        raise ValueError('Unresolved cross-document reference')
    template_hash = sha(ROOT/'thesis/thesis.tex')
    preamble = (ROOT/'thesis/thesis.tex').read_text().split('\\begin{document}')[0]
    preamble = preamble.replace('\\documentclass[11pt,oneside]{report}','\\documentclass[11pt]{article}')
    preamble = preamble.replace('PROVED IN THIS THESIS','PROVED IN SOURCE')
    bib = (ROOT/'thesis/bib_new.tex').read_text()
    companions = r'''
\bibitem[Niroula and Niroula(2026)]{p3:paper1} Niroula, P. and Niroula, P. (2026). \emph{Auditable Memory and Financial Identification Limits in Electronic Limit Order Books}. Companion working paper.
\bibitem[Niroula et~al.(2026)]{p3:paper2} Niroula, P., Alkhushayni, S., Chen, Y., Bhavsar, M. and Niroula, P. (2026). \emph{From Human Markets to Machine Markets: Transient Amplification, an Exact Depth Condition, and a Maximal Pre-Trade Guard}. Companion working paper.
'''
    bib = bib.replace('\\end{thebibliography}',companions+'\\end{thebibliography}')
    front = (HERE/'frontmatter.tex').read_text()
    tex = preamble+'\\begin{document}\n'+front+'\n'+body+'\n\\appendix\n\\section{Proofs}\n'+'\n'.join(proofs)+'\n'+bib+'\n\\end{document}\n'
    (HERE/'paper3.tex').write_text('% GENERATED: edit thesis/ch4_paper3.tex or paper3/frontmatter.tex.\n'+tex)
    for _ in range(3):
        r = subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','paper3.tex'],cwd=HERE,capture_output=True,text=True)
        if r.returncode:
            print(r.stdout[-5000:]);raise SystemExit(r.returncode)
    log = (HERE/'paper3.log').read_text()
    if 'undefined references' in log or 'Citation' in log and 'undefined' in log:
        raise ValueError('Unresolved references in stand-alone paper')
    abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',front,re.S)[1]
    if sha(source_path) != source_hash:
        raise RuntimeError('Authoritative thesis source changed during build; rebuild the draft')
    if sha(ROOT/'thesis/thesis.tex') != template_hash:
        raise RuntimeError('Thesis template changed during generation')
    receipt={'source_sha256':source_hash,'thesis_template_sha256':template_hash,'frontmatter_sha256':sha(HERE/'frontmatter.tex'),
             'bibliography_sha256':sha(ROOT/'thesis/bib_new.tex'),'generated_tex_sha256':sha(HERE/'paper3.tex'),
             'pdf_sha256':sha(HERE/'paper3.pdf'),'proof_blocks':len(proofs),
             'abstract_words':len(abstract.split()),'external_references':used,
             'status':'review_draft_with_targets_and_pending_evidence_not_submission_ready'}
    (HERE/'build_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(re.search(r'Output written.*',log)[0])
    print('Abstract words:',receipt['abstract_words'],'; shared-source proof blocks:',len(proofs))


if __name__=='__main__':
    main()
