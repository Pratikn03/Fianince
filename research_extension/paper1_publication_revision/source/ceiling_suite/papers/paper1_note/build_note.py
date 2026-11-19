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

def sort_bib_entries(bib_str):
    import re
    p = bib_str.split(r"\bibitem")
    hdr = p[0]
    ftr = r"\end{thebibliography}"
    ents = [r"\bibitem" + x.replace(ftr, "").strip() for x in p[1:] if x.strip()]
    def _k(entry):
        m = re.match(r"\\bibitem\[([^\]]+)\]", entry)
        if not m: return (entry.lower(), "")
        lbl = m.group(1)
        auth = lbl.split("(")[0].replace("~", " ").strip()
        yr = re.search(r"\((\d{4}[a-z]?)\)", lbl)
        y_str = yr.group(1) if yr else ""
        clean = "".join(c for c in auth if c.isalpha() or c == " ")
        return (clean.lower(), y_str)
    ents.sort(key=_k)
    return hdr + "\n\n".join(ents) + "\n\n" + ftr

bib = sort_bib_entries(bib)
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
    "identifying functional of such a market: populations with the same kernel produce the same prices, profits and "
    "equilibria, and prices identify nothing finer. Learning the composition of the population costs data of order "
    "$(\\Delta\\eta)^{-(4K-2)}$ for $K$ groups whose memories lie within $\\Delta\\eta$, even near instability: "
    "there exist moment-matched, stable two-group populations with half-lives of 5 to 9 days that need more than "
    "4{,}000 years of daily prices to be told apart, a worst-case bound rather than a typical one. "
    "Market-wide actions need only the kernel, and a broad class of market-wide questions is answered at the usual "
    "statistical rate whatever the number of groups, so the two costs separate without bound as memories converge. When the population drifts, composition can be tracked only below a speed "
    "limit. Two remedies follow. Tagging all but one memory class removes the barrier, and the last tag is worth "
    "nothing. Without any tags, pooling $D$ markets in which the same algorithms trade in different proportions "
    "lowers the exponent near generic configurations to $2(K-1+\\lceil K/D\\rceil)$, because an algorithm's memory is the same everywhere it "
    "trades. Core results are machine-checked in Lean~4.")
