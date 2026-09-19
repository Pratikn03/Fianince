from __future__ import annotations

import numpy as np

from mm_next.market import MarketConfig, SyntheticMarket


def test_step_reconciles_inventory_cash_and_fees() -> None:
    env = SyntheticMarket(MarketConfig(horizon=4, seed=7, partial_fill=0.25))
    observation = env.reset()
    assert observation.shape == (7,)

    before_cash = env.cash
    before_inventory = env.inventory
    result = env.step(0.5)

    assert abs(env.inventory - before_inventory - result.filled_quantity) < 1e-12
    expected_cash = before_cash - result.filled_quantity * result.execution_price - result.fees
    assert abs(env.cash - expected_cash) < 1e-12
    assert abs(result.filled_quantity) <= 0.5 + 1e-12
    assert np.isfinite(result.mark_to_market_equity)


def test_margin_breach_is_reported_and_episode_stops() -> None:
    env = SyntheticMarket(
        MarketConfig(
            horizon=5,
            seed=2,
            max_inventory=0.2,
            margin_rate=0.9,
            maintenance_margin=0.01,
            partial_fill=0.0,
        )
    )
    env.reset()
    result = env.step(1.0)
    assert result.event in {"margin_breach", "halt", "default"}
    assert result.done