"""Proof audit, October 2026: independent symbolic and numerical checks of statements in both papers.
Output: recomputed/R_audit_oct2026.json
"""
import json, os
import numpy as np, sympy as sp
from scipy.optimize import brentq

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recomputed", "R_audit_oct2026.json")
res = {}

# ---- Paper 2, Proposition sum: closed form of S and det(I - M3) (symbolic) ----
a, phi, eps, kap, r, eta, q = sp.symbols('a phi epsilon kappa r eta q', real=True)
M3 = sp.Matrix([[a + kap*eta*q, phi, kap*(1-eta)], [eps*eta*q, 1-r, eps*(1-eta)], [eta*q, 0, 1-eta]])
S = sp.simplify(((sp.eye(3) - M3).inv() * sp.Matrix([kap, eps, 0]))[0])
kt = kap + phi*eps/r
res["P2_prop_sum_symbolic_residual"] = str(sp.simplify(S - kt/((1-a) - q*kt)))
res["P2_prop_sum_det_residual"] = str(sp.simplify((sp.eye(3)-M3).det() - eta*(r*((1-a)-kap*q) - phi*eps*q)))

# ---- Paper 2, Proposition shape: peak time ----
rng = np.random.default_rng(2)
n = 200000
A_ = rng.uniform(0.01, 0.999, n); R_ = rng.uniform(0.001, 0.99, n); B_ = 1 - R_; PE = rng.uniform(0, 2, n)
ok = (np.abs(A_ - B_) > 1e-3) & (PE - (1 - A_) > 0)
A_, B_, PE = A_[ok], B_[ok], PE[ok]
Bc = PE / (B_ - A_); Ac = 1 - Bc
ks = np.log(-Ac*np.log(A_)/(Bc*np.log(B_))) / np.log(B_/A_)
k = np.arange(0, 3000); kp = np.empty(len(A_), int)
for i in range(0, len(A_), 2000):
    h = Ac[i:i+2000, None]*A_[i:i+2000, None]**k + Bc[i:i+2000, None]*B_[i:i+2000, None]**k
    kp[i:i+2000] = np.argmax(h, 1)
near = np.rint(ks).astype(int)
lo, hi = np.maximum(np.floor(ks), 1).astype(int), np.maximum(np.ceil(ks), 1).astype(int)
res["P2_prop_shape"] = {"amplifying_draws": int(len(A_)), "share_peak_not_nearest_integer": float(np.mean(kp != near)),
                        "share_peak_outside_floor_ceil_bracket": float(np.mean((kp != lo) & (kp != hi)))}

# ---- Paper 2, Remark counterexamples ----
def sim3(a_, ph, ep, ka, r_, et, q_, L=2000):
    x = np.zeros(L); d = np.zeros(L); f = np.zeros(L)
    for t in range(L):
        u = 1.0 if t == 0 else 0.0
        if t > 0:
            f[t] = (1-et)*f[t-1] + et*q_*x[t-1]
        x[t] = (a_*x[t-1] + ph*d[t-1] if t else 0) + ka*(u + f[t])
        d[t] = ((1-r_)*d[t-1] if t else 0) + ep*(u + f[t])
    M = np.array([[a_+ka*et*q_, ph, ka*(1-et)], [ep*et*q_, 1-r_, ep*(1-et)], [et*q_, 0, 1-et]])
    kk = int(np.argmax(np.abs(x)))
    return {"C3": ph*ep + ka**2*et*q_ - (1-a_)*ka, "rho": float(max(abs(np.linalg.eigvals(M)))), "peak": float(x[kk]), "lag": kk}
res["P2_remark_counterexamples"] = [sim3(0.98526, 0.7409, 0.01183, 1, 0.03436, 0.5092, 0.01127),
                                    sim3(0.9426, 2.614, -0.405, 1, 0.033, 0.0016, 0.0785)]

