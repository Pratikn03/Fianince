"""Information-safety extension of Paper 2: simulation tests T01-T09 and T12 (data-free). Writes results/IS_results.json.
Run: python3 run_all.py   (deterministic seeds; about 5-10 minutes)."""
import json, os, itertools, time
from fractions import Fraction as Fr
import numpy as np
from scipy.stats import norm
from model_contracts import (impulse, impulse_exact, kernel, moments_from_impulse, summed_response, closed_loop_matrix,
                             impulse_state_space)
from markov_krein import phi_bounds, best_approx_error_formula, principal
from certificate import certificate, lam_bar, tail_bound, T_for, N_sufficient, lower_bound_N
from robust_admission import alpha_star, S_alpha, Phi_from_S

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results"); os.makedirs(OUT, exist_ok=True)
R = {}
t0 = time.time()

# ---------------------------------------------------------------- T01: exact two-market witness (rational arithmetic)
a, ka = Fr(2, 5), Fr(1)
A = ([Fr(8, 100)], [Fr(1, 2)])
B = ([Fr(2, 100) / Fr(95, 100), Fr(2, 100) / Fr(5, 100)], [Fr(95, 100), Fr(5, 100)])
hA, hB = impulse_exact(a, ka, *A, 8), impulse_exact(a, ka, *B, 8)
SA = ka / (1 - a - ka * sum(A[0])); SB = ka / (1 - a - ka * sum(B[0]))
R["T01_witness"] = {"h_A": [str(x) for x in hA[:5]], "h_B": [str(x) for x in hB[:5]],
                    "equal_lags": [k for k in range(8) if hA[k] == hB[k]], "first_differ": next(k for k in range(8) if hA[k] != hB[k]),
                    "S_A": float(SA), "S_B": float(SB), "safe_shock_A": float(1 / SA), "safe_shock_B": float(1 / SB),
                    "pass": hA[:3] == hB[:3] and hA[3] != hB[3]}

# ---------------------------------------------------------------- T02: information-safety lower bound (Theorem A)
# (a) exact witness, TV = 0: every rule with P_B(admit > v_B) <= beta loses >= (1-beta)(v_A - v_B) in A.
vA, vB = float(1 / SA), float(1 / SB)
def capacity_loss_bound(vA, vB, beta, tv):
    return (vA - vB) * max(0.0, 1 - beta - tv)
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
R["T02_two_world"] = {"witness": rules, "noisy": noisy, "pass": all(x["respects_bound"] for x in noisy)}

# ---------------------------------------------------------------- Theorem B checks (window certification)
rhoB = 0.95; aB, kaB = 0.4, 1.0
rB = np.linspace(0.05, 0.93, 8); etaB = 1 - rB; qB = np.full(8, 0.42 / 8)
hBf = impulse(aB, kaB, qB, etaB, 60)
TB = []
for n in [3, 4, 6, 8, 10, 12, 16, 20]:
    c = moments_from_impulse(aB, kaB, hBf, n)
    try:
        lo, up, L_, U_ = phi_bounds(c, rhoB)
    except ValueError:
        TB.append({"n": n, "note": "moment vector on the boundary: measure identified"}); continue
    w = up - lo; bnd = 2 * c[0] * best_approx_error_formula(n - 1, rhoB)
    TB.append({"n": n, "Phi_lo": lo, "Phi_up": up, "Phi_true": float(qB.sum()),
               "S_lo": summed_response(aB, kaB, lo), "S_up": summed_response(aB, kaB, up),
               "width": w, "width_bound": bnd, "within_bound": w <= bnd * (1 + 1e-9)})
div = []
r_ = np.array([0.2, 0.5, 0.8]); w_ = np.array([0.3, 0.3, 0.2]); cc = [float(np.sum(w_ * r_ ** j)) for j in range(4)]
for rho in [0.9, 0.99, 0.999, 0.9999]:
    div.append({"rho": rho, "Phi_up": phi_bounds(cc, rho)[1]})
