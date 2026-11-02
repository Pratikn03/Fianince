# Paper 1 — internal adversarial review (30 October 2026)

Two passes: (1) a line-by-line audit with computations by the AI assistant that helped write the paper;
(2) a second review in a fresh context that saw only the PDF and source text, none of the project's notes
(section 3). Neither is independent review; see `REVIEWER_GUIDE.md`.

Severity: **CRITICAL** = a central result false or unproven; **MAJOR** = a stated result needed a correction or
an added assumption; **MINOR** = wording, constants, references.

## 1. Findings from the line-by-line audit

| # | Severity | Result | Problem | Evidence | Fix (status) |
|---|---|---|---|---|---|
| 1 | MAJOR | resolvent identity (3 places) | H₁ − H₀ = H₁H₀ΔG missed a factor z⁻¹; the passive theorem's non-vanishing step used the wrong function | `phase7_checks.json`: error 1e−3 without z⁻¹, 4e−16 with | fixed; bounds unchanged since \|z\| = 1 |
| 2 | MAJOR | `prop:choice`(ii) | "G is unimodal" is false: in the negative tail G rises back toward zero | `prop_choice_check.json`: 9,229 of 19,814 cases violate whole-domain unimodality, 0 violate the corrected statement | statement and proof corrected; conclusions unchanged |
| 3 | MAJOR | `prop:passive` | sample lower bound relied on KL_T = TD + O(1), not shown uniform in the separation; attainment claimed uniformly | derivation | nonasymptotic Toeplitz bound KL_T ≤ C·T·ε²; attainment stated pointwise only; Gaussian assumptions stated |
| 4 | MAJOR | abstract, introduction, tables | dollar bounds read as applying to any observer; tagging saving compressed to one exponent; passive "same order" claimed as attained | consistency check | scoped to the probing observer; both savings stated; passive claims lower-bound only |
| 5 | MINOR | text after `thm:uniformw1` | "impossible as rates collide, at any sample size" mixes non-identification with cost | — | rewritten |
| 6 | MINOR | proof of `thm:uniformw1` | Lipschitz step holds only near the class; small-N case unaddressed | — | note added (bound trivial after enlarging C) |
| 7 | MINOR (priority) | `prop:esprit` | Katz, Diab and Batenkov (2023) show Prony attains the min-max bound for clustered exponents; the paper's upper bound adapts this | literature search | cited in text and in the comparison table; contribution restated as an adaptation |
| 8 | MINOR | `thm:merged`(ii) | constant K clashed with the number of cohorts | — | renamed C_F |
| 9 | MINOR | results map | CAT-budget row contradicted its table | table 16 | fixed |
| 10 | MINOR | code | grid put a memory rate at 1.006 (`disclosure_value.py`) | — | grid restricted; paper numbers unchanged |
| 11 | MINOR | provenance | Table 5 rows L = 320, 480 had no producing script; finite-horizon appendix missing from the map | — | `hardening/rh_quad.py` reproduces all six values to 5e−14; map rows added |

## 2. Checked and found correct (audit)
- `thm:merged`: transfer function from (1)–(2), partial fractions, no cancellation, degree for a > 0 and a = 0;
  (ii) bound including the ΔG formula and |ΔG| ≤ 2qδ²/ε³ (re-derived symbolically).
- `thm:quantity`: d₂ = −κ²qδ²; exact minimax error and pulse attainment; quantity bound from (10).
- `thm:cap`: every entry of A_t ≤ κ/2 (the off-diagonal bound uses monotonicity of h); nonnegative probes give
  vᵀA_tv ≤ (κ/2)U_t².
- `thm:capital`: coercivity constant m = κ(1 − r)/(1 + r); KL and Pinsker steps.
- `thm:spectral`: Toeplitz symbol 2Re H − κ; Parseval bound. `thm:adaptive`: pathwise Parseval bound and the
  factor kl(0.05, 0.95)/(2z²) = 0.4897.
- `thm:kcohort`: Gauss and Gauss–Radau moments; response-difference orders 2.98, 5.02, 7.05, 9.07 against
  3, 5, 7, 9 for K = 2–5 (`edge_case_search.json`); positive Radau weights.