# ---- Paper 2, Proposition equil: numerical example ----
v, c, th, Lam, m0, qq, ktt = 0.002, 0.5, 0.3, 1e-4, 0.005, 0.02, 1.0
g = lambda m: ktt/(m-qq*ktt)**2; Sf = lambda m: ktt/(m-qq*ktt)
eq = {}
for N in [1, 40]:
    meq = brentq(lambda m: m-m0-N*v/c-th*Lam*g(m)/c, qq*ktt+1e-9, 10)
    msp = brentq(lambda m: m-m0-N*v/c-N*Lam*g(m)/c, qq*ktt+1e-9, 10)
    eq[N] = {"S_eq": Sf(meq), "S_sp": Sf(msp)}
qsp = brentq(lambda x: 0.3-20*x-Lam*ktt**2/(0.03-x*ktt)**2, 0, 0.03-1e-9)
res["P2_prop_equil"] = {"by_N": eq, "q_private": 0.015, "q_planner": qsp}

# ---- Paper 1, Theorem quantity: K* bound and d_2 identity ----
def impulse(a_, ka, qs, etas, L=3000):
    y = np.zeros(len(qs)); xp = 0; h = np.zeros(L)
    for t in range(L):
        x = a_*xp + ka*np.dot(qs, y) + (ka if t == 0 else 0)
        y = (1-etas)*y + etas*x; h[t] = x; xp = x
    return h
rng = np.random.default_rng(3); worst1 = 0; cnt = 0; d2err = 0
for i in range(3000):
    a_ = rng.uniform(0, 0.95); ka = rng.uniform(0.05, 2); Sx = rng.uniform(0.05, 0.98)
    if Sx <= a_:
        continue
    q_ = (Sx-a_)/ka; e_ = rng.uniform(0.02, 0.4); et = rng.uniform(e_+1e-3, 1-e_-1e-3)
    dl = rng.uniform(0, 1)*min(et-e_, 1-e_-et)
    if dl < 1e-4:
        continue
    dd = impulse(a_, ka, np.array([q_/2, q_/2]), np.array([et-dl, et+dl])) - impulse(a_, ka, np.array([q_]), np.array([et]))
    Ks = 2*ka**2*q_/(e_**3*(1-Sx)**2)
    worst1 = max(worst1, np.abs(dd).sum()/(Ks*dl*dl)); d2err = max(d2err, abs(dd[2]+ka**2*q_*dl*dl)); cnt += 1
res["P1_thm_quantity"] = {"draws": cnt, "max_l1_norm_over_Kstar_delta2": worst1, "max_abs_error_d2_identity": d2err}

# ---- Paper 1, Theorem twocohort: moment identities (symbolic) ----
qs_, tau, eb, D = sp.symbols('q tau etabar Delta', positive=True)
pm = sp.Rational(1, 2) - tau/qs_; pp = sp.Rational(1, 2) + tau/qs_
t0 = [(qs_*pm, eb-pp*D), (qs_*pp, eb+pm*D)]; t1 = [(qs_*pp, eb-pm*D), (qs_*pm, eb+pp*D)]
dm = [sp.simplify(sum(w*e**m for w, e in t1) - sum(w*e**m for w, e in t0)) for m in range(4)]
res["P1_thm_twocohort_moment_gaps_0_to_2"] = [str(x) for x in dm[:3]]
res["P1_thm_twocohort_M3_residual"] = str(sp.simplify(dm[3] - 4*tau*pm*pp*D**3))

# ---- Paper 1, Theorem blind: example numbers ----
bl = {}
for thv in [1, 3, 10, 30, 100]:
    J = np.array([[0.8, thv], [0, 0.7]]); Jk = np.eye(2); gs = []
    for kk in range(400):
        gs.append(np.linalg.norm(Jk[0])); Jk = Jk @ J
    bl[thv] = {"gain": max(gs), "cumulative": sum(gs)}
res["P1_thm_blind"] = bl

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, "w"), indent=2, default=float)
print(json.dumps(res, indent=1, default=float))
