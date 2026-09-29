"""Post-hoc case 140: exact predictions, costs, and unfavorable sensitivities.

The case was selected after inspecting the complete stipulated-state grid.
It is not confirmatory evidence, a trained population, or a novelty certificate.
"""
import argparse
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from pathlib import Path

from .exact_audit import STATES, PAIRS, evaluate, write_new_json


def prediction(epsilon, alpha):
    """Gross own-profit and welfare release contrasts of the proved special case."""
    if any(not isinstance(x, F) for x in (epsilon, alpha)):
        raise TypeError("rational parameters required")
    if not 0 <= epsilon <= 1 or not 0 <= alpha <= 1:
        raise ValueError("parameter outside [0,1]")
    if alpha == 0:
        return F(0), F(0)
    return ((1-epsilon)**2*(36-19*epsilon)/432,
            -(1-epsilon/3)*(1-epsilon)**2/72)


def witness_report():
    state = STATES[140]
    records = []
    for profile, mask in product(PAIRS, repeat=2):
        records.append({"profile": profile, "mask": mask,
                        **evaluate(state[:2], state[2:], profile, mask)})
    failures = []
    for epsilon, alpha in product((F(0), F(1, 10), F(1, 2), F(1)),
                                  (F(0), F(1, 100), F(1, 2), F(1))):
        a, b = [evaluate(state[:2], state[2:], (early, False), (False, True),
                         epsilon=epsilon, alpha=alpha)["total"] for early in (False, True)]
        got = b[0]-a[0], b[3]-a[3]
        if got != prediction(epsilon, alpha):
            failures.append({"epsilon": epsilon, "alpha": alpha, "got": got})
    costs = F(1, 20), F(1, 20)
    game = {p: evaluate(state[:2], state[2:], p, (False, True), costs=costs)["total"] for p in PAIRS}
    pure = [p for p in PAIRS if all(game[p][i] >= game[tuple(not p[j] if j == i else p[j] for j in range(2))][i]
                                    for i in range(2))]
    best_welfare = max(cell[3] for cell in game.values())
    planner = [p for p in PAIRS if game[p][3] == best_welfare]
    # Dealer 1's active and candidate tables are identical, and costs never
    # enter reward updates: its early choice loses k1 under either rival choice.
    rival_gains = [game[(p, True)][1]-game[(p, False)][1] for p in (False, True)]
    sensitivity = []
    for q in ((F(-1, 100),)*3, (F(0),)*3, (F(1, 100),)*3,
              (F(1, 100), F(0), F(-1, 100)), (F(-1, 100), F(0), F(1, 100))):
        outputs = [evaluate(state[:2], (state[2], q), (e, False), (False, True))["total"]
                   for e in (False, True)]
        sensitivity.append({"rival_shadow": q, "gross_delta_own_welfare":
                            (outputs[1][0]-outputs[0][0], outputs[1][3]-outputs[0][3])})
    return {"status": "posthoc_exact_witness_not_novelty_or_confirmation", "state_id": 140,
            "state": state, "zero_cost_cells": records,
            "formula_checks": 16, "formula_failures": failures,
            "costly_game": {"costs": costs, "learning_mask": (False, True),
                            "cells": [{"profile": p, "total": game[p]} for p in PAIRS],
                            "pure_equilibria": pure, "planner_profiles": planner,
                            "rival_early_gains": rival_gains,
                            "welfare_gap": game[(False, False)][3]-game[(True, False)][3],
                            "focal_net_gain": game[(True, False)][0]-game[(False, False)][0],
                            "no_other_mixed_equilibrium_reason": "rival strictly prefers wait, focal strictly prefers early against wait"},
            "initial_shadow_sensitivity": sensitivity}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference-root", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    report = witness_report()
    report["checker_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if args.reference_root:
        # Reuse import checks/provenance for declared bridge fixtures, then
        # explicitly compare the newly selected case, all profiles and masks.
        import sys
        sys.path.insert(0, str(args.reference_root.resolve()))
        from studies.learning_spillovers_v12.exact import evaluate as old_evaluate
        from studies.learning_spillovers_v12.model import default_economy, State, Budget
        import studies.learning_spillovers_v12.exact as old_module
        if not Path(old_module.__file__).resolve().is_relative_to(args.reference_root.resolve()):
            raise RuntimeError("reference path mismatch")
        failures = []
        state = STATES[140]
        for cell in report["zero_cost_cells"]:
            answer = old_evaluate(default_economy(), State(state[:2], state[2:], 0),
                                  cell["profile"], cell["mask"], (F(0), F(0)), 2, Budget())
            if answer.status != "complete":
                raise RuntimeError(answer)
            p = answer.payoff
            if (*p.net, p.customer_surplus, p.welfare, p.trade) != cell["total"]:
                failures.append({"profile": cell["profile"], "mask": cell["mask"]})
        report["reference_comparison"] = {"root": str(args.reference_root.resolve()),
                                           "compared": 16, "failures": failures}
    else:
        report["reference_comparison"] = {"status": "not_run"}
    write_new_json(args.output, report)
    print(json.dumps({"formula_checks": report["formula_checks"],
                      "formula_failures": report["formula_failures"],
                      "costly_game": report["costly_game"],
                      "reference_comparison": report["reference_comparison"]}, default=str))
    if report["formula_failures"] or report["reference_comparison"].get("failures"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
