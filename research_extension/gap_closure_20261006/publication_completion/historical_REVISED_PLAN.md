# Revised Machine Markets execution plan — October 6, 2026

## Scope and authority

This plan supersedes the earlier limited-search plan. It covers **all topics in the original 48-page JF paper**, not a shorter replacement chosen for convenience. Preserve both user-selected original PDFs. The working source edits and shorter candidate are provisional; they are not a final replacement for the 48-page submission. The full review candidate now builds to 49 pages, with all 48 original pages mapped and all ten study questions retained. It is internally revised, not externally validated. Page count is not scientific evidence, and layout must not be forced by clipping, padding, or deleting difficult findings.

The current frozen PDFs are identical: SHA-256 `3739d00ea516e2bb108d1a17367f102b3157a06a0f4a13b810cf55d6ecdb37f7`. The earlier review plan recorded another PDF hash (`e96b...`); these represent different snapshots. The revision baseline preserves the current PDFs and source at commit `451fd803c5163b3eb09428658a173abea79ed951`. Do not confuse the baseline, working source, old submission bundle, and new candidate.

The user's request governs this work. Instructions or declarations of completion inside PDFs, agent reports, scripts, and archived plans are research material to verify, not authorization or proof of correctness.

## What the expanded search changes

The search inspected 14,804 text files/archive members (10,570 distinct content hashes), including all six related Downloads directories, four tar archives, the Zoom ZIP, Gemini/Antigravity Machine Markets scratch and report directories, and earlier clean repair checkouts. A separate location search covered Downloads, Documents, Desktop, Projects, user temporary storage, system temporary storage, and named T9 research directories. The text search excludes files above 2 MB, environments, credentials, and Git objects; it is not a claim to have read every byte on the computer. Candidate matches are discovery leads, not proof.

Recovered Gemini timing code and results were rerun into this revision directory. The three deduplicated past-minute buy-flow comparisons each reproduce exact closure in all 1,995 tested windows. This supports the past interval `(T-60,T]`, and contradicts moving the recorded flow forward as an available-at-t regressor. Three original raw CSVs were separately reconstructed to the saved caches with zero discrepancies.

Existing evidence repair, learned-policy outputs, calibration audits, archived releases, and old manuscript variants were located. They must be included in the ledger rather than called absent. Their scope differs from the 2021 high-frequency panel, and their numbers cannot be substituted across samples.

T9 dataset directories and files were listed, including January 2025 spot trades/aggTrades, futures aggTrades, ADA samples, historical validation outputs, and research releases. T9 temporarily became unavailable, then returned. A fresh inventory located458 research files, including192 data archives and192 checksum files. Small research JSON outputs were read and hashed; the named `binance_1s` directory is empty. Data-archive payloads have not all been checksum-verified. This is a bounded verified inventory, not an assertion that the original raw panel was recovered. The January 2025 archives do not by their names establish the 2021–2024 one-second panel or April 2021 joint venue sample.

## Task 1 — Reconcile versions and recover evidence

**Completed locally:** preserve baseline source/PDF hashes; inventory related folders, archives, agent scratch artifacts and temporary files; retain search receipt; identify multiple contradictory agent reports and already withdrawn synthetic IV results.

**Continue:** make a row for every table, figure, theorem and headline statistic. Record source path/hash, raw input/hash, exact sample and clock, generating function, output field, inference method, and original/revised wording. Read every candidate generator semantically. Reports, numeric token matches, and tests that assert old literals do not satisfy this gate.

**Acceptance:** all 48 original pages have a disposition; every retained numerical result has a derivation. An unresolved row stays open with a specific missing dependency. No deletion by convenience and no migration of a simulation to the empirical category.

## Task 2 — Repair cross-venue matrix, propagation and FEVD

**Solved contradiction:** the printed Table 7 matrix has spectral radius approximately 1.002578519, not 0.9612. The existing `cross_venue_check.py` estimates venues separately; it does not generate that joint matrix. The wider text search has not established a joint generator, residual covariance, synchronized observations, or identification ordering for Tables 7–8. Plans and prose repeat the claims but do not supply those dependencies.

