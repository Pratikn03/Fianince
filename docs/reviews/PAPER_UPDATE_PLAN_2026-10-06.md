# Machine Markets manuscript update plan

Prepared 2026-10-06 for the two user-selected root PDFs: `Machine_Markets_JF_Submission.pdf` and `Machine_Markets_External_Review_Freeze.pdf`. The reviewed PDFs were identical, 48 pages, SHA-256 `e96b091196e691ba90d8e5e28982afa7be42b93d2ebd63a4083e5458fe3d9a23`.

This is a revision plan, not a completed replication, novelty certificate, or publication assessment by an external reviewer. No manuscript, empirical result, or selected PDF was changed while preparing it. Source observations below are from a limited live inspection; a complete dependency and provenance audit remains required.

## Objective and proposed scientific scope

Produce a defensible manuscript on what aggregate financial data can identify about feedback, and why dynamic stability alone is insufficient to bound financially relevant losses. Retain model limits, rejected specifications, null intervention results, and matched-flow counterexamples.

Use three evidence categories throughout: mathematical results conditional on assumptions; observational market estimates; simulation consequences conditional on calibration. The manuscript must not promote one category into another.

The first goal is a corrected internally reproducible working paper. External replication, independent mathematical review, and a literature audit are separate later gates. A top-journal outcome cannot be promised by completing a checklist.

## Live findings that determine the work order

1. Table 7's displayed 4-variable matrix has eigenvalues approximately 1.002579, 0.901782, 0.777625, 0.735615. Its radius contradicts the PDF's reported 0.9612.
2. `empirical_pipeline/binance_panel.py` loads 1-second public klines. It sets `mid = close`; this is a transaction close-price proxy, not an observed bid-ask midpoint or historical book.
3. `empirical_pipeline/feedback_var.py::build_series` constructs log-price minus a trailing EMA, not the raw mid-price return defined in the PDF. It shifts flow forward with `np.roll(..., -1)`. This requires an explicit causal-timing audit.
4. The inspected cross-venue script and summary compare separate venue estimates. They do not themselves produce the joint 4-variable VAR shown in Table 7. Another generating artifact may exist; locate it before concluding that it is absent.
5. The current JF LaTeX source already explicitly acknowledges the minimum-distance specification rejection. That wording is clearer than the reviewed PDF. Reconcile versions before making duplicate edits.
6. The PDF has overlapping footer/body text and a cut-off conclusion. The source contains `\enlargethispage{12\baselineskip}` near the final sections; investigate these layout overrides.
7. The current headline checker mainly asserts that expected numeric strings are present. This verifies textual synchronization, not that estimates were recomputed correctly.

## Stage 0 — Establish artifact authority and a revision baseline

Tasks:
- Select `paper/Machine_Markets_JF_Submission.tex` as the revision target for this requested paper after verifying its correspondence to the reviewed PDFs.
- Record commit, clean/dirty state, source hash, included tables/figures, compiler, Python/dependency versions, PDF hashes and page counts.
- Map root, paper-directory, external-review and submission-bundle copies. Preserve the reviewed PDFs as a reproducible baseline.
- Separate planned revision output from existing release output. The JF build script currently copies into root and the submission bundle; add a candidate-output workflow before using it for revisions.
- Note that `tools/build_paper.py` builds the integrated master source, not the selected JF source.

Deliverable: a version/build map and revision baseline manifest.
Pass: one documented authoritative source and dependency set can produce one clearly identified candidate artifact; release copies are not silently overwritten.

## Stage 1 — Build the claim-to-evidence ledger

