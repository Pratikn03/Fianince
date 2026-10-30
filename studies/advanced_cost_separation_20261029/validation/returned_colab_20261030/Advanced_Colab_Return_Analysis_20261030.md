# Analysis of the returned advanced Colab run

The run completed successfully. Its scientific outcome is conditional: the
implementation is reproducible, and the experiments reveal both useful
information and economically wasteful information purchases. The run does not
establish general profitability, real-market safety, literature novelty or a
9+ publication assessment.

## What was verified

The uploaded ZIP contains 612 files: 611 manifest entries and the manifest.
Every checksum matches, the ZIP passes its integrity test, and there are no
unlisted files. Every one of the 288 checkpoint JSON files links to the correct
statistics archive. All 15 source-snapshot files match the released code. The
recomputed source fingerprint matches the recorded fingerprint.

The research runner completed in 52.71 seconds, excluding notebook setup.
The configuration was Deep Research, 24 seed clusters, 12 economies per seed,
4,096 measurement repetitions per economy and N, N=8/32/128, three information
prices, seven measurement rules and a same-error oracle. The resulting 20,736
policy/cost rows share observations; they are not 20,736 independent markets.
Python was 3.13.18; NumPy/SciPy/pandas match the pinned versions.

All 27 implemented tests passed. Lean 4.19.0 verified seven concrete numerical
inequalities and reported no axioms for those certificates. The compiler ran
without the local host compatibility shim. These certificates do not formalize
the market dynamics, Gaussian tail argument or complete general theorem.

The numerical policy results also reproduce the local headless run with the
same seed to a maximum absolute difference of about 1.25e-14 across numeric
fields, despite different Python minor versions. This is reproducibility using
the same implementation, not independent replication.

## The central financial finding

For the standard Gaussian rule in the independent-Gaussian economy design:

| Information price | Mean net advantage over matched-error no-data | Exploratory 95% seed-cluster interval | Positive rows | Negative rows |
| --- | ---: | --- | ---: | ---: |
| Free | +0.13047 | [0.08458, 0.18420] | 99/144 | 0/144 |
| Baseline price | -0.02953 | [-0.07022, 0.01310] | 59/144 | 80/144 |
| Five times baseline | -0.17212 | [-0.21856, -0.12715] | 26/144 | 83/144 |

Values are hypothetical model dollars per inventory-service decision. Baseline
price is N*(0.0005+0.000025*H); it varies with the observation count and horizon.
H=10/60/240 denotes model minutes. A zero includes no-purchase fallbacks and
decisions with no economically relevant change; it is not necessarily a failed
observation. The counts use a 1e-10 numerical tolerance.

These price-specific intervals are an additional exploratory analysis performed
after the return, using paired averages within 24 seed clusters and 5,000
bootstrap resamples. They are not confidence statements about actual market
profit. The baseline-price interval crosses zero: the run does not establish
positive average net value there, or a reliably negative population mean there.
The high-price design has a negative interval under this simulator sampling
scheme. No prior probability distribution over actual markets is justified.

The original illustrative positive-value contract remains a separate pointwise
example. Its exact conservative numerical witness was checked again. The
existence of a positive-value example does not imply positive value for all
economies or all information prices.

## Certification and economic value are separate questions

Among purchased standard-Gaussian rules in the independent-Gaussian scenario,
the mean unsafe-action frequency was 0.834%, below the nominal 2.5% allowance.
Across all 6,535 declared-valid purchased-rule checks, Holm correction produced
zero rejections. Some individual simulated frequencies exceed 2.5% because
finite repetitions fluctuate. Non-rejection does not prove the theorem.

Here an unsafe action means its reserve exceeds the budget against a permitted
worst-case future shock path. It is not an observed liquidation, default,
historical crash frequency or real-world loss event. Passing that audit does
not mean that paying for the certificate was profitable.

The standard Gaussian and declared-variance Gaussian rules coincide exactly
in the independent-noise design. The scalar rule beats the full-response
ellipsoid by 0.01038 model dollars on average, with an exploratory paired
seed-cluster interval [0.00388, 0.01900]. This is a task-specific comparison
between existing interval constructions, not evidence of a new estimator.

## Failures that must remain visible

For purchased standard-Gaussian rules, the mean unsafe-action frequency was:

