# From Human Markets to Machine Markets
## Master Research Release 2.0 (Submission-Ready Master Edition) | September 2026

**Start with [the integrated research paper](paper/Machine_Markets_Final_Integrated_Paper.pdf) (62 pages) or the [combined master volume](Machine_Markets_Combined_Master.pdf) (86 pages).**
The self-contained [LaTeX source](paper/Machine_Markets_Final_Integrated_Paper.tex) and the [Mathematical Supplement source](paper/Machine_Markets_Mathematical_Supplement.tex) are beside them in `paper/`.

This master release establishes the complete, unified scientific package for *Machine Markets*:
1. **8-Chapter Consolidated Main Manuscript** (62 pages, 0 overfull `\hbox`es, 0 undefined references/citations).
2. **Mathematical Supplement** (24 pages, Sections S1–S14, complete proofs, continuous-time dynamics, and covariance geometry).
3. **Combined Master Volume** (86 pages, uniting the main paper and supplement).
4. **219-Test Hierarchical Verification Suite** (104 native + 87 pytest + 4 numerical suites + 24 independent gates) passing at 100% offline.
5. **Standalone Zero-Dependency Verifier** (`independent_verifier/verifier.py`) passing all 24 verification gates ($< 7.2 \times 10^{-14}$ error) without importing project libraries.
6. **Method-to-Evidence Crosswalk** (Table 4) establishing unbroken theorem $\to$ code $\to$ artifact $\to$ paper traceability.
7. **Learned-Agent Transfer Layer (Layer 4)** (Section 6.4, Table 14) evaluating tabular Q-learning policies (6,125 states, 5 actions), active counterfactual adaptation, and model-class validity audits.
8. **Empirical Microstructure Calibration (Gates 2–4)** (Section 7.3, Table 17) authenticating external market channels across 3.41 GB of public LOB depth and klines from Binance Vision.

---

## The Core Submission Blockers & Master Resolutions

| Blocker | Master Resolution | Evidence / Location |
| :--- | :--- | :--- |
| **1. Proof $\to$ Code $\to$ Result Linkage** | Integrated Method-to-Evidence Crosswalk Table; mapped every mathematical theorem to its exact codebase implementation, experiment ID, output artifact, and paper location. | Table 4 (p. 22), `docs/CLAIM_MAP.md`, `manifests/claims.csv` |
| **2. Conic Certificate Informativeness** | Executed monotonic budget sweep ($R=128 \to 32,768$, 300 solves total); proved the conic certificate contracts by up to 70.4% in width, reaching **100.0% decisiveness and 0.0% conditional error** at $R=32,768$. | Figure 4 (p. 24), `research_extension/outputs/conic_contraction_results.json` |
| **3. Output-Error 57.1% Error Rate** | Factorial diagnostic across conditions C1–C4 ($N=400$ panels); proved matched models achieve zero bias ($|\text{bias}| \le 0.00004$), while single-rate fitting to a two-rate ground truth induces $-0.1072$ structural misspecification bias. | Table 6 (p. 25), `research_extension/outputs/output_error_diagnostic_results.json` |
| **4. Step-Function vs Smooth Solvency Surface** | Executed 330-cell factorial shock sweep ($\mu \in [-0.2, -2.0]$); established smooth monotone solvency boundary and isolated causal chain: dealer halts occur with positive equity (\$9,999.06) from **inventory capacity exhaustion** ($|\text{inv}_t| > 25 \times \text{mult}$), whereas unlimited funding produces true balance-sheet insolvency ($-\$122.03$). | Table 12 (p. 39), Table 13 (p. 40), Section 6.2 |
| **5. Empirical Predictive Overclaims** | Re-anchored Coinbase ($N=10$) and Binance US (175 runs) studies strictly as exploratory cross-sectional associations and empirical model sensitivity under passive observation; eliminated uncalibrated crisis prediction claims. | Chapter 7, Tables 15–16 (pp. 43–45) |
| **6. Learned-Agent Transfer Layer (RL)** | Executed tabular Q-learning across 6,125 states; verified learned policies reduce halts to 0% and dislocations by 75%; demonstrated that observer model audit classifies 5/5 learned policies as `OUTSIDE_CERTIFIED_MODEL_CLASS` ($R^2 \approx 0.01\text{--}0.24$), proving safe abstention. | Chapter 6, Section 6.4, Table 14 (p. 41) |
| **7. Public Microstructure Grounding (Gates 2–4)** | Calibrated market channels against 3.41 GB public Binance Vision data; proved costed active probing protocol (\$0.59 to \$89.00/1,000 episodes); confirmed balance-sheet conservation ($\Delta\text{eq} < 10^{-10}$) and monotone solvency frontiers. | Chapter 7, Section 7.3, Table 17 (p. 46) |

