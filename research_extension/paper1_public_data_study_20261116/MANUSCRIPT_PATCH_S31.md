# Manuscript patch — S31.1 lock timestamp and candidate-list integrity

**For the session holding the manuscript source** (branch
`paper1-focused-validation-2026-11-14`, commit `3b8bc316`): apply these two
edits to the S31.1 subsection of the 141-page revision
(`Paper1_Observationally_Equivalent_Algorithms_Public_Data_Revision_2026-11-16`),
then rebuild. Both edits only make the text consistent with the delivered
`run_manifest.json`; no number, design, or result changes.

## Edit 1 — lock timestamp (consistency with run manifest)

FIND:

> The protocol was locked on 16 November 2026 before final-validation outcome extraction (SHA-256 4345510fd1d1b16021483a726494f0aafb21f3b7bc7045bc522c5c1d3204b40e).

REPLACE WITH:

> The protocol (SHA-256 4345510fd1d1b16021483a726494f0aafb21f3b7bc7045bc522c5c1d3204b40e) was locked before the final-validation outcome extraction recorded in the run manifest, which ran 15 November 2026, 22:33:53--22:36:30 UTC; 16 November 2026 is the manuscript revision date, not the lock time.

Rationale: the manifest's `started_utc` / `finished_utc` fall on 15 November UTC,
and `outcome_available_on_2026_11_16` is `false`. A referee diffing the
manuscript against the manifest will otherwise read the lock as post-dating the
run.

## Edit 2 — frozen candidate list hash (third-party reproducibility)

FIND:

> Addresses were ordered by ascending SHA256(Paper1-public-account-v1$\|$lowercase address), and the first 192 were queried.

REPLACE WITH:

> Addresses were ordered by ascending SHA256(Paper1-public-account-v1$\|$lowercase address), and the first 192 were queried. The frozen 192-candidate list has SHA-256 6d4fd1fbbac918f1bd97f5d3cb6ac79bc206a8cf9421147e70c05f37ab55ce58 (run manifest); the originating 47{,}705-row leaderboard frame snapshot is retained with its hash for third-party verification and will be deposited with the replication archive.

Rationale: the frame itself is not in the delivered zip, so selection is
currently checkable only through the 192-row ledger. Publishing the candidate
hash (already in the manifest) and archiving the frame hash closes the chain
47,705 -> 192 -> 60 without exposing anything new.

## After applying

1. Rebuild the PDF through your normal chain.
2. Recompute and record the new PDF SHA-256 in
   `research_extension/paper1_public_data_study_20261116/README.md`.
3. Push from the machine holding commit `3b8bc316` with
   `git pull --rebase origin paper1-focused-validation-2026-11-14` first —
   that branch now exists on the remote (integration commit `fa87234e`); do not
   force-push over it.
