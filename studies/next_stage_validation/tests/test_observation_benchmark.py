from __future__ import annotations

from mm_next.observation_benchmark import ObservationBenchmarkConfig, run_condition


def test_observation_benchmark_reports_coverage_and_unresolved_fraction() -> None:
    result = run_condition(
        ObservationBenchmarkConfig(replicates=8, episodes=12, horizon=6, seed=9),
        dependent=True,
        noise_sd=0.1,
    )
    assert result["replicates"] == 8
    assert 0 <= result["coverage"] <= 1
    assert 0 <= result["unresolved_fraction"] <= 1
