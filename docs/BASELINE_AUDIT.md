# WP00 baseline audit

## Scope

This audit records a fresh repository-level baseline from the isolated
WP00/WP01 worktree. It distinguishes the current Git-published release from
the original checksum manifest and from historical execution logs.

## Environment

| Item | Observed value |
|---|---|
| Python | 3.11.14 |
| NumPy | 2.3.5 |
| SciPy | 1.17.1 (installed environment; release requirement declares 1.17.0) |
| pandas | 3.0.3 (installed environment; release requirement declares 2.2.3) |
| pytest | 9.0.2 |
| Platform | macOS arm64, Python 3.11 |
| Worktree | isolated WP00/WP01 worktree |

## Executed commands

| Command | Exit | Result |
|---|---:|---|
| `python3.11 tools/verify_master.py --strict` | 1 | Six checksum discrepancies and 30 unlisted files; details below |
| `python3.11 tools/verify_master.py` | 1 | Same six checksum discrepancies; unlisted files are non-fatal without `--strict` but errors remain |
| `python3.11 tools/run_all_tests.py --log-dir /tmp/mm_wp00_tests` | 0 | 98 scientific tests and 6 release-tool tests passed |
| `python3.11 studies/observable_stress_tests/provenance/verify_original_algebra.py` | 0 | 625 scalar and 250 network checks passed; max reported errors were floating-point roundoff |

## Checksum discrepancies

The strict verifier reported 502 verified files and six errors:

1. `.gitignore` differs from the original `SHA256SUMS.txt` because the Git
   publication added `.DS_Store` to the ignore list.
2. `studies/audited_constraints/logs/final_latex.log` is absent from the
   published checkout.
3. `studies/full_horizon_audit/results/reproduction_progress.log` is absent.
4. `studies/full_horizon_audit/results/run_progress.log` is absent.
5. `studies/full_horizon_audit/results/sensitivity_progress.log` is absent.
6. `verification/PAPER_BUILD.log` is absent.

The new `research_extension/` files are intentionally outside the old master
checksum manifest. They have their own generated evidence manifest under
`research_extension/outputs/evidence_manifest.json`.

These differences are recorded, not repaired by editing the old checksum file.
The missing files are execution logs, not reported result arrays, but their
absence prevents a strict claim that the Git checkout is byte-identical to the
original extracted release.

## Scientific baseline

- All four native study suites passed in the fresh worktree.
- The release launcher reports `full_experiments_rerun: false` and
  `external_replication: false`.
- The algebra verifier is a numerical check of the specified restricted model,
  not an empirical market or trained-agent result.
- No data, paper, or historical result was changed during WP00.

## Acceptance decision

WP00 is `DONE_INTERNAL`: baseline execution and discrepancies are recorded.
The original release is not promoted to a strict byte-identical archive until
the six discrepancies are resolved in a separately versioned release process.
