from __future__ import annotations

from mm_next.agents import AdaptiveLinearAgent
from mm_next.interventions import evaluate_interventions
from mm_next.market import MarketConfig


def test_intervention_report_has_paired_out_of_sample_targets() -> None:
    report = evaluate_interventions(
        MarketConfig(horizon=8, max_order=1.0, max_inventory=1.0),
        AdaptiveLinearAgent(),
        episodes=3,
        seed=41,
    )
    assert report["paired_tape"] is True
    assert set(report["policies"]) == {"none", "throttle", "liquidate"}
    assert all("event_rate" in row for row in report["policies"].values())
