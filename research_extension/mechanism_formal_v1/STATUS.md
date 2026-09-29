# Accepted bounded formal package

Verified 2026-09-27 UTC / 2026-09-26 America/Chicago.

Accepted run: `verification/final_clean/report.json` (`passed: true`). This is
the post-review clean-copy run. Earlier `first`/`clean_initial` reports are
retained but superseded for integrity claims. `fixed_initial` is the repaired
incremental run, not the accepted clean-copy reproduction.

## Fresh verification

- Lean 4.29.1 clean build: passed. No external packages or toolchains installed.
- 26 hand-written theorem statements, including actual model-derived default
  payoffs, unique pure equilibrium, planner choice, and a null counterexample.
- All 115 local theorem declarations, including generated auxiliaries, found
  from the elaborated environment and checked for permitted transitive axioms.
- Kernel replay of all five local modules: passed.
- Cross-language exact agreement: 16 zero-cost profile/mask cases, four costed
  profiles, and 54 settlement branches. Not a universal Python refinement proof.
- Post-fix Python suite: **408 passed**. Command:
  `python3.11 -m pytest -q -p no:cacheprovider tests research_extension/tests reference_directory research_extension/mechanism_dossier_20260926 research_extension/mechanism_formal_v1`.
- Native isolated runner earlier in this turn: **98 scientific + 6 release-tool
  tests passed**. Logs are under `verification/native/`.
- Bare repository-wide pytest: 12 legacy `src`-package collection errors.
  Preserved studies require their isolated runner; these errors were not hidden
  or represented as passing.
- Seven claim records resolve to audited theorem declarations; the central
  private-gain, gross-welfare and costed-gap numbers match the accepted fixture.
- Prior dossier preservation: 23 local and 31 reference-source hashes unchanged.
- No tracked manuscript/source changes outside this new package; the prior
  untracked dossier remains present. No commit, push, training, emails, or submission.

## Scientific status

The finite default-parameter example is now model-derived and kernel-checked.
It remains post-hoc, initialization-sensitive and within an established
strategic-teaching/accommodation channel. Its welfare changes depend on low-ask
participation in the specified economy; no broad finance or systemic-risk claim
is certified.

Pending: continuous-parameter formalization, arbitrary-horizon equivalence,
general normalization, mixed-equilibrium formalization, meaningful robustness,
novelty clearance, trained-population confirmation, independent human review,
and publication requirements. The main PDF was intentionally not edited.

The next high-value step is a separately specified robustness/characterization
study that asks whether the private/social deployment distinction survives
non-tied learning states and a smooth second learning rule. Large training runs
remain premature until that contribution and design are justified.
