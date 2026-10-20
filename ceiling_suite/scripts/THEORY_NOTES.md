# New theory results (Oct 19, 2026), for the final write-up

## Paper 2: three-state amplification (replaces Prop. t6m's false numerical "iff")

Model: x_t = a x + phi d + kappa (u + f), d_t = (1-r) d + eps (u + f), f_t = (1-eta) f + eta q x_{t-1}.
Initial state after a unit shock: x0 = kappa, d0 = eps, f0 = 0. h_k = x_k.

1. **Sufficient (unchanged, proved):** h1 - h0 = C3 = phi eps + kappa^2 eta q - (1-a) kappa. So C3 > 0 implies amplification.

2. **The converse is FALSE (new, numerical counterexamples; t6m_search*.py):**
   - q < 0 (contrarian flow): oscillatory overshoot with C3 << 0 (ratios up to 11x).
   - q > 0 and phi*eps < 0 (replenishment, which is the empirical regime): oscillatory overshoot at C3 ~ -1 (ratios up to 9x, peaks at lag 50-500, needs slow refill and slow momentum).
   - q > 0 and phi*eps >= 0 (all channels reinforcing): small overshoots (up to 9%) at C3 slightly below 0.
   - The old text ("in 1,136 random stable draws, amplified iff C3 > 0") must be removed.

3. **Theorem A (depth-free; proved, verified in 30,702 draws):** if phi*eps = 0 and q >= 0, the (x, f) system matrix
   M = [[a + kappa eta q, kappa (1-eta)], [eta q, 1-eta]] is entrywise nonnegative; h_k = kappa (M^k)_11.
   Real eigenvalues lambda2 <= m11 <= lambda1 (Perron), so (M^k)_11 = c1 lambda1^k + c2 lambda2^k with c1, c2 in [0, 1], c1 + c2 = 1.
   Hence h_k <= kappa rho^k < kappa for every k >= 1: **a stable book cannot amplify through momentum alone.**
   Corollary: stability forces m11 < rho < 1, so C3_flow < 0 always. C3_flow measures the distance to the stability boundary.
   This extends Lemma lem:cm (the cohort economy cannot amplify without depth).

4. **Theorem C (no-overshoot bound, any signs; proved by induction, verified numerically):**
   If Cbar = |phi eps| (1 + kappa |q| / r) + kappa^2 |q| - (1-a) kappa <= 0, then sup_k |h_k| = kappa.
   Proof: if |x_j| <= kappa for j < k, then |f_j| <= |q| kappa, |d_{k-1}| <= |eps| (1 + |q| kappa / r), so
   |x_k| <= a kappa + |phi eps| (1 + |q| kappa / r) + kappa^2 |q| <= kappa.
   With phi*eps >= 0 and q >= 0 this gives the sandwich C3 > 0 => amplifies => Cbar > 0.

5. **Empirical reading:** the forecasting content comes from the one-period margin C3 moving with the spectral radius.
   Momentum and slow reversion push rho toward 1, inflating the SUMMED response that bounds the adverse excursion
   (guard theorem: |p_T - p_0| <= U sum |h_k|). This is why Part 6 B tests GM = S60/|h0|.

## Paper 1: matching upper bound for every K (closes the open problem)

Class: rates r_i = r_c + Delta s_i, with s in a compact set, min |s_i - s_j| >= gamma > 0, and weights omega_i in [omega_min, omega_max].
Kernel values k_m = sum w_i r_i^m are power sums of the merged measure.
- Centring and rescaling: mu_m = sum_j C(m, j) (-r_c)^{m-j} k_j (Delta-free linear map); t_m = mu_m / Delta^m = sum w_i s_i^m.
- The map (s, omega) -> (t_0, ..., t_{2K-1}) does not depend on Delta. Its Jacobian is a confluent Vandermonde with
  det = prod omega_i * prod_{i<j} (s_i - s_j)^4 != 0, so it is locally bi-Lipschitz on the class.
- Error in t_m = error in mu_m / Delta^m <= C sigma N^{-1/2} Delta^{-(2K-1)} (worst at m = 2K-1).
- Prony on the first 2K kernel values (coordinate-free; computed in centred coordinates for numerical stability)
  therefore has weight error O(sigma N^{-1/2} Delta^{-(2K-1)}) once that quantity is below a constant.
- N = C sigma^2 Delta^{-(4K-2)} suffices, matching Theorem kcohort's lower bound (the Gauss/Gauss-Radau pair lies in the class).
- Kernel from impulse responses: k is a smooth, locally Lipschitz (Delta-free) function of h_0..h_{2K} through the
  closed-loop recursion (h_0 = kappa != 0), so noise passes through with constant factors.
