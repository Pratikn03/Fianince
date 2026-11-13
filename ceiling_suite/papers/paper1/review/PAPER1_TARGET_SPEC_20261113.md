# Paper 1 at the top level: the results it would need and what it would look like (13 November 2026)

Written by an AI system for the authors; judgement, not independent review.

**How to read this.** This is a target, not a paper. Each result is marked **have**, **partial** or **target**.
A target is something to test or try to prove. It is not something to "find": a registered test is run once and
reported as it comes out, and a conjecture that turns out false is dropped or reported as false. If a target
fails, the paper changes; the result does not. Even with every target met, a rating above 90 is possible, not
certain.

## 1. The paper in one page

**Working title.** *What Prices Cannot Reveal: An Identification Law for Algorithmic Markets*

**Claim.** In a market where traders react to prices, prices reveal one object about the trader population and
nothing finer. The data needed to learn anything finer grow as a fixed power of how similar the traders are.
The law holds for any smooth family of trading rules, real accounts obey it, and a small amount of disclosure
removes it.

**What a reader should be able to repeat afterwards.**
1. Prices reveal the aggregate response and nothing else (a theorem).
2. Telling K similar groups apart costs data of order (spacing)^-(4K-2), whatever the rules (a theorem).
3. On a venue where every account is visible, prices fail exactly as the law says and the accounts' own records
   do not (a measured fact).
4. Calm prices say nothing about how close traders are to liquidation; stress does (a theorem and a measured fact).
5. Tagging all but one class of traders removes the cost, and the last tag is worth nothing (a theorem and a
   measured fact).

**Shape when done.** Main text of at most 40 pages: five theorems, six registered empirical results, three
figures, one table of money values. Supplement of at most 60 pages. Every theorem machine-checked or its
unchecked steps listed. Every test registered before its data, run once, failures reported.

## 2. Theory results

| # | Result | Status | What has to be done |
|---|---|---|---|
| T1 | **Sufficiency.** Populations with the same aggregate flow map give the same prices, profits and equilibria, for any dealer and insider rules | Have, machine-checked | Authors' proof check |
| T2 | **The law, exponential memory.** Cost of composition is of order (spacing)^-(4K-2), matched above and below; passive data cost the same; nearness to instability does not help | Have, machine-checked in large part | Authors' proof check |
| T3 | **The law is universal.** For any smooth one-parameter family of trading rules whose derivatives in the type parameter are linearly independent up to order 2K-1, the cost of telling K types apart is of the same order (spacing)^-(4K-2). For types with several parameters, the cost is (spacing)^-2m, where m is the first order at which two matched populations' flow maps differ. Exponential memory, saturation with equal leverage (m = 2K-1) and saturation with distinct leverage (m = 0) become special cases | **Target.** The pieces exist separately (`thm:kcohort`, `prop:nlcost`, `thm:anypop`) | Prove the general statement: aggregate flow is linear in the type measure for any rules that depend on public history, so composition is a linear inverse problem and the two-point and Prony arguments extend. Check novelty against Heinrich and Kahn (2018) and the strong-identifiability literature before claiming anything beyond "new in this setting" |
| T4 | **Calm hides, stress reveals.** With position limits, calm prices carry no information about distance to limits; probes or shocks that reach the limits identify it, at the parametric rate | Have (`thm:satsuff`, `thm:stress`, `thm:satident`, rates in the companion note) | Authors' proof check; restate with liquidation, to match the data in E6 |
| T5 | **Disclosure.** With m of K classes tagged, the cost is that of the K-m untagged classes; the last tag is worth nothing; pooling D markets lowers the exponent to 2(K-1+ceil(K/D)) | Have | Authors' proof check |
| T6 | **Equilibrium with hiding.** Traders choose their rules knowing how they are watched; the supervisor chooses what to disclose and whom to target. Without tags, more data push traders' rules together and detection stays capped; with tags they separate. A welfare comparison of the three regimes (no tags, class tags, full audit trail) | **Partial**: a two-group hiding game and a detection cap are proved (`prop:hiding`, `prop:hidegame`) | Extend to K groups and a supervisor who chooses the disclosure regime; state existence and the comparison. This is real research and may not come out cleanly |

T3 is the result that would lift the theory above "known rates applied to a market". T6 is what an economics
audience would ask for. Either may fail.

## 3. Empirical results (all on account-level data; all to be registered before their data are read)

Venue: Hyperliquid, where every trade carries the wallet addresses, and positions and liquidations are public.
The registered test H1 opens on 10 December 2026 and its days are then spent. Every test below needs its own
specification, simulation check and approval, on days H1 did not use. A schema probe on already-spent days must
first confirm that positions, leverage and liquidation prices can be read per account.

