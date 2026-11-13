"""Monte Carlo check of the cheap/expensive dichotomy (supplement Section app:questions).

Two groups at memories 0.5 - d and 0.5 + d with weights 0.3 and 0.2. The observer sees the first L kernel taps,
averaged over N experiments, with noise sd sigma / sqrt(N). Two questions:
  cheap:     discounted feedback F = int (1 - beta r)^-1 dM, beta = 0.9 (square-summable coefficients), estimated by
             the truncated sum sum_{t<L} beta^t kbar_t (Theorem thm:questions(i));
  expensive: the two weights, estimated by Prony's method from kbar_0..kbar_3 (Theorem prop:esprit).
Prediction: the error of the first does not depend on d (slope 0 in log error against log d); the error of the second
grows like d^-3 (slope -3).
Run: python3 mc_questions.py -> mc_questions_results.json"""
import json
import numpy as np

rng = np.random.default_rng(20261112)
SIGMA_BAR = 1e-5          # sd of each averaged tap, sigma / sqrt(N)
L, BETA, REPS = 120, 0.9, 2000
W = np.array([0.3, 0.2])


def prony2(k):
    H = np.array([[k[0], k[1]], [k[1], k[2]]]); c = np.linalg.solve(H, -np.array([k[2], k[3]]))
    nodes = np.sort(np.roots([1.0, c[1], c[0]]).real)
    V = np.vander(nodes, 2, increasing=True).T
    return np.linalg.solve(V, k[:2]), nodes


out = {"sigma_bar": SIGMA_BAR, "L": L, "beta": BETA, "reps": REPS, "rows": []}
for d in (0.2, 0.1, 0.05):
    r = np.array([0.5 - d, 0.5 + d])
    k = (W[None, :] * r[None, :] ** np.arange(L)[:, None]).sum(1)
    F = float((W / (1 - BETA * r)).sum())
    eF, eW = [], []
    for _ in range(REPS):
        kb = k + SIGMA_BAR * rng.standard_normal(L)
        eF.append(abs((BETA ** np.arange(L) * kb).sum() - F))
        w_hat, _ = prony2(kb)
        eW.append(float(np.max(np.abs(w_hat - W))))
    out["rows"].append({"d": d, "median_error_discounted_feedback": float(np.median(eF)),
                        "median_error_weights": float(np.median(eW))})
ds = np.log([x["d"] for x in out["rows"]])
out["slope_discounted_feedback"] = float(np.polyfit(ds, np.log([x["median_error_discounted_feedback"] for x in out["rows"]]), 1)[0])
out["slope_weights"] = float(np.polyfit(ds, np.log([x["median_error_weights"] for x in out["rows"]]), 1)[0])
print(json.dumps(out, indent=1))
json.dump(out, open("mc_questions_results.json", "w"), indent=1)
