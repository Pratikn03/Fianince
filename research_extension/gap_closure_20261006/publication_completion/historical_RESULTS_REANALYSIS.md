# Machine Markets — actual revision results

October 6, 2026. These are computed results, not promised future experiments. The review candidate retains all ten original study questions and includes a disposition of all 48 original pages. Its scientific gaps remain explicit. The original PDFs are preserved.

## Corrected primary Coinbase diagnostics

Past-observed 10-second flow, 300-second log-price EMA deviation, gap/date resets, five-horizon burn-in. Intervals are date-level Student-t summaries, not structural/causal learning confidence sets. Dates: April7–19,2021, including partial endpoints.

|Asset|Dates|Segments|Transitions|Q mean [95% CI]|S mean|Maximum fitted rho|Forward-flow Q mean|
|---|---:|---:|---:|---|---:|---:|---:|
|BTC|13|16|102470|0.001935317 [0.000317916,0.003552719]|0.942598321|0.958741998|0.012522669|
|ETH|13|14|102771|0.000979537 [0.000062779,0.001896295]|0.939156249|0.957446043|0.011301826|
|ADA|13|13|102898|0.000616315 [0.000156473,0.001076156]|0.935037706|0.951466299|0.007205755|

All raw-to-cache comparisons are exact for sec/mid/flow/duplicate indicators. Recovered Gemini timing results were rerun into this revision and match the saved agent JSON exactly; all1,995 tested past-minute buy sums per asset close after deduplication. This resolves local timing arithmetic, not provider authentication. Raw-return Q intervals span zero for all three assets. Four no-adaptation null families (60 repeats each) and both timing conventions show that small positive Q is not sufficient to identify adaptive learning. All24 nondegenerate sampling/window cells are saved, including negative/zero-spanning cells.

## Specification tests

|Asset|Moment rows|Rank|df|J statistic|Chi-square p|MD Q|
|---|---:|---:|---:|---:|---:|---:|
|BTC|102454|7|4|41.40631136|2.21440277e-08|0.000831403|
|ETH|102757|7|4|28.30938706|1.07954777e-05|0.000475507|
|ADA|102885|7|4|12.11748801|0.0164986475|0.000910641|

All three reject5%. Successful optimization does not reverse this specification finding. HAC reference inference and unrestricted innovations do not establish a causal learner model.

## Fee contrast — same saved192-row panel

|Outcome|Covariance|Coefficient|SE|df|p|95% CI|
|---|---|---:|---:|---:|---:|---|
|Q|classical|-0.001855525|0.003072041|188|0.5465690|[-0.007915625,0.004204574]|
|Q|asset_cluster|-0.001855525|0.000884149|7|0.0740177|[-0.003946205,0.000235154]|
|Q|date_cluster|-0.001855525|0.003411629|23|0.5917560|[-0.008913017,0.005201966]|
|S|classical|-0.000389699|0.024585136|188|0.9873701|[-0.048887880,0.048108482]|
|S|asset_cluster|-0.000389699|0.019525726|7|0.9846337|[-0.046560703,0.045781305]|
|S|date_cluster|-0.000389699|0.013234149|23|0.9767625|[-0.027766623,0.026987225]|

Q date-cluster TOST at margin0.007: p=0.072594207; equivalence not established at5%. Descriptive asset-assignment rank fractions are Q=0.75, S=1.0. Single treated asset, nonrandom assignment and possible spillovers limit causal interpretation.

The recovered event-study script assigns pooled DiD SE*sqrt(2) to individual dated gaps and literal +180% volume growth. Those operations do not establish the old monthly joint F/p or observed volume response. Correctly dated point contrasts are saved without fabricated inference.

## Saved Binance evidence

768 asset-days,96dates, 6,519,552 fitted states. Maximum Q/S/rho identity error=0.0. Qmean=0.008153613, date-block CI=[0.007295824138671828, 0.009011402701745585]; Smean=0.920554395; positiveQ share=86.84896%; maximumrho=0.976139953. These are saved-derived legacy timing results, not raw reproduction or L3 measurements.

The original Table7 displayed matrix has radius1.002578519, not0.9612. That arithmetic is resolved. A generating joint fit, raw join and residual covariance are still not established after expanded searching; the empirical propagation and FEVD study gates stay open.

## Liquidity, equities and January secondary sample

Corrected first50,000 BTC-record conditional regression: calm flow slope0.626728431, wide-spread0.750974908, difference0.124246478, HAC SE0.218130659,p0.568951347. Residual SD ratio1.450627273. These dimensional slopes are not structural Q. Old62.7x scalar switching output is archived; it does not validate a bivariate structural S or an unsupported extremep.

The supplied equity counts are18308,39555,66862,71750,76466 (272941total), not five equal54588 samples. Every retained session is listed in the candidate. Source/provider stock mapping remains unauthenticated, and event-time fits do not share a physical sampling rate with crypto.

