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
| $S=\kappa/(1-a-\kappa\Phi)$ | sum the recursion over $t\ge0$: $S-\kappa=aS+\kappa\Phi S$, using Tonelli/Cauchy product of nonnegative absolutely convergent series and $\sum_mk_m=\sum_iq_i$ | **Proved analytically in §2.1 below** (3-state analogue in Lean: `is_summed_response_closed_form`); checked in exact rationals (`part_a`) and long-horizon sum (`test_a_summed_response_formula_matches_long_horizon_sum`) |
| $h_2^\delta-h_2^0=-\kappa^2q\delta^2$ | $k_0$ equal; $k_1^\delta=k_1^0-q\delta^2$; $h_2=ah_1+\kappa(k_0h_1+k_1h_0)$ | **Lean, full** for the reset recursion: `symmetric_third_tap_difference`, `physical_third_observation_separation`; exact check `part_a` |
| Gaussian KL $=N\lVert\Delta h\rVert^2/2\sigma^2$; two-point error $\ge(1-\mathrm{TV})/2$ | equal-variance Gaussians; Le Cam | **Lean, full:** `actual_pair_observation_kl`, `gaussian_equal_variance_kl`, `binary_rule_minimax_error_lower_bound` |
| $\lVert\Delta h\rVert_2=\Theta(\delta^2)$ uniformly in the horizon | Explicit two-sided Parseval/resolvent sandwich $\kappa^2 q\delta^2 \le \lVert\Delta h(\delta)\rVert_2 \le C_{\mathrm{Parseval}}(\bar\delta)\delta^2$ proved analytically in §2.2 below | **Proved analytically in §2.2 below** and verified numerically in `part_b` (`within_analytic_sandwich: true` across all $\delta$; measured log-log slope $2.002$) |
| $\mathrm{TV}\le\sqrt{\mathrm{KL}/2}$ | Pinsker | **Cited** (classical Pinsker inequality; Lean takes it as an explicit hypothesis in `thmC_algebraic_core`) |
| Certificate validity and $N$-rate | deterministic geometric tail + Gaussian tail of an average | **Conditional:** tail in Lean (`p2_thm_certcost`); Gaussian step analytic. Matching lower bound (Thm 5.4(ii)) proved in `p2_appendix.tex` |
| $n=2$ window endpoints | lower: Jensen on convex $f(r)=1/(1-r)$; upper: chord $f(r)\le1+r/(1-\bar r)$ on $[0,\bar r]$, equality at atoms $\{0,\bar r\}$ | **Elementary, proved here;** independent LP and 200 random measures agree (`part_d`, `test_d_*`). General $n$ is Markov–Krein (cited); Lean has weak duality only (`is_upper_bound`, `is_lower_bound`) |
| Explicit unbounded family | atoms $\{0,1-\delta\}$ with weights $k_1/(1-\delta)$ and $k_0-k_1/(1-\delta)$ have moments $(k_0,k_1)$ and $\Phi(\delta)=k_0+k_1/\delta$ | **Proved here;** exact check `part_d`. General $n$: `p2_thm_window` (iii), conditional on the interior moment-cone hypothesis |
| Two-world loss | $E=\{A\le v_0\}$, Markov | **Lean, full:** `p2_prop_twoworld` (measure-theoretic), `is_two_world_capacity_loss` |

### 2.1 Self-contained analytical proof of $S = \kappa/(1-a-\kappa\Phi)$ on $\mathcal E^+$

Let $E\in\mathcal E^+$ have parameters $a\ge 0$, $\kappa>0$, $q_i\ge 0$, $\eta_i\in(0,1]$, $\bar r = \max_i(1-\eta_i)<1$, and $\bar s = a+\kappa\Phi < 1$ where $\Phi=\sum_{i=1}^K q_i$.
1. **Nonnegativity and geometric decay.** By induction on $t\ge 0$, $h_t\ge 0$ and $y_{i,t}=\eta_i\sum_{m=0}^t (1-\eta_i)^{t-m}h_m\ge 0$. By the positive-cohort contraction lemma (`is_iter_bound` in Lean), $0\le h_t\le \kappa\bar\lambda^t$ with $\bar\lambda = 1 - (1-\bar r)(1-\bar s)\in[0,1)$. Hence $S = \sum_{t=0}^\infty h_t < \infty$ and $Y_i = \sum_{t=0}^\infty y_{i,t} < \infty$ converge absolutely.
2. **Cohort state sum.** By Tonelli's theorem for nonnegative series,
   \[
   Y_i = \sum_{t=0}^\infty \eta_i \sum_{m=0}^t (1-\eta_i)^{t-m} h_m = \sum_{m=0}^\infty h_m \, \eta_i \sum_{k=0}^\infty (1-\eta_i)^k = \sum_{m=0}^\infty h_m \, \eta_i \cdot \frac{1}{\eta_i} = S.
   \]
