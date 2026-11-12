"""Builds paper1_note.tex: the short main text (note_main.tex) followed by an online supplement made of the core
version's main-text sections 2-8 (full statements, unchanged labels) and the core version's supplement.
Run build_core.py in ../paper1_core first."""
import re
core = open("../paper1_core/paper1_core.tex", encoding="utf-8").read()
pre = core[:core.index("\\begin{document}")]
pre = pre.replace("\\begin{document}", "") + "\\graphicspath{{../paper1_core/}}\n"
pre = pre.replace("\\date{Working paper, core version: 12 November 2026}", "\\date{12 November 2026}")
pre = pre.replace("\\title{A Sufficient Statistic for Algorithmic Feedback:\\\\ What Prices Reveal About Trader Groups, and Who Needs the Rest}",
                  "\\title{Observationally Equivalent Algorithms:\\\\ What Prices Reveal About Trader Populations,\\\\ and What Supervisors Need}")
pre = pre.replace("\\fancyhead[R]{\\small A Sufficient Statistic for Algorithmic Feedback}", "\\fancyhead[R]{\\small Observationally Equivalent Algorithms}")
main_core = core[core.index("\\begin{document}"):core.index("\\appendix")]
bib = main_core[main_core.index("\\begin{thebibliography}"):main_core.index("\\end{thebibliography}") + len("\\end{thebibliography}")]
full = main_core[main_core.index("\\section{Model and motivating examples}"):main_core.index("\\section{Conclusion}")]
supp = core[core.index("\\appendix"):core.index("\\end{document}")]
# core supplement front matter -> note supplement front matter
i = supp.index("\\begin{center}{\\Large Online Supplement}"); j = supp.index("\n\n", supp.index("\\noindent The supplement contains", i))
head = supp[:i]
front = ("\\begin{center}{\\Large Online Supplement}\\\\[4pt]{\\large Observationally Equivalent Algorithms}\\\\[2pt]"
         "{\\normalsize Niroula, Niroula and Khatiwada, 12 November 2026}\\end{center}\n\n"
         "\\noindent Sections~S1--S7 reproduce Sections~2--8 of the longer core version of this paper (12 November 2026): "
         "every result in full, with the remarks, machine-check notes and the results that the note omits. "
         "The remaining sections give the proofs, further results, machine checks and notation. "
         "Theorem numbers in the supplement are those of these sections, not of the note. "
         "The note's results correspond to them as follows: Theorem~\\ref{n:suff} to Theorem~\\ref{thm:eqinv} and Proposition~\\ref{prop:anylinear}; "
         "Theorem~\\ref{n:ident} to Theorem~\\ref{thm:merged}(i); Theorem~\\ref{n:cost} to Theorems~\\ref{thm:kcohort}, \\ref{prop:esprit} and~\\ref{prop:passive}; "
         "Proposition~\\ref{n:target} to Propositions~\\ref{prop:target}(i) and~\\ref{prop:targetK}; Theorem~\\ref{n:disc} to Theorem~\\ref{thm:discvalue}; "
         "Proposition~\\ref{n:nearcrit} to Proposition~\\ref{prop:nearcrit}; Proposition~\\ref{n:hiding} to Proposition~\\ref{prop:hiding}; Theorem~\\ref{n:sat_thm} to Theorems~\\ref{thm:satsuff}, \\ref{thm:stress} and~\\ref{thm:satident}.\n\n")
rest = supp[j:]

# Leaner supplement: the note's main text gives the reading of each result, so the supplement drops the expository
# paragraphs below when they carry no label, environment or figure (statements, proofs and checks are kept).
DROP = ("In words.", "The model in words.", "What the exponential case adds.", "The analogy with aggregate demand.",
        "Relation to network identifiability.")
def _lean(t):
    def keep(m):
        b = m.group(0)
        return b if ("\\label" in b or "\\begin{" in b or "\\ref{fig" in b) else ""
    pat = r"\\paragraph\{(?:" + "|".join(re.escape(d) for d in DROP) + r")\}(?:(?!\n\n).)*\n\n"
    return re.sub(pat, keep, t, flags=re.S)
_n0 = len(full) + len(rest)
full, rest = _lean(full), _lean(rest)
print("supplement text cut by", _n0 - len(full) - len(rest), "characters")
note = open("note_main.tex", encoding="utf-8").read()
decl = open("../paper1_core/src/declarations.tex", encoding="utf-8").read()
body = (pre + "\\begin{document}\n\\maketitle\n\\thispagestyle{empty}\\pagestyle{empty}\n\\begingroup\\onehalfspacing\n\n" + note + "\n" + decl + "\n" + bib + "\n"
        + head + front + full + rest + "\\end{document}\n")
open("paper1_note.tex", "w", encoding="utf-8").write(body)
print("written paper1_note.tex", len(body.splitlines()), "lines")

# Submission build (Review of Financial Studies: abstract of at most 100 words, double-spaced manuscript).
# Same text; only the main-text spacing changes. Compile paper1_note_submission.tex and split with
# python3 split_note.py paper1_note_submission.pdf Paper1_note_submission_main.pdf Paper1_note_submission_supplement.pdf
sub = body.replace("\\onehalfspacing\n\\emergencystretch", "\\doublespacing\n\\emergencystretch", 1).replace("\\begingroup\\onehalfspacing", "\\begingroup\\doublespacing")
assert sub != body
open("paper1_note_submission.tex", "w", encoding="utf-8").write(sub)
print("written paper1_note_submission.tex")
