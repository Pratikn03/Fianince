"""Item 7: window-polynomial (Markov--Krein/Chebyshev) certificate vs tail-bound certificate.
Deterministic horizon and statistical cost for a fixed economy class point."""
import numpy as np, json, mpmath as mp
mp.mp.dps = 80
def f(r): return 1 / (1 - r)
def cheb_upper(rbar, deg):
    """Chebyshev interpolant of f on [0,rbar] at deg+1 Chebyshev nodes, shifted up by its sup error -> p_+ >= f.
    Returns monomial coefficients (mp) and the sup gap sup(p_+ - f) bound (2*err)."""
    n = deg + 1
    xs = [mp.cos(mp.pi * (2 * j + 1) / (2 * n)) for j in range(n)]
    rs = [rbar * (x + 1) / 2 for x in xs]
    # Newton/Vandermonde solve in mp for monomial coefficients
    V = mp.matrix([[r ** k for k in range(n)] for r in rs]); y = mp.matrix([f(r) for r in rs])
    c = mp.lu_solve(V, y)
    grid = [rbar * mp.mpf(i) / 4000 for i in range(4001)]
    err = max(abs(sum(c[k] * r ** k for k in range(n)) - f(r)) for r in grid)
    err *= mp.mpf('1.01')
    c[0] += err
    return [c[k] for k in range(n)], 2 * err
def sens(a, kap, h, n):
    """Jacobian dk/dh for k_0..k_{n-1} from h_0..h_n via k_t=(h_{t+1}-a h_t - kap sum_{m<t} k_m h_{t-m})/kap^2."""
    eps = 1e-7; base = kvals(a, kap, h, n); J = np.zeros((n, n + 1))
    for j in range(n + 1):
        hp = h.copy(); hp[j] += eps; J[:, j] = (kvals(a, kap, hp, n) - base) / eps
    return J
def kvals(a, kap, h, n):
    k = np.zeros(n)
    for t in range(n):
        k[t] = (h[t + 1] - a * h[t] - kap * sum(k[m] * h[t - m] for m in range(t))) / kap ** 2
    return k
out = {}
a, kap = 0.5, 0.8
rbar, sbar = 0.99, None
# economy: three cohorts with rates <= rbar
rates = np.array([0.5, 0.9, 0.99]); w = np.array([0.01, 0.01, 0.002]); q = w / (1 - rates)
S_ = a + kap * q.sum(); sbar = S_ + 0.02
L = 20000; y = np.zeros(3); h = []; xp = 0
for t in range(L):
    xt = a * xp + kap * (q @ y) + (kap if t == 0 else 0); y = rates * y + (1 - rates) * xt; h.append(xt); xp = xt
h = np.array(h); Phi = q.sum(); S = kap / (1 - a - kap * Phi)
lam = 1 - (1 - rbar) * (1 - sbar)
rows = []
for eps_rel in (1e-2, 1e-3):
    epsS = eps_rel * S
    # tail certificate horizon: kappa lam^T/(1-lam) <= eps/2
    T_tail = int(np.ceil(np.log(2 * kap / ((1 - lam) * epsS)) / np.log(1 / lam)))
    N_tail = 16 * 1.645 ** 2 * T_tail / epsS ** 2      # per unit sigma^2
    # window certificate: smallest n with S(Phi+gap) - S <= eps/2, gap = k0*2err
    k0 = w.sum()
    best = None
    for deg in range(2, 80):
        c, gap = cheb_upper(mp.mpf(rbar), deg)
        Phi_up = Phi + float(gap) * k0
        if a + kap * Phi_up >= 1: continue
        dS = kap / (1 - a - kap * Phi_up) - S
        if dS <= epsS / 2:
            n = deg + 1; J = sens(a, kap, h, n)
            cvec = np.array([float(x) for x in c])
            g = (kap ** 2 / (1 - a - kap * Phi) ** 2) * (J.T @ cvec)   # dS/dh
            N_win = (2 * 1.645 * np.linalg.norm(g) / epsS) ** 2
            best = dict(n_taps=n + 1, N_per_sigma2=float(N_win), coef_l1=float(sum(abs(x) for x in c)))
            break
    rows.append(dict(eps_rel=eps_rel, T_tail=T_tail, N_tail_per_sigma2=float(N_tail), window=best))
out["rbar"] = rbar; out["sbar"] = sbar; out["S"] = S; out["rows"] = rows
print(json.dumps(out, indent=1)); json.dump(out, open("R_P2_cheb_tradeoff.json", "w"), indent=1)
