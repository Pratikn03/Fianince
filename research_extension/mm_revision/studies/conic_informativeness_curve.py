"""Workstream 2C: Conic Certificate Informativeness and Interval Contraction Curve.

Evaluates how the Conic Certificate interval [S_-, S_+] contracts as observation
budget R scales geometrically from R=128 to R=32,768 under Contract I0.

Models tested:
  1. Strongly Stable: S = 0.60 (a = 0.40, Q = 0.20)
  2. Moderately Stable: S = 0.82 (a = 0.40, Q = 0.42)
  3. Unstable: S = 1.25 (a = 0.40, Q = 0.85)

Corrective Gaussian coefficient experiment, not episode regression or an
asymptotic theorem. Known covariance uses chi-square calibration; estimated
covariance is an independent Wishart draw and uses the F pivot. Numerical
candidates are distinct from certified labels, which remain withheld.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
from scipy.stats import wishart
from collections import Counter
from research_extension.mm_revision.decisions import (
    DecisionLabel, evaluate_decision_accuracy, interval_contains, summarize_interval_widths,
)

from research_extension.mm_revision.inference.conic_certificate import fit_conic_certificate
from research_extension.mm_revision.studies.output_error_misspecification_diagnostic import simulate_impulse_response


def run_conic_informativeness_study(
    budgets: List[int] = [128, 512, 2048, 8192, 32768],
    n_replications: int = 20,
    H: int = 24,
    seed: int = 20260924,
    covariance_mode: str = 'estimated',
    panel_callback=None,
) -> Dict[str, Any]:
    """Execute budget sweep measuring interval contraction and decisiveness."""
    if covariance_mode not in ('known', 'estimated'):
        raise ValueError('covariance_mode must be known or estimated')
    if H < 2 or n_replications < 1 or any(r-2 < H+1 for r in budgets):
        raise ValueError('require positive replications, H>=2 and residual df>=H+1')
    rng = np.random.default_rng(seed)
    cov_rng = np.random.default_rng(np.random.SeedSequence([seed, 917]))
    models = {
        "stable_060": {"S": 0.60, "a": 0.40, "rates": [0.05], "weights": [0.20], "kappa": 1.0},
        "stable_082": {"S": 0.82, "a": 0.40, "rates": [0.05], "weights": [0.42], "kappa": 1.0},
        "unstable_125": {"S": 1.25, "a": 0.40, "rates": [0.05], "weights": [0.85], "kappa": 1.0},
    }

    sigma_eps = 0.05
    results = {}
    panels = []

    for m_name, m_info in models.items():
        results[m_name] = []
        beta_true = simulate_impulse_response(
            a=m_info["a"],
            rates=m_info["rates"],
            weights=m_info["weights"],
            kappa=m_info["kappa"],
            H=H
        )
        true_S = m_info["S"]

        for R in budgets:
            records = []
            widths = []
            coverages = []
            decisions = []
            wrong_calls = []

            for rep in range(n_replications):
                # Sample noise scaled by 1/sqrt(R)
                noise = rng.normal(0.0, sigma_eps / np.sqrt(R), size=H + 1)
                beta_hat = beta_true + noise
                true_cov = np.eye(H + 1) * ((sigma_eps ** 2) / R)
                cov_est = (true_cov.copy() if covariance_mode == 'known' else
                    wishart.rvs(df=R-2, scale=true_cov/(R-2), random_state=cov_rng))
                cov_est = (cov_est + cov_est.T) / 2

                try:
                    res = fit_conic_certificate(
                        beta_hat=beta_hat, covariance=cov_est, df=R-2, alpha=.05,
                        eta_floor=.002, bins=16, covariance_mode=covariance_mode)
                except Exception as exc:
                    # Preserve the input and failed attempt; never call missing
                    # endpoints covered or lose earlier successful panels.
                    res = dict(S_lower=np.nan, S_upper=np.nan,
                        numerical_decision='CONFLICT', decision='ABSTAIN', is_definite=False,
                        certified=False, status='exception', covariance_mode=covariance_mode,
                        error=f'{type(exc).__name__}: {exc}')

                s_lo = res["S_lower"]
                s_hi = res["S_upper"]
                width = s_hi - s_lo
                widths.append(width)

                covered = interval_contains(s_lo, s_hi, true_S)
                coverages.append(1.0 if covered else 0.0)

                numerical = evaluate_decision_accuracy(DecisionLabel(res['numerical_decision']), true_S)
                is_decisive = numerical['is_issued']
                decisions.append(1.0 if is_decisive else 0.0)

                # Wrong call if decisive but classifies incorrectly
                is_wrong = numerical['is_wrong']
                wrong_calls.append(1.0 if is_wrong else 0.0)
                diff = beta_hat - beta_true
                try:
                    distance = float(diff @ np.linalg.solve(cov_est, diff))
                except (np.linalg.LinAlgError, ValueError) as exc:
                    distance = None
                    res['response_diagnostic_error'] = f'{type(exc).__name__}: {exc}'
                record = dict(model=m_name, budget_R=R, replicate=rep,
                    beta_hat=beta_hat.tolist(), covariance=cov_est.tolist(),
                    covariance_mode=covariance_mode, df=R-2, lower=s_lo, upper=s_hi,
                    is_covered=covered, diagnostics=res, **numerical,
                    response_event_contains_truth=(bool(distance <= res['radius_squared'])
                        if distance is not None and 'radius_squared' in res else None),
                    response_mahalanobis_squared=distance)
                records.append(record)
                panels.append(record)
                if panel_callback is not None:
                    panel_callback(record)

            width_summary = summarize_interval_widths(records)
            results[m_name].append({
                "budget_R": R,
                "true_S": true_S,
                "mean_width": width_summary['mean_interval_width'],
                "p90_width": width_summary['p90_interval_width'],
                **width_summary,
                "coverage_pct": float(np.mean(coverages) * 100.0),
                "numerical_decisiveness_pct": float(np.mean(decisions) * 100.0),
                "certified_decisiveness_pct": 100*sum(r['diagnostics']['is_definite'] for r in records)/n_replications,
                "response_coverage_pct": (100*sum(r['response_event_contains_truth'] is True for r in records)/n_replications
                    if all(r['response_event_contains_truth'] is not None for r in records) else None),
                "response_event_unavailable": sum(r['response_event_contains_truth'] is None for r in records),
                "status_counts": dict(Counter(r['diagnostics']['status'] for r in records)),
                "wrong_calls": int(np.sum(wrong_calls)),
                "cond_error_pct": float((np.sum(wrong_calls) / max(1, np.sum(decisions))) * 100.0) if np.sum(decisions) > 0 else None
            })
            print(f'sweep {covariance_mode} {m_name} R={R}: {n_replications} panels', flush=True)

    return {
        "budgets": budgets,
        "n_replications": n_replications,
        "H": H,
        "seed": seed,
        "covariance_mode": covariance_mode,
        "analysis_status": "post_hoc_corrective_rerun",
        "sampling_contract": "Gaussian coefficients; independent Wishart covariance only in estimated mode",
        "results": results,
        "panel_records": panels,
    }


if __name__ == "__main__":
    import argparse
    from research_extension.evidence_repair.statistical_repair import write_locked_json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--covariance-mode', choices=('known', 'estimated'), default='estimated')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Refusing to overwrite saved results')
    write_locked_json(args.output, run_conic_informativeness_study(covariance_mode=args.covariance_mode))
