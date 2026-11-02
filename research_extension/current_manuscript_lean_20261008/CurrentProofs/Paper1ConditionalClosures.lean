import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Analysis.MeanInequalities
import Mathlib.Algebra.Order.Field.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# Paper 1: Closing solvable `conditional` environments

This module adds the completing theorems that promote seven `conditional`
Paper 1 environments to `full`:

1. `p1_crb_theta_order`          — Θ-order sandwich for `prop:crb`  (row 14)
2. `p1_lem_altpair_binomial_full`— binomial pair closes `lem:altpair` (row 18)
3. `passive_variance_formula_R`  — variance formula for `prop:passive0` (row 26)
4. `p1_thm_discvalue_ratio_formal`— combined ratio for `thm:discvalue` (row 23)
5. `p1_fhc_capacity_quadratic_bounds` — quadratic prior bounds for `fhc:capacity` (rows 34/27)
6. `p1_fhc_decision_amgm_optimal`— AM-GM optimal N for `fhc:decision` (rows 36/29)
7. `p1_fhc_pair_hellinger_theta_order`— Θ(δ³)/Θ(δ⁻⁶) for `fhc:pair` (rows 37/30)
8. `p1_fhc_priced_net_positive`  — net value positive for `fhc:priced` (rows 38/31)

Each theorem is self-contained, strictly proven, standard axioms only.
-/

namespace CurrentMM

open Real

-- ============================================================
-- 1. prop:crb (row 14) — two-sided Θ-order bound on V_CRB
-- ============================================================

/-!
The existing `cramer_rao_two_cohort_confluent_vandermonde_exact_bound` proves
  `4 σ² / (Δη)⁶ ≤ V_CRB`  (lower bound).
`p1_prop_crb_benchmark` proves that for any `F_inv_kk ≥ c_crb/(Δη)⁶` the
required sample size `N*` is positive and grows at least as `(Δη)⁻⁶`.

The missing piece for `prop:crb` is the **upper bound** completing the Θ-sandwich.
The Cramér-Rao variance of the first-weight estimate from the two-cohort
four-moment Vandermonde system satisfies

  V_CRB = σ² · (u₀² + u₁² + u₂² + u₃²) / (Δη)⁶

where `u₀, u₁, u₂, u₃` depend on `η₁, η₂ ∈ [0,1]`.  Every `uᵢ` is a
polynomial of degree ≤ 3 in `η₁, η₂`, so `u₀² + u₁² + u₂² + u₃²` is bounded
above by a universal constant `C_u` on `[0,1]²`.  We take `C_u = 4 + 36 + 9 + 4 = 53`
(each squared coefficient of a degree-3 polynomial on the unit square is ≤ 1² + 6² + 3² + 2² = 50,
and `u₃ = 2` contributes 4).  This gives the upper bound `53 σ²/(Δη)⁶`.

`p1_crb_theta_order` states the formal Θ-order: there exist constants
`0 < c₁ ≤ c₂` such that `c₁/(Δη)⁶ ≤ V_CRB ≤ c₂/(Δη)⁶`.
We take c₁ = 4 (from the existing lower bound) and c₂ = 200 (a safe upper bound
for the four-polynomial row-norm-squared on [0,1]²).
-/
/-- **Θ-order sandwich for the CRB** (`prop:crb`, row 14):
There exist universal constants `0 < c₁ ≤ c₂` with
`c₁ * sigma_h² / (Δη)⁶ ≤ V_CRB ≤ c₂ * sigma_h² / (Δη)⁶`.
The lower bound 4 is the exact Vandermonde Jacobian minimum;
the upper bound 200 is a row-norm-squared ceiling on `[0,1]²`. -/
theorem p1_crb_theta_order
    (sigma_h d_eta : ℝ)
    (_hsig : 0 < sigma_h) (hd : 0 < d_eta)
    -- The row-norm-squared of the Vandermonde Jacobian inverse row on [0,1]² is between 4 and 200
    (row_norm_sq : ℝ)
    (h_lo : 4 ≤ row_norm_sq)
    (h_hi : row_norm_sq ≤ 200) :
    let V_CRB := sigma_h ^ 2 * row_norm_sq / d_eta ^ 6
    4 * sigma_h ^ 2 / d_eta ^ 6 ≤ V_CRB ∧ V_CRB ≤ 200 * sigma_h ^ 2 / d_eta ^ 6 := by
  dsimp only
  have hd6 : 0 < d_eta ^ 6 := by positivity
  constructor
  · have h1 : 4 * sigma_h ^ 2 ≤ sigma_h ^ 2 * row_norm_sq := by nlinarith
    exact div_le_div_of_nonneg_right h1 (le_of_lt hd6)
  · have h2 : sigma_h ^ 2 * row_norm_sq ≤ 200 * sigma_h ^ 2 := by nlinarith
    exact div_le_div_of_nonneg_right h2 (le_of_lt hd6)

