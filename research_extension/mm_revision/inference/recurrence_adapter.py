"""Adapter for the observable recurrence LP interval and deconvolution interval under Contract I0."""
from typing import Dict, Any, Tuple, Optional
import numpy as np
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
obs_src = ROOT / "studies" / "observable_stress_tests" / "src"
if str(obs_src) not in sys.path:
    sys.path.insert(0, str(obs_src))

from observable import (
    recurrence_interval as raw_recurrence_interval,
    deconvolution_interval as raw_deconvolution_interval,
    response_intervals,
    label as obs_label
)
from research_extension.mm_revision.decisions import DecisionLabel, classify_interval


def fit_recurrence_interval(
    lower_response: np.ndarray,
    upper_response: np.ndarray,
    eta_floor: float = 0.002,
    bins: int = 64
) -> Dict[str, Any]:
    """Fit the outer stability interval [S_-, S_+] using the observable LP recurrence formulation."""
    lower = np.asarray(lower_response, dtype=float)
    upper = np.asarray(upper_response, dtype=float)

    raw_res = raw_recurrence_interval(lower, upper, eta_floor=eta_floor, bins=bins)
    raw_label = raw_res.get("label", "inconclusive")
    lo = raw_res.get("lower", float("nan"))
    hi = raw_res.get("upper", float("nan"))

    # Map to standardized DecisionLabel
    if raw_label == "model_conflict" or np.isnan(lo) or np.isnan(hi) or lo > hi:
        decision = DecisionLabel.CONFLICT
    elif raw_label == "stable":
        decision = DecisionLabel.STABLE
    elif raw_label == "unstable":
        decision = DecisionLabel.UNSTABLE
    else:
        decision = DecisionLabel.ABSTAIN

    return {
        "S_lower": float(lo) if np.isfinite(lo) else None,
        "S_upper": float(hi) if np.isfinite(hi) else None,
        "decision": decision,
        "raw_label": raw_label,
        "details": raw_res,
        "is_definite": bool(decision in (DecisionLabel.STABLE, DecisionLabel.UNSTABLE)),
        "is_conflict": bool(decision == DecisionLabel.CONFLICT),
    }


def fit_deconvolution_interval(
    lower_response: np.ndarray,
    upper_response: np.ndarray,
    eta_floor: float = 0.002
) -> Dict[str, Any]:
    """Fit stability interval using the interval deconvolution tail envelope."""
    lower = np.asarray(lower_response, dtype=float)
    upper = np.asarray(upper_response, dtype=float)

    raw_res = raw_deconvolution_interval(lower, upper, eta_floor=eta_floor)
    raw_label = raw_res.get("label", "inconclusive")
    lo = raw_res.get("lower", float("nan"))
    hi = raw_res.get("upper", float("nan"))

    if raw_label == "model_conflict" or np.isnan(lo) or np.isnan(hi) or lo > hi:
        decision = DecisionLabel.CONFLICT
    elif raw_label == "stable":
        decision = DecisionLabel.STABLE
    elif raw_label == "unstable":
        decision = DecisionLabel.UNSTABLE
    else:
        decision = DecisionLabel.ABSTAIN

    return {
        "S_lower": float(lo) if np.isfinite(lo) else None,
        "S_upper": float(hi) if np.isfinite(hi) else None,
        "decision": decision,
        "raw_label": raw_label,
        "details": raw_res,
        "is_definite": bool(decision in (DecisionLabel.STABLE, DecisionLabel.UNSTABLE)),
        "is_conflict": bool(decision == DecisionLabel.CONFLICT),
    }
