"""Run the unchanged extended-search design with independent starts on CPU workers.

Random draws, solver tolerances, ordering, and duplicate filtering match the
serial script. Output goes to a separate directory. This is a numerical search,
not a proof or a live-data experiment.
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import itertools
import os
import runpy
import sys

# Avoid nested BLAS oversubscription on the Mac or a shared reproduction host.
for _name in ['OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS']:
    os.environ[_name] = '1'
import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'source/research_extension/cross_market'
sys.path.insert(0, str(SOURCE))
import global_fibres as gf


def solve_start(args):
    z0, target, K, D, L, lo, hi = args
    r = least_squares(lambda z: gf.moments(z, K, D, L) - target, z0,
                      bounds=(lo, hi), xtol=1e-14, ftol=1e-14, gtol=1e-14)
    return r.x, float(np.max(np.abs(r.fun)))


def main():
    destination = HERE / 'parallel_global_search'
    destination.mkdir(exist_ok=True)
    os.chdir(destination)
    with ProcessPoolExecutor(max_workers=min(8, os.cpu_count() or 1)) as pool:
        def parallel_solutions(x0, K, D, L, starts=400):
            target = gf.moments(x0, K, D, L)
            lo = np.r_[-np.ones(K), .05*np.ones(K*D)]
            hi = np.r_[np.ones(K), 3*np.ones(K*D)]
            perms = [np.r_[x0[:K][list(p)], x0[K:].reshape(D, K)[:, list(p)].ravel()]
                     for p in itertools.permutations(range(K))]
            jobs = [(gf.rng.uniform(lo, hi), target, K, D, L, lo, hi) for _ in range(starts)]
            found = []
            for x, residual in pool.map(solve_start, jobs, chunksize=4):
                if residual < 1e-10 and min(np.max(np.abs(x-p)) for p in perms) > 1e-3:
                    if all(np.max(np.abs(x-f)) > 1e-4 for f in found):
                        found.append(x)
            return found
        gf.other_solutions = parallel_solutions
        runpy.run_path(str(SOURCE / 'global_fibres_extended.py'), run_name='p1f_parallel_design')


if __name__ == '__main__':
    main()
