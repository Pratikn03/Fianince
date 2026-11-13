# Paper 1: line-by-line check of the new proofs (12 November 2026)

Done by an AI system, the same kind of system that wrote the proofs. It is a careful first pass, not independent
verification; the authors' own check (`AUTHOR_PROOF_CHECKLIST_20261112.md`) is still needed before the AI-use
disclosure can say the authors verified every proof.

Scope: every result marked "new in this version" in the supplement guide: Section 4 (saturating traders: Theorems
`thm:satsuff`, `thm:stress`, `thm:satident`, Propositions `prop:smooth`, `prop:delever`, `prop:dealers`), Theorem
`thm:anypop`, Propositions `prop:nearcrit` and `prop:noisystress`, Lemma `lem:everyK` and Proposition
`prop:targetK`, Theorems `thm:partial` and `thm:pool`, and the several-group remark after `prop:hiding`. Each step
was re-derived; every constant was traced; each numerical claim was matched to its script and results file.

## Verdicts

| Result | Verdict | What was wrong | Fixed how |
|---|---|---|---|
| `thm:pool`(iv), global pooling | **Gap, fixed** | The statement claimed the order is exactly (Δη)^-2l_g, but the proof only gave the upper bound at l_g and a lower bound at l*. | Restated with two orders: l_c (least order at which the moment map is injective on the class) gives the lower bound by a two-point argument; l_g (injective and an immersion) gives the upper bound; l* ≤ l_c ≤ l_g ≤ 2K-1, with l_g = l_c when condition (R) holds on the class. Note and abstract changed to match. |
| `thm:pool` numerical global claims | **Wrong, fixed** | "So l_g = l* there" rested on three configurations per case, and the reported (3,3) collisions were ill-conditioning at two nearly coincident nodes (gap 0.003), not collisions. | Search extended to 15 configurations per case and every apparent solution inspected: none at separated configurations in any case. Text now says this is consistent with l_c = l* but does not prove it. |
| `thm:pool` setup | **Missing assumption, fixed** | Stability of each market was used but not stated. | Added: each market Schur stable on the class. |
| `thm:pool`, redundant markets | **Unproved sentence, fixed** | "Markets whose weights are linear combinations ... do not lower the exponent" had no proof. | One-line proof added to (i). |
| `thm:pool` Monte Carlo | **Wording, fixed** | Did not say the estimator search starts at the true configuration. | Now says it checks the local estimator of (ii). |
| `thm:partial` | **Correct**; Lean scope overstated, fixed | The Lean bound assumes a common noise variance for prices and flows and a finite record length. | Text now says so, and that σ is replaced by min(σ, σ_f) otherwise. |
| `thm:anypop`(iii) | **Gap, fixed** | The band-linear class does not contain the linear economies under passive Gaussian records (traders eventually leave their bands). | Restricted the exact statement to impulse-response records; for passive records added a total-variation approximation (Theorem `thm:stress`(iii)) valid when capacities are unbounded. |
| `prop:nearcrit` | **Gap, fixed** | Constants of Step 2 depend on the economy, which depends on Δη; uniformity in Δη was claimed but not argued. Last step cited Theorem `prop:passive` for a pair with different persistences. | Added the continuity argument (the limit economy at Δη = 0 has the same properties); replaced the citation by the direct bound. |
| `thm:satident`(iii), cubic shape | **Half proved, fixed** | Proof showed probes reveal at most the first and third leverage moments, not that they reveal them. | Added the identification half (coefficients of x_j and x_j^3 give all moments of both measures). |
| `prop:noisystress` | Correct | | |
| `thm:satsuff`, `thm:stress`, `prop:smooth`, `prop:delever`, `prop:dealers` | Correct | Constants re-derived (e.g. C_D, the 12 in `prop:smooth`(ii), the Gaussian tail bound). | |
| `lem:everyK`, `prop:targetK` | Correct | | |
| `prop:hiding`, several groups | Correct | | |

None of the gaps changes a headline; the corrected (3,3) reading removes the one case where the global order seemed
larger than the local one: the local pooling exponent, the partial-disclosure exponent, the near-instability
bound and the any-population lower bound all stand. The global pooling statement is weaker than before: the paper
now claims only that pooling never needs more data than one market, and that the global order lies between the
local one and that bound.

## Extended global search

`global_fibres_extended.py` adds 12 random configurations per case to the original 3 (400 starts each). It found
apparent other solutions only for (4,2), at 3 of 12 configurations. `global_fibres_inspect.py` shows that all of
them, and the 5 reported earlier for (3,3), lie within 0.05 of an original configuration with two nearly coincident
nodes (gaps 0.003 to 0.033), with residuals just under the 1e-10 tolerance and next-order gaps near 1e-9. They are
directions in which the moment map is ill-conditioned. At configurations with separated nodes, no collision was
found in any of the five cases. `run_all_checks.py --slow` now checks this.

## Cross-market test

Decision: **do not register P1X.** Two designs were checked by simulation before any data were read
(`research_extension/cross_market/p1x_design_sim.py`; results in `results_p1x/` and
`ceiling_suite/p1_empirics/P1X_spec_DRAFT.md`, section 9). Both fail criteria fixed before running:

- Design 1 (number of memory classes chosen by BIC) always picks one class. Under a true premise each market's single
  fitted memory then reflects its own mix of classes, and the test rejects a true premise in 10-66% of replications.
- Design 2 (three classes fixed) no longer rejects a true premise (0-2%), but detects a large violation in at most 1%,
  because three free memories per market absorb it.

Weekly class positions aggregated over many funds cannot resolve memories within a class; that is the paper's own
cost theorem at work. A test of the pooling premise needs positions by fund or strategy across markets, which are not
public. So no new data test is proposed. The data status of Paper 1 is unchanged: two registered tests (one supporting
a weaker reading, one inconclusive) and the Binance replication after February 2027.
