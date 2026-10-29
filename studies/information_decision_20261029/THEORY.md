# The mathematical contract and proof boundary

This is an exploratory finite-class research package, not a claimed new general
minimax theorem. The eight freshly buildable Lean statements are standard
conditional decision logic. They do not formalize the statistical or market
arguments below. Independent review of both novelty and correctness remains open.

## A. Market and account

At minute t, x[t+1] = a*x[t] + kappa*(sum_i q[i]*y[i,t] + u[t]),
y[i,t+1] = (1-eta[i])*y[i,t] + eta[i]*x[t+1].
The candidate class fixes a=.4, kappa=1, q>=0 and rates in [.02,.8]. It
includes nearby split cohorts around .2 and .5 at gaps .01, .02 and .04;
grid singletons are not equated with general identifiability. The
hard-pair witness uses other explicitly named rates. Observation sigma=.02 is
known. These are substantive assumptions, not quantities learned from public data.

The observer measures L=12 impulse taps from N independent reset episodes, with
independent Gaussian reading errors across taps and episodes. Each episode also
requires a verified zero initial state. A trading account or exchange tape does
not supply these conditions automatically. Common training and validation paths
are additional reset observations and their counts are recorded separately.

The investor starts flat with W0=1000 and P0=100, chooses 0<=I<=9.9, buys at
time 0, holds I for H=60 one-minute periods, and closes completely at minute 60.
The position is price-taking. A round-trip dollar charge c(I)=.002*I+.0002*I^2
is split equally between entry and exit. Intermediate equity is cash+I*P[t];
terminal wealth is W0+I*x[H]-c(I). There is no leverage, borrowing cost, futures
funding, passive-fill uncertainty, or effect of this account on market feedback.
No result is about equilibrium, market-wide admission, or customer liquidity.

## B. Finite-horizon loss bound (analytic proof; NOT Lean-formalized)

Let h[j] be the price response to a unit flow impulse under zero initial state.
Linearity gives x[t] = sum_{j=0}^{t-1} h[j]*u[t-1-j]. For |u[t]|<=ubar,
|x[t]| <= ubar*sum_{j<t}|h[j]| <= ubar*G_H, with G_H=sum_{j<H}|h[j]|.
The first inequality is the triangle inequality; the second adds nonnegative
terms. The full round-trip cost is at least the cost paid before any intermediate
mark. Hence loss from INITIAL wealth at every date is bounded by
I*ubar*G_H+c(I). At the terminal date an adverse reversed-sign shock sequence
attains the price bound for a fixed impulse response; in the positive class the
constant negative sequence attains it for a long position. Actual code tests
all shock corners for a small horizon and the account cash identities.

For a candidate set C, use max_{theta in C} G_H(theta). This is a sufficient
bound for the true economy if it belongs to C. Empty C is an inference conflict:
the code abstains from positive positions, rather than exploiting logical
vacuity. This result is not a bound on peak-to-trough drawdown, does not cover
changing inventory, and is not a new general control-theoretic identity.

## C. Simultaneous finite-tap confidence set (analytic proof; NOT Lean-formalized)

For each tap, its N-reading mean has error Normal(0,sigma^2/N). Choose
r=sigma/sqrt(N)*Phi^{-1}(1-gamma/(2L)). Each tap exceeds its band with
probability gamma/L. The union bound gives probability at most gamma that ANY
true tap leaves its band. No independence between the resulting coverage events
is required for the union bound, but the specified standard errors must be valid.

C consists of the DECLARED finite-class economies whose L exact responses all
lie in these bands. If the true economy is in that class, P(truth in C)>=1-gamma.
It follows that every policy selected from the robust feasible action set has
the stated loss bound on the same coverage event, including data-selected actions.
This is one-decision coverage, not time-uniform control of repeated deployment.

The experiment deliberately violates class membership, reading correlation,
reading bias, or temporal invariance in four regimes. The above guarantee then
does not apply. Report their outcomes; no pass is guaranteed by this protocol.

## D. Disclosure and the objective

Exact verified disclosure intersects C with a band of width .05 around the
true minimum eta. If truthful, it preserves membership and weakly enlarges the
unpaid feasible action set. It need not enlarge it strictly. Paid disclosure
subtracts $0.01 from wealth and from the remaining loss budget. A net benefit is
NOT guaranteed. This illustrative price is not calibrated to a reporting regime.

All certificate policies optimize the same empirical expected-log terminal
wealth objective from the same training paths. The oracle knows the response,
not the future shocks, and receives the same return-training information.
The robust empirical comparator also uses a fixed adverse shifted empirical law.
These finite-horizon baselines are adaptations; they do not reproduce published
infinite-horizon risk-constrained or distributionally robust Kelly theorems.
Equal risk bounds do not imply equal expected returns, utility or optimal policies.

## E. The separation witness and open central theorem

The one-cohort economy q=.4, eta=.5 and the two-cohort economy with weights
.2,.2 and rates .5-delta,.5+delta have the same infinite gain 1/(1-.4-.4)=5.
Their finite impulse sequences differ. The known-alternative Gaussian testing
error is Phi(-sqrt(N)*||h1-h0||/(2*sigma)). The emitted table is a numerical
witness with exact known-alternative error, not proof of a uniform unknown-
mixture rate or a disclosure-welfare theorem. Finite-horizon gains need not be
exactly equal. All reset counts and tap counts remain distinct.

OPEN: an independently reviewed comparison of optimal identification and
decision VALUE under a matched information budget, a well-defined loss/utility
class and an appropriate continuous model class. A finite declared grid cannot
establish that theorem. Existing manuscript rate claims remain under their
existing review status; this package does not mark them proved.

## F. Fresh Lean coverage

DecisionCore.lean proves eight elementary logical statements: membership-to-
soundness, disclosure refinement, data-selected action soundness, empty-set
vacuity, certification without uniqueness, feasible-set value monotonicity,
equal-loss safety equivalence, and a counterexample to equal-risk/equal-utility.
It uses no sorry, custom axioms or Mathlib. The receipt records actual compiler
output and axiom prints. Natural-number cost and integer-value abstractions in
two lemmas are NOT a formalization of real-valued account dynamics.

The optional host shim redirects only /proc/<CURRENT_PID>/exe to its equivalent
/proc/self/exe on restricted containers. It never changes the Lean kernel or
proof source; its hashes and use are recorded. Normal Colab should not need it.
