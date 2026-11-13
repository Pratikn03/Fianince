# Part A, step by step: how to do each part of the Paper 1 plan (13 November 2026)

Written by an AI system for the authors; judgement, not independent review. This is the working guide for the
target in `PAPER1_TARGET_SPEC_20261113.md`. Result codes (T1–T6, E1–E8, M1–M3) are the ones used there.

## Before starting: one decision and four rules

**The decision.** The current paper is ready for JEDC. The new work below would make a much larger paper.
A journal will not take two overlapping papers, so choose one of these before Step 2:

| Option | What happens | Risk |
|---|---|---|
| (a) Submit to JEDC now | The theory is published as it is. The account-level evidence becomes a revision, or a second paper ("the law in real accounts") that cites the first and aims higher | The second paper has less theory of its own |
| (b) Hold the paper | Everything goes into one large paper | If the tests fail, time is lost and the paper is the same as today |

My recommendation is (a).

**The rules.**
1. A test is registered before its data are read, run once, and reported as it comes out.
2. A test is registered only if simulations show it would pass when the theory is true and fail when it is false.
3. Nothing is registered, and no amendment made, without the authors' approval.
4. No number enters the paper without a script that produces it. No theorem is stated before it is proved.

**Who does what.** Pratik: decisions, data runs, theory attempts. Prashant and Sujan: proof checks. The AI
system: drafts, simulations, Lean, builds. It does not approve, register or submit.

---

## Step 1. Check the proofs you already have (T1, T2, T4, T5)

**Goal.** Each of the three authors can defend every step in a referee exchange.

**Order.** `thm:eqinv` and `prop:anylinear` (sufficiency); `thm:merged`; `thm:kcohort` (lower bound);
`prop:esprit` (Prony upper bound); `prop:passive`; `prop:nearcrit`; `thm:partial`; `thm:pool`; `thm:satsuff`,
`thm:stress`, `thm:satident`.

**For each result:**
1. Read only the statement. Write down what it claims in your own words.
2. Close the paper and write the proof yourself from the statement.
3. Compare with the paper's proof line by line. Mark every step you cannot justify.
4. Open the Lean file named in the supplement's verification table. Compare the Lean statement with the prose:
   same hypotheses, same conclusion, same quantifiers.
5. Open the "Check by hand" column of `AUTHOR_PROOF_CHECKLIST_20261112.md` for that result and do what it lists.
6. Record one row: result, checker, outcome (agrees / gap / error), and what was changed.

**If something does not hold.** Fix the proof, or weaken the statement until it is true, and rebuild. Do not
leave a gap with a note.

**Done when.** Every result has a row from at least one author other than the one who wrote the first check,
and the disclosure sentence on the title page is true for the current text.

## Step 2. Send out the current paper

1. Approve or change the cut list in `STAGE_STATUS_20261113.md`. The AI system applies it and rebuilds.
2. Read the main text once from start to finish for sense, not for proofs.
3. Rebuild all versions; confirm no undefined references; rerun the checks and the Lean build; commit the receipts.
4. Write the cover letter: the headline, the scope condition (mechanical impact), what is machine-checked,
   the AI-use statement.
5. Post the working paper (SSRN, arXiv q-fin). Then submit to JEDC, if option (a).

**Done when.** The paper is public and, under option (a), submitted.

## Step 3. Check the data before the test opens

**3a. Collector health (allowed before 10 December).** The opening rule of H1 counts valid days from coverage
only, so this may be done without reading a trade.
1. Run the coverage count in `thesis/evidence/h1_hyperliquid.py` on the merged output.
2. Record, per market: days with at least 95% live connection; days passing the valid-day rule.
3. Count markets with at least 30 valid days. H1 needs 20.

**If fewer than 20 are on course.** Do nothing to the data. The specification already says what happens: the
analysis opens on 31 January 2027 in any case, and is void below 20.

**3b. Schema probe for positions (needed for E6).** The H1 collector records trades only. Distance to
liquidation needs each account's position, leverage and liquidation price.
1. Query the public information endpoint for the state of a few addresses that are not in the H1 universe's
   top accounts. Record which fields exist, how far back they go, and the rate limits.
