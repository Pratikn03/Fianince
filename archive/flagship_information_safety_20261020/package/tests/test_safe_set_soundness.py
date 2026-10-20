"""Blueprint Section G test: test_safe_set_soundness.py (D3, E03)."""
from research_extension.information_safety.tests.test_confidence_coverage import (
    test_confidence_coverage_and_false_certification,
)


def test_safe_set_soundness():
    test_confidence_coverage_and_false_certification()


if __name__ == "__main__":
    test_safe_set_soundness()
    print("[PASS] test_safe_set_soundness.py")
