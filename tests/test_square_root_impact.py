"""
Unit and Microstructure Tests for Frontier 1: Non-Linear Square-Root Market Impact
==================================================================================
Tests Theorem NL1 (Non-Linear Kreiss Bound Conservatism) and Bouchaud-Gatheral
empirical parameter estimation on Bitcoin Level-3 order books.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from empirical_pipeline.square_root_impact import (
    estimate_square_root_impact,
    verify_non_linear_kreiss_invariance,
    run_square_root_impact_pipeline,
    OUTPUT_FILE,
    DATA_FILE
)


class TestSquareRootImpact:
    @pytest.mark.skipif(not DATA_FILE.exists(), reason="Real L3 BTC data required")
    def test_empirical_square_root_estimation(self):
        """Test empirical estimation of concave market impact on L3 tick records."""
        stats = estimate_square_root_impact(n_rows=10_000)
        assert stats["n_samples"] > 50
        # Power law alpha must be strictly sublinear (concave, < 1.0)
        assert 0.05 <= stats["alpha_hat"] <= 0.85
        assert stats["alpha_stderr"] > 0.0
        assert stats["c_square_root"] > 0.0
        # Bouchaud Y coefficient is normalized in range [0.45, 0.75]
        assert 0.40 <= stats["bouchaud_y_coefficient"] <= 0.80
        assert stats["avg_top_depth_btc"] > 0.0

    def test_theorem_nl1_kreiss_invariance(self):
        """Verify Theorem NL1: linear Kreiss radius guarantees invariant non-linear safety."""
        invar = verify_non_linear_kreiss_invariance(horizon=50, kappa_linear=0.75, b_limit=4.0, r_star=1.2)
        assert invar["theorem_nl1_conservative_satisfied"] is True
        # Under concave impact, boundary excursion matches worst-case linear envelope
        assert invar["max_nonlinear_excursion"] <= invar["max_linear_excursion"] + 1e-6
        assert invar["ratio_nl_to_lin_at_limit"] <= 1.0 + 1e-6
        # In intermediate sector, concave excursion is strictly dominated by sector-linear dynamics
        assert invar["nonlinear_excursion_half_rate"] <= invar["sector_linear_excursion_half"] + 1e-6
        assert invar["ratio_nl_to_sector_half"] <= 1.0 + 1e-6

    def test_liquidity_cliff_catastrophe(self):
        """Verify discontinuous price gapping when cumulative flow exceeds book depth."""
        invar = verify_non_linear_kreiss_invariance()
        assert invar["liquidity_cliff_triggered"] is True
        assert invar["cliff_state_blowup"] > invar["nominal_state_without_cliff"]

    def test_end_to_end_pipeline_and_provenance(self):
        """Verify full pipeline execution and JSON artifact persistence."""
        res = run_square_root_impact_pipeline()
        assert OUTPUT_FILE.exists()
        with open(OUTPUT_FILE) as f:
            data = json.load(f)
        assert data["frontier"] == "Frontier 1: Non-Linear Square-Root Market Impact"
        assert data["theoretical_invariance"]["theorem_nl1_conservative_satisfied"] is True
