"""Example ex:witness and Proposition prop:twoworld (blueprint D2, D4; tests T01, T02).

Two stable markets agree EXACTLY on the price responses at lags 0-2 (rational arithmetic) and differ threefold in summed
response, hence in safe capacity; any supervisor that rarely admits an unsafe level gives up capacity (two-world bound)."""
from fractions import Fraction as Fr
import numpy as np
from model_contracts import impulse, impulse_exact, summed_response
from uncertainty_calibration import certificate


def witness():
    a, ka = Fr(2, 5), Fr(1)
    A = ([Fr(8, 100)], [Fr(1, 2)])
    B = ([Fr(2, 100) / Fr(95, 100), Fr(2, 100) / Fr(5, 100)], [Fr(95, 100), Fr(5, 100)])
    return a, ka, A, B


def capacity_loss_bound(vA, vB, beta, tv):
    return (vA - vB) * max(0.0, 1 - beta - tv)


def run_witness():
    a, ka, A, B = witness()
    hA, hB = impulse_exact(a, ka, *A, 8), impulse_exact(a, ka, *B, 8)
    SA = ka / (1 - a - ka * sum(A[0])); SB = ka / (1 - a - ka * sum(B[0]))
    out = {"h_A": [str(x) for x in hA[:5]], "h_B": [str(x) for x in hB[:5]],
                        "equal_lags": [k for k in range(8) if hA[k] == hB[k]], "first_differ": next(k for k in range(8) if hA[k] != hB[k]),
                        "S_A": float(SA), "S_B": float(SB), "safe_shock_A": float(1 / SA), "safe_shock_B": float(1 / SB),
                        "pass": hA[:3] == hB[:3] and hA[3] != hB[3]}
    return out, SA, SB


def run_two_world(SA, SB):
    # (a) exact witness, TV = 0: every rule with P_B(admit > v_B) <= beta loses >= (1-beta)(v_A - v_B) in A.
    vA, vB = float(1 / SA), float(1 / SB)
    rules = {}
    for beta in [0.0, 0.05, 0.10]:
        # the best beta-safe rule on identical data: admit vA with prob beta, else vB (randomized); its loss in A attains the bound
        loss_A = (1 - beta) * (vA - vB)
        rules[str(beta)] = {"bound": capacity_loss_bound(vA, vB, beta, 0.0), "attained_by_randomized_rule": loss_A}
    # (b) noisy two-point: two single-cohort markets differing in q; certificate rule (Theorem C) at level beta
    rng = np.random.default_rng(2)
    a_, ka_, eta_, sig = 0.5, 0.8, 0.4, 0.2
    rho_, sbar_ = 0.6, 0.8
    def cap_of(q):   # safe per-period shock for unit inventory and unit budget = 1/S
        return 1.0 / summed_response(a_, ka_, q)
    noisy = []
    for q0, q1 in [(0.200, 0.202), (0.200, 0.205), (0.200, 0.210)]:
        h0, h1 = impulse(a_, ka_, [q0], [eta_], 400), impulse(a_, ka_, [q1], [eta_], 400)
        v0, v1 = cap_of(q1), cap_of(q0)            # market 0 (riskier, q1) has smaller capacity v0
        for N in [1, 4, 16]:
            T = 40
            dh = np.linalg.norm(h1[:T] - h0[:T]); tv = min(1.0, dh * np.sqrt(N) / (2 * sig))
            losses = []; unsafe = 0
            for rep in range(2000):
                hb_safe = h0[:T] + rng.normal(0, sig / np.sqrt(N), T)          # data from the safer market (q0)
                hb_risk = h1[:T] + rng.normal(0, sig / np.sqrt(N), T)
                for hb, is_safe in [(hb_safe, True), (hb_risk, False)]:
                    Sup = certificate(np.r_[hb, np.zeros(400 - T)], sig, N, ka_, rho_, sbar_, T, gamma=0.05)
                    adm = 1.0 / Sup
                    if is_safe:
                        losses.append(v1 - min(adm, v1))
                    else:
                        unsafe += adm > v0
            noisy.append({"q0": q0, "q1": q1, "N": N, "TV_upper": tv, "beta_empirical": unsafe / 2000,
                          "mean_capacity_loss_safe_market": float(np.mean(losses)),
                          "lower_bound": capacity_loss_bound(v1, v0, 0.05, tv), "respects_bound": float(np.mean(losses)) >= capacity_loss_bound(v1, v0, 0.05, tv) - 1e-12})
    return {"witness": rules, "noisy": noisy, "pass": all(x["respects_bound"] for x in noisy)}
