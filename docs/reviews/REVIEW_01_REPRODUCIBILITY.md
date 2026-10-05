# Review 1 — reproducibility and evidence integrity

## Scope

This pass inspected the next-stage scripts, saved JSON outputs, tests, the
generated paper, and the existing strict master-release verifier.

## Findings

1. **High — the legacy strict verifier is not a clean release gate.** The
   untouched master release already reports six missing or mismatched baseline
   artifacts, and the extension adds files that are intentionally outside the
   immutable master checksum manifest. A passing extension test suite cannot be
   reported as a strict master-release pass.
2. **Medium — raw empirical inputs are external to Git.** The L2 result is
   reproducible only when the T9 corpus is mounted. Absolute paths in the
   machine manifest are useful for provenance but are not portable paths.
3. **Medium — the original L2 runner hard-coded a 31-day expectation and did
   not record its own digest.** That could silently misdescribe a different
   corpus if the script were reused.

## Implemented remediation

- Added `docs/L2_CALIBRATION_REPORT.md` with corpus, hash, split, storage, and
  claim-boundary documentation.
- Extended the L2 runner with `--expected-days`, shared-date checks, pair-count
  metadata, source-date metadata, and a SHA-256 digest of the runner itself.
- Added unit tests for public CSV parsing and symbol/date pairing.
- Kept the legacy master manifest unchanged and disclosed its known strict-gate
  discrepancies rather than rewriting historical evidence.

## Residual status

The extension is reproducible from the recorded T9 corpus and its sidecar
checksums. A fresh-copy reproduction by an unaffiliated person remains an
external gate and is not claimed here.