- `prop:esprit`: Lipschitz kernel map, confluent Vandermonde determinant, Δη-scaling of the moment errors.
- `thm:general`: full line-by-line check of both bounds (Jackson constant, Chebyshev coefficient bound
  B(ρ)^{L+1}, kernel-recovery Neumann series, choice of L, Le Cam/Bretagnolle–Huber step, c* = 1/4).
- `prop:tagged`: IV moment matrix, determinant formula, long-run variance with MA(1) errors.
- `lem:micro`: Kalman gain formula. `lem:cm`: nonnegative, nonincreasing response with peak κ and
  Re H ≥ κ/2 in 3,000 random positive economies, also at a = 0 (`edge_case_search.json`).
- Finite-horizon appendix `fhc:pair`: moment structure (first two moments match, third differs by 1.5δ³).
- Citations: Tsybakov (2009) Lemma 2.6 and Theorem 2.2; Wu and Yang (2020) rate n^{−1/(4k−2)} and moment
  comparison; Bernstein's constant 0.2802 (Varga and Carpenter 1985).

## 3. Fresh-context second review (saw only the PDF and source)

No critical errors: no load-bearing theorem was found false. Five major and eighteen minor findings. The two
headline numerical claims below were re-verified independently before changing the paper.

| # | Severity | Finding | Verified? | Disposition |
|---|---|---|---|---|
| M1 | MAJOR | `thm:discvalue` had no real proof: no tagged reset-experiment model; the (σ/σ_f)² factor unproven (with noisy prices the IV instrument is invalid) | yes (by reading) | Theorem restated with an explicit tagged reset-experiment model; constants depend on (σ, σ_f) and the class; two-sided proof (plug-in least squares; Le Cam); note on why `prop:tagged`'s IV setting differs |
| M2 | MAJOR | "$15M–$356M at calibrated parameters": only σ is estimated; structural parameters and Δη = 0.10 assumed; constant very sensitive; deterministic probes only | yes: C* = 358.8, 179.0, 61.1, 13.9 for a = 0…0.7; 3.9…305.2 for η̄ = 0.2…0.6 | "illustrative parameters (spacing 0.10)", "deterministic probes" in abstract and introduction; sensitivity, adaptivity factor 0.49, Radau orientation and row-spread caveats added to the CAT section |
| M3 | MAJOR | `prop:choice` treats price-only attribution time as exact though `prop:passive` is a lower bound; weight target removes the lower edge | yes | assumption stated; slower price attribution only enlarges the band; weight-target caveat; abstract says "stylised decision model" |
| M4 | MAJOR | worked example rescaled the η̄ = 0.4 constant: 262 should be about 77 par units (4×10⁵ → 1.2×10⁵ USDT) | yes: 76.35 / 76.20 by direct evaluation | corrected |
| M5 | MAJOR | `thm:twocohort` uses w for intensities q, not merged weights; under the defined notation the remark on summed responses would be false; Δη conventions differ across results | yes: summed response 2.353 (intensity) vs 8.551/8.522 (merged) | notation stated in the theorem; Δη spread conventions stated in the CAT section |
| m1 | MINOR | `lem:altpair` atom at rate 0 | — | wording: n-atom merged measure; atom at 0 allowed |
| m2 | MINOR | "unless the number of cohorts and their spacing are known" contradicts `thm:uniformw1` | — | fixed |
| m3 | MINOR | Table 13 row shows L+1 | — | relabelled |
| m4 | MINOR | `thm:rh` closed form is "≥", not "=" | — | fixed |
| m5 | MINOR | 64.76 vs 65.02; λ_L vs λ_{L−1} | — | explained; fixed |
| m6 | MINOR | "certified" infimum on a grid | refinement agrees to 4 digits | stated as numerical evaluation, not interval enclosure |
| m7 | MINOR | Stein vs Chernoff exponent | — | both stated |
| m8 | MINOR | `thm:kcohort` needs Δη < min(r_c, 1−r_c); log(2/β) vs log(2K/β) | — | fixed |
| m9 | MINOR | two-cohort (iii) unbiased only to first order; one-parameter family | — | stated; general K = 2 bound referred to `prop:esprit` |
| m10 | MINOR | `prop:primitives`(ii) transfers W₁ to merged weights, not intensity weights | not yet checked | **open — team review area A/C** |
| m11 | MINOR | `prop:tagged` CLT is not one-dependent; needs w ≥ w_min | — | martingale CLT wording; w_min is in the class of `thm:discvalue` |
| m12 | MINOR | signed weights make T_h indefinite (round trip earns 0.32) | — | cost results stated as positive-economy only |
| m13 | MINOR | "iff" over (0,1) vs η = 1 | — | (0,1] |
| m14 | MINOR | Alfonsi et al. citation | yes (ASS 2012 abstract) | Gatheral 2010; Alfonsi–Schied–Slynko 2012 added; 2016 as multivariate extension |
| m15 | MINOR | rounding mismatches (99,192 vs 99,193 etc.); "0.64–0.92" vs registered range | not yet checked | **open — needs the source JSON** |
| m16 | MINOR | data availability omitted CFTC and Yahoo | — | fixed |
| m17 | MINOR | editorial (cut "Spec." note, commas, "Part 13" references) | — | "Spec." fixed; others open |
| m18 | MINOR | inventory term in the microfoundation remark; "Q-learning has the same form" loose; Δη > 1 region in `prop:choice` | — | **open — wording** |