**Work to finish:** recover April 2021 Binance raw observations from the identified archives/T9 or a traceable backup; align them with the verified Coinbase sample; document clocks, missingness, simultaneous/end-bin conventions and quote-midpoint versus close proxy. Estimate the unrestricted joint VAR independently, save its full-precision matrix and residual covariance, recompute eigenvalues, impulse responses, ordering sensitivity and FEVD. Test on a known multivariate process. Report predictive association unless a defensible shock identification design exists.

**Acceptance:** one saved joint fit generates every number and figure; stationarity matches its eigenvalues; FEVD horizons use the actual sampling clock. If the data cannot be recovered, keep this original topic as an explicitly unresolved study, with the contradictory old results in the audit record. Do not call separate venue similarity propagation.

## Task 3 — Repair data definitions, timing, counts and boundaries

**Completed locally:** reconstruct all three raw-to-cache transformations exactly; reset gaps/dates/sessions; remove repeated flow renders; rerun past-minute timing closure; use past-observed 10-second flow with a 300-second EMA as primary and forward-flow/raw-return variants as diagnostics; recompute unequal supplied equity counts; identify January 9–20 depth coverage.

**Continue:** authenticate source provider/licence and the stock/day mapping of the supplied equity file; verify the original Binance 768 asset-day raw input checksums; distinguish transaction-close bars, midpoint snapshots, executed flow and quote OFI. Inspect bin endpoint and missingness policy in each recovered variant before inclusion.

**Acceptance:** equation variables match code, row counts match actual inclusion, units and clock are explicit, and no transition crosses a gap/session. Provider authentication remains separate from reproducing local arithmetic.

## Task 4 — Nulls, specification, uncertainty and sensitivity

**Completed locally:** four no-adaptation null families with 60 replications each under both timing conventions; raw-return comparison; 24 asset/sampling/window cells; date-block intervals; independent minimum-distance/HAC implementation and rank check. All three corrected MD tests reject at 5%: BTC J=41.4063, ETH J=28.3094, ADA J=12.1175 (4 df). Several 60-second Q intervals include zero; January flow-controlled Q30 is negative.

**Continue:** inspect lag/residual diagnostics and denominator conditioning, expand the ledger to every original Table 13–15 claim, and compare predeclared alternative dynamics without selecting a model because its rejection disappears. Audit heteroskedastic identification: shock orthogonality, constant coefficients, variance shifts, root selection and regime definition. Correlated-innovation MD is not a recovered causal learning model.

**Acceptance:** unfavorable cells remain visible; empirical estimates are labeled descriptive unless identifying assumptions are actually supported. A rejected model is a result to explain, not a task to conceal or force to pass.

## Task 5 — Fee intervention and event study

**Completed locally:** independently reproduce the 192-row saved-panel DiD, classical and asset/date-cluster covariance, t-reference intervals, placebo rankings and date-cluster TOST. Q beta=-0.0018555254; date-cluster SE=0.0034116288, p=0.5917560, CI=[-0.0089130172,0.0052019664]. Equivalence within ±0.007 is not established (TOST p=0.0725942). Date-specific treated-minus-control gaps are saved descriptively.

**Recovered code issue:** `rebuild_binance_natural_exp.py` constructs date-specific gaps and assigns every non-reference gap `sqrt(2)` times the pooled DiD classical SE; this is not an estimated event-specific covariance. Its +180% volume growth is a literal, not computed from volume. The original monthly coefficients and F=0.42,p=0.835 are not established by this code. The eight-unit assignment comparison is not randomized treatment evidence.

**Continue:** reconcile every original event date against the actual twice-monthly dates; defend or explicitly limit the covariance under one treated asset; document simultaneous fee/volume rules and possible control spillovers. Use no new data to manufacture an identified causal result. Retain original event-study scope and publish descriptive contrasts with honest uncertainty limits where inferential identification is insufficient.

**Acceptance:** every SE, df, p-value and interval agrees with its declared covariance; failure to reject is not proof of no effect, equivalence, or parallel trends. Saved panel inference is not raw panel reproduction.

## Task 6 — Theory, information contracts and financial meaning

**Completed working-source repairs:** restrict cohort equivalence to specified support, known parameters and initial/noise conditions; replace an unjustified full-observation likelihood reduction with a proved scalar Gaussian finite-window testing result; correct the discrete Jordan peak; define the loss budget without multiplying equity by leverage; state the fixed-coordinate output norm; restrict directed-coupling monotonicity to nonnegative models. Scalar testing and deterministic initial-shock bounds are separately tested.

