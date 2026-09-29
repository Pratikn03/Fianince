"""Build, audit, independently compare, and save a create-only verification run."""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tempfile
import time

from .verification import compare_fixture, parse_axioms, write_new

APPROVED_DOSSIER_SEAL = "4421b8aed40305317b205811e45c555f93622d84dbc305e068783c3bbaff4a6b"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_hashes(root, expected):
    mismatches = [name for name, sha in expected.items()
                  if not (root/name).is_file() or digest(root/name) != sha]
    return {"passed": not mismatches, "checked": len(expected), "mismatches": mismatches}


def validate_dossier(root):
    if not (root/"manifest.json").is_file() or digest(root/"manifest.json") != APPROVED_DOSSIER_SEAL:
        return {"passed": False, "reason": "not the approved sealed dossier manifest"}
    manifest = json.loads((root/"manifest.json").read_text())
    if manifest.get("schema") != 1 or not {"exact_audit.py", "verified/witness_results.json"}.issubset(manifest.get("files_sha256", {})):
        return {"passed": False, "reason": "incomplete dossier schema/inventory"}
    return check_hashes(root, manifest["files_sha256"])


def source_inventory(project):
    paths = [p for p in project.rglob("*.lean") if ".lake" not in p.relative_to(project).parts]
    paths += list(project.glob("*.py"))
    paths += [project/name for name in ("lean-toolchain", "lakefile.toml", "lake-manifest.json")]
    return {str(p.relative_to(project)): digest(p) for p in sorted(paths)}


def validate_executed_copy(original, executed, expected):
    return {"passed": check_hashes(original, expected)["passed"] and check_hashes(executed, expected)["passed"],
            "original": check_hashes(original, expected), "executed": check_hashes(executed, expected)}


def audit_environment(lake, root, log):
    raw = checked_process([str(lake), "env", "lean", "AxiomAudit.lean"], root, log)
    lines = [line for line in raw.splitlines() if line.strip()]
    if len(lines) != 1 or not lines[0].startswith("MM_AUDIT "):
        return {"passed": False, "errors": ["missing, truncated, or unexpected environment audit output"]}
    payload = json.loads(lines[0][len("MM_AUDIT "):])
    rows = payload["declarations"]
    names = [row["name"] for row in rows]
    text = "\n".join(f"'{row['name']}' depends on axioms: [{', '.join(row['axioms'])}]" for row in rows)
    result = parse_axioms(text, names)
    result["inventory_method"] = "Lean elaborated environment by local source module"
    result["modules"] = payload["modules"]
    result["theorem_count"] = sum(row["kind"] == "theorem" for row in rows)
    if any(row["kind"] == "axiom" for row in rows):
        result["passed"] = False
        result["errors"].append("custom local axiom declared")
    return result


def checked_process(command, cwd, log):
    result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=300,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    with Path(log).open("x") as stream:
        stream.write(result.stdout)
    if result.returncode:
        raise RuntimeError(f"exit {result.returncode}: {command}; see {log}")
    return result.stdout


