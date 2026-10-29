# Economic contract: decisions, observables, and costs

## Objects that must stay separate

| Object | Definition | Information required |
|---|---|---|
| Hidden identity | Desk labels, cohort decomposition, allocations | Public aggregate responses generally do not recover these |
| Merged measure | `sum q_i eta_i delta_(1-eta_i)` | Identification is conditional on the response and plant contract |
| Stability | All closed-loop roots inside the unit disk | Positive total-margin criterion only in the positive class; signed systems need additional root restrictions |
| Infinite-horizon loss | Fixed position times bounded-flow absolute response | Initial-state and tail assumptions; signed sum is insufficient with sign changes |
| Finite-horizon loss | Absolute response through a declared H | Does not require the same infinite-tail claim |
| Account solvency | Cash, inventory, fills, margin, fees, hedges | A dynamic balance-sheet and execution contract |
| Welfare | Economic surplus net of real costs/externalities | Preferences, counterparties, resource costs and equilibrium |

## Minimal individual choice calculation

One possible *conditional* trading problem is

`max_u beta*y*u - (lambda/2)*u^2 - (gamma/2)*(I+u)^2`,

with lambda>0 and gamma>=0. Its unconstrained choice is
`u=(beta*y-gamma*I)/(lambda+gamma)`. With gamma=0 this reduces to the
paper's `q=beta/lambda` response. Constraints clip or otherwise modify the rule.
This calculation does not derive beta, the perceived continuation signal y,
market clearing, or rational-expectations consistency. Those remain economic
modeling tasks. Interpreting y as both smoothed displacement and private
fundamental value without an observation model is not justified.

## Plant and institution

The linear impact/execution schedule is a maintained local market model. Specify
who supplies liquidity, how trades clear and how execution prices produce the
account's cash flow. A price-taking dealer controls its own exposure. Venue-wide
admission can change aggregate feedback and potentially depth; the proportional
feedback intervention is an assumption, not identified by a predictive regression.
Admission that adds liquidity can make safe sets nonmonotone.

## Observation contracts

* Synthetic/audited reset: independent episodes, true displacement, known plant
  and specified observation errors. Trading access alone cannot reset a market.
* Passive public records: prices and anonymous executed flow. Fundamental value
  remains latent. EMA displacement is a proxy with mechanical persistence.
* Tagged flow: class-specific executed demand under specified reporting noise.
  Position ratios are stocks, not automatically this flow channel.
* Disclosed sensitivity: bounds on absolute response can support robust control
  even if memory is unknown; truthfulness/maintenance of the envelope matters.

Inference is about its declared target under one contract. Comparing different
contracts should price the information change rather than call it an estimator
improvement. Reset count, tap count, wall-clock horizon, executed quantity,
trading loss and survival capital are different resources.

## Decision and welfare interpretation

Worst-case safe capacity is a decision constraint. To turn it into a welfare or
optimal-disclosure theorem, specify participation value, the cost of supplying
information, who bears losses and which costs are real resource costs rather
than transfers. A synthetic probing bill versus a regulatory reporting budget
does not supply a social cost-benefit calculation.

When admission is selected using estimated risk, coverage must hold
simultaneously for the candidate actions, or selection must otherwise be
accounted for. Pointwise coverage for a fixed action does not automatically
protect a data-selected counterfactual policy. Agents changing their signal or
response after admission can change the observation law.
