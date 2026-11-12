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
| Linear feedback only | Sufficiency stated for linear and saturating flows | **New Theorem (Any population):** for any causal aggregate flow map, (i) sufficiency, (ii) prices identify exactly the flow map, and a group-level quantity is identified iff it is a function of it (machine-checked for an arbitrary map, `Paper1GeneralIdentification.lean`, standard axioms only), (iii) the cost lower bounds hold over every class containing the linear rules, including band-linear classes. Still open: upper bounds (rates) for general nonlinear classes; for some families composition is not identified at all. |
| Near-instability bound per observation only | Disclosed | Exact finite-sample information computed (`finite_sample_check.py`): within 97.8-99.8% of n times the rate, for margins down to 1e-3 and n up to 4,000. Numerical evidence; the uniform finite-sample proof is still open. |
| Stress identification needs exact observations | Disclosed | **New Proposition (noisy stress identification), with proof:** a minimum-distance estimator recovers the signed capacity measure consistently under Gaussian observation noise. No rate. |
| One hiding group | Disclosed | Bound shown to hold group by group in any equilibrium among several groups; what determines each group's alpha is not modelled. |
| Lean receipt dated 9 November | Needed the author's Mac | Full `lake build` running in this session (Mathlib modules compiled from source). |
| No empirical confirmation | | Unchanged by design: tests in the supplement; Binance replication after February 2027. |
| Constants grow fast with K | | Unchanged; stated. |

## Net effect

Gaps 1, 2 and 6 were the likeliest reasons for a JEDC rejection. With them and the second-pass gaps closed, the
estimate is about 80-82, with a chance of eventual acceptance at JEDC of roughly 45%. The main remaining limit
is that attainable rates for general nonlinear rules are open. These numbers are judgement, not data.

## Third pass (12 November 2026): results restored from the full working paper

Inventory: every theorem, proposition, lemma and corollary of the full working paper (SSRN source of
8 November 2026) was compared with the current versions. Other branches were checked: `main` has nothing the
working branch lacks; the older `codex/*` and research branches hold no Paper 1 result missing here (gap audit of
7 November, re-checked by commit dates). Restored verbatim by line range, with their proofs, into the supplement of
all versions:

| Result | Why it matters | Machine check |
|---|---|---|
| General memory: minimax accuracy of exact order 1/log(N) (Theorem `thm:general`, Lemma `lem:altpair`) | Removes "exponential memory only" | Both bounds, larger constants |
| Uniform rate without separation (`thm:uniformw1`) | Merged distribution recoverable at the same order with no separation | Arithmetic step only |
| Spectral blindness (`thm:blind`) | Eigenvalues and volatility cannot replace composition | None |
| Identification in economic primitives; intensity tied to information (`prop:primitives`, `prop:tied`) | What prices hide is the quality of each desk's information | None |
| Cramer-Rao benchmark (`prop:crb`) | Local information | Two-sided Fisher bound for K = 2 |
| Endogenous-pricing invariance; limits of evasion; when an audit trail is chosen (`prop:endogenous_kappa`, `prop:strategic`, `prop:choice`) | Policy and robustness | Arithmetic steps only |
| Finite-window abstention; passive distinction with zero quantity (`thm:abstain`, `prop:passive0`) | Finite-sample surveillance | None |
| Account-level capital (`prop:tri`, `thm:spectral`, `thm:adaptive`, `thm:rh`, `cor:garch`) and the hypothetical dollar illustration | Probing costs money: quantity order delta^-2, capital order delta^-4 | Per the full paper |
| Robustness to nonlinear and adaptive rules (simulations); worked example; real-noise injection (slopes -6.01, -9.81) | Where the linear theory holds; non-Gaussian noise | n/a |

Not restored, by design: the CFTC and Binance class-ratio tests and the empirical feedback measurements (they remain
in the full working paper, cited as Niroula et al. 2026a), and the post-breach fire-sale "theorem" added on `main` on
8 November, which the audit of 10 November found unproved.

Main text: new paragraph "Three extensions" (no separation, general memory, money), two sentences on spectral
blindness and economic primitives, one on the audit-trail decision, one on real noise next to Table 1.
Supplement grows from 58 to 86 pages; main text 16 pages. Estimate after this pass: about 82-84, JEDC chance
roughly 45-50%. Judgement, not data.

## Fourth pass (12 November 2026): a new result, partial disclosure

Theorem `thm:partial` (core Section 5.x; note and theory Theorem "Partial disclosure"): when m of K groups are
tagged, the cost of composition is that of the K' = K - m untagged groups alone, of order (Delta eta)^-(4K'-2) for
K' >= 2 (lower bound with the tagged groups held fixed; upper bound by subtract-then-Prony), and independent of
Delta eta for K' <= 1. Consequences: each tag lowers the exponent by four; the tag that leaves one class untagged is
worth a factor (Delta eta)^-6; the last tag is worth nothing for the weights; what matters is the number of untagged
memory classes, not traders. Numerical check: slopes 10.05, 6.02, 5.96 against 10, 6, 6
(`research_extension/partial_disclosure/`). Lean: algebraic steps (`Paper1PartialDisclosure.lean`, 4 theorems,
standard axioms); probabilistic steps on paper. Added to the theory abstract.

## Fifth pass (12 November 2026): the surprise result, pooling markets

Search: every part of the model was reread for a place where experts' expectation and the model disagree. Rejected
ideas, with reasons: high-frequency data (composition is a drift-like, calendar-time object; known for drifts),
hidden gross feedback (follows from the two-layer theorem), collusion indistinguishability (Vandermonde, too
direct), tag-by-similarity (follows from cluster super-resolution). Kept: pooling markets.

Theorem `thm:pool` (core Section 5.x, note/theory Theorem "Pooling markets"): the same K algorithms (common memory)
in D markets with participation matrix of rank D. Data needed: (Delta eta)^-2(K-1+ceil(K/D)), locally at generic
configurations; one market 4K-2, K or more markets 2K. Lower bound near every generic configuration (counting plus
constant rank); local upper bound under condition (R), verified by exact computation (rank mod a large prime) for K <= 8, all D.
Numerical: 60-digit Jacobian slopes 3,2 / 5,4,3 / 7,5,5,4. Calibration (passive, half-lives 5-9 days): one market
~7,000 years; two markets with shares differing by 50 points ~90 years (hardest pair found), 20 points ~4,000.
Lean: counting steps (`Paper1PoolingMarkets.lean`). Closest literature: multi-snapshot super-resolution (Li, Zhu,
Gao and Liao 2022). Economic reading: an algorithm's memory is the same everywhere it trades, which gives it away;
cross-market surveillance substitutes for tagging; hiding requires identical proportions in every market.

Open: global identification; markets with cross-impact; condition (R) for K > 8 (conjectured).
Estimate: about 86-88. Judgement, not data.
