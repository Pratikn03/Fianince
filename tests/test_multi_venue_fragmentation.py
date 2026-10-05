"""
Unit and Game-Theoretic Tests for Frontier 2: Multi-Venue Fragmentation & Arbitrage
===================================================================================
Tests Theorem G3 (Cross-Venue Predatory Leakage) and evaluates the Federated AMIP
zero-knowledge cross-venue risk signaling protocol across fragmented spot & perpetual markets.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from simulations.multi_venue_fragmentation import (
    simulate_multi_venue_ecosystem,
    run_multi_venue_pipeline,
    OUTPUT_FILE
)


class TestMultiVenueFragmentation:
    def test_multi_venue_simulation_structure(self):
        """Verify 2-venue simulation runs and models all three governance regimes."""
        res = simulate_multi_venue_ecosystem(n_steps=100)
        assert "unprotected_market" in res
        assert "local_single_venue_amip" in res
        assert "federated_amip" in res
        assert res["federated_protocol_active"] is True

    def test_theorem_g3_predatory_leakage(self):
        """
        Verify Theorem G3: When only Venue 1 enforces AMIP, predatory shorting shifts
        to Venue 2 and leaks back to Venue 1 via statistical arbitrage.
        """
        res = simulate_multi_venue_ecosystem(n_steps=150)
        local_amip = res["local_single_venue_amip"]
        fed_amip = res["federated_amip"]

        # Predatory leakage flow in local AMIP strictly exceeds federated leakage
        assert res["theorem_g3_predatory_leakage_validated"] is True
        assert local_amip["max_cross_venue_leakage_flow"] > fed_amip["max_cross_venue_leakage_flow"]

        # Local AMIP experiences substantial spillover drawdown on Venue 1
        assert local_amip["max_drawdown_venue1_pct"] > 10.0

    def test_federated_amip_contagion_containment(self):
        """
        Verify that Federated AMIP (cross-venue risk commitment) suppresses
        contagion drawdown by at least 60%.
        """
        res = simulate_multi_venue_ecosystem(n_steps=150)
        assert res["cross_venue_drawdown_reduction_pct"] >= 60.0
        assert res["federated_amip"]["max_drawdown_venue1_pct"] < 10.0

    def test_end_to_end_pipeline_and_provenance(self):
        """Verify pipeline execution and JSON provenance artifact persistence."""
        res = run_multi_venue_pipeline()
        assert OUTPUT_FILE.exists()
        with open(OUTPUT_FILE) as f:
            data = json.load(f)
        assert data["frontier"] == "Frontier 2: Multi-Venue Fragmentation & Cross-Exchange Arbitrage"
        assert data["simulation_results"]["theorem_g3_predatory_leakage_validated"] is True
