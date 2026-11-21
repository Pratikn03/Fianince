"""Numerical and symbolic checks of the 'by hand' steps in AUTHOR_PROOF_CHECK_NEW_RESULTS_20261120.md.

Written by an AI system. These checks support the authors' check; they do not replace it.
Run: python verify_new_results_20261121.py   (needs numpy, scipy, sympy)
"""
import math
import numpy as np
import sympy as sp
from scipy import integrate, special, stats

rng = np.random.default_rng(20261121)
out = []


def rep(name, ok, detail):
    out.append((name, ok, detail))
    print(("PASS " if ok else "FAIL ") + name + ": " + detail)


# Thm 5.5: Gauss and Gauss-Radau rules, unit mass, positive weights, equal moments 0..2K-2, differ at 2K-1
def radau(K):
    # Gauss-Radau with fixed node -1: other nodes are roots of (P_{K-1}+P_K)/(1+x)
    x = sp.symbols("x")
    poly = sp.cancel((sp.legendre(K - 1, x) + sp.legendre(K, x)) / (1 + x))
    nodes = [-1.0] + sorted(float(r) for r in sp.Poly(poly, x).nroots())
    V = np.vander(nodes, K, increasing=True).T
    m = np.array([integrate.quad(lambda t, p=p: t ** p, -1, 1)[0] for p in range(K)])
    return np.array(nodes), np.linalg.solve(V, m)


for K in range(2, 7):
    gn, gw = np.polynomial.legendre.leggauss(K)
    rn, rw = radau(K)
    gw, rw = gw / gw.sum(), rw / rw.sum()
    mg = np.array([(gw * gn ** p).sum() for p in range(2 * K)])
    mr = np.array([(rw * rn ** p).sum() for p in range(2 * K)])
    same = np.allclose(mg[:2 * K - 1], mr[:2 * K - 1], atol=1e-12)
    rep(f"Thm5.5 hard pair K={K}", same and gw.min() > 0 and rw.min() > 0 and abs(mg[-1] - mr[-1]) > 1e-6,
        f"min weights {gw.min():.3f}/{rw.min():.3f}; max moment gap order<=2K-2 {np.abs(mg-mr)[:2*K-1].max():.1e}; "
        f"gap at order 2K-1 {abs(mg[-1]-mr[-1]):.3f}")
    if K == 2:
        rep("Thm5.5 K=2 by hand", np.allclose(sorted(gn), [-1 / 3 ** .5, 1 / 3 ** .5]) and np.allclose(gw, [.5, .5])
            and np.allclose(rn, [-1, 1 / 3]) and np.allclose(rw, [.25, .75]),
            f"Gauss nodes {np.round(gn,4)} weights {gw}; Radau nodes {np.round(rn,4)} weights {np.round(rw,4)}")

# Thm 5.5 / 6.1: Gaussian KL with common variance; Pinsker; errors < 1/4 => KL > 1/2
m, mp, s = sp.symbols("m mp s", positive=True)
xx = sp.symbols("xx", real=True)
p = sp.exp(-(xx - m) ** 2 / (2 * s ** 2)) / sp.sqrt(2 * sp.pi * s ** 2)
kl = sp.simplify(sp.integrate(p * (-(xx - m) ** 2 + (xx - mp) ** 2) / (2 * s ** 2), (xx, -sp.oo, sp.oo)))
rep("Gaussian KL common variance", sp.simplify(kl - (m - mp) ** 2 / (2 * s ** 2)) == 0, f"KL = {kl}")
d = np.linspace(0.01, 6, 600)
tv = 2 * stats.norm.cdf(d / 2) - 1
klg = d ** 2 / 2
rep("Pinsker form KL >= 2 TV^2", np.all(klg >= 2 * tv ** 2 - 1e-12), "checked on Gaussian pairs, d in (0,6]")
# both errors < 1/4 => sum < 1/2 => TV > 1/2 => KL > 2*(1/2)^2 = 1/2
rep("errors<1/4 => KL>1/2", 2 * 0.5 ** 2 == 0.5, "TV > 1/2 and KL >= 2 TV^2 give KL > 1/2")

