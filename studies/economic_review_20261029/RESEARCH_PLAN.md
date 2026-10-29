# Owner's research plan

Reviewed base: `ff5317641af5e76011079cb9346ee06264ffef81`.
New analyses here are exploratory and not independent validation. Historical
registered specifications and archived results are preserved. No journal outcome
or foundational status is implied by completing this checklist.

## P0 - Corrections included in this branch

- [x] Restore `q_i/eta_i` in the cumulative hidden-state drift identity and proof.
- [x] Separate that sum from the exact finite-horizon pointwise-loss envelope.
- [x] Replace the false exact hidden-state capacity cost by a sufficient invariant
  box; show zero capacity reduction in the original calibration.
- [x] Preserve the old result JSON; create a repaired result with a distinct name
  and update the current number checker to read it.
- [x] Remove the general necessity assertion for the forward account bound:
  separate price, fill and inventory maxima need not be jointly attained.
- [x] Repair the inventory-kernel positivity proof using a convex combination of
  geometric taps instead of the invalid intermediate inequality.
- [x] Correct the CAT display factor, C2 Taylor remainder and population-mass
  terminology; distinguish original Gaussian response errors from nonlinear
  transformed errors.
- [x] Include the structural timing zero in the minimum-phase statement and
  separate it from recovered memory rates.
- [x] Correct generic non-normality language and restrict signed-margin summaries.
- [x] Correct finite-window infinite-endpoint attainment and require a stable
  compatible economy; correct the logarithm theorem part-number reference.
- [x] Separate market access from the ability to reset the market, and public
  EMA-proxy evidence from structural certification in the synthesis.
- [x] Add an assumption-focused economic contract and exploratory Colab runner.
- [x] Refresh modular mirrors and generated working, journal and thesis sources; repair missing B2 macro imports and guarded thesis extraction ranges.
- [x] Replace blanket name-mapping success with an explicit incomplete audit (three unmapped and seven revised statements at this snapshot).

The proof corrections above are written analytic arguments with numerical
regression checks. They are not newly kernel-checked Lean results. The ledger
records remaining reviewer obligations rather than marking all entries solved.

## P1 - Independent proof and novelty review

- [ ] General-memory minimax identification bounds and constants.
- [ ] K-cohort lower bounds, separated inverse bounds and uniform Wasserstein
  recovery, including the loss function, compact class and rate-order convention.
- [ ] Modulus dual, square-summability necessity and potential-theory logarithmic
  lower bound. Compare assumptions directly with optimal-recovery literature.
- [ ] Passive uniform near-unit-root results, nuisance-root restrictions, exact
  displacement/exogeneity and finite-sample versus asymptotic interpretation.
- [ ] Moment-cone interior characterizations for odd/even window lengths; exact
  formulations of principal representations and boundary cases.
- [ ] Rigorous continuous frequency/angle extrema. Dense grids alone are not
  outward numerical certification; do not promote decimal matches into proofs.
- [ ] Prony deconvolution concentration constants, dependence on the distance to
  instability and allowable noise neighborhood.
- [ ] Economic-primitives mapping and tied-intensity rate statements, including
  the assumed self-confirming map versus an equilibrium derived from primitives.
- [ ] Simultaneous coverage for data-selected admission and counterfactual policy
  changes. Restricted iid decoys are not arbitrary manipulation resistance.
- [ ] Update Lean mappings for all new/revised environments after independent
  semantic review. Hash agreement is not a fresh Lean rebuild.

## P2 - Experiments and completion criteria

| Study | Implemented work | Completion criterion and resource |
|---|---|---|
| E1 drift/guard | CPU runner + independent resolvent and corner-path tests | Identity agrees; box induction is valid; report finite-horizon and infinite-limit results separately |
| E2 filtering | Martingale/persistent-flow nulls and direct/EMA structural comparison | Report every span and null outcome; no interpretation of an EMA coefficient as structural Phi |
| E3 information targets | Known-pair Gaussian error, equal risk target, interval coverage and tap-count accounting | Distinguish witness from a uniform theorem; do not substitute a simulated slope for the proof |
| E4 controls | Three synthetic regimes, training capacity calibration, independent test comparison | Report exposure drift, all baselines and paired intervals; a positive result is not required |
| E5 market CSV | Purged forecasts and paired block bootstrap | Document input provenance, units/timing and prior sample use; stronger volatility and economic designs still needed |
| E6 coverage | Valid Gaussian setting + four misspecification diagnostics | Report coverage with Monte Carlo uncertainty, widths and assumption flags |
| E7 known feedback / AI | Links to existing K1/B3/B2/H1/H2/E2 protocols | Acquire resources, preserve original endpoints; new runs are labeled replications/exploration |

Before any new confirmatory study, freeze the design, primary endpoint, sample,
exclusions, baseline tuning, minimum economically relevant effect and analysis
code at an independently recorded timestamp. A configuration saved immediately
before a local run is useful provenance, not independent preregistration.

## P3 - Economic and editorial decisions with the professor

- [ ] Choose the lead question: the information minimally required for a defined
  financial decision. Use the existing `Identify or Certify?` synthesis.
- [ ] Derive agents' beliefs and continuation opportunities or explicitly present
  them as behavioral assumptions; separate filtering from equilibrium.
- [ ] Specify whose action is controlled and whether depth changes with admission.
- [ ] Establish a credible observable-to-response bridge; consider K1 rather than
  adding many unrelated venues to a weakly identified proxy.
- [ ] Define the economic benefit of admitted trade and the cost of disclosure.
- [ ] Keep theoretical, reduced-form, causal and welfare claims separate.
- [ ] Retire obsolete engine-invariance, predatory-equilibrium, Pareto-optimality
  and maximal-ellipsoid assertions from active summaries. See the historical
  quarantine note; do not silently rewrite archived outputs.

## What to bring back from Colab

Download each results ZIP. Keep `manifest.json`, configuration, all CSV rows,
interpretation file and plots. Record any changed setting or failed run. Do not
select the seed with the nicest result. Bring the corrected proposition, the
same-risk hard-pair example, the economic contract and a mixed-results table to
the professor. Raw private data need not be uploaded to GitHub.
