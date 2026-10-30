# Paper 1 — Phase 1–2 register (identity, scope, versions, claims)

Status date: 30 October 2026. Statuses use the plan's vocabulary: *Not assessed, Open, In progress,
Internally checked, Independently reviewed, Closed, Removed from scope.* "Internally checked" means checked by
the authors with AI assistance (code reruns, verifier scripts); nothing in this register is independently reviewed yet.

## 1. Identity (Phase 1)

**Working question.** What can market observations reveal about hidden trading groups, and what observation and
economic costs are required to distinguish those groups?

**Primary result (one paragraph).** In a linear closed-loop market where K groups of traders update positions on
exponentially weighted price signals, prices and anonymous flow identify exactly one object, the merged
rate–weight measure M = Σ q_i η_i δ_{1−η_i} (Theorem `thm:merged`). Everything finer is identified only at a
cost that explodes as the groups' memories approach each other: Θ((Δη)^−(4K−2)) independent experiments for K
unknown groups, with matching lower (`thm:kcohort`) and upper (`prop:esprit`) bounds, the same order from passive
data (`prop:passive`), and accuracy 1/log N without the exponential form (`thm:general`). In a market the sample
cost becomes money: executed quantity Θ(δ^−2) and round-trip trading loss or margin capital Θ(δ^−4) for a known
pair (`thm:quantity`, `thm:cap`, `thm:capital`, `thm:spectral`). Class-tagged records remove the barrier
(`prop:tagged`), saving a factor (Δη)^−(4K−4) (`thm:discvalue`), and an observer buys them exactly when that saving
exceeds their price (`prop:choice`).

**Economic significance.** Who-trades-how questions (which group drives a feedback loop) are priced, and their
price decides between waiting for public data, probing with trades, and buying disclosure. Aggregate-risk
questions are cheap from public data (`rem:riskneutral`), so the cost is specific to attribution.

**Boundary with Paper 2.** Paper 1 = what observations reveal and what identification costs. Paper 2 = when
available information supports an exposure bound or admission restriction (guard, depth condition, certification).
Paper 1 cites Paper 2 only for the identification-free alternative; it uses none of Paper 2's results.

**Audience.** Researchers in market microstructure and financial econometrics who estimate trader-type or
agent-based models from prices (the estimates of type-separating parameters in that literature are often weak;
Paper 1 gives a computable reason), and supervisors/exchanges deciding what to record.

**Title.** Pending author choice (Section 5, item T1).

## 2. Classification of results (Phase 1)

| Class | Results |
|---|---|
| Central | `thm:merged` (what is identified); `thm:kcohort` + `prop:esprit` (K-group minimax order); `thm:quantity`, `thm:cap`, `thm:capital` (samples → quantity → capital); `prop:tagged`, `thm:discvalue` (what disclosure buys); `prop:choice` (when it is bought) |
| Supporting | `lem:micro`, `lem:cm`, `lem:toeplitz`, `prop:primitives`, `prop:tied`, `prop:disclosure`, `prop:crb`, `thm:twocohort`, `rem:riskneutral`, `thm:uniformw1`, `lem:altpair`, `thm:general`, `thm:minphase`, `prop:passive`, `thm:spectral` (certified constant); CAT dollar table; CFTC and Binance tests |
| Extension (internet appendix) | `prop:tri`, `thm:adaptive`, `thm:rh`, `cor:garch`; robustness to learning rules (simulations); finite-horizon decision appendix (`fhc:*`, SSRN build only) |
| Candidate outside scope | `thm:blind` (spectral blindness) and `thm:abstain` (finite-window abstention) serve Paper 2's monitoring question; the reduced-form feedback-measurement appendix (`sec:empirics`) is about index construction, not identification. Proposal: keep in the SSRN preprint's internet appendix, drop from the QF submission. Needs author decision. |

Three concepts (plan, Phase 4) map onto the results as follows: **non-identification** — `thm:merged`(i) only;
**finite-sample difficulty** — `thm:quantity`, `thm:twocohort`, `thm:kcohort`, `thm:general`(i), `prop:passive`;
**unstable recovery** — `prop:crb`, `prop:esprit` (inverse-map conditioning), `thm:uniformw1`. The Phase 4 audit
checks that the text never calls a finite-sample difficulty "non-identification".

## 3. Version register (Phase 2)

| Version | Where | Status |
|---|---|---|
| **`paper1.tex` (authoritative source)** | repo `ceiling_suite/papers/paper1/` | Working draft; every other version is built from it |
| `paper1_ssrn.pdf` (named full preprint) | built by `make_wfa.py --ssrn` | Same text + finite-horizon appendix, repo link |
| `paper1_wfa.pdf` (anonymous) | built by `make_wfa.py` | Same text, anonymised, hygiene-stripped; WFA no longer the target, kept as the anonymous build for journal submission |
| `Paper1_QE.pdf` (claude.ai project) | uploaded 26 Oct | **Superseded.** Title "Auditable Memory … Electronic Limit Order Books"; old abstract and introduction |
| `Auditable Memory … .pdf` (claude.ai project) | uploaded 26 Oct | **Superseded.** Same text as `Paper1_QE.pdf` except the AI statement and the companion citation (see O2, O3) |

Differences, superseded → current, at the level of claims: (a) title and abstract reframed (question first; CFTC
result and CAT dollars in the abstract); (b) `prop:choice` added; (c) literature now covers heterogeneous-agent
estimation, closed-loop identification and trader-type inference; (d) account-level capital, near-colliding
rates, learning-rule robustness, spectral blind spot and feedback measurement moved to the internet appendix;
(e) results map row on CAT dollars corrected (O1). Proofs, theorem statements, tables and numbers are unchanged
(76/76 numbers verified by `verify_paper_numbers.py`).

