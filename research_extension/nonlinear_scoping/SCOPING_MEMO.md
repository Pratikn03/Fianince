# Scoping: a sufficient statistic for markets of nonlinear (learning) traders

*8 November 2026. Exploratory work, not a registered study. The simulation is in `sim_wiener.py`, with results in
`sim_wiener_results.json`.*

## The question

Paper 1's core result is linear. The feedback kernel is sufficient for every outcome that price-based trading
determines, and it is all that prices identify. Every precedent (Granger 1980, disaggregation, intertemporal MPCs) is
linear too. Is there a statement about **nonlinear** traders that is true, sharp and not already known?

## Verdict, in one paragraph

Yes, for one class. Take traders who have an exponential memory, as now, but whose trades **saturate**: position
limits, margin caps, or a capped or `tanh` policy.
- **The sufficient object.** It is no longer the kernel. It is a measure **ν over memory and leverage**: each trader
  contributes its capacity c at the point (memory rate r, leverage ℓ).
- **What normal-times prices reveal.** Only the kernel, which is the first leverage moment of ν at each memory.
- **What they do not reveal.** How close traders are to their limits, which is what governs behaviour under stress.
- **How it can be learned.** Only by pushing traders toward their limits, or through disclosure. With hard limits,
  calm data carry no information about it, exactly. With smooth saturation, the information grows like the sixth
  power of the probe size.

This is a sharper and more distinctive statement than the linear paper. I did not find it in the literature. The
intuition that "calm data say little about stress" is familiar, but I found no formal sufficiency and identification
result of this kind for feedback markets. A first theorem is within days, and a full paper within weeks. Learning
agents whose rules keep changing (class 2 below) are not within reach yet.

## 1. Which class of agents

| Class | Agents | First theorem? |
|---|---|---|
| **1. Saturating trend followers and contrarians** (exponential memory with a capped or smooth-saturating policy) | Kalman or online-gradient desks with position limits or margin caps; risk-capped CTAs | **Yes.** See §3. |
| 2. Slow learners whose parameters drift (two timescales) | Online learners that re-estimate their intensity on a slow clock | Only as an extension: ν becomes a slowly moving ν_t. Identifying its dynamics is hard. |
| 3. General RL or LLM agents | Arbitrary nonlinear policies with internal state | No. Only the trivial statement: the aggregate input–output operator is sufficient. It has no finite description, so nothing useful is identified. |

## 2. The candidate aggregate Y

Agent i has memory rate r_i, capacity c_i > 0 and leverage ℓ_i = q_i η_i / c_i. Its flow is c_i ψ(ℓ_i z_{i,t−1}),
with z_{i,t} = r_i z_{i,t−1} + x_t, and ψ is a common saturating shape: ψ(u) = u near 0, bounded. Aggregate flow is

  F_t = ∫ c ψ(ℓ · Σ_m r^m x_{t−1−m}) dν,  with ν = Σ_i c_i δ_{(r_i, ℓ_i)}.

- **Y = ν**, a measure on (memory, leverage) weighted by capacity.
- **Linear limit.** Its first leverage moment at each memory, M₁(r) = Σ_{i: r_i = r} c_i ℓ_i, is exactly the
  merged measure of Paper 1.
- **Smooth ψ (for example tanh).** The order-(2n+1) Volterra kernel of aggregate flow depends on the population only
  through M_{2n+1}(r) = Σ c_i ℓ_i^{2n+1}. Each order of nonlinearity reveals one more moment of the leverage
  distribution within each memory class.

## 3. Theorems within reach, with their status

| # | Statement | Difficulty | Evidence so far |
|---|---|---|---|
| A | **Sufficiency.** For any common ψ, every outcome of the market game (prices, flows, insider profit, dealer inventory) depends on the traders only through ν. This is the same induction as Theorem 3.1. | Days; Lean-ready | Simulation: populations with the same ν (one trader versus the same trader split in two) give identical paths. Largest gap 0.0 over 400 periods. |
| B | **Hierarchy.** For analytic odd ψ with all odd coefficients nonzero (tanh), responses to probes of all small amplitudes identify μ = Σ c_iℓ_i δ_{(r_i, ℓ_i²)}. That is the whole equivalence class, apart from exactly offsetting trend-follower and contrarian pairs. Multi-pulse designs separate the memory moments. | Weeks (closed-loop Volterra inversion; Hausdorff moment problem) | Two populations with the same kernel (M₁ = 0.1) but different M₃ (0.001 vs 0.002125). The first-tap gap divided by A³ is 1.5359×10⁻⁴ at A = 0.05, against a predicted κ⁴·(−1/3)·ΔM₃ = 1.5360×10⁻⁴. |
| C | **No information without stress.** For hard limits (ψ = clip): two populations with the same kernel produce identical price paths on every event in which no agent reaches its limit. So the total-variation distance between their observation laws is at most the probability that some agent hits its limit. Under Gaussian noise, that probability is exponentially small in (1/(ℓ_max s_z))². Calm passive data therefore need exponentially many observations, and probes must push someone to a limit. | Days to a week; Lean-ready | Clipped policy, same kernel, different capacities: identical responses (gap exactly 0) for pulses up to 4, and a gap appears only once the most-levered agent saturates (pulse 6: gap 0.072; pulse 12: 0.364). |
| D | **The cost of a stress probe** (smooth case). Distinguishing populations that differ at M₃ takes N ≳ σ²/(A⁶κ⁸ΔM₃²) probes of size A. Capital per probe grows like A², and large probes push the market toward the very limits being measured. This is a trade-off a supervisor actually faces. | Weeks | Follows from B with the two-point method of Paper 1. |
| E | **Passive non-Gaussianity.** With smooth saturation, Gaussian shocks produce non-Gaussian prices, and the fourth cumulant depends on M₃. | Harder | **Weak so far.** In the stable calibration, the excess kurtosis of the two populations differed by under 0.01 at 400,000 observations. That is within sampling error. This supports C and D: calm data say little. It is not a usable estimator. |

