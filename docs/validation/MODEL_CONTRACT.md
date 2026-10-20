# Machine Markets — Canonical Model & Variable Contract (`MODEL_CONTRACT.md`)

**Source of Truth Parameter Dictionary:** [`config/model_parameters.json`](../../config/model_parameters.json)

This document defines the exact variable symbols, physical units, sign conventions,Lean 4 identifiers, and Python variables across the manuscript (`paper/Machine_Markets_JF_Submission.tex`), the 30-module Lean 4 formalization (`research_extension/current_manuscript_lean_20261008/CurrentProofs/`), and the executable Python validation suite (`breakthrough_experiments/` and `scripts/`).

---

## 1. Canonical Variable Dictionary & Units

| Symbol | Physical Meaning | Units | Sign / Domain Convention | Lean 4 Identifier | Python Variable |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $p_t = P^* + x_t$ | Asset mid-price at step $t$ | USDT / unit | $P^* = 100.0\text{ USDT}$, $x_t \in \mathbb{R}$ | `P_star + x_t` | `p_curr = P_STAR + x_t` |
| $x_t = C_{\mathrm{price}} z_t$ | Price displacement from $P^*$ | USDT / unit | $C_{\mathrm{price}} = [1, 0, 0]$ | `x_t` | `x_next = float(C_t @ z_next)` |
| $I_t$ | Dealer physical inventory | Asset units | $I_0 = -2{,}000\text{ units}$ (short; adverse to $x_t > 0$) | `I_t`, `inv` | `inv` (`I0_UNITS = -2000.0`) |
| $K_t$ | Dealer cash balance | USDT | $K_0 = E_0 - I_0 P^* = 210{,}000\text{ USDT}$ | `K_t`, `cash` | `cash` (`CASH0_USDT = 210000.0`) |
| $E_t = K_t + I_t p_t$ | Mark-to-market dealer equity | USDT | $E_0 = 10{,}000\text{ USDT}$ | `E_t` | `eq_curr = cash + inv * p_curr` |
| $\mathrm{MM}_t$ | Binance Tier-2 maintenance margin | USDT | $\max(0,\; 0.005 |I_t| p_t - 50)$, $\mathrm{MM}_0 = 950\text{ USDT}$ | `MM_t` | `mm_curr = max(0.0, MAINT_RATE * abs(inv) * p_curr - MAINT_AMOUNT)` |
| $B_{\mathrm{maint}} = E_0 - \mathrm{MM}_0$ | Initial loss-to-liquidation buffer | USDT | $9{,}050.0\text{ USDT}$ | `B_maint` | `B_MAINT_BUDGET = 9050.0` |
| $\Delta_{\mathrm{safety}}$ | Protective safety reserve above $\mathrm{MM}_t$ | USDT | $950.0\text{ USDT}$ | `Delta_safety` | `SAFETY_RESERVE = 950.0` |
| $\alpha_t \in \mathcal{A}_{41}$ | Non-anticipative admission control | Dimensionless $\in [0, 1]$ | 41-point uniform grid $\{0, 0.025, \dots, 1.0\}$ | `alpha` | `g_star` in `np.linspace(0.0, 1.0, 41)` |
| $s(\alpha_t)$ | Venue shock-gating attenuation | Dimensionless $\in [0.15, 1]$ | $0.15 + 0.85\alpha_t$ (gated) or $1.0$ (unattenuated) | `s_alpha` | `shock_scale` |
| $\Delta I^{\mathrm{hedge}}_t(\alpha_t)$ | Pre-shock inventory hedge execution | Asset units | $-0.06(1 - \alpha_t) I_t$ when $\alpha_t < 0.99$, else $0$ | `dI_hedge` | `hedge_qty = -0.06 * (1.0 - g_star) * inv` |
| $I^{\mathrm{post}}_t(\alpha_t)$ | Post-hedge pre-fill inventory | Asset units | $I_t + \Delta I^{\mathrm{hedge}}_t(\alpha_t) = (1 - 0.06(1-\alpha_t))I_t$ | `I_next` | `inv_after_hedge` |
| $\Delta I^{\mathrm{fill}}_t(\alpha_t)$ | Passive maker order-flow fill absorbed | Asset units | $-12 \alpha_t s(\alpha_t) w_{1,t}$ (or $0$ if halted) | `dI_fill` | `flow_absorbed = -12.0 * g_star * shock_scale * float(shocks[t, 0])` |
| $\Delta I^{\mathrm{fill}}_{\max}(\alpha_t)$ | Admissible passive fill upper bound | Asset units | $12 \alpha_t s(\alpha_t) \bar{u}_{\mathrm{step}}$ | `dI_fill_max` | `max_fill_qty = 12.0 * alpha * shock_scale * u_bar_step` |
| $C_{\mathrm{hedge}}(\alpha_t)$ | Taker hedge spread + fee cost | USDT | $|\Delta I^{\mathrm{hedge}}_t| \cdot (0.02 + 0.0004 \max(p_t, P^*))$ | `C_hedge` | `hedge_fee_cost` |
| $C_{\mathrm{fill}}(\alpha_t)$ | Worst-case post-fill margin & inventory charge | USDT | $\Delta I^{\mathrm{fill}}_{\max}(\alpha_t)\bigl[\mu(p_t + \Delta p_{\max}(\alpha_t)) + \max(0, \frac{1}{2}\Delta p_{\max}(\alpha_t) - 0.02)\bigr]$ | `C_fill` | `fill_margin_charge + fill_inv_loss` |
| $\bar{u}_{\mathrm{step}}, \bar{u}_{\mathrm{cum}}$ | Admissible step / cumulative shock bounds | USDT / unit | $\bar{u}_{\mathrm{step}} = 0.05$, $\bar{u}_{\mathrm{cum}} = 0.135$ | `u_step`, `u_cum` | `u_bar_step = 0.05`, `u_bar_cum = 0.135` |
| $L_{\mathrm{cap}}(\delta; d_1, d_2)$ | Spectral capital floor at tail level $\delta$ | USDT | Infimum over $\mathcal{D}_{\mathrm{adm}} = 64.7485 > 64.7423\text{ USDT}$ | `capitalFloor` | `L_cap` in `verify_p02_full_domain_certificate.py` |
| $\Delta\eta = \eta_2 - \eta_1$ | Cohort learning-rate separation | Dimensionless $\in (0, 1)$ | $\eta_1, \eta_2 \in [\eta_{\min}, \eta_{\max}] \subset (0, 1)$ | `d_eta` | `delta_eta` |
| $Q = \beta_1 + \beta_2$ | Reduced-form flow-feedback index | Dimensionless | Forward EMA ($0.0081536$) vs Observed EMA ($0.0003807$) vs Raw ($-0.0002821$) | `feedbackMeasure` | `Q_ema_fwd`, `Q_ema_obs`, `Q_raw` |