R["ThmB_window"] = {"market_B_rho_0.95": TB, "divergence_as_rho_to_1": div}

# ---------------------------------------------------------------- T03: risk-specific vs identification sample complexity
# Paper 1 two-cohort family (q = 0.2, etabar = 0.4, tau = 0.01, a = 0.5, kappa = 0.8, sigma_h = 1.6e-3 per tap)
a3, k3, q3, eb, tau, sg = 0.5, 0.8, 0.20, 0.40, 0.01, 1.6e-3
pm, pp = 0.5 - tau / q3, 0.5 + tau / q3
rows3 = []
for De in [0.30, 0.20, 0.14, 0.10, 0.08, 0.06, 0.05, 0.04]:
    th0 = ([q3 * pm, q3 * pp], [eb - pp * De, eb + pm * De]); th1 = ([q3 * pp, q3 * pm], [eb - pm * De, eb + pp * De])
    h0, h1 = impulse(a3, k3, *th0, 121), impulse(a3, k3, *th1, 121)
    N_id = 4 * sg ** 2 * norm.ppf(0.95) ** 2 / np.sum((h1 - h0) ** 2)
    S0 = summed_response(a3, k3, q3)
    eps = 0.01 * S0                                    # certify S to within 1%
    rmax = max(1 - np.array(th0[1] + th1[1])); sbar = a3 + k3 * q3 + 0.02
    N_cert, Tc = N_sufficient(eps, sg, k3, rmax, sbar)
    rows3.append({"Delta_eta": De, "N_identify_weights_LeCam": N_id, "N_certify_S_1pct_sufficient": N_cert, "T": Tc,
                  "S_theta0": S0, "S_theta1": summed_response(a3, k3, sum(th1[0])), "S_equal": abs(S0 - summed_response(a3, k3, sum(th1[0]))) < 1e-12})
lD = np.log([r["Delta_eta"] for r in rows3])
R["T03_sample_complexity"] = {"rows": rows3,
                              "slope_identify": float(np.polyfit(lD, np.log([r["N_identify_weights_LeCam"] for r in rows3]), 1)[0]),
                              "slope_certify": float(np.polyfit(lD, np.log([r["N_certify_S_1pct_sufficient"] for r in rows3]), 1)[0])}
# lower bound constant for certification: single cohort, perturb q
qq, et = 0.2, 0.4; dq = 1e-6
hq0, hq1 = impulse(a3, k3, [qq], [et], 400), impulse(a3, k3, [qq + dq], [et], 400)
dS = summed_response(a3, k3, qq + dq) - summed_response(a3, k3, qq)
C_lb = np.linalg.norm(hq1 - hq0) / dS
eps_grid = [0.1, 0.03, 0.01, 0.003]
R["T03_sample_complexity"]["cert_rates"] = [{"eps": e, "N_lower": lower_bound_N(e, sg, C_lb), "N_upper": N_sufficient(e, sg, k3, 1 - et, a3 + k3 * qq + 0.02)[0]}
                                            for e in eps_grid]
R["T03_sample_complexity"]["cert_slope_upper_in_eps"] = float(np.polyfit(np.log(eps_grid), np.log([x["N_upper"] for x in R["T03_sample_complexity"]["cert_rates"]]), 1)[0])

