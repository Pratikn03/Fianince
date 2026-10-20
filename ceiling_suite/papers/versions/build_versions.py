"""Build journal-format versions from the working sources (run after every edit of the sources)."""
import re, subprocess, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
PAPERS_DIR = os.path.dirname(HERE)
P1, P2, OUT = os.path.join(PAPERS_DIR, "paper1"), os.path.join(PAPERS_DIR, "paper2"), HERE
def build(tex, name):
    open(os.path.join(OUT, name + ".tex"), "w").write(tex)
    for _ in range(3):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", name + ".tex"], cwd=OUT, capture_output=True)
    log = open(os.path.join(OUT, name + ".log"), errors="ignore").read()
    bad = re.findall(r"(Overfull \\hbox \([0-9.]+pt|LaTeX Warning: (?:Reference|Citation)[^\n]*|! [^\n]*)", log)
    pages = re.search(r"Output written on .*?\((\d+) pages", log)
    return int(pages.group(1)) if pages else None, bad[:6]
for d in ("figs",):
    for src in (P1, P2):
        if os.path.isdir(os.path.join(src, d)):
            os.makedirs(os.path.join(OUT, d), exist_ok=True)
            for f in os.listdir(os.path.join(src, d)):
                shutil.copy(os.path.join(src, d, f), os.path.join(OUT, d, f))
rd = lambda p: open(p).read()

# ---------------- Paper 2, Journal of Finance format ----------------
front = rd(f"{P2}/p2_front.tex")
front = front.replace("\\usepackage[margin=1in]{geometry}", "\\usepackage[left=1in,right=1in,top=1.5in,bottom=1.5in]{geometry}")
front = front.replace("\\doublespacing", "\\onehalfspacing")
a = front.index("\\begin{abstract}"); b = front.index("\\end{abstract}")
JF_ABS = ("\\begin{abstract}\n\\noindent Eigenvalues and volatility do not bound the losses a stable market produces before it settles. "
          "We show that cumulative transient risk in a limit order book equals long-run impact divided by reversion net of momentum, "
          "that a pre-trade guard on this summed response is the largest safe admission rule without identifying traders, "
          "and that dealers under-supply reversion in equilibrium. The statistic forecasts next-hour adverse excursions beyond "
          "volatility forecasts in four pre-registered tests in thin Binance books and, more weakly, in thin US stocks; it is "
          "negligible on Bybit, and as a position limit it improves volatility limits only modestly.\n")
front = front[:a] + JF_ABS + front[b:]
front = front.replace("\\newpage\n\\setcounter{page}{1}\n\\tableofcontents\n\\newpage", "\\newpage\n\\setcounter{page}{1}")
app = rd(f"{P2}/p2_appendix.tex")
i_ia = app.index("\\section{Additional material}\\label{app:ia}")
app_main, app_ia = app[:i_ia], app[i_ia:]
app_ia = app_ia.replace("\\end{document}", "")
IA_HEAD = ("\\clearpage\n\\setcounter{page}{1}\\renewcommand{\\thepage}{IA-\\arabic{page}}\n"
           "\\begin{center}{\\Large Internet Appendix for ``From Human Markets to Machine Markets''}\\end{center}\n\\label{app:iastart}\n")
body = "".join(rd(f"{P2}/{f}") for f in ["p2_theory1.tex", "p2_theory2.tex", "p2_equil.tex", "p2_evidence.tex", "p2_thin.tex", "p2_close.tex"])
ia_extra = ""
MOVES = [
    ("\\subsection{Is $\\hat C_3$ just price impact?}\\label{sec:y8}",
     "\\subsection{Is $\\hat C_3$ just price impact?}\\label{sec:y8}\nBoth working terms contain the impact coefficient $\\kappa$. In a post-hoc check on the ten new symbols, reported in the Internet Appendix (Table~\\ref{tab:y8}), $\\hat C_3$ keeps about 80\\% of its gain in $R^2$ ($0.68$ of $0.85$ points, interval above zero) with four impact controls ($\\hat\\kappa$, $\\hat\\kappa^2$, Kyle's $\\lambda$ and the Amihud ratio), both terms survive separately, and impact alone forecasts nothing; with $\\hat\\kappa$ controlled, the gain in tail classification is no longer significant. The later tests include these controls in the baseline.\n\n",
     "\\section{Is $\\hat C_3$ just price impact?}"),
    ("\\subsection{A calibrated illustration}\\label{sec:calib}",
     "\\subsection{A calibrated illustration}\\label{sec:calib}\nAt the median BTCUSDT depth estimates, price impact is so persistent ($\\hat a\\approx0.97$ per minute) that the summed gain over 15 minutes is about 13 times the peak, so a guard calibrated to the peak would admit inventory about 13 times larger than is safe against a sustained flow of the declared size, even though this book does not amplify. The Internet Appendix gives the calculation (Figure~\\ref{fig:calib}, Table~\\ref{tab:calib}).\n\n",
     "\\section{A calibrated illustration}"),
    ("\\subsection{Tick size: a caution and a robustness check}\\label{sec:tick}",
     "\\subsection{Tick size}\\label{sec:tick}\nTick-size changes, a difference-in-differences design around them, and post-hoc tick-size robustness checks of Table~\\ref{tab:x6} are reported in the Internet Appendix (Table~\\ref{tab:x6r}): the result survives controls for tick size, the removal of days traded at a non-training tick and the removal of any single symbol, and weakens when the six thin symbols that ever changed tick are dropped.\n\n",
     "\\section{Tick size: a caution and a robustness check}"),
    ("\\subsection{October 10, 2025}\\label{sec:oct10}",
     "\\subsection{October 10, 2025}\\label{sec:oct10}\nThe Internet Appendix describes what the statistics did on the largest liquidation day on record (Figure~\\ref{fig:oct10}). The summed response was elevated all day and above its previous-week 90th percentile in 16 of 18 thin symbols at the crash hour, but volatility was equally extreme by then, and the statistic did not rank which coins fell furthest; the episode is descriptive and supports no inference.\n\n",
     "\\section{October 10, 2025}"),
]
for head, pointer, ia_head in MOVES:
    i0 = body.index(head); i1 = body.index("\\subsection{", i0 + 10)
    blk = body[i0:i1]
    body = body[:i0] + pointer + body[i1:]
    ia_extra += blk.replace(head, ia_head)
