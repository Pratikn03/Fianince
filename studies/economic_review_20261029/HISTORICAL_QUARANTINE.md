# Historical claims that are not current evidence

The original files are retained for provenance. This note does not claim that
every assertion in every historical version has been audited.

* `simulations/tri_simulator_validation.py` increments `lp_certified_count` when
  `expected_stable` is true. That counting step does not solve a recurrence LP.
  Its coverage/invariance summary cannot establish universal engine-invariant
  stability or probability-one decisiveness. Conservation alone is insufficient.
* The older integrated manuscript's numeric predatory-profit scenario does not
  establish subgame-perfect equilibrium without a specified game and proof of
  sequential optimality.
* A finite set of throttle scenarios, with a special-cased parameter in
  `simulations/welfare_pareto_frontier.py`, does not prove global Pareto optimality.
* The claimed maximal Kreiss/Lyapunov ellipsoid is not generally maximal: for
  J=0.5I, P=(4/3)I, K=1, the proposed radius is sqrt(3/4)B while the maximal safe
  Euclidean ball has radius B. A conservative sufficient region may survive.
* Original `R_P2_step2_theory.json` records conservative admission 0.24 and zero
  observed breaches. Those observations do not establish maximality or an exact
  capacity cost of 0.06. Use the separately named repaired result for current work.

Existing PDFs are snapshots. Corrected modular sources and the new revision note
govern this branch. A revised statement does not inherit semantic Lean coverage
merely because its label is unchanged.
