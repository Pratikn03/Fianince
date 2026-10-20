"""Unit tests for Theorem E global optimizer and abstention behavior (T06)."""
from research_extension.information_safety.model_contracts import BalanceSheetContract
from research_extension.information_safety.robust_admission import (
    closed_form_optimal_admission,
    solve_balance_sheet_guard_globally,
)


def test_robust_optimizer_and_abstention():
    # Feasible interior case
    res = closed_form_optimal_admission(
        a_lower=0.40,
        q_upper=0.42,
        kappa_upper=1.0,
        budget_rem=1.0,
        reserve_safe=0.0,
        inventory_abs=1.0,
        shock_u=0.36,
    )
    assert res["abstain"] is False
    # 0.60 - alpha*0.42 = 0.36 => alpha* = 0.24 / 0.42 = 4/7
    assert abs(res["alpha_star"] - (0.24 / 0.42)) < 1e-9

    # Infeasible at alpha=0 -> ABSTAIN
    res_infeas = closed_form_optimal_admission(
        a_lower=0.40,
        q_upper=0.42,
        kappa_upper=1.0,
        budget_rem=1.0,
        reserve_safe=0.0,
        inventory_abs=1.0,
        shock_u=0.75,
    )
    assert res_infeas["abstain"] is True
    assert res_infeas["status"] == "ABSTAIN_INFEASIBLE_AT_ZERO"


if __name__ == "__main__":
    test_robust_optimizer_and_abstention()
    print("[PASS] test_robust_optimizer.py")
