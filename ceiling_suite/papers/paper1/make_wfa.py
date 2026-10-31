"""Build the anonymous WFA 2027 submission of Paper 1 from paper1.tex (the working draft stays unchanged).

Keeps the paper itself (abstract through Appendix D) and removes what is not part of a submission: the dated research
status paragraph, the development-revision and information-decision blocks, the finite-horizon extension and the
returned-experiment work register (all retained in paper1.tex and in studies/). Anonymises the title page, running
header and the self-citation of the companion paper. Output: paper1_wfa.tex -> paper1_wfa.pdf.

With --ssrn it builds the named public preprint instead (same text and structure, authors and companion citation kept,
link to the public code repository, plus the finite-horizon decision extension as a further internet appendix):
paper1_ssrn.tex -> paper1_ssrn.pdf. --solo drops the second author; use it only
once both authors have agreed in writing.
"""
import argparse
import re
import subprocess
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--ssrn", action="store_true", help="named public preprint instead of the anonymous WFA version")
ap.add_argument("--solo", action="store_true", help="single-author byline (only after written agreement)")
ARGS = ap.parse_args()
NAME = "paper1_ssrn" if ARGS.ssrn else "paper1_wfa"
HERE = Path(__file__).resolve().parent
src = (HERE / "paper1.tex").read_text()

core, _, _ = src.partition("% BEGIN ECONOMIC REVIEW 20261029")
assert "\\section{Reproducibility: source of every number}" in core and "returned_results" not in core
core = re.sub(r"% BEGIN ADVANCED FRONT STATUS 20261030.*?% END ADVANCED FRONT STATUS 20261030\n", "", core, flags=re.S)
core = core.replace("\\date{Development revision, 30 October 2026}", "\\date{This version: 30 October 2026}")
if ARGS.ssrn:
    if ARGS.solo:
        core = re.sub(r"\n\\and Prashant Niroula\\thanks\{.*?\}\}", "}", core, count=1, flags=re.S)
        core = core.replace("\\fancyhead[L]{\\small Niroula and Niroula}", "\\fancyhead[L]{\\small Niroula}")
    repo = ("\n\n\\noindent\\textbf{Code and data.} All code, pre-specified test specifications and result files are public at "
            "\\url{https://github.com/Pratikn03/Fianince}.\n")
    core = core.replace("\\paragraph{Reproducibility.}", repo + "\n\\paragraph{Reproducibility.}", 1)
else:
    core = re.sub(r"\\author\{.*?\}\}\n", r"\\author{}\n", core, count=1, flags=re.S)
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
if ARGS.ssrn:
    # SSRN = journal-length main paper + online supplement. These blocks move, unchanged and with their labels,
    # from the main text to the supplement (headings must still exist in core when each move runs).
    MOVES = [
        ("\\subsection{Related literature}", "\\subsection{Outline}", "Extended related literature"),
        ("\\subsection{What prices hide, in economic terms}", "\\subsection{Natural excitation and the cost of ambiguity}",
         "What prices hide, in economic terms"),
        ("\\subsection{Natural excitation and the cost of ambiguity}", "\\section{Account-level capital}",
         "Natural excitation and the cost of ambiguity"),
        ("\\subsection{Local information: the Cram\\'er--Rao benchmark}", "\\subsection{A global two-point bound for any estimator}",
         "Local information: the Cram\\'er--Rao benchmark"),
        ("\\subsection{Disclosure in dollars}", "\\subsection{When disclosure is worth acquiring}",
         "A hypothetical scale illustration: disclosure in dollars"),
    ] + MOVES
repro = "\\section{Reproducibility: source of every number}"
moved = []
MOVED_SEC_LABELS = []
supp_blocks = []   # --ssrn: the spectral blind spot and feedback measurement go to a separate supplement PDF
for start, stop, title in MOVES:
    i, j = core.index(start), core.index(stop)
    block = core[i:j]
    core = core[:i] + core[j:]
    head = block[:block.index("}") + 1]
    body = block[len(head):]
    if head.startswith("\\subsection"):                     # a moved subsection becomes an appendix section;
        body = body.replace("\\subsubsection{", "\\subsection{")  # (none present, kept for safety)
    MOVED_SEC_LABELS.extend(re.findall(r"\\label\{((?:sec|app):[^}]*)\}", block))
    if False and title in ("A spectral blind spot", "Empirical feedback and its measurement"):  # now part of the online supplement
        supp_blocks.append("\\section{" + title + "}" + body)
    else:
        moved.append("\\section{Internet appendix: " + title + "}" + body)
