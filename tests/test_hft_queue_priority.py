"""
Unit and Microstructure Tests for Frontier 4: LOB FIFO Queue Priority & Fill Dynamics
======================================================================================
Tests FIFO queue priority matching, fill probability, adverse selection toxic loss
reduction, and inventory variance stabilization under AMIP on Level-3 Bitcoin data.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from agentic_guard.hft_queue_priority_model import (
    simulate_hft_queue_priority,
    run_hft_queue_priority_pipeline,
    OUTPUT_FILE,
    DATA_FILE
)


class TestHFTQueuePriority:
    @pytest.mark.skipif(not DATA_FILE.exists(), reason="Real L3 BTC data required")
    def test_fifo_queue_priority_simulation(self):
        """Test FIFO queue matching and queue depletion on empirical L3 books."""
        res = simulate_hft_queue_priority(n_rows=5_000, sample_stride=25)
        assert res["orders_evaluated"] > 10
        assert res["fifo_priority_validated"] is True

        static = res["static_amip_pegged"]
        qa = res["queue_aware_amip"]

        # Both policies achieve high fill rate (> 50%)
        assert static["fill_rate_pct"] > 50.0
        assert qa["fill_rate_pct"] > 50.0

        # Queue-Aware AMIP must reduce toxic dollar losses significantly
        assert qa["toxic_loss_usd"] <= static["toxic_loss_usd"]
        assert res["toxic_loss_reduction_pct"] >= 20.0

        # Inventory variance must be strictly reduced
        assert res["inventory_variance_reduction_pct"] > 30.0

    @pytest.mark.skipif(not DATA_FILE.exists(), reason="Real L3 BTC data required")
    def test_end_to_end_pipeline_and_provenance(self):
        """Test full execution and JSON provenance artifact persistence."""
        res = run_hft_queue_priority_pipeline()
        assert OUTPUT_FILE.exists()
        with open(OUTPUT_FILE) as f:
            data = json.load(f)
        assert data["frontier"] == "Frontier 4: LOB FIFO Queue Priority & Fill Dynamics"
        assert data["microstructure_results"]["fifo_priority_validated"] is True
        assert data["microstructure_results"]["toxic_loss_reduction_pct"] > 0.0
