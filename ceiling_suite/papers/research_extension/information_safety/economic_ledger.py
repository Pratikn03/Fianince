"""Economic ledgers: the equilibrium rebate priced from a certified summed response (Proposition prop:equil; test T12,
blueprint E14) and the dealer balance-sheet step of Theorem thm:forward (margin, hedge, worst-case fills, reserve)."""
import numpy as np
from scipy.optimize import brentq


def run_rebate():
    v, c, th, Lam, m0, qx, ktt = 0.002, 0.5, 0.3, 1e-4, 0.005, 0.02, 1.0
    from scipy.optimize import brentq as bq
    g = lambda m: ktt / (m - qx * ktt) ** 2
    t12 = []
    for N in [5, 20]:
        msp = bq(lambda m: m - m0 - N * v / c - N * Lam * g(m) / c, qx * ktt + 1e-9, 10)
        tau_true = (1 - th / N) * Lam * g(msp)
        def welfare(m):
            s = (m - m0) / N
            return N * (v * s - c / 2 * s ** 2) - Lam * ktt / (m - qx * ktt)
        for infl in [1.0, 1.1, 1.5]:           # rebate computed from S_up = infl * S at the first best
            tau = (1 - th / N) * Lam * (infl * ktt / (msp - qx * ktt)) ** 2 / ktt
            meq = bq(lambda m: m - m0 - N * (v + tau) / c - th * Lam * g(m) / c, qx * ktt + 1e-9, 10)
            t12.append({"N_dealers": N, "S_up_over_S": infl, "welfare_loss_vs_first_best_pct": 100 * (welfare(msp) - welfare(meq)) / abs(welfare(msp))})
    return t12



# ------------------------------------------------------------------------------------------------ balance sheet (thm:forward)
def buffer(K, I, p, mu, c0):
    """Remaining buffer B_rem = E - MM with E = K + I p and MM = max(0, mu |I| p - c0)."""
    return K + I * p - max(0.0, mu * abs(I) * p - c0)


def guard_lhs(I_post, mu, MC, z_norm, s, Gcum, ucum, C_hedge, C_fill, R_safe):
    """Left side of the guard inequality (eq. guardineq)."""
    return abs(I_post) * (1 + mu) * (MC * z_norm + s * Gcum * ucum) + C_hedge + C_fill + R_safe


def admissible_shock_alpha0(B_rem, R_safe, I, mu, z_norm=0.0):
    return (B_rem - R_safe - abs(I) * (1 + mu) * z_norm) / (abs(I) * (1 + mu))


def step(K, I, p, dp, C_hedge=0.0, C_fill=0.0):
    """Mark to market a price move dp and pay hedge and fill costs from cash."""
    return K - C_hedge - C_fill, I, p + dp


def run_balance_sheet(seed=12, cases=20000):
    """Sufficiency of the guard inequality over adversarial price moves (z = 0, one step), and the Section 6 scenario."""
    # scenario of Section 6 (E0 = 10,000, I0 = -2,000 at 100, mu = 0.005, buffer 9,050, reserve 950)
    p0, I0, mu, R_safe = 100.0, -2000.0, 0.005, 950.0
    K0 = 10000.0 - I0 * p0; c0 = mu * abs(I0) * p0 - (10000.0 - 9050.0)
    B0 = buffer(K0, I0, p0, mu, c0); u_adm = admissible_shock_alpha0(B0, R_safe, I0, mu)
    after = {d: buffer(*step(K0, I0, p0, d), mu, c0) for d in (4.02, u_adm, 4.05)}
    scen = {"buffer": B0, "c0": c0, "admissible_shock": u_adm, "buffer_after_move": {f"{d:.4f}": v for d, v in after.items()},
            "reserve_kept_at_4.02": after[4.02] >= R_safe, "reserve_kept_at_adm": after[u_adm] >= R_safe - 1e-9,
            "reserve_violated_at_4.05": after[4.05] < R_safe}
    # random states: if the inequality holds, every move within the envelope keeps the buffer above the reserve
    rng = np.random.default_rng(seed); viol = 0; tight = []; held = 0
    for _ in range(cases):
        p = rng.uniform(10, 200); I = rng.uniform(-5000, 5000); mu_ = rng.uniform(0.002, 0.05)
        E = abs(I) * p * rng.uniform(0.05, 0.6); K = E - I * p; c0_ = rng.uniform(0, 0.5) * mu_ * abs(I) * p
        R_ = rng.uniform(0, 0.3) * E; Ch, Cf = rng.uniform(0, 0.02) * E, rng.uniform(0, 0.02) * E
        s, G, u = 1.0, rng.uniform(1, 5), rng.uniform(0, 0.05) * p
        if guard_lhs(I, mu_, 1.0, 0.0, s, G, u, Ch, Cf, R_) > buffer(K, I, p, mu_, c0_):
            continue
        held += 1
        for dp in (s * G * u, -s * G * u, rng.uniform(-1, 1) * s * G * u):       # worst moves are at the envelope edges
            b = buffer(*step(K, I, p, dp, Ch, Cf), mu_, c0_)
            viol += b < R_ - 1e-9 * max(1.0, E); tight.append(b - R_)
    return {"scenario": scen, "states_satisfying_guard": held, "violations": viol, "min_slack": float(min(tight)),
            "pass": bool(viol == 0 and scen["reserve_kept_at_4.02"] and scen["reserve_violated_at_4.05"])}
