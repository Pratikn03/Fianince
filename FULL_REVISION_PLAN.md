# Machine Markets: full revision and contribution-development plan

Date: 2026-10-06

## Objective and assessment

Develop the strongest defensible paper from the existing Machine Markets program while preserving all original study questions and unfavorable results. The delivered 49-page PDF is an internal review candidate. A numerical rating is a subjective shorthand, not an acceptance standard. No hard 8/10 ceiling is established. Exceptional potential must be tested through the contribution, proofs, evidence, and independent scrutiny; neither favorable agent ratings nor local test passes establish it.

This plan supplements REVISED_PLAN.md, GAPS.md, FULL_48_PAGE_AUDIT.md, and RESULTS_REANALYSIS.md. It does not overwrite the original freezes. The user's existing deferrals remain: no additional large datasets, new complex learning-agent experiments, or extra market modules until existing evidence is reliable. Auditing and using already located evidence remains active work.

## Task 1 — Close the evidence ledger and select the authoritative package

Dependencies: none. Gaps: G01, G04, G05, G15, G22–G26.

1. Reconcile the delivered PDF receipt, working TeX, baseline, and all revised outputs. Label older copies explicitly.
2. Expand claim_evidence_map.json into one entry for every theorem, table cell, figure series, headline number, and empirical sentence. Link each entry to original page and revised location.
3. Each entry records raw input path/hash, provider/sample/clock, transformation, generator/function, estimator, covariance and degrees of freedom, output field, interpretation, status, and rerun command.
4. Inspect generators semantically. A repeated number, agent report, or matching numeric token is not derivation evidence.
5. Use existing T9/archive inventories to prioritize candidate inputs. Verify selected archives against their supplied checksums before extracting only relevant members. Check available storage first. Different sample dates cannot replace missing original dates.
6. Separate local arithmetic reproduction from provider authentication, licensing, and structural identification.

Outputs: machine-readable claim ledger, human-readable evidence table, input manifest, missing-input list, updated data dictionary.

Gate: every original page and retained claim has a disposition. Every retained numerical claim has a generating chain or an explicit unresolved label. If raw data are absent, preserve the saved-panel result with its narrower status; do not claim raw reproduction.

## Task 2 — Resolve the joint cross-venue study

Dependencies: Task 1 lineage for the specific observations. Gaps: G02, G03, G25.

1. Inspect candidate existing archives/backups for the original overlapping Binance–Coinbase sample.
2. Record timestamp timezone, precision, availability time, endpoint convention, instrument mapping, missing intervals, and price/flow definitions. A close-price proxy and a quote midpoint require explicit differentiation.
3. Build a synchronized panel without forward-looking regressors or transitions across gaps. Report overlap and attrition.
4. Estimate one joint model and save full-precision coefficients, residual covariance, lag order, sample mask, and estimator settings.
5. Recompute eigenvalues, impulse responses, and FEVD from that saved fit. State horizons in seconds as well as observation steps.
6. Check a known synthetic multivariate process, covariance validity, normalization, ordering sensitivity, and uncertainty. Use predictive language unless shock identification is defended.

Outputs: joint-panel manifest, joint-fit object, regenerated propagation/FEVD tables and figures, sensitivity report.

Gate: the same saved fit generates all reported joint results. The old printed matrix has radius about 1.002578519, so the old 0.9612 stability claim cannot be reused. If the required observations remain absent, publish the contradiction and unresolved study outcome in the audit; separate-venue fits do not establish propagation.

## Task 3 — Repair measurement and authenticate samples

Dependencies: Task 1. Gaps: G04–G06, G15, G23.

1. Carry exact raw-to-cache closure already achieved into the ledger; rerun only when code or inputs change.
2. Standardize past-available flow, gap/session resets, EMA burn-in, missingness, and inclusion rules across applicable studies.
3. Distinguish executed trade flow, quote OFI, close bars, midpoint snapshots, event time, and physical time in equations and captions.
4. Authenticate equity stock/day mappings and depth provider/venue using existing metadata and source records. Record unavailable authentication explicitly.
5. Reconcile advertised rows, raw rows, retained states, and fitted transitions. Reconcile January coverage with Jan 9–20 rather than a full-month description.
6. Explain why filtered-state Q differs from raw-return diagnostics; do not equate a positive filtered coefficient with identified learning.

Outputs: sample-flow tables, variable definitions, timing diagram, authenticated/unverified source register.

Gate: readers can reconstruct what every variable measures and which observations enter each estimate. Provider uncertainty remains visible even when arithmetic reproduces.

## Task 4 — Explain specification rejection and test mechanisms

Dependencies: Task 3; joint results only if Task 2 succeeds. Gaps: G06–G08, G12, G13, G22.

