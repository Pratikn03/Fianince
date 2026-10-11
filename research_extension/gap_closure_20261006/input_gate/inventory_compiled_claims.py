"""Inventory the actual compiler-loaded project sources, including generated files.
Literal claims/equations are review obligations; discovery does not certify them.
"""
from pathlib import Path
import re,json,hashlib,sys
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;ROOT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    fls=Path(sys.argv[1]) if len(sys.argv)>1 else BASE/'build/Machine_Markets_GateRepair_20261008.fls';lines=fls.read_text().splitlines();pwd=Path(next(l[4:] for l in lines if l.startswith('PWD ')));inputs=[]
    for line in lines:
        if not line.startswith('INPUT '):continue
        p=Path(line[6:]);p=(p if p.is_absolute() else pwd/p).resolve()
        if p.is_file() and p.is_relative_to(ROOT) and p not in inputs:inputs.append(p)
    sources=[p for p in inputs if p.suffix=='.tex'];assets=[p for p in inputs if p.suffix in ['.pdf','.png','.jpg','.jpeg']];objects=[];numeric=[]
    # Keep character positions/line numbers while hiding ordinary TeX comments.
    for p in sources:
        text=p.read_text();active=re.sub(r'(?<!\\)%[^\n]*',lambda m:' '*len(m.group()),text)
        consumed=set()
        pattern=r'\\begin\{(table\*?|longtable|figure\*?|theorem|proposition|lemma|corollary|equation\*?|align\*?)\}(?:\[([^\]]*)\])?'
        for m in re.finditer(pattern,active):
            env=m.group(1);end=active.find('\\end{'+env+'}',m.end())
            if end<0:raise ValueError('Unterminated literal environment '+str(p)+':'+env)
            end+=len('\\end{'+env+'}');snippet=text[m.start():end];startline=text.count('\n',0,m.start())+1;endline=text.count('\n',0,end)+1;consumed.update(range(startline,endline+1));labels=re.findall(r'\\label\{([^}]+)\}',snippet)
            objects.append({'source':str(p.relative_to(ROOT)),'source_sha256':sha(p),'environment':env,'labels':labels,'line':startline,'end_line':endline,'object_sha256':hashlib.sha256(snippet.encode()).hexdigest(),'status':'SEMANTIC_REVIEW_OPEN','limits':'Literal compiler-loaded source inventory; macro expansion and semantic proof/result lineage require separate verification'})
        bibliography=False
        for n,line in enumerate(active.splitlines(),1):
            if '\\begin{thebibliography}' in line:bibliography=True
            if n in consumed or bibliography:continue
            if line.startswith(('\\documentclass','\\usepackage','\\newcommand','\\setlength','\\setcounter','\\definecolor','\\hypersetup','\\newtheorem')):continue
            if re.search(r'(?<![A-Za-z])\d+(?:\.\d+)?',line):numeric.append({'source':str(p.relative_to(ROOT)),'line':n,'text':text.splitlines()[n-1],'status':'SEMANTIC_REVIEW_OPEN','classification':'Numeric source text: may be a definition, methodological count, citation, literal result or claim; not automatically empirical'})
    from collections import Counter
    counts=dict(Counter(o['environment'] for o in objects))
    out={'status':'COMPILER_BOUND_INVENTORY_FULL_SEMANTIC_RECONCILIATION_OPEN','compiler_record_sha256':sha(fls),'compiler_pwd':str(pwd),'sources':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sources],'rendered_assets':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in assets],'objects':objects,'numeric_source_review_queue':numeric,'counts':counts,'limits':['Tracks actual compiler-loaded project sources including generated TeX','Includes table/figure starred environments omitted by the older scanner','Does not treat numeric text matching as evidence','Not a full macro-expanded semantic audit or a scientific completion certificate']}
    target=Path(sys.argv[2]) if len(sys.argv)>2 else HERE/'compiled_claim_inventory.json'
    target.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'source_files':len(sources),'assets':len(assets),'objects':len(objects),'counts':counts,'numeric_review_lines':len(numeric)},indent=2))
if __name__=='__main__':run()
