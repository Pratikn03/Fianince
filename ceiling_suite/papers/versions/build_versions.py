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
front = front.replace("\\usepackage[margin=1in]{geometry}", "\\usepackage[margin=1in]{geometry}")
front = front.replace("\\doublespacing", "\\onehalfspacing")
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
   "\\subsection{Post-hoc checks on opened data (Part 18)}\\label{sec:p18}\nPost-hoc checks on samples already opened, an order-splitting placebo on the Binance samples of Parts 9 and 16 and three more guard controls (a certified peak-response guard, a participation cap and a margin-style rule) on Parts 15 and 16, are reported in the Internet Appendix (Table~\\ref{tab:p18}).\n\n")
mv("\\subsection{Three analyses specified in advance, not deposited (Parts 19--21)}\\label{sec:p1921}",
   "\\subsection{Pre-registered test of the liquidation mechanism (Part 22)}\\label{sec:p22}",
   "Analyses specified in advance, not deposited (Parts 19--21)",
   "\\subsection{Three analyses specified in advance, not deposited (Parts 19--21)}\\label{sec:p1921}\\label{sec:p19}\\label{sec:p20}\\label{sec:p21}\nThree further analyses were specified in an earlier draft before their data were downloaded but were not hash-registered; the Internet Appendix reports their full tables (Tables~\\ref{tab:p19}--\\ref{tab:p21}). In Part 19 (19 thin symbols on the 8th of each month), Primary 1---the interaction of $\\hat C_3$ with high open-interest-to-depth leverage (${\\rm LEV}\\ge16.77$)---fails ($-0.18$~bp, 95\\% CI $[-3.02,+3.73]$); post hoc, $\\hat C_3$ already contains $\\hat\\kappa$, so high-${\\rm LEV}$ hours have larger variance in $\\hat C_3$ ($\\Delta R^2=+8.172$ vs.\\ $+3.678$ points; difference $+4.495$ points, 95\\% CI $[-1.094,+11.663]$), while the matched spot gain is $15.2\\%$ of the perpetual gain ($+0.987$ vs.\\ $+6.495$ points, Clark--West $t=4.96$, ratio 95\\% CI $[-0.015,+0.308]$, exploratory). In Part 20 (BTCUSDT spot zero-fee introduction and removal), the primary reversion ($\\hat m=-0.00120$, $p=0.590$, 80\\% MDE $31.9\\%$) and gain-multiple ($\\widehat{S/\\tilde\\kappa}=-26.88$, $p=0.362$, MDE $52.0\\%$) hypotheses are not supported, while spot impact falls $18.3\\%$ ($\\hat\\kappa=-0.2432$, $t=-3.86$, $p=0.0002$, exploratory, single treated pair; $+0.0082$, $p=0.887$ when pooling a third VIP maker-fee date), consistent with Proposition~\\ref{prop:equil}(v). In Part 21, the guard alone lowers hourly $\\mathrm{ES}_{95}$ per \\$1M of position by \\$3{,}045 ($p=0.0025$) and \\$10{,}518 ($p=0.004$) against a static limit, while adding it to a volatility cap lowers $\\mathrm{ES}_{95}$ by \\$398 ($p=0.196$) and \\$2{,}557 ($p=0.036$, Holm $p=0.07$), neither significant.\n\n")
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
for tlab, tsec in [
    ("tab:certvsid", "Certification vs.\\ identification sample complexity table"),
    ("tab:discsim", "Disclosure value across cohort memory rates table"),
    ("tab:d2", "Validation of the 30-second depth snapshots"),
    ("tab:fixedgrid", "Depletion on a fixed price grid table"),
    ("tab:p15", "Pre-registered test on untouched days table (Part 15)"),
    ("tab:p16", "Pre-registered test on untouched symbols table (Part 16)"),
    ("tab:p22", "Pre-registered liquidation mechanism table (Part 22)"),
    ("tab:p23", "Pre-registered multi-hour guard capacity table (Part 23)"),
]:
    _l0 = body.index("\\label{" + tlab + "}")
    _t0 = body.rfind("\\begin{table}", 0, _l0)
    _t1 = body.index("\\end{table}", _l0) + len("\\end{table}")
    ia_extra += "\\section{" + tsec + "}\n" + body[_t0:_t1] + "\n"
    body = body[:_t0] + body[_t1:]
    body = body.replace("Table~\\ref{" + tlab + "}", "Internet Appendix Table~\\ref{" + tlab + "}")
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
f1 = re.sub(r"\\usepackage\[[^\]]*\]\{geometry\}", "\\\\usepackage[margin=1.1in]{geometry}", f1)
f1 = f1.replace("\\doublespacing", "\\onehalfspacing")
f1 = f1.replace("\\begin{document}", "\\usepackage{etoolbox}\\AtBeginEnvironment{tabular}{\\scriptsize}\\setlength{\\tabcolsep}{3pt}\\sloppy\n\\begin{document}", 1)
f1 = f1.replace("\\newpage\n\\setcounter{page}{1}\n\\tableofcontents\n\\newpage", "\\newpage\n\\setcounter{page}{1}")
_mp1_0 = f1.index("\\begin{table}[t]\\centering\\small\n\\begin{threeparttable}\n\\caption{Map of results}")
_mp1_1 = f1.index("\\end{table}", _mp1_0) + len("\\end{table}")
supp_extra1 = "\\section{Map of results}\n" + f1[_mp1_0:_mp1_1] + "\n"
f1 = f1[:_mp1_0] + f1[_mp1_1:]
app1 = rd(f"{P1}/p1_appendix.tex")
i1_proofs = app1.index("\\section{Proofs}\\label{app:proofs}")
main1 = app1[:i1_proofs]
supp1 = app1[i1_proofs:].replace("\\end{document}", "")
SUP = ("\\clearpage\n\\setcounter{page}{1}\\renewcommand{\\thepage}{S-\\arabic{page}}\n"
       "\\setcounter{section}{0}\\renewcommand{\\thesection}{S.\\arabic{section}}\n"
       "\\begin{center}{\\Large Supplemental Appendix for ``Auditable Memory and Financial Identification Limits''}\\end{center}\n\\label{app:suppstart}\n")
