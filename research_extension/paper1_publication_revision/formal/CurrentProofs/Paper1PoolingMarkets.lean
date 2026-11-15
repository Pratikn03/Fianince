import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Algebra.Order.Group.Nat
import Mathlib.Tactic.Push

/-!
# Paper 1: pooling markets (counting steps)

With `K` algorithms of common memory trading in `D` markets with market-specific weights, the rescaled moments of
orders `0, …, l` in every market are `D (l + 1)` equations in the `K (D + 1)` unknowns (nodes and weights).
The exponent of the cross-market theorem (core `thm:pool`) is `2 l*` with `l* = K - 1 + q*`, `q*` the least `q` with `K ≤ D q`.

* `p1_pool_rows_lt`: below `l*`, there are fewer equations than unknowns, so the moment map up to that order is not
  injective near any configuration (the lower-bound step).
* `p1_pool_rows_ge`: at `l*` there are at least as many equations as unknowns (necessary for the upper bound).
* `p1_pool_single_market`: with one market, `l* = 2K - 1`, the exponent `4K - 2` of the single-market theorem.
* `p1_pool_many_markets`: with `D ≥ K` markets, `l* = K`, exponent `2K`.
Here `⌈K / D⌉` is written `(K + D - 1) / D`.
-/

namespace CurrentMM

/-- Write the order as `l + 1 = K + q`. If `D q < K`, the moments up to order `l` in all `D` markets are fewer
equations than the `K (D + 1)` unknowns: the moment map is not injective near any configuration. -/
theorem p1_pool_rows_lt (K D l q : ℕ) (hq : D * q < K) (hl : l + 1 ≤ K + q) :
    D * (l + 1) < K * (D + 1) := by
  have h1 : D * (l + 1) ≤ D * (K + q) := Nat.mul_le_mul_left D hl
  nlinarith [h1, hq]

/-- If `K ≤ D q`, the moments up to order `K - 1 + q` give at least as many equations as unknowns. -/
theorem p1_pool_rows_ge (K D q : ℕ) (hq : K ≤ D * q) : K * (D + 1) ≤ D * (K + q) := by
  nlinarith [hq]

/-- One market (`D = 1`): every `q < K` leaves too few equations, so the first order that can suffice is
`l + 1 = 2K`, i.e. `l* = 2K - 1` and the exponent `2 l* = 4K - 2` of the single-market theorem. -/
theorem p1_pool_single_market (K q : ℕ) (hq : q < K) (l : ℕ) (hl : l + 1 ≤ K + q) :
    1 * (l + 1) < K * (1 + 1) :=
  p1_pool_rows_lt K 1 l q (by simpa using hq) hl

/-- At least `K` markets: `q = 1` already gives enough equations, so `l* = K` and the exponent is `2K`. -/
theorem p1_pool_many_markets (K D : ℕ) (hDK : K ≤ D) : K * (D + 1) ≤ D * (K + 1) :=
  p1_pool_rows_ge K D 1 (by simpa using hDK)

end CurrentMM
