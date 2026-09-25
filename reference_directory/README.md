# Machine Markets: Mathematical Supplement Reference Directory

This directory contains the reference implementation, 21 unit tests, and looped numerical consistency fixtures for the mathematical supplement:
**"Mathematical Repairs and Covariance-Aware Inference for Machine Markets"** (September 24, 2026).

## Execution

From this directory:
```bash
python -m unittest discover -v
python run_checks.py
```

From repository root:
```bash
PYTHONPATH=. python -m unittest discover -s reference_directory -v
PYTHONPATH=. python reference_directory/run_checks.py
```

## Structure

- `continuous.py`: Continuous-time stability boundaries, Metzler/Hurwitz positive vector characterization (Lemma 3.1), small-gain boundary $\rho(\Gamma^{-1} g B C) < 1$ (Theorem 3.3), common-rate spectral abscissa formula (Proposition 3.5), forward Euler scaling, and exact sampling limits (Theorem 3.6).
- `group.py`: Group identification under channel probing $b = \eta U q$ (Theorem 4.1), unknown-rate polyhedral identified sets (Theorem 4.2), 4-tap aggregate recovery (Proposition 4.3), and heterogeneous mode separation (Section 4.5).
- `ellipsoid.py`: Finite-sample Gaussian response ellipsoids, Hotelling exact $F$-calibration $k_\alpha^2$ (Theorem 5.1), linear contrast support (Proposition 5.2), and the rational 4-coefficient non-identification witness (Proposition 5.3).
- `conic.py`: Exact model-compatible set $\mathcal{K}_\alpha$, data-derived mass cap $M = U_2 / (\underline\eta L_0)$ (Lemma 7.1), continuous rate-bin envelopes (Section 7.2), McCormick bilinear lifting (Section 7.3), conic relaxation containment (Theorem 7.2), and residual-corrected dual lower bounds (Proposition 9.1).
- `decisions.py`: Directional decision rules (Theorem 10.1), two-world abstention bounds (Theorem 10.2), and account solvency non-transfer simulation (Proposition 11.1).
- `test_mathematical_supplement.py`: 21 unit tests covering all formal propositions and bounds.
- `run_checks.py`: The executable numerical check script covering:
  - 120 continuous systems fixtures.
  - Gaussian calibration illustration ($R=32, p=4, 10,000$ panels, seed 240926): exact $F$ coverage $94.76\%$ ($9,476/10,000$) vs $\chi^2_4$ $89.46\%$ ($8,946/10,000$).
  - 200 off-grid positive-model fixtures.
  - Calculation log verification ($S=0.82$, $\rho(J)=0.9900902493$, $T_8$ two-sided $p=0.03871045$, decision bound $14.88\%$).