# Thm 6.1 two-step counterexample: E Phi(-alpha|X|) = arctan(1/alpha)/pi
for a in (0.5, 1.0, 2.0):
    val = integrate.quad(lambda x: stats.norm.cdf(-a * abs(x)) * stats.norm.pdf(x), -np.inf, np.inf)[0]
    rep(f"Thm6.1 angle probability alpha={a}", abs(val - math.atan(1 / a) / math.pi) < 1e-8,
        f"{val:.8f} vs {math.atan(1/a)/math.pi:.8f}")

# Thm 6.1 mixture: -log sum pi_j p_j <= -log p_* + log(1/pi_*)
P = rng.random((1000, 5)); w = rng.dirichlet(np.ones(5), 1000)
q = (w * P).sum(1)
rep("Thm6.1 Bayes mixture inequality", np.all(-np.log(q) <= -np.log(P[:, 2]) + np.log(1 / w[:, 2]) + 1e-12),
    "1000 random cases")

# Prop 5.6: Gaussian norm concentration ||xi|| <= sigma(sqrt(L)+sqrt(2 log 1/delta))/sqrt(N)
for L, N, dl in ((5, 50, 0.05), (20, 200, 0.01)):
    xi = rng.normal(0, 1, (200000, L)) / math.sqrt(N)
    bound = (math.sqrt(L) + math.sqrt(2 * math.log(1 / dl))) / math.sqrt(N)
    rate = (np.linalg.norm(xi, axis=1) > bound).mean()
    rep(f"Prop5.6 concentration L={L} delta={dl}", rate <= dl, f"exceedance {rate:.4f} <= {dl}")

# Thm 5.7: confluent Vandermonde determinant of the moment-map Jacobian
for K in (2, 3):
    ss = sp.symbols(f"s1:{K+1}"); ww = sp.symbols(f"w1:{K+1}", positive=True)
    mu = [sum(ww[i] * ss[i] ** pp for i in range(K)) for pp in range(2 * K)]
    J = sp.Matrix(mu).jacobian(list(ss) + list(ww))
    det = sp.factor(J.det())
    target = sp.prod(ww) * sp.prod([(ss[i] - ss[j]) ** 4 for i in range(K) for j in range(i + 1, K)])
    rep(f"Thm5.7 Jacobian det K={K}", sp.simplify(det - target) == 0 or sp.simplify(det + target) == 0, f"det = {det}")

# Thm 5.7: kernel recovered from impulse response (h0 = kappa)
a, kap = 0.3, 0.7
k = rng.normal(0, .2, 6)
h = [kap]
for t in range(6):
    h.append(a * h[t] + kap * sum(k[mm] * h[t - mm] for mm in range(t + 1)))
krec = []
for t in range(6):
    krec.append((h[t + 1] - a * h[t] - kap * sum(krec[mm] * h[t - mm] for mm in range(t))) / kap ** 2)
rep("Thm5.7 kernel from impulse response", np.allclose(k, krec), "k_t = (h_{t+1}-a h_t-kappa sum_{m<t} k_m h_{t-m})/kappa^2")

# Thm 5.7 rank examples
th, thc = sp.symbols("theta theta_c")
for K, L in ((2, 4), (3, 7)):
    for name, g in (("exponential", lambda mm: (1 - th) * th ** mm), ("power law", lambda mm: (mm + 1) ** (-th))):
        A = sp.Matrix([[sp.diff(g(mm), th, pp).subs(th, sp.Rational(1, 2)) / sp.factorial(pp) for pp in range(2 * K)]
                       for mm in range(L)])
        r = A.rank()
        rep(f"Thm5.7 rank {name} K={K} L={L}", r == 2 * K, f"rank {r} at theta_c = 1/2")

