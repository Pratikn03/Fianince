"""Reproducible checks for the Paper 1 -> Paper 2 bridge proposition (see BRIDGE_PROPOSITION.md).

Everything is in the positive cohort economy of Paper 2, eq. (J)/(eq:rec):

    x_{t+1} = a x_t + kappa * sum_i q_i y_{i,t},     y_{i,t+1} = (1 - eta_i) y_{i,t} + eta_i x_{t+1},
    h_0 = kappa,  y_{i,0} = eta_i h_0,   h_t = x_t   (price response to a unit of flow at t = 0).

Parts
  A  exact rational check that a cohort split leaves Phi (hence S and every guard decision) unchanged while moving
     the response at lag 2 by exactly -kappa^2 q delta^2;
  B  the Le Cam two-point necessary sample size for telling the pair apart (scaling delta^-4);
  C  Monte Carlo under observation contract (O1): the certificate of Paper 2 Thm 5.4 does not depend on delta,
     the cohort test does;
  D  the window family with a closed form (n = 2 moments): Phi_-(k) = k0^2/(k0-k1), Phi_+(rbar) = k0 + k1/(1-rbar),
     the explicit family Phi(delta) = k0 + k1/delta that has no finite certificate without a memory bound,
     checked against an independent linear program;
  E  counterexample to the sufficiency step when responses are signed (contrarian cohort);
  F  counterexample to hidden-state invariance when initial state z_0 != 0 is not reset or observed.

Run:  python3 ceiling_suite/bridge/bridge_check.py   (writes results/bridge_results.json)
"""

from __future__ import annotations

import json
import math
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results" / "bridge_results.json"


# --------------------------------------------------------------------------------------------------------------
# model
# --------------------------------------------------------------------------------------------------------------
def response(a, kappa, q, eta, horizon):
    """Impulse response h_0..h_{horizon-1}; exact if all inputs are Fractions."""
    x = kappa
    y = [e * kappa for e in eta]
    out = [x]
    for _ in range(horizon - 1):
        x = a * x + kappa * sum(qi * yi for qi, yi in zip(q, y))
        y = [(1 - e) * yi + e * x for e, yi in zip(eta, y)]
        out.append(x)
    return out


def phi(q):
    return sum(q)


def summed_response(a, kappa, q):
    return kappa / (1 - a - kappa * phi(q))


def operator(a, kappa, q, eta):
    n = len(q)
    m = np.zeros((n + 1, n + 1))
    m[0, 0] = a
    m[0, 1:] = [kappa * float(v) for v in q]
    for i in range(n):
        m[i + 1, 0] = float(eta[i]) * a
        m[i + 1, 1:] = [float(eta[i]) * kappa * float(v) for v in q]
        m[i + 1, i + 1] += 1 - float(eta[i])
    return m


# --------------------------------------------------------------------------------------------------------------
# A. exact: Phi is invariant to the split, the response is not
# --------------------------------------------------------------------------------------------------------------
A0, KAPPA, Q0, ETA0 = F(2, 5), F(1), F(2, 25), F(1, 2)  # Example ex:witness, market A


def part_a():
    rows = []
    for d in [F(1, 5), F(1, 10), F(1, 20), F(1, 40)]:
        single = response(A0, KAPPA, [Q0], [ETA0], 8)
        split = response(A0, KAPPA, [Q0 / 2, Q0 / 2], [ETA0 - d, ETA0 + d], 8)
        diff = [s - t for s, t in zip(split, single)]
        rows.append(
            {
                "delta": str(d),
                "phi_single": str(phi([Q0])),
                "phi_split": str(phi([Q0 / 2, Q0 / 2])),
                "S_single": str(summed_response(A0, KAPPA, [Q0])),
                "S_split": str(summed_response(A0, KAPPA, [Q0 / 2, Q0 / 2])),
                "response_diff_lags_0_to_4": [str(v) for v in diff[:5]],
                "predicted_lag2_diff": str(-(KAPPA**2) * Q0 * d**2),
                "lag2_matches_prediction": diff[2] == -(KAPPA**2) * Q0 * d**2,
                "lags_0_1_equal": diff[0] == 0 and diff[1] == 0,
            }
        )
    return rows


# --------------------------------------------------------------------------------------------------------------
# B. Le Cam necessary sample size and its scaling
# --------------------------------------------------------------------------------------------------------------
SIGMA = 0.01
A_F, K_F, Q_F, ETA_F = 0.4, 1.0, 0.08, 0.5


def delta_h(delta, horizon=400):
    single = np.array(response(A_F, K_F, [Q_F], [ETA_F], horizon), dtype=float)
    split = np.array(response(A_F, K_F, [Q_F / 2, Q_F / 2], [ETA_F - delta, ETA_F + delta], horizon), dtype=float)
    return split - single


