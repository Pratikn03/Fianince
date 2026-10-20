# The Paper 1 → Paper 2 Bridge: Safety Without Identification

**Status:** working technical note, written against `main` @ `0b46a08`. Every number below is produced by
[`bridge_check.py`](bridge_check.py) (results in [`results/bridge_results.json`](results/bridge_results.json)) and pinned by
[`tests/test_bridge_proposition.py`](../../tests/test_bridge_proposition.py). Nothing here has been reviewed by anyone but the author of this note.

## 1. The claim, stated so that it can fail

> A market need not reveal *which* algorithms trade in order to reveal *enough about their aggregate effect* to support
> a risk decision. The decision depends on the cohorts only through one scalar, $\Phi$; that scalar is cheap to certify
> under a controlled-probe contract, impossible to certify from a finite window without a memory bound, and its
> misjudgement has a price in safe trading that can be computed.

### Setting (Paper 2 §5.1; Paper 1 positive-cohort economy)

Class $\mathcal E^+$: $a\ge 0$, $\kappa>0$, cohorts $(q_i,\eta_i)$ with $q_i\ge 0$, $\eta_i\in(0,1]$, and $a+\kappa\Phi<1$ where
$\Phi=\sum_i q_i=\int dM(r)/(1-r)$ and $M=\sum_i q_i\eta_i\delta_{1-\eta_i}$. The price response to one unit of flow is
$h_0=\kappa$, $h_{t+1}=ah_t+\kappa\sum_{m\le t}k_mh_{t-m}$ with $k_m=\int r^m\,dM$.

**Risk contract (R).** Position $I$ fixed; per-period shock $|u_t|\le\bar u$; marked to market at every date; unbounded horizon; hidden state at the start is zero (a reset) **or** its drift is observed. Budget $\mathcal B$.

**Observation contracts.** (O1) $N$ independent controlled-probe experiments returning $h_0..h_{T-1}$ with independent $N(0,\sigma^2)$ errors; (O2) an exact window $h_0..h_n$, optionally with a memory bound $\bar r<1$; (O4) audited exposure revealing $\Phi$. *Passive public prices are a different contract and are not covered (§5).*

### Proposition B (bridge)

For every $E\in\mathcal E^+$:

1. **Sufficiency.** The worst-case loss under (R) is $|I|\,\bar u\,S$ with $S=\kappa/(1-a-\kappa\Phi)$. Hence which decisions are certifiably safe, unsafe or undecidable given data $D$ depends on $D$ only through $\{\Phi(E):E\in\Theta(D)\}$.
2. **Rate separation.** For every $\delta>0$ there are $E_0,E_\delta\in\mathcal E^+$ that are *decision-equivalent but not observationally equivalent*: identical $\Phi$ (so identical $S$ and identical quantity-gate decisions for every $(I,\bar u,\mathcal B)$), yet cohort memories differing by $\Delta\eta=2\delta$, equal responses at lags 0–1 and
   $h_2^{\delta}-h_2^{0}=-\kappa^2q\delta^2$ exactly (the complete responses differ from lag 2 on). Telling them apart with total error $\le 10\%$ needs $N\ge 3.24\,\sigma^2/\|\Delta h\|_2^2$, and $\|\Delta h\|_2=O(\delta^2)$, so **$N=\Omega(\sigma^2\delta^{-4})$ is necessary.** A *matching upper bound* (that $O(\sigma^2\delta^{-4})$ experiments suffice) is Paper 1's claim for the pair and for general $K$; it is not re-derived here. Certifying $S$ to precision $\varepsilon$ under (O1) needs $N=O(\sigma^2\varepsilon^{-2}\log(1/\varepsilon))$ whatever $\delta$ is (Paper 2 Thm 5.4).
3. **Limits of finite windows.** Let $M$ be a nonnegative measure on $[0,\bar r]$ with $\bar r<1$, observed through an exact window $h_0,h_1,h_2$ (hence $k_0=\int dM>0$ and $k_1=\int r\,dM$), with $0<k_1/k_0<\bar r$ (interior of the moment space for $n=2$). Then the compatible $\Phi=\int dM/(1-r)$ fill exactly $[\,k_0^2/(k_0-k_1),\;k_0+k_1/(1-\bar r)\,]$, with $S$ finite only while $a+\kappa\Phi<1$. Without the bound $\bar r$ (rates allowed in $[0,1)$), two cohorts suffice to make $S$ arbitrarily large, or the economy unstable, with $h_0,h_1,h_2$ unchanged.
4. **Price of missing information.** If a rule must admit an unsafe level with probability $\le\beta$ in economy 0, it gives up at least $(v_1-v_0)[1-\beta-\mathrm{TV}]_+$ of safe capacity in economy 1 (Paper 2 Prop 5.2).