if ARGS.ssrn:
    # The full preprint also carries the finite-horizon decision extension (complete statements and proofs, with its
    # own status paragraph) as a further internet appendix. Its separate reference list is merged into the main one.
    a, b = "% BEGIN FINITE HORIZON COST 20261029\n", "% END FINITE HORIZON COST 20261029"
    fhc = src[src.index(a) + len(a):src.index(b)]
    # The full note (statements, proofs, its own references) is published as a separate supplement PDF in the
    # repository; the preprint carries a one-page summary with the same label.
    supp = (src[:src.index("\\begin{document}")] + "\\begin{document}\n\\begin{center}\\large Supplement to ``What Prices "
            "Reveal About Hidden Trader Populations, and What Identifying Them Costs''\\end{center}\n" + fhc + "\n\\end{document}\n")
    (HERE / "paper1_finite_horizon_supplement.tex").write_text(supp)
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "paper1_finite_horizon_supplement.tex"], cwd=HERE,
                       stdout=subprocess.DEVNULL)
    i, j = fhc.index("\\begin{thebibliography}"), fhc.index("\\end{thebibliography}") + len("\\end{thebibliography}")
    fhc = fhc[:i] + fhc[j:]
    fhc = fhc.replace("\\section*{Finite-horizon information, cohort ambiguity, and net inventory-service value}",
                      "\\section{Internet appendix: Finite-horizon information, cohort ambiguity, and net inventory-service value}"
                      "\\label{app:fhc}", 1)
    fhc = fhc.replace("\\section*{Checked synthetic financial illustration}", "\\subsection*{Checked synthetic financial illustration}")
    assert "\\section*" not in fhc
    for old, new in [  # wording written for the development log, restated for a public reader (same claims)
        ("It does not close the broader open\ntheorem of the preceding drafts.",
         "It does not settle the general question of when identification is worth its cost."),
        ("are candidate additions to this project, not verified first-in-literature\nclaims. A specialist must check whether "
         "they are an immediate corollary of\nexisting task-specific or constrained-decision results before publication.",
         "are candidate additions, not verified first-in-literature\nclaims. They have not been independently reviewed, and "
         "they may be an immediate corollary of\nexisting task-specific or constrained-decision results."),
        ("This illustration uses the frozen primary design and the stronger comparison\nrecorded in the design amendment. "
         "It is exploratory and was developed after\nthe earlier project runs; it is not independent preregistration or replication.",
         "This illustration is exploratory. It was developed after the paper's other\nsimulations and is not an "
         "independent preregistration or replication."),
    ]:
        assert fhc.count(old) == 1, old[:40]
        fhc = fhc.replace(old, new)
    fhc = fhc.replace("fhc:waarde", "vanwaarde2020").replace("fhc:heinrich", "heinrich2018").replace("fhc:wagenmaker", "wagenmaker2021")
    moved.append(
        "\\section{Internet appendix: A finite-horizon decision that needs only the combined response}\\label{app:fhc}\n"
        "A separate note, \\texttt{paper1\\_finite\\_horizon\\_supplement.pdf} in the public repository, works out one "
        "financial decision in full. An unlevered desk that warehouses inventory for $H$ periods under a hard stress budget "
        "buys $N$ reset experiments, pays for them out of the same capital, and sizes its position from an upper confidence "
        "bound on the summed price response over the horizon. With probability at least $1-\\gamma$ the position meets the "
        "stress budget for every bounded shock path; its profit shortfall is at most $AN^{-1/2}+Dc_HN$ for explicit "
        "constants $A$ and $D$ and cost $c_H$ per experiment; and a stated inequality guarantees a positive expected net "
        "value of the information. These guarantees hold uniformly over the positive cohort class, whatever the number and "
        "spacing of the cohorts. Under the same observations, telling apart two particular two-cohort economies whose rates "
        "are of order $\\delta$ apart requires a number of experiments of order $\\delta^{-6}$, so at a fixed information price "
        "cohort identification becomes unaffordable while the decision keeps its positive value.\n\n"
        "The lesson cuts both ways. Many risk decisions need only the combined response, which public data identify at the "
        "ordinary rate; class-level records are valuable only for decisions that depend on attribution, such as the "
        "targeted halt of Proposition~\\ref{prop:target}. The note's proofs have not been independently reviewed, its "
        "numerical illustration is exploratory, and its priority is unconfirmed.\n\n")
    # its sources go into the reproducibility map (first longtable after the map heading)
    fhc_rows = (r"Finite-horizon decision appendix: primary decisions, cost--horizon sensitivities (819 rows), hard-pair "
                r"requirements, assumption failures, cash-flow audit & \texttt{studies/finite\_horizon\_costs\_20261029/run.py} "
                r"$\to$ \texttt{results/final\_full\_20261030/} & recomputed\\" + "\n"
                r"Finite-horizon appendix: independent checks and LP cross-check & "
                r"\texttt{studies/finite\_horizon\_costs\_20261029/validation/} & audit\\" + "\n")
    r0 = core.index("\\section{Reproducibility: source of every number}")
    r1 = core.index("\\end{longtable}", r0)
    core = core[:r1] + fhc_rows + core[r1:]
