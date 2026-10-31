# Development sources that were never committed (archived 31 Oct 2026)

`dev_sources.tar.gz` holds 177 code and log files (about 1 MB) that existed only in the working container, outside
the repository, found by a content-hash comparison of every file outside the repository against every blob in the
repository's history (all branches). They are archived for completeness; none is cited by a paper.

| Folder | What it is |
|---|---|
| `p5`-`p10`, `p10b`, `xsec`, `depth`, `eq`, `suite`, `nbbuild` | Builders for the Colab notebooks (cell sources, `build.py`), local runners (`run_local.py`) and **fake-data generators** (`fake_*.py`, `debug_fake*.py`) used to smoke-test notebooks before the real Colab runs |
| `leanwork/InfoSafetyLean`, `leanwork/port` | A Lean 4 project (Paper 2 information-safety port) that built locally (984 jobs) but was never added to the repository's Lean projects |
| `theory` | Earlier versions of scripts whose current versions are in `ceiling_suite/theory/` |
| `outputs`, `papers`, `papers_snapshots`, `papers_local_before_sync_oct21` | Helper scripts and notes only (superseded PDF and LaTeX drafts were not archived) |

Deliberately **not** archived: about 3,300 result files (JSON, Parquet, CSV) written by the local runners on
**synthetic (fake) data** (`*/run/ceiling_suite_local/`, `depth/ceiling_suite_local/`, `eq/ceiling_suite_local/`).
They are debug outputs, not results, and must never be confused with the real Colab results, all of which are in
the repository (`p*res`, `realres`, `xres`, `depthres`). Superseded PDF/LaTeX drafts and plain-text extracts were
also left out.
