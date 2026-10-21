# Final Gate Status & Master Release Verification (Superseded)

> **SUPERSEDED (2026-10-20):** This legacy gate status document is **superseded** and retained only as a historical record of the earlier single-volume release. Its summary assertion ("100% COMPLETE & VERIFIED") does **not** describe the current two-paper suite (`ceiling_suite/paper1/` and `ceiling_suite/paper2/`).
>
> For the authoritative, claim-by-claim scientific status of the repository, consult:
> 1. **[`MASTER_CLAIM_REGISTER.md`](../MASTER_CLAIM_REGISTER.md)** — Master Claim Register across Paper 1 (26 environments), Paper 2 (26 environments), the Paper 1 $\to$ Paper 2 Bridge Proposition, and the 18-part empirical ledger, including exact scope restrictions, proof status, Lean 4 status (`full` / `conditional` / `arithmetic`), empirical status (including failed pre-registered tests), and open obligations.
> 2. **[`research_extension/current_manuscript_lean_20261008/COVERAGE.md`](../research_extension/current_manuscript_lean_20261008/COVERAGE.md)** and **[`formal_verification_receipt.json`](../research_extension/current_manuscript_lean_20261008/formal_verification_receipt.json)** — Lean 4 + Mathlib formalization receipt (`443` declarations, `0` `sorry`, standard axioms only, with `complete: false` explicitly recording that kernel-checked formalization covers specific algebraic/measure-theoretic/interval-arithmetic steps rather than every analytic theorem of the manuscripts).
> 3. **[`ceiling_suite/bridge/BRIDGE_PROPOSITION.md`](../ceiling_suite/bridge/BRIDGE_PROPOSITION.md)** — Paper 1 $\to$ Paper 2 Information–Safety Bridge, its 4 counterexamples (C1 signed cohorts, C2 unbounded window without memory bound, C3 passive observation domain, C4 unknown non-zero hidden initial state), and remaining specialist-review obligations.

---

## Current Verification Summary (as of 2026-10-20)

| Component | Current Status | Authoritative Record |
|---|---|---|
| **Paper 1 & Paper 2 Claim Register** | **Audited (52 manuscript environments + Bridge + 18 empirical parts)** | [`MASTER_CLAIM_REGISTER.md`](../MASTER_CLAIM_REGISTER.md) |
| **Lean 4 + Mathlib Formalization** | **443 declarations, 0 `sorry`, standard axioms only (`complete: false` — partial/conditional for analytic steps)** | [`research_extension/current_manuscript_lean_20261008/COVERAGE.md`](../research_extension/current_manuscript_lean_20261008/COVERAGE.md) |
| **Information–Safety Suite (T01–T15)** | **Deterministic reproduction verified (including 60-digit `ThmB_window` & `T10_certified_numerics`)** | [`research_extension/information_safety/run_all.py`](../research_extension/information_safety/run_all.py) |
| **Paper 1 $\to$ Paper 2 Bridge** | **Reproducible (`bridge_check.py`), 4 counterexamples (C1–C4), Option A hidden-state restriction** | [`ceiling_suite/bridge/BRIDGE_PROPOSITION.md`](../ceiling_suite/bridge/BRIDGE_PROPOSITION.md) |
| **External LOB CSVs (`BTC_1sec.csv`, `BTC_1min.csv`)** | **External inputs not bundled in repo; 10 dependent tests explicitly skipped until authentic files are supplied** | [`MASTER_CLAIM_REGISTER.md`](../MASTER_CLAIM_REGISTER.md) §6 |
| **Independent Specialist Proof Review (Paper 1 rates)** | **Open obligation (self-contained proof audit package prepared)** | [`MASTER_CLAIM_REGISTER.md`](../MASTER_CLAIM_REGISTER.md) §5 |

---

## Historical Table (Superseded Legacy Single-Volume Release)

The table below reflects the earlier internal release and is superseded by [`MASTER_CLAIM_REGISTER.md`](../MASTER_CLAIM_REGISTER.md):

| Gate | Historical Status | Notes / Current Status |
|---|:---:|---|
| **Frozen baseline and claim ledger** | Historical | Superseded by [`MASTER_CLAIM_REGISTER.md`](../MASTER_CLAIM_REGISTER.md) |
| **Local runtime fail-closed controls** | Historical | `agentic_guard/core.py`, `agentic_guard/institutional_gateway.py` |
| **Noisy/dependent observation benchmark** | Historical | Superseded by `T11_unknown_covariance` (`uncertainty_calibration.py`) |
| **Historical Level-2/Level-3 LOB calibration** | External Data | `1-09-1-20.csv` present; `BTC_1sec.csv` and `BTC_1min.csv` are external (10 tests skipped when absent) |
| **Formal Lean 4 Mechanization Suite** | Superseded | Replaced by 443-declaration Mathlib project (`research_extension/current_manuscript_lean_20261008/`) with honest `full` / `conditional` / `arithmetic` classification in [`COVERAGE.md`](../research_extension/current_manuscript_lean_20261008/COVERAGE.md) |
| **Independent External Peer Review** | Pending | Specialist review of Paper 1 minimax rates and journal peer review remain open |
