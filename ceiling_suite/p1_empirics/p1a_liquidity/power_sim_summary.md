### Table A. The threats: how often each estimator wrongly rejects a true theory

P(contrary | gamma = 0), 30 pools x 104 weeks, instrument strength 0.3; normal critical values, 400 draws per cell.

| Response reliability | Composition tied to response (psi) | Depth feeds composition (lambda) | OLS | IV |
|---|---|---|---|---|
| 0.6 | 0.0 | 0.0 | 0% | 0% |
| 0.6 | 0.0 | 0.3 | 0% | 0% |
| 0.6 | 0.5 | 0.0 | 72% | 1% |
| 0.6 | 0.5 | 0.3 | 100% | 1% |
| 0.8 | 0.0 | 0.0 | 0% | 0% |
| 0.8 | 0.0 | 0.3 | 0% | 1% |
| 0.8 | 0.5 | 0.0 | 0% | 0% |
| 0.8 | 0.5 | 0.3 | 98% | 0% |
| 0.95 | 0.0 | 0.0 | 0% | 1% |
| 0.95 | 0.0 | 0.3 | 0% | 0% |
| 0.95 | 0.5 | 0.0 | 0% | 0% |
| 0.95 | 0.5 | 0.3 | 2% | 0% |

### Table B. IV: power to support a true theory, and the size of the support claim

Worst realistic case: psi = 0.5, lambda = 0.3. Cells: P(supportive | gamma = 0) / P(supportive | gamma = delta) / P(contrary | gamma = 2 delta). Normal critical values, 400 draws per cell (Monte Carlo standard error at most 2.5 points).

| Pools x weeks | Reliability | Instrument 0.15 | Instrument 0.3 | Instrument 0.6 |
|---|---|---|---|---|
| 20 x 52 | 0.6 | 0% / 0% / 15% | 0% / 0% / 22% | 2% / 0% / 40% |
| 20 x 52 | 0.8 | 0% / 0% / 16% | 0% / 0% / 22% | 7% / 1% / 51% |
| 20 x 52 | 0.95 | 0% / 0% / 17% | 0% / 0% / 25% | 12% / 2% / 54% |
| 30 x 104 | 0.6 | 0% / 0% / 19% | 0% / 0% / 37% | 46% / 4% / 74% |
| 30 x 104 | 0.8 | 0% / 0% / 16% | 1% / 0% / 42% | 64% / 7% / 84% |
| 30 x 104 | 0.95 | 0% / 0% / 18% | 2% / 0% / 43% | 73% / 7% / 83% |
| 40 x 104 | 0.6 | 0% / 0% / 18% | 1% / 0% / 42% | 67% / 4% / 86% |
| 40 x 104 | 0.8 | 0% / 0% / 21% | 3% / 0% / 43% | 83% / 8% / 92% |
| 40 x 104 | 0.95 | 0% / 0% / 26% | 9% / 1% / 52% | 90% / 7% / 96% |

### Table C. IV first-stage strength (median cluster-robust F for composition)

| Pools x weeks | Instrument 0.15 | Instrument 0.3 | Instrument 0.6 |
|---|---|---|---|
| 20 x 52 | 15 | 66 | 384 |
| 30 x 104 | 47 | 199 | 1154 |
| 40 x 104 | 59 | 267 | 1509 |

Across all 108 designs: the IV support claim's size at the boundary is at most 8%; IV's false-contrary rate at most 5%; OLS's at most 100%.
