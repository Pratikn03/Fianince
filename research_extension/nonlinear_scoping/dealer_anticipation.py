"""Core version, Proposition 7.6: expected next-period feedback flow, which a forward-looking dealer prices, under two
populations with the same kernel. Next state m+ = E + s*Z at memory 0.7, clipped traders. Exact Gaussian integrals."""
import numpy as np, json
from scipy.stats import norm
def e_clip(mu, sd):   # E[clip(Y)], Y ~ N(mu, sd^2), clip to [-1,1]
    a, b = (-1 - mu) / sd, (1 - mu) / sd
    return -norm.cdf(a) + (1 - norm.cdf(b)) + mu * (norm.cdf(b) - norm.cdf(a)) + sd * (norm.pdf(a) - norm.pdf(b))
P = [(1.0, 0.1)]; Pp = [(0.25, 0.2), (1.0, 0.05)]
rows = []
for Em in [1.0, 2.0, 3.0]:
    for s in [0.5, 1.0, 2.0]:
        fP = sum(c * e_clip(l * Em, abs(l) * s) for c, l in P); fPp = sum(c * e_clip(l * Em, abs(l) * s) for c, l in Pp)
        bound = sum(c * np.sqrt(2 / np.pi) * abs(l) * s * np.exp(-(1 - abs(l * Em))**2 / (2 * (l * s)**2)) for c, l in P + Pp)
        rows.append({"E_m_next": Em, "sd_m_next": s, "linear_flow": 0.1 * Em, "E_flow_P": float(fP), "E_flow_Pp": float(fPp),
                     "gap": float(fP - fPp), "bound": float(bound)})
json.dump(rows, open("dealer_anticipation_results.json", "w"), indent=1)
for r in rows: print(r)
