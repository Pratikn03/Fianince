"""Build journal-format versions from the working sources (run after every edit of the sources)."""
import re, subprocess, os, shutil
_H = os.path.dirname(os.path.abspath(__file__))
P1, P2, OUT = os.path.join(_H, "..", "paper1"), os.path.join(_H, "..", "paper2"), _H
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
P2_BODY = ["p2_theory1.tex", "p2_t6.tex", "p2_infosafety.tex", "p2_guard.tex", "p2_disclosure.tex", "p2_equil.tex", "p2_evidence.tex", "p2_thin.tex", "p2_istests.tex", "p2_close.tex"]

# ---------------- Paper 2, Journal of Finance format ----------------
front = rd(f"{P2}/p2_front.tex")
front = front.replace("\\usepackage[margin=1in]{geometry}", "\\usepackage[left=1in,right=1in,top=1.5in,bottom=1.5in]{geometry}")
front = front.replace("\\doublespacing", "\\onehalfspacing")
a = front.index("\\begin{abstract}"); b = front.index("\\end{abstract}")
JF_ABS = ("\\begin{abstract}\n\\noindent " + 'Eigenvalues and volatility do not bound the losses a market produces before settling. We show that cumulative transient risk equals long-run impact divided by reversion net of momentum, that a pre-trade guard on this summed response is the largest safe admission rule for bounded shocks, and that certifying it is cheaper than identifying the traders: experiments certify it at the parametric rate, and the guard is minimax-optimal in lost capacity. In pre-registered tests the statistic forecasts adverse excursions beyond volatility in thin Binance books, including untouched days and symbols, more weakly in thin US stocks, not on Bybit or Coinbase; on untouched dates its spot gain is $15.2\\%$ of its perpetual gain and $2.2\\times$ larger in high-leverage hours; around three fee events zero fees lower impact by $18.3\\%$ while leaving reversion unchanged; and on a $\\$1\\text{M}$ $20\\times$ position the certified guard saves $\\$398$--$\\$2{,}557$/hr in $\\mathrm{ES}_{95}$ beyond a volatility cap.' + "\n")
front = front[:a] + JF_ABS + front[b:]
front = front.replace("\\newpage\n\\setcounter{page}{1}\n\\tableofcontents\n\\newpage", "\\newpage\n\\setcounter{page}{1}")
app = rd(f"{P2}/p2_appendix.tex")
i_ia = app.index("\\section{Additional material}\\label{app:ia}")
app_main, app_ia = app[:i_ia], app[i_ia:]
app_ia = app_ia.replace("\\end{document}", "")
IA_HEAD = ("\\clearpage\n\\setcounter{page}{1}\\renewcommand{\\thepage}{IA-\\arabic{page}}\n"
           "\\setcounter{section}{0}\\renewcommand{\\thesection}{IA.\\arabic{section}}\n" + "\\begin{center}{\\Large Internet Appendix for ``From Human Markets to Machine Markets''}\\end{center}\n\\label{app:iastart}\n")
body = "".join(rd(f"{P2}/{f}") for f in P2_BODY)
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
_c0 = body.index("\\subsection{Crash events}"); _c1 = body.index("\\section{Evidence from spot prices}")
ia_extra += "\\section{BTCUSDT crash events}" + body[_c0+len("\\subsection{Crash events}"):_c1]
body = body[:_c0] + "\\subsection{Crash events}\nOn three crash days with valid depth data (SVB, the 2024 yen carry unwind and the 2025 tariff shock), $\\hat C_3$ was elevated in the hours before the worst hour but stayed negative throughout (Internet Appendix, Table~\\ref{tab:d9} and Figure~\\ref{fig:events}); three events are not a test.\n\n" + body[_c1:]
_m0 = body.index("\\subsection{Multi-asset coupling}"); _m1 = body.index("\\section{When does a book amplify?")
ia_extra += "\\section{Multi-asset coupling}" + body[_m0+len("\\subsection{Multi-asset coupling}"):_m1]
body = body[:_m0] + "\\subsection{Multi-asset coupling}\nWith many instruments and a leader--satellite cross-impact structure, every power of the stacked operator is entrywise non-decreasing in the cross-impact, so directed coupling can only shrink the safe radius and raise the Kreiss constant (Internet Appendix, Proposition~\\ref{prop:multi}); symmetric coupling raises persistence without transient amplification.\n\n" + body[_m1:]
_i0 = body.index("\\paragraph{Bybit with order-book depth.}"); _i1 = body.index("\\subsection{A regulated market: thin US stocks}")
ia_extra += "\\section{Bybit with order-book depth}\n" + body[_i0:_i1].replace("\\paragraph{Bybit with order-book depth.} ", "")
body = body[:_i0] + "\\paragraph{Bybit with order-book depth.} A second pre-registered Bybit test, with depth within 1\\% of the mid rebuilt from Bybit's order-book files and the full volatility baseline, kept six coins under its pre-registered inclusion rule. Its criterion is met ($\\hat C_3$ adds $0.033$ points of $R^2$, 95\\% interval $[0.019,0.053]$, Clark--West $t=5.73$), but the effect is about one eightieth of the Binance gain, tail classification does not improve, and only the momentum term helps. The Internet Appendix gives the design and the full results (Table~\\ref{tab:bybitob}). With trades alone the statistic has no content on Bybit, and with depth its content is detectable but too small to matter.\n\n" + body[_i1:]

