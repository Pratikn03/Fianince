#!/bin/sh
# End-to-end clean reproduction of the October 2026 paper suite (Paper 1 and Paper 2), from this repository.
#   1. copies ceiling_suite/papers to a fresh temporary folder and creates a fresh Python virtual environment;
#   2. runs the 28 unit tests and every data-free result (T01-T15) and checks each equals the committed result;
#   3. recompiles both papers and both journal versions from the LaTeX sources and compares them with the committed PDFs;
#   4. recomputes every row of Paper 2's ledger of pre-registered tests from the archived real-data result files;
#   5. checks that research_extension/information_safety is the same code as the copy inside ceiling_suite/papers;
#   6. (unless SKIP_LEAN=1) builds the Lean 4 + Mathlib formalization and runs its axiom audit.
# Market data are not downloaded: the real-data results are reproduced by re-running the Colab notebooks (Parts 1-18).
# Needs python3 (3.11+), pdflatex, pdfinfo, pdftotext, and for step 6 elan/lake.
set -e
ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT"
echo "== code identity"
diff -rq --exclude=__pycache__ --exclude=.pytest_cache research_extension/information_safety ceiling_suite/papers/research_extension/information_safety
echo "identical"
sh ceiling_suite/papers/reproduce_clean.sh "$ROOT/ceiling_suite/papers"
if [ "${SKIP_LEAN:-0}" != "1" ]; then
  echo "== Lean 4 + Mathlib formalization"
  cd "$ROOT/research_extension/current_manuscript_lean_20261008"
  lake exe cache get || echo "(Mathlib cache unavailable: building from source)"
  lake build
  lake env lean AxiomAudit.lean
fi
echo "== paper suite reproduction complete"
