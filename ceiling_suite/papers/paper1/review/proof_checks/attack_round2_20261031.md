# Attack round 2 (31 October 2026): external AI referee on Theorems 3.1, 5.4, 5.6

Source: report produced by another AI model with the round-1 prompt, pasted by Pratik. **AI review, not
independent human review.** Every finding was checked against the manuscript text before acting.

| Step | Referee verdict | Check | Action |
|---|---|---|---|
| 3.1 statement | `C_F` dependence unquantified | fair | Statement now names what `C_F` depends on (ε, the stability bound on `|H|`, total weight `q`) |
| 3.1 statement | assumes `κ ≠ 0` implicitly | **rejected**: statement says `κ > 0` and `a ∈ [0,1)` known | none |
| S1.2 | needs `κ ≠ 0`, distinct rates, nonzero weights | **rejected**: `κ > 0` stated; the merged measure is by definition distinct rates with nonzero merged weight | none |
| S1.4 | breaks if `η_i = 1` (rate 0) | **rejected**: the statement and proof absorb rate-0 cohorts into `a' = a + κM({0})` | none |
| S1.6 | shared roots elsewhere not excluded | **rejected** (numerator roots are only 0 and the `r_i`, both checked) but the proof did not say so | Added: "the numerator has no roots other than 0 and the `r_i`, so these are the only possible cancellations" |
| S1.8 | separation must keep `δ` away from `η̄` | **partly fair**: the bound holds factor by factor once all three rates lie in `[ε, 1−ε]`, but "rates bounded away from 0 and 1" left ε undefined and "each factor" was loose | Statement now says all rates in `[ε, 1−ε]`; proof bounds each linear factor by `1 − r ≥ ε` and gives `|G_δ − G_0| ≤ 2qδ²/ε³` |
| 5.4 statement | constants grow fast in `K` | fair (not an error) | Added sentence: order is for fixed `K`; constants grow quickly; points to the K = 4 numerical failure in Table S-stress |
| 5.4 statement | ordering of roots ambiguous | **rejected**: proof already requires error `< γ/2` | none |
| S2.10 | Prony roots could be complex for finite N | **rejected in substance** (output equals `F^{-1}(t̂)`, a real point) but one link was implicit | Added: Prony polynomial is unique and equals `∏(z − ŝ_i)`, so roots are real and distinct |
| 5.6 statement | lower bound weakens as `ρ → 1` | true property, not an error | none |
| 5.6 statement | `μ̂` not constrained to mass `W` | **rejected**: minimax over all estimators; round 1 item 6 checked the mass slack | none |
| S3.15 | `N_0` unstated | **rejected**: Theorem 5.6(ii) states `N_0(ρ, W, a, κ, β)` explicitly | none |
| all others | (d) cited / (e) no problem | agree | none |

No finding changes a rate or a conclusion. Four wording fixes, no counterexamples.
