# Number checks for the 21 November 2026 main text

| Number in the paper | Where | Check | Result |
|---|---|---|---|
| Table of years of daily data (8 rows x 2 margins) | Main text, Section 5 table | `check_table_years.py`: independent recomputation from the footnote (Whittle KL rate, n >= ln5/KL, 252 days) | all 16 entries agree to two significant digits |
| About 2.03 x 10^6 public-response repetitions; ceiling 0.375 | Main text, Section 7 figure | `../validation/intervention_figure.py` rerun | 2,026,833 (prints 2.03 x 10^6) |
| Nash example: entry gain 4.49, noise cost 3.49, w* = 0.032, payoff 0.0165 | Companion and Supplement S17.4 | `../nash/nash_float.py` | 4.486, 3.490, 0.0319, 0.0165 |
| Nash certificate bounds -3.17, -7.92, 8.5529, -69.145 | Supplement S17.4 | `../nash/nash_certify.py` (interval arithmetic) | as printed |
| Fitted slopes -0.02 and -3.02 (Monte Carlo of cheap and expensive questions) | Main text, Section 5 | `research_extension/theorem_checks/mc_questions.py` rerun with its fixed seed | -0.019 and -3.022; the stored results file is reproduced byte for byte |
| P7S readout: calm difference -0.002, 90% interval [-0.007, 0.004], difference in differences 0.041, p = 0.553 | Supplement S7 | read from `ceiling_suite/p1_empirics/results/p7s_eval_results.json` (the registered run of 11 Nov 2026) | matches |
| All 48 theorem checks (simulations behind Sections 5 and 6 and the companion) | Supplement | `research_extension/theorem_checks/run_all_checks.py` rerun | 48 of 48 pass (`run_all_theorem_checks_20261121.log`) |
| Disclosure-game closed forms | Proposition 7.4, Supplement S28 | `../t6/t6_check.py` | pass |

Not rechecked in this pass: the supplement's calendar-year figures for pooling (numerical hardest-pair search), and the 11-of-23 count of the companion empirical paper, which is cited, not computed here.

Notation: the H-class share in Proposition 7.4 and Supplement S28 is now chi (it was theta, which the main text also uses for types and the supplement for the insider's price convention).
