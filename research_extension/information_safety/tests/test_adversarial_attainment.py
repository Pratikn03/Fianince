"""The worst-case bound is attained by an admissible path (sign path or l1-ball vertex) and the peak understates it."""
import itertools
import numpy as np


def test_attained_and_peak_understates():
    rng = np.random.default_rng(5); understated = 0; n = 0
    for _ in range(60):
        J = rng.normal(0, .5, (3, 3)); J /= max(1.0, max(abs(np.linalg.eigvals(J))) / .95)
        Hv, C = rng.normal(0, 1, 3), rng.normal(0, 1, 3)
        for T in range(1, 9):
            g = np.array([C @ np.linalg.matrix_power(J, m) @ Hv for m in range(T)])
            sgn = np.sign(g[::-1]); sgn[sgn == 0] = 1
            assert abs(abs(np.dot(g[::-1], sgn)) - np.abs(g).sum()) < 1e-9          # attaining sign path
            e = np.zeros(T); e[np.argmax(np.abs(g[::-1]))] = 1
            assert abs(abs(np.dot(g[::-1], e)) - np.abs(g).max()) < 1e-12           # attaining vertex of the l1 ball
            understated += np.abs(g).sum() > np.abs(g).max() + 1e-12; n += 1
    assert understated > 0.8 * n
