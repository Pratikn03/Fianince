# Internal adversarial review, 2026-09-27

Review type: AI-assisted, read-only. Reviewer identifier:
01a0e4de-0cbc-7fc1-81d8-a5db73dde48e (Wegener). No independent human review,
attribution approval, novelty clearance, or publication decision is implied.

## Scope and scientific findings

The reviewer inspected the protocol, evaluator, interval method, tests, runner,
verifier, and THEORY.md. It compared the sealed prior evaluator and independently
checked the completed receipts. It found no economic or numerical error that
invalidated the completed outputs. In particular it checked chosen-action
updates, timing of observations, mandatory frozen refresh, accounting, ties,
abstention, interval operations, contrasts, and deployment-cost treatment.

It also checked the three reward-change events in the smooth welfare proof:
ask 4 receives 2 -> 4 with probability 1/8; ask 6 receives 0 -> 3 with
probability 1/8, and 0 -> 1 with probability 3/8. Those updates strictly
decrease next-period softmax ask-2 probability. The direct private-profit
formula was also checked. There is no uniform negative margin as temperature,
learning rate, exploration, or Q values approach limiting regimes.

## Reproduced defects and corrections

1. **Optimized Python skipped verifier assertions.** A test launched Python
   with `-O` and demonstrated disjoint enclosures accepted by the original
   verifier. All its verification assertions were replaced by explicit
   exception gates. Regression test now rejects disjoint inputs under `-O`.
2. **Distinct 40/60 inputs not enforced.** The corrected verifier rejects
   repeated input paths and requires the expected precision in each summary
   and every encoded interval. Mixed/wrong-precision regressions pass.
3. **Failure records incomplete.** Preflight was outside the handler, and a
   failure during the next state could lose completed cells held in memory.
   The corrected create-only runner writes a preflight failure receipt and
   partial records containing completed states plus cells in an interrupted
   state. An injected failure at cell 18 retains 17 computed cells. This does
   not promise recovery after disk failure or an uncatchable process kill.

All four regression cases failed before correction and passed after it.
Original source snapshots match the hashes recorded by verification/first.
Original results, receipts, and artifacts/v1 were preserved as superseded
records. Both precision grids were rerun with corrected tooling. Every one
of the six numerical result blocks per precision is byte-identical to its
pre-correction version; provenance records appropriately differ.

## Verification of corrected version

- 31 study tests; 439 combined repository tests.
- Native suites separately: 98 scientific tests and six release-tool tests.
- 10,464 payoff cells per precision, with no excluded economic states.
- 1,744 exact-reference cells matched.
- 334,194 numeric comparisons across precisions passed.
- 60 separate 100-digit, 2,916-history calculations enclosed.
- Complete clean-source replay matched.
- All 23 + 60 sealed files and five locked manuscript/source files unchanged.

The full scalar-history cross-check is diagnostic, not a second proof of
Decimal rounding or external replication. Broad test counts do not establish
novelty or external validity.

The reviewer rechecked the corrections and closed all three original findings,
with no remaining P1/P2 defect in that scope. A **minor metadata-validation gap**
remains: when an expected precision is supplied, read_checked does not require
the summary's precision field to be present. It still validates all actual
interval precisions. Both accepted summaries contain the correct integer
precision, independently checked by the reviewer. This gap does not invalidate
these outputs; it prevents describing the schema validator as exhaustive or
unconditionally fail-closed for every malformed metadata input. Harden it in
the next tooling revision, with a new verification receipt.

## Deliberately unresolved

Novelty, human proof/economic review, real-market calibration, longer horizons,
trained-candidate prevalence, mixed-equilibrium analysis, and formalization of
the new smooth proposition remain outside this bounded study. The reviewer did
not audit graphical layout or descriptive near-zero fields; the main agent
checked the generated figure/table bindings and visually inspected the PNGs.
