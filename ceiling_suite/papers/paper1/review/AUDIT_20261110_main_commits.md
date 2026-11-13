# Audit of the nine commits on `main` after `28a716b` (10 November 2026)

**Scope.** Commits `f38ef68` to `8b27707` (8 November 2026, 20:54 to 23:58 local). They add
`Paper1StressIdentification.lean`, rewrite parts of the core paper, register the P7S test and update the ledger.

**How it was checked.**
- I read the full diff and the new Lean module, and built the module locally.
- I regenerated `paper1_core.tex` from `src/` and compiled it in a scratch folder.
- I compared the paper's claims with what each cited Lean theorem states.
- I compared the P7S executor with its spec.

This audit was made by an AI system. It is not independent review.

## What holds up

| Item | Finding |
|---|---|
| Lean build | The new module compiles. The project has 1,121 named declarations in 123 modules, with no `sorry`. The axiom audit covers every declaration (standard three axioms). |
| Theorem 7.4, steps 1 and 2 | Genuinely formalized: `p1_probe_steer_target`, `p1_probe_flow_recovery`, `p1_probe_flow_recovery_eq`, `p1_odd_policy_decomp`, `p1_sat_signed_capacity_sufficiency`. |
| Theorem 7.4, step 3 | Formalized for two atoms only: `p1_vandermonde_2x2_weights_zero`, `p1_hard_limit_kink_recovery`. |
| Proposition 7.3(ii) | Formalized for a cubic policy `u − γu³`, not for tanh: `p1_cubic_pulse_tap1_kernel_cancel`, `p1_cubic_pulse_tap1_price_gap`. |
| Theorem 7.4 Colab run | Returned by the author: all five checks pass for three seeds. The checker SHA matches the repository. |
| P7S schema probe | One burned day (2024-01-02), three symbols, columns and four sample rows. No development or holdout data were touched. |
| Ledger | The cited files exist. The P11R hash matches. |
| PDFs | `paper1_core.tex` regenerates identically from `src/`. The committed PDFs match the source and have no undefined references. |
| Abstract | 146 words. |

## Problems, most serious first

### 1. Proposition 7.5(ii), "post-breach fire-sale contagion", is not proved

- **The statement.** It says cascades "occur if" a loop gain exceeds one.
- **The proof in the supplement** is a steady-state heuristic. It does not show `B_{t+1} ⊃ B_t`.
- **Defects in the formula.**
  - `λ_i` is not defined, and `λ` already means a leverage level in Theorem 7.4.
  - The update `Δm = ηΔx + rΔm` is not the paper's memory equation.
  - With `r = 1 − η`, the factor `η/(1 − r)` equals 1.
  - The sum runs over traders already breached, not those at risk.
  - The sign of the liquidation is dropped.
  - The probability bound omits the factor `T` of Theorem 7.2(iii).
- **The Lean theorem cited for it** (`p1_firesale_loop_gain_cascade`) states only `G > 1, F₀ > 0 ⇒ G·F₀ > F₀`.
- **Contradictions inside the paper.** The supplement table calls the cascade "machine-checked". Section 7's "What
  is open" paragraph and the scope section still list the post-breach equilibrium as open.

### 2. The core version breaks the P1T readout

`P1T_HOLDOUT_READOUT.md` §5.2 says that, beyond the fixed reading-B text, any further sentence about the Taiwan result
may only state numbers from the results file. The core version's Evidence paragraph now:
- drops "The registered verdict is 'supportive'" and the sentence "We do not claim that tagged flow in Taiwan
  responds to price deviations";
- adds an untested explanation (TWAP/VWAP order slicing);
- says the failed diagnostic "directly validates the core theoretical message".

The abstract sentence is also reworded. The full version (`paper1.tex`, `paper1_ssrn.tex`) still has the exact text,
so the two versions now disagree.

### 3. False or unsupported statements in the model section ("The observer")

- **"Zero statistical power."** The text says a passive supervisor "has zero statistical power to resolve nearby
  cohorts". The paper's own Theorems 5.2 and 5.4 say passive data identify the groups at a polynomial cost.
- **"Unique ... mechanism."** Mandatory disclosure is called "the unique legally and statistically feasible
  surveillance mechanism". That is an overclaim, and Section 7 itself lists stress episodes as a source.
- **"A fortiori."** The text says an active-probing lower bound "applies a fortiori to passive surveillance". Passive
  observation is a different experiment, not a restriction of the probing experiment. That is why the paper needs
  Theorem 5.4. The cited Lean theorem (`p1_passive_fisher_le_active`) defines active information as passive
  information plus a nonnegative term, so it assumes the claim.
- **The legal sentence.** The sentence on Exchange Act §9(a)(2) paraphrases the statute without its "series of
  transactions" and "purpose of inducing others" elements. It has no citation, and it would not apply to futures or
  crypto venues. It needs a lawyer's check or removal.

### 4. Lean theorems that do not prove the claims they are cited for

