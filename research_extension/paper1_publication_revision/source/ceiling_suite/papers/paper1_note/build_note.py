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
EXTRABIB = r"""\bibitem[Blackwell(1953)]{blackwell1953} Blackwell, D. (1953). Equivalent comparisons of experiments. \emph{Annals of Mathematical Statistics} 24(2), 265--272.

\bibitem[Le~Cam(1964)]{lecam1964} Le~Cam, L. (1964). Sufficiency and approximate sufficiency. \emph{Annals of Mathematical Statistics} 35(4), 1419--1455.

\bibitem[van Waarde et~al.(2020)]{vanwaarde2020} van Waarde, H.~J., J. Eising, H.~L. Trentelman, and M.~K. Camlibel (2020). Data informativity: A new perspective on data-driven analysis and control. \emph{IEEE Transactions on Automatic Control} 65(11), 4753--4768.

"""
bib = bib.replace("\\end{thebibliography}", EXTRABIB + "\\end{thebibliography}")
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
         "Proposition~\\ref{n:nearcrit} to Proposition~\\ref{prop:nearcrit}; Proposition~\\ref{n:hiding} to Proposition~\\ref{prop:hiding}; Theorem~\\ref{n:partial} to Theorem~\\ref{thm:partial}; Theorem~\\ref{n:pool} to Theorem~\\ref{thm:pool}; Theorem~\\ref{n:track} to Theorem~\\ref{thm:track}; Theorem~\\ref{n:sat_thm} to Theorems~\\ref{thm:satsuff}, \\ref{thm:stress} and~\\ref{thm:satident}.\n\n")
rest = supp[j:]

# Leaner supplement: the note's main text gives the reading of each result, so the supplement drops the expository
# paragraphs below when they carry no label, environment or figure (statements, proofs and checks are kept).
DROP = ("In words.", "The model in words.", "What the exponential case adds.", "The analogy with aggregate demand.",
        "Relation to network identifiability.", "What the supervisor can and cannot learn.",
        "Existing runs and the remaining synthetic check.", "In executed quantity and money.", "The value of each tag.")
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
ABS_THEORY = ("Algorithmic traders read prices and, by trading, move them. One object, the feedback kernel, is a minimal "
    "sufficient statistic for such a market: populations with the same kernel produce the same prices, profits and "
    "equilibria, and prices identify nothing finer. Learning the composition of the population costs data of order "
    "$(\\Delta\\eta)^{-(4K-2)}$ for $K$ groups whose memories lie within $\\Delta\\eta$, even near instability: "
    "two-group populations with half-lives of 5 to 9 days need more than 4{,}000 years of daily prices to be told "
    "apart. Market-wide actions need only the kernel, and a broad class of market-wide questions is answered at the usual "
    "statistical rate whatever the number of groups, so the two costs separate without bound as memories converge. When the population drifts, composition can be tracked only below a speed "
    "limit. Two remedies follow. Tagging all but one memory class removes the barrier, and the last tag is worth "
    "nothing. Without any tags, pooling $D$ markets in which the same algorithms trade in different proportions "
    "lowers the exponent near generic configurations to $2(K-1+\\lceil K/D\\rceil)$, because an algorithm's memory is the same everywhere it "
    "trades. Core results are machine-checked in Lean~4.")
