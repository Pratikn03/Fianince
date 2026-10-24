# Referee & Replication Verification Checklist

**Research Program:** Machine Markets  
**Date of Audit:** October 22, 2026  
**Audited Baseline Commit:** `cf55c05` (`main`)  
**Continuous Integration Status:** Passing (100% Green on GitHub Actions Run `39705944833`)

---

## Part 1: Mathematical Theorems & Formal Mechanization

| Environment ID | Manuscript Statement | Lean 4 Status | Mechanization File | Axiom Audit |
| :--- | :--- | :---: | :--- | :---: |
| `p1_prop_ident` | Prop: Price-only Unidentifiability | **Full** | `ARKernels.lean` | 0 sorry, 0 unapproved |
| `p1_thm_probe` | Thm: Active Probing Capital Scaling | **Full** | `SpectralCapital.lean` | 0 sorry, 0 unapproved |
| `p1_prop_lecam` | Prop: Le Cam Two-Point Lower Bound | **Full** | `GaussianInformation.lean` | 0 sorry, 0 unapproved |
| `p1_prop_esprit`| Prop: Confluent Vandermonde Minimax Rate | **Full** | `ProbeGeometry.lean` | 0 sorry, 0 unapproved |
| `p1_thm_dual` | Thm: Finite-Horizon Rayleigh-Hölder Duality | **Full** | `PhysicalAccounts.lean` | 0 sorry, 0 unapproved |
| `p2_prop_kreiss`| Prop: Non-Normal Transient Amplification | **Full** | `KreissResolvent.lean` | 0 sorry, 0 unapproved |
| `p2_thm_depth` | Thm: Exact Kreiss Depth Condition | **Full** | `Capacity.lean` | 0 sorry, 0 unapproved |
| `p2_thm_guard` | Thm: Maximal Pre-Trade Resolvent Guard | **Full** | `WindowGate.lean` | 0 sorry, 0 unapproved |
| `p2_prop_twoworld`| Prop: Separation of Identification vs Safety | **Full** | `InfoSafetyExtensions.lean`| 0 sorry, 0 unapproved |
| `p2_prop_equil`| Prop: Equilibrium Depth & Risk Rebate | **Full** | `Microfoundations.lean` | 0 sorry, 0 unapproved |

- **Total Lean 4 Declarations:** 473 named declarations across 38 modules (445 manuscript, 28 thesis).
- **Transitive Axiom Footprint:** Strictly standard Lean 4 axioms (`propext`, `Classical.choice`, `Quot.sound`). Zero `sorry`, zero unapproved axioms.

---

## Part 2: Numerical Verification & Arbitrary-Precision Audits

- **Verification Script:** `ceiling_suite/papers/independent_math_audit.py`
- **Arithmetic Engine:** 80-digit `decimal.Decimal` arbitrary precision.
- **Verified Endpoints:**
  - Tap-2 impulse response difference ($\Delta h_2$): Exact match to $10^{-80}$ ($0.0$ error).
  - Probing Volume Slope: $-2.002$ (theoretical: $-2.000$).
  - Quadratic Capital Slope: $-4.005$ (theoretical: $-4.000$).
  - Repeated-Cycle Energy Dissipation Slope: $-3.997$ (theoretical: $-4.000$).
  - Gauss vs. Gauss–Radau moments matched through $2K-2$: Exact to $10^{-80}$ ($0.0$ residual).

---

## Part 3: Empirical Ledgers & Pre-Registered Tests

- **Ledger Audit Script:** `verify_paper_numbers.py`
- **Result:** **74 numbers checked, 0 mismatches**.
- **Historical Crisis Datasets:** 345,600 SHA-256 verified 1-second spot intervals across May 2021 Flash Crash, May 2022 Terra/LUNA, Nov 2022 FTX, Mar 2023 SVB depeg.
- **Contagion Cascade Replay:** 691,200 1-second bars across 8 cross-margined assets (BTC, ETH, SOL, BNB, ADA, XRP, DOGE, MATIC).
- **Multi-Policy Fair Benchmarks:** Matched training notional ($1\text{M}$ USDT) and matched risk budget ($\mathrm{ES}_{95}$):
  - Peak catastrophic drawdown reduced by $28.5\%$ ($623\text{k} \to 445\text{k}$ USDT).
  - Admitted capacity increased by $+7.9\%$ at matched $\mathrm{ES}_{95}$.
  - Directional long/short breaches accounted for ($14.3\% / 18.3\%$ vs. $31.3\%$ 2-sided).

---

## Part 4: Known Boundaries & Negative Results Preserved

In accordance with strict research integrity standards, all limitations, null results, and failed primaries are fully reported:
1. **Part 25 Primary 2 Placebo Failure:** The 5-minute jump placebo absorbed $78.6\%$ of variance and failed Primary 2, fully disclosed as path-norm collinearity ($r=0.9235$ under Gaussian random walk).
2. **Disclosure Value Interpretation:** Regulatory inventory disclosure improves forecasting by revealing aggregate level persistence ($y_{t+6} \approx \rho^6 y_t$, explaining $>99\%$ of $R^2$), not by uncovering hidden algorithmic memory kernels.
3. **S21 Estimator-Level Bound:** Minimax parameter-blind recovery for confluent Vandermonde systems is bounded under true poles; uniform finite-sample stability under empirical sample poles remains a conditional asymptotic property.
