#!/bin/sh
# paper1/paper1.tex is the single source of Paper 1. The split files p1_*.tex are regenerated from it
# (split_sources.py) for the older tools that still read them; never edit the split files by hand.
cd "$(dirname "$0")/paper1"
python3 split_sources.py
for i in 1 2 3; do pdflatex -interaction=nonstopmode paper1.tex >/dev/null 2>&1; done
echo "paper1: $(pdfinfo paper1.pdf | grep Pages)"; grep -c Overfull paper1.log; grep -i "undefined\|multiply" paper1.log | head
