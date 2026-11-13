"""P1X design check by simulation (no real data are read).

Question for the design: can weekly class positions in about 30 futures markets test the premise of the pooling
theorem (core thm:pool), that a trader class's memory rates are the same in every market it trades while its weights
differ across markets?

Simulated data mimic CFTC managed-money net positions scaled by open interest:
  z_{j,t}   weekly volatility-normalized return of market j: Student-t(5), unit variance, common factor loading 0.3
  S_t(r)    = r S_{t-1}(r) + z_{t-1}           (exponential trend signal with memory rate r)
  P_{j,t}   = c_j + sum_i W_{ij} S_t(r_{ij}) + e_{j,t},  e AR(1) with coefficient 0.9 (positions unrelated to trends)
Weights W_{ij} = exp(N(0, 0.5^2)); the trend part explains a share R2 of the variance of weekly flows (changes in P).
Models are fitted to weekly flows on changes in the signals, by least squares over a fixed grid of 24 half-lives from
1 to 78 weeks. Development and holdout samples of 480 weeks each, after a 52-week burn-in.

  R_K  (premise)    K memory rates common to all markets, market-specific weights and intercepts
  U_K  (no premise) K memory rates for each market
  R1   (rank one)   two common memory rates, a common mixing share, one scale per market

Decision rules (the tests run on the holdout; the development sample only chooses K):
  K       design 1: chosen on the development sample by BIC of R_K, K in {1, 2, 3} (argument "bic");
          design 2: fixed in advance (argument "3"), so that R_K contains populations of up to K classes.
  H1      premise. Statistic F1 = SSR(R_K) / SSR(U_K) - 1 on the holdout. Its null law is obtained by a residual
          bootstrap from the fitted R_K: fitted flows plus residuals resampled in blocks of 26 weeks, the same weeks
          for every market, 199 draws, refitting both models each time. The premise is rejected if p < 0.05.
  H2      weights of rank above one. F2 = SSR(R1) / SSR(R_2) - 1, null law by the same bootstrap from the fitted R1.
          Rank one is rejected if p < 0.05.
Scenarios: premise true with two classes (half-lives 4 and 20 weeks) or three (2, 8 and 30 weeks); premise violated,
each market's half-lives multiplied by exp(tau N(0, 1)) with tau = 0.5 or 1; weights of rank one.
Design criteria fixed before running: H1 rejects in at most 7.5% of replications under the premise (nominal 5%, Monte
Carlo error about 2%) and in at least 80% under tau = 1; H2 rejects in at least 80% when weights vary across markets
and in at most 7.5% under rank one. Power at tau = 0.5 is reported, not required.
Run: python3 p1x_design_sim.py [reps] [bic|K] [R2 list] -> p1x_design_sim_results_K<mode>_R2_<list>.json
"""
import json, sys, math, itertools
import numpy as np
from scipy.signal import lfilter

REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 100
KMODE = sys.argv[2] if len(sys.argv) > 2 else "bic"
R2S = [float(v) for v in sys.argv[3].split(",")] if len(sys.argv) > 3 else [0.1, 0.25]   # "bic" (design 1) or a fixed K, e.g. "3" (design 2)
D, TD, TH, BURN = 30, 480, 480, 52
HL_GRID = np.exp(np.linspace(np.log(1.0), np.log(78.0), 24))
R_GRID = 0.5 ** (1.0 / HL_GRID)
H = len(HL_GRID)
OMEGAS = np.linspace(0.0, 1.0, 21)
BLOCK, NBOOT = 26, 199
rng = np.random.default_rng(20261112)
COMBOS = {K: np.array(list(itertools.combinations(range(H), K))) for K in (1, 2, 3)}


def signal(z, r):
    return lfilter([0.0, 1.0], [1.0, -r], z)