3. **Price recursion sum.** Summing $h_{t+1} = a h_t + \kappa\sum_{i=1}^K q_i y_{i,t}$ over $t=0,1,2,\ldots$ yields
   \[
   S - h_0 = a S + \kappa \sum_{i=1}^K q_i Y_i = (a + \kappa\Phi) S \quad\Longrightarrow\quad (1 - a - \kappa\Phi) S = \kappa \quad\Longrightarrow\quad S = \frac{\kappa}{1 - a - \kappa\Phi}.
   \]

### 2.2 Self-contained analytical proof of the uniform sandwich $\lVert\Delta h(\delta)\rVert_2 = \Theta(\delta^2)$

Compare the single-cohort economy $E_0=(a,\kappa,q,\eta_0)$ with the symmetric split $E_\delta=\bigl(a,\kappa,(q/2,q/2),(\eta_0-\delta,\eta_0+\delta)\bigr)$ for $\delta\in(0,\bar\delta]$ where $\bar\delta < \min(\eta_0,1-\eta_0)$ and $\bar s = a+\kappa q < 1$. Write $r_0 = 1-\eta_0$.
1. **Lower bound.** Because $h_0(\delta)-h_0(0)=0$, $h_1(\delta)-h_1(0)=0$, and $h_2(\delta)-h_2(0)=-\kappa^2 q\delta^2$ (`symmetric_third_tap_difference` in Lean),
   \[
   \lVert\Delta h(\delta)\rVert_2 \;\ge\; \bigl(\lvert h_0(\delta)-h_0(0)\rvert^2 + \lvert h_1(\delta)-h_1(0)\rvert^2 + \lvert h_2(\delta)-h_2(0)\rvert^2\bigr)^{1/2} \;=\; \kappa^2 q\,\delta^2.
   \]
2. **Uniform upper bound via Parseval's identity.** For $|\zeta|\le 1$, the open-loop memory transfer function is $K_\delta(\zeta) = \frac{q\zeta}{2}\bigl(\frac{\eta_0-\delta}{1-(r_0+\delta)\zeta} + \frac{\eta_0+\delta}{1-(r_0-\delta)\zeta}\bigr)$. Putting the difference over a common denominator gives the exact rational identity
   \[
   K_\delta(\zeta) - K_0(\zeta) \;=\; \frac{-q(1-\zeta)\zeta^2\,\delta^2}{(1-r_0\zeta)\bigl((1-r_0\zeta)^2 - \delta^2\zeta^2\bigr)}.
   \]
   On the unit circle $|\zeta|=1$, $|1-\zeta|\le 2$, $|1-r_0\zeta|\ge 1-r_0=\eta_0$, and $|(1-r_0\zeta)^2-\delta^2\zeta^2| = |1-(r_0+\delta)\zeta|\,|1-(r_0-\delta)\zeta| \ge (\eta_0-\bar\delta)^2 > 0$. Moreover, since $k_m(\delta)\ge 0$ and $\sum_{m=0}^\infty k_m(\delta)=q$, the closed-loop denominator satisfies $|1 - a\zeta - \kappa K_\delta(\zeta)| \ge 1 - a - \kappa q = 1-\bar s > 0$ for all $|\zeta|=1$ and all $\delta\in[0,\bar\delta]$. By Parseval's identity applied to $H_\delta(z) - H_0(z) = \frac{\kappa^2(K_\delta(z^{-1})-K_0(z^{-1}))}{(1-az^{-1}-\kappa K_\delta(z^{-1}))(1-az^{-1}-\kappa K_0(z^{-1}))}$,
   \[
   \kappa^2 q\,\delta^2 \;\le\; \lVert\Delta h(\delta)\rVert_2 \;\le\; \frac{2\kappa^2 q}{(1-a-\kappa q)^2\,\eta_0\,(\eta_0-\bar\delta)^2}\,\delta^2 \equiv C_{\mathrm{Parseval}}(\bar\delta)\,\delta^2.
   \]

### 2.3 Rate hierarchy across identification vs. certification problems

