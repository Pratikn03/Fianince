import Mathlib

/-!
# Paper 1, 21 November 2026: the surveillance paradox (Theorem `n:paradox`)

A group chooses its memory distance `D ∈ [0, D0]` to its neighbour and pays `k (D0 - D)² + L π(c N Dⁿ)`.
The lemmas below are the deterministic steps of the two-sided bound on the optimal distance:
`2 k² D0² ≤ D^(n-2) · L² c N 2ⁿ` and `D^(n-2) · L² β² c N ≤ 4 k² D0²`.
The probabilistic inputs (unbiasedness `π ≥ α`, Pinsker `π - α ≤ √(J/2)`, the power envelope
`π - α ≥ β √J` below `J̄`) enter as hypotheses on real numbers.
-/
namespace Paper1Revision6

/-- Moving the distance from `D` to `0` changes the distortion cost by at most `2 k D0 D` and at most `k D0²`. -/
theorem compare_zero (k D0 D : ℝ) (hk : 0 ≤ k) (hD : 0 ≤ D) (hDD : D ≤ D0) :
    k * (D0 - 0) ^ 2 - k * (D0 - D) ^ 2 ≤ 2 * k * D0 * D ∧
    k * (D0 - 0) ^ 2 - k * (D0 - D) ^ 2 ≤ k * D0 ^ 2 := by
  constructor <;> nlinarith [mul_nonneg hk (mul_nonneg hD hD)]

/-- Upper bound: if `L β √(c N Dⁿ) ≤ 2 k D0 D` with `D > 0` and `n ≥ 2`, then `D^(n-2) L² β² c N ≤ 4 k² D0²`. -/
theorem paradox_upper (L β c N k D0 D : ℝ) (n : ℕ) (hn : 2 ≤ n) (hL : 0 ≤ L) (hβ : 0 ≤ β)
    (hc : 0 ≤ c) (hN : 0 ≤ N) (hD : 0 < D) (hk : 0 ≤ k) (hD0 : 0 ≤ D0)
    (h : L * β * Real.sqrt (c * N * D ^ n) ≤ 2 * k * D0 * D) :
    D ^ (n - 2) * (L ^ 2 * β ^ 2 * c * N) ≤ 4 * k ^ 2 * D0 ^ 2 := by
  have hJ : 0 ≤ c * N * D ^ n := by positivity
  have hlhs : 0 ≤ L * β * Real.sqrt (c * N * D ^ n) := by positivity
  have hsq : (L * β * Real.sqrt (c * N * D ^ n)) ^ 2 ≤ (2 * k * D0 * D) ^ 2 :=
    pow_le_pow_left₀ hlhs h 2
  have e1 : (L * β * Real.sqrt (c * N * D ^ n)) ^ 2 = L ^ 2 * β ^ 2 * (c * N * D ^ n) := by
    rw [mul_pow, mul_pow, Real.sq_sqrt hJ]
  have e2 : D ^ n = D ^ (n - 2) * D ^ 2 := by
    rw [← pow_add]; congr 1; omega
  rw [e1, e2] at hsq
  have hD2 : 0 < D ^ 2 := by positivity
  have : (D ^ (n - 2) * (L ^ 2 * β ^ 2 * c * N)) * D ^ 2 ≤ (4 * k ^ 2 * D0 ^ 2) * D ^ 2 := by
    nlinarith [hsq]
  exact le_of_mul_le_mul_right this hD2

/-- Doubling the distance from `D ≤ D0/3` saves at least `k D0 D` of distortion cost. -/
theorem compare_double (k D0 D : ℝ) (hk : 0 ≤ k) (hD : 0 ≤ D) (h3 : 3 * D ≤ D0) :
    k * D0 * D ≤ k * (D0 - D) ^ 2 - k * (D0 - 2 * D) ^ 2 := by
  have e : k * (D0 - D) ^ 2 - k * (D0 - 2 * D) ^ 2 = k * D * (2 * D0 - 3 * D) := by ring
  rw [e]
  nlinarith [mul_nonneg hk hD]

/-- Lower bound: if `k D0 D ≤ L √(c N (2D)ⁿ / 2)` with `D > 0` and `n ≥ 2`, then
`2 k² D0² ≤ D^(n-2) · L² c N 2ⁿ`. -/
theorem paradox_lower (L c N k D0 D : ℝ) (n : ℕ) (hn : 2 ≤ n) (hL : 0 ≤ L) (hc : 0 ≤ c) (hN : 0 ≤ N)
    (hD : 0 < D) (hk : 0 ≤ k) (hD0 : 0 ≤ D0)
    (h : k * D0 * D ≤ L * Real.sqrt (c * N * (2 * D) ^ n / 2)) :
    2 * k ^ 2 * D0 ^ 2 ≤ D ^ (n - 2) * (L ^ 2 * c * N * 2 ^ n) := by
  have hJ : 0 ≤ c * N * (2 * D) ^ n / 2 := by positivity
  have hlhs : 0 ≤ k * D0 * D := by positivity
  have hsq : (k * D0 * D) ^ 2 ≤ (L * Real.sqrt (c * N * (2 * D) ^ n / 2)) ^ 2 :=
    pow_le_pow_left₀ hlhs h 2
  have e1 : (L * Real.sqrt (c * N * (2 * D) ^ n / 2)) ^ 2 = L ^ 2 * (c * N * (2 * D) ^ n / 2) := by
    rw [mul_pow, Real.sq_sqrt hJ]
  have e2 : (2 * D) ^ n = 2 ^ n * (D ^ (n - 2) * D ^ 2) := by
    rw [mul_pow, ← pow_add]; congr 2; omega
  rw [e1, e2] at hsq
  have hD2 : 0 < D ^ 2 := by positivity
  have : (2 * k ^ 2 * D0 ^ 2) * D ^ 2 ≤ (D ^ (n - 2) * (L ^ 2 * c * N * 2 ^ n)) * D ^ 2 := by
    nlinarith [hsq]
  exact le_of_mul_le_mul_right this hD2

end Paper1Revision6
