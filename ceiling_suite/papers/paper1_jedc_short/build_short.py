"""Build the JEDC submission: the short main text and its Online Supplement (22 November 2026).

1. make_short.py writes Paper1_JEDC_main.tex from the received 27-page main text, with the corrections.
2. The Online Supplement is the supplement of the journal version (../paper1_note/paper1_jedc.tex, built by
   build_ssrn.py), made a standalone document. Its references to main-text results point to the short main text
   through xr-hyper (prefix M-); the main text points to the supplement with prefix S-. Its bibliography keeps the
   references the supplement cites.
3. Both are compiled in turn until the cross-references settle, and the logs are checked: no undefined or multiply
   defined references, no undefined citations, no overfull boxes.
4. The PDFs go to pdf_delivered/ (repository root and ceiling_suite/papers/).

Run: python ceiling_suite/papers/paper1_jedc_short/build_short.py   (after build_ssrn.py --pdf)
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTE = HERE.parent / 'paper1_note'
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'research_extension/paper1_publication_revision/t6'))
import make_short  # noqa: E402
import round9  # noqa: E402

MAIN, SUPP = 'Paper1_JEDC_main', 'Paper1_JEDC_online_supplement'
SUPP_START = '\\singlespacing\\small\\sloppy\n'


SUPP_EXTRA_BIBITEMS = (
    "\n"
    r"\bibitem[Avellaneda and Stoikov(2008)]{avellaneda2008} Avellaneda, M., and S. Stoikov (2008). High-frequency trading in a limit order book. \emph{Quantitative Finance} 8, 217--224." + "\n\n"
    r"\bibitem[Barndorff-Nielsen et~al.(2008)]{barndorff2008} Barndorff-Nielsen, O.~E., P.~R. Hansen, A. Lunde, and N. Shephard (2008). Designing realized kernels to measure the ex post variation of equity prices in the presence of noise. \emph{Econometrica} 76(6), 1481--1536." + "\n\n"
    r"\bibitem[Border and Sobel(1987)]{border1987} Border, K.~C., and J. Sobel (1987). Samurai accountant: A theory of auditing and plunder. \emph{Review of Economic Studies} 54(4), 525--540." + "\n\n"
    r"\bibitem[Brillinger(1965)]{brillinger1965} Brillinger, D.~R. (1965). An introduction to polyspectra. \emph{Annals of Mathematical Statistics} 36(5), 1351--1374." + "\n\n"
    r"\bibitem[Brunnermeier and Pedersen(2009)]{brunnermeier2009} Brunnermeier, M.~K., and L.~H. Pedersen (2009). Market liquidity and funding liquidity. \emph{Review of Financial Studies} 22(6), 2201--2238." + "\n\n"
    r"\bibitem[Hinich(1982)]{hinich1982} Hinich, M.~J. (1982). Testing for Gaussianity and linearity of a stationary time series. \emph{Journal of Time Series Analysis} 3(3), 169--176." + "\n\n"
    r"\bibitem[Huberman and Stanzl(2004)]{huberman2004} Huberman, G., and W. Stanzl (2004). Price manipulation and quasi-arbitrage. \emph{Econometrica} 72(4), 1247--1275." + "\n\n"
    r"\bibitem[Jacod et~al.(2009)]{jacod2009} Jacod, J., Y. Li, P.~A. Mykland, M. Podolskij, and M. Vetter (2009). Microstructure noise in the continuous case: The pre-averaging approach. \emph{Stochastic Processes and their Applications} 119(7), 2249--2276." + "\n\n"
    r"\bibitem[Ma\'ckowiak and Wiederholt(2009)]{mackowiak2009} Ma\'ckowiak, B., and M. Wiederholt (2009). Optimal sticky prices under rational inattention. \emph{American Economic Review} 99(3), 769--807." + "\n\n"
    r"\bibitem[Mancini(2009)]{mancini2009} Mancini, C. (2009). Non-parametric threshold estimation for models with stochastic diffusion coefficient and jumps. \emph{Scandinavian Journal of Statistics} 36(2), 270--296." + "\n\n"
    r"\bibitem[Roll(1984)]{roll1984} Roll, R. (1984). A simple implicit measure of the effective bid-ask spread in an efficient market. \emph{Journal of Finance} 39, 1127--1139." + "\n\n"
    r"\bibitem[Sims(2003)]{sims2003} Sims, C.~A. (2003). Implications of rational inattention. \emph{Journal of Monetary Economics} 50(3), 665--690." + "\n\n"
    r"\bibitem[Subrahmanyam(1994)]{subrahmanyam1994} Subrahmanyam, A. (1994). Circuit breakers and market volatility: A theoretical perspective. \emph{Journal of Finance} 49(1), 237--254." + "\n"
)


def _rep_supp(doc, old, new, count=1):
    n = doc.count(old)
    assert n == count, (old[:120], n, count)
    return doc.replace(old, new)


def supplement_tex():
    t = (NOTE / 'paper1_jedc.tex').read_text()
    pre = t[:t.index('\\begin{document}')]
    pre = pre.replace('\\externaldocument[][nocite]{paper1b_companion}',
                      '\\externaldocument[][nocite]{../paper1_note/paper1b_companion}\n\\externaldocument[M-]{' + MAIN + '}')
    pre = pre.replace('\\graphicspath{{../paper1_core/}}', '\\graphicspath{{../paper1_core/}{../paper1_note/}}')
    assert '\\externaldocument[M-]' in pre
    a = t.index('\\appendix\n\\clearpage\n' + SUPP_START)
    body = t[a + len('\\appendix\n\\clearpage\n'):t.index('\\end{document}')]
    main_labels = set(make_short.LABELS.values())
    defined_here = set(re.findall(r'\\label\{([^}]+)\}', body))
    assert not (main_labels & defined_here), main_labels & defined_here
    n = 0
    for lab in sorted(main_labels):
        for cmd in ('ref', 'eqref'):
            old = '\\' + cmd + '{' + lab + '}'
            n += body.count(old)
            body = body.replace(old, '\\' + cmd + '{M-' + lab + '}')
    body = body.replace('{\\normalsize Niroula, Niroula and Khatiwada, 21 November 2026}',
                        '{\\normalsize Niroula, Niroula and Khatiwada, November 2026}')
    b0 = t.index('\\begin{thebibliography}')
    b1 = t.index('\\end{thebibliography}') + len('\\end{thebibliography}')
    bib = t[b0:b1].replace('\\end{thebibliography}', SUPP_EXTRA_BIBITEMS + '\\end{thebibliography}')
    doc = pre + '\\begin{document}\n' + body + '\n' + bib + '\n\\end{document}\n'
    doc = round9.longtable_newlean(doc)

    # ---------------------------------------------------------------- mathematical and editorial fixes
    mapping_old = r"Theorem~\ref{M-n:paradox} to Section~\ref{app:paradox}."
    mapping_new = (
        r"Theorem~\ref{M-n:paradox} to Section~\ref{app:paradox} (and Proposition~\ref{M-prop:endogenous_supervisor} is proved in Main Appendix~A, extending Section~\ref{app:paradox}); "
        r"Theorem~\ref{M-thm:fragility} and Corollary~\ref{M-cor:posthaltflip} are proved in Main Appendix~A (with dealer-entry unfolding in Section~\ref{sec:mixed_sign}); "
        r"Theorem~\ref{M-thm:mpv} is proved in Main Appendix~A (details in Section~\ref{sec:mpv_supp}); "
        r"Proposition~\ref{M-thm:instruments} is proved in Main Appendix~A and Sections~\ref{app:instruments}--\ref{app:passiveincidence}."
    )
    doc = _rep_supp(doc, mapping_old, mapping_new)
    doc = _rep_supp(doc, r"Since $A=A_0+\lambda^2CD+O(\varepsilon^2)$", r"Since $A=A_0+\lambda^2 C L+O(\varepsilon^2)$")
    doc = _rep_supp(doc, r"\subsection{The targeted halt for every $K$}", r"\subsection{The targeted halt for every \texorpdfstring{$K$}{K}}")
    doc = _rep_supp(doc, "The additional revision file is audited separately;", "All eighteen revision files are audited under the same strict axiom scan;")
    doc = _rep_supp(doc, "is recorded in Supplement Section~\\ref{app:verification} (and \\nolinkurl{formal_verification_receipt.json}).",
                    "is recorded in \\nolinkurl{formal_verification_receipt.json}.")
    doc = doc.replace(", and a prospective window from November 2026 serves as a replication", "")
    doc = doc.replace(r"J'=TJT^{-1}={\rm diag}(0,r_1,\ldots)+uu^\top",
                      r"J'=TJT^{-1}={\rm diag}(0,r_1,\ldots)+uu^\top \succeq 0\text{ (since }r_i\ge 0\text{ and }uu^\top\succeq 0\text{, so }\lambda_\ell\ge 0)")
    doc = doc.replace("detection probability, and $k(\\delta_0-\\delta)^2$", "detection probability, $k(\\delta_0-\\delta)^2$")
    doc = _rep_supp(doc, "1,238 named declarations", "1,306 named declarations")
    doc = doc.replace(r"13 November 2026 (Lean 4.34.1, Mathlib commit \texttt{d13f23b})",
                      r"26 November 2026 (Lean 4.34.1 commit \texttt{5045d00}, Mathlib commit \texttt{d13f23b})")
    doc = doc.replace(r"fourteen Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision14.lean}",
                      r"eighteen Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision18.lean}")
    doc = doc.replace("The uniform positive lower bound and the maximum principle bound $B$ away from zero",
                      r"The uniform positive lower bound on the unit circle and the minimum principle for harmonic functions (applied to $\operatorname{Re}B$) bound $\operatorname{Re}B$, and hence $|B|$, away from zero")
    doc = doc.replace("by Cauchy's inequality", "by Cauchy's integral estimate")
    doc = doc.replace("on on [0,1]^K", "on [0,1]^K")
    doc = _rep_supp(
        doc,
        r"(\nolinkurl{tag_minimax_on}) & none\\",
        r"(\nolinkurl{tag_minimax_on}) & existence on compact $[0,1]^K$ and strict-convexity group-uniform uniqueness\\",
    )
    doc = _rep_supp(
        doc,
        "Since the sample covariance matrix has operator norm at most\n" + r"$\sup f$",
        "Since the population Toeplitz covariance matrix has operator norm at most\n" + r"$\sup f$",
    )
    doc = _rep_supp(
        doc,
        r"Price only, $K=3$ (H3) & $-10$ & $-9.81$ & $-9.96$",
        r"Price only, $K=3$ (H3)$^\dagger$ & $-10$ & $-9.81^\dagger$ & $-9.96$",
    )
    doc = _rep_supp(
        doc,
        r"Repeated cycles, learning about $\chi$ and enforcement costs are outside the model.",
        r"Repeated cycles, learning about $\chi$ and enforcement costs are outside the model. (In institutional US equity trails, offshore total-return swaps $\gamma_{\mathrm{TRS}}$ and net-zero multi-desk pods inside one LEI create synthetic routing channels analogous to cheap labels in Proposition~\ref{prop:relabelK}; SEC CAT funding also remains subject to the Eleventh Circuit's July~2025 vacatur in \emph{ASA v.\ SEC}.)",
    )

    # Merge duplicate Table S2 rows: Theorem 5.5 and Cor. 7.2
    old_thm_shape_1 = (r"Theorem~\ref{M-n:shape} & signed atomic measures with vanishing moments are zero (\texttt{vandermonde\_signed\_zero}); "
                       r"remainder absorption (\texttt{inverse\_remainder\_absorption}) & "
                       r"Lipschitz inverse on the compact class; Lipschitz bounds of the response map\\")
    new_thm_shape_1 = (r"Theorem~\ref{M-n:shape} & signed atomic measures with vanishing moments are zero (\texttt{vandermonde\_signed\_zero}); "
                       r"remainder absorption (\texttt{inverse\_remainder\_absorption}); "
                       r"absorption of the Taylor remainder (\nolinkurl{absorption}) & "
                       r"Lipschitz inverse on the compact class; Lipschitz bounds of the response map; "
                       r"injectivity and the Jacobian of the moment map, compactness, the Gaussian norm bound\\")
    doc = doc.replace(old_thm_shape_1, new_thm_shape_1)
    old_thm_shape_2 = (r"Theorem~\ref{M-n:shape} & absorption of the Taylor remainder (\nolinkurl{absorption}) & "
                       r"injectivity and the Jacobian of the moment map, compactness, the Gaussian norm bound\\" + "\n")
    doc = doc.replace(old_thm_shape_2, "")

    old_cor_loss_1 = (r"Cor.~\ref{M-n:decisionloss} & two-point loss bound, its divergence form, the record length and the tagged loss "
                      r"(\texttt{decision\_loss\_tv}, \texttt{decision\_loss\_kl}, \texttt{decision\_record\_length}, \texttt{decision\_tag\_loss}) & "
                      r"Pinsker's inequality and the Gaussian tail (hypotheses)\\")
    new_cor_loss_1 = (r"Cor.~\ref{M-n:decisionloss} & two-point loss bound, its divergence form, the record length and the tagged loss "
                      r"(\texttt{decision\_loss\_tv}, \texttt{decision\_loss\_kl}, \texttt{decision\_record\_length}, \texttt{decision\_tag\_loss}); "
                      r"loss at least $\min(b,c)$ times the mean error (\nolinkurl{decision_loss_min}) & "
                      r"Pinsker's inequality and the Gaussian tail (hypotheses); total variation\\")
    doc = doc.replace(old_cor_loss_1, new_cor_loss_1)
    old_cor_loss_2 = (r"Cor.~\ref{M-n:decisionloss} & loss at least $\min(b,c)$ times the mean error (\nolinkurl{decision_loss_min}) & "
                      r"total variation\\" + "\n")
    doc = doc.replace(old_cor_loss_2, "")

    s23_old = (r"Section~\ref{app:passiveincidence} & "
               r"Fourier first-moment budget (\texttt{fourier\_first\_moment\_budget}, \texttt{fourier\_first\_moment\_disk}), "
               r"truncation tail (\texttt{fourier\_truncation\_tail}), spectral floor Lipschitz (\texttt{spectral\_floor\_lipschitz}), "
               r"quadrature error (\texttt{quadrature\_fourier\_error}), transfer factor and "
               r"function errors (\texttt{transfer\_factor\_error}, \texttt{transfer\_function\_error}), incidence estimator bound "
               r"(\texttt{incidence\_estimator\_bound}) (\nolinkurl{PublicationRevision14.lean}) & "
               r"stationary Gaussian likelihood, spectral estimation, uniform central limit theorem, and Parseval isometry\\")
    s23_new = (r"Section~\ref{app:passiveincidence} (Proposition~\ref{M-thm:instruments}) & "
               r"Fourier first-moment budget (\texttt{p1\_fourier\_first\_moment\_bound}, \texttt{p1\_sum\_j\_logCoeff\_le}, "
               r"\texttt{p1\_sum\_j\_logCoeff\_disk\_le}, \texttt{p1\_fourier\_first\_moment\_budget}, \texttt{p1\_fourier\_first\_moment\_disk}), "
               r"truncation tail (\texttt{p1\_fourier\_truncation\_tail}), spectral floor log-Lipschitz (\texttt{p1\_spectral\_floor\_log\_lipschitz}, "
               r"\texttt{p1\_spectral\_floor\_lipschitz}), cell-average equidistant quadrature error (\texttt{p1\_quadrature\_fourier\_error}), transfer factor and "
               r"function errors (\texttt{p1\_transfer\_factor\_error}, \texttt{p1\_transfer\_function\_error}), Cauchy coefficient incidence estimator bound "
               r"(\texttt{p1\_incidence\_estimator\_bound}), deterministic end-to-end error assembly conditional on sample-covariance and floor bounds (\texttt{p1\_passive\_incidence\_end\_to\_end}) "
               r"and constrained desk quadratic optimum (\texttt{instrument\_desk\_constrained\_opt}) (\nolinkurl{PublicationRevision14.lean}, \nolinkurl{PublicationRevision18.lean}; \nolinkurl{Paper1PassiveIncidenceUpper.lean}, \nolinkurl{Paper1FragilityAndDesign.lean}) & "
               r"fourth-moment covariance convergence, uniform spectral floor probability, central limit theorem, and Parseval isometry\\" + "\n"
               r"Theorem~\ref{M-thm:fragility} \& Cor.~\ref{M-cor:posthaltflip}(i) & discriminant positivity, ordered roots, Vieta variance bound $V<2\sigma_F^2$, $S^*(\lambda_{\mathrm{crit}})<1$, $\lambda_{\mathrm{crit}}$ upper bound, and post-halt capacity-withdrawal flip (\texttt{fragility\_discriminant\_pos\_iff}, \texttt{fragility\_quadratic\_roots\_ordered}, \texttt{fragility\_vieta\_variance\_bound}, \texttt{fragility\_effective\_budget\_lt\_one}, \texttt{fragility\_lambda\_crit\_upper\_bound}, \texttt{post\_halt\_capacity\_withdrawal\_flip}) (\nolinkurl{PublicationRevision18.lean}; \nolinkurl{Paper1FragilityAndDesign.lean}) & critical fold $F_{DD}>0$ square-root asymptotics\\" + "\n"
               r"Cor.~\ref{M-cor:posthaltflip}(ii) & see Prop.~\ref{M-n:target}(ii) (\texttt{no\_common\_zero}, \texttt{node\_no\_recur}, \texttt{weight\_from\_lagrange}) & window feasibility $\kappa q_{\max}^{(2)} < 1 - \bar s$ and $(\Delta\eta)^{-(4K-2)}$ sample bound\\" + "\n"
               r"Prop.~\ref{M-n:target}(iii) & endpoint atom $W/K^2$ and budget separation via Prob/moments (\texttt{p1\_every\_k\_halt}, \nolinkurl{Paper1EveryKHalt.lean}) & Gauss--Radau vs Gauss node ordering and $(\Delta\eta)^{-(4K-2)}$ bound\\" + "\n"
               r"Lemma~\ref{M-lem:micro} & small-feedback impact derivative, $n_{\mathcal{H}}<0<n_{\mathcal{B}}$ separation, Kalman variance identity, strict convexity $P''(r)>0$, and monotone $P'(r)$ (\texttt{micro\_welfare\_weight\_separation}, \texttt{kalman\_stationary\_var\_identity}, \texttt{kalman\_stationary\_var\_strict\_convex}, \texttt{kalman\_deriv\_strict\_mono}) (\nolinkurl{PublicationRevision18.lean}; \nolinkurl{Paper1FragilityAndDesign.lean}) & third-order Taylor remainder in $r-r_0$\\" + "\n"
               r"Proposition~\ref{M-prop:endogenous_supervisor} & exact $4/(n \beta L)$ FOC crowding envelope, high-/low-stakes regime boundaries, composite GLRT envelope, Stackelberg general-$n$ collapse, simultaneous non-existence of pure NE, and tag decoupling (\texttt{supervisor\_no\_test}, \texttt{supervisor\_no\_test\_unique}, \texttt{trader\_crowding\_envelope}, \texttt{high\_stakes\_regime\_gap}, \texttt{low\_stakes\_regime\_dominance}, \texttt{composite\_glrt\_envelope}, \texttt{divergence\_collapse\_n4}, \texttt{divergence\_collapse\_general}, \texttt{tagging\_decoupling}, \texttt{supervisor\_effort\_collapse}, \texttt{supervisor\_effort\_collapse\_general}, \texttt{simultaneous\_no\_pure\_ne}) (\nolinkurl{PublicationRevision15.lean}; \nolinkurl{Paper1EndogenousSupervisor.lean}) & Neyman--Pearson lemma and Gaussian shift experiment power envelope\\" + "\n"
               r"Theorem~\ref{M-thm:mpv} & discrete floor tick-quantization cell coincidence, $(2K-1)$-exponent sub-tick gap with cell-center margin, closed-loop coincidence, zero-divergence inequality, and deterministic $(0,1)$ scalar interval bounds on $1 - \alpha^2/(12\sigma^2)$ and $1 - (1-a^2)\alpha^2/(6\sigma^2)$ (\texttt{tickQuantize\_eq\_of\_mem\_cell}, \texttt{quantized\_cell\_coincidence}, \texttt{sub\_tick\_response\_gap}, \texttt{sub\_tick\_closed\_loop\_coincidence}, \texttt{sub\_tick\_zero\_divergence\_bound}, \texttt{zero\_divergence\_minimax\_risk}, \texttt{sample\_complexity\_infinite}, \texttt{mpv\_threshold\_pos}, \texttt{mpv\_threshold\_mono}, \texttt{sheppard\_dither\_factor\_bounds}, \texttt{hmm\_double\_quantization\_factor\_bounds}) (\nolinkurl{PublicationRevision16.lean}; \nolinkurl{Paper1MPVQuantization.lean}) & Gaussian score integration over tick cells, reset Sheppard expansion, AR(1)/ARMA Whittle Fisher loss, and Markov-chain conditioning\\" + "\n"
               r"Theorem~\ref{thm:batch_restoration} \& Sec.~\ref{sec:kyle_hostoll}--\ref{sec:margin_scaling} & CDA arrival non-commutativity witness, fixed-price two-sided cleared-volume and uniform-fill permutation invariance, order-split linearity, moment-matched batch convolution, boundary snipe fraction algebra, joint Ho--Stoll carry reduction, and stressed-floor APC buffer bounds (\texttt{cda\_fifo\_noncommutative\_witness}, \texttt{two\_sided\_cleared\_volume\_perm\_invariant}, \texttt{batch\_two\_sided\_fill\_perm\_invariant}, \texttt{batch\_order\_split\_linearity}, \texttt{batch\_kernel\_convolution\_eq}, \texttt{jittered\_boundary\_snipe\_share}, \texttt{ho\_stoll\_joint\_carry\_reduction}, \texttt{apc\_margin\_buffer\_bounds}, \texttt{apc\_stressed\_lookback\_floor}) endogenous clearing-price monotonicity, Nyquist $\omega=\pi$ stability sign, and Huberman--Stanzl spread/fee no-arbitrage bound (\texttt{batch\_clearing\_price\_monotone}, \texttt{nyquist\_pi\_stability\_sign}, \texttt{huberman\_stanzl\_round\_trip\_no\_arb}) (\nolinkurl{PublicationRevision17.lean}, \nolinkurl{PublicationRevision18.lean}; \nolinkurl{Paper1FrequentBatchAuction.lean}, \nolinkurl{Paper1FragilityAndDesign.lean}) & Poisson/uniform jitter arrival clocks and continuous-time limit order book dynamics\\" + "\n"
               r"Proposition~\ref{prop:natural_exp} (Sec.~\ref{sec:natural_experiments}) & class-removal Difference-in-Differences kernel identity, second-order endogenous depth remainder, and turnover-orthogonal stock separation (\texttt{class\_removal\_kernel\_did}) (\nolinkurl{PublicationRevision17.lean}; \nolinkurl{Paper1FrequentBatchAuction.lean}) & cross-sectional regression identification and continuous-book queue transitions\\")
    doc = _rep_supp(
        doc,
        r"diagonalization\\Theorem~\ref{M-n:questions}",
        r"diagonalization\\" + "\n" + r"Theorem~\ref{M-n:questions}",
    )
    doc = _rep_supp(doc, s23_old, s23_new)
    doc = _rep_supp(doc, "144 modules", "145 modules")
    doc = _rep_supp(doc, r"existence with continuity; strict-loss case\\", r"compact existence (\nolinkurl{minimax_compact_existence}) and strict-loss dominance (\nolinkurl{minimax_strict_loss_dominance}) (\nolinkurl{PublicationRevision18.lean}); exchangeable-prior integration\\")
    doc = _rep_supp(doc, r"existence on compact $[0,1]^K$ and strict-convexity group-uniform uniqueness\\", r"group-uniform strict-cost uniqueness (\nolinkurl{minimax_partial_tags_strict_unique}, \nolinkurl{PublicationRevision18.lean}); compact existence via \nolinkurl{minimax_compact_existence}\\")

    symbols = (r"$B(z), B_h(z)$ & autocovariance generating functions $\sum_k \gamma_k z^{|k|}$ and $\sum_k \gamma_{k+h} z^{|k|}$\\" + "\n"
               r"$C_h(z)$ & holding covariance difference $2(B(z) - B_h(z))/(1-z)$\\" + "\n"
               r"$Q(z)$ & stationary inverse transfer factor $1 - z(a + J(z))$\\" + "\n"
               r"$J(z)$ & feedback generating function $\kappa \sum_{m \ge 0} k_m z^m$\\" + "\n"
               r"$\nu$ & desk quadratic position adjustment penalty parameter\\" + "\n"
               r"$\tau$ & desk transaction tax / per-trade execution cost\\" + "\n"
               r"$\Delta g'$ & jump in one-sided derivative of policy function at cap or exit kink\\" + "\n")
    if r"$B(z), B_h(z)$" not in doc:
        doc = doc.replace(r"$K_*$ & transfer-difference constant $2\kappa^2q/[\epsilon^3(1-S)^2]$\\" + "\n" + r"\bottomrule",
                          r"$K_*$ & transfer-difference constant $2\kappa^2q/[\epsilon^3(1-S)^2]$\\" + "\n" + symbols + r"\bottomrule")

    doc = _rep_supp(
        doc,
        r"$k_m,\ G(z)$ & feedback kernel and its transform\\",
        r"$k_m,\ G(z),$\newline $S_M(D)$ & feedback kernel, frequency transfer $G(z)=\sum_{m\ge0} k_m z^{-m}=z S_M(z)$, and main-text Stieltjes transform $S_M(D)=\int (D-r)^{-1}\,dM(r)$\\",
    )

    doc = _rep_supp(
        doc,
        r"Requirements above $4{,}096$ use the central-limit draw described in the text.",
        r"$^\dagger$All $K=3$ points ($>4{,}096$) and $K=2$ spacings below $0.25$ use the pre-specified covariance-matched Gaussian CLT draw (not heavy tails) because the 21-day archive contains $30{,}240$ one-minute bars; finite fourth moments ($\kappa_4 = 19.4$) inflate variance constants without altering the $(\Delta\eta)^{-(4K-2)}$ slope, whereas infinite-fourth-moment tails ($\alpha \in (2,4)$) slow passive covariance rates to $O_P(n^{-(1-2/\alpha)})$."
    )
    doc = _rep_supp(
        doc,
        r"\paragraph{A weight estimated from the same record.}",
        r"\paragraph{Finite-sample prefactor and heavy-tail discipline.} "
        r"The deterministic bound in \nolinkurl{PublicationRevision14.lean} shows that the leading estimation error scales with $2 B_{\mathrm{poly}} C_Q / [f_{\min}(1-s)]$, which is practical when the feedback-induced budget shift $\Delta S$ is economically sizable ($\Delta S \gtrsim 10^{-2}$, requiring $n \sim 10^4\text{--}10^6$), whereas tiny daily shares ($\Delta S \approx 2\times 10^{-4}$ in Table~\ref{M-tab:taiwan}) require unattainably long passive records. Under martingale-difference stochastic volatility with finite eighth return moments ($\E[\varepsilon_t^8] < \infty$), sample autocovariances retain the $O_P(n^{-1/2})$ rate with stationary block-bootstrap standard errors and \citet{mancini2009} threshold jump truncation; when tail indices lie in $\alpha \in (2,4)$, fourth-moment divergence slows covariance concentration to $O_P(n^{-(1-2/\alpha)})$."
        + "\n\n" + r"\paragraph{A weight estimated from the same record.}"
    )

    doc = _rep_supp(
        doc,
        r"\item \emph{A fixed unknown population in stationarity.} Assume a stationary solution with iid $N(0,\sigma^2)$ innovations, $\sigma>0$, and $W=\sum_iw_i>0$.",
        r"\item \emph{A fixed unknown population in stationarity.} Assume a stationary solution with nonnegative weights $w_i \ge 0$, $a \ge 0$, iid $N(0,\sigma^2)$ innovations, $\sigma>0$, and $W=\sum_iw_i>0$.",
    )

    thm_irr_proof = (
        r"\begin{proof}[Proof of Theorem~\ref{n:irr}]" + "\n"
        r"\emph{(i)} Recursive substitution of group feedback states from zero initialization (\nolinkurl{pos_closed}, \nolinkurl{positions_kernel}, \nolinkurl{initial_state_residual}) expresses every $q_i y_{i,t}$ as a measurable linear function of past prices $(x_0,\ldots,x_t)$, so $\mathcal{C}_t = \mathcal{P}_t$. Since $\varepsilon_{t+1}$ has mean zero and variance $\sigma^2$ independent of $\mathcal{P}_t$, both optimal predictors equal $a x_t + \kappa\sum_{m=0}^t k_m x_{t-m}$ with one-step mean squared error $\sigma^2$." + "\n"
        r"\emph{(ii)} Write $x_t = \sum_{j \ge 1} \phi_j x_{t-j} + \varepsilon_t$ with $\phi_1 = a + \kappa k_0$ and $\phi_j = \kappa k_{j-1} = \kappa\sum_i w_i r_i^{j-1}$ for $j \ge 2$. Under nonnegative feedback weights and $S < 1$, $|1 - e^{-i\omega}(a + J(e^{-i\omega}))| \ge 1 - S$ on $[-\pi,\pi]$, so the stationary spectral density satisfies $f(\omega) \le \sigma^2/(1-S)^2$. Applying Parseval's identity in $L^2(\mathbb{T})$ to the omitted tail projection error $\sum_{j > L} \phi_j x_{t-j}$ gives" + "\n"
        r"\[\begin{aligned}" + "\n"
        r"  0 \le A_L &\le \mathbb{E}\Bigl[\Bigl(\sum_{j > L} \phi_j x_{t-j}\Bigr)^2\Bigr]"
        r"  = \frac{1}{2\pi}\int_{-\pi}^{\pi} \Bigl|\sum_{j > L} \phi_j e^{-ij\omega}\Bigr|^2 f(\omega)\,d\omega \\" + "\n"
        r"  &\le \frac{\sigma^2}{(1-S)^2} \sum_{j > L} \phi_j^2"
        r"  \le \frac{\sigma^2(\kappa W)^2}{(1-S)^2(1-\bar r^2)}\,\bar r^{2L}," + "\n"
        r"\end{aligned}\]" + "\n"
        r"because $0 \le \phi_j \le \kappa W \bar{r}^{j-1}$ for every $j > L \ge 1$. Under $L_T = \lceil c\log T\rceil$ with $c\log(1/\bar{r}) > 1/2$, $T \bar{r}^{2L_T} \to 0$ (hence $A_{L_T} = o(L_T/T)$), and the common-row same-realization least-squares theorem of \citet[Proposition~2]{ingwei2005} with $K_T = \lfloor T^{1/(2+\epsilon)}\rfloor$ yields $\mathbb{E}(x_{T+1} - \hat{x}_{T+1})^2 - \sigma^2 = (\sigma^2 L_T/T)\{1 + o(1)\}$." + "\n"
        r"\end{proof}" + "\n\n"
    )
    doc = _rep_supp(
        doc,
        r"\subsection{Proofs}" + "\n\n\n" + r"\begin{proof}[Proof of Theorem~\ref{M-n:dual}]",
        r"\subsection{Proofs}" + "\n\n\n" + thm_irr_proof + r"\begin{proof}[Proof of Theorem~\ref{M-n:dual}]",
    )

    twse_context_old = r"For each stock, $x_t$ is the event-adjusted log price minus $\hat\beta$ times the log TAIEX, minus its trailing 60-day mean; it stands in for the model's pricing error, and its persistence partly reflects the detrending."
    twse_context_new = (
        r"During 2013--2016 TWSE stepped periodic call auction intervals down ($20\text{s}\to 15\text{s}\to 10\text{s}\to 5\text{s}$), expanded day trading in 2014, enforced daily price limits ($\pm 7\%$ before 1~June~2015 and $\pm 10\%$ thereafter), and broadcast daily T86 institutional totals at $15{:}00$~TST; later, on 23~March~2020 (inside the P1T 2019--2023 holdout), TWSE transitioned to continuous intraday matching. "
        r"For each stock, $x_t$ is the event-adjusted log price minus $\hat\beta$ times the log TAIEX, minus its trailing 60-day mean (estimated full-period within-sample; \nolinkurl{p1m_core.py} keeps stock means un-re-estimated inside bootstrap draws, inducing minor $-6.6\%$ relative Nickell distortion on $1-\hat a$ and mechanical Slutsky--Yule AR(1) persistence $118/121 \approx 0.9752$ on a random walk; \nolinkurl{p1m_core.py} also contains an unexecuted \texttt{exclude\_limits} flag and \texttt{price\_diff} specification verified on synthetic data in \nolinkurl{test_round2_fixes.py}). "
        r"Notice also that P1M uses \texttt{delay=1}: $u_{c,t}$ responds to $x_{t-1}$ and $x_t$ responds to $U_{t-1}$, yielding transfer $A(z) = 1 - \sum_j a_j z^j - \kappa z^{1+d} \sum_c w_c/(1 - r_c z)$ ($z^2$ loop for $d=1$ vs.\ $z^1$ in Eq.~(1)); in the contemporaneous $d=0$ sensitivity row below, contemporaneous endogeneity flips $\hat w_{\mathrm{Dealers}}$ positive ($+0.0328$), while aggregate \texttt{Dealers} ($w_D = -0.022$) conflates warrant hedging with proprietary book flow (isolating proprietary \texttt{DealerOwn} gives $\hat r_D = 0.190$ $[0.165, 0.216]$, $\hat w_D = +0.00295$ $[-0.00031, +0.00677]$, and $\hat H_D = 1.83\times 10^{-5}$)."
    )
    doc = _rep_supp(doc, twse_context_old, twse_context_new)

    doc = _rep_supp(
        doc,
        r"\paragraph{The ranges on the theory's class (P1M-A1, part A).} Protocol \nolinkurl{P1M_A1_protocol.md}, fixed before the run, recomputes the targeted and uniform ranges above with the alternative compositions restricted to memories in $[0,0.99]$, weights either all nonnegative (P, the class of the lower bounds) or with the signs of the tagged estimates (T), and memories at least $\gamma$ apart. The spectral-rate constraint, boxes and starts are P1M's. The reported endpoints come from feasible points visited by the search. Global extrema are unknown.",
        r"\paragraph{The ranges on the theory's class (P1M-A1, part A).} Protocol \nolinkurl{P1M_A1_protocol.md}, fixed before the run, recomputes the targeted and uniform ranges above with the alternative compositions restricted to memories in $[0,0.99]$, weights either all nonnegative (P, permitting corner zeros $w'_c = 0$ where three-group rules collapse toward one or two active classes; Theorem~\ref{M-n:shape}'s strict interior separation instead requires $w'_c \ge \omega_{\min} > 0$) or with the signs of the tagged estimates (T), and memories at least $\gamma$ apart. The spectral-rate constraint, boxes and starts are P1M's. The reported endpoints come from feasible points visited by sequential SLSQP runs (`best found', not global extrema, so local tolerance differences occasionally invert nested subset boxes, e.g.\ $U_{\max}=0.001835$ under the tight box vs.\ $0.001755$ under the primary box at $\gamma=0.02$).",
    )

    p1m_b_old = r"Effects are in units of $10^{-4}$, with 95\% intervals; the last column gives $\phi_1$ for Foreign, Trust and Dealers. The restricted estimates of the table above are 14, 4.2, $-$1.3 and 17."
    p1m_b_new = (
        r"Effects are in units of $10^{-4}$, with 95\% intervals; the last column gives $\phi_1$ for Foreign, Trust and Dealers. The restricted estimates of the table above are 14, 4.2, $-$1.3 and 17. "
        r"In the primary $J=10$ AR(2) Foreign regression (\nolinkurl{p1m_a1_partB_results.json}), the individual distributed lags are $(\hat\beta_{F,1},\dots,\hat\beta_{F,5}) = (-1.235, +0.741, +0.496, +0.229, +0.143)$ (cumulative sum $+0.341$; $\hat\phi_1 = 0.313, \hat\phi_2 = 0.167$), showing day-1 liquidity/slicing reversal followed by positive multi-day persistence."
    )
    doc = _rep_supp(doc, p1m_b_old, p1m_b_new)

    p1t_table = (
        "\n\n"
        r"\paragraph{Pre-registered 2019--2023 holdout (P1T Rule~4) and synthetic harness repairs.} Table~\ref{tab:p1t_holdout} summarizes all printed holdout metrics archived in \nolinkurl{p1t_holdout_A4_printed_output.txt} (2019--2023 out-of-sample holdout, $N=284$ eligible stocks; note that TWSE transitioned from 5-second call auctions to continuous matching on 23~March~2020 inside this window). While the pooled Foreign primary statistic passes ($\hat D = 0.0426$, block-60 $p=0.0024$), predictive power disappears in 2022--2023 ($+0.0141, -0.0158$), Trust and \texttt{DealerOwn} vanish under Holm correction ($p_{\mathrm{Holm}} = 1.0$; individual CIs, Rule~4 secondary \texttt{S2}, and \S7.4 sensitivities are omitted from the archived printed excerpt and only \nolinkurl{p1t_holdout_A4_printed_output.txt} values are tabulated), the reverse-causality diagnostic is negative ($\hat D = -0.0065$, $[-0.0316, +0.0165]$), and closed-form Rule~4 SE ratios (S3) fail against the bootstrap ($n=7$ valid stocks; median ratio $0.0238$ after excluding $286/293$ stocks whose fitted AR(1) feedback roots satisfy $|\hat r|\ge 1$ under 60-day detrending persistence). Executing the repaired pipeline in \nolinkurl{P1_Round3_Referee_Sensitivity_Colab.ipynb} (\nolinkurl{p1_round3_sensitivity_results.json}) yields limit-masked holdout $\hat D = 0.0410$ ($p=0.0000$, block-20 CI $[0.0197,0.0623]$, block-60 $p=0.0019$, reverse causality $\hat D=-0.0083$ $[-0.0332,+0.0150]$), pre-23-March-2020 5s call-auction $\hat D = 0.0319$ ($[0.0219,0.0415]$, $67.6\% > 0$) rising to $\hat D = 0.0421$ ($[0.0145,0.0701]$, $77.7\% > 0$) post-23-March-2020 continuous matching, limit-excluded P1M $\hat\kappa=0.00409$, and first-differenced P1M $\hat\kappa_{\Delta x}=0.00209$ ($[0.00163,0.00262]$), $\sum a_{\Delta x}=-0.109$ ($[-0.132,-0.088]$), $r_c\in[0.360,0.395]$."
        "\n\n"
        r"\begin{table}[!htbp]\centering\footnotesize" + "\n"
        r"\caption{Archived P1T Rule~4 out-of-sample holdout diagnostics (2019--2023, \nolinkurl{p1t_holdout_A4_printed_output.txt}).}\label{tab:p1t_holdout}" + "\n"
        r"\resizebox{\textwidth}{!}{\begin{tabular}{@{}lccc@{}}\toprule" + "\n"
        r"Diagnostic / subsample & Estimate $\hat D$ (or ratio) & 95\% block CI & Outcome ($n$)\\\midrule" + "\n"
        r"Primary Foreign (block 20) & $0.0426$ & $[0.0206, 0.0643]$ & $p = 0.0000$, $79.6\% > 0$ ($n=284$)\\" + "\n"
        r"Primary Foreign (block 10 / 60) & $0.0426$ & $[0.0235, 0.0616]$ / $[0.0156, 0.0709]$ & block-60 $p = 0.0024$\\" + "\n"
        r"Reverse causality diagnostic & $-0.0065$ & $[-0.0316, +0.0165]$ & median $\hat d = 0.0118$\\" + "\n"
        r"Calendar 2019 / 2020 / Feb--Jun 2020 & $0.0379$ / $0.0767$ / $0.0631$ & $[0.0279,0.0482]$ / $[0.0478,0.1057]$ / $[0.0337,0.0910]$ & supportive\\" + "\n"
        r"Calendar 2021 / 2022 / 2023 & $0.0985$ / $0.0141$ / $-0.0158$ & $[0.0470,0.1529]$ / $[-0.0230,0.0455]$ / $[-0.0543,0.0140]$ & 2022--2023 inconclusive\\" + "\n"
        r"S1 secondary (Trust / DealerOwn) & omitted in log & omitted in log & $p_{\mathrm{Holm}} = 1.0$ / $1.0$\\" + "\n"
        r"S3 closed-form / bootstrap SE & $0.0238$ (median) & IQR $[0.0166, 0.4130]$ & fail ($n=7$; $286/293$ $|\hat r|\ge 1$)\\" + "\n"
        r"\bottomrule\end{tabular}}" + "\n"
        r"\end{table}" + "\n\n"
        r"\begin{table}[!htbp]\centering\footnotesize" + "\n"
        r"\caption{TWSE P1M specification sensitivity across baseline, limit-excluded, and first-differenced models (\nolinkurl{p1_round3_sensitivity_results.json}).}\label{tab:p1m_sensitivity}" + "\n"
        r"\resizebox{\textwidth}{!}{\begin{tabular}{@{}lcccc@{}}\toprule" + "\n"
        r"Specification & Impact $\hat{\kappa}$ & Price $\sum \hat{a}_j$ & Memory rates $(\hat{r}_F, \hat{r}_T, \hat{r}_D)$ & Weights $(\hat{w}_F, \hat{w}_T, \hat{w}_D)$\\\midrule" + "\n"
        r"Baseline (updated panel) & $0.00375$ & $0.967$ & $(0.349,\, 0.414,\, 0.334)$ & $(0.238,\, 0.0655,\, -0.0225)$\\" + "\n"
        r"Exclude $\pm 7\%/\pm 10\%$ limit/halt days & $0.00409$ & --- & $(0.349,\, 0.398,\, 0.346)$ & $(0.258,\, 0.0604,\, -0.0236)$\\" + "\n"
        r"First-differenced price ($\Delta x_t$) & $0.00209$ $[0.00163,0.00262]$ & $-0.109$ $[-0.132,-0.088]$ & $(0.394,\, 0.395,\, 0.360)$ & ---\\" + "\n"
        r"\bottomrule\end{tabular}}" + "\n"
        r"\end{table}" + "\n\n"
        r"\begin{figure}[!htbp]\centering\includegraphics[width=.96\linewidth]{fig_twse_sensitivity.pdf}" + "\n"
        r"\caption{TWSE 2019--2023 holdout regime split (Panel~A) and P1M class-persistence stability across specifications (Panel~B).}\label{fig:supp_twse_sensitivity}\end{figure}" + "\n\n"
        r"\begin{figure}[!htbp]\centering\includegraphics[width=.96\linewidth]{fig_supp_fragility_equilibrium.pdf}" + "\n"
        r"\caption{Equilibrium saddle-node liquidity collapse (Panel~A) and Vieta conditional variance bound $V(\lambda_{\mathrm{crit}})<2\sigma_F^2$ (Panel~B) for Theorem~\ref{M-thm:fragility} ($A=0.5, \sigma_F=0.25, \sigma_\xi=0.35, \bar{a}=0.30, r=0.50$).}\label{fig:supp_fragility}\end{figure}" + "\n\n"
        r"\begin{figure}[!htbp]\centering\includegraphics[width=.96\linewidth]{fig_supp_surveillance_mpv.pdf}" + "\n"
        r"\caption{Surveillance paradox crowding rates (Panel~A, Proposition~\ref{M-prop:endogenous_supervisor}) and Section~\ref{app:passiveincidence} adaptive passive-incidence RMSE vs.\ the fixed-degree plateau (Panel~B, \nolinkurl{passive_diagnostics.json}).}\label{fig:supp_surveillance_mpv}\end{figure}" + "\n\n"
        r"\subsection{Structural natural-experiment designs: class bans and matching-interval transitions}\label{sec:natural_experiments}" + "\n"
        r"Because observational daily investor-class aggregates cannot by themselves isolate causal feedback from return-chasing or fundamental news, direct empirical falsification of Theorems~\ref{M-n:suff}, \ref{M-n:cost}, and~\ref{thm:batch_restoration} requires pairing order- or stock-level class tags with an exogenous regulatory or market-structure shock (implemented for TWSE's 23~March~2020 regime switch in \nolinkurl{P1_Round3_Referee_Sensitivity_Colab.ipynb}):" + "\n\n"
        r"\begin{proposition}[Difference-in-differences under selective class bans and batch-to-continuous transitions]\label{prop:natural_exp}" + "\n"
        r"Consider a cross-section of securities $i \in \{1,\dots,M\}$ governed prior to intervention date $T_*$ by $x_{i,t} = a_i x_{i,t-1} + \kappa_{i,0} \sum_{c} (k_i^{(c)} * x_i)_{t-1} + \varepsilon_{i,t}$:" + "\n"
        r"\begin{enumerate}" + "\n"
        r"  \item[(i)] \emph{Selective class ban and reinstatement (kernel DiD vs.\ unconditional turnover).} Suppose a regulation removes non-exempt trader class $S$ (with pre-ban short-lag feedback sum $K_{i,S} = \sum_{m=0}^{L-1} k_{i,m}^{(S)}$ and remaining classes $K_{i,\mathrm{rem}}$) while endogenous dealer impact adjusts linearly from $\kappa_{i,0}$ to $\kappa_{i,\mathrm{post}} = \kappa_{i,0} - d_{\kappa,i} K_{i,S}$ per Theorem~\ref{M-n:thm_inventory}(iv). Then total impact-weighted feedback $A_i = \kappa_i K_i$ changes by" + "\n"
        r"  \[" + "\n"
        r"    \Delta A_i = -(\kappa_{i,0} + d_{\kappa,i} K_{i,\mathrm{rem}}) K_{i,S} = -\kappa_{i,0} K_{i,S} - d_{\kappa,i} K_{i,\mathrm{rem}} K_{i,S}." + "\n"
        r"  \]" + "\n"
        r"  Endogenous depth re-optimization enters only through the second-order cross-product $-d_{\kappa,i} K_{i,\mathrm{rem}} K_{i,S}$; whenever $\kappa_{i,0} + d_{\kappa,i} K_{i,\mathrm{rem}} > 0$, $\Delta A_i$ strictly separates securities with distinct pre-ban feedback slopes $K_{i,S1} \neq K_{i,S2}$ even when class $S$ has identical unconditional turnover share $\bar V_{i,S}$ (\texttt{class\_removal\_kernel\_did}, \nolinkurl{PublicationRevision17.lean}), and reverses sign upon reinstatement." + "\n"
        r"  \item[(ii)] \emph{Batch-to-continuous matching regime switch and tagged audit shocks.} When a venue transitions from periodic uniform-price call auctions (e.g.\ TWSE's 5-second call auction prior to 23~March~2020) to continuous price-time priority matching, Theorem~\ref{thm:batch_restoration} predicts arrival-order invariance and uncongested moment-matched kernel equivalence pre-transition, whereas post-transition continuous message cancellation and latency preemption introduce non-commutative execution wedges scaling with quote-to-trade ratios and latency dispersion; under surveillance regime expansions (e.g.\ HFT or large-trader audit tags), Theorem~\ref{M-n:paradox}(iv) predicts memory dispersion $\hat\delta_i$ widens once inquiries decouple from price-only tests." + "\n"
        r"\end{enumerate}" + "\n"
        r"\end{proposition}" + "\n"
        r"\begin{proof}" + "\n"
        r"For~(i), expanding $\Delta A_i = (\kappa_{i,0} - d_{\kappa,i} K_{i,S}) K_{i,\mathrm{rem}} - \kappa_{i,0}(K_{i,\mathrm{rem}} + K_{i,S})$ yields $-(\kappa_{i,0} + d_{\kappa,i} K_{i,\mathrm{rem}})K_{i,S}$, whose difference from fixed-impact $-\kappa_{i,0}K_{i,S}$ is $-d_{\kappa,i} K_{i,\mathrm{rem}} K_{i,S}$, and for $K_{i,S1} < K_{i,S2}$ gives $\Delta A_{i,1} - \Delta A_{i,2} = (\kappa_{i,0} + d_{\kappa,i} K_{i,\mathrm{rem}})(K_{i,S2} - K_{i,S1}) > 0$ (\nolinkurl{PublicationRevision17.lean}). Part~(ii) combines Theorem~\ref{thm:batch_restoration}(i)--(ii) before $T_*$ with the CDA non-commutativity witness (\texttt{cda\_fifo\_noncommutative\_witness}) and Theorem~\ref{M-n:paradox}(iv) after $T_*$." + "\n"
        r"\end{proof}" + "\n"
    )
    p1m_b_end = (
        r"$J=10$, AR(1) & 14 [12, 17] & 3.1 [2.3, 4.1] & $-$0.94 [$-$1.3, $-$0.64] & 16 [13, 20] & 0.37, 0.40, 0.35\\" + "\n"
        r"\bottomrule\end{tabular}" + "\n"
        r"\end{center}"
    )
    doc = _rep_supp(doc, p1m_b_end, p1m_b_end + p1t_table)

    doc = _rep_supp(doc, '\\section{Proofs of the main results}', "\n\\subsection{Continuous double auctions, latency preemption, and frequent batch auctions}\\label{sec:latency_batch}\nIn a continuous double auction (CDA) matching engine operating under price-time priority, incoming orders from algorithms with heterogeneous communication latencies $\\ell_1 < \\ell_2$ do not aggregate additively. When a trading signal arrives, a faster desk sweeps resting top-of-book depth $Q_{\\mathrm{top}}$ before a slower Immediate-or-Cancel (IOC) order arrives, or cancels resting quotes (`zero-volume cancel race') ahead of marketable flow, making executed volume non-commutative: $\\mathcal{M}(u_1, u_2; \\ell_1, \\ell_2) \\neq \\mathcal{M}(u_2, u_1; \\ell_1, \\ell_2)$. Thus continuous-book latency preemption and message cancellation break additive linear kernel aggregation unless paired with asymmetric resting-quote protection (e.g., speed bumps delaying aggressive takes relative to passive cancels, paired with MiFID~II RTS~9 convex order-to-trade ratio tariffs alongside venue minimum resting times that exempt bona fide passive quoting) or discrete call clearing.\n\n\\begin{theorem}[Frequent batch auctions restore kernel sufficiency]\\label{thm:batch_restoration}\nDiscretize trading into frequent uniform-price call auctions \\citep{budish2015} over batch intervals $[T_{k-1}, T_k)$ with separate gross demand and supply schedules $D_k(p) = \\bar{D}_k(p) + \\sum_i u_{i,k}^+ \\mathbf{1}_{\\{p \\le p^{\\mathrm{cap}}_{i,k}\\}}$ and $S_k(p) = \\bar{S}_k(p) + \\sum_i u_{i,k}^- \\mathbf{1}_{\\{p \\ge p^{\\mathrm{floor}}_{i,k}\\}}$ (decomposition $u_{i,k} = u_{i,k}^+ - u_{i,k}^-$ against strictly monotone continuous exogenous limit schedules $\\bar{S}_k - \\bar{D}_k$), clearing price $p_k^* \\in \\arg\\max_p \\min(D_k(p), S_k(p))$, marginal-only \\citet{budish2015} uniform random tie-breaking (strictly dominating pro-rata rationing on congested branches, which otherwise rewards order padding and breaks $M^A = M^B$ net-flow equivalence under gross splitting), and either a deterministic baseline plus bounded uniform jitter $T_k - T_{k-1} = \\tau + \\tilde{\\zeta}_k$ ($\\tilde\\zeta_k \\sim U[0, \\tau_{\\mathrm{jitter}}]$) or an unbounded Poisson/exponential termination clock $\\mathrm{Exp}(\\lambda)$. Then:\n\\begin{enumerate}\n  \\item[(i)] \\emph{Arrival-order invariance and uncongested split linearity.} For any finite list of within-batch gross buy and sell submissions $\\{(u_{i,k}^+, u_{i,k}^-)\\}_{i=1}^K$ evaluated at clearing price $p_k^*$, two-sided cleared volume $V_k^* = \\min(D_k(p_k^*), S_k(p_k^*))$ and uniform-fill individual executions are strictly invariant to microsecond arrival permutations and linear under order splitting at fixed fill ratio (reducing identically to submitted net flow $u_{i,k}$ on the uncongested branch).\n  \\item[(ii)] \\emph{Uncongested kernel preservation and sniping bounds.} On the uncongested clearing branch with net flow invariance, any two trader populations matching power moments $\\sum_{i=1}^K w_i r_i^m = \\sum_{i=1}^K w'_i (r'_i)^m$ for $m < T$ generate pathwise identical batch net flows and pricing errors. Under an unbounded memoryless clock $\\mathrm{Exp}(\\lambda)$, boundary sniping probability is $1 - e^{-\\lambda \\Delta_{\\mathrm{lat}}} \\le \\lambda \\Delta_{\\mathrm{lat}}$; under $\\tau + U[0, \\tau_{\\mathrm{jitter}}]$ with $\\Delta_{\\mathrm{lat}} \\le \\tau$, unconditional arrival sniping is bounded by $\\Delta_{\\mathrm{lat}}/(\\tau + \\tau_{\\mathrm{jitter}})$, whereas conditional on surviving into the closing jitter window $[\\tau, \\tau+\\tau_{\\mathrm{jitter}}]$, residual sniping share is $\\min(1, \\Delta_{\\mathrm{lat}}/\\tau_{\\mathrm{jitter}})$.\n\\end{enumerate}\n\\end{theorem}\nThe CDA non-commutativity witness, fixed-price two-sided call-auction cleared-volume and uniform-fill permutation invariance, order-split linearity, batch kernel convolution, and sniping-fraction algebra are verified in Lean~4 (\\nolinkurl{PublicationRevision17.lean}); endogenous clearing-price monotonicity and stochastic clock distributions are proved on paper.\n\n\\section{Proofs of the main results}")

    doc = _rep_supp(doc, '\\section{The supervisory decision in detail}', "\n\\subsection{Dynamic Kyle filtering and flow-conserving Ho--Stoll quote shading}\\label{sec:kyle_hostoll}\n\\paragraph{Latent-fundamental Riccati filtering.}\nWhen $F_t$ is unobserved by market makers (distinct from the public-$F_t$ inventory benchmark of Remark~\\ref{M-rem:obs}), zero-expected-profit competitive dealers price only the unanticipated flow \\emph{innovation} $\\tilde{Y}_t = Y_t - \\E_{t-1}[Y_t] = \\tilde{Y}_t^F + \\xi_t$ via $p_t = \\hat{F}_{t|t-1} + \\beta_t \\tilde{Y}_t$ with stationary Kalman--Riccati gain $\\beta_t \\to \\beta^*$ (pricing raw predictable flow $Y_t$ would leave predictable returns $\\E_{t-1}[\\Delta p_t] \\neq 0$). Because $\\tilde{Y}_t$ and its innovation covariance depend on the population solely through the merged kernel $k_m$, the stationary filter gain $\\beta^*$ is invariant across moment-matched populations.\n\n\\paragraph{Flow-conserving Ho--Stoll quote shading.}\nIn the inventory economy, suppose dealers shade quotes around mid-price in proportion to end-of-period inventory pressure $\\kappa H_t$ \\citep{ho1981,avellaneda2008}: $p_t^{\\mathrm{ask}} = m_t + s_t/2 - \\kappa H_t$ and $p_t^{\\mathrm{bid}} = m_t - s_t/2 - \\kappa H_t$ (yielding pricing error $x_t$ aligned with CARA clearing). Shaded quotes attract contemporaneous price-elastic liquidity buyers/sellers $\\lambda_0 \\kappa H_t$ ($\\lambda_0 > 0$), enforcing exact inventory conservation $H_t = \\bar{a} H_{t-1} - Y_t - \\lambda_0 \\kappa H_t$, which solves to\n\\[\n  H_t = \\frac{\\bar{a}}{1 + \\lambda_0 \\kappa} H_{t-1} - \\frac{1}{1 + \\lambda_0 \\kappa} Y_t.\n\\]\nJoint quote shading and elastic liquidity absorption therefore \\emph{reduce} effective carry persistence to $\\bar{a}_{\\mathrm{eff}} = \\frac{\\bar{a}}{1 + \\lambda_0 \\kappa} \\in [0, \\bar{a})$ (strictly below $\\bar{a}$ when $\\bar{a} > 0$) and attenuate exogenous shock impact to $\\kappa / (1 + \\lambda_0 \\kappa) < \\kappa$ (verified in \\nolinkurl{PublicationRevision17.lean}), preserving Theorem~\\ref{M-n:thm_inventory}'s rational transfer structure.\n\n\\subsection{Mixed-sign stability, no-arbitrage spread bounds, and two-timescale dealer entry}\\label{sec:mixed_sign}\nThree structural boundary conditions discipline the linear equilibrium benchmark:\n\\begin{enumerate}\n  \\item[(i)] \\emph{Mixed-sign contrarian stability.} When contrarian desks carry negative weights ($w_i < 0$, as for dealers in Table~\\ref{M-tab:taiwan}), $S = a + \\kappa \\sum_i q_i < 1$ rules out a unit root at $\\omega = 0$ but does not prevent high-frequency cobweb oscillations at $\\omega = \\pi$. Necessary and sufficient Schur stability holds if and only if the causal lag polynomial $A(z) = 1 - z(a + \\kappa \\sum_{m \\ge 0} k_m z^m)$ has all zeros strictly outside the closed unit disk $|z| \\le 1$, equivalent to zero Nyquist encirclement of $0$ by $A(e^{-i\\omega})$ (requiring $A(1) = 1 - S > 0$ at $\\omega=0$ and $A(-1) = 1 + a + \\kappa\\sum_{m\\ge 0} (-1)^m k_m > 0$ at $\\omega=\\pi$, with sufficient condition $\\sup_{\\omega \\in [-\\pi, \\pi]} |a + \\kappa \\sum_{m \\ge 0} k_m e^{-i\\omega m}| < 1$), and worst-case $\\ell_1$ amplification uses $\\|h\\|_1 = \\sum_{t \\ge 0} |h_t|$ (whereas signed $S$ can fall below $\\|h\\|_1$ under alternating signs).\n  \\item[(ii)] \\emph{Spread and quadratic-fee bounds against round-trip manipulation.} In frictionless mid-quotes, non-symmetric or overshooting transient impact matrices $\\mathcal{K}$ ($\\mathcal{K}_{t,s} = h_{t-s}$ for $s \\le t$, symmetric part $\\mathcal{K}_{\\mathrm{sym}} = \\tfrac{1}{2}(\\mathcal{K} + \\mathcal{K}^\\top)$) admit round-trip pump-and-dump sequences $v = (v_0, \\dots, v_M)$ with $\\sum_t v_t = 0$ and $-v^\\top \\mathcal{K}_{\\mathrm{sym}} v > 0$ \\citep{huberman2004}. Writing $\\mu_* = \\max_{\\|v\\|_2 = 1} (-v^\\top \\mathcal{K}_{\\mathrm{sym}} v)_+$, unconstrained round-trip arbitrage is ruled out globally when quadratic execution fees satisfy $\\lambda_{\\mathrm{tc}} \\ge \\mu_*$ (or $\\mu_* = 0$, i.e.\\ positive-real transfer $\\min_\\omega \\operatorname{Re} H(e^{-i\\omega}) \\ge 0$); under a position/order size cap $|v_t| \\le \\bar{u}$ ($\\|v\\|_1 \\ge \\|v\\|_2^2/\\bar{u}$), adding an effective half-spread $s_{\\mathrm{eff}}/2$ rules out round-trips whenever $s_{\\mathrm{eff}}/2 \\ge (\\mu_* - \\lambda_{\\mathrm{tc}})\\bar{u}$.\n  \\item[(iii)] \\emph{Two-timescale dealer entry.} Theorem~\\ref{M-thm:fragility} characterizes intraday or crisis liquidity collapse under fixed dealer count $N$ and fixed aggregate risk tolerance $A^{-1}$. Over multi-month horizons with free entry at finite per-dealer setup cost $F_{\\mathrm{entry}} > 0$ ($A = \\gamma / N$), rising fee and spread revenue attracts dealer capital until zero-net-profit entry pins finite $N^*$ and $\\Lambda(D) > 0$ is restored, unfolding the fixed-$N$ saddle-node cliff into a smooth upward-sloping schedule.\n\\end{enumerate}\n\n\\subsection{Randomized hazard volatility interruptions and cross-venue coordination}\\label{sec:jittered_auctions}\nUnder a deterministic halt trigger $S_t \\ge \\bar{s}$---and likewise under a bounded uniform trigger $\\tilde{s}_{\\mathrm{trig}} \\sim U[\\bar{s}-\\delta_s, \\bar{s}]$, whose conditional hazard $(\\bar{s} - S_t)^{-1}$ still diverges at the upper endpoint $\\bar{s}$---forward-looking dealers anticipate illiquidity lock-up as $S_t \\uparrow \\bar{s}$ and collapse depth prematurely \\citep{subrahmanyam1994}. Mitigating pre-trigger magnet spikes favors a stress-thresholded excursion/imbalance hazard intensity $\\lambda_{\\mathrm{trig}}(|r_{t-1}|, \\Delta_{\\mathrm{imb}})\\,\\mathbf{1}_{\\{\\max(|r_{t-1}|/\\sigma_0,\\, \\Delta_{\\mathrm{imb}}/\\Delta_0) \\ge 1\\}} > 0$ (identically zero during calm zero-volatility sessions) transitioning into a randomized call-auction uncrossing interval $T_{\\mathrm{uncross}} = T_0 + \\tilde{\\epsilon}$, paired with randomized imbalance collars rather than unannounced opaque halts and cross-market LULD/futures coordination across SEC cash equities, CFTC futures, and ETFs.\n\n\\subsection{Pre-funded countercyclical margin buffers and maker-exempt fee incidence}\\label{sec:margin_scaling}\nRaising margin requirements mechanically as crisis stress rises (e.g., hyperbolic stress-escalating schedules) is procyclical: margin calls during drawdowns force leveraged fire sales and accelerate liquidity spirals \\citep{brunnermeier2009}. Instead, central counterparties mitigate procyclicality within EMIR RTS Art.~28 / SEC Rule~17Ad-22(e)(6) 99\\% MPOR VaR constraints via a stressed-lookback floor $m_{\\mathrm{floor}}^{\\mathrm{stress}}$ (anchoring initial margin on a 25\\%--50\\% stressed historical window) plus a countercyclical anti-procyclicality (APC) buffer $b_{\\mathrm{APC}}(1 - \\phi(\\hat\\sigma_t/\\sigma_{\\mathrm{calm}}))$ ($\\phi \\in [0, 1]$ nondecreasing):\n\\[\n  m_{\\mathrm{tot}}(\\hat{\\sigma}_t, Q_{c,t}) = \\max\\bigl(m_{\\mathrm{VaR},99}(\\hat{\\sigma}_t, Q_{c,t}),\\; m_{\\mathrm{floor}}^{\\mathrm{stress}} + m_{\\mathrm{conc}}(|Q_{c,t}|) + b_{\\mathrm{APC}}\\,\\bigl(1 - \\phi(\\hat{\\sigma}_t / \\sigma_{\\mathrm{calm}})\\bigr)\\bigr).\n\\]\nWhile stressed-lookback $m_{\\mathrm{floor}}^{\\mathrm{stress}} \\ge m_{\\mathrm{VaR},99}$ holds, releasing $b_{\\mathrm{APC}}$ offsets moderate volatility increases without procyclical margin hikes (checked in \\nolinkurl{PublicationRevision17.lean}); extreme shocks exceeding $m_{\\mathrm{floor}}^{\\mathrm{stress}}$ still trigger mandatory 99\\% VaR escalations. Moreover, CCP initial-margin schedules bind strictly on margined clearing-member accounts and cannot enforce uniform $\\theta \\mathbf{1}$ cuts on unmargined cash Securities Investment Trust Enterprises (`SITEs'), intraday-flat algorithmic desks ($Q_{c,\\mathrm{EOD}}=0$), or net-omnibus customer accounts; uniform prudential surcharges must therefore apply at the venue order-flow level, with MiFID~II RTS~8 exemptions restricted to registered market-making entities (and U.S.\\ NYSE/Cboe Designated Market Makers) rather than passive cancel-race quotes.\n\n\\section{The supervisory decision in detail}")

    doc = _rep_supp(doc, '\\section{Surveillance over time and against strategic traders}', "\n\\subsection{Elastic outside options and dynamic revelation audits}\\label{sec:elastic_exit}\nTheorem~\\ref{M-n:minimax} establishes minimax optimality of uniform cuts when active groups remain in the venue on $[0, 1]^K$. If anonymous groups possess heterogeneous elastic outside options (exiting to offshore or dark venues whenever $\\theta_c < \\underline{\\theta}_i$), an asymmetric schedule straddling $\\underline{\\theta}_i$ can achieve lower worst-case loss than a flat cut; restoring permutation-invariant optimality then requires conditioning retention schedules on observable liquidity-supply metrics. Similarly, to prevent multi-account shell splitting on the label simplex in Section~\\ref{app:relabel}, linear per-dollar penalties do not suffice; the mechanism must combine strictly superadditive or per-account beneficial-owner registration fees with volume- and price-excursion-contingent audit probabilities $\\pi_{\\mathrm{audit}}(V_c, |\\Delta p|)$ and clawbacks satisfying \\citet{border1987} monotone likelihood conditions, rendering multi-entity splitting strictly suboptimal.\n\n\\subsection{Non-Gaussian identification and bispectral polyspectra}\\label{sec:bispectrum}\nSecond-order power spectra $f(\\omega) = \\sigma^2 |B(e^{-i\\omega})|^2$ depend only on $|B(e^{-i\\omega})|$ and therefore cannot distinguish minimum-phase from non-minimum-phase transmission-zero reflections ($z_0$ versus $1/\\bar{z}_0$) in the innovation representation. When innovations have non-zero third cumulant ($\\E[\\varepsilon_t^3] = \\gamma_3 \\neq 0$), the bispectrum\n\\[\n  f_3(\\omega_1, \\omega_2) = \\frac{\\gamma_3}{(2\\pi)^2} B(e^{-i\\omega_1}) B(e^{-i\\omega_2}) B(e^{i(\\omega_1 + \\omega_2)})\n\\]\nrecovers the bispectral phase $\\psi(\\omega_1, \\omega_2) = \\arg B(e^{-i\\omega_1}) + \\arg B(e^{-i\\omega_2}) - \\arg B(e^{-i(\\omega_1 + \\omega_2)})$ \\citep{brillinger1965,hinich1982}, resolving transmission-zero reflections. However, for minimum-phase populations whose feedback memory poles $r_i \\in r_c + \\Delta\\eta[-1, 1]$ collide while matching moments $0, \\dots, 2K-2$, Taylor expansion of $f_3$ retains leading discrepancy $O((\\Delta\\eta)^{2K-1})$, so under non-Gaussian innovation laws satisfying sequential quadratic location-KL regularity ($\\mathrm{KL}(p(\\cdot - \\delta)\\|p) \\le C_{\\mathrm{loc}}\\delta^2$) replacing the Gaussian KL step of Section~\\ref{app:univirr} (Theorem~\\ref{M-n:univ}), the local $(\\Delta\\eta)^{-(4K-2)}$ sample-complexity barrier continues to hold.\n\n\\section{Surveillance over time and against strategic traders}")

    doc = _rep_supp(doc, '\\section{Notation}', "\n\\section{Rational inattention, solvency boundaries, and noise deconvolution}\\label{app:microfoundations}\n\n\\subsection{Microfounding exponential memory via subjective-AR(1) rational inattention}\\label{sec:inattention}\nIn the public-$F_t$ inventory benchmark (Remark~\\ref{M-rem:obs}), exponential memory rules represent boundedly rational or mandate-constrained execution schedules rather than frictionless full-information arbitrage (which would trade immediately against mean-reverting $x_t$). Formally, under dynamic LQG rational inattention \\citep{sims2003,mackowiak2009}, desk $i$ tracks $x_t$ using a capacity-constrained subjective AR(1) / persistent-trend working model with per-bit information flow cost $\\mu_i > 0$, yielding the steady-state Kalman recursion\n\\[\n  \\hat{x}_{i,t} = (1 - \\eta_i^*) \\hat{x}_{i,t-1} + \\eta_i^* x_t + \\tilde{\\xi}_{i,t}, \\qquad r_i = 1 - \\eta_i^*(\\mu_i) \\in (0, 1).\n\\]\nAs analyzed in Section~\\ref{sec:kyle_hostoll} and Remark~\\ref{M-rem:returns}, idiosyncratic channel-processing noise $\\tilde{\\xi}_{i,t}$ enters aggregate customer order flow as an additive variance component while leaving the deterministic feedback kernel $k_m = \\sum_i w_i r_i^m$ and closed-loop poles intact.\n\n\\subsection{Drawdown constraints and the domain of linear kernel sufficiency}\\label{sec:solvency}\nUnder unbounded Gaussian innovations, strict zero-ruin probability $\\mathbb{P}(\\inf_t W_{i,t} \\le 0) = 0$ is infeasible for any non-zero position rule. Realistic desks instead enforce mechanical state-dependent drawdown caps $|u_{i,t}| \\le \\bar{u}(W_{i,t})$ prior to risk-limit activation. Once wealth or position thresholds bind ($W_{i,t} \\le \\bar{W}_{\\mathrm{crit}}$), individual order flow becomes a nonlinear path-dependent functional of group-specific wealth histories, breaking global linear kernel sufficiency (Theorem~\\ref{M-n:suff}): two populations with identical linear kernels $k_m$ diverge pathwise as soon as a concentrated group hits its risk limit while split groups remain unconstrained. Theorem~\\ref{M-n:suff} therefore governs the interior well-capitalized mechanical-rule regime strictly prior to the first stopping time $\\tau_{\\mathrm{bind}}$ (pre-binding behavioral anticipation of $\\tau_{\\mathrm{bind}}$ would alter trading rules beforehand and lies outside fixed-rule sufficiency).\n\n\\subsection{Minimum price variation and stochastic dithering details}\\label{sec:mpv_supp}\nUnder discrete rounding $\\mathcal{Q}(p) = \\Delta_{\\mathrm{tick}} \\lfloor p / \\Delta_{\\mathrm{tick}} + 1/2 \\rfloor$, two regimes arise in Theorem~\\ref{M-thm:mpv}. First, under bounded innovations $\\|v\\|_\\infty \\le \\bar{v}$ whose baseline closed-loop trajectory satisfies $|p_t^A - m_t \\Delta_{\\mathrm{tick}}| + C_{\\mathrm{cl}}(\\bar{v} + \\|\\tilde{x}^A\\|_\\infty) (\\Delta\\eta)^{2K-1} < \\Delta_{\\mathrm{tick}}/2$ around integer tick indices $m_t$, $\\mathcal{Q}(p_t^A) = \\mathcal{Q}(p_t^B)$ identically (including closed-loop tick feedback; \\nolinkurl{PublicationRevision16.lean}) and $\\KL(P_{\\mathcal{Q}}^A \\| P_{\\mathcal{Q}}^B) = 0$. Second, under continuous Gaussian innovations $\\varepsilon_t \\sim N(0, \\sigma^2)$, noise crosses cell boundaries with positive probability (`stochastic dithering'): each tick cell $m$ has probability $p_m(\\mu_t) = \\Phi(((m+\\tfrac{1}{2})\\Delta_{\\mathrm{tick}} - \\mu_t)/\\sigma) - \\Phi(((m-\\tfrac{1}{2})\\Delta_{\\mathrm{tick}} - \\mu_t)/\\sigma)$ with derivative $\\partial_{\\mu} p_m(\\mu_t) = -\\sigma^{-1}[\\phi(((m+\\tfrac{1}{2})\\Delta_{\\mathrm{tick}} - \\mu_t)/\\sigma) - \\phi(((m-\\tfrac{1}{2})\\Delta_{\\mathrm{tick}} - \\mu_t)/\\sigma)]$, so shifting the conditional mean by $\\delta_t = O((\\Delta\\eta)^{2K-1})$ shifts cell probabilities by $\\Delta p_m = (\\partial_\\mu p_m(\\mu_t))\\,\\delta_t + O(\\delta_t^2)$. For EVERY $\\Delta_{\\mathrm{tick}} > 0$, quantized Fisher information $\\mathcal{I}_{\\mathcal{Q}}(\\mu_t) = \\sum_{m\\in\\mathbb{Z}} (\\partial_\\mu p_m)^2 / p_m$ is strictly positive (the $2\\sqrt{3}\\,\\sigma$ zero of $1 - \\Delta_{\\mathrm{tick}}^2/(12\\sigma^2)$ is solely a truncated small-tick expansion artifact as $\\Delta_{\\mathrm{tick}}/\\sigma \\to 0$); in stationary AR(1) records where both lagged and current prices are rounded (`HMM double quantization'), the small-tick Whittle Fisher efficiency for autoregressive persistence $a$ obeys $1 - (1 - a^2)\\Delta_{\\mathrm{tick}}^2/(6\\sigma^2) + O(\\Delta_{\\mathrm{tick}}^4/\\sigma^4)$ (generalizing via spectral curvature integration for higher-order feedback ARMA) alongside Markov-chain conditioning loss (\\nolinkurl{PublicationRevision16.lean}).\n\n\\subsection{Discrete Roll-bounce deconvolution vs.\\ infill pre-averaging}\\label{sec:preaveraging}\nWhen observed prices contain additive i.i.d.\\ microstructure noise $\\tilde{x}_t = x_t + \\eta_t$ with $\\E[\\eta_t] = 0$, $\\operatorname{Var}(\\eta_t) = \\sigma_\\eta^2$ \\citep{roll1984}, raw lag-zero sample autocovariances suffer $O(1)$ upward bias $+\\sigma_\\eta^2$, attenuating cepstral coefficients $\\ell_j$ and inducing spurious feedback poles. In our discrete-time unit-step ARMA model, $\\operatorname{Cov}(\\eta_t, \\eta_{t-m}) = 0$ for every lag $m \\ge 1$, so higher-lag sample autocovariances $\\hat{\\gamma}_m(\\tilde{x}) = \\gamma_m(x) + O_P(n^{-1/2})$ ($m \\ge 1$) remain unbiased. Crucially, naively subtracting an estimated noise variance $\\hat\\sigma_\\eta^2$ at lag~$0$ without joint Toeplitz positive-semidefinite regularization can produce negative deconvolved spectra ($\\tilde f^{\\mathrm{deconv}}(\\omega) \\le 0$) and hit spectral floors, while unrestricted high-order shifted Yule--Walker Hankel systems become rank-deficient once $L > K+1$. Instead, parametric estimation fits a positive rational ARMA/spectral factor $f_x(\\omega) = \\sigma_x^2 / |Q(e^{-i\\omega})|^2 \\ge f_{\\min} > 0$ directly to lags $m \\ge 1$ (or via Toeplitz-PSD-constrained Whittle/covariance matching), guaranteeing PSD spectra and restoring the $O_P(n^{-1/2})$ parametric rate. Conversely, in the high-frequency infill Ornstein--Uhlenbeck limit ($\\Delta_n \\to 0$), adjacent signal increments shrink relative to bounce noise, requiring level pre-averaged realized kernels over blocks $k_n = \\lceil c_w n^{1/2}\\rceil$ with triangle weights $w_j = \\min(u, 1-u)$ \\citep{jacod2009,barndorff2008} and noise-bias subtraction across $0 \\le m < k_n$, which yields the infill noise-limited rate $O_P(n^{-1/4})$.\n\n\\section{Notation}")

    doc = _rep_supp(
        doc,
        r"Across 96 draws at each size, the RMSE of the quadratic-cost budget estimate falls from 0.0353 at 512 prices to 0.0035 at 32,768 prices. This finite-design calculation shows the size of the errors. The rate in the theorem follows from the proof rather than the simulation.",
        r"Across 96 draws at each size (\nolinkurl{passive_diagnostics.json}), the data-driven estimator (\texttt{estimate\_adaptive}: lag/polynomial depth $L_n = \lceil c_{\mathrm{log}}(\hat\rho)\log n\rceil$, Bartlett-smoothed PSD floor, and two-fold split-sample cross-validated pilot norm bound without oracle \texttt{spectrum\_lower}, \texttt{coefficient\_bound}, or \texttt{radius}) reduces the RMSE of the quadratic-cost budget estimate monotonically from $0.01255$ ($n=512$) and $0.00768$ ($n=2{,}048$) to $0.00458$ ($n=8{,}192$) and $0.00232$ ($n=32{,}768$)---a $1.97\times$ reduction over the final $4\times$ sample increase matching the theoretical $n^{-1/2}$ rate (whereas under-truncated fixed $2\log n$ lags plateau near $0.0031$). The asymptotic $n^{-1/2}$ rate in the theorem follows from the proof rather than the simulation.",
    )

    doc, dropped = round9.tidy_bib(doc)
    return doc, n, dropped


def pdflatex(stem):
    r = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', stem + '.tex'], cwd=HERE,
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:])
        raise SystemExit(f'pdflatex failed on {stem}')


def check(stem):
    log = (HERE / (stem + '.log')).read_text(errors='replace')
    problems = []
    for pat in (r'Reference `[^\']+\' on page \d+ undefined', r'Citation `[^\']+\' on page \d+ undefined',
                r"Label `[^']+' multiply defined", r'Overfull \\hbox \([0-9.]+pt too wide\)',
                r'Token not allowed in a PDF string[^\n]*', r'destination with the same identifier[^\n]*'):
        problems += re.findall(pat, log)
    if 'There were undefined references' in log:
        problems.append('There were undefined references')
    return problems


def main():
    (HERE / (MAIN + '.tex')).write_text(make_short.build(make_short.SRC.read_text()))
    doc, n, dropped = supplement_tex()
    (HERE / (SUPP + '.tex')).write_text(doc)
    print(f'supplement: {n} references to the main text rewritten; {len(dropped)} uncited references dropped')
    for _ in range(3):
        pdflatex(MAIN)
        pdflatex(SUPP)
    pdflatex(MAIN)
    bad = {s: check(s) for s in (MAIN, SUPP)}
    for s, p in bad.items():
        print(s, 'problems:', len(p))
        for x in p[:20]:
            print('   ', x)
    if any(bad.values()):
        raise SystemExit('validation failed')
    pages = {}
    for s in (MAIN, SUPP):
        out = subprocess.run(['pdfinfo', str(HERE / (s + '.pdf'))], capture_output=True, text=True).stdout
        pages[s] = int(re.search(r'Pages:\s+(\d+)', out).group(1))
    combined = HERE / 'Paper1_JEDC_main_and_supplement.pdf'
    subprocess.run(['pdfunite', str(HERE / (MAIN + '.pdf')), str(HERE / (SUPP + '.pdf')), str(combined)], check=True)
    for dest in (ROOT / 'pdf_delivered', ROOT / 'ceiling_suite/papers/pdf_delivered'):
        dest.mkdir(exist_ok=True)
        for f in (MAIN + '.pdf', SUPP + '.pdf', combined.name):
            shutil.copy(HERE / f, dest / f)
    print(f'delivered: main {pages[MAIN]} pages, supplement {pages[SUPP]} pages')


if __name__ == '__main__':
    main()
