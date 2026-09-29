"""Fail-closed checks: corrupted numbers, missing cases, and unproved axioms."""
import copy
import json
from pathlib import Path

import pytest

from .verification import compare_fixture, parse_axioms, write_new


def fixture():
    # One compact synthetic bridge fixture tests the validator, not the economy.
    return {"contract": "test", "cells": [
        {"profile": [False, False], "mask": [False, True],
         "total": ["1/2", "1/3", "1/6", "1", "1"]}]}


def test_exact_rational_bridge_accepts_equal_numbers():
    left, right = fixture(), fixture()
    right["cells"][0]["total"][0] = "2/4"
    assert compare_fixture(left, right)["passed"]


def test_bridge_rejects_wrong_payoff_and_input():
    for field in ("total", "mask"):
        bad = copy.deepcopy(fixture())
        bad["cells"][0][field][0] = "2/3" if field == "total" else True
        assert not compare_fixture(bad, fixture())["passed"]
    bad = fixture()
    bad["contract"] = "different"
    assert not compare_fixture(bad, fixture())["passed"]


def test_bridge_rejects_missing_duplicate_and_float_cells():
    for cells in ([], fixture()["cells"] * 2):
        assert not compare_fixture({"contract": "test", "cells": cells}, fixture())["passed"]
    bad = fixture()
    bad["cells"][0]["total"][0] = 0.5
    assert not compare_fixture(bad, fixture())["passed"]


def test_axioms_require_complete_allowed_closure():
    good = "'Mechanism.a' does not depend on any axioms\n'Mechanism.b' depends on axioms: [propext, Quot.sound]\n"
    assert parse_axioms(good, ["Mechanism.a", "Mechanism.b"])["passed"]
    for forbidden in ("sorryAx", "Lean.ofReduceBool", "unprovedEconomicClaim"):
        text = f"'Mechanism.a' depends on axioms: [{forbidden}]\n"
        assert not parse_axioms(text, ["Mechanism.a"])["passed"]
    assert not parse_axioms(good, ["Mechanism.a", "Mechanism.b", "Mechanism.missing"])["passed"]
    assert not parse_axioms(good, ["Mechanism.a"])["passed"]
    assert not parse_axioms(good + "error: truncated proof\n", ["Mechanism.a", "Mechanism.b"])["passed"]
    assert not parse_axioms("", ["Mechanism.a"])["passed"]


def test_outputs_refuse_overwrite(tmp_path):
    target = tmp_path / "result.json"
    write_new(target, {"one": 1})
    with pytest.raises(FileExistsError):
        write_new(target, {"one": 2})
    assert json.loads(target.read_text()) == {"one": 1}


def test_checked_process_preserves_failure_and_blocks_acceptance(tmp_path):
    import sys
    from .run_verify import checked_process
    with pytest.raises(RuntimeError):
        checked_process([sys.executable, "-c", "print('deliberate failure'); raise SystemExit(7)"],
                        tmp_path, tmp_path / "failed.txt")
    assert "deliberate failure" in (tmp_path / "failed.txt").read_text()


def test_manifest_detects_missing_and_modified_input(tmp_path):
    from .run_verify import check_hashes
    p = tmp_path / "input.txt"
    p.write_text("altered")
    assert not check_hashes(tmp_path, {"input.txt": "0" * 64})["passed"]
    assert not check_hashes(tmp_path, {"missing.txt": "0" * 64})["passed"]


def test_empty_dossier_manifest_is_not_a_seal(tmp_path):
    from .run_verify import validate_dossier
    (tmp_path / "manifest.json").write_text('{"files_sha256": {}}')
    assert not validate_dossier(tmp_path)["passed"]


def test_executed_copy_must_match_source_inventory(tmp_path):
    from .run_verify import validate_executed_copy
    original, executed = tmp_path/"original", tmp_path/"executed"
    original.mkdir()
    executed.mkdir()
    for root in (original, executed):
        (root/"Export.lean").write_text("real exporter")
    import hashlib
    expected = {"Export.lean": hashlib.sha256(b"real exporter").hexdigest()}
    (executed/"Export.lean").write_text("saved fixture exporter")
    assert not validate_executed_copy(original, executed, expected)["passed"]


def test_environment_audit_catches_indented_foreign_namespace_theorem(tmp_path):
    """Real Lean regression: textual theorem scans missed this declaration."""
    import shutil
    from .run_verify import audit_environment, checked_process
    lake = Path.home()/".elan/toolchains/leanprover--lean4---v4.29.1/bin/lake"
    if not lake.is_file():
        pytest.skip("Pinned Lean 4.29.1 is not installed; no automatic download")
    source = Path(__file__).parent
    for name in ("lakefile.toml", "lean-toolchain", "AxiomAudit.lean"):
        shutil.copy2(source/name, tmp_path/name)
    (tmp_path/"Mechanism.lean").write_text(
        "namespace Outside\naxiom unproved : False\n  theorem concealed : False := unproved\nend Outside\n")
    checked_process([str(lake), "build"], tmp_path, tmp_path/"build.txt")
    result = audit_environment(lake, tmp_path, tmp_path/"audit.txt")
    assert not result["passed"]
    assert any("Outside.unproved" in str(x) for x in result["errors"])
