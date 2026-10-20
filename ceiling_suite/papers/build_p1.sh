#!/bin/sh
cd "$(dirname "$0")/paper1"
cat p1_front.tex p1_ident.tex p1_account.tex p1_mixture.tex p1_disclosure.tex p1_empirics.tex p1_appendix.tex > paper1.tex
for i in 1 2 3; do pdflatex -interaction=nonstopmode paper1.tex >/dev/null 2>&1; done
echo "paper1: $(pdfinfo paper1.pdf | grep Pages)"; grep -c Overfull paper1.log; grep -i "undefined\|multiply" paper1.log | head
