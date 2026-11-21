"""Float replication of Companion Proposition insidergame's example (a=0.3, kappa=0.5, r=0.6, theta=1, T=10)."""
import numpy as np
a, kap, r, th, T, Sig, sig2, wbar = 0.3, 0.5, 0.6, 1.0, 10, 1.0, 1.0, 0.515


def H_of(w):
    h = np.zeros(T); h[0] = kap
    for t in range(1, T):
        h[t] = a * h[t-1] + kap * w * sum(r ** (j-1) * h[t-j] for j in range(1, t+1))
    return h


def toep_lower(h):
    return np.array([[h[i-j] if i >= j else 0 for j in range(T)] for i in range(T)])


R = np.array([[r ** (i-j-1) if i > j else 0 for j in range(T)] for i in range(T)])  # m_t = sum_{j>=1} r^{j-1} x_{t-j}


def parts(w):
    h = H_of(w); H = toep_lower(h); G = H / kap
    M = np.array([[th * kap if i == j else h[abs(i-j)] / 2 for j in range(T)] for i in range(T)])
    return H, G, M


def zeta_star(w):
    return 0.5 * np.linalg.solve(parts(w)[2], np.ones(T))


def UG(w, z):
    H, G, M = parts(w)
    one = np.ones(T)
    I = one @ R @ H @ z - z @ H.T @ R.T @ H @ z
    N = np.trace(R @ G @ G.T)
    return w * (Sig * I - sig2 * N), I, N

z0 = zeta_star(0.0)
_, I0, N0 = UG(0.0, z0)
print("I0", round(I0, 3), "N0", round(N0, 3))
ws = np.linspace(-wbar, wbar, 4001)
w = 0.0
for _ in range(200):
    z = zeta_star(w)
    w_new = ws[np.argmax([UG(x, z)[0] for x in ws])]
    if abs(w_new - w) < 1e-12:
        break
    w = w_new
print("equilibrium w", w, "payoff", UG(w, zeta_star(w))[0])