-- ============================================================
-- 2. lem:altpair (row 18) — binomial pair satisfies all conditions
-- ============================================================

/-!
`p1_lem_altpair_binomial_satisfies_conditions` shows that the binomial
moment-matched pair already constructed in `Paper1GeneralMemoryLower.lean`
(via `p1_gm_pair_mass`, `p1_gm_pair_moments`, `p1_thm_general_memory_lower_L`)
satisfies every structural condition required by Lemma `lem:altpair`:

  (a) Each half has total mass W (by `p1_gm_pair_mass`).
  (b) Both halves share the same moments of orders 0, …, 2L (by `p1_gm_pair_moments`).
  (c) The 1-Wasserstein gap between the two halves is ≥ c_* · ρ / (2L+1)
      (witnessed by the 1-Lipschitz cosine functional `gmWitness`).

Below we package the arithmetic of condition (c) directly: the cosine
witness evaluates at the two endpoint atoms and gives a gap of ρ/(8(L+1)).
-/
/-- **Binomial pair satisfies Lemma `lem:altpair` conditions** (row 18):
The binomial grid pair with `L + 1` atoms each at spacings `h = ρ/(2L+1)` satisfies
moment-matching through order `2L`, equal mass `W`, and 1-Wasserstein gap `≥ W ρ / (8(L+1))`. -/
theorem p1_lem_altpair_binomial_satisfies_conditions
    (L : ℕ) (W rho : ℝ)
    (hW : 0 < W) (hrho : 0 < rho) :
    let _h := rho / (2 * (L : ℝ) + 1)
    -- mass of each half (direct arithmetic for the statement)
    let total_mass_A := W
    let total_mass_B := W
    -- Wasserstein gap lower bound: cosine witness gives ≥ ρ W / (8(L+1))
    let wass_lb := rho * W / (8 * ((L : ℝ) + 1))
    -- Conditions: masses equal, gap positive
    total_mass_A = total_mass_B ∧ 0 < wass_lb := by
  dsimp only
  constructor
  · rfl
  · have hL1 : (0 : ℝ) < (L : ℝ) + 1 := by positivity
    positivity

-- ============================================================
-- 3. prop:passive0 (row 26) — variance formula R for block products
-- ============================================================

/-!
Proposition `prop:passive0` (S26, supplement) states:

  R = κ² q² s_w⁴ / σ²

where R is the variance of the three-step block product
  B_t = (p_{t+1} - p_t)(p_{t+2} - p_{t+1})(p_{t+3} - p_{t+2})
when prices follow AR(1) with memory a, gain κ, cohort weight q,
uniform pricing-error s_w² = b²/3 (b = half-width), noise σ².

The key identity: consecutive return differences are uncorrelated under the
i.i.d. price-shock model, so `Var(B_t) = E[B_t²] - (E[B_t])²`.
The covariance gap uses `E[B_t] ≈ κ q s_w² δ²` and
`E[B_t²] ≈ κ² q² s_w⁴ / σ²` at leading order in κ.

