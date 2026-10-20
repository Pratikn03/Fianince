"""Vectorized interval arithmetic with outward rounding.

Every operation is computed in IEEE double precision (round to nearest, error at most half an ulp) and the result is then
widened by one ulp in each direction with numpy.nextafter, so the returned interval contains the exact real result of the
operation applied to any reals in the input intervals. Inputs that are not exactly representable are enclosed with `enclose`.
This is the standard 'outward rounding by one ulp' construction (e.g. Rump, Acta Numerica 2010, Sec. 3); it is slower and
slightly wider than directed rounding but needs no change of the FPU rounding mode.
"""
import numpy as np

_INF = np.inf


def _dn(x):
    return np.nextafter(x, -_INF)


def _up(x):
    return np.nextafter(x, _INF)


class IV:
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        lo = np.asarray(lo, dtype=float)
        hi = lo if hi is None else np.asarray(hi, dtype=float)
        if np.any(lo > hi):
            raise ValueError("empty interval")
        self.lo, self.hi = lo, hi

    # -- construction -----------------------------------------------------------------------------
    @staticmethod
    def enclose(x):
        """Smallest float interval guaranteed to contain the real number(s) that the decimal input denotes."""
        x = np.asarray(x, dtype=float)
        return IV(_dn(x), _up(x))

    # -- arithmetic -------------------------------------------------------------------------------
    def __add__(self, o):
        o = _as(o)
        return IV(_dn(self.lo + o.lo), _up(self.hi + o.hi))
    __radd__ = __add__

    def __sub__(self, o):
        o = _as(o)
        return IV(_dn(self.lo - o.hi), _up(self.hi - o.lo))

    def __rsub__(self, o):
        return _as(o) - self

    def __neg__(self):
        return IV(-self.hi, -self.lo)

    def __mul__(self, o):
        o = _as(o)
        c = np.stack([self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi])
        return IV(_dn(c.min(0)), _up(c.max(0)))
    __rmul__ = __mul__

    def recip(self):
        if np.any((self.lo <= 0) & (self.hi >= 0)):
            raise ZeroDivisionError("interval contains zero")
        return IV(_dn(1.0 / self.hi), _up(1.0 / self.lo))

    def __truediv__(self, o):
        return self * _as(o).recip()

    def __rtruediv__(self, o):
        return _as(o) * self.recip()

    def sq(self):
        a = np.abs(self.lo); b = np.abs(self.hi)
        lo = np.where((self.lo <= 0) & (self.hi >= 0), 0.0, np.minimum(a, b) ** 2)
        return IV(_dn(lo) * (lo > 0), _up(np.maximum(a, b) ** 2))

    def abs(self):
        lo = np.where((self.lo <= 0) & (self.hi >= 0), 0.0, np.minimum(np.abs(self.lo), np.abs(self.hi)))
        return IV(lo, np.maximum(np.abs(self.lo), np.abs(self.hi)))

    def mag(self):
        """Upper bound of |x| over the interval."""
        return np.maximum(np.abs(self.lo), np.abs(self.hi))

    def width(self):
        return self.hi - self.lo

    def __repr__(self):
        return f"IV({self.lo}, {self.hi})"


def _as(x):
    return x if isinstance(x, IV) else IV.enclose(x)


def matvec(J, v):
    """Interval 3x3 (or n x n, list of lists of IV) times interval vector (list of IV)."""
    n = len(v)
    return [sum((J[i][k] * v[k] for k in range(1, n)), J[i][0] * v[0]) for i in range(n)]


def matmul(A, B):
    n = len(A)
    return [[sum((A[i][k] * B[k][j] for k in range(1, n)), A[i][0] * B[0][j]) for j in range(n)] for i in range(n)]


def norm_inf_upper(P):
    """Upper bound of the infinity norm of every real matrix in the interval matrix P (rows: sum of magnitudes)."""
    n = len(P)
    rows = [_up_sum([P[i][j].mag() for j in range(n)]) for i in range(n)]
    return np.maximum.reduce(rows)


def _up_sum(xs):
    s = xs[0]
    for x in xs[1:]:
        s = _up(s + x)
    return s