def mv(start, end, ia_title, pointer):
    global body, ia_extra
    i0 = body.index(start); i1 = body.index(end, i0 + len(start))
    blk = body[i0:i1]
    head_end = blk.index("\n") + 1
    ia_extra += "\\section{" + ia_title + "}" + blk[len(start):] if blk.startswith(start) else blk
    body = body[:i0] + pointer + body[i1:]
mv("\\subsection{Structural estimates}", "\\subsection{Pre-registered out-of-sample test}", "BTCUSDT structural estimates and local projections",
   "\\subsection{Structural estimates and local projections}\nDay-by-day fits of model \\eqref{eq:x}--\\eqref{eq:d} on one-minute bars (Internet Appendix, Table~\\ref{tab:d3}) put the market on the stable side of the condition: $\\hat C_3<0$ on 93.5\\% of training days and the median implied response peaks at impact. In the re-centred bands the depletion coefficient is small and negative, a sign that Section~\\ref{sec:fixedgrid} shows to be an artefact; the momentum term is about $0.008$ against $(1-a)\\kappa\\approx0.022$. Local projections with future flow, and then future depth, held fixed show no overshoot in any version (Figure~\\ref{fig:med}, Table~\\ref{tab:d4}).\n\n")
mv("\\section{Evidence from spot prices}", "\\section{Evidence from thinner books}", "Evidence from spot prices",
   "\\subsection{Spot prices}\nOn Binance BTCUSDT spot, a unit-free amplification statistic from one-second data is indistinguishable from one and from a no-feedback pipeline null on five crash days; overshoots disappear once future flow is held fixed, so they come from order splitting; and a pre-registered predictive test fails ($\\Delta R^2=-0.023$ points, interval $[-0.056,-0.002]$). The Internet Appendix reports the details (Section~\\ref{sec:spot}).\n\n")
mv("\\subsection{Overshoot and depletion}", "\\subsection{Depletion on a fixed price grid}", "Overshoot and depletion in Binance depth bands",
   "\\subsection{Overshoot and depletion}\nWith future flow held fixed there is no overshoot in any liquidity tercile, so the registered prediction of an overshoot in thin books fails (Internet Appendix, Table~\\ref{tab:x4}); in Binance's re-centred depth bands, taker flow appears to replenish the side it hits even at the 30-second snapshot scale (Table~\\ref{tab:x8}).\n\n")
mv("\\subsection{Out-of-sample replication on new symbols}\\label{sec:y6}", "\\subsection{Is $\\hat C_3$ just price impact?}", "Replication on new symbols",
   "\\subsection{Out-of-sample replication on new symbols}\\label{sec:y6}\nA second registered test on ten thin symbols never used before passes ($+0.85$ points of $R^2$, interval $[0.30,6.37]$; Internet Appendix, Table~\\ref{tab:y6}); the momentum and reversion terms each carry content, the depth term and a unit-free ratio do not.\n\n")
mv("\\subsection{A third test on fresh days}\\label{sec:z6}", "\\subsection{Beyond volatility forecasting}", "A third test on fresh days",
   "\\subsection{A third test on fresh days}\\label{sec:z6}\nOn fresh days, with impact in the baseline, $\\hat C_3$ adds $1.6$ points of $R^2$ (Internet Appendix, Table~\\ref{tab:z6}); two unit-free statistics, the gain multiple and the log half-life of reversion, each add about half a point; the reversion term carries most of the signal; and the depth-free statistic forecasts as well as the full one. The registered six-hour position-sizing backtest on the same days fails (Section~\\ref{sec:backtest}).\n\n")
