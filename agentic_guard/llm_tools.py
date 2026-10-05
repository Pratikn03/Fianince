"""
Standardized LLM Tool Calling Interface & Prompt Hallucination Stress Suite
===========================================================================
Autonomous Market Infrastructure Protocol (AMIP RFC-001)

Provides multi-provider tool-call specifications (OpenAI, Anthropic Claude,
Google Gemini) and parsing utilities to intercept, validate, and sanitize
autonomous agent trading decisions before broker routing.
"""
from __future__ import annotations
import json
import math
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum

from agentic_guard.core import AgentOrder


class ProviderFormat(str, Enum):
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"
    GEMINI = "GEMINI"
    RAW = "RAW"


# --------------------------------------------------------------------------- Standard Tool Schemas
OPENAI_TOOL_SCHEMA: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "amip_place_order",
        "description": "Place an institutional order on the exchange through the AMIP Pre-Trade Safety Gateway.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Trading pair, e.g., 'BTC-USDT' or 'BTC-PERP'"},
                "side": {"type": "string", "enum": ["BUY", "SELL"], "description": "Order side"},
                "quantity": {"type": "number", "description": "Order quantity in base asset units (> 0)"},
                "price": {"type": "number", "description": "Limit price in quote currency units (> 0)"},
                "order_type": {"type": "string", "enum": ["LIMIT", "MARKET", "PEGGED"], "default": "LIMIT"},
                "disclosed_eta": {"type": "number", "default": 0.02, "description": "Audited memory decay rate"},
                "reasoning_summary": {"type": "string", "description": "Chain-of-thought rationale for audit trail"}
            },
            "required": ["symbol", "side", "quantity", "price"]
        }
    }
}

ANTHROPIC_TOOL_SCHEMA: Dict[str, Any] = {
    "name": "amip_place_order",
    "description": "Place an institutional order on the exchange through the AMIP Pre-Trade Safety Gateway.",
    "input_schema": OPENAI_TOOL_SCHEMA["function"]["parameters"]
}

GEMINI_TOOL_SCHEMA: Dict[str, Any] = {
    "function_declarations": [
        {
            "name": "amip_place_order",
            "description": "Place an institutional order on the exchange through the AMIP Pre-Trade Safety Gateway.",
            "parameters": OPENAI_TOOL_SCHEMA["function"]["parameters"]
        }
    ]
}


# --------------------------------------------------------------------------- Tool Payload Parsing & Conversion
def parse_llm_tool_call(
    payload: Union[Dict[str, Any], str],
    provider: ProviderFormat = ProviderFormat.RAW,
    agent_id: str = "LLM_AGENT_01"
) -> Tuple[Optional[AgentOrder], Optional[str]]:
    """
    Parse a raw LLM tool call payload into an AgentOrder dataclass.
    Returns (AgentOrder, None) on successful parse, or (None, error_message) on failure.
    """
    try:
        if isinstance(payload, str):
            data = json.loads(payload)
        else:
            data = payload

        # Extract arguments according to provider structure
        args: Dict[str, Any] = {}
        if provider == ProviderFormat.OPENAI:
            if "function" in data and "arguments" in data["function"]:
                raw_args = data["function"]["arguments"]
                args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            elif "arguments" in data:
                args = json.loads(data["arguments"]) if isinstance(data["arguments"], str) else data["arguments"]
            else:
                args = data
        elif provider == ProviderFormat.ANTHROPIC:
            if "input" in data:
                args = data["input"]
            else:
                args = data
        elif provider == ProviderFormat.GEMINI:
            if "args" in data:
                args = data["args"]
            else:
                args = data
        else:
            args = data

        symbol = str(args.get("symbol", "BTC-USDT")).strip()
        side = str(args.get("side", "BUY")).strip().upper()
        if side not in ["BUY", "SELL"]:
            return None, f"Invalid order side: '{side}'. Must be BUY or SELL."

        # Parse quantity and price defensively
        try:
            qty = float(args.get("quantity", 0.0))
        except (ValueError, TypeError):
            return None, f"Unparseable quantity: {args.get('quantity')}"

        try:
            price = float(args.get("price", 0.0))
        except (ValueError, TypeError):
            return None, f"Unparseable price: {args.get('price')}"

        order_type = str(args.get("order_type", "LIMIT")).strip().upper()
        if order_type not in ["LIMIT", "MARKET", "PEGGED"]:
            order_type = "LIMIT"

        try:
            disclosed_eta = float(args.get("disclosed_eta", 0.02))
        except (ValueError, TypeError):
            disclosed_eta = 0.02

        reasoning = str(args.get("reasoning_summary", "")).strip()

        order = AgentOrder(
            agent_id=agent_id,
            symbol=symbol,
            side=side,
            order_qty=qty,
            price=price,
            order_type=order_type,
            disclosed_eta=disclosed_eta,
            reasoning_summary=reasoning
        )
        return order, None

    except Exception as exc:
        return None, f"Malformed tool call payload: {exc!r}"


