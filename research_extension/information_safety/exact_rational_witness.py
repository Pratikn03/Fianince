"""Exact rational construction of the Two-Market Ambiguity Witness and Theorem A lower bound (T01, T02)."""
from __future__ import annotations
from fractions import Fraction
import numpy as np
from .model_contracts import PositiveMemoryMarket
from .price_response import exact_impulse_response, closed_to_open_moments_rational, transition_matrix_float


def build_witness_markets() -> tuple[PositiveMemoryMarket, PositiveMemoryMarket]:
    """Construct Market A and Market B from Section 1 of the Flagship Upgrade Blueprint."""
    market_A = PositiveMemoryMarket(
        name="Market A (Single Moderate Cohort)",
        a=Fraction(2, 5),          # 0.40
        etas=(Fraction(1, 2),),    # 0.50
        qs=(Fraction(2, 25),),     # 0.08
    )
    market_B = PositiveMemoryMarket(
        name="Market B (Fast + Slow Cohort Pair)",
        a=Fraction(2, 5),                       # 0.40
        etas=(Fraction(1, 1), Fraction(1, 20)), # 1.00, 0.05
        qs=(Fraction(1, 50), Fraction(2, 5)),   # 0.02, 0.40
    )
    return market_A, market_B


def theorem_A_capacity_loss_bound(
    v0: Fraction, v1: Fraction, beta: Fraction, d_tv: Fraction = Fraction(0, 1)
) -> Fraction:
    """Compute (v1 - v0) * max(0, 1 - beta - d_tv) in exact rational arithmetic."""
    if v1 <= v0:
        raise ValueError("Require v0 < v1")
    factor = max(Fraction(0, 1), Fraction(1, 1) - beta - d_tv)
    return (v1 - v0) * factor


def verify_witness_and_theorem_A(max_lag: int = 12) -> dict:
    """Run exact rational verification of Market A vs Market B and Theorem A (T01 & T02)."""
    mA, mB = build_witness_markets()
    hA = exact_impulse_response(mA, max_lag=max_lag)
    hB = exact_impulse_response(mB, max_lag=max_lag)

    # Exact assertions from Section 1 of the Blueprint
    assert mA.total_feedback_Q == Fraction(2, 25)      # 0.08
    assert mB.total_feedback_Q == Fraction(21, 50)     # 0.42
    assert hA[0] == hB[0] == Fraction(1, 1)            # 1.00
    assert hA[1] == hB[1] == Fraction(2, 5)            # 0.40
    assert hA[2] == hB[2] == Fraction(1, 5)            # 0.20
    assert hA[3] == Fraction(29, 250)                  # 0.116
    assert hB[3] == Fraction(23, 200)                  # 0.115
    assert hA[3] - hB[3] == Fraction(1, 1000)          # 0.001
    assert mA.long_run_gain == Fraction(25, 13)        # 1.9230769...
    assert mB.long_run_gain == Fraction(50, 9)         # 5.5555556...
    assert mA.max_per_period_shock() == Fraction(13, 25) # 0.52
    assert mB.max_per_period_shock() == Fraction(9, 50)  # 0.18

    # Check open-loop moments
    momA = closed_to_open_moments_rational(hA[:4], mA.a)
    momB = closed_to_open_moments_rational(hB[:4], mB.a)
    assert momA[0] == momB[0] == Fraction(1, 25)       # m_0 = 0.04
    assert momA[1] == Fraction(1, 50)                  # m_1^A = 0.020
    assert momB[1] == Fraction(19, 1000)               # m_1^B = 0.019

    # Check spectral stability
    rho_A = float(np.max(np.abs(np.linalg.eigvals(transition_matrix_float(mA)))))
    rho_B = float(np.max(np.abs(np.linalg.eigvals(transition_matrix_float(mB)))))
    assert rho_A < 1.0 and rho_B < 1.0

    # Theorem A exact bound at beta = 0.05 = 1/20, d_TV = 0
    v0 = mB.max_per_period_shock()  # 9/50 = 0.18
    v1 = mA.max_per_period_shock()  # 13/25 = 0.52
    beta = Fraction(1, 20)          # 0.05
    loss_bound = theorem_A_capacity_loss_bound(v0, v1, beta, Fraction(0, 1))
    assert loss_bound == Fraction(323, 1000)  # 0.323

    return {
        "market_A": {
            "Q": str(mA.total_feedback_Q),
            "Q_float": float(mA.total_feedback_Q),
            "h_0_to_5": [float(x) for x in hA[:6]],
            "h_0_to_3_rational": [str(x) for x in hA[:4]],
            "long_run_gain_rational": str(mA.long_run_gain),
            "long_run_gain_float": round(float(mA.long_run_gain), 6),
            "v_max_rational": str(v1),
            "v_max_float": float(v1),
            "spectral_radius": round(rho_A, 6),
        },
        "market_B": {
            "Q": str(mB.total_feedback_Q),
            "Q_float": float(mB.total_feedback_Q),
            "h_0_to_5": [float(x) for x in hB[:6]],
            "h_0_to_3_rational": [str(x) for x in hB[:4]],
            "long_run_gain_rational": str(mB.long_run_gain),
            "long_run_gain_float": round(float(mB.long_run_gain), 6),
            "v_max_rational": str(v0),
            "v_max_float": float(v0),
            "spectral_radius": round(rho_B, 6),
        },
        "lag_3_difference_rational": str(hA[3] - hB[3]),
        "lag_3_difference_float": float(hA[3] - hB[3]),
        "theorem_A": {
            "v0": float(v0),
            "v1": float(v1),
            "beta": float(beta),
            "d_tv": 0.0,
            "min_expected_capacity_loss_rational": str(loss_bound),
            "min_expected_capacity_loss_float": float(loss_bound),
        },
        "impulse_series_A": [float(x) for x in hA],
        "impulse_series_B": [float(x) for x in hB],
    }
