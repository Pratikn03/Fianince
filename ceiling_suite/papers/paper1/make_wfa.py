"""Build the anonymous WFA 2027 submission of Paper 1 from paper1.tex (the working draft stays unchanged).

Keeps the paper itself (abstract through Appendix D) and removes what is not part of a submission: the dated research
status paragraph, the development-revision and information-decision blocks, the finite-horizon extension and the
returned-experiment work register (all retained in paper1.tex and in studies/). Anonymises the title page, running
header and the self-citation of the companion paper. Output: paper1_wfa.tex -> paper1_wfa.pdf.
"""
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
src = (HERE / "paper1.tex").read_text()

core, _, _ = src.partition("% BEGIN ECONOMIC REVIEW 20261029")
assert "\\section{Reproducibility: source of every number}" in core and "returned_results" not in core
core = re.sub(r"% BEGIN ADVANCED FRONT STATUS 20261030.*?% END ADVANCED FRONT STATUS 20261030\n", "", core, flags=re.S)
core = re.sub(r"\\author\{.*?\}\}\n", r"\\author{}\n", core, count=1, flags=re.S)
core = core.replace("\\date{Development revision, 30 October 2026}", "\\date{November 2026}")
core = core.replace("\\fancyhead[L]{\\small Niroula and Niroula}", "\\fancyhead[L]{\\small Anonymous submission}")
core = re.sub(r"\\bibitem\[Niroula et~al\.\(2026\)\]\{niroula2026b\}.*?\n",
              "\\\\bibitem[Anonymous(2026)]{niroula2026b} Anonymous (2026). Companion paper on transient amplification and "
              "pre-trade guards in closed-loop markets. Working paper, withheld for anonymous review.\n", core, count=1)
core = core.replace("The historical simulation results retain their original execution records; this revision reruns the "
                    "named advanced experiment only. ", "")
# Focus the main text on the paper's question (what prices reveal, what disclosure buys, in money and in data).
# Supporting material moves, unchanged and with its labels, to the internet appendix before the reproducibility map.
MOVES = [  # (heading that starts the block, heading that ends it, appendix title)
    ("\\section{Account-level capital}", "\\section{Unknown mixtures and passive data}", "Account-level capital"),
    ("\\subsection{Near-colliding rates: a uniform rate for the merged measure}", "\\subsection{General memory: the minimax rate is logarithmic}",
     "Near-colliding rates: a uniform rate for the merged measure"),
    ("\\section{Robustness to nonlinear and adaptive trading rules}", "\\section{What disclosure buys}", "Robustness to nonlinear and adaptive trading rules"),
    ("\\section{A spectral blind spot}", "\\section{Empirical feedback and its measurement}", "A spectral blind spot"),
    ("\\section{Empirical feedback and its measurement}", "\\section{Implications for supervision and market design}", "Empirical feedback and its measurement"),
]
repro = "\\section{Reproducibility: source of every number}"
moved = []
for start, stop, title in MOVES:
    i, j = core.index(start), core.index(stop)
    block = core[i:j]
    core = core[:i] + core[j:]
    head = block[:block.index("}") + 1]
    body = block[len(head):]
    if head.startswith("\\subsection"):                     # a moved subsection becomes an appendix section;
        body = body.replace("\\subsubsection{", "\\subsection{")  # (none present, kept for safety)
    moved.append("\\section{Internet appendix: " + title + "}" + body)
core = core.replace(repro, "".join(moved) + repro, 1)
# References to moved material say "Appendix", not "Section".
for lab in ("sec:account", "sec:dollars", "sec:uniform", "sec:learners", "sec:blind", "sec:empirics"):
    core = core.replace("Section~\\ref{" + lab + "}", "Appendix~\\ref{" + lab + "}")
    core = core.replace("Sections~\\ref{" + lab + "}", "Appendices~\\ref{" + lab + "}")
# No table of contents in a submission; an outline that matches the submission's own order.
core = core.replace("\\setcounter{page}{1}\n\\tableofcontents\n\\newpage\n", "\\setcounter{page}{1}\n", 1)
o1, o2 = core.index("\\subsection{Outline}"), core.index("\\section{Model and microfoundations}")
core = core[:o1] + ("\\subsection{Outline}\n"
    "Section~\\ref{sec:model} sets out the model and Section~\\ref{sec:ident} the identification boundary. "
    "Section~\\ref{sec:resources} turns memory resolution into executed quantity, capital and money for a known pair, and "
    "Section~\\ref{sec:mixtures} treats unknown mixtures, general memory and passive data. Section~\\ref{sec:disclosure} "
    "states what disclosure buys, prices it against the Consolidated Audit Trail, and tests it on the CFTC's mandated "
    "trader-class reports and on Binance's class ratios. Section~\\ref{sec:policy} draws the implications for "
    "supervision and Section~\\ref{sec:conclusion} concludes. Proofs are in Appendix~\\ref{app:proofs}; the internet "
    "appendix contains account-level capital, near-colliding rates, robustness to learning rules, the spectral blind spot "
    "and the measurement of reduced-form feedback, and Appendix~\\ref{app:repro} maps every number to its source.\n\n") + core[o2:]
# Hygiene for a submission: no internal tags, script names or hashes outside the reproducibility appendix
# (Appendix "Reproducibility: source of every number" keeps the full map from each number to its script).
core = core.replace("\\newcommand{\\lab}[1]{\\textsc{[#1]}}", "\\newcommand{\\lab}[1]{}")
cut = core.index("\\section{Reproducibility: source of every number}")
head, tail = core[:cut], core[cut:]
TT = r"\\texttt\{(?:[^{}]|\{[^{}]*\})*?\}"
head = re.sub(r"\s*Kind: [^\n]*?(?=\\end\{tablenotes\})", "", head)                      # 'Kind: recomputed (...)' table notes
head = re.sub(r"\s*\(" + TT + r"(?:\s*(?:and|,|\$\\to\$)\s*" + TT + r")*\)", "", head)    # (script.py) parentheticals
head = re.sub(r";\s*" + TT + r"(?:\s*\$\\to\$\s*" + TT + r")?\)", ")", head)              # '...; script.py)'
head = re.sub(r"\s*From " + TT + r"(?:\s*and\s*" + TT + r")*;\s*", " ", head)                 # 'From a.py and b.py; '
head = re.sub(r"\s*Recomputed columns from " + TT + r"\.?", "", head)
head = re.sub(r"Estimators re-implemented in " + TT + r":\s*", "Estimators: ", head)
head = re.sub(r"\s*\((?:registered,\s*)?SHA-256 " + TT + r"\)", "", head)                  # (SHA-256 abc...)
head = re.sub(r"[,;]?\s*[Ss]pecification SHA-256 " + TT + r"[;,.]?", "", head)
head = re.sub(r"\s*SHA-256 " + TT, "", head)
core = head + tail
left = [m.group(0)[:90] for m in re.finditer(r"[^\n]{0,40}(\.py\b|SHA-256)[^\n]{0,40}", head)]
print("script/hash mentions left outside the reproducibility appendix:", len(left))
for l in left[:12]:
    print("   ", l)
out = core.rstrip() + "\n\n\\end{document}\n"
for word in ("Niroula", "Pratik", "Prashant", "Mankato", "Tribhuvan", "mnsu", "Pratikn03", "fianince"):
    assert word.lower() not in out.lower().replace("niroula2026b", ""), f"identifying text left: {word}"
(HERE / "paper1_wfa.tex").write_text(out)
for _ in range(2):
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "paper1_wfa.tex"], cwd=HERE,
                   check=True, stdout=subprocess.DEVNULL)
print("built paper1_wfa.pdf")
