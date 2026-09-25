"""Reference package for Machine Markets mathematical supplement:
Mathematical repairs, continuous-time stability, and covariance-aware inference.
"""
from reference_directory.continuous import (
    build_continuous_matrix,
    is_metzler,
    is_hurwitz,
    spectral_radius,
    spectral_abscissa,
    hurwitz_threshold_spectral_radius,
    common_rate_spectral_abscissa_formula,
    forward_euler_parameters,
    forward_euler_matrix,
    max_admissible_euler_step,
    exact_sampled_matrix,
    euler_error_theoretical_bound,
    continuous_tail_bound,
)
from reference_directory.group import (
    verify_known_rate_identifiability,
    recover_unknown_rate_and_q,
    four_tap_aggregate_recovery,
    heterogeneous_vandermonde_recovery,
)
from reference_directory.ellipsoid import (
    hotelling_f_critical_value,
    estimate_ols_response_and_covariance,
    compute_mahalanobis_distance,
    is_in_ellipsoid,
    linear_contrast_support,
    get_four_coefficient_witness,
)
from reference_directory.conic import (
    compute_coordinate_bounds_from_ellipsoid,
    compute_data_derived_mass_cap,
    compute_rate_bin_envelopes,
    mccormick_envelopes,
    verify_conic_lift_containment,
    residual_corrected_dual_lower_bound,
)
from reference_directory.decisions import (
    classify_interval,
    compute_two_world_abstention_bound,
    simulate_solvency_shock,
)

__all__ = [
    "build_continuous_matrix",
    "is_metzler",
    "is_hurwitz",
    "spectral_radius",
    "spectral_abscissa",
    "hurwitz_threshold_spectral_radius",
    "common_rate_spectral_abscissa_formula",
    "forward_euler_parameters",
    "forward_euler_matrix",
    "max_admissible_euler_step",
    "exact_sampled_matrix",
    "euler_error_theoretical_bound",
    "continuous_tail_bound",
    "verify_known_rate_identifiability",
    "recover_unknown_rate_and_q",
    "four_tap_aggregate_recovery",
    "heterogeneous_vandermonde_recovery",
    "hotelling_f_critical_value",
    "estimate_ols_response_and_covariance",
    "compute_mahalanobis_distance",
    "is_in_ellipsoid",
    "linear_contrast_support",
    "get_four_coefficient_witness",
    "compute_coordinate_bounds_from_ellipsoid",
    "compute_data_derived_mass_cap",
    "compute_rate_bin_envelopes",
    "mccormick_envelopes",
    "verify_conic_lift_containment",
    "residual_corrected_dual_lower_bound",
    "classify_interval",
    "compute_two_world_abstention_bound",
    "simulate_solvency_shock",
]
