#!/bin/sh
# Build generated paper chapters, then compile the current thesis with strict error handling.
set -eu
cd "$(dirname "$0")"
"${THESIS_PYTHON:-python3}" make_chapters.py
build_dir=$(mktemp -d "${TMPDIR:-/tmp}/machine-markets-thesis.XXXXXX")
trap 'rm -rf "$build_dir"' EXIT HUP INT TERM
for i in 1 2 3; do
  if ! pdflatex -recorder -output-directory="$build_dir" -halt-on-error -file-line-error -interaction=nonstopmode thesis.tex > "$build_dir/build-pass.log" 2>&1; then
    cp "$build_dir/thesis.log" thesis.log
    tail -60 "$build_dir/build-pass.log"
    exit 1
  fi
done
cp "$build_dir/thesis.log" thesis.log
if grep -Eq 'There were undefined references|There were undefined citations|Rerun to get cross-references right' thesis.log; then
  grep 'LaTeX Warning' thesis.log
  exit 1
fi
cp "$build_dir/thesis.pdf" thesis.pdf
cp "$build_dir/thesis.fls" thesis.fls
grep "Output written" thesis.log
grep "LaTeX Warning" thesis.log | sed 's/on input line.*//' | sort | uniq -c || true