def simulate(hl_true, tau, r2, rank_one=False):
    K = len(hl_true); T = BURN + TD + TH
    f = rng.standard_t(5, T) / math.sqrt(5 / 3)
    z = 0.3 * f[None, :] + math.sqrt(0.91) * rng.standard_t(5, (D, T)) / math.sqrt(5 / 3)
    W = (np.exp(rng.normal(0, 0.5, (D, 1))) * np.full((1, K), 1.0 / K)) if rank_one else np.exp(rng.normal(0, 0.5, (D, K)))
    hl = np.asarray(hl_true)[None, :] * np.exp(tau * rng.normal(0, 1, (D, K)))
    P = np.zeros((D, T))
    for j in range(D):
        trend = sum(W[j, i] * signal(z[j], 0.5 ** (1 / hl[j, i])) for i in range(K))
        e = lfilter([1.0], [1.0, -0.9], rng.normal(0, 1, T))
        vt, ve = np.diff(trend[BURN:]).var(), np.diff(e[BURN:]).var()
        P[j] = trend + e * math.sqrt(vt * (1 - r2) / (r2 * ve))
    return z, P


def design(z, P, sl):
    """Flows and signal changes on the sample slice sl."""
    S = np.stack([np.stack([signal(z[j], r) for r in R_GRID]) for j in range(D)])
    dS = np.diff(S, axis=2)[:, :, sl.start - 1:sl.stop - 1]
    y = np.diff(P, axis=1)[:, sl.start - 1:sl.stop - 1]
    X = np.concatenate([np.ones((D, 1, y.shape[1])), dS], axis=1)
    return X, y


class Fit:
    """Least squares of y on [1, dS_c] for every combination c of K grid rates, for every market."""
    def __init__(self, X, K):
        self.X, self.K = X, K
        self.idx = np.c_[np.zeros(len(COMBOS[K]), int), COMBOS[K] + 1]
        G = np.einsum("jat,jbt->jab", X, X)
        self.inv = np.linalg.inv(G[:, self.idx[:, :, None], self.idx[:, None, :]] + 1e-10 * np.eye(K + 1))

    def ssr(self, y):
        g = np.einsum("jat,jt->ja", self.X, y)[:, self.idx]
        beta = np.einsum("jcab,jcb->jca", self.inv, g)
        return np.einsum("jt,jt->j", y, y)[:, None] - np.einsum("jca,jca->jc", g, beta), beta

    def stats(self, y):
        s, beta = self.ssr(y)
        cR = int(np.argmin(s.sum(0)))
        return s[:, cR].sum(), s.min(1).sum(), cR, beta[:, cR]

    def fitted(self, cR, beta):
        return np.einsum("ja,jat->jt", beta, self.X[:, self.idx[cR]])


def rank_one(X, y):
    """Common pair (a, b) and share omega; regressor omega dS_a + (1 - omega) dS_b; scale and intercept per market."""
    n = y.shape[1]
    Xc = X[:, 1:] - X[:, 1:].mean(2, keepdims=True); yc = y - y.mean(1, keepdims=True)
    V = np.einsum("jat,jbt->jab", Xc, Xc); C = np.einsum("jat,jt->ja", Xc, yc); vy = (yc ** 2).sum(1)
    a, b = COMBOS[2][:, 0], COMBOS[2][:, 1]
    om = OMEGAS[None, :, None]
    var = om ** 2 * V[:, a, a].T[:, None, :] + 2 * om * (1 - om) * V[:, a, b].T[:, None, :] + (1 - om) ** 2 * V[:, b, b].T[:, None, :]
    cov = om * C[:, a].T[:, None, :] + (1 - om) * C[:, b].T[:, None, :]
    ssr = vy[None, None, :] - cov ** 2 / var                         # pairs x omegas x markets
    tot = ssr.sum(2); p, o = np.unravel_index(np.argmin(tot), tot.shape)
    x = OMEGAS[o] * X[:, 1 + a[p]] + (1 - OMEGAS[o]) * X[:, 1 + b[p]]
    slope = cov[p, o] / var[p, o]
    fitted = y.mean(1, keepdims=True) + slope[:, None] * (x - x.mean(1, keepdims=True))
    return tot[p, o], fitted