The January file covers January9–20,2023, including partial dates and gaps. It is quote/depth data with OFI, not authenticated executed trades or an untouched whole-month holdout. Primary Q remains positive in its date summary; Q30 is negative with a negative interval. The actual output file preserves all segments and counts.

## Simulation and mathematical results

All48 funded-dealer replay cells (400 seeds each;19,200paths) match the archived halt counts. Exact binomial intervals are generated. These results remain conditional on the preserved flow-moment calibration, which was not independently re-estimated.

At fixedrho=.85, nonnormal theta0,.5,2,8 yields M_C=1,1.383514147,5.337804416,21.301194083 and safe radii1,.722797090,.187342945,.046945725 for budget1. The nonzero examples peak at discrete time6. Constructed worst-direction shocks at the radius attain the budget; slightly larger shocks breach it.

The initial-shock theorem's repeated-input gap now has a separate proved linear induced-gain statement and computable stable-tail bound. A signed/nonnormal finite-horizon construction test attains its scalar-output gain and checks the tail certificate. Applying it to real execution still requires calibrated C,D,units and admissible bounded inputs. A scalar Gaussian surveillance lower bound is proved for its own experiment; it does not prove the old full noiseless control/state claim.

The historical crash source assigns reported feedback parameters and simulates E-mini price/depth. Its Treasury function returns constants. Those outputs are illustrative scenarios, not historical TAQ estimates. Protected E-mini scenarios also change depth/external liquidation, so they do not isolate interceptor effects.

## Expanded evidence search and why gaps remain

The text/archive search inspected14,804 items,10,570unique content hashes, with no archive-read errors. Exact scope/exclusions/hashes and candidate snippets are in `existing_evidence_search.json`. The agent's numeric-token matcher accepts unrelated tokens with sign/percentage rescaling; its “verified” label is not scientific lineage. Already withdrawn synthetic-IV results, earlier repairs and learner outputs were located and remain recovery leads.

T9 temporarily became unavailable and then returned. A fresh458-file inventory includes192 archives/192 checksum files; small result JSONs were read/hashed and two release archives audited. The named binance_1s directory is empty. Large data-archive payload verification is not claimed, and January2025 files are not the original2021–2024 one-second input sample. The older January result repeats withdrawn Coinbase S=-0.3796 and has prose claiming S=-0.312 despite positive numeric S near0.9827/0.9811. The gap register distinguishes these from genuinely unestablished artifacts.

## Delivery and validation boundary

The full review candidate is49pages and retains all original scientific topics; it adds methods, complete dealer/session ledgers, repeated-input mathematics and the48-page disposition. It is a review candidate with unresolved raw/joint/causal/provider/external-review gates, not an externally validated submission. Ten revision tests pass. The final build and visual receipt records exact PDF/source hashes, page count and inspection scope. See `REVISED_PLAN.md`, `GAPS.md`, and `FULL_48_PAGE_AUDIT.md` for active work and the three user-requested expansion deferrals.

## Full original-input recovery and corrected panel

All768 original study units are restored from current official checksum/CRC-verified archives; saved core/flow-control estimates reproduce. The raw archive has66,316,704 rows and66,316,341 unique seconds. Corrected gap-reset fits retain6,513,239 transitions in784 segments. MeanQ is0.000380685 instead of legacy0.008153613; the raw-return interval spans zero. The recovered sampled-day quote-volume increase is75.010858%, replacing the old uncomputed180% literal. Corrected date-cluster feeQ effect=-0.000105705, p=.814284, CI[-.001025969,.000814559]. The inherited±.007 equivalence margin is too wide relative to this corrected diagnostic to establish economic equivalence.

The independent joint original-overlap study supplies complete matrices, covariance, responses and24 ordering sensitivities. Large ordering ranges preclude causal transmission attribution. Exact true-state/demand contracts now have single-cohort and bounded merged-cohort identification proofs; these do not apply to noisy anonymous records. See the gap-closure result files and delivery receipt for exact source/input/output hashes and remaining gates.

## Model diagnostic extension

Independent stable/SPD covariance parameterization and global/segment centering retain all24 reference rejections. The retrospective predictor battery retains513 fold/model records and96 lag/target contrasts; price-loss difference intervals all include zero. Joint ETH/ADA forecasts can worsen. The C2 audit exposes unestablished timing/innovation/regime/label assumptions and includes exact covariance-equivalent branches and a conditional-selection illustration. See `research_extension/gap_closure_20261006/model_diagnostics/MODEL_DIAGNOSTICS.md`. These findings diagnose model limitations and do not establish absence of adaptive trading.

## Risk-contract extension

Signed downstream-only output monotonicity and a hedged-output reversal are proved in fixed coordinates. Structured spectrum-preserving amplification now includes directed and symmetric positive-definite impact families, with15 exact rational tail certificates. Common-metric bounds include changing coefficients, nonlinear/affine residuals, finite-horizon unit roots and Gaussian/moment-tail contracts. Nonlinear mark-to-dollar mapping explicitly requires actual price/currency channels and known positions; stable pricing error alone cannot certify marked wealth. These are conditional mathematical results, not institutional or market-policy validation. The complete suite now passes34 tests.

