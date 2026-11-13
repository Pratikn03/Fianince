# P1R: tests of Paper 1 on algorithm-level regulator data (DRAFT: not approved, not registered, no data)

Drafted 13 November 2026 by an AI system for the authors. Nothing here can run without a data-sharing agreement with
a regulator or exchange; no such agreement exists, and no data have been requested or read.

## Data that would be needed

Executed trades or positions with an identifier of the algorithm or trading strategy, at daily or finer frequency,
across several instruments and over several years. Examples of where such records exist: the US Consolidated Audit
Trail; transaction reports under MiFID II/MiFIR with the algorithm identifier field; exchange records in markets that
require algorithm identifiers on orders. Access would come through a regulator's or exchange's research programme.

## Tests (to be fixed, simulated and registered before any data are read)

1. **Common memory across markets (premise of `thm:pool`).** For each algorithm active in several instruments,
   estimate its memory rate per instrument from its own flow (tagged regression, `prop:tagged`); test equality across
   instruments with an equivalence margin. Unlike P1X, the flow is per algorithm, so the test does not face the
   mixture problem that sank the P1X designs.
2. **Speed limit (`thm:track`).** Estimate composition from prices alone with a moving window and compare it with the
   composition computed from the identifiers. Prediction: the price-based composition error grows with the measured
   drift speed of the population at the cube-root rate, and is of order one above the speed limit; price-based
   market-wide quantities track well throughout.
3. **Crowding (`prop:hidegame`).** Measure the dispersion of memory rates across algorithm classes before and after
   an algorithm-identification requirement is introduced. Prediction: dispersion rises after identification, most for
   strategies with the most to lose from targeting.
4. **Partial disclosure (`thm:partial`).** With identifiers hidden for a chosen subset of classes, compare the
   error of price-based composition estimates with the predicted exponent `4K' - 2`.

## Before registration

As for every earlier test: specification, executor and simulation check (size and power) committed and hashed
before any data are read; each test runs once; failures reported as they come.
