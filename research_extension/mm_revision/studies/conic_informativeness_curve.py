"""Workstream 2C: Conic Certificate Informativeness and Interval Contraction Curve.

Evaluates how the Conic Certificate interval [S_-, S_+] contracts as observation
budget R scales geometrically from R=128 to R=32,768 under Contract I0.

Models tested:
  1. Strongly Stable: S = 0.60 (a = 0.40, Q = 0.20)
  2. Moderately Stable: S = 0.82 (a = 0.40, Q = 0.42)
  3. Unstable: S = 1.25 (a = 0.40, Q = 0.85)

Generates empirical evidence demonstrating that the Conic Certificate is asymptotically
informative and decisive as budget R scales, addressing the 0% decisiveness critique.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

from research_extension.mm_revision.inference.conic_certificate import fit_conic_certificate
from research_extension.mm_revision.studies.output_error_misspecification_diagnostic import simulate_impulse_response


def run_conic_informativeness_study(
    budgets: List[int] = [128, 512, 2048, 8192, 32768],
    n_replications: int = 20,
    H: int = 24,
    seed: int = 20260924
) -> Dict[str, Any]:
    """Execute budget sweep measuring interval contraction and decisiveness."""
    rng = np.random.default_rng(seed)
    models = {
        "stable_060": {"S": 0.60, "a": 0.40, "rates": [0.05], "weights": [0.20], "kappa": 1.0},
        "stable_082": {"S": 0.82, "a": 0.40, "rates": [0.05], "weights": [0.42], "kappa": 1.0},
        "unstable_125": {"S": 1.25, "a": 0.40, "rates": [0.05], "weights": [0.85], "kappa": 1.0},
    }

    sigma_eps = 0.05
    results = {}

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
            widths = []
            coverages = []
            decisions = []
            wrong_calls = []

            for rep in range(n_replications):
                # Sample noise scaled by 1/sqrt(R)
                noise = rng.normal(0.0, sigma_eps / np.sqrt(R), size=H + 1)
                beta_hat = beta_true + noise
                # Estimated covariance V = (sigma^2 / R) * I
                cov_est = np.eye(H + 1) * ((sigma_eps ** 2) / R)

                res = fit_conic_certificate(
                    beta_hat=beta_hat,
                    covariance=cov_est,
                    df=R - 2,
                    alpha=0.05,
                    eta_floor=0.002,
                    bins=16
                )

                s_lo = res["S_lower"]
                s_hi = res["S_upper"]
                width = s_hi - s_lo
                widths.append(width)

                covered = (s_lo <= true_S <= s_hi)
                coverages.append(1.0 if covered else 0.0)

                # Decisive if strictly stable (s_hi < 1.0) or strictly unstable (s_lo > 1.0)
                is_decisive = (s_hi < 1.0) or (s_lo > 1.0)
                decisions.append(1.0 if is_decisive else 0.0)

                # Wrong call if decisive but classifies incorrectly
                is_wrong = False
                if s_hi < 1.0 and true_S >= 1.0:
                    is_wrong = True
                elif s_lo > 1.0 and true_S < 1.0:
                    is_wrong = True
                wrong_calls.append(1.0 if is_wrong else 0.0)

            results[m_name].append({
                "budget_R": R,
                "true_S": true_S,
                "mean_width": float(np.mean(widths)),
                "p90_width": float(np.percentile(widths, 90)),
                "coverage_pct": float(np.mean(coverages) * 100.0),
                "decisiveness_pct": float(np.mean(decisions) * 100.0),
                "wrong_calls": int(np.sum(wrong_calls)),
                "cond_error_pct": float((np.sum(wrong_calls) / max(1, np.sum(decisions))) * 100.0) if np.sum(decisions) > 0 else None
            })

    return {
        "budgets": budgets,
        "n_replications": n_replications,
        "H": H,
        "results": results
    }


if __name__ == "__main__":
    out_dir = Path("research_extension/outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    res = run_conic_informativeness_study()
    out_file = out_dir / "conic_contraction_results.json"
    with open(out_file, "w") as f:
        json.dump(res, f, indent=2)
    print(f"Conic informativeness curve saved to {out_file}")
    for m, rows in res["results"].items():
        print(f"\nModel: {m}")
        for r in rows:
            print(f"  R={r['budget_R']:5d}: width={r['mean_width']:.3f}, cov={r['coverage_pct']:.1f}%, dec={r['decisiveness_pct']:.1f}%")
