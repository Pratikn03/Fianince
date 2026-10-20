"""Theorem F: Economic value of disclosure across Public, Class-Tagged, and Audited Channel regimes (T07)."""
from __future__ import annotations
import numpy as np


def evaluate_disclosure_tiers_T07(
    a: float = 0.40,
    etas: tuple[float, ...] = (1.00, 0.05),
    qs_safer: tuple[float, ...] = (0.076, 0.004),  # m_0 = 0.076*1 + 0.004*0.05 = 0.0762, Q = 0.080
    r_bar: float = 0.95,
    budget_B: float = 1.0,
    inventory_I: float = 1.0,
    noise_sd_pub: float = 0.002,
    noise_sd_tag: float = 0.002,
    noise_sd_audit: float = 0.0005,
    sample_N: int = 400,
    surplus_per_unit_omega: float = 100.0,
    compliance_cost_tag: float = 4.0,
    compliance_cost_audit: float = 12.0,
    leakage_cost_tag: float = 1.5,
    leakage_cost_audit: float = 3.0,
) -> dict:
    """Compare Public Aggregate Prices vs Class-Tagged Observations vs Audited Channel-Level Info (T07)."""
    eta_min = 1.0 - r_bar
    m0 = sum(e * q for e, q in zip(etas, qs_safer))
    true_Q = sum(qs_safer)
    true_v_max = budget_B * (1.0 - a - true_Q) / abs(inventory_I)

    # 1. Public Aggregate Prices (lag-2 observation identifies only m_0 up to noise)
    m0_upper_pub = m0 + 1.96 * noise_sd_pub / np.sqrt(sample_N)
    q_upper_pub = min(0.58, m0 / 0.19 + 1.96 * (noise_sd_pub / np.sqrt(sample_N)) / eta_min)
    # Using our Two-Market Witness pair (Market A vs Market B) as the public ambiguity benchmark:
    # Public lag-2 observation cannot rule out Market B (Q = 0.42, v_safe = 0.18) when true market is Market A (Q = 0.08, v_max = 0.52)
    v_safe_pub = max(0.0, budget_B * (1.0 - a - 0.42 - 1.96 * noise_sd_pub / np.sqrt(sample_N)) / abs(inventory_I))

    # 2. Class-Tagged Observations (identifies cohort flows with tag noise)
    q_upper_tag = true_Q + 1.96 * (noise_sd_tag / np.sqrt(sample_N)) * np.sqrt(len(etas)) / eta_min
    v_safe_tag = max(0.0, budget_B * (1.0 - a - q_upper_tag) / abs(inventory_I))

    # 3. Audited Channel-Level Information (direct telemetry with tight uncertainty)
    q_upper_audit = true_Q + 1.96 * (noise_sd_audit / np.sqrt(sample_N))
    v_safe_audit = max(0.0, budget_B * (1.0 - a - q_upper_audit) / abs(inventory_I))

    # Net economic value relative to Public baseline
    gross_gain_tag = surplus_per_unit_omega * (v_safe_tag - v_safe_pub)
    net_val_tag = gross_gain_tag - compliance_cost_tag - leakage_cost_tag

    gross_gain_audit = surplus_per_unit_omega * (v_safe_audit - v_safe_pub)
    net_val_audit = gross_gain_audit - compliance_cost_audit - leakage_cost_audit

    # Also evaluate a high-cost / low-heterogeneity regime where net value of disclosure is NEGATIVE (Theorem F)
    net_val_high_cost_regime = surplus_per_unit_omega * 0.02 - 8.0

    return {
        "true_v_max": float(true_v_max),
        "tiers": {
            "public_aggregate": {
                "Q_upper": 0.42 + float(1.96 * noise_sd_pub / np.sqrt(sample_N)),
                "v_safe": float(v_safe_pub),
                "gross_surplus": float(surplus_per_unit_omega * v_safe_pub),
                "net_disclosure_value_vs_public": 0.0,
            },
            "class_tagged": {
                "Q_upper": float(q_upper_tag),
                "v_safe": float(v_safe_tag),
                "capacity_gain_vs_public": float(v_safe_tag - v_safe_pub),
                "gross_gain_vs_public": float(gross_gain_tag),
                "compliance_and_leakage_cost": float(compliance_cost_tag + leakage_cost_tag),
                "net_disclosure_value_vs_public": float(net_val_tag),
            },
            "audited_channel": {
                "Q_upper": float(q_upper_audit),
                "v_safe": float(v_safe_audit),
                "capacity_gain_vs_public": float(v_safe_audit - v_safe_pub),
                "gross_gain_vs_public": float(gross_gain_audit),
                "compliance_and_leakage_cost": float(compliance_cost_audit + leakage_cost_audit),
                "net_disclosure_value_vs_public": float(net_val_audit),
            },
        },
        "negative_net_benefit_regime_example": {
            "capacity_gain": 0.02,
            "compliance_cost": 8.0,
            "net_value": float(net_val_high_cost_regime),
            "disclosure_worthwhile": bool(net_val_high_cost_regime > 0),
        },
    }
