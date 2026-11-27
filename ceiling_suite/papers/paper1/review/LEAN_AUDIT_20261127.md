# Audit of the Lean 4 files added since 22 November 2026 (27 November 2026)

Written by an AI system for the authors. This is a reading of statements and proofs plus mechanical checks; it is not
independent review.

## Scope

Six files in `research_extension/paper1_publication_revision/` and six in
`research_extension/current_manuscript_lean_20261008/CurrentProofs/`:

| File | Declarations | Duplicate of |
|---|---|---|
| `PublicationRevision14.lean` | 24 (26 after this audit) | `Paper1PassiveIncidenceUpper.lean` (same content, namespace `CurrentMM`) |
| `PublicationRevision15.lean` | 12 | `Paper1EndogenousSupervisor.lean` |
| `PublicationRevision16.lean` | 11 | `Paper1MPVQuantization.lean` |
| `PublicationRevision17.lean` | 10 | `Paper1FrequentBatchAuction.lean` (the batch-auction part) |
| `PublicationRevision18.lean` | 17 (19 after this audit) | `Paper1FragilityAndDesign.lean` |
| `Paper1InstrumentIncidence.lean` | 5 | none |

The five `CurrentProofs` copies repeat the `PublicationRevision` files under the `CurrentMM` namespace with a `p1_`
prefix. The receipt's count of named declarations (`verify_formalization.py`, lake target `CurrentProofs`) covers the
`CurrentProofs` project only, so the copies are counted once and the `PublicationRevision` files are not counted.
Nothing is double-counted. The cost is that two copies must be kept in step. Every change below was made in both.

## Mechanical checks

- **Every file compiles** against the pinned Mathlib (Lean 4.34.1), with no `sorry`, `admit` or new axioms.
- **Axioms:** `#print axioms` for every theorem and lemma in the six source files (85 declarations after this audit)
  reports only `propext`, `Classical.choice` and `Quot.sound`.
- **CI gap, fixed here:** `.github/workflows/ci.yml` compiled `PublicationRevision.lean` to `PublicationRevision12.lean`
  only. Revisions 13–18 were never checked in CI. They are now added.

## What the statements prove, by class

