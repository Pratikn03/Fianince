"""Price responses of the three-state book of Section 4 (depletion, refill, momentum) and the mechanism controls of test T08
(blueprint E08): channels with equal summed response give equal guard capacity although their peaks and one-period margins differ."""
import numpy as np
from scipy.optimize import brentq


def imp_t6(a, phi, kappa, r, eps, eta, q, L=4000):
    x = np.zeros(L); dd = np.zeros(L); f = np.zeros(L)
    for t in range(L):
        if t > 0:
            f[t] = (1 - eta) * f[t - 1] + eta * q * x[t - 1]
        tot = (1.0 if t == 0 else 0.0) + f[t]
        x[t] = (a * x[t - 1] + phi * dd[t - 1] if t else 0) + kappa * tot
        dd[t] = ((1 - r) * dd[t - 1] if t else 0) + eps * tot
    return x


def run_mechanisms():
    target = 5.0; kap = 1.0
    # (i) momentum feedback only; (ii) depth only; (iii) slow dealer reversion only
    m_i = None
    qi = brentq(lambda q: imp_t6(0.6, 0, kap, 0.1, 0, 0.3, q).sum() - target, 0, 0.39)
    ei = brentq(lambda e: imp_t6(0.6, 0.5, kap, 0.1, e, 0.3, 0.0).sum() - target, 0, 1.0)
    ai = brentq(lambda a: imp_t6(a, 0, kap, 0.1, 0, 0.3, 0.0).sum() - target, 0, 0.95)
    qf = brentq(lambda q: imp_t6(0.6, 0, kap, 0.1, 0, 1.0, q).sum() - target, 0, 0.39)
    ch = {"momentum_learners": imp_t6(0.6, 0, kap, 0.1, 0, 0.3, qi), "fixed_rule_traders": imp_t6(0.6, 0, kap, 0.1, 0, 1.0, qf), "depth": imp_t6(0.6, 0.5, kap, 0.1, ei, 0.3, 0.0),
          "slow_reversion": imp_t6(ai, 0, kap, 0.1, 0, 0.3, 0.0)}
    out = {k: {"S": float(v.sum()), "sum_abs": float(np.abs(v).sum()), "peak": float(v.max()), "h1_minus_h0": float(v[1] - v[0]),
                               "guard_capacity_unit_budget": float(1 / np.abs(v).sum())} for k, v in ch.items()}
    out["note"] = "equal S gives equal guard capacity whatever the channel; peak and one-period margin differ"

    return out
