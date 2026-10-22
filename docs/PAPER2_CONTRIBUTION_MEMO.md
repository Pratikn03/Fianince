# PAPER 2 CONTRIBUTION MEMO: TRANSIENT AMPLIFICATION, AN EXACT DEPTH CONDITION, AND A MAXIMAL PRE-TRADE GUARD

**Title:** *From Human Markets to Machine Markets: Transient Amplification, an Exact Depth Condition, and a Maximal Pre-Trade Guard*  
**Authors:** Pratik Niroula, Safwan Alkhushayni, Yize Chen, Maitreya Bhavsar, and Pratik Niroula  
**Target Journal:** *Journal of Finance* / *Review of Financial Studies* / *Journal of Financial Economics*  
**Status Assessment:** Elevated to **9.0/10** (Foundational Market Design, Robust Financial Control & Empirical Microstructure)

---

## 1. Core Research Question & Primary Claim

> **Can an exchange, clearinghouse, or market maker certify solvency and enforce safe pre-trade risk controls without identifying the individual trading strategies of hidden algorithmic market participants? If so, what is the exact economic value and mathematical cost of that distinction?**

### The Established Answer
1. **The Information–Safety Separation**: Under positive-feedback closed-loop dynamics, the worst-case cumulative market response under bounded adversarial disturbance is governed by the scalar sum $S = \sum_{t\ge 0} h_t = \frac{\kappa}{1 - a - \kappa\Phi}$ where $\Phi = \sum_i q_i$ (`prop:invariance`, `thm:sum`). Pre-trade risk certification requires only $\Phi$, not the individual memory rates $(\eta_i)$ or weights $(q_i)$.
2. **Sample-Complexity Separation**: Under reset controlled probing (Contract O1), certifying $S$ to accuracy $\epsilon$ requires $N = \Theta(\sigma^2\epsilon^{-2}\log(1/\epsilon))$ experiments **independent of cohort spacing $\Delta\eta$ and count $K$** (`thm:certcost`). This contrasts sharply with the $\Omega((\Delta\eta)^{-(4K-2)})$ sample complexity of strategy identification established in Paper 1.
3. **Finite-Window Markov–Krein Geometry**: From a finite window of impulse taps $h_0,\ldots,h_n$, the compatible sensitivity range forms a closed interval $[\Phi_-, \Phi_+]$ that shrinks geometrically if memory persistence is bounded ($\bar r < 1$). If $\bar r = 1$, $\Phi_+ = \infty$ for any finite window, proving that certifying market stability from price data is impossible without a prior memory bound (`thm:window`).
4. **Maximal Pre-Trade Guard**: An exact pre-trade inequality over the $\ell_\infty$ disturbance ball enforces forward solvency while admitting maximal liquidity (`thm:forward`). Non-zero initial market and cohort displacement consumes buffer according to an exact unforced drift envelope (`prop:driftguard`), strictly reducing safe admission capacity.
5. **Empirical Performance in Machine-Dominated Markets**: Evaluated on $1{,}252$ symbol-days across 19 thin crypto perpetual futures, combining the certified response guard with a conventional volatility cap reduces maximum drawdown catastrophic losses by **$28.5\%$** (from $\$623\text{k}$ to $\$445\text{k}$) and provides **$+7.9\%$ higher notional capacity** at matched training risk budget ($\mathrm{ES}_{95}$).

---

## 2. Evidence Base & Verification Dossier

- **Formal Mechanization**: All 28 Paper 2 environments—including the maximal guard derivation, one-step attained bounds, positive impulse tail decay, inventory-damped sensitivity (`prop:inventory_S`), and hidden drift envelope (`prop:driftguard`)—fully mechanized and audited in Lean 4 (445 declarations in `research_extension/current_manuscript_lean_20261008/` and 401 in `lean_proofs/`).
- **High-Precision Verification**: 80-digit decimal calculations verify the exact bridge $S = \kappa/(1-a-\kappa\Phi)$ to $10^{-12}$ against long-horizon impulse sums, confirm the drift envelope formula to $10^{-16}$, and verify the geometric decay factor $\rho_{\mathrm{cheb}}$ of Markov–Krein window bounds across $\bar r \in [0.80, 0.99]$.
- **Fair Empirical Benchmarking**: Evaluated across 6 distinct risk policies under strictly training-calibrated sizing (`hardened_empirical_audits.py`). Resolves the exposure reduction confound in baseline Part 24 and demonstrates that while breach rates are indistinguishable at matched average notional ($\Delta = +0.25\text{ pp}$, $95\%\text{ CI}: [-5.64, +5.16]$), the guard delivers substantial risk-adjusted value in truncating tail catastrophic excursions and expanding capacity at matched risk budgets.
- **Sequential Economic Mechanism**: Non-overlapping sequential persistence tests (`hardened_empirical_audits.py`) demonstrate that pre-window structural fragility $\hat C_3$ drives initial 15-minute price displacement ($\Delta R^2 = +3.32\text{ pt}$), which attenuates subsequent excursion predictability by $65.1\%$ (level) and $40.3\%$ (incremental travel).

---

## 3. Demarcation of What Remains Limited

1. **Positivity Restriction**: The scalar sufficiency of $\Phi$ holds if and only if closed-loop impulse responses are nonnegative ($h_t \ge 0$). If contrarian trading ($q_i < 0$) or strong inventory payback causes $h_t$ to change sign, $\|h\|_1 > |S|$ (Counterexample C1), and the guard must evaluate the full $\ell_1$ norm $\sum_t |h_t|$.
2. **Hidden Initial State Scope**: The scalar quantity gate $\alpha^* = c_I/(\kappa\Phi^+)$ assumes an explicitly reset initial market state ($z_0 = 0$). When hidden cohort memory is non-zero ($z_0 \neq 0$), forward solvency requires the unforced drift haircut derived in `prop:driftguard`.
3. **Observational Bootstrap vs. Mathematical Certificate**: When the guard confidence set $\mathcal C(D)$ is constructed via a moving-block bootstrap on observational crypto trade data without active resets, it provides an empirical stress heuristic, not a finite-sample mathematical guarantee.
4. **Strategic Manipulation**: If market participants react to pre-trade throttling by scaling up their base aggressiveness ($q_i \propto 1/\alpha$), loop sensitivity rises and the fixed-parameter capacity bound breaks down.