## 2. Proofs and what each step rests on

| Step | Argument | Status |
|---|---|---|
| Worst case $=\bar u\sum_k\lvert g_k\rvert$, attained by $u_k=\bar u\,\mathrm{sign}(g_k)$ | Hölder; sign-aligned path | **Lean, full:** `p2_thm_guard_maximal`, `is_per_period_upper`, `is_per_period_attained` |
| $h_t\ge0$ and $h_t\le\kappa\bar\lambda^t$, so $\sum\lvert h_t\rvert=\sum h_t$ | positivity of $J\ge0$; row sums | **Lean, full:** `actual_positive_impulse_peak`, `is_iter_bound`, `is_tail_bound` |
| $S=\kappa/(1-a-\kappa\Phi)$ | sum the recursion over $t\ge0$: $S-\kappa=aS+\kappa\Phi S$, using the Cauchy product of absolutely convergent series and $\sum_mk_m=\sum_iq_i$ | **Not in Lean.** Elementary proof (here); checked in exact rationals, `part_a`, and by a long-horizon sum, `test_a_summed_response_formula_matches_long_horizon_sum` |
| $h_2^\delta-h_2^0=-\kappa^2q\delta^2$ | $k_0$ equal; $k_1^\delta=k_1^0-q\delta^2$; $h_2=ah_1+\kappa(k_0h_1+k_1h_0)$ | **Lean, full** for the reset recursion: `symmetric_third_tap_difference`, `physical_third_observation_separation`; exact check `part_a` |
| Gaussian KL $=N\lVert\Delta h\rVert^2/2\sigma^2$; two-point error $\ge(1-\mathrm{TV})/2$ | equal-variance Gaussians; Le Cam | **Lean, full:** `actual_pair_observation_kl`, `gaussian_equal_variance_kl`, `binary_rule_minimax_error_lower_bound` |
| $\lVert\Delta h\rVert_2=O(\delta^2)$ uniformly in the horizon | $\Delta h(\delta)$ is even and smooth in $\delta$, vanishes at $\delta=0$, and the operators have spectral radius bounded away from 1 for $\delta\le0.2$ | **Argued, not formalized.** Measured log-log slope $2.002$ is a consistency check, not a proof. Without this step only $N\ge 3.24\sigma^2/\lVert\Delta h\rVert^2$ is proved, not $\Omega(\delta^{-4})$ |
| $\mathrm{TV}\le\sqrt{\mathrm{KL}/2}$ | Pinsker | **Cited, not formalized** (Lean takes it as a hypothesis in `thmC_algebraic_core`) |
| Certificate validity and $N$-rate | deterministic geometric tail + Gaussian tail of an average | **Conditional:** tail in Lean (`p2_thm_certcost`); Gaussian step analytic. Matching lower bound (Thm 5.4(ii)) *not re-derived here* |
| $n=2$ window endpoints | lower: Jensen on convex $f(r)=1/(1-r)$; upper: chord $f(r)\le1+r/(1-\bar r)$ on $[0,\bar r]$, equality at atoms $\{0,\bar r\}$ | **Elementary, proved here;** independent LP and 200 random measures agree (`part_d`, `test_d_*`). General $n$ is Markov–Krein (cited); Lean has weak duality only (`is_upper_bound`, `is_lower_bound`) |
| Explicit unbounded family | atoms $\{0,1-\delta\}$ with weights $k_1/(1-\delta)$ and $k_0-k_1/(1-\delta)$ have moments $(k_0,k_1)$ and $\Phi(\delta)=k_0+k_1/\delta$ | **Proved here;** exact check `part_d`. General $n$: `p2_thm_window` (iii), conditional on the interior moment-cone hypothesis |
| Two-world loss | $E=\{A\le v_0\}$, Markov | **Lean, full:** `p2_prop_twoworld` (measure-theoretic), `is_two_world_capacity_loss` |