mv("\\subsection{The cross-section of the amplification condition}", "\\subsection{Overshoot and depletion}", "The cross-section of the amplification condition",
   "\\subsection{The cross-section of the amplification condition}\nAcross the 30 perpetuals, mean $\\hat C_3$ is negative in every liquidity tercile; what changes with depth is the frequency of the amplifying regime, from 9.4\\% of symbol-days in the thick tercile to 16.1\\% in the thin one (Spearman $-0.59$ with log depth). Measured feedback is largest in the \\emph{deepest} books (Spearman $+0.70$), so feedback and amplification are different objects (Internet Appendix, Table~\\ref{tab:x3}).\n\n")
mv("\\subsection{Pre-registered out-of-sample test}", "\\subsection{Crash events}", "BTCUSDT pre-registered test",
   "\\subsection{Pre-registered out-of-sample test}\nA registered test (SHA-256 \\texttt{d95212187ae4\\ldots}, opened once) of whether six-hour $\\hat C_3$ forecasts the next hour's adverse excursion in BTCUSDT on 2025--2026 fails: it adds $0.018$ points of $R^2$ with an interval including zero, and a volatility flag classifies tail hours far better (Internet Appendix, Table~\\ref{tab:d8}).\n\n")
mv("\\subsection{The guard as a position limit}\\label{sec:backtest}", "\\subsection{A certified guard}", "The guard as a position limit",
   "\\subsection{The guard as a position limit}\\label{sec:backtest}\nA registered backtest sized positions as $c_s/R_t$ with $R_t$ a six-hour volatility limit scaled by the gain multiple. It fails: the scaled limit lowers tail loss per unit of position in 91\\% of bootstrap draws, but the interval includes zero, and limits built on the six-hour response alone are worse than volatility and than a static limit (Internet Appendix, Table~\\ref{tab:backtest}).\n\n")
_k0 = body.index("\\begin{table}[t]\\centering\\small\n\\begin{threeparttable}\n\\caption{Safe radius and Kreiss bounds")
_k1 = body.index("\\end{table}", _k0) + len("\\end{table}")
ia_extra += "\\section{Kreiss bounds at a fixed spectral radius}\n" + body[_k0:_k1] + "\n"
body = body[:_k0] + body[_k1:]
body = body.replace("Table~\\ref{tab:kreiss} illustrates the theorem", "Internet Appendix Table~\\ref{tab:kreiss} illustrates the theorem")
mv("\\subsection{A second venue: Bybit}\\label{sec:bybit}", "\\paragraph{Bybit with order-book depth.}", "Bybit with trades only",
   "\\subsection{A second venue: Bybit}\\label{sec:bybit}\nA registered test on Bybit USDT perpetuals of the same coins, with trades only, fails without ambiguity ($\\hat C_3^{\\rm flow}$ adds $-0.000$ points of $R^2$, interval $[-0.001,0.001]$). A post-hoc check rules out bid--ask bounce and points to sparse trading: 11\\% of Bybit minutes have no trade, against 0.1\\% on Binance (Internet Appendix).\n\n")
mv("\\subsection{A certified guard}\\label{sec:certguard}", "\\subsection{October 10, 2025}", "A certified guard",
   "\\subsection{A certified guard}\\label{sec:certguard}\nA second registered backtest certifies the operator once a day from the previous three days (SHA-256 \\texttt{b9a56af48c93\\ldots}). Scaling a volatility limit by the certified gain multiple lowers tail loss per unit of position by 2.4\\% (interval $[-5.1\\%,-0.04\\%]$), a narrow pass; limits built on the certified response alone are far worse than volatility. Used as a one-sided throttle, as Lemma~\\ref{thm:guard} uses it, the certified guard lowers tail loss on a static limit by 13\\% after the fact (Part 13), a result Part 15 confirms on untouched days (Section~\\ref{sec:p15}); on a volatility limit it adds nothing (Internet Appendix, Table~\\ref{tab:certguard}).\n\n")
mv("\\subsection{Balance-sheet solvency}", "\\section{The value of disclosure for safe trading}", "Balance-sheet solvency",
   "\\subsection{Balance-sheet solvency}\nThe Internet Appendix embeds the guard in a dealer's balance sheet with maintenance margin, hedging cost, worst-case passive fills and a safety reserve (Theorem~\\ref{thm:forward}), and states when an eigenvalue rule admits a level that this solvency certificate does not cover (Proposition~\\ref{prop:dominance}) and when re-optimizing learners reinforce the guard (Proposition~\\ref{prop:lucas}).\n\n")
