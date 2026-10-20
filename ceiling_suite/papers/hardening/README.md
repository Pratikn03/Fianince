# October 2026 theorem hardening: numerical checks

Scripts behind the numbers quoted for the hardened theorems. Each writes a JSON file next to it.

| Script | Paper result | Output | Runtime |
|---|---|---|---|
| `rh_bound.py [n_theta]` | Paper 1, Theorem thm:rh (explicit F_dom, W_perp, gamma; Table tab:rh full-bound column) | `R_P1_rh_explicit.json` | ~10 min at 3,600 angles |
| `rh_check.py` | Paper 1, Theorem thm:rh: numerically optimized loss-plus-fee probes lie above the bound | stdout | ~5 min |
| `p1_checks.py` | Paper 1: McMillan degree at a = 0 (thm:merged), sigma_min of Toeplitz sections (thm:spectral iv), passive Whittle slopes for every K (prop:passive iii), IV Jacobian determinant (prop:tagged) | `R_P1_hardening_checks.json` | ~2 min |
| `p2_sec4_checks.py` | Paper 2, Theorem thm:peak: residues of the counterexample, momentum-only residues, confluent peak lag | `R_P2_sec4_checks.json` | ~1 min |
| `p2_cheb_tradeoff.py` | Paper 2, Remark rem:cheb: window-polynomial versus tail certificate | `R_P2_cheb_tradeoff.json` | ~5 min |

The noisy-proxy intersection of Paper 2, Theorem thm:disclosure (v), is test T15 of `research_extension/information_safety`
(`run_all.py`). Unit tests of the renewal monotonicity (prop:lucas ii), the confluent peak lag and the a = 0 dimension drop
are in `research_extension/information_safety/tests/test_hardening_theory.py`.
