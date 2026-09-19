# Full-horizon research implementation plan

Goal: execute the user's specified equal-information comparison and provide auditable positive and negative evidence.
Architecture: immutable v1 provenance; regenerated full measurements; estimator module accepting only declared inputs; experiment runners; separate verification scripts; results-driven report.
Tech stack: Python 3.13, NumPy, SciPy NNLS/HiGHS, pytest; LaTeX and python-docx for reports.
Spec: docs/RESEARCH_PROTOCOL.md.

1. Run and record the v1 tests; inspect the source archive. Completed before this plan.
2. Write tests for rate-bin envelopes, single-rate recovery, off-grid containment, information boundaries, and ambiguous pairs. Run before implementation and retain the failing log.
3. Implement estimators; run all tests and benchmark runtime without outcome-based hyperparameter tuning.
4. Regenerate original full inputs and verify every previously saved measurement.
5. Run all 86,400 paired rows and predetermined resolution checks. Save partial chunks while running, combine deterministically, retain failures.
6. Prove and numerically check the Gaussian hidden-mode identification lower bound. Recheck the exact v1 construction in rational arithmetic.
7. Verify numerical outputs, test an alternate LP solver, and reproduce a predetermined subset in a clean directory.
8. Write a primary-source literature/claim audit, detailed paper, and findings summary from saved results. Render documents and inspect.
9. Hash final files, test ZIP integrity, preserve the old release, and deliver the new separate archive.
