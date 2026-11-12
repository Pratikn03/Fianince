# P1T readout, amendment R1 (12 November 2026): the JEDC theory version does not report the Taiwan test

- **Decision:** the authors (Pratik Niroula, 12 November 2026), after the holdout result was known (run once,
  8 November 2026, reading B).
- **What changes:** rule 3 of `P1T_HOLDOUT_READOUT.md` (the primary verdict appears in the abstract, the empirical
  section and "What we do not claim") no longer applies to the theory version submitted to the Journal of Economic
  Dynamics and Control (`papers/paper1_note/paper1_theory.tex`, built by `build_note.py`). That version makes no
  empirical claim about the feedback premise and does not mention the Taiwan test.
- **What does not change:** the registered result, its reading (B) and its wording. Every other version that reports
  the test (the full working paper, the core version, the note and its RFS submission build) keeps the reading-B text
  word for word. The specification, amendments, executor, results and this file stay public in the repository.
  `EMPIRICAL_LEDGER.md` keeps row E24.
- **Why:** the authors judge the theory version should rest on its theorems; the Taiwan test bears on the feedback
  premise of the full working paper.
- **Risk recorded at the time of the decision:** the test is public in the repository the paper cites, and a reader who
  finds a registered test of the model's premise not mentioned in the paper may read the omission as selective
  reporting. The alternative considered and not chosen was to keep it in Supplement Section S7 only.
- Recorded by an AI system at the authors' instruction.
