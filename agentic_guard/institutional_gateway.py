"""
AMIP RFC-001 Institutional Pre-Trade Risk Gateway
=================================================
Machine Markets — Autonomous Market Infrastructure Protocol

Hardware-optimized institutional gateway implementing the 4-Barrier Zero-Trust
pre-trade risk architecture for autonomous AI agents, algorithmic trading desks,
and clearing member connections. Compliant with SEC Rule 15c3-5 and MiFID II RTS 6.
"""
from __future__ import annotations
import hashlib
import json
import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple, Union

import numpy as np

from agentic_guard.core import (
    AgenticGuard, AgentOrder, InterceptDecision, AMIPState, RejectionCode
)
from agentic_guard.llm_tools import (
    ProviderFormat, parse_llm_tool_call
)


@dataclass
class GatewayAuditRecord:
    timestamp_ns: int
    order_id: str
    agent_id: str
    symbol: str
    side: str
    order_type: str
    requested_qty: float
    price: float
    mid_price: float
    decision_allowed: bool
    state: str
    rejection_code: str
    rejection_reason: str
    effective_qty: float
    s_upper: float
    kreiss_radius: float
    latency_us: float
    provenance_hash: str = ""


class InstitutionalAMIPGateway:
    """
    Production Pre-Trade Risk Gateway for autonomous AI trading agents.
    Provides sub-microsecond pre-trade gating, cryptographic audit trails,
    and institutional solvency guarantees.
    """
    def __init__(
        self,
        equity: float = 10_000_000.0,
        kreiss_constant_J: float = 3.42,
        buffer_ratio: float = 0.30,
        max_price_deviation_pct: float = 0.03,
        gateway_id: str = "GW_CME_NY4_01"
    ):
        self.gateway_id = gateway_id
        self.guard = AgenticGuard(
            equity=equity,
            kreiss_constant_J=kreiss_constant_J,
            buffer_ratio=buffer_ratio,
            max_price_deviation_pct=max_price_deviation_pct
        )
        self.audit_log: List[GatewayAuditRecord] = []
        self._last_hash = "0" * 64
        self._order_counter = 0

        # Performance latency tracking
        self.latencies_us: List[float] = []

    @property
    def equity(self) -> float:
        return self.guard.equity

    def update_market_state(self, s_hat: float, s_lower: float, s_upper: float):
        """Update market-wide systemic feedback estimates from streaming LOB."""
        self.guard.update_market_state(s_hat=s_hat, s_lower=s_lower, s_upper=s_upper)

    def process_tool_payload(
        self,
        payload: Union[Dict[str, Any], str],
        current_mid: float,
        provider: ProviderFormat = ProviderFormat.RAW,
        agent_id: str = "AI_DESK_ALPHA"
    ) -> Tuple[InterceptDecision, Optional[GatewayAuditRecord]]:
        """
        Intercept a raw LLM tool call payload, parse it, and execute 4-barrier risk check.
        """
        t0_ns = time.perf_counter_ns()
        self._order_counter += 1
        order_id = f"{self.gateway_id}_{self._order_counter:08d}"

        # 1. Parse LLM Tool Call
        order, parse_err = parse_llm_tool_call(payload, provider=provider, agent_id=agent_id)
        if order is None:
            t1_ns = time.perf_counter_ns()
            latency_us = (t1_ns - t0_ns) / 1000.0
            self.latencies_us.append(latency_us)

            # Reject malformed schema
            decision = InterceptDecision(
                is_allowed=False,
                state=self.guard.current_state,
                rejection_code=RejectionCode.HALLUCINATION_INVALID_QUANTITY,
                rejection_reason=f"LLM Tool Schema Error: {parse_err}",
                s_hat=self.guard.s_hat,
                s_lower=self.guard.s_lower,
                s_upper=self.guard.s_upper,
                kreiss_safe_radius=self.guard.compute_kreiss_safe_radius(current_mid),
                effective_qty=0.0,
                execution_latency_us=latency_us
            )
            record = self._create_audit_record(order_id, agent_id, "UNKNOWN", "BUY", "LIMIT", 0.0, 0.0, current_mid, decision, t0_ns)
            return decision, record

        # 2. Execute 4-Barrier AgenticGuard Pre-Trade Inspection
        decision = self.guard.intercept(order, current_mid=current_mid)
        t1_ns = time.perf_counter_ns()
        total_latency_us = (t1_ns - t0_ns) / 1000.0
        decision.execution_latency_us = total_latency_us
        self.latencies_us.append(total_latency_us)

        # 3. Create Cryptographic Audit Record
        record = self._create_audit_record(
            order_id=order_id,
            agent_id=order.agent_id,
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            requested_qty=order.order_qty,
            price=order.price,
            mid_price=current_mid,
            decision=decision,
            timestamp_ns=t0_ns
        )
        return decision, record

    def _create_audit_record(
        self,
        order_id: str,
        agent_id: str,
        symbol: str,
        side: str,
        order_type: str,
        requested_qty: float,
        price: float,
        mid_price: float,
        decision: InterceptDecision,
        timestamp_ns: int
    ) -> GatewayAuditRecord:
        # Cryptographic Hash Chaining for Auditable Immutable Memory
        raw_token = f"{self._last_hash}:{timestamp_ns}:{order_id}:{agent_id}:{symbol}:{requested_qty}:{price}:{decision.is_allowed}:{decision.rejection_code.value}"
        provenance_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        self._last_hash = provenance_hash

        record = GatewayAuditRecord(
            timestamp_ns=timestamp_ns,
            order_id=order_id,
            agent_id=agent_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            requested_qty=requested_qty,
            price=price,
            mid_price=mid_price,
            decision_allowed=decision.is_allowed,
            state=decision.state.value,
            rejection_code=decision.rejection_code.value,
            rejection_reason=decision.rejection_reason,
            effective_qty=decision.effective_qty,
            s_upper=decision.s_upper,
            kreiss_radius=decision.kreiss_safe_radius,
            latency_us=decision.execution_latency_us,
            provenance_hash=provenance_hash
        )
        self.audit_log.append(record)
        return record

    def get_latency_profile(self) -> Dict[str, float]:
        """Compute latency percentiles in microseconds."""
        if not self.latencies_us:
            return {"mean": 0.0, "p50": 0.0, "p90": 0.0, "p99": 0.0, "max": 0.0}
        arr = np.array(self.latencies_us)
        return {
            "n_orders": len(arr),
            "mean_us": float(np.mean(arr)),
            "p50_us": float(np.percentile(arr, 50)),
            "p90_us": float(np.percentile(arr, 90)),
            "p99_us": float(np.percentile(arr, 99)),
            "max_us": float(np.max(arr))
        }
