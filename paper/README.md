# Main paper

Read `Machine_Markets_Final_Integrated_Paper.pdf`. Its full self-contained source is
`Machine_Markets_Final_Integrated_Paper.tex`. This is the master edition of the version 0.5
scientific manuscript, not a separate new experiment. The original version 0.5 PDF/TeX pair is
preserved under `../studies/audited_constraints/paper/`.

The master edition retains the scientific text and all previously reported failures, adds a
section-level table of contents, changes the edition header, and appends a guide to complete
study packages, the evidence status, checks and pending scientific gates.

The bibliography, mathematical figure and original executable algebra listing are embedded.
No external `.bib`, image, data download or shell escape is required to compile. Use the root
helper: `python tools/build_paper.py --output ../Machine_Markets_Rebuilt.pdf`.

Required TeX packages: fontenc, inputenc, lmodern, geometry, amsmath, amssymb, amsthm, mathtools,
bm, microtype, booktabs, tabularx, longtable, array, enumitem, xcolor, graphicx, pgfplots, listings,
natbib, xurl, hyperref, cleveref and fancyhdr. A conventional TeX Live installation with these
packages is sufficient; the PDF itself requires no TeX installation.

The paper summarizes the complete result tables. Every individual CSV row and raw archive belongs
in the accompanying studies, not printed as thousands of pages. Data dictionaries explain which
raw paths were retained and which can be regenerated from seeds.
# Next-stage paper

The scoped follow-up manuscript is `Machine_Markets_Next_Research_Paper.tex`.
Its tables and figures are regenerated from
`studies/next_stage_validation/results/` by:

```bash
python3.11 studies/next_stage_validation/scripts/render_paper_artifacts.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error Machine_Markets_Next_Research_Paper.tex
pdflatex -interaction=nonstopmode -halt-on-error Machine_Markets_Next_Research_Paper.tex
```

This is a limited internally reproducible paper. It does not claim external
replication, full exchange calibration, authorship review, or publication
acceptance.