## 4. Claim register (headline claims)

| ID | Claim | Key assumptions | Evidence | Review status | Limitation | Next action |
|---|---|---|---|---|---|---|
| C1 | Prices identify exactly the merged measure M | Linear model, known (a, κ), zero initial state, common probe | Proof `thm:merged`; Hankel-rank check | Internally checked | Model-specific; nonlinear rules can break equivalence | Phase 4 audit; expert review |
| C2 | Known pair: quantity Θ(δ^−2), capital Θ(δ^−4) | Known parameters, deterministic probes, no process noise (iv adds it), linear book | Proofs `thm:quantity`, `thm:cap`, `thm:capital`; ledger identity 5.7e−13 | Internally checked | Lower bound for the stated probe class and contract only | Phase 5: quantifiers, probe class |
| C3 | Certified constant [61.41, 64.48] par units at δ=0.05 | Calibration a=0.5, κ=0.8, q=0.2, η=0.4, σ=0.01 | `thm:spectral`, `thm:rh`; scripts | Internally checked | Calibration-dependent | none |
| C4 | K unknown groups: N* ≍ σ²(Δη)^−(4K−2) | Separated rescaled rates, weights bounded below, reset experiments | `thm:kcohort` (Gauss vs Gauss–Radau), `prop:esprit` (Prony); slopes −5.94…−18.34 | Internally checked | Upper bound only on separated class; constants class-dependent | Expert review (load-bearing) |
| C5 | General CM memory: accuracy Θ(1/log N) | Uniform stability, mass W, ρ<1 | `lem:altpair`, `thm:general` | Internally checked | Constants differ by a factor growing as ρ→1 | Expert review |
| C6 | Passive data: same polynomial order | Single innovation, stationary Gaussian, compact stable family | `thm:minphase`, `prop:passive`; Whittle slopes | Internally checked | Asymptotic in T | Phase 4 |
| C7 | Tagged flow removes the barrier; saves (Δη)^−(4K−4) | Class flow observed with noise independent of prices | `prop:tagged` (IV), `thm:discvalue` | Internally checked | Real data are positions, not flow | Phase 9 |
| C8 | Disclosure is bought iff F/M + c < ℓG; region is an interval | Cost structure of `prop:choice` | Proof; 0 violations in 18,346 cases | Internally checked | Stylised waiting cost; no equilibrium | Phase 8 |
| C9 | Weekly probing loss $15M–$356M per market per year (K=2, Δη=0.10) vs $228.3M CAT budget | Weekly renewal; Roll vs 1-s noise; lower bound, not social cost | `recompute_p1_cat_costs.py`; SEC releases | Internally checked | Renewal frequency assumed | none |
| C10 | CFTC class reports restrict fast-class persistence in 8/8 markets; trend-following H2 fails 4/8 | Registered spec 6f1d6f35…, opened once | `P11_cot.json`, C3/C4 results | Internally checked | Positions not flow; "memory" interpretation is a model mapping | Phase 9 |
| C11 | Binance class ratios: 30/30 width ratio; merged response identified in 5/30 (registered test failed its 80% criterion) | Registered spec 65acda36… | Part 6 results | Internally checked | Mechanical part of the width ratio acknowledged | Phase 9 |
| C12 | Class data do not improve return forecasts (registered, failed); class-state tracking gain is persistence | Registered specs f0182ce5…, 5136cc6b… | OOS results; exploratory decomposition | Internally checked | — | keep as reported |

## 5. Open issues found in this pass

- **O1 (fixed).** Results map said the CAT budget is exceeded "once K≥3 or Δη≤0.04". The table shows the
  K=3, Δη=0.20 row needs 5.5 markets at Roll noise, and the known-pair Δη=0.04 row needs 1.1. Row now matches the
  text: one market exceeds the budget once K≥3 at Δη≤0.10 or K=4 at Δη=0.20, under both noise calibrations.
- **O2 (Pratik).** The two project PDFs carry different AI-use statements. One says the research questions,
  modelling, design, data collection and pre-registration are the authors' own and AI helped derive and check
  proofs; the repo says Claude was used to write and debug code, check derivations and draft text. Only the
  authors can say which is accurate; the published statement must be the accurate one.
- **O3 (Pratik).** Companion-paper citation: one PDF has "Niroula and Niroula (2026b)", the repo has five
  authors (Niroula, Alkhushayni, Chen, Bhavsar, Niroula). Must match Paper 2's agreed byline.
- **T1 (Pratik, title).** "From Human Markets to Machine Markets" is Paper 2's title. Using it for Paper 1 gives two
  papers one name. If the umbrella title moves to Paper 1, Paper 2 must be retitled first.
- **N1 (notation).** `thm:merged`(ii) uses K for a family constant while K also counts groups; `thm:capital` is a
  lemma with a theorem label; `prop:passive` is a theorem with a proposition label. Cosmetic, fix in Phase 11.
- **R1 (rates, for Phase 5).** δ^−4 and δ^−6 are different objects: δ^−4 is **capital** for a known symmetric pair
  (quantity δ^−2 squared through the Toeplitz form) and also the passive/average-power **horizon** for that pair;
  (Δη)^−6 is the **number of experiments** for K=2 unknown groups ((4K−2) at K=2; the finite-horizon appendix's
  Θ(δ^−6) is the same object). The text should say this in one place.
