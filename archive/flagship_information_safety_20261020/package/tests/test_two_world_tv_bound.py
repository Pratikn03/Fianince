"""Blueprint Section G test: test_two_world_tv_bound.py (D4, D5, E02)."""
from research_extension.information_safety.tests.test_two_world_bound import (
    test_two_world_bound_and_sample_complexity,
)


def test_two_world_tv_bound():
    test_two_world_bound_and_sample_complexity()


if __name__ == "__main__":
    test_two_world_tv_bound()
    print("[PASS] test_two_world_tv_bound.py")