body1 = "".join(rd(f"{P1}/{f}") for f in ["p1_ident.tex", "p1_account.tex", "p1_mixture.tex", "p1_disclosure.tex", "p1_empirics.tex"])
def mv1(start, end, supp_title, pointer):
    global body1, supp_extra1
    i0 = body1.index(start); i1 = body1.index(end, i0 + len(start))
    blk = body1[i0:i1]
    supp_extra1 += "\\section{" + supp_title + "}" + blk[len(start):]
    body1 = body1[:i0] + pointer + body1[i1:]
mv1("\\subsection{Observation design and the tri-region partition}",
    "\\subsection{Account-level capital and the gap to the lower bound}",
    "Observation design and the tri-region partition",
    "\\subsection{Observation design and the tri-region partition}\nUnder observation horizon $T$ per pulse, $(\\delta,B)$ space splits into three regions: a feasible single-pulse region ($C^*=\\Theta(\\delta^{-4})$ for symmetric splitting), a sequential bounded-probing region where each capped pulse supplies divergence $V_{\\rm eff}^2\\|d_T\\|_2^2/(2\\sigma^2)$, and an infeasible region below the finite-session resolution floor $\\delta_{\\min}=\\Theta(T_{\\rm session}^{-1/4})$ (Supplemental Appendix, Proposition~\\ref{prop:tri} and Figure~\\ref{fig:phase}).\n\n")
mv1("\\subsection{Robustness: heteroskedastic impact and probing protocols}",
    "\\subsection{From par units to Bitcoin dollars}\\label{sec:dollars}",
    "Robustness: heteroskedastic impact and probing protocols",
    "\\subsection{Robustness: heteroskedastic impact and probing protocols}\nProbing-induced heteroskedasticity and convex impact leave the $\\delta^{-4}$ capital order unchanged (Supplemental Appendix, Corollary~\\ref{cor:garch}), and four simulated probing protocols all exhibit log--log capital slopes near $-4$ (Table~\\ref{tab:protocols}).\n\n")
mv1("\\section{A spectral blind spot}\\label{sec:blind}",
    "\\section{Empirical feedback and its measurement}\\label{sec:empirics}",
    "A spectral blind spot\\label{sec:blind}",
    "\\section{A spectral blind spot}\nFor any eigenvalues $0<\\lambda_2<\\lambda_1<1$, one-step price variance and sufficiently large stationary price variance, there is a family of two-state markets sharing all three quantities whose worst-case transient gain grows without bound (Supplemental Appendix, Theorem~\\ref{thm:blind} and Figure~\\ref{fig:blind}).\n\n")
mv1("\\section{Empirical feedback and its measurement}\\label{sec:empirics}",
    "\\section{Implications for supervision and market design}\\label{sec:policy}",
    "Empirical feedback and its measurement\\label{sec:empirics}",
    "\\section{Empirical feedback and its measurement}\nAcross a 96-date, eight-pair Binance spot panel (66.3M one-second bars), a 72-date BTCUSDT one-second panel, 30 USD-M perpetuals and two BTCUSDT spot zero-fee events, standard reduced-form feedback indices are dominated by EMA filtering mechanics ($1-\\alpha=0.9355$) and clock alignment ($0.0081$ with look-ahead vs.\\ $0.00037$ aligned); real feedback beyond the placebo is positive but small ($0.0045$), rises with market depth (Spearman $+0.70$), and does not move when zero fees multiply trading volume by $2.6$ to $4.9$ (Supplemental Appendix, Tables~\\ref{tab:samples}--\\ref{tab:fee2}).\n\n")
tex1 = f1 + body1 + main1 + SUP + supp_extra1 + supp1 + "\n\\end{document}\n"
n1, bad1 = build(tex1, "Paper1_QE")
aux = open(f"{OUT}/Paper1_QE.aux").read()
m = re.search(r"\\newlabel\{app:suppstart\}\{\{[^}]*\}\{([^}]*)\}", aux)
print("Paper1_QE pages:", n1, "| supplement starts at page label:", m.group(1) if m else None, bad1)
