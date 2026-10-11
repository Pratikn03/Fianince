"""JF format candidate: retain every scientific body object and original freeze.

Unknown author disclosures/affiliations remain explicit draft fields. No author
attestation, independent review or submission readiness is inferred from formatting.
"""
from pathlib import Path
import re,json,hashlib,subprocess
HERE=Path(__file__).resolve().parent;COMPLETION=HERE.parent;ROOT=HERE.parents[3];BASE=COMPLETION.parent
ABSTRACT=r'''We study identification of adaptive memory under financially constrained probing. For a known symmetric cohort pair, deterministic reset probes without process noise require executed quantity of order $\delta^{-2}$ and solvent trader capital of order $\delta^{-4}$ under noisy-price observations. We prove attainable bounds and show how financial disclosure or natural excitation changes the experiment. Reconstruction of 768 market study units reveals timing and filter sensitivity and rejects maintained covariance restrictions. Financial replays distinguish inventory limits from defaults. These results define conditional information contracts rather than identify participant-level learning or certify operational market safety.'''
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 original=ROOT/'paper/Machine_Markets_JF_Submission.tex';s=original.read_text();baseline=sha(original)
 body=s[s.index(r'\section{Introduction}'):s.index(r'\end{document}')]
 words=re.sub(r'\$[^$]*\$','mathematical-order',ABSTRACT).split();assert len(words)<=100
 candidate=s.replace(r'\usepackage[margin=1in]{geometry}',r'\usepackage[left=1in,right=1in,top=1.5in,bottom=1.5in]{geometry}')
 a=candidate.index(r'\begin{abstract}');b=candidate.index(r'\end{abstract}',a)+len(r'\end{abstract}')
 candidate=candidate[:a]+r'\begin{abstract}\noindent '+ABSTRACT+r'\end{abstract}'+candidate[b:]
 # Emails do not establish an affiliation; never invent a university appointment.
 a=candidate.index(r'\author{');b=candidate.index(r'\date{',a)
 candidate=candidate[:a]+r'''\author{\textbf{Pratik Niroula}\thanks{Current affiliation pending author confirmation. Email: \texttt{pratik.niroula@alumni.harvard.edu}.} \quad and \quad \textbf{Prashant Niroula}\thanks{Current affiliation pending author confirmation. Email: \texttt{prashant.niroula@alumni.harvard.edu}.}}
'''+candidate[b:]
 anchor=r'\newpage'+'\n'+r'\setcounter{page}{1}'
 disclosure=r'''\clearpage
\thispagestyle{empty}
\section*{Disclosure Statement: Pratik Niroula}
\noindent\textbf{Author-provided declaration; review draft.} This format candidate is not ready for submission. Current affiliations/status remain unknown. The authors declare equal contribution, no external research funding and no conflicts; scientific review and final submission checks remain open.

\noindent Pratik Niroula and Prashant Niroula contributed equally. No external research funding was received. No conflicts of interest are declared.

\clearpage
\thispagestyle{empty}
\section*{Disclosure Statement: Prashant Niroula}
\noindent\textbf{Author-provided declaration; review draft.} Pratik Niroula and Prashant Niroula contributed equally. No external research funding was received. No conflicts of interest are declared.

\noindent A separate AI-assistance and source/rights record accompanies this review candidate. Author responsibility and journal submission declarations require confirmation before submission.

\clearpage
\setcounter{page}{1}'''
 assert anchor in candidate;candidate=candidate.replace(anchor,disclosure,1)
 assert candidate[candidate.index(r'\section{Introduction}'):candidate.index(r'\end{document}')]==body
 target=ROOT/'paper/Machine_Markets_JF_Format_Candidate_20261008.tex';target.write_text(candidate)
 build=BASE/'build';logs=BASE/'logs';job='Machine_Markets_JF_Format_Candidate_20261008'
 for iteration in range(1,4):
  r=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-recorder',f'-jobname={job}',f'-output-directory={build}',str(target)],cwd=ROOT/'paper',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  (logs/f'{job}_pass{iteration}.txt').write_bytes(r.stdout)
  if r.returncode:raise RuntimeError(r.stdout.decode()[-3000:])
 assert sha(original)==baseline
 text=r.stdout.decode();info=subprocess.run(['pdfinfo',str(build/f'{job}.pdf')],capture_output=True,text=True,check=True).stdout
 pages=int(next(line.split(':',1)[1] for line in info.splitlines() if line.startswith('Pages:')))
 receipt=dict(status='JF_FORMAT_DRAFT_AUTHOR_AND_SCIENTIFIC_GATES_OPEN',baseline_source_sha256=baseline,candidate_source_sha256=sha(target),scientific_body_sha256=hashlib.sha256(body.encode()).hexdigest(),scientific_body_identical=True,abstract_word_count=len(words),font_pt=12,line_spacing='onehalfspacing',side_margin_inches=1,top_bottom_margin_inches=1.5,physical_pages=pages,disclosure_pages=2,counted_manuscript_pages=pages-2,within_60_page_limit=pages-2<=60,overfull_boxes='Overfull' in text,undefined_references='undefined' in text.lower(),guidelines='https://afajof.org/submissions/',limits=['Affiliations/status remain unknown. Equal contribution, no external funding and no conflicts are author-provided declarations; final submission requirements remain open.','Formatting does not establish novelty, scientific validity, data rights or independent review.'])
 (HERE/'jf_format_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':run()