| Problem | Unknowns & Observation Contract | Minimax Sample / Probe Complexity | Dependence on Pole Separation $\Delta\eta = 2\delta$ | Where Established |
|---|---|---|---|---|
| **Known-pair binary testing** ($K=2$ vs. $1$) | Candidate poles $\eta_0\pm\delta$ known; contract `O1` | $N = \Theta(\sigma^2\delta^{-4})$ | $\delta^{-4}$ | Bridge Prop B(2); Paper 1 `thm:quantity`, `thm:spectral`, `thm:rh` |
| **Unknown 2-cohort parameter learning** ($K=2$) | Both $(\eta_1,\eta_2,q_1,q_2)$ unknown; permutation-invariant loss | $N = \Theta(\sigma^2(\Delta\eta)^{-6})$ | $(\Delta\eta)^{-6}$ | Paper 1 `prop:crb`, `thm:twocohort` |
| **General unknown $K$-cohort learning** | All $(q_i,\eta_i)_{i=1}^K$ unknown; contract `O1` or passive `I2` | $N = \Theta(\sigma^2(\Delta\eta)^{-(4K-2)})$ | $(\Delta\eta)^{-(4K-2)}$ | Paper 1 `thm:kcohort` (lower), `prop:esprit` (upper), `prop:passive` (passive) |
| **Unrestricted completely monotone memory** | Arbitrary nonnegative measure $M$ on $[0,\bar r]$ under $W_1$ metric | $W_1 \asymp (\log N)^{-1} \iff N = \exp(\Theta(\varepsilon^{-1}))$ | Exponential in $1/\varepsilon$ | Paper 1 `lem:altpair`, `thm:general` |
| **Summed-gain risk certification** ($S$ or $\Phi$) | Any $E\in\mathcal E^+$ with memory bound $\bar r<1$ and stability margin $\bar s<1$; contract `O1` | $N = \Theta(\sigma^2\varepsilon^{-2}\log(1/\varepsilon))$ | **Independent of $\Delta\eta$ and $K$** | Bridge Prop B(1)–(2); Paper 2 `thm:certcost`, `thm:robustguard` |

## 3. Counterexamples under weaker assumptions

**C1 — drop positivity (signed or contrarian cohorts): sufficiency fails.** Take $a=0.4,\kappa=1$ and cohorts $q=(0.9,-0.82)$, $\eta=(0.07,0.99)$. Then $\Phi=0.08$, the operator is stable (spectral radius $0.974$), and $\sum h_t=25/13=1.923$ exactly as for the one-cohort market with $q=0.08$. But $h_t$ changes sign (min $-0.349$) and $\sum|h_t|=2.667$: the true worst-case loss is **38.7% larger** than the $S$-based guard states. $\Phi$ is then not a sufficient statistic; the guard needs $\sum|g_k|$, which is not a function of $\Phi$. *Consequence: the bridge is a theorem about positive-feedback economies. Paper 1 checks its identification result for signed weights (`p1_mixture.tex`, 1,733 random economies); nothing in either paper extends the safety sufficiency to them, and Paper 2's guard already uses $\sum|g_k|$ for exactly this reason — it is just not a function of $\Phi$ once signs mix.*

**C2 — drop the memory bound: no finite window certifies anything.** With $a=0.4,\kappa=1$ and moments $(k_0,k_1)=(1/25,1/50)$ (market A), the economies with atoms $\{0,1-\delta\}$ all reproduce $h_0,h_1,h_2=(1,\,11/25,\,267/1250)$, yet

| $\delta$ | 1/2 | 1/4 | 1/10 | 1/20 | 1/25 | 1/27 | $\le 1/28$ |
|---|---|---|---|---|---|---|---|
| $S$ | 25/13 | 25/12 | 25/9 | 25/4 | 50/3 | 50 | unstable |

($\delta^*=1/28$.) With a memory bound $\bar r=0.95$ the same data certify $S\le25/4$; Example `ex:witness` market B ($S=95/17$) sits inside $[25/13,\,25/4]$.

**C3 — change the observation contract: not a counterexample, an untested domain.** (O1) assumes controlled, independent probes. Passive prices need the estimation of $h$ from observational data; Paper 1's passive cost and the failed pre-registered tests below say this is where the bridge is weakest.

