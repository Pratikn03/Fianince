"""Strict rational bridge and proof-dependency checks, not a Python refinement proof."""
from fractions import Fraction
import json
from pathlib import Path
import re


def write_new(path, data):
    with Path(path).open("x") as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write("\n")


def compare_fixture(actual, expected):
    errors = []
    if actual.get("contract") != expected.get("contract"):
        errors.append("input contract differs")

    def index(data):
        rows = {}
        for cell in data["cells"]:
            profile, mask = cell["profile"], cell["mask"]
            if len(profile) != 2 or len(mask) != 2 or any(type(x) is not bool for x in profile + mask):
                raise ValueError("invalid profile/mask")
            key = tuple(profile), tuple(mask)
            if key in rows:
                raise ValueError("duplicate cell")
            values = cell["total"]
            if len(values) != 5 or any(type(x) is not str for x in values):
                raise ValueError("five rational strings required")
            rows[key] = tuple(Fraction(x) for x in values)
        return rows

    try:
        left, right = index(actual), index(expected)
        if not right or left.keys() != right.keys():
            errors.append("missing/extra cells")
        for key in left.keys() & right.keys():
            if left[key] != right[key]:
                errors.append(f"payoff mismatch {key}")
    except (ValueError, TypeError, KeyError, ZeroDivisionError) as exc:
        errors.append(str(exc))
    return {"passed": not errors, "errors": errors, "bridge_kind": "tested_agreement"}


def parse_axioms(log, expected):
    allowed = {"propext", "Classical.choice", "Quot.sound"}
    pattern = re.compile(r"^'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])$")
    found, errors = {}, []
    for line in log.splitlines():
        if not line.strip():
            continue
        match = pattern.fullmatch(line.strip())
        if not match:
            errors.append(f"unparsed diagnostic: {line}")
            continue
        name, raw = match.groups()
        if name in found:
            errors.append(f"duplicate declaration {name}")
        axioms = set(x.strip() for x in (raw or "").split(",") if x.strip())
        found[name] = sorted(axioms)
        if axioms - allowed:
            errors.append(f"forbidden axioms: {name}: {sorted(axioms-allowed)}")
    if set(found) != set(expected) or len(expected) != len(set(expected)) or not expected:
        errors.append("missing, unlisted, duplicate, or empty theorem inventory")
    return {"passed": not errors, "errors": errors, "declarations": found,
            "allowed_axioms": sorted(allowed)}