**Priority (second review).** The logarithmic rate and the moment/polynomial technique are known for general mixing
distributions (Wu–Yang 2020, log log n/log n) and for exponential mixtures (Rebafka–Roueff, arXiv 1002.4516, (log n)^−2α
with matching lower bound); the known-pair δ^−4 law is classical in resolution analysis (Shahram–Milanfar 2005,
IEEE TSP); labelled samples are far more informative in mixtures (Castelli–Cover 1996). All four are now cited, and
the paper claims only the closed-loop, passive and financial forms. No prior passive Whittle bound for K clustered
modes in a closed loop was found.

## 4. Gemini review (third model, harsh-referee prompt, 30 October)

Recommendation: major revision; score 7.8 as a foundational paper. Each point was checked against the source.

| Point | Valid? | Disposition |
|---|---|---|
| G(z) defined with a factor z in Section 2 but without it in Appendix A; McMillan degree at a = 0 inconsistent | **No.** G(z) = Σ wᵢz/(z − rᵢ) is defined once and used consistently; the minimum-phase proof's delay-variable form is (4) divided by z^{K+1}, as it says. Gemini's own counter-check confirms the degree claim | no change |
| Prony proof skips the root-perturbation step | Partly. The inverse-function argument already covers it (Prony's output is F⁻¹(t̂) on the ball), but the proof did not say so | sentence added, with Katz et al. (2023) |
| Passive theorem claims uniform attainment | No — already stated as pointwise only after the earlier fix | no change |
| Regulators do not probe; frame dollar figures as a hypothetical shadow cost | Yes | abstract, introduction, observer subsection and CAT section now say "hypothetical benchmark", "outside participant", "shadow cost"; the supervisor's cost is detection delay (Proposition `prop:choice`) |
| Reset experiments unrealistic | Yes, as a limitation | added: unknown free response is a nuisance that only makes separation harder, so lower bounds hold; upper bounds need reset or known state |
| Known primitives | Already stated | no change |
| Positions vs tagged flow | Already stated | no change |
| Abstract tagging claim needs its observation contract | Yes | "Under the stated observation contracts" |
| OOS primary pass should say it reflects persistence | Yes | added in the sentence itself |
| Conclusion should carry the model qualifier | Yes | added |
| Empty "Probing protocols" heading | Yes (table floated) | intro sentence; table placement fixed |
| Cut the finite-horizon appendix; condense the feedback-measurement appendix | Valid for the journal version | kept in the full SSRN preprint (author's choice); to be cut in the QF build |
| Script names in tables | SSRN keeps them by design (code link); the anonymous build strips them | no change |
| Semi-synthetic injection test on real Binance tape | Useful idea | listed as a candidate run in `evidence_inventory.md`; needs approval and a fixed design |

**Calibration note.** Gemini was the most lenient of the three reviews: it called the closed-loop transmission-zero
extraction "genuinely new", which this paper itself now says is a smooth invertible map that decides the method,
not the rate; and it judged novelty "sufficient" without checking the literature beyond the references given.
Treat its 7.8 as optimistic.

## Two independent referee reports (30 Oct 2026): dispositions

Report A (4/10, reject) and Report B (5.5/10, major revision bordering on reject). Both are AI-generated reviews run by the authors; they are not independent human review.

### Fixed in the manuscript
| Point | Change |
|---|---|
| CAT comparison in the abstract is apples-to-oranges (A, B) | Removed from the abstract and the introduction; abstract now calls the probing figure a shadow price, not a social cost. The comparison stays in Section 6.4 with its caveats |
| "These regimes rest on an implicit claim" overstates (A) | Rewritten: audit trails serve many purposes; the paper studies one question they raise |
| Superseded CAT budget (B) | 2026 CAT LLC budget, $147.0M (31 Mar 2026); market columns recomputed; earlier vintages documented |
| Minimax claim unrestricted (B) | `prop:esprit` restricted to rich classes; singleton counterexample remark |
| c0 in the Prony proof did not keep the perturbation inside the root-separation radius (B) | c0 = min(ρ0, γ/(2L))/C1 |
| `thm:twocohort`(iii) "unbiased to first order" projection estimator unproven (B) | Replaced by reference to `prop:esprit` (K=2) |
| `thm:twocohort`(ii) permutation-invariant range (B) | Stated: only for Δη ≥ 2τq/(q+2τ); W1 statement below that |
| `thm:merged` with η=1 (B) | Effective anchor a′ = a + κM({0}); degree counted over supp(M)∩(0,1) |
| `prop:tagged` CLT for m-dependent sequences not justified with endogenous instruments (B) | Martingale CLT via (Z_t − r_i Z_{t+1})ε_{i,t} |
| α, β undefined in `thm:adaptive` (B) | Terminal test with stated error levels |
| Boundary Λ_N = 4 log(1/ρ) (B) | Strict inequality |
| Notebook references "Part 13, R6/R7" (B) | Removed |
| "certified constant" in conclusion (B) | "numerically evaluated" |
| Fundamental value known; no dealer equilibrium (A) | Stated in the model section |
| Negative CFTC w_c outside the positive economy (B) | Stated; dollar bounds do not apply there |
| Missing literature (A, B) | Leach–Madhavan 1993; Andrews–Cheng 2012; Barth–Kahn 2021 (all verified) |
| J identified only up to realization class (B) | Conclusion corrected; open question stated |

### Not done; author decision needed
1. Cut to a focused ~40-page theory paper; move empirics, FHC, spectral blind spot, feedback appendices out (both reports).
2. A decision proposition comparing aggregate vs cohort-targeted intervention, showing tagged information changes the optimal action (both reports' "single most important change").
3. Real-noise validation (semi-synthetic injection test).
4. A tagged-flow test on CFTC flows (requires registration and approval).

### Not accepted
No point was rejected outright. Neither report showed a central mechanism to be false; the disputes were scope, quantifiers, novelty and economic framing.

## Five AI professor-role reviews (30 Oct 2026, on the 124-page build): dispositions

AI-generated critiques run by the authors (files in `five_AI_reviews_20261030/`). Not independent review. Scores: P1 5.5, P2 5, P3 5, P4 5.5, P5 5.5 (all "do not forward unchanged"). None verified a false theorem, a false number or fabrication.

### Fixed (verified against the source text or primary sources)
| Point (reviewer) | Change |
|---|---|
| Abstract overloaded; dollar figure and CAT in abstract (P2, P4, P5) | Abstract rewritten (~230 words): linear model up front, no dollar figure, failures stated |
| "Registered" read as external preregistration (P3, P5) | Defined as the authors' declaration; "pre-specified" in abstract and introduction |
| Failures buried (P3, P5) | New Table "What the empirical tests found: passes and failures" in the introduction (11 rows) |
| Tagging "does not depend on spacing" too strong (P1, verified: V_i depends on r_i and the price spectrum) | "stays well conditioned / no singularity as rates collide" |
| Thm discvalue (ii) target constant (P1) | c0 Delta-eta with c0 below the radius of a ball in the node class |
| W1 vs fixed-weight loss (P1) | Paragraph after Thm kcohort says which loss each bound matches |
| Prony global inverse (P1) | Injectivity on a neighbourhood, single inverse, nonsingular Hankel, Prony returns F^-1 exactly |
| Proof status (P1) | Front matter lists the five results most needing independent proof check; constants are computed, not theorems |
| "certified" constants (P1, P5) | "numerically evaluated lower bound" |
| General-memory and passive scope (P1) | Qualifiers in the introduction |
| "Competitive dealers"; known fundamental (P2) | "Reduced-form dealer sector ... imposed primitive"; both assumptions in "What we do not claim" |
| Kalman/OGD as microfoundation (P1, P2) | Section and lemma renamed "motivating examples"; memory rate is a tuning parameter of two illustrative families |
| Reset experiments (P2) | Stated as a benchmark experiment no outsider can run |
| No decision where attribution matters (P1, P2, P5) | Stated as the main open economic question in the introduction and conclusion |
| CFTC comparison not equal-estimand; bootstrap near unit root; fast/slow labels; price-source basis; categories; Tuesday snapshot (P3, P4) | All stated in Section 6.3 and Table note |
| Binance: lead with horizon-matched result (P3) | Sentence added; introduction leads with 29/29, median 7.3 |
| OOS forecast wording (P3) | "statistically inconclusive, no evidence of a gain" |
| CAT scope, PII relief scope (Feb 2025: names, addresses, years of birth of natural persons reported with transformed SSN/ITIN), access by SROs, accounts vs algorithms, pseudonymous label (P4) | Policy paragraph rewritten; verified against the CAT Alert 2025-01 |
| MiFID citation (P4) | RTS 24 (Delegated Reg. 2017/580) Art. 2(1)(b)-(c) added (verified via an LME notice) |
| 2016/2012 estimates vs operating budgets; 2025 budget further reduced (P4) | Split into two kinds of figure; "reduced further later in 2025" (a $196M forecast reported Oct 2025; P4's $188M not verified, not used) |
| CAT break-even in results map and conclusion (P2, P4) | Removed; results map row is the hypothetical probing loss; Section 6.2 opens with a "hypothetical scale illustration" disclaimer |
| Economies of scale as CAT design (P4) | Narrowed |
| AI statement incomplete (P5) | Now names Claude, ChatGPT and Gemini and says AI critiques are not independent review (authors must confirm) |
| Date (P5) | "This version: 30 October 2026" |
| van Waarde grammar, Monte Carlo wording, machine-precision wording, 892-economies note (P1, P5) | Fixed |
| Length (all) | SSRN build 130 -> 115 pages: reproducibility map moved to `REPRODUCIBILITY_MAP.md` + `paper1_reproducibility_map.pdf`; finite-horizon appendix replaced by a one-page summary, full note in `paper1_finite_horizon_supplement.pdf` |

### Not done (needs author decision or new work)
- Funding and full competing-interest statements (only the authors know); acknowledgments.
- Companion-paper author list (bibliography lists 5 authors).
- Release tag `paper1-ssrn-v1` to be created at the final upload commit.
- Block-length (26/52-week) and weak-ID-robust intervals for the CFTC test; CME futures returns instead of spot/Yahoo (reanalysis of existing data; needs approval).
- Aggregate-vs-targeted decision proposition (all five reviews).
- Independent human proof check of Theorems prop:esprit, thm:general, prop:passive, thm:spectral, thm:rh.
- 10-15 page faculty synopsis (P5).
- Moving the feedback-index and spectral appendices to a separate paper (P5).

### Not accepted
- P5's alternative title: kept the current title; the abstract's first sentences now say "linear market model".
- P1 #13 "attach a critical-lemma inventory": done as one sentence in the front matter rather than a page.

## Second round: five professor-role AI reviews of the 115-page build (30 Oct 2026)

AI-generated (files in `professor_reviews_round2_20261030/`); not independent review. Scores for posting: P1 6.0, P2 5.5, P3 6.5, P4 7.0, P5 7.5 (after fixes 8.5, 7.5, 8.5, 9.0, 9.2). Forward to a colleague: P1, P3, P4, P5 yes; P2 no. No reviewer found a false theorem, number or regulatory fact (P4 verified every regulatory citation).

Note: part of this round's changes were already in the working tree, uncommitted, when this session resumed (edits dated 23:59-00:00 UTC by another session); they were checked here and kept. They include Proposition prop:target and `theory/targeted_intervention.py`, whose table was reproduced exactly.

### Fixed
| Point (reviewer) | Change |
|---|---|
| No decision where attribution matters (P2; all of round 1) | New Proposition prop:target (market-wide limit needs only S; whether halting one group suffices needs q_i and inherits the (Delta eta)^-(4K-2) cost; tagged data: bounded). Table tab:target reproduced from `theory/targeted_intervention.py`. Abstract, results map, policy opening, conclusion and finite-horizon summary updated |
| CAT market-count columns and break-even sentences (P2, P4) | Removed; Section 6.2 keeps the CAT budget only "for orientation" and says why the two numbers are not comparable |
| Appendices G (spectral blind spot) and H (feedback measurement) stitched on (P1-P5) | Moved to `paper1_feedback_spectral_supplement.pdf`; references point to Supplement S1/S2. SSRN build now 112 pages |
| "Pre-registered" in tables (P3, P5) | "Pre-specified" throughout |
| JSON file names and bug log in text (P5) | Removed (also the trained-learners file name, which left "json,)" after hash stripping) |
| Thm 5.5 finite-sample quantifiers (P1) | h_0 = kappa known; explicit Gaussian event over 2K taps with log(4K/beta); radius condition |
| Thm 5.4 stability and tap horizon (P1) | Added |
| Thm 5.2 8/11 (P1) | Explained |
| Prop 6.1 martingale wording, Thm 5.7 triangle step (P1) | Present |
| Kalman desks vs trading on x_t; known p* (P2) | Reconciled in the remark; known p* is an a fortiori aid for the lower bounds |
| Missing finance literature (P2) | Barberis et al. 2015, 2018; Cespa-Vives 2015; Biais-Foucault-Moinas 2015; Crouzet-Dew-Becker-Nathanson 2020 (RFS, not JF as P2 said). All verified |
| CFTC price-only regression unspecified; weak identification (P3) | Specified (each week's return on its own 12 lags, then two-exponential fit); weak-ID and near-unit-root T^-1 scaling notes |
| Return proxies (P3, P4) | Corrected the description: crude oil and natural gas already use front-month futures; the other six use spot/index/yield (basis ignored). Rerun with CME futures returns not done (needs data access) |
| Positions vs flows; inventory root (P3) | Added |
| Table 16 jackknife note; "333" wording (P3) | Added; "fitted day-demeaned persistences (illustrative calibration)" |
| MiFID RTS 6, firm-specific IDs (P4) | Added |
| Policy summary paragraph (P4) | Added at the start of Section 7 |
| "companion thesis" (P5) | Now "public replication repository" |
| Sentence rewrites (P5) | Applied the clearest ones |

### Not done
- CFTC rerun with CME futures returns for the six spot/index/yield series (P3, P4, P5): needs Yahoo/CME data from Colab and the user's approval; would be reported as a post hoc robustness check.
- Acknowledgments and funding statement (P5): authors must supply.
- Repository name "Fianince" (P5): renaming is the user's decision (GitHub redirects old URLs).
- 35-40 page version / executive summary (P5).
- Independent human check of the five key proofs and of Proposition prop:target.
- Proof that Gauss and Gauss-Radau maximal weights differ for every K (checked K <= 8 only; stated in the paper).