# Thm 6.2: spectral bounds and tail bound for a nonnegative AR with sum S
phi = np.array([0.3, 0.15, 0.08, 0.04, 0.02]); S = phi.sum()
w_ = np.linspace(0, np.pi, 2001)
f = 1 / np.abs(1 - sum(phi[j] * np.exp(1j * (j + 1) * w_) for j in range(len(phi)))) ** 2 / (2 * np.pi)
rep("Thm6.2 spectral density bounds", np.all(f <= 1 / (2 * np.pi * (1 - S) ** 2) + 1e-12)
    and np.all(f >= 1 / (2 * np.pi * (1 + S) ** 2) - 1e-12), f"S = {S:.2f}")
# E x^2 <= sigma^2/(1-S)^2 under zero initialization (causal inverse filter psi)
psi = [1.0]
for t in range(1, 400):
    psi.append(sum(phi[j] * psi[t - 1 - j] for j in range(len(phi)) if t - 1 - j >= 0))
psi = np.array(psi)
rep("Thm6.2/6.3 variance bound", (psi ** 2).sum() <= 1 / (1 - S) ** 2 and psi.min() >= 0,
    f"sum psi^2 = {(psi**2).sum():.3f} <= {1/(1-S)**2:.3f}; sum psi = {psi.sum():.3f} <= {1/(1-S):.3f}")

# Thm 6.3: Gaussian-prior marginal (log q_L formula) against direct integration, L = 1
sig = 0.8
X = rng.normal(0, 1, 6); Z = rng.normal(0, 1, (6, 1))
num = integrate.quad(lambda b: np.prod(stats.norm.pdf(X, Z[:, 0] * b, sig)) * stats.norm.pdf(b), -20, 20)[0]
H = np.eye(1) + Z.T @ Z / sig ** 2
bhat = np.linalg.solve(Z.T @ Z + sig ** 2 * np.eye(1), Z.T @ X)
mn = ((X - Z @ bhat) ** 2).sum() + sig ** 2 * (bhat ** 2).sum()
formula = -6 / 2 * math.log(2 * math.pi * sig ** 2) - 0.5 * math.log(np.linalg.det(H)) - mn / (2 * sig ** 2)
rep("Thm6.3 log q_L formula", abs(math.log(num) - formula) < 1e-8, f"{math.log(num):.10f} vs {formula:.10f}")
# pathwise log(pL/qL) <= ||phi||^2/2 + logdet/2, and E logdet <= L log(1 + E tr/(L sigma^2))
ok = True
for _ in range(500):
    Z = rng.normal(0, 1, (30, 3)); phi3 = rng.normal(0, .3, 3); X = Z @ phi3 + rng.normal(0, sig, 30)
    H = np.eye(3) + Z.T @ Z / sig ** 2
    bh = np.linalg.solve(Z.T @ Z + sig ** 2 * np.eye(3), Z.T @ X)
    mn = ((X - Z @ bh) ** 2).sum() + sig ** 2 * (bh ** 2).sum()
    lq = -15 * math.log(2 * math.pi * sig ** 2) - .5 * math.log(np.linalg.det(H)) - mn / (2 * sig ** 2)
    lp = -15 * math.log(2 * math.pi * sig ** 2) - ((X - Z @ phi3) ** 2).sum() / (2 * sig ** 2)
    ok &= lp - lq <= .5 * (phi3 ** 2).sum() + .5 * math.log(np.linalg.det(H)) + 1e-9
    ok &= math.log(np.linalg.det(H)) <= 3 * math.log(1 + np.trace(Z.T @ Z) / (3 * sig ** 2)) + 1e-9
rep("Thm6.3 pathwise and AM-GM steps", bool(ok), "500 random designs")

# Prop 6.5(c): Kalman fixed point and gain rho^2 P
rho, ve, vf = 0.8, 1.0, 0.5
Pk = 1.0
for _ in range(500):
    Pk = vf * (rho ** 2 * Pk + ve) / (rho ** 2 * Pk + ve + vf)
rep("Prop6.5(c) filtering fixed point", Pk > 0 and abs(Pk - vf * (rho ** 2 * Pk + ve) / (rho ** 2 * Pk + ve + vf)) < 1e-12,
    f"P = {Pk:.4f}; gain rho^2 P = {rho**2*Pk:.4f}")

print(f"\n{sum(o[1] for o in out)} of {len(out)} checks pass")
