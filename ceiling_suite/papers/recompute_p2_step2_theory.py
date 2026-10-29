"""Paper 2 Step 2 Theory Verification:
  1. Proposition prop:inventory_S: Closed-form summed response S(psi) when traders carry inventory
     (I_{i,t} = (1 - delta_inv) I_{i,t-1} + u_{i,t}, u_{i,t} = q_i y_{i,t} - psi_i I_{i,t-1}).
  2. Proposition prop:driftguard: Uniformly safe pre-trade guard under interval-bounded unknown
     hidden cohort drift ||y_0||_infty <= y_bar_0, with corrected cumulative identity and a sufficient invariant box.

Output: ceiling_suite/papers/recomputed/R_P2_step2_theory_repaired.json
"""
from __future__ import annotations

import json
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def simulate_inventory_impulse(a: float, kappa: float, q: np.ndarray, eta: np.ndarray, psi: np.ndarray, delta_inv: float, T: int = 800) -> np.ndarray:
    K = len(q)
    y = np.zeros(K)
    inv = np.zeros(K)
    h = np.zeros(T)
    xp = 0.0
    for t in range(T):
        # At t=0 exogenous unit shock enters price: x_0 = kappa, y_{i,0} = eta_i * x_0, inv_{i,0} = 0
        if t == 0:
            xt = kappa
            u_coh = np.zeros(K)
        else:
            u_coh = q * y - psi * inv
            xt = a * xp + kappa * float(np.sum(u_coh))
        y = (1.0 - eta) * y + eta * xt
        inv = (1.0 - delta_inv) * inv + u_coh
        h[t] = xt
        xp = xt
    return h


def verify_inventory_proposition(rng: np.random.Generator) -> dict:
    max_err_signed = 0.0
    max_err_l1_monotone = 0.0
    n_nonmonotone_overshoot = 0
    for _ in range(500):
        K = int(rng.integers(2, 5))
        a = float(rng.uniform(0.3, 0.7))
        kappa = float(rng.uniform(0.5, 1.2))
        delta_inv = float(rng.uniform(0.25, 0.80))
        eta = rng.uniform(0.15, float(delta_inv), size=K)
        q_raw = rng.uniform(0.02, 0.12, size=K)
        # Ensure stability a + kappa * sum(q) < 0.90
        if a + kappa * float(np.sum(q_raw)) >= 0.88:
            q_raw *= (0.85 - a) / (kappa * float(np.sum(q_raw)))
        # Monotone regime: delta_inv >= eta_i and 0 <= psi_i <= 1 - delta_inv
        psi_mod = rng.uniform(0.01, 0.8 * (1.0 - delta_inv), size=K)
        h_mod = simulate_inventory_impulse(a, kappa, q_raw, eta, psi_mod, delta_inv, T=1000)
        phi_eff = float(np.sum(q_raw * (delta_inv / (delta_inv + psi_mod))))
        s_closed = kappa / (1.0 - a - kappa * phi_eff)
        err_s = abs(float(np.sum(h_mod)) - s_closed)
        err_l1 = abs(float(np.sum(np.abs(h_mod))) - s_closed)
        max_err_signed = max(max_err_signed, err_s)
        max_err_l1_monotone = max(max_err_l1_monotone, err_l1)

    # Worked example at calibration a=0.4, kappa=1.0, K=2, q=[0.12, 0.12], eta=[0.5, 0.25], delta_inv=0.5, psi=[0.10, 0.10]
    a0, k0, d0 = 0.4, 1.0, 0.5
    q0 = np.array([0.12, 0.12])
    eta0 = np.array([0.50, 0.25])
    psi0 = np.array([0.10, 0.10])
    h0 = simulate_inventory_impulse(a0, k0, q0, eta0, psi0, d0, T=1000)
    phi0 = float(np.sum(q0))
    phi_eff0 = float(np.sum(q0 * (d0 / (d0 + psi0))))
    s_psi0 = k0 / (1.0 - a0 - k0 * phi_eff0)
    s_no_inv = k0 / (1.0 - a0 - k0 * phi0)

    # Also test strong inventory unloading (delta_inv=0.05, psi=0.45) where h_t changes sign at long lags
    h_strong = simulate_inventory_impulse(0.4, 1.0, np.array([0.20]), np.array([0.60]), np.array([0.45]), 0.05, T=1000)
    s_strong_signed = float(np.sum(h_strong))
    s_strong_l1 = float(np.sum(np.abs(h_strong)))

    return {
        "n_trials": 500,
        "max_abs_err_signed_sum_vs_closed_form": float(max_err_signed),
        "max_abs_err_l1_norm_in_monotone_regime": float(max_err_l1_monotone),
        "worked_example": {
            "a": a0, "kappa": k0, "delta_inv": d0, "phi_raw": round(phi0, 4),
            "phi_eff": round(phi_eff0, 4),
            "S_no_inventory": round(s_no_inv, 4),
            "S_with_inventory_closed": round(s_psi0, 4),
            "S_with_inventory_sim_l1": round(float(np.sum(np.abs(h0))), 4),
        },
        "sign_reversal_regime_example": {
            "S_signed": round(s_strong_signed, 4),
            "S_l1_norm": round(s_strong_l1, 4),
            "l1_exceeds_signed": bool(s_strong_l1 > s_strong_signed + 1e-3),
        },
    }


def verify_drift_guard_proposition(rng: np.random.Generator) -> dict:
    """Check the corrected identity, peak envelope and sufficient invariant box.

    Historical R_P2_step2_theory.json is retained; it did not test maximality.
    """
    import sys
    from pathlib import Path
    root = str(Path(__file__).resolve().parents[2])
    if root not in sys.path:
        sys.path.insert(0, root)
    from studies.economic_review_20261029.models import (
        box_admission, cumulative_drift, finite_peak_envelope, state_matrix,
    )
    a, kappa, phi, eta = .4, 1., .4, .1
    J = state_matrix(a, kappa, [phi], [eta])
    z = np.array([0., .25])
    exact = float((np.linalg.solve(np.eye(2)-J,z)-z)[0])
    corrected = cumulative_drift(a,kappa,[phi],[eta],0.,[.25])
    alpha_box = box_admission(a,kappa,phi,1.,1.,.48,0.,.25)
    worst = 0.
    for _ in range(500):
        K = int(rng.integers(1,5))
        q = phi*rng.dirichlet(np.ones(K))
        rates = rng.uniform(.01,1.,K)
        peak = finite_peak_envelope(a,kappa,q,rates,0.,.25,.48,300,alpha_box).max()
        worst = max(worst,float(peak))
    assert abs(exact-corrected)<1e-10
    assert worst<=1+1e-10
    return dict(status="corrected; original exact-capacity-cost claim withdrawn",
                cumulative_original_expression=.5, cumulative_corrected=corrected,
                cumulative_resolvent=exact, alpha_box=round(alpha_box,4),
                calibration_capacity_reduction=0., max_peak_500_models=worst,
                proof_scope="box sufficiency for all rates; exact peak for each fixed model",
                historical_result_file="R_P2_step2_theory.json")


def main():
    rng = np.random.default_rng(20261021)
    res = {
        "inventory_proposition": verify_inventory_proposition(rng),
        "drift_guard_proposition": verify_drift_guard_proposition(rng),
    }
    fp = os.path.join(HERE, "recomputed", "R_P2_step2_theory_repaired.json")
    json.dump(res, open(fp, "w"), indent=2)
    print(json.dumps(res, indent=2))
    print("Wrote", fp)


if __name__ == "__main__":
    main()
