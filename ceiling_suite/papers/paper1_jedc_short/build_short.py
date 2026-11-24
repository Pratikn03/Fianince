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
    bib = t[b0:b1]
    doc = pre + '\\begin{document}\n' + body + '\n' + bib + '\n\\end{document}\n'
    doc, dropped = round9.tidy_bib(doc)
    doc = round9.longtable_newlean(doc)

    # ---------------------------------------------------------------- mathematical and editorial fixes
    mapping_old = r"Theorem~\ref{M-n:paradox} to Section~\ref{app:paradox}."
    mapping_new = (
        r"Theorem~\ref{M-n:paradox} and Proposition~\ref{M-prop:endogenous_supervisor} to Section~\ref{app:paradox}; "
        r"Theorem~\ref{M-thm:fragility} and Corollary~\ref{M-cor:posthaltflip} to Section~\ref{app:eqinv}; "
        r"Theorem~\ref{M-thm:mpv} to Section~\ref{app:microfoundations}; Proposition~\ref{M-thm:instruments} (Derived incidence) to Sections~\ref{app:instruments}--\ref{app:passiveincidence}."
    )
    doc = doc.replace(mapping_old, mapping_new)
    doc = doc.replace(", and a prospective window from November 2026 serves as a replication", "")
    doc = doc.replace(r"J'=TJT^{-1}={\rm diag}(0,r_1,\ldots)+uu^\top",
                      r"J'=TJT^{-1}={\rm diag}(0,r_1,\ldots)+uu^\top \succeq 0\text{ (since }r_i\ge 0\text{ and }uu^\top\succeq 0\text{, so }\lambda_\ell\ge 0)")
    doc = doc.replace("detection probability, and $k(\\delta_0-\\delta)^2$", "detection probability, $k(\\delta_0-\\delta)^2$")
    doc = doc.replace("1,238 named declarations", "1,265 named declarations")
    doc = doc.replace(r"13 November 2026 (Lean 4.34.1, Mathlib commit \texttt{d13f23b})",
                      r"23 November 2026 (Lean 4.34.1 commit \texttt{5045d00}, Mathlib commit \texttt{d13f23b})")
    doc = doc.replace(r"fourteen Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision14.lean}",
                      r"seventeen Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision17.lean}")
    doc = doc.replace("The uniform positive lower bound and the maximum principle bound $B$ away from zero",
                      r"The uniform positive lower bound on the unit circle and the minimum principle for harmonic functions (applied to $\operatorname{Re}B$) bound $\operatorname{Re}B$, and hence $|B|$, away from zero")
    doc = doc.replace("by Cauchy's inequality", "by Cauchy's integral estimate")
    doc = doc.replace("on on [0,1]^K", "on [0,1]^K")

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
               r"Fourier first-moment budget (\texttt{p1\_fourier\_first\_moment\_bound}, \texttt{sum\_j\_logCoeff\_le}, "
               r"\texttt{sum\_j\_logCoeff\_disk\_le}, \texttt{fourier\_first\_moment\_budget}, \texttt{fourier\_first\_moment\_disk}), "
               r"truncation tail (\texttt{fourier\_truncation\_tail}), spectral floor log-Lipschitz (\texttt{p1\_spectral\_floor\_log\_lipschitz}, "
               r"\texttt{spectral\_floor\_lipschitz}), quadrature error (\texttt{quadrature\_fourier\_error}), transfer factor and "
               r"function errors (\texttt{transfer\_factor\_error}, \texttt{transfer\_function\_error}), incidence estimator bound "
               r"(\texttt{incidence\_estimator\_bound}), end-to-end passive incidence assembly (\texttt{p1\_passive\_incidence\_end\_to\_end}) "
               r"(\nolinkurl{PublicationRevision14.lean}; \nolinkurl{Paper1PassiveIncidenceUpper.lean}) & "
               r"stationary Gaussian likelihood, spectral estimation, uniform central limit theorem, and Parseval isometry\\" + "\n"
               r"Theorem~\ref{M-thm:fragility} \& Cor.~\ref{M-cor:posthaltflip} & quadratic discriminant $\Lambda(D)$, critical threshold, effective depth collapse, and post-halt budget shift (\texttt{e4\_reduced\_form.py}, \texttt{e4\_fragility\_K.py}, \texttt{e3\_halt.py}, \texttt{every\_k\_halt\_check.py}) & continuous-time/discrete-time inventory clearing and dealer CARA optimization\\" + "\n"
               r"Proposition~\ref{M-prop:endogenous_supervisor} & unique Nash equilibrium crowding distance, surveillance collapse, and zero asymptotic information (\texttt{supervisor\_nash\_unique}, \texttt{surveillance\_collapse\_rate}, \texttt{surveillance\_information\_collapse}) (\nolinkurl{PublicationRevision15.lean}; \nolinkurl{endogenous_supervisor_check.py}) & Neyman--Pearson lemma and Gaussian shift experiment power envelope\\" + "\n" + r"Theorem~\ref{M-thm:mpv} & Minimum price variation resolution limit, sub-tick response bound, and zero divergence (\texttt{sub\_tick\_response\_gap}, \texttt{mpv\_threshold\_pos}, \texttt{zero\_divergence\_minimax\_risk}, \texttt{sample\_complexity\_infinite}, \texttt{mpv\_threshold\_mono}) (\nolinkurl{PublicationRevision16.lean}) & discrete tick quantization operator, metric entropy, and testing lower bounds\\" + "\n" + r"Theorem~\ref{thm:batch_restoration} & Frequent batch auction commutativity, latency preemption elimination, and kernel preservation (\texttt{batch\_two\_desk\_comm}, \texttt{batch\_three\_desk\_comm}, \texttt{batch\_kernel\_step}, \texttt{batch\_stability\_multiplier}) (\nolinkurl{PublicationRevision17.lean}) & uniform-price call auction clearing and continuous double auction priority\\")
    doc = doc.replace(s23_old, s23_new)

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

    doc = doc.replace('\\section{Proofs of the main results}', "\n\\subsection{Continuous double auctions, latency preemption, and frequent batch auctions}\\label{sec:latency_batch}\nIn a continuous double auction matching engine operating under price-time priority, incoming orders from algorithms with heterogeneous communication latencies $\\ell_1 < \\ell_2$ do not aggregate additively. When an aggressive trading opportunity arises, the faster desk ($\\ell_1$) sweeps resting limit order depth at the inside spread, shifting the best bid or offer. Slower incoming Immediate-or-Cancel (IOC) orders from the second desk ($\\ell_2$) arrive at an empty queue and are canceled with zero fill ($u_2^{\\mathrm{exec}} = 0$). Realized order flow is therefore governed by a non-commutative execution priority operator $\\mathcal{M}(u_1, u_2; \\ell_1, \\ell_2) \\neq u_1 + u_2$. In continuous double auctions with latency races, the linear aggregate convolution kernel $k_m = \\sum_i w_i r_i^m$ does not exist.\n\n\\begin{theorem}[Frequent batch auctions restore kernel sufficiency]\\label{thm:batch_restoration}\nDiscretize continuous trading into frequent batch auctions of fixed duration $\\tau > 0$ (Budish et al., 2015). Within each batch interval $[k\\tau, (k+1)\\tau)$, all submitted orders are accumulated without execution and cleared simultaneously at a single uniform price uncrossing. Then:\n\\begin{enumerate}\n  \\item[(i)] \\emph{Commutativity.} For any set of algorithmic orders $\\{u_{i,\\tau}\\}_{i=1}^K$ arriving at arbitrary microsecond timestamps within the batch, the executed volume is independent of arrival order: $\\mathcal{M}(\\{u_{i,\\tau}\\}) = \\sum_{i=1}^K u_{i,\\tau}$.\n  \\item[(ii)] \\emph{Kernel preservation.} If two trader populations match their power moments $\\sum_{i=1}^K w_i r_i^m = \\sum_{i=1}^K w'_i (r'_i)^m$ for $m < T$, their expected aggregate batch order flows and pricing errors are pathwise identical. The aggregate convolution kernel $k_m$ is structurally restored by the batch market design.\n\\end{enumerate}\n\\end{theorem}\nThe deterministic commutativity and stability properties are verified in Lean~4 (\\nolinkurl{PublicationRevision17.lean}).\n\n\\section{Proofs of the main results}")
    doc = doc.replace('\\section{The supervisory decision in detail}', "\n\\subsection{Dynamic Kyle filtering and Ho--Stoll quote shading}\\label{sec:kyle_hostoll}\n\\paragraph{Endogenous price impact via discrete algebraic Riccati equations.}\nLet competitive market makers update quotes via Bayesian filtering: $p_t = p_{t-1} + \\lambda_t Y_t$ with filtering gain $\\lambda_t = \\Sigma_{t|t-1} / (\\Sigma_{t|t-1} + \\sigma_\\xi^2)$, where conditional variance $\\Sigma_{t|t-1}$ tracks persistent customer flow. In stationary linear equilibrium, $\\lambda_t \\to \\lambda^*$, where $\\lambda^*$ is the unique positive root of the discrete algebraic Riccati equation. Because total customer order flow variance $\\operatorname{Var}(Y_t)$ depends on the trader population solely through the aggregate kernel $k_m$, the stationary gain $\\lambda^*$ is identical across moment-matched populations, preserving Theorem~\\ref{M-n:suff}'s kernel sufficiency under endogenous price impact.\n\n\\paragraph{Ho--Stoll inventory quote shading.}\nWhen dealers actively manage inventory risk by shading quotes around mid-price (Ho and Stoll, 1981; Avellaneda and Stoikov, 2008), posted bid and ask quotes satisfy $p_t^{\\mathrm{ask}} = m_t + s_t/2 - c_1 H_t$ and $p_t^{\\mathrm{bid}} = m_t - s_t/2 - c_1 H_t$. Inventory-induced quote shading introduces an endogenous mean-reverting drift in transaction prices $\\Delta m_{t+1} = -c_1 H_t + \\dots$, which maps directly into an effective inventory carry parameter $\\bar{a}_{\\mathrm{eff}} = \\bar{a} + c_1 \\in [0, 1)$, preserving the rational transfer function representation of Theorem~\\ref{M-n:thm_inventory}.\n\n\\subsection{State-contingent volatility auctions with randomized jittered clocks and magnet effects}\\label{sec:jittered_auctions}\nWhen trading halts are triggered by deterministic price or budget thresholds ($S_t \\ge \\bar{s}$), risk-averse dealers anticipate the imminent suspension of liquidity and widen bid-ask spreads or withdraw quotes entirely as $S_t \\to \\bar{s}$, generating a classic circuit-breaker magnet effect (Subrahmanyam, 1994; Lauterbach and Monroe, 1999). To eliminate this gaming margin, macroprudential market design replaces rigid halts with state-contingent volatility interruptions (call auctions) where the uncrossing time $T_{\\mathrm{uncross}} = T_0 + \\tilde{\\epsilon}$ is randomized uniformly over a jitter window $\\tilde{\\epsilon} \\sim U[0, \\tau_{\\mathrm{jitter}}]$. Because predatory traders cannot time-snipe the uncrossing instant, order submission during the call auction is incentive-compatible and liquidity collapse prior to the freeze is structurally mitigated.\n\n\\subsection{Dynamic anti-cyclical margin scaling linked to aggregate budget}\\label{sec:margin_scaling}\nCentral counterparties (CCPs) can operationalize the minimax optimal uniform feedback policy of Theorem~\\ref{M-n:minimax} without trader identification by linking regulatory initial margin requirements directly to the estimable aggregate budget $S$: $m(S) = m_0 / (1 - \\mu S)$ with $\\mu \\in (0, 1)$. Because leverage scales inversely with margin requirements ($L(S) \\propto 1/m(S) = (1 - \\mu S)/m_0$), leveraged algorithmic desks uniformly compress position sizing and trading intensity by factor $\\theta(S) = 1 - \\mu S \\in (0, 1)$. This macroprudential margin schedule implements the uniform scaling policy $\\theta \\mathbf{1}$ across all active desks through standard clearinghouse leverage channels, enforcing stability without requiring identity disclosure or individual desk tagging.\n\n\\section{The supervisory decision in detail}")
    doc = doc.replace('\\section{Surveillance over time and against strategic traders}', '\n\\subsection{Non-Gaussian identification and bispectral polyspectra}\\label{sec:bispectrum}\nWhile second-order power spectra $f(\\omega) = \\sigma^2 |B(e^{-i\\omega})|^2$ cannot distinguish rational transfer functions with identical polynomial moments through order $2K-2$, non-Gaussian innovations with non-zero third cumulant ($\\E[\\varepsilon_t^3] = \\gamma_3 \\neq 0$) generate a non-trivial bispectrum:\n\\[\n  f_3(\\omega_1, \\omega_2) = \\frac{\\gamma_3}{(2\\pi)^2} B(e^{-i\\omega_1}) B(e^{-i\\omega_2}) B(e^{i(\\omega_1 + \\omega_2)}).\n\\]\nThe bispectral phase $\\psi(\\omega_1, \\omega_2) = \\arg B(e^{-i\\omega_1}) + \\arg B(e^{-i\\omega_2}) - \\arg B(e^{-i(\\omega_1 + \\omega_2)})$ eliminates phase ambiguity and uniquely identifies the system poles $r_i$ (Brillinger, 1965; Hinich, 1982). Observational equivalence across distinct pole configurations is therefore strictly a feature of linear Gaussian systems or symmetrically distributed innovations.\n\n\\section{Surveillance over time and against strategic traders}')
    doc = doc.replace('\\section{Notation}', "\n\\section{Rational inattention and solvency microfoundations}\\label{app:microfoundations}\n\n\\subsection{Microfounding memory through rational inattention}\\label{sec:inattention}\nLet algorithmic trading desk $i$ maximize expected trading profits minus the information-processing cost of tracking market pricing errors (Sims, 2003; Mackowiak and Wiederholt, 2009):\n\\[\n  \\max_{\\mathcal{I}_i} \\E[\\Pi_i(u_{i,t}, x_t)] - \\mu_i \\mathcal{I}(x_t; \\hat{x}_{i,t}),\n\\]\nwhere $\\mathcal{I}(x_t; \\hat{x}_{i,t}) = -\\frac{1}{2}\\log(1 - \\rho_i^2)$ is Shannon mutual information and $\\mu_i > 0$ represents the desk's unit compute, server, and data-pipeline cost. Under Gaussian signal channels, the optimal information-constrained filter is an exponentially weighted moving average $y_{i,t} = (1 - \\eta_i^*) y_{i,t-1} + \\eta_i^* x_t$, where the optimal adaptation rate $\\eta_i^*(\\mu_i)$ is a strictly decreasing function of compute cost $\\mu_i$. Heterogeneous memory rates $r_i = 1 - \\eta_i^*$ thus reflect heterogeneous infrastructure latency costs, and clustering around $r_c$ reflects standard commercial hardware specifications.\n\n\\subsection{Dynamic robust control and terminal wealth solvency bounds}\\label{sec:solvency}\nTo rule out un-hedged wealth destruction, let desks solve an infinite-horizon robust portfolio problem (Hansen and Sargent, 2008) subject to a strict terminal wealth solvency constraint $\\mathbb{P}(\\inf_t W_{i,t} \\le 0) = 0$:\n\\[\n  \\max_{u_{i,t}} \\min_{\\nu_t} \\E_t \\left[ \\sum_{s=t}^\\infty \\beta^{s-t} \\left( u_{i,s}(p_{s+1} - p_s) - \\frac{\\lambda_i}{2} u_{i,s}^2 + \\theta_i \\mathcal{D}_{\\mathrm{KL}}(\\nu_s \\| P_s) \\right) \\right].\n\\]\nThe optimal policy scales trading intensity continuously with equity capital: $q_{i,t}^* = q_i \\cdot \\max(0, 1 - \\bar{W} / W_{i,t})$. As a desk approaches its capital floor, $q_{i,t}^* \\to 0$ endogenously. This eliminates artificial money-burning paths near instability, bounding total order-flow variance along every equilibrium trajectory.\n\n\\subsection{Minimum price variation resolution limit details}\\label{sec:mpv_supp}\nTheorem~\\ref{M-thm:mpv} establishes that discrete tick quantization introduces an absolute resolution limit. Under Minimum Price Variation $\\Delta_{\\mathrm{tick}}$, response differences below $\\Delta_{\\mathrm{tick}}/2$ produce identically zero variation on the quantized grid, rendering the sample complexity infinite. The deterministic threshold bounds are checked in Lean~4 (\\nolinkurl{PublicationRevision16.lean}).\n\n\\subsection{Pre-averaged realized kernels for microstructure noise deconvolution}\\label{sec:preaveraging}\nIn the presence of additive microstructure noise (e.g., Roll bid-ask bounce $\\tilde{p}_t = p_t + \\eta_t$ with $\\operatorname{Var}(\\eta_t) = s_{\\mathrm{spread}}^2 / 4$), raw sample autocovariances are contaminated by the noise variance at lag zero and non-zero bid-ask bounces. To restore consistency for the nonparametric Fourier spectral density estimator of Proposition~\\ref{M-thm:instruments}, the supervisor applies pre-averaging over sliding blocks of length $k_n = \\lceil c_w \\sqrt{n} \\rceil$ with smooth weight function $g(u) = \\min(u, 1-u)$ (Jacod et al., 2009; Barndorff-Nielsen et al., 2008):\n\\[\n  \\bar{x}_t = \\sum_{j=1}^{k_n - 1} g\\left(\\frac{j}{k_n}\\right) \\Delta \\tilde{p}_{t+j}.\n\\]\nThe pre-averaged realized autocovariance $\\hat{\\Gamma}_m = \\frac{1}{n} \\sum_t \\bar{x}_t \\bar{x}_{t+m} - \\frac{1}{2 k_n} \\hat{\\psi} \\delta_{m,0}$ eliminates the noise variance at rate $O_P(n^{-1/4})$. Substituting the pre-averaged spectral estimate $\\hat{f}(\\omega)$ into the Fourier inversion formula preserves the $O_P(n^{-1/2})$ rate of the derived incidence estimator up to the microstructure noise bandwidth constant.\n\n\\section{Notation}")
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
                r"Label `[^']+' multiply defined", r'Overfull \\hbox \([0-9.]+pt too wide\)'):
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
