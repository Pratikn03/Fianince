"""Insert the verified-return record while preserving all existing formal blocks."""
from pathlib import Path
import hashlib,json,re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BEGIN='% BEGIN ADVANCED RETURN STATUS 20261030'
END='% END ADVANCED RETURN STATUS 20261030'
FRONT=r'''\paragraph{Research status update: 30 October 2026.}
This development revision records a verified returned synthetic experiment and
a dated work register at the end. The new audit supports a conditional
finite-horizon financial decision result, not general profitability or
real-market safety. Earlier theoretical and historical claims are retained
with their stated assumptions; this update does not independently verify every
proof or rerun every earlier empirical study. Novelty, full proof review,
economic information acquisition and the public-data bridge remain open.
'''
REPRO='The historical simulation results retain their original execution records; this revision reruns the named advanced experiment only.'
MAIN=[
 'ceiling_suite/papers/paper1/paper1.tex','ceiling_suite/papers/paper2/paper2.tex',
 'ceiling_suite/papers/versions/Paper1_QE.tex','ceiling_suite/papers/versions/Paper2_JF.tex',
 'ceiling_suite/papers/flagship/identify_certify.tex',
 'ceiling_suite/paper1/paper1.tex','ceiling_suite/paper2/paper2.tex']
FRONTS=[f'ceiling_suite/{prefix}{paper}/{name}_front.tex' for prefix in ['','papers/'] for paper,name in [('paper1','p1'),('paper2','p2')]]
FORMAL=re.compile(r'\\begin\{(theorem|lemma|proposition|corollary|definition|assumption|proof)\}(.*?)\\end\{\1\}',re.S)

def integrate():
    changes=[]
    def save(rel,old,new):
        if new==old:return
        a=[m.group() for m in FORMAL.finditer(old)];b=[m.group() for m in FORMAL.finditer(new)]
        if a!=b:raise ValueError('Original formal blocks changed: '+rel)
        (ROOT/rel).write_text(new)
        changes.append(dict(path=rel,original_sha256=hashlib.sha256(old.encode()).hexdigest(),updated_sha256=hashlib.sha256(new.encode()).hexdigest(),original_formal_blocks=len(a),formal_blocks_unchanged=True))
    def front(s):
        if '% BEGIN ADVANCED FRONT STATUS 20261030' not in s:
            s=s.replace(r'\end{abstract}',r'\end{abstract}'+'\n\n% BEGIN ADVANCED FRONT STATUS 20261030\n'+FRONT+'% END ADVANCED FRONT STATUS 20261030\n',1)
        return s.replace('Every simulation number was re-run for this version.',REPRO).replace('Development revision, 29 October 2026','Development revision, 30 October 2026')
    def block(depth,thesis=False):
        location='../'*depth+'studies/advanced_results_revision_20261030/'
        heading=r'\chapter{Verified advanced run and remaining research}'+'\n' if thesis else ''
        return '\n'+BEGIN+'\n'+heading+r'\input{'+location+'returned_results.tex}\n'+r'\input{'+location+'work_register.tex}\n'+END+'\n'
    for rel in MAIN:
        p=ROOT/rel;old=p.read_text();s=front(old)
        if BEGIN not in s:s=s.replace(r'\end{document}',block(2 if rel.startswith('ceiling_suite/paper') and not rel.startswith('ceiling_suite/papers/') else 3)+r'\end{document}')
        save(rel,old,s)
    for rel in FRONTS:
        p=ROOT/rel;old=p.read_text();save(rel,old,front(old))
    for rel in ['thesis/ch2_paper1.tex','thesis/ch3_paper2_full.tex']:
        p=ROOT/rel;old=p.read_text();s=old.replace('Every simulation number was re-run for this version.',REPRO).replace('in the published version of the paper','in the companion working draft');save(rel,old,s)
    rel='thesis/thesis.tex';p=ROOT/rel;old=p.read_text();s=old
    if '% BEGIN ADVANCED FRONT STATUS 20261030' not in s:
        s=s.replace(r'\chapter*{Statement of co-authorship}','% BEGIN ADVANCED FRONT STATUS 20261030\n'+FRONT+'% END ADVANCED FRONT STATUS 20261030\n\n'+r'\chapter*{Statement of co-authorship}',1)
    s=s.replace('Thesis working draft, revised 29 October 2026','Thesis working draft, revised 30 October 2026')
    s=s.replace('Every result in the new chapters carries a tag:','Tags record the presence of a written argument or pending work, not independent proof approval. Every result in the new chapters carries a tag:')
    if BEGIN not in s:s=s.replace(r'\chapter*{Bibliography for Chapters~1, 4 and 5}',block(1,True)+'\n'+r'\chapter*{Bibliography for Chapters~1, 4 and 5}')
    save(rel,old,s)
    rel='thesis/appA_status.tex';p=ROOT/rel;old=p.read_text();s=old
    note='\n\\noindent\\textbf{Reading this register.} Historical ``proved'' tags mean that a proof is presented in the draft. They do not record independent expert verification. The dated advanced-return work register at the end distinguishes completed execution from open mathematical, novelty and empirical obligations.\n'
    if 'Reading this register.' not in s:s=s.replace(r'\section{Status register}',r'\section{Status register}'+note,1)
    save(rel,old,s)
    rel='thesis/ch1_intro.tex';p=ROOT/rel;old=p.read_text();s=old.replace('condensed from the published version','condensed from the companion working draft');save(rel,old,s)
    rel='studies/finite_horizon_costs_20261029/appendix.tex';p=ROOT/rel;old=p.read_text();s=old.replace(r'\date{29 October 2026}',r'\date{30 October 2026}')
    if BEGIN not in s:s=s.replace(r'\end{document}',block(2)+r'\end{document}')
    save(rel,old,s)
    receipt=HERE/'source_preservation.json'
    if receipt.exists():
        prior=json.loads(receipt.read_text())['changes'];by_path={x['path']:x for x in prior}
        for c in changes:
            if c['path'] in by_path:
                c['original_sha256']=by_path[c['path']]['original_sha256']
            by_path[c['path']]=c
        changes=list(by_path.values())
    receipt.write_text(json.dumps(dict(status='PASS',changes=changes,all_original_formal_blocks_unchanged=True),indent=2)+'\n')
    print(json.dumps(dict(changed_files=len(changes),formal_blocks_preserved=sum(x['original_formal_blocks'] for x in changes))))

if __name__=='__main__':integrate()
