"""Decision logic and rigorous error metric denominators for stability certification.

Produces:
- Classes: STABLE, UNSTABLE, ABSTAIN, CONFLICT
- Proper error denominators:
  * parameter_coverage = covered / total
  * decisiveness = issued / total
  * unconditional_error = wrong / total
  * conditional_error = wrong / issued (None if issued == 0)
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any
import numpy as np


class DecisionLabel(str, Enum):
    STABLE = "STABLE"
    UNSTABLE = "UNSTABLE"
    ABSTAIN = "ABSTAIN"
    CONFLICT = "CONFLICT"


def classify_interval(
    lower_bound: float,
    upper_bound: float,
    threshold: float = 1.0,
    tol: float = 1e-9
) -> DecisionLabel:
    """Classify a bounding interval [S_-, S_+] relative to stability threshold (default 1.0).

    - If lower_bound > upper_bound + tol: CONFLICT (empty enclosure)
    - If upper_bound < threshold - tol: STABLE
    - If lower_bound > threshold + tol: UNSTABLE
    - Otherwise (interval straddles threshold or hits boundary): ABSTAIN
    """
    if lower_bound > upper_bound + tol:
        return DecisionLabel.CONFLICT
    if upper_bound < threshold - tol:
        return DecisionLabel.STABLE
    if lower_bound > threshold + tol:
        return DecisionLabel.UNSTABLE
    return DecisionLabel.ABSTAIN


def evaluate_decision_accuracy(
    decision: DecisionLabel,
    true_S: float,
    threshold: float = 1.0,
    tol: float = 1e-9
) -> Dict[str, Any]:
    """Evaluate correctness of a single decision relative to ground truth S."""
    true_stable = (true_S < threshold - tol)
    true_unstable = (true_S > threshold + tol)
    true_boundary = not (true_stable or true_unstable)

    is_issued = (decision in (DecisionLabel.STABLE, DecisionLabel.UNSTABLE))
    is_wrong = False

    if decision == DecisionLabel.STABLE:
        # Wrong if truth is unstable or boundary
        is_wrong = not true_stable
    elif decision == DecisionLabel.UNSTABLE:
        # Wrong if truth is stable or boundary
        is_wrong = not true_unstable

    return {
        "decision": decision.value,
        "true_S": float(true_S),
        "is_issued": bool(is_issued),
        "is_wrong": bool(is_wrong),
        "is_abstain": bool(decision == DecisionLabel.ABSTAIN),
        "is_conflict": bool(decision == DecisionLabel.CONFLICT),
    }


@dataclass
class AggregatedDecisionMetrics:
    total_panels: int
    covered_panels: int
    issued_decisions: int
    wrong_decisions: int
    abstentions: int
    conflicts: int
    parameter_coverage_pct: float
    decisiveness_pct: float
    unconditional_error_pct: float
    conditional_error_pct: Optional[float]
    conflict_pct: float
    abstention_pct: float


def aggregate_decision_metrics(
    records: List[Dict[str, Any]],
    threshold: float = 1.0
) -> AggregatedDecisionMetrics:
    """Compute rigorous decision metrics across panels with correct denominators."""
    total = len(records)
    if total == 0:
        return AggregatedDecisionMetrics(
            total_panels=0, covered_panels=0, issued_decisions=0, wrong_decisions=0,
            abstentions=0, conflicts=0, parameter_coverage_pct=0.0, decisiveness_pct=0.0,
            unconditional_error_pct=0.0, conditional_error_pct=None,
            conflict_pct=0.0, abstention_pct=0.0
        )

    covered = sum(1 for r in records if r.get("is_covered", False))
    issued = sum(1 for r in records if r.get("is_issued", False))
    wrong = sum(1 for r in records if r.get("is_wrong", False))
    abstain = sum(1 for r in records if r.get("is_abstain", False))
    conflicts = sum(1 for r in records if r.get("is_conflict", False))

    param_cov = (covered / total) * 100.0
    decisiveness = (issued / total) * 100.0
    uncond_err = (wrong / total) * 100.0
    cond_err = ((wrong / issued) * 100.0) if issued > 0 else None
    conflict_pct = (conflicts / total) * 100.0
    abstain_pct = (abstain / total) * 100.0

    return AggregatedDecisionMetrics(
        total_panels=total,
        covered_panels=covered,
        issued_decisions=issued,
        wrong_decisions=wrong,
        abstentions=abstain,
        conflicts=conflicts,
        parameter_coverage_pct=float(param_cov),
        decisiveness_pct=float(decisiveness),
        unconditional_error_pct=float(uncond_err),
        conditional_error_pct=float(cond_err) if cond_err is not None else None,
        conflict_pct=float(conflict_pct),
        abstention_pct=float(abstain_pct),
    )
