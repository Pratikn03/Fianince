"""Blueprint Section G test: test_witness_exact.py (D2, E01)."""
from research_extension.information_safety.tests.test_exact_witness import test_exact_witness_rational_values


def test_witness_exact():
    test_exact_witness_rational_values()


if __name__ == "__main__":
    test_witness_exact()
    print("[PASS] test_witness_exact.py")