def verify(output, lake, dossier, clean=False):
    project = Path(__file__).resolve().parent
    output.mkdir(parents=True, exist_ok=False)
    report = {"passed": False, "bridge_kind": "tested_agreement", "clean_build": clean,
              "python": platform.python_version(), "independent_human_review": False,
              "continuum_theorem_formalized": False, "training_performed": False}
    started = time.monotonic()
    try:
        report["dossier_integrity"] = validate_dossier(dossier)
        if not report["dossier_integrity"]["passed"]:
            raise RuntimeError("sealed dossier changed; comparison withheld")
        report["sources_sha256"] = source_inventory(project)
        sources = [project/name for name in report["sources_sha256"]]
        report["dossier_manifest_sha256"] = digest(dossier/"manifest.json")
        report["python_reference_sha256"] = digest(dossier/"exact_audit.py")
        report["lake_sha256"] = digest(lake)
        report["lean_sha256"] = digest(lake.parent/"lean")
        root = project
        if clean:
            root = Path(tempfile.mkdtemp(prefix="machine-markets-formal-"))
            for path in sources:
                destination = root/path.relative_to(project)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination)
            report["clean_copy_path"] = str(root)
        def assert_sources():
            bound = validate_executed_copy(project, root, report["sources_sha256"])
            if (not bound["passed"] or source_inventory(root) != report["sources_sha256"]
                    or source_inventory(project) != report["sources_sha256"]):
                raise RuntimeError("original or executed source inventory/hash changed")
        assert_sources()
        report["toolchain"] = checked_process([str(lake), "env", "lean", "--version"], root, output/"toolchain.txt").strip()
        checked_process([str(lake), "build"], root, output/"build.txt")
        assert_sources()
        report["axiom_audit"] = audit_environment(lake, root, output/"axioms.txt")
        if not report["axiom_audit"]["passed"]:
            raise RuntimeError("incomplete or disallowed axiom closure")
        checked_process([str(lake), "env", "leanchecker", "--verbose", "Mechanism"], root, output/"kernel_replay.txt")
        assert_sources()
        raw = checked_process([str(lake), "env", "lean", "--run", "Export.lean"], root, output/"export.txt")
        assert_sources()
        actual = json.loads(raw)
        write_new(output/"lean_fixture.json", actual)
        spec = importlib.util.spec_from_file_location("mechanism_reference", dossier/"exact_audit.py")
        ref = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ref)
        s = ref.STATES[140]
        contract = {"model": "v0.12-state140-H2", "epsilon": "1/10", "alpha": "1/2",
                    "asks": ["2","4","6"], "state": [[str(x) for x in q] for q in s],
                    "atoms": [[str(p),str(v),str(c)] for p,v,c in ref.atoms()],
                    "refresh": "both-before-period-1-including-frozen-shadows", "costs": ["0","0"]}
        def cells(costs):
            return [{"profile": list(p), "mask": list(m), "total": list(map(str,
                     ref.evaluate(s[:2], s[2:], p,m,costs=costs)["total"]))}
                    for p in ref.PAIRS for m in (ref.PAIRS if costs == (F(0),F(0)) else [(False,True)])]
        expected = {"contract": contract, "cells": cells((F(0),F(0)))}
        report["zero_cost_bridge"] = compare_fixture(actual, expected)
        costs_contract = {**contract, "costs": ["1/20","1/20"]}
        report["costly_bridge"] = compare_fixture(
            {"contract": costs_contract, "cells": actual["costly_cells"]},
            {"contract": costs_contract, "cells": cells((F(1,20),F(1,20)))})
        settlement_expected = [{"quotes": [str(a),str(b)], "value": str(v), "customer": str(c),
                                "total": list(map(str, ref.settlement((a,b),v,c)))}
                               for a in ref.ASKS for b in ref.ASKS for _,v,c in ref.atoms()]
        report["settlement_bridge"] = {"passed": actual["settlements"] == settlement_expected,
                                       "compared": len(settlement_expected)}
        report["compared_payoff_cells"] = len(expected["cells"])+4
        write_new(output/"python_fixture.json", {**expected, "costly_cells": cells((F(1,20),F(1,20))),
                                              "settlements": settlement_expected})
        if not all(report[k]["passed"] for k in ("zero_cost_bridge", "costly_bridge", "settlement_bridge")):
            raise RuntimeError("economic bridge mismatch")
        assert_sources()
        if not validate_dossier(dossier)["passed"]:
            raise RuntimeError("reference dossier changed during verification")
        report["passed"] = True
    except Exception as exc:
        report["failure"] = f"{type(exc).__name__}: {exc}"
    report["elapsed_seconds"] = time.monotonic()-started
    write_new(output/"report.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--lake", type=Path, required=True)
    parser.add_argument("--dossier", type=Path, default=Path(__file__).resolve().parent.parent/"mechanism_dossier_20260926")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    report = verify(args.output.resolve(), args.lake.resolve(), args.dossier.resolve(), args.clean)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
