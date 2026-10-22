#!/bin/sh
# Build the thesis: regenerate Chapters 3 and 4 from the paper sources, then compile three times.
set -e
cd "$(dirname "$0")"
python3 make_chapters.py
for i in 1 2 3; do pdflatex -interaction=nonstopmode thesis.tex >/dev/null 2>&1 || true; done
if grep -q "^!" thesis.log; then grep "^!" thesis.log | head; exit 1; fi
grep "Output written" thesis.log
grep "LaTeX Warning" thesis.log | sed 's/on input line.*//' | sort | uniq -c || true