Tasks:
- Inventory every substantive number in the abstract, main text, tables and figures, including confidence intervals, sample sizes and test statistics.
- For each, record source file/hash, generating function, variable definitions, date window, estimator, output field, rounding and claim type.
- Classify entries as reproducible, requiring correction, unsupported pending provenance, or simulation-only.
- Locate the saved full-precision Table 7 matrix and its raw-data join. Recompute eigenvalues and dependent impulse responses/FEVD from that same matrix. If it cannot be traced, remove the propagation table until independently rebuilt.
- Rebuild manuscript tables from output data rather than repeated literals.
- Upgrade headline checking to recompute identities and numerical statistics. Do not write tests that force old estimates to remain unchanged.

Deliverables: claim ledger; regenerated numeric tables; semantic verification report.
Pass: every retained headline claim has a reproducible derivation, and no table has an unresolved internal contradiction. Unsupported claims are removed or labeled pending.

## Stage 2 — Reconcile data, variables and time conventions

Tasks:
- Create a data dictionary for each sample: provider, actual venue/instrument, UTC bounds, observed fields, clock type, row counts before/after cleaning, licensing and hashes.
- Label Binance klines as price/volume bars. Do not describe their close-price column as bid-ask midpoint or their sample as full L3 order books.
- Distinguish executed signed flow, quote/book OFI, depth, and flow proxies. Document conversions and units.
- Decide the primary observable state from scientific considerations: raw returns, EMA deviation, or another justified state. If retaining EMA deviation, consistently describe an operational reference rather than observed fundamentals.
- Derive the mapping from latent theoretical state to observed state, including filtering-induced memory and correlated innovations. If no valid equivalence is established, call the VAR a reduced-form diagnostic.
- Audit bin endpoints and every shift: explicitly list what information is available at t and the execution interval associated with each row. Test the pipeline on hand-built timestamp examples.
- Audit forward/backward fills, stale rows, duplicated renders, day/session boundaries and discontinuities. Never form a transition across unrelated sessions.
- Reconcile January holdout dates with actual coverage; avoid claiming a complete calendar month.
- Trace FI-2010 stock/day identifiers to their original representation. Equal counts are not proof of fabricated boundaries. Verify normalization and event-clock interpretation before cross-market comparisons.

Deliverables: corrected data section, timing diagrams, data dictionary and transformation audit.
Pass: every empirical equation uses the same variables and timing as the implementation; actual missingness and coverage are disclosed.

## Stage 3 — Test whether the feedback signal exceeds mechanical filtering effects

Tasks:
- Establish baseline results for the correctly defined primary observable state before selecting robustness variants.
- Run null simulations with no adaptive feedback: martingale prices passed through the same EMA; persistent exogenous flow; order-splitting without adaptive learning; common shocks to prices and flow.
- Apply identical cleaning, filtering, timing, estimation and uncertainty calculations to null and observed series.
- Compare raw-return and EMA-state diagnostics where scientifically meaningful. Report residual autocorrelation and full fitted spectral radius, not only S.
- Evaluate declared sampling/window/lag grids. Distinguish a predeclared robustness grid from exploratory specification search.
- Preserve negative or failed cells. Inspect weak denominators in Q = J12*J21/(1-J22) and uncertainty near singularity.
- Use dependence-aware uncertainty at the asset-day/block level and justify clustering for each estimator.

Deliverables: mechanical-null comparison table; estimator diagnostics; uncertainty/sensitivity figures.
Pass: the manuscript either shows evidence beyond declared mechanical nulls or explicitly limits the result to a filtered aggregate descriptive statistic. A positive point estimate alone is not sufficient.

## Stage 4 — Resolve specification and structural identification claims

Tasks:
- Preserve the MD rejection J=73, df=4, p<0.001. Verify moments, normalization, HAC weighting and degrees of freedom from the actual generating script.
- Determine why the model fails: lag order, filtering, heterogeneity, regime mixture, residual dynamics or another diagnosed cause. Specify remedies before comparing them; avoid searching until a p-value passes.
- Describe unrestricted-covariance MD as dynamic reduced-form estimation unless additional structural restrictions genuinely identify causal coefficients.
- For heteroskedastic identification, justify coefficient constancy, structural shock orthogonality, nonproportional variance shifts, root/sign selection and regime selection. Report uncertainty and failed identification cases.
- Do not label identified aggregate shocks as specific traders without independent evidence.

