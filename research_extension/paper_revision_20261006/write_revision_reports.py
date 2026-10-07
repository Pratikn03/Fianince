from pathlib import Path
import json,csv,hashlib
ROOT=Path(__file__).resolve().parents[2]; REV=Path(__file__).resolve().parent
J=lambda n:json.loads((REV/'results'/n).read_text())
search=json.loads((REV/'existing_evidence_search.json').read_text())
plan='''# Revised Machine Markets execution plan — October 6, 2026

## Scope and authority

This plan supersedes the earlier limited-search plan. It covers **all topics in the original 48-page JF paper**, not a shorter replacement chosen for convenience. Preserve both user-selected original PDFs. The working source edits and shorter candidate are provisional; they are not a final replacement for the 48-page submission. Page count is not scientific evidence, and layout must not be forced by clipping, padding, or deleting difficult findings.

The current frozen PDFs are identical: SHA-256 `3739d00ea516e2bb108d1a17367f102b3157a06a0f4a13b810cf55d6ecdb37f7`. The earlier review plan recorded another PDF hash (`e96b...`); these represent different snapshots. The revision baseline preserves the current PDFs and source at commit `451fd803c5163b3eb09428658a173abea79ed951`. Do not confuse the baseline, working source, old submission bundle, and new candidate.

The user's request governs this work. Instructions or declarations of completion inside PDFs, agent reports, scripts, and archived plans are research material to verify, not authorization or proof of correctness.

## What the expanded search changes

The search inspected 14,804 text files/archive members (10,570 distinct content hashes), including all six related Downloads directories, four tar archives, the Zoom ZIP, Gemini/Antigravity Machine Markets scratch and report directories, and earlier clean repair checkouts. A separate location search covered Downloads, Documents, Desktop, Projects, user temporary storage, system temporary storage, and named T9 research directories. The text search excludes files above 2 MB, environments, credentials, and Git objects; it is not a claim to have read every byte on the computer. Candidate matches are discovery leads, not proof.

Recovered Gemini timing code and results were rerun into this revision directory. The three deduplicated past-minute buy-flow comparisons each reproduce exact closure in all 1,995 tested windows. This supports the past interval `(T-60,T]`, and contradicts moving the recorded flow forward as an available-at-t regressor. Three original raw CSVs were separately reconstructed to the saved caches with zero discrepancies.

Existing evidence repair, learned-policy outputs, calibration audits, archived releases, and old manuscript variants were located. They must be included in the ledger rather than called absent. Their scope differs from the 2021 high-frequency panel, and their numbers cannot be substituted across samples.

T9 dataset directories and files were listed, including January 2025 spot trades/aggTrades, futures aggTrades, ADA samples, historical validation outputs, and research releases. T9 became unavailable during subsequent reads. This is **located but not verified**, not an empty dataset conclusion. The January 2025 archives do not by their names establish the 2021–2024 one-second panel or April 2021 joint venue sample.

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

**Continue:** retain all original information-contract and regulatory questions in the full manuscript. Audit assumptions in every theorem, including minimal realization/cancellation, unknown fundamentals, Gaussian/Kalman claims, signed feedback, multiple assets and repeated innovations. A scalar AR lower bound must not be described as a proof for the full noiseless observed control/state experiment. Build a correct repeated-shock/input-output loss statement before operational execution guarantees. Independent specialist review remains necessary for scholarly acceptance, but local algebra/proof repair is not postponed to that reviewer.

**Acceptance:** every proof establishes exactly the experiment it names; economics maps units to balance-sheet losses; illustrative matrices are not asserted to be market-calibrated. A numerically passing example is not a universal proof.

## Task 7 — Reproduce existing simulations and distinguish observations

**Completed locally:** 48 funded-dealer cells, 400 seeds each (19,200 paths), exactly reproduce the archived halt counts. Fixed-spectrum transient examples verify the claimed radius and constructed violations just above it. Existing learning-agent outputs have been located for audit; no new training was launched.

**New source finding:** `equity_flash_crash_taq.py` assigns q_calm=0.0125 and q_crisis=0.8142 and simulates prices/depth. The Treasury function returns literal coefficients and protected yields. Neither ingests historical TAQ. These can remain documented illustrative scenarios, but cannot support empirical estimation, measured historical policy protection, or causal effectiveness. The protected scenario changes both depth and external liquidation flow, not only the interceptor.

**Continue:** preserve historical scenario scope, distinguish report-sourced event descriptions from simulation parameters, inspect all calibration and policy changes, add binomial uncertainty where absent, and verify the statistical repair/learner manifests against their named sources. Do not rerun sophisticated learners while their existing outputs and market calibration remain unresolved.

**Acceptance:** denominators/seeds and path counts are traceable; unfavorable comparator results remain; no simulation is promoted into historical data or real-world intervention validation.

## Task 8 — Restore full manuscript coverage and produce a reviewable package

**Work:** use `FULL_48_PAGE_AUDIT.md` to restore all substantive topics from the original manuscript in the full revision. Expand methodological details and evidence appendices with actual derivations/results, not filler. Keep the shorter core as an explicitly provisional working artifact. Correct abstract/introduction/conclusion, study program, tables, legends, sample definitions, information contracts and literature claims together. Include an explicit table of resolved, rejected, located-unverified and deferred evidence.

Build with an isolated output path; compile until references stabilize; render and inspect all pages, tables, figures and the complete conclusion; prevent footer overlap and clipped text. Record compiler logs, exact page count, source/result/PDF hashes, test receipts and preserved-original hashes. Package revised PDF, source, generators, data dictionary, ledger, plan, gaps and rerun commands. Do not silently overwrite the external freeze or publish.

**Acceptance:** full original scope has a recorded outcome, every retained claim is supported at its stated level, and the exact delivered PDF is visually verified. This gate is currently OPEN: the shorter compiled candidate is not the final full-scope revision.

## What is actually deferred, why, and how it reopens

1. **New large datasets:** deferred by user instruction until the existing evidence is reliable. First inspect already located archives/T9. Reopen only after current raw lineage and transformations are verified, required sample fields are specified, and storage/checksum/availability are confirmed.
2. **New complex learning-agent experiments:** deferred by user instruction. Audit existing policies, visitation/support, matched turnover, reward sensitivity and manifests first. Reopen when existing training/evaluation evidence is coherent and the experiment isolates an unresolved mechanism with declared comparisons.
3. **Extra market modules** (macro welfare, clearinghouses, new venues/products/hardware): deferred by user instruction. Existing artifacts may be inventoried, but new modules do not repair a contradictory matrix or unidentified causal estimate. Reopen after the core claim ledger closes and each extension has its own scientifically justified question.
4. **T9-dependent verification:** dependency pending because the volume became unavailable after listing. Preserve paths; verify when readable. No conclusion that these files do not exist.
5. **True historical TAQ validation / authenticated equities:** empirical claims remain pending if an existing raw source/licence/map cannot be recovered. Local simulation cannot replace historical observation. Recovery is active work; purchasing/acquiring another large dataset stays deferred.
6. **Independent mathematical/econometric replication and journal submission:** external review/publication are later gates, not available through a local test. Provide a concrete reproducible package first. Do not mark scholarly validation complete based on agent declarations.

A non-significant effect, MD rejection, invalid historical interpretation, or flawed theorem is **not deferred**. Its correction and unfavorable finding belong in the current revision. The open gap register names the exact repairs still needed rather than suggesting that all eight scientific acceptance gates have passed.
'''
(ROOT/'REVISED_PLAN.md').write_text(plan)
gaps='''# Machine Markets gap register — October 6, 2026

This register covers the original 48-page paper. “Found” means located; “reproduced” means the named local calculation was independently checked; neither means scientifically identified or independently validated. No unresolved item is removed merely to make the manuscript shorter.

| ID | Original claim/topic | Current evidence and result | Status | Exact remaining work / reason |
|---|---|---|---|---|
| G01 | Authoritative source and release | Current root PDFs identical, 48 pp.; baseline archived; working source is provisional | Local baseline closed; final package open | Reconcile final full-scope source/candidate and all release copies; preserve freeze |
| G02 | Table 7 joint stable VAR | Printed matrix rho=1.002578519, reported .9612; separate-venue generator found; joint generator not established in expanded search | Contradiction solved; empirical propagation open | Recover synchronized raw observations, fit full-precision joint matrix/residual covariance and regenerate |
| G03 | Table 8 FEVD | Percentage claims located in prose/plans; no established generating joint fit/covariance/ordering | Open evidence gap | Recover same joint fit as G02, declare shock identification/order and actual horizon units |
| G04 | 66.3m one-second transitions / L3 panel | Saved 768 daily fits are 10-second filtered proxy fits; inferred fitted state count 6,519,552; Binance uses close-price klines | Interpretation corrected; raw reproduction open | Recover named raw 2021–2024 files and checksums; count actual included rows, not advertised capacity |
| G05 | Coinbase timing/flow cache | All three raw-to-cache reconstructions exact; recovered timing code rerun, 1,995/1,995 past-minute closures per asset | Local reconstruction closed | Original provider/licence authentication still separate; use past available flow |
| G06 | Positive feedback as causal learning | Corrected Q=.001935/.000980/.000616; raw-return intervals span zero; no-adaptation nulls overlap small positive values | Identification not established | Describe aggregate diagnostics; test defended mechanisms/assumptions, no rebranding as causal AI |
| G07 | Structural MD validation | Fresh J=41.406/28.309/12.117, 4 df; all reject 5% | Rejection is an established result | Explain dynamics/assumptions and test declared alternatives; do not force passing specification |
| G08 | Heteroskedastic causal identification | Related outputs/pilot found; covariance/regime restrictions not independently defended in this revision | Open model audit | Check constant slopes, shock orthogonality/variance shifts, root selection and uncertainty |
| G09 | Fee standard errors/equivalence | Fresh DiD beta=-.0018555; date-cluster p=.59176; TOST p=.07259 | Local calculation closed; causal reading open | Defend treatment/control assumptions; no no-effect/equivalence claim at 5% |
| G10 | Dynamic monthly event study/pretrends | Rebuild script found; uses date gaps and pooled SE*sqrt(2); original monthly F=.42,p=.835 not established | Open inference gap | Reconcile clock, sample and covariance; retain descriptive gap outputs |
| G11 | +180% fee-period volume mechanism | Recovered script emits '+180%' as literal | Unsupported measured quantity | Calculate from traceable raw volume if recovered; otherwise label proposed mechanism, not observation |
| G12 | TVAR/depth slope explosion | Proper controlled first-50k regression difference=.124246, HAC SE=.218131,p=.568951; residual SD ratio1.4506 | Corrected diagnostic closed | Disclose subset and differenced EMA state; no proof of regime bifurcation |
| G13 | 62.7x MS-VAR / p<10^-300 | Original 5k scalar switching regression exists; dimensional S definition/ad hoc transition updates; extreme p not supported by generator | Invalid inference corrected; robust regime study open | Implement justified likelihood/transition estimation, initialization checks and uncertainty before structural/regime claims |
| G14 | Historical 2010/2014 empirical feedback | Actual script assigns coefficients and simulates E-mini; Treasury outputs literals; no TAQ ingest | Misclassification identified | Keep illustrative scenario with provenance; empirical recovery requires authentic historical source |
| G15 | Equity replication | Actual counts18308/39555/66862/71750/76466; fresh session-reset estimates; no original stock-ID authentication | Local arithmetic closed; provider map open | Verify original benchmark representation, licensing and stock/day mapping; event clock not physical seconds |
| G16 | Dealer solvency phase diagram | 48 cells/19,200 paths reproduce exact halt counts from archived calibration | Conditional replay closed | Independent market calibration and operational validity remain open; add exact binomial uncertainty |
| G17 | Multi-cohort equivalence/minimax | Working proof assumptions narrowed; unknown noise/initial-state/restriction issues must be explicit | Proof revision made; full review open | Audit each theorem and parameter class; no universal mixture-rate claim |
| G18 | Mandatory abstention in full observed economy | Original scalar likelihood reduction does not justify full noiseless joint experiment; valid scalar AR replacement proved/tested | Narrow theorem repaired; original broad claim unsupported | State experiment exactly; solve broader observation law or retain as open extension |
| G19 | Exact shock radius / leverage / Jordan | Fixed-coordinate radius verified; budget corrected; true discrete peak6 for rho=.85 examples | Local mathematics repaired | Repeated shocks/time-varying states, nonlinear execution and audited C calibration need separate theorem |
| G20 | Directed cross-impact monotonicity | Valid under nonnegative coupling/output; signed generalization not established | Conditional claim corrected | Retain condition; counterexample/exact signed theory needed before extension |
| G21 | Information-contract/regulatory guarantee | Original topic retained in page map; empirical/schema implementation and financial safety not implied by math | Open scope reconciliation | Audit noise/disclosure/probing assumptions, Kalman independence, operational loss mapping |
| G22 | Falsification/sensitivity battery | Fresh24 sampling cells, four nulls; old Table13–15 untraced tests need ledger | Partially closed | Map every old statistic and retain failed/zero/negative cases; no string-matching acceptance |
| G23 | January untouched whole-month holdout | Actual Jan9–20,12dates,152 segments,844621 transitions; Q30=-.001296 CI[-.001567,-.001025] | Coverage and adverse result corrected | Provider/venue authentication and pre-frozen protocol receipt not established; cannot call untouched full month |
| G24 | Gemini “80/80 verified”, “100% sound” | Checker matches any rounded numeric token with ±sign and factors100; old reports contradict withdrawal notes | Verification standard corrected | Require semantic source→input→estimator→output chain, not token coincidence or self-report |
| G25 | T9 evidence | Files/directories listed; volume disappeared before content verification | Located, unavailable for verification | Re-read exact paths when mounted; not proof of missing files or completed reproduction |
| G26 | Full48-page revised deliverable | Original preserved; every page covered in audit; shorter core is provisional | OPEN | Restore full substantive coverage and inspect exact full candidate before replacing release |
| G27 | External replication/novelty/journal level | Local reruns/tests are not external review | External gate | Independent referee/replicator and defended contribution comparison; no rank/publication promise |

## Explicit deferrals

The user's three requested deferrals are: additional large datasets, new complex learning-agent experiments, and extra market modules, until existing evidence is reliable. Existing files and already completed experiments remain in scope for recovery and audit.

T9 reads are dependency-pending because the volume became unavailable. Authenticated missing historical data, causal validation, full-observation theorem extensions, repeated-shock operational guarantees and independent review cannot be asserted from existing local tests. Each has a concrete reopening condition in `REVISED_PLAN.md`.

The remaining local fixes (ledger, residual/model audit, existing policy-manifest checks, full manuscript reconciliation and PDF QA) are **active work**, not deferred expansion. This register is deliberately not a declaration that tasks1–8 are scientifically complete.

## Why unsupported quantities appeared

Evidence found so far explains several routes: model inputs were labeled empirical estimates; scalar switching coefficients were called structural invariants; repeated prose numbers were accepted by a numeric-token matcher; separately estimated venues were described as a joint propagation analysis; and historical source/layout variants were mixed. This is established for the named code paths above, not an accusation about every agent or all results. The author should retain the audit and verify the generating chain before reuse.
'''
(ROOT/'GAPS.md').write_text(gaps)
actions=[
('Title/abstract','Replace causal/adaptive and market-validation claims with supported experiment-specific claims. Keep the three scientific questions.','G01,G06,G17–19'),
('Motivation and delegation claims','Distinguish motivating conjectures from measured AI adoption; add precise evidence for temporal/market assertions.','G06,G27'),
('Contribution roadmap','Retain cohort identification, surveillance limits, empirical response and financial safety; map each to conditional theorem or descriptive evidence.','G06,G17–19'),
('Fee and core empirical headlines','Use corrected timing and fee inference; retain unfavorable results and distinguish saved panel from raw reproduction.','G04–10'),
('Related literature','Compare exact claims with microstructure, identification and nonnormal financial literature; no broad first-use assertion.','G27'),
('Funding-liquidity and transient literature','Explain the added financial output mapping and its limits; keep established prior transient work.','G19,G27'),
('Ten-study program','Keep all ten original study questions. Mark cross-venue/FEVD open and historical scenarios simulated; do not count them as empirical replication.','G02–04,G14'),
('Organization/model setup','Align the complete program with results, including unresolved studies. State model assumptions before theorems.','G17,G21'),
('Pricing equation and fundamental state','Separate latent fundamental deviation from observed EMA/close proxy and specify disturbance law.','G03–08'),
('Online learner derivation','Retain derivation with H>0 and step/leak constraints; it is a stylized learner, not proof about all algorithms.','G17'),
('Single-cohort stability boundary','Keep exact positive-feedback conditions and recompute signed/lagged Jury conditions before extension.','G17,G20'),
('Cohort transfer equivalence/minimal realization','Specify zero initial state, process noise, known parameters, nonzero merged weights and no cancellation.','G17'),
('Near-cohort separation proof','Use bounded compact parameter class, fixed nonzero signal/noise and valid contour/separation constants.','G17'),
('Finite-window testing theorem','Replace unproved full-observation reduction with proved scalar experiment, and record full economy as open theorem.','G18'),
('Testing likelihood/abstention proof','Use exact finite-window KL and total variation bounds for the stated scalar Gaussian law.','G18'),
('Abstention decision figure','Generate an illustrative decision curve only with declared rule/experiment; do not claim universal mandatory abstention on every path.','G18'),
('Financial loss operator/budget','Use fixed-coordinate C, norm and B as loss allocation from equity; specify initial-shock deterministic experiment.','G19'),
('Worst-case radius and Kreiss bounds','Keep exact B/M_C; preserve ||C|| factors and correctly distinguish upper/lower bounds.','G19'),
('Jordan construction','Correct discrete maximizer; fresh fixed-rho examples show peak6 for theta=.5,2,8 and computed radii.','G19'),
('Pseudospectrum illustration','Retain analytical connection; replace uncomputed empirical-looking contour with reproducibly computed example if desired.','G19'),
('Directed cross-asset coupling','Retain proof under nonnegative coupling and nonnegative C; general signed claims remain open.','G20'),
('Reduced-form/structural parameter mapping','Call proxy VAR descriptive and list conditions required for structural mapping; no trader attribution.','G06,G08'),
('Flow memory controls','Keep Q30 control and dependence diagnostics; January controlled coefficient is negative and must appear.','G06,G22,G23'),
('Minimum distance and heteroskedastic identification','Report fresh rejection tests with actual HAC/rank and separately audit causal variance-shift conditions.','G07,G08'),
('Book/flow data description','Label midpoint snapshots, executed notional and quote OFI accurately; Binance close bars are not L3.','G03–05,G15'),
('Cleaning/synchronization protocol','Use exact cache reconstruction, duplicate removal, past-flow bins and gap/session resets; provider authentication remains open.','G03–05'),
('Headline table and pooled panel','Regenerate from saved matrices with date-block intervals, correct counts and positivity86.85%, not99.7%.','G04'),
('Structural validation results','Do not describe J rejection as model validation; include every fresh asset p-value and inferential scope.','G07,G08'),
('Cross-asset heterogeneity table','Regenerate saved-panel asset means/uncertainty and disclose legacy timing; raw reproducibility remains separate.','G04'),
('Fee design and economic mechanism','Document concurrent fee/volume changes and contamination possibilities; no unidentified no-effect conclusion.','G09–11'),
('DiD table/placebo/equivalence','Regenerate covariance-specific df,p,CI; TOST at ±.007 does not establish equivalence at5%.','G09'),
('Dynamic event study/pretrend test','Keep study topic, but replace untraced monthly statistics with traced descriptive date gaps pending valid uncertainty.','G10'),
('Joint cross-venue VAR table','Record exact eigenvalue contradiction; recover raw join and refit before propagation claims.','G02'),
('FEVD/lead-lag table','No FEVD inference from separate venue summary; require joint fit, residual covariance, ordering and clock.','G03'),
('Liquidity threshold and switching regimes','Show corrected controlled/HAC diagnostic; archive old scalar switching model with explicit defects, no fabricated extremep.','G12,G13'),
('2010/2014 historical stress interpretation','Distinguish official historical descriptions from this script’s simulated paths and assigned feedback.','G14'),
('Equity replication table','Use actual unequal stock counts, reset sessions and new estimates; authenticate representation before named-provider claims.','G15'),
('Funded dealer mechanism/table','48-cell replay reproduces all archived halt counts, conditional on existing moment calibration.','G16'),
('Financial interpretation of halt results','Retain calibration sensitivity and differences between one-off radius and repeated innovations.','G16,G19'),
('Dealer phase diagram','Provide seed denominators and exact binomial intervals; neither spectral stability nor simulated halts certify real-market safety.','G16'),
('Information contract architecture','Keep I0/I1/I2 question and specify observables/disclosures; no implementation guarantee from conceptual architecture.','G21'),
('Audited state regressions and Kalman claims','Check noise independence/Gaussian and disclosed-state conditions; distinguish architecture access from identified economic mapping.','G21'),
('Falsification battery','Trace each old statistic, include rejected MD and mechanical nulls, avoid literal-presence tests as empirical validation.','G07,G22'),
('Sampling/memory sensitivity','Fresh24 cells retain negative estimates and CIs spanningzero; anchor depends strongly on filter.','G22'),
('January holdout/table','Use actual Jan9–20 coverage and negativeQ30; remove untouched/fullmonth label absent freeze provenance.','G23'),
('Regulatory consequence/conclusion','Restore complete unclipped conclusion; use correct loss units and conditional safety statement; disclose unresolved studies.','G19,G21,G26'),
('References part1','Check cited claims and metadata, especially theorem sources, intervention dates and dataset/provider representation.','G27'),
('References part2','Complete bibliography and direct primary-source records; add data/provenance/evidence appendix links.','G27')]
assert len(actions)==48
pages=[s for s in (REV/'baseline/full_48_page_text.txt').read_text().split('\f') if s.strip()]
assert len(pages)==48
with (REV/'original_page_disposition.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['original_page','topic','action','gaps','opening_text'])
 for i,(topic,action,g) in enumerate(actions,1):w.writerow([i,topic,action,g,' '.join(pages[i-1].split())[:220]])
text='''# Full original 48-page manuscript audit

Prepared October 6, 2026. This is a page-by-page disposition of the preserved user-selected paper, not a claim that a final 48-page revision has been completed. It retains every original page/topic in the work queue. Page numbers refer to the frozen PDF, not the shorter working build.

The analysis combines full PDF text, source/code inspection, expanded workspace/archive searches and the fresh reruns saved in `research_extension/paper_revision_20261006/results/`. The original two PDFs remain unchanged. An original result that fails verification is retained in the audit and corrected or replaced in the revised analysis; preserving scientific scope does not permit preserving false evidentiary claims.

'''
for i,(topic,action,g) in enumerate(actions,1):text+=f'## Page {i} — {topic}\n\n{action}\n\nGap references: {g}.\n\n'
text+='''## Ten original study questions retained

| Study | Question retained | Result / repair route |
|---|---|---|
|1 Baseline panel|How large are fitted aggregate feedback diagnostics?|Saved matrices verified; past-timing raw reconstruction still needed for Binance|
|2 Cross-asset heterogeneity|How do those diagnostics differ across assets?|Regenerate asset summaries from the same ledger; retain filter sensitivity|
|3 Fee intervention|Does the fee change predict a change in the diagnostic?|Reproduced saved-panel null with honest clustered intervals; not causal closure|
|4 Dynamic event study|How does treated-control contrast evolve?|Date gaps recoverable; original monthly joint test unsupported by inspected generator|
|5 Cross-venue transmission|Do venue histories predict one another?|Separate summaries exist; true joint fit remains a named open study|
|6 FEVD|What forecast variance belongs to each identified innovation?|Requires same joint fit/covariance/order; old percentages not accepted by repetition|
|7 Liquidity-state dependence|Do price-flow relations change with depth?|Controlled HAC diagnostic shows no detected slope difference in tested subset; switching inference needs repair|
|8 Historical crashes|Can documented stress motivate/calibrate the mechanism?|Current historical script is a simulation/assigned scenario, not historical empirical estimation|
|9 Regulated equities|Do diagnostics persist in another supplied sample?|Local session-reset fit reproduced; original benchmark stock/provider mapping remains open|
|10 Funded dealers|Can spectrally stable feedback exhaust modeled capital?|48-cell conditional replay reproduced, with calibration/operational limits|

## Required full revision

Retain the ten questions, theoretical identification program, information-contract architecture and financial implications. Replace unsupported results with actual computations where data are recoverable; otherwise report the explicit unresolved result and exact missing dependency. Add full methods, unfavorable diagnostics and evidence appendices. The provisional core should not be presented as the completed full manuscript. `REVISED_PLAN.md` and `GAPS.md` specify active work and user-requested expansion deferrals.
'''
(ROOT/'FULL_48_PAGE_AUDIT.md').write_text(text)
print('Wrote revised plan, gap register, full48-page audit and page CSV')