2. If only the current state is available, E6 needs a new snapshot collector. Write its rule (which accounts,
   how often, which fields), get approval, then start it. E6 can use only days after it starts.
3. Write the findings into `SCHEMA_PROBE.md`.

**Done when.** The coverage table exists and the probe says whether E6 is possible and from which date.

## Step 4. Run H1 once (E1, E2)

1. On or after 10 December 2026, confirm the opening rule: at least 20 evaluable markets.
2. Confirm `thesis/checks/prereg/H1_unlock.json` reads `opens = 0` and the pipeline hashes match the registration.
3. Run `thesis/evidence/H1_Hyperliquid.ipynb` once, start to finish. Save every output file.
4. Commit the outputs and the unlock file in one commit.
5. Write the readout using the two primaries as registered: (1) accounts are tag-identified in at least 75% of
   markets; (2) more markets are tag-identified but not price-identified than the reverse. Holm correction.
6. Report pass or fail in the registered words. Anything found afterwards is labelled post hoc.

**Done when.** The readout is committed. No rerun, whatever it shows.

## Step 5. Try to prove the universal law (T3)

**The statement to aim at.** Let each trader type be a number θ and its rule f_θ map the public history to an
order. A population is a measure ν on types, and aggregate flow is the integral of f_θ against ν, which is
linear in ν whatever the rules. If θ ↦ f_θ is smooth and its derivatives up to order 2K-1 are linearly
independent, then telling K types within Δ apart costs data of order Δ^-(4K-2).

**The work, in order:**
1. **Lower bound.** Take the existing hard pair (two K-point measures with equal moments below order 2K-1),
   scaled to width Δ. Taylor-expand f_θ in θ: the two flows differ by order Δ^(2K-1). Carry the difference
   through the closed loop (the stable-loop bound already used in the companion note), then Le Cam.
   Needed: bounds on the θ-derivatives of f_θ that are uniform over the histories a bounded probe can produce.
2. **Upper bound.** Find 2K functionals of the response whose values are integrals of functions φ_j(θ) against
   ν, with the φ_j forming a system for which K atoms are determined by 2K values. Show the Jacobian is
   nonsingular (a generalized confluent Vandermonde determinant). A minimum-distance estimator then gives the rate.
3. **Several parameters.** State the general form: the cost is Δ^-2m, with m the first order at which two
   matched populations' flow maps differ. Check that it returns `thm:kcohort` (m = 2K-1), equal leverage
   (m = 2K-1) and distinct leverage (m = 0).
4. **Numerical check.** Pick two rule families that are not exponential memory (for example a power-law memory
   indexed by its exponent, and a smoothed fixed-window rule indexed by its window). Fit the slope of the data
   requirement in Δ for K = 2 and 3. Expect -6 and -10.
5. **Novelty check.** Read Heinrich and Kahn (2018), Ho and Nguyen (2016) and Wu and Yang (2020) on strongly
   identifiable mixtures. Write one paragraph saying exactly what is the same (the exponent) and what differs
   (a closed loop, a regression on responses, nonlinear rules, the contact-order form).
6. **Formalize.** Machine-check the moment-matching and Taylor step in general form.

**If it fails.** If the upper bound needs conditions that real rule families do not meet, state the lower bound
alone as the theorem. If the statement is already in the literature, cite it and present the market version as
an application.

**Done when.** A proved statement with its conditions, a numerical check, the novelty paragraph, and an
author's proof check as in Step 1.

## Step 6. Design, register and run the new tests (E3 with E5, then E6, then E4)

**The same seven steps for every test:**
1. **Write the specification:** question; data and days; estimators; each primary hypothesis with a number that
   decides it; corrections for several hypotheses; when the test is void; the exact sentence for each outcome.
2. **Build a simulated market** with known truth, at the size and noise of the real data.
3. **Run the whole pipeline on simulations.** It must pass when the theory holds (power of at least 80%) and
   pass no more than 5% of the time when it does not.