1. Treat the three MD rejections at 5% as findings. Report restrictions, covariance, rank, degrees of freedom, and uncertainty.
2. Diagnose residual serial dependence, heteroskedasticity, lag adequacy, omitted observed variables, unstable denominators, and timing sensitivity.
3. Define a small alternative-model comparison before fitting further alternatives. Include a persistence/filtering explanation and any existing mechanism-specific model supported by the data.
4. Use contiguous date blocks for estimation/evaluation. Document prior exploration; reused data are not an untouched holdout.
5. Require the proposed mechanism to make a discriminating prediction beyond positive Q. Explain what observable result would distinguish it from non-adaptive dynamics and what would falsify it.
6. Audit heteroskedastic identification assumptions: constant slopes, orthogonal shocks, variance changes, regime definitions, root selection, and uncertainty. If those fail, retain reduced-form interpretation.
7. Replace unsupported switching/regime inference only with a justified likelihood and reproducible estimation, initialization checks, uncertainty, and meaningful alternative comparison. Do not use extreme p-values unsupported by the procedure.
8. Retain existing null, raw-return, sampling-grid, zero, negative, and adverse results. The existing nulls are illustrations, not a fully calibrated null for every market dataset.

Outputs: diagnostics report, declared model-comparison protocol, falsification table, decision on supported economic interpretation.

Gate: either a mechanism-specific claim survives defended alternatives, or the paper explicitly establishes a narrower diagnostic/measurement result. Model rejection cannot be solved by choosing a specification solely because it passes.

## Task 5 — Finish the fee intervention analysis

Dependencies: Tasks 1 and 3. Gaps: G09–G11.

1. Reconcile event dates and the actual twice-monthly saved-panel clock.
2. Generate dynamic contrasts from the actual design matrix with the stated covariance, reference period, and degrees of freedom. Do not assign sqrt(2) times a pooled standard error to every event coefficient.
3. Explain the one-treated-asset problem, small cluster counts, concurrent policies, anticipation, and possible control spillovers. Do not interpret assignment rankings as randomized evidence.
4. Retain the reproduced Q estimate, date-cluster interval/p-value, and failed 5% equivalence test. Non-significance does not establish no effect or parallel trends.
5. Calculate volume changes only from traceable existing observations. The old +180% literal is not measured evidence.

Outputs: event-date/design table, reproducible contrast table, sensitivity appendix, calibrated interpretation.

Gate: every interval and test follows its stated design and covariance. If causal assumptions cannot be defended, this remains a descriptive policy-period comparison rather than a natural experiment establishing mechanism.

## Task 6 — Strengthen the theoretical contribution

Dependencies: Task 1 proof ledger; financial calibration depends on Task 3. Gaps: G17–G21, G27.

1. Audit each statement and proof for experiment, parameter class, information set, noise, initial conditions, identifiability, stability, and quantifiers.
2. Keep the scalar Gaussian testing theorem distinct from the full observed market experiment. Determine whether the broader observation law supports a new result; otherwise retain its limitation explicitly.
3. Audit cohort realization/cancellation conditions and any mixture-rate claim. Established results require appropriate attribution; local examples are not universal proofs.
4. Complete review of the bounded repeated-input gain and tail certificate, including dimensions, norms, attainability, signed/nonnormal examples, and initial shocks.
5. Map C, D, shock units, and loss budget to actual financial quantities before using the theorem operationally. Unbounded Gaussian innovations do not satisfy a bounded-input guarantee.
6. Preserve the nonnegative-coupling condition on monotonicity. Seek a signed extension only if needed for the central contribution and provable within scope.
7. Build a contribution comparison against primary research papers: existing result, exact difference, necessary assumptions, new consequence, proof/evidence, and counterexample or falsifier. Verify current sources when undertaking this literature review.
8. Choose the strongest supported central proposition: a new economic mechanism, a meaningful information limitation, a financially interpretable robustness result, or a measurement/falsification finding. Do not claim all are independently established breakthroughs.

Outputs: theorem-assumption ledger, complete proofs, counterexamples, contribution comparison, one-page central contribution statement.

Gate: a specialist can identify exactly what is new and what establishes it. Mathematical validity, novelty, economic relevance, and operational calibration are separate gates.

## Task 7 — Audit existing simulations and policy evidence

Dependencies: Tasks 1, 3, and 6. Gaps: G14, G16, G19, G21, G24.

1. Preserve the completed 48-cell/19,200-path conditional replay receipt. Add uncertainty for reported halt probabilities and disclose calibration inputs.
2. Audit matched seeds, budgets, starting states, external liquidation flow, depth, and all policy differences. Attribute effects only at the scope the comparisons permit.
3. Label historical crash scripts as illustrative simulations where coefficients are assigned and observations are not ingested.
4. Audit already located learning-agent policies, training/evaluation splits, manifests, reward sensitivity, turnover, and state/support coverage. No new complex training is authorized by this plan.
5. Separate loss driven by exogenous flow from a demonstrated adaptive-agent mechanism. Keep unfavorable comparator findings.
6. Connect transient amplification examples to the exact theorem; disclose matrices that are illustrative rather than market-calibrated.

