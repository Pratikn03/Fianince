"""Comprehensive error metrics audit and reporting module.

Addresses Reviewer Gap C:
Separates and reports:
1. Coverage: P(true parameter in reported interval)
2. Decisiveness: P(label issued) = N_decisive / N_total
3. Conditional error: P(wrong confident | decisive) = N_wrong / N_decisive
4. Unconditional error: P(wrong confident) = N_wrong / N_total

Exposes the conditional error rate in constrained / edge benchmarks
(e.g., Table 12: P(decisive)=0.095, P(wrong)=0.075 => 78.9% conditional error).
"""

import json
import numpy as np


def compute_metrics(n_total, n_decisive, n_wrong, n_covered=None):
    decisiveness = n_decisive / n_total if n_total > 0 else 0.0
    unconditional_error = n_wrong / n_total if n_total > 0 else 0.0
    conditional_error = n_wrong / n_decisive if n_decisive > 0 else 0.0
    coverage = n_covered / n_total if n_covered is not None and n_total > 0 else None

    return {
        "n_total": int(n_total),
        "n_decisive": int(n_decisive),
        "n_wrong": int(n_wrong),
        "n_inconclusive": int(n_total - n_decisive),
        "decisiveness_pct": float(decisiveness * 100.0),
        "unconditional_error_pct": float(unconditional_error * 100.0),
        "conditional_error_pct": float(conditional_error * 100.0),
        "coverage_pct": float(coverage * 100.0) if coverage is not None else None,
    }


def audit_table_benchmark():
    """Audit the benchmark cases cited by the reviewer and primary results."""
    records = {}

    # 1. Primary Observable Recurrence Bound (Lag 64, N=1024, Pulse=4)
    # 480 panels, 80 decisive (all correct), 400 inconclusive, 0 wrong
    records["primary_recurrence_lag64_n1024_p4"] = compute_metrics(
        n_total=480, n_decisive=80, n_wrong=0, n_covered=480
    )

    # 2. Point Fit comparator on same primary panel (always issues label, 37 wrong)
    records["primary_point_fit_lag64_n1024_p4"] = compute_metrics(
        n_total=480, n_decisive=480, n_wrong=37, n_covered=None
    )

    # 3. Naive interval deconvolution comparator on same primary panel (0 decisive)
    records["primary_interval_deconvolution"] = compute_metrics(
        n_total=480, n_decisive=0, n_wrong=0, n_covered=480
    )

    # 4. Reviewer-highlighted constrained robustness benchmark (200 replicates)
    # P(decisive) = 0.095 (19/200), P(wrong) = 0.075 (15/200)
    records["constrained_robustness_benchmark_review"] = compute_metrics(
        n_total=200, n_decisive=19, n_wrong=15, n_covered=None
    )

    # 5. Added covariance procedure in constrained benchmark
    # P(decisive) = 1 - 0.915 = 0.085 (17/200), P(wrong) = 0.065 (13/200) => 13/17 = 76.47%
    records["covariance_constrained_benchmark_review"] = compute_metrics(
        n_total=200, n_decisive=17, n_wrong=13, n_covered=None
    )

    # 6. Audited Linear Primary (Table 14.1 / v0.5): 2,880 panels, 745 decisive, 20 wrong, 2,758 covered
    records["audited_linear_primary_v05"] = compute_metrics(
        n_total=2880, n_decisive=745, n_wrong=20, n_covered=2758
    )

    # 7. Endpoint Confirmation (Table 14.2)
    # Fixed 64 at N=32: 26/240 decisive, 0 wrong
    records["endpoint_fixed64_n32"] = compute_metrics(
        n_total=240, n_decisive=26, n_wrong=0, n_covered=232
    )
    # Diversified at N=32: 75/240 decisive, 2 wrong
    records["endpoint_diversified_n32"] = compute_metrics(
        n_total=240, n_decisive=75, n_wrong=2, n_covered=230
    )

    return records


if __name__ == "__main__":
    table = audit_table_benchmark()
    print(json.dumps(table, indent=2))