**C4 — drop the reset / observed-drift condition ($z_0 \neq 0$ unknown): forward solvency and drift loss are not cohort-invariant (`part_f`).** Take $a=2/5$, $\kappa=1$, and two two-cohort positive economies:
- $\theta^{(1)}$: $q^{(1)}=(1/5,\,1/5)$, $\eta^{(1)}=(5/8,\,3/8)$ ($r^{(1)}=(3/8,\,5/8)$);
- $\theta^{(2)}$: $q^{(2)}=(9/25,\,1/25)$, $\eta^{(2)}=(13/24,\,1/8)$ ($r^{(2)}=(11/24,\,7/8)$).

Both economies lie in $\mathcal E^+$, share identical total feedback $\Phi^{(1)}=\Phi^{(2)}=2/5$ (hence identical infinite-horizon summed response $S^{(1)}=S^{(2)}=5$), and share identical early impulse taps $(h_0,h_1,h_2)=(1,\,3/5,\,363/800)$ (matching both $k_0=1/5$ and $k_1=3/32$). Yet when the initial state $z_0=(x_0,y_{1,0},y_{2,0})^\top\neq 0$ is not reset:
1. After a single unit flow shock two steps prior ($t=-2$), both economies have the **exact same observed price path** $(x_{-2},x_{-1},x_0)=(1,\,3/5,\,363/800)$, but their hidden cohort states $y_0^{(1)}=(1311/2560,\,5853/12800)$ and $y_0^{(2)}=(175747/345600,\,2791/12800)$ generate different next-step unforced price drift $b_1=c_{\mathrm{price}}^\top J z_0$: $3003/8000 = 9009/24000$ in $\theta^{(1)}$ versus $8959/24000$ in $\theta^{(2)}$ (difference $50/24000=1/480$).
2. From the state after three lags ($t=-3$ shock), the exact cumulative future unforced price drift $\sum_{t=1}^\infty c_{\mathrm{price}}^\top J^t z_0 = \bigl(a x_0 + \kappa\sum_i(q_i/\eta_i)y_{i,0}\bigr)/(1-a-\kappa\Phi)$ is $20567/8000 = 61701/24000$ in $\theta^{(1)}$ versus $61751/24000$ in $\theta^{(2)}$.
3. Over an unknown hidden cohort state $z_0=(0,y_0)$ with $\lVert y_0\rVert_2\le 1$, the worst-case cumulative future drift is $5\sqrt{\sum_i(q_i/\eta_i)^2}=3.110$ in $\theta^{(1)}$ versus $3.688$ in $\theta^{(2)}$ (**18.6% larger**), and the one-step price-row norm $\lVert c_{\mathrm{price}}^\top J\rVert_2=\sqrt{a^2+\kappa^2\sum_i q_i^2}$ in the forward-solvency inequality (`thm:forward`) is $0.490$ versus $0.540$ (**10.2% larger**). *Consequence: Proposition B(1) and Paper 2's quantity-gate theorems (`thm:guard`, `thm:robustguard`) hold under an explicitly reset initial state ($z_0=0$) or when the unforced drift $b_t=CJ^t z_0$ is observed and subtracted from the loss budget; the general forward-solvency theorem (`thm:forward`) with unknown hidden cohort states $z_t\neq 0$ is not identification-invariant.*

## 4. One reproducible illustration (all of `bridge_check.py`)

**Design.** Single cohort $(q,\eta)=(0.08,0.5)$ against the split $(0.04,\,0.5\mp\delta)$, $a=0.4$, $\kappa=1$. Contract (O1) with independent $N(0,\sigma^2)$ errors, $\sigma=0.01$ per tap, $N=2000$ probes, $T=80$ taps, $\gamma=0.05$, memory bound $0.7$, $a+\kappa\Phi\le0.5$. The mean of $N$ independent responses is $N(h,\sigma^2/N)$ per tap, so it is sampled directly. Seed $20261020$; $4000$ replications per economy, so $8000$ trials per row (both economies have the same $S=25/13$). Intervals are Wilson 95%.

| $\delta$ | $\Delta\eta$ | $\lVert\Delta h\rVert_2$ | $N$ necessary to separate (≥) | Bayes accuracy of the two-point test at $N=2000$ (MC; 95% CI) | certificate coverage (95% CI) | mean excess of $\hat S^+$ over $S$ |
|---|---|---|---|---|---|---|
| 0.02 | 0.04 | $7.7\times10^{-5}$ | 54,000 | **0.570** [0.559, 0.581] | 0.956 [0.952, 0.961] | 0.0033 |
| 0.05 | 0.10 | $4.8\times10^{-4}$ | 1,400 | 0.860 [0.852, 0.867] | 0.949 [0.943, 0.953] | 0.0033 |
| 0.10 | 0.20 | $1.9\times10^{-3}$ | 86 | 1.000 [0.9995, 1.000] | 0.951 [0.946, 0.955] | 0.0033 |
| 0.20 | 0.40 | $7.8\times10^{-3}$ | 5 | 1.000 [0.9995, 1.000] | 0.951 [0.946, 0.956] | 0.0033 |