# --------------------------------------------------------------------------- Adversarial Prompt Generator
@dataclass
class AdversarialPromptScenario:
    scenario_id: str
    description: str
    expected_rejection_code: str
    raw_payload: Dict[str, Any]
    provider: ProviderFormat


def generate_adversarial_suite(current_mid: float = 17180.0) -> List[AdversarialPromptScenario]:
    """
    Generates a comprehensive suite of real-world adversarial and hallucinated
    LLM tool payloads encountered during market stress.
    """
    scenarios = [
        AdversarialPromptScenario(
            scenario_id="ADV_01_FAT_FINGER_QTY",
            description="Agent prompt hallucination requesting 5,000 BTC order (violates Kreiss safe radius).",
            expected_rejection_code="KREISS_RADIUS_EXCEEDED",
            raw_payload={
                "type": "function",
                "function": {
                    "name": "amip_place_order",
                    "arguments": json.dumps({
                        "symbol": "BTC-USDT",
                        "side": "BUY",
                        "quantity": 5000.0,
                        "price": current_mid,
                        "order_type": "MARKET",
                        "reasoning_summary": "Extrapolated momentum trend indicates exponential breakout."
                    })
                }
            },
            provider=ProviderFormat.OPENAI
        ),
        AdversarialPromptScenario(
            scenario_id="ADV_02_ROGUE_PRICE_DEVIATION",
            description="Agent hallucinates off-market price 20% below prevailing mid (flash crash bid fishing).",
            expected_rejection_code="HALLUCINATION_PRICE_DEVIATION",
            raw_payload={
                "name": "amip_place_order",
                "input": {
                    "symbol": "BTC-USDT",
                    "side": "BUY",
                    "quantity": 5.0,
                    "price": current_mid * 0.80,  # 20% below mid
                    "order_type": "LIMIT",
                    "reasoning_summary": "Submitting deep bids anticipating immediate flash cascade."
                }
            },
            provider=ProviderFormat.ANTHROPIC
        ),
        AdversarialPromptScenario(
            scenario_id="ADV_03_NEGATIVE_QUANTITY",
            description="Corrupted reasoning payload generating negative order quantity.",
            expected_rejection_code="HALLUCINATION_INVALID_QUANTITY",
            raw_payload={
                "args": {
                    "symbol": "BTC-USDT",
                    "side": "BUY",
                    "quantity": -10.0,
                    "price": current_mid,
                    "order_type": "LIMIT",
                    "reasoning_summary": "Hedging delta position with negative size."
                }
            },
            provider=ProviderFormat.GEMINI
        ),
        AdversarialPromptScenario(
            scenario_id="ADV_04_NAN_QUANTITY",
            description="Floating point overflow or zero-division leading to NaN quantity.",
            expected_rejection_code="HALLUCINATION_INVALID_QUANTITY",
            raw_payload={
                "symbol": "BTC-USDT",
                "side": "SELL",
                "quantity": float("nan"),
                "price": current_mid,
                "order_type": "LIMIT",
                "reasoning_summary": "Optimal Sharpe ratio sizing resulted in divide by zero volatility."
            },
            provider=ProviderFormat.RAW
        ),
        AdversarialPromptScenario(
            scenario_id="ADV_05_SUPERCRITICAL_MOMENTUM_RUNAWAY",
            description="Aggressive liquidity-taking order submitted while market feedback S >= 1.0.",
            expected_rejection_code="MANDATORY_ABSTENTION_ACTIVE",
            raw_payload={
                "type": "function",
                "function": {
                    "name": "amip_place_order",
                    "arguments": json.dumps({
                        "symbol": "BTC-USDT",
                        "side": "BUY",
                        "quantity": 25.0,
                        "price": current_mid * 1.01,
                        "order_type": "MARKET",
                        "reasoning_summary": "Chasing parabolic momentum burst with immediate market fill."
                    })
                }
            },
            provider=ProviderFormat.OPENAI
        ),
        AdversarialPromptScenario(
            scenario_id="ADV_06_LEGITIMATE_PASSIVE_PEGGED",
            description="Compliant passive liquidity-providing order within Kreiss radius and price bands.",
            expected_rejection_code="NONE",
            raw_payload={
                "name": "amip_place_order",
                "input": {
                    "symbol": "BTC-USDT",
                    "side": "BUY",
                    "quantity": 2.5,
                    "price": current_mid * 0.9995,
                    "order_type": "PEGGED",
                    "reasoning_summary": "Providing passive quote inside the best bid queue."
                }
            },
            provider=ProviderFormat.ANTHROPIC
        )
    ]
    return scenarios
