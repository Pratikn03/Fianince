"""Unit tests for the Exact Rational Two-Market Ambiguity Witness (T01)."""
from fractions import Fraction
from research_extension.information_safety.exact_rational_witness import (
    build_witness_markets,
    verify_witness_and_theorem_A,
)
from research_extension.information_safety.price_response import exact_impulse_response


def test_exact_witness_rational_values():
    res = verify_witness_and_theorem_A(max_lag=10)
    mA, mB = build_witness_markets()
    hA = exact_impulse_response(mA, max_lag=5)
    hB = exact_impulse_response(mB, max_lag=5)
    assert hA[:3] == [Fraction(1, 1), Fraction(2, 5), Fraction(1, 5)]
    assert hB[:3] == [Fraction(1, 1), Fraction(2, 5), Fraction(1, 5)]
    assert hA[3] == Fraction(29, 250)
    assert hB[3] == Fraction(23, 200)
    assert mA.long_run_gain == Fraction(25, 13)
    assert mB.long_run_gain == Fraction(50, 9)
    assert mA.max_per_period_shock() == Fraction(13, 25)
    assert mB.max_per_period_shock() == Fraction(9, 50)
    assert res["theorem_A"]["min_expected_capacity_loss_rational"] == "323/1000"


if __name__ == "__main__":
    test_exact_witness_rational_values()
    print("[PASS] test_exact_witness.py")
