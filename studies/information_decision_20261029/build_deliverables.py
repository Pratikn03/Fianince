"""Compile blank manuscript and make an embedded, checksum-verified Colab notebook."""
from pathlib import Path
import base64,hashlib,io,json,subprocess,zipfile
import nbformat

ROOT=Path(__file__).resolve().parent
paper=ROOT/'paper';paper.mkdir(exist_ok=True)
sections1=['Abstract','Economic question and contribution','Closest results and precise distinction',
 'Institution and observation contracts','Closed-loop model and identifiable objects',
 'Identification limit: statement and proof','Information and financial resource costs',
 'Disclosure and matched information requirements','Numerical witnesses and robustness',
 'Empirical design and sample-use record','Results','Limitations and conclusion']
sections2=['Abstract','Economic question and contribution','Related portfolio and market-microstructure research',
 'Institution, objective and available actions','Information sets and observation assumptions',
 'Entry, holding horizon, exit and account accounting','Exposure bound: statement and proof',
 'Confidence set and data-selected decision: statement and proof',
 'Identification versus decision value: statement and proof',
 'Disclosure benefit and acquisition cost','Baseline policies and evaluation design',
 'Synthetic results','Market-data results','Misspecification and negative results',
 'Economic interpretation','Limitations and conclusion']
tex=r'''\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{hyperref}
\hypersetup{pdftitle={Machine Markets: Blank Research Paper Templates}}
\setlength{\parindent}{0pt}
\newcommand{\slot}[1]{\section{#1}\noindent\mbox{}\par\vspace{3.1cm}}
\begin{document}
\begin{center}{\Large Machine Markets}\\[0.3cm]{\large Research Paper Templates}\end{center}
'''
def slots(items):
    return '\n'.join('\\slot{'+x+'}'+('\\clearpage' if i%2==1 else '') for i,x in enumerate(items))
tex+='\\clearpage\\part*{Paper 1: Information Limits and Financial Identification}\n'
tex+=slots(sections1)
tex+='\n\\clearpage\n\\setcounter{section}{0}\n\\part*{Paper 2: Information Required for an Exposure Decision}\n'
tex+=slots(sections2)
tex+='\n\\clearpage\n\\appendix\n'
tex+=slots(['Notation and time conventions','Proofs and counterexamples',
 'Theorem-to-code and formalization correspondence','Data provenance and sample-use ledger',
 'Additional tables and figures','Reproduction and independent review','References'])
tex+='\n\\end{document}\n'
(paper/'Blank_Research_Papers.tex').write_text(tex)
subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','Blank_Research_Papers.tex'],cwd=paper,check=True,stdout=subprocess.PIPE)
for ext in ['aux','log','out']:(paper/('Blank_Research_Papers.'+ext)).unlink(missing_ok=True)

