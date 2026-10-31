# Results of the tests registered on 31 October 2026 (commit 4ec2931)

Each test was opened once (unlock counters read 1).

## P1O (Binance, 1-30 October 2026), spec SHA-256 72cbc8ba...
- `zip/` holds the byte-exact contents of `p1o_results.zip` as returned by the author's Colab run (unlock `n = 1`, 2026-10-31T22:53:00Z).
- `colab_console_p1o_20261031.txt`: verbatim console output.
- Outcomes:
  - N2 FAIL, 1/30 (18 required); median out-of-sample R^2 gain -0.0001.
  - N3 FAIL, 5/30 (24 required).
  - N3-H2 FAIL, 21/30 (24 required).
  - N3-H3 PASS, 30/30 (median half-width ratio 1.69; theory 1.73).

## P11R (CFTC replication, 12 new markets), spec SHA-256 591e71c9...
- Unlock file: `n = 1`, 2026-10-31T22:35:36Z (copy in `P11R_unlocks.json`).
- Result file: `C6R_cot_replication.json`, in the author's Google Drive (`My Drive/ceiling_suite/results/`, Drive file id `1P0vaBwz3K4he2WvAOFOOXUg-HIO8PKG2`, 23,357 bytes, written 2026-10-31T22:37:10Z). It was read through the Drive connector on 2026-10-31. A byte-exact copy is still to be committed.
- Outcomes:
  - H1 PASS, 12/12.
  - H2 PASS, 11/12 (NQ negative).
  - H3 FAIL, 3/12 (GC, NQ, SI).