CAL = r"""
\paragraph{How large is the barrier?} Table~\ref{n:tab_cal} puts numbers on part~(iii) for two groups. What matters is the spread of memories relative to their size. There exist moment-matched, stable populations whose memories all have half-lives between 5 and 9 days that cannot be told apart with both error probabilities at $5\%$ from less than $4{,}000$ years of daily prices, however close the market is to instability; this is the worst case over the range, and other populations in it are easier to separate. When half-lives differ by a factor of three or more, a century of daily data can suffice. With three groups the numbers grow to the order of $10^8$ years. The numbers bound every test, for the passive record; probing faces the same order (part~(i)). The exponents do not depend on Gaussian noise: with real Bitcoin price noise injected into synthetic groups, the fitted slopes are $-6.01$ and $-9.81$, against $-6$ and $-10$ (Supplement Section~\ref{sec:injection}).

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
\parbox{\textwidth}{\footnotesize Bound: $n\ge\ln 5/\mathrm{KL}$ observations (Bretagnolle--Huber), with KL the Gaussian information per observation, computed as in Figure~\ref{n:fig_barrier}, at a common feedback budget $S$, impact $\kappa=0.5$ and feedback share $\kappa\sum_iq_i=0.3$ (total weight $0.6(1-r_c)$ at centre rate $r_c$). Memory rates are per day, 252 days a year; for traders whose memories are counted in five-minute periods, with prices recorded every five minutes around the clock, divide by $417$. Two significant digits.}
\end{table}
"""
EQ_SEC = r"""
\section{Sufficiency and identification in equilibrium}\label{n:sec_equilibrium}

The identification results of Section~\ref{n:suff_sec} take the price impact $\kappa$ and the persistence $a$ of pricing errors as given. This section derives both endogenously from competitive dealers who carry inventory risk. It shows that the equilibrium price follows the closed loop of Section~\ref{n:model} with effective parameters and unchanged memory rates. Consequently, the kernel remains the minimal sufficient statistic in equilibrium, and the sample complexity of learning composition retains its $(\Delta\eta)^{-(4K-2)}$ barrier.

\paragraph{An inventory equilibrium.}
\begin{itemize}[itemsep=1pt,topsep=2pt]
\item \emph{Fundamental and price.} The fundamental $F_t$ is a public random walk with innovation variance $\sigma_F^2$, and the transaction price is $p_t=F_t+x_t$, where $x_t$ is the pricing error.
\item \emph{Groups.} Feedback groups trade $u_{i,t+1}=r_i u_{i,t}+w_i x_t$, with exponential memory rates $r_i=1-\eta_i\in(0,1)$ and weights $w_i=q_i\eta_i$.
\item \emph{Exogenous flow.} An exogenous shock $\xi_t\sim N(0,\sigma_\xi^2)$, i.i.d., represents noise trading or supervisory probing. Total customer order flow is $y_t=\sum_i u_{i,t}+\xi_t$.
\item \emph{Dealers.} Competitive risk-averse dealers absorb customer order flow and lay off a fraction $1-\bar a$ of their inventory each period, yielding the inventory evolution $H_t=\bar a H_{t-1}-y_t$. An overlapping generation of dealers with CARA risk aversion $A$ prices the asset so that $H_t=(E_t p_{t+1}-p_t)/(A V)$, with conditional price variance $V=\mathrm{Var}_t(p_{t+1})$.
\end{itemize}
We consider stationary linear equilibria where $x_t$ is linear in dealer inventory and future feedback trades. Let $G(D)=\sum_i w_i/(D-r_i)$ denote the Stieltjes transform of the merged measure.

\begin{theorem}[Price impact and persistence in an inventory equilibrium]\label{n:thm_inventory}
Consider stationary linear equilibria of the inventory model above.
\begin{enumerate}[label=(\roman*),itemsep=1pt]
\item \emph{Characterization.} The pricing error satisfies
\[
 x_t=-\kappa H_t+\kappa\sum_i\frac{u_{i,t+1}}{D-r_i}
\]
with $D\ne0$ and $D\ne r_i$, if and only if the induced dynamics are stable and
\begin{equation}\label{n:eq:inventory_eq}
 D=1-\kappa\,G(D),\qquad \kappa(D-\bar a)=A\,V\,D,\qquad V=\sigma_F^2+\frac{\kappa^2\sigma_\xi^2}{D^2}.
\end{equation}
An unexpected unit of order flow moves the price by $\kappa/D$.
\item \emph{No feedback.} When $w_i=0$, $D=1$ and the pricing error satisfies $x_t=\bar a\,x_{t-1}+\kappa\,y_t$. Persistence is the dealer carry share $a=\bar a$, and impact $\kappa$ solves $\kappa(1-\bar a)=A(\sigma_F^2+\kappa^2\sigma_\xi^2)$. An equilibrium exists if and only if $\Delta=(1-\bar a)^2-4A^2\sigma_F^2\sigma_\xi^2\ge0$. When $\Delta>0$, the low-impact root $\kappa_-\approx A\sigma_F^2/(1-\bar a)$ is the equilibrium price of inventory risk.
\item \emph{Invariance.} The equilibrium coefficients $(\kappa,D,V)$ depend on the groups only through the Stieltjes transform $G$, and therefore only through the merged measure $M$.
\item \emph{Small feedback.} For small feedback intensity $G(1)=\sum_i q_i$, there exists a unique equilibrium near $(\kappa_-,1)$ with
\[
 D=1-\kappa_-G(1)+o(G(1)),\qquad \kappa=\kappa_-+\frac{\kappa_-^2(\bar a+2A\kappa_-\sigma_\xi^2)}{\sqrt\Delta}\,G(1)+o(G(1)).
\]
Positive feedback increases both price impact $\kappa$ and unexpected shock impact $\kappa/D$.
\end{enumerate}
\end{theorem}

\begin{remark}[Observability of pricing errors]\label{n:rem_observability}
While feedback traders and dealers in Theorem~\ref{n:thm_inventory} condition on the pricing error $x_t = p_t - F_t$, an outside market supervisor observing only raw transaction prices $p_t = F_t + x_t$ with an unobserved random-walk fundamental $F_t$ receives strictly less information. Every sample-complexity lower bound established below therefore holds a fortiori under unobserved fundamentals (while Corollary~\ref{cor:unknown_primitives} handles unknown primitives under active reset probes).
\end{remark}

\begin{theorem}[The identification results hold in equilibrium]\label{n:thm_eqreduced}
In the inventory equilibrium of Theorem~\ref{n:thm_inventory}:
\begin{enumerate}[label=(\roman*),itemsep=1pt]
\item \emph{Reduced form.} The pricing error follows the closed loop of Section~\ref{n:model} with effective persistence $a^*=\bar a/D$, effective impact $\kappa^*=\kappa/D$, unchanged memory rates $r_i$, and rescaled weights $\tilde w_i=w_i(D-\bar a)/(D-r_i)$.
\item \emph{Zeros.} The memory rates $r_i$ remain the transmission zeros of the equilibrium price response.
\item \emph{Identification boundary.} The effective merged measure $\tilde M=h\,M$ with $h(r)=(D-\bar a)/(D-r)>0$ is in one-to-one correspondence with the primitive merged measure $M$. Hence the merged measure remains the exact identifying functional of equilibrium prices.
\item \emph{Minimax rate preservation.} Two economies with identical primitives $(A,\sigma_F^2,\sigma_\xi^2,\bar a)$ that differ only in their feedback groups require $N\ge c\,\sigma^2(\Delta\eta)^{-(4K-2)}$ observations to be distinguished.
\end{enumerate}
\end{theorem}
"""

