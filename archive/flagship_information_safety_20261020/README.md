# Archived: "flagship" information-safety package (Theorems A–G numbering)

This package implemented an earlier draft of Paper 2's information-safety sections (labels `thm:flagship_A`–`G`). It was
replaced on 2026-10-20 by `research_extension/information_safety/` (identical to
`ceiling_suite/papers/research_extension/information_safety/`), which matches the current manuscript: Theorems
`thm:window`, `thm:certcost`, `thm:robustguard`, `thm:disclosure`, `thm:venuebb`; Propositions `prop:twoworld`,
`prop:hotelling`, `prop:venue`, `prop:probe`; Lemmas `lem:sound`, `lem:certnum`. See `MERGE_NOTES.md` there for the
module-by-module mapping. Kept for the record; not imported by any current code or test.

## paper2_flagship_sections/

The flagship information-safety sections of Paper 2 as committed in 357eb92 (`p2_information_safety.tex`,
`p2_appendix_information_safety.tex`, `p2_disclosure_value.tex`, `p2_robust_admission.tex`, `p2_theory2.tex` and the seven
`fig_flagship_*` figures). They are no longer part of the build: their content was integrated into
`p2_infosafety.tex`, `p2_guard.tex`, `p2_disclosure.tex`, `p2_t6.tex` and the appendix, and they are kept here unchanged.