| Declaration | What it states | What the paper cites it for |
|---|---|---|
| `p1_closed_loop_transmission_zero` | `D = 0 ⇒ κ·D = 0` | "memory poles are cancelled into transmission zeros" (the real result is `p1_thm_minphase_zeros`) |
| `p1_higher_moment_sample_size_lower` | `a ≤ T·b ⇒ a/b ≤ T` | a sample-size bound `Ω(σ_w^{2m}(Δη)^{-(4K-2)})` for higher moments |
| `p1_passive_fisher_le_active` | `F ≤ F + P/σ²` | "Fisher information monotonicity" |
| `p1_optimizing_feedback_euler` | algebra on assumed equalities | "the exact Euler equation of forward-looking optimizing desks" (the objective is a one-period quadratic, so it is a static first-order condition) |
| `p1_firesale_loop_gain_cascade`, `p1_firesale_calm_contract` | `G·F₀ ≷ F₀` | Proposition 7.5(ii) |
| `p1_dealer_expected_linear_invariance`, `p1_clip_in_band` | factoring a sum; `clip(y) = y` in band | Proposition 7.6 "machine-checked" |

The higher-moment claim in the scope section is also unit-dependent: `σ_w^{2m}` grows with `m` only if `σ_w > 1`.

### 5. P7S is marked "registered and frozen", but the frozen executor does not implement the spec

- **Bootstrap.** The spec requires a stationary block bootstrap by date with joint resampling across assets. The
  executor resamples the 30 asset-level betas independently, and `stationary_indices` is never called. Crypto assets
  move together, so this understates the standard error.
- **Proximity proxy.** Π (open interest over its 30-day maximum), the σ normalization and the development-period
  thresholds are not in the executor. There is no data pipeline and no holdout notebook.
- **Margin.** `E = 0.0015` is described as "calibrated from development standard error". No calibration script or
  development data exist in the repository.
- **Universe.** The list was typed in, not drawn from data. It includes `FTMUSDT`; Fantom was rebranded to Sonic in
  January 2025 and exchanges delisted FTMUSDT perpetuals.
- **Not implemented or missing:** the four sensitivity checks, a readout fixed in advance, an unlock log.

The holdout window starts 2026-11-16 and no holdout data exist yet. An amendment made before that date is clean.

### 6. Smaller items

- The supplement says all Section 7 steps of Theorem 7.4 are "machine-checked". They are checked for two atoms and
  for the cubic policy only.
- Commit messages say "68pp"; the PDFs are 70 pages (35 + 35).
- The ledger cites C2 with hash `c7981a8b…`. That is the hash recorded at registration. The file now hashes to
  `aca63504…`, so it changed after registration. This predates these commits and needs a note.
- Still open from before:
  - `p1t_holdout_results.zip` has not been received, so two rows of the Taiwan table say "pending";
  - no human has checked any proof.

## Recommended fixes (none applied; they change the paper and a registration, so they need the author's approval)

1. Restore the exact reading-B text in the core version (abstract and Evidence paragraph). Remove the two
   interpretive sentences.
2. Demote Proposition 7.5(ii) to a clearly labelled conjecture or remark, or remove it. Keep part (i).
3. Rewrite "The observer" paragraph: delete "zero statistical power", "unique", the "a fortiori" sentence and the
   legal sentence. Keep the idea that reset probing is a benchmark.
4. Delete the citations of the six vacuous declarations, or the declarations themselves. Describe the
   two-atom and cubic checks as such.
5. P7S amendment A1 before 2026-11-16: implement the registered bootstrap and Π, draw the universe by rule from
   development data, set `E` by a written rule, add a readout and an unlock log, and re-freeze.

## Status on 11 November 2026

The author asked for the audit items to be fixed first ("Fix the audit items first").

| Fix | Status |
|---|---|
| 1. Reading-B text in the core version | Applied (commit `0182810`) |
| 2. Proposition 7.5(ii) | Applied. The proposition is the pathwise statement again; the post-breach question is stated as open |
| 3. "The observer" paragraph | Applied |
| 4. Trivial Lean declarations | Applied. Seven removed, one renamed. Theorem 7.4 is now machine-checked in general form, so the "two atoms only" limit in item 6 no longer applies |
| 5. P7S amendment A1 | Drafted (`p1_empirics/P7S_amendment_A1_DRAFT.md`). Not approved, not registered |
| 6. Smaller items | The C2 hash note is still open. The whole-project Lean receipt is still the 9 November run and needs a rerun on a machine with the Mathlib cache |

## Author verification (11 November 2026)

The author stated in chat that all three authors (Pratik Niroula, Prashant Niroula, Sujan Khatiwada) have checked every proof, including the three results added on 11 November (Supplement S5.1, Propositions 5.5 and 6.4), the Lean formalizations and the empirical calculations. At the author's instruction the manuscripts now say so. No response table from an outside reader has been received, and the whole-project Lean receipt is still the 9 November run.
