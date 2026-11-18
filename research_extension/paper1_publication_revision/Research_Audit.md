---
title: "Paper 1: Revision, Rating, and Research Audit"
subtitle: "Observationally Equivalent Algorithms"
date: "14 November 2026 · AI-assisted review for the authors"
---

The strongest version of this paper explains **why estimating a market's aggregate response can be much easier than deciding whose trading to restrict**. That is a useful finance question with a defensible theoretical mechanism. The supplied SSRN draft weakened that contribution by making several broader claims than its proofs establish. The revised manuscript repairs those claims, adds an explicit intervention-loss result, improves the forecasting argument, and separates formal, numerical, and empirical evidence. It also incorporates the three new SSRN results supplied during this review, with corrected initialization, loss and observation conditions.

The delivered PDFs are revised research drafts suitable for author and referee review. They are not certified as accepted, independently reviewed, fully formalized, or empirically validated. This audit addresses every gap identified in this review. It does not establish that no other gap exists in the inherited proof corpus.

## Numerical rating and conditional ceiling

These scores are my structured editorial judgment, not measured probabilities of publication. Treat differences of roughly three points as judgmental uncertainty. “Ceiling” means a demanding target for this same research contribution after the specified evidence and proof obligations are met; it is not a mathematical upper bound on the author's future work.

| Dimension | Maximum | Supplied SSRN draft | Delivered revision | Conditional ceiling |
|:--|--:|--:|--:|--:|
| Distinct contribution relative to prior literature | 20 | 14 | 16 | 17 |
| Mathematical validity, assumptions, and claim discipline | 25 | 18 | 23 | 24 |
| Economic interpretation and decision relevance | 20 | 15 | 17 | 19 |
| Evidence and connection to observable markets | 15 | 7 | 8 | 13 |
| Reproducibility and traceable verification | 10 | 8 | 10 | 10 |
| Exposition and organization | 10 | 6 | 9 | 9 |
| **Total** | **100** | **68** | **83** | **92** |

The revision gains points because its statements now match their experiments, its new arguments have explicit assumptions, the numerical information calculation is stable, and the empirical defects are documented and tested. It receives only a small evidence increase: synthetic results and code repairs do not create a real-data intervention test. A full proof audit by people who did not develop the manuscript also remains important.

At 83, I see a serious specialized theory submission candidate after the authors complete their review. At 92, I would expect a substantially stronger contribution with independently checked central proofs and convincing evidence or an unusually sharp economic decision result. No journal acceptance probability is warranted. Adding pages, more theorem names, or more passing fixtures alone would not move the paper to that ceiling.

## The contribution that a finance reader should retain

In the positive linear-feedback economy, the response kernel aggregates the effects of different trading groups. Multiplying every group's activity by the same factor changes the aggregate budget in a way determined by that kernel. Halting a particular group depends on its separate weight. Moment-matched populations can have nearly identical public responses and a persistent difference in the outcome of the halt.

For the worked two-group example, both original markets are stable, with a feedback budget near 0.5006. Halting the largest group leaves budgets near 0.3945 and 0.3455. A prudential ceiling of 0.375 separates the decisions. A common one-third scaling meets that ceiling in both. The relevant distinction is the effect of the intervention, not whether an unstable market has been stabilized.

The revised corollary converts the testing problem into an economic loss bound. If an unsuccessful halt costs $b$ and an unnecessarily broad restriction costs $c$, the equally weighted expected loss is at least

$$
\frac{\min(b,c)}2\bigl(1-\operatorname{TV}(P_0,P_1)\bigr).
$$

The Gaussian information bound then gives a necessary observation budget. A tagged Gaussian experiment gives an explicit sufficient budget for the same binary decision. The costs remain specified primitives. The result is a useful application of established decision theory, rather than a newly invented statistical principle or an estimated welfare benefit.

## Literature comparison and novelty boundary

This review checked the new theorem statements against the mixture, super-resolution, prediction, control, and identity-disclosure literatures. It also searched for recent related work. Discovery is not an exhaustive novelty certificate. The complete 2003 Ing–Wei article was not accessible through the publisher; its relevant expansion was checked in the authors' 2005 restatement. The Frino et al. comparison uses the publisher and author-institution records and accessible abstract, not an independent audit of their full proofs.