# map of results (unreferenced full-page float) to the Internet Appendix
_mp0 = front.index("\\begin{table}[p]\\centering\\footnotesize\n\\begin{threeparttable}\n\\caption{Map of results}")
_mp1 = front.index("\\end{table}", _mp0) + len("\\end{table}")
ia_extra = "\\section{Map of results}\n" + front[_mp0:_mp1] + "\n" + ia_extra
front = front[:_mp0] + front[_mp1:]
body = body.replace("\\FloatBarrier\n\\section{Tests of the information-safety results}", "\\section{Tests of the information-safety results}", 1)
mv("\\subsection{When admission changes the dynamics}\\label{sec:venue}", "\\subsection{A calibrated illustration}", "When admission changes the dynamics",
   "\\subsection{When admission changes the dynamics}\\label{sec:venue}\nTheorem~\\ref{thm:robustguard} relies on risk rising with the admission level. When admitting a class also deepens the book and speeds reversion, low admission can bring mostly feedback and high admission mostly liquidity; the safe levels can then be two intervals, such as $[0,0.035]\\cup[0.386,1]$, and a rule that certifies the largest safe level and admits everything below it admits unsafe levels (Internet Appendix, Proposition~\\ref{prop:venue}). Without a closed form, interval branch and bound with outward rounding certifies the whole safe set: every level it classifies safe is safe for every economy in the certified box, every level it classifies unsafe is unsafe for one of them, and the largest safe level is bracketed (Internet Appendix, Theorem~\\ref{thm:venuebb}; test T13).\n\n")
mv("\\paragraph{Unknown noise covariance.}", "\\section{An identification-free pre-trade guard}", "Certification with unknown noise covariance",
   "\\paragraph{Unknown noise covariance.} If the noise in the taps of one experiment is correlated, the certificate of Theorem~\\ref{thm:certcost}(i) can undercover (75\\% at nominal 95\\% with autocorrelation $0.8$), while a $t$-certificate on the summed taps and a Hotelling region remain exact for any covariance; dependence across experiments breaks both (Internet Appendix, Proposition~\\ref{prop:hotelling}; test T11). Experiments can also be run sequentially with an anytime-valid certificate (Internet Appendix, Proposition~\\ref{prop:probe}).\n\n")
_s0 = body.index("\\begin{table}[!tbp]\\centering\\footnotesize\n\\begin{threeparttable}\n\\caption{Simulation tests of the information-safety results}")
_s1 = body.index("\\end{table}", _s0) + len("\\end{table}")
ia_extra += "\\section{Simulation tests of the information-safety results}\n" + body[_s0:_s1] + "\n"
body = body[:_s0] + body[_s1:]
body = body.replace("(Table~\\ref{tab:simtests})", "(Internet Appendix, Table~\\ref{tab:simtests})")
mv("\\subsection{Post-hoc checks on opened data (Part 18)}\\label{sec:p18}", "\\FloatBarrier", "Post-hoc checks on opened data (Part 18)",
   "\\subsection{Post-hoc checks on opened data (Part 18)}\\label{sec:p18}\nPost-hoc checks on samples already opened, an order-splitting placebo on the Binance samples of Parts 9 and 16 and three more guard controls (a certified peak-response guard, a participation cap and a margin-style rule) on Parts 15 and 16, are reported in the Internet Appendix.\n\n")