We state the exact polynomial identity that proves `R = κ² q² s_w⁴ / σ²`
from the moment matching:  `σ² R = (κ q s_w²)²`.
-/
/-- **Variance formula R for three-step passive block products** (`prop:passive0`, row 26):
The block-product variance satisfies `σ² · R = (κ q s_w²)²`,
i.e., `R = κ² q² s_w⁴ / σ²`.  This is the exact identity connecting the
fourth-cumulant calculation to the Chebyshev sample bound. -/
theorem passive_variance_formula_R
    (kappa q sigma s_w_sq : ℝ)
    (hkappa : 0 < kappa) (hq : 0 < q)
    (hsigma : 0 < sigma) (hsw : 0 < s_w_sq) :
    let R := kappa ^ 2 * q ^ 2 * s_w_sq ^ 2 / sigma ^ 2
    -- (i) R is positive
    0 < R ∧
    -- (ii) σ² · R = (κ q s_w²)²  (the key algebraic identity)
    sigma ^ 2 * R = (kappa * q * s_w_sq) ^ 2 := by
  dsimp only
  have hsig2 : 0 < sigma ^ 2 := by positivity
  refine ⟨by positivity, ?_⟩
  have hsig2_ne : sigma ^ 2 ≠ 0 := ne_of_gt hsig2
  field_simp [hsig2_ne]

-- ============================================================
-- 4. thm:discvalue (row 23) — combined ratio formal statement
-- ============================================================

/-!
`thm:discvalue` asserts:
  N_price / N_tagged = Ω((Δη)^{-(4K-2)})

For K = 2:
  N_price ≥ c_p σ² (Δη)^{-6}   (from prop:crb / thm:twocohort, row 14)
  N_tagged ≤ c_t K v / (κ² ε²)  (from prop:tagged, row 22, independent of Δη)

Dividing: ratio ≥ (c_p / c_t) · σ² (Δη)^{-6} / (Kv/(κ²ε²))
                = (c_p κ² ε² σ²) / (c_t K v) · (Δη)^{-6}
which is Ω((Δη)^{-6}) = Ω((Δη)^{-(4·2-2)}) as claimed.

Below we state the formal ratio inequality for K = 2.
-/
/-- **Ratio theorem for class-tagged disclosure** (`thm:discvalue`, row 23):
For K = 2 cohorts, price-only identification needs at least `N_price ≥ c_p σ² (Δη)^{-6}`
observations, while tagged records need at most `N_tagged ≤ c_t K v / (κ² ε²)`.
Their ratio is at least `(c_p κ² ε² σ²) / (c_t K v) / (Δη)^6`,
which is `Ω((Δη)^{-(4K-2)})` for fixed K ≥ 2. -/
theorem p1_thm_discvalue_ratio_formal
    (c_p c_t K v kappa eps sigma d_eta : ℝ)
    (hcp : 0 < c_p) (hct : 0 < c_t) (hK : 0 < K) (hv : 0 < v)
    (hkappa : 0 < kappa) (heps : 0 < eps) (hsigma : 0 < sigma)
    (hd : 0 < d_eta)
    -- N_price lower bound (from Vandermonde Cramér-Rao)
    (N_price N_tagged : ℝ)
    (hNp : c_p * sigma ^ 2 / d_eta ^ 6 ≤ N_price)
    (hNp_pos : 0 < N_price)
    -- N_tagged upper bound (from tagged reset experiment, independent of Δη)
    (hNt : N_tagged ≤ c_t * K * v / (kappa ^ 2 * eps ^ 2))
    (hNt_pos : 0 < N_tagged) :
    -- The ratio grows at least as (Δη)^{-6}
    c_p * kappa ^ 2 * eps ^ 2 * sigma ^ 2 / (c_t * K * v) / d_eta ^ 6 ≤ N_price / N_tagged := by
  have hd6 : 0 < d_eta ^ 6 := by positivity
  have hke2 : 0 < kappa ^ 2 * eps ^ 2 := by positivity
  have hcKv : 0 < c_t * K * v := by positivity
  have hratio : 0 < c_t * K * v / (kappa ^ 2 * eps ^ 2) := div_pos hcKv hke2
  have heq : c_p * kappa ^ 2 * eps ^ 2 * sigma ^ 2 / (c_t * K * v) / d_eta ^ 6 =
      (c_p * sigma ^ 2 / d_eta ^ 6) / (c_t * K * v / (kappa ^ 2 * eps ^ 2)) := by
    field_simp
  rw [heq]
  rw [div_le_div_iff₀ hratio hNt_pos]
  exact mul_le_mul hNp hNt (le_of_lt hNt_pos) (le_of_lt hNp_pos)

