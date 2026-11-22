# Files received on 22 November 2026, and what was done with them

The authors received a bundle, `Paper1_JEDC_final_bundle.zip`, with a 27-page main text for JEDC and a Lean file. This folder keeps the main text unchanged as the input to `../make_short.py`.

| File | SHA-256 (first 16) | Use |
|---|---|---|
| `Paper1_JEDC_final.tex` | `190728c0ce7d579e` | Input to `../make_short.py`. Unchanged. |
| `Paper1_JEDC_final.pdf` (bundle only) | `8d5556f666eb618f` | Not stored. It was compiled from the tex above. |
| `PublicationRevision12_EndToEnd_received.lean.txt` | `c1f4a2119081bea6` | Kept as text only. It does not compile; see below. |
| `PublicationRevision12_EndToEnd_received_compile_output.txt` | | Compiler output for the file above. |
| `fig1.png`, `fig2.png` (bundle only) | | Not used. Figure 1 was the inadmissible-pair figure. Figure 2 is a raster copy of `fig_intervention_revision.pdf`. |
| `commit_and_push.sh` (bundle only) | | Not run. It creates and pushes a separate branch; this repository uses `main` only. |

## The main text

### What it does well

The format is what both simulated referees asked for:
- about 27 pages;
- self-contained proofs of the main economic results in Appendix A;
- a notation table;
- a clear list of contributions.

It also adds two results:
- **Uniqueness in Theorem 7.3(ii).** The uniform cut is the unique minimax policy when the cost is strictly convex. The argument is correct.
- **Lemma 7.7.** A Kalman-filtering desk gives the quadratic distortion cost, and equilibrium impact gives the welfare weights. Part (ii) checks out. Part (i) treats the value of the externality as a parameter.

### What it still had wrong

These are the points both simulated referees raised:

1. **Theorem 7.9 (surveillance paradox).** It kept p = 6 and N^(-1/2) as the headline and called the result an equilibrium. Against the closest economy in which the group trades like its neighbour, the exponent is 4, so the rate is N^(-1) (`paradox/exponent_check.py`, fitted slope 4.1). Part (iv) misattributed where the information comes from with tags.
2. **Near instability, Figure 1 and Table 1** used a pair with different persistences, which the paper's observer can tell apart. They are recomputed for an admissible pair (`nearcrit_admissible.py`).
3. **Taiwan.** The abstract said the calibration "confirms" the result. The range [-0.028, 0.028] was presented as a finding, but it is the cap by construction, because weights of opposite sign cancel.
4. **Overclaims:**
   - "only owner-linked audit trails escape";
   - the equilibrium wording;
   - Monte Carlo checks of results that follow from Jensen's inequality;
   - "a fortiori" applied to the positive results;
   - a small-feedback condition stated through G(1) alone;
   - the reset contract left implicit in the equilibrium rate.
5. **Remark 4.3** attributed an analysis of raw-return feedback to Supplement S8. The supplement contains no such analysis.
6. **The AI declaration** said all proofs "were independently verified ... by the authors". That cannot yet be true of results that are new or corrected in this version.

All six are corrected in `../Paper1_JEDC_main.tex`. The full list is in `../../paper1/review/REFEREE_RESPONSE_20261121.md`.

## The Lean file

`PublicationRevision12_EndToEnd.lean` was compiled with Lean 4.34.1 and the project's pinned Mathlib. The output is in `PublicationRevision12_EndToEnd_received_compile_output.txt`. Five errors:

| Declaration | Status |
|---|---|
| `perm_average_const` | Error (type mismatch). Depends on `sorryAx`. |
| `minimax_uniform_strict_cost` | Depends on `sorryAx` through the lemma above. |
| `minimax_uniform_unique` | Compiles. Its hypotheses already assume what uniqueness needs. |
| `pinsker_pointwise_kernel` | Errors. Even if repaired, it is a pointwise inequality, not Pinsker's inequality. |
| `gaussian_log_ratio_identity` | Compiles. Algebra only. |
| `kl_chain_rule_finite` | Compiles, but its hypothesis is its conclusion. It proves nothing. |

The header's claim that the file "eliminates the three probability-fact hypotheses of Theorem 6.1" is therefore false. Nothing in the paper relies on it.

`research_extension/paper1_publication_revision/PublicationRevision12.lean` replaces it:
- It checks strict dominance and uniqueness of the uniform minimax policy for a cost that is strictly convex on a convex, relabeling-invariant set of policies, such as [0,1]^K.
- It compiles with only the standard axioms (`barrier/PublicationRevision12_axiom_audit.txt`).
- It is in CI.
