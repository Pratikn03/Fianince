"""Report-only audit: for every table in paper1.tex, match each printed number to a numeric value in the result
files named for that table in the reproducibility appendix or its table note (rounding to the printed precision,
with unit scalings). Unmatched numbers are inputs, derived arithmetic, labels, or gaps to check by hand."""
import re, json, os, subprocess, math
from pathlib import Path
R=Path("/home/claude/fianince")
tex=(R/"ceiling_suite/papers/paper1/paper1.tex").read_text()
i=tex.index("\\section{Reproducibility: source of every number}"); mp=tex[i:tex.index("\\end{longtable}",i)]
body=tex[:i]
files=subprocess.run(["git","ls-files"],cwd=R,capture_output=True,text=True).stdout.split("\n")
js=[f for f in files if f.endswith(".json")]
def resolve(idv):
    idv=idv.replace("\\_","_").replace("\\allowbreak","").strip().rstrip("/")
    b=os.path.basename(idv)
    c=[f for f in js if os.path.basename(f) in (b, b+".json")]
    if not c and idv.endswith("/"): c=[f for f in js if idv in f]
    return c
def leaves(o,acc):
    if isinstance(o,dict):
        for v in o.values(): leaves(v,acc)
    elif isinstance(o,list):
        for v in o: leaves(v,acc)
    elif isinstance(o,(int,float)) and not isinstance(o,bool) and math.isfinite(o): acc.append(float(o))
    return acc
def nums(seg):
    seg=re.sub(r"\\(ref|label|cite[pt]?|texttt|eqref)\{[^}]*\}","",seg)
    seg=seg.replace("{,}","").replace("\\,","")
    out=[]
    for m in re.finditer(r"(?<![A-Za-z_\\])([-−]?\$?-?\d+\.\d+|[-]?\d{2,})(?:\\times10\^\{(-?\d+)\})?",seg):
        t=m.group(1).replace("$","").replace("−","-")
        try: v=float(t)
        except: continue
        if m.group(2): v*=10**int(m.group(2))
        dec=len(t.split(".")[1]) if "." in t else 0
        out.append((t,v,dec))
    return out
report=[]
for lab in re.findall(r"\\label\{(tab:[^}]+)\}",body):
    rows=[r for r in mp.split("\\\\") if "\\ref{"+lab+"}" in r]
    ids=[x for r in rows for x in re.findall(r"\\(?:texttt|path)\{((?:[^{}]|\{[^{}]*\})*)\}",r)]
    k=body.index("\\label{"+lab+"}"); s=body.rfind("\\begin{table",0,k); e=body.find("\\end{table}",k)
    seg=body[s:e]
    tb=seg[seg.find("\\begin{tabular"):seg.find("\\end{tabular}")]
    note=re.search(r"Kind: [^\n]*",seg)
    ids+= re.findall(r"\\texttt\{((?:[^{}]|\{[^{}]*\})*)\}", note.group(0)) if note else []
    jfiles=sorted({f for x in ids for f in resolve(x)})
    vals=[]
    for f in jfiles:
        try: vals+=leaves(json.load(open(R/f)),[])
        except Exception: pass
    pn=nums(tb)
    def ok(v,dec):
        tol=0.5*10**(-dec)+1e-12
        for x in vals:
            for sc in (1,100,0.01,1e-6,1e6,1e3,1e-3):
                if abs(x*sc-v)<=tol*1.0001 or abs(abs(x*sc)-abs(v))<=tol*1.0001: return True
        return False
    matched=[p for p in pn if ok(p[1],p[2])] if vals else []
    report.append((lab,len(jfiles),len(pn),len(matched),[p[0] for p in pn if p not in matched][:12]))
for r in report:
    print(f"{r[0]:22s} json={r[1]:2d} numbers={r[2]:3d} matched={r[3]:3d}  unmatched e.g. {r[4]}")