_f0 = body.index("\\begin{figure}[p]\\centering\n\\includegraphics[height=0.62\\textheight]{figs/fig_forest.pdf}") if "height=0.62" in body else body.index("\\begin{figure}[p]\\centering\n\\includegraphics[width=0.78\\textwidth]{figs/fig_forest.pdf}")
_f1 = body.index("\\end{figure}", _f0) + len("\\end{figure}")
ia_extra += "\\section{Every out-of-sample forecasting evaluation}\n" + body[_f0:_f1].replace("height=0.62\\textheight", "height=0.85\\textheight") + "\n"
body = body[:_f0] + body[_f1:]
body = body.replace("Figure~\\ref{fig:forest}", "Internet Appendix Figure~\\ref{fig:forest}")
app_main = app_main.replace("\\begin{thebibliography}{99}\\setlength{\\itemsep}{2pt}\\small", "\\begin{thebibliography}{99}\\setlength{\\itemsep}{0pt}\\small")
_q0 = body.index("\\begin{table}[!tbp]\\centering\\small\n\\begin{threeparttable}\n\\caption{Pre-registered test on a new venue (Part 17)")
_q1 = body.index("\\end{table}", _q0) + len("\\end{table}")
ia_extra += "\\section{Pre-registered test on a new venue (Part 17)}\n" + body[_q0:_q1] + "\n"
body = body[:_q0] + body[_q1:]
body = body.replace("The test fails (Table~\\ref{tab:p17}).", "The test fails (Internet Appendix, Table~\\ref{tab:p17}).")
body = body.replace("\\FloatBarrier\n", "")
_c0 = body.index("The endpoints in these examples are computed, not proved, in floating point.")
_c1 = body.index("The interval endpoints quoted in this paper are therefore results, not approximations.", _c0) + len("The interval endpoints quoted in this paper are therefore results, not approximations.")
ia_extra += "\\section{Certified window endpoints}\n" + body[_c0:_c1] + "\n"
body = body[:_c0] + "The interval endpoints quoted here are proved, not only computed: weak-duality polynomials verified in outward-rounded interval arithmetic enclose them to within $1.5\\times10^{-8}$ (Internet Appendix, Lemma~\\ref{lem:certnum}; test T10)." + body[_c1:]
# hardening additions (Oct 2026): long proofs and remarks of the main text to the Internet Appendix
def mvblk(start, end_marker, ia_title, pointer, include_end=True):
    global body, ia_extra
    i0 = body.index(start); i1 = body.index(end_marker, i0) + (len(end_marker) if include_end else 0)
    ia_extra += "\\section{" + ia_title + "}\n" + body[i0:i1] + "\n"
    body = body[:i0] + pointer + body[i1:]
_pk = body.index("\\begin{proof}", body.index("\\label{thm:peak}"))
mvblk(body[_pk:_pk + 40], "\\end{proof}", "Proof of Theorem~\\ref{thm:peak}", "The proof is in the Internet Appendix.\n")
mvblk("The spectral reason is visible in the first example.", "until lag 60.", "Why the one-period condition fails: a negative residue",
      "The reason is spectral: depth depletion can put a negative residue on an intermediate mode, so the response first dips and then rises (Internet Appendix).")
mvblk("\\begin{remark}[Shorter windows cost more experiments]", "\\end{remark}", "Shorter windows cost more experiments", "")
_pe = body.index("\\begin{proof}", body.index("\\label{prop:equil}"))
mvblk(body[_pe:_pe + 40], "\\end{proof}", "Proof of Proposition~\\ref{prop:equil}", "The proof is in the Internet Appendix.\n")
mvblk("Part (v) quantifies this.", "(Table~\\ref{tab:discsim}).", "Noisy proxies: simulation of Theorem~\\ref{thm:disclosure}(v)",
      "The Internet Appendix quantifies part (v): intersecting the two certificates admits nearly as much as the better one at every memory rate (test T15).")
mvblk("\\begin{figure}[t]\\centering\n\\includegraphics[width=0.6\\textwidth]{figs/fig_t6.pdf}", "\\end{figure}", "Illustrative impulse responses of the book model", "")
body = body.replace("Figure~\\ref{fig:t6} illustrates the four cases.", "Internet Appendix Figure~\\ref{fig:t6} illustrates the four cases.")
mvblk("\\begin{remark}[Counterexamples to an exact one-period condition]", "\\end{remark}", "Counterexamples to an exact one-period condition",
      "Two explicit counterexamples, one with all channels reinforcing and $C_3=-0.00024$ but a peak of $1.092\\kappa$ at lag 60, are in the Internet Appendix (Remark~\\ref{rem:counter}). ")
# proofs and notation to the Internet Appendix
_p0 = app_main.index("\\section{Proofs}\\label{app:proofs}")
ia_extra = app_main[_p0:] + ia_extra
app_main = app_main[:_p0]
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
          "trading capital of order $\\delta^{-4}$, with explicit constants, and five nonlinear and reinforcement-learning rules follow the same "
          "$O(A^2)$ local gap and $\\delta^{-4}$ scaling below their saturation thresholds; separating $K$ unknown cohorts costs $(\\Delta\\eta)^{-(4K-2)}$ "
          "experiments, a rate attained by Prony's method; with general completely monotone memory the minimax accuracy is only of order "
          "$1/\\log N$. Class-tagged disclosure removes the barrier, reduces the sample requirement by a factor of order "
          "$(\\Delta\\eta)^{-(4K-4)}$, and breaks even against U.S.\\ Consolidated Audit Trail operating costs at 16 markets for $K=3$ ($\\Delta\\eta=0.10$). "
          "In data, trader-class positions published by Binance and, in a pre-registered test, by the CFTC for "
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
