"""Blueprint Section G test: test_balance_sheet_accounting.py (D7, E05)."""
from research_extension.information_safety.tests.test_balance_sheet import test_balance_sheet_solvency_contract


def test_balance_sheet_accounting():
    test_balance_sheet_solvency_contract()


if __name__ == "__main__":
    test_balance_sheet_accounting()
    print("[PASS] test_balance_sheet_accounting.py")
