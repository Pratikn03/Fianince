# TRAINED AGENT VALIDATION AUDIT (PHASE 3)

**Repository:** `Pratikn03/Fianince`  
**Audit Baseline Commit:** `94dc1511d5de13f6d6bd1b81f1100554e08a85cd`  
**Baseline Script Audited:** `ceiling_suite/papers/recompute_p1_learners.py` (`R_P1_learners.json`, preserved intact)  
**Hardened Validation Script:** `ceiling_suite/papers/validate_trained_learners_hardened.py`  
**Hardened Outputs:**
- `ceiling_suite/papers/recomputed/R_P1_trained_learners_hardened.json`
- `ceiling_suite/papers/recomputed/learner_checkpoints/checkpoints_summary.json`
- `ceiling_suite/papers/recomputed/learner_checkpoints/{rls_trained,mlp_sgd_trained,profit_grad_trained,tabular_bellman_q_trained}_eta_0.40.json`

---

## 1. Code Audit of Baseline `recompute_p1_learners.py` (Task 3.1)

A line-by-line inspection of `ceiling_suite/papers/recompute_p1_learners.py` (lines 112–295) identified two critical scientific defects in the original `P1_trained_learners` implementation:

1. **Checkpoint Bypass Between Burn-In and Probing**:
   - `burn_in_cohort(rule_kind, eta_val, T_burn=5000, seed=...)` (lines 112–162) runs a $5{,}000$-step closed-loop burn-in and returns a dictionary `b_info` containing `"settled_gain"`, `"theta_rls"`, `"theta_mlp"`, and `"theta_q"`.
   - However, in `simulate_trained_learner_experiment()` (lines 200–295), `b_info` is used **only** to record `b_info["settled_gain"]` in the summary JSON; `probe_settled_population()` (lines 165–197) **never accepts `b_info` as an argument**.
   - Inside `probe_settled_population()`, line 172 re-initializes `gains = np.ones(K, dtype=float)` for every rule, and lines 179–180 evaluate the neural rule using `W_in * dphi_0` (normalized by its initial norm) rather than the learned readout vector `theta_mlp`.
   - Consequently, Panel B rows 6–8 in Table 8 (`tab:learners`) of the baseline manuscript tested fixed analytic post-burn-in surrogates rather than the actual learned parameter checkpoints produced by `burn_in_cohort()`.

2. **Mislabeling of `q_profit_trained`**:
   - In `burn_in_cohort()` (lines 149–152), `q_profit_trained` updates a single scalar parameter `theta_q` via online gradient ascent on a smooth saturating feature $y_{\mathrm{st}} = y / \sqrt{1 + (y/0.9)^2}$ (`td_err * y_st / (y_st^2 + 0.02)`).
   - It does **not** maintain a multi-state/multi-action value table $Q(s, a)$ or perform Bellman backups $r_t + \gamma \max_{a'} Q(s_{t+1}, a')$. It is therefore an online **profit-gradient scalar learner**, not a tabular Bellman Q-learner.

In accordance with Global Research-Integrity Rules 2, 3, 11, and 14, `ceiling_suite/papers/recompute_p1_learners.py` and `ceiling_suite/papers/recomputed/R_P1_learners.json` are preserved unaltered so that all 74 registered numbers verified by `verify_paper_numbers.py` remain intact, while the defect is explicitly disclosed in the manuscript and corrected in `ceiling_suite/papers/validate_trained_learners_hardened.py`.

---

## 2. Hardened Implementation of Genuinely Trained Learners (Task 3.2)

`ceiling_suite/papers/validate_trained_learners_hardened.py` trains four distinct online learning rules over $T_{\mathrm{burn}} = 5{,}000$ closed-loop market periods ($x_{t+1} = a x_t + \kappa u_t + \xi_t$, $y_{i,t+1} = (1-\eta_i)y_{i,t} + \eta_i x_{t+1}$), serializes the learned parameter checkpoints to `ceiling_suite/papers/recomputed/learner_checkpoints/`, and reloads those exact checkpoints inside `simulate_probe_from_checkpoints()`:

1. **`rls_trained` (Recursive Least Squares Forecast Learner)**:
   - Maintains forecast slope $\hat\theta_{\mathrm{rls},t} \in \mathbb R$ and inverse covariance $P_{\mathrm{rls},t} > 0$ with forgetting factor $\lambda_{\mathrm{rls}} = 0.995$.
   - Settles at $\bar\eta = 0.40$ to $\hat\theta_{\mathrm{rls}} = 1.0342$ ($P_{\mathrm{rls}} = 0.2546$).

2. **`mlp_sgd_trained` (Two-Layer $\tanh$ Neural Readout Learner)**:
   - Fixed hidden feature map $\phi(y) = \tanh(W_{\mathrm{in}} y + b_{\mathrm{in}}) - \tanh(b_{\mathrm{in}}) \in \mathbb R^8$ with learned readout weights $\hat\theta_{\mathrm{mlp},t} \in \mathbb R^8$ updated by online normalized SGD with $\ell_2$ regularization.
   - Settles at $\bar\eta = 0.40$ to local tangent slope $g(\bar\eta) = \hat\theta_{\mathrm{mlp}}^\top \phi'(0) = 0.9457$.

3. **`profit_grad_trained` (Smooth Online Profit-Gradient Learner, formerly `q_profit_trained`)**:
   - Learns scalar policy parameter $\hat\theta_{\mathrm{pg},t}$ on saturating state $y / \sqrt{1 + (y/c_i)^2}$ via online gradient updates.
   - Settles at $\bar\eta = 0.40$ to $\hat\theta_{\mathrm{pg}} = 0.8741$.

4. **`tabular_bellman_q_trained` (Genuine Tabular Bellman Q-Learner)**:
   - State grid $s_1 < \cdots < s_{21}$ on $[-0.08, 0.08]$ with Gaussian kernel responsibility weights $w_s(y) \propto \exp(-\frac12((y - s_k)/\sigma_s)^2)$, and discrete action grid $a_1 < \cdots < a_{21}$ on $[-0.08, 0.08]$.
   - Updates the $21 \times 21$ value table $Q_t \in \mathbb R^{21\times 21}$ via genuine TD(0) Bellman backups with discount factor $\gamma_{\mathrm{disc}} = 0.90$ and quadratic execution/inventory penalty $\lambda_{\mathrm{inv}} = 0.55$:
     $$ Q_{t+1}(s_k, a_j) = Q_t(s_k, a_j) + \alpha_q w_{s_k}(y_t)\Bigl[a_j r_{t+1} - \tfrac12\lambda_{\mathrm{inv}} a_j^2 + \gamma_{\mathrm{disc}}\max_{a'\in\mathcal A}(\bar Q_t(y_{t+1}, a')) - Q_t(s_k, a_j)\Bigr]. $$
   - Selects actions via the centered Boltzmann policy $\pi_Q(y) = \sum_j a_j \bigl(p_j(y) - p_j(0)\bigr)$ where $p_j(y) \propto \exp(\beta \sum_k w_{s_k}(y) Q(s_k, a_j))$.
   - Settles at $\bar\eta = 0.40$ to local tangent slope $g(\bar\eta) = \pi'_Q(0) = 0.0221$.

---

## 3. Evaluation Across the Three Required Regimes (Task 3.3)

