# Execution and correction log

- Started at b5f0bdc8d75d56c159e879d32d7c8e81bf685252 on
  codex/paper-evidence-repair-20260926. Only the earlier two sealed research
  directories were untracked; no tracked modifications.
- Wrote protocol and 15 test cases before the new evaluator. Initial run:
  15 expected import errors (implementation absent).
- First implementation: 14 passed, one action-permutation test failed.
  Investigation showed outward interval sums depended on summation order
  by a few final decimal units, not a change in the exact action law.
  Canonical summation of exponential weights makes returned enclosures
  invariant to action relabeling. No experiment outcomes used in this fix.
- mpmath is not installed; the implementation uses Python's standard-library
  Fraction and Decimal. No packages or toolchains installed.
- Runner and verification tests were written before their modules (six and
  two expected missing-module errors respectively). Artifact tests likewise
  preceded the renderer. The post-hoc theory diagnostic had a failing
  missing-module test before implementation.
- Both 40- and 60-digit runs completed all 10,464 cells. All 1,744 exact greedy
  cells matched the sealed evaluator; 60 smooth cells matched independent
  full-history enumeration; 334,194 numeric values had compatible enclosures
  across precision runs. The complete clean-source rerun matched exactly.
- No production experimental failures or excluded states. Earlier TDD failures
  above are development failures, not excluded economic outcomes.
- After inspecting the grid, derived the restricted smooth-choice welfare
  proposition and direct-profit formula in THEORY.md. Explicitly post-hoc.
  Formula checks matched 1,090 comparisons over 545 state/temperature cases.
- Figures were generated only from verified outputs and visually inspected.
  Both show full denominators and redundant shape/hatching distinctions;
  scatter panels deliberately retain common axes and disclose overlap.
  No specialized color-vision simulation was performed.
- AI-assisted read-only review found no incorrect economic/numerical result,
  but reproduced three tooling defects: assert checks disabled by Python -O;
  missing enforcement of distinct 40/60 inputs; and incomplete exception/partial
  result retention. Four new regression tests failed before fixes and passed
  afterward. Prior source snapshots are in snapshots/pre_review and match the
  source digests recorded by verification/first.
- Corrected gates use explicit exceptions, validate every encoded precision,
  preserve preflight exception receipts and completed cells in interrupted
  runs. Filesystem write failure or an uncatchable process kill cannot guarantee
  a failure receipt; no durability claim beyond handled exceptions is made.
- Original p40/p60 outputs, first verification and v1 figures remain as
  superseded records. The scientific protocol, model.py and grid are unchanged;
  results/reviewed_p40 and reviewed_p60 rerun the same grid with corrected tooling.
- Follow-up review closed all three original findings. One minor malformed-
  metadata validation gap remains documented in REVIEW.md; accepted summaries
  have correct precision fields and all interval precisions were validated.
- Final verification/reviewed passed; final_repository_tests.txt records 439
  passing tests. Study suite has 31 tests. Native suites record 98 scientific
  and six release-tool tests. Artifacts/v2 binds the corrected receipts.
