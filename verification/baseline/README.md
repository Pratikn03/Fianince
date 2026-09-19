# Baseline verification record

This directory records the WP00 checkpoint for the frozen master release. The
machine-readable summary is in `BASELINE_SUMMARY.json`; interpretation and the
full discrepancy list are in [`docs/BASELINE_AUDIT.md`](../../docs/BASELINE_AUDIT.md).

The strict verifier did not pass at this checkpoint. Its six discrepancies are
preserved in the summary and audit. The release test suite and original algebra
checks passed. No missing log or checksum entry was recreated merely to make the
strict verifier green.
