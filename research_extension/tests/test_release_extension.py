import json
from pathlib import Path

from research_extension.release_extension import build_evidence_manifest, gate_status


def test_evidence_manifest_excludes_its_own_output(tmp_path: Path):
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    (tmp_path / "b.json").write_text('{"ok": true}', encoding="utf-8")
    manifest = build_evidence_manifest(tmp_path, exclude_prefixes=("outputs/",))
    assert manifest["file_count"] == 2
    assert manifest["files"][0]["path"] == "a.txt"
    assert manifest["files"][0]["sha256"]


def test_gate_status_keeps_external_gates_pending():
    status = gate_status()
    assert status["external_replication"]["status"] == "pending"
    assert status["crypto_calibration"]["status"] == "pending"
    assert status["local_runtime_audit"]["status"] == "implemented"
    assert all("acceptance" in value for value in status.values())
