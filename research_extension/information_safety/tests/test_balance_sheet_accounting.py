"""Theorem thm:forward: the guard inequality keeps the buffer above the reserve for every move within the envelope."""
from economic_ledger import run_balance_sheet, buffer, admissible_shock_alpha0


def test_scenario_numbers():
    r = run_balance_sheet(cases=2000)
    sc = r["scenario"]
    assert abs(sc["admissible_shock"] - 8100 / 2010) < 1e-12 and sc["reserve_violated_at_4.05"] and sc["reserve_kept_at_4.02"]
    assert r["violations"] == 0
