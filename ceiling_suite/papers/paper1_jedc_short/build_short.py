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
        r"Proposition~\ref{M-thm:instruments} (Derived incidence) to Sections~\ref{app:instruments}--\ref{app:passiveincidence}."
    )
    doc = doc.replace(mapping_old, mapping_new)
    doc = doc.replace(", and a prospective window from November 2026 serves as a replication", "")
    doc = doc.replace(r"J'=TJT^{-1}={\rm diag}(0,r_1,\ldots)+uu^\top",
                      r"J'=TJT^{-1}={\rm diag}(0,r_1,\ldots)+uu^\top \succeq 0\text{ (since }r_i\ge 0\text{ and }uu^\top\succeq 0\text{, so }\lambda_\ell\ge 0)")
    doc = doc.replace("detection probability, and $k(\\delta_0-\\delta)^2$", "detection probability, $k(\\delta_0-\\delta)^2$")
    doc = doc.replace("1,238 named declarations", "1,256 named declarations")
    doc = doc.replace(r"13 November 2026 (Lean 4.34.1, Mathlib commit \texttt{d13f23b})",
                      r"23 November 2026 (Lean 4.34.1 commit \texttt{5045d00}, Mathlib commit \texttt{d13f23b})")
    doc = doc.replace(r"fourteen Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision14.lean}",
                      r"fifteen Lean~4 files, \nolinkurl{PublicationRevision.lean} to \nolinkurl{PublicationRevision15.lean}")
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
               r"Proposition~\ref{M-prop:endogenous_supervisor} & unique Nash equilibrium crowding distance, surveillance collapse, and zero asymptotic information (\texttt{supervisor\_nash\_unique}, \texttt{surveillance\_collapse\_rate}, \texttt{surveillance\_information\_collapse}) (\nolinkurl{PublicationRevision15.lean}; \nolinkurl{endogenous_supervisor_check.py}) & Neyman--Pearson lemma and Gaussian shift experiment power envelope\\")
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
