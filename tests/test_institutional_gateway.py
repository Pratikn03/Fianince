"""
Unit & Integration Tests for Institutional AMIP Pre-Trade Risk Gateway
======================================================================
Machine Markets — Autonomous Market Infrastructure Protocol (AMIP RFC-001)
"""
from __future__ import annotations
import json
import numpy as np
import pytest

from agentic_guard.core import (
    AMIPState, RejectionCode, AgentOrder
)
from agentic_guard.institutional_gateway import (
    InstitutionalAMIPGateway, GatewayAuditRecord
)
from agentic_guard.llm_tools import (
    ProviderFormat, parse_llm_tool_call, generate_adversarial_suite,
    OPENAI_TOOL_SCHEMA, ANTHROPIC_TOOL_SCHEMA, GEMINI_TOOL_SCHEMA
)


class TestInstitutionalGateway:
    @pytest.fixture
    def gateway(self):
        return InstitutionalAMIPGateway(
            equity=10_000_000.0,
            kreiss_constant_J=3.42,
            buffer_ratio=0.30,
            max_price_deviation_pct=0.03
        )

    def test_tool_schemas_valid(self):
        assert OPENAI_TOOL_SCHEMA["type"] == "function"
        assert OPENAI_TOOL_SCHEMA["function"]["name"] == "amip_place_order"
        assert ANTHROPIC_TOOL_SCHEMA["name"] == "amip_place_order"
        assert len(GEMINI_TOOL_SCHEMA["function_declarations"]) == 1

    def test_openai_tool_parsing_and_execution(self, gateway):
        payload = {
            "type": "function",
            "function": {
                "name": "amip_place_order",
                "arguments": json.dumps({
                    "symbol": "BTC-USDT",
                    "side": "BUY",
                    "quantity": 2.5,
                    "price": 17180.0,
                    "order_type": "LIMIT",
                    "reasoning_summary": "Rebalancing test"
                })
            }
        }
        dec, record = gateway.process_tool_payload(
            payload=payload,
            current_mid=17180.0,
            provider=ProviderFormat.OPENAI,
            agent_id="GPT4O_DESK"
        )
        assert dec.is_allowed is True
        assert dec.rejection_code == RejectionCode.NONE
        assert dec.effective_qty == 2.5
        assert record is not None
        assert record.decision_allowed is True
        assert len(record.provenance_hash) == 64

    def test_anthropic_tool_parsing(self, gateway):
        payload = {
            "name": "amip_place_order",
            "input": {
                "symbol": "BTC-USDT",
                "side": "SELL",
                "quantity": 1.2,
                "price": 17180.0,
                "order_type": "LIMIT"
            }
        }
        dec, record = gateway.process_tool_payload(
            payload=payload,
            current_mid=17180.0,
            provider=ProviderFormat.ANTHROPIC,
            agent_id="CLAUDE_DESK"
        )
        assert dec.is_allowed is True
        assert dec.effective_qty == 1.2

    def test_gemini_tool_parsing(self, gateway):
        payload = {
            "args": {
                "symbol": "BTC-USDT",
                "side": "BUY",
                "quantity": 3.0,
                "price": 17180.0,
                "order_type": "PEGGED"
            }
        }
        dec, record = gateway.process_tool_payload(
            payload=payload,
            current_mid=17180.0,
            provider=ProviderFormat.GEMINI,
            agent_id="GEMINI_DESK"
        )
        assert dec.is_allowed is True
        assert dec.effective_qty == 3.0

    def test_hallucination_price_deviation_rejection(self, gateway):
        payload = {
            "symbol": "BTC-USDT",
            "side": "BUY",
            "quantity": 1.0,
            "price": 15000.0,  # ~12.7% deviation
            "order_type": "LIMIT"
        }
        dec, record = gateway.process_tool_payload(
            payload=payload,
            current_mid=17180.0,
            provider=ProviderFormat.RAW,
            agent_id="ROGUE_LLM"
        )
        assert dec.is_allowed is False
        assert dec.rejection_code == RejectionCode.HALLUCINATION_PRICE_DEVIATION
        assert record.decision_allowed is False
        assert "Hallucination rejected" in dec.rejection_reason

    def test_adversarial_suite(self, gateway):
        current_mid = 17180.0
        scenarios = generate_adversarial_suite(current_mid=current_mid)
        for sc in scenarios:
            if sc.scenario_id == "ADV_05_SUPERCRITICAL_MOMENTUM_RUNAWAY":
                gateway.update_market_state(s_hat=1.20, s_lower=1.10, s_upper=1.30)
                gateway.guard.inventory = 0.0
            elif sc.scenario_id == "ADV_01_FAT_FINGER_QTY":
                gateway.update_market_state(s_hat=0.70, s_lower=0.65, s_upper=0.75)
                gateway.guard.inventory = gateway.guard.compute_kreiss_safe_radius(current_mid) + 5.0
            else:
                gateway.update_market_state(s_hat=0.70, s_lower=0.65, s_upper=0.75)
                gateway.guard.inventory = 0.0

            dec, record = gateway.process_tool_payload(
                payload=sc.raw_payload,
                current_mid=current_mid,
                provider=sc.provider,
                agent_id="ADVERSARIAL_TEST"
            )
            assert dec.rejection_code.value == sc.expected_rejection_code, (
                f"Scenario {sc.scenario_id} failed: expected {sc.expected_rejection_code}, got {dec.rejection_code.value}"
            )

    def test_cryptographic_audit_chain(self, gateway):
        current_mid = 17180.0
        for i in range(10):
            payload = {
                "symbol": "BTC-USDT",
                "side": "BUY",
                "quantity": 1.0 + i,
                "price": current_mid,
                "order_type": "LIMIT"
            }
            gateway.process_tool_payload(payload, current_mid=current_mid)

        assert len(gateway.audit_log) == 10
        # Verify hashes are unique and non-empty
        hashes = [r.provenance_hash for r in gateway.audit_log]
        assert len(set(hashes)) == 10
        assert all(len(h) == 64 for h in hashes)

    def test_latency_profile_sub_100us(self, gateway):
        current_mid = 17180.0
        payload = {
            "symbol": "BTC-USDT",
            "side": "BUY",
            "quantity": 1.0,
            "price": current_mid,
            "order_type": "LIMIT"
        }
        for _ in range(500):
            gateway.process_tool_payload(payload, current_mid=current_mid)

        prof = gateway.get_latency_profile()
        assert prof["n_orders"] >= 500
        # Gateway latency should be institutional grade (< 100 µs, typically < 10 µs)
        assert prof["mean_us"] < 100.0
        assert prof["p90_us"] < 100.0