**The one dependency gap that matters:** the closed form for $S$ in the *cohort* economy is the load-bearing step for part 1, and it is not mechanized (Paper 2 `thm:sum` in Lean is the separate 3-state system). It is a two-line analytic proof, but `COVERAGE.md` should say so.

## 3. Counterexamples under weaker assumptions

**C1 — drop positivity (signed or contrarian cohorts): sufficiency fails.** Take $a=0.4,\kappa=1$ and cohorts $q=(0.9,-0.82)$, $\eta=(0.07,0.99)$. Then $\Phi=0.08$, the operator is stable (spectral radius $0.974$), and $\sum h_t=25/13=1.923$ exactly as for the one-cohort market with $q=0.08$. But $h_t$ changes sign (min $-0.349$) and $\sum|h_t|=2.667$: the true worst-case loss is **38.7% larger** than the $S$-based guard states. $\Phi$ is then not a sufficient statistic; the guard needs $\sum|g_k|$, which is not a function of $\Phi$. *Consequence: the bridge is a theorem about positive-feedback economies. Paper 1 checks its identification result for signed weights (`p1_mixture.tex`, 1,733 random economies); nothing in either paper extends the safety sufficiency to them, and Paper 2's guard already uses $\sum|g_k|$ for exactly this reason — it is just not a function of $\Phi$ once signs mix.*

**C2 — drop the memory bound: no finite window certifies anything.** With $a=0.4,\kappa=1$ and moments $(k_0,k_1)=(1/25,1/50)$ (market A), the economies with atoms $\{0,1-\delta\}$ all reproduce $h_0,h_1,h_2=(1,\,11/25,\,267/1250)$, yet

| $\delta$ | 1/2 | 1/4 | 1/10 | 1/20 | 1/25 | 1/27 | $\le 1/28$ |
|---|---|---|---|---|---|---|---|
| $S$ | 25/13 | 25/12 | 25/9 | 25/4 | 50/3 | 50 | unstable |

($\delta^*=1/28$.) With a memory bound $\bar r=0.95$ the same data certify $S\le25/4$; Example `ex:witness` market B ($S=95/17$) sits inside $[25/13,\,25/4]$.

**C3 — change the observation contract: not a counterexample, an untested domain.** (O1) assumes controlled, independent probes. Passive prices need the estimation of $h$ from observational data; Paper 1's passive cost and the failed pre-registered tests below say this is where the bridge is weakest.

## 4. One reproducible illustration (all of `bridge_check.py`)

**Design.** Single cohort $(q,\eta)=(0.08,0.5)$ against the split $(0.04,\,0.5\mp\delta)$, $a=0.4$, $\kappa=1$. Contract (O1) with independent $N(0,\sigma^2)$ errors, $\sigma=0.01$ per tap, $N=2000$ probes, $T=80$ taps, $\gamma=0.05$, memory bound $0.7$, $a+\kappa\Phi\le0.5$. The mean of $N$ independent responses is $N(h,\sigma^2/N)$ per tap, so it is sampled directly. Seed $20261020$; $4000$ replications per economy, so $8000$ trials per row (both economies have the same $S=25/13$). Intervals are Wilson 95%.

| $\delta$ | $\Delta\eta$ | $\lVert\Delta h\rVert_2$ | $N$ necessary to separate (≥) | Bayes accuracy of the two-point test at $N=2000$ (MC; 95% CI) | certificate coverage (95% CI) | mean excess of $\hat S^+$ over $S$ |
|---|---|---|---|---|---|---|
| 0.02 | 0.04 | $7.7\times10^{-5}$ | 54,000 | **0.570** [0.559, 0.581] | 0.956 [0.952, 0.961] | 0.0033 |
| 0.05 | 0.10 | $4.8\times10^{-4}$ | 1,400 | 0.860 [0.852, 0.867] | 0.949 [0.943, 0.953] | 0.0033 |
| 0.10 | 0.20 | $1.9\times10^{-3}$ | 86 | 1.000 [0.9995, 1.000] | 0.951 [0.946, 0.955] | 0.0033 |
| 0.20 | 0.40 | $7.8\times10^{-3}$ | 5 | 1.000 [0.9995, 1.000] | 0.951 [0.946, 0.956] | 0.0033 |

