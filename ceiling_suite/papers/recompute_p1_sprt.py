"""Paper 1: SPRT with the fee-free optimal probe split into M equal-information copies (each costs C_quad/M,
carries KL_target/M). 20,000 runs under H0. Capital = realized loss at stopping."""
import numpy as np, json
from scipy.stats import norm
Cq = json.load(open("recomputed/R_P1_capital_ledger.json"))["capbounds"]["0.05"]["C_quad"]
z = norm.ppf(0.95); KLt = 0.5 * (2 * z) ** 2; A, B = np.log(0.95 / 0.05), np.log(0.05 / 0.95)
rng = np.random.default_rng(7); out = {}
for M in [10, 20, 40]:
    kl1 = KLt / M; taus, err = [], []
    for _ in range(20000):
        llr, n = 0.0, 0
        while B < llr < A:                                  # H0 true: LLR(H1:H0) increments ~ N(-kl1, 2 kl1)
            llr += rng.normal(-kl1, np.sqrt(2 * kl1)); n += 1
        taus.append(n); err.append(llr >= A)
    loss = np.array(taus) * Cq / M
    out[M] = {"mean_loss": float(loss.mean()), "p95": float(np.quantile(loss, .95)), "p99": float(np.quantile(loss, .99)),
              "insolvent_if_funded_at_mean": float(np.mean(loss > loss.mean())), "error_H0": float(np.mean(err))}
    print(M, {k: round(v, 3) for k, v in out[M].items()})
json.dump(out, open("recomputed/R_P1_sprt.json", "w"), indent=1)