| # | Result the paper would report | Design in one line | Pass criterion (to be fixed in the specification) | My rough odds |
|---|---|---|---|---|
| E1 | **Accounts differ.** Large accounts have distinct, stable memories that their own records reveal | H1, primary 1 | As registered | Fair |
| E2 | **Prices do not show it.** Prices and anonymous flow fail to separate those memories | H1, primary 2 | As registered | Good |
| E3 | **The exponent.** Across markets, the price-only error in composition grows with the inverse spacing of the accounts' measured memories at the predicted power | Regress log error on log spacing across markets and windows; spacing measured from account records | Fitted slope within a pre-set band around the prediction for the measured K | Uncertain: needs stable memories and enough spread in spacing |
| E4 | **Sufficiency in data.** When the mix of accounts changes but the aggregate response does not, price dynamics do not change; when the aggregate response changes, they do | Compare pairs of windows matched on the estimated kernel but different in account composition, and the reverse | Equivalence test passes for matched pairs; difference detected for unmatched pairs | Uncertain: matched pairs may be rare |
| E5 | **Tags work, and the last tag is worth nothing.** Coarsen accounts into classes; with class-tagged flow the error is flat in spacing; with all but one class tagged it equals the fully tagged error | Recompute E3 with tagged class flow at several levels of tagging | Slope near zero with tags; no gain from the last tag | Good, if E3 works |
| E6 | **Calm hides, stress reveals.** In calm windows, prices do not predict the distribution of accounts' distance to liquidation; after large moves they do | Predict the liquidation-distance distribution (known on chain) from prices, calm against stressed windows | No predictive gain in calm; a gain under stress | Fair |
| E7 | **Pooling.** For accounts active in several markets in different proportions, pooled price records recover composition at the lower predicted exponent | E3 with D markets pooled | Slope moves toward the pooled prediction | Long shot |
| E8 | **A second venue.** The main results repeat on another venue with account-level data | Replicate E2 and E3 | Same criteria | Unknown: depends on data access |

A paper with E1–E3 and E5–E6 passing would have direct evidence for every main theorem. A paper in which E3
fails still reports it, and then rests on E1, E2 and E6.

## 4. Money

| # | Result | Status | Work |
|---|---|---|---|
| M1 | Years of data needed to learn composition from prices, at the measured memories and noise of real markets | Partial: computed at illustrative parameters (more than 4,000 years for half-lives of 5 to 9 days) | Recompute with the estimates from E1 |
| M2 | Dollar cost of learning composition by trading, against the published budgets of audit-trail regimes | Partial: in the October preprint with illustrative inputs | Recompute with measured inputs |
| M3 | The value of one tag, in dollars, market by market | Target | From T5 and E5 |

## 5. Layout of the finished paper

1. **Introduction** (4 pages). The question; the five things a reader should repeat; what is known and what is new.
2. **Model and the object prices reveal** (4 pages). T1. Figure 1: two different populations, one price path.
3. **The law** (7 pages). T2, then T3. Figure 2: cost against spacing, theory line with the data points of E3 on it.
4. **The law in real accounts** (9 pages). E1–E4, each with its registered criterion and its outcome.
5. **Limits: calm hides, stress reveals** (5 pages). T4 and E6. Figure 3: prediction of liquidation distance, calm against stress.
6. **What disclosure buys** (6 pages). T5, E5, M1–M3. Table: the value of a tag.
7. **Hiding** (3 pages). T6, as far as it is proved.
8. **Scope** (2 pages). Mechanical impact; accounts are not firms; one venue; every failed test.

## 6. Order of work

1. Authors check the proofs of T1, T2, T4, T5.
2. Submit the current paper to JEDC as it is; this plan does not depend on waiting.
3. Schema probe on spent Hyperliquid days: can positions, leverage and liquidation prices be read per account?
4. 10 December: run H1 once (E1, E2).
5. Attempt T3 on paper; check novelty; formalize if it holds.
6. Write, simulate and approve the specification for E3 and E5 together, then E6, then E4. Push each before its data. Run each once.
7. Recompute M1–M3 from the measured values.
8. Attempt T6.
9. Write the paper around what held, with every failure reported.

## 7. Rules that keep the result worth having

- No test is run before its specification is public. No test is rerun or redefined after it fails.
- No theorem is stated before it is proved; nothing is called machine-checked unless the Lean statement is the claim.
- No number enters the paper without a script that produces it.
- AI tools may draft and check; they may not be the source of a result. A draft from any tool that states a result
  no test or proof produced is discarded.