**How to read it.** The accuracy column is the Bayes accuracy for the *simple-versus-simple* problem: two known Gaussian-mean economies, equal prior probability, 0-1 loss, for which the likelihood-ratio rule is optimal and its accuracy is $\Phi(d'/2)$ with $d'=\sqrt N\lVert\Delta h\rVert_2/\sigma$ (theory column matches the MC to within 0.003). It is *not* a bound on any procedure that must also learn the economies, and it says nothing about other priors or minimax criteria. The certificate, built without knowing the split, covers at about the nominal level with the same width for every $\delta$. $\lVert\Delta h\rVert_2$ has measured log-log slope $2.002$ (necessary $N$ slope $-4.003$), a consistency check on the analytic scaling in §2, not a proof. The contract requires controlled, independent probes; nothing in this table speaks to passive prices.

## 5. What this does and does not establish

**Novelty, honestly.** Part 1 combines realization theory (impulse response determines only the merged measure), $\ell_1$-optimal control (worst case $=\ell_1$ norm), and the positive-feedback closed form. Part 2 is Le Cam plus a Gaussian average. Part 3 is Markov–Krein. A control or statistics referee will say each ingredient is classical. The defensible contribution is the finance statement: *for positive-feedback adaptive trading, risk certification is cheaper than identification by a polynomial factor in $1/\Delta\eta$, but only under a controlled-probe contract, a positivity assumption and a memory bound — and the price of lacking them is computable.* I would not describe it as a new mathematical principle.

**What it does not support.** It does not support "passive public prices certify risk". The repository's own evidence on that contract is: no overshoot in the BTCUSDT depth analysis; the merged response was estimated precisely in 5 of 30 markets (a failed pre-registered criterion); a failed pre-registered Coinbase test; a ~2.4% certified position-limit gain over a volatility limit in one test. Those results narrow the empirical claim; they should not be cited as confirming the bridge.

## 6. Open obligations (ordered by how much they threaten the claim)

| # | Obligation | Why it matters |
|---|---|---|
| 1 | **Hidden initial state.** (R) assumes a reset or an observed drift. Theorems using $M_C\lVert z_t\rVert$ (forward solvency) depend on hidden cohort memory and are **not** cohort-invariant (Paper 2 notes the row norm depends on the coordinates). | The bridge applies to the quantity-gate contract, not automatically to the margin theorem. Needs an explicit statement in Paper 2 §6. |
| 2 | **Passive observation.** No finite-sample guarantee exists; evidence is mixed-to-negative. | Decides whether the bridge is a theory of controlled probing only. |
| 3 | **Dependent noise, model-order error, delays, retraining, and algorithms that react to probes.** O1 assumes independent Gaussian taps and, per Paper 1 (`p1_front.tex`, "Algorithms that react to being probed"), that cohorts keep their memories while probed. `prop:hotelling` is conditional; none of these was re-run here. C1 shows the model boundary is real. | Required before any "robustness" language; probe-reactivity bears directly on whether O1 is realizable. |
| 4 | **Mechanize the cohort $S$ formula** and either formalize Pinsker or label it as cited. | Closes the one load-bearing unformalized step. |
| 5 | **Specialist review of Paper 1's $(\Delta\eta)^{-(4K-2)}$ and $1/\log N$ rates and of Thm 5.4(ii).** I re-derived only the $K=2$-vs-1 pair scaling, and only its necessary direction. | The rates are the premise of part 2 for general $K$. |
| 6 | **Repository integrity — resolved 2026-10-20.** After merging `0b46a08` the generated receipts listed 396 declarations while `COVERAGE.md` claimed 443 (the 47 `is_*` theorems in `InfoSafetyExtensions.lean` were un-audited). `verify_formalization.py` was re-run: 443 declarations, standard axioms only, no `sorry`; `named_declarations.json`, `checked_theorem_types.json` and `axiom_audit.jsonl` now agree with `COVERAGE.md`, and `verify_ceiling_suite_lean_proofs.py` passes (26 + 26 + 3). | Kept as a record. `complete = False` in the receipt still stands: kernel-checked is not the same as every manuscript statement fully formalized. |
