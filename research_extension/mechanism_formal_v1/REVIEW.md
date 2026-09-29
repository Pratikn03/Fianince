# Internal review and correction record

Date: 2026-09-27 UTC. Both reviewers were AI agents in this workflow, not
unaffiliated human reviewers. No external-review gate is satisfied.

## Literature reviewer

Read-only review completed and closed. See `LITERATURE_CHALLENGE.md` for exact
sources and reading scope. Verdict: a restricted, exact strategic-accommodation
example; not a new learning mechanism merely because the choice is one-shot
deployment. No full literature-review or novelty-clearance claim.

## Fresh code/proof reviewer

Reviewed the new formal package, approved economic contract, executable exporter,
bridge, and integrity checks. A separate literal-history implementation reproduced
all 20 payoff cases over 58,320 histories (reviewer-reported reproduction).
The main implementation independently reproduced the 20 cases through the
sealed dossier calculator. No economic or proof-statement defect was established.

Three Important verifier defects were reproduced, so the reviewer requested
changes to the integrity claim:

1. A source-line theorem inventory missed an imported indented theorem using a
   custom axiom to prove False. Kernel replay alone accepts declared axioms.
2. Clean-copy checks hashed the original tree, not the actually executed copy;
   a substituted fixture-printing exporter escaped that check.
3. An empty dossier file inventory satisfied the generic hash check vacuously.

All three entered one correction pass. Regression tests failed before the new
checks existed. The correction inventories theorem/axiom declarations from
Lean's elaborated local modules; binds both original and executed inventories at
each acceptance boundary; and pins the exact approved dossier-manifest digest.
The Lean regression uses a real miniature compiled project containing a foreign-
namespace indented theorem and a custom axiom, not a mocked audit result.

Post-fix targeted suite: 10 tests passed, including all three regressions.
A second reviewer was not dispatched; final acceptance depends on fresh tests,
clean build, full axiom audit, kernel replay, and exact comparison after fixes.

## Scope rulings

- Preserve the old formal scaffold and dossier; add this separately named
  package in the current evidence-repair checkout. Cost: users must distinguish
  the variants rather than assume the old scaffold gained coverage.
- Certify fixed default parameters first. Cost: continuous epsilon/alpha and
  arbitrary-horizon claims remain unformalized, not silently generalized.
- Review exclusions remain pending research: general normalization/invariance,
  full history-recursion equivalence, mixed-equilibrium formalization, Python
  refinement, novelty, empirical validity, independent human review.
- No minor findings were supplied in the review's final verdict.

Reviewer reproductions remain in `/tmp/mm-formal-review.RKly1C/`; the actionable
defects are also captured by the versioned regression tests. Temporary artifacts
are supporting diagnostics, not the durable accepted release.
