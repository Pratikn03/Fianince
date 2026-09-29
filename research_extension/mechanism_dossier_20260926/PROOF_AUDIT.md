# A finite deployment externality: calculation and limits

Status: new post-hoc mathematical audit of the already approved v0.12 model.
The derivation below is an informal proof checked by exact arithmetic and an
AI-assisted adversarial reviewer. It is **not a Lean certificate, independent
human review, priority claim, or confirmatory population experiment**.

## 1. Economic contract

Two risk-neutral dealers post asks in {2,4,6}. Each period independently draws
V in {0,4} with equal probability and Z in {-2,2,6} with probabilities
{1/4,1/2,1/4}; customer valuation is C=V+Z. Dealers quote before seeing that
period's V, C, or rival quote. A customer accepts the minimum ask iff C is at
least that ask; tied best dealers each supply half of one unit.

Dealer i earns x_i(a_i-V). The customer receives x(C-a), and gross total
surplus is x(C-V). Actual deployment resource costs are deducted once, from
dealer payoffs and welfare. Payments cancel. There is no inventory, funding,
capital constraint, liquidation, dealer withdrawal, calibrated execution, or
systemic-loss variable in this model.

Each dealer has active A_i and shadow S_i action-value tables. With probability
epsilon it explores uniformly; otherwise it picks uniformly among the active
maximizers. Early deployment copies S_i to A_i before t=0; waiting retains A_i.
Before t=1 both dealers refresh from their current shadows, even if learning
is frozen. A learning dealer changes only its chosen shadow entry by

    S_i(a) <- (1-alpha) S_i(a) + alpha * own realized gross reward.

The learner receives no counterfactual reward or current private value before
quoting. An owner choosing early/wait knows the model and initial tables, not
future draws. This is an ex-ante finite deployment game with fixed downstream
algorithms, not unrestricted rational market-making equilibrium. The planner
has the same information and four-profile menu as the owners.

## 2. Accounting benchmark, not a new theorem

For any current quote law independent of the current economic draw:

| Minimum ask | Total dealer profit | Customer surplus | Gross welfare | Units |
|---|---:|---:|---:|---:|
| 2 | -1/4 | 5/2 | 9/4 | 7/8 |
| 4 | 1/2 | 3/2 | 2 | 1/2 |
| 6 | 3/2 | 1/2 | 2 | 1/2 |

Therefore E[W_t]=2+P(minimum ask_t=2)/4. A switch from minimum ask 4 to 6
alone changes transfers, not total surplus. In the one-period quote game,
ask 4 strictly dominates ask 2 (profit gains 1/8, 1/2, 3/4 against rival asks
2,4,6). Hence any gross welfare effect in this particular economy depends on
the frequency of a statically dominated ask. This is an important limitation,
not a generic definition of financial-market welfare.

## 3. Selected example and proposition

The approved development grid has 256 stipulated states, not trained policies.
After enumerating all 4,096 state/profile/learning-mask cells, we selected
state 140, the first state in grid order with the particular joint property
reported here. The broad screen requires positive focal profit and negative
welfare contrasts with rival learning ON, but not that same joint sign pattern
when rival learning is OFF. Six states qualify: 140,141,156,157,188,189. Requiring
**both** frozen focal-profit and frozen welfare contrasts to be exactly zero
leaves four: 140,141,156,157. States 188 and 189 already have frozen focal gains
of 81/400. State 140 meets the stricter criterion. The selection is disclosed;
the example does not estimate how frequently trained agents exhibit the effect.

Use zero-based dealer labels 0 and 1 and ask-order (2,4,6):

    A_0=(0,1,0), S_0=(0,0,1)
    A_1=(0,0,0), S_1=(0,0,0).

Dealer 0's shadow learning is frozen. Dealer 1 learns. H=2, costs initially
zero, alpha in (0,1], and epsilon in [0,1]. Dealer 1 waits; its initial active
and shadow tables are identical, so early release would not change its actions.

Let Delta be dealer 0 early minus wait. Then

    Delta E[profit_0] = (1-epsilon)^2 (36-19 epsilon) / 432,
    Delta E[W] = -(1-epsilon/3)(1-epsilon)^2 / 72.

For 0<=epsilon<1 the first expression is strictly positive and the second
strictly negative. Both vanish if dealer 1's learning is frozen, or alpha=0,
or epsilon=1. These are claims about this specified initial state and H=2.

### Proof

Write l=epsilon/3 and g=1-2epsilon/3. Early release moves probability
1-epsilon from dealer 0's initial ask 4 to ask 6, leaving its ask-2 probability
unchanged. Dealer 1 initially randomizes uniformly across all three asks.
Against that uniform rival, asks 4 and 6 each yield expected dealer-0 profit
1/4, so there is no first-period private gain. The unchanged minimum-ask-2
probability also makes first-period expected welfare unchanged.

Dealer 1's initial shadow is zero. For alpha>0, a positive selected reward
makes that action the unique maximizer; a negative reward excludes it from
the maximizing set; a zero reward leaves all three tied. Reward magnitude
within a sign class does not matter for the next action law.

Changing dealer 0's ask from 4 to 6 does not change the sign of dealer 1's
reward when dealer 1 chooses 2 or 4. When dealer 1 chooses 6, however, a
previously unfilled order becomes a tied fill with strictly positive reward
iff C>=6, an event of probability 1/2. Thus mass (1-epsilon)/6 switches from
zero reward/all ties to positive reward/unique ask-6 maximizer.

The t=1 rival action-law change is consequently

    (-d, -d, 2d),   d=(1-epsilon)^2/18.

