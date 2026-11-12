# Paper 1, theory version for JEDC: referee-style gap analysis (12 November 2026)

Done by an AI system reading as a JEDC referee would. Not independent review.

## Gaps closed in this pass

| # | Likely referee objection | Risk | What was done |
|---|---|---|---|
| 1 | "The sufficiency theorem is a tautology: same kernel, same flow, same prices." | High | The paper now states what the two theorems give together: the kernel is a *minimal* sufficient statistic (it fixes everything prices show, and prices fix it). The proof is called short; the claim rests on the object and on minimality. |
| 2 | "The calibration is cherry-picked: memory rate 0.5 means a half-life of one day." | High | Table 1 now covers centre rates 0.5, 0.8 and 0.9 at a fixed feedback share, with half-lives. The headline uses half-lives of 5 to 9 days: more than 4,000 years of daily prices. The table also shows the honest flip side: half-lives differing threefold can be told apart in about a century. |
| 3 | "The five-minute column mixes time scales." | Medium | Column removed; the note explains that rates are per period and how to convert. |
| 4 | "The supervisor is assumed to know a and kappa." | Medium | Sentence added: knowing them only helps the observer, so the lower bounds hold a fortiori when they must be estimated. |
| 5 | "Why only prices? Supervisors also see volume and order flow." | Medium | Sentence added: aggregate untagged flow is itself a function of the kernel, so it adds nothing about composition; only class tags do. |
| 6 | "Ignores the JEDC literature estimating heterogeneous-agent models." | High at JEDC | Positioned against Brock and Hommes (1998), Hommes (2006), Boswijk, Hommes and Manzan (2007), Franke and Westerhoff (2012), Lux and Zwinkels (2018); references checked. |
| 7 | "Claims rest on an unpublished 'full working paper'." | Medium | Every such pointer is now a citation, Niroula, Niroula and Khatiwada (2026a), with the public repository. |
| 8 | "Version clutter: core version, note, 'new to this version'." | Low | Removed from the theory build. |

## Second pass (12 November 2026): the remaining gaps

| Gap | Before | Now |
|---|---|---|
| Linear feedback only | Sufficiency stated for linear and saturating flows | Sufficiency now stated for **any** population whose aggregate flow is a causal function of public signals, including strategy switching after past profits (the induction is already machine-checked in this generality, `p1_flow_market_invariance`). Identification and cost results still need linear flows and exponential memory; that remains the main scope limit. |
| Near-instability bound per observation only | Disclosed | Exact finite-sample information computed (`finite_sample_check.py`): within 97.8-99.8% of n times the rate, for margins down to 1e-3 and n up to 4,000. Numerical evidence; the uniform finite-sample proof is still open. |
| Stress identification needs exact observations | Disclosed | **New Proposition (noisy stress identification), with proof:** a minimum-distance estimator recovers the signed capacity measure consistently under Gaussian observation noise. No rate. |
| One hiding group | Disclosed | Bound shown to hold group by group in any equilibrium among several groups; what determines each group's alpha is not modelled. |
| Lean receipt dated 9 November | Needed the author's Mac | Full `lake build` running in this session (Mathlib modules compiled from source). |
| No empirical confirmation | | Unchanged by design: tests in the supplement; Binance replication after February 2027. |
| Constants grow fast with K | | Unchanged; stated. |

## Net effect

Gaps 1, 2 and 6 were the likeliest reasons for a JEDC rejection. With them and the second-pass gaps closed, the
estimate is about 79-81, with a chance of eventual acceptance at JEDC of roughly 40-45%. The main remaining limit
is that identification and cost need linear flows. These numbers are judgement, not data.
