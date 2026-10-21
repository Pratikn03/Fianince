"""Paper 2 Step 2 Theory Verification:
  1. Proposition prop:inventory_S: Closed-form summed response S(psi) when traders carry inventory
     (I_{i,t} = (1 - delta_inv) I_{i,t-1} + u_{i,t}, u_{i,t} = q_i y_{i,t} - psi_i I_{i,t-1}).
  2. Proposition prop:driftguard: Uniformly safe pre-trade guard under interval-bounded unknown
     hidden cohort drift ||y_0||_infty <= y_bar_0, and its exact capacity cost.

Output: ceiling_suite/papers/recomputed/R_P2_step2_theory.json
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
    """Verify Proposition prop:driftguard on the bridge_check.py rational pair and 500 random economies."""
    # Rational counterexample pair from bridge_check.py Part F:
    # a = 0.4, kappa = 1.0, Phi = 0.40, S(1) = 5.0
    a, kappa, phi_plus = 0.4, 1.0, 0.40
    I_pos = 1.0
    u_bar = 0.48
    B_bud = 1.00
    y_bar_0 = 0.25
    x_0 = 0.0

    # Rest-state guard: c_I = 1 - a - kappa * |I| * u_bar / B = 0.6 - 0.20 / 1.50 = 0.46667
    # alpha^* = min(1, c_I / (kappa * Phi^+))
    c_I = 1.0 - a - kappa * I_pos * u_bar / B_bud
    alpha_rest = min(1.0, c_I / (kappa * phi_plus))
    # Drift-adjusted guard: alpha_drift^* = min(1, ((1 - a)*B - |I|*(a|x_0| + kappa*u_bar)) / (kappa * Phi^+ * (B + |I|*y_bar_0)))
    alpha_drift = min(1.0, max(0.0, ((1.0 - a) * B_bud - I_pos * (a * abs(x_0) + kappa * u_bar)) / (kappa * phi_plus * (B_bud + I_pos * y_bar_0))))
    cap_cost_closed = alpha_rest * (I_pos * y_bar_0) / (B_bud + I_pos * y_bar_0)

    def max_loss_sim(q_vec, eta_vec, alpha_val, y0_vec, H=300):
        # Worst-case adversary u_t = u_bar for positive system with y0_vec
        y = np.array(y0_vec, dtype=float)
        xp = x_0
        max_x = abs(xp)
        for _ in range(1, H + 1):
            u_coh = alpha_val * float(np.dot(q_vec, y))
            xt = a * xp + kappa * (u_coh + u_bar)
            y = (1.0 - eta_vec) * y + eta_vec * xt
            max_x = max(max_x, abs(xt))
            xp = xt
        return I_pos * max_x

    q1, eta1 = np.array([0.20, 0.20]), np.array([5.0 / 8.0, 3.0 / 8.0])
    q2, eta2 = np.array([9.0 / 25.0, 1.0 / 25.0]), np.array([13.0 / 24.0, 1.0 / 8.0])

    # Under worst-case hidden state y_0 = [y_bar_0, y_bar_0]:
    loss_rest_e1 = max_loss_sim(q1, eta1, alpha_rest, [y_bar_0, y_bar_0])
    loss_rest_e2 = max_loss_sim(q2, eta2, alpha_rest, [y_bar_0, y_bar_0])
    loss_drift_e1 = max_loss_sim(q1, eta1, alpha_drift, [y_bar_0, y_bar_0])
    loss_drift_e2 = max_loss_sim(q2, eta2, alpha_drift, [y_bar_0, y_bar_0])

    # Check 500 random economies with random y_0 in [-y_bar_0, y_bar_0]^K
    n_breach_drift = 0
    n_breach_rest = 0
    for _ in range(500):
        K = int(rng.integers(2, 5))
        w_split = rng.dirichlet(np.ones(K))
        q_k = phi_plus * w_split
        eta_k = rng.uniform(0.10, 0.85, size=K)
        y0_k = rng.uniform(-y_bar_0, y_bar_0, size=K)
        if max_loss_sim(q_k, eta_k, alpha_drift, y0_k) > B_bud + 1e-9:
            n_breach_drift += 1
        if max_loss_sim(q_k, eta_k, alpha_rest, np.full(K, y_bar_0)) > B_bud + 1e-9:
            n_breach_rest += 1

    return {
        "calibration": {
            "a": a, "kappa": kappa, "Phi_plus": phi_plus, "I": I_pos,
            "u_bar": u_bar, "B": B_bud, "y_bar_0": y_bar_0,
        },
        "alpha_rest": round(alpha_rest, 4),
        "alpha_drift": round(alpha_drift, 4),
        "capacity_cost_closed_form": round(cap_cost_closed, 4),
        "capacity_cost_diff": round(alpha_rest - alpha_drift, 4),
        "loss_under_rest_guard_econ1": round(loss_rest_e1, 4),
        "loss_under_rest_guard_econ2": round(loss_rest_e2, 4),
        "loss_under_drift_guard_econ1": round(loss_drift_e1, 4),
        "loss_under_drift_guard_econ2": round(loss_drift_e2, 4),
        "breaches_500_random_economies_drift_guard": n_breach_drift,
        "breaches_500_worst_state_rest_guard": n_breach_rest,
    }


def main():
    rng = np.random.default_rng(20261021)
    res = {
        "inventory_proposition": verify_inventory_proposition(rng),
        "drift_guard_proposition": verify_drift_guard_proposition(rng),
    }
    fp = os.path.join(HERE, "recomputed", "R_P2_step2_theory.json")
    json.dump(res, open(fp, "w"), indent=2)
    print(json.dumps(res, indent=2))
    print("Wrote", fp)


if __name__ == "__main__":
    main()
