"""Hardware evidence must distinguish source availability from physical measurements."""
import hashlib
import json
from unittest.mock import patch

from agentic_guard.hardware import run_vivado_synthesis_audit as audit


def test_rtl_and_tcl_sources_exist():
    assert "module amip_fpga_pipeline" in audit.RTL_FILE.read_text()
    assert "report_timing_summary" in audit.TCL_FILE.read_text()


def test_missing_vivado_never_fabricates_measurements(tmp_path):
    with patch.object(audit.shutil, "which", return_value=None), \
         patch.object(audit, "OUTPUT_FILE", tmp_path / "primary.json"), \
         patch.object(audit, "SECONDARY_FILE", tmp_path / "secondary.json"):
        result = audit.run_vivado_silicon_audit(run_live=True)
    assert result["status"] == "NOT_MEASURED" and result["measurements_verified"] is False
    report = result["post_route_synthesis_report"]
    assert report["pipeline_timing"]["timing_constraints_met"] is None
    assert report["pipeline_timing"]["deterministic_latency_ns"] is None
    assert report["resource_utilization"] is None and report["power_analysis_watts"] is None
    assert report["audit_metadata"]["live_vivado_executed"] is False
    assert report["audit_metadata"]["wire_speed_hft_sla_compliance"] is None
    assert json.loads((tmp_path / "primary.json").read_text()) == result
    assert (tmp_path / "primary.json").read_bytes() == (tmp_path / "secondary.json").read_bytes()


def test_default_audit_does_not_launch_hardware_tools(tmp_path):
    with patch.object(audit.shutil, "which", return_value="/example/vivado"), \
         patch.object(audit.subprocess, "run") as run, \
         patch.object(audit, "OUTPUT_FILE", tmp_path / "primary.json"), \
         patch.object(audit, "SECONDARY_FILE", tmp_path / "secondary.json"):
        result = audit.run_vivado_silicon_audit()
    run.assert_not_called()
    for relative, digest in result["source_sha256"].items():
        assert hashlib.sha256((audit.ROOT / relative).read_bytes()).hexdigest() == digest
