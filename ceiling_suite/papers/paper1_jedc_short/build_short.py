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