| Scenario | Mean frequency | Interpretation |
| --- | ---: | --- |
| Independent Gaussian readings | 0.834% | Within the stated noise/stationarity contract |
| Correlated Gaussian readings, iid rule used | 14.695% | Independence assumption is wrong |
| Downward-biased readings | 31.169% | Mean is wrong; a variance correction cannot repair it |
| Future regime change | 61.033% | Past gain no longer bounds the future gain |

These are unweighted descriptive averages of dependent configuration rows,
including the predeclared zero-price setting. They are diagnostic frequencies,
not pooled independent market failure probabilities. Individual configurations
can fail much more severely than their scenario average.

Under correlated Gaussian readings, the declared-variance rule reduces the
mean frequency to 0.409%, and the projected Student-t rule to 1.153%. Their
average net advantages are nevertheless negative over this broad design.
Conservative information can improve protection while being too expensive.

The median-of-means rule retained its stated finite-variance/reset assumptions,
but was often very conservative and economically costly; for N below its
proved block requirement it used a paid prior-bound fallback. Student-t's exact
Gaussian guarantee does not extend automatically to the t3 scenario, even when
its observed failure rate happens to look acceptable. Neither method fixes
biased measurements or future structural change.

The full returned design retains 7,489 negative-advantage rows and 1,743
unaffordable purchase rows. These totals mix methods/scenarios and must not be
turned into an overall market success/failure percentage.

## A concrete economic weakness in the current purchase protocol

The fixed-N experiment purchases information whenever the bill is affordable.
It does not optimize whether information should be purchased. Affordability
and economic value are different requirements.

In 32 of 288 generated economies the known service premium is no greater than
the known linear execution/carry cost. Even before observing anything, positive
inventory has no positive expected service surplus. Paying for measurements
cannot rescue that particular objective. These cases correctly expose the
cost of a fixed-purchase rule; they should not be sold as economically optimal
information acquisition.

A second transparent example is case s000_c000 at N=32 and baseline price.
The no-data and response-informed oracle already have the same expected value,
about 0.75902, because additional response knowledge cannot relax the relevant
position limit. The purchased rule earns about 0.73500 after a 0.024 information
bill. Learning something measurable need not change the financial decision.
This is the first indexed case, not a selected best-performing example.

The next model improvement should make the information purchase explicit:
first screen known nonprofitable services and cases where response information
cannot change exposure; then study an acquisition rule that uses only available
information. Choosing the best N or policy after examining hidden true gains
would leak information. Any new purchase rule needs its own proof/validation
and an explicit record that its design followed this run.

## What belongs in the papers

Paper 1 can retain the scoped latent-cohort identification obstruction. This
run does not prove a new first-in-literature identification lower bound or
extend it to arbitrary probes or ordinary exchange tapes.

Paper 2 should explain the financial institution, timing and costs before
presenting the aggregate-response certificate. The appropriate claim is:

> Under controlled, stationary observation assumptions, a finite-horizon
> aggregate-response bound can support an exposure decision without recovering
> latent cohort weights. Positive net information value requires additional
> economic conditions; high prices and invalid observations can defeat it.

The thesis can connect three distinct questions: what is identifiable, what is
sufficient for a particular financial decision, and when purchasing that
information is worthwhile. The returned evidence strengthens the need for the
third question. It does not establish a market-wide stability transformation.

There are no historical coins, exchange tapes or crash replays in this returned
run. The quote-data stage is explicitly NOT_RUN. The tiny synthetic quote
fixture inside the test suite does not count as empirical validation. These
results must be kept separate from any historical data in earlier drafts.

The present evidence supports a reproducible restricted research draft.
Exceptional publication quality remains unestablished. The substantive next
requirements are a precise literature gap, independent review of the complete
general proof, an economically defensible acquisition decision, and a valid
bridge from available observations to the claimed financial use. More random
seeds alone cannot resolve those questions.

## Provenance

- Uploaded file: MM_advanced_deep_seed20261101_v1.zip
- ZIP SHA256: e35c10f6b2767a4800c960ef769d1ab05862c4a37422d179f4973b5c8cf151e9
- Source SHA256: ce8caa657f6ad626391a5fe6429450842365259c767942641673159521a49610
- Base seed: 20261101; profile: deep; workers: 2.
- The original return ZIP is preserved. This analysis does not alter its source,
  configuration, statistics or outcomes. The additional price/paired analyses
  are explicitly exploratory. This report has not rewritten the manuscript PDFs.
