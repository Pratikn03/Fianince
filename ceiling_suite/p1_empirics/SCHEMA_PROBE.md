# Schema probe (Phase 2), declared 7 November 2026 before any download

**Purpose.** Learn the field layout, units, sign conventions and identifiers of candidate tagged-flow sources.

**What it is not.** It is not a test.
- No estimator is run.
- No outcome is computed.
- No price or flow series is inspected beyond the first rows needed to read the layout.

**Burned days.** Every day touched by the probe is excluded from every later confirmatory sample.
- TWSE, three major institutional investors, per stock (report T86): trading dates 2024-01-02 and 2024-01-03.
- TPEx, three major institutional investors, per stock: same two dates.
- JPX, weekly trading by type of investors: the file for the first week of January 2024.
- NSE, participant-wise F&O trading volume: trading date 2024-01-02.
- KRX: documentation only. Its per-stock investor-type download needs a session, so no file is requested.

**Hyperliquid.** It is not probed. The author's commitment (H1 unlock counter 0) keeps H1 Hyperliquid data closed
until 2026-12-10. That is a self-imposed analysis boundary, not a statement about data availability.

**Outputs.**
- `schema_probe_results.zip` containing the raw responses, one `schema.json` per source and a log.
- `schema.json` records columns, types, row counts, encoding, the first three rows, and request URLs with HTTP status.

**Run location.** The author runs the notebook in Colab, because this workspace cannot reach the exchanges.