THEORY_EDITS = [
    ("with effective impact and persistence, and with the memory rates unchanged (Supplement Theorems~\\ref{thm:inventory} and~\\ref{thm:eqreduced}).",
     "with effective impact and persistence, and with the memory rates unchanged (Theorems~\\ref{n:thm_inventory} and~\\ref{n:thm_eqreduced}).\n\nTogether, Theorems~\\ref{n:suff} and~\\ref{n:ident} make the kernel a \\emph{minimal identifying functional} of the population for prices: it determines everything prices can show, and prices determine it. (The merged measure has finitely many atoms, so its moments, the kernel, determine it.)\n\n" + EQ_SEC),
    (r"\item \emph{Identification} (Theorem~\ref{n:ident}). Two populations give identical price responses to every trade sequence exactly when their \emph{merged measures}, the trading weight at each memory rate, coincide. Groups with the same memory cannot be separated however long the record. For any population, linear or not, prices identify exactly its aggregate flow map, and the cost bounds below hold over any class that contains the linear rules.",
     r"""\item \emph{Identification} (Theorem~\ref{n:ident}). Two populations give identical price responses to every trade sequence exactly when their \emph{merged measures}, the trading weight at each memory rate, coincide. Groups with the same memory cannot be separated however long the record. For any population, linear or not, prices identify exactly its aggregate flow map, and the cost bounds below hold over any class that contains the linear rules.
\item \emph{Equilibrium microfoundations} (Theorems~\ref{n:thm_inventory} and~\ref{n:thm_eqreduced}). In an inventory equilibrium with competitive risk-averse dealers, price impact and persistence arise endogenously. The equilibrium price is the closed loop with effective parameters, the memory rates are preserved, and the identification boundary and minimax sample-complexity bounds hold unchanged."""),
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
     "is very expensive in the hardest configurations, even on the eve of a crash: at illustrative parameters there exist moment-matched, stable populations with memory half-lives between 5 and 9 days whose separation needs more than 4{,}000 years of daily prices (Table~\\ref{n:tab_cal}); easier populations in the same range can need far less."),
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
decl_th = decl
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

# Sort bibliography in theory version alphabetically
i_th = theory.index(r"\begin{thebibliography}")
j_th = theory.index(r"\end{thebibliography}") + len(r"\end{thebibliography}")
bib_th = theory[i_th:j_th]
theory = theory[:i_th] + sort_bib_entries(bib_th) + theory[j_th:]

for a, b in (("(full working paper, internet appendix)", "(\\citealp{niroula2026a}, internet appendix)"), ("(full working paper)", "\\citep{niroula2026a}"), ("The full working paper", "\\citet{niroula2026a}"),
             ("the full working paper", "\\citet{niroula2026a}"),
             ("reproduce Sections~2--8 of the longer core version of this paper (12 November 2026): every result in full, with the remarks, machine-check notes and the results that the note omits.",
              "state every result in full, with the remarks, machine-check notes and the results that the main text omits."),
             ("Theorem numbers in the supplement are those of these sections, not of the note. The note's results correspond", "Theorem numbers in the supplement are those of these sections, not of the main text. The main text's results correspond"),
             ("The main text's results correspond to them as follows: Theorem~\\ref{n:suff}", "The main text's results correspond to them as follows: Theorems~\\ref{n:thm_inventory} and~\\ref{n:thm_eqreduced} to Theorems~\\ref{thm:inventory} and~\\ref{thm:eqreduced}; Theorem~\\ref{n:suff}")):
    theory = theory.replace(a, b)
