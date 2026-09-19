# v0.5 implementation plan

Goal: extend v0.4 with auditable-tail logic, fixed-budget measurements and binding financial constraints without conflating claims.
Architecture: separate audit, observable-only inference and transaction simulator modules; dedicated linear/financial runners; standalone verifier. Tech: Python 3, NumPy, SciPy, pandas, pytest, LaTeX. Spec: docs/PROTOCOL.md.

- [x] Write failing audit/tail tests, implement manifest and analytical tail bounds; verify exact and mutation cases.
- [x] Write failing terminal-regression and binomial tests; implement public-price filter reconstruction, one-row per episode inference and simultaneous planned-look intervals.
- [x] Write failing financial tests; implement double-entry settlement, feasible-order limits, forced liquidation and dealer clearing/halts. Verify restrictions really bind.
- [x] Freeze numeric configuration; run linear panels and constraints with complete per-panel/per-episode results. Keep exploratory controls separate.
- [x] Independently reassemble selected equations, counts and confidence intervals; archive rerun and hash comparison.
- [x] Update original integrated manuscript and references, leaving legacy findings labeled. Render all new pages and inspect.
- [x] Deliver updated PDF, self-contained TeX, summary and zip; publish exact verification counts and open external-replication gate.

External scientific gates remain open: authenticated configuration review, outside replication, calibrated transfer and independent novelty/proof assessment. These are not marked completed by the internal release.
