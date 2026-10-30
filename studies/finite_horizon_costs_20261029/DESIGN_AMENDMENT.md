# Stronger no-data benchmark added after the first execution

The first full synthetic run was inspected before this amendment. A proof
review found that a deterministic no-data rule has zero unsafe-action
probability, whereas the certificate allows gamma=.025 measurement error.
To compare the same allowed error budget, add the analytically optimal
randomized no-data benchmark: use the sharp robust position with probability
1-gamma and the unconstrained prefunded optimum with probability gamma.
Its optimality is proved in the appendix and checked against an independent
linear program. This is a theoretical comparison, not a proposed desk policy.
Add the analogous same-gamma full-information oracle as an upper benchmark.

The primary model, fees, holding period, reading budget and seed are unchanged.
The amended execution supersedes the first execution for final comparisons.
The sufficient positive-value inequality and every sensitivity now compare
against the stronger same-gamma no-data value. Both deterministic and
randomized values remain visible. This makes the comparison harder; it does
not select a more favourable parameter row. No preregistration is claimed.

Information is purchased ahead of a common future service-start deadline.
The desk's cash may earn the common reference rate while data are acquired;
no extra warehousing opportunities before that deadline are in the model.
The exogenous reset fee includes the stipulated measurement and time charges.
It is not an estimate of the self-impact or capital cost of performing actual
market probes. Those costs would need separate calibration and may eliminate
the benefit. Nothing establishes that the illustrative information fee is
available from an actual provider.
