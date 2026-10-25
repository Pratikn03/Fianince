#!/bin/sh
# Builds the flagship paper. Numbers come from thesis/checks (thesis pipeline) and from robustness.py (exploratory);
# figures from make_figures.py; both read only committed result files.
cd "$(dirname "$0")/flagship"
python3 robustness.py >/dev/null && python3 make_figures.py >/dev/null
for i in 1 2 3; do pdflatex -interaction=nonstopmode identify_certify.tex >/dev/null 2>&1; done
echo "flagship: $(pdfinfo identify_certify.pdf | grep Pages)"; grep -i "undefined" identify_certify.log | head
