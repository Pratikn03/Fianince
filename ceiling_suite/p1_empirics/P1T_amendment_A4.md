# P1T amendment A4: one index-row label on 2019-04-29 (APPROVED 8 November 2026)

**Status.** Proposed on 8 November 2026, after the holdout notebook's integrity gate stopped the run and before any
statistic was computed. The holdout counter is 0. Approved by the author ("approve", 8 November 2026) and logged in `P1T_unlocks.json`. In force.

## What happened (logged as it came out)

1. The holdout notebook downloaded 2013-01-02 to 2023-12-29: 2,691 trading days, of which 1,216 are holdout days.
   The integrity gate failed on one day: `mi_bad_days = ['20190429']`. Every other check passed.
2. A metadata-only diagnosis showed that the MI_INDEX response for 2019-04-29 is complete:
   - stat OK;
   - a 1,091-row quote table, against 1,091 on 2019-04-26;
   - a 51-row price-index table;
   - the same layout as 2019-04-30.

   T86 for that day is normal (988 rows).
3. A label-only listing printed no values. It showed that TWSE used short row labels in that day's price-index table.
   - The weighted index (TAIEX) is `加權股價指數` at row 1, where it is `發行量加權股價指數` on 2019-04-26.
   - Other rows are shortened too, for example `寶島指數` for `寶島股價指數`.
   - The registered parser matches the exact name, so the index was missing for that one day.

## The amendment

- **How the label is read.** In the MI_INDEX table titled `…價格指數(臺灣證券交易所)`, a row labelled exactly
  `加權股價指數` is read as `發行量加權股價指數`. That applies on 2019-04-29 only, provided the table has exactly one
  such row and no row with the registered name.
- **When the run stops.** Any other occurrence of the alias stops the run before any statistic. The notebook asserts
  that the relabelling was applied on exactly that one day.
- **What is not changed.** The executor (`p1t_executor.py`, sha256 `8d8a70a3…`), the spec, the readout, the gate's
  other checks, and the stored data. Nothing is downloaded again.
- **Notebook.** `P1T_Holdout_A4_Colab.ipynb`, built by `make_holdout_A4_notebook.py` from the unchanged holdout
  notebook.

## Test on simulated responses (`test_holdout_A4.py`, `test_holdout_A4_results.json`)

- **Without A4.** With the alias planted on 2019-04-29, the unamended analysis stops at the gate with
  `mi_bad_days = ['20190429']`. This reproduces the failure.
- **With A4.** It passes the gate, applies the alias exactly once on `20190429`, and gives a primary result identical
  to the run on unaliased data.
- **Alias on another day** (2020-02-28): A4 stops before any statistic, and no primary file is written.

## Why this is not a change of method

The relabelled row is TWSE's own weighted index for that day. It is the same row, at the same position, in the same
table as on the neighbouring days, so the registered statistic is the one computed. Without A4, the registered rule
would have to treat the day's index as missing, which is a gap in the parser, not a decision of the spec.