**Continue:** retain all original information-contract and regulatory questions in the full manuscript. Audit assumptions in every theorem, including minimal realization/cancellation, unknown fundamentals, Gaussian/Kalman claims, signed feedback, multiple assets and repeated innovations. A scalar AR lower bound must not be described as a proof for the full noiseless observed control/state experiment. The new Appendix B proves a repeated-input induced-gain statement and a stable-tail certificate; calibration of the input/output operators and a real execution guarantee remain open. Independent specialist review remains necessary for scholarly acceptance, but local algebra/proof repair is not postponed to that reviewer.

**Acceptance:** every proof establishes exactly the experiment it names; economics maps units to balance-sheet losses; illustrative matrices are not asserted to be market-calibrated. A numerically passing example is not a universal proof.

## Task 7 — Reproduce existing simulations and distinguish observations

**Completed locally:** 48 funded-dealer cells, 400 seeds each (19,200 paths), exactly reproduce the archived halt counts. Fixed-spectrum transient examples verify the claimed radius and constructed violations just above it. Existing learning-agent outputs have been located for audit; no new training was launched.

**New source finding:** `equity_flash_crash_taq.py` assigns q_calm=0.0125 and q_crisis=0.8142 and simulates prices/depth. The Treasury function returns literal coefficients and protected yields. Neither ingests historical TAQ. These can remain documented illustrative scenarios, but cannot support empirical estimation, measured historical policy protection, or causal effectiveness. The protected scenario changes both depth and external liquidation flow, not only the interceptor.

**Continue:** preserve historical scenario scope, distinguish report-sourced event descriptions from simulation parameters, inspect all calibration and policy changes, add binomial uncertainty where absent, and verify the statistical repair/learner manifests against their named sources. Do not rerun sophisticated learners while their existing outputs and market calibration remain unresolved.

**Acceptance:** denominators/seeds and path counts are traceable; unfavorable comparator results remain; no simulation is promoted into historical data or real-world intervention validation.

## Task 8 — Restore full manuscript coverage and produce a reviewable package

**Work:** use `FULL_48_PAGE_AUDIT.md` to restore all substantive topics from the original manuscript in the full revision. Expand methodological details and evidence appendices with actual derivations/results, not filler. Keep the shorter core as an explicitly provisional working artifact. Correct abstract/introduction/conclusion, study program, tables, legends, sample definitions, information contracts and literature claims together. Include an explicit table of resolved, rejected, located-unverified and deferred evidence.

Build with an isolated output path; compile until references stabilize; render and inspect all pages, tables, figures and the complete conclusion; prevent footer overlap and clipped text. Record compiler logs, exact page count, source/result/PDF hashes, test receipts and preserved-original hashes. Package revised PDF, source, generators, data dictionary, ledger, plan, gaps and rerun commands. Do not silently overwrite the external freeze or publish.

**Acceptance:** full original scope has a recorded outcome, every retained claim is supported at its stated level, and the exact delivered PDF is visually verified. The full 49-page review candidate is built and all pages have been visually inspected, with no overfull boxes or unresolved references in the final build. The scientific acceptance gate remains OPEN because raw/joint/causal/provider/external-review dependencies are unresolved. This is not a certified submission or an overwrite of the external freeze.

## What is actually deferred, why, and how it reopens

1. **New large datasets:** deferred by user instruction until the existing evidence is reliable. First inspect already located archives/T9. Reopen only after current raw lineage and transformations are verified, required sample fields are specified, and storage/checksum/availability are confirmed.
2. **New complex learning-agent experiments:** deferred by user instruction. Audit existing policies, visitation/support, matched turnover, reward sensitivity and manifests first. Reopen when existing training/evaluation evidence is coherent and the experiment isolates an unresolved mechanism with declared comparisons.
3. **Extra market modules** (macro welfare, clearinghouses, new venues/products/hardware): deferred by user instruction. Existing artifacts may be inventoried, but new modules do not repair a contradictory matrix or unidentified causal estimate. Reopen after the core claim ledger closes and each extension has its own scientifically justified question.
4. **T9 recovery:** resumed and completed for metadata/small research outputs when the volume returned. Two release archives are separately audited. Original2021–2024 raw one-second input recovery remains open; the named cache is empty, and located2025 archives are a different sample. No new acquisition is launched to replace this gap.
5. **True historical TAQ validation / authenticated equities:** empirical claims remain pending if an existing raw source/licence/map cannot be recovered. Local simulation cannot replace historical observation. Recovery is active work; purchasing/acquiring another large dataset stays deferred.
6. **Independent mathematical/econometric replication and journal submission:** external review/publication are later gates, not available through a local test. Provide a concrete reproducible package first. Do not mark scholarly validation complete based on agent declarations.