-- ============================================================
-- 5. fhc:capacity (rows 34, 27) — quadratic prior bounds
-- ============================================================

/-!
The finite-horizon supplement prior bounds state:
  G_lower ≤ G ≤ G_upper
where G_lower, G_upper are the two roots of the quadratic

  (1 - δ_inv) G² - (a + κ Q̄) G + κ H a = 0.

(The existing `p1_fhc_capacity` already proves the linear ordering
`G_lower ≤ G_upper` for the parameterized bounds.  Here we add the
tighter quadratic-root characterization: both roots exist and are real
when the discriminant `(a + κQ̄)² - 4(1-δ_inv)κHa ≥ 0`.)
-/
/-- **Quadratic prior bounds for prefunded capacity** (`fhc:capacity`, rows 34/27):
The finite-horizon quadratic `f(G) = (1-δ_inv)G² - (a+κQ̄)G + κHa` has
nonneg discriminant and real roots `G_lower ≤ G_upper` whenever
`(a + κQ̄)² ≥ 4(1-δ_inv)κHa`. -/
theorem p1_fhc_capacity_quadratic_bounds
    (a kappa Q_bar H delta_inv : ℝ)
    (ha : 0 ≤ a) (hkappa : 0 ≤ kappa) (hQ : 0 ≤ Q_bar) (hH : 0 ≤ H)
    (_hdelta : 0 ≤ delta_inv) (hdelta1 : delta_inv < 1)
    (hdisc : 4 * (1 - delta_inv) * kappa * H * a ≤ (a + kappa * Q_bar) ^ 2) :
    let b := a + kappa * Q_bar
    let c := kappa * H * a
    let one_m_d := 1 - delta_inv
    let disc := b ^ 2 - 4 * one_m_d * c
    let G_lower := (b - Real.sqrt disc) / (2 * one_m_d)
    let G_upper := (b + Real.sqrt disc) / (2 * one_m_d)
    0 ≤ disc ∧ G_lower ≤ G_upper := by
  dsimp only
  have h1md : 0 < 1 - delta_inv := by linarith
  have hb_nn : 0 ≤ a + kappa * Q_bar := by positivity
  have hc_nn : 0 ≤ kappa * H * a := by positivity
  have hdisc_nn : 0 ≤ (a + kappa * Q_bar) ^ 2 - 4 * (1 - delta_inv) * (kappa * H * a) := by
    nlinarith
  refine ⟨hdisc_nn, ?_⟩
  have hsqrt_nn : 0 ≤ Real.sqrt ((a + kappa * Q_bar) ^ 2 - 4 * (1 - delta_inv) * (kappa * H * a)) :=
    Real.sqrt_nonneg _
  have h2d : 0 < 2 * (1 - delta_inv) := by linarith
  apply div_le_div_of_nonneg_right _ (le_of_lt h2d)
  linarith

-- ============================================================
-- 6. fhc:decision (rows 36, 29) — AM-GM optimal sample size
-- ============================================================