| Regime | Learner | Learned Slope $g(\bar\eta)$ | Exp. Fit $R^2$ | Test A Raw Slope ($O(A^2)$) | Test A Norm. Slope ($O(A)$) | Test A Rel. Gap ($A=0.005$) | Test B $\|\Delta h\|_2$ Slope | Test B Capital Slope |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **Regime 1a**: Unnormalized Frozen Checkpoints (Shared Burn-In Stream) | `rls_trained` | $1.0342$ | $0.9934$ | $3.000$ | $2.000$ | $3.22\times 10^{-7}$ | $2.008$ | $-4.014$ |
| | `mlp_sgd_trained` | $0.9457$ | $0.9942$ | $1.878$ | $0.878$ | $9.67\times 10^{-6}$ | $2.007$ | $-4.012$ |
| | `profit_grad_trained` | $0.8741$ | $0.9948$ | $3.000$ | $2.000$ | $2.16\times 10^{-7}$ | $2.004$ | $-4.006$ |
| | `tabular_bellman_q_trained` | $0.0221$ | $1.0000$ | $2.108$ | $1.108$ | $3.67\times 10^{-6}$ | $1.994$ | $-3.973$ |
| **Regime 1b**: Unnormalized Frozen Checkpoints (Independent Burn-In Streams) | `rls_trained` | $1.0221$ | $0.9935$ | $3.000$ | $2.000$ | $3.16\times 10^{-7}$ | $0.916$ | $-1.746$ |
| | `mlp_sgd_trained` | $0.9391$ | $0.9942$ | $1.878$ | $0.878$ | $9.58\times 10^{-6}$ | $0.493$ | $-0.973$ |
| | `profit_grad_trained` | $0.8591$ | $0.9949$ | $3.000$ | $2.000$ | $2.11\times 10^{-7}$ | $0.846$ | $-1.623$ |
| | `tabular_bellman_q_trained` | $0.0225$ | $1.0000$ | $3.162$ | $2.162$ | $1.88\times 10^{-7}$ | $0.129$ | $-0.375$ |
| **Regime 2**: Tangent-Normalized Frozen Checkpoints | `rls_trained` | $1.0342 \to 1$ | $0.9937$ | $3.000$ | $2.000$ | $3.06\times 10^{-7}$ | $2.007$ | $-4.012$ |
| | `mlp_sgd_trained` | $0.9457 \to 1$ | $0.9937$ | $1.878$ | $0.878$ | $1.05\times 10^{-5}$ | $2.007$ | $-4.012$ |
| | `profit_grad_trained` | $0.8741 \to 1$ | $0.9937$ | $3.000$ | $2.000$ | $2.62\times 10^{-7}$ | $2.007$ | $-4.012$ |
| | `tabular_bellman_q_trained` | $0.0221 \to 1$ | $0.9938$ | $2.113$ | $1.113$ | $2.39\times 10^{-4}$ | $2.007$ | $-4.012$ |
| **Regime 3a**: Continuing Online Adaptation (Moderate LR $=0.01$) | `rls_trained` | $1.0342$ | $0.9934$ | $1.010$ | $0.010$ | $3.03\times 10^{-5}$ | $2.008$ | $-4.015$ |
| | `mlp_sgd_trained` | $0.9457$ | $0.9942$ | $1.356$ | $0.356$ | $3.61\times 10^{-5}$ | $2.007$ | $-4.013$ |
| | `profit_grad_trained` | $0.8741$ | $0.9948$ | $0.960$ | $-0.040$ | $2.61\times 10^{-5}$ | $2.004$ | $-4.006$ |
| | `tabular_bellman_q_trained` | $0.0221$ | $1.0000$ | $2.111$ | $1.111$ | $3.63\times 10^{-6}$ | $1.994$ | $-3.973$ |
| **Regime 3b**: Continuing Online Adaptation (Fast Non-Stationary LR $=0.35$) | `rls_trained` | $1.0342$ | $0.9929$ | $0.995$ | $-0.005$ | $1.10\times 10^{-3}$ | $2.009$ | $-4.019$ |
| | `mlp_sgd_trained` | $0.9457$ | $0.9937$ | $1.022$ | $0.022$ | $1.02\times 10^{-3}$ | $2.009$ | $-4.017$ |
| | `profit_grad_trained` | $0.8741$ | $0.9943$ | $0.997$ | $-0.003$ | $9.44\times 10^{-4}$ | $2.006$ | $-4.009$ |
| | `tabular_bellman_q_trained` | $0.0221$ | $1.0000$ | $2.055$ | $1.055$ | $1.48\times 10^{-5}$ | $1.994$ | $-3.975$ |