# ---------------------------------------------------------------- T04: coverage, width, abstention of the certificate
rng = np.random.default_rng(4); cov = []
for (rho, sbar) in [(0.6, 0.7), (0.9, 0.8), (0.97, 0.85)]:
    for N in [20, 200, 2000]:
        for gamma in [0.05, 0.10]:
            miss = 0; widths = []; abst = 0; reps = 1000
            for rep in range(reps):
                K = rng.integers(1, 4); eta = rng.uniform(1 - rho, 0.95, K); aa = rng.uniform(0.1, 0.6); kk = rng.uniform(0.3, 1.2)
                Phi_ = rng.uniform(0.05, 1.0) * (sbar - aa) / kk
                if Phi_ <= 0:
                    continue
                q = rng.dirichlet(np.ones(K)) * Phi_
                h = impulse(aa, kk, q, eta, 800); S = h.sum(); sig_ = 0.05 * kk
                T = T_for(0.05 * S, kk, rho, sbar); T = min(T, 800)
                hb = h + rng.normal(0, sig_ / np.sqrt(N), 800)
                Sup = certificate(hb, sig_, N, kk, rho, sbar, T, gamma)
                miss += Sup < S; widths.append(Sup / S - 1)
                abst += alpha_star(aa, kk, Phi_from_S(aa, kk, Sup) if Sup > 0 else np.inf, 1.0, 0.2 * (1 - aa) / kk, 1.0) in (None, 0.0)
            cov.append({"rho": rho, "sbar": sbar, "N": N, "gamma": gamma, "coverage": 1 - miss / reps,
                        "median_rel_excess": float(np.median(widths)), "abstain_rate": abst / reps})
R["T04_coverage"] = {"rows": cov, "pass": all(r["coverage"] >= 1 - r["gamma"] - 0.02 for r in cov)}

# ---------------------------------------------------------------- T05: exact worst case by exhaustive sign enumeration
rng = np.random.default_rng(5); t5 = {"per_period_sum_exact": 0, "total_budget_peak_exact": 0, "peak_under_per_period_violations": 0, "cases": 0}
for trial in range(200):
    n = 3; J = rng.normal(0, 0.5, (n, n)); J /= max(1.0, max(abs(np.linalg.eigvals(J))) / 0.95)
    Hv = rng.normal(0, 1, n); C = rng.normal(0, 1, n)
    for Tn in range(1, 11):
        g = np.array([C @ np.linalg.matrix_power(J, m) @ Hv for m in range(Tn)])
        worst = max(abs(np.dot(g[::-1], np.array(s))) for s in itertools.product([-1, 1], repeat=Tn))
        t5["per_period_sum_exact"] += abs(worst - np.abs(g).sum()) < 1e-9
        vert = max(abs(g))                                   # l1 ball: maximum at a vertex
        t5["total_budget_peak_exact"] += abs(vert - np.max(np.abs(g))) < 1e-12
        t5["peak_under_per_period_violations"] += worst > np.max(np.abs(g)) + 1e-12
        t5["cases"] += 1
t5["pass"] = t5["per_period_sum_exact"] == t5["cases"]
R["T05_exact_worst_case"] = t5

# ---------------------------------------------------------------- T06: optimizer correctness (closed form vs brute force)
rng = np.random.default_rng(6); mism = 0; nonint = 0; cases = 0; infeas = 0
for trial in range(500):
    K = rng.integers(1, 4); eta = rng.uniform(0.05, 0.95, K); aa = rng.uniform(0, 0.8); kk = rng.uniform(0.2, 1.5)
    Phi_ = rng.uniform(0.1, 2.0) * (1 - aa) / kk; q = rng.dirichlet(np.ones(K)) * Phi_
    I, ub, Bb = rng.uniform(0.5, 2), rng.uniform(0.01, 0.3), 1.0
    ast = alpha_star(aa, kk, Phi_, I, ub, Bb)
    grid = np.linspace(0, 1, 1001)
    safe = []
    for al in grid:
        Jm = closed_loop_matrix(aa, kk, al * q, eta); bvec = kk * np.r_[1.0, eta]
        if max(abs(np.linalg.eigvals(Jm))) >= 1:
            safe.append(False); continue
        Smat = np.linalg.solve(np.eye(K + 1) - Jm, bvec)[0]
        safe.append(I * ub * Smat <= Bb * (1 + 1e-9))
    safe = np.array(safe)
    cases += 1
    if ast is None:
        infeas += 1; mism += safe.any(); continue
    bf = grid[safe].max() if safe.any() else None
    mism += bf is None or abs(bf - ast) > 1.5e-3
    first_unsafe = np.argmax(~safe) if (~safe).any() else len(safe)
    nonint += safe[first_unsafe:].any()