---

## Read in this order
1. **[Main Paper](paper/Machine_Markets_Final_Integrated_Paper.pdf)**: 8-chapter core manuscript (Introduction, Closed-Loop Model, Identification Boundaries, Observable Probes, Group Identification, Funded Market Solvency & RL Transfer, Empirical Calibration & Digital Assets, Discussion & Frontiers).
2. **[Mathematical Supplement](paper/Machine_Markets_Mathematical_Supplement.pdf)**: Sections S1–S14, exact proofs, continuous-time small-gain theorems, F-calibrated response ellipsoids, McCormick conic relaxations, and two-world abstention bounds.
3. **[Claim Map & Traceability Matrix](docs/CLAIM_MAP.md)**: Cryptographic and experimental provenance for every numerical, mathematical, and empirical claim.
4. **[Reproduction Report](docs/REPRODUCTION_REPORT.md)**: Baseline and extension audit of all 210 automated tests and numerical fixtures.
5. **[Reproduction Guide](docs/REPRODUCTION_GUIDE.md)**: Complete offline instructions for running tests, verifiers, and rebuilding PDFs.
6. **[Requirements for Flagship Acceptance](docs/FINAL_RESEARCH_REQUIREMENTS.md)**: Prospective scientific gates for future empirical and laboratory research programs.

---

## Folder map
```text
Machine_Markets_Master_Release/
  README.md                            Master release index and blocker resolution summary
  Machine_Markets_Combined_Master.pdf  Combined 86-page master volume (Main + Supplement)
  paper/
    Machine_Markets_Final_Integrated_Paper.tex   Self-contained 8-chapter LaTeX source (62 pages)
    Machine_Markets_Final_Integrated_Paper.pdf   Compiled main manuscript (0 overfulls, 0 undefined refs)
    Machine_Markets_Mathematical_Supplement.tex  Mathematical supplement LaTeX source (24 pages)
    Machine_Markets_Mathematical_Supplement.pdf  Compiled supplement (0 overfulls)
    Machine_Markets_Combined_Master.pdf          Combined master volume
  independent_verifier/
    verifier.py                        Zero-dependency verifier testing 24 numerical gates (< 7.2e-14 error)
  manifests/
    claims.csv                         Machine-readable scientific claim register with source artifacts
    study_inventory.json               Inventory of simulation and empirical studies
  reference_directory/
    run_checks.py                      Numerical checks for supplement theorems and ellipsoids
    test_mathematical_supplement.py    21 automated tests for supplement theorems
  tests/
    test_q_learning_transfer.py        Automated test for Q-learning transfer results & model audit
    test_gate24_public_data.py         Automated test for Gate 2-4 public data calibration
    mm_revision/                       Master revision test suites (conic certificate, contracts, gates)
  research_extension/
    learned_agents/                    Q-learning environment, training, evaluation, and policy audit
    gate24_public_data/                Binance Vision public data pipeline and calibrated simulator
    mm_revision/                       Core revision modules: conic certificate, output-error, funded stress
    outputs/                           Frozen JSON and CSV output artifacts from all experiments
    tests/                             Group identification and extension test suite
  studies/
    audited_constraints/               v0.5 study: audited memory and dealer stress
    observable_stress_tests/           v0.4 study: observable recurrence LP and probe designs
    full_horizon_audit/                Full conventional-estimator comparison
    hidden_slow_learners/              Original exact construction and experiments
  docs/                                Traceability matrices, reproduction guides, and research gates
  tools/                               Portable verifier, test launcher, and build scripts
```

---

## Quick Verification (Offline)
```bash
# 1. Native Test Suite (104 tests):
python tools/run_all_tests.py

# 2. Pytest Suite (87 tests):
PYTHONPATH=. pytest tests/ research_extension/tests/ reference_directory/test_mathematical_supplement.py

# 3. Independent Zero-Dependency Verifier (24 gates):
python independent_verifier/verifier.py

# 4. Mathematical Supplement Numerical Checks:
python reference_directory/run_checks.py
```
Total automated tests: **219 passed in ~8 seconds**.
All experiments require no GPU, no financial account, no live market connection, and no external API key.

---

## Scientific Positioning & Epistemic Scope
This package provides a rigorous, model-conditioned analysis of what finite market observations can establish about adaptive algorithmic feedback, what audited architectural disclosure adds, and why signal-level stability ($S < 1$) fails to guarantee balance-sheet solvency when trading buffers bind. The empirical cryptocurrency studies are explicitly exploratory. External replication and live institutional validation remain pending (see `docs/FINAL_RESEARCH_REQUIREMENTS.md`).

