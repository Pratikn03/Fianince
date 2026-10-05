"""
Unit and Hardware Timing Tests for Frontier 6: Physical FPGA Silicon Synthesis
==============================================================================
Validates AMD Alveo U50 synthesis metrics, zero setup/hold timing violations,
resource utilization limits, and 8-cycle deterministic latency SLA for AMIP.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from agentic_guard.hardware.run_vivado_synthesis_audit import (
    run_vivado_silicon_audit,
    OUTPUT_FILE,
    RTL_FILE,
    TCL_FILE
)


class TestFPGASiliconSynthesis:
    def test_verilog_and_tcl_sources_exist(self):
        """Verify RTL pipeline and Vivado synthesis script exist on disk."""
        assert RTL_FILE.exists(), f"Missing Verilog RTL: {RTL_FILE}"
        assert TCL_FILE.exists(), f"Missing TCL script: {TCL_FILE}"
        
        # Verify RTL module ports
        content = RTL_FILE.read_text()
        assert "module amip_fpga_pipeline" in content
        assert "kreiss_safe_radius" in content
        assert "decision_allowed" in content
        assert "effective_qty" in content

    def test_silicon_timing_and_slack_constraints(self):
        """Verify timing constraints at 400 MHz: positive slack (WNS > 0, WHS > 0)."""
        res = run_vivado_silicon_audit()
        timing = res["post_route_synthesis_report"]["pipeline_timing"]
        assert timing["timing_constraints_met"] is True
        assert timing["setup_slack_wns_ns"] > 0.0, "Setup timing slack WNS must be positive"
        assert timing["hold_slack_whs_ns"] > 0.0, "Hold timing slack WHS must be positive"
        assert timing["total_negative_slack_tns_ns"] == 0.0
        assert timing["deterministic_latency_ns"] == 20.00
        assert timing["pipeline_stages_cycles"] == 8

    def test_hardware_resource_utilization_ceilings(self):
        """Verify that AMIP occupies less than 1.0% of Alveo U50 FPGA resources."""
        res = run_vivado_silicon_audit()
        util = res["post_route_synthesis_report"]["resource_utilization"]
        assert util["lut"]["utilization_pct"] < 1.0
        assert util["ff"]["utilization_pct"] < 1.0
        assert util["dsp48e2"]["utilization_pct"] < 1.0
        # Zero BRAM usage for pure register pipeline
        assert util["bram36k"]["used"] == 0
        assert util["bram36k"]["utilization_pct"] == 0.0

    def test_end_to_end_synthesis_pipeline_and_provenance(self):
        """Verify full execution and JSON provenance artifact persistence."""
        res = run_vivado_silicon_audit()
        assert OUTPUT_FILE.exists()
        with open(OUTPUT_FILE) as f:
            data = json.load(f)
        assert data["frontier"] == "Frontier 6: Physical FPGA Silicon Synthesis (AMD Alveo U50)"
        assert data["post_route_synthesis_report"]["target_silicon"]["device_part"] == "xcu50-fsvh2104-2-e"
