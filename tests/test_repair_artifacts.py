from fractions import Fraction as F
import pytest


def test_exact_witness_recurrence_matches_rational_table():
    from research_extension.evidence_repair.render_artifacts import exact_witness
    stable, unstable = exact_witness()
    assert stable[:4] == unstable[:4] == [F(1), F(2,5), F(82,325), F(23,125)]
    assert float(stable[4]) == pytest.approx(.1384284023668639)
    assert float(unstable[4]) == pytest.approx(.1591976331360947)


def test_known_total_does_not_replace_known_rate_with_one_channel():
    # U=[1,0], Q=.4, two different (eta,q) produce b=.06.
    assert F(1,5)*F(3,10) == F(3,10)*F(1,5) == F(3,50)
    assert F(3,10)+F(1,10) == F(1,5)+F(1,5)