R["T06_optimizer"] = {"cases": cases, "mismatches": int(mism), "non_interval_safe_sets": int(nonint), "infeasible_states": infeas,
                      "pass": mism == 0 and nonint == 0}

# ---------------------------------------------------------------- T07: value of disclosure
rng = np.random.default_rng(7); t7 = []
for rho_true in [0.6, 0.9, 0.97, 0.995]:
    aa, kk = 0.4, 1.0; eta = np.array([1 - rho_true, 0.5]); q = np.array([0.06, 0.12])     # one long-memory class
    Phi_ = q.sum(); S = summed_response(aa, kk, Phi_); I, ub, Bb = 1.0, 0.48, 1.0
    a_oracle = alpha_star(aa, kk, Phi_, I, ub, Bb)
    sbar = aa + kk * Phi_ + 0.02; N, sig_ = 500, 0.05
    res = {"rho": rho_true, "S": S, "alpha_oracle_audited": a_oracle}
    # public: price-response certificate with memory bound rho_true
    aps = []
    h = impulse(aa, kk, q, eta, 20000); T = min(T_for(0.02 * S, kk, rho_true, sbar), 20000)
    for rep in range(300):
        hb = h[:T] + rng.normal(0, sig_ / np.sqrt(N), T)
        Sup = certificate(np.r_[hb], sig_, N, kk, rho_true, sbar, T, 0.05)
        aps.append(alpha_star(aa, kk, Phi_from_S(aa, kk, Sup), I, ub, Bb) or 0.0)
    res["alpha_public_mean"] = float(np.mean(aps)); res["T_public"] = int(T)
    # class-tagged: each class's flow u_c,t = r_c u_c,t-1 + w_c x_t + noise; passive data, T_f periods
    Tf, sf = 2000, 0.02; atg = []
    for rep in range(300):
        x = np.zeros(Tf); y = np.zeros(2)
        for t in range(1, Tf):
            x[t] = aa * x[t - 1] + kk * np.dot(q, y) + rng.normal(0, 1); y = (1 - eta) * y + eta * x[t]
        Phi_up = 0.0; var_sum = 0.0
        for c in range(2):
            u = q[c] * np.zeros(Tf); yy = 0.0
            yc = np.zeros(Tf)
            for t in range(1, Tf):
                yc[t] = (1 - eta[c]) * yc[t - 1] + eta[c] * x[t]
            sig_c = q[c] * yc; u = sig_c + rng.normal(0, 0.1 * np.std(sig_c), Tf)   # tagged flows measured with 10% noise
            # 2SLS: u_t on (u_{t-1}, x_t), instrumenting the noisy u_{t-1} by u_{t-2} (Paper 1, Proposition tagged)
            yv = u[2:]; X = np.c_[u[1:-1], x[2:]]; Z = np.c_[u[:-2], x[2:]]
            Pz = Z @ np.linalg.solve(Z.T @ Z, Z.T @ X)
            beta = np.linalg.solve(Pz.T @ X, Pz.T @ yv); res_ = yv - X @ beta
            s2 = res_ @ res_ / (len(yv) - 2); V = s2 * np.linalg.inv(Pz.T @ Pz)
            r_h, w_h = beta; g = np.array([w_h / (1 - r_h) ** 2, 1 / (1 - r_h)])
            Phi_up += w_h / (1 - r_h); var_sum += g @ V @ g
        Phi_up += norm.ppf(0.95) * np.sqrt(var_sum)
        atg.append(alpha_star(aa, kk, max(Phi_up, 1e-9), I, ub, Bb) or 0.0)
    res["alpha_tagged_mean"] = float(np.mean(atg))
    res["value_tagged_vs_public"] = res["alpha_tagged_mean"] - res["alpha_public_mean"]
    res["value_audited_vs_public"] = a_oracle - res["alpha_public_mean"]
    t7.append(res)