- Numerical check (R_P1_kcohort_upper.json): fitted slopes of N* in Delta: K=2 -5.94, K=3 -10.00, K=4 -13.93, K=5 -18.34
  (theory -6, -10, -14, -18).
- Related literature for the write-up: Batenkov, Goldman & Yomdin (2021), super-resolution of near-colliding point sources;
  Moitra (2015); Li & Liao (2021). Ours is the real-node (decaying-exponential) version, with the Gauss/Radau lower bound.

## Paper 1: capital tables recomputed (recompute_p1_capital.py -> recomputed/R_P1_capital_ledger.json)
- Certified C_det (quad + fee lower bound phi P* 2 sigma z / sup|dH|): 61.41 at delta = 0.05 (old 61.44). Adaptive LB with fee 30.22 (old 30.09).
- Feasible UB (SLSQP-refined generalized eigenvector, L = 240): 64.48 (old 64.56). The bracket is now [61.41, 64.48].
- Ledger: old designs reproduced exactly once the spacing was recovered (pulses every 40 steps, each sold 20 steps later):
  229.13/0.0578, 189.45/0.0308, 157.89/0.0442, 378.82/0.004; eigenvector probes 65.06 (L = 120) and 64.86 (L = 160).
- Still from earlier scripts: the interval-arithmetic RH certificates (64.7423, 63.0368), the SPRT simulation (45.96, 106.53, 155.99, 37.7%),
  the protocol slopes table, and the extended-T floors (0.1376, ...).

## Paper 2: equilibrium section (equilibrium.py -> R_P2_equilibrium.json)
- **Closed form (proved via (I - M)^{-1}; exact to 7e-14 in 3,000 stable draws):** sum_k h_k = S = kt / (m - q kt),
  where kt = kappa + phi eps / r (long-run impact = direct + depth) and m = 1 - a (reversion). For the nonnegative system,
  stable iff m > q kt (det(I - M3) = eta [r (m - kappa q) - phi eps q]). Depth-free case: S = kappa / (m - kappa q).
  Interpretation: cumulative transient risk = long-run impact / (reversion - momentum x long-run impact).
- **Model:** N dealers each supply reversion s_i, so m = m0 + sum s_i, with private value v s_i - c/2 s_i^2. Aggregate tail loss
  Lambda S(m) (guard theorem: worst-case loss ∝ U S); dealers bear a share theta/N each, the rest falls on leveraged users.
  Momentum traders choose q with private value b q - e/2 q^2.