CAL = r"""
\paragraph{How large is the barrier?} Table~\ref{n:tab_cal} puts numbers on part~(iii) for two groups. What matters is the spread of memories relative to their size. Populations whose memories all have half-lives between 5 and 9 days cannot be told apart with both error probabilities at $5\%$ from less than $4{,}000$ years of daily prices, however close the market is to instability. When half-lives differ by a factor of three or more, a century of daily data can suffice. With three groups the numbers grow to the order of $10^8$ years. The numbers bound every test, for the passive record; probing faces the same order (part~(i)). The exponents do not depend on Gaussian noise: with real Bitcoin price noise injected into synthetic groups, the fitted slopes are $-6.01$ and $-9.81$, against $-6$ and $-10$ (Supplement Section~\ref{sec:injection}).

\begin{table}[t]
\centering
\caption{Years of daily price data below which no test tells the two populations of Theorem~\ref{n:cost}(i) apart with both error probabilities at $5\%$.}
\label{n:tab_cal}
\begin{tabular}{cccrr}
\toprule
& memory rates & half-lives (days) & $1-S=0.1$ & $1-S=10^{-6}$\\
\midrule
$K=2$ & $0.5\pm0.1$ & 0.8--1.4 & 20{,}000 & 16{,}000\\
& $0.5\pm0.05$ & 0.9--1.2 & $1.2\times10^{6}$ & $9.0\times10^{5}$\\
& $0.8\pm0.1$ & 1.9--6.6 & 100 & 69\\
& $0.8\pm0.05$ & 2.4--4.3 & 6{,}000 & 3{,}900\\
& $0.9\pm0.05$ & 4.3--13.5 & 120 & 77\\
& $0.9\pm0.025$ & 5.2--8.9 & 7{,}000 & 4{,}300\\
\midrule
$K=3$ & $0.5\pm0.1$ & 0.8--1.4 & $1.5\times10^{8}$ & $9.9\times10^{7}$\\
& $0.5\pm0.05$ & 0.9--1.2 & $1.5\times10^{11}$ & $9.6\times10^{10}$\\
\bottomrule
\end{tabular}
\par\smallskip
\parbox{\textwidth}{\footnotesize Bound: $n\ge\ln 5/\mathrm{KL}$ observations (Bretagnolle--Huber), with KL the Gaussian information per observation, computed as in Figure~\ref{n:fig_barrier}, at a common feedback budget $S$, impact $\kappa=0.5$ and feedback share $\kappa\sum_iq_i=0.3$ (total weight $0.6(1-r_c)$ at centre rate $r_c$). Memory rates are per day, 252 days a year; for traders whose memories are counted in five-minute periods, with prices recorded every five minutes around the clock, divide by $417$. Two significant digits. Script: \nolinkurl{research_extension/fragility_reveals/calibration_table.py}.}
\end{table}
"""
THEORY_EDITS = [
    ("with effective impact and persistence, and with the memory rates unchanged (Supplement Theorems~\\ref{thm:inventory} and~\\ref{thm:eqreduced}).",
     "with effective impact and persistence, and with the memory rates unchanged (Supplement Theorems~\\ref{thm:inventory} and~\\ref{thm:eqreduced}).\n\nTogether, Theorems~\\ref{n:suff} and~\\ref{n:ident} make the kernel a \\emph{minimal} sufficient statistic of the population for prices: it determines everything prices can show, and prices determine it. (The merged measure has finitely many atoms, so its moments, the kernel, determine it.)"),
    ("Reset probing is a benchmark for what data can reveal, not a proposed policy.",
     "Reset probing is a benchmark for what data can reveal, not a proposed policy. Knowing $(a,\\kappa)$ only helps the observer, so the lower bounds below hold a fortiori when $(a,\\kappa)$ must be estimated."),
    ("\\citet{auclert2024} make the corresponding sufficient-statistic argument",
     "A large literature models markets with heterogeneous fundamentalist and chartist traders \\citep{brock1998,hommes2006} and estimates their shares from prices \\citep{boswijk2007,franke2012,lux2018}; our results say which features of a population such estimates can recover from prices, and at what cost, when demand is linear in past prices. \\citet{auclert2024} make the corresponding sufficient-statistic argument"),
    ("This is Supplement Proposition~\\ref{prop:nearcrit}, new to this version.", "This is Supplement Proposition~\\ref{prop:nearcrit}."),
    ("Part~(ii) is Supplement Proposition~\\ref{prop:targetK}, which is new to this version; its pair", "Part~(ii) is Supplement Proposition~\\ref{prop:targetK}; its pair"),
    (note[note.index("\\noindent\\textbf{Relation to other versions.}"):note.index("\\noindent\\textbf{Keywords:}")],
     "\\noindent\\textbf{Supplement.} The online supplement states every result in full, with proofs and machine-check details.\n\n"),
    (note[note.index("\\noindent Algorithmic traders"):note.index("\\end{abstract}")], "\\noindent " + ABS_THEORY + "\n"),
    ("is very expensive, even on the eve of a crash.",
     "is very expensive, even on the eve of a crash: at illustrative parameters, more than 4{,}000 years of daily prices when the traders' memories have half-lives between 5 and 9 days (Table~\\ref{n:tab_cal})."),
    ("prices then reveal how close the market is to breaking, not who is trading.",
     "prices then reveal how close the market is to breaking, not who is trading. Table~\\ref{n:tab_cal} gives the data this takes at illustrative parameters."),
    ("\\item \\emph{Evidence} (Section~\\ref{n:concl}). We report two registered tests, each run once, with the wording fixed before the results were known.\n", ""),
    ("Figure~\\ref{n:fig_barrier} shows both statements.\n\n", "Figure~\\ref{n:fig_barrier} shows both statements.\n\n"),
    ("\\end{figure}\n\n\n\\section{Who needs composition", "\\end{figure}\n" + CAL + "\n\\section{Who needs composition"),
    (note[note.index("\\paragraph{Evidence.}"):note.index("The sufficiency results hold whenever")],
     "\\paragraph{Evidence.} The contribution is theoretical, and the tagged flows and position limits it concerns are "
     "rarely observed. Supplement Section~\\ref{sec:scope} reports two registered tests on public data, on Taiwan's "
     "tagged exchange flows and on Binance perpetual futures, with their readouts as registered.\n\n"),
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
NEWBIB = r"""\bibitem[Boswijk et~al.(2007)]{boswijk2007} Boswijk, H.~P., C.~H. Hommes, and S. Manzan (2007). Behavioral heterogeneity in stock prices. \emph{Journal of Economic Dynamics and Control} 31, 1938--1970.

\bibitem[Franke and Westerhoff(2012)]{franke2012} Franke, R., and F. Westerhoff (2012). Structural stochastic volatility in asset pricing dynamics: Estimation and model contest. \emph{Journal of Economic Dynamics and Control} 36, 1193--1211.

\bibitem[Hommes(2006)]{hommes2006} Hommes, C.~H. (2006). Heterogeneous agent models in economics and finance. In L. Tesfatsion and K.~L. Judd (eds.), \emph{Handbook of Computational Economics}, Vol.~2, 1109--1186. Elsevier.

\bibitem[Lux and Zwinkels(2018)]{lux2018} Lux, T., and R.~C.~J. Zwinkels (2018). Empirical validation of agent-based models. In C. Hommes and B. LeBaron (eds.), \emph{Handbook of Computational Economics}, Vol.~4, 437--488. Elsevier.

\bibitem[Niroula et~al.(2026a)]{niroula2026a} Niroula, P., P. Niroula, and S. Khatiwada (2026a). What prices cannot tell a market supervisor: The cost of identifying trader groups and the value of class disclosure. Working paper, 5 November 2026, \url{https://github.com/Pratikn03/Fianince}.

"""
theory = theory.replace("\\end{thebibliography}", NEWBIB + "\\end{thebibliography}", 1)
theory = theory.replace("\\bibitem[Niroula et~al.(2026)]{niroula2026b}", "\\bibitem[Niroula et~al.(2026b)]{niroula2026b}", 1)
theory = theory.replace("Niroula, S. Alkhushayni, Y. Chen, M. Bhavsar, and P. Niroula (2026).", "Niroula, S. Alkhushayni, Y. Chen, M. Bhavsar, and P. Niroula (2026b).", 1)
for a, b in (("(full working paper, internet appendix)", "(\\citealp{niroula2026a}, internet appendix)"), ("(full working paper)", "\\citep{niroula2026a}"), ("The full working paper", "\\citet{niroula2026a}"),
             ("the full working paper", "\\citet{niroula2026a}"),
             ("reproduce Sections~2--8 of the longer core version of this paper (12 November 2026): every result in full, with the remarks, machine-check notes and the results that the note omits.",
              "state every result in full, with the remarks, machine-check notes and the results that the main text omits."),
             ("Theorem numbers in the supplement are those of these sections, not of the note. The note's results correspond", "Theorem numbers in the supplement are those of these sections, not of the main text. The main text's results correspond")):
    theory = theory.replace(a, b)
for a, b in (("\\citet{niroula2026a} reports", "\\citet{niroula2026a} report"), ("\\citet{niroula2026a} proves", "\\citet{niroula2026a} prove"),
             ("\\citet{niroula2026a} matches", "\\citet{niroula2026a} match")):
    theory = theory.replace(a, b)
# P1T readout amendment R1 (12 November 2026, authors' decision): in this version the Taiwan test is reported in
# Supplement S7 only, not in the abstract or the main text.
assert "Taiwan" not in ABS_THEORY
assert "full working paper" not in theory and "core version" not in theory.split("\\begin{document}")[1], "version clutter left"
open("paper1_theory.tex", "w", encoding="utf-8").write(theory)
print("written paper1_theory.tex; abstract words:", len(ABS_THEORY.split()))

# Focused version and companion (13 November 2026). The focused version is the theory version with the results on
# cascades, insiders and nonlinear or learning traders moved to a companion note; cross-references between the two
# resolve through xr-hyper. Compile order: paper1_focus, paper1b_companion, paper1_focus, paper1b_companion,
# paper1_focus. The theory version above stays the complete record.
MOVE = {"After a breach": ["The cascade after a breach", "Forward-looking dealers after a breach", "How a cascade unfolds"],
        "Insiders": ["A long-lived insider", "An insider against a strategic group"],
        "Nonlinear and learning traders": ["Traders with a dead band", "Saturation of every order", "A rate for noisy stress identification",
                                           "A rate under hard limits", "The cost of composition when traders are nonlinear", "Traders who learn"]}
KEEP = ["The moment gap of the hard pair", "The largest weights of the hard pair"]
i = theory.index("\\section{Questions left open in earlier versions}"); j = theory.index("\\section{", i + 10)
sec = theory[i:j]
cuts = [m.start() for m in re.finditer(r"\\subsection\{", sec)] + [len(sec)]
subs = {re.match(r"\\subsection\{([^\n]*)\}", sec[a:]).group(1).split("}")[0]: sec[a:b] for a, b in zip(cuts, cuts[1:])}
assert set(subs) == set(KEEP) | {t for v in MOVE.values() for t in v}, set(subs) ^ (set(KEEP) | {t for v in MOVE.values() for t in v})
newsec = ("\\section{The hard pair: moment gap and largest weights}\\label{app:openres}\n\nThis section gives the exact size of the moment gap "
          "behind the constants of Theorem~\\ref{thm:kcohort} and compares the largest weights of the hard pair for every $K$.\n\n" + "".join(subs[t] for t in KEEP))
focus = theory[:i] + newsec + theory[j:]
i = focus.index("\\section{Robustness to nonlinear and adaptive trading rules}"); j = focus.index("\\section{", i + 10)
sims = focus[i:j]; focus = focus[:i] + focus[j:]
comp_body = "".join("\\section{" + k + "}\n\n" + "".join(subs[t] for t in v) for k, v in MOVE.items()) + sims
moved = set(re.findall(r"\\label\{([^}]*)\}", comp_body))
KIND = r"(?:Theorems?|Propositions?|Corollar(?:y|ies)|Lemmas?|Sections?)"
GROUP = re.compile(r"(Supplement )?(" + KIND + r")((?:(?:~|,\s*|\s+and~|,\s+and~)\\ref\{[^}]*\}(?:\([ivx]+\))?)+)")
def reword(text, is_moved, word, report):
    def f(m):
        labs = re.findall(r"\\ref\{([^}]*)\}", m.group(3))
        hit = [is_moved(l) for l in labs]
        if all(hit): return word + m.group(2) + m.group(3)
        if any(hit): report.append(m.group(0))
        return m.group(0)
    return GROUP.sub(f, text)
mixed = []
focus = reword(focus, lambda l: l in moved, "Companion ", mixed)
for a, b in (("Supplement Theorem~\\ref{thm:cascade} and Propositions~\\ref{prop:reecascade} and~\\ref{prop:cascadedyn}",
              "Companion Theorem~\\ref{thm:cascade} and Propositions~\\ref{prop:reecascade} and~\\ref{prop:cascadedyn}"),):
    if a in focus: focus = focus.replace(a, b); mixed = [x for x in mixed if x not in a]
print("focus: mixed reference groups left for manual wording:", mixed)
focus = focus.replace("\\usepackage[colorlinks=true", "\\usepackage{xr-hyper}\n\\usepackage[colorlinks=true", 1)
focus = focus.replace("\\begin{document}", "\\externaldocument{paper1b_companion}\n\\begin{document}", 1)
focus = focus.replace("\\noindent\\textbf{Supplement.} The online supplement states every result in full, with proofs and machine-check details.",
    "\\noindent\\textbf{Supplement and companion.} The online supplement states every result in full, with proofs and machine-check details. "
    "Results on cascades after a breach, insiders, and nonlinear or learning traders are in a companion note \\citep{niroula2026c}; "
    "references of the form C1.1 are to it.")
CBIB = ("\\bibitem[Niroula et~al.(2026c)]{niroula2026c} Niroula, P., P. Niroula, and S. Khatiwada (2026c). After a breach, and beyond linear rules: "
        "Companion results to ``Observationally equivalent algorithms''. Working paper, 13 November 2026, \\url{https://github.com/Pratikn03/Fianince}.\n\n")
focus = focus.replace("\\end{thebibliography}", CBIB + "\\end{thebibliography}", 1)
assert "niroula2026c" in focus.split("\\begin{thebibliography}")[0]
_fb = focus[focus.index("\\begin{thebibliography}"):focus.index("\\end{thebibliography}")]
_it = re.split(r"\n(?=\\bibitem)", _fb)
_txt = focus.replace(_fb, "")
_c = set(k.strip() for g in re.findall(r"\\cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", _txt) for k in g.split(","))
_kept = [x for x in _it[1:] if re.search(r"\]\{([^}]*)\}", x).group(1) in _c]
print("focus bibliography:", len(_it) - 1, "->", len(_kept), "entries")
focus = focus.replace(_fb, _it[0] + "\n" + "\n".join(_kept) + "\n")
focus = focus.replace("\\date{12 November 2026}", "\\date{13 November 2026}")
open("paper1_focus.tex", "w", encoding="utf-8").write(focus)

cpre = pre.replace("\\title{Observationally Equivalent Algorithms:\\\\ What Prices Reveal About Trader Populations,\\\\ and What Supervisors Need}",
                   "\\title{After a Breach, and Beyond Linear Rules:\\\\ Companion Results to\\\\ ``Observationally Equivalent Algorithms''}")
assert cpre != pre
cpre = cpre.replace("\\date{12 November 2026}", "\\date{13 November 2026}")
cpre = cpre.replace("\\fancyhead[R]{\\small Observationally Equivalent Algorithms}", "\\fancyhead[R]{\\small After a Breach, and Beyond Linear Rules}")
cpre = cpre.replace("\\usepackage[colorlinks=true", "\\usepackage{xr-hyper}\n\\usepackage[colorlinks=true", 1)
back = []
comp_body = reword(comp_body, lambda l: l not in moved and not l.startswith("fig") and not l.startswith("tab"), "main-paper ", back)
comp_body = comp_body.replace("main-paper Supplement ", "main-paper ").replace("main-paper Sections", "main-paper Sections")
CABS = ("\\begin{abstract}\n\\noindent This note collects results that extend ``Observationally Equivalent Algorithms'' \\citep{niroula2026m} beyond its "
        "linear model and beyond calm markets. After a position limit is breached, a cascade occurs exactly where the liquidation triggered per unit of "
        "price move exceeds one; forward-looking dealers make every fixed point an equilibrium, and slow-moving capital makes the fall overshoot and lowers "
        "the threshold. A long-lived insider cannot manipulate a stable market, and a group that chooses its rule against her becomes a momentum trader "
        "whose choice is still summarized by the kernel. For traders with dead bands or smooth or hard position limits, large probes identify the "
        "population at the parametric rate, and nonlinearity lowers the cost of learning composition only when it separates the groups. "
        "Several steps are machine-checked in Lean~4; the main paper's supplement lists them.\n\\end{abstract}\n\n"
        "\\noindent\\textbf{AI-use disclosure.} Claude, ChatGPT/Codex and Gemini provided material assistance with research development, code, numerical "
        "checks, Lean proofs, manuscript drafting and internal critique. Human authors remain responsible for the content. AI checks do not constitute "
        "independent review.\n\n"
        "\\noindent\\textbf{Numbering.} Results here are numbered C1.1, C1.2, and so on. Numbers of the form 3.1 refer to the main text of the main paper, "
        "and numbers of the form S4.1 to its online supplement. Code and proofs: \\url{https://github.com/Pratikn03/Fianince}.\n\n")
MBIB = ("\\bibitem[Niroula et~al.(2026d)]{niroula2026m} Niroula, P., P. Niroula, and S. Khatiwada (2026d). Observationally equivalent algorithms: What prices "
        "reveal about trader populations, and what supervisors need. Working paper, 13 November 2026, \\url{https://github.com/Pratikn03/Fianince}.\n\n")
cb = theory[theory.index("\\begin{thebibliography}"):theory.index("\\end{thebibliography}")]
items = re.split(r"\n(?=\\bibitem)", cb); bhead = items[0]
cited = set(k.strip() for g in re.findall(r"\\cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", comp_body + CABS) for k in g.split(","))
keepb = [it for it in items[1:] if re.search(r"\]\{([^}]*)\}", it).group(1) in cited]
cbib = bhead + "\n" + MBIB + "\n".join(keepb) + "\n\\end{thebibliography}\n"
missing = cited - {"niroula2026m"} - {re.search(r"\]\{([^}]*)\}", it).group(1) for it in keepb}
assert not missing, missing
comp = (cpre + "\\externaldocument{paper1_focus}\n\\begin{document}\n\\maketitle\n" + CABS + "\\renewcommand{\\thesection}{C\\arabic{section}}\n"
        + comp_body + "\n" + cbib + "\\end{document}\n")
open("paper1b_companion.tex", "w", encoding="utf-8").write(comp)
print("written paper1_focus.tex and paper1b_companion.tex; moved labels:", len(moved), "; cited keys in companion:", len(cited))