R["T07_disclosure"] = {"rows": t7, "note": "capacity alpha* in [0,1]; value = extra admitted fraction of algorithmic flow; "
                       "net value = w * value - disclosure cost, which can be negative"}

# ---------------------------------------------------------------- T08: mechanism controls (same S, different channels)
def imp_t6(a, phi, kappa, r, eps, eta, q, L=4000):
    x = np.zeros(L); dd = np.zeros(L); f = np.zeros(L)
    for t in range(L):
        if t > 0:
            f[t] = (1 - eta) * f[t - 1] + eta * q * x[t - 1]
        tot = (1.0 if t == 0 else 0.0) + f[t]
        x[t] = (a * x[t - 1] + phi * dd[t - 1] if t else 0) + kappa * tot
        dd[t] = ((1 - r) * dd[t - 1] if t else 0) + eps * tot
    return x
target = 5.0; kap = 1.0
# (i) momentum feedback only; (ii) depth only; (iii) slow dealer reversion only
m_i = None
from scipy.optimize import brentq
qi = brentq(lambda q: imp_t6(0.6, 0, kap, 0.1, 0, 0.3, q).sum() - target, 0, 0.39)
ei = brentq(lambda e: imp_t6(0.6, 0.5, kap, 0.1, e, 0.3, 0.0).sum() - target, 0, 1.0)
ai = brentq(lambda a: imp_t6(a, 0, kap, 0.1, 0, 0.3, 0.0).sum() - target, 0, 0.95)
qf = brentq(lambda q: imp_t6(0.6, 0, kap, 0.1, 0, 1.0, q).sum() - target, 0, 0.39)
ch = {"momentum_learners": imp_t6(0.6, 0, kap, 0.1, 0, 0.3, qi), "fixed_rule_traders": imp_t6(0.6, 0, kap, 0.1, 0, 1.0, qf), "depth": imp_t6(0.6, 0.5, kap, 0.1, ei, 0.3, 0.0),
      "slow_reversion": imp_t6(ai, 0, kap, 0.1, 0, 0.3, 0.0)}
R["T08_mechanisms"] = {k: {"S": float(v.sum()), "sum_abs": float(np.abs(v).sum()), "peak": float(v.max()), "h1_minus_h0": float(v[1] - v[0]),
                           "guard_capacity_unit_budget": float(1 / np.abs(v).sum())} for k, v in ch.items()}
R["T08_mechanisms"]["note"] = "equal S gives equal guard capacity whatever the channel; peak and one-period margin differ"

# ---------------------------------------------------------------- T09: misspecification stress tests of the certificate
rng = np.random.default_rng(9); t9 = {}
def run_cov(gen, reps=600, N=500, gamma=0.05, rho=0.9, sbar=0.8):
    miss = 0; viol = 0
    for rep in range(reps):
        h, kk, aa = gen()
        S_abs = np.abs(h).sum(); sig_ = 0.05 * kk
        T = min(T_for(0.05 * S_abs, kk, rho, sbar), len(h))
        hb = h + rng.normal(0, sig_ / np.sqrt(N), len(h))
        Sup = certificate(np.abs(hb), sig_, N, kk, rho, sbar, T, gamma)   # sum of |hbar| bounds sum |h| only up to noise
        miss += Sup < S_abs
    return 1 - miss / reps
def g_ok():
    K = rng.integers(1, 4); eta = rng.uniform(0.1, 0.95, K); aa = rng.uniform(0.1, 0.5); kk = rng.uniform(0.3, 1.2)
    q = rng.dirichlet(np.ones(K)) * rng.uniform(0.05, 1) * (0.8 - aa) / kk
    return impulse(aa, kk, q, eta, 3000), kk, aa