def n_lower_bound(norm_dh, sigma=SIGMA, total_error=0.10):
    """Any test with err_0 + err_1 <= total_error needs TV >= 1 - total_error; TV <= sqrt(N) ||dh|| / (2 sigma)."""
    return (2 * sigma * (1 - total_error) / norm_dh) ** 2


def part_b():
    deltas = [0.02, 0.04, 0.08, 0.16]
    delta_bar = 0.20
    s_bar = A_F + K_F * Q_F
    c_lower = (K_F**2) * Q_F
    c_upper = (2.0 * (K_F**2) * Q_F) / (((1.0 - s_bar) ** 2) * ETA_F * ((ETA_F - delta_bar) ** 2))
    rows = []
    for d in deltas:
        nd = float(np.linalg.norm(delta_h(d)))
        lb_analytic = c_lower * (d**2)
        ub_analytic = c_upper * (d**2)
        rows.append(
            {
                "delta": d,
                "norm_dh": nd,
                "analytic_lower_bound_norm_dh": lb_analytic,
                "analytic_upper_bound_norm_dh": ub_analytic,
                "within_analytic_sandwich": bool(lb_analytic <= nd <= ub_analytic),
                "N_necessary_to_separate": n_lower_bound(nd),
            }
        )
    slope = np.polyfit(np.log(deltas), np.log([r["norm_dh"] for r in rows]), 1)[0]
    return {
        "sigma": SIGMA,
        "analytic_c_lower": c_lower,
        "analytic_c_upper": c_upper,
        "rows": rows,
        "loglog_slope_norm_dh": float(slope),
        "implied_N_exponent": float(-2 * slope),
    }


