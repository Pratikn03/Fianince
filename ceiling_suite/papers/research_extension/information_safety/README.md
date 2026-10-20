# Information-safety extension (Paper 2, Sections 5-7 and 12)

Data-free code for the information-safety results of Paper 2. Deterministic seeds; Python 3 with numpy, scipy, mpmath.

| File | Content |
|---|---|
| `model_contracts.py` | Positive cohort economy: impulse response (state space and kernel recursion), moments from a window, summed response |
| `markov_krein.py` | Theorem `thm:window`: principal representations (60-digit arithmetic), sharp bounds on Phi, best-approximation formula |
| `certificate.py` | Theorem `thm:certcost`: certificate, tail bound, sufficient and lower-bound sample sizes |
| `robust_admission.py` | Theorem `thm:robustguard`: closed-form admission level |
| `run_all.py` | Tests T01-T09 and T12 -> `results/IS_results.json` (about 3 minutes) |
| `tests/` | Fast unit tests: `python3 -m pytest -q tests` |

Numerical endpoints of Theorem `thm:window` are computed in 60-digit arithmetic and checked against a linear program on a 4,001-point grid
(relative gap at most 1e-5, the grid resolution); they are exact up to floating error but are not interval-certified.
