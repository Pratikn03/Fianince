# Integrating the verified advanced run

This revision preserves the existing papers and records the returned Colab evidence and open work. Start with `Machine_Markets_Research_Status_20261030.pdf` and `RESEARCH_WORK_REGISTER.md`.

`returned_results.tex` and `work_register.tex` are shared by all six paper/thesis layouts and the standalone technical appendix. `remaining_work.json` carries explicit status and acceptance criteria. The empirical/theoretical experiment itself is not changed or rerun by this document update.

To rebuild the six layouts from repository root:

```bash
python studies/economic_review_20261029/build_updated_pdfs.py --out /absolute/output/directory --date-tag 20261030
```

Build `research_status.tex` in this directory, and `appendix.tex` in `studies/finite_horizon_costs_20261029/`, with three pdflatex passes each. The existing `integrate_results.py` is idempotent and preserves original formal blocks; do not use it to regenerate historical experiment outputs.

All changes are for author/co-author and specialist review. Seven scalar Lean certificates do not formalize the general theorem. No actual market-data run or first-in-literature conclusion is added.