- **E2 under-provision:** with theta < N, m_eq < m_SP and S_eq > S_SP (FOCs; g(m) = kt/(m - q kt)^2 is decreasing in m).
- **E3 thin books:** m - m0 = N v/c + theta Lam g(m)/c, so dm/dN = (v/c) / (1 - theta Lam g'(m)/c) > 0. Fewer dealers means
  less reversion and higher S. (Numerical: S_eq goes 27.9 -> 6.8 as N goes 1 -> 40; the planner's S is 1.5-2.7x lower.)
- **E4 the Pigouvian price is identified:** the first best is implemented by a rebate per unit of reversion
  tau* = (1 - theta/N) Lam kt/(m - q kt)^2 = (1 - theta/N) Lam S^2 / kt. It uses only S and kt, which are identified from public
  data without identifying algorithms (Props invariance/bridge). The guard statistic is the policy price.
- **E5 momentum over-provision:** private q = b/e exceeds the planner's q (example: 0.015 vs 0.0062).
- Testable predictions: (i) S is higher in thin books; (ii) S/C3 forecasts tail size where m - q kt is small (thin) and not where
  it is large (deep). (ii) matches X6/Y6/Y8; (i) can be measured from Part 6 blocks (S60 by group) with one extra cell.

## Paper 1: value-of-disclosure theorem (disclosure_value.py -> R_P1_disclosure_value.json)
- **Theorem:** to resolve K cohorts with rate spacing Delta, price-only needs N_p ≍ sigma^2 Delta^{-(4K-2)} (kcohort lower bound plus
  the Prony upper bound). With class-tagged flow, each class is a single-exponential problem whose Fisher information does not
  depend on Delta, so the weights need N_t ≍ sigma_f^2 (Delta-free) and the rates, to precision Delta, need N_t ≍ sigma_f^2 Delta^{-2}.
  Value of disclosure: N_p / N_t ≍ (sigma/sigma_f)^2 Delta^{-(4K-2)} for weights and Delta^{-(4K-4)} for rates.
- Numerical check (same noise and lags for both observers, K = 2, r_c = 0.95): price slope -6.08, ratio slope -4.34 (theory -6, -4).
- Calibrated to the real tagged rates (X9, 5-minute data): see the calibrated block in the JSON.
  BTC: Delta = 0.0097 gives N_price ≈ 5,974 days vs N_tagged ≈ 18 days (ratio ≈ 333). ETH: Delta = 0.0179 gives a ratio ≈ 19.
  Cross-check with the real noise: X9's tagged rate CI width for BTC (0.0064 with 48 days) implies about 21 days to resolve Delta/4,
  so price-only would need about 7,000 days (~19 years). Headline: the published long/short ratios are worth ~16-19 years of prices
  for this question.

## Paper 1: general memory-kernel theorem (general_kernel.py -> R_P1_general_kernel.json)
- Setup: completely monotone kernel k_m = int r^m dmu(r), mu on [0, rho], rho < 1 (any mixture of exponential memories).
- Lower bound: let mu_A, mu_B be the n-point Gauss and Gauss-Radau rules mapped to [0, rho]; nu = mu_A - mu_B annihilates
  polynomials of degree <= 2n-2. Generating function: G(z) = sum_m Dk_m z^m = int 1/(1 - r z) dnu = z^{2n-1} int r^{2n-1}/(1 - r z) dnu,
  so ||Dk||_2 <= 2 rho^{2n-1}/(1 - rho) (Parseval). W1(mu_A, mu_B) ≍ 1/n (numerically 0.398 at n = 10, rho = 0.9; about 0.4 rho/n).
  Le Cam: separating them needs N >= c sigma^2 (1 - rho)^2 rho^{-2(2n-1)}. In terms of accuracy w = W1: N >= exp(c(rho)/w).
- Numerical: ||Dk||_2 falls by 0.249 per atom (rho = 0.9) and 0.575 (rho = 0.99); W1 ~ 0.4/n; low moments agree to 1e-16.
- Upper bound: moment-based estimators reach W1 = O(1/log N) (cite Kong & Valiant 2017; Wu & Yang 2020), so the rate is
  logarithmic: identification of general memory is exponentially costly. Exponential-memory cohorts (polynomial Delta^{-(4K-2)}) are the
  OPTIMISTIC case; the barrier is not an artefact of the parametric model, and the general case is worse.

## Paper 1: remaining recomputations (recompute_p1_protocols.py, recompute_p1_sprt.py)
- Resolution floors reproduce exactly: T = 3, 4, 10, 20, 100 give 0.2028, 0.1376, 0.0973, 0.0914, 0.0905.
- Disclosure-contracts table reproduces exactly in closed form: 12.70, 15.52 (V >= 5.590), 271/4,305.25, 58/923.875, 12/193.625, 11/177.75.
- Protocols A (single pulse) and B (capped pulses) reproduce exactly (6,985.91 / 921.73 / 146.73 / 31.45; 7,035.75 / 923.88 / 146.00 / 34.88).
  C (SPRT, 2,000 runs) re-implemented: 3,585 / 500 / 94.3 / 29.9 (old 3,515 / 469 / 88.2 / 27.3). Savings vs B: 49%, 46%, 35%, 14%.
  D re-implemented (generalized-eigenvector cycle of length T+1, max trade 3.75): 2,633 / 354 / 57.5 / 13.6. It is cheaper than the old D
  (a different and better trajectory). Slopes: A -3.90, B -3.84, C -3.47 (0.12 point has 1.7 pulses), D -3.81.
- SPRT capital (optimal probe in M equal-information copies, 20,000 runs, M = 10): mean loss 39.5 (between the adaptive bound 29.94
  and the deterministic 61.14), p95 91.7, p99 128.4, insolvency 37.5% if funded at the mean (old 45.96 / 106.53 / 155.99 / 37.7%).
- Still from earlier scripts: only the interval-arithmetic RH certificates (64.7423, 63.0368); label them as such or drop that column.

# RESULTS OF PARTS 6-8 (Oct 19, 2026)
## Part 6 (fresh days; prereg 65acda36...; unlocks 1; 1,137 fresh symbol-days valid; thin test 13,428 h, 39 dates)
- A PASS: thin (20 symbols) dR2 +1.583 pts, 97.5% CI [0.588, 3.237], CW t 9.46, with the 4 impact controls in the baseline;
  baseline R2 0.185; AUC 0.810 -> 0.812, dAUC CI [-0.003, 0.006] (n.s.); coef +68.0.
- B FAIL: theta = 0.25 (training TLR 349.1 vs vol 354.8); test log TLR amp_vol - vol = -0.0172, 97.5% CI [-0.045, 0.011]
  (91% of bootstrap draws < 0). The pure guard is much worse than vol (+0.404 [0.285, 0.525]), the peak guard worse (+0.165),
  static worse (+0.313); summed vs peak +0.239. Test TLR: vol 348.6, amp_vol 342.7, peak 411.4, static 476.8, summed 522.2.
  Training Spearman of risk with MAE: vol 0.513, amp_vol 0.518, peak 0.428, summed 0.414.
- C FAIL: 5/30 pass (16.7%). (i) width ratio > 10 in 30/30 (27.6-124.0); (ii) price-only width > 0.25 in 30/30 (0.645-0.99);
  (iii) M0 CI excludes 0 in only 5/30 (ACH, API3, OGN, ZEN, DASH).
- Secondary, Paper 2 (Holm): C3_flow (no depth) +1.747 [0.725, 3.393] p ~ 0  => the depth-free statistic WORKS on Binance, so the
  Bybit failure is venue-specific, not statistic-specific. Reversion +1.442 [0.679, 2.621]; momentum +0.422 [0.000, 1.063] (Holm 2e-5);
  depth +0.323 [0.092, 0.639]; UNIT-FREE gain_multiple +0.488 [0.252, 0.851]; UNIT-FREE log_halflife +0.619 [0.351, 1.031]
  (dAUC CI [0.0003, 0.0026]); mid C3 +0.055 [-0.047, 0.239] (CW Holm 0.038 but the R2 CI includes 0); guard comparisons Holm 1.0.
- Secondary, Paper 1: tagged position features -> MAE: dR2 -0.193 [-0.991, 0.825], dAUC [-0.012, -0.003] (worse); CW p 0.0085.
  No forecasting value. Classes differ (top position vs all accounts) in 11/30 symbols.
- Z8 (equilibrium, training only): S60 thin 54.1 vs mid 53.2 (diff CI [-1.32, 3.45]) -> NOT supported; gain multiple slightly LOWER in
  thin (34.5 vs 35.8, CI [-2.20, -0.27]); kappa higher in thin (1.65 vs 1.52); C3 lower in thin. Thin-vs-mid depth is not dealer count.
## Part 7 (Bybit; 14 of 20 coins available; test 10,764 h): FAIL. C3_flow dR2 -0.0000 [-0.0011, 0.0011] pts, CW p 0.50; momentum and
  reversion n.s. (training momentum coefficient -130 vs +110 on Binance). theta = 0, so amp_vol = vol. Pure guard +0.484 [0.251, 0.662]
  worse than vol; peak +0.363; static +0.407. Hypothesis (post hoc, untested): sparse Bybit trades -> last-trade minute bars (bid-ask
  bounce) instead of klines; differing participants.
## Part 8 (spot panel reproduced): 768 units, 6,634,752 transitions. forward Q 0.0081424 [0.0072965, 0.0089882] (87.4% > 0);
  observed 0.0003733 [0.0002351, 0.0005116] (62.4%); raw -0.0001555 [-0.0003732, 0.0000622] (49.2%); observed Q30 0.000258
  [0.0001415, 0.0003745]; J11 observed 0.92035 [0.91604, 0.92466] vs mechanical 0.93548; placebo Q 0.0000016 [-0.000002, 0.0000052],
  placebo J11 0.93509. Fee events (date-clustered, +/-20 days, 8 pairs): volume on +0.945 (se 0.074), off-event reversal 1.599 (0.080),
  pooled 1.272; Q: on +0.00058 [-0.00007, 0.00123] p 0.078; off -0.00091 [-0.00213, 0.00031] p 0.14; pooled -0.00016 [-0.00087, 0.00055] p 0.65.
## Part 9 (vol benchmark; prereg 71983f1a...; unlocks 1; 1,161 fresh symbol-days, days 6/20): PASS.
 C3 +2.787 [1.425, 4.944] pts, dAUC [0.0019, 0.0080], CW t 12.59, base R2 0.186 -> 0.214. S60 +2.098 [1.165, 3.597]; reversion +2.451; momentum +0.731;
 gain_multiple +0.563; log_halflife +0.806; C3_flow +2.989; mid C3 +0.316 [0.108, 0.635] (significant). Vol benchmarks over the Part 6 baseline: -0.757 [-3.38, 2.10].
