"""Paper 2 equilibrium: dealers provide reversion m, momentum traders provide q; tail loss is Lambda * S,
S = kt / (m - q kt), kt = kappa + phi eps / r. Verifies the closed form and computes the equilibrium."""
import numpy as np, json
from scipy.optimize import brentq
import numpy as np
def imp(a,phi,kappa,r,eps,eta,q,L=3000):
    x=np.zeros(L); d=np.zeros(L); f=np.zeros(L)
    for t in range(L):
        if t>0: f[t]=(1-eta)*f[t-1]+eta*q*x[t-1]
        tot=(1.0 if t==0 else 0.0)+f[t]
        x[t]=(a*x[t-1]+phi*d[t-1] if t else 0)+kappa*tot
        d[t]=((1-r)*d[t-1] if t else 0)+eps*tot
    return x
def J(a,phi,kappa,r,eps,eta,q):
    # state (x,d,f): f_t=(1-eta)f+eta q x ; x_t = a x + phi d + kappa f_t ; d_t=(1-r)d+eps f_t
    F=np.array([[0,0,0],[0,0,0],[eta*q,0,1-eta]],float)
    M=np.zeros((3,3)); M[2]=[eta*q,0,1-eta]
    M[0]=[a+kappa*eta*q, phi, kappa*(1-eta)]
    M[1]=[eps*eta*q, 1-r, eps*(1-eta)]
    return M
# 1) closed form for the summed response
rng = np.random.default_rng(11); errs = []; n = 0
while n < 3000:
    a = rng.uniform(0.5, 0.995); kappa = 10 ** rng.uniform(-1, 0.5); r = rng.uniform(0.02, 1); eta = 10 ** rng.uniform(-2, 0)
    phi, eps = rng.uniform(0, 2), rng.uniform(0, 0.3); q = 10 ** rng.uniform(-3, 0)
    Mx = J(a, phi, kappa, r, eps, eta, q)
    if max(abs(np.linalg.eigvals(Mx))) > 0.995: continue
    h = imp(a, phi, kappa, r, eps, eta, q, L=6000); kt = kappa + phi * eps / r; m = 1 - a
    S = kt / (m - q * kt); n += 1; errs.append(abs(h.sum() - S) / S)
print(f"closed form for sum h_k: {n} stable draws, max relative error {max(errs):.2e}")
# 2) equilibrium. Dealer i: v s_i - c/2 s_i^2 - (theta/N) Lam S(m); planner: N(v s - c/2 s^2) - Lam S(m)
def S_of(m, q, kt): return kt / (m - q * kt)
def g(m, q, kt): return kt / (m - q * kt) ** 2                        # -dS/dm
def m_nash(N, v, c, th, Lam, m0, q, kt):
    f = lambda m: N * (v + (th / N) * Lam * g(m, q, kt)) / c - (m - m0)
    return brentq(f, q * kt + 1e-9, 50)
def m_plan(N, v, c, Lam, m0, q, kt):
    f = lambda m: N * (v + Lam * g(m, q, kt)) / c - (m - m0)
    return brentq(f, q * kt + 1e-9, 50)
base = dict(v=0.002, c=0.5, th=0.3, Lam=1e-4, m0=0.005, q=0.02, kt=1.0)
rows = []
for N in [1, 2, 3, 5, 8, 12, 20, 40]:
    mn = m_nash(N, **base); mp = m_plan(N, **{k: v for k, v in base.items() if k != "th"})
    Sn, Sp = S_of(mn, base["q"], base["kt"]), S_of(mp, base["q"], base["kt"])
    tau = (1 - base["th"] / N) * base["Lam"] * g(mn, base["q"], base["kt"])
    rows.append({"N": N, "m_nash": mn, "m_plan": mp, "S_nash": Sn, "S_plan": Sp, "S_gap_pct": 100 * (Sn / Sp - 1),
                 "pigou_rebate": tau, "rebate_from_S": (1 - base["th"] / N) * base["Lam"] * Sn ** 2 / base["kt"]})
    print({k: round(v, 5) for k, v in rows[-1].items()})
# momentum traders: aggregate q chosen with private value b q - e/2 q^2 vs social minus Lam S
b, e = 0.3, 20.0
qn = b / e
qp = brentq(lambda q: b - e * q - base["Lam"] * base["kt"] ** 2 / (0.03 - q * base["kt"]) ** 2, 0, 0.03 - 1e-9)
print(f"momentum: private q = {qn:.4f}, planner q = {qp:.4f} (m = 0.03)")
json.dump({"closed_form_max_rel_err": max(errs), "draws": n, "params": base, "by_N": rows, "momentum": {"q_private": qn, "q_planner": qp}},
          open("R_P2_equilibrium.json", "w"), indent=1)