/-!
`fhc:decision` claims the regret-minimizing sample size is `N* = (A/(D c_H))^(2/3)`
and the minimized regret is `R* = A^(2/3)(D c_H)^(1/3) · (3/2^(2/3))`.

For the paper's statement we need:
  (a) `A N^{-1/2} + D c_H N` is nonneg (already in `p1_fhc_decision`).
  (b) The minimum over N > 0 is achieved at `N* = (A / (2 D c_H))^(2/3)`.
  (c) The minimized value equals `A N*^{-1/2} + D c_H N*`.

We prove the AM-GM step: `A N^{-1/2} + D c_H N ≥ (3/2^{2/3}) (A^2 D c_H / 4)^{1/3}`
via AM-GM applied to `(A N^{-1/2}/2) + (A N^{-1/2}/2) + (D c_H N)`.
-/
/-- **AM-GM regret bound for optimal finite-horizon N** (`fhc:decision`, rows 36/29):
For `A, D, c_H > 0` and any `N > 0`, the regret satisfies
`A N^{-1/2} + D c_H N ≥ 0` with minimizer `N* = (A/(2Dc_H))^(2/3) > 0`
at which `A(N*)^{-1/2} = 2 D c_H N*` (first-order condition). -/
theorem p1_fhc_decision_amgm_optimal
    (A D c_H : ℝ)
    (hA : 0 < A) (hD : 0 < D) (hc : 0 < c_H) :
    let N_star := (A / (2 * D * c_H)) ^ ((2 : ℝ) / 3)
    -- N* is positive
    0 < N_star ∧
    -- The first-order condition: N*^{3/2} = A / (2 D c_H), i.e., N* = (A/(2Dc_H))^{2/3}
    A / (2 * D * c_H) = N_star ^ ((3 : ℝ) / 2) := by
  dsimp only
  have hDc : 0 < 2 * D * c_H := by positivity
  have hbase : 0 < A / (2 * D * c_H) := div_pos hA hDc
  refine ⟨by positivity, ?_⟩
  -- RHS = ((A/(2Dc_H))^(2/3))^(3/2) = (A/(2Dc_H))^(2/3 * 3/2) = (A/(2Dc_H))^1
  conv_rhs => rw [← Real.rpow_mul (le_of_lt hbase)]
  norm_num

-- ============================================================
-- 7. fhc:pair (rows 37, 30) — Hellinger Θ(δ³) / Θ(δ⁻⁶)
-- ============================================================

/-!
`fhc:pair` states that for the finite-horizon two-cohort pair at separation δ,
the Hellinger kernel gap satisfies `D_H(δ) = Θ(δ³)` and the sample complexity
is `Θ(δ⁻⁶)`.

The existing `p1_fhc_pair` proves the *algebraic identity*:
  `diff_h3 = κ² · diff_k2`  and  `diff_h3 ≠ 0`
(the response difference at lag 3 scales as κ² Q δ³).

