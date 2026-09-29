# What survives smoothing, and what does not

Status: bounded mathematical analysis accompanying a predeclared numerical
robustness grid. The proposition below was developed **after inspecting the
grid**, not registered as a confirmatory prediction. It is an elementary
model-specific proposition, not an established novel theorem. It has not been
formalized in Lean. Earlier Lean certificates do not cover this extension.

## 1. Contract and notation

Use exactly the two-period economy and information timing in PROTOCOL.md.
Dealer 0 has A0=(0,1,0), S0=(0,0,1) in ask order (2,4,6), and does not learn.
Dealer 1 waits at time zero and does learn. Its initial active and shadow
tables can be any finite real triples, not necessarily equal or tied. Both
dealers refresh from shadow before period 1. Let the rival's step size be
0 < alpha <= 1, and let both use

    p_j(Q) = epsilon/3 + (1-epsilon) exp(Q_j/tau) / sum_k exp(Q_k/tau),

where 0 <= epsilon < 1 and 0 < tau < infinity. Costs are initially zero.
All expectations integrate independent current economic draws, not signals
observed before quoting. Delta denotes dealer 0 early deployment minus waiting,
with every other primitive and decision held fixed.

Write l=p_2(S0)=p_4(S0), h=p_6(S0), and d=h-l>0. Early deployment replaces
probability d of dealer-0 ask 4 by ask 6; its ask-2 probability is unchanged.
Let b_a>0 be dealer 1's initial probability of ask a, and q its initial shadow.
Let f(q)=p_2(q) be its next-period probability of ask 2.

## 2. Proposition: the gross welfare effect is strictly negative

Under the contract above, Delta E[W0]=0 and Delta E[W1]<0. Therefore the
cumulative gross welfare contrast is strictly negative, for any finite rival
active/shadow tables. With rival learning disabled, the gross welfare contrast
is zero. The same zero follows at alpha=0 or epsilon=1. These statements do
not assert that the private gain is positive or exceeds a deployment cost.

### Proof

Direct settlement and the stated distribution give

    E[W_t | current quote law] = 2 + Pr(minimum ask_t=2)/4.

Because deployment leaves dealer 0's ask-2 probability unchanged and the
rival's period-0 law fixed, its period-0 welfare contrast is zero.

Couple the changed mass d at focal ask 4 versus 6 and condition on the rival's
chosen action and the economic draw. If it chooses ask 2, its reward and update
are identical. If it chooses ask 4, switching the focal ask 4 to 6 changes a
tied fill to a full fill. Its reward rises from 2 to 4 when V=0 and C>=4, an
event of probability 1/8; in all other events its reward is unchanged (a fill
at V=4 has zero profit). If it chooses ask 6, the same focal switch changes
no fill to a half fill whenever C>=6. This raises its reward from 0 to 3
when V=0 (probability 1/8) and from 0 to 1 when V=4 (probability 3/8).
All these probabilities are unconditional on the rival action and follow
directly from the six economic atoms.

For j in {4,6}, the softmax component obeys

    partial f / partial q_j = -(1-epsilon) s_2(q) s_j(q) / tau < 0,

where s is the unmixed softmax. Increasing a chosen non-low action value
strictly decreases next-period ask-2 probability. Define q^(j,r) by replacing
q_j with (1-alpha)q_j + alpha*r, leaving other entries unchanged. Integration
over all affected events gives the exact expression

    Delta E[p_2(Q1)] = d * {
      b_4/8 * [f(q^(4,4)) - f(q^(4,2))]
      + b_6/8 * [f(q^(6,3)) - f(q^(6,0))]
      + 3*b_6/8 * [f(q^(6,1)) - f(q^(6,0))]
    } < 0.

Dealer 0 refreshes its identical frozen shadow in both regimes at period 1,
with ask-2 probability l. Conditional action randomization is independent.
Thus the change in probability that at least one dealer quotes 2 is
(1-l) times the expression above. Multiplication by 1/4 proves the strict
welfare result. Disabling learning or setting alpha=0 makes all three bracketed
differences zero; epsilon=1 makes d=0. This proves the stated nulls. QED.

The proof does not rely on a tied rival initialization. It does rely on this
quote grid, economic distribution, the focal policy swap, own learning being
off, rival learning being on, and the two-period horizon. It cannot be reused
for arbitrary multi-period learning, equilibrium candidate selection, or
financial instability.

## 3. Why profit need not have the same robust sign

At period 1 the focal dealer's expected profit against rival asks 2,4,6 is

    u = (-l/8, 0, l/4 + 3*h/4).

The learning contribution to profit is u dot Delta E[p(Q1)]. The update toward
ask 6 tends to help the focal dealer, but the update toward ask 4 can pull
probability away from ask 6 and reduce its profit. There is no general
positive-profit claim here. Separately, with initial rival probabilities b,
the immediate strategic profit contrast is

    Delta E[profit_0, period 0] = d * (-b_4/4 + b_6/4).

It is zero against an initially uniform rival but can have either sign with
non-tied active values. This explains why a positive learning interaction
need not imply a positive total incentive. The learning-interaction contrast
subtracts the frozen-rival deployment contrast at otherwise identical inputs;
it does not establish a unique mediation decomposition.

## 4. Strict inequalities persist locally under a smooth rule

For fixed finite horizon, finite action/economic support, and tau>0, each
history probability is a product of smooth softmax probabilities. The shadow
updates along a fixed history are affine in initial tables. A finite sum of
history-weighted payoffs is therefore continuous in initial tables, alpha,
epsilon and positive tau; net payoffs are also continuous in deployment costs.

Consequently, any **strictly verified** profit-positive/welfare-negative point
has a nonempty open neighborhood retaining those signs. Likewise, a strict
pure equilibrium and strict planner ranking persist locally. This continuity
fact supplies a local existence statement, not the radius of that neighborhood
or proof that every point between sampled grid values has the same sign.
It does not turn a selected example into a prevalence result.

## 5. Economic and novelty boundaries

Gross welfare varies here through participation at the minimum ask 2, which
is statically dominated in the one-period dealer-profit game. Raising the
minimum from 4 to 6 changes transfers but not total gains from trade. The
mechanism is therefore tightly tied to this stipulated economy and bounded
learning behavior. An owner does not choose a fully optimal contingent
teaching strategy or an unrestricted rational trading policy.

Influencing a learner through realized rewards is established strategic
teaching. Arslantas, Yuceel and Sayin (2024), Section II, already specify
softmax action choice and chosen-action reward updates:
https://arxiv.org/html/2403.08906v3 . Our audit is not a priority claim for
those ingredients. The candidate economic distinction remains a restricted
early-deployment game with explicit participation, customer surplus and real
costs, and must still be compared critically with the closest literature.

The computation enumerates the finite probability tree; it does not train
agents, validate a real market, or establish an operational intervention.
