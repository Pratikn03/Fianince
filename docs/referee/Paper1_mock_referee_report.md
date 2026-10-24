# Mock referee report: "Auditable Memory and Financial Identification Limits in Electronic Limit Order Books"

*Internal, adversarial review written to anticipate a field-journal referee (Quantitative Economics or a comparable journal).
Version reviewed: repository main, 24 October 2026 (95-page working paper and the 78-page journal version).*

## Summary

The paper models a market in which K cohorts of traders follow exponential-memory rules (the reduced form of steady-state
Kalman filtering or regularized online learning) and asks what an outside observer can learn about them from prices and
aggregate order flow. It shows that prices identify only a merged rate–weight measure, that separating K cohorts with memory
spacing Δη needs of order (Δη)^-(4K-2) reset experiments (with matching upper and lower bounds), that general completely
monotone memory can be learned only at rate 1/log N, that probing costs executed quantity of order δ^-2 and capital of order
δ^-4, and that class-tagged disclosure removes the polynomial barrier. Empirically, Binance trader-class positioning ratios
and CFTC Commitments of Traders reports are said to pin down class memories far more precisely than prices and flow.

The question is good, the writing in places is careful about what is and is not claimed, and the paper reports
non-confirmatory evidence, which is rare. My concerns are about novelty relative to the mixture and super-resolution
literature, the economic content of the model, and above all whether the empirical comparison measures what the theory says.

## Main concerns

**1. What is new beyond a known moment problem?** The authors concede that the (Δη)^-(4K-2) exponent is the squared amplitude
condition number for clustered nodes. The closed loop is then handled by a recursion that recovers the kernel k from the
impulse response h with a Lipschitz constant independent of Δη (proof of the matching upper bound). If so, the closed-loop
problem reduces to the open-loop moment problem up to a known smooth, well-conditioned map, and "the rates are zeros, not
poles" reads as a reparametrization rather than a source of difficulty. The authors should either show a case in which the
loop changes a rate or a constant materially, or reframe the contribution around the two parts that are genuinely financial:
the translation into executed quantity and capital, and the value of disclosure.

**2. The agents do not solve an economic problem in equilibrium.** The new Proposition on economic primitives helps: memory
rates come from signal-to-noise ratios through the Kalman gain, and the barrier transfers to those ratios. But trading
intensities are exogenous, desks' perceived signal processes are not required to be consistent with the closed loop they
create, and the impact parameters are primitives rather than equilibrium objects. The paper says so honestly; a finance
referee will still ask for at least one equilibrium in which memories and intensities are both derived, and for a check of
whether the barrier survives when intensity is tied to information quality (the paper notes that it could weaken).

**3. The reset contract.** "N independent reset experiments" is the contract under which the minimax results are proved, and
no market allows a reset. The capital translation addresses cost but not feasibility, and the passive Whittle result relies on
stationarity and Gaussianity. Please state early, in the introduction, that the theorems describe what a probing supervisor
could learn, and that passive observation is a different and weaker contract.

**4. The empirical comparison may be driven by its design, not by identification.** This is the most important point.
 - *Different horizons.* The price-only estimates come from a regression of five-minute flow on twelve lagged five-minute
   returns: a one-hour window. The class-tagged memory rates are near 0.99 per five minutes, half-lives of roughly six to
   twelve hours. A one-hour kernel cannot see memories of that length, so the price-only intervals are wide partly by
   construction.
 - *Bounded parameters.* The price-only rates are fitted on [0, 0.99]. In the fresh replication (Test E1v2), at least one
   price-only rate interval reaches a bound of the fit in 28 of 30 symbols. A width ratio between an interval that spans the
   admissible range and one that does not is not a ratio of precisions; "28 to 124 times more precise" overstates what is
   measured. Compare in common units (implied half-lives, or the same functional estimated both ways) and over a common
   horizon.
 - *Different objects.* The tagged series is the persistence of a long/short positioning ratio. Slow position turnover would
   produce high persistence without any learning memory. The theory's tagged contract is class-tagged *flow*; the data are
   class-level *positions*. The mapping n = (R−1)/(R+1) and the AR(1) with contemporaneous returns needs a derivation from
   the model, or the claim should be weakened to "positioning data restrict a persistence parameter that prices leave free".
 - *Drift.* An exploratory analysis in the companion thesis finds that the top-position persistence differs across quarters
   in 13 of 30 symbols. Pooling 21 months then mixes regimes; the registered scaling test D1 fails its rate prediction,
   plausibly for this reason.

**5. Weekly COT against fast memory.** The CFTC evidence narrows "fast-class memory intervals" using weekly reports. Please
explain how weekly positions identify memories that the theory places at intraday horizons, and report the implied
half-lives.

**6. Capital figures.** The USDT capital numbers depend on the calibrated Roll noise and on margin and fee assumptions. A
sensitivity table (noise, margin, fee) would show whether the δ^-4 law, not the calibration, drives the headline figures.

**7. Length and focus.** At 95 pages (78 in the journal version) the paper carries a resource theory, a minimax theory for
general memory, an accounting theory with duality, disclosure, spectral blindness, empirical work on two asset classes and
learning-agent simulations. The core contribution is lost. A 40-page paper built around one theorem (the barrier and its
price in capital) and one piece of evidence would be far stronger; move the rest to an online appendix or a second paper.

**8. Registered evidence should be in the paper.** The authors registered and ran a fresh replication of the disclosure result
(E1v2 P2, passed in 30 of 30 symbols) and a scaling test (D1: the tagging advantage grows, passed; the parametric rate,
failed). Both belong in the paper, with point 4's caveats, because they are the strongest and the most honest evidence
available.

## Minor points

- Define "merged measure" once in words before using it; readers from finance will not know a moment problem.
- Table 1 (comparison with mixture estimation) is useful; add a row for "what the observer must assume" (memory bound,
  stationarity).
- Lean declarations are mentioned in the main text; a finance audience will read this as distraction. Keep one sentence in
  the introduction and move the rest to the replication package.
- Several numbers are reported to four or five significant figures; two or three suffice.
- The worked example (two Kalman desks) is the most persuasive page of the paper; move it to the introduction.

## Recommendation

Major revision at a field journal. As it stands, the theory is solid but its novelty over the mixture literature is
under-argued, and the headline empirical comparison is vulnerable to the horizon and bounded-parameter problems in point 4.
Both are fixable: a horizon-matched, common-unit comparison, and a paper cut to its core.

## What would change my recommendation to "accept after minor revision"

1. A horizon-matched comparison of price-only and tagged estimates in common units, on fresh data, pre-registered.
2. One equilibrium in which memories and intensities are derived, or a precise statement of the class of equilibria for which
   the barrier holds.
3. A 40-page main text built around the barrier, its price in capital and the value of disclosure.
