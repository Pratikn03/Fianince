"""Record hardware tool execution and raw reports without inventing physical measurements.

Previous fixed utilization, power and slack numbers were not parsed from reports and are withdrawn as measurement
evidence. Timing and a wire-to-wire SLA remain unverified until raw implementation reports are independently checked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import time

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RTL_FILE = ROOT / "agentic_guard/hardware/amip_fpga_pipeline.v"
TCL_FILE = ROOT / "agentic_guard/hardware/synth_amip_alveo_u50.tcl"
OUTPUT_FILE = ROOT / "results/provenance/fpga_silicon_synthesis_report.json"
SECONDARY_FILE = ROOT / "research_extension/outputs/fpga_silicon_synthesis_report.json"


def run_vivado_silicon_audit(run_live=False):
    """Audit sources; run Vivado only when requested, and retain hashes of fresh raw reports."""
    for path in (RTL_FILE, TCL_FILE):
        if not path.is_file():
            raise FileNotFoundError(path)
    started = time.time()
    vivado = shutil.which("vivado")
    executed, returncode, error, reports = False, None, None, {}
    if run_live and vivado:
        try:
            result = subprocess.run([vivado, "-mode", "batch", "-source", str(TCL_FILE)], cwd=ROOT,
                                    capture_output=True, text=True, timeout=600)
            executed, returncode = True, result.returncode
            if returncode == 0:
                for name in ("utilization_route.rpt", "timing_summary.rpt", "power_analysis.rpt"):
                    path = ROOT / "vivado_build" / name
                    if path.is_file() and path.stat().st_mtime >= started:
                        reports[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        except (OSError, subprocess.TimeoutExpired) as exc:
            error = type(exc).__name__
    elif run_live:
        error = "Vivado unavailable"
    report = {
        "frontier": "Frontier 6: Physical FPGA Silicon Synthesis (AMD Alveo U50)",
        "status": "RAW_REPORTS_UNVERIFIED" if len(reports) == 3 else "NOT_MEASURED",
        "measurements_verified": False,
        "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (RTL_FILE, TCL_FILE)},
        "raw_report_sha256": reports,
        "post_route_synthesis_report": {
            "target_silicon": {"device_part": "xcu50-fsvh2104-2-e", "target_clock_mhz": 400.0},
            "pipeline_timing": {"timing_constraints_met": None, "deterministic_latency_ns": None,
                                "setup_slack_wns_ns": None, "hold_slack_whs_ns": None},
            "resource_utilization": None, "power_analysis_watts": None,
            "audit_metadata": {"live_vivado_executed": executed, "returncode": returncode,
                               "wire_speed_hft_sla_compliance": None, "error": error},
        },
        "limits": ["Target clock is a design constraint, not an achieved measurement.",
                   "Previous hard-coded slack, resource and power values are not validated hardware evidence.",
                   "No physical timing or regulatory compliance conclusion follows from this audit."],
    }
    for path in (OUTPUT_FILE, SECONDARY_FILE):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Hardware audit: {report['status']}; measurements_verified=False")
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-live", action="store_true")
    run_vivado_silicon_audit(ap.parse_args().run_live)
