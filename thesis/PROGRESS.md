# Thesis completion progress

## A1 — 2026-10-22
Status: partial

What changed: `ch4_paper3.tex`, `ch5_conclusion.tex`, `appA_status.tex`,
`checks/check_dich_lower.py`, `checks/R_dich_lower.json`,
`verify_thesis_numbers.py`, and rebuilt `thesis.pdf`.

Result: The attempted local non-negative-coefficient proof is invalid. Taylor
truncation error only upper-bounds best approximation error, so it cannot imply
the claimed necessary Taylor depth. The proposed Gauss/Radau pair has zero tap
difference at every early matched moment and cannot simultaneously have the
asserted nonzero coefficient-aligned direction. The proposed KL calculation
also omits any observed taps beyond its selected prefix. Replaced it with a
written fixed-atom parametric lower-bound argument controlling divergence at
all observation depths. Deterministic evaluations for the safety, single-tap,
and discounted functionals verify admissibility, separation, divergence and
parametric scaling. Quadrature checks verify moment matching rather than
misrepresenting it as coefficient alignment. These are analytic diagnostics,
not an empirical/simulation experiment or validation of the full rate.
A cancellation family with an eventually strictly positive geometric tail also
refutes the full statement as written with constants uniform across the entire
coefficient class at a common accuracy. Its functional lies in a known interval
narrower than the requested accuracy, while its Taylor depth and coefficient
energy grow without bound. This does not settle a function-specific asymptotic
version or the all-non-negative coefficient restriction. The manuscript records
this distinction explicitly. The result artifact records the counterexample
and that a matching energy bound is not established; `--require-full` intentionally exits unsuccessfully. The original target remains visibly marked for reformulation; the
non-negative-coefficient restriction remains open.
No proof status was promoted and no new Lean coverage is claimed.

Checks: build ok (184 pages, no LaTeX errors); verify ok (76 paper numbers,
0 mismatches; A1 result recomputation and status guard pass); reproduce failed
at `TEXT DIFFERS versions/Paper2_JF` after 28 unit tests and all regenerated
numerical result comparisons passed; ruff ok; lean n.a. (not changed; the new
arguments remain unformalized). Representative final theory pages and the
status table were rendered and inspected. Existing box warnings remain, so
C3's warning-free requirement is not met.

Reproduction failure details: Paper 1, Paper 2 and Paper1_QE PDF comparisons
passed. The Paper2_JF word/number comparator reports a mismatch at token 19707
(33818 vs 33819 tokens). The extracted text includes different merged fragments
around an inline equation (`Proposispeed` versus `Proposid`), as well as different
reference extraction order. This may be platform/layout dependent, but is not
waived: the full local reproduction gate is failed. No paper source, delivered
paper PDF or comparator was changed to suppress the failure. The ledger stage
was checked separately by the successful paper-number verifier.

The existing remote run for the starting SHA was green:
https://github.com/Pratikn03/Fianince/actions/runs/39815122918
That run does not validate these new local changes. No new CI pass is claimed.

Open issues:
- Reformulate the refuted uniform statement, specifying the regularity
  normalization or a functional-dependent asymptotic threshold. Resolve the
  non-negative coefficient case with an attainable moment direction and KL
  control over all observed taps.
- Formalize any result before assigning a new proved tag under the task rules.
- The bridge to Corollary `cor:cases`(e) remains heuristic.
- The new thesis verifier covers the A1 artifact and its status only; it does not
  certify all inherited prose numbers. The paper verifier remains separate.
- A2–C3 have not been completed; the task order requires A1 acceptance first.

## Instruction routing and completion limits — 2026-10-22

The starting checkout was already synchronized to `origin/main` at
`4b3b154586858359449fba4fdfbdb5660693c16d`. This is Claude's retitled,
three-paper thesis. The supplied task file predates the reorganization:

| Old instruction location | Current location |
| --- | --- |
| Framework and nonlinear/learning theory | `ch4_paper3.tex` |
| Generated Paper 1 and Paper 2 chapters | `ch2_paper1.tex`, `ch3_paper2.tex` |
| Evidence E1/E2 and open problems | `ch5_conclusion.tex` |
| Beyond-markets grid/platoon sections | Absent in current thesis; no existing proposition to update |

Generated paper chapters were not edited by hand. The unfinished local proof,
script, malformed result JSON and PDF were preserved before replacement at
`/var/folders/pk/ksqc41pj60q3589gfwhqz5tw0000gn/T/thesis-a1-before-0d9_ga1c`.
This temporary backup is local recovery evidence, not a permanent release.

B1–B5 are not completed or preregistered by this change. E2 requires future data
collected after registration, including at least three months for its preferred
stream design. No retrospective result can satisfy that prospective requirement.
No data were downloaded and no future empirical outcome is asserted. No claim
is made that the thesis meets the supplied definition of done.

Human tasks still required: agree the co-authorship statement, obtain co-author
permission to include the papers, and decide journals and thesis submission.
