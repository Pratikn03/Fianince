# P0-2 Certificate Boundary & Outward-Rounded Enclosure Architecture (`64.7423` USDT)

**Manuscript Theorems:** Theorem IA.D.1 & Theorem IA.D.4 (`S20`)  
**Lean 4 Module:** [`CurrentProofs/SpectralCapital.lean`](../../research_extension/current_manuscript_lean_20261008/CurrentProofs/SpectralCapital.lean)  
**Standalone Verifier:** [`scripts/independent_checks/verify_p02_full_domain_certificate.py`](../../scripts/independent_checks/verify_p02_full_domain_certificate.py)

---

## 1. Exact Division of Labor Between Lean 4 and Standalone Outward-Rounded `Decimal`

| Verification Layer | Mathematical Object Certified | Method & Precision | Certified Output |
| :--- | :--- | :--- | :--- |
| **Lean 4 Kernel (`CurrentProofs/SpectralCapital.lean`)** | 1. Universal strategy-level Rayleigh–Hölder decomposition (`finite_horizon_generalized_rayleigh_decomposition`)<br>2. Telescopic double-entry round-trip loss identity (`flat_round_trip_double_entry_terminal_loss_identity`)<br>3. Closed-form $\Delta_2$-free quadratic-linear envelope (`analytical_quadratic_linear_envelope_bound`)<br>4. Exact 2-slab concave-secant certificate at the worst angular interval $m^* = 955$ (`worst_interval_955_two_slab_rational_certificate`) | Exact symbolic algebra (`ring`, `linarith`, `positivity`) and exact rational arithmetic (`norm_num`) inside the Lean 4 kernel (`0` `sorry`, `0` unapproved axioms). | Proves `g_hi * u_top < 99/100`, `fm_lo^2 <= 1 - g_hi * u_mid <= fm_hi^2`, `ft_lo^2 <= 1 - g_hi * u_top`, and `min(slab1_lb, slab2_lb) > 64.7429 > 64.7423` USDT at $m^* = 955$. |
| **Upstream 50-Digit `Decimal` Impulse Verifier (`_decimal_primary_impulse_enclosure`)** | Closed-loop null and alternative impulse responses $h_0(t), h_1(t)$ ($t = 0, \dots, 160$) from exact rational parameters $(\kappa=0.8, a=0.5, q=0.2, \eta_0=0.4, \eta_{1,\pm}=0.4 \pm 0.05)$ | 50-digit outward-rounded `Decimal` interval recursion (`ROUND_FLOOR` for `h_lo`, `ROUND_CEILING` for `h_hi`), compared against `Decimal.from_float(h_flt[t])` purely in 50-digit `Decimal`. | Maximum float-vs-`Decimal` impulse discrepancy $\le 4.55 \times 10^{-17}$; 50-digit `Decimal` interval width $\le 1.8 \times 10^{-48}$. |
| **Weyl Generalized Eigenvalue Enclosure (`verify_full_domain_certificate`)** | Generalized spectrum $\lambda_k(M, G_0)$ and $G_0$-orthonormal basis residual $R = M V - G_0 V \Lambda$ | Outward-rounded 40-digit `Decimal` bound on $\|R\|_F / (\sqrt{\lambda_{\min}(G_0)}(1 - \|V^\top G_0 V - I\|_F))$ propagated from 50-digit impulse error `mat_input_pad_dec`. | Certified Weyl eigenvalue perturbation bound $\varepsilon_{\mathrm{Weyl}} \le 8.75 \times 10^{-13}$. |
| **50-Digit `Decimal` Taylor Trigonometric Enclosure (`decimal_cos_sin_enclosure`)** | $\cos\theta, \sin\theta$ over each of the $n_\theta = 1{,}800$ intervals $I_m = [\theta_{m,a}, \theta_{m,b}] \subset [0, \pi]$ | 18-term alternating Taylor series evaluated in 50-digit `Decimal` with certified truncation + rounding remainder $\le 10^{-22}$ and exact endpoint monotonicity. | Pure `Decimal` interval bounds `[cos_lo, cos_hi]`, `[sin_lo, sin_hi]` with zero floating-point `np.cos`/`np.sin` calls inside the certified loop. |
| **Directed `Decimal` Square-Root Enclosures (`decimal_sqrt_floor`, `decimal_sqrt_ceil`)** | All square roots in secant slopes $\sqrt{1 - \gamma_{\max} u}$, $\sqrt{L_{0,\min}}$, and $W_{\perp,\max}$ | Exact 100-digit square verification (`s_lo^2 <= x < next_plus(s_lo)^2` and `next_minus(s_hi)^2 < x <= s_hi^2`), bypassing Python's `ROUND_HALF_EVEN` `Decimal.sqrt()`. | Provably directed lower and upper square-root bounds across all 1,800 intervals. |
| **Full 1,800-Interval Whole-Domain Sweep (`verify_full_domain_certificate`)** | Global infimum of $L_0(v) + c_{\mathrm{fee}}\|v\|_1$ over all flat round-trip probes $v \in \mathcal{V}_{80}$ ($(\theta, \Delta_2) \in [0, \pi) \times [0, \infty)$) | 1,800 angular intervals $\times$ 2 concave-secant slabs on $[0, \Delta_{2,\max}(I_m)]$ + analytical fee non-negativity on $[\Delta_{2,\max}(I_m), \infty)$. | `full_domain_2slab_outward_decimal_lb = 64.7429062992 >= 64.7423` USDT (`1`-slab bound `64.7377978874` USDT; worst interval $m^* = 955$). |

