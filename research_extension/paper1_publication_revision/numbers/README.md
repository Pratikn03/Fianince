# Number checks for the 21 November 2026 main text

| Number in the paper | Where | Check | Result |
|---|---|---|---|
| Table of years of daily data (8 rows x 2 margins) | Main text, Section 5 table | `check_table_years.py`: independent recomputation from the footnote (Whittle KL rate, n >= ln5/KL, 252 days) | all 16 entries agree to two significant digits |
| About 2.03 x 10^6 public-response repetitions; ceiling 0.375 | Main text, Section 7 figure | `../validation/intervention_figure.py` rerun | 2,026,833 (prints 2.03 x 10^6) |
| Nash example: entry gain 4.49, noise cost 3.49, w* = 0.032, payoff 0.0165 | Companion and Supplement S17.4 | `../nash/nash_float.py` | 4.486, 3.490, 0.0319, 0.0165 |
| Nash certificate bounds -3.17, -7.92, 8.5529, -69.145 | Supplement S17.4 | `../nash/nash_certify.py` (interval arithmetic) | as printed |
| Disclosure-game closed forms | Proposition 7.4, Supplement S28 | `../t6/t6_check.py` | pass |

Not rechecked in this pass: simulation slopes quoted from earlier runs (for example the fitted slopes -0.02 and -3.02 in Section 5), the supplement's calendar-year figures for pooling, and the registered empirical readouts, which come from their own result files.