| Closest work | What is already established | What this paper must contribute |
|:--|:--|:--|
| [Heinrich and Kahn, finite-mixture rates](https://doi.org/10.1214/17-AOS1641) | Local Wasserstein rates depend on component collisions under strong identifiability. | A financial feedback experiment and intervention comparison. Do not claim the collision exponent itself as new. |
| [Batenkov, Goldman and Yomdin, super-resolution](https://arxiv.org/abs/1904.09186v2) | Clustered nodes and amplitudes create strong error amplification in spectral measurements. | Specify why the market observation law has the stated information cost. Their Fourier experiment is not passive market data. |
| [Ing and Wei, same-realization prediction](https://arxiv.org/pdf/math/0602326) | Least-squares AR prediction has a complexity and approximation expansion under stated conditions. | Verify those conditions for the feedback model and separate fixed-process asymptotics from uniform collision claims. |
| [van Waarde et al., data informativity](https://arxiv.org/abs/1908.00468) | Some decisions or control objectives need less information than full system identification. | Show the particular common-versus-class-specific financial decision and its quantitative cost. |
| [Hendry and Hubrich, aggregation and forecasting](https://doi.org/10.1198/jbes.2009.07112) | Disaggregated information can help predict an aggregate. | State exactly when feedback components add no information, and where exogenous component dynamics restore value. |
| [Linnainmaa and Saar, investor identity and order flow](https://doi.org/10.1093/rfs/hhs002) | Broker identity can convey investor information relevant to price formation. | Avoid a general identity-irrelevance claim. Distinguish response identification from private-information inference. |
| [Frino et al., delayed identity disclosure, 2026](https://researchers.mq.edu.au/en/publications/revealing-the-invisible-the-role-of-delayed-trader-identity-discl/) | A recent model and institutional-trade evidence connect delayed disclosure to price informativeness. | Explain the different common-signal assumptions and supervisory objective; “identity can matter” is not new. |
| [Lux and Zwinkels, empirical validation](https://research.vu.nl/ws/files/129130045/LuxZwinkels2018_Empirical_validation_of_agentbased_models.pdf) | Heterogeneous-agent estimation faces serious practical identification difficulties. | Derive a mechanism under an explicit model; do not treat difficult estimation alone as evidence for that mechanism. |
| [Sanders, Irwin and Merrin, large-trader forecasts](https://doi.org/10.22004/ag.econ.54547) | Predictive tests of position reports in agricultural futures supply context. | Avoid extrapolation to every asset or a causal validation of feedback sufficiency. |

The revised introduction adds the two identity-disclosure comparisons. Its novelty statement emphasizes the model, observation contract, intervention, partial disclosure, and pooling restrictions. General aggregation, moment matching, Blackwell-style decision comparisons, and the AR risk expansion are credited to their existing literatures.

## Gap inventory: mathematics and interpretation

“Repaired” means the delivered text or code addresses the identified defect. “Scoped” means an unsupported extension has been removed or made explicitly conditional. “Open” means the stronger research result still needs evidence or a proof. A scoped theorem can be valid even though a more ambitious theorem remains open.

| ID and gap | Repair or required test | Status |
|:--|:--|:--|
| G01. The kernel was called a minimal sufficient statistic. | Define it as an identifying functional of the population under the full-response experiment; distinguish a parameter reduction from a statistic of a finite sample. | Repaired in main and supplement. |
| G02. Exact non-identification and weak identification were conflated. | Separate equal merged measures, nearly colliding types, and finite noisy records. Use distinct quantifiers for equality and lower bounds. | Repaired in framing. |
| G03. Every smooth family was said to have the same attainable rate. | Give the parameter-independent smooth-rule counterexample; retain a worst-case lower bound and a conditional upper bound. | Repaired; restricted linear-cluster attainment is now proved, while general attainment remains open. |
| G04. Initial information in the Gaussian experiment was incomplete. | Require a common observed initial history or common observed state law; otherwise include initial KL information. | Repaired proof and theorem. |
| G05. Probe strength could change the derivative constant. | Require the second-moment envelope to be uniform over dates, spreads and the admissible policy class before asserting a rate. | Repaired; unrestricted high-energy probes excluded. |
| G06. Bounded saturation was treated as bounded parameter derivatives. | State the derivative bound itself. Supply the geometric-history envelope argument for appropriate linear kernels. | Repaired; generic nonlinear derivative control open. |
| G07. The upper bound used a different observation experiment. | Explicitly identify fixed-history noisy flow observations. A transfer to passive prices requires a feasible history design and its noise law. | Scoped; general transfer open. |
| G08. The minimum-distance estimator needed existence and optimization control. | Assume compactness and continuity; prove the $2\|\bar\xi\|+\zeta$ bound for criterion tolerance $\zeta$. | Repaired; deterministic inequality checked in Lean. |
| G09. Local jets were being used as evidence for a global inverse bound. | Retain local numerical evidence and state the uniform inverse inequality as an independent assumption. | Restricted linear-cluster inverse theorem now proved; unrestricted global theorem open. |
| G10. Wasserstein accuracy, weight recovery and rate recovery were mixed. | State each loss and its accuracy scale in the theorem's observation contract. A $W_1$ error proportional to spread differs from fixed accuracy of each weight. | Clarified; no cross-loss inference claimed. |
| G11. Information slopes used unstable finite differences and Gram inversion. | Use analytic response derivatives, high-precision QR nuisance projection, positive information checks, and precision replication. | Repaired in a new reproducible check. |
| G12. Zero initial states and a stationary infinite past were mixed. | Split the forecast theorem into two regimes; obtain stationary oracle risk directly from the actual current states. | Repaired; residual-state identity checked in Lean. |
| G13. Known weights were insufficient without known memory rates. | Specify all feedback parameters needed to reconstruct group states in part (i). | Repaired. |
| G14. Unknown fixed constants were described as additional sigma-field information. | Distinguish known-parameter information sets from an implementable predictor versus a parameter/state oracle. A Bayesian/minimax value requires its own model. | Repaired. |
| G15. AR asymptotic assumptions and estimator conventions were vague. | Use iid Gaussian innovations, a fixed stationary population, explicit common fit rows and a permissible candidate-order sequence. Check stability and summability. | Repaired on paper with a cited statistical ingredient. |
| G16. The approximation constant omitted stability and innovation scale. | Prove $A_L\le\sigma^2(\kappa W)^2\bar r^{2L}/[(1-S)^2(1-\bar r^2)]$. | Repaired with explicit derivation. |
| G17. Pointwise asymptotics became a uniform or monotone irrelevance claim. | Remove the finite-sample/uniform/monotone assertion; retain the fixed-process result and explicit approximation bound. | Uniform cumulative log-loss theorem now proved; uniform estimated-predictor MSE theorem open. |
| G18. Observed pricing errors were identified with traded prices or returns. | Give the Gaussian hidden-state counterexample: a tag can improve filtering without advance news. State P1F as a related predictive comparison. | Repaired with proof and numerical check. |
| G19. The informed-trader example lacked complete timing. | Specify offsetting orders revealing next-period news, canceling in public flow; distinguish an existence example from equilibrium. | Repaired with explicit construction. |
| G20. Exogenous-flow irrelevance omitted observation assumptions. | Require exact aggregate flows, known recoverable feedback, appropriate initialization and innovation independence. | Repaired. |
| G21. Hard-limit calm equivalence was extended to smooth saturation. | Keep the exact claim for band-linear hard limits; distinguish noiseless small-probe identification for smooth shapes. | Repaired. |
| G22. The last tag was declared valueless. | State equality of the leading spacing exponent; give an independent-report example that halves variance. | Repaired; arithmetic inequality checked in Lean. |
| G23. Decision importance was insufficiently quantified. | Add a two-action loss corollary, tagged Gaussian upper bound and a stable worked example with a positive limiting margin. | Repaired at the theoretical level; monetary calibration open. |
| G24. Equilibrium and policy statements lacked invariance qualifications. | Restrict pathwise equivalence to common causal strategies and public payoffs; require a separate argument for behavioral responses to intervention. | Repaired in interpretation; richer endogenous policy games open. |
| G25. A latent atom was treated as an executable account identity. | State the verified class-to-account mapping needed for targeted action; include relabeling and account-splitting stress tests in future designs. | Scoped; institution-specific implementation open. |
| G26. Shared memory across markets was presented as a fact. | Make shared rates and sufficiently diverse participation explicit hypotheses. Distinguish local identification from global uniqueness and test cross-impact violations. Add a full-column-rank block-Hankel certificate for exact global reconstruction. | Generic and rank-certified compact-class global recovery proved; exceptional rank-deficient classes remain open. |
| G27. The forecast-drift simulation selected its window on evaluation error. | Withdraw it as validation; supply a fixed-order, fixed-seed stationary check. For drift, preselect the rule, enforce increment bounds and derive uniform dependence bounds. | Selection problem repaired in evidence use; drift forecast theorem open. |
| G28. Calendar-year lower bounds sounded like market estimates or sufficient sample sizes. | Label a particular moment-matched worst case with illustrative parameters. A smaller lower bound does not prove sufficiency. | Repaired. |
| G29. Non-Gaussian robustness was broader than the proof. | Restrict to the stated location-divergence conditions; separate resampled-noise simulations from distribution-free theorems. | Repaired. |

## Gap inventory: empirical implementation and publication evidence

The registered A1 files and unlock counter are preserved. Candidate changes are delivered separately with live execution disabled. Their presence is not a new registration, and the registered study cannot silently adopt them. Changes to scoring, features, confidence rules or bootstrap dependence need a documented amendment before evaluation data are accessed.

| ID and gap | Repair or required test | Status |
|:--|:--|:--|
| G30. Real market results were absent or future collection was described as underway. | State the actual pending status and the original void outcome. A future window cannot supply current evidence. | Repaired in text; evidence pending. |
| G31. A2 training included a label from the test half. | Purge the final one-step training origin; a sentinel mutation of every test return must leave fitted training data unchanged. | Candidate implemented; regression test passes and reproduces the original defect. |
| G32. A1 training used eight-step labels crossing the boundary. | Purge all eight forward-label origins; mutate future class observations and compare fit inputs. | Candidate implemented; regression test passes. |
| G33. Final-day observations were counted but omitted from scoring. | Aggregate every eligible observation into UTC day buckets, including the partial final day; verify 30 days and the exact row count. | Candidate implemented and tested. |
| G34. The power gate calibrated marginal rather than incremental signal. | Calibrate from inner-training baseline residual variance, with an infeasibility check; distinguish estimated calibration from a known population effect. Validate achieved power across specified DGPs. | Algebra and isolation repaired; broad calibration gate remains open. |
| G35. Independent-day resampling ignored persistence across days. | Candidate uses circular blocks of three days and reports one- and five-day sensitivity, with common resampled days across symbols. Establish size and coverage under slow common factors. | Implemented; inferential adequacy requires simulation. |
| G36. The relevance verdict did not establish exceeding the economic margin. | Candidate requires the one-sided lower confidence limit to exceed the margin. Report inconclusive otherwise. Establish size at the boundary. | Implemented; this changes the registered rule. |
| G37. Feature definitions differed from the specification. | Candidate uses quantity open interest and a trailing 48-bar arithmetic average. State five-minute half-lives in bar units. Freeze an exact data dictionary in an amendment. | Candidate implemented; final protocol interpretation must be documented. |
| G38. The five-minute secondary output was missing. | Candidate builds five-minute panels from the same raw files and adds the output; secondary analysis uses the primary retained universe. | Implemented; synthetic pipeline exercises it when the gate passes. |
| G39. Timestamp precision caused a parser failure. | Use `searchsorted(end, side="left") - 1` for strict-before selection, avoiding a one-nanosecond subtraction incompatible with microsecond indices. | Repaired; boundary and five-minute tests pass. |
| G40. Synthetic infrastructure passes were interpreted too strongly. | Test both layouts, checksums, missing files and look-ahead, then separately evaluate statistical size, power and coverage. | Infrastructure checked; real-world validity not inferred. |
| G41. A forecast pass was called structural invisibility. | Restrict the reading to specified learners, observed proxies, horizon and margin; avoid an exhaustive causal explanation. | Repaired in manuscript and candidate wording. |
| G42. Registered unfavorable or void results could disappear from the narrative. | Preserve the existing registered readouts in the supplement, the void P1F result, and the audit trail. The revised main text points to them. | Preserved; no outcome reclassified here. |
| G43. Counts of Lean declarations implied complete proof coverage. | Rebuild and scan axioms, then map the additional lemmas to exact proof steps. Keep probability, asymptotic and semantic-coverage obligations explicit. | Build and axiom checks pass; full semantic coverage remains open. |
| G44. Author approval and independent verification were asserted too broadly. | Label this revision for author review and avoid certifying human verification on the authors' behalf. | Repaired; human review pending. |
| G45. Nearby identity-disclosure literature was missing. | Add the 2012 investor-identity and 2026 delayed-disclosure comparisons; narrow the novelty statement. | Repaired; exhaustive priority certification is not claimed. |
| G46. Main/supplement dates, companion cross-references and delivery traceability were inconsistent. | Synchronize revision dates, build companion references, inspect rendered pages and include source hashes, logs and source files. | Addressed by the delivery workflow. |
| G47. Equal-kernel equivalence was interpreted as zero value of anonymous flow. | State preservation of the equivalence class, not zero incremental information. A dealer that always quotes zero hides kernels in prices while first aggregate flow under a constant public signal reveals the first kernel tap. | Repaired with an explicit counterexample and a sharper identification contract. |
| G48. A slow validation assertion read an archived extended-search file. | Separately regenerate the full extended search and evaluate its actual output; distinguish fresh searches from a check of an inherited artifact. | Fresh reproduction is recorded in the verification results below. |
| G49. Fitted-learner equivalence was being interpreted as oracle information irrelevance. | Prove $\Delta_{\rm fit}=\Delta_*+e_B-e_A$ using conditional-expectation orthogonality. Oracle irrelevance additionally needs an upper bound on $e_A$. Preserve the failed population-boundary diagnostic and calibrate the declared estimand. | Interpretation repaired by a new proposition; oracle-valid empirical inference remains open. |

## Reconciliation with the incoming SSRN version

The user supplied the ceiling note dated 15 November, found at `ceiling_suite/papers/paper1/review/CEILING_AND_SSRN_VERSION_20261115.md`, and the associated source at commit `63e28aaa`. Its judgments are another AI-assisted reading, not independent referee approval. I retained its substantive improvements while correcting their scope. The earlier isolated revision was rated 81; incorporating the supported theory additions increases this merged revision to 83 on the same rubric. The incoming note's 76–78 judgment uses a different unstated rubric and is not a calibrated competing measurement.

1. **Detection and forecast mismatch:** incorporated the exact directional Gaussian KL identity and the necessary testing threshold. These require common observed initialization, a common predictable probe policy, common known noise variance and finite mean-gap energy. The identity concerns two specified conditional mean functions. It does not prove that every aggregate kernel is cheaply estimated or that a failed test implies a small KL divergence.
2. **Linear-memory recovery:** incorporated the full inverse proof on a compact class of separated normalized types and positive weights. This closes the conditional inverse gap for that restricted shrinking-cluster class. The observation model is noisy deterministic impulse responses, with known design, centre, spread and number of types. It does not itself settle pooling, passive stochastic-price attainability, nonlinear rules, or a numerically certified global optimizer. The additional block-Hankel proposition below settles generic pooled uniqueness under an explicit certificate.
3. **Uniform Bayesian forecast bound:** incorporated a finite-horizon expected cumulative log-loss bound, with zero initialization and known Gaussian innovation variance. This is a substantive uniform result. It is not a uniform terminal squared-error theorem. An explicit large-initial-state example shows why its initialization condition matters.

The additional literature context is the established prequential approach and online Bayesian prediction: [Dawid (1984)](https://doi.org/10.2307/2981683) and [Vovk (2001)](https://doi.org/10.1111/j.1751-5823.2001.tb00457.x). Their role is credited; the Gaussian integral and market-specific tail bound are derived in the supplement.

| ID and incoming gap | Implemented repair | Status |
|:--|:--|:--|
| G50. A simulated Gaussian error curve was treated as universal for random predictable gaps. | Give the two-step normal experiment with exact error $\arctan(1/\alpha)/\pi$, differing from $\Phi(-\alpha)$ despite the KL identity. Retain the incoming curve only as a numerical reference. | Repaired with proof and four regression cases. |
| G51. The Bayesian log-score was described as being “within” a bound, suggesting an absolute difference. | State the one-sided regret inequality and positive prior mass on the truth; test a path with negative regret whose absolute value exceeds the bound. | Repaired. |
| G52. Uniform log-loss and pointwise MSE were conflated. | Give separate theorems with explicit losses, priors, known variance, fixed margins, and initialization; keep the uniform MSE extension open. | Repaired in statement and interpretation. |
| G53. The rank theorem omitted key class and experiment qualifications. | Specify known design and number of types, positive weight and normalized separation bounds, sufficiently small spread, a nonempty compact class and deterministic-response measurement noise. State the fixed accuracy needed for the lower bound. | Repaired; proof incorporated. |
| G54. A necessary detectability condition was used like an equivalence. | Preserve the exact KL identity but state the error threshold only as necessary. Do not infer small KL from non-detection alone. | Repaired. |
| G55. Optimizer performance used truth initialization. | Label the incoming recovery simulation as a local conditioning check. The minimum-distance theorem is about an exact global minimizer; optimization tolerance must be controlled. | Scoped; certified practical global optimization remains open. |
| G56. New forecast examples confused memory-update rates with persistence rates. | Record that the incoming script inputs are update rates $\eta$, with persistence $r=1-\eta$; keep these examples separate from the earlier stationary fixed-order simulation. | Clarified in the evidence record. |
| G57. Shared work was absent from the active branch and a case-colliding PDF interrupted the rebase. | Preserve incoming source and both PDF blobs, finish the rebase, integrate a reproducible canonical build, and verify a single consolidated `main`. | Consolidation is recorded in the delivery receipt. |

The review also produced a block-Hankel certificate for pooled moments. Its proof recovers the monic annihilating polynomial from a full-column-rank linear system, then the common nodes and each market's weights. A partition-of-nodes construction proves generic full rank at the claimed pooling order; compact rank-certified classes have a Lipschitz inverse. This is standard multi-channel Prony reasoning applied explicitly to the paper's model, not a claim to invent that method. Thirty-five exact rational reconstruction cases and a positive-weight rank-deficient control passed.

| ID and additional gap | Implemented repair | Status |
|:--|:--|:--|
| G58. Generic global pooling uniqueness was left to multistart searches. | Give the block-Hankel certificate, prove uniqueness and genericity, and prove a compact-class inverse bound. Keep exceptional rank-deficient cases separate. | Repaired under the explicit certificate; full statistical mechanization remains open. |

A further current-literature check identified [Huang and Liu's 10 November 2026 preprint](https://arxiv.org/abs/2611.13633) on single- and multi-snapshot ESPRIT stability. The manuscript adds a narrow scope comparison; this review does not independently validate every bound in that new preprint. Together with [Li et al.](https://arxiv.org/abs/2105.14304), it reinforces the need to locate novelty in the financial observation and intervention problem.

| ID and reproducibility gap | Implemented repair | Status |
|:--|:--|:--|
| G59. The registered A1 notebook fails current notebook-schema validation because its Markdown cell contains an `outputs` field. | Preserve the registered bytes and hash. Deliver a separately named schema-corrected review copy with an unconditional guard in every code cell. Validate the repaired schema and verify all guards. Exclude only the immutable invalid artifact from Ruff; keep hash and defect regression checks. | Format repair implemented in an unregistered copy; execution intentionally blocked. A protocol amendment remains required. |

The two historical P1T investigation scripts are pasted cells that require the preceding notebook's variables. Their narrow undefined-name lint exceptions now reflect that execution context. The current source and candidate files otherwise pass the repository's configured Ruff checks. The complete registered study was not executed.

## Tests required to reach the higher ceiling

These are acceptance conditions, not a calendar plan. Favorable outcomes must not be required for completion: a negative result can produce a publishable boundary or rejection if it is reported honestly.

1. **Uniform squared-error forecast bound.** The merged version already proves a uniform cumulative log-loss result. For a stronger MSE result, Fix a class with $S\le1-\gamma$, $r_i\le1-\eta$, bounded total weight and a noise specification. Prove a finite-sample or uniform expected-risk bound for a precisely defined feasible predictor without a hidden inverse-spacing constant. Test $\Delta\to0$ and $S\to1$ separately. Passing means the proof supplies constants and covers the estimator actually used; a fitted slope is insufficient.

2. **Attainability beyond the proved response experiment.** The merged version proves recovery for separated linear-memory clusters from noisy deterministic responses. To extend it to passive prices or nonlinear rules, prove injectivity and a quantitative inverse modulus on a declared compact class, then show the histories can be generated with the declared probe budget and observed through the declared noise law. Include coincident types, vanishing weights and infeasible histories as failure cases. Passing requires a theorem under the same observation contract as the lower bound.

3. **Pooling beyond the certificate.** The merged paper supplies a global inverse theorem for compact classes satisfying the block-Hankel certificate and proves generic full rank. Characterize the remaining rank-deficient classes, or give explicit non-identification examples, and develop a justified numerical rank rule under noisy moments. Numerical multistart searches can reveal counterexamples but cannot certify their absence. Include rank loss, different rates across markets and cross-impact in stress tests.

4. **Intervention validation.** Obtain verified class-level executed flows and an externally documented intervention affecting a specified class. Fix the population fit and predicted responses before the event. Compare realized responses against the aggregate-only and class-aware predictions, with a justified counterfactual and confounding checks. Passing requires an identified intervention effect or a precisely documented failure of the theory's assumptions; a return-prediction gain alone is insufficient.

5. **Economic value of reports.** Specify the supervisor's objective, feasible actions, implementation costs and error costs; estimate or bound the loss parameters. Evaluate paying for tags against the best aggregate-only action, allowing correlated reporting errors and strategic response. Passing means a decision-relevant net value under stated uncertainty, rather than a declaration that all tags are useful.

6. **Empirical calibration grid.** Before using held-out market data, evaluate candidate size and equivalence coverage at gains of zero, half the margin, exactly the margin and twice the margin. Cross this with common market factors, serial persistence, class-report measurement error, missing days, changing volatility and heavy-tailed innovations. Count Monte Carlo uncertainty. Passing requires a frozen size/coverage/power criterion and all scenarios reported, including failures. The two original synthetic worlds do not exhaust this grid.

7. **Measurement bridge.** Compare pricing-error observations, traded prices with an observed fundamental proxy, and traded prices with hidden fundamentals. Measure whether class features help through state filtering, private information or heterogeneous exogenous flow. Passing requires the empirical target and information set to match the theorem being tested, or a clearly different estimand.

8. **Independent proof review.** Give another qualified reader the theorem-to-proof map, new derivations, formal statements and test logs. Resolve every central objection about quantifiers, initialization, observation laws, estimator definitions and economic counterfactuals. Passing is documented review of those claims, not a declaration count or an AI-generated approval statement.

## Verification record

{{VALIDATION}}

The 59 new tests include counterexamples and failure-path checks. They are not empirical confirmations. The additional Lean file contains ten deterministic lemmas: polynomial cancellation, positive-mass remainder control, their flow-gap consequence, approximate minimum-distance estimation, initialization residuals, binary decision-loss arithmetic, additional-tag precision, the limiting intervention margin, forecast mismatch algebra, and inverse-remainder absorption. The statistical ingredients listed in the supplement remain on paper or cited.

The repository test suite also exercises projects beyond this paper. Its passing count is reported for traceability and is not treated as evidence for Paper 1's economic claims. Its generated changes to unrelated benchmark outputs were retained in a diagnostic patch and restored to their initial tracked state. Concurrent manuscript edits in the main checkout were preserved; the delivered revision is built from the isolated snapshot identified below.

## Provenance and reproduction

The supplied main and supplement match repository revision `9b7043f2a0c469b806fe2e30812ef2005ffc1f89`. The local checkout's starting commit was `3e5eac94`; the revision uses an isolated copy of the newer SSRN sources. It does not replace the author's original PDFs.

Original SHA-256 values:

- Main: `144aad4395ee35a48952f96bb9f40059cb86208a70b9dad46adc3114b9f3946c`
- Supplement: `2fe8bcb718ff366221945c27ae4ea7d3379634ed84641e7317d9953f2b6b8bca`

The package includes the revised main text, supplement, unchanged companion source, build script, proof amendments, candidate empirical executor, tests, result JSON files, logs, and a source manifest. `README.md` provides exact reproduction commands. Registered study files and counters are included for comparison with their recorded hashes. No live study-window data are read by the new checks.

**What is complete:** the concrete manuscript revision and the local verification recorded here. **What remains conditional:** the stronger research ceiling, real-data findings, extensions beyond the stated rank and initialization conditions, full mechanization, independent review and author approval. Calling those complete would make the paper less credible.
