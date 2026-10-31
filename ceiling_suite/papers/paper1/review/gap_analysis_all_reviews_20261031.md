# Paper 1: the two-part SSRN build checked against every review (31 October 2026)

Reviews checked: two independent referee reports (A: 4/10, B: 5.5/10), the Gemini review, five professor-role
reviews of the 124-page build (round 1) and five of the 115-page build (round 2). All are AI-generated; none is
independent human review. Status refers to the current build: `paper1_ssrn.pdf` = `paper1_main.pdf` (main paper)
+ `paper1_online_supplement.pdf`.

## 1. Points raised by more than one review

| Point | Raised by | Status in the current build |
|---|---|---|
| No decision in which knowing the groups changes the action | A, B, R1 P1/P2/P5, R2 P2 | **Closed in the model**: Proposition `prop:target` (market-wide limit needs only S; whether halting one group suffices needs its own intensity and inherits the (Delta eta)^-(4K-2) cost; tagged data decide with a bounded number of experiments), Table `tab:target`, Section 6.2. Stated as stylised; a loss function estimated from real interventions remains open |
| CAT budget comparison misleading | A, B, R1 P2/P4/P5, R2 P2/P4 | **Closed**: not in abstract, introduction, results map or conclusion; break-even columns removed; dollar illustration moved to the supplement with a disclaimer |
| Too long, stitched together | A, B, R1 all, R2 P1-P5 | **Closed**: 54-page main paper; supplement holds proofs, extended literature, dollar illustration, spectral blind spot, feedback measurement |
| "Registered" read as external preregistration | R1 P3/P5, R2 P3/P5 | **Closed**: "pre-specified" throughout, defined as the authors' declaration |
| Failures buried | R1 P3/P5 | **Closed**: pass/fail table on page 5; abstract states the failures |
| Known fundamental value; no dealer equilibrium | A, R1 P2, R2 P2 | **Closed as limits**: stated in "What we do not claim", the model section and the assumptions; known p* is an a fortiori aid for the lower bounds; endogenous impact (Kyle) now discussed (new this round) |
| Novelty of the exponent | A, B, R1 P1, R2 P1 | **Closed**: credited in the main-text literature paragraph (Heinrich-Kahn, Wu-Yang, Katz et al., Shahram-Milanfar, Rebafka-Roueff, Castelli-Cover) |
| Missing finance literature | A, B, R2 P2 | **Closed**: Leach-Madhavan, Andrews-Cheng, Barth-Kahn, Barberis et al., Cespa-Vives, Biais-Foucault-Moinas, Crouzet et al. (all verified) |
| CFTC returns from spot/index/yield, not CME futures | R2 P3/P4/P5 | **Open, needs approval**: draft script `ceiling_suite/p11/robustness_cme_futures_DRAFT.py`; the note now states exactly which series are futures (crude, gas) and which are not |
| Positions are not flows; near unit root | R1 P3, R2 P3 | **Closed as limits**: stated wherever the result is claimed; inventory-root and T^-1 scaling notes |
| Independent proof check | R1 P1/P5, R2 P1/P5 | **Open, needs people**: priority list in the publication guide |
| Acknowledgments, funding | R1 P5, R2 P5 | **Open, needs author facts** |

## 2. Theory points

| Point | Source | Status |
|---|---|---|
| Rich-class qualifier for the minimax rate; singleton counterexample | B, R1 P1 | Closed |
| Prony global inverse; finite-sample event; h_0 known; log(4K/beta) | R1 P1, R2 P1 | Closed |
| Thm 5.4 stability condition and tap horizon | R2 P1 | Closed |
| Loss targets: fixed-accuracy weights vs W1 at Delta eta | R1 P1 | Closed (paragraph after Thm 5.4) |
| Tagging precision "independent of spacing" | R1 P1 | Closed ("no singularity as rates collide") |
| Disclosure-value threshold c_0 | R1 P1 | Closed |
| Martingale CLT for the IV score | B, R2 P1 | Closed |
| eta = 1 anchor; adaptive alpha/beta; strict Lambda_N | B | Closed |
| Passive bound with observation noise | R2 P1 (question) | **Closed this round**: data-processing remark (noise can only lower the divergence) |
| Endogenous impact makes probing costlier | R2 P2 (question) | **Closed this round** as a stated expectation, not a result |
| Gauss vs Gauss-Radau largest weights differ for every K | prop:target | Open: closed form for K = 2, 3, numerical for K <= 8, stated in the paper |
| Lean coverage of the rate theorems | R1 P1 | Open: arithmetic cores only; the paper says the proofs are not formally verified |

## 3. Writing points

| Point | Source | Status |
|---|---|---|
| Abstract overloaded (>270 words) | R1 P5, R2 P5 | **Closed this round**: about 220 words, failures kept |
| Flagged sentences (contribution list, assumptions, Lemma 4.5 constant, Thm 5.2(ii), probe-design sentence, state-tracking result) | R2 P5 | **Closed this round** |
| File names and bug log in the text | R2 P5 | Closed |
| Binance section reads as a chronology | R2 P3/P5 | Partly closed: the fair horizon-matched test is flagged first and summarised in the pass/fail table; the follow-ups remain in time order |
| Executive summary for faculty | R2 P5 | The introduction now serves this; a separate 10-15 page note is optional |

## 4. Still author decisions

Byline (Prashant's written agreement); AI-use statement; funding, conflicts, acknowledgments; companion-paper author
list; CFTC futures re-run approval; human proof check; repository name and release tag; the two unmerged thesis
branches; QF preprint policy.

## 5. Honest score estimate

Reviewer "after fixes" estimates were P1 8.5, P2 7.5, P3 8.5, P4 9.0, P5 9.2. Every fix they listed that does not
need an author decision is now in. A realistic next-round range is 8-9.5 per role; the two items most likely to keep
the finance theorist (P2) and the econometrician (P3) below 9 are the absence of an estimated supervisory loss and
the pending CME-futures re-run. Only a new review round can measure the score.