Deliverables: explicit assumption table, MD diagnostic results and revised identification section.
Pass: causal claims have defended identifying assumptions; unresolved estimates remain reduced-form and model rejection remains visible.

## Stage 5 — Reanalyze the fee intervention with appropriate limits

Tasks:
- Document fees, affected pairs, accompanying volume/reward-rule changes, and later policy changes affecting treated/control pairs during the study window.
- State the effect being estimated and explain the single-treated-asset design, spillovers and treatment-assignment assumptions.
- Reproduce DiD and event-study estimates from the same audited panel. Resolve twice-monthly sampling versus month-level event bins.
- Report intervals and sensitivity to defensible inference methods. Eight assignment permutations give coarse resolution; do not portray this exercise as high-powered randomized inference.
- Treat failure to reject pre-trends as absence of detected differences, not proof of parallel trends.
- Predefine economically interpretable equivalence margins. Under the paper's reported small-cluster reference, one TOST side has p=0.069, so equivalence at 5% is not established.
- Trace the 180% volume increase to a reproducible definition/window. Discuss changed incentives before assigning it to learning intensity.

Deliverables: intervention chronology, reproducible DiD/event-study tables, intervals, placebo/sensitivity appendix.
Pass: no-effect, equivalence and mechanism statements accurately match the available precision and assumptions. A null result may remain the final result.

## Stage 6 — Audit theoretical statements and their financial interpretation

Tasks:
- For merged-cohort equivalence, state initial/reset conditions, known parameters, treatment of zero merged weights, pole cancellations and generic/minimal-realization conditions.
- Put uniform stability, symmetric alternatives, probe power and observation-noise assumptions into the separation theorem statement. Distinguish a lower bound from an attained detection rate and deterministic probing from passive inference.
- Audit abstention assumptions, observed-state definition, initialization and uniformity of finite-window probability bounds. Distinguish required positive abstention probability from deterministic abstention on every realization.
- Correct the discrete peak of t*rho^(t-1): the written ceiling of -1/log(rho) is not generally its exact integer maximizer (rho=.85 peaks at t=6).
- Specify economically meaningful state scaling, shock sets and the portfolio-loss operator C. Normality/transient Euclidean norms depend on coordinates even when eigenvalues do not.
- Explain whether B=gamma*L*E is a modeled exposure/margin allowance or actual loss-absorbing equity. Do not equate greater leverage with more real capital without a balance-sheet derivation.
- Keep full-state Kreiss bounds distinct from arbitrary output-operator bounds. Repeated shocks require input-to-output/cumulative bounds beyond a one-time initial disturbance.
- Audit the gating implication from order volume to the full state disturbance; bounding one coordinate is not automatically an upper bound on the whole state norm.
- Obtain independent mathematical review of the final statements. Formal-code bridges validate only the properties actually encoded, not automatically the manuscript's full probability/economic claims.

Deliverables: repaired theorem statements/proofs, economic units appendix and numerical counterexample checks.
Pass: every theorem conclusion follows under its explicit assumptions, and financial interpretation matches the state and shock model.

## Stage 7 — Separate solvency mechanisms in simulations

Tasks:
- Separate inventory-capacity halts, margin breaches and equity insolvency, with explicit accounting and criteria.
- Keep nominal S, effective S and actual spectral radius in all tables. Supercritical inventory examples cannot establish failure inside the stable regime.
- Distinguish transient amplification from persistent flow accumulation. Retain variance-, autocorrelation- and long-run-variance-matched benchmarks.
- Identify a targeted comparison holding spectrum, economically defined shock set and loss operator fixed while changing transient amplification, if feasible within the model.
- Inspect actual loss magnification rather than relying on labels such as non-normal.
- Evaluate proposed gating against simple size/depth/inventory limits under matched operating conditions. Measure execution delay, fill rate, liquidity, rejected volume and failure as well as drawdown.
- Label flash-crash exercises calibrated illustrations, and show sensitivity to uncertain calibration values.

