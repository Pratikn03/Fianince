# Paper 1: full plan of work (13 November 2026)

Written by an AI system for the authors; judgement, not independent review. The plan is ordered: each stage depends
on the one before it. No new theorems are added except where a stage says so.

## Stage 0. Freeze and clean the base

0.1 Freeze the results. No new propositions unless a later stage or a referee calls for one.
0.2 Finish the full Lean build and regenerate `formal_verification_receipt.json`, so the repository count matches
    the paper (1,235 declarations, 144 modules). The current receipt is stale (1,306, from another tool's run).
0.3 Delete the two merged branches in the GitHub interface, so `main` is the only branch.
0.4 Stop any other tool from pushing to `main`.
0.5 Tag the current state as the "everything" version, so nothing is lost when the paper is cut.

## Stage 1. Choose the flagship

1.1 Decide the single headline. Candidate: an impossibility result with numbers. "From prices, a supervisor needs
    X years of data to tell two crowded populations apart; one stress probe or one disclosure does it at once."
1.2 Calibrate X. Take impact, memory rates, noise and group counts from published estimates for one real market,
    and compute the data requirement from the existing bounds (constants included, using the exact moment gap).
1.3 Write the headline as one theorem with three parts: (a) prices reveal the kernel only; (b) the cost of
    composition, upper and lower; (c) calm hides, stress reveals. Everything else becomes a corollary or an extension.
1.4 Test the headline: can each author state it in two sentences without notes? If not, rewrite it.

## Stage 2. Defend the model

2.1 Add a short main-text section on when price impact is mechanical: limit order books, automated market makers,
    dealers who price flow by inventory, not information.
2.2 State the boundary openly: with a rational market maker, feedback flow is netted out (the paper's own result).
    Present this as the scope condition, not a footnote.
2.3 State openly which tools are classical (observational equivalence, aggregation, Prony, super-resolution) and
    list what is new: sufficiency inside a strategic market, the calm/stress asymmetry, the value of disclosure.
2.4 Move linearity and exponential memory from assumptions to a discussed choice: what survives without them
    (the sufficiency results, the lower bounds) and what does not (the explicit upper bounds).

## Stage 3. Cut and split

3.1 Classify every supplement result as: supports the headline; robustness of the headline; separate topic.
3.2 Keep the first two classes. Target a supplement of about 40 pages.
3.3 Move the separate topics to a second paper: cascades (threshold, dealers, dynamics), the insider (alone and
    against a strategic group), nonlinear and learning traders, hard-limit rates. They form a coherent paper on
    "what happens after a breach".
3.4 Rebuild the verification table, the checks and the Lean import list for each paper, so each stands alone.
3.5 Recheck every cross-reference, the abstract and the introduction against what remains.

## Stage 4. Author verification of the proofs

4.1 Work through the "Check by hand" column of the author checklist for every result that stays in Paper 1.
4.2 For each proof, one author writes it out independently from the statement, then compares with the text.
4.3 For each Lean-checked result, compare the Lean statement with the prose statement, line by line.
4.4 Log every discrepancy; fix the text or weaken the claim. Nothing is called machine-checked unless the Lean
    statement is the claim.
4.5 Priority order: the headline theorem; the lower bound (hard pair, Le Cam step); the Prony upper bound; the
    saturation theorems; then the rest.

## Stage 5. Evidence

5.1 Hyperliquid (H1). Data are not analysed before 10 December 2026. Before that date: write the specification,
    simulate it, have the authors approve it, and push it. The test: account-level positions give composition
    directly, so check whether composition changes while the estimated kernel and prices do not.
5.2 Run it once. Report the result as it comes, pass or fail. No rerun, no redefinition.
5.3 Whatever the outcome, add a calibration exercise that needs no test: the data requirement of Stage 1.2 for two
    or three real markets, as a table in the main text.
5.4 Keep Taiwan in supplement S7 only (amendment R1). Keep the failed KRX design reported as failed.
5.5 If H1 passes, it becomes the paper's second headline and moves into the abstract. If it fails, the paper stays
    a theory paper with a calibration, and says so.

## Stage 6. Rewrite the main text

6.1 Introduction: question, headline with numbers, why the model, what is new, what is not claimed.
6.2 One section per part of the headline theorem; one section of extensions; one of scope and limits.
6.3 One figure that carries the headline (data requirement against memory separation, with the stress and
    disclosure alternatives marked).
6.4 Plain statement of AI involvement in the acknowledgements or methods note, as the journal's policy requires.
6.5 Length check against JEDC limits; abstract within the word limit.

## Stage 7. Consistency and release audit

7.1 Full rebuild of all versions; zero undefined references; bibliography pruned to cited keys.
7.2 Full check suite and full Lean build with axiom audit; receipts regenerated and committed.
7.3 Every number in the text traced to a script output (the traceability audit, rerun).
7.4 A hostile-referee pass on the cut paper: the ten hardest questions, each with a written answer.
7.5 Replication package: one command for the checks, one for the Lean build, a README with versions.

## Stage 8. Submit

8.1 Cover letter stating the headline, the scope condition, and what is machine-checked.
8.2 Submit Paper 1 to JEDC. Post the working paper.
8.3 Then start the second paper from the material moved in Stage 3.3.

## What cannot be fixed by work alone

- A true breakthrough result needs either new mathematics or a striking empirical fact. The plan gives the second
  a fair chance (Stage 5); it cannot guarantee it.
- The model's scope condition (mechanical impact) is a real limit. It can be defended, not removed.
