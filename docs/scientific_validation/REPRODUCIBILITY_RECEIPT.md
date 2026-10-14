# Machine Markets (107p) — End-to-End Reproducibility Receipt

## 1. Independent Reference Oracle Verification
```bash
.venv/bin/python3 scripts/independent_checks/independent_model_and_counterexamples.py
```
- **Output Receipt:** `scripts/independent_checks/independent_oracle_receipt.json`
- **Module Independence:** Zero project modules imported (`sys.modules` check enforced).
- **Verified Counterexamples & Bounds:**
  - `CE-01`: Two-trade flat sequence $v = (+1, -1)^\top$: Toeplitz fee-free loss $= 0.348800$~USDT vs. direct-only proxy $= 0.800000$~USDT (`C_account_pathwise = 0.428800$~USDT vs. proxy `0.885000$~USDT).
  - `CE-02`: Zero-padded $L=240$ candidate extended to $L=320$ and $L=480$: $C_{\mathrm{account}} = 64.5646$~USDT at $L=240, 320, 480$, satisfying $C^*(L+1) \le C^*(L)$.
  - `CE-03`: Unshifted Nyquist value $\operatorname{Re} H_0(-1) - \kappa/2 = -0.919529 < 0$ vs. shifted $\operatorname{Re}\widehat{H}_0(-1) - \kappa/2 = +0.119529 > 0$.
  - `CE-04`: Literal Eq. (`eq:ia_lecam_pair`) at $\Delta\eta = 0.10$: $\Delta M_0 = \Delta M_1 = \Delta M_2 = 0$, $\Delta M_3 = 9.9\times 10^{-6}$, $\|\Delta h\|_2 = 6.8371\times 10^{-5}$, $N^*_{\mathrm{LeCam,an}} = 5{,}927.57 \implies 5{,}928$ resets (vs. rate-refined $N^*_{\mathrm{LeCam,ref}} = 6{,}172.24 \implies 6{,}173$ resets with $\Delta M_1 = -8.604\times 10^{-6}$, $\Delta M_2 = -6.883\times 10^{-6}$).
  - `CE-05`: Rate-spacing boundary $\Delta\eta_{\max} = \bar{\eta}/p_+ = 8/11 \approx 0.727273$; at $\Delta\eta = 0.75 \in (0, 2\bar{\eta})$, $\eta_{0,1} = -0.0125 < 0$.
  - `CE-06` & `CE-07`: Single-step admissible shock threshold $\bar{u}_{\mathrm{adm,safe}} = 4.0299$~USDT ($\bar{u}_{\mathrm{adm,liq}} = 4.5025$~USDT); out-of-domain shock $u_0 = (100, 0, 0)^\top$ causes $201{,}000$~USDT drawdown unattenuated ($30{,}150$~USDT attenuated) $> B_{\mathrm{maint}} = 9{,}050$~USDT, liquidating for every $\alpha \in [0, 1]$.
  - `CE-15`: Signed-shock counterexample at $I_0 = -2{,}000, P^* = 100$: $|\Delta p_1| = 10 > 4.0299$~USDT yields $E_1 = 30{,}000 > \mathrm{MM}_1 = 850$~USDT (`SAFE_SOLVENT`) when $\Delta p_1 = -10$~USDT, and $E_1 = -10{,}000 < \mathrm{MM}_1 = 1{,}050$~USDT (`INSOLVENT_LIQUIDATED`) when $\Delta p_1 = +10$~USDT.

## 2. Remediated Breakthrough Experiments & Figures Reproduction
```bash
.venv/bin/python3 breakthrough_experiments/exp13_account_capital.py
.venv/bin/python3 breakthrough_experiments/exp16_nonconvex_duality_closing.py
.venv/bin/python3 breakthrough_experiments/exp17_minimax_lecam_bound.py
.venv/bin/python3 breakthrough_experiments/exp18_crash_free_ai_guard.py
.venv/bin/python3 breakthrough_experiments/exp19_historical_crash_replay.py
.venv/bin/python3 breakthrough_experiments/exp21_empirical_multi_asset_kreiss_network.py
python3 breakthrough_experiments/generate_all_breakthrough_figures.py
```

## 3. Theorem-to-Code Bridge & Lean 4 Axiom Audit
```bash
.venv/bin/python3 scripts/verify_theorem_code_bridge.py
```
- **Result:** All 23 manuscript mathematical environments matched; `268` named Lean 4 declarations verified with `0` `sorry` and `0` unapproved axioms.

## 4. LaTeX Manuscript Build & Test Suite Execution
```bash
cd paper && pdflatex -interaction=nonstopmode Machine_Markets_JF_Submission.tex && pdflatex -interaction=nonstopmode Machine_Markets_JF_Submission.tex
.venv/bin/pytest tests/ -q
/opt/homebrew/bin/ruff check scripts/independent_checks/ tests/scientific_validation/
```
