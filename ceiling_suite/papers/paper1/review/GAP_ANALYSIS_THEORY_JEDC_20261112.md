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

## Gaps that remain (disclosed in the paper, not fixable by writing)

| Gap | Risk | Status |
|---|---|---|
| Linear feedback and exponential memory | Medium | Stated in Scope; the two-layer theorem covers saturating limits. Nonlinear switching (as in Brock-Hommes) is outside the theorems. |
| Near-instability bound is per observation, not a finite-sample bound uniform in the margin | Low | Stated next to the proposition. |
| Stress identification assumes exactly observed responses | Medium | Stated in the theorem. A noisy version is open. |
| One hiding group, no equilibrium among several | Low | Stated after the proposition. |
| No empirical confirmation | Low at JEDC | Tests in the supplement with registered readouts; the Binance replication reports after February 2027. |
| Lean receipt dated 9 November | Low | Needs `python3 verify_formalization.py` on the author's machine. |
| Constants in the cost bounds grow fast with K | Low | Stated in the supplement. |

## Net effect

Gaps 1, 2 and 6 were the likeliest reasons for a JEDC rejection. With them closed, the estimate moves from about
75-78 to about 78-80, with a chance of eventual acceptance at JEDC of roughly 40%. These numbers are judgement,
not data.