---

## 4. Scientific Interpretation and Required Manuscript Revisions (Task 3.4)

1. **Why Regime 1a vs. Regime 1b vs. Regime 2 Clarifies the Exact Scope of the $\delta^{-4}$ Law**:
   - In **Regime 1a** (actual frozen checkpoints trained on the same market innovation path without unit-slope normalization), all four learners satisfy single-exponential impulse fit ($R^2 \in [0.9934, 1.0000]$), small-probe merged-measure equivalence (relative gap $\le 9.67\times 10^{-6} \ll 1\%$), and $\delta^{-4}$ capital scaling (slopes $-4.014, -4.012, -4.006, -3.973$). Because $g(\eta)$ is smooth in $\eta$, the symmetric pair $\bar\eta \pm \delta$ has $\frac12[g(\bar\eta-\delta)+g(\bar\eta+\delta)] = g(\bar\eta) + O(\delta^2)$ and first moment $\frac12[(\bar\eta-\delta)g(\bar\eta-\delta)+(\bar\eta+\delta)g(\bar\eta+\delta)] = \bar\eta g(\bar\eta) + O(\delta^2)$, so all $O(\delta)$ terms cancel by symmetry even without post-training normalization.
   - In **Regime 1b** (actual frozen checkpoints trained on *independent* finite $5{,}000$-step random streams without normalization), random finite-burn-in estimation differences $\hat\theta^{(1)}(\bar\eta) \neq \frac12[\hat\theta^{(2)}(\bar\eta-\delta)+\hat\theta^{(3)}(\bar\eta+\delta)]$ leave a zero/first-order mismatch $\Delta\Phi_{\mathrm{eff}} = O(T_{\mathrm{burn}}^{-1/2})$ between the two economies. That zeroth-order mismatch dominates the $O(\delta^2)$ splitting signal at small $\delta$, flattening the capital slope to $[-1.75, -0.38]$. This demonstrates an important economic point: the $\delta^{-4}$ barrier applies specifically when competing multi-cohort hypotheses are **moment-matched** in aggregate sensitivity $\Phi_{\mathrm{eff}}$ and first moment $k_0$ (as in **Regime 1a** and **Regime 2**).
   - Notice also that for odd functions like $\tanh(y/c_i)$ (`rls_trained`) and $y/\sqrt{1+(y/c_i)^2}$ (`profit_grad_trained`), the quadratic Taylor term at $y=0$ vanishes ($\pi''(0)=0$), so the raw gap between a 1-cohort and 2-cohort economy with different saturation caps is $O(A^3)$ (raw slope $3.000$, probe-normalized slope $2.000$), whereas for asymmetric policies with $\pi''(0) \neq 0$ (`mlp_sgd_trained` with random biases $b_{\mathrm{in}} \neq 0$ and `tabular_bellman_q_trained`), the raw gap is $O(A^2)$ (probe-normalized slopes $0.878$ and $1.108$).

2. **Required Manuscript Revisions in Paper 1 (`ceiling_suite/papers/paper1/p1_mixture.tex`)**:
   - Explicitly disclose that in the baseline `recompute_p1_learners.py` script (`R_P1_learners.json`), `probe_settled_population()` re-initialized unit gains rather than loading `b_info`, and that `q_profit_trained` was a scalar profit-gradient learner.
   - Report the hardened results from `validate_trained_learners_hardened.py` (`R_P1_trained_learners_hardened.json`) across all four genuinely trained learners (including the $21\times 21$ tabular Bellman Q-learner) and across Regimes 1a, 1b, 2, and 3, while retaining the original pre-registered table values for provenance.