def block_index(n):
    nb = int(math.ceil(n / BLOCK)); st = rng.integers(0, n - BLOCK + 1, nb)
    return (st[:, None] + np.arange(BLOCK)[None, :]).ravel()[:n]


def choose_K(Xd, yd):
    n = yd.size; best = None
    for K in (1, 2, 3):
        sR, _, _, _ = Fit(Xd, K).stats(yd)
        bic = n * math.log(sR / n) + (K + D * (K + 1)) * math.log(n)
        if best is None or bic < best[0]:
            best = (bic, K)
    return best[1]


def tests(z, P):
    T = z.shape[1]
    Xd, yd = design(z, P, slice(BURN, BURN + TD))
    Xh, yh = design(z, P, slice(BURN + TD, T))
    K = choose_K(Xd, yd) if KMODE == "bic" else int(KMODE)
    fK = Fit(Xh, K)
    sR, sU, cR, beta = fK.stats(yh)
    F1 = sR / sU - 1
    fitR = fK.fitted(cR, beta); res = yh - fitR
    F1b = []
    for _ in range(NBOOT):
        ys = fitR + res[:, block_index(yh.shape[1])]
        a, b, _, _ = fK.stats(ys); F1b.append(a / b - 1)
    p1 = (1 + sum(f >= F1 for f in F1b)) / (NBOOT + 1)
    f2 = Fit(Xh, 2)
    s2, _, _, _ = f2.stats(yh)
    s1, fit1 = rank_one(Xh, yh); res1 = yh - fit1
    F2 = s1 / s2 - 1; F2b = []
    for _ in range(NBOOT):
        ys = fit1 + res1[:, block_index(yh.shape[1])]
        a, _, _, _ = f2.stats(ys); c, _ = rank_one(Xh, ys); F2b.append(c / a - 1)
    p2 = (1 + sum(f >= F2 for f in F2b)) / (NBOOT + 1)
    hlR = HL_GRID[COMBOS[K][cR]]
    return K, p1, p2, hlR


SCEN = [("two classes, premise", (4, 20), 0.0, False), ("three classes, premise", (2, 8, 30), 0.0, False),
        ("two classes, tau=0.5", (4, 20), 0.5, False), ("two classes, tau=1", (4, 20), 1.0, False),
        ("two classes, rank one", (4, 20), 0.0, True)]
if __name__ == "__main__":
    out = {"design": {"markets": D, "dev_weeks": TD, "holdout_weeks": TH, "block": BLOCK, "bootstrap_draws": NBOOT,
                      "reps": REPS, "grid_half_lives": HL_GRID.round(2).tolist()}, "scenarios": {}}
    for r2 in R2S:
        for name, hl, tau, r1 in SCEN:
            Ks, rej1, rej2, hls = [], 0, 0, []
            for _ in range(REPS):
                z, P = simulate(hl, tau, r2, r1)
                K, p1, p2, hlR = tests(z, P)
                Ks.append(K); rej1 += p1 < 0.05; rej2 += p2 < 0.05; hls.append(hlR.tolist())
            key = f"R2={r2}: {name}"
            out["scenarios"][key] = {"H1_reject_rate": rej1 / REPS, "H2_reject_rate": rej2 / REPS,
                                     "K_chosen": {k: Ks.count(k) for k in (1, 2, 3)},
                                     "example_half_lives_R": hls[:5]}
            print(key, {k: v for k, v in out["scenarios"][key].items() if k != "example_half_lives_R"}, flush=True)
    out["design"]["K_mode"] = KMODE
    json.dump(out, open(f"p1x_design_sim_results_K{KMODE}_R2_{'_'.join(map(str, R2S))}.json", "w"), indent=1)
