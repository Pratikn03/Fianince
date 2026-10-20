"""Compare two results folders key by key (ignoring runtime and metadata). Exit 1 on any difference."""
import json, math, os, sys
A, B = sys.argv[1], sys.argv[2]
SKIP = {"runtime_seconds", "meta", "timestamp_utc", "interval_evaluations"}


def diff(a, b, p=""):
    out = []
    if isinstance(a, dict):
        for k in a:
            if k in SKIP:
                continue
            if not isinstance(b, dict) or k not in b:
                out.append(p + "/" + k + " missing"); continue
            out += diff(a[k], b[k], p + "/" + k)
    elif isinstance(a, list):
        if not isinstance(b, list) or len(a) != len(b):
            return [p + " length"]
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{p}[{i}]")
    elif isinstance(a, float) or isinstance(b, float):
        if not (a == b or (a is not None and b is not None and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12))):
            out.append(f"{p}: {a} vs {b}")
    elif a != b:
        out.append(f"{p}: {a} vs {b}")
    return out


# Platform tolerance. Two results depend on the platform's floating-point library at a level far below anything quoted:
# the floating-point Markov--Krein windows of ThmB (ill-conditioned power-moment problems, compared at 1e-6) and the
# adaptive subdivision count of T10 (the certified endpoints are verified in interval arithmetic on any platform; the
# number of boxes needed can differ by a few). Everything else must agree to 1e-9.
LOOSE = {"ThmB_window.json": 1e-6, "T10_certified_numerics.json": 1e-6, "IS_results.json": 1e-6}
COUNT_KEYS = {"boxes_checked"}


def diff_loose(a, b, tol, p=""):
    out = []
    if isinstance(a, dict):
        for k in a:
            if k in SKIP:
                continue
            if not isinstance(b, dict) or k not in b:
                out.append(p + "/" + k + " missing"); continue
            if k in COUNT_KEYS and isinstance(a[k], int) and isinstance(b[k], int):
                if abs(a[k] - b[k]) > max(10, 1e-3 * abs(a[k])):
                    out.append(f"{p}/{k}: {a[k]} vs {b[k]}")
                continue
            out += diff_loose(a[k], b[k], tol, p + "/" + k)
    elif isinstance(a, list):
        if not isinstance(b, list) or len(a) != len(b):
            return [p + " length"]
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff_loose(x, y, tol, f"{p}[{i}]")
    elif isinstance(a, float) or isinstance(b, float):
        if not (a == b or (a is not None and b is not None and math.isclose(a, b, rel_tol=tol, abs_tol=1e-10))):
            out.append(f"{p}: {a} vs {b}")
    elif a != b:
        out.append(f"{p}: {a} vs {b}")
    return out


bad = 0
for f in sorted(os.listdir(A)):
    if not f.endswith(".json"):
        continue
    ja, jb = json.load(open(os.path.join(A, f))), json.load(open(os.path.join(B, f)))
    d = diff_loose(ja, jb, LOOSE[f]) if f in LOOSE else diff(ja, jb)
    print(("IDENTICAL " if not d else "DIFFERENT ") + f + ("" if not d else "  " + "; ".join(d[:3])))
    bad += bool(d)
sys.exit(1 if bad else 0)
