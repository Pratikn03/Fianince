"""
AgenticGuard — Universal Pre-Trade Safety SDK for Autonomous Financial AI
=========================================================================
Machine Markets — Reference Implementation of AMIP RFC-001

A drop-in zero-trust interceptor that protects financial institutions, trading
desks, and clearing members against autonomous agentic AI hallucinations,
momentum feedback runaway (S >= 1.0), and nonnormal liquidation cascades.

Usage:
  from agentic_guard import AgenticGuard, AgentOrder

  guard = AgenticGuard(equity=10_000_000, kreiss_constant=3.42)
  decision = guard.intercept(order)
  if decision.is_allowed:
      execute_order(decision.effective_order)
  else:
      log_rejection(decision.rejection_reason)
"""
from __future__ import annotations

from agentic_guard.core import (
    AgenticGuard,
    AgentOrder,
    InterceptDecision,
    AMIPState,
    RejectionCode
)

__version__ = "1.0.0"
__all__ = [
    "AgenticGuard",
    "AgentOrder",
    "InterceptDecision",
    "AMIPState",
    "RejectionCode",
]
