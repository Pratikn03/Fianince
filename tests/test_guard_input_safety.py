from dataclasses import replace

import pytest

from agentic_guard.core import AgenticGuard, AgentOrder, AMIPState
from agentic_guard.institutional_gateway import InstitutionalAMIPGateway


@pytest.mark.parametrize("mid,price", [(0, 100), (float("nan"), 100), (100, float("nan")), (100, float("inf"))])
def test_nonfinite_price_or_midpoint_never_authorizes(mid, price):
    decision = AgenticGuard().intercept(AgentOrder("a", "X", "BUY", 1, price), mid)
    assert not decision.is_allowed and decision.effective_qty == 0


def test_bad_certificate_latches_red_until_valid_update():
    guard = AgenticGuard()
    with pytest.raises(ValueError):
        guard.update_market_state(float("nan"), 0.5, 0.8)
    assert guard.current_state == AMIPState.RED
    assert not guard.intercept(AgentOrder("a", "X", "BUY", 1, 100), 100).is_allowed
    guard.update_market_state(0.7, 0.6, 0.8)
    assert guard.intercept(AgentOrder("a", "X", "BUY", 1, 100), 100).is_allowed


@pytest.mark.parametrize("upper", [0.90, 0.96, 1.05])
def test_order_state_and_status_use_same_threshold(upper):
    guard = AgenticGuard()
    guard.update_market_state(upper - 0.02, upper - 0.04, upper)
    assert guard.intercept(AgentOrder("a", "X", "BUY", 1, 100, order_type="MARKET"), 100).state == guard.current_state


def test_reducing_position_can_cross_zero_to_opposite_radius():
    guard = AgenticGuard(equity=1000, current_inventory=2, kreiss_constant_J=1, buffer_ratio=0.3)
    d = guard.intercept(AgentOrder("a", "X", "SELL", 6, 100), 100)
    assert d.is_allowed and d.effective_qty == pytest.approx(5)
    assert abs(guard.inventory - d.effective_qty) <= d.kreiss_safe_radius


@pytest.mark.parametrize("field,value", [("side", "SELL"), ("effective_qty", 999), ("mid_price", 101), ("s_upper", 2)])
def test_audit_chain_covers_execution_and_certificate_fields(field, value):
    gateway = InstitutionalAMIPGateway()
    gateway.process_tool_payload({"symbol": "X", "side": "BUY", "quantity": 1, "price": 100}, 100)
    assert gateway.verify_audit_chain()
    gateway.audit_log[0] = replace(gateway.audit_log[0], **{field: value})
    assert not gateway.verify_audit_chain()


def test_rejected_nan_price_is_auditable():
    gateway = InstitutionalAMIPGateway()
    decision, _ = gateway.process_tool_payload({"symbol": "X", "side": "BUY", "quantity": 1, "price": float("nan")}, 100)
    assert not decision.is_allowed and gateway.verify_audit_chain()


def test_certificate_arithmetic_failure_after_history_update_is_rejected(monkeypatch):
    guard = AgenticGuard()
    certificates = iter([(0.7, 0.6, 0.8), (float("nan"),) * 3])
    monkeypatch.setattr(guard, "_compute_conic_certificate", lambda: next(certificates))
    decision = guard.intercept(AgentOrder("a", "X", "BUY", 1, 100), 100)
    assert not decision.is_allowed and decision.state == AMIPState.RED
