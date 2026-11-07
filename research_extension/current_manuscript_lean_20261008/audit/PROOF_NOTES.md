# Proof notes: routes chosen and how each connects to the model

## Cramér–Rao (S7.1 i): `Paper1GaussianHCR.lean`, `Paper1GaussianCR.lean`

1. Change of measure. `N(m₁,v) = N(m₀,v).withDensity ρ` with `ρ = exp(((x-m₀)(m₁-m₀) - (m₁-m₀)²/2)/v)`. This is
   proved from Mathlib's `gaussianPDFReal`, and extended coordinatewise to the product record by `prod_withDensity`.
2. Second moment of the density. `∫ρ² = exp((m₁-m₀)²/v)`, from the Gaussian MGF `mgf_id_gaussianReal`. The record
   version is a product, by `integral_prod_mul`.
3. Hammersley–Chapman–Robbins. Apply covariance Cauchy–Schwarz to `T` and `ρ` under the base law. This gives
   `(E₁T - E₀T)² ≤ Var₀T · (∫ρ² - 1)` for every `T ∈ L²`.
4. Limit along a line. Take `m₁ = h(θ₀ + t a)` and use local unbiasedness: `t² a_k² ≤ V (e^{Q(t)/v} - 1) ≤ V (Q/v) e^{Q/v}`,
   where `Q(t) = ‖h(θ₀+ta) - h(θ₀)‖²`. Divide by `t²` and let `t → 0` in `𝓝[≠] 0`. Since `Q/t² → ‖Ja‖²` by
   `HasDerivAt.tendsto_slope_zero`, this gives `a_k² ≤ V‖Ja‖²/v`.
5. Choose `a = (JᵀJ)⁻¹e_k`. Then `a_k = ‖Ja‖² = [(JᵀJ)⁻¹]_kk`, so `V ≥ v[(JᵀJ)⁻¹]_kk`.

The experiment is the averaged record `N(h(θ), σ_h² I)`. The statement covers every square-integrable, locally
unbiased statistic of that record, and it uses no domination or regularity condition.

## Spectral identification (Thm 5.4 ii, every K): `Paper1SpectralID.lean`

1. For a real polynomial `p` on `|z| = 1`: `z^{deg p}|p(z)|² = p(z)·p^rev(z)`. This uses `eval₂_reverse_mul_pow` and
   `conj z = z⁻¹`.
2. Equal spectra make `L = s₁ n₁ n₁^rev d₂ d₂^rev X^{deg n₂ + deg d₁}` and `R` agree on the circle. The circle is
   infinite, by the Möbius map `(1+it)/(1-it)`. So `L = R` as polynomials.
3. Let `α` be a nonzero zero of `n₁` in the disk. Then `L(α) = 0`. On the right side:
   - `n₂^rev(α) ≠ 0` and `d₁^rev(α) ≠ 0`, since their zeros are reciprocals of zeros inside the disk;
   - `d₁(α) ≠ 0`, since there is no cancellation (`p1_thm_minphase_zeros`).
   So `n₂(α) = 0`.
4. The zeros of `tfTop` are `0` and the rates, so the two sets of rates coincide.

## Passive reset blocks (S3.2): `Paper1PassiveVariance.lean`

- The block law is an explicit product of five independent coordinates.
- `Z` and `Z²` are written as coefficient–exponent vectors. Their integrals are sums of products of moments
  (`integral_prod_mul`, `integral_finsetSum`).
- Then `Var Z = E Z² - (E Z)²`. The `n` blocks are `Measure.pi`, with `variance_sum_pi` and Chebyshev.
