"""Pytest integration for Flagship Paper 2 Information-Safety Extension (T01-T12)."""
from research_extension.information_safety.tests.test_exact_witness import test_exact_witness_rational_values
from research_extension.information_safety.tests.test_convolution_gain import test_convolution_gain_horizons_1_to_8
from research_extension.information_safety.tests.test_confidence_coverage import (
    test_confidence_coverage_and_false_certification,
)
from research_extension.information_safety.tests.test_two_world_bound import (
    test_two_world_bound_and_sample_complexity,
)
from research_extension.information_safety.tests.test_robust_optimizer import test_robust_optimizer_and_abstention
from research_extension.information_safety.tests.test_balance_sheet import test_balance_sheet_solvency_contract


def test_all_flagship_information_safety_checks():
    test_exact_witness_rational_values()
    test_convolution_gain_horizons_1_to_8()
    test_confidence_coverage_and_false_certification()
    test_two_world_bound_and_sample_complexity()
    test_robust_optimizer_and_abstention()
    test_balance_sheet_solvency_contract()
