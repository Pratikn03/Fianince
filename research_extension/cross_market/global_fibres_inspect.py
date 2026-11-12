"""Inspect every 'other configuration' found by the global searches (proof check, 12 November 2026).

Part A reads global_fibres_extended_solutions_upto_4_2.json (the extended search, rerun with saving; it reproduces
global_fibres_extended_results.json). Part B (flag --original) reruns global_fibres.py's loop with its seed 0 up to
(K, D) = (3, 3), the case where the original search reported other solutions, and prints them.
For each solution it prints the smallest node gap of the original configuration, the distance to the nearest
relabelling and the gap at the next moment order. Finding: every solution lies within 0.05 of an original
configuration that has two nearly coincident nodes (gap below 0.04), with residuals just under the 1e-10 threshold;
they are directions along which the moment map is ill-conditioned, not distinct configurations of a class with
separated nodes.
Run: python3 global_fibres_inspect.py [--original] > global_fibres_inspect_printed_output.txt"""
import sys, math, json, itertools
import numpy as np


def describe(gf, K, D, x0, x, L):
    x0, x = np.asarray(x0), np.asarray(x)
    perms = [np.r_[x0[:K][list(p)], x0[K:].reshape(D, K)[:, list(p)].ravel()] for p in itertools.permutations(range(K))]
    return (f"K={K} D={D} order={L}: original node gap {np.min(np.diff(np.sort(x0[:K]))):.4f}, "
            f"distance to nearest relabelling {min(float(np.max(np.abs(x - p))) for p in perms):.4f}, "
            f"residual {float(np.max(np.abs(gf.moments(x, K, D, L) - gf.moments(x0, K, D, L)))):.1e}, "
            f"next-order gap {float(np.max(np.abs(gf.moments(x, K, D, L + 1) - gf.moments(x0, K, D, L + 1)))):.1e}")


if __name__ == "__main__":
    original = "--original" in sys.argv
    sys.argv = sys.argv[:1]
    import global_fibres as gf
    print("Part A: extended search")
    for key, cases in json.load(open("global_fibres_extended_solutions_upto_4_2.json")).items():
        K, D = map(int, key.split(",")); lstar = K - 1 + math.ceil(K / D)
        for c in cases:
            for x in c["at_lstar"]:
                print(describe(gf, K, D, c["x0"], x, lstar))
            for x in c["at_lstar_plus_1"]:
                print(describe(gf, K, D, c["x0"], x, lstar + 1))
    if original:
        print("Part B: original search, seed 0, up to (3, 3)")
        rng = gf.rng
        for K, D in ((2, 2), (3, 2), (3, 3)):
            lstar = K - 1 + math.ceil(K / D)
            for trial in range(3):
                s = np.sort(rng.uniform(-0.9, 0.9, K)); W = rng.uniform(0.4, 1.6, (D, K))
                x0 = np.r_[s, W.ravel()]
                for L in range(lstar, 2 * K):
                    sols = gf.other_solutions(x0, K, D, L)
                    for x in sols:
                        print(describe(gf, K, D, x0, x, L), flush=True)
                    if len(sols) == 0:
                        break
