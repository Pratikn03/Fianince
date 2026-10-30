# A positive-value witness without floating-point root or quantile calculations

This is a concrete arithmetic certificate, not the entire model formalized.
Retain the original controlled Gaussian reset and inventory-service contract.
Use N=32, H=60, sigma=1/50, error budget gamma=1/40 and a conservative
normal margin z=21/10. The standard error squared is 3/4000, which is below
(11/400)^2. Thus twice the margin is below 231/2000.

The standard Mills bound gives P(Z>z) <= exp(-z^2/2)/(z*sqrt(2*pi)).
Since pi>3, sqrt(2*pi)>12/5. Lower-bound exp(z^2/2) by the first nine
positive Taylor terms. Exact rational arithmetic verifies that the resulting
tail upper bound is less than 1/40. This ANALYTIC Mills implication is written
here; the Lean file checks only its final rational inequality certificate.

At total feedback .4, the infinite positive gain is 5, so the finite gain is
at most 5. On the two-sided good-reading event (probability at least .95),
the gain upper bound is at most 5+231/2000. The fixed position 449/100
prefunds every charge and has stress reserve below 1. The actual optimized
position is at least that large on this event. Costs use b=1/500+1/1752,
d=1/5000, data bill 8/125, and service premium 2/25.

The sharp prior gain is 20*(1-(19/20)^60). At position 131/100 the
no-data stress reserve is greater than 1, so the robust position is below
131/100. The prefunded unrestricted position is below 10. Consequently an
upper bound on the best same-error-budget no-data profit is
(p-b)*[(39/40)*(131/100)+(1/40)*10].

Subtract that bound and the information bill from .95 times the gross profit
at position 449/100. Exact fractions give a lower bound approximately
0.14419015, strictly above 0.14. All seven concrete inequalities are exported
with their numerators and denominators and checked by Lean with no axioms
reported when the compiler succeeds. Their translation and the Gaussian,
market and optimization implications still require the written proof and
independent review. No general theorem or originality is inferred from these
seven numerical certificates.
