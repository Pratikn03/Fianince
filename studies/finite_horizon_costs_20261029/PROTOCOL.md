# Fixed-horizon information and net inventory-service value

This is a new exploratory analytic extension, not an independent preregistration.
The design uses lessons from the preceding returned synthetic run. This file is
frozen before this package's first experiment; its hash is exported. All rows,
failed comparisons and assumption violations are retained. No publication score
or confirmed priority follows from the run.

Primary question: with the same noisy response observations and all information
and trading charges paid, can a finite-horizon exposure decision have positive
net information value while resolving the cohort weights is unaffordable?

Primary model: a=.4, kappa=1, total feedback Q=.4; cohort pair A has weights
Q/2,Q/2 at rates .5-delta,.5+delta; pair B has weights Q/5,4Q/5 at rates
.5-2delta,.5+delta/2. Primary delta=.01. The decision horizon and each reset
experiment last 60 one-minute model periods. All 60 response taps are observed;
per-tap reading noise sigma=.02 is independent Gaussian with known variance.
The two structural alternatives and every policy receive these same taps.
The broad certification class allows arbitrary finite positive cohorts with
Q<=.55 and rates in (0,1]; no lower memory-rate bound is imposed. The known
feedback upper bound, plant, reset and noise are substantive assumptions.

The institution is a price-taking, unlevered inventory-warehousing desk. It
receives a prequoted service fee of .08 per unit after settlement, holds one
fixed long position for 60 model minutes, and then closes. Initial price=100,
wealth=1000, stressed-settlement loss budget=1, external flow bound=.04.
Trading charges are .002 I + .0002 I^2, plus a 5% annualized opportunity/carry
charge on 100 I for 60/(365*24*60) years. Information costs .002 per reset,
including its stated experimental/time charges, so N=32 costs .064. These
prices are hypothetical normalized dollars; no market calibration is claimed.
The total information fee enters both the stress reserve and net profit.
The service fee is unavailable as collateral until after stressed settlement.
The known future zero-mean bounded-flow assumption defines expected service
profit; no return-training or validation tapes are supplied to any policy.

Primary measures: certified units, expected service profit after every charge,
the analytic lower bound on net information value relative to the SHARP
no-observation robust policy, risk-reserve violations, and exact known-pair
testing sample requirements. Readings repeat 20,000 times in full mode; these
are synthetic noise draws, not independent market days. Gaussian quadrature
also integrates decision values directly. The seed is 20261030.

Benchmarks: no-data robust optimum; oracle response; direct Gaussian functional
certificate; Gaussian linear-functional projection (exactly the SAME rule,
included to expose methodological overlap); full-response ellipsoid;
uncorrected point estimate; exact gain disclosure at several hypothetical
fees; an optimistic identify-first lower-cost requirement. A rational identify-
first user may abandon identification and choose no-data; no unnecessary
identification mandate is asserted to be current regulatory practice.

Sensitivity grids: N=8,32,128; feedback Q=.1,.4,.55; eta=.02,.2,.5,1;
per-reset fees=0,.001,.002,.005,.01,.02,.05; service fees=.002,.003,.02,.08;
horizons=10,60,240. No best sensitivity row replaces the primary.
Hard-pair deltas=.08,.04,.02,.01,.005,.0025, calculated in rational arithmetic
before conversion to floating point; report all, not only a fitted slope.

Failure challenges: positively correlated tap noise with and without the
correct variance; biased readings; changed feedback after measurement;
signed response outside the positive class; and repeated deployments without
a time-uniform or multiplicity-adjusted certificate. Funding, trade and
information costs must remain in every relevant comparison.

The theorem has a written analytic proof and exact rational/numerical checks.
It is NOT a completed Lean formalization, an independent proof review, proof of
novelty, an ordinary-public-tape guarantee, an endogenous market equilibrium,
or evidence that an actual exchange becomes safer.