def g_longmem():          # memory longer than the declared bound (rates up to 0.995 vs declared 0.9)
    K = 2; eta = np.array([rng.uniform(0.005, 0.03), rng.uniform(0.3, 0.9)]); aa = rng.uniform(0.1, 0.5); kk = rng.uniform(0.3, 1.2)
    q = rng.dirichlet(np.ones(K)) * rng.uniform(0.3, 1) * (0.8 - aa) / kk
    return impulse(aa, kk, q, eta, 6000), kk, aa
def g_signed():           # contrarian cohorts (negative weights)
    K = 2; eta = rng.uniform(0.1, 0.95, K); aa = rng.uniform(0.1, 0.5); kk = rng.uniform(0.3, 1.2)
    q = np.array([rng.uniform(0.05, 0.3), -rng.uniform(0.05, 0.3)]) * (0.8 - aa) / kk
    return impulse(aa, kk, q, eta, 3000), kk, aa
def g_depth():            # depth channel (Paper 2 three-state book), amplifying
    aa = rng.uniform(0.5, 0.9); kk = 1.0; r = rng.uniform(0.05, 0.3); ph = rng.uniform(0.2, 1); ep = rng.uniform(0, 0.3)
    return imp_t6(aa, ph, kk, r, ep, 0.3, 0.05, L=3000), kk, aa
def g_drift():            # rates drift: certified on one economy, used on one with 20% more feedback
    h, kk, aa = g_ok(); return h * 1.0, kk, aa
def g_delay():            # feedback acts with a two-period execution delay
    K = rng.integers(1, 3); eta = rng.uniform(0.1, 0.95, K); aa = rng.uniform(0.1, 0.5); kk = rng.uniform(0.3, 1.2)
    q = rng.dirichlet(np.ones(K)) * rng.uniform(0.05, 1) * (0.8 - aa) / kk
    L = 3000; x = np.zeros(L); y = np.zeros((L, K))
    for t in range(L):
        fb = kk * np.dot(q, y[t - 2]) if t >= 2 else 0.0
        x[t] = (aa * x[t - 1] if t else 0) + fb + (kk if t == 0 else 0)
        y[t] = (1 - eta) * (y[t - 1] if t else 0) + eta * x[t]
    return x, kk, aa
for name, gen in [("as_assumed", g_ok), ("delayed_feedback", g_delay), ("memory_longer_than_declared", g_longmem), ("contrarian_cohorts", g_signed),
                  ("depth_channel", g_depth)]:
    t9[name] = {"coverage_at_95": run_cov(gen)}
# nonstationarity: certificate from economy theta, risk under theta' with Phi' = 1.2 Phi
miss = 0; reps = 600
for rep in range(reps):
    K = rng.integers(1, 4); eta = rng.uniform(0.1, 0.95, K); aa = rng.uniform(0.1, 0.5); kk = rng.uniform(0.3, 1.2)
    q = rng.dirichlet(np.ones(K)) * rng.uniform(0.05, 0.8) * (0.8 - aa) / kk
    h = impulse(aa, kk, q, eta, 3000); h2 = impulse(aa, kk, 1.2 * q, eta, 3000); sig_ = 0.05 * kk
    T = min(T_for(0.05 * h.sum(), kk, 0.9, 0.8), 3000)
    Sup = certificate(h + rng.normal(0, sig_ / np.sqrt(500), 3000), sig_, 500, kk, 0.9, 0.8, T, 0.05)
    miss += Sup < h2.sum()
t9["feedback_rises_20pct_after_certification"] = {"coverage_at_95": 1 - miss / reps}
R["T09_misspecification"] = t9

# ---------------------------------------------------------------- T12: equilibrium rebate from a certified S
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
R["T12_equilibrium_rebate"] = t12

R["runtime_seconds"] = time.time() - t0
json.dump(R, open(os.path.join(OUT, "IS_results.json"), "w"), indent=2, default=float)
print(json.dumps({k: (bool(v.get("pass")) if isinstance(v, dict) and "pass" in v else "-") for k, v in R.items()}, indent=1))
print("runtime", R["runtime_seconds"])
