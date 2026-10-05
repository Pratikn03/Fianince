"""
Comprehensive Unit & Integration Tests for the 5 Scientific Frontiers
======================================================================
Machine Markets — Top-Tier Institutional Verification Suite
"""
from __future__ import annotations
import numpy as np
import pytest

from research_extension.game_theory.strategic_equilibrium import (
    analyze_boundary_chipping, simulate_predatory_shorting_game
)
from empirical_pipeline.threshold_var_flash_crashes import (
    estimate_threshold_var
)
from simulations.multi_asset_cross_impact import (
    evaluate_multi_asset_cross_impact, compute_kreiss_constant
)
from simulations.welfare_pareto_frontier import (
    compute_welfare_pareto_frontier
)
from agentic_guard.kernel.fast_kernel import (
    FastAMIPKernel, benchmark_fast_kernel
)


class TestFiveFrontiers:
    # ---------------------------------------------------------------- WP1: Strategic Game Theory
    def test_strategic_boundary_chipping_bounded(self):
        r_star = 51.05
        res = analyze_boundary_chipping(kreiss_radius=r_star, epsilons=[0.01, 1.0])
        for eps_key, data in res.items():
            assert data["invariant_strictly_maintained"] is True
            assert data["total_inventory_accumulated"] <= r_star + 1e-4
            assert data["step_clamped"] in [1, 2]

    def test_predatory_shorting_eliminated(self):
        res = simulate_predatory_shorting_game()
        naive = res["naive_trading_ban"]
        amip = res["amip_passive_pegged_defense"]
        # Naive halt permits positive predatory profit
        assert naive["predatory_shorting_profitable"] is True
        assert naive["predator_strategy_profit_usd"] > 0.0
        # AMIP eliminates predatory profit (makes it negative EV)
        assert amip["predatory_profit_eliminated"] is True
        assert amip["predator_strategy_profit_usd"] < naive["predator_strategy_profit_usd"]

    # ---------------------------------------------------------------- WP2: Regime-Dependent TVAR
    def test_threshold_var_econometrics(self):
        res = estimate_threshold_var(n_rows=5000, depth_quantile_threshold=0.90)
        assert res["sample_size"] == 4999
        r1 = res["regime_1_calm_liquid"]
        r2 = res["regime_2_crisis_depleted"]
        assert r1["n_observations"] > 0
        assert r2["n_observations"] > 0
        assert "econometric_conclusion" in res

    # ---------------------------------------------------------------- WP3: Multi-Asset Cross-Impact
    def test_multi_asset_cross_impact(self):
        res = evaluate_multi_asset_cross_impact(d=3)
        assert res["portfolio_dimension"] == 3
        dec = res["decoupled_regime"]
        coup = res["coupled_cross_impact_regime"]
        assert dec["spectral_radius"] < 1.0
        assert coup["spectral_radius"] < 1.0
        # Cross impact should inflate or match Kreiss constant
        assert coup["kreiss_constant"] >= dec["kreiss_constant"]
        assert coup["safe_radius_units"] <= dec["safe_radius_units"]

    # ---------------------------------------------------------------- WP4: Welfare Pareto Frontier
    def test_welfare_pareto_frontier(self):
        res = compute_welfare_pareto_frontier(n_steps=20)
        frontier = res["pareto_frontier"]
        assert len(frontier) == 6
        # Find AMIP RFC-001 arm (theta = 0.25)
        amip_arm = [d for d in frontier if d["throttling_parameter_theta"] == 0.25][0]
        assert amip_arm["insolvency_loss_usd"] == 0.0
        assert amip_arm["is_solvent"] is True

    # ---------------------------------------------------------------- WP5: Sub-Microsecond Kernel
    def test_fast_kernel_correctness_and_sub_microsecond(self):
        kernel = FastAMIPKernel(equity=10_000_000.0)
        mid = 17180.0

        # Valid order
        allowed = kernel.evaluate_order(1.0, mid, mid, is_market_order=False, is_buy=True)
        assert allowed is True
        assert kernel.last_state == 0  # GREEN
        assert kernel.last_qty == 1.0

        # Rogue price deviation
        bad_px = kernel.evaluate_order(1.0, 15000.0, mid, is_market_order=False, is_buy=True)
        assert bad_px is False
        assert kernel.last_rejection == 2  # PRICE_DEVIATION

        # Mandatory abstention in RED state
        kernel.update_feedback(1.20)
        market_ord = kernel.evaluate_order(5.0, mid, mid, is_market_order=True, is_buy=True)
        assert market_ord is False
        assert kernel.last_rejection == 4  # MANDATORY_ABSTENTION_ACTIVE

        # Passive order throttled to 25% in RED state
        passive_ord = kernel.evaluate_order(4.0, mid, mid, is_market_order=False, is_buy=True)
        assert passive_ord is True
        assert kernel.last_qty == 1.0  # 4.0 * 0.25 = 1.0

        # Benchmark latency
        bench = benchmark_fast_kernel(n_iterations=5000)
        assert bench["latency_statistics_ns"]["is_sub_microsecond"] is True
        assert bench["latency_statistics_ns"]["mean_ns"] < 1000.0  # Sub-1000ns