for a, b in (("\\citet{niroula2026a} reports", "\\citet{niroula2026a} report"), ("\\citet{niroula2026a} proves", "\\citet{niroula2026a} prove"),
             ("\\citet{niroula2026a} matches", "\\citet{niroula2026a} match")):
    theory = theory.replace(a, b)

body = body.replace("is (see Reproducibility Table).", "is recorded in Supplement Section~\\ref{app:verification} (and \\nolinkurl{formal_verification_receipt.json}).")
body = body.replace("(see Reproducibility Table)", "(Supplement Section~\\ref{app:verification}, \\nolinkurl{reproduce.py})")
sub = sub.replace("is (see Reproducibility Table).", "is recorded in Supplement Section~\\ref{app:verification} (and \\nolinkurl{formal_verification_receipt.json}).")
sub = sub.replace("(see Reproducibility Table)", "(Supplement Section~\\ref{app:verification}, \\nolinkurl{reproduce.py})")
theory = theory.replace("is (see Reproducibility Table).", "is recorded in Supplement Section~\\ref{app:verification} (and \\nolinkurl{formal_verification_receipt.json}).")
theory = theory.replace("(see Reproducibility Table)", "(Supplement Section~\\ref{app:verification}, \\nolinkurl{reproduce.py})")
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
KEEP = ["The moment gap of the hard pair", "The largest weights of the hard pair",
        "The pooling moment map: Jacobian and global immersion",
        "Pure Nash equilibrium: existence via concavity and uniqueness via residual monotonicity",
        "Gaussian-convolved news of arbitrary law"]
i = theory.index("\\section{Questions left open in earlier versions}"); j = theory.index("\\section{", i + 10)
sec = theory[i:j]
cuts = [m.start() for m in re.finditer(r"\\subsection\{", sec)] + [len(sec)]
subs = {re.match(r"\\subsection\{([^\n]*)\}", sec[a:]).group(1).split("}")[0]: sec[a:b] for a, b in zip(cuts, cuts[1:])}
assert set(subs) == set(KEEP) | {t for v in MOVE.values() for t in v}, set(subs) ^ (set(KEEP) | {t for v in MOVE.values() for t in v})
newsec = ("\\section{The hard pair: moment gap, largest weights, Jacobian and extensions}\\label{app:openres}\n\nThis section gives the exact size of the moment gap behind the constants of Theorem~\\ref{thm:kcohort}, compares the largest weights of the hard pair, proves global immersion of the pooling moment map, existence and uniqueness of pure Nash equilibrium, and the extension of passive lower bounds to Gaussian-convolved news.\n\n" + "".join(subs[t] for t in KEEP))
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
focus = focus.replace("\\begin{document}", "\\externaldocument[][nocite]{paper1b_companion}\n\\begin{document}", 1)
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
cdecl = ("\n\n\\subsection*{Declarations}\n\n\\paragraph{Declaration of generative AI and AI-assisted technologies.} "
         "During the preparation of this work, the authors used large language model systems (Claude, ChatGPT/Codex, and Gemini) "
         "for code development, numerical cross-checks, Lean~4 formalization checks, and manuscript drafting assistance. After using these "
         "tools, the authors reviewed, validated, and edited all materials, verified all mathematical proofs and empirical calculations, "
         "and take full responsibility for the content and conclusions of this manuscript.\n\n")
comp = (cpre + "\\externaldocument[][nocite]{paper1_focus}\n\\begin{document}\n\\maketitle\n" + CABS + "\\renewcommand{\\thesection}{C\\arabic{section}}\n"
        + comp_body + cdecl + "\n" + cbib + "\\end{document}\n")
open("paper1b_companion.tex", "w", encoding="utf-8").write(comp)
print("written paper1_focus.tex and paper1b_companion.tex; moved labels:", len(moved), "; cited keys in companion:", len(cited))