---

## 2. Equation-to-Code Identity Invariants

1. **Exact Passive Fill Law (`E2E-A`, Theorem IA.D.8 Eq. IA.39):**
   - **Manuscript:** $\Delta I^{\mathrm{fill}}_t(\alpha_t) = -12\,\alpha_t\,s(\alpha_t)\,w_{1,t}$, with admissible envelope $\Delta I^{\mathrm{fill}}_{\max}(\alpha_t) = 12\,\alpha_t\,s(\alpha_t)\,\bar{u}_{\mathrm{step}}$.
   - **Code (`exp18_crash_free_ai_guard.py`):**
     - Guard envelope (`evaluate_guard_inequalities_ia39`): `max_fill_qty = 12.0 * alpha * shock_scale * u_bar_step`.
     - Episode simulator (`simulate_double_entry_dealer_episode`): `flow_absorbed = 0.0 if step_infeasible_halt else -12.0 * g_star * shock_scale * float(shocks[t, 0])`.
   - **Invariant:** For all $\alpha_t \in \mathcal{A}_{41}$ and $|w_{1,t}| \le \bar{u}_{\mathrm{step}}$, $|\Delta I^{\mathrm{fill}}_t(\alpha_t)| \le \Delta I^{\mathrm{fill}}_{\max}(\alpha_t)$, with equality when $|w_{1,t}| = \bar{u}_{\mathrm{step}}$.

2. **Non-Anticipative Action Timing & `NO_SAFE_ACTION` Protective Halt (`E2E-B`):**
   - $\alpha_t$ is selected strictly from pre-shock state $(z_t, I_t, p_t, E_t, \mathrm{MM}_t)$ before `shocks[t]` is read.
   - If all 41 candidates $\alpha \in \mathcal{A}_{41}$ violate Equation (IA.39), the controller sets `pre_infeasible = True`, transitions immediately to `status = "NO_SAFE_ACTION"` (`protective_halt_engaged = True`, `g_star = 0.0`, `flow_absorbed = 0.0`), and records the protective halt step without overriding the action post-shock.