buf=io.BytesIO()
with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(ROOT.rglob('*')):
        if f.is_file() and f.suffix in ['.py','.md','.csv','.txt','.lean','.tex','.pdf','.c'] and not any(x in f.relative_to(ROOT).parts for x in ['validation','results','__pycache__']):
            zi=zipfile.ZipInfo(str(f.relative_to(ROOT)),date_time=(2026,10,29,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(zi,f.read_bytes())
payload=buf.getvalue();sha=hashlib.sha256(payload).hexdigest();b64=base64.b64encode(payload).decode()
nb=nbformat.v4.new_notebook();nb.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}}
nb.cells=[
 nbformat.v4.new_markdown_cell('''# Machine Markets: information to financial decision

Use **Runtime → Run all** with a CPU runtime. This notebook embeds the exact source package; it does not clone the repository. The default full run tests seven synthetic regimes and produces a return ZIP. The manuscript templates remain blank.

The experiment assumes controlled independent reset observations and a declared finite candidate class. It cannot establish live-market safety, a general minimax theorem, or a publication rating. Eight conditional decision-logic lemmas are checked separately with pinned Lean; their limited scope is exported.

The first Lean install downloads approximately 344 MB. All results, errors, source hashes and skipped stages are kept. No real-market run occurs unless you supply a CSV path below.'''),
 nbformat.v4.new_code_cell('''# Configuration: retain all seeds and outcomes; changing settings creates a new exploratory run.
PROFILE = "full"  # "smoke" checks software only
SEED = 20261029
CHECK_LEAN = True
LEAN_CACHE = None  # optional existing pinned toolchain directory; otherwise uses ~/.cache
MARKET_CSV = None  # optional /content/file.csv: timestamp,market,price,signed_flow
'''),
 nbformat.v4.new_code_cell('''import sys, subprocess
subprocess.run([sys.executable,"-m","pip","install","-q","numpy>=1.26,<3","scipy>=1.11,<2","pandas>=2.1,<3","matplotlib>=3.8,<4","pytest>=8,<9","nbformat>=5.9,<6","zstandard>=0.22,<1"], check=True)
'''),
 nbformat.v4.new_code_cell('''import base64, hashlib, io, zipfile
from pathlib import Path
from datetime import datetime, timezone
'''+'SOURCE_SHA256 = '+repr(sha)+'\nEMBEDDED_PACKAGE = '+repr(b64)+'''
payload = base64.b64decode(EMBEDDED_PACKAGE)
assert hashlib.sha256(payload).hexdigest() == SOURCE_SHA256
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
base = Path("/content" if Path("/content").exists() else ".").resolve()
source = base / ("mm_information_decision_source_" + stamp)
source.mkdir(exist_ok=False)
with zipfile.ZipFile(io.BytesIO(payload)) as z:
    for item in z.infolist():
        target = (source / item.filename).resolve()
        assert target.is_relative_to(source), "Unsafe archive path"
    z.extractall(source)
print("Source SHA-256:", SOURCE_SHA256)
print("Source:", source)
'''),
 nbformat.v4.new_code_cell('''out = base / ("Information_Decision_Results_" + stamp)
cmd = [sys.executable, str(source/"run.py"), "--profile", PROFILE, "--seed", str(SEED), "--out", str(out), "--lean", "install" if CHECK_LEAN else "skip"]
if MARKET_CSV:
    cmd += ["--market-csv", MARKET_CSV]
if LEAN_CACHE:
    cmd += ["--lean-cache", LEAN_CACHE]
print("Running; all policy and regime outputs will be preserved.")
# Capture logs and continue to the download cell even if a check fails.
execution = subprocess.run(cmd, cwd=source, capture_output=True, text=True)
execution_log = out.parent / (out.name + "_execution.log")
execution_log.write_text(execution.stdout + "\\n" + execution.stderr)
print(execution.stdout[-5000:])
if execution.returncode:
    print("Run failed or stopped. Keep the ZIP/log for diagnosis:", execution.stderr[-2000:])
'''),
 nbformat.v4.new_code_cell('''# Repackage after adding the outer execution log and actual installed-package list.
import json, shutil
if not out.exists():
    out.mkdir()
    (out/"run_status.json").write_text(json.dumps({"status":"FAILED_BEFORE_OUTPUT","returncode":execution.returncode}))
shutil.copy2(execution_log, out/"execution.log")
(out/"embedded_source_sha256.txt").write_text(SOURCE_SHA256+"\\n")
packages = subprocess.run([sys.executable,"-m","pip","freeze"],capture_output=True,text=True)
(out/"installed_packages.txt").write_text(packages.stdout)
manifest = {str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob("*") if f.is_file() and f.name!="manifest.json"}
(out/"manifest.json").write_text(json.dumps(manifest,indent=2))
zip_path = out.with_suffix(".zip")
with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
    for f in sorted(out.rglob("*")):
        if f.is_file(): z.write(f,f.relative_to(out))
print("Upload this results ZIP back for analysis:",zip_path)
print("ZIP SHA-256:",hashlib.sha256(zip_path.read_bytes()).hexdigest())
try:
    from google.colab import files
    files.download(str(zip_path))
except ImportError:
    from IPython.display import FileLink, display
    display(FileLink(str(zip_path)))
''')]
nbformat.validate(nb);nbformat.write(nb,ROOT/'Information_Decision_Run_and_Return.ipynb')
(ROOT/'EMBEDDED_SOURCE.json').write_text(json.dumps({'sha256':sha,'bytes':len(payload),'purpose':'source bytes embedded in downloadable notebook'},indent=2))
print('Notebook and blank paper built',sha,len(payload))