Outputs: calibration and policy-comparison ledger, uncertainty tables, existing-agent audit, corrected historical-scenario labels.

Gate: simulations establish conditional behavior under declared inputs. Historical validity and real-world policy effectiveness require separate evidence.

## Task 8 — Integrate the paper and obtain independent scrutiny

Dependencies: all earlier tasks have a recorded outcome; an outcome may be a documented unresolved limitation.

1. Rewrite title, abstract, introduction, and conclusion around the strongest supported contribution. Preserve the full original topic disposition and audit material.
2. Align every table, figure, theorem, definition, count, and interpretation with the ledger. Clearly distinguish proved, observed, illustrative, rejected, and unresolved results.
3. Keep the full review version. Any future journal-length version must preserve substantive results and limitations through appendices/supplement; do not silently drop difficult studies.
4. Produce a reproducible package with source, manifests, scripts, environment, rerun commands, data-access limitations, ledger, and gap register.
5. Build in isolation, stabilize citations/references, inspect all rendered pages, and record exact PDF/source/result hashes. Repeat affected checks after changes.
6. Prepare an external-review brief for mathematical, econometric, and microstructure specialists, with exact questions and no numerical score as an acceptance criterion. Sending requests requires the user's authorization.
7. Record independent criticisms and responses. A clean build, agent consensus, or passing tests cannot substitute for this review.
8. Select a journal only after the central contribution and evidence are settled; verify its current scope and requirements then. Submission/publication is a separate authorized action.

Outputs: revised review PDF, complete source/evidence package, reviewer brief, response register, journal-fit decision.

Gate: each claim is supported at its declared level, known contradictions are corrected, uncertainty is candid, and independent review has addressed the principal contribution. No publication outcome is promised.

## Execution order and decision points

Execute Tasks 1–8 sequentially as requested. Within each task, finish existing local work first and record missing external dependencies precisely. Do not indefinitely rerun broad searches already documented; new recovery attempts should target a named archive, sample, or source lead.

After Task 1: decide which original samples are genuinely recoverable.

After Task 4: decide whether the strongest empirical claim is mechanism-specific or descriptive.

After Task 6: decide which contribution merits the paper's main argument and which are supporting results/open extensions.

After Task 8: decide whether the package is ready for specialist review, further focused work, or submission consideration.

Wall-clock estimates should follow the ledger and archive-access check. Raw-data recovery and external review have uncertain durations; do not promise a deadline for dependencies outside local control.

## Route to exceptional quality

An exceptional paper needs a consequential central insight, a clear difference from existing explanations, evidence/proofs that survive serious objections, and independent replication or scrutiny. Additional pages, assets, modules, agents, or favorable ratings do not establish those properties.

Potential is presently uncertain rather than capped. If mechanism-specific evidence and novelty are established, the ambition can remain high. If they are not, a narrower rigorous contribution is still valuable, but its claims and journal target must follow the evidence.

## Deferral register and reopening conditions

| Deferred work | Why | Reopening condition |
|---|---|---|
| Additional large datasets | User instruction; existing lineage unresolved | Current core evidence is reliable, a missing discriminating observation is specified, and storage/access/checksum requirements are satisfied |
| New complex learning-agent experiments | User instruction; existing policy and calibration audit comes first | Existing manifests/evaluation are coherent and a declared experiment isolates the unresolved mechanism |
| Extra market modules | User instruction; expansions do not repair current contradictions | Central contribution and evidence gates are settled and each extension has its own justified question |
| Missing historical empirical validation | Existing scripts simulate rather than ingest the claimed observations | Authentic existing source, mapping, and permissions are recovered; new large acquisition remains separately deferred |
| Broader full-observation and operational guarantees | Present theorems have narrower assumptions | Observation law and financially meaningful operators are specified and the broader statements are actually proved |
| External validation and submission | Local tools cannot establish scholarly acceptance | Concrete package prepared, appropriate independent review completed, and external actions authorized |

Model rejection, unsupported quantities, contradictory matrices, inaccurate timing/counts, and negative results are current findings to resolve or report, not deferred findings to hide.

## Verified progress since this plan was written

Original raw-panel inputs are restored and their core estimates reproduced for all768 original units. The original-overlap joint VAR/FEVD is independently reconstructed. Corrected full-panel observed timing, gap handling, raw-return comparison, measured volume and fee covariance are now computed. Two exact-disclosure propositions resolve bounded-order noiseless cases and explain why price-only abstention cannot extend universally. All23 current tables have cell/field mapping, and both plot artists are checked against their numerical sources. The remaining scientific and external gates in GAPS.md still apply.
