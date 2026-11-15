"""Numerical checks for Paper 1, core thm:running and prop:nongauss (supplement section app:runningnews).

(a) thm:running(ii): in one running market (unknown initial state, Gaussian or Laplace news, observation noise),
    the cross-correlation estimator of the taps h_0..h_4 from +-A probes has mean squared error at most
    (2||h||^2 + s^2/A^2)/T, where s^2 = sup_t E n_t^2.
(b) prop:nongauss: for the K = 2 Gauss and Gauss-Radau pair, the divergence between the price records from rest
    under Laplace or Student-t(5) news is at most sigma^2 I* times the Gaussian one, and close to sigma^2 I(f) times
    it (the pair is close, so the local factor binds).
Run: python3 running_check.py -> running_check_results.json"""
import json
import numpy as np
from scipy import integrate, special, stats

A_, KAPPA, W, RC, DETA = 0.5, 0.5, 0.03, 0.5, 0.3
NODES = {"gauss": (np.array([-1, 1]) / np.sqrt(3), np.array([0.5, 0.5])),
         "radau": (np.array([-1.0, 1 / 3]), np.array([0.25, 0.75]))}


def response(rule, T):
    s, p = NODES[rule]
    r = RC + DETA * s; w = W * p
    k = np.array([np.sum(w * r ** m) for m in range(T)])
    h = np.zeros(T); h[0] = KAPPA
    for t in range(1, T):
        h[t] = A_ * h[t - 1] + KAPPA * np.dot(k[:t], h[t - 1::-1][:t])
    return h          # response to a unit trade; response to a unit news shock is h / KAPPA


def part_a(reps=400, T=4000, A=1.0, sw=0.3, sn=0.3, law="gauss", seed=1):
    rng = np.random.default_rng(seed)
    L = 400
    h = response("gauss", L)
    g = h / KAPPA
    s2 = sw ** 2 * np.sum(g ** 2) + sn ** 2            # stationary variance of the noise part (sup over t)
    J = 5
    err = np.zeros((reps, J))
    for rep in range(reps):
        burn = int(rng.integers(200, 2000))           # unknown start, so the state at the first record is unknown
        n_tot = burn + T + J
        if law == "gauss":
            e = rng.normal(0, sw, n_tot)
        else:
            e = rng.laplace(0, sw / np.sqrt(2), n_tot)
        eps = np.zeros(n_tot); eps[burn - J:] = rng.choice([-1.0, 1.0], n_tot - burn + J)
        x = np.convolve(KAPPA * A * eps + e, g)[:n_tot]   # the closed loop is linear: x = g * (kappa v + news)
        y = x + rng.normal(0, sn, n_tot)
        obs = slice(burn, burn + T)
        hh = np.array([np.mean(y[obs] * eps[burn - j:burn - j + T]) / A for j in range(J)])
        err[rep] = hh - h[:J]
    mse = (err ** 2).mean(0)
    bound = (2 * np.sum(h ** 2) + s2 / A ** 2) / T
    return {"law": law, "T": T, "A": A, "mse_by_tap": mse.tolist(), "bound": float(bound),
            "max_mse_over_bound": float(mse.max() / bound), "mean_error_over_sd": (err.mean(0) / err.std(0) * np.sqrt(reps)).tolist()}


def location_kl(logpdf, delta, lo=-60, hi=60):
    f = lambda z: np.exp(logpdf(z)) * (logpdf(z) - logpdf(z - delta))
    return integrate.quad(f, lo, hi, limit=400, points=[0, delta])[0]


def part_b(T=200, reps=20000, seed=2):
    rng = np.random.default_rng(seed)
    gA = response("gauss", T) / KAPPA; gB = response("radau", T) / KAPPA
    # innovations of B computed from A's prices: xi^B = (gB^{-1} * gA) * xi^A; Delta_t = xi^A_t - xi^B_t
    u = np.zeros(T); u[0] = 1.0
    for t in range(1, T):
        u[t] = gA[t] - np.dot(gB[1:t + 1], u[t - 1::-1][:t])
    d = -u.copy(); d[0] = 0.0                          # Delta_t = -sum_{j>=1} u_j xi_{t-j}
    out = {}
    laws = {"laplace": (lambda z: -np.abs(z) - np.log(2.0), 2.0),
            "student_t5": (lambda z: stats.t.logpdf(z, 5), 5 / 3)}
    for name, (lp, var) in laws.items():
        grid = np.concatenate([np.linspace(1e-3, 0.5, 30), np.linspace(0.6, 20, 30)])
        kl = np.array([location_kl(lp, dl) for dl in grid])
        Istar = float(2 * np.max(kl / grid ** 2))
        If = 1.0 if name == "laplace" else (5 + 1) / (5 + 3)
        xi = (rng.laplace(0, 1, (reps, T)) if name == "laplace" else rng.standard_t(5, (reps, T)))
        Delta = np.stack([np.convolve(xi[i], d)[:T] for i in range(min(reps, 4000))])
        dl = np.sort(np.abs(Delta).ravel())
        # KL_f = sum_t E g(Delta_t), with g interpolated on a fine grid of |Delta|
        fine = np.linspace(0, max(1e-6, dl[-1]), 400)
        gfine = np.array([location_kl(lp, v) if v > 0 else 0.0 for v in fine])
        kl_f = float(np.interp(np.abs(Delta), fine, gfine).mean(0).sum())
        kl_gauss = float((Delta ** 2).mean(0).sum() / (2 * var))
        out[name] = {"sigma2_Ifisher": var * If, "sigma2_Istar": var * Istar, "KL_f": kl_f, "KL_gauss": kl_gauss,
                     "ratio": kl_f / kl_gauss}
    return out


if __name__ == "__main__":
    res = {"a_gauss": part_a(law="gauss"), "a_laplace": part_a(law="laplace", seed=3), "b": part_b()}
    print(json.dumps(res, indent=1))
    json.dump(res, open("running_check_results.json", "w"), indent=1)