Dealer 0 always refreshes its unchanged high-ask shadow at t=1, giving action
probabilities (l,l,g) in both regimes. Its expected profits conditional on
rival asks 2,4,6 are respectively

    -l/8,   0,   l/4+3g/4.

Taking the dot product gives d(5l/8+3g/2), equal to the private-gain formula.
The probability of minimum ask 2 changes by -(1-l)d. Multiplying by the
accounting coefficient 1/4 gives the welfare formula. Refreshing the unchanged
rival shadow when learning is off makes its t=1 action law identical in both
regimes. At alpha=0 the same argument applies. At epsilon=1 all quotes ignore
the tables. This proves the stated nulls.

The shift can be traced on a concrete event: dealer 1 asks 6 and (V,C)=(4,6).
Dealer 0 asking 4 leaves dealer 1 unfilled with reward zero; dealer 0 asking 6
creates a half-fill and dealer-1 reward 1. Its selected shadow entry becomes
alpha and its next greedy action becomes 6. This event illustrates the path;
the full expectation above includes every event, not just this selected path.

## 4. Private versus feasible social deployment

At epsilon=1/10 and alpha=1/2, gross private gain is 1023/16000=0.0639375,
and gross welfare change is -87/8000=-0.010875, in model payoff units.
Frozen rival learning gives both contrasts exactly zero. Dealer 1's profit
and customer surplus can still change in period zero: the null is not a claim
that every participant's payoff is unchanged.

For any k_1>0, dealer 1 strictly prefers waiting, since early deployment only
charges a resource cost for an identical policy. For

    0 <= k_0 < (1-epsilon)^2(36-19epsilon)/432,

dealer 0 strictly prefers early release, while the feasible planner prefers
waiting for dealer 0. With k_0=k_1=1/20, the unique equilibrium is (early,wait)
and the unique feasible welfare maximizer is (wait,wait). The focal dealer's
net gain is 223/16000; the planner-equilibrium welfare gap is 487/8000.
Strict dominance of waiting for dealer 1 excludes other mixed equilibria;
dealer 0's strict best response to waiting then fixes its action.

At the private cost threshold dealer 0 is indifferent; above it, it waits.
At k_1=0 dealer 1 is indifferent and its pure/mixed choices are payoff-equivalent.
These degeneracies must not be omitted. Owners anticipate fixed learning rules;
learners do not optimize the entire deployment game themselves.

## 5. Counterexamples and assumption stress

For the declared grid and the narrow contrast (focal learning off, rival waiting,
rival learning on versus off), t=1 welfare interactions are positive in 88,
negative in 88, and zero in 80 of 256 states. Those counts are not probabilities
under an economically justified population distribution. This rules out a
universal direction claim over that finite grid.

Holding the selected state's other inputs fixed, small changes to the rival's
initial shadow produce the following post-hoc sensitivities:

| Rival shadow | Focal gross gain | Gross welfare change |
|---|---:|---:|
| (-0.01,-0.01,-0.01) | 0 | 0 |
| (0,0,0) | 1023/16000 | -87/8000 |
| (0.01,0.01,0.01) | 3069/32000 | -261/16000 |
| (0.01,0,-0.01) | 1539/16000 | -261/8000 |
| (-0.01,0,0.01) | 0 | 0 |

Identical initial quote laws are not identical learning states: shifting all
three shadow entries by a common c preserves their initial maximizing set, but
the chosen entry retains only (1-alpha)c after an update while unchosen entries
retain c. Thus zero reward promotes an action from a negative baseline, leaves
it tied at zero, and demotes it from a positive baseline. This explains why
matching initial actions alone is insufficient for a common-state experiment.

The theorem is not uniform around the tied zero initialization. Its independence
from positive alpha follows from sign-based tie breaking here; it is not a
general learning-rate invariance theorem. Some nearby states preserve the
effect, others eliminate it. Long-horizon persistence, trained-candidate
prevalence, smooth-policy robustness and empirical relevance are unestablished.

If V and C are independent with their original marginals, stage gross welfare
is 5/2 for every legal minimum ask. Any adaptive schedule then has expected
gross welfare (5/2)H. This null does not mean profits or learning stop changing.

## 6. Trust and contribution boundary

The reference Python evaluator and this separately implemented calculator agree
on all 16 profile/mask cells of state 140 and on 48 preselected comparison cells.
The closed forms match 16 epsilon/alpha checks, including null endpoints. Those
finite checks support the derivation; they do not prove the continuum statement.
Its proof is the sign/case analysis above and still needs human review.

Existing Lean coverage in the other worktree cannot be transferred to this new
proposition. Inspection found that `Transitions.lean` defines its transition as
the identity on a weighted list, not the economic update kernel;
`Expectation.lean` equates two summations of a supplied list, not finite economic
history enumeration; and `DeploymentGame.lean` proves an addition identity.
Those statements can be correct while leaving the economic mechanism unproved.
The zero-valued bridge fixtures are likewise not payoff certificates for this
economy. Transfer-cancellation algebra is useful but much narrower than a
formalization of the deployment game. No new formal theorem was added or
certified in this pass. **A Lean build must not be described as formal
verification of state 140, its equilibrium, or the Python economic evaluator.**

The example is consistent with strategic teaching/accommodation: the focal
dealer changes the rival's profitable experience and benefits from its subsequent
policy response. Merely giving this a learning-spillover name does not separate
it from predecessors. The literature comparison remains a required gate before
claiming a new mechanism or launching a broad confirmatory training program.

It also does **not** show that the rival's estimates become less accurate.
More favorable high-ask experience changes a subsequent policy; rival profits
can increase while customer surplus and total welfare fall. Learning-mediated
allocation effects, estimate corruption, and general learning inefficiency are
different claims. Only the first is established by this bounded example.
