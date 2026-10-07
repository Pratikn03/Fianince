#!/bin/zsh
set -euo pipefail
revision_dir=${0:A:h}
repo_dir=${revision_dir:h:h}
/opt/homebrew/bin/python3.11 "$revision_dir/build_full_scope_appendix.py"
/opt/homebrew/bin/python3.11 "$revision_dir/update_manuscript.py"
cd "$repo_dir/paper"
for pass in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$revision_dir/build" -jobname=Machine_Markets_JF_Submission_Revised Machine_Markets_JF_Submission.tex > "$revision_dir/logs/rebuild_pass${pass}.txt" 2>&1
done