4. **If the simulation check fails,** change the design and repeat, or do not register the test. Record this.
5. **Authors approve.** Push the specification in a commit of its own, with its hash and an unlock counter at zero.
6. **Run once** on days no earlier test has read. Commit outputs with the counter.
7. **Write the readout** in the registered words.

**E3, the exponent.**
- Unit: a market in a window of days after H1's window.
- From account records: estimate each large account's memory; group accounts into K classes (fix K = 2 first);
  the spacing Δ is the gap between class memories.
- From prices alone: estimate composition by the paper's method; the error is its distance from the
  account-based value.
- Primary: in a regression of log error on log Δ across units, with market fixed effects, the slope lies in a
  band around -(2K-1), fixed in the specification from the simulations.
- Known difficulty: Δ is measured with noise, which flattens the slope. The simulation must include this and
  the band must allow for it.

**E5, tags.**
- Recompute the E3 error using class-tagged flow built from the wallet labels.
- Primary 1: the slope in Δ is near zero. Primary 2: with all but one class tagged, the error equals the fully
  tagged error within a tolerance fixed in advance.

**E6, calm and stress** (only if Step 3b says positions can be read).
- Target: the share of open notional within a fixed distance of liquidation, from the snapshots.
- Predictors: prices only.
- Windows: calm and stressed, split by a return threshold fixed in advance.
- Primary 1: in calm windows, prices do not predict the target out of sample (an equivalence test with a
  margin fixed in advance). Primary 2: after stress they do.

**E4, sufficiency.**
- Find pairs of windows in the same market with the same estimated kernel but different account composition,
  and pairs with different kernels.
- Primary 1: price dynamics are equivalent within the first kind of pair. Primary 2: they differ within the second.
- Register only if the simulation shows enough matched pairs will exist.

**E7 and E8** follow the same steps and are optional.

**Done when.** Each registered test has a committed readout.

## Step 7. Redo the money numbers (M1–M3)

1. Replace the illustrative inputs in `research_extension/fragility_reveals/calibration_table.py` with the
   memories, weights and noise measured in H1. Rebuild the table of years of data.
2. Do the same for the dollar comparison with audit-trail budgets (the script behind the October preprint's table).
3. Compute the value of one tag per market from the tagged and untagged data requirements.
4. Each number is written to a result file and read into the paper from it.

## Step 8. Try the equilibrium with hiding (T6)

1. Write the game: K groups choose their rules at a cost of moving away from their preferred rule; a
   supervisor chooses a disclosure regime (none, class tags, full trail) and whom to target; being targeted is
   costly.
2. Start from the two-group result already proved. Extend the detection cap to K groups.
3. Show what tags change: an account's tag does not move when its rule does.
4. Compare welfare across the three regimes, with the cost of disclosure as a parameter.
5. Check each step numerically before stating it.

**If it does not come out cleanly.** Keep the two-group result and the cap, and say the general case is open.

## Step 9. Write the paper around what held

1. Fill the layout in the target specification, section by section, from the results that exist.
2. Every failed test gets its own sentence in the section where its result would have gone.
3. Run Step 1 on every new proof.
4. Trace every number to its script. Rebuild. Rerun all checks and the Lean build.
5. Write answers to the ten hardest referee questions.
6. Choose the journal from the results:

| What held | Where it can reasonably go |
|---|---|
| H1 fails | The JEDC paper stands as it is |
| H1 passes, little else | A revision of the JEDC paper, or a short empirical companion |
| H1, E3, E5 and E6 pass | A separate paper on the law in real accounts, at a leading finance or economics field journal |
| Those, and T3 proved and new | An attempt at a top general journal becomes reasonable. It is still an attempt |

## What can start now

- Step 1 (authors).
- Step 2, item 1: the cut list (authors decide, the AI system applies).
- Step 3b: the schema probe (the AI system can draft the probe; it reads no H1 data).
- Step 5: the attempt at T3 (the AI system can draft the proof and the numerical check).
