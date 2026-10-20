#!/bin/sh
# Clean-environment reproduction of everything in the package that does not need market data (Gate 8 of the blueprint).
# Usage:  sh reproduce_clean.sh Papers_LaTeX_and_Scripts_Oct2026.zip      (or a folder with the same layout)
# Needs: python3 (3.11+), pdflatex, pdfinfo, pdftotext, unzip. Creates a temporary folder; touches nothing else.
set -e
# The argument is the replication zip or a folder laid out like it (e.g. ceiling_suite/papers in the repository).
SRC="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
W=$(mktemp -d); echo "working in $W"; cd "$W"
if [ -d "$SRC" ]; then cp -r "$SRC" papers; else unzip -q "$SRC"; fi
cd papers
rm -rf research_extension/information_safety/.pytest_cache research_extension/information_safety/__pycache__
echo "== 1. fresh virtual environment"
python3 -m venv venv; . venv/bin/activate
pip install -q -r research_extension/information_safety/requirements_lock.txt
python3 -c "import numpy, scipy, mpmath; print('numpy', numpy.__version__, 'scipy', scipy.__version__, 'mpmath', mpmath.__version__)"
echo "== 2. unit tests and all data-free results"
cd research_extension/information_safety
mv results results_archived; mkdir results
python3 -m pytest -q tests
python3 run_all.py
python3 compare_results.py results_archived results
cd ../..
echo "== 3. recompile both papers and both journal versions from source"
sh build_p1.sh; sh build_p2.sh
python3 versions/build_versions.py
for f in paper1/paper1 paper2/paper2 versions/Paper1_QE versions/Paper2_JF; do
  pdftotext -layout "$f.pdf" "$f.rebuilt.txt"; pdftotext -layout "pdf_delivered/$(basename $f).pdf" "$f.delivered.txt"
  if cmp -s "$f.rebuilt.txt" "$f.delivered.txt"; then echo "IDENTICAL TEXT $f"; else echo "TEXT DIFFERS $f"; diff "$f.rebuilt.txt" "$f.delivered.txt" | head -5; fi
done
echo "== 4. every ledger number from the archived real-data results"
python3 verify_paper_numbers.py
echo "== done: all checks passed"