---

## 2. Whole-Domain Coverage on $[0, \pi) \times [0, \infty)$ (`0` Omitted Tail Regions)

For every angular interval $I_m \subset [0, \pi)$ ($m = 0, \dots, 1799$):
1. **Large-$\Delta_2$ Region ($\Delta_2 \ge \Delta_{2,\max}(I_m) \equiv 65.50 - L_{0,\min}(I_m)$):**
   Because $\ell_1$ transaction fees are non-negative ($c_{\mathrm{fee}}\|v\|_1 \ge 0$), total probing loss satisfies
   $$L_{\mathrm{tot}}(v) = L_0(\theta) + \Delta_2 + c_{\mathrm{fee}}\|v\|_1 \ge L_{0,\min}(I_m) + \Delta_{2,\max}(I_m) = 65.50 > 64.7423\text{ USDT}.$$
2. **Bounded-$\Delta_2$ Region ($\Delta_2 \in [0, \Delta_{2,\max}(I_m)]$):**
   Across all 1,800 intervals, the verifier explicitly computes and asserts
   $$\max_{0 \le m < 1800} \gamma_{\max}(I_m)\,\Delta_{2,\max}(I_m) = 0.687314 < 0.99 < 1.$$
   Consequently, `unverified_d2_tail_intervals == 0`: $u_{\mathrm{top}} = \Delta_{2,\max}(I_m)$ identically for every interval, and the two concave-secant slabs $[0, u_{\mathrm{mid}}]$ and $[u_{\mathrm{mid}}, \Delta_{2,\max}(I_m)]$ cover $100\%$ of $[0, \Delta_{2,\max}(I_m)]$ without truncation.

---

## 3. Adversarial Negative / Rejection Tests (`E2E-C`, `T03-09`, `T03-10`)

1. **`T03-09` (Deliberately Perturbed Eigenpair Rejected):**
   Perturbing the dominant generalized eigenvalue $\lambda_1(M, G_0)$ by $+1\%$ inflates the generalized residual $\|M V - G_0 V \Lambda_{\mathrm{bad}}\|_F$ and the Weyl perturbation bound $\varepsilon_{\mathrm{Weyl}}$, dropping the certified lower bound below `62.0` USDT and causing the certificate check (`>= 64.7423`) to fail (`adversarial_perturbed_eigenpair_rejected == True`).
2. **`T03-10` (Unguarded `Decimal.sqrt()` Rejected as Floor):**
   Under 25-digit `ROUND_FLOOR`, Python's `Decimal(2).sqrt()` returns `1.414213562373095048801689`, whose exact 50-digit square exceeds `2` (`raw_decimal_sqrt_rejected_as_floor == True`), whereas `decimal_sqrt_floor(Decimal(2), prec=25)` returns `1.414213562373095048801688` with exact square strictly $< 2$.
