"""
AgenticGuard Core Pre-Trade Interceptor & Safety Controller
===========================================================
Machine Markets — AMIP RFC-001 Reference Implementation
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import numpy as np


class AMIPState(str, Enum):
    GREEN = "GREEN_ACTIVE"
    YELLOW = "YELLOW_THROTTLE"
    RED = "RED_MANDATORY_ABSTENTION"


class RejectionCode(str, Enum):
    NONE = "NONE"
    HALLUCINATION_PRICE_DEVIATION = "HALLUCINATION_PRICE_DEVIATION"
    HALLUCINATION_INVALID_QUANTITY = "HALLUCINATION_INVALID_QUANTITY"
    KREISS_RADIUS_EXCEEDED = "KREISS_RADIUS_EXCEEDED"
    MANDATORY_ABSTENTION_ACTIVE = "MANDATORY_ABSTENTION_ACTIVE"
    MARGIN_BREACH_PREVENTED = "MARGIN_BREACH_PREVENTED"


@dataclass
class AgentOrder:
    agent_id: str
    symbol: str
    side: str  # "BUY" or "SELL"
    order_qty: float
    price: float
    order_type: str = "LIMIT"  # "MARKET", "LIMIT", "PEGGED"
    disclosed_eta: float = 0.02
    reasoning_summary: str = ""


@dataclass
class InterceptDecision:
    is_allowed: bool
    state: AMIPState
    rejection_code: RejectionCode
    rejection_reason: str
    s_hat: float
    s_lower: float
    s_upper: float
    kreiss_safe_radius: float
    effective_qty: float
    execution_latency_us: float

    @property
    def is_throttled(self) -> bool:
        return self.is_allowed and self.state == AMIPState.YELLOW


class AgenticGuard:
    """
    Institutional Pre-Trade Safety Gatekeeper for Autonomous AI Agents.
    Enforces AMIP RFC-001 across four non-bypassable barriers:
      1. Semantic Anti-Hallucination & Conservation Check
      2. Streaming Conic Feedback Gain Certification [S_lower, S_upper]
      3. Pseudospectral Kreiss Solvency Radius Limits (Theorem M5)
      4. Three-State Mandatory Abstention Supervisory Router
    """
    def __init__(
        self,
        equity: float = 10_000_000.0,
        cash: Optional[float] = None,
        current_inventory: float = 0.0,
        kreiss_constant_J: float = 3.42,
        buffer_ratio: float = 0.30,
        window_size: int = 60,
        max_price_deviation_pct: float = 0.03,  # 3% maximum deviation from mid
    ):
        self.equity = equity
        self.cash = cash if cash is not None else (0.40 * equity)
        self.inventory = current_inventory
        self.kreiss_constant_J = kreiss_constant_J
        self.buffer_ratio = buffer_ratio
        self.window_size = window_size
        self.max_price_dev = max_price_deviation_pct

        # Rolling history buffers
        self.flow_history: List[float] = []
        self.price_history: List[float] = []

        # Metrics & audit logs
        self.intercepted_count = 0
        self.rejections_count = 0
        self.throttled_count = 0
        self.abstentions_count = 0
        self.audit_log: List[Dict[str, Any]] = []
        self._override_s_bounds: Optional[Tuple[float, float, float]] = None

    def update_market_state(self, s_hat: float, s_lower: float, s_upper: float):
        """Update market-wide systemic feedback estimates from external streaming estimator."""
        self._override_s_bounds = (float(s_hat), float(s_lower), float(s_upper))

    @property
    def s_hat(self) -> float:
        return self._override_s_bounds[0] if self._override_s_bounds else 0.70

    @property
    def s_lower(self) -> float:
        return self._override_s_bounds[1] if self._override_s_bounds else 0.65

    @property
    def s_upper(self) -> float:
        return self._override_s_bounds[2] if self._override_s_bounds else 0.75

    @property
    def current_state(self) -> AMIPState:
        s_up = self.s_upper
        if s_up >= 1.0:
            return AMIPState.RED
        elif s_up >= 0.85:
            return AMIPState.YELLOW
        return AMIPState.GREEN

    def _compute_conic_certificate(self) -> Tuple[float, float, float]:
        """Streaming Conic Certificate [S_lower, S_upper] in < 25 microseconds."""
        if self._override_s_bounds is not None:
            return self._override_s_bounds

        if len(self.flow_history) < 15:
            return 0.70, 0.65, 0.75  # Prior default subcritical

        y_flow = np.array(self.flow_history[-self.window_size:])
        x_px = np.array(self.price_history[-self.window_size:])

        dx = np.diff(x_px, prepend=x_px[0])
        lag_flow = np.roll(y_flow, 1)
        lag_flow[0] = 0.0

        var_flow = np.var(lag_flow)
        if var_flow < 1e-8:
            s_hat = 0.75
            se = 0.04
        else:
            cov = np.cov(dx, lag_flow)[0, 1]
            q_proxy = float(cov / (var_flow + 1e-8))
            s_hat = float(np.clip(0.40 + q_proxy * 5.0, 0.10, 2.50))
            se = float(0.08 / np.sqrt(len(y_flow)))

        s_lower = float(s_hat - 1.96 * se)
        s_upper = float(s_hat + 1.96 * se)
        return s_hat, s_lower, s_upper

    def compute_kreiss_safe_radius(
        self,
        current_price: float,
        conservative: bool = False,
        dim: int = 2
    ) -> float:
        """Theorem M5 Solvency Radius: exact r^* = B / (M_C * P) or conservative r_cons = B / (alpha_n * K(J) * P)."""
        buffer_capital = self.equity * self.buffer_ratio
        denom = self.kreiss_constant_J * max(current_price, 1e-4)
        if conservative:
            denom *= (np.e * dim)
        return float(buffer_capital / denom)

    def intercept(
        self,
        order: AgentOrder,
        current_mid: float,
        current_spread: float = 0.10
    ) -> InterceptDecision:
        t0 = time.perf_counter_ns()
        self.intercepted_count += 1

        # ------------------------------------------------------------- Barrier 1: Semantic Hallucination Filter
        if order.order_qty <= 0 or not np.isfinite(order.order_qty):
            lat_us = (time.perf_counter_ns() - t0) / 1000.0
            self.rejections_count += 1
            return InterceptDecision(
                is_allowed=False,
                state=AMIPState.GREEN,
                rejection_code=RejectionCode.HALLUCINATION_INVALID_QUANTITY,
                rejection_reason=f"Agent generated non-positive quantity: {order.order_qty}",
                s_hat=0.70, s_lower=0.65, s_upper=0.75,
                kreiss_safe_radius=self.compute_kreiss_safe_radius(current_mid),
                effective_qty=0.0,
                execution_latency_us=lat_us
            )

        # Check price reasonability (Hallucination detection)
        if order.order_type == "LIMIT":
            dev_pct = abs(order.price - current_mid) / current_mid
            if dev_pct > self.max_price_dev:
                lat_us = (time.perf_counter_ns() - t0) / 1000.0
                self.rejections_count += 1
                return InterceptDecision(
                    is_allowed=False,
                    state=AMIPState.GREEN,
                    rejection_code=RejectionCode.HALLUCINATION_PRICE_DEVIATION,
                    rejection_reason=(
                        f"Agent price {order.price:.2f} deviates {dev_pct*100:.2f}% from mid {current_mid:.2f} "
                        f"(max permitted: {self.max_price_dev*100:.1f}%). Hallucination rejected."
                    ),
                    s_hat=0.70, s_lower=0.65, s_upper=0.75,
                    kreiss_safe_radius=self.compute_kreiss_safe_radius(current_mid),
                    effective_qty=0.0,
                    execution_latency_us=lat_us
                )

        # ------------------------------------------------------------- Barrier 2: Streaming Conic Feedback Certification
        signed_flow = order.order_qty if order.side.upper() == "BUY" else -order.order_qty
        self.flow_history.append(signed_flow)
        self.price_history.append(current_mid)

        s_hat, s_lower, s_upper = self._compute_conic_certificate()
        kreiss_radius = self.compute_kreiss_safe_radius(current_mid)

        # ------------------------------------------------------------- Barrier 3: Kreiss Solvency Radius Enforcement
        new_inv = self.inventory + signed_flow
        if abs(new_inv) > kreiss_radius:
            # Capacity exceeded
            allowed_room = max(0.0, kreiss_radius - abs(self.inventory))
            if allowed_room <= 0.0:
                lat_us = (time.perf_counter_ns() - t0) / 1000.0
                self.rejections_count += 1
                return InterceptDecision(
                    is_allowed=False,
                    state=AMIPState.YELLOW if s_upper < 1.0 else AMIPState.RED,
                    rejection_code=RejectionCode.KREISS_RADIUS_EXCEEDED,
                    rejection_reason=(
                        f"Kreiss safe radius exceeded: requested position {abs(new_inv):.2f} > "
                        f"limit {kreiss_radius:.2f} units (Theorem M5 solvency bound)."
                    ),
                    s_hat=s_hat, s_lower=s_lower, s_upper=s_upper,
                    kreiss_safe_radius=kreiss_radius,
                    effective_qty=0.0,
                    execution_latency_us=lat_us
                )
            effective_qty = float(min(order.order_qty, allowed_room))
        else:
            effective_qty = order.order_qty

        # ------------------------------------------------------------- Barrier 4: Fallback State Machine
        if s_upper >= 1.0:
            # RED: Mandatory Abstention triggered!
            self.abstentions_count += 1
            lat_us = (time.perf_counter_ns() - t0) / 1000.0
            
            # In RED state: aggressive market orders are completely banned
            if order.order_type in ["MARKET", "IOC"]:
                self.rejections_count += 1
                return InterceptDecision(
                    is_allowed=False,
                    state=AMIPState.RED,
                    rejection_code=RejectionCode.MANDATORY_ABSTENTION_ACTIVE,
                    rejection_reason=(
                        f"MANDATORY ABSTENTION ACTIVE (S_upper = {s_upper:.3f} >= 1.0). "
                        f"Aggressive liquidity-taking forbidden to prevent cascade."
                    ),
                    s_hat=s_hat, s_lower=s_lower, s_upper=s_upper,
                    kreiss_safe_radius=kreiss_radius,
                    effective_qty=0.0,
                    execution_latency_us=lat_us
                )
            else:
                # Limit orders converted to passive pegged liquidity
                lat_us = (time.perf_counter_ns() - t0) / 1000.0
                return InterceptDecision(
                    is_allowed=True,
                    state=AMIPState.RED,
                    rejection_code=RejectionCode.NONE,
                    rejection_reason="Pegged passive liquidity only under Mandatory Abstention.",
                    s_hat=s_hat, s_lower=s_lower, s_upper=s_upper,
                    kreiss_safe_radius=kreiss_radius,
                    effective_qty=effective_qty * 0.25,  # 75% size reduction
                    execution_latency_us=lat_us
                )

        elif s_upper >= 0.95:
            # YELLOW: Throttle orders by 50%
            self.throttled_count += 1
            lat_us = (time.perf_counter_ns() - t0) / 1000.0
            effective_qty = float(effective_qty * 0.50)
            return InterceptDecision(
                is_allowed=True,
                state=AMIPState.YELLOW,
                rejection_code=RejectionCode.NONE,
                rejection_reason="Throttled by 50% due to pre-critical conic proximity (0.95 <= S_upper < 1.0).",
                s_hat=s_hat, s_lower=s_lower, s_upper=s_upper,
                kreiss_safe_radius=kreiss_radius,
                effective_qty=effective_qty,
                execution_latency_us=lat_us
            )

        else:
            # GREEN: Full execution authorized
            lat_us = (time.perf_counter_ns() - t0) / 1000.0
            return InterceptDecision(
                is_allowed=True,
                state=AMIPState.GREEN,
                rejection_code=RejectionCode.NONE,
                rejection_reason="Authorized within stable conic bounds.",
                s_hat=s_hat, s_lower=s_lower, s_upper=s_upper,
                kreiss_safe_radius=kreiss_radius,
                effective_qty=effective_qty,
                execution_latency_us=lat_us
            )

    def record_fill(self, executed_qty: float, executed_price: float, side: str):
        """Update internal balance sheet post-execution."""
        signed_qty = executed_qty if side.upper() == "BUY" else -executed_qty
        self.inventory += signed_qty
        self.cash -= signed_qty * executed_price
        self.equity = self.cash + self.inventory * executed_price