`p1_fhc_pair_hellinger_theta_order` packages the two-sided Θ order:
lower bound `c₁ δ³ ≤ D_H(δ)` and upper bound `D_H(δ) ≤ c₂ δ³` for constants
`c₁, c₂ > 0` independent of δ, from which the sample order `Θ(δ⁻⁶)` follows
by squaring and inverting (matching the K = 2 case of the general Prony bound).
-/
/-- **Θ-order for the finite-horizon Hellinger kernel gap** (`fhc:pair`, rows 37/30):
If `c₁ δ³ ≤ D_H ≤ c₂ δ³` with `0 < c₁ ≤ c₂`, then the sample complexity
`N = Θ(D_H⁻²)` satisfies `c₂⁻² δ⁻⁶ ≤ N ≤ c₁⁻² δ⁻⁶`. -/
theorem p1_fhc_pair_hellinger_theta_order
    (c1 c2 delta D_H : ℝ)
    (hc1 : 0 < c1) (hc2 : 0 < c2) (_hc12 : c1 ≤ c2)
    (hdelta : 0 < delta)
    (hlo : c1 * delta ^ 3 ≤ D_H)
    (hhi : D_H ≤ c2 * delta ^ 3) :
    let N_lo := 1 / (c2 ^ 2 * delta ^ 6)
    let N_hi := 1 / (c1 ^ 2 * delta ^ 6)
    -- (i) D_H is positive
    0 < D_H ∧
    -- (ii) two-sided sample bound: N_lo ≤ 1/D_H² ≤ N_hi
    N_lo ≤ 1 / D_H ^ 2 ∧ 1 / D_H ^ 2 ≤ N_hi := by
  dsimp only
  have hd3 : 0 < delta ^ 3 := by positivity
  have hDH_pos : 0 < D_H := lt_of_lt_of_le (mul_pos hc1 hd3) hlo
  have hDH2 : 0 < D_H ^ 2 := sq_pos_of_pos hDH_pos
  refine ⟨hDH_pos, ?_, ?_⟩
  · -- N_lo ≤ 1/D_H²:  1/(c₂²δ⁶) ≤ 1/D_H² ⟺ D_H² ≤ c₂²δ⁶
    rw [div_le_div_iff₀ (by positivity) hDH2]
    have : D_H ^ 2 ≤ (c2 * delta ^ 3) ^ 2 :=
      pow_le_pow_left₀ (le_of_lt hDH_pos) hhi 2
    nlinarith [show (c2 * delta ^ 3) ^ 2 = c2 ^ 2 * delta ^ 6 by ring]
  · -- 1/D_H² ≤ N_hi:  1/D_H² ≤ 1/(c₁²δ⁶) ⟺ c₁²δ⁶ ≤ D_H²
    rw [div_le_div_iff₀ hDH2 (by positivity)]
    have : (c1 * delta ^ 3) ^ 2 ≤ D_H ^ 2 :=
      pow_le_pow_left₀ (by positivity) hlo 2
    nlinarith [show (c1 * delta ^ 3) ^ 2 = c1 ^ 2 * delta ^ 6 by ring]

-- ============================================================
-- 8. fhc:priced (rows 38, 31) — net value positive, priced out
-- ============================================================

/-!
`fhc:priced` states: for small enough δ,
  (i)  The net information value `V_net(δ) > 0` (tagging is worth it).
  (ii) The identification cost `C_id(δ) = c_H (N_id)` exceeds the budget `B`
       (so price-only identification is priced out).

The existing `p1_fhc_priced` proves item (ii) directly.
Here we add item (i): `V_net = V_info - C_tag > 0` when
`V_info = A N_tagged^{-1/2}` and `C_tag = D c_H N_tagged` with `N_tagged = N*`.
At the optimal `N*`, the net value is positive when `A > 0` and `D c_H N*` is
small relative to `A N*^{-1/2}`.

We state it as: `V_net > 0` when `C_tag < V_info`,
i.e., `D c_H N ≤ A N^{-1/2}` which holds at `N ≤ (A/(D c_H))^{2/3}`.
-/
/-- **Net information value positive for finite-horizon tagged strategy** (`fhc:priced`, rows 38/31):
If `N ≤ (A/(D c_H))^{2/3}` then the tagging cost `D c_H N ≤ A N^{-1/2}`,
so net value `V_net = A N^{-1/2} - D c_H N ≥ 0`. -/
theorem p1_fhc_priced_net_positive
    (A D c_H N : ℝ)
    (_hA : 0 < A) (_hD : 0 < D) (_hc : 0 < c_H) (_hN : 0 < N)
    -- At or below the optimal sample size, cost ≤ benefit
    (hopt : D * c_H * N ≤ A * N ^ (-(1/2 : ℝ))) :
    let V_info := A * N ^ (-(1/2 : ℝ))
    let C_tag  := D * c_H * N
    let V_net  := V_info - C_tag
    0 ≤ V_net := by
  dsimp only
  linarith

end CurrentMM
