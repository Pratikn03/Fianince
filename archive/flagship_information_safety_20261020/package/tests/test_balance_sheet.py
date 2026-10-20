"""Unit tests for full post-trade balance-sheet solvency contract (Theorem 5.4 & Theorem E, T06)."""
from research_extension.information_safety.model_contracts import BalanceSheetContract
from research_extension.information_safety.robust_admission import solve_balance_sheet_guard_globally


def test_balance_sheet_solvency_contract():
    bs = BalanceSheetContract(
        equity_E0=10000.0,
        inventory_I0=-2000.0,
        mark_price_P=100.0,
        maintenance_margin_mu=0.005,
        reserve_R_safe=950.0,
        max_fill_u=200.0,
        hedge_capacity_H=100.0,
        exec_cost_rate=0.02,
    )
    assert abs(bs.initial_buffer_B_rem - 9050.0) < 1e-9
    # Available buffer after reserve = 9050 - 950 = 8100.
    # At alpha = 0, post_trade_inventory(0) = 2000, (1+mu)*2000 = 2010, so max admissible price shock = 8100/2010 = 4.02985...
    res_safe = solve_balance_sheet_guard_globally(
        bs=bs, state_norm_z=0.0, a_lower=0.40, q_upper=0.20, kappa_upper=1.0, shock_u_step=1.80
    )
    assert res_safe["abstain"] is False
    assert res_safe["is_monotone_interval"] is True
    assert res_safe["loss_at_alpha_star"] <= res_safe["available_buffer"] + 1e-6

    res_breach = solve_balance_sheet_guard_globally(
        bs=bs, state_norm_z=0.0, a_lower=0.40, q_upper=0.20, kappa_upper=1.0, shock_u_step=2.50
    )
    assert res_breach["abstain"] is True


if __name__ == "__main__":
    test_balance_sheet_solvency_contract()
    print("[PASS] test_balance_sheet.py")