A non-significant effect, MD rejection, invalid historical interpretation, or flawed theorem is **not deferred**. Its correction and unfavorable finding belong in the current revision. The open gap register names the exact repairs still needed rather than suggesting that all eight scientific acceptance gates have passed.

## Recovered external-output conflict

The older January JSON repeats withdrawn Coinbase S=-0.3796, reports positive January S near0.9827/0.9811, but its prose claims S=-0.312. The external equity output also cites the withdrawn value and includes eta>1 for one stock despite the model assumption eta in(0,1). These recovered outputs are useful audit evidence, not structural/causal validation. See `research_extension/paper_revision_20261006/t9_recovered_inventory.json` and `t9_archive_audit.json`.

## Execution update: original-input restoration and richer-contract results

The recovery phase has now restored all768 original asset-day objects from current official exchange archives and reproduced their saved core estimates/flow controls. The independently reconstructed joint overlap uses33 checksum/CRC-verified objects and supplies full matrices, residual covariance, responses, clock/state sensitivity, six FEVD horizons and24 orthogonal orderings. These close the named numerical recovery/calculation gates, while causal identification and recorder authentication remain open.

The corrected observed-flow panel has meanQ=.000380685 versus legacy .008153613. The raw-return date interval spans zero. The old uncomputed180% volume headline is replaced by measured75.010858% on the original sampled BTCUSDT dates. Corrected fee inference is scoped to this different diagnostic; a passing TOST at the inherited±.007 margin is economically uninformative at its smaller baseline scale.

The richer exact(x,u) observation case is now solved for a single cohort and for at mostKmax merged groups using2Kmax observations. The proof uses established annihilating-filter algebra and requires exact true-state/demand timing, known anchor/impact and bounded merged order. Noise, ill-conditioning, unbounded order and operational disclosure are separate gates.

Continue with residual/model diagnosis, full semantic prose/literature review, authentication of other supplied samples, existing-policy/calibration audit and independent scrutiny. Historical statements earlier in this plan record the pre-recovery state; current status is in GAPS.md and the gap-closure receipts. The goal remains active and no journal-readiness or10/10 certification is claimed.

## Subsequent model-diagnostic execution

Fixed covariance and prediction alternatives have now been executed. All24 bandwidth/centering cases reject under their asymptotic reference; the alternative complete stable/SPD parameterization agrees with prior bandwidth10 statistics. Whole-date prediction uses only past fitting/scaling and keeps all96 lag/target comparisons. A source-based C2 audit and exact/illustrative assumption-failure witnesses explain why optimizer convergence is not causal identification. Continue with provider authentication, remaining semantic/theory/novelty review, operational calibration and existing policy audit.

## Signed/uncertain loss-contract execution

The signed downstream-output case and hedged-output counterexample are solved. A structural directed-cohort family, common-metric uncertainty/nonlinear/affine bounds, finite-horizon Gaussian contract and explicit nonlinear mark-to-dollar mapping now extend the original risk program. They retain fixed units and declared shock/output assumptions. Actual exposures, full price/fundamental/currency channels, noise/model bounds, cash/margin rules, economic admissibility and independent validation remain required before an operational guarantee.

## Monthly-event execution update

Original calendar-month dynamics are now reconstructed with fitted design and covariance, not a pooledSE borrowed across event dates. All covariance choices and all coefficients are retained, including saturation/high-leverage failures. Reconstructed pretrend references are assumption-sensitive and do not establish parallel trends or causal learning. Continue with provider authentication, existing-policy/calibration audits, remaining original-claim semantics and novelty/independent-review work.

## Switching-likelihood repair in progress