_i0 = body.index("\\paragraph{Bybit with order-book depth.}"); _i1 = body.index("\\subsection{A regulated market: thin US stocks}")
ia_extra += "\\section{Bybit with order-book depth}\n" + body[_i0:_i1].replace("\\paragraph{Bybit with order-book depth.} ", "")
body = body[:_i0] + "\\paragraph{Bybit with order-book depth.} A second pre-registered Bybit test, with depth within 1\\% of the mid rebuilt from Bybit's order-book files and the full volatility baseline, kept six coins under its pre-registered inclusion rule. Its criterion is met ($\\hat C_3$ adds $0.033$ points of $R^2$, 95\\% interval $[0.019,0.053]$, Clark--West $t=5.73$), but the effect is about one eightieth of the Binance gain, tail classification does not improve, and only the momentum term helps. The Internet Appendix gives the design and the full results (Table~\\ref{tab:bybitob}). With trades alone the statistic has no content on Bybit, and with depth its content is detectable but too small to matter.\n\n" + body[_i1:]
body = body.replace("\\includegraphics[width=0.78\\textwidth]{figs/fig_forest.pdf}", "\\includegraphics[height=0.62\\textheight]{figs/fig_forest.pdf}")
tex2 = front + body + app_main + IA_HEAD + ia_extra + app_ia + "\n\\end{document}\n"
n2, bad2 = build(tex2, "Paper2_JF")
log = open(f"{OUT}/Paper2_JF.aux").read()
m = re.search(r"\\newlabel\{app:iastart\}\{\{[^}]*\}\{([^}]*)\}", log)
print("Paper2_JF pages:", n2, "| main ends before IA page label:", m.group(1) if m else None, bad2)

# ---------------- Paper 1, Quantitative Economics format ----------------
f1 = rd(f"{P1}/p1_front.tex")
f1 = re.sub(r"\\usepackage\[[^\]]*\]\{geometry\}", "\\\\usepackage[margin=1.25in]{geometry}", f1)
f1 = f1.replace("\\begin{document}", "\\usepackage{etoolbox}\\AtBeginEnvironment{tabular}{\\scriptsize}\\setlength{\\tabcolsep}{3pt}\\sloppy\n\\begin{document}", 1)
if "\\doublespacing" not in f1:
    f1 = f1.replace("\\begin{document}", "\\doublespacing\n\\begin{document}", 1)
a = f1.index("\\begin{abstract}"); b = f1.index("\\end{abstract}")
QE_ABS = ("\\begin{abstract}\n\\noindent When trading algorithms condition on recent prices, price formation is a closed-loop system. We ask what an "
          "outside observer can learn about the algorithms from market data, and at what cost. In a linear cohort model, prices identify "
          "only a merged rate--weight measure. Separating two memory rates $\\delta$ apart costs executed quantity of order $\\delta^{-2}$ and "
          "trading capital of order $\\delta^{-4}$, with explicit constants; separating $K$ unknown cohorts costs $(\\Delta\\eta)^{-(4K-2)}$ "
          "experiments, a rate attained by Prony's method; with general completely monotone memory the minimax accuracy is only of order "
          "$1/\\log N$. Class-tagged disclosure removes the barrier and reduces the sample requirement by a factor of order "
          "$(\\Delta\\eta)^{-(4K-4)}$. In data, trader-class positions published by Binance and, in a pre-registered test, by the CFTC for "
          "eight regulated futures markets pin down memories that prices leave unrestricted.\n")
f1 = f1[:a] + QE_ABS + f1[b:]
app1 = rd(f"{P1}/p1_appendix.tex")
i1 = app1.index("\\section{Internet appendix}\\label{app:ia}")
main1, supp1 = app1[:i1], app1[i1:].replace("\\end{document}", "")
SUP = ("\\clearpage\n\\setcounter{page}{1}\\renewcommand{\\thepage}{S-\\arabic{page}}\n"
       "\\begin{center}{\\Large Supplemental Appendix for ``Auditable Memory and Financial Identification Limits''}\\end{center}\n\\label{app:suppstart}\n")
body1 = "".join(rd(f"{P1}/{f}") for f in ["p1_ident.tex", "p1_account.tex", "p1_mixture.tex", "p1_disclosure.tex", "p1_empirics.tex"])
tex1 = f1 + body1 + main1 + SUP + supp1 + "\n\\end{document}\n"
n1, bad1 = build(tex1, "Paper1_QE")
aux = open(f"{OUT}/Paper1_QE.aux").read()
m = re.search(r"\\newlabel\{app:suppstart\}\{\{[^}]*\}\{([^}]*)\}", aux)
print("Paper1_QE pages:", n1, "| supplement starts at page label:", m.group(1) if m else None, bad1)