**How to read it.** The accuracy column is the Bayes accuracy for the *simple-versus-simple* problem: two known Gaussian-mean economies, equal prior probability, 0-1 loss, for which the likelihood-ratio rule is optimal and its accuracy is $\Phi(d'/2)$ with $d'=\sqrt N\lVert\Delta h\rVert_2/\sigma$ (theory column matches the MC to within 0.003). It is *not* a bound on any procedure that must also learn the economies, and it says nothing about other priors or minimax criteria. The certificate, built without knowing the split, covers at about the nominal level with the same width for every $\delta$. $\lVert\Delta h\rVert_2$ has measured log-log slope $2.002$ (necessary $N$ slope $-4.003$), a consistency check on the analytic scaling in §2, not a proof. The contract requires controlled, independent probes; nothing in this table speaks to passive prices.

## 5. What this does and does not establish (Nearest-Literature Comparison)

**Novelty, honestly.** Part 1 combines realization theory (impulse response determines only the merged measure), $\ell_1$-optimal control (worst case $=\ell_1$ norm), and the positive-feedback closed form. Part 2 is Le Cam plus a Gaussian average. Part 3 is Markov–Krein. A control or statistics referee will say each ingredient is classical. The defensible contribution is the finance statement: *for positive-feedback adaptive trading, risk certification is cheaper than identification by a polynomial factor in $1/\Delta\eta$, but only under a controlled-probe contract, a positivity assumption and a memory bound — and the price of lacking them is computable.* I would not describe it as a new mathematical principle.

| Adjacent Literature | Closest Existing Result & What It Assumes | What the Machine Markets Program Adds |
|---|---|---|
| **Financial Microstructure** (Kyle 1985; Glosten–Milgrom 1985; Hasbrouck 1991; Bouchaud et al. 2018) | Infers private information or transient impact kernels from prices and order flow assuming exogenous impact kernels or static informed-trader rules. | Treats the price-response kernel as the **closed-loop output of adaptive filtering/learning cohorts**, proves what public prices cannot identify about cohort memories, and maps statistical experiments into executed quantity, trading loss, and dealer margin capital. |
| **Statistical Mixture & Super-Resolution Theory** (Moitra 2015; Kong–Valiant 2017; Wu–Yang 2020; Batenkov et al. 2021; Manole–Ho 2022) | Establishes $(\Delta\eta)^{-(2K-1)}$ conditioning and $(\Delta\eta)^{-(4K-2)}$ sample complexity for open-loop moment / exponential-sum recovery. | Extracts the moment problem from the **zeros (not poles) of a closed-loop price transfer function** (`thm:merged`), proves matching real-node lower/upper bounds for finite $K$ and $\Theta(1/\log N)$ for general completely monotone memory, and prices class-tagged disclosure (`thm:discvalue`) at $\Theta((\Delta\eta)^{-(4K-4)})$. |
| **System Identification** (Ho–Kalman 1966; Ljung 1999; Whittle 1953) | Shows input–output data identify minimal state-space realizations up to similarity transforms $z\mapsto Tz$ and Whittle spectral information governs passive estimation. | Shows that cohort splitting leaves the minimal realization and summed gain $S$ invariant while making individual strategy identification arbitrarily ill-conditioned, and proves that Euclidean latent-state norms $\lVert z_t\rVert_2$ are coordinate-dependent and not cohort-invariant (`prop:invariance`, Counterexample C4). |
| **Robust & $\ell_1$-Optimal Control** (Vidyasagar 1986; Dahleh–Pearson 1987; Kreiss 1962; Trefethen–Embree 2005) | Establishes that the $\ell_\infty\to\ell_\infty$ induced norm is the $\ell_1$ impulse norm $\sum_k\lvert g_k\rvert$ and that non-normal operators exhibit transient growth invisible to $\rho(J)$. | Applies $\ell_1$ gain certification to **endogenous admission gates** $J(\alpha)=J_0+\alpha B_F$ where the dealer's control action alters the market operator itself, carries the bound through maintenance margin, hedging, and passive fills (`thm:forward`), and proves non-monotone safe admission sets in venue mode (`prop:venue`, `thm:venuebb`). |
| **Moment Problems & Extremal Approximations** (Markov; Krein–Nudel'man 1977; Achieser 1956) | Characterizes sharp upper/lower bounds on $\int g(r)\,dM(r)$ from finite moment prefixes $(k_0,\ldots,k_{n-1})$ on a compact interval $[0,\bar r]$. | Embeds the Markov–Krein moment interval into closed-loop market stability $S=\kappa/(1-a-\kappa\Phi)$ (`thm:window`), proving that without a memory bound $\bar r<1$ no finite impulse window can certify even market stability ($a+\kappa\Phi<1$), and provides outward-rounded interval-arithmetic certificates (`lem:certnum`). |
| **Information Economics & Market Design** (Pagano–Röell 1996; SEC Rule 15c3-5; MiFID II / CAT) | Qualitative or static welfare analysis of pre-/post-trade transparency and pre-trade broker-dealer risk limits. | Quantifies the **information–safety separation**: under reset positive-cohort dynamics (`R`, `O1`), pre-trade solvency requires only $\Phi$ at $\delta$-free cost $O(\sigma^2\varepsilon^{-2}\log(1/\varepsilon))$, whereas strategy surveillance requires class-tagged disclosure (`I1`) to avoid the $(\Delta\eta)^{-(4K-2)}$ barrier. |

**What it does not support.** It does not support "passive public prices certify risk". The repository's own evidence on that contract is: no overshoot in the BTCUSDT depth analysis; the merged response was estimated precisely in 5 of 30 markets (a failed pre-registered criterion); a failed pre-registered Coinbase test; a ~2.4% certified position-limit gain over a volatility limit in one test. Those results narrow the empirical claim; they should not be cited as confirming the bridge.

## 6. Open obligations (ordered by how much they threaten the claim)

| # | Obligation | Why it matters |
|---|---|---|
| 1 | **Hidden initial state — resolved (Option A scope restriction, 2026-10-20).** (R) explicitly requires a reset ($z_0=0$) or observed drift $b_t=CJ^t z_0$. Counterexample C4 (`part_f`) proves that two positive-cohort economies with identical $\Phi=2/5$ ($S=5$) and identical $(h_0,h_1,h_2)=(1,3/5,363/800)$ have different unforced drift $CJ^t z_0$ and different forward-solvency bounds $M_C\lVert z_t\rVert_2$ when $z_t\neq 0$ is unknown. Paper 2 §6 (`p2_guard.tex`) now states this scope restriction and counterexample explicitly. | Restricts identification-invariance to the reset/observed-drift quantity-gate contract; general forward solvency with unknown hidden state is not claimed to be identification-invariant. |
| 2 | **Passive observation.** No finite-sample guarantee exists; evidence is mixed-to-negative. | Decides whether the bridge is a theory of controlled probing only. |
| 3 | **Dependent noise, model-order error, delays, retraining, and algorithms that react to probes.** O1 assumes independent Gaussian taps and, per Paper 1 (`p1_front.tex`, "Algorithms that react to being probed"), that cohorts keep their memories while probed. `prop:hotelling` is conditional; none of these was re-run here. C1 shows the model boundary is real. | Required before any "robustness" language; probe-reactivity bears directly on whether O1 is realizable. |
| 4 | **Mechanize the cohort $S$ formula** and either formalize Pinsker or label it as cited. | Closes the one load-bearing unformalized step. |
| 5 | **Specialist review of Paper 1's $(\Delta\eta)^{-(4K-2)}$ and $1/\log N$ rates and of Thm 5.4(ii).** I re-derived only the $K=2$-vs-1 pair scaling, and only its necessary direction. | The rates are the premise of part 2 for general $K$. |
| 6 | **Repository integrity — resolved 2026-10-20.** After merging `0b46a08` the generated receipts listed 396 declarations while `COVERAGE.md` claimed 443 (the 47 `is_*` theorems in `InfoSafetyExtensions.lean` were un-audited). `verify_formalization.py` was re-run: 443 declarations, standard axioms only, no `sorry`; `named_declarations.json`, `checked_theorem_types.json` and `axiom_audit.jsonl` now agree with `COVERAGE.md`, and `verify_ceiling_suite_lean_proofs.py` passes (26 + 26 + 3). | Kept as a record. `complete = False` in the receipt still stands: kernel-checked is not the same as every manuscript statement fully formalized. |