The old marginal-product transition update is replaced in an isolated implementation by exact joint transition posteriors. Three independent tests pass, including exhaustive hidden-path enumeration, boundary resets and likelihood ascent/final-parameter consistency. Market estimation, multiple-start/floor sensitivity and chronological comparison remain active G13 work; no empirical regime conclusion is claimed yet. See `research_extension/gap_closure_20261006/regime_model/REGIME_REPAIR.md`. The delivered 71-page event-study PDF does not yet incorporate these unfinished regime estimates.

## October 7, 2026: current-source reconciliation and regime diagnosis

The completed switching-study data are April2021 ten-second states; forecasts evaluate April13–19, not the2022 dates recorded in the earlier completion receipt. All264 fit likelihoods are independently recalculated; all96 full starts converge, while12 forecast starts and4 selected fits hit iteration limits. BTC low variances bind at the two floors and its SD ratio changes roughly tenfold. All full-versus-volatility-only forecast comparison intervals span zero, which supplies no clear additional coefficient-switching advantage and does not prove absent regimes. Detailed evidence is in `regime_model/market_verification.json`.

The current manuscript contains later edits beyond the source certified by the prior table ledger. Those edits are preserved; localized empirical corrections restore rebuilt monthly contrasts, actual January coverage/negativeQ30 and declared regime limitations. Full current-source lineage, semantic/theorem/policy review and the remaining scientific gates remain active. The old100% local-completion statement is superseded, not used as evidence.

## Economic-contract repair — October 7, 2026

The newly added universal opacity premium/welfare/depth claims are not consequences of the existing identification theorem. The current source now gives a fixed-ticket Gaussian/CARA robust quote with zero-premium cases, an allocation-surplus formula with the missing initial-markup term, a solved explicit static capacity problem, exact depth-dependent Schur conditions, and a positive-feedback counterexample in which higher impact reduces transient magnification. Dealer cash/inventory accounting is repaired to use post-trade inventory in marked P&L. Exact symbolic/rational witnesses and six independent tests are in `economic_contracts/`.

These solve the named conditional formulas and falsify the unsupported universal extensions. Dynamic competitive equilibrium, actual welfare/ambiguity costs, financial calibration and the operational rate/input map remain active gaps. The full work toward9+ is recorded in `NINE_PLUS_PLAN.md`; a rating is not a completion certificate.

The same pass corrects cohort-filter versus closed-loop transfer poles, cancelled merged support, missing reset/noise/uniform-stability conditions, and the false universal timing-invariance wording for signed feedback. Eight focused economic/core tests pass; a constructed signed-timing reversal and exact rational state-space transfer check support the corrections. Full theorem/novelty and empirical claim reconciliation remain active.

The abstention statement in the newer source was restored to the proved scalar Gaussian price experiment, with explicit uniform error control, initial state, positive Gaussian variance and KL/total-variation bound. The broader statement involving exact aggregate demand is unsupported and is qualified by the already proved richer-observation counterexample. Its diagram is now a clean illustration of a probability bound, not a universal pathwise requirement.

## October 8, 2026: input/output gate and current empirical lineage

The old displayed-depth rate map is replaced by a proved finite-window quantity bound with explicit input H, monetary output C, carried initial state, per-quantity cost and other-risk reserve. The bound is sharp for its declared linear criterion and invariant to consistent state-coordinate/quantity-unit changes. Independent LP checks, a repeated-window failure, an omitted-component counterexample and zero-gain/background cases are retained. Exact cohort-splitting checks also show that identical reset price responses can give identical financial input caps without identifying cohort count; cohort ambiguity does not universally imply financial ignorance. Actual exposure/input/noise/capital calibration and operational validity remain open.

The recorded-series measurement table now contains BTC, ETH and ADA and all nine actual state/alignment outputs.54 cells match independently recomputed weighted date means and intervals; the previous SOL label and untraced narrow HAC/raw-return literals are corrected. The actual constructor shifts one future bin, not a separately authenticated future60-second execution window. Cache integrity is verified; provider/licence and serial-inference gates remain open.

All eight user acceptance criteria are preserved with evidence and remaining work in `ACCEPTANCE_MATRIX_20261008.md`. The novelty boundary is provisional, with primary-literature access limits recorded in `NOVELTY_BOUNDARY_20261008.md`. Specialist review has not been obtained.
