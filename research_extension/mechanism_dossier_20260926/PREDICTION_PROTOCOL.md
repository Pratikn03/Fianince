# Locked predictions; production-training gate remains closed

Version: mechanism-dossier-predictions-v1. Local record, not external
preregistration or an immutable third-party timestamp. Its exact bytes and
associated source hashes are recorded in the dossier manifest. Changes require
a new version; old records are retained.

## What is and is not locked

The exact state-140 predictions, nulls, observation contract, proposed numerical
validation design and rejection rules below are fixed before any **new sampled
validation under this protocol**. The state and predictions were discovered
post hoc in a fully inspected finite development grid. A later Monte Carlo match
is a numerical implementation check, not confirmation of a novel economic
mechanism or evidence about independent trained populations.

No new training or sampled validation was performed in this dossier. The wider
trained-population study is BLOCKED pending the novelty comparison, a reviewed
candidate-generation process and a separate powered population protocol.

## Numerical validation contract

- Model: `PROOF_AUDIT.md`, state 140, H=2, alpha=1/2, epsilon=1/10, zero costs.
- Arms: all four initial deployment profiles crossed with all four shadow masks.
- Primary estimand: t=1 gross welfare, dealer 0 early minus wait, rival waiting,
  focal learning OFF and rival learning ON. Expected value: -87/8000.
- Necessary null: same contrast with rival learning OFF equals zero. Their
  difference is a controlled intervention interaction, not natural mediation.
- Supporting predictions: gross focal total-profit gain 1023/16000; first-period
  welfare and focal-profit contrasts zero; changes in minimum-ask-2 probability
  account for welfare. Customer and rival payoffs remain separately reported.
- Complete common initial state; identical candidate tables in every branch.
- Pair exogenous customer draws and independent uniform quote channels across
  arms. Do not force endogenous quotes, rewards or shadow tables to match.
- Within each trajectory use independent quote uniforms for each dealer and
  independent current V and Z channels. Use inverse-CDF sampling in increasing
  ask order. The same inputs drive each arm; new trajectories are independent.
- Initial release costs never enter the shadow reward. No oracle information
  enters a learner. Record actions, fills, rewards, table updates and refreshes.
- Seed namespace: `mechanism-dossier-v1/numerical-validation`. For each of the
  four channel names `dealer0`, `dealer1`, `V`, `Z`, set the Python 3.11
  `random.Random` seed to the integer represented by the full SHA-256 digest of
  UTF-8 `namespace + ":" + channel`. In trajectory-major, then period-major
  order, consume one `randrange(60)` per dealer, one `randrange(2)` for V,
  and one `randrange(4)` for Z, regardless of treatment or realized trade.
  Dealer integers choose the first increasing-ask CDF strictly above integer/60;
  every possible policy probability at epsilon=1/10 is representable on that
  grid. Map V integers to 0,4 and Z integers to -2,2,2,6. Reuse these inputs
  in every arm. Record the precise runtime version. This namespace has not been
  executed in this pass; historical global seed uniqueness is not asserted.
  IID guarantees below concern the ideal sampling model; a deterministic
  pseudorandom implementation is not itself a proof of independence.

### Sample size and uncertainty for this finite fixture only

The paired t=1 welfare difference Y lies in [-2,2]. Why: with the same V,C draw,
the two arms can differ in trade only for C=2, because asks are 2,4,6 and C is
in {-2,2,6,10}. At C=2, C-V is either 2 or -2. Therefore a two-sided 95%
Hoeffding interval for E[Y] has half-width

    r_N = sqrt(8 log(40) / N).

Fix N=1,000,000 independent paired trajectories, no optional stopping. Then
r_N is approximately 0.0054324, less than half 87/8000. Under the stated IID
contract, this also implies at least 95% probability that the interval is
strictly negative when the exact benchmark mean is correct. This deliberately
conservative computational-check design is not a power calculation for learned
populations. It is **specified, not run**. If resources are insufficient, do not
silently reduce N and retain the same precision claim.

Other arm means and mechanism diagnostics are secondary descriptive checks,
not a family of individually unadjusted confirmatory significance claims.
Finite exact arithmetic remains the primary benchmark, requiring no confidence
interval. Reusing this already discovered example provides no novelty evidence.

## Rejection and failure rules

1. Exact independent enumeration disagrees with the algebra: suspend the result
   and investigate the derivation/implementation; never average the discrepancy.
2. State/cost/accounting/refresh or observer-isolation checks fail: invalidate
   the affected run. Save logs and counts; do not drop failed trajectories.
3. Frozen-rival, alpha-zero, identical-policy or uniform-exploration controls
   produce an exact nonzero matched gross release contrast: the asserted pathway
   or implementation is wrong under this contract.
4. A Monte Carlo interval excludes its exact expected value: report the
   discrepancy and investigate. A single 95% failure is possible by chance and
   alone does not disprove a mathematically established identity. Do not rerun
   until a favorable sample appears.
5. An effect appears only through the deployment cost: report a resource-cost
   wedge, not a learning mechanism. Retain zero-cost allocation contrasts.
6. A broader claim that early deployment always harms welfare is already
   rejected by the inspected sign-reversal grid; do not test it as if unresolved.
7. Prior work already establishes an equivalent mechanism under corresponding
   assumptions: withdraw novelty wording. A correct special case is still useful
   as a transparent benchmark, not a field-defining discovery.

## Separate trained-population protocol: not yet approved or locked

Before training, specify a candidate-generation procedure that does not select
on joint-deployment harm; train common snapshots then clone complete states;
cross fixed-candidate and continued-learning conditions; include non-tied
initializations and a second economically justified learning rule; retain
unfavorable outcomes. Independently trained populations are the uncertainty unit.

The human-reviewed proposal must lock one economically meaningful welfare
effect size, training/evaluation horizons and information, a development-only
variance pilot, a 90%-power calculation, multiplicity policy, resource budget,
untouched evaluation seeds and reporting of all failures. The current finite
example supplies neither that variance nor a representative distribution of
trained states. Those fields are deliberately not fabricated or labeled complete.