core = core.replace(repro, "".join(moved) + repro, 1)
# References to moved material say "Appendix", not "Section".
for lab in ("sec:account", "sec:dollars", "sec:uniform", "sec:learners", "sec:blind", "sec:empirics"):
    core = core.replace("Section~\\ref{" + lab + "}", "Appendix~\\ref{" + lab + "}")
    core = core.replace("Sections~\\ref{" + lab + "}", "Appendices~\\ref{" + lab + "}")
if ARGS.ssrn and supp_blocks:
    # Build the supplement once to learn its numbering, then point the preprint's references at it.
    bib = core[core.index("\\begin{thebibliography}"):core.index("\\end{thebibliography}") + len("\\end{thebibliography}")]
    pre = core[:core.index("\\begin{document}")]
    supp_tex = (pre + "\\begin{document}\n\\begin{center}\\large Supplement to ``What Prices Reveal About Hidden Trader "
                "Populations, and What Identifying Them Costs'': a spectral blind spot and the measurement of reduced-form "
                "feedback\\end{center}\n\\renewcommand{\\thesection}{S\\arabic{section}}\\renewcommand{\\thetable}{S\\arabic{table}}"
                "\\renewcommand{\\thefigure}{S\\arabic{figure}}\\renewcommand{\\theequation}{S\\arabic{equation}}\n"
                "These two analyses accompany the paper but are not needed for its main results.\n\n"
                + "".join(supp_blocks) + "\n" + bib + "\n\\end{document}\n")
    SUPP = "paper1_feedback_spectral_supplement"
    (HERE / f"{SUPP}.tex").write_text(supp_tex)
    subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{SUPP}.tex"], cwd=HERE, stdout=subprocess.DEVNULL)
    supp_labels = dict(re.findall(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", (HERE / f"{SUPP}.aux").read_text()))
    for lab, num in supp_labels.items():
        for word in ("Appendix", "Appendices", "Section", "Sections"):
            core = core.replace(word + "~\\ref{" + lab + "}", "Supplement~" + num)
        core = core.replace("\\eqref{" + lab + "}", "(" + num + ")").replace("\\ref{" + lab + "}", num)
if ARGS.ssrn:
    # Journal-length main paper followed by an S-numbered online supplement (one PDF; split into two files below).
    for lab in MOVED_SEC_LABELS:
        for w in ("Section", "Sections"):
            core = core.replace(w + "~\\ref{" + lab + "}", "Supplement~\\ref{" + lab + "}")
    core = core.replace("Appendix~\\ref{", "Supplement~\\ref{").replace("Appendices~\\ref{", "Supplements~\\ref{")
    core = core.replace("(Internet Appendix, ", "(Online Supplement, ")
    core = core.replace("\\section{Internet appendix: ", "\\section{").replace("\\section{Internet appendix}", "\\section{Further results}")
    m0 = core.index("\\caption{Map of results}"); t0 = core.rfind("\\begin{table}", 0, m0)
    t1 = core.index("\\end{table}", m0) + len("\\end{table}")
    maptable = core[t0:t1]; core = core[:t0] + core[t1:]          # the map of results stays in the main text
    lit = (HERE / "review" / "litmain.tex").read_text() + maptable + "\n\n"
    core = core.replace("\\subsection{Outline}", lit + "\\subsection{Outline}", 1)
    core = core.replace("\\doublespacing", "\\onehalfspacing", 1)
    supp_head = ("\\appendix\n\\clearpage\n\\setcounter{page}{1}\\renewcommand{\\thepage}{S-\\arabic{page}}"
                 "\\renewcommand{\\thesection}{S\\arabic{section}}\\setcounter{table}{0}\\renewcommand{\\thetable}{S\\arabic{table}}"
                 "\\setcounter{figure}{0}\\renewcommand{\\thefigure}{S\\arabic{figure}}\\setcounter{equation}{0}"
                 "\\renewcommand{\\theequation}{S\\arabic{equation}}\\fancyhead[R]{\\small Online Supplement}\n"
                 "\\begin{center}{\\Large Online Supplement}\\\\[4pt]{\\large What Prices Reveal About Hidden Trader Populations, "
                 "and What Identifying Them Costs}\\end{center}\n\\noindent The supplement contains the proofs (Section~S1), "
                 "further results and robustness checks, the extended literature review, the hypothetical dollar illustration, "
                 "a finite-horizon decision example, the spectral blind spot, the measurement of reduced-form feedback and the reproducibility map. Section, table, figure and equation numbers "
                 "prefixed with S refer to this supplement.\n\n")
    assert core.count("\\appendix\n") == 1
    core = core.replace("\\appendix\n", supp_head, 1)
# No table of contents in a submission; an outline that matches the submission's own order.
core = core.replace("\\setcounter{page}{1}\n\\tableofcontents\n\\newpage\n", "\\setcounter{page}{1}\n", 1)
o1, o2 = core.index("\\subsection{Outline}"), core.index("\\section{Model and motivating examples}")
_outline = ("\\subsection{Outline}\n"
    "Section~\\ref{sec:model} sets out the model and Section~\\ref{sec:ident} the identification boundary. "
    "Section~\\ref{sec:resources} turns memory resolution into executed quantity, capital and money for a known pair, and "
    "Section~\\ref{sec:mixtures} treats unknown mixtures, general memory and passive data. Section~\\ref{sec:disclosure} "
    "states what disclosure buys and when it changes a supervisor's decision, and tests it on the CFTC's mandated "
    "trader-class reports and on Binance's class ratios. Section~\\ref{sec:policy} draws the implications for "
    "supervision and Section~\\ref{sec:conclusion} concludes. ")
if ARGS.ssrn:
    _outline += ("The online supplement contains the proofs, the extended literature review, further results and robustness "
                 "checks, the hypothetical dollar illustration, a finite-horizon decision example, the spectral blind spot, the "
                 "measurement of reduced-form feedback and the reproducibility map.\n\n")
else:
    _outline += ("Proofs are in Appendix~\\ref{app:proofs}; the internet appendix contains account-level capital, near-colliding "
                 "rates, robustness to learning rules, the spectral blind spot and the measurement of reduced-form feedback, and "
                 "Appendix~\\ref{app:repro} maps every number to its source.\n\n")
core = core[:o1] + _outline + core[o2:]
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
if ARGS.ssrn:
    # The full source map moves to the public repository (REPRODUCIBILITY_MAP.md and a PDF of the same table);
    # the preprint keeps a short pointer section with the same label.
    r0 = core.index("\\section{Reproducibility: source of every number}")
    block = core[r0:].replace("\\end{document}", "").rstrip()
    preamble = core[:core.index("\\begin{document}")]
    standalone = (preamble + "\\begin{document}\n\\begin{center}\\large Reproducibility map for ``What Prices Reveal About "
                  "Hidden Trader Populations, and What Identifying Them Costs''\\end{center}\n"
                  + block.replace("\\section{Reproducibility: source of every number}\\label{app:repro}",
                                  "\\section*{Source of every number}") + "\n\\end{document}\n")
    core = core[:r0] + ("\\section{Reproducibility}\\label{app:repro}\n"
        "Every table, figure and number in this paper is mapped to the notebook or script and the result file that "
        "produce it in the reproducibility map, \\path{ceiling_suite/papers/paper1/REPRODUCIBILITY_MAP.md} "
        "(also as \\texttt{paper1\\_reproducibility\\_map.pdf}) in the public repository "
        "\\url{https://github.com/Pratikn03/Fianince}, release tag \\texttt{paper1-ssrn-v1}. The map also lists the "
        "replication notebooks in run order and the specification files of the pre-specified tests.\n")
out = core.rstrip() + "\n\n\\end{document}\n"
if not ARGS.ssrn:
    for word in ("Niroula", "Pratik", "Prashant", "Mankato", "Tribhuvan", "mnsu", "Pratikn03", "fianince"):
        assert word.lower() not in out.lower().replace("niroula2026b", ""), f"identifying text left: {word}"
elif ARGS.solo:
    assert "Prashant" not in out.split("\\begin{abstract}")[0], "second author still on the title page"
(HERE / f"{NAME}.tex").write_text(out)
for _ in range(2):
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{NAME}.tex"], cwd=HERE,
                   check=True, stdout=subprocess.DEVNULL)
print(f"built {NAME}.pdf")
if ARGS.ssrn:
    # Split the combined preprint into the journal's two files: main paper and online supplement.
    import pypdf
    rd = pypdf.PdfReader(str(HERE / f"{NAME}.pdf"))
    k = next(i for i, pg in enumerate(rd.pages) if "The supplement contains the proofs" in (pg.extract_text() or ""))
    for name, rng in (("paper1_main", range(0, k)), ("paper1_online_supplement", range(k, len(rd.pages)))):
        w = pypdf.PdfWriter()
        for i in rng:
            w.add_page(rd.pages[i])
        w.write(str(HERE / f"{name}.pdf"))
    print(f"split: main {k} pages, supplement {len(rd.pages) - k} pages")
if ARGS.ssrn:
    # Resolve cross-references to the preprint's numbering, then build the map as PDF and Markdown.
    labels = dict(re.findall(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", (HERE / f"{NAME}.aux").read_text()))
    standalone = re.sub(r"\\ref\{([^}]*)\}", lambda m: labels.get(m.group(1), "??"), standalone)
    (HERE / "paper1_reproducibility_map.tex").write_text(standalone)
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "paper1_reproducibility_map.tex"], cwd=HERE,
                       stdout=subprocess.DEVNULL)
    subprocess.run(["pandoc", "paper1_reproducibility_map.tex", "-o", "REPRODUCIBILITY_MAP.md", "-t", "gfm"], cwd=HERE,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("built paper1_reproducibility_map.pdf and REPRODUCIBILITY_MAP.md; unresolved refs:", standalone.count("??"))
if ARGS.ssrn and supp_blocks:
    # Resolve the supplement's references to the preprint, then rebuild it.
    labels = dict(re.findall(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", (HERE / f"{NAME}.aux").read_text()))
    t = (HERE / f"{SUPP}.tex").read_text()
    t = re.sub(r"\\eqref\{([^}]*)\}", lambda m: "(" + labels[m.group(1)] + ")" if m.group(1) in labels and m.group(1) not in supp_labels else m.group(0), t)
    t = re.sub(r"\\ref\{([^}]*)\}", lambda m: labels[m.group(1)] if m.group(1) in labels and m.group(1) not in supp_labels else m.group(0), t)
    (HERE / f"{SUPP}.tex").write_text(t)
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{SUPP}.tex"], cwd=HERE, stdout=subprocess.DEVNULL)
    print("built", SUPP + ".pdf")