def wilson(p_hat, n, z=1.959964):
    """Wilson score interval for a binomial proportion."""
    centre = (p_hat + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p_hat * (1 - p_hat) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [centre - half, centre + half]


# --------------------------------------------------------------------------------------------------------------
# C. Monte Carlo under (O1): the certificate does not depend on delta, the cohort test does
# --------------------------------------------------------------------------------------------------------------
def part_c(n_exp=2000, reps=4000, horizon_t=80, gamma=0.05, seed=20261020):
    """Monte Carlo under (O1). Averaging N independent N(h, sigma^2) responses gives N(h, sigma^2/N) per tap exactly,
    so the average is sampled directly. Coverage and accuracy are reported with Wilson 95% intervals."""
    rng = np.random.default_rng(seed)
    rbar, sbar = 0.7, 0.5  # memory bound and a + kappa*Phi <= sbar for every economy below (0.4 + 0.08 = 0.48)
    lam = 1 - (1 - rbar) * (1 - sbar)
    z = float(norm.ppf(1 - gamma))
    tail = K_F * lam**horizon_t / (1 - lam)
    margin = z * SIGMA * math.sqrt(horizon_t / n_exp) + tail
    s_true = K_F / (1 - A_F - K_F * Q_F)
    rows = []
    for d in [0.02, 0.05, 0.1, 0.2]:
        h0 = np.array(response(A_F, K_F, [Q_F], [ETA_F], horizon_t))
        h1 = np.array(response(A_F, K_F, [Q_F / 2, Q_F / 2], [ETA_F - d, ETA_F + d], horizon_t))
        # the mean of n_exp independent N(h, sigma^2) responses is N(h, sigma^2/n_exp) per tap
        se = SIGMA / math.sqrt(n_exp)
        cover, excess, correct = [], [], []
        w = h1 - h0
        mid = 0.5 * (h0 + h1)
        for truth, h in ((0, h0), (1, h1)):
            hbar = h + se * rng.standard_normal((reps, horizon_t))
            s_plus = hbar.sum(axis=1) + margin
            cover.append(np.mean(s_plus >= s_true))  # both markets share S (Phi is identical)
            excess.append(np.mean(s_plus - s_true))
            stat = (hbar - mid) @ w  # likelihood-ratio statistic for known means
            correct.append(np.mean((stat > 0) == (truth == 1)))
        d_prime = math.sqrt(n_exp) * float(np.linalg.norm(w)) / SIGMA
        trials = 2 * reps  # both economies, reps replications each
        cov_mean, acc_mean = float(np.mean(cover)), float(np.mean(correct))
        rows.append(
            {
                "delta": d,
                "certificate_coverage": cov_mean,
                "certificate_coverage_ci95": wilson(cov_mean, trials),
                "certificate_mean_excess": float(np.mean(excess)),
                "cohort_test_accuracy_mc": acc_mean,
                "cohort_test_accuracy_ci95": wilson(acc_mean, trials),
                "cohort_test_accuracy_theory": float(norm.cdf(d_prime / 2)),
                "trials_per_row": trials,
            }
        )
    return {
        "N": n_exp,
        "sigma": SIGMA,
        "T": horizon_t,
        "gamma": gamma,
        "S_true": s_true,
        "certificate_margin": margin,
        "reps": reps,
        "seed": seed,
        "rows": rows,
    }


# --------------------------------------------------------------------------------------------------------------
# D. windows: closed form for n = 2, explicit unbounded family, independent LP
# --------------------------------------------------------------------------------------------------------------
K0, K1 = F(1, 25), F(1, 50)  # moments of market A: k0 = q eta, k1 = q eta (1 - eta)


def atoms_to_cohorts(atoms):
    """(r_i, w_i) -> (q_i, eta_i) with eta = 1 - r, q = w / eta."""
    eta = [1 - r for r, _ in atoms]
    q = [w / e for (_, w), e in zip(atoms, eta)]
    return q, eta


def two_atom_family(delta):
    """Atoms {0, 1 - delta} with the moments (k0, k1): w_b = k1 / (1 - delta), w_a = k0 - w_b."""
    wb = K1 / (1 - delta)
    return [(F(0), K0 - wb), (1 - delta, wb)]


def part_d():
    phi_minus = K0**2 / (K0 - K1)
    rows = []
    for delta in [F(1, 2), F(1, 4), F(1, 10), F(1, 20), F(1, 25), F(1, 27)]:
        q, eta = atoms_to_cohorts(two_atom_family(delta))
        h = response(A0, KAPPA, q, eta, 6)
        ref = response(A0, KAPPA, [Q0], [ETA0], 6)
        phi_d = phi(q)
        stable = A0 + KAPPA * phi_d < 1
        rows.append(
            {
                "delta": str(delta),
                "r_max": str(1 - delta),
                "phi": str(phi_d),
                "phi_closed_form": str(K0 + K1 / delta),
                "phi_matches_closed_form": phi_d == K0 + K1 / delta,
                "lags_0_to_2_equal_reference": h[:3] == ref[:3],
                "stable": bool(stable),
                "S": str(summed_response(A0, KAPPA, q)) if stable else "infinite (a + kappa Phi >= 1)",
            }
        )
    delta_star = K1 / ((1 - A0) / KAPPA - K0)
    # independent LP for rbar = 0.95 on a grid containing 0, 0.5 and 0.95
    grid = np.linspace(0, 0.95, 1901)
    a_eq = np.vstack([np.ones_like(grid), grid])
    b_eq = [float(K0), float(K1)]
    cost = 1 / (1 - grid)
    lp_max = linprog(-cost, A_eq=a_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    lp_min = linprog(cost, A_eq=a_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    rbar = F(19, 20)
    phi_plus = K0 + K1 / (1 - rbar)
    return {
        "phi_minus_closed_form": str(phi_minus),
        "S_at_phi_minus": str(summed_response(A0, KAPPA, [phi_minus])),
        "phi_plus_rbar_0.95_closed_form": str(phi_plus),
        "S_at_phi_plus_rbar_0.95": str(summed_response(A0, KAPPA, [phi_plus])),
        "lp_phi_max_rbar_0.95": float(-lp_max.fun),
        "lp_phi_min_rbar_0.95": float(lp_min.fun),
        "critical_delta_for_instability": str(delta_star),
        "family": rows,
    }


# --------------------------------------------------------------------------------------------------------------
# E. counterexample: signed responses break "worst-case loss = |I| u S"
# --------------------------------------------------------------------------------------------------------------
def part_e(horizon=3000):
    q = [0.9, -0.82]
    eta = [0.07, 0.99]
    positive = [Q_F]
    h_pos = np.array(response(A_F, K_F, positive, [ETA_F], horizon))
    h_sig = np.array(response(A_F, K_F, q, eta, horizon))
    rho = float(max(abs(np.linalg.eigvals(operator(A_F, K_F, q, eta)))))
    s_net = K_F / (1 - A_F - K_F * sum(q))
    return {
        "q": q,
        "eta": eta,
        "phi_signed": sum(q),
        "phi_positive_reference": Q_F,
        "spectral_radius_signed": rho,
        "S_net_formula": s_net,
        "sum_h_signed": float(h_sig.sum()),
        "sum_abs_h_signed": float(np.abs(h_sig).sum()),
        "sum_abs_h_positive_reference": float(np.abs(h_pos).sum()),
        "min_h_signed": float(h_sig.min()),
        "loss_understatement_ratio": float(np.abs(h_sig).sum() / s_net),
    }


# --------------------------------------------------------------------------------------------------------------
# F. counterexample: unknown non-zero initial hidden cohort state z_0 != 0 breaks cohort invariance
# --------------------------------------------------------------------------------------------------------------
def part_f():
    """Two positive-cohort economies with identical (a, kappa) = (2/5, 1), identical total feedback Phi = 2/5 (S = 5),
    and identical early impulse window (h_0, h_1, h_2) = (1, 3/5, 363/800), yet different future drift from non-zero
    initial cohort states z_0 != 0."""
    a, kappa = F(2, 5), F(1, 1)
    q1, eta1 = [F(1, 5), F(1, 5)], [F(5, 8), F(3, 8)]
    q2, eta2 = [F(9, 25), F(1, 25)], [F(13, 24), F(1, 8)]

    def _sim_states(q, eta, steps=5):
        x = kappa
        y = [e * x for e in eta]
        states = [(x, list(y))]
        for _ in range(steps - 1):
            x = a * x + kappa * sum(qi * yi for qi, yi in zip(q, y))
            y = [(1 - e) * yi + e * x for e, yi in zip(eta, y)]
            states.append((x, list(y)))
        return states

    st1 = _sim_states(q1, eta1, 5)
    st2 = _sim_states(q2, eta2, 5)
    h1 = [s[0] for s in st1]
    h2 = [s[0] for s in st2]

    # At t = 0 after a unit shock two steps earlier (lag 2): x_0 = h_2 = 363/800 in both economies
    x0_1, y0_1 = st1[2]
    x0_2, y0_2 = st2[2]
    b1_1 = a * x0_1 + kappa * sum(qi * yi for qi, yi in zip(q1, y0_1))
    b1_2 = a * x0_2 + kappa * sum(qi * yi for qi, yi in zip(q2, y0_2))

    # At t = 0 after a unit shock three steps earlier (lag 3): cumulative future drift sum_{t>=1} b_t
    x3_1, y3_1 = st1[3]
    x3_2, y3_2 = st2[3]
    s_val = kappa / (1 - a - kappa * sum(q1))
    cum_drift_1 = (a * x3_1 + kappa * sum((qi / ei) * yi for qi, ei, yi in zip(q1, eta1, y3_1))) / (
        1 - a - kappa * sum(q1)
    )
    cum_drift_2 = (a * x3_2 + kappa * sum((qi / ei) * yi for qi, ei, yi in zip(q2, eta2, y3_2))) / (
        1 - a - kappa * sum(q2)
    )

    # Worst-case cumulative future drift over unknown hidden cohort state ||y_0||_2 <= 1 at x_0 = 0
    wc_cum_drift_1 = float(s_val) * math.sqrt(float(sum((qi / ei) ** 2 for qi, ei in zip(q1, eta1))))
    wc_cum_drift_2 = float(s_val) * math.sqrt(float(sum((qi / ei) ** 2 for qi, ei in zip(q2, eta2))))

    # One-step price-row operator norm ||c_price^T J||_2 = sqrt(a^2 + kappa^2 sum_i q_i^2)
    row_norm_1 = math.sqrt(float(a**2 + kappa**2 * sum(qi**2 for qi in q1)))
    row_norm_2 = math.sqrt(float(a**2 + kappa**2 * sum(qi**2 for qi in q2)))

    return {
        "economy_1": {"q": [str(x) for x in q1], "eta": [str(x) for x in eta1]},
        "economy_2": {"q": [str(x) for x in q2], "eta": [str(x) for x in eta2]},
        "phi_equal": sum(q1) == sum(q2) == F(2, 5),
        "S_equal": str(s_val),
        "h_lags_0_to_2_equal": h1[:3] == h2[:3] == [F(1, 1), F(3, 5), F(363, 800)],
        "h_lags_0_to_2": [str(x) for x in h1[:3]],
        "next_step_drift_b1_economy_1": str(b1_1),
        "next_step_drift_b1_economy_2": str(b1_2),
        "next_step_drift_diff": str(b1_1 - b1_2),
        "cum_future_drift_from_lag3_economy_1": str(cum_drift_1),
        "cum_future_drift_from_lag3_economy_2": str(cum_drift_2),
        "cum_future_drift_diff": str(cum_drift_1 - cum_drift_2),
        "worst_case_unit_hidden_norm_drift_economy_1": wc_cum_drift_1,
        "worst_case_unit_hidden_norm_drift_economy_2": wc_cum_drift_2,
        "worst_case_hidden_drift_ratio": wc_cum_drift_2 / wc_cum_drift_1,
        "one_step_price_row_norm_economy_1": row_norm_1,
        "one_step_price_row_norm_economy_2": row_norm_2,
    }


def main():
    out = {
        "A_exact_split": part_a(),
        "B_lecam": part_b(),
        "C_monte_carlo_O1": part_c(),
        "D_windows": part_d(),
        "E_signed_counterexample": part_e(),
        "F_hidden_state_counterexample": part_f(),
    }
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