## Monthly fee-event reconstruction

This reconstructs the original monthly question using the restored original 2022 panel: 192 asset-days, eight assets, 24 sampled dates, two dates per month. It does not add a dataset or establish a causal fee effect.

The monthly model contains asset and sampled-date fixed effects and 11 BTC-by-month interactions, with June as the reference. Rank is 42 and residual degrees of freedom are 150. All 44 coefficients across legacy/observed Q/S match independently aggregated monthly treated-minus-control gaps. Classical, HC1, HC3, asset-cluster, date-cluster and month-cluster calculations are retained.

For observed Q, the five-restriction January–May pretrend reference has classical p=0.323499, HC3 p=0.288727, and date-cluster p=0.0000392661. These differences preclude treating a selected non-rejection as validation of parallel counterfactual trends. One treated asset, few clusters, serial dependence, concurrent changes and spillovers remain limitations.

Month clustering is degenerate because monthly treated interactions fit the treated-month cluster contrasts. Date-saturated interactions likewise make date-cluster event covariance degenerate; HC3 is unavailable at unit leverage. Joint F/p values are absent for invalid references. Individual degenerate contrast entries carry explicit status labels; their numerical zero-width intervals are not valid uncertainty intervals.

Seven focused tests cover point aggregation, QR covariance calculations, relabeling, event clocks, and saturation/high-leverage failures. The cumulative revision suite passes 41 tests. The manuscript lineage ledger checks 28 tables and 3,135 cells against named output fields; this checks rendering and numerical provenance, not scientific validity.


## October 7, 2026: current-source reconciliation and regime diagnosis

The completed switching-study data are April2021 ten-second states; forecasts evaluate April13–19, not the2022 dates recorded in the earlier completion receipt. All264 fit likelihoods are independently recalculated; all96 full starts converge, while12 forecast starts and4 selected fits hit iteration limits. BTC low variances bind at the two floors and its SD ratio changes roughly tenfold. All full-versus-volatility-only forecast comparison intervals span zero, which supplies no clear additional coefficient-switching advantage and does not prove absent regimes. Detailed evidence is in `regime_model/market_verification.json`.

The current manuscript contains later edits beyond the source certified by the prior table ledger. Those edits are preserved; localized empirical corrections restore rebuilt monthly contrasts, actual January coverage/negativeQ30 and declared regime limitations. Full current-source lineage, semantic/theorem/policy review and the remaining scientific gates remain active. The old100% local-completion statement is superseded, not used as evidence.

## Economic-contract repair — October 7, 2026

The newly added universal opacity premium/welfare/depth claims are not consequences of the existing identification theorem. The current source now gives a fixed-ticket Gaussian/CARA robust quote with zero-premium cases, an allocation-surplus formula with the missing initial-markup term, a solved explicit static capacity problem, exact depth-dependent Schur conditions, and a positive-feedback counterexample in which higher impact reduces transient magnification. Dealer cash/inventory accounting is repaired to use post-trade inventory in marked P&L. Exact symbolic/rational witnesses and six independent tests are in `economic_contracts/`.

These solve the named conditional formulas and falsify the unsupported universal extensions. Dynamic competitive equilibrium, actual welfare/ambiguity costs, financial calibration and the operational rate/input map remain active gaps. The full work toward9+ is recorded in `NINE_PLUS_PLAN.md`; a rating is not a completion certificate.

## October 8, 2026: input/output gate and current empirical lineage

The old displayed-depth rate map is replaced by a proved finite-window quantity bound with explicit input H, monetary output C, carried initial state, per-quantity cost and other-risk reserve. The bound is sharp for its declared linear criterion and invariant to consistent state-coordinate/quantity-unit changes. Independent LP checks, a repeated-window failure, an omitted-component counterexample and zero-gain/background cases are retained. Exact cohort-splitting checks also show that identical reset price responses can give identical financial input caps without identifying cohort count; cohort ambiguity does not universally imply financial ignorance. Actual exposure/input/noise/capital calibration and operational validity remain open.

The recorded-series measurement table now contains BTC, ETH and ADA and all nine actual state/alignment outputs.54 cells match independently recomputed weighted date means and intervals; the previous SOL label and untraced narrow HAC/raw-return literals are corrected. The actual constructor shifts one future bin, not a separately authenticated future60-second execution window. Cache integrity is verified; provider/licence and serial-inference gates remain open.

All eight user acceptance criteria are preserved with evidence and remaining work in `ACCEPTANCE_MATRIX_20261008.md`. The novelty boundary is provisional, with primary-literature access limits recorded in `NOVELTY_BOUNDARY_20261008.md`. Specialist review has not been obtained.
