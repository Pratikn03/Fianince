# Paper 1: operational observation bridge and critical review

This revision adds an observed tagged-flow decision experiment, six contract stress cases, a nearest-literature assessment and a correspondence inventory of all 36 numbered standalone Paper 1 statements.

Run `python flow_decision.py` and `python flow_falsification.py` from this directory. Both use declared fixed seeds; NumPy is required. `flow_results.json` retains all 60 configurations, including negative information values. The selected best case has a grid-adjusted simultaneous Hoeffding interval; normal approximations are diagnostics only. The study uses synthetic reset observations and synthetic payoffs, not historical position ratios.

`CLAIM_VERIFICATION_LEDGER.json` binds exact statements to hashes and records historical typed declarations without treating a name mapping as semantic equivalence. `build_claim_ledger.py` regenerates that inventory from the repository sources and the current release axiom record. The ledger's obligations remain open until a substantive correspondence review resolves them.

`NOVELTY_AND_OBSERVATION_REVIEW.md` identifies inherited results and the proposed model-specific contribution, documents provider definitions and records limits of the literature access. It does not certify priority or independent review.

The new Lean modules are `Paper1FlowDecision.lean` and `Paper1ClaimRepairs.lean` in the current manuscript proof project. Use `studies/supervisory_release_20261105/tools/verify_release.py` for the full source-bound build/axiom audit. The receipt identifies the checked sources; a declaration count does not certify every manuscript conclusion. The executable decision-rule correspondence and external market assumptions are separate obligations.