**A. Substantive (the Lean statement carries real mathematical content):**
- Rev14: `fourier_first_moment_bound` (first-moment bound from the model's primitives), `sum_convPow_le`,
  `sum_mul_convPow_le`, `sum_j_logCoeff_le` and `sum_j_logCoeff_disk_le` (coefficient bounds for log(1 − φ) by
  convolution powers), `fourier_first_moment_budget`, `fourier_truncation_tail`, `spectral_floor_log_lipschitz`
  (via the mean value theorem).
- Rev16: the tick-quantization cell lemmas (`tickQuantize_eq_of_mem_cell`, `quantized_cell_coincidence`,
  `sub_tick_closed_loop_coincidence`).
- Rev18: the fragility discriminant, ordered roots and Vieta bound; `minimax_compact_existence`;
  `minimax_strict_loss_dominance`; `minimax_partial_tags_strict_unique`; `instrument_desk_constrained_opt`;
  `batch_clearing_price_monotone`; `nyquist_pi_stability_sign`; `huberman_stanzl_round_trip_no_arb`. I checked the
  last three by hand: each conclusion follows from its hypotheses as stated.

**B. Correct but elementary algebra (a deterministic step, as the paper says):** most of Rev15, Rev17 and the
instrument file. Examples: the crowding and composite-test envelopes rearrange a first-order condition the paper
derives; the call-auction lemmas are permutation invariance of list sums and a numerical example; the margin lemmas
are linear inequalities; `class_removal_kernel_did` is a polynomial identity; the five instrument-incidence identities
are over the rationals.

**C. Statements weaker than their names or docstrings (fixed in the docstrings here):**

| Declaration | Name or docstring said | The statement is |
|---|---|---|
| `sample_complexity_infinite` (Rev16) | "infinite sample-complexity barrier" | `N * 0 < c` for `c > 0` |
| `zero_divergence_minimax_risk` (Rev16) | "minimax testing risk lower bound at J = 0" | `(1 - √0)/2 = 1/2` |
| `sub_tick_zero_divergence_bound` (Rev16) | "zero total-variation contribution" | `a = b → |a - b| = 0` |
| `supervisor_effort_collapse_general` (Rev15) | "for all n > 2" | `n` does not appear; the hypothesis `L·J_bound < c_min ≤ C` gives the conclusion directly |
| `simultaneous_no_pure_ne` (Rev15) | "non-existence of pure Nash equilibrium" | two payoff inequalities under assumed hypotheses; the best-response argument is on paper |
| `micro_welfare_weight_separation` (Rev18) | (no docstring; Table S2 lists it for "n_H < 0 < n_B separation") | the separation conjuncts restate the hypotheses `hH` and `hB` |
| `kalman_stationary_var_strict_convex`, `kalman_deriv_strict_mono` (Rev18) | (Table S2: "strict convexity P''(r) > 0, monotone P'(r)") | positivity and monotonicity of explicit formulas; nothing showed the formulas were the derivatives |

**D. Key analytic facts taken as hypotheses:**
- `spectral_floor_lipschitz` assumes the logarithm's Lipschitz bound. It is proved separately in
  `spectral_floor_log_lipschitz`, so nothing is missing.
- `transfer_factor_error` assumed that `exp` is `exp(B)`-Lipschitz on `(-∞, B]`.
- `passive_incidence_end_to_end` chains error bounds that are all hypotheses. Table S2 says "conditional on
  sample-covariance and floor bounds", which is accurate.

## Changes made in this audit (Lean only; no paper text changed)

1. **Kalman derivatives proved.** `kalmanP_hasDerivAt` and `kalmanPderiv_hasDerivAt` (Rev18) prove that
   `kalmanPderiv` and `kalmanPsecondDeriv` are the first and second derivatives of `kalmanP` on (−1, 1). Table S2's
   "strict convexity P''(r) > 0" is now checked as stated.
2. **The exponential bound proved.** `exp_lipschitz_below` and `transfer_factor_error_unconditional` (Rev14) remove
   the hypothesis from the transfer-factor bound.
3. **Docstrings corrected** for every class-C item, saying what is arithmetic only and what is on paper.
4. **CI** now compiles Revisions 13–18.
5. **Copies kept in step.** The same theorems (prefixed `p1_`) and docstring corrections are added to
   `Paper1FragilityAndDesign.lean`, `Paper1PassiveIncidenceUpper.lean`, `Paper1EndogenousSupervisor.lean` and
   `Paper1MPVQuantization.lean`.
6. **Receipt.** `formal_verification_receipt.json`, `named_declarations.json` and `AxiomAudit.lean` were regenerated
   by `verify_formalization.py` (strict axiom audit passes; the count rises from 1,306 by the four new declarations).

## Recommended paper edits (not made: the authors have read the current text)

- **Table S2, Lemma 7.x (micro):** say that the sign separation n_H < 0 < n_B is a hypothesis of the Lean statement.
  Optionally cite `kalmanP_hasDerivAt` and `kalmanPderiv_hasDerivAt` for the convexity claim.
- **Table S2, Theorem on minimum tick (mpv):** drop `sub_tick_zero_divergence_bound`, `zero_divergence_minimax_risk`
  and `sample_complexity_infinite` from the machine-checked column, or call them "arithmetic of the zero-divergence
  case".
- **Table S2, Proposition on the endogenous supervisor:** say the Nash-equilibrium argument is on paper, with Lean
  checking the payoff inequalities.
- **Supplement, verification section:** the declaration count in the text (1,306) should be updated to the new
  receipt count when the supplement is next rebuilt.
