#!/bin/sh
cd "$(dirname "$0")/paper2"
cat p2_front.tex p2_theory1.tex p2_t6.tex p2_infosafety.tex p2_guard.tex p2_disclosure.tex p2_equil.tex p2_evidence.tex p2_thin.tex p2_istests.tex p2_close.tex p2_appendix.tex > paper2.tex
for i in 1 2 3; do pdflatex -interaction=nonstopmode paper2.tex >/dev/null 2>&1; done
echo "paper2: $(pdfinfo paper2.pdf | grep Pages)"; grep -c Overfull paper2.log; grep -i "undefined\|multiply" paper2.log | head; grep -A3 "^! " paper2.log | head -20
