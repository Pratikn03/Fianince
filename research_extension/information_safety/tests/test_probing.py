"""Proposition prop:probe: the anytime-valid sequential certificate keeps its error level under optional stopping."""
from adaptive_probing import simulate


def test_sequential_error_level():
    for S in (1.9, 1.95, 2.05, 2.1):
        r = simulate(S, 2.0, 0.17, reps=300, seed=int(100 * S))
        assert r["error_rate"] <= 0.05
