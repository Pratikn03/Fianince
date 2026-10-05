"""
Unit and Integration Tests for AgenticGuard (AMIP RFC-001)
==========================================================
Machine Markets — Universal Pre-Trade Agentic AI Safety Standard
"""
from __future__ import annotations
import numpy as np
import pytest

from agentic_guard.core import (
    AgenticGuard, AgentOrder, InterceptDecision, AMIPState, RejectionCode
)
from agentic_guard.multi_agent_sandbox import run_multi_agent_sandbox_benchmark


class TestAgenticGuardCore:
    def test_guard_initialization(self):
        guard = AgenticGuard(equity=10_000_000.0, kreiss_constant_J=3.42, buffer_ratio=0.30)
        assert guard.equity == 10_000_000.0
        assert guard.kreiss_constant_J == 3.42
        r_star = guard.compute_kreiss_safe_radius(current_price=17180.0)
        assert r_star > 0.0
        # Expected r* = (10M * 0.30) / (3.42 * 17180) ~ 51.05 BTC
        assert abs(r_star - 51.05) < 0.50

    def test_hallucination_price_deviation_rejected(self):
        guard = AgenticGuard(equity=10_000_000.0, max_price_deviation_pct=0.03)
        current_mid = 17180.0

        # Rogue hallucination: 10% below market price
        rogue_order = AgentOrder(
            agent_id="ROGUE_LLM",
            symbol="BTC-PERP",
            side="BUY",
            order_qty=1.0,
            price=15000.0,  # ~12.7% deviation
            order_type="LIMIT"
        )
        dec = guard.intercept(rogue_order, current_mid=current_mid)
        assert dec.is_allowed is False
        assert dec.rejection_code == RejectionCode.HALLUCINATION_PRICE_DEVIATION
        assert "Hallucination rejected" in dec.rejection_reason

    def test_hallucination_invalid_quantity_rejected(self):
        guard = AgenticGuard(equity=10_000_000.0)
        current_mid = 17180.0

        invalid_orders = [
            AgentOrder("AI_1", "BTC-PERP", "BUY", -5.0, current_mid),
            AgentOrder("AI_2", "BTC-PERP", "BUY", 0.0, current_mid),
            AgentOrder("AI_3", "BTC-PERP", "BUY", float("nan"), current_mid),
        ]
        for ord in invalid_orders:
            dec = guard.intercept(ord, current_mid=current_mid)
            assert dec.is_allowed is False
            assert dec.rejection_code == RejectionCode.HALLUCINATION_INVALID_QUANTITY

    def test_kreiss_safe_radius_enforcement(self):
        guard = AgenticGuard(equity=1_000_000.0, kreiss_constant_J=3.42, buffer_ratio=0.30)
        current_mid = 17180.0
        r_star = guard.compute_kreiss_safe_radius(current_mid)  # ~5.1 BTC

        # Order within limit
        safe_order = AgentOrder("AI_MM", "BTC-PERP", "BUY", 2.0, current_mid)
        dec_safe = guard.intercept(safe_order, current_mid=current_mid)
        assert dec_safe.is_allowed is True
        assert dec_safe.effective_qty == 2.0
        guard.record_fill(2.0, current_mid, "BUY")

        # Huge order exceeding remaining headroom
        oversized_order = AgentOrder("AI_MM", "BTC-PERP", "BUY", 10.0, current_mid)
        dec_over = guard.intercept(oversized_order, current_mid=current_mid)
        # Should be clamped to remaining safe room
        assert dec_over.effective_qty < 10.0
        assert dec_over.effective_qty <= (r_star - 2.0 + 1e-4)

    def test_conic_feedback_state_machine(self):
        guard = AgenticGuard(equity=10_000_000.0, window_size=20)
        current_mid = 17180.0

        # Normal calm orders -> GREEN
        calm_order = AgentOrder("AI_1", "BTC-PERP", "BUY", 0.5, current_mid)
        dec_calm = guard.intercept(calm_order, current_mid=current_mid)
        assert dec_calm.state == AMIPState.GREEN
        assert dec_calm.is_allowed is True

        # Inject extreme upward momentum spiral into history
        guard.flow_history = [1.0 + 0.5 * i for i in range(30)]
        guard.price_history = [17000.0 + 20.0 * i for i in range(30)]
        spiral_mid = 17000.0 + 20.0 * 30

        # Aggressive market order under RED state -> Mandatory Abstention
        panic_market_order = AgentOrder("AI_MOM", "BTC-PERP", "BUY", 5.0, spiral_mid, order_type="MARKET")
        dec_panic = guard.intercept(panic_market_order, current_mid=spiral_mid)
        assert dec_panic.state == AMIPState.RED
        assert dec_panic.is_allowed is False
        assert dec_panic.rejection_code == RejectionCode.MANDATORY_ABSTENTION_ACTIVE

        # Passive limit order under RED state -> Allowed with 75% size reduction
        passive_limit_order = AgentOrder("AI_PASSIVE", "BTC-PERP", "BUY", 4.0, spiral_mid, order_type="LIMIT")
        dec_passive = guard.intercept(passive_limit_order, current_mid=spiral_mid)
        assert dec_passive.state == AMIPState.RED
        assert dec_passive.is_allowed is True
        assert dec_passive.effective_qty <= 1.0  # Reduced to 25%

    def test_sub_100_microsecond_latency_sla(self):
        guard = AgenticGuard(equity=10_000_000.0)
        current_mid = 17180.0
        order = AgentOrder("BENCH_AI", "BTC-PERP", "BUY", 1.0, current_mid)

        latencies = []
        for _ in range(500):
            dec = guard.intercept(order, current_mid=current_mid)
            latencies.append(dec.execution_latency_us)

        mean_lat = np.mean(latencies)
        p99_lat = np.percentile(latencies, 99)
        assert mean_lat < 100.0, f"Mean latency {mean_lat:.2f}μs breached 100μs SLA"
        assert p99_lat < 250.0, f"P99 latency {p99_lat:.2f}μs breached 250μs limit"

    def test_multi_agent_sandbox_benchmark_execution(self):
        results = run_multi_agent_sandbox_benchmark(n_steps=50, seed=42)
        assert "regime_comparison" in results
        unprot = results["regime_comparison"]["unprotected_market"]
        prot = results["regime_comparison"]["agentic_guard_protected"]
        # Protected drawdown must be significantly smaller than unprotected
        assert abs(prot["max_market_drawdown_pct"]) < abs(unprot["max_market_drawdown_pct"])
        assert prot["defaulted_agents"] == 0