**A first run used an unstable market.** The first simulation used a calibration whose linear feedback budget exceeded
one (1.03). The saturation then held the market in a bounded but strongly non-Gaussian state, with excess kurtosis
near −1. I reran everything at a stable calibration (budget 0.77); all numbers above are from that run. This is itself
a pointer: near the stability boundary, saturation dominates, and so does ν.

## 4. Why this could matter more than the linear paper

- **The object is new and economically loaded.** ν is the distribution of how close machine traders are to their
  limits. That is what drives fire sales, crowded unwinds and liquidity spirals (Brunnermeier and Pedersen 2009;
  empirical crowding and tail risk: Barroso, Edelen and Karehnke 2022).
- **The statement is sharp.** Normal-times prices identify the kernel and nothing about the leverage distribution;
  with hard limits, exactly nothing. That turns "stress tests and position disclosure are necessary" from practice
  into a theorem, with rates.
- **There is a policy hook.** Disclosure of capacities and limits (margins, position limits, risk caps) is the
  information that prices cannot supply. It is a different disclosure from Paper 1's tagged flow, and a natural
  companion to it.

## 5. Risks

1. **The "obvious" objection.** "You learn about limits only by hitting them" sounds obvious. The defence is the
   exact sufficient object ν, the identification hierarchy (B) and sharp exponential and polynomial rates (C, D).
   Without B and the rates, it is a remark, not a paper.
2. **A common ψ shape.** Results A and C need only that each policy is linear inside its own band, so they extend to
   heterogeneous shapes. B needs a common analytic shape, or a richer ν over shapes.
3. **Strategic deleveraging.** Real traders cut leverage as they approach limits, which is class 2. A first paper
   should state this as the main open problem.
4. **Known mathematics.** Identifying sums of Wiener branches is a known system-identification problem (parallel
   Wiener–Hammerstein, tensor decompositions of Volterra kernels; Dreesen et al. 2017). The contribution must be the
   market structure (feedback loop, equilibrium, the game, supervision), not the decomposition technique.
5. **The literature search was not exhaustive.** I found no formal result of this kind, but that is not proof that
   none exists. A targeted search in nonlinear system identification and macro-finance (leverage cycles, Geanakoplos)
   should be done before writing.

## 6. Also found: action for the core paper

Leclère and Rosenbaum (arXiv:2609.03115, 2 September 2026) study a linear mean-field model of agents with
heterogeneous forecast horizons under market impact. There, too, market impact "depends on aggregate positions rather
than trader identities." It is close to Paper 1's linear setting and should be cited in the core version's
related-work section.

## 7. Recommendation

The bet is worth making, in this order:
1. **Theorems A and C** with Lean (about a week). They alone give a short, sharp note: *"Normal-times prices cannot
   reveal how close machine traders are to their limits."*
2. **Theorem B and the cost result D** (a few weeks). Together they would make it a full paper.
3. **Class 2** (strategic deleveraging) as the open problem, possibly with Kyle's input.

Decide after step 1. If C comes out with clean matching rates, this becomes the lead project.

## Update (8 November 2026, later): step 1 done, written into the core paper

- **Theorem A** is now Theorem 7.1 of the core version. It is machine-checked pathwise for every shape ψ and every
  causal insider, dealer and signal rule (`p1_sat_sufficiency`).
- **Theorem C** is now Theorem 7.2.
  - Part (i), the pathwise statement, is machine-checked (`p1_sat_stress_invariance`, `p1_sat_follows_linear`).
  - Parts (ii)–(iv), the total-variation, Gaussian and probe bounds, are proved on paper.
  - `sim_passive_clip.py`: the simulated exceedance probability lies below the bound at every noise level tested. The
    bound is loose in its constant (a union bound over dates).
- **Theorem D** (smooth case) is now Proposition 7.3, proved on paper: a cubic response gap, an N ≳ σ²/A⁶ lower bound,
  and the order attained through the first tap.
- **Theorem B** (the full identification hierarchy) remains open, and the paper says so.
- **Lean module:** `Paper1SaturatingSufficiency.lean`, standard axioms only. There are now 1093 named declarations
  across 121 modules.

## Update 2 (8 November 2026): identification closed, deleveraging, dealers

- **Theorem B, the identification, is closed qualitatively** as Theorem 7.4 of the core version, proved on paper.
  - **Statement:** for tanh or hard limits, responses to all probes identify exactly the signed measure
    μ̃ = Σ c_i sgn(ℓ_i) δ_(r_i, |ℓ_i|). That is the whole equivalence class.
  - **Proof:** probes steer the price along any path. Two dates of prices then give a sum of scaled copies of ψ. The
    copies are separated by the poles of tanh, or by the kinks of the hard limit.
  - **Rates beyond the third order remain open.**
  - **Recovery check:** kinks found at 3.702 and 14.813; net capacities recovered as 0.24989 and 0.99988, against
    true values 0.25 and 1.
- **Deleveraging traders (Proposition 7.5).** Theorem 7.2 holds for any causal rule outside the bands. This is
  machine-checked in `Paper1CoreExtensions.lean`.
- **Dealers (Proposition 7.6).**
  - Kernel-only dealers preserve every Section 7 result.
  - An informed forward-looking dealer leaks leverage information into calm prices, but only at the scale of the
    probability of a breach. The bound is checked numerically.
  - A full equilibrium of this kind is open.
- **Proposition 3.2** is now machine-checked for arbitrary kernels.
