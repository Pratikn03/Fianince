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

# Theory version (Journal of Economic Dynamics and Control): same theorems, the two empirical tests moved to the
# supplement, a calibration of the barrier added. Built from note_main.tex by the replacements below, so that the
# note stays the single source. Compile paper1_theory.tex; split with
# python3 split_note.py paper1_theory.pdf Paper1_theory_main.pdf Paper1_theory_supplement.pdf
ABS_THEORY = ("Algorithmic traders read prices and, by trading, move them. One object, the feedback kernel, is a sufficient "
    "statistic for such a market: for any insider strategy and causal dealer rule, trader populations with the same "
    "kernel produce the same prices, order flows, profits and equilibria, and prices identify nothing finer. Learning "
    "the composition of the population costs data of order $(\\Delta\\eta)^{-(4K-2)}$ for $K$ groups whose memories "
    "lie within $\\Delta\\eta$, by probing or by waiting. At illustrative parameters, two-group populations with "
    "memories within $0.1$ need more than 15{,}000 years of daily prices to be told apart, even one millionth below "
    "instability. Market-wide supervision therefore needs only the kernel; targeted supervision needs flow tagged by "
    "class. With position limits, calm prices reveal the kernel and nothing more. Core results are machine-checked "
    "in Lean~4.")
CAL = r"""
\paragraph{How large is the barrier?} Table~\ref{n:tab_cal} puts numbers on part~(iii). Two populations of two groups each, with memory rates within $0.1$ of $0.5$, cannot be told apart with both error probabilities at $5\%$ from less than $20{,}000$ years of daily prices; one millionth below instability the bound is still $16{,}000$ years, and with five-minute prices around the clock it is $37$ years. With three groups the daily figure is about $10^8$ years. The numbers bound every test, for the passive record; probing faces the same order (part~(i)). The illustrative parameters move the constant, not the exponent.

\begin{table}[t]
\centering
\caption{Years of price data below which no test tells the two populations of Theorem~\ref{n:cost}(i) apart with both error probabilities at $5\%$.}
\label{n:tab_cal}
\begin{tabular}{ccrrr}
\toprule
$K$ & $\Delta\eta$ & daily, $1-S=0.1$ & daily, $1-S=10^{-6}$ & five-minute, $1-S=10^{-6}$\\
\midrule
2 & 0.2 & 350 & 270 & 0.66\\
2 & 0.1 & 20{,}000 & 16{,}000 & 37\\
2 & 0.05 & $1.2\times10^{6}$ & $9.0\times10^{5}$ & 2{,}200\\
3 & 0.2 & $1.4\times10^{5}$ & $9.4\times10^{4}$ & 220\\
3 & 0.1 & $1.5\times10^{8}$ & $9.9\times10^{7}$ & $2.4\times10^{5}$\\
3 & 0.05 & $1.5\times10^{11}$ & $9.6\times10^{10}$ & $2.3\times10^{8}$\\
\bottomrule
\end{tabular}
\par\smallskip
\parbox{\textwidth}{\footnotesize Bound: $n\ge\ln 5/\mathrm{KL}$ observations (Bretagnolle--Huber), with KL the Gaussian information per observation, computed as in Figure~\ref{n:fig_barrier} (centre memory rate $0.5$, total weight $0.3$, impact $0.5$, common feedback budget $S$). Daily: 252 observations a year; five-minute: 105{,}120 a year in a 24-hour market. Two significant digits. Script: \nolinkurl{research_extension/fragility_reveals/calibration_table.py}.}
\end{table}
"""
THEORY_EDITS = [
    (note[note.index("\\noindent Algorithmic traders"):note.index("\\end{abstract}")], "\\noindent " + ABS_THEORY + "\n"),
    ("is very expensive, even on the eve of a crash.",
     "is very expensive, even on the eve of a crash: at illustrative parameters, more than 15{,}000 years of daily prices for two populations of two groups each (Table~\\ref{n:tab_cal})."),
    ("prices then reveal how close the market is to breaking, not who is trading.",
     "prices then reveal how close the market is to breaking, not who is trading. Table~\\ref{n:tab_cal} gives the data this takes at illustrative parameters."),
    ("\\item \\emph{Evidence} (Section~\\ref{n:concl}). We report two pre-registered tests, each run once, with the wording fixed before the results were known.\n", ""),
    ("Figure~\\ref{n:fig_barrier} shows both statements.\n\n", "Figure~\\ref{n:fig_barrier} shows both statements.\n\n"),
    ("\\end{figure}\n\n\n\\section{Who needs composition", "\\end{figure}\n" + CAL + "\n\\section{Who needs composition"),
    (note[note.index("\\paragraph{Evidence.}"):note.index("The sufficiency results need aggregate")],
     "\\paragraph{Evidence.} The contribution is theoretical. Supplement Section~\\ref{sec:scope} reports two pre-registered tests on public data, on Taiwan's tagged exchange flows and on Binance perpetual futures, with their readouts as registered.\n\n"),
]
th = note
for old, new in THEORY_EDITS:
    assert th.count(old) == 1, old[:60]
    th = th.replace(old, new)
decl_th = decl.replace("\\paragraph{Use of AI tools.} See the AI-use disclosure on the title page.",
    "\\paragraph{Declaration of generative AI and AI-assisted technologies.} During the preparation of this work the authors "
    "used Claude, ChatGPT/Codex and Gemini for research development, code, numerical checks, Lean proofs, drafting and internal "
    "critique, as stated on the title page. After using these tools, the authors reviewed and edited the content as needed and "
    "take full responsibility for the content of the publication.")
assert decl_th != decl
theory = (pre + "\\begin{document}\n\\maketitle\n\\thispagestyle{empty}\\pagestyle{empty}\n\\begingroup\\onehalfspacing\n\n" + th + "\n" + decl_th + "\n" + bib + "\n"
          + head + front + full + rest + "\\end{document}\n")
open("paper1_theory.tex", "w", encoding="utf-8").write(theory)
print("written paper1_theory.tex; abstract words:", len(ABS_THEORY.split()))
