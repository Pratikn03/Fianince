"""Separate rational H1/H2 calculation of the approved v0.12 economy.

This checker imports no project settlement, policy, transition, or game code.
Only compare_reference() imports the old evaluator, after computing independent
answers. This is differential checking by the same research team, not external
replication. Terminal-period integration is cached by its complete action law;
no learning states are merged before the final payoff period.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from functools import cache
import hashlib
from itertools import product
import json
from pathlib import Path
import platform
import subprocess
import sys

ASKS = (F(2), F(4), F(6))
PAIRS = tuple(product((False, True), repeat=2))
TABLES = ((F(0), F(0), F(0)), (F(1), F(0), F(0)),
          (F(0), F(1), F(0)), (F(0), F(0), F(1)))
STATES = tuple(product(TABLES, repeat=4))


def atoms(law="default"):
    if law == "default":
        return tuple((p/2, v, v+z) for v in (F(0), F(4))
                     for z, p in ((F(-2), F(1, 4)), (F(2), F(1, 2)), (F(6), F(1, 4))))
    if law == "independent":
        return tuple((p/2, v, c) for v in (F(0), F(4)) for c, p in
                     ((F(-2), F(1, 8)), (F(2), F(3, 8)), (F(6), F(3, 8)), (F(10), F(1, 8))))
    raise ValueError("unknown economic law")


def settlement(quotes, value, customer):
    """Return (profit0, profit1, customer surplus, welfare, total units)."""
    best = min(quotes)
    if customer < best:
        return (F(0),)*5
    winners = [i for i in range(2) if quotes[i] == best]
    profits = tuple((best-value)/len(winners) if i in winners else F(0) for i in range(2))
    return (*profits, customer-best, customer-value, F(1))


@cache
def stage(quotes, law="default"):
    values = [F(0)]*5
    for p, v, c in atoms(law):
        row = settlement(quotes, v, c)
        for i in range(5):
            values[i] += p*row[i]
    return tuple(values)


def policy(table, epsilon):
    if len(table) != 3 or any(not isinstance(q, F) for q in table):
        raise TypeError("three rational table entries required")
    if not isinstance(epsilon, F):
        raise TypeError("epsilon must be rational")
    if not 0 <= epsilon <= 1:
        raise ValueError("epsilon outside [0,1]")
    return _policy_cached(table, epsilon)


@cache
def _policy_cached(table, epsilon):
    n = table.count(max(table))
    return tuple(epsilon/3 + ((1-epsilon)/n if q == max(table) else F(0)) for q in table)


@cache
def _last_period(laws, law):
    result = [F(0)]*5
    for a, b in product(range(3), repeat=2):
        weight = laws[0][a]*laws[1][b]
        cell = stage((ASKS[a], ASKS[b]), law)
        for j in range(5):
            result[j] += weight*cell[j]
    p, q = laws[0][0], laws[1][0]
    return tuple(result), p+q-p*q


def evaluate(active, shadow, profile, mask, *, horizon=2, costs=(F(0), F(0)),
             epsilon=F(1, 10), alpha=F(1, 2), law="default"):
    if type(horizon) is not int or horizon not in (1, 2):
        raise ValueError("checker supports only H=1 or H=2")
    for pair in (profile, mask):
        if not isinstance(pair, tuple) or len(pair) != 2 or any(type(x) is not bool for x in pair):
            raise TypeError("profile and mask must be boolean pairs")
    if len(active) != 2 or len(shadow) != 2 or len(costs) != 2:
        raise ValueError("two dealers required")
    if any(not isinstance(x, F) for x in (*costs, epsilon, alpha)):
        raise TypeError("all economic numeric inputs must be rational")
    if any(x < 0 for x in costs) or not 0 <= alpha <= 1:
        raise ValueError("negative costs or invalid alpha")
    for table in (*active, *shadow):
        policy(table, epsilon)
    initial = tuple(shadow[i] if profile[i] else active[i] for i in range(2))
    laws = tuple(policy(q, epsilon) for q in initial)
    first, first_low = _last_period(laws, law)
    periods, exposure = [first], [first_low]
    if horizon == 2:
        later = [F(0)]*5
        later_low = F(0)
        for a, b in product(range(3), repeat=2):
            action_mass = laws[0][a]*laws[1][b]
            if not action_mass:
                continue
            for p, v, c in atoms(law):
                reward = settlement((ASKS[a], ASKS[b]), v, c)
                updated = [list(q) for q in shadow]
                for i, action in enumerate((a, b)):
                    if mask[i]:
                        updated[i][action] = (1-alpha)*updated[i][action]+alpha*reward[i]
                next_laws = tuple(policy(tuple(q), epsilon) for q in updated)
                terminal, low = _last_period(next_laws, law)
                for j in range(5):
                    later[j] += action_mass*p*terminal[j]
                later_low += action_mass*p*low
        periods.append(tuple(later))
        exposure.append(later_low)
    total = [sum(period[j] for period in periods) for j in range(5)]
    charged = tuple(costs[i]*profile[i] for i in range(2))
    total[0] -= charged[0]
    total[1] -= charged[1]
    total[3] -= sum(charged)
    assert sum(total[:3]) == total[3]
    return {"total": tuple(total), "periods": tuple(periods),
            "minimum_ask2": tuple(exposure), "costs_charged": charged}


def write_new_json(path, data):
    def encode(value):
        if isinstance(value, F):
            return str(value)
        raise TypeError(f"cannot serialize {type(value)}")
    with Path(path).open("x") as handle:
        json.dump(data, handle, default=encode, indent=2, sort_keys=True)
        handle.write("\n")


def build_grid():
    """Every approved stipulated state; no search for a favorable trained policy."""
    records, counts = [], Counter()
    for state_id, state in enumerate(STATES):
        cells = {}
        for profile, mask in product(PAIRS, repeat=2):
            cells[profile, mask] = evaluate(state[:2], state[2:], profile, mask)
        # Prespecified audit contrast: dealer 0 release, rival waits, own learning
        # off; interaction switches only rival learning. t=1 removes direct t=0.
        def delta(mask, field=3):
            return (cells[(True, False), mask]["periods"][1][field]
                    - cells[(False, False), mask]["periods"][1][field])
        interaction = delta((False, True))-delta((False, False))
        sign = "positive" if interaction > 0 else "negative" if interaction < 0 else "zero"
        counts[sign] += 1
        record = {"state_id": state_id, "state": state,
                  "rival_learning_welfare_interaction_t1": interaction,
                  "cells": [{"profile": p, "mask": m, **cells[p, m]}
                            for p, m in product(PAIRS, repeat=2)]}
        records.append(record)
    return {"states": len(STATES), "cells": len(STATES)*16,
            "status": "exploratory_exact_audit_not_confirmatory",
            "replication_unit": "stipulated state, not a trained population",
            "primary_audit_interaction_signs": dict(counts), "records": records}


def compare_reference(root, records):
    """Check all profile/mask cells of three preselected cases, not a proof."""
    root = Path(root).resolve()
    sys.path.insert(0, str(root))
    from studies.learning_spillovers_v12.exact import evaluate as old_evaluate
    from studies.learning_spillovers_v12.model import default_economy, State, Budget
    import studies.learning_spillovers_v12.exact as old_module
    if not Path(old_module.__file__).resolve().is_relative_to(root):
        raise RuntimeError("reference import resolved outside the declared checkout")
    mismatches, compared = [], 0
    for state_id in (0, 108, 175):
        state = STATES[state_id]
        for cell in records[state_id]["cells"]:
            old = old_evaluate(default_economy(), State(state[:2], state[2:], 0),
                               cell["profile"], cell["mask"], (F(0), F(0)), 2, Budget())
            if old.status != "complete":
                raise RuntimeError(f"reference unresolved: {state_id}: {old}")
            p = old.payoff
            answer = (*p.net, p.customer_surplus, p.welfare, p.trade)
            compared += 1
            if answer != cell["total"]:
                mismatches.append({"state_id": state_id, "profile": cell["profile"],
                                   "mask": cell["mask"], "reference": answer,
                                   "independent": cell["total"]})
    files = sorted((root/"studies/learning_spillovers_v12").glob("*.py"))
    files += [root/"studies/learning_spillovers_v12/PROTOCOL.md"]
    return {"root": str(root), "state_ids": [0, 108, 175], "compared": compared,
            "mismatches": mismatches, "passed": not mismatches,
            "commit": subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
            "source_sha256": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference-root", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    grid = build_grid()
    grid["checker_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    grid["python"] = platform.python_version()
    grid["reference_comparison"] = (compare_reference(args.reference_root, grid["records"])
                                    if args.reference_root else {"status": "not_run"})
    write_new_json(args.output, grid)
    print(json.dumps({k: v for k, v in grid.items() if k not in ("records", "reference_comparison")}))
    print(json.dumps({k: v for k, v in grid["reference_comparison"].items() if k != "source_sha256"}, default=str))
    if grid["reference_comparison"].get("passed") is False:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
