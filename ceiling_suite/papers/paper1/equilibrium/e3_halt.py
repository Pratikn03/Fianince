"""E3: targeted intervention in the market of e1_demo.py.

Gauss pair (weights 1/2,1/2 at c -/+ d/sqrt(3)) vs Radau pair (1/4, 3/4 at c-d, c+d/3), total weight W.
Pre-halt: both configurations, same draws. Post-halt: remove the largest cohort (for Gauss, the weights tie and we remove the cohort at c+d/sqrt3;
for Radau, the 3/4 cohort at c+d/3).
Report the maximum price gap over dates and draws, pre- and post-halt, for several spacings d, and the kernel l1 gap.
"""
import json
import numpy as np
from e1_demo import run

def kernel_l1(w1, n1, w2, n2, c, d, W, M=400):
    m = np.arange(M)
    k1 = sum(W * a * (c + d * s) ** m for a, s in zip(w1, n1))
    k2 = sum(W * a * (c + d * s) ** m for a, s in zip(w2, n2))
    return float(np.abs(k1 - k2).sum())

def main():
    c, T, W = 0.6, 40, 0.5
    G = ([0.5, 0.5], [-1 / np.sqrt(3), 1 / np.sqrt(3)]); R = ([0.25, 0.75], [-1.0, 1 / 3])
    Gh = ([0.5], [-1 / np.sqrt(3)]); Rh = ([0.25], [-1.0])
    rows = []
    for d in [0.05, 0.1, 0.2]:
        rng = np.random.default_rng(7)
        pre, post = 0.0, 0.0
        for _ in range(200):
            v = rng.standard_normal(); z = 0.5 * rng.standard_normal(T)
            pre = max(pre, float(np.abs(run(*G, c, d, T, v, z)[0] - run(*R, c, d, T, v, z)[0]).max()))
            post = max(post, float(np.abs(run(*Gh, c, d, T, v, z)[0] - run(*Rh, c, d, T, v, z)[0]).max()))
        rows.append({"d": d, "pre_halt_max_gap": pre, "post_halt_max_gap": post,
                     "pre_kernel_l1": kernel_l1(*G, *R, c, d, W), "post_kernel_l1": kernel_l1(*Gh, *Rh, c, d, W),
                     "pre_gap_over_d3": pre / d ** 3})
        print(json.dumps(rows[-1]))
    json.dump(rows, open("e3_halt_results.json", "w"), indent=1)

if __name__ == "__main__":
    main()