Deliverables: mechanism comparison, separate failure tables and gating tradeoff results.
Pass: claimed mechanisms are supported by the relevant counterfactuals; numerical results are not generalized into demonstrated real-market policy benefits.

## Stage 8 — Verify and sharpen novelty

Tasks:
- Conduct a primary-source literature review of closed-loop microstructure, realization/observability, near-coincident pole testing, abstention and non-normal financial dynamics.
- For each proposed contribution list prior result, inherited technique, new statement, changed assumptions and new economic implication.
- Recast standard mathematical tools as foundations rather than newly invented results.
- If evidence supports it, focus on one principal advance with supporting empirical diagnostics. Otherwise narrow the paper to its defensible contribution instead of expanding its scope.

Deliverables: contribution comparison table, revised literature section and explicit novelty paragraph.
Pass: novelty claims are specific and attributable. Independent field review remains separate from internal screening.

## Stage 9 — Rewrite and rebuild the selected manuscript

Tasks:
- Rewrite abstract and introduction after final results are known. Lead with the one question answered and separate theory, observational evidence and simulations.
- Rewrite data/methods to match audited implementation; regenerate every table and figure.
- Keep key evidence in the main text and move secondary diagnostics and calibrated examples to the supplement where appropriate. Do not preserve an arbitrary page count by clipping content.
- Replace unsupported universal/production/regulatory claims with conditional statements.
- Remove excessive page-enlargement overrides; allow natural pagination. Render all pages and check equations, table readability, figures, captions, footers and the complete conclusion.
- Verify bibliography metadata and cited institutional details.
- Synchronize README, cover letter, disclosures and publication packet with the corrected manuscript. Current repository descriptions refer to other editions and stronger claims; they cannot serve as authority for this candidate.

Deliverables: corrected candidate TeX/PDF, supplement, build log and visual review checklist.
Pass: complete readable PDF, no missing conclusion, unresolved references or numerical/prose disagreements, and no stale package claims.

## Stage 10 — Reproducibility and release gates

Tasks:
- Execute only affected pipeline stages first, using the declared environment; broaden checks when shared changes justify it.
- Reproduce retained headline claims from audited inputs in a clean environment. Record unavailable datasets and external requirements instead of filling gaps with preset output numbers.
- Verify raw-data hashes, analysis manifests, seeds, output hashes and claim derivations separately from software unit tests.
- Seek an independent econometrics review and an independent mathematical review, preserving unfavorable feedback.
- Produce a candidate release receipt with exact source commit, versions, hashes, page count, named checks and unresolved limitations. Preserve the previous release.

Pass: no unresolved critical contradictions, documented scientific limits, reproducible retained numbers, readable manuscript, and aligned submission package. External replication must be labeled pending until someone independent actually performs it.

## Work priority and stopping rules

Immediate: artifact/source reconciliation; Table 7; true dataset and observable definitions; timing; full PDF pagination. These can change the meaning of all later results.

Next: claim provenance; mechanical nulls; MD rejection; fee inference; theorem/economic units audit.

Then: simulation mechanisms; novelty review; rewrite; clean reproduction and independent review.

Defer large new datasets, complex learning-agent training, extra market modules and production claims until the existing evidence is reliable. New data should answer a diagnosed scientific gap. Correctness and traceability are higher priority than more studies.

When a result cannot be supported, remove or narrow it; do not force it to match the old manuscript. If stock/date identification is unavailable, retain an explicitly pooled sample or withdraw the stock-specific claim. If joint venue data cannot be synchronized, report separate-venue comparison rather than propagation. If adaptive feedback cannot be separated from filtering, make that identification limit a central result.
